#!/usr/bin/env python3
"""Exercise effective mip sizing, tail decisions, alias epochs and retirement.

The effective T# fields, tiling tables, ImageInfo methods, cache lookup/registry,
SlotVector/LRU and tail methods are compiled. Vulkan image creation, format
conversion, overlap merging and command submission are fixture boundaries.
No GPU performance or gameplay result is inferred from this host gate.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile

from test_sotc_texture_find_memo import function, strip_includes


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <cmath>
#include <compare>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <numeric>
#include <optional>
#include <ranges>
#include <set>
#include <span>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_set>
#include <utility>
#include <vector>
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define DEBUG_ASSERT(x) assert(x)
#define UNREACHABLE_MSG(...) do {assert(false);std::abort();}while(false)
#define LOG_WARNING(...) ((void)0)
__COMMON__
namespace Common {
void* ReserveMemoryPages(std::size_t n)noexcept{return std::calloc(1,n);}
void CommitMemoryPages(void*,std::size_t)noexcept{}
void ReleaseMemoryPages(void* p,std::size_t)noexcept{std::free(p);}
struct ElfInfo {std::string serial="CUSA08809";
    static ElfInfo& Instance(){static ElfInfo v;return v;}
    const std::string& GameSerial()const{return serial;}};
}
namespace Libraries::Kernel {inline bool neo=false;bool sceKernelIsNeoMode(){return neo;}}
namespace AmdGpu {
__ENUMS__
__TILING_METHODS__
__FORMAT_BITS__
inline DataFormat RemapDataFormat(DataFormat f){return f;}
inline NumberFormat RemapNumberFormat(NumberFormat n,DataFormat){return n;}
inline bool BachataOrderNoMsaa(){return false;}
struct CbDbExtent;
struct Image {
__SHARP_FIELDS__
__SHARP_METHODS__
    // Format swizzles and macro bank selection do not affect the eligible
    // linear/1D layouts; macro layouts are rejected by RebaseToMip.
    int DstSelect()const{return 0;}
    u8 GetBankSwizzle()const{return 0;}
};
static_assert(sizeof(Image)==32);
}
namespace Shader {
enum class MipStorageFallbackMode{None,ConstantIndex,DynamicIndex};
struct ImageResource{bool is_written=false,is_depth=false,is_array=false;
    MipStorageFallbackMode mip_fallback_mode=MipStorageFallbackMode::None;};
}
namespace vk {enum class Format:u32{eUndefined=0};}
namespace Vulkan::LiverpoolToVK {
inline vk::Format SurfaceFormat(AmdGpu::DataFormat f,AmdGpu::NumberFormat n){return vk::Format(u32(f)*16+u32(n));}
inline vk::Format PromoteFormatToDepth(vk::Format f){return vk::Format(u32(f)+1024);}
inline int ComponentMapping(int m){return m;}
}
__POLICY__
__INFO_HEADER__
__TILE__
namespace VideoCore {
namespace LiverpoolToVK=Vulkan::LiverpoolToVK;
__INFO_METHODS__
struct ImageViewInfo{
    bool is_storage=false;vk::Format format{};int mapping=0;
    AmdGpu::ImageType type{};u32 min_lod=0;SubresourceRange range;
    ImageViewInfo()=default;ImageViewInfo(const AmdGpu::Image&,const Shader::ImageResource&)noexcept;
};
__VIEW_CONSTRUCTOR__
__IMAGE_FLAGS__
struct Image {
    inline static u64 next_uid=1;
    ImageInfo info;ImageFlagBits flags=ImageFlagBits::CpuDirty;
    u64 image_uid=next_uid++,tick_accessed_last=0;size_t lru_id=0;
    u64 hash=0;unsigned uploads=0;
    struct{u32 is_bound:1;u32 is_target:1;u32 needs_rebind:1;u32 force_general:1;u32 mip_tail_writer:1;}binding{};
    Image(int,int,int,const ImageInfo& i):info(i){}
__OVERLAPS__
__SAFE_DOWNLOAD__
};
inline unsigned violations=0;
void NoteSotcMipTailWrite(const Image&){++violations;}
__WRITE_HELPERS__
bool IsVulkanFormatCompatible(vk::Format a,vk::Format b){return a==b;}
struct CheckedMutex{
    bool held=false;void lock(){assert(!held);held=true;}void unlock(){assert(held);held=false;}
};
struct Pages{
    std::map<u64,std::vector<ImageId>> data;
    std::vector<ImageId>* find(u64 p){auto i=data.find(p);return i==data.end()?nullptr:&i->second;}
    auto& operator[](u64 p){return data[p];}
};
struct CheckedLru:Common::LeastRecentlyUsedCache<ImageId,u64>{
    using Base=Common::LeastRecentlyUsedCache<ImageId,u64>;
    std::set<size_t> live;unsigned touches=0;
    size_t Insert(ImageId id,u64 tick){auto n=Base::Insert(id,tick);assert(live.insert(n).second);return n;}
    void Free(size_t id){assert(live.erase(id)==1);Base::Free(id);}
    void Touch(size_t id,u64 tick){assert(live.contains(id));++touches;Base::Touch(id,tick);}
};
struct TextureCache {
__BINDING_TYPE__;
    struct ImageDesc {
        ImageInfo info;ImageViewInfo view_info;BindingType type=BindingType::Texture;
        u8 rebase_mip=0;bool rebased_now=false;u16 orig_min_lod=0;
        u32 orig_base_layer=0;
        std::optional<ImageInfo> other_info;
        ImageDesc()=default;
        ImageDesc(const AmdGpu::Image& i,const Shader::ImageResource& r):info{i,r},view_info{i,r},
            type{r.is_written?BindingType::Storage:BindingType::Texture}{InitMipTail(i,r);}
        void InitMipTail(const AmdGpu::Image&,const Shader::ImageResource&);
    };
    using ImageIds=std::vector<ImageId>;
__TRAITS__;
__MEMBERS__
    Common::SlotVector<Image> slot_images{1024};Pages page_table;CheckedLru lru_cache;CheckedMutex mutex;
    std::atomic<u64>target_registry_epoch{1};u64 total_used_memory=0,gc_tick=0;
    struct Scheduler{u64 tick=1;u64 CurrentTick()const{return tick;}}scheduler;
    int instance=0,runtime=0,slot_image_views=0;
    std::vector<ImageId>deferred;
    u64 TargetRegistryEpoch()const{return target_registry_epoch.load(std::memory_order_acquire);}
    void RegisterImage(ImageId);void UnregisterImage(ImageId);void TouchImage(const Image&);
    ImageId FindImage(ImageDesc&,bool=false);ImageId FindImageFromRange(VAddr,size_t,bool=true);
    void InvalidateMemoryFromGPU(VAddr,size_t,bool=false);
    bool ReusePreparedTargets(std::span<const ImageId>,u64);
    void UntrackImage(ImageId){}
    void DeleteImage(ImageId id){deferred.push_back(id);}
__FREE_IMAGE__
    Image& GetImage(ImageId id){auto& image=slot_images[id];TouchImage(image);return image;}
    void Retire(){for(auto id:deferred)slot_images.Erase(id);deferred.clear();}
    ImageId Add(const ImageInfo& info){std::scoped_lock lock{mutex};
        auto id=slot_images.Insert(0,0,0,info);RegisterImage(id);return id;}
    ImageId overlap_result{};int overlap_mip=-1,overlap_layer=-1;
    std::tuple<ImageId,int,int>ResolveOverlap(const ImageInfo&,BindingType,ImageId,ImageId){
        return {overlap_result,overlap_mip,overlap_layer};}
__FOR_EACH_REGION__
__FOR_EACH_PAGE__
};
__CACHE_METHODS__
inline unsigned hash_calls=0;
u64 XXH3_64bits(const void* p,size_t n){++hash_calls;u64 h=1469598103934665603ull;
    for(auto c:std::span(static_cast<const u8*>(p),n)){h^=c;h*=1099511628211ull;}return h;}
void ProbeMaybeDirtyRefresh(Image& image){
    if(False(image.flags&ImageFlagBits::Dirty))return;
__MAYBE_DIRTY__
    ++image.uploads;image.flags&=~ImageFlagBits::Dirty;
}
}
using namespace VideoCore;
'''


TESTS = r'''
static AmdGpu::Image Sharp(u32 width=1024,u32 height=1024,u32 base=2,u32 last=4){
    AmdGpu::Image s{};s.base_address=0x800000000ull>>8;s.width=width-1;s.height=height-1;
    s.pitch=width-1;s.base_level=base;s.last_level=last;s.min_lod=768;
    s.type=u64(AmdGpu::ImageType::Color2D);s.data_format=u64(AmdGpu::DataFormat::Format8_8_8_8);
    s.tiling_index=u64(AmdGpu::TileMode::DisplayLinearAligned);return s;
}
static bool IsRegisteredImage(const TextureCache& cache,ImageId id){return True(cache.slot_images[id].flags&ImageFlagBits::Registered);}
static ImageId WarmTail(TextureCache& cache,TextureCache::ImageDesc& desc){
    const auto id=cache.FindImage(desc);assert(desc.rebased_now);
    assert(cache.FindImage(desc)==id&&cache.FindImage(desc)==id);
    assert(cache.MemoLookup(desc.info,false)==id);return id;
}
static void LayoutAndView(){
    Shader::ImageResource r;auto sharp=Sharp();ImageInfo full{sharp,r};
    assert(full.guest_size==5586944&&full.resources.levels==5);
    TextureCache cache;TextureCache::ImageDesc desc{sharp,r};const auto id=WarmTail(cache,desc);
    assert(desc.info.guest_size==344064&&desc.info.sotc_dropped_bytes==5242880);
    assert(desc.info.resources.levels==3&&desc.info.size.width==256&&desc.info.size.height==256);
    assert(desc.view_info.range.base.level==0&&desc.view_info.range.extent.levels==3&&desc.view_info.min_lod==256);
    for(u32 i=0;i<desc.info.resources.levels;++i){
        auto& a=full.mips_layout[i+2];auto& b=desc.info.mips_layout[i];
        assert(full.guest_address+a.offset==desc.info.guest_address+b.offset&&a.size==b.size);
    }
    for(int pass=0;pass<8;++pass){assert(cache.FindImage(desc)==id);assert(desc.view_info.min_lod==256);}
    desc.orig_min_lod=896;SetSotcMipTailView(desc,-1);assert(desc.view_info.min_lod==384);
    SetSotcMipTailView(desc,1);assert(desc.view_info.min_lod==640&&desc.view_info.range.base.level==1);
    SetSotcMipTailView(desc,-1);assert(desc.view_info.min_lod==384);
    unsigned accepted=0,refused=0;
    for(u32 width:{7u,31u,64u,255u,1024u})for(u32 height:{1u,9u,32u,257u})
    for(u32 layers:{1u,2u,6u})for(u32 base:{1u,2u,4u})
    for(auto format:{AmdGpu::DataFormat::Format8,AmdGpu::DataFormat::Format8_8_8_8,AmdGpu::DataFormat::FormatBc1,AmdGpu::DataFormat::FormatBc3})
    for(auto tile:{AmdGpu::TileMode::DisplayLinearAligned,AmdGpu::TileMode::Thin1DThin,AmdGpu::TileMode::Thick1DThick}){
        auto s=Sharp(width,height,base,5);s.data_format=u64(format);s.tiling_index=u64(tile);
        s.type=u64(AmdGpu::ImageType::Color2DArray);s.depth=layers-1;
        ImageInfo original{s,r},tail=original;
        if(!tail.RebaseToMip(base)){++refused;assert(tail.guest_address==original.guest_address&&tail.guest_size==original.guest_size);continue;}
        ++accepted;assert(tail.guest_size+tail.sotc_dropped_bytes==original.guest_size);
        for(u32 mip=0;mip<tail.resources.levels;++mip){
            auto&a=original.mips_layout[base+mip];auto&b=tail.mips_layout[mip];
            assert(a.offset==b.offset+tail.sotc_dropped_bytes&&a.pitch==b.pitch&&a.height==b.height&&a.size==b.size);
        }
    }
    assert(accepted>1000);std::cout<<"MIP_TAIL_LAYOUT_CASES accepted="<<accepted<<" refused="<<refused<<'\n';
    auto damaged=full;damaged.mips_layout[3].height+=8;auto before=damaged;
    assert(!damaged.RebaseToMip(2));assert(damaged.guest_size==before.guest_size&&damaged.guest_address==before.guest_address);
    auto bad=full;bad.guest_size=0;assert(!bad.RebaseToMip(2));
    bad=full;bad.guest_address=UINT64_MAX-16;assert(!bad.RebaseToMip(2));
    bad=full;bad.array_mode=AmdGpu::ArrayMode::Array2DTiledThin1;assert(!bad.RebaseToMip(2));
    bad=full;bad.alt_tile=true;assert(!bad.RebaseToMip(2));
    bad=full;bad.bank_swizzle=1;assert(!bad.RebaseToMip(2));
    bad=full;bad.props.is_depth=true;assert(!bad.RebaseToMip(2));
    bad=full;bad.props.is_volume=true;assert(!bad.RebaseToMip(2));
    bad=full;bad.num_samples=4;assert(!bad.RebaseToMip(2));
    bad=full;bad.num_bits=4;assert(!bad.RebaseToMip(2));
    assert(!bad.RebaseToMip(0)&&!bad.RebaseToMip(5));
    for(auto mode:{Shader::MipStorageFallbackMode::ConstantIndex,Shader::MipStorageFallbackMode::DynamicIndex}){
        r.mip_fallback_mode=mode;TextureCache::ImageDesc d{sharp,r};assert(!d.other_info&&!d.rebase_mip);}
    r={};r.is_written=true;assert(!TextureCache::ImageDesc(sharp,r).other_info);
    r={};r.is_depth=true;assert(!TextureCache::ImageDesc(sharp,r).other_info);
    // The raw descriptor cache must include all T# bytes, depth and Neo mode.
    r={};auto changed=Sharp(512,128);ImageInfo a{changed,r};assert(a.size.width==512&&a.size.height==128);
    changed=sharp;changed.alt_tile_mode=1;Libraries::Kernel::neo=false;ImageInfo normal{changed,r};
    Libraries::Kernel::neo=true;ImageInfo neo{changed,r};assert(!normal.alt_tile&&neo.alt_tile);
    Libraries::Kernel::neo=false;ImageInfo normal_again{changed,r};assert(!normal_again.alt_tile);
}
static ImageInfo Alias(const ImageInfo& tail){
    auto a=tail;a.sotc_first_mip=0;a.sotc_dropped_bytes=0;a.guest_address-=256;
    a.guest_size+=512;a.size.width+=1;return a;
}
static void RefindLayer(){
    for(u32 original_layer:{0u,2u}){
        TextureCache cache;Shader::ImageResource resource;auto sharp=Sharp(256,256,1,1);
        if(original_layer){resource.is_array=true;sharp.type=u64(AmdGpu::ImageType::Color2DArray);
            sharp.depth=3;sharp.base_array=original_layer;sharp.last_array=3;}
        TextureCache::ImageDesc desc{sharp,resource};auto array=*desc.other_info;
        array.sotc_first_mip=0;array.sotc_dropped_bytes=0;array.resources.layers=8;array.UpdateSize();
        const auto array_id=cache.Add(array);cache.overlap_result=array_id;
        cache.overlap_mip=0;cache.overlap_layer=3;
        assert(cache.FindImage(desc)==array_id&&desc.rebased_now&&desc.view_info.range.base.layer==3);
        cache.FreeImage(array_id);cache.overlap_result={};cache.overlap_mip=cache.overlap_layer=-1;
        const auto writer=cache.Add(Alias(desc.info));MarkMipTailGpuModified(cache.slot_images[writer]);
        const auto replacement=cache.FindImage(desc);
        assert(!desc.rebased_now&&desc.view_info.range.base.layer==original_layer);
        assert(desc.view_info.range.base.layer+desc.view_info.range.extent.layers<=cache.slot_images[replacement].info.resources.layers);
    }
}
static void PendingWriterAndEpoch(){
    for(int kind=0;kind<3;++kind){
        TextureCache cache;Shader::ImageResource r;TextureCache::ImageDesc desc{Sharp(),r};
        const auto tail=WarmTail(cache,desc);cache.slot_images[tail].binding.is_bound=1;
        const auto writer=cache.Add(Alias(desc.info));cache.slot_images[writer].flags&=~ImageFlagBits::Dirty;
        assert(cache.FindImage(desc)==tail&&cache.FindImage(desc)==tail); // alias is read-only so far
        const auto registry=cache.TargetRegistryEpoch();const auto epoch=sotc_mip_tail_gpu_epoch.load();
        if(kind==0)MarkMipTailWriterIntent(cache.slot_images[writer]);
        else if(kind==1){std::array ids{writer};assert(cache.ReusePreparedTargets(ids,registry));}
        else MarkMipTailGpuModified(cache.slot_images[writer]);
        assert(cache.TargetRegistryEpoch()==registry&&sotc_mip_tail_gpu_epoch.load()!=epoch);
        const auto full=cache.FindImage(desc);assert(full!=tail&&!desc.rebased_now);
        assert(!IsRegisteredImage(cache,tail)&&cache.slot_images.IsAllocated(tail));
        assert(cache.slot_images[tail].binding.needs_rebind);
        const auto touches=cache.lru_cache.touches;cache.gc_tick=99;cache.GetImage(tail);
        assert(cache.lru_cache.touches==touches); // freed/reused LRU node cannot be touched
        assert(IsRegisteredImage(cache,writer));cache.Retire();assert(!cache.slot_images.IsAllocated(tail));
    }
    // Writer memo warmed while no tails existed cannot skip retirement after a
    // tail at a different base was registered. Per-address generation is unchanged.
    TextureCache cache;Shader::ImageResource r;ImageInfo full{Sharp(),r};auto tail_info=full;
    assert(tail_info.RebaseToMip(2));TextureCache::ImageDesc writer_desc;writer_desc.info=Alias(tail_info);
    writer_desc.type=TextureCache::BindingType::Storage;
    const auto writer=cache.FindImage(writer_desc);cache.FindImage(writer_desc);cache.FindImage(writer_desc);
    cache.slot_images[writer].binding={}; // prior command had no GPU write
    const auto generation=cache.MemoGeneration(writer_desc.info.guest_address);
    TextureCache::ImageDesc tail_desc{Sharp(),r};const auto tail=WarmTail(cache,tail_desc);
    assert(cache.MemoGeneration(writer_desc.info.guest_address)==generation);
    assert(cache.FindImage(writer_desc)==writer&&!IsRegisteredImage(cache,tail));
}
static void RetirementAndRefresh(){
    TextureCache cache;Shader::ImageResource r;auto sharp=Sharp();TextureCache::ImageDesc desc{sharp,r};
    const auto tail=WarmTail(cache,desc);
    assert(!cache.FindImageFromRange(desc.info.guest_address,desc.info.guest_size,false));
    auto full=ImageInfo{sharp,r};
    cache.InvalidateMemoryFromGPU(full.guest_address,full.guest_size);
    assert(True(cache.slot_images[tail].flags&ImageFlagBits::GpuDirty));
    // A later base mip retires old idle tails of the same chain, but keeps live
    // or GPU-written images. Actual destruction remains deferred.
    cache.scheduler.tick=100;cache.slot_images[tail].tick_accessed_last=1;
    sharp.base_level=3;TextureCache::ImageDesc smaller{sharp,r};const auto new_id=cache.FindImage(smaller);
    assert(new_id!=tail&&!IsRegisteredImage(cache,tail)&&cache.slot_images.IsAllocated(tail));
    auto kept=cache.Add(desc.info);cache.slot_images[kept].binding.is_bound=1;
    cache.PruneMipTails(new_id);assert(IsRegisteredImage(cache,kept));
    cache.slot_images[kept].binding={};cache.slot_images[kept].flags|=ImageFlagBits::GpuModified;
    cache.PruneMipTails(new_id);assert(IsRegisteredImage(cache,kept));
    // Prefix texels are unchanged while a later mip changes. A tail must upload
    // on MaybeCpuDirty instead of returning on the old 8x8 prefix hash.
    std::vector<u8> bytes(desc.info.guest_size,7);Image image(0,0,0,desc.info);
    image.info.guest_address=reinterpret_cast<VAddr>(bytes.data());
    image.flags=ImageFlagBits::MaybeCpuDirty;image.hash=XXH3_64bits(bytes.data(),8*8*4);
    bytes.at(desc.info.mips_layout[1].offset)^=31;const auto hashes=hash_calls;
    ProbeMaybeDirtyRefresh(image);assert(image.uploads==1&&hash_calls==hashes);
    // A late unexpected write is retained as GPU data, never dropped by writer retirement.
    const auto before=violations;MarkMipTailGpuModified(cache.slot_images[new_id]);
    assert(violations==before+1&&True(cache.slot_images[new_id].flags&ImageFlagBits::GpuModified));
}
int main(int argc,char**argv){
    const auto expected=argc>1?std::string(argv[1]):"active";
    if(expected=="other")Common::ElfInfo::Instance().serial="CUSA00785";
    Shader::ImageResource r;auto sharp=Sharp();
    if(expected=="off"||expected=="other"){
        assert(!SotcMipTailMode());TextureCache::ImageDesc d{sharp,r};assert(!d.other_info&&!d.rebase_mip);
        TextureCache cache;auto id=cache.FindImage(d);assert(cache.slot_images[id].info.guest_size==5586944);
        const auto epoch=sotc_mip_tail_gpu_epoch.load();MarkMipTailWriterIntent(cache.slot_images[id]);
        MarkMipTailGpuModified(cache.slot_images[id]);assert(sotc_mip_tail_gpu_epoch.load()==epoch);
        assert(!cache.slot_images[id].binding.mip_tail_writer);std::cout<<"MIP_TAIL_DISABLED_PASS\n";return 0;
    }
    if(expected=="streamed"){
        assert(SotcMipTailMode()==1);assert(!TextureCache::ImageDesc(sharp,r).other_info);
        sharp.lod_hw_cnt_en=1;assert(TextureCache::ImageDesc(sharp,r).other_info);
        std::cout<<"MIP_TAIL_STREAMED_POLICY_PASS\n";return 0;
    }
    assert(SotcMipTailMode()==2);LayoutAndView();RefindLayer();PendingWriterAndEpoch();RetirementAndRefresh();
    std::cout<<"MIP_TAIL_REAL_CACHE_LAYOUT_VIEW_WRITER_DIRTY_LIFETIME_PASS\n";
}
'''


def program(root):
    def read(name):
        return (root/name).read_text()
    tc=read('video_core/texture_cache/texture_cache.cpp')
    th=read('video_core/texture_cache/texture_cache.h')
    image=read('video_core/texture_cache/image.h')
    info=read('video_core/texture_cache/image_info.cpp')
    sharp=read('video_core/amdgpu/resource.h')
    tiling=read('video_core/amdgpu/tiling.h')
    tiling_cpp=read('video_core/amdgpu/tiling.cpp')
    pixel=read('video_core/amdgpu/pixel_format.h')
    pixel_cpp=read('video_core/amdgpu/pixel_format.cpp')
    view=read('video_core/texture_cache/image_view.cpp')
    ctor='ImageInfo::ImageInfo(const AmdGpu::Image& image, const Shader::ImageResource& desc) noexcept'
    view=view.replace(': is_storage{desc.is_written}',': is_storage(desc.is_written)')
    common='\n'.join(strip_includes(read(n)) for n in (
        'common/types.h','common/enum.h','common/alignment.h','common/div_ceil.h','common/slot_vector.h',
        'common/lru_cache.h','video_core/texture_cache/types.h'))
    enums='\n'.join(function(s,sig)+';' for s,sig in (
        (sharp,'enum class ImageType :'),(pixel,'enum class DataFormat :'),
        (pixel,'enum class NumberFormat :'),(tiling,'enum class TileMode :'),(tiling,'enum class ArrayMode :')))
    sharp_fields=sharp[sharp.index('struct Image {')+len('struct Image {'):sharp.index('    static constexpr Image Null(')]
    # The resource file also contains buffer GetDataFmt/GetNumberFmt methods.
    # function() requires a unique signature, so select the image declaration.
    sharp_image=sharp[sharp.index('struct Image {'):sharp.index('static_assert(sizeof(Image)')]
    sharp_methods='\n'.join(function(sharp_image,sig) for sig in (
        '    VAddr Address() const {','    u32 Pitch() const {','    [[nodiscard]] u32 NumLayers()',
        '    u32 NumLevels() const {','    u32 NumSamples() const {','    ImageType GetType() const noexcept',
        '    DataFormat GetDataFmt() const noexcept','    NumberFormat GetNumberFmt() const noexcept',
        '    TileMode GetTileMode() const {','    bool IsTiled() const {',
        '    ImageType GetBaseType() const noexcept','    ImageType GetViewType(',
        '    [[nodiscard]] u32 NumViewLevels(','    [[nodiscard]] u32 NumViewLayers('))
    bits=pixel_cpp[pixel_cpp.index('static constexpr std::array BITS_PER_BLOCK'):pixel_cpp.index('static constexpr std::array BITS_PER_ELEMENT')]
    info_methods=info[info.index('namespace {\n// The raw T#'):info.index(ctor)]
    info_methods+='\n'+'\n'.join(function(info,sig) for sig in (
        ctor,'std::optional<ImageInfo> ImageInfo::CachedRebase(',
        'bool ImageInfo::RebaseToMip(','void ImageInfo::UpdateSize()'))
    cache_methods='\n'.join(function(tc,sig) for sig in (
        'static bool IsSotcMemoPerfectMatch(','bool TextureCache::FindMemoEnabled(',
        'TextureCache::FindMemo& TextureCache::MemoSlot(','u64 TextureCache::MemoGeneration(',
        'ImageId TextureCache::MemoLookup(','static void SetSotcMipTailView(',
        'void TextureCache::ImageDesc::InitMipTail(','bool TextureCache::IsMipTailIdle(',
        'void TextureCache::FreeMipTail(','bool TextureCache::DecideMipTail(',
        'void TextureCache::PruneMipTails(','ImageId TextureCache::FindImage(',
        'ImageId TextureCache::FindImageFromRange(','void TextureCache::RegisterImage(',
        'void TextureCache::UnregisterImage(','void TextureCache::TouchImage(',
        'void TextureCache::InvalidateMemoryFromGPU(','bool TextureCache::ReusePreparedTargets('))
    maybe=function(tc,'    if (True(image.flags & ImageFlagBits::MaybeCpuDirty) &&')
    helpers=image[image.index('inline std::atomic<u64> sotc_mip_tail_gpu_epoch'):image.index('} // namespace VideoCore')]
    parts={
        'COMMON':common,'ENUMS':enums,'SHARP_FIELDS':sharp_fields,'SHARP_METHODS':sharp_methods,
        'TILING_METHODS':'\n'.join(function(tiling_cpp,sig) for sig in (
            'ArrayMode GetArrayMode(','bool IsMacroTiled(','u32 GetMicroTileThickness(')),
        'FORMAT_BITS':bits+'\n'+function(pixel,'constexpr bool IsBlockCoded('),
        'POLICY':strip_includes(read('video_core/texture_cache/sotc_mip_tail_policy.h')),
        'INFO_HEADER':strip_includes(read('video_core/texture_cache/image_info.h')),
        'TILE':strip_includes(read('video_core/texture_cache/tile.h')),'INFO_METHODS':info_methods,
        'VIEW_CONSTRUCTOR':function(view,'ImageViewInfo::ImageViewInfo(const AmdGpu::Image&'),
        'IMAGE_FLAGS':image[image.index('enum ImageFlagBits :'):image.index('struct UniqueImage')],
        'OVERLAPS':function(image,'    bool Overlaps('),'SAFE_DOWNLOAD':function(image,'    bool SafeToDownload('),
        'WRITE_HELPERS':helpers,'BINDING_TYPE':function(th,'    enum class BindingType :'),
        'TRAITS':function(th,'    struct Traits {'),
        'MEMBERS':th[th.index('    // BACHATA_SOTC_TEXTURE_FIND_MEMO_V1'):th.index('    Common::SlotVector<Image> slot_images;')],
        'FREE_IMAGE':function(th,'    void FreeImage('),
        'FOR_EACH_REGION':'template<typename Func>\n'+function(th,'    void ForEachImageInRegion('),
        'FOR_EACH_PAGE':'template<typename Func>\n'+function(th,'    static void ForEachPage('),
        'CACHE_METHODS':cache_methods,'MAYBE_DIRTY':maybe,
    }
    code=PREAMBLE
    for name,value in parts.items():
        token=f'__{name}__';assert code.count(token)==1,token;code=code.replace(token,value)
    return code+TESTS


def source_contracts(root):
    runtime=(root/'video_core/renderer_vulkan/vk_runtime.cpp').read_text()
    assert runtime.count('VideoCore::MarkMipTailGpuModified(*dst);')==6
    assert 'dst->flags |= VideoCore::ImageFlagBits::GpuModified;' not in runtime
    raster=(root/'video_core/renderer_vulkan/vk_rasterizer.cpp').read_text()
    assert raster.count('VideoCore::MarkMipTailWriterIntent(image);\n        image.binding.is_target = 1u;')==2
    cache=(root/'video_core/texture_cache/texture_cache.cpp').read_text()
    assert 'image.info.guest_address != desc.info.stencil_addr || image.info.sotc_first_mip' in cache
    info=(root/'video_core/texture_cache/image_info.cpp').read_text()
    assert 'micro_tiled_mips |= 1u << mip' in info and 'mip_bytes>UINT32_MAX' in info


def run(root):
    source_contracts(root)
    code=program(root)
    with tempfile.TemporaryDirectory(prefix='bachata-mip-tail-') as directory:
        d=Path(directory)
        def build(name,source):
            path=d/(name+'.cpp');exe=d/name;path.write_text(source)
            subprocess.run(['g++','-std=c++20','-O1','-Wall','-Wextra','-Wno-sign-compare',str(path),'-o',str(exe)],check=True,capture_output=True,text=True)
            return exe
        executable=build('positive',code)
        for mode,arg in ((None,'active'),('0','off'),('1','streamed'),(None,'other')):
            env=os.environ.copy();env.pop('SOTC_MIP_TAIL',None);env.pop('BACHATA_SOTC_FIND_MEMO',None)
            if mode is not None:env['SOTC_MIP_TAIL']=mode
            subprocess.run([str(executable),arg],check=True,env=env)
        controls={
            'view_lod':('desc.orig_min_lod - 256 * shift','desc.orig_min_lod'),
            'refind_layer':('desc.view_info.range.base.layer = desc.orig_base_layer;','/* omitted original layer restore */'),
            'writer_epoch':('if (!image.binding.mip_tail_writer && False(image.flags & ImageFlagBits::GpuModified)) {','if (false) {'),
            'gpu_epoch':('if (False(image.flags & ImageFlagBits::GpuModified) && SotcMipTailMode()) {','if (false) {'),
            'memo_epoch':('memo.gpu_epoch != sotc_mip_tail_gpu_epoch.load(std::memory_order_relaxed)','false'),
            'alias_generation':('memo.alias_generation != TargetRegistryEpoch()','false'),
            'retired_lru':('if (True(image.flags & ImageFlagBits::Registered)) {\n        lru_cache.Touch','if (true) {\n        lru_cache.Touch'),
            'tail_cpu_dirty':('False(image.flags & ImageFlagBits::CpuDirty) && !image.info.sotc_first_mip)','False(image.flags & ImageFlagBits::CpuDirty))'),
            'range_writer':('image.info.guest_address != address || image.info.sotc_first_mip','image.info.guest_address != address'),
        }
        for name,(old,new) in controls.items():
            assert code.count(old)==1,(name,code.count(old));bad=build(name,code.replace(old,new))
            env=os.environ.copy();env.pop('SOTC_MIP_TAIL',None);env.pop('BACHATA_SOTC_FIND_MEMO',None)
            result=subprocess.run([str(bad),'active'],env=env,capture_output=True,text=True)
            assert result.returncode!=0,f'negative control unexpectedly passed: {name}'
            assert 'Assertion' in result.stderr or 'assertion' in result.stderr,(name,result.stderr)
        print(f'MIP_TAIL_NEGATIVE_CONTROLS_PASS count={len(controls)}')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path)
    args=parser.parse_args();root=args.source
    if (root/'src').is_dir():root=root/'src'
    try:run(root)
    except subprocess.CalledProcessError as error:
        if error.stdout:print(error.stdout)
        if error.stderr:print(error.stderr)
        raise
