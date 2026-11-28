"""Adapt the donor PreparedStage/PrepareResources worker to the FEX draw FIFO.

The producer already chooses the exact pipeline and synchronizes SRT pages.
The helper reads only a lease of that immutable snapshot: no guest loads,
Vulkan calls, resource cache mutation, or waits on the renderer. The consumer
uses the result only after release publication and still validates live mappings.
"""
from pathlib import Path

HEADER=r'''#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <deque>
#include <functional>
#include <mutex>
#include <optional>
#include <thread>
#include <vector>
#ifdef __linux__
#include <sys/resource.h>
#endif
namespace BachataPreparedSharps {
using U64=std::uint64_t;
template<class Image,class Res>
U64 ImageHash(const Image& image,const Res& res) {
    std::array<U64,4> key;
    static_assert(sizeof(key)==sizeof(Image));
    std::memcpy(key.data(),&image,sizeof(key));
    const unsigned flags=unsigned(res.is_written)|unsigned(res.is_depth)<<1|unsigned(res.is_array)<<2;
    U64 hash=flags*0x9E3779B97F4A7C15ull;
    for(U64 word:key) {hash=(hash^word)*0xFF51AFD7ED558CCDull;hash^=hash>>32;}
    return hash;
}

template<class Buffer,class Image,class Sampler>
struct Stage {
    std::atomic<bool> ready{false};
    std::vector<Buffer> buffers;
    std::vector<Image> images;
    std::vector<Sampler> samplers;
    std::vector<U64> hashes;
    Stage()=default;
    // Live pipeline metadata must not inherit a previous packet's result.
    Stage(const Stage&) {}
    Stage(Stage&&) noexcept {}
    Stage& operator=(const Stage&) { Reset();return *this; }
    Stage& operator=(Stage&&) noexcept { Reset();return *this; }
    void Reset(){ready.store(false,std::memory_order_relaxed);}
    template<class Info>
    void Prepare(const Info& info) {
        buffers.resize(info.buffers.size());
        images.resize(info.images.size());hashes.resize(info.images.size());
        samplers.resize(info.samplers.size());
        for(size_t i=0;i<buffers.size();++i)
            buffers[i]=info.buffers[i].IsSpecial()?Buffer::Null():info.buffers[i].GetSharp(info);
        for(size_t i=0;i<images.size();++i) {
            const auto& res=info.images[i];
            // Array representative selection still depends on live mapping.
            images[i]=res.array_size?Image::Null(res.is_depth):res.GetSharp(info,false);
            hashes[i]=ImageHash(images[i],res);
        }
        for(size_t i=0;i<samplers.size();++i) samplers[i]=info.samplers[i].GetSharp(info);
        ready.store(true,std::memory_order_release);
    }
    template<class Info,class Res>
    Buffer GetBuffer(const Info& info,const Res& res) const {
        if(!ready.load(std::memory_order_acquire))return res.GetSharp(info);
        return buffers[&res-info.buffers.data()];
    }
    template<class Info,class Res,class Mapped>
    Image GetImage(const Info& info,const Res& res,Mapped mapped) const {
        if(res.array_size||!ready.load(std::memory_order_acquire))return res.GetSharp(info);
        auto image=images[&res-info.images.data()];
        if(image.Address()&&!mapped(image.Address()))return Image::Null(res.is_depth);
        return image;
    }
    template<class Info,class Res>
    Sampler GetSampler(const Info& info,const Res& res) const {
        if(!ready.load(std::memory_order_acquire))return res.GetSharp(info);
        return samplers[&res-info.samplers.data()];
    }
    template<class Info,class Res>
    std::optional<U64> Hash(const Info& info,const Res& res,const Image& image) const {
        if(!ready.load(std::memory_order_acquire)||res.array_size)return {};
        const auto* begin=info.images.data();
        // Never subtract pointers unless the referenced resource belongs to this snapshot.
        size_t index=0;
        for(;index<info.images.size();++index)if(&begin[index]==&res)break;
        if(index==info.images.size()||std::memcmp(&image,&images[index],sizeof(image)))return {};
        return hashes[index];
    }
};

class Worker {
    std::mutex mutex;
    std::condition_variable cv;
    std::deque<std::function<void()>> queue;
    std::jthread thread;
public:
    Worker():thread([this](std::stop_token stop){
#ifdef __linux__
        // Donor preparation uses spare CPU cycles, not the GPU recorder's priority.
        (void)setpriority(PRIO_PROCESS,0,10);
#endif
        for(;;) {
            std::unique_lock lock{mutex};
            cv.wait(lock,[&]{return stop.stop_requested()||!queue.empty();});
            if(stop.stop_requested())return;
            auto task=std::move(queue.front());queue.pop_front();
            lock.unlock();task();
        }
    }){}
    ~Worker(){thread.request_stop();cv.notify_all();}
    void TrySubmit(std::function<void()> task) {
        std::unique_lock lock{mutex,std::try_to_lock};
        if(!lock.owns_lock()||queue.size()>=8)return;
        queue.emplace_back(std::move(task));lock.unlock();cv.notify_one();
    }
};
inline Worker& PrepareWorker(){static Worker worker;return worker;}
template<class Info> struct Scope {
    inline static thread_local const Info* active=nullptr;
    const Info* previous;
    explicit Scope(const Info& info):previous{active}{active=&info;}
    ~Scope(){active=previous;}
};
}
'''

SNAPSHOT=r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <vector>
#include "shader_recompiler/bachata_prepared_sharps.h"
namespace BachataDrawPipe {
template<class Info,std::size_t Count> struct Snapshots {
    struct Storage {
        std::array<Info,Count> values{};
        std::array<const Info*,Count> origins{};
        std::array<const Info*,Count> pointers{};
        std::array<std::vector<std::uint32_t>,Count> words;
    };
    std::shared_ptr<Storage> storage;
    std::array<const Info*,Count> pointers{};
    void Invalidate() {
        if(storage && storage.use_count()==1)storage->origins.fill(nullptr);
        else storage.reset();
        pointers.fill(nullptr);
    }
    void Capture(std::span<const Info* const> stages,bool prepare=false) {
        // A helper may outlive the draw. Never reuse its storage until its
        // lease is gone; this also protects the spans into the UD vectors.
        if(!storage||storage.use_count()!=1)storage=std::make_shared<Storage>();
        auto& s=*storage;
        s.pointers.fill(nullptr);
        for(const Info* source:stages) {
            if(!source)continue;
            const auto slot=static_cast<std::size_t>(source->sw_stage);
            assert(slot<Count);
            auto& value=s.values[slot];
            if(s.origins[slot]!=source) {value=*source;s.origins[slot]=source;}
            value.params.reset();
            s.words[slot].assign(source->user_data.begin(),source->user_data.end());
            value.user_data=s.words[slot];
            value.pgm_base=source->pgm_base;
            value.flattened_ud_buf=source->flattened_ud_buf;
            value.srt_guest_sources=source->srt_guest_sources;
            value.sharp_tables=source->sharp_tables;
            if constexpr(requires{value.order_sharps.Reset();})value.order_sharps.Reset();
            s.pointers[slot]=&value;
        }
        pointers=s.pointers;
        if constexpr(requires(Info& i){i.order_sharps.Prepare(i);}) {
            if(prepare)BachataPreparedSharps::PrepareWorker().TrySubmit([lease=storage]{
                for(size_t i=0;i<Count;++i)if(lease->pointers[i]) {
                    auto& stage=lease->values[i];
                    stage.order_sharps.Prepare(stage);
                }
            });
        }
    }
};
}
'''

def apply(root):
    src=Path(root)/'src'
    def edit(rel,a,b,n=1):
        p=src/rel;s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f'{rel}: expected {n} anchors, found {s.count(a)}: {a[:90]}')
        p.write_text(s.replace(a,b))
    (src/'shader_recompiler/bachata_prepared_sharps.h').write_text(HEADER)
    (src/'video_core/amdgpu/bachata_draw_snapshot.h').write_text(SNAPSHOT)
    r='shader_recompiler/resource.h'
    edit(r,'''    constexpr AmdGpu::Image GetSharp(const auto& info) const noexcept {
        if (!array_size) return GetElementSharp(info,0);
        for (u32 i=0;i<array_size;++i) {
            auto image=GetElementSharp(info,i);''','''    constexpr AmdGpu::Image GetSharp(const auto& info,bool check_mapping=true) const noexcept {
        if (!array_size) return GetElementSharp(info,0,check_mapping);
        for (u32 i=0;i<array_size;++i) {
            auto image=GetElementSharp(info,i,check_mapping);''')
    edit(r,'constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {',
         'constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element,bool check_mapping=true) const noexcept {')
    edit(r,'(!std::is_constant_evaluated() && image.Address() != 0 &&',
         '(check_mapping && !std::is_constant_evaluated() && image.Address() != 0 &&')
    h='shader_recompiler/info.h'
    edit(h,'#include "shader_recompiler/resource.h"',
         '#include "shader_recompiler/resource.h"\n#include "shader_recompiler/bachata_prepared_sharps.h"')
    edit(h,'    std::vector<u32> flattened_ud_buf;',
         '    std::vector<u32> flattened_ud_buf;\n    BachataPreparedSharps::Stage<AmdGpu::Buffer,AmdGpu::Image,AmdGpu::Sampler> order_sharps;')
    edit(h,'    void RefreshFlatBuf() {','    void RefreshFlatBuf() {\n        order_sharps.Reset();')
    edit('video_core/amdgpu/liverpool.cpp','    if(pipeline)op.stages.Capture(pipeline->GetStages());',
         '    if(pipeline)op.stages.Capture(pipeline->GetStages(),\n        Common::ElfInfo::Instance().GameSerial()=="CUSA00785");')
    v='video_core/renderer_vulkan/vk_rasterizer.cpp'
    edit(v,'    const u32 flags = u32(res.is_written) | u32(res.is_depth) << 1 | u32(res.is_array) << 2;\n    u64 hash = flags * 0x9E3779B97F4A7C15ull;\n    for (u64 word : key) {\n        hash = (hash ^ word) * 0xFF51AFD7ED558CCDull;\n        hash ^= hash >> 32;\n    }',
         '''    const u32 flags = u32(res.is_written) | u32(res.is_depth) << 1 | u32(res.is_array) << 2;
    const auto* prepared=BachataPreparedSharps::Scope<Shader::Info>::active;
    const auto cached=prepared?prepared->order_sharps.Hash(*prepared,res,sharp):std::nullopt;
    const u64 hash=cached?*cached:BachataPreparedSharps::ImageHash(sharp,res);''')
    edit(v,'            const auto vsharp = desc.GetSharp(stage);',
         '            const auto vsharp = stage.order_sharps.GetBuffer(stage,desc);')
    edit(v,'        const auto sharp=res.GetSharp(stage);',
         '        const auto sharp=stage.order_sharps.GetImage(stage,res,Shader::IsBachataMappedImageBase);')
    edit(v,'        const auto tsharp = image_desc.GetSharp(stage);',
         '        const auto tsharp = stage.order_sharps.GetImage(stage,image_desc,Shader::IsBachataMappedImageBase);')
    edit(v,'        auto ssharp = sampler.GetSharp(stage);','        auto ssharp = stage.order_sharps.GetSampler(stage,sampler);')
    # Preserve the existing barrier provenance guard as the first statement.
    bind_textures_scope = ('void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {\n'
                           '    const OrderBarrierScope order_barrier_scope{&runtime,OrderBarrierOrigin::Texture};')
    edit(v,bind_textures_scope,bind_textures_scope+'\n    BachataPreparedSharps::Scope<Shader::Info> prepared_scope{stage};')
