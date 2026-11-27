"""Actual Order Android selective 2x2 VRS path, with native recorder ownership.

Reference Android overlay order1886_vrs.h, vk_instance.cpp, vk_graphics_pipeline.cpp
and vk_rasterizer.cpp::Order1886UseVrs2x2. Unlike broad VRS, only opaque scene
geometry is eligible. Retain 1x1 for alpha coverage, depth/stencil exports,
storage effects, depth samples, blending, feedback and unknown half-res draws.
ORDER1886_VRS_2X2=0 restores per-pixel rate on the same device.
"""
from pathlib import Path

HEADER=r'''#pragma once
#include <atomic>
#include <cstdint>
namespace Vulkan {
inline std::atomic_bool order_vrs_enabled{false};
inline std::atomic_uint64_t order_vrs_draws{0};
inline std::atomic_uint64_t order_vrs_halfres_draws{0};
inline constexpr bool OrderVrsGeometry(std::uint32_t width,std::uint32_t height,
    std::uint32_t targets,bool geometry,bool depth_write,bool clip_disabled) {
    if(width>=960 && height>=540) return targets>=2;
    return width==640 && height==360 && targets==1 && geometry && depth_write && !clip_disabled;
}
}
'''
GUARD=r'''// BACHATA_ORDER_VRS: donor 1x1/2x2 policy, not a frame/draw skip.
static bool OrderUseVrs2x2(const GraphicsPipeline* pipeline,const AmdGpu::Regs& regs,
                           const RenderState& state,bool feedback,bool geometry) {
    if(feedback || !state.depth_stencil_attachment.has_depth ||
       !regs.depth_control.depth_enable || regs.depth_control.stencil_enable) return false;
    const auto& key=pipeline->GetGraphicsKey();
    if(key.num_samples!=1 && !AmdGpu::BachataOrderNoMsaa()) return false;
    if(!OrderVrsGeometry(state.width,state.height,std::popcount(key.mrt_mask),geometry,
                         regs.depth_control.depth_write_enable,regs.IsClipDisabled())) return false;
    const auto* fs=pipeline->GetStages()[u32(Shader::SwStage::Fragment)];
    if(!fs || fs->has_discard || fs->has_storage_images || fs->translation_failed) return false;
    const auto& exports=regs.depth_shader_control;
    if(exports.z_export_enable || exports.stencil_op_val_export_enable ||
       exports.stencil_test_val_export_enable || exports.mask_export_enable ||
       exports.coverage_to_mask_enable) return false;
    for(const auto& image:fs->images) if(image.is_depth || image.is_written) return false;
    for(const auto& buffer:fs->buffers) if(buffer.is_written) return false;
    for(u32 i=0;i<state.num_color_attachments;++i) {
        if((key.mrt_mask&(1u<<i)) &&
           (key.blend_controls[i].enable || !state.color_attachments[i].image_view)) return false;
    }
    return true;
}

void Rasterizer::SetOrderVrs(const GraphicsPipeline* pipeline,const RenderState& state,
                             bool direct,bool is_indexed) {
    if(!order_vrs_enabled.load(std::memory_order_relaxed)) return;
    const auto& regs=liverpool->DrawRegs();
    const bool geometry=direct && order_vrs_has_vertices &&
        (is_indexed || regs.num_indices>6 || regs.num_instances.NumInstances()>1);
    const bool coarse=OrderUseVrs2x2(pipeline,regs,state,attachment_feedback_loop,geometry);
    if(coarse) {
        const auto n=order_vrs_draws.fetch_add(1,std::memory_order_relaxed)+1;
        if(state.width==640 && state.height==360)
            order_vrs_halfres_draws.fetch_add(1,std::memory_order_relaxed);
        if(n==1 || !(n&0x3ffff))
            LOG_INFO(Render_Vulkan,"BACHATA_ORDER_VRS_DRAW_COUNTS rate=2x2 draws={} halfres={}",
                     n,order_vrs_halfres_draws.load(std::memory_order_relaxed));
    }
    const vk::Extent2D rate{coarse?2u:1u,coarse?2u:1u};
    // This extension command takes pointers. Use the owned deferred closure
    // so the fake command-buffer recorder never borrows stack storage.
    scheduler.RecordDeferred([rate](vk::CommandBuffer real) {
        const std::array<vk::FragmentShadingRateCombinerOpKHR,2> ops{
            vk::FragmentShadingRateCombinerOpKHR::eKeep,vk::FragmentShadingRateCombinerOpKHR::eKeep};
        real.setFragmentShadingRateKHR(rate,ops);
    });
}

'''
def one(s,a,b,label):
    if s.count(a)!=1: raise RuntimeError("Order VRS anchor "+label+": "+str(s.count(a)))
    return s.replace(a,b,1)

def add_vrs_query_feature(s):
    anchor="const vk::StructureChain feature_chain"
    if s.count(anchor)!=1:
        raise RuntimeError("Order VRS feature chain declaration drift")
    first=s.index(anchor)
    begin=s.index("getFeatures2<",first)
    end=s.index(">();",begin)
    query=s[begin:end]
    if query.count("vk::PhysicalDeviceShaderClockFeaturesKHR")!=1 or \
            "vk::PhysicalDeviceFragmentShadingRateFeaturesKHR" in query:
        raise RuntimeError("Order VRS feature query type drift")
    return s[:end]+", vk::PhysicalDeviceFragmentShadingRateFeaturesKHR"+s[end:]

def apply(root:Path):
    d=Path(root)/"src/video_core/renderer_vulkan"
    (d/"order_vrs_parity.h").write_text(HEADER)
    inc='#include "video_core/renderer_vulkan/order_vrs_parity.h"\n'
    p=d/"vk_instance.cpp";s=p.read_text()
    s=inc+'#include <cstdlib>\n'+s
    if '#include "common/elf_info.h"' not in s: s='#include "common/elf_info.h"\n'+s
    s=one(s,"bool Instance::CreateDevice() {","bool Instance::CreateDevice() {\n    order_vrs_enabled.store(false,std::memory_order_relaxed);","reset device state")
    # Scope the insertion to the getFeatures2 template list. The same
    # shader-clock type also occurs in feature_chain.get<> and unlink<>.
    # Editing those queries would alter a different Vulkan contract.
    s=add_vrs_query_feature(s)
    s=one(s,"    boost::container::static_vector<const char*, 32> enabled_extensions;",
          "    boost::container::static_vector<const char*, 64> enabled_extensions;","extension capacity")
    s=one(s,"    const bool calibrated_timestamps =",r'''    bool order_vrs_supported=false;
#ifdef __ANDROID__
    const char* vrs_env=std::getenv("ORDER1886_VRS_2X2");
    const bool order_vrs_requested=Common::ElfInfo::Instance().GameSerial()=="CUSA00785" &&
        (!vrs_env || vrs_env[0]!='0');
    if(order_vrs_requested &&
       feature_chain.get<vk::PhysicalDeviceFragmentShadingRateFeaturesKHR>().pipelineFragmentShadingRate &&
       std::find(available_extensions.begin(),available_extensions.end(),
                 std::string(VK_KHR_FRAGMENT_SHADING_RATE_EXTENSION_NAME))!=available_extensions.end()) {
        const auto [result,rates]=physical_device.getFragmentShadingRatesKHR();
        if(result==vk::Result::eSuccess &&
           std::ranges::any_of(rates,[](const auto& rate){
               return rate.fragmentSize.width==2 && rate.fragmentSize.height==2 &&
                      static_cast<bool>(rate.sampleCounts&vk::SampleCountFlagBits::e1);
           })) order_vrs_supported=add_extension(VK_KHR_FRAGMENT_SHADING_RATE_EXTENSION_NAME);
    }
    if(order_vrs_requested)
        LOG_INFO(Render_Vulkan,"BACHATA_ORDER_VRS requested=true supported_2x2={} mode={}",
                 order_vrs_supported,order_vrs_supported?"selective-2x2":"1x1");
#endif
    const bool calibrated_timestamps =''',"extension negotiation")
    s=one(s,"""        vk::PhysicalDeviceShaderClockFeaturesKHR{
            .shaderSubgroupClock = shader_clock_features.shaderSubgroupClock,
        },""",
        """        vk::PhysicalDeviceShaderClockFeaturesKHR{
            .shaderSubgroupClock = shader_clock_features.shaderSubgroupClock,
        },
        vk::PhysicalDeviceFragmentShadingRateFeaturesKHR{
            .pipelineFragmentShadingRate=order_vrs_supported,
        },""","device feature")
    s=one(s,"    auto [device_result, dev] = physical_device.createDeviceUnique(device_chain.get());",
        "    if(!order_vrs_supported) device_chain.unlink<vk::PhysicalDeviceFragmentShadingRateFeaturesKHR>();\n"
        "    auto [device_result, dev] = physical_device.createDeviceUnique(device_chain.get());","disable unsupported feature")
    s=one(s,"    VULKAN_HPP_DEFAULT_DISPATCHER.init(*device);",
        "    VULKAN_HPP_DEFAULT_DISPATCHER.init(*device);\n    order_vrs_enabled.store(order_vrs_supported,std::memory_order_release);","publish after device creation")
    p.write_text(s)
    p=d/"vk_graphics_pipeline.cpp";s=inc+p.read_text()
    # A one-sample pipeline does not need per-sample shading. Keep all
    # multisample behavior intact; the extension only advertises 2x2 at e1.
    s=one(s,"    const vk::PipelineViewportDepthClipControlCreateInfoEXT clip_control = {",
        "    if(order_vrs_enabled.load(std::memory_order_acquire) &&\n"
        "       sdata.multisampling.rasterizationSamples==vk::SampleCountFlagBits::e1)\n"
        "        sdata.multisampling.sampleShadingEnable=false;\n\n"
        "    const vk::PipelineViewportDepthClipControlCreateInfoEXT clip_control = {","single-sample pipeline")
    s=one(s,"    const vk::PipelineDynamicStateCreateInfo dynamic_info = {",
        "    if(order_vrs_enabled.load(std::memory_order_acquire))\n"
        "        dynamic_states.push_back(vk::DynamicState::eFragmentShadingRateKHR);\n\n"
        "    const vk::PipelineDynamicStateCreateInfo dynamic_info = {","dynamic shading rate")
    p.write_text(s)
    p=d/"vk_rasterizer.h";s=p.read_text()
    s=one(s,"    bool needs_barrier{};",
        "    bool needs_barrier{};\n    bool order_vrs_has_vertices{};\n"
        "    void SetOrderVrs(const GraphicsPipeline* pipeline,const RenderState& state,bool direct,bool is_indexed);","draw state")
    p.write_text(s)
    p=d/"vk_rasterizer.cpp";s=inc+'#include <bit>\n'+p.read_text()
    s=one(s,"void Rasterizer::Draw(bool is_indexed,u32 index_offset,",GUARD+"void Rasterizer::Draw(bool is_indexed,u32 index_offset,","draw guard")
    a=s.index("void Rasterizer::BindVertexBuffers(");b=s.index("\nvoid Rasterizer::BindIndexBuffer(",a)
    body=s[a:b]
    body=one(body,"    if (bindings.empty()) {",r'''    order_vrs_has_vertices=!bindings.empty() &&
        std::ranges::any_of(guest_buffers,[](const auto& b){return b.base_address!=0&&b.GetSize()>0;});
    if (bindings.empty()) {''',"real vertex-buffer candidate")
    s=s[:a]+body+s[b:]
    for marker,direct in (("void Rasterizer::Draw(",True),("void Rasterizer::DrawIndirect(",False)):
        a=s.index(marker);o=s.index("{",a);depth=1;b=o+1
        while depth:
            depth+=(s[b]=="{")-(s[b]=="}");b+=1
        body=s[a:b]
        anchor="    cmdbuf.bindPipeline(vk::PipelineBindPoint::eGraphics, pipeline->Handle());"
        body=one(body,anchor,anchor+"\n    SetOrderVrs(pipeline,state,"+("true" if direct else "false")+",is_indexed);","rate before actual draws")
        s=s[:a]+body+s[b:]
    p.write_text(s)
    return {"donor":"Android selective-2x2 guard","policy":"enabled only CUSA00785 + feature + advertised e1 2x2; ORDER1886_VRS_2X2=0 restores 1x1",
            "precision":"1x1 for shadow/depth sampling, alpha discard/coverage, blend, feedback, storage and unknown indirect halfres",
            "recording":"owned deferred real Vulkan command before every draw; no draw/feature omitted"}
