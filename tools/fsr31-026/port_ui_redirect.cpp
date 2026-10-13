// SPDX-License-Identifier: GPL-2.0-or-later
// Port-style *separate* 720p RGBA8 HUD target. The FSR output is an actual
// render target, not a blit to a guest 1080p image. Only the original
// Bloodborne Scaleform vertex shader hashes may trigger the redirection.
#include "vulkan_capture.h"
#include <vulkan/vulkan.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <vector>
namespace {
struct Depth {
    VkImage image=VK_NULL_HANDLE;
    VkDeviceMemory memory=VK_NULL_HANDLE;
    VkImageView view=VK_NULL_HANDLE;
    VkFormat format=VK_FORMAT_UNDEFINED;
    VkImageLayout layout=VK_IMAGE_LAYOUT_UNDEFINED;
};
struct State {
    VkRenderingInfo guest{};
    std::vector<VkRenderingAttachmentInfo> color;
    VkRenderingAttachmentInfo depth{},stencil{};
    bool hasDepth=false,hasStencil=false,inside=false,khr=false;
    bool uiPhase=false,uiPass=false,everRedirected=false;
    VkImageView originalUI=VK_NULL_HANDLE,output=VK_NULL_HANDLE;
    VkViewport viewport{};
    VkRect2D scissor{};
    bool haveViewport=false,haveScissor=false;
    bool viewportWithCount=false,scissorWithCount=false;
    bool jitterActive=false;
    float jitterX=0,jitterY=0;
    VkImageView candidateScene=VK_NULL_HANDLE;
    VkExtent2D sceneExtent{};
    uint64_t frame=0;
    bool earlierStencilOnlyMask=false;
    VkRenderingInfo resumed{};
    std::array<VkRenderingAttachmentInfo,1> hudColor{};
    VkRenderingAttachmentInfo hudDepth{},hudStencil{};
};
std::mutex uiMutex;
std::unordered_map<VkCommandBuffer,State> cmds;
std::unordered_map<VkImageView,Depth> uiDepth;
std::unordered_map<VkShaderModule,uint64_t> guestHashes;
std::unordered_map<VkPipeline,bool> uiPipelines;
std::unordered_map<VkCommandBuffer,bool> shaderBoundUI;
std::unordered_map<VkCommandBuffer,VkImageView> lastOutput;
std::unordered_set<VkCommandBuffer> completedHud;
struct UiFrame {
    VkImageView original{},output{};
    VkImage color{},depth{};
    uint64_t frame=0;
    bool complete=false;
};
UiFrame currentUi{};
extern "C" uint64_t bs4_port_frame_generation();
PFN_vkSetDebugUtilsObjectNameEXT realObjectName{};
PFN_vkCreateGraphicsPipelines realCreatePipelines{};
PFN_vkDestroyPipeline realDestroyPipeline{};
PFN_vkCmdBindPipeline realBindPipeline{};
PFN_vkCmdSetViewport realSetViewport{};
PFN_vkCmdSetScissor realSetScissor{};
PFN_vkCmdSetViewportWithCount realSetViewportWithCount{};
PFN_vkCmdSetScissorWithCount realSetScissorWithCount{};
PFN_vkCmdBeginRendering realBegin{};
PFN_vkCmdEndRendering realEnd{};
PFN_vkCmdBeginRenderingKHR realBeginKHR{};
PFN_vkCmdEndRenderingKHR realEndKHR{};
bool firstReport=false;

VkViewport scaled(VkViewport v) {
    v.x*=2.f/3.f;v.y*=2.f/3.f;
    v.width*=2.f/3.f;v.height*=2.f/3.f;
    return v;
}
VkRect2D scaled(VkRect2D r) {
    r.offset.x=int32_t(std::round(r.offset.x*2.0/3.0));
    r.offset.y=int32_t(std::round(r.offset.y*2.0/3.0));
    r.extent.width=uint32_t(std::round(r.extent.width*2.0/3.0));
    r.extent.height=uint32_t(std::round(r.extent.height*2.0/3.0));
    return r;
}
VkImageAspectFlags aspects(VkFormat f) {
    if(f==VK_FORMAT_D32_SFLOAT_S8_UINT ||
       f==VK_FORMAT_D24_UNORM_S8_UINT)return VK_IMAGE_ASPECT_DEPTH_BIT|
                                               VK_IMAGE_ASPECT_STENCIL_BIT;
    return VK_IMAGE_ASPECT_DEPTH_BIT;
}
} // namespace


// This is the port's subpixel viewport technique. It is called only AFTER
// genuine guest camera constants are found on a live G-buffer draw.
// Core025 supports VK_EXT_extended_dynamic_state; native viewport/scissor
// calls can be WithCount rather than old first/count. Preserve the exact
// dynamic-state family used by the game, for both camera and UI.
void native_viewport(VkCommandBuffer cb,const State& s,const VkViewport* v){
    if(s.viewportWithCount && realSetViewportWithCount)
        realSetViewportWithCount(cb,1,v);
    else if(realSetViewport)realSetViewport(cb,0,1,v);
}
void native_scissor(VkCommandBuffer cb,const State& s,const VkRect2D* rect){
    if(s.scissorWithCount && realSetScissorWithCount)
        realSetScissorWithCount(cb,1,rect);
    else if(realSetScissor)realSetScissor(cb,0,1,rect);
}
extern "C" int bs4_port_ui_apply_camera_jitter(
    VkCommandBuffer cb,float x,float y) {
    if(!cb || !std::isfinite(x) || !std::isfinite(y) ||
       std::abs(x)>0.501f || std::abs(y)>0.501f ||
       (!realSetViewport && !realSetViewportWithCount))
        return 0;
    std::lock_guard lock{uiMutex};
    const auto it=cmds.find(cb);
    if(it==cmds.end())return 0;
    auto& s=it->second;
    if(!s.inside || s.uiPhase || !s.haveViewport ||
       s.guest.colorAttachmentCount<5 || !s.hasDepth ||
       s.guest.renderArea.extent.width>4096 ||
       s.guest.renderArea.extent.height>4096)return 0;
    if(s.jitterActive)return 1;
    VkViewport p=s.viewport;
    p.x+=x;p.y+=y;
    native_viewport(cb,s,&p);
    s.jitterActive=true;s.jitterX=x;s.jitterY=y;
    return 1;
}
extern "C" int bs4_port_jitter_for_pass(VkExtent2D,float*,float*);
extern "C" int bs4_port_can_prepare_ui(VkCommandBuffer);
extern "C" VkImageView bs4_port_prepared_output(VkCommandBuffer);
extern "C" VkImageView bs4_port_scene_color(VkCommandBuffer);
extern "C" VkImageView bs4_port_current_scene(VkCommandBuffer,VkExtent2D*);
extern "C" VkImageView bs4_port_prepare_ui(VkCommandBuffer);
extern "C" VkImage bs4_fsr31_output_image(VkImageView);
extern "C" int bs4_fsr31_set_output_layout(VkImageView,VkImageLayout);
extern "C" int bs4_fsr31_ui_device(
    VkDevice* out_device,VkPhysicalDevice* out_physical);
extern "C" int bs4_fsr31_capture_image(VkImageView,Bs4FsrCaptureImage*);

extern "C" void bs4_port_ui_install_rendering(
    PFN_vkCmdBeginRendering b,PFN_vkCmdEndRendering e,
    PFN_vkCmdBeginRenderingKHR bk,PFN_vkCmdEndRenderingKHR ek) {
    std::lock_guard lock{uiMutex};
    if(b)realBegin=b;if(e)realEnd=e;
    if(bk)realBeginKHR=bk;if(ek)realEndKHR=ek;
}
extern "C" void bs4_port_ui_reset(VkCommandBuffer cb){
    std::lock_guard lock{uiMutex};
    cmds.erase(cb);shaderBoundUI.erase(cb);lastOutput.erase(cb);
    completedHud.erase(cb);
}
extern "C" VkImageView bs4_port_ui_present(VkCommandBuffer cb){
    (void)cb;const uint64_t frame=bs4_port_frame_generation();
    std::lock_guard lock{uiMutex};
    return currentUi.complete&&currentUi.frame==frame?currentUi.output:VK_NULL_HANDLE;
}

// The Port derives the projection-axis signs from the ACTUAL G-buffer
// viewport, not from camera constants alone. Inspect at draw time after
// vkCmdSetViewport; geometry and camera must belong to the same pass.
extern "C" int bs4_port_ui_projection_signs(
    VkCommandBuffer cb,float* x,float* y) {
    if(!cb || !x || !y)return 0;
    std::lock_guard lock{uiMutex};
    const auto it=cmds.find(cb);
    if(it==cmds.end())return 0;
    const auto& s=it->second;
    if(!s.inside || s.uiPhase || !s.hasDepth ||
       s.guest.colorAttachmentCount<2 || !s.haveViewport ||
       std::abs(s.viewport.width)<0.001f ||
       std::abs(s.viewport.height)<0.001f)return 0;
    *x=s.viewport.width<0.f?-1.f:1.f;
    *y=s.viewport.height<0.f?-1.f:1.f;
    return 1;
}
extern "C" void bs4_port_ui_note_draw(VkCommandBuffer cb) {
    std::lock_guard lock{uiMutex};
    auto it=cmds.find(cb);
    if(it==cmds.end() || !it->second.inside)return;
    // Bloodborne UI movie masks sometimes draw into stencil with NO color.
    // Redirecting only later color draws would lose those masks. For now,
    // use the unchanged game renderer instead of breaking those frames.
    if(!it->second.uiPhase && shaderBoundUI[cb] &&
       it->second.color.empty() && it->second.hasStencil)
        it->second.earlierStencilOnlyMask=true;
}
extern "C" VkImageView bs4_port_ui_redirect_sampled(
    VkCommandBuffer cb,VkImageView candidate) {
    if(!cb || !candidate)return VK_NULL_HANDLE;
    const uint64_t frame=bs4_port_frame_generation();
    std::lock_guard lock{uiMutex};
    if(!currentUi.complete||currentUi.frame!=frame)return VK_NULL_HANDLE;
    Bs4FsrCaptureImage sampled{};
    if(!bs4_fsr31_capture_image(candidate,&sampled) || sampled.image!=currentUi.color ||
       sampled.format!=VK_FORMAT_R8G8B8A8_UNORM)return VK_NULL_HANDLE;
    const auto state=cmds.find(cb);
    // Sampling into a DIFFERENT display target is safe even inside its pass;
    // sampling our current UI attachment would create feedback and is refused.
    if(state!=cmds.end() && state->second.inside && state->second.uiPass)
        return VK_NULL_HANDLE;
    return currentUi.output;
}
extern "C" void bs4_port_ui_finish_present(VkCommandBuffer cb){
    (void)cb;std::lock_guard lock{uiMutex};
    lastOutput.clear();completedHud.clear();currentUi={};
}

namespace {
bool createDepth(VkImageView output,VkFormat format,Depth& dest){
    VkDevice dev=VK_NULL_HANDLE;
    VkPhysicalDevice phys=VK_NULL_HANDLE;
    if(!bs4_fsr31_ui_device(&dev,&phys)||!dev||!phys)return false;
    const VkImageAspectFlags aspect=aspects(format);
    VkImageCreateInfo ci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
    ci.imageType=VK_IMAGE_TYPE_2D;ci.format=format;ci.extent={1280,720,1};
    ci.mipLevels=1;ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;
    ci.tiling=VK_IMAGE_TILING_OPTIMAL;
    ci.usage=VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT;
    VkImage image=VK_NULL_HANDLE;
    if(vkCreateImage(dev,&ci,nullptr,&image)!=VK_SUCCESS)return false;
    VkMemoryRequirements req{};
    vkGetImageMemoryRequirements(dev,image,&req);
    VkPhysicalDeviceMemoryProperties props{};
    vkGetPhysicalDeviceMemoryProperties(phys,&props);
    uint32_t memoryIndex=UINT32_MAX;
    for(uint32_t i=0;i<props.memoryTypeCount;i++) {
        if(req.memoryTypeBits&(1u<<i)) {
            if(props.memoryTypes[i].propertyFlags&VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT) {
                memoryIndex=i;break;
            }
            if(memoryIndex==UINT32_MAX)memoryIndex=i;
        }
    }
    if(memoryIndex==UINT32_MAX){vkDestroyImage(dev,image,nullptr);return false;}
    VkMemoryAllocateInfo alloc{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc.allocationSize=req.size;alloc.memoryTypeIndex=memoryIndex;
    VkDeviceMemory memory=VK_NULL_HANDLE;
    if(vkAllocateMemory(dev,&alloc,nullptr,&memory)!=VK_SUCCESS){
        vkDestroyImage(dev,image,nullptr);return false;
    }
    if(vkBindImageMemory(dev,image,memory,0)!=VK_SUCCESS){
        vkDestroyImage(dev,image,nullptr);vkFreeMemory(dev,memory,nullptr);
        return false;
    }
    VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    vi.image=image;vi.viewType=VK_IMAGE_VIEW_TYPE_2D;
    vi.format=format;vi.subresourceRange={aspect,0,1,0,1};
    VkImageView view=VK_NULL_HANDLE;
    if(vkCreateImageView(dev,&vi,nullptr,&view)!=VK_SUCCESS){
        vkDestroyImage(dev,image,nullptr);vkFreeMemory(dev,memory,nullptr);
        return false;
    }
    dest={image,memory,view,format,VK_IMAGE_LAYOUT_UNDEFINED};
    return true;
}
void transition(VkCommandBuffer cb,VkImage image,VkImageAspectFlags aspect,
                VkImageLayout oldLayout,VkImageLayout layout){
    if(oldLayout==layout)return;
    VkImageMemoryBarrier2 bar{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
    bar.srcStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    bar.srcAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;
    bar.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    bar.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;
    bar.oldLayout=oldLayout;bar.newLayout=layout;bar.image=image;
    bar.srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
    bar.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
    bar.subresourceRange={aspect,0,1,0,1};
    VkDependencyInfo dep{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
    dep.imageMemoryBarrierCount=1;dep.pImageMemoryBarriers=&bar;
    vkCmdPipelineBarrier2(cb,&dep);
}
// Build a valid Vulkan 1.3 dynamic rendering attachment set.
bool substitute(State& state,VkImageView output,Depth& depth,
                VkRenderingInfo& result) {
    if(state.guest.pNext || (state.guest.flags & (
       VK_RENDERING_RESUMING_BIT|VK_RENDERING_SUSPENDING_BIT)) ||
       state.guest.colorAttachmentCount>1 || state.color.size()>1)
        return false;
    if(!state.color.empty()) {
    state.hudColor[0]=state.color[0];
    state.hudColor[0].imageView=output;
    state.hudColor[0].imageLayout=VK_IMAGE_LAYOUT_GENERAL;
    state.hudColor[0].loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
    state.hudColor[0].resolveImageView=VK_NULL_HANDLE;
    state.hudColor[0].resolveMode=VK_RESOLVE_MODE_NONE;
    }
    result=state.guest;
    result.renderArea.offset={0,0};
    result.renderArea.extent={1280,720};
    result.pColorAttachments=state.color.empty()?nullptr:state.hudColor.data();
    if(state.hasDepth) {
        state.hudDepth=state.depth;
        state.hudDepth.imageView=depth.view;
        state.hudDepth.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
        state.hudDepth.loadOp=state.uiPhase?VK_ATTACHMENT_LOAD_OP_LOAD:VK_ATTACHMENT_LOAD_OP_CLEAR;
        state.hudDepth.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
        result.pDepthAttachment=&state.hudDepth;
    }
    if(state.hasStencil) {
        state.hudStencil=state.stencil;
        state.hudStencil.imageView=depth.view;
        state.hudStencil.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
        state.hudStencil.loadOp=state.uiPhase?VK_ATTACHMENT_LOAD_OP_LOAD:VK_ATTACHMENT_LOAD_OP_CLEAR;
        state.hudStencil.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
        result.pStencilAttachment=&state.hudStencil;
    }
    return true;
}
bool safeOriginal(State& s){
    if(!s.inside || s.uiPhase || s.guest.renderArea.offset.x ||
       s.guest.renderArea.offset.y || s.guest.renderArea.extent.width!=1920 ||
       s.guest.renderArea.extent.height!=1080 || s.color.size()>1 ||
       s.guest.pNext || (s.guest.flags & (VK_RENDERING_RESUMING_BIT|VK_RENDERING_SUSPENDING_BIT)) ||
       !s.haveViewport || !s.haveScissor || !s.candidateScene ||
       std::abs(s.viewport.width)<1919.f || std::abs(s.viewport.height)<1079.f)return false;
    Bs4FsrCaptureImage scene{},target{};
    if(!bs4_fsr31_capture_image(s.candidateScene,&scene) ||
       scene.format!=VK_FORMAT_R8G8B8A8_UNORM)return false;
    if(!s.color.empty()) {
        const auto& c=s.color[0];
        if(!c.imageView || c.storeOp!=VK_ATTACHMENT_STORE_OP_STORE || c.resolveImageView ||
           !bs4_fsr31_capture_image(c.imageView,&target) || target.image!=scene.image ||
           target.format!=scene.format)return false;
    } else if(!s.hasStencil || !s.hasDepth) return false;
    return true;
}
}
// Host rendering wrappers from original core024 call here before begin/end.
extern "C" bool bs4_port_ui_redirect_begin(
    VkCommandBuffer cb,const VkRenderingInfo* input,bool khr,
    VkRenderingInfo* output) {
    if(!cb||!input||!output)return false;
    const VkImageView candidate=bs4_port_scene_color(cb);
    const uint64_t frame=bs4_port_frame_generation();
    Bs4FsrCaptureImage color{},z{};
    if(input->colorAttachmentCount==1 && input->pColorAttachments)
        bs4_fsr31_capture_image(input->pColorAttachments[0].imageView,&color);
    if(input->pDepthAttachment)
        bs4_fsr31_capture_image(input->pDepthAttachment->imageView,&z);
    std::lock_guard lock{uiMutex};
    State& s=cmds[cb];
    s.candidateScene=candidate;s.frame=frame;
    s.inside=true;s.khr=khr;s.guest=*input;
    s.color.clear();
    if(input->pColorAttachments && input->colorAttachmentCount)
        s.color.assign(input->pColorAttachments,
                       input->pColorAttachments+input->colorAttachmentCount);
    s.hasDepth=input->pDepthAttachment!=nullptr;
    s.hasStencil=input->pStencilAttachment!=nullptr;
    if(s.hasDepth)s.depth=*input->pDepthAttachment;
    if(s.hasStencil)s.stencil=*input->pStencilAttachment;
    // Never jitter a render pass merely because its dimensions resemble a
    // G-buffer. The genuine Port requires CURRENT scene-camera constants
    // before applying jitter. bs4_port_scan_at_draw verifies those constants
    // and applies the Halton viewport shift before the guest draw command.
    const bool continuation=currentUi.output&&currentUi.frame==frame &&
        ((color.image && color.image==currentUi.color) ||
         (input->colorAttachmentCount==0&&z.image&&z.image==currentUi.depth));
    if(continuation){
        s.uiPhase=true;s.everRedirected=true;s.output=currentUi.output;
        s.originalUI=currentUi.original;
        currentUi.complete=false;
        auto depth=uiDepth.find(s.output);
        if(depth==uiDepth.end())return false;
        const VkImage source=bs4_fsr31_output_image(s.output);
        if(!source)return false;
        transition(cb,source,VK_IMAGE_ASPECT_COLOR_BIT,
                   VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
                   VK_IMAGE_LAYOUT_GENERAL);
        bs4_fsr31_set_output_layout(s.output,VK_IMAGE_LAYOUT_GENERAL);
        s.uiPass=substitute(s,s.output,depth->second,*output);
        return s.uiPass;
    }
    s.uiPass=false;return false;
}
extern "C" void bs4_port_ui_redirect_end(VkCommandBuffer cb) {
    std::lock_guard lock{uiMutex};
    const auto it=cmds.find(cb);
    if(it==cmds.end())return;
    auto& s=it->second;
    s.inside=false;
    if(s.uiPass && s.output) {
        const VkImage image=bs4_fsr31_output_image(s.output);
        if(image) {
            transition(cb,image,VK_IMAGE_ASPECT_COLOR_BIT,
                VK_IMAGE_LAYOUT_GENERAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
            bs4_fsr31_set_output_layout(s.output,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
            completedHud.insert(cb); // Only completed HUDs can be presented.
            if(currentUi.output==s.output&&currentUi.frame==s.frame)currentUi.complete=true;
        }
    }
    s.uiPass=false;
    if(s.jitterActive && (realSetViewport || realSetViewportWithCount)) {
        native_viewport(cb,s,&s.viewport);
        s.jitterActive=false;s.jitterX=s.jitterY=0;
    }
}
// Called before the first positively identified guest UI draw, while inside
// original dynamic rendering. Replaces the pass with a 720p guest HUD pass.
extern "C" bool bs4_port_ui_try_activate(VkCommandBuffer cb) {
    const VkImageView candidate=bs4_port_scene_color(cb);
    VkExtent2D sceneExtent{};
    uint64_t frame=0;bs4_port_current_scene(cb,&sceneExtent);
    std::unique_lock lock{uiMutex};
    const auto it=cmds.find(cb);
    if(it==cmds.end() || !shaderBoundUI[cb])return false;
    State& s=it->second;s.candidateScene=candidate;s.sceneExtent=sceneExtent;
    if(!safeOriginal(s))return false;
    if(s.hasDepth || s.hasStencil) {
        Bs4FsrCaptureImage originalDepth{};
        const VkImageView d=s.hasDepth?s.depth.imageView:s.stencil.imageView;
        if(!d||!bs4_fsr31_capture_image(d,&originalDepth) ||
           !(originalDepth.aspects & VK_IMAGE_ASPECT_DEPTH_BIT))
            return false;
        // The proxy depth must have the same format as the guest pipeline.
        if(originalDepth.format!=VK_FORMAT_D32_SFLOAT_S8_UINT &&
           originalDepth.format!=VK_FORMAT_D24_UNORM_S8_UINT &&
           originalDepth.format!=VK_FORMAT_D32_SFLOAT)return false;
    }
    const auto end_fn=s.khr?reinterpret_cast<PFN_vkCmdEndRendering>(realEndKHR):realEnd;
    const auto begin_fn=s.khr?reinterpret_cast<PFN_vkCmdBeginRendering>(realBeginKHR):realBegin;
    // Core025 may use ONLY Vulkan 1.3 extended dynamic-state entrypoints.
    // Requiring the old vkCmdSetViewport/Scissor proc pointers made the
    // R18 WithCount interception ineffective at the *actual* activation.
    if(!end_fn || !begin_fn ||
       !(realSetViewport || realSetViewportWithCount) ||
       !(realSetScissor || realSetScissorWithCount) ||
       (s.viewportWithCount && !realSetViewportWithCount) ||
       (s.scissorWithCount && !realSetScissorWithCount))
       return false;

    // R23 recorded vkCmdEndRendering before even checking whether the
    // temporal source/camera existed; a failed dispatch then re-opened the
    // guest pass with LOAD, which is NOT a safe no-op.
    // Verify real LDR scene + camera + same-size depth WITHOUT recording a
    // single Vulkan command. If unavailable leave the entire game pass intact.
    lock.unlock();
    const bool ready=bs4_port_can_prepare_ui(cb)!=0;
    lock.lock();
    if(!ready || !s.inside || !safeOriginal(s))return false;
    // Preflight has already built the SDK context and all color/depth/motion
    // surfaces WITHOUT recording any command. Allocate the UI proxy too
    // before ending the guest pass; rejected preparation is a true no-op.
    lock.unlock();
    const VkImageView prepared=bs4_port_prepared_output(cb);
    lock.lock();
    if(!prepared)return false;
    VkFormat originalFmt=VK_FORMAT_UNDEFINED;
    if(s.hasDepth||s.hasStencil) {
        Bs4FsrCaptureImage originalDepth{};
        const VkImageView d=s.hasDepth?s.depth.imageView:s.stencil.imageView;
        if(!bs4_fsr31_capture_image(d,&originalDepth))return false;
        originalFmt=originalDepth.format;
    }
    Depth& proxy=uiDepth[prepared];
    if(originalFmt!=VK_FORMAT_UNDEFINED && !proxy.image &&
       !createDepth(prepared,originalFmt,proxy))return false;
    VkRenderingInfo validated{};
    if(!substitute(s,prepared,proxy,validated))return false;
    end_fn(cb);
    // FSR dispatch binds its own Vulkan compute pipeline, which is also
    // seen by our proc-address hooks. Do not hold uiMutex across dispatch.
    lock.unlock();
    const VkImageView out=bs4_port_prepare_ui(cb);
    lock.lock();
    if(!out) {
        // FSR rejected inputs: resume original target and let game draw.
        VkRenderingInfo resume=s.guest;
        for(auto& a:s.color)a.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        resume.pColorAttachments=s.color.data();
        if(s.hasDepth){s.depth.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
                       resume.pDepthAttachment=&s.depth;}
        if(s.hasStencil){s.stencil.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
                         resume.pStencilAttachment=&s.stencil;}
        begin_fn(cb,&resume);return false;
    }
    const VkImage image=bs4_fsr31_output_image(out);
    if(!image) {
        // Not expected after a successful dispatch. Preserve the guest pass.
        VkRenderingInfo resume=s.guest;
        for(auto& a:s.color)a.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        resume.pColorAttachments=s.color.data();begin_fn(cb,&resume);
        return false;
    }
    Depth& depth=uiDepth[prepared];
    transition(cb,image,VK_IMAGE_ASPECT_COLOR_BIT,
        VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,VK_IMAGE_LAYOUT_GENERAL);
    bs4_fsr31_set_output_layout(out,VK_IMAGE_LAYOUT_GENERAL);
    if(depth.image) {
        transition(cb,depth.image,aspects(depth.format),depth.layout,
                   VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL);
        depth.layout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
    }
    VkRenderingInfo ri{};
    if(!substitute(s,out,depth,ri))return false;
    begin_fn(cb,&ri);
    // The game bound a 1920x1080 viewport, now the host HUD is 1280x720.
    const VkViewport vp=scaled(s.viewport);
    const VkRect2D sc=scaled(s.scissor);
    native_viewport(cb,s,&vp);
    native_scissor(cb,s,&sc);
    s.uiPhase=true;s.uiPass=true;
    s.originalUI=s.color.empty()?s.candidateScene:s.color[0].imageView;
    s.output=out;s.everRedirected=true;
    Bs4FsrCaptureImage sourceColor{},sourceDepth{};
    bs4_fsr31_capture_image(s.originalUI,&sourceColor);
    if(s.hasDepth)bs4_fsr31_capture_image(s.depth.imageView,&sourceDepth);
    currentUi={s.originalUI,out,sourceColor.image,sourceDepth.image,s.frame,false};
    lastOutput[cb]=out;
    completedHud.erase(cb); // Do not present while guest is still drawing.
    if(!firstReport) {
        firstReport=true;
        std::fprintf(stderr,
            "[BS4_PORT] FIRST_REAL_RUNSCALED_UI scene=%ux%u "
            "output=1280x720 camera_target_verified=1 guest_UI_preserved=1\n",
            s.sceneExtent.width,s.sceneExtent.height);
    }
    return true;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_port_ui_name(
    VkDevice dev,const VkDebugUtilsObjectNameInfoEXT* info) {
    if(info && info->objectType==VK_OBJECT_TYPE_SHADER_MODULE &&
       info->pObjectName) {
        const char* q=std::strstr(info->pObjectName,"0x");
        if(q){
            char* end=nullptr;
            uint64_t h=std::strtoull(q+2,&end,16);
            if(end!=q+2) {
                std::lock_guard lock{uiMutex};
                guestHashes[(VkShaderModule)(uintptr_t)info->objectHandle]=h;
            }
        }
    }
    return realObjectName?realObjectName(dev,info):VK_ERROR_EXTENSION_NOT_PRESENT;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_port_ui_create_pipelines(
    VkDevice dev,VkPipelineCache cache,uint32_t count,
    const VkGraphicsPipelineCreateInfo* cis,const VkAllocationCallbacks* ac,
    VkPipeline* output) {
    if(!realCreatePipelines)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult status=realCreatePipelines(dev,cache,count,cis,ac,output);
    if(status==VK_SUCCESS&&cis&&output){
        std::lock_guard lock{uiMutex};
        for(uint32_t i=0;i<count;++i){
            if(!output[i])continue;
            // Port native-viewport path: no title-specific shader hashes.
            // Only non-depth-tested blended/stencil UI pipelines may trigger;
            // safeOriginal separately verifies the camera-matched LDR image.
            const auto& ci=cis[i];
            const bool noDepth=ci.pDepthStencilState &&
                !ci.pDepthStencilState->depthTestEnable &&
                !ci.pDepthStencilState->depthWriteEnable;
            bool blended=false;
            if(ci.pColorBlendState)for(uint32_t j=0;j<ci.pColorBlendState->attachmentCount;j++)
                blended|=ci.pColorBlendState->pAttachments[j].blendEnable;
            const bool eligible=noDepth && (blended || ci.pDepthStencilState->stencilTestEnable);
            uiPipelines[output[i]]=eligible;
        }
    }
    return status;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_ui_destroy_pipeline(
    VkDevice d,VkPipeline p,const VkAllocationCallbacks* ac) {
    {std::lock_guard lock{uiMutex};uiPipelines.erase(p);}
    if(realDestroyPipeline)realDestroyPipeline(d,p,ac);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_ui_bind_pipeline(
    VkCommandBuffer cb,VkPipelineBindPoint point,VkPipeline p) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS) {
        std::lock_guard lock{uiMutex};
        const auto it=uiPipelines.find(p);
        shaderBoundUI[cb]=it!=uiPipelines.end()&&it->second;
    }
    if(realBindPipeline)realBindPipeline(cb,point,p);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_ui_viewport(
    VkCommandBuffer cb,uint32_t first,uint32_t count,const VkViewport* v) {
    bool redirect=false;
    VkViewport out{};
    if(first==0&&count==1&&v) {
        std::lock_guard lock{uiMutex};
        auto& s=cmds[cb];s.viewport=*v;s.haveViewport=true;
        s.viewportWithCount=false;
        redirect=s.uiPass || s.jitterActive;
        if(s.uiPass)out=scaled(*v);
        else if(s.jitterActive) {
            out=*v;out.x+=s.jitterX;out.y+=s.jitterY;
        }
    }
    if(realSetViewport)
        realSetViewport(cb,first,count,redirect?&out:v);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_ui_scissor(
    VkCommandBuffer cb,uint32_t first,uint32_t count,const VkRect2D* rect) {
    bool redirect=false;
    VkRect2D out{};
    if(first==0&&count==1&&rect) {
        std::lock_guard lock{uiMutex};
        auto& s=cmds[cb];s.scissor=*rect;s.haveScissor=true;
        s.scissorWithCount=false;
        redirect=s.uiPass; if(redirect)out=scaled(*rect);
    }
    if(realSetScissor)
        realSetScissor(cb,first,count,redirect?&out:rect);
}
// Vulkan 1.3 extended dynamic-state entry points. Ignoring these made
// s.haveViewport / s.haveScissor false on core025, so no camera, no HUD,
// and therefore no FSR dispatch despite correct attach/preset logs.
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_ui_viewport_with_count(
    VkCommandBuffer cb,uint32_t count,const VkViewport* views) {
    bool redirect=false;
    VkViewport out{};
    if(count==1 && views) {
        std::lock_guard lock{uiMutex};
        auto& s=cmds[cb];
        s.viewport=*views;s.haveViewport=true;s.viewportWithCount=true;
        redirect=s.uiPass || s.jitterActive;
        if(s.uiPass)out=scaled(*views);
        else if(s.jitterActive){
            out=*views;out.x+=s.jitterX;out.y+=s.jitterY;
        }
    }
    if(realSetViewportWithCount)
        realSetViewportWithCount(cb,count,redirect?&out:views);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_ui_scissor_with_count(
    VkCommandBuffer cb,uint32_t count,const VkRect2D* rects) {
    bool redirect=false;
    VkRect2D out{};
    if(count==1 && rects) {
        std::lock_guard lock{uiMutex};
        auto& s=cmds[cb];
        s.scissor=*rects;s.haveScissor=true;s.scissorWithCount=true;
        redirect=s.uiPass;
        if(redirect)out=scaled(*rects);
    }
    if(realSetScissorWithCount)
        realSetScissorWithCount(cb,count,redirect?&out:rects);
}
extern "C" PFN_vkVoidFunction bs4_port_ui_wrap_proc(
    const char* name,PFN_vkVoidFunction proc){
    if(!name||!proc)return proc;
#define UI_WRAP(original,api,fn) \
    if(!std::strcmp(name,api)){original=reinterpret_cast<decltype(original)>(proc); \
        return reinterpret_cast<PFN_vkVoidFunction>(fn);}
    UI_WRAP(realObjectName,"vkSetDebugUtilsObjectNameEXT",bs4_port_ui_name)
    UI_WRAP(realCreatePipelines,"vkCreateGraphicsPipelines",bs4_port_ui_create_pipelines)
    UI_WRAP(realDestroyPipeline,"vkDestroyPipeline",bs4_port_ui_destroy_pipeline)
    UI_WRAP(realBindPipeline,"vkCmdBindPipeline",bs4_port_ui_bind_pipeline)
    UI_WRAP(realSetViewport,"vkCmdSetViewport",bs4_port_ui_viewport)
    UI_WRAP(realSetScissor,"vkCmdSetScissor",bs4_port_ui_scissor)
    UI_WRAP(realSetViewportWithCount,"vkCmdSetViewportWithCount",bs4_port_ui_viewport_with_count)
    UI_WRAP(realSetScissorWithCount,"vkCmdSetScissorWithCount",bs4_port_ui_scissor_with_count)
    UI_WRAP(realSetViewportWithCount,"vkCmdSetViewportWithCountEXT",bs4_port_ui_viewport_with_count)
    UI_WRAP(realSetScissorWithCount,"vkCmdSetScissorWithCountEXT",bs4_port_ui_scissor_with_count)
#undef UI_WRAP
    return proc;
}

extern "C" void bs4_port_ui_free_surfaces() {
    VkDevice dev=VK_NULL_HANDLE;
    VkPhysicalDevice phys=VK_NULL_HANDLE;
    if(!bs4_fsr31_ui_device(&dev,&phys) || !dev)return;
    std::lock_guard lock{uiMutex};
    // Called only after FSR backend's vkDeviceWaitIdle() on resize/rebuild.
    for(auto& [_,d]:uiDepth) {
        if(d.view)vkDestroyImageView(dev,d.view,nullptr);
        if(d.image)vkDestroyImage(dev,d.image,nullptr);
        if(d.memory)vkFreeMemory(dev,d.memory,nullptr);
    }
    uiDepth.clear();lastOutput.clear();completedHud.clear();currentUi={};
}
