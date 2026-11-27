#!/usr/bin/env python3
"""Compile the effective memo/registration methods and exercise their contracts."""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
import tempfile

import port_texture_binding_memo as overlay


def method(source, signature):
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 1
    at = opening + 1
    while depth:
        depth += (source[at] == '{') - (source[at] == '}')
        at += 1
    return source[start:at]


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <set>
#include <string>
#include <vector>
using u8=uint8_t; using u32=uint32_t; using u64=uint64_t; using VAddr=u64;
#define ASSERT_MSG(condition, ...) assert(condition)
namespace Common {
inline u64 AlignUp(u64 value,u64 align){return (value+align-1)&~(align-1);}
struct ElfInfo {
    std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo info;return info;}
    const std::string& GameSerial() const{return serial;}
};
}
namespace AmdGpu { struct Image {std::array<u64,4> words{};}; constexpr u32 NUM_COLOR_BUFFERS=8; }
namespace Shader {
enum class MipStorageFallbackMode {None,ConstantIndex,DynamicIndex};
struct ImageResource {bool is_written=false,is_depth=false,is_array=false;
    MipStorageFallbackMode mip_fallback_mode=MipStorageFallbackMode::None;
    u32 array_size=0;};
}
namespace VideoCore {
using ImageId=u32;
enum class ImageFlagBits:u32 {Registered=1,GpuModified=2,Dirty=4};
u32 operator&(u32 value,ImageFlagBits flag){return value&u32(flag);}
u32 operator~(ImageFlagBits flag){return ~u32(flag);}
u32& operator|=(u32& value,ImageFlagBits flag){value|=u32(flag);return value;}
bool False(u32 value){return !value;} bool True(u32 value){return value!=0;}
struct ImageViewInfo {u32 mip=0,layer=0;};
struct ImageView {u64 serial=1;};
struct Info {VAddr guest_address=0;u64 guest_size=64;
    struct {bool is_tiled=false;} props;struct {u32 width=64;} size;};
struct Image {
    Info info;u64 image_uid=0,tick_accessed_last=0,lru_id=0;
    u32 flags=0;struct {bool needs_rebind=false,is_bound=false,force_general=false;} binding;
    int view_calls=0;ImageView view;
    bool IsTracked() const{return false;}
    bool SafeToDownload() const{return (flags&ImageFlagBits::GpuModified)&&!(flags&ImageFlagBits::Dirty);}
    ImageView& FindView(const ImageViewInfo&){++view_calls;return view;}
};
struct Slots {
    std::map<ImageId,Image> items;
    bool IsAllocated(ImageId id) const{return items.contains(id);}
    Image& operator[](ImageId id){return items.at(id);}
    const Image& operator[](ImageId id) const{return items.at(id);}
};
struct PageTable {
    std::map<u64,std::vector<ImageId>> values;
    std::vector<ImageId>& operator[](u64 page){return values[page];}
    std::vector<ImageId>* find(u64 page){auto it=values.find(page);return it==values.end()?nullptr:&it->second;}
};
struct Lru {
    int touches=0,frees=0;u64 last_tick=0;
    u64 Insert(ImageId id,u64){return id;}
    void Touch(u64,u64 tick){++touches;last_tick=tick;}
    void Free(u64){++frees;}
};
struct Scheduler {u64 tick=1;u64 CurrentTick()const{return tick;}};
struct TextureCache {
    enum class BindingType {Texture,Storage,RenderTarget,DepthTarget};
    struct ImageDesc {
        Info info;ImageViewInfo view_info;BindingType type=BindingType::Texture;
        u32 flags=0;static inline u64 builds=0;
        ImageDesc()=default;
        ImageDesc(const AmdGpu::Image& sharp,const Shader::ImageResource& resource){
            ++builds;info.guest_address=sharp.words[0];info.guest_size=64;
            flags=u32(resource.is_written)|(u32(resource.is_depth)<<1)|(u32(resource.is_array)<<2);
            type=resource.is_written?BindingType::Storage:BindingType::Texture;
        }
    };
    Slots slot_images;PageTable page_table;Lru lru_cache;Scheduler scheduler;
    std::mutex mutex,download_images_mutex;
    std::atomic<u64> registry_generation{0};
    u64 total_used_memory=0,gc_tick=1,next_uid=1;
    bool readback_linear_images=true;
    std::set<ImageId> download_images;
    struct {int writes=0;void Write(VAddr,u64){++writes;}} surface_metadata;
    int finds=0,range_finds=0,refreshes=0,tracks=0;
    std::function<void()> on_find;
    std::vector<std::function<void()>> retired;
    bool BindingMemoEnabled() const;
    u64 RegistryGeneration() const noexcept {return registry_generation.load(std::memory_order_acquire);}
    u64 MemoImageUid(ImageId);
    bool TryMemoImage(ImageId,u64,u64);
    bool IsStructuralImageMiss(VAddr,u64,u64);
    void RegisterImage(ImageId);void UnregisterImage(ImageId);void TouchImage(const Image&);
    void FreeImage(ImageId);
    void TrackImage(ImageId){++tracks;}
    void UntrackImage(ImageId){}
    void RefreshImage(Image& image){++refreshes;image.flags&=~ImageFlagBits::Dirty;}
    void UpdateImage(ImageId);
    ImageView& FindTexture(ImageId,const ImageDesc&);
    void DeleteImage(ImageId id){retired.push_back([this,id]{slot_images.items.erase(id);});}
    void Retire(){for(auto& fn:retired)fn();retired.clear();}
    template<class Fn>void ForEachPage(VAddr address,u64,Fn fn){fn(address>>12);}
    template<class Fn>void ForEachImageInRegion(VAddr address,u64 size,Fn fn){
        for(auto&[id,image]:slot_images.items)
            if((image.flags&ImageFlagBits::Registered)&&image.info.guest_address<address+size&&
               address<image.info.guest_address+image.info.guest_size)fn(id,image);
    }
    ImageId Add(VAddr address,ImageId id=0){
        if(!id)id=slot_images.items.empty()?1:slot_images.items.rbegin()->first+1;
        Image image;image.info.guest_address=address;image.image_uid=next_uid++;
        slot_images.items[id]=image;RegisterImage(id);return id;
    }
    ImageId FindImage(ImageDesc& desc){
        ++finds;if(on_find){auto fn=std::move(on_find);on_find={};fn();}
        ImageId id=0;
        for(auto&[candidate,image]:slot_images.items)
            if((image.flags&ImageFlagBits::Registered)&&image.info.guest_address==desc.info.guest_address){id=candidate;break;}
        if(!id)id=Add(desc.info.guest_address);
        desc.view_info.mip=7;desc.view_info.layer=3;
        auto& image=slot_images[id];image.tick_accessed_last=scheduler.CurrentTick();TouchImage(image);
        return id;
    }
    ImageId FindImageFromRange(VAddr address,u64 size){
        ++range_finds;std::vector<ImageId> matches;
        ForEachImageInRegion(address,size,[&](ImageId id,Image& image){
            if(image.info.guest_address==address&&image.SafeToDownload())matches.push_back(id);
        });
        if(matches.size()==1)return matches[0];
        for(auto id:matches)if(slot_images[id].info.guest_size==size)return id;
        return {};
    }
};
struct BufferCache {
    TextureCache& texture_cache;
    struct ImageMiss {VAddr address=0;u32 size=0;u64 generation=~0ull;};
    std::array<ImageMiss,256> image_miss_cache{};
    ImageId FindImageForTexelBuffer(VAddr,u32);
};
}
namespace Vulkan {
class Rasterizer {
public:
    VideoCore::TextureCache& texture_cache;
    explicit Rasterizer(VideoCore::TextureCache& cache):texture_cache(cache){}
__RASTER_MEMBERS__
};
}
'''

CASES = r'''
using namespace VideoCore;
AmdGpu::Image sharp(VAddr address,u64 salt=0){return {{address,salt,salt+2,salt+3}};}
int main(int argc,char** argv){
    if(argc>1)Common::ElfInfo::Instance().serial=argv[1];
    TextureCache cache;auto raster=std::make_unique<Vulkan::Rasterizer>(cache);
    // The same core process can move between titles. Only the environment
    // override may be static; a previous title must not freeze the policy.
    const auto selected_serial=Common::ElfInfo::Instance().serial;
    const char* override_value=std::getenv("BACHATA_ORDER_TEXTURE_MEMO");
    const bool configured=!override_value||std::atoi(override_value)!=0;
    for(const char* serial:{"CUSA00000","CUSA00785","CUSA08809","CUSA00785"}){
        Common::ElfInfo::Instance().serial=serial;
        assert(cache.BindingMemoEnabled()==(configured&&std::string(serial)=="CUSA00785"));
    }
    Common::ElfInfo::Instance().serial=selected_serial;
    BufferCache buffers{cache};Shader::ImageResource res;auto t=sharp(0x10000);
    const auto bind=[&](const AmdGpu::Image& tex,const Shader::ImageResource& resource){
        auto desc=raster->CachedImageDesc(tex,resource);
        auto id=raster->FindBoundImage(tex,resource,desc);
        assert(desc.view_info.mip==7&&desc.view_info.layer==3);
        cache.FindTexture(id,desc);return id;
    };
    if(!cache.BindingMemoEnabled()){
        bind(t,res);const auto before=cache.finds;bind(t,res);bind(t,res);
        assert(cache.finds==before+2);
        buffers.FindImageForTexelBuffer(0x90000,64);auto ranges=cache.range_finds;
        buffers.FindImageForTexelBuffer(0x90000,64);assert(cache.range_finds==ranges+1);
        std::cout<<"TEXTURE_MEMO_DISABLED_POLICY_PASS\n";return 0;
    }
    const auto id=bind(t,res);bind(t,res);const auto lookups=cache.finds;
    const auto builds=TextureCache::ImageDesc::builds;
    const auto refreshes=cache.refreshes,touches=cache.lru_cache.touches;
    cache.scheduler.tick=99;cache.gc_tick=20;bind(t,res);
    assert(cache.finds==lookups&&TextureCache::ImageDesc::builds==builds);
    assert(cache.refreshes==refreshes+1&&cache.lru_cache.touches>touches);
    assert(cache.slot_images[id].tick_accessed_last==99&&cache.lru_cache.last_tick==20);
    // Every raw T# word and every resource flag contributes to the full key.
    for(u32 flags=0;flags<8;++flags){
        Shader::ImageResource varied;varied.is_written=flags&1;varied.is_depth=flags&2;varied.is_array=flags&4;
        auto desc=raster->CachedImageDesc(t,varied);assert(desc.flags==flags);
    }
    for(u32 word=0;word<4;++word){auto changed=t;++changed.words[word];
        auto before=TextureCache::ImageDesc::builds;raster->CachedImageDesc(changed,res);
        assert(TextureCache::ImageDesc::builds==before+1);
    }
    // Storage side effects/refreshes still execute on hits.
    res.is_written=true;bind(t,res);bind(t,res);
    auto writes=cache.surface_metadata.writes;auto views=cache.slot_images[id].view_calls;
    bind(t,res);assert(cache.surface_metadata.writes==writes+1);
    assert(cache.slot_images[id].view_calls==views+1&&cache.download_images.contains(id));
    res.is_written=false;
    // Mip override lookups retain their original slow path.
    res.mip_fallback_mode=Shader::MipStorageFallbackMode::ConstantIndex;
    auto before=cache.finds;bind(t,res);bind(t,res);assert(cache.finds==before+2);
    res.mip_fallback_mode=Shader::MipStorageFallbackMode::DynamicIndex;
    before=cache.finds;bind(t,res);bind(t,res);assert(cache.finds==before+2);
    res.mip_fallback_mode=Shader::MipStorageFallbackMode::None;
    bind(t,res);bind(t,res);
    auto generation=cache.RegistryGeneration(),uid=cache.MemoImageUid(id);
    assert(cache.TryMemoImage(id,uid,generation));
    cache.slot_images[id].binding.needs_rebind=true;
    before=cache.finds;bind(t,res);assert(cache.finds==before+1);
    assert(!cache.TryMemoImage(id,uid,generation));
    cache.slot_images[id].binding.needs_rebind=false;
    cache.slot_images[id].image_uid+=0x10000000;assert(!cache.TryMemoImage(id,uid,generation));
    bind(t,res);bind(t,res);
    // Free invalidates immediately, while the slot remains allocated until retirement.
    generation=cache.RegistryGeneration();uid=cache.MemoImageUid(id);
    cache.FreeImage(id);assert(cache.RegistryGeneration()==generation+1);
    assert(cache.slot_images.IsAllocated(id)&&!cache.TryMemoImage(id,uid,generation));
    cache.Retire();assert(!cache.slot_images.IsAllocated(id));
    const auto recycled=cache.Add(t.words[0],id);assert(recycled==id);
    assert(!cache.TryMemoImage(id,uid,cache.RegistryGeneration()));
    bind(t,res);bind(t,res);
    // Registration during FindImage does not stamp the pre-lookup generation.
    auto other=sharp(0x20000);cache.on_find=[&]{cache.Add(0x40000);};
    bind(other,res);before=cache.finds;bind(other,res);assert(cache.finds==before+1);
    before=cache.finds;bind(other,res);assert(cache.finds==before);
    // Descriptor values held by earlier bindings survive many cache replacements.
    auto owned=raster->CachedImageDesc(t,res);auto owned_address=owned.info.guest_address;
    for(u64 i=0;i<10000;++i)raster->CachedImageDesc(sharp(0x100000+i*64,i),res);
    assert(owned.info.guest_address==owned_address);
    // Target key contains all provided register blocks; last/global memo both hit.
    TextureCache::ImageDesc target;int descriptions=0;u32 tag=1,reg=12,hint=44;
    auto make=[&]{++descriptions;target.info.guest_address=0x80000;};
    auto target_id=raster->FindTargetMemoized(target,raster->last_targets[0],make,tag,reg,hint);
    raster->FindTargetMemoized(target,raster->last_targets[0],make,tag,reg,hint);
    before=cache.finds;auto old_descriptions=descriptions;target.view_info.mip=0;
    assert(raster->FindTargetMemoized(target,raster->last_targets[0],make,tag,reg,hint)==target_id);
    assert(cache.finds==before&&descriptions==old_descriptions&&target.view_info.mip==7);
    raster->last_targets[0]={};
    raster->FindTargetMemoized(target,raster->last_targets[0],make,tag,reg,hint);
    assert(cache.finds==before&&descriptions==old_descriptions);
    ++hint;raster->FindTargetMemoized(target,raster->last_targets[0],make,tag,reg,hint);
    assert(cache.finds==before+1);before=cache.finds;
    ++tag;raster->FindTargetMemoized(target,raster->last_targets[0],make,tag,reg,hint);
    assert(cache.finds==before+1);
    // Negative range memo caches structural absence, never readiness/ambiguity.
    assert(!buffers.FindImageForTexelBuffer(0x90000,64));auto ranges=cache.range_finds;
    assert(!buffers.FindImageForTexelBuffer(0x90000,64)&&cache.range_finds==ranges);
    const auto delayed=cache.Add(0x90000);
    assert(!buffers.FindImageForTexelBuffer(0x90000,64));ranges=cache.range_finds;
    cache.slot_images[delayed].flags|=ImageFlagBits::GpuModified;
    assert(buffers.FindImageForTexelBuffer(0x90000,64)==delayed&&cache.range_finds==ranges+1);
    cache.slot_images[delayed].flags|=ImageFlagBits::Dirty;
    assert(!buffers.FindImageForTexelBuffer(0x90000,64));ranges=cache.range_finds;
    cache.slot_images[delayed].flags&=~ImageFlagBits::Dirty;
    assert(buffers.FindImageForTexelBuffer(0x90000,64)==delayed&&cache.range_finds==ranges+1);
    const auto twin=cache.Add(0x90000);cache.slot_images[twin].flags|=ImageFlagBits::GpuModified;
    assert(!buffers.FindImageForTexelBuffer(0x90000,32));ranges=cache.range_finds;
    cache.slot_images[twin].flags|=ImageFlagBits::Dirty;
    assert(buffers.FindImageForTexelBuffer(0x90000,32)==delayed&&cache.range_finds==ranges+1);
    assert(!cache.IsStructuralImageMiss(0xa0000,64,cache.RegistryGeneration()-1));
    std::cout<<"TEXTURE_BINDING_MEMO_REAL_METHODS_PASS\n";
}
'''


def run(root):
    tc = (root/'src/video_core/texture_cache/texture_cache.cpp').read_text()
    th = (root/'src/video_core/texture_cache/texture_cache.h').read_text()
    rc = (root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp').read_text()
    rh = (root/'src/video_core/renderer_vulkan/vk_rasterizer.h').read_text()
    bc = (root/'src/video_core/buffer_cache/buffer_cache.cpp').read_text()
    members = rh[rh.index('    // Runtime-only caches:'):rh.index('    using ImageBindingInfo =')]
    preamble = PREAMBLE
    if 'void RegisterAlias(ImageId image_id);' in th:
        # This fixture has no same-address image groups. The alias gate executes
        # the real authority/copy protocol; retain real registry/memo bodies here.
        preamble = preamble.replace('    void RegisterImage(ImageId);',
            '    void RegisterAlias(ImageId){}\n'
            '    void SynchronizeAlias(ImageId){}\n'
            '    void PublishAliasWrite(ImageId){}\n'
            '    void RegisterImage(ImageId);', 1)
    if 'BACHATA_ORDER_TEXTURE_VIEW_MEMO_V1' in th:
        # This gate exercises the lookup family with no view-memo argument.
        # The separate view-memo gate compiles its real backing/view protocol.
        preamble = preamble.replace('namespace VideoCore {',
            'namespace VideoCore {\nbool OrderDescriptorViewMemoEnabled(){return true;}', 1)
        preamble = preamble.replace('    ImageView& FindTexture(ImageId,const ImageDesc&);',
            '    struct ViewMemo {};\n'
            '    ImageView* TryViewMemo(ImageId,const ImageViewInfo&,const ViewMemo&) {assert(false);return nullptr;}\n'
            '    void RememberViewMemo(ImageId,const ImageViewInfo&,const ImageView&,ViewMemo&) {assert(false);}\n'
            '    ImageView& FindTexture(ImageId,const ImageDesc&,ViewMemo* memo=nullptr);')
    code = preamble.replace('__RASTER_MEMBERS__',members)
    prepared = root / 'src/shader_recompiler/bachata_prepared_sharps.h'
    if prepared.is_file():
        code = '#include "' + str(prepared.resolve()) + '"\n' + code
        code = code.replace('namespace VideoCore {', 'namespace Shader { struct Info { std::vector<ImageResource> images; BachataPreparedSharps::Stage<AmdGpu::Image,AmdGpu::Image,AmdGpu::Image> order_sharps; }; }\nnamespace VideoCore {', 1)
    code += '\nnamespace VideoCore {\n'
    for signature in ('bool TextureCache::BindingMemoEnabled()', 'u64 TextureCache::MemoImageUid(',
                      'bool TextureCache::TryMemoImage(', 'bool TextureCache::IsStructuralImageMiss(',
                      'void TextureCache::RegisterImage(', 'void TextureCache::UnregisterImage(',
                      'void TextureCache::TouchImage(', 'ImageView& TextureCache::FindTexture('):
        code += method(tc,signature)+'\n'
    for signature in ('void UpdateImage(', 'void FreeImage('):
        body = method(th,signature).replace('void ', 'void TextureCache::',1)
        code += body+'\n'
    code += method(bc,'ImageId BufferCache::FindImageForTexelBuffer(')+'\n}\nnamespace Vulkan {\n'
    for signature in ('Rasterizer::ImageDescCacheEntry& Rasterizer::CachedImageDescEntry(',
                      'VideoCore::TextureCache::ImageDesc Rasterizer::CachedImageDesc(',
                      'VideoCore::ImageId Rasterizer::FindBoundImage(',
                      'template <typename MakeDesc, typename... Parts>\nVideoCore::ImageId Rasterizer::FindTargetMemoized('):
        code += method(rc,signature)+'\n'
    code += '\n}\n'+CASES
    with tempfile.TemporaryDirectory(prefix='order-texture-memo-') as temp:
        temp=Path(temp);source=temp/'test.cpp';source.write_text(code);binary=temp/'test'
        subprocess.run(['c++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-pthread',
                        str(source),'-o',str(binary)],check=True)
        environment=dict(os.environ);environment.pop('BACHATA_ORDER_TEXTURE_MEMO',None)
        subprocess.run([str(binary)],check=True,env=environment)
        subprocess.run([str(binary),'CUSA08809'],check=True,env=environment)
        environment['BACHATA_ORDER_TEXTURE_MEMO']='0'
        subprocess.run([str(binary)],check=True,env=environment)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True,help='effective source tree after all overlays')
    args=parser.parse_args()
    run(args.source)
