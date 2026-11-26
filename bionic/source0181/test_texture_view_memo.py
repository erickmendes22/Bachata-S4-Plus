#!/usr/bin/env python3
"""Compile effective view lookup methods, identities and slot retirement.

Vulkan creation/conversion is a deterministic fixture. Image::FindView, view
keys, backing members, UID providers, SlotVector, FindTexture, registry/retire
methods and descriptor token methods come from --source. Counts demonstrate
avoided searches; they are not a device FPS benchmark.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


def strip_includes(source):
    return re.sub(r'^\s*#(?:include|pragma)[^\n]*\n', '', source, flags=re.M)


def function(source, signature):
    assert source.count(signature) == 1, signature
    begin = source.index(signature)
    index = source.index('{', begin) + 1
    depth, state = 1, ''
    while depth:
        char = source[index]
        if state == 'line':
            if char == '\n': state = ''
        elif state == 'block':
            if source[index:index + 2] == '*/': state = ''; index += 1
        elif state in ('"', "'"):
            if char == '\\': index += 1
            elif char == state: state = ''
        elif source[index:index + 2] == '//': state = 'line'; index += 1
        elif source[index:index + 2] == '/*': state = 'block'; index += 1
        elif char in ('"', "'"): state = char
        elif char == '{': depth += 1
        elif char == '}': depth -= 1
        index += 1
    return source[begin:index]


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <compare>
#include <cstddef>
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
#include <ranges>
#include <set>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define DEBUG_ASSERT(x) assert(x)
#define TEST_ORDER_MEMO __ORDER__
__COMMON__
namespace Common {
void* ReserveMemoryPages(std::size_t size) noexcept {return std::calloc(1,size);}
void CommitMemoryPages(void*,std::size_t) noexcept {}
void ReleaseMemoryPages(void* base,std::size_t) noexcept {std::free(base);}
struct ElfInfo {
    std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo info;return info;}
    const std::string& GameSerial()const{return serial;}
};
}
namespace boost::container {template<class T,std::size_t>using small_vector=std::vector<T>;}
namespace AmdGpu {
enum class ImageType {Color2D,Color3D,Color2DArray};
struct Image {std::array<u64,4> words{};};
struct ColorBuffer;struct DepthBuffer;struct DepthView;struct DepthControl;
}
namespace Shader {
enum class MipStorageFallbackMode {None,ConstantIndex,DynamicIndex};
struct ImageResource {bool is_written=false,is_depth=false,is_array=false;
    MipStorageFallbackMode mip_fallback_mode=MipStorageFallbackMode::None;};
}
namespace vk {
enum class Format {eR8G8B8A8Unorm,eR8G8B8A8Srgb};
struct ComponentMapping {
    u32 r=0,g=1,b=2,a=3;
    static inline u64 comparisons=0;
    bool operator==(const ComponentMapping& other)const{
        ++comparisons;return r==other.r&&g==other.g&&b==other.b&&a==other.a;
    }
    auto operator<=>(const ComponentMapping&)const=default;
};
using UniqueImageView=u64;
}
struct CheckedMutex {
    bool held=false;
    void lock(){assert(!held);held=true;}
    void unlock(){assert(held);held=false;}
};
namespace VideoCore {struct Image;}
namespace Vulkan {
struct Instance{};
struct Runtime {
    Instance instance;u32 conversions=0;
    const Instance& GetInstance()const{return instance;}
    void SetBackingSamples(VideoCore::Image*,u32);
};
}
__POLICY__
namespace VideoCore {
__FLAGS__
__VIEW_INFO__;
__VIEW__;
struct UniqueImage {u64 handle=0;};
struct ImageInfo {
    u32 num_samples=1;VAddr guest_address=0x10000;u32 guest_size=4096;
    struct {bool is_tiled=false;}props;
    struct {u32 width=32;}size;
    struct {VAddr cmask_addr=0,fmask_addr=0,htile_addr=0;}meta_info;
};
struct Image {
    static Common::IncrementalIdProvider<u64> global_image_uid;
    __BACKING_UID_DECL__
    struct State{};
    __BACKING__;
    std::deque<BackingImage> backing_images;
    BackingImage* backing=nullptr;
    Vulkan::Runtime* runtime;
    Common::SlotVector<ImageView>* slot_image_views;
    ImageInfo info;
    u64 image_uid=global_image_uid.Next(),lru_id=0,tick_accessed_last=0;
    ImageFlagBits flags=ImageFlagBits::CpuDirty;
    struct {bool needs_rebind=false,is_bound=false,is_target=false,force_general=false;}binding;
    u32 tracks=0,refreshes=0,uploads=0;
    Image(Vulkan::Runtime& rt,Common::SlotVector<ImageView>& views,VAddr address)
        :runtime(&rt),slot_image_views(&views){
        info.guest_address=address;backing=&backing_images.emplace_back();backing->num_samples=1;
    }
    bool IsTracked()const{return false;}
    ImageView& FindView(const ImageViewInfo&,bool ensure_guest_samples=true);
};
Common::IncrementalIdProvider<u64> Image::global_image_uid{};
__BACKING_UID_DEF__
__VIEW_UID_DEF__
static u64 next_view_handle=0;
ImageView::ImageView(const Vulkan::Instance&,const ImageViewInfo& requested,const Image&)
    :info(requested),image_view(++next_view_handle){}
ImageView::~ImageView()=default;
__FIND_VIEW__
}
void Vulkan::Runtime::SetBackingSamples(VideoCore::Image* image,u32 samples){
    ++conversions;
    auto found=std::ranges::find(image->backing_images,samples,&VideoCore::Image::BackingImage::num_samples);
    if(found==image->backing_images.end()){
        image->backing=&image->backing_images.emplace_back();image->backing->num_samples=samples;
    }else image->backing=&*found;
}
namespace VideoCore {
struct PageTable {
    std::map<u64,std::vector<ImageId>> entries;
    auto& operator[](u64 page){return entries[page];}
    auto* find(u64 page){auto it=entries.find(page);return it==entries.end()?nullptr:&it->second;}
};
struct Lru {
    u64 touches=0;
    u64 Insert(ImageId id,u64){return id.index;}
    void Free(u64){}
    void Touch(u64,u64){++touches;}
};
struct Scheduler {
    std::deque<std::function<void()>> pending;
    void DeferOperation(std::function<void()> fn){pending.push_back(std::move(fn));}
    void Finish(){while(!pending.empty()){auto fn=std::move(pending.front());pending.pop_front();fn();}}
};
struct TextureCache {
    enum class BindingType {Texture,Storage,RenderTarget,DepthTarget};
    struct ImageDesc {
        ImageInfo info;ImageViewInfo view_info;BindingType type=BindingType::Texture;
        ImageDesc()=default;
        ImageDesc(const AmdGpu::Image& sharp,const Shader::ImageResource& res){
            info.guest_address=sharp.words[0];view_info.min_lod=sharp.words[1];
            view_info.is_storage=res.is_written;type=res.is_written?BindingType::Storage:BindingType::Texture;
        }
    };
    Common::SlotVector<ImageView> slot_image_views{4096};
    Common::SlotVector<Image> slot_images{32};
    Vulkan::Runtime runtime;CheckedMutex mutex,download_images_mutex;
    PageTable page_table;Lru lru_cache;Scheduler scheduler;
    std::atomic<u64> registry_generation{0};u64 total_used_memory=0,gc_tick=1;
    bool readback_linear_images=true;
    std::set<ImageId> download_images;
    struct {u64 writes=0;void Write(VAddr,u64){++writes;}}surface_metadata;
    std::function<void()> on_refresh;
    bool BindingMemoEnabled()const{
        const char* env=std::getenv("BACHATA_ORDER_TEXTURE_MEMO");
        return (!env||env[0]!='0')&&Common::ElfInfo::Instance().GameSerial()=="CUSA00785";
    }
    ImageId Add(VAddr address=0x10000){
        auto id=slot_images.Insert(runtime,slot_image_views,address);
#if TEST_ORDER_MEMO
        RegisterImage(id);
#else
        slot_images[id].flags|=ImageFlagBits::Registered;
#endif
        return id;
    }
    void TrackImage(ImageId id){++slot_images[id].tracks;}
    void UntrackImage(ImageId){}
    void TouchImage(const Image& image){lru_cache.Touch(image.lru_id,gc_tick);}
    void RefreshImage(Image& image){
        ++image.refreshes;if(True(image.flags&ImageFlagBits::Dirty))++image.uploads;
        image.flags&=~ImageFlagBits::Dirty;
        if(on_refresh){auto fn=std::move(on_refresh);on_refresh={};fn();}
    }
    void CancelImageReadbacks(VAddr,u64){}
    void UnregisterMeta(VAddr,u64){}
    template<class F>void ForEachPage(VAddr address,u64 size,F fn){
        for(u64 page=address>>20;page<=((address+size-1)>>20);++page)fn(page);
    }
#if TEST_ORDER_MEMO
    __VIEW_MEMO__;
    ImageView* TryViewMemo(ImageId,const ImageViewInfo&,const ViewMemo&);
    void RememberViewMemo(ImageId,const ImageViewInfo&,const ImageView&,ViewMemo&);
    ImageView& FindTexture(ImageId,const ImageDesc&,ViewMemo* memo=nullptr);
    __UPDATE_IMAGE__
    void RegisterImage(ImageId);void UnregisterImage(ImageId);void DeleteImage(ImageId);
    __FREE_IMAGE__
#endif
};
__TEXTURE_METHODS__
}
#if TEST_ORDER_MEMO
namespace Vulkan {
struct Rasterizer {
    VideoCore::TextureCache& texture_cache;
    explicit Rasterizer(VideoCore::TextureCache& cache):texture_cache(cache){}
    __DESC_ENTRY__;
    using ImageDescMemo=std::array<ImageDescCacheEntry,4096>;
    std::unique_ptr<ImageDescMemo> image_desc_cache;
    u64 desc_use_counter=0;
    ImageDescCacheEntry& CachedImageDescEntry(const AmdGpu::Image&,const Shader::ImageResource&);
    std::vector<std::pair<VideoCore::ImageId,VideoCore::TextureCache::ImageDesc>> image_bindings;
    __RASTER_MEMBERS__
};
__RASTER_METHODS__
}
#endif
'''


CASES = r'''
using namespace VideoCore;
static ImageViewInfo View(u32 lod=0){ImageViewInfo info;info.min_lod=lod;return info;}
static void TestLastView(bool enabled){
    TextureCache cache;auto id=cache.Add();auto& image=cache.slot_images[id];
    for(u32 i=0;i<64;++i)image.FindView(View(i));
    image.FindView(View(63));
    const auto views=cache.slot_image_views.Size();
    vk::ComponentMapping::comparisons=0;
    for(u32 i=0;i<4096;++i)assert(image.FindView(View(63)).info.min_lod==63);
    assert(vk::ComponentMapping::comparisons==(enabled?4096:4096*64));
    assert(cache.slot_image_views.Size()==views);
}
static void TestCompleteViewKey(){
    TextureCache cache;auto id=cache.Add();auto& image=cache.slot_images[id];
    const auto base=View();const auto original=image.FindView(base).image_view;
    std::vector<ImageViewInfo> changed;
    auto add=[&](auto fn){auto next=base;fn(next);changed.push_back(next);};
    add([](auto& v){v.type=AmdGpu::ImageType::Color3D;});
    add([](auto& v){v.format=vk::Format::eR8G8B8A8Srgb;});
    add([](auto& v){++v.range.base.level;});add([](auto& v){++v.range.base.layer;});
    add([](auto& v){++v.range.extent.levels;});add([](auto& v){++v.range.extent.layers;});
    add([](auto& v){++v.mapping.r;});add([](auto& v){++v.mapping.g;});
    add([](auto& v){++v.mapping.b;});add([](auto& v){++v.mapping.a;});
    add([](auto& v){++v.min_lod;});add([](auto& v){v.is_storage=true;});
    for(const auto& next:changed){
        auto& view=image.FindView(next);assert(view.info==next&&view.image_view!=original);
        assert(image.FindView(next).image_view==view.image_view);
    }
    assert(image.FindView(base).image_view==original);
}
static void TestBackingSamples(){
    TextureCache cache;auto id=cache.Add();auto& image=cache.slot_images[id];
    const auto requested=View();const auto single=image.FindView(requested).image_view;
    auto* original=image.backing;image.info.num_samples=4;
    const auto ms=image.FindView(requested).image_view;
    assert(ms!=single&&image.backing!=original&&image.backing->num_samples==4);
    assert(cache.runtime.conversions==1);
    image.backing=original; // render-target path may intentionally use this backing
    assert(image.FindView(requested,false).image_view==single);
    assert(cache.runtime.conversions==1);
    assert(image.FindView(requested,true).image_view==ms&&cache.runtime.conversions==2);
}
#if TEST_ORDER_MEMO
static TextureCache::ViewMemo Warm(TextureCache& cache,ImageId id,TextureCache::ImageDesc desc={}){
    TextureCache::ViewMemo memo;cache.FindTexture(id,desc,&memo);
    assert(memo.image_id==id&&memo.view_id&&memo.image_uid&&memo.backing_uid&&memo.view_uid);
    return memo;
}
static void TestDescriptorHitsAndEffects(){
    TextureCache cache;auto id=cache.Add();auto& image=cache.slot_images[id];
    for(u32 i=0;i<64;++i)image.FindView(View(i));
    std::array<TextureCache::ImageDesc,2> descs;
    for(u32 i=0;i<2;++i){descs[i].view_info=View(62+i);descs[i].type=TextureCache::BindingType::Storage;}
    std::array<TextureCache::ViewMemo,2> memos{Warm(cache,id,descs[0]),Warm(cache,id,descs[1])};
    const auto uploads=image.uploads,refreshes=image.refreshes,tracks=image.tracks;
    const auto writes=cache.surface_metadata.writes,views=cache.slot_image_views.Size();
    vk::ComponentMapping::comparisons=0;
    image.flags|=ImageFlagBits::CpuDirty;
    for(u32 i=0;i<4096;++i){
        auto& view=cache.FindTexture(id,descs[i%2],&memos[i%2]);
        assert(view.info.min_lod==62+i%2);
    }
    // A complete key comparison per hit replaces the linear view-array scan.
    assert(vk::ComponentMapping::comparisons==4096);
    assert(image.uploads==uploads+1&&image.refreshes==refreshes+4096&&image.tracks==tracks+4096);
    assert(cache.surface_metadata.writes==writes+4096&&cache.download_images.contains(id));
    assert(cache.slot_image_views.Size()==views);
    auto changed=descs[0].view_info;changed.min_lod=3;
    assert(!cache.TryViewMemo(id,changed,memos[0]));
    auto wrong_image=memos[0];++wrong_image.image_uid;
    assert(!cache.TryViewMemo(id,descs[0].view_info,wrong_image));
    image.binding.needs_rebind=true;
    assert(!cache.TryViewMemo(id,descs[0].view_info,memos[0]));
    image.binding.needs_rebind=false;
}
static void TestViewSlotReuse(){
    TextureCache cache;auto id=cache.Add();TextureCache::ImageDesc desc;auto memo=Warm(cache,id,desc);
    auto& image=cache.slot_images[id];const auto slot=memo.view_id;
    cache.slot_image_views.Erase(slot);
    assert(!cache.TryViewMemo(id,desc.view_info,memo));
    auto replacement=View(99);
    const auto recycled=cache.slot_image_views.Insert(cache.runtime.GetInstance(),replacement,image);
    assert(recycled==slot&&cache.slot_image_views[recycled].view_uid!=memo.view_uid);
    image.backing->image_view_infos[image.backing->last_view]=replacement;
    assert(!cache.TryViewMemo(id,desc.view_info,memo));
    auto& actual=cache.FindTexture(id,desc,&memo);
    assert(actual.info==desc.view_info&&memo.view_id!=recycled);
}
static void TestBackingRecreatedAtSameAddress(){
    TextureCache cache;auto id=cache.Add();TextureCache::ImageDesc desc;auto memo=Warm(cache,id,desc);
    auto& image=cache.slot_images[id];auto* backing=image.backing;
    const auto old_uid=backing->backing_uid;
    for(auto view:backing->image_view_ids)cache.slot_image_views.Erase(view);
    std::destroy_at(backing);std::construct_at(backing);backing->num_samples=1;
    assert(image.backing==backing&&backing->backing_uid!=old_uid);
    auto& fresh=image.FindView(desc.view_info);
    // Even if every other key and the recycled view slot match, a new backing
    // at the same address cannot inherit the old allocation's memo.
    memo.view_id=backing->image_view_ids.back();memo.view_uid=fresh.view_uid;
    assert(!cache.TryViewMemo(id,desc.view_info,memo));
    cache.FindTexture(id,desc,&memo);
    assert(memo.backing==backing&&memo.backing_uid==backing->backing_uid);
}
static void TestDescriptorMsaaAndRefresh(){
    TextureCache cache;auto id=cache.Add();TextureCache::ImageDesc desc;auto memo=Warm(cache,id,desc);
    auto& image=cache.slot_images[id];const auto single=memo.view_id;auto* old=image.backing;
    image.info.num_samples=4;
    assert(!cache.TryViewMemo(id,desc.view_info,memo));
    auto& ms=cache.FindTexture(id,desc,&memo);
    assert(image.backing!=old&&memo.backing==image.backing&&memo.view_id!=single);
    assert(memo.view_uid==ms.view_uid&&cache.runtime.conversions==1);
    image.info.num_samples=1;
    cache.on_refresh=[&]{image.backing=old;};
    auto& restored=cache.FindTexture(id,desc,&memo);
    assert(memo.backing==old&&memo.view_id==single&&memo.view_uid==restored.view_uid);
}
static void TestDeferredRetirement(){
    TextureCache cache;auto id=cache.Add();TextureCache::ImageDesc desc;auto memo=Warm(cache,id,desc);
    const auto view=memo.view_id;const auto uid=memo.image_uid;
    cache.FreeImage(id);
    assert(cache.slot_images.IsAllocated(id)&&cache.slot_image_views.IsAllocated(view));
    assert(!cache.TryViewMemo(id,desc.view_info,memo));
    cache.scheduler.Finish();
    assert(!cache.slot_images.IsAllocated(id)&&!cache.slot_image_views.IsAllocated(view));
    assert(!cache.TryViewMemo(id,desc.view_info,memo));
    const auto recycled=cache.Add();assert(recycled==id&&cache.slot_images[id].image_uid!=uid);
    auto newer=Warm(cache,recycled,desc);newer.image_uid=uid;
    assert(!cache.TryViewMemo(recycled,desc.view_info,newer));
}
static AmdGpu::Image Sharp(u64 salt=0){return {{0x10000,salt,2,3}};}
static void TestDescriptorOwnership(){
    TextureCache cache;auto id=cache.Add();Vulkan::Rasterizer raster(cache);
    Shader::ImageResource res;TextureCache::ImageDesc desc;
    raster.image_bindings.emplace_back(id,desc);
    raster.RememberImageViewToken(Sharp(),res);
    auto token=raster.image_view_memo_tokens.back();assert(raster.IsViewMemoTokenCurrent(token));
    raster.FindTextureWithViewMemo(id,desc,token);
    assert((*raster.descriptor_view_memos)[token.index].view_id);
    // Real cache replacement, not a fake borrowed pointer invalidation.
    for(u32 i=1;i<20000&&raster.IsViewMemoTokenCurrent(token);++i)
        raster.CachedImageDescEntry(Sharp(i),res);
    assert(!raster.IsViewMemoTokenCurrent(token));
    auto& old_slot=(*raster.descriptor_view_memos)[token.index];
    old_slot.image_uid=0xfeed;
    raster.FindTextureWithViewMemo(id,desc,token);
    assert(old_slot.image_uid==0xfeed);

    raster.RememberImageViewToken(Sharp(),res);token=raster.image_view_memo_tokens.back();
    raster.FindTextureWithViewMemo(id,desc,token);
    cache.on_refresh=[&]{
        // Replacement between local-copy and commit must leave the new
        // owner's memo untouched, even if allocation callbacks reenter.
        for(u32 i=30000;i<60000&&raster.IsViewMemoTokenCurrent(token);++i)
            raster.CachedImageDescEntry(Sharp(i),res);
        assert(!raster.IsViewMemoTokenCurrent(token));
        (*raster.descriptor_view_memos)[token.index].image_uid=0xbeef;
    };
    raster.FindTextureWithViewMemo(id,desc,token);
    assert((*raster.descriptor_view_memos)[token.index].image_uid==0xbeef);

    raster.image_view_memo_tokens.clear();raster.image_bindings.clear();
    raster.image_bindings.resize(3);raster.RememberImageViewToken(Sharp(),res);
    assert(!raster.image_view_memo_tokens[0].identity&&!raster.image_view_memo_tokens[1].identity);
    assert(raster.IsViewMemoTokenCurrent(raster.image_view_memo_tokens[2]));
    raster.image_view_memo_tokens.clear();res.mip_fallback_mode=Shader::MipStorageFallbackMode::DynamicIndex;
    raster.RememberImageViewToken(Sharp(),res);assert(raster.image_view_memo_tokens.empty());
}
#endif
int main(int argc,char** argv){
    if(argc>1)Common::ElfInfo::Instance().serial=argv[1];
    const auto serial=Common::ElfInfo::Instance().serial;
    const bool order_setting=!std::getenv("BACHATA_ORDER_TEXTURE_VIEW_MEMO")||std::getenv("BACHATA_ORDER_TEXTURE_VIEW_MEMO")[0]!='0';
    const bool sotc_setting=!std::getenv("SOTC_TEX_BIND_P1")||std::getenv("SOTC_TEX_BIND_P1")[0]!='0';
    for(const char* title:{"CUSA00000","CUSA00785","CUSA08809","CUSA08034","CUSA00000"}){
        Common::ElfInfo::Instance().serial=title;
        const bool expected_order=std::string(title)=="CUSA00785"&&order_setting;
        const bool expected_sotc=(std::string(title)=="CUSA08809"||std::string(title)=="CUSA08034")&&sotc_setting;
        assert(OrderDescriptorViewMemoEnabled()==expected_order);
        assert(ImageLastViewMemoEnabled()==(expected_order||expected_sotc));
    }
    Common::ElfInfo::Instance().serial=serial;
    TestLastView(ImageLastViewMemoEnabled());TestCompleteViewKey();TestBackingSamples();
#if TEST_ORDER_MEMO
    if(OrderDescriptorViewMemoEnabled()){
        TestDescriptorHitsAndEffects();TestViewSlotReuse();TestBackingRecreatedAtSameAddress();
        TestDescriptorMsaaAndRefresh();TestDeferredRetirement();TestDescriptorOwnership();
    }
#endif
    std::cout<<"TEXTURE_VIEW_MEMO_REAL_METHODS_PASS "<<serial<<" last="<<ImageLastViewMemoEnabled()
             <<" descriptor="<<(TEST_ORDER_MEMO&&OrderDescriptorViewMemoEnabled())<<'\n';
}
'''


def program(root):
    src = root / 'src'
    image = (src / 'video_core/texture_cache/image.h').read_text()
    views = (src / 'video_core/texture_cache/image_view.h').read_text()
    cache = (src / 'video_core/texture_cache/texture_cache.cpp').read_text()
    header = (src / 'video_core/texture_cache/texture_cache.h').read_text()
    raster = (src / 'video_core/renderer_vulkan/vk_rasterizer.cpp').read_text()
    raster_h = (src / 'video_core/renderer_vulkan/vk_rasterizer.h').read_text()
    order = 'BACHATA_ORDER_TEXTURE_VIEW_MEMO_V1' in header
    common = '\n'.join(strip_includes((src / name).read_text()) for name in (
        'common/types.h', 'common/enum.h', 'common/alignment.h', 'common/incremental_id.h',
        'common/slot_vector.h', 'video_core/texture_cache/types.h'))
    values = {
        '__ORDER__': '1' if order else '0', '__COMMON__': common,
        '__POLICY__': strip_includes((src / 'video_core/texture_cache/texture_view_memo_policy.h').read_text()),
        '__FLAGS__': image[image.index('enum ImageFlagBits :'):image.index('struct UniqueImage')],
        '__VIEW_INFO__': function(views, 'struct ImageViewInfo {'),
        '__VIEW__': function(views, 'struct ImageView {'),
        '__BACKING__': function(image, '    struct BackingImage {'),
        '__BACKING_UID_DECL__': 'static Common::IncrementalIdProvider<u64> global_backing_uid;' if order else '',
        '__BACKING_UID_DEF__': 'Common::IncrementalIdProvider<u64> Image::global_backing_uid{};' if order else '',
        '__VIEW_UID_DEF__': 'Common::IncrementalIdProvider<u64> ImageView::global_view_uid{};' if order else '',
        '__FIND_VIEW__': function((src / 'video_core/texture_cache/image.cpp').read_text(), 'ImageView& Image::FindView('),
        '__VIEW_MEMO__': function(header, '    struct ViewMemo {') if order else '',
        '__UPDATE_IMAGE__': function(header, '    void UpdateImage(') if order else '',
        '__FREE_IMAGE__': function(header, '    void FreeImage(') if order else '',
        '__TEXTURE_METHODS__': '\n'.join(function(cache, signature) for signature in (
            'ImageView* TextureCache::TryViewMemo(', 'void TextureCache::RememberViewMemo(',
            'ImageView& TextureCache::FindTexture(', 'void TextureCache::RegisterImage(',
            'void TextureCache::UnregisterImage(', 'void TextureCache::DeleteImage(')) if order else '',
        '__DESC_ENTRY__': function(raster_h, '    struct ImageDescCacheEntry {') if order else '',
        '__RASTER_MEMBERS__': '', '__RASTER_METHODS__': '',
    }
    if order:
        first = raster_h.index('    struct ViewMemoToken {')
        last = raster_h.index('ViewMemoToken token);', first) + len('ViewMemoToken token);')
        values['__RASTER_MEMBERS__'] = raster_h[first:last]
        values['__RASTER_METHODS__'] = '\n'.join(function(raster, signature) for signature in (
            'Rasterizer::ImageDescCacheEntry& Rasterizer::CachedImageDescEntry(',
            'void Rasterizer::RememberImageViewToken(', 'bool Rasterizer::IsViewMemoTokenCurrent(',
            'VideoCore::ImageView& Rasterizer::FindTextureWithViewMemo('))
    code = PREAMBLE
    for token, value in values.items():
        assert code.count(token) == 1, token
        code = code.replace(token, value)
    return code + CASES, order


def run(root):
    code, order = program(root)
    with tempfile.TemporaryDirectory(prefix='bachata-texture-view-memo-') as path:
        path = Path(path)

        def build(name, source):
            cpp = path / (name + '.cpp')
            binary = path / name
            cpp.write_text(source)
            subprocess.run(['c++', '-std=c++20', '-O1', '-Wall', '-Wextra', '-Werror',
                '-Wno-parentheses', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                '-pthread', str(cpp), '-o', str(binary)], check=True)
            return binary

        binary = build('effective', code)
        environment = dict(os.environ)
        for key in ('BACHATA_ORDER_TEXTURE_VIEW_MEMO', 'SOTC_TEX_BIND_P1', 'BACHATA_ORDER_TEXTURE_MEMO'):
            environment.pop(key, None)
        for title in ('CUSA00785', 'CUSA08809', 'CUSA08034', 'CUSA00000'):
            subprocess.run([str(binary), title], check=True, env=environment)
        for title, variable in (('CUSA00785', 'BACHATA_ORDER_TEXTURE_VIEW_MEMO'),
                                ('CUSA08809', 'SOTC_TEX_BIND_P1')):
            subprocess.run([str(binary), title], check=True, env={**environment, variable: '0'})

        controls = {
            'last_view': ('if (use_last_view && backing->last_view < view_infos.size() &&',
                          'if (false && use_last_view && backing->last_view < view_infos.size() &&'),
            'sample_conversion': ('if (ensure_guest_samples && backing->num_samples > 1 != info.num_samples > 1)',
                                  'if (false && ensure_guest_samples && backing->num_samples > 1 != info.num_samples > 1)'),
        }
        if order:
            controls.update({
                'backing_uid': ('memo.backing_uid != image.backing->backing_uid ||', 'false ||'),
                'view_uid': ('return view.view_uid == memo.view_uid ? &view : nullptr;', 'return &view;'),
                'registered': ('False(image.flags & ImageFlagBits::Registered) || image.binding.needs_rebind ||',
                               'image.binding.needs_rebind ||'),
                'view_key': ('memo.view_info != view_info || !slot_image_views.IsAllocated(memo.view_id)',
                             '(void(view_info), false) || !slot_image_views.IsAllocated(memo.view_id)'),
                'token_commit': ('if (IsViewMemoTokenCurrent(token)) (*descriptor_view_memos)[token.index] = memo;',
                                 '(*descriptor_view_memos)[token.index] = memo;'),
            })
        for name, (old, replacement) in controls.items():
            assert code.count(old) == 1, name
            mutant = build(name, code.replace(old, replacement, 1))
            result = subprocess.run([str(mutant), 'CUSA00785'], env=environment,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            assert result.returncode != 0, f'negative control unexpectedly passed: {name}'
        print(f'TEXTURE_VIEW_MEMO_NEGATIVE_CONTROLS_PASS {len(controls)}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    run(parser.parse_args().source.resolve())
