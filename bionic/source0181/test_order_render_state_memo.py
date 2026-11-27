#!/usr/bin/env python3
"""Execute the applied render-state memo and the original attachment transaction.

Real methods: Scheduler begin/end/recording, Rasterizer wrapper/full/signature,
TextureCache validation/UpdateImage/FindRenderTarget/FindDepthTarget/metadata,
page dirty invalidation, Image barriers and Runtime transitions. Device storage,
view allocation and uploads are boundary fixtures, not gameplay measurements.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from test_order_readconst_pool import block
import test_order_render_pass_coalescing as coalescing


IMAGE = r'''
struct Image {
    struct State {vk::PipelineStageFlags2 pl_stage=vk::PipelineStageFlagBits2::eAllCommands;
        vk::AccessFlags2 access_mask=vk::AccessFlagBits2::eNone;vk::ImageLayout layout=vk::ImageLayout::eUndefined;};
    struct Backing {u64 backing_uid=1;State state;std::vector<State>subresource_states;
        u32 num_samples=1,last_view=~0u;std::vector<ImageViewId>image_view_ids;
        std::vector<ImageViewInfo>image_view_infos;};
    Backing object;Backing*backing=&object;
    struct Info {
        SubresourceExtent resources{};
        struct{u32 width=2,height=2,depth=1;}size;
        struct{bool has_stencil=true,is_tiled=true,is_depth=false;}props;
        struct{VAddr cmask_addr{},fmask_addr{},htile_addr{};s32 htile_clear_mask=-1;}meta_info;
        VAddr guest_address=0x4000,stencil_addr{};u32 guest_size=4096,stencil_size{},num_samples=1;
        vk::Format pixel_format=vk::Format::eR8G8B8A8Unorm;
    }info;
    struct{bool needs_rebind{},is_bound{},force_general{};}binding;
    struct{bool render_target{},depth_target{};}usage;
    vk::ImageAspectFlags aspect_mask=vk::ImageAspectFlagBits::eColor;
    ImageFlagBits flags=ImageFlagBits::Registered|ImageFlagBits::GpuModified;
    u64 handle=1,image_uid=1,lru_id=1,tick_accessed_last{},hash=1;
    VAddr track_addr=0x4000,track_addr_end=0x5000;
    ImageId depth_id{};u64 depth_uid{};
    ViewSlots*slot_image_views{};
    void AssociateDepth(ImageId id,u64 uid){depth_id=id;depth_uid=uid;}
    vk::Image GetImage()const{return handle;}
    bool IsTracked(){return track_addr&&track_addr_end;}
    bool Overlaps(VAddr a,u64 n)const{return a<info.guest_address+info.guest_size&&info.guest_address<a+n;}
    ImageView&FindView(const ImageViewInfo&,bool);
    using Barriers=std::vector<vk::ImageMemoryBarrier2>;
    void GetBarriers(Barriers&,vk::ImageLayout,vk::AccessFlags2,vk::PipelineStageFlags2,std::optional<SubresourceRange>);
};
'''


SUPPORT = r'''
using ImageId=Common::SlotId;using ImageViewId=Common::SlotId;
@FLAGS@
@VIEW_INFO@;
struct ImageView {
    u64 view_uid=1,handle=1;
    const u64*image_view=&handle;
    ImageViewInfo info;
};
template<class T>struct Slots {
    std::map<Common::SlotId,T>items;u32 next=1;
    T&operator[](Common::SlotId id){return items.at(id);}
    const T&operator[](Common::SlotId id)const{return items.at(id);}
    bool IsAllocated(Common::SlotId id)const{return items.contains(id);}
    void Erase(Common::SlotId id){assert(items.erase(id)==1);}
};
using ViewSlots=Slots<ImageView>;
'''


SUPPORT_AFTER = r'''
struct ObservedMutex {
    std::mutex value;std::function<void()>before_lock;
    void lock(){if(before_lock)before_lock();value.lock();}
    void unlock(){value.unlock();}
};
struct Desc {Image::Info info;ImageViewInfo view_info;};
ImageView&Image::FindView(const ImageViewInfo&v,bool) {
    for(auto id:backing->image_view_ids)
        if((*slot_image_views)[id].info==v)return (*slot_image_views)[id];
    const ImageViewId id{slot_image_views->next++};
    auto[it,inserted]=slot_image_views->items.try_emplace(id);assert(inserted);
    auto&result=it->second;result.handle=handle;result.info=v;result.view_uid=id.index;
    backing->image_view_ids.push_back(id);backing->image_view_infos.push_back(v);
    return result;
}
enum class PageOp{Track,Untrack};
struct PageManager {
    static VAddr GetPageAddr(VAddr a){return a&~u64{4095};}
    static VAddr GetNextPageAddr(VAddr a){return (a+4096)&~u64{4095};}
    u64 tracked{};void UpdatePageWatchers(VAddr,u64,PageOp op){tracked+=op==PageOp::Track;}
};
template<class K,class V>struct Map {
    std::map<K,V>items;
    struct Iter {
        typename std::map<K,V>::iterator it;
        V&value()const{return it->second;}
        bool operator==(const Iter&)const=default;
    };
    Iter find(const K&k){return {items.find(k)};}
    Iter end(){return {items.end()};}
    void emplace(const K&k,const V&v){items.emplace(k,v);}
    void erase(Iter it){items.erase(it.it);}void erase(const K&key){items.erase(key);}
};
'''


CACHE = r'''
struct TextureCache {
    using Image=VideoCore::Image;using ImageId=VideoCore::ImageId;using ImageViewId=VideoCore::ImageViewId;
    using ImageView=VideoCore::ImageView;using ImageViewInfo=VideoCore::ImageViewInfo;
    using ImageFlagBits=VideoCore::ImageFlagBits;using ImageInfo=VideoCore::Image::Info;
    using PageManager=VideoCore::PageManager;using PageOp=VideoCore::PageOp;
    using MetaType=VideoCore::SurfaceMetadata::Type;
    using ImageDesc=VideoCore::Desc;
    struct MetaDataInfo{MetaType type;ImageId owner_id;u64 owner_uid;u32 num_samples=1;
        s32 clear_mask=-1;u32 layers=1;bool stencil=false;};
    VideoCore::Map<VAddr,MetaDataInfo>surface_metas;
    mutable VideoCore::ObservedMutex mutex;
    std::mutex download_images_mutex;
    VideoCore::SurfaceMetadata surface_metadata;
    VideoCore::Slots<Image>slot_images;
    VideoCore::ViewSlots slot_image_views;
    Scheduler&scheduler;
    VideoCore::PageManager tracker;
    struct{u64 touches{};void Touch(u64,u64){++touches;}}lru_cache;
    u64 gc_tick=1,generation=1,updates{},refreshes{},targets{},depth_targets{},new_uid=100;
    bool readback_linear_images=false;
    std::set<ImageId>download_images;
    std::map<ImageId,u32>pending_upload;
    int instance{},runtime{};
    explicit TextureCache(Scheduler&s):scheduler{s}{for(u32 i=1;i<10;++i)Add(i);}
    void Add(u32 id) {
        auto[it,inserted]=slot_images.items.try_emplace(ImageId{id});assert(inserted);
        auto&i=it->second;i.handle=id;i.image_uid=++new_uid;i.object.backing_uid=i.image_uid;
        i.info.guest_address=0x4000+u64{id}*0x2000;i.track_addr=i.info.guest_address;
        i.track_addr_end=i.track_addr+i.info.guest_size;i.slot_image_views=&slot_image_views;
        ++generation;
    }
    Image&GetImage(ImageId id){return slot_images[id];}
    ImageId FindImage(const ImageDesc&){assert(false);return {};}
    u64 RegistryGeneration()const{return generation;}
    bool HasLiveMeta(VAddr a)const{return surface_metadata.TypeAt(a).has_value();}
    bool IsLiveImage(ImageId id,u64 uid)const{return id&&slot_images.IsAllocated(id)&&
        slot_images[id].image_uid==uid&&True(slot_images[id].flags&ImageFlagBits::Registered);}
    void TrackImage(ImageId);
    void TrackImageHead(ImageId);void TrackImageTail(ImageId);
    void UntrackImage(ImageId id){slot_images[id].track_addr=slot_images[id].track_addr_end=0;}
    void UntrackImageHead(ImageId id){MarkAsMaybeDirty(id,slot_images[id]);}
    void UntrackImageTail(ImageId id){MarkAsMaybeDirty(id,slot_images[id]);}
    void MarkAsMaybeDirty(ImageId id,Image&i){i.flags|=ImageFlagBits::MaybeCpuDirty;UntrackImage(id);}
    void InvalidateAlias(Image&){}
    void ResolveImageReadbacks(VAddr,u64,bool){}
    template<class F>void ForEachImageInRegion(VAddr address,u64 size,F f) {
        for(auto&[id,image]:slot_images.items)if(image.Overlaps(address,size))f(id,image);
    }
    void RefreshImage(Image&image) {
        ++updates;
        if(False(image.flags&ImageFlagBits::Dirty))return;
        ++refreshes;
        scheduler.EndRendering(OrderPassEndReason::ImageRefresh);
        if(auto it=pending_upload.find(ImageId{u32(image.handle)});it!=pending_upload.end()) {
            const auto value=it->second;const auto handle=image.handle;
            auto f=[gpu=&scheduler.gpu,value,handle]{for(auto&p:gpu->surfaces[handle])p.color={value,value,value,value};};
            if(scheduler.recorder)scheduler.recorder->Run(f);else f();
            pending_upload.erase(it);
        }
        image.flags&=~ImageFlagBits::Dirty;
    }
    void SynchronizeAlias(ImageId){}
    void PublishAliasWrite(ImageId){}
    void TouchImage(const Image&);
    void RegisterMeta(VAddr,MetaDataInfo);void UnregisterMeta(VAddr,u64);
    ImageView&FindRenderTarget(ImageId,const ImageDesc&);
    ImageView&FindDepthTarget(ImageId,const ImageDesc&);
    void InvalidateMemory(VAddr,size_t);void InvalidateMemoryFromGPU(VAddr,size_t);
    @VIEW_MEMO@;
    @CACHE_API@
    @UPDATE_IMAGE@
    @META_METHODS@
};
'''


TESTS = r'''
using namespace Vulkan;
bool enabled=true,inline_enabled=false;
constexpr u32 N=8192;
void Warm(Rasterizer&r,GraphicsPipeline&p) {
    r.Draw(p,1);r.Draw(p,2);r.Draw(p,3);
    assert(r.order_begin_memo.valid);
}
void ReadOnlyCost(bool deferred,bool active) {
    Rasterizer r{deferred};GraphicsPipeline p;
    for(u32 i=0;i<N;++i)r.Draw(p,i);
    r.scheduler.EndRendering();r.scheduler.Sync();
    assert(r.scheduler.gpu.begins==1&&r.scheduler.gpu.barriers==1);
    assert(r.texture_cache.targets==(active?2:N));
    assert(r.texture_cache.updates==2*r.texture_cache.targets);
    assert(r.scheduler.gpu.surfaces.at(1)[0].color[0]==N-1);
    std::cout<<"ORDER_RENDER_STATE_COST deferred="<<deferred<<" draws="<<N
             <<" full="<<r.texture_cache.targets<<" updates="<<r.texture_cache.updates
             <<" begins="<<r.scheduler.gpu.begins<<" barriers="<<r.scheduler.gpu.barriers<<"\n"<<std::flush;
}
void Rearm(bool deferred,bool depth) {
    Rasterizer r{deferred};GraphicsPipeline p;
    const VAddr address=depth?0x2000:0x1000;
    if(depth){p.key.mrt_mask=0;r.cb_descs[0].first={};r.db_desc.first=5;r.db_desc.second.view_info.is_storage=true;r.db_desc.second.info.meta_info.htile_addr=address;}
    else r.cb_descs[0].second.info.meta_info.cmask_addr=address;
    if(depth)r.cp.regs.depth_htile_data_base.address=address;else r.cp.regs.color_buffers[0].address=address;
    Warm(r,p);
    const auto before=r.texture_cache.updates;
    assert(r.texture_cache.surface_metadata.Clear(address,64));
    bool consumed=false;auto state=r.BeginRendering(&p,consumed);
    assert(consumed&&r.texture_cache.updates>before&&!r.order_begin_memo.valid);
    if(r.needs_barrier)r.runtime.FlushBarriers();
    r.scheduler.BeginRendering(state,consumed);r.scheduler.EndRendering();r.scheduler.Sync();
    assert(depth?r.scheduler.gpu.surfaces.at(5)[0].depth==std::bit_cast<u32>(.25f):
                 r.scheduler.gpu.surfaces.at(1)[0].color[0]==11);
}
void DirtyWrite(bool deferred,bool gpu,bool maybe) {
    Rasterizer r{deferred};GraphicsPipeline p;Warm(r,p);
    auto&i=r.texture_cache.GetImage(1);const auto before=r.texture_cache.updates;
    r.texture_cache.pending_upload[1]=89;
    if(gpu)r.texture_cache.InvalidateMemoryFromGPU(i.info.guest_address,8);
    else r.texture_cache.InvalidateMemory(i.info.guest_address+(maybe?4090:0),maybe?8:4);
    if(maybe)i.flags|=VideoCore::ImageFlagBits::MaybeCpuDirty;
    r.Draw(p,9);r.scheduler.EndRendering();r.scheduler.Sync();
    assert(r.texture_cache.updates>before&&r.texture_cache.refreshes==1);
    assert(r.scheduler.gpu.surfaces.at(1)[1].color[0]==89);
}
void ResourceReject(u32 variant,bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;Warm(r,p);
    auto&i=r.texture_cache.GetImage(1);const auto before=r.texture_cache.updates;
    VideoCore::Image::Backing alternate;
    switch(variant) {
    case 0:++i.image_uid;break;
    case 1:++i.object.backing_uid;break;
    case 2:alternate=i.object;i.backing=&alternate;break;
    case 3:++r.texture_cache.slot_image_views[i.object.image_view_ids[0]].view_uid;break;
    case 4:i.flags|=VideoCore::ImageFlagBits::Aliased;break;
    case 5:i.flags&=~VideoCore::ImageFlagBits::GpuModified;break;
    case 6:i.track_addr_end-=4096;break;
    case 7:++r.texture_cache.generation;break;
    case 8:i.object.state.layout=vk::ImageLayout::eGeneral;break;
    case 9:i.object.state.access_mask=vk::AccessFlagBits2::eShaderWrite;break;
    case 10:i.object.subresource_states={i.object.state};i.object.subresource_states[0].access_mask=vk::AccessFlagBits2::eShaderWrite;break;
    case 11:i.object.num_samples=2;break;
    default:assert(false);
    }
    bool consumed=false;(void)r.BeginRendering(&p,consumed);
    assert(r.texture_cache.updates>before);
    r.scheduler.EndRendering();r.scheduler.Sync();
}
void SignatureReject(u32 variant) {
    Rasterizer r;GraphicsPipeline p;Warm(r,p);const auto before=r.texture_cache.targets;
    switch(variant) {
    case 0:p.key.mrt_mask=3;r.cb_descs[1].first=2;break;
    case 1:r.cb_descs[0].first=2;break;
    case 2:r.cb_descs[0].second.view_info.min_lod=4;break;
    case 3:r.cb_descs[0].second.view_info.mapping.r=1;break;
    case 4:p.key.color_samples[0]=2;break;
    case 5:r.cb_descs[0].second.info.meta_info.cmask_addr=0x1000;break;
    case 6:r.cb_descs[0].second.info.meta_info.fmask_addr=0x3000;break;
    case 7:p.key.num_samples=2;break;
    case 8:r.cp.regs.depth_control.depth_enable=false;break;
    case 9:r.cp.regs.depth_buffer.depth_valid=false;break;
    default:assert(false);
    }
    bool consumed=false;(void)r.BeginRendering(&p,consumed);assert(r.texture_cache.targets>before);
}
void Boundary(u32 variant,bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;Warm(r,p);const auto before=r.texture_cache.targets;
    switch(variant) {
    case 0:r.scheduler.EndRendering();break;
    case 1:{auto s=r.order_begin_memo.state;r.scheduler.EndRendering();r.scheduler.BeginRendering(s);break;}
    case 2:++r.scheduler.tick;break;
    case 3:r.needs_barrier=true;break;
    case 4:r.cp.regs.depth_render_control.depth_clear_enable=true;break;
    default:assert(false);
    }
    r.Draw(p,4);assert(r.texture_cache.targets>before);r.scheduler.EndRendering();r.scheduler.Sync();
}
void Feedback(bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;Warm(r,p);const auto before=r.texture_cache.targets;
    r.texture_cache.GetImage(1).binding.is_bound=true;
    r.Draw(p,8);assert(r.texture_cache.targets>before&&r.attachment_feedback_loop&&!r.order_begin_memo.valid);
    r.scheduler.EndRendering();r.scheduler.Sync();
}
void MetadataOwner() {
    Rasterizer r;GraphicsPipeline p;r.cb_descs[0].second.info.meta_info.cmask_addr=0x1000;r.cp.regs.color_buffers[0].address=0x1000;Warm(r,p);
    const auto before=r.texture_cache.targets;
    auto&i=r.texture_cache.GetImage(2);
    r.texture_cache.RegisterMeta(0x1000,{TextureCache::MetaType::CMask,2,i.image_uid});
    r.texture_cache.surface_metadata.Touch(0x1000,0,false);
    r.Draw(p,6);assert(r.texture_cache.targets>before);
    assert(r.texture_cache.surface_metas.find(0x1000).value().owner_id==VideoCore::ImageId{1});
}
void Companion() {
    Rasterizer r;GraphicsPipeline p;p.key.mrt_mask=0;r.cb_descs[0].first={};r.db_desc.first=5;r.db_desc.second.view_info.is_storage=true;
    auto&companion=r.texture_cache.GetImage(7);companion.info.pixel_format=vk::Format::eUndefined;
    r.db_desc.second.info.stencil_addr=companion.info.guest_address;r.db_desc.second.info.stencil_size=32;
    Warm(r,p);const auto before=r.texture_cache.depth_targets;
    companion.AssociateDepth(6,r.texture_cache.GetImage(6).image_uid);
    r.Draw(p,7);assert(r.texture_cache.depth_targets>before);
    assert(companion.depth_id==VideoCore::ImageId{5});
}

void RawMetadataAddress(bool depth,bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;
    if(depth){p.key.mrt_mask=0;r.cb_descs[0].first={};r.db_desc.first=5;r.db_desc.second.view_info.is_storage=true;}
    Warm(r,p);
    const VAddr raw=0x7000;
    auto&other=r.texture_cache.GetImage(2);
    r.texture_cache.RegisterMeta(raw,{depth?TextureCache::MetaType::HTile:TextureCache::MetaType::CMask,2,other.image_uid});
    r.texture_cache.surface_metadata.Touch(raw,0,false);
    if(depth)r.cp.regs.depth_htile_data_base.address=raw;else r.cp.regs.color_buffers[0].address=raw;
    r.Draw(p,31); // normalized descriptor remains zero while the raw register is nonzero
    assert(r.texture_cache.surface_metadata.Clear(raw,64));
    bool consumed=false;const auto state=r.BeginRendering(&p,consumed);
    assert(consumed);
    if(r.needs_barrier)r.runtime.FlushBarriers();
    r.scheduler.BeginRendering(state,consumed);r.scheduler.EndRendering();r.scheduler.Sync();
    assert(depth?r.scheduler.gpu.surfaces.at(5)[0].depth==std::bit_cast<u32>(.25f):
                 r.scheduler.gpu.surfaces.at(1)[0].color[0]==11);
}


void ConcurrentInvalidation(bool generation_change) {
    Rasterizer r;GraphicsPipeline p;Warm(r,p);
    auto signature=r.MakeOrderBeginSignature(&p);
    auto targets=r.OrderRenderStateImages(signature,r.order_begin_memo.state);
    std::mutex signal_mutex;std::condition_variable cv;
    bool attempted=false,done=false,result=true;
    r.texture_cache.mutex.lock();
    r.texture_cache.mutex.before_lock=[&]{std::scoped_lock signal{signal_mutex};attempted=true;cv.notify_one();};
    std::thread caller([&]{
        const bool accepted=r.texture_cache.CheckRenderStateImages(targets,r.order_begin_memo.images,signature.generation,false);
        std::scoped_lock signal{signal_mutex};result=accepted;done=true;cv.notify_one();
    });
    {
        std::unique_lock signal{signal_mutex};
        assert(cv.wait_for(signal,std::chrono::seconds(2),[&]{return attempted||done;}));
        assert(attempted&&!done); // the real validation must wait before reading mutable state
    }
    if(generation_change)++r.texture_cache.generation;
    else r.texture_cache.GetImage(1).flags|=VideoCore::ImageFlagBits::CpuDirty;
    r.texture_cache.mutex.unlock();caller.join();assert(done&&!result);
}

void Policy() {
    Rasterizer r;GraphicsPipeline p;Warm(r,p);
    const auto before=r.texture_cache.targets;Common::ElfInfo::Instance().serial="CUSA08809";
    r.Draw(p,4);assert(r.texture_cache.targets==before+1&&!r.order_begin_memo.valid);
    Common::ElfInfo::Instance().serial="CUSA00785";
}
int main(int argc,char**argv) {
    const bool active=argc<2||std::string_view(argv[1])!="desktop";
    assert(OrderRenderStateMemoEnabled()==active);
    for(bool deferred:{false,true})ReadOnlyCost(deferred,active);
    if(!active){std::cout<<"ORDER_RENDER_STATE_DESKTOP_PASS\n";return 0;}
    for(bool deferred:{false,true}) {
        Rearm(deferred,false);Rearm(deferred,true);
        RawMetadataAddress(false,deferred);RawMetadataAddress(true,deferred);
        DirtyWrite(deferred,false,false);DirtyWrite(deferred,true,false);DirtyWrite(deferred,false,true);
        for(u32 i=0;i<12;++i)ResourceReject(i,deferred);
        for(u32 i=0;i<5;++i)Boundary(i,deferred);
        Feedback(deferred);
    }
    for(u32 i=0;i<10;++i)SignatureReject(i);
    MetadataOwner();Companion();ConcurrentInvalidation(false);ConcurrentInvalidation(true);Policy();
    std::cout<<"ORDER_RENDER_STATE_MEMO_REAL_METHODS_PASS\n";
}
'''


def program(source: Path) -> str:
    root = source / "src"
    code = coalescing.program(source).split("using namespace Vulkan;\nbool enabled{},inline_enabled{};")[0]
    # The earlier gate deliberately extracts the original transaction; install
    # both actual methods here, alongside the actual memo and validation APIs.
    rc = (root / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    rh = (root / "video_core/renderer_vulkan/vk_rasterizer.h").read_text()
    tc = (root / "video_core/texture_cache/texture_cache.cpp").read_text()
    th = (root / "video_core/texture_cache/texture_cache.h").read_text()
    sh = (root / "video_core/renderer_vulkan/vk_scheduler.h").read_text()
    ih = (root / "video_core/texture_cache/image.h").read_text()
    vh = (root / "video_core/texture_cache/image_view.h").read_text()
    slots = (root / "common/slot_vector.h").read_text()
    code = '#include <condition_variable>\n#include <atomic>\n#include <mutex>\n#include <set>\n#include "common/enum.h"\n' + code
    code = code.replace("namespace Common {\nstruct ElfInfo", "namespace Common {\n" + block(slots, "struct SlotId {") + ";\nstruct ElfInfo", 1)
    code = code.replace("namespace vk {\nusing ImageView=u64;", "namespace Shader{struct ImageResource;}\nnamespace AmdGpu{struct Image;struct ColorBuffer;struct DepthBuffer;struct DepthView;struct DepthControl;enum class ImageType{Color2D,Color2DArray};constexpr u32 NUM_COLOR_BUFFERS=8;}\nnamespace vk {\nenum class Format{eUndefined,eR8G8B8A8Unorm};\nstruct ComponentMapping{u32 r{},g{},b{},a{};auto operator<=>(const ComponentMapping&)const=default;};\nusing ImageView=u64;", 1)
    support = SUPPORT.replace("@FLAGS@", ih[ih.index("enum ImageFlagBits :"):ih.index("struct UniqueImage {")])
    support = support.replace("@VIEW_INFO@", block(vh, "struct ImageViewInfo {"))
    old_image = block(code, "struct Image {")
    code = code.replace(old_image + ";", support + IMAGE, 1)
    code = code.replace("struct Desc {struct{SubresourceRange range;bool is_storage=true;}view_info;};", SUPPORT_AFTER, 1)
    old_cache = block(code, "struct TextureCache {")
    cache = CACHE.replace("@VIEW_MEMO@", block(th, "    struct ViewMemo {"))
    api_start = th.index("    struct RenderStateImage {")
    api_end = th.index("\n    /// Updates image contents", api_start)
    cache = cache.replace("@CACHE_API@", th[api_start:api_end])
    cache = cache.replace("@UPDATE_IMAGE@", block(th, "    void UpdateImage("))
    cache = cache.replace("@META_METHODS@", "\n".join(block(th, f) for f in ("    bool IsMetaCleared(", "    bool TouchMeta(")))
    methods = "\n".join(block(tc, f) for f in (
        "bool TextureCache::CheckRenderStateImages(", "void TextureCache::TrackImage(",
        "void TextureCache::TrackImageHead(", "void TextureCache::TrackImageTail(",
        "void TextureCache::TouchImage(", "void TextureCache::RegisterMeta(",
        "void TextureCache::UnregisterMeta(", "ImageView& TextureCache::FindRenderTarget(",
        "ImageView& TextureCache::FindDepthTarget(", "void TextureCache::InvalidateMemory(",
        "void TextureCache::InvalidateMemoryFromGPU("))
    # Counters are fixture observability, outside the production control flow.
    methods = methods.replace("    Image& image = slot_images[image_id];\n    image.flags |= ImageFlagBits::GpuModified;",
                              "    ++targets;\n    Image& image = slot_images[image_id];\n    image.flags |= ImageFlagBits::GpuModified;", 1)
    pos = methods.index("ImageView& TextureCache::FindDepthTarget(")
    methods = methods[:pos] + methods[pos:].replace("    Image& image = slot_images[image_id];", "    ++depth_targets;\n    Image& image = slot_images[image_id];", 1)
    # View-allocation boundary of the real depth companion method: the tests
    # pre-create legal companion slots, so its creation branch must stay unused.
    methods = methods.replace("stencil_id = slot_images.Insert(instance, runtime, slot_image_views, info);\n            RegisterImage(stencil_id);", "assert(false); (void)info;")
    code = code.replace(old_cache + ";", "using namespace VideoCore;\nnamespace LiverpoolToVK{inline bool IsFormatStencilCompatible(vk::Format){return false;}}\n" + cache + methods, 1)
    code = code.replace("TextureCache texture_cache;", "TextureCache texture_cache{scheduler};", 1)
    code = code.replace("std::array<std::pair<u32,VideoCore::Desc>,8>cb_descs;", "std::array<std::pair<VideoCore::ImageId,VideoCore::Desc>,8>cb_descs;")
    code = code.replace("std::pair<u32,VideoCore::Desc>db_desc;", "std::pair<VideoCore::ImageId,VideoCore::Desc>db_desc;")
    code = code.replace("std::vector<u32>bound_images;", "std::vector<VideoCore::ImageId>bound_images;")
    code = code.replace("struct{bool depth_enable=true,depth_write_enable=true,stencil_enable=true;}depth_control;", "struct{u32 depth_enable:1=1,depth_write_enable:1=1,stencil_enable:1=1,unused:29=0;}depth_control;")
    code = code.replace("struct{bool DepthValid()const{return true;}bool StencilValid()const{return true;}}depth_buffer;", "struct{bool depth_valid=true,stencil_valid=true;bool DepthValid()const{return depth_valid;}bool StencilValid()const{return stencil_valid;}}depth_buffer;")
    code = code.replace("u64 address=0x1000;", "u64 address=0;")
    code = code.replace("struct{VAddr GetAddress()const{return 0x2000;}}depth_htile_data_base;", "struct{VAddr address{};VAddr GetAddress()const{return address;}}depth_htile_data_base;")
    code = code.replace("struct GraphicsPipeline {struct{u32 mrt_mask=1;", "struct GraphicsPipeline {struct{u32 mrt_mask=1,num_samples=1;")
    code = code.replace("    void SetBackingSamples(VideoCore::Image*,u32){}", "    void SetBackingSamples(VideoCore::Image*i,u32 n){i->backing->num_samples=n;}")
    members_start = rh.index("    RenderState BeginRenderingFull(")
    members_end = rh.index("\n    void Resolve();", members_start)
    code = code.replace("    RenderState BeginRendering(const GraphicsPipeline*,bool&metadata_clear_consumed);", "    RenderState BeginRendering(const GraphicsPipeline*,bool&metadata_clear_consumed);\n" + rh[members_start:members_end], 1)
    scheduler_api = "\n".join(block(sh, f) for f in ("    [[nodiscard]] bool IsRenderingWith(", "    [[nodiscard]] u64 RenderingSerial("))
    code = code.replace("    void Sync(){if(recorder)recorder->Sync();}", "    u64 tick=1;u64 CurrentTick()const{return tick;}\n" + scheduler_api + "\n    void Sync(){if(recorder)recorder->Sync();}", 1)
    full = block(code, "RenderState Rasterizer::BeginRendering(")
    method_start = rc.index("static bool OrderRenderStateMemoEnabled()")
    method_end = rc.index("RenderState Rasterizer::BeginRenderingFull(", method_start)
    code = code.replace(full, rc[method_start:method_end] + block(rc, "RenderState Rasterizer::BeginRenderingFull("), 1)
    # Production logging still instantiates its arguments so private/missing
    # APIs cannot hide behind a no-op preprocessor macro.
    code = code.replace("#define LOG_INFO(...) ((void)0)", "template<class... T>void IgnoreLog(T&&...){}\nconstexpr int Render_Vulkan=0;\n#define LOG_INFO IgnoreLog")
    code = code.replace("VideoCore::TextureCache::", "TextureCache::")
    assert "@" not in code
    return code + TESTS


def run(directory: Path, source: Path, code: str, name: str, *, desktop=False, negative=False) -> None:
    path = directory / (name + ".cpp")
    exe = directory / name
    path.write_text(code)
    args = shlex.split(os.environ.get("CXX", "c++")) + ["-std=c++23", "-O1", "-g", "-pthread",
        "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter", "-Wno-unused-variable", "-Wno-missing-field-initializers",
        "-fsanitize=undefined", "-fno-sanitize-recover=all", "-I", str(source / "src"), str(path), "-o", str(exe)]
    if not desktop: args.insert(1, "-D__ANDROID__")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        (directory / (name + ".build.log")).write_text(result.stdout + result.stderr)
        raise RuntimeError(name + " compile:\n" + "\n".join(result.stderr.splitlines()[:65]))
    env = dict(os.environ, ORDER1886_COALESCE_CLEAR_PASS="1", ORDER1886_INLINE_ATTACHMENT_CLEAR="0")
    result = subprocess.run([str(exe)] + (["desktop"] if desktop else []), capture_output=True,
                            text=True, env=env, timeout=20)
    (directory / (name + ".run.log")).write_text(result.stdout + result.stderr)
    if negative:
        assert result.returncode != 0, f"negative survived: {name}"
        print("ORDER_RENDER_STATE_NEGATIVE_PASS", name, flush=True)
    else:
        if result.returncode: raise RuntimeError(name + " run:\n" + result.stdout + result.stderr)
        print(result.stdout, end="", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--keep", type=Path)
    parser.add_argument("--positive-only", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve()
    with tempfile.TemporaryDirectory(prefix="order-render-state-") as temporary:
        directory = args.keep.resolve() if args.keep else Path(temporary)
        directory.mkdir(parents=True, exist_ok=True)
        code = program(source)
        run(directory, source, code, "enabled")
        if args.positive_only: return
        run(directory, source, code, "desktop", desktop=True)
        negatives = {
            "memo_removed": ("if (forced) event = OrderBeginEvent::ClearOrBarrier;", "if (true) event = OrderBeginEvent::ClearOrBarrier;"),
            "signature_ignored": ("else if (signature != memo.signature)", "else if (false)"),
            "scope_restarted": ("memo.rendering_serial != scheduler.RenderingSerial() ||", ""),
            "commandbuffer_tick": ("memo.tick != scheduler.CurrentTick() ||", ""),
            "dirty_ignored": ("ImageFlagBits::Dirty | ImageFlagBits::Aliased", "ImageFlagBits::Aliased"),
            "alias_ignored": ("ImageFlagBits::Dirty | ImageFlagBits::Aliased", "ImageFlagBits::Dirty"),
            "uid_ignored": ("view.image_uid != image.image_uid ||", ""),
            "backing_uid": ("view.backing_uid != image.backing->backing_uid ||", ""),
            "view_uid": ("live_view.view_uid != view.view_uid ||", ""),
            "metadata_rearm": ("if (target.clear_address && surface_metadata.IsCleared(target.clear_address, layer)) return false;", "if (false) return false;"),
            "metadata_owner": ("it.value().owner_id == target.image_id &&\n                   it.value().owner_uid == image.image_uid &&", ""),
            "partial_transition": ("index >= subresources.size() || !matches_state(subresources[index])", "index >= subresources.size()"),
            "gpu_modified": ("False(image.flags & ImageFlagBits::GpuModified) ||", ""),
            "companion_owner": ("companion.depth_id != target.image_id || companion.depth_uid != image.image_uid", "false"),
            "other_title": ('return Common::ElfInfo::Instance().GameSerial() == "CUSA00785";', "return true;"),
        }
        for name, (old, new) in negatives.items():
            assert code.count(old) == 1, (name, code.count(old))
            run(directory, source, code.replace(old, new), name, negative=True)
        raw_mutant = code.replace("!signature.metadata_addresses_match ||", "").replace("signature.metadata_addresses_match &&\n            texture_cache.CheckRenderStateImages", "texture_cache.CheckRenderStateImages")
        assert raw_mutant != code
        run(directory, source, raw_mutant, "raw_metadata_addresses", negative=True)
        check = block(code, "bool TextureCache::CheckRenderStateImages(")
        unlocked = check.replace("    std::scoped_lock lock{mutex};", "")
        assert unlocked != check
        run(directory, source, code.replace(check, unlocked), "missing_validation_lock", negative=True)
        no_recheck = check.replace("    if (generation != RegistryGeneration()) return false;", "")
        assert no_recheck != check
        run(directory, source, code.replace(check, no_recheck), "generation_after_lock", negative=True)
        print(f"ORDER_RENDER_STATE_MEMO_GATE_PASS negatives={len(negatives)+3}", flush=True)


if __name__ == "__main__":
    main()
