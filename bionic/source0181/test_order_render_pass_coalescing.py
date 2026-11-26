#!/usr/bin/env python3
"""Execute the effective render-pass group, metadata consumption and barriers.

The Vulkan device/recorder queue and texture lookup are boundary fixtures. The
RenderState, Rasterizer::BeginRendering, Image::GetBarriers, Runtime transitions,
metadata masks and Scheduler::Begin/End/RecordDeferred bodies are production.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from test_order_readconst_pool import block as function
from port_order_render_pass_coalescing import HELPERS, NEW_BEGIN, OLD_BEGIN, validate_contract


PRELUDE = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <chrono>
#include <compare>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <ranges>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>
#include "common/types.h"
#include "video_core/texture_cache/surface_metadata.h"
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define LOG_INFO(...) ((void)0)
namespace Common {
struct ElfInfo {
    std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo i;return i;}
    std::string_view GameSerial()const{return serial;}
};
template<class R,class... Args>using UniqueFunction=std::function<R(Args...)>;
}
namespace vk {
using ImageView=u64;
using Image=u64;
enum class ImageLayout:u32 {eUndefined,eGeneral,eColorAttachmentOptimal,
 eAttachmentFeedbackLoopOptimalEXT,eDepthStencilAttachmentOptimal,eDepthAttachmentOptimal,
 eDepthStencilReadOnlyOptimal,eDepthReadOnlyOptimal,eDepthReadOnlyStencilAttachmentOptimal,
 eDepthAttachmentStencilReadOnlyOptimal,eStencilAttachmentOptimal};
enum class ImageAspectFlagBits:u32 {eColor=1,eDepth=2,eStencil=4};
template<class E>struct Flags {
    using U=std::underlying_type_t<E>;U bits{};
    constexpr Flags()=default;
    constexpr Flags(E value):bits{U(value)}{}
    constexpr explicit Flags(U value):bits{value}{}
    constexpr explicit operator bool()const{return bits!=0;}
    constexpr Flags& operator|=(Flags other){bits|=other.bits;return *this;}
    constexpr auto operator<=>(const Flags&)const=default;
};
template<class E>constexpr Flags<E> operator|(E a,E b){return Flags<E>{std::underlying_type_t<E>(a)|std::underlying_type_t<E>(b)};}
template<class E>constexpr Flags<E> operator|(Flags<E> a,Flags<E>b){a|=b;return a;}
template<class E>constexpr Flags<E> operator|(Flags<E> a,E b){a|=Flags<E>{b};return a;}
template<class E>constexpr Flags<E> operator|(E a,Flags<E> b){b|=Flags<E>{a};return b;}
template<class E>constexpr Flags<E> operator&(Flags<E> a,Flags<E>b){return Flags<E>{a.bits&b.bits};}
template<class E>constexpr Flags<E> operator&(Flags<E> a,E b){return a&Flags<E>{b};}
using ImageAspectFlags=Flags<ImageAspectFlagBits>;
enum class PipelineStageFlagBits2:u64{eNone=0,eAllCommands=1,eColorAttachmentOutput=2,eEarlyFragmentTests=4,eLateFragmentTests=8};
using PipelineStageFlags2=Flags<PipelineStageFlagBits2>;
enum class AccessFlagBits2:u64{eNone=0,eTransferWrite=1,eShaderWrite=2,eMemoryWrite=4,
 eColorAttachmentWrite=8,eColorAttachmentRead=16,eDepthStencilAttachmentWrite=32,eDepthStencilAttachmentRead=64};
using AccessFlags2=Flags<AccessFlagBits2>;
enum class AttachmentLoadOp:u32{eLoad,eClear};
enum class AttachmentStoreOp:u32{eStore};
struct ClearColorValue{std::array<u32,4>uint32;};
struct ClearDepthStencilValue{float depth;u32 stencil;};
union ClearValue{ClearColorValue color;ClearDepthStencilValue depthStencil;};
struct Offset2D{s32 x,y;};
struct Extent2D{u32 width,height;};
struct Rect2D{Offset2D offset;Extent2D extent;};
struct ClearAttachment{ImageAspectFlags aspectMask;u32 colorAttachment;ClearValue clearValue;};
struct ClearRect{Rect2D rect;u32 baseArrayLayer,layerCount;};
struct RenderingAttachmentInfo{ImageView imageView;ImageLayout imageLayout;
 AttachmentLoadOp loadOp;AttachmentStoreOp storeOp;ClearValue clearValue;};
struct RenderingInfo{Rect2D renderArea;u32 layerCount,colorAttachmentCount;
 const RenderingAttachmentInfo*pColorAttachments,*pDepthAttachment,*pStencilAttachment;};
struct ImageSubresourceRange{ImageAspectFlags aspectMask;u32 baseMipLevel,levelCount,baseArrayLayer,layerCount;};
struct ImageMemoryBarrier2{PipelineStageFlags2 srcStageMask;AccessFlags2 srcAccessMask;
 PipelineStageFlags2 dstStageMask;AccessFlags2 dstAccessMask;ImageLayout oldLayout,newLayout;
 u32 srcQueueFamilyIndex,dstQueueFamilyIndex;Image image;ImageSubresourceRange subresourceRange;};
struct MemoryBarrier2{PipelineStageFlags2 srcStageMask;AccessFlags2 srcAccessMask;};
struct DependencyInfo{const MemoryBarrier2*pMemoryBarriers{};u32 memoryBarrierCount{};
 const ImageMemoryBarrier2*pImageMemoryBarriers{};u32 imageMemoryBarrierCount{};};
struct CommandBuffer;
}
constexpr u32 VK_QUEUE_FAMILY_IGNORED=~0u,VK_REMAINING_MIP_LEVELS=~0u,VK_REMAINING_ARRAY_LAYERS=~0u;

struct Pixel {std::array<u32,4>color{};u32 depth{},stencil{};auto operator<=>(const Pixel&)const=default;};
struct DeviceModel {
    std::map<u64,std::array<Pixel,16*32>>surfaces;
    std::vector<vk::RenderingAttachmentInfo>colors;
    std::optional<vk::RenderingAttachmentInfo>depth,stencil;
    vk::Rect2D area{};u32 layers{};
    u64 begins{},ends{},inline_calls{},barriers{},draws{};
    bool active{};
    std::vector<std::string>events;
    void Apply(const vk::ClearAttachment&clear,const vk::ClearRect&rect) {
        assert(active&&rect.rect.offset.x==0&&rect.rect.offset.y==0&&rect.baseArrayLayer==0);
        assert(rect.rect.extent.width==area.extent.width&&rect.rect.extent.height==area.extent.height);
        assert(rect.layerCount==layers);
        auto each=[&](u64 view,auto op) {
            assert(view&&rect.rect.extent.width*rect.rect.extent.height<=16&&layers<=32);
            for(u32 layer=0;layer<layers;++layer)
                for(u32 pixel=0;pixel<area.extent.width*area.extent.height;++pixel)
                    op(surfaces[view][layer*16+pixel]);
        };
        if(clear.aspectMask&vk::ImageAspectFlagBits::eColor) {
            assert(clear.colorAttachment<colors.size());
            each(colors[clear.colorAttachment].imageView,[&](Pixel&p){p.color=clear.clearValue.color.uint32;});
        }
        if(clear.aspectMask&vk::ImageAspectFlagBits::eDepth) {
            assert(depth);each(depth->imageView,[&](Pixel&p){p.depth=std::bit_cast<u32>(clear.clearValue.depthStencil.depth);});
        }
        if(clear.aspectMask&vk::ImageAspectFlagBits::eStencil) {
            assert(stencil);each(stencil->imageView,[&](Pixel&p){p.stencil=clear.clearValue.depthStencil.stencil;});
        }
    }
    void Begin(vk::RenderingInfo info) {
        assert(!active&&info.renderArea.offset.x==0&&info.renderArea.offset.y==0);
        active=true;++begins;events.push_back("begin");area=info.renderArea;layers=info.layerCount;
        colors.assign(info.pColorAttachments,info.pColorAttachments+info.colorAttachmentCount);
        depth=info.pDepthAttachment?std::optional{*info.pDepthAttachment}:std::nullopt;
        stencil=info.pStencilAttachment?std::optional{*info.pStencilAttachment}:std::nullopt;
        const vk::ClearRect rect{area,0,layers};
        for(u32 i=0;i<colors.size();++i) {
            assert(colors[i].storeOp==vk::AttachmentStoreOp::eStore);
            if(colors[i].imageView&&colors[i].loadOp==vk::AttachmentLoadOp::eClear)
                Apply({vk::ImageAspectFlagBits::eColor,i,colors[i].clearValue},rect);
        }
        if(depth&&depth->imageView&&depth->loadOp==vk::AttachmentLoadOp::eClear)
            Apply({vk::ImageAspectFlagBits::eDepth,0,depth->clearValue},rect);
        if(stencil&&stencil->imageView&&stencil->loadOp==vk::AttachmentLoadOp::eClear)
            Apply({vk::ImageAspectFlagBits::eStencil,0,stencil->clearValue},rect);
    }
    void End(){assert(active);active=false;++ends;events.push_back("end");}
    void Clear(u32 count,const vk::ClearAttachment*a,u32 rect_count,const vk::ClearRect*r) {
        assert(active&&count&&count<=9&&rect_count==1);++inline_calls;events.push_back("clear");
        for(u32 i=0;i<count;++i)Apply(a[i],r[0]);
    }
    void Draw(u32 value) {
        assert(active);++draws;events.push_back("draw");
        for(const auto&cb:colors)if(cb.imageView)
            for(u32 layer=0;layer<layers;++layer)
                for(u32 p=0;p<area.extent.width*area.extent.height;p+=2)
                    surfaces[cb.imageView][layer*16+p].color={value,value+1,value+2,value+3};
        if(depth)surfaces[depth->imageView][0].depth=value;
        if(stencil)surfaces[stencil->imageView][0].stencil=value;
    }
};
namespace vk {
struct CommandBuffer {
    DeviceModel*gpu{};std::vector<std::function<void()>>*queue{};
    bool Fake()const{return queue!=nullptr;}
    void beginRendering(const RenderingInfo&info)const {
        if(!queue){gpu->Begin(info);return;}
        std::vector<RenderingAttachmentInfo>colors(info.pColorAttachments,info.pColorAttachments+info.colorAttachmentCount);
        auto depth=info.pDepthAttachment?std::optional{*info.pDepthAttachment}:std::nullopt;
        auto stencil=info.pStencilAttachment?std::optional{*info.pStencilAttachment}:std::nullopt;
        queue->push_back([device=gpu,info=vk::RenderingInfo{info},colors,depth,stencil]()mutable{
            info.pColorAttachments=colors.data();info.pDepthAttachment=depth?&*depth:nullptr;
            info.pStencilAttachment=stencil?&*stencil:nullptr;device->Begin(info);
        });
    }
    void endRendering()const {if(queue)queue->push_back([device=gpu]{device->End();});else gpu->End();}
    void clearAttachments(u32 count,const ClearAttachment*a,u32 n,const ClearRect*r)const {
        // Real GenericThunk refuses pointer arguments on a fake handle.
        assert(!Fake());gpu->Clear(count,a,n,r);
    }
    void pipelineBarrier2(const DependencyInfo&)const {
        auto f=[device=gpu]{assert(!device->active);++device->barriers;device->events.push_back("barrier");};
        if(queue)queue->push_back(f);else f();
    }
    void Draw(u32 value)const {if(queue)queue->push_back([device=gpu,value]{device->Draw(value);});else gpu->Draw(value);}
};
}
namespace Vulkan {
@RENDER_STATE@
struct Recorder {
    DeviceModel&gpu;std::vector<std::function<void()>>commands;u64 count{};
    void CountCommand(){++count;}
    void Run(std::function<void()>f){commands.push_back(std::move(f));}
    vk::CommandBuffer Real(vk::CommandBuffer fake){assert(fake.Fake());return {&gpu,nullptr};}
    void Sync(){auto pending=std::move(commands);commands.clear();for(auto&f:pending)f();}
};
struct Scheduler {
    DeviceModel gpu;
    std::unique_ptr<Recorder>recorder;
    RenderState render_state{};bool is_rendering{};u64 drains{};
    explicit Scheduler(bool deferred=false){if(deferred)recorder=std::make_unique<Recorder>(gpu);}
    void DrainDrawPipe(){++drains;}
    vk::CommandBuffer CommandBuffer(){DrainDrawPipe();return {&gpu,recorder?&recorder->commands:nullptr};}
    void RecordDeferred(Common::UniqueFunction<void,vk::CommandBuffer>&&func);
    void BeginRendering(const RenderState&,bool metadata_clear_consumed=false);
    void EndRendering();
    void Sync(){if(recorder)recorder->Sync();}
};
@HELPERS@
@SCHEDULER@
}
namespace VideoCore {
@SUBRES@
struct Image {
    struct State {vk::PipelineStageFlags2 pl_stage=vk::PipelineStageFlagBits2::eAllCommands;
        vk::AccessFlags2 access_mask=vk::AccessFlagBits2::eNone;vk::ImageLayout layout=vk::ImageLayout::eUndefined;};
    struct Backing {State state;std::vector<State>subresource_states;};
    Backing object;Backing*backing=&object;
    struct {SubresourceExtent resources{};struct{u32 width=2,height=2;}size;struct{bool has_stencil=true;}props;}info;
    struct{bool needs_rebind{},is_bound{},force_general{};}binding;
    struct{bool render_target{},depth_target{};}usage;
    vk::ImageAspectFlags aspect_mask=vk::ImageAspectFlagBits::eColor;
    u64 handle=1;
    vk::Image GetImage()const{return handle;}
    using Barriers=std::vector<vk::ImageMemoryBarrier2>;
    void GetBarriers(Barriers&,vk::ImageLayout,vk::AccessFlags2,vk::PipelineStageFlags2,std::optional<SubresourceRange>);
};
@IMAGE_BARRIERS@
struct Desc {struct{SubresourceRange range;bool is_storage=true;}view_info;};
}
'''


RESOURCE_FIXTURE = r'''
namespace Vulkan {
struct Runtime {
    Scheduler&scheduler;
    vk::MemoryBarrier2 memory_barrier{};
    std::vector<vk::ImageMemoryBarrier2>image_barriers;
    struct{void Clear(){}}donor_barriers;
    u64 donor_access_epoch=1;
    std::array<int,2>donor_access_memo{};
    struct Resource {struct{void Clear(){}}read_ranges,write_ranges;};
    std::vector<Resource>resources;Resource*resource{};
    void SetBackingSamples(VideoCore::Image*,u32){}
    bool Transit(VideoCore::Image*,vk::ImageLayout,vk::PipelineStageFlags2,vk::AccessFlags2,std::optional<VideoCore::SubresourceRange> = {});
    void FlushBarriers();
};
@RUNTIME@
struct TextureCache {
    VideoCore::SurfaceMetadata surface_metadata;
    std::array<VideoCore::Image,10>images;
    struct View {struct{VideoCore::SubresourceRange range;}info;u64 handle{};
        const u64*image_view=&handle;};
    std::array<View,10>views;
    TextureCache(){for(u32 i=0;i<views.size();++i){images[i].handle=i;views[i].handle=i;}}
    bool HasLiveMeta(VAddr address)const{return surface_metadata.TypeAt(address).has_value();}
    @META_METHODS@
    VideoCore::Image& GetImage(u32 id){assert(id);return images[id];}
    u32 FindImage(const VideoCore::Desc&){assert(false);return 0;}
    void UpdateImage(u32){}
    const View& FindRenderTarget(u32 id,const VideoCore::Desc&){return views[id];}
    const View& FindDepthTarget(u32 id,const VideoCore::Desc&){return views[id];}
};
struct Instance {u32 GetMaxFramebufferWidth()const{return 4;}u32 GetMaxFramebufferHeight()const{return 4;}
 bool IsAttachmentFeedbackLoopLayoutSupported()const{return true;}};
struct ColorBuffer {u64 address=0x1000;std::array<u32,4>clear{11,12,13,14};VAddr CmaskAddress()const{return address;}};
namespace LiverpoolToVK {vk::ClearValue ColorBufferClearValue(const ColorBuffer&cb){return {.color={cb.clear}};}}
struct Regs {
    std::array<ColorBuffer,8>color_buffers;
    struct{VAddr GetAddress()const{return 0x2000;}}depth_htile_data_base;
    struct{bool depth_clear_enable{},stencil_clear_enable{};}depth_render_control;
    struct{bool depth_enable=true,depth_write_enable=true,stencil_enable=true;}depth_control;
    struct{bool DepthValid()const{return true;}bool StencilValid()const{return true;}}depth_buffer;
    float depth_clear=.25f;u32 stencil_clear=37;
};
struct Liverpool {Regs regs;const Regs&DrawRegs()const{return regs;}};
struct GraphicsPipeline {struct{u32 mrt_mask=1;std::array<u32,8>color_samples{1,1,1,1,1,1,1,1};}key;
 const auto&GetGraphicsKey()const{return key;}};
struct Rasterizer {
    Instance instance;Scheduler scheduler;Runtime runtime{scheduler};TextureCache texture_cache;
    Liverpool cp;Liverpool*liverpool=&cp;
    std::array<std::pair<u32,VideoCore::Desc>,8>cb_descs;
    std::pair<u32,VideoCore::Desc>db_desc;
    std::vector<u32>bound_images;
    bool attachment_feedback_loop{},needs_barrier{};
    explicit Rasterizer(bool deferred=false):scheduler{deferred}{cb_descs[0].first=1;}
    RenderState BeginRendering(const GraphicsPipeline*,bool&metadata_clear_consumed);
    RenderState Draw(const GraphicsPipeline&pipeline,u32 value) {
        bool metadata_clear_consumed=false;
        const auto state=BeginRendering(&pipeline,metadata_clear_consumed);
        if(needs_barrier)runtime.FlushBarriers();
        scheduler.BeginRendering(state,metadata_clear_consumed);scheduler.CommandBuffer().Draw(value);needs_barrier=false;
        return state;
    }
};
@RASTERIZER@
}
'''


TESTS = r'''
using namespace Vulkan;
bool enabled{},inline_enabled{};

RenderState State(u32 layers=1) {
    RenderState s{};s.width=2;s.height=2;s.num_layers=layers;s.num_color_attachments=1;
    s.color_attachments[0].image_view=1;
    s.color_attachments[0].image_layout=vk::ImageLayout::eColorAttachmentOptimal;
    return s;
}
void ClearToLoad(bool deferred) {
    Rasterizer rasterizer{deferred};GraphicsPipeline pipeline;
    auto&meta=rasterizer.texture_cache.surface_metadata;
    meta.Register(0x1000,1,VideoCore::SurfaceMetadata::Type::CMask);
    const auto first=rasterizer.Draw(pipeline,100);
    assert(first.color_attachments[0].is_clear==1&&!meta.IsCleared(0x1000,0));
    const auto barrier_count=rasterizer.runtime.image_barriers.size();
    assert(barrier_count==0);
    const auto second=rasterizer.Draw(pipeline,200);
    assert(second.color_attachments[0].is_clear==0);
    assert(first.color_attachments[0].image_view==second.color_attachments[0].image_view);
    rasterizer.scheduler.EndRendering();rasterizer.scheduler.Sync();
    const auto&gpu=rasterizer.scheduler.gpu;
    assert(gpu.begins==(enabled?1:2)&&gpu.ends==gpu.begins&&gpu.barriers==1&&gpu.draws==2);
    assert(gpu.surfaces.at(1)[0].color[0]==200);
    assert((gpu.surfaces.at(1)[1].color==std::array<u32,4>{11,12,13,14}));
}

void InlineClear(bool deferred,u32 layers,bool with_depth) {
    Scheduler scheduler{deferred};auto state=State(layers);
    state.num_color_attachments=3;state.color_attachments[2]=state.color_attachments[0];
    state.color_attachments[2].image_view=3;
    if(with_depth) {
        auto&ds=state.depth_stencil_attachment;ds.image_view=5;
        ds.image_layout=vk::ImageLayout::eDepthStencilAttachmentOptimal;ds.has_depth=true;ds.has_stencil=true;
    }
    scheduler.BeginRendering(state);scheduler.CommandBuffer().Draw(50);
    auto cleared=state;
    cleared.color_attachments[0].is_clear=1;cleared.color_attachments[0].clear_value={7,8,9,10};
    cleared.color_attachments[2].is_clear=1;cleared.color_attachments[2].clear_value={17,18,19,20};
    if(with_depth) {
        auto&ds=cleared.depth_stencil_attachment;ds.depth_clear=true;ds.stencil_clear=true;
        ds.clear_value[0]=std::bit_cast<u32>(.75f);ds.clear_value[1]=93;
    }
    scheduler.BeginRendering(cleared);
    // Overwrite caller values before the deferred queue consumes the inline clear.
    cleared={};std::array<u64,1024>scrub{};scrub.fill(0xfedcba9876543210ULL);
    scheduler.CommandBuffer().Draw(70);scheduler.EndRendering();scheduler.Sync();
    assert(scrub[7]);
    const auto&gpu=scheduler.gpu;
    const bool inline_expected=enabled&&inline_enabled&&layers<=16;
    assert(gpu.begins==(inline_expected?1:2)&&gpu.ends==gpu.begins);
    assert(gpu.inline_calls==(inline_expected?1:0)&&gpu.draws==2);
    for(u32 layer=0;layer<layers;++layer) {
        assert((gpu.surfaces.at(1)[layer*16+1].color==std::array<u32,4>{7,8,9,10}));
        assert((gpu.surfaces.at(3)[layer*16+1].color==std::array<u32,4>{17,18,19,20}));
    }
    if(with_depth) {
        assert(gpu.surfaces.at(5)[1].depth==std::bit_cast<u32>(.75f));
        assert(gpu.surfaces.at(5)[1].stencil==93);
    }
    if(inline_expected)assert((gpu.events==std::vector<std::string>{"begin","draw","clear","draw","end"}));
}

void Incompatible(u32 variant,bool deferred) {
    Scheduler scheduler{deferred};auto state=State();
    state.color_attachments[0].is_clear=1;state.color_attachments[0].clear_value={1,2,3,4};
    scheduler.BeginRendering(state);scheduler.CommandBuffer().Draw(5);
    auto next=state;next.color_attachments[0].is_clear=0;next.color_attachments[0].clear_value={};
    switch(variant) {
    case 0:next.color_attachments[0].image_view=2;break; // new backing/format/samples/view range
    case 1:next.color_attachments[0].image_layout=vk::ImageLayout::eGeneral;break;
    case 2:next.width=3;break;
    case 3:next.height=3;break;
    case 4:next.num_layers=2;break;
    case 5:next.num_color_attachments=2;next.color_attachments[1]=next.color_attachments[0];next.color_attachments[1].image_view=2;break;
    case 6:next.depth_stencil_attachment.image_view=5;next.depth_stencil_attachment.image_layout=vk::ImageLayout::eDepthStencilAttachmentOptimal;next.depth_stencil_attachment.has_depth=true;break;
    default:assert(false);
    }
    scheduler.BeginRendering(next);scheduler.CommandBuffer().Draw(6);scheduler.EndRendering();scheduler.Sync();
    assert(scheduler.gpu.begins==2&&scheduler.gpu.ends==2&&scheduler.gpu.inline_calls==0);
}

void NewClearMustExecute(bool deferred) {
    Scheduler scheduler{deferred};auto state=State();scheduler.BeginRendering(state);
    scheduler.CommandBuffer().Draw(99);
    state.color_attachments[0].is_clear=1;state.color_attachments[0].clear_value={11,12,13,14};
    scheduler.BeginRendering(state);scheduler.EndRendering();scheduler.Sync();
    for(u32 p=0;p<4;++p)assert((scheduler.gpu.surfaces.at(1)[p].color==std::array<u32,4>{11,12,13,14}));
    assert(scheduler.gpu.inline_calls==((enabled&&inline_enabled)?1:0));
}

void RearmedSameMetadata(bool deferred,bool depth) {
    Rasterizer r{deferred};GraphicsPipeline p;
    if(depth){r.cb_descs[0].first=0;p.key.mrt_mask=0;r.db_desc.first=5;}
    auto&meta=r.texture_cache.surface_metadata;
    const auto address=depth?0x2000:0x1000;
    meta.Register(address,depth?5:1,depth?VideoCore::SurfaceMetadata::Type::HTile:
                                           VideoCore::SurfaceMetadata::Type::CMask);
    r.Draw(p,100);
    assert(meta.Clear(address,64));
    bool consumed=false;
    const auto second=r.BeginRendering(&p,consumed);
    assert(consumed);
    if(r.needs_barrier)r.runtime.FlushBarriers();
    r.scheduler.BeginRendering(second,consumed);r.scheduler.EndRendering();r.scheduler.Sync();
    const auto observed=depth?r.scheduler.gpu.surfaces.at(5)[0].depth:
                              r.scheduler.gpu.surfaces.at(1)[0].color[0];
    const u32 expected=depth?std::bit_cast<u32>(r.cp.regs.depth_clear):11;
    // Preserve other platforms/titles, but do not lose a new Order clear just
    // because its bits equal those consumed before the previous draw.
    assert(observed==(enabled?expected:100));
    assert(r.scheduler.gpu.begins==(enabled&&!inline_enabled?2:1));
    assert(r.scheduler.gpu.inline_calls==((enabled&&inline_enabled)?1:0));
}

void PersistentDepthClear(bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;p.key.mrt_mask=0;r.cb_descs[0].first=0;r.db_desc.first=5;
    r.cp.regs.depth_render_control.depth_clear_enable=true;
    r.Draw(p,100);
    bool consumed=true;
    const auto state=r.BeginRendering(&p,consumed);assert(!consumed);
    r.scheduler.BeginRendering(state,consumed);r.scheduler.EndRendering();r.scheduler.Sync();
    assert(r.scheduler.gpu.begins==1&&r.scheduler.gpu.inline_calls==0);
    assert(r.scheduler.gpu.surfaces.at(5)[0].depth==100);
}

void AspectClears(bool deferred) {
    for(u32 mask:{1u,2u,3u})for(u32 bits:{0x80000000u,0x3f400000u,0x7fc00123u}) {
        Scheduler scheduler{deferred};auto state=State();state.num_color_attachments=0;state.color_attachments={};
        auto&ds=state.depth_stencil_attachment;ds.image_view=5;ds.has_depth=true;ds.has_stencil=true;
        ds.image_layout=mask==1?vk::ImageLayout::eDepthAttachmentStencilReadOnlyOptimal:
                        mask==2?vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal:
                                vk::ImageLayout::eDepthStencilAttachmentOptimal;
        scheduler.BeginRendering(state);scheduler.CommandBuffer().Draw(99);
        ds.depth_clear=(mask&1)!=0;ds.stencil_clear=(mask&2)!=0;ds.clear_value[0]=bits;ds.clear_value[1]=213;
        scheduler.BeginRendering(state);scheduler.EndRendering();scheduler.Sync();
        const auto&p=scheduler.gpu.surfaces.at(5)[0];
        assert(p.depth==((mask&1)?bits:99)&&p.stencil==((mask&2)?213u:99u));
        assert(scheduler.gpu.inline_calls==((enabled&&inline_enabled)?1:0));
    }
}

void AllAttachments(bool deferred) {
    Scheduler scheduler{deferred};auto state=State(2);state.num_color_attachments=8;
    for(u32 i=0;i<8;++i){state.color_attachments[i]=state.color_attachments[0];state.color_attachments[i].image_view=i+1;}
    auto&ds=state.depth_stencil_attachment;ds.image_view=9;ds.has_depth=true;ds.has_stencil=true;
    ds.image_layout=vk::ImageLayout::eDepthStencilAttachmentOptimal;
    scheduler.BeginRendering(state);scheduler.CommandBuffer().Draw(77);
    for(u32 i=0;i<8;++i){state.color_attachments[i].is_clear=1;state.color_attachments[i].clear_value={0xffffffffu,i,0x7fc01234u,0x80000000u};}
    ds.depth_clear=true;ds.stencil_clear=true;ds.clear_value[0]=std::bit_cast<u32>(.5f);ds.clear_value[1]=111;
    scheduler.BeginRendering(state);scheduler.EndRendering();scheduler.Sync();
    for(u32 i=0;i<8;++i)for(u32 layer=0;layer<2;++layer)
        assert(scheduler.gpu.surfaces.at(i+1)[layer*16].color==state.color_attachments[i].clear_value);
    assert(scheduler.gpu.surfaces.at(9)[16].depth==ds.clear_value[0]);
    assert(scheduler.gpu.surfaces.at(9)[16].stencil==111);
    assert(scheduler.gpu.inline_calls==((enabled&&inline_enabled)?1:0));
}

void ReadOnlyClearFallback(bool deferred) {
    for(bool depth:{false,true}) {
        Scheduler scheduler{deferred};auto state=State();
        auto&ds=state.depth_stencil_attachment;ds.image_view=5;ds.has_depth=true;ds.has_stencil=true;
        ds.image_layout=depth?vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal:
                              vk::ImageLayout::eDepthAttachmentStencilReadOnlyOptimal;
        scheduler.BeginRendering(state);
        ds.depth_clear=depth;ds.stencil_clear=!depth;ds.clear_value[0]=std::bit_cast<u32>(.5f);ds.clear_value[1]=71;
        scheduler.BeginRendering(state);scheduler.EndRendering();scheduler.Sync();
        assert(scheduler.gpu.begins==2&&scheduler.gpu.inline_calls==0);
    }
}

void ExplicitBoundary(bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;
    r.texture_cache.surface_metadata.Register(0x1000,1,VideoCore::SurfaceMetadata::Type::CMask);
    r.Draw(p,10);
    auto&image=r.texture_cache.GetImage(1);
    const auto mask=vk::AccessFlagBits2::eColorAttachmentWrite|vk::AccessFlagBits2::eColorAttachmentRead;
    assert(!r.runtime.Transit(&image,vk::ImageLayout::eColorAttachmentOptimal,
                             vk::PipelineStageFlagBits2::eColorAttachmentOutput,mask));
    r.runtime.FlushBarriers(); // Empty same-attachment barrier preserves the pass.
    assert(r.scheduler.is_rendering);
    assert(r.runtime.Transit(&image,vk::ImageLayout::eGeneral,
                            vk::PipelineStageFlagBits2::eAllCommands,vk::AccessFlagBits2::eShaderWrite));
    r.runtime.FlushBarriers();assert(!r.scheduler.is_rendering);
    r.Draw(p,20);r.scheduler.EndRendering();r.scheduler.Sync();
    assert(r.scheduler.gpu.begins==2&&r.scheduler.gpu.barriers==3&&r.scheduler.gpu.draws==2);
}

void OtherTitles(bool deferred) {
    const auto previous=Common::ElfInfo::Instance().serial;
    for(const char*serial:{"CUSA08809","CUSA08034","CUSA00004",""}) {
        Common::ElfInfo::Instance().serial=serial;
        Scheduler scheduler{deferred};auto state=State();state.color_attachments[0].is_clear=1;
        scheduler.BeginRendering(state);state.color_attachments[0].is_clear=0;
        scheduler.BeginRendering(state);scheduler.EndRendering();scheduler.Sync();
        assert(scheduler.gpu.begins==2&&scheduler.gpu.inline_calls==0);
    }
    Common::ElfInfo::Instance().serial=previous;
}

void RepeatedMetadata(bool deferred) {
    Rasterizer r{deferred};GraphicsPipeline p;
    auto&meta=r.texture_cache.surface_metadata;
    meta.Register(0x1000,1,VideoCore::SurfaceMetadata::Type::CMask);
    constexpr u32 rounds=2048;
    for(u32 i=0;i<rounds;++i) {
        if(i)assert(meta.Clear(0x1000,64));
        r.cp.regs.color_buffers[0].clear={i,i+1,i+2,i+3};
        r.Draw(p,10+i);r.Draw(p,20+i);
    }
    r.scheduler.EndRendering();r.scheduler.Sync();
    const auto&g=r.scheduler.gpu;
    assert(g.draws==rounds*2&&g.begins==(enabled?(inline_enabled?1:rounds):rounds*2));
    assert(g.inline_calls==((enabled&&inline_enabled)?rounds-1:0)&&g.barriers==1);
    assert(g.surfaces.at(1)[1].color[0]==rounds-1);
    std::cout<<"ORDER_PASS_COST recorder="<<deferred<<" rounds="<<rounds<<" begins="<<g.begins
             <<" ends="<<g.ends<<" inline="<<g.inline_calls<<" draws="<<g.draws<<"\n";
}

int main(int argc,char**argv) {
    enabled=argc>1&&std::string_view(argv[1])=="enabled";
    inline_enabled=std::getenv("ORDER1886_INLINE_ATTACHMENT_CLEAR")[0]!='0';
    assert(UsesOrderRenderPassCoalescing()==enabled);
    assert(UsesOrderInlineAttachmentClear()==inline_enabled);
    for(bool deferred:{false,true}) {
        ClearToLoad(deferred);
        for(u32 layers:{1u,2u,16u,17u})for(bool depth:{false,true})InlineClear(deferred,layers,depth);
        for(u32 variant=0;variant<7;++variant)Incompatible(variant,deferred);
        NewClearMustExecute(deferred);AspectClears(deferred);AllAttachments(deferred);
        RearmedSameMetadata(deferred,false);RearmedSameMetadata(deferred,true);PersistentDepthClear(deferred);
        ReadOnlyClearFallback(deferred);ExplicitBoundary(deferred);
        OtherTitles(deferred);RepeatedMetadata(deferred);
    }
    std::cout<<"ORDER_RENDER_PASS_COALESCING_PASS enabled="<<enabled<<"\n";
}
'''


def program(source: Path, scheduler_override: str | None = None) -> str:
    root = source / "src"
    scheduler = scheduler_override or (root / "video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
    header = (root / "video_core/renderer_vulkan/vk_scheduler.h").read_text()
    image = (root / "video_core/texture_cache/image.cpp").read_text()
    types = (root / "video_core/texture_cache/types.h").read_text()
    runtime = (root / "video_core/renderer_vulkan/vk_runtime.cpp").read_text()
    rasterizer = (root / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    assert "bool metadata_clear_consumed = false" in header
    for signature in ("void Rasterizer::Draw(", "void Rasterizer::DrawIndirect("):
        consumer = function(rasterizer, signature)
        assert consumer.count("BeginRendering(pipeline, metadata_clear_consumed)") == 1
        assert consumer.count("scheduler.BeginRendering(state, metadata_clear_consumed)") == 1
    cache = (root / "video_core/texture_cache/texture_cache.h").read_text()
    helper_start = scheduler.index("// BACHATA_ORDER_RENDER_PASS:")
    helper_end = scheduler.index("void Scheduler::BeginRendering", helper_start)
    replacements = {
        "@RENDER_STATE@": header[header.index("struct RenderAttachment {"):header.index("struct SubmitInfo {")],
        "@HELPERS@": scheduler[helper_start:helper_end],
        "@SCHEDULER@": "\n".join(function(scheduler, f) for f in (
            "void Scheduler::RecordDeferred(", "void Scheduler::BeginRendering(", "void Scheduler::EndRendering(")),
        "@SUBRES@": types[types.index("struct SubresourceBase {"):types.index("struct ImageCopy {")],
        "@IMAGE_BARRIERS@": function(image, "void Image::GetBarriers("),
        "@RUNTIME@": "\n".join(function(runtime, f) for f in ("bool Runtime::Transit(", "void Runtime::FlushBarriers(")),
        "@RASTERIZER@": function(rasterizer, "RenderState Rasterizer::BeginRendering("),
        "@META_METHODS@": "\n".join(function(cache, f) for f in ("    bool IsMetaCleared(", "    bool TouchMeta(")),
    }
    if "RenderState Rasterizer::BeginRenderingFull(" in rasterizer:
        # This gate owns the original clear/transition transaction. The later
        # memo wrapper and its invalidations execute in test_order_render_state_memo.
        replacements["@RASTERIZER@"] = function(
            rasterizer, "RenderState Rasterizer::BeginRenderingFull(").replace(
                "Rasterizer::BeginRenderingFull(", "Rasterizer::BeginRendering(", 1)
    code = PRELUDE + RESOURCE_FIXTURE + TESTS
    if (root / "video_core/renderer_vulkan/order_resource_census.h").exists():
        code = code.replace("#define LOG_INFO(...) ((void)0)",
            '#define LOG_INFO(...) ((void)0)\n#include "video_core/renderer_vulkan/order_resource_census.h"', 1)
        code = code.replace("    Scheduler&scheduler;", "    Scheduler&scheduler;\n    bool order_resource_census=false;\n    OrderBarrierPending order_barrier_pending{};", 1)
        code = code.replace("    void Sync(){if(recorder)recorder->Sync();}",
            "    bool RenderingActive()const{return is_rendering;}\n    void Sync(){if(recorder)recorder->Sync();}", 1)
    if "u64 rendering_serial{};" in header:
        code = code.replace("RenderState render_state{};bool is_rendering{};u64 drains{};",
                            "RenderState render_state{};bool is_rendering{};u64 drains{},rendering_serial{};", 1)
    if (root / "video_core/renderer_vulkan/order_render_pass_reasons.h").exists():
        code = '#include "video_core/renderer_vulkan/order_render_pass_reasons.h"\n' + code
        code = code.replace('    void EndRendering();',
            '    void EndRendering(OrderPassEndReason reason = OrderPassEndReason::Unspecified);', 1)
    for key, value in replacements.items():
        assert code.count(key) == 1, key
        code = code.replace(key, value)
    return code


def compile_run(directory: Path, code: str, name: str, *, android: bool = True,
                enabled: bool = True, inline_enabled: bool = True,
                expect_failure: bool = False) -> str:
    path = directory / (name + ".cpp")
    exe = directory / name
    path.write_text(code)
    command = shlex.split(os.environ.get("CXX", "c++")) + (["-D__ANDROID__"] if android else []) + [
        "-std=c++23", "-O1", "-g", "-fsanitize=undefined", "-fno-sanitize-recover=all",
        "-pthread", "-Wall", "-Wextra", "-Wno-unused-variable", "-Wno-missing-field-initializers",
        "-I", str(SOURCE / "src"), str(path), "-o", str(exe)]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        (directory / (name + ".build.log")).write_text(result.stdout + result.stderr)
        raise RuntimeError(f"compile {name}:\n" + "\n".join(result.stderr.splitlines()[:70]))
    env = dict(os.environ, ORDER1886_COALESCE_CLEAR_PASS="1" if enabled else "0",
               ORDER1886_INLINE_ATTACHMENT_CLEAR="1" if inline_enabled else "0")
    result = subprocess.run([str(exe), "enabled" if enabled else "disabled"],
                            text=True, capture_output=True, env=env, timeout=30)
    if expect_failure:
        assert result.returncode != 0, f"negative control survived: {name}"
        print(f"ORDER_RENDER_PASS_NEGATIVE_PASS {name}", flush=True)
    else:
        if result.returncode:
            raise RuntimeError(f"run {name}:\n{result.stdout}\n{result.stderr}")
        print(result.stdout, end="", flush=True)
    return result.stdout


def application_guards(directory: Path, source: Path) -> None:
    rel = Path("src/video_core/renderer_vulkan/vk_scheduler.cpp")
    text = (source / rel).read_text()
    header = (source / rel.with_suffix(".h")).read_text()
    if "u64 rendering_serial{};" in header:
        assert text.count("    ++rendering_serial;\n") == 1
        text = text.replace("    ++rendering_serial;\n", "", 1)
    if 'BACHATA_ORDER_PASS_END_REASON' in text:
        # Undo only the subsequent diagnostic decoration before checking the
        # unchanged coalescing patch and its six incompatible-state negatives.
        from port_order_pass_end_reasons import COUNTER
        assert text.count(COUNTER) == 1
        text = text.replace(COUNTER, '')
        text = text.replace('void Scheduler::EndRendering(OrderPassEndReason reason)',
                            'void Scheduler::EndRendering()')
        text = text.replace('EndRendering(Vulkan::OrderPassEndReason::RenderState);', 'EndRendering();')
        text = text.replace('    if (UsesOrderRenderPassCoalescing()) CountOrderPassEndReason(this, reason);\n', '')
        header = header.replace('void EndRendering(OrderPassEndReason reason = OrderPassEndReason::Unspecified);',
                                'void EndRendering();')
    assert text.count(HELPERS) == 1 and text.count(NEW_BEGIN) == 1
    original = text.replace(HELPERS, "").replace(NEW_BEGIN, OLD_BEGIN)
    original = original.replace("void Scheduler::BeginRendering(const RenderState& new_state, bool metadata_clear_consumed) {",
                                "void Scheduler::BeginRendering(const RenderState& new_state) {")
    original = original.replace(
        "    if (UsesOrderRenderPassCoalescing()) CountOrderRenderPass(OrderRenderPassEvent::End);\n", "")
    validate_contract(original, header)
    mutations = (
        (original.replace(".storeOp = vk::AttachmentStoreOp::eStore,", ".storeOp = vk::AttachmentStoreOp::eDontCare,", 1), header),
        (original.replace(".renderArea =", ".viewMask = 1,\n        .renderArea =", 1), header),
        (original.replace(".imageView = cb.image_view,", ".imageView = cb.image_view,\n            .resolveMode = vk::ResolveModeFlagBits::eAverage,", 1), header),
        (original.replace(".offset = {0, 0},", ".offset = {1, 1},", 1), header),
        (original.replace(".layerCount = render_state.num_layers,", ".layerCount = 1,", 1), header),
        (original, header.replace("struct RenderState {", "struct RenderState {\n    u32 new_identity_field;", 1)),
    )
    for cpp, h in mutations:
        try:
            validate_contract(cpp, h)
        except RuntimeError:
            pass
        else:
            raise AssertionError("unsafe dynamic-rendering contract accepted")
    print("ORDER_RENDER_PASS_APPLICATION_GUARDS_PASS negative_controls=6", flush=True)


def main() -> None:
    global SOURCE
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--keep", type=Path)
    args = parser.parse_args()
    SOURCE = args.source.resolve()
    code = program(SOURCE)
    directory_context = tempfile.TemporaryDirectory(prefix="bachata-order-pass-")
    directory = args.keep.resolve() if args.keep else Path(directory_context.name)
    directory.mkdir(parents=True, exist_ok=True)
    application_guards(directory, SOURCE)
    compile_run(directory, code, "enabled")
    compile_run(directory, code, "disabled", enabled=False)
    compile_run(directory, code, "inline_disabled", inline_enabled=False)
    compile_run(directory, code, "desktop", android=False, enabled=False)
    negatives = {
        "missing_coalescence": ("if (order_pass_coalescing) {", "if (false) {"),
        "identity_ignored": ("if (prior == new_state)", "if (true)"),
        "new_clear_dropped": ("if (!requests_clear)", "if (true)"),
        "inline_not_recorded": ("cmdbuf.clearAttachments(count, clears.data(), 1, &rect);", "(void)cmdbuf;"),
        "fake_clear_pointer": ("RecordDeferred([clears, count, rect](vk::CommandBuffer cmdbuf)", "[clears, count, rect](vk::CommandBuffer cmdbuf)"),
        "layer_range_lost": (".baseArrayLayer = 0, .layerCount = new_state.num_layers", ".baseArrayLayer = 0, .layerCount = 1"),
        "readonly_clear": ("&& OrderInlineClearLayoutCompatible(new_state)", ""),
        "other_title_changed": ('if (Common::ElfInfo::Instance().GameSerial() != "CUSA00785") return false;', ""),
        "same_metadata_clear_lost": (" && !(order_pass_coalescing && metadata_clear_consumed)", ""),
        "persistent_register_recleared": ("order_pass_coalescing && metadata_clear_consumed", "order_pass_coalescing"),
    }
    for name, (old, new) in negatives.items():
        assert code.count(old) == 1, (name, code.count(old))
        mutant = code.replace(old, new)
        if name == "fake_clear_pointer":
            mutant = mutant.replace("cmdbuf.clearAttachments(count, clears.data(), 1, &rect);\n                        });",
                                     "cmdbuf.clearAttachments(count, clears.data(), 1, &rect);\n                        }(CommandBuffer());")
        if name == "new_clear_dropped":
            # Disable inline substitution too: the new request must never be
            # absorbed by the CLEAR->LOAD path when no inline clear executes.
            mutant = mutant.replace("if (UsesOrderInlineAttachmentClear() &&", "if (false &&")
        compile_run(directory, mutant, name, expect_failure=True)
    print("ORDER_RENDER_PASS_GROUP_PASS negative_controls=10 application_guards=6", flush=True)
    directory_context.cleanup()


if __name__ == "__main__":
    main()
