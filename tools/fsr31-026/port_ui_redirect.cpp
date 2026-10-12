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
    bool jitterActive=false;
    float jitterX=0,jitterY=0;
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
PFN_vkSetDebugUtilsObjectNameEXT realObjectName{};
PFN_vkCreateGraphicsPipelines realCreatePipelines{};
PFN_vkDestroyPipeline realDestroyPipeline{};
PFN_vkCmdBindPipeline realBindPipeline{};
PFN_vkCmdSetViewport realSetViewport{};
PFN_vkCmdSetScissor realSetScissor{};
PFN_vkCmdBeginRendering realBegin{};
PFN_vkCmdEndRendering realEnd{};
PFN_vkCmdBeginRenderingKHR realBeginKHR{};
PFN_vkCmdEndRenderingKHR realEndKHR{};
bool firstReport=false;

bool uiShader(uint64_t hash){
    return hash==0x34e8a281ULL||hash==0x81d336ceULL||
           hash==0x09957251ULL||hash==0x24042a9bULL||
           hash==0xa400228bULL||hash==0xbb4d5f8cULL||
           hash==0xe94b5b06ULL||hash==0x9951d199ULL||
           hash==0x44072322ULL||hash==0xa334a845ULL;
}
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
extern "C" int bs4_port_ui_apply_camera_jitter(
    VkCommandBuffer cb,float x,float y) {
    if(!cb || !std::isfinite(x) || !std::isfinite(y) ||
       std::abs(x)>0.501f || std::abs(y)>0.501f || !realSetViewport)
        return 0;
    std::lock_guard lock{uiMutex};
    const auto it=cmds.find(cb);
    if(it==cmds.end())return 0;
    auto& s=it->second;
    if(!s.inside || s.uiPhase || !s.haveViewport ||
       s.guest.colorAttachmentCount<2 || !s.hasDepth ||
       s.guest.renderArea.extent.width>1280 ||
       s.guest.renderArea.extent.height>720)return 0;
    if(s.jitterActive)return 1;
    VkViewport p=s.viewport;
    p.x+=x;p.y+=y;
    realSetViewport(cb,0,1,&p);
    s.jitterActive=true;s.jitterX=x;s.jitterY=y;
    return 1;
}
extern "C" int bs4_port_jitter_for_pass(VkExtent2D,float*,float*);
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
    std::lock_guard lock{uiMutex};
    auto it=lastOutput.find(cb);
    return it==lastOutput.end() || !completedHud.count(cb)?
           VK_NULL_HANDLE:it->second;
}
extern "C" void bs4_port_ui_finish_present(VkCommandBuffer cb){
    std::lock_guard lock{uiMutex};
    lastOutput.erase(cb);
    completedHud.erase(cb);
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
       state.guest.colorAttachmentCount!=1 || state.color.size()!=1)
        return false;
    state.hudColor[0]=state.color[0];
    state.hudColor[0].imageView=output;
    state.hudColor[0].imageLayout=VK_IMAGE_LAYOUT_GENERAL;
    state.hudColor[0].loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
    state.hudColor[0].resolveImageView=VK_NULL_HANDLE;
    state.hudColor[0].resolveMode=VK_RESOLVE_MODE_NONE;
    result=state.guest;
    result.renderArea.offset={0,0};
    result.renderArea.extent={1280,720};
    result.pColorAttachments=state.hudColor.data();
    if(state.hasDepth) {
        state.hudDepth=state.depth;
        state.hudDepth.imageView=depth.view;
        state.hudDepth.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
        state.hudDepth.loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;
        state.hudDepth.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
        result.pDepthAttachment=&state.hudDepth;
    }
    if(state.hasStencil) {
        state.hudStencil=state.stencil;
        state.hudStencil.imageView=depth.view;
        state.hudStencil.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
        state.hudStencil.loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;
        state.hudStencil.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
        result.pStencilAttachment=&state.hudStencil;
    }
    return true;
}
bool safeOriginal(State& s){
    if(!s.inside || s.uiPhase || s.guest.renderArea.offset.x ||
       s.guest.renderArea.offset.y ||
       s.guest.renderArea.extent.width!=1920 ||
       s.guest.renderArea.extent.height!=1080 ||
       s.color.size()!=1 || !s.color[0].imageView ||
       s.color[0].storeOp!=VK_ATTACHMENT_STORE_OP_STORE ||
       s.color[0].resolveImageView || s.guest.pNext ||
       !s.haveViewport || !s.haveScissor)return false;
    Bs4FsrCaptureImage target{};
    if(!bs4_fsr31_capture_image(s.color[0].imageView,&target) ||
       target.format!=VK_FORMAT_R8G8B8A8_UNORM)return false;
    // Do not splice when the shader declares stencil but no matching
    // proxy image can be allocated, or when attachment samples are invalid.
    return true;
}
}
// Host rendering wrappers from original core024 call here before begin/end.
extern "C" bool bs4_port_ui_redirect_begin(
    VkCommandBuffer cb,const VkRenderingInfo* input,bool khr,
    VkRenderingInfo* output) {
    if(!cb||!input||!output)return false;
    std::lock_guard lock{uiMutex};
    State& s=cmds[cb];
    s.inside=true;s.khr=khr;s.guest=*input;
    s.color.clear();
    if(input->pColorAttachments && input->colorAttachmentCount)
        s.color.assign(input->pColorAttachments,
                       input->pColorAttachments+input->colorAttachmentCount);
    s.hasDepth=input->pDepthAttachment!=nullptr;
    s.hasStencil=input->pStencilAttachment!=nullptr;
    if(s.hasDepth)s.depth=*input->pDepthAttachment;
    if(s.hasStencil)s.stencil=*input->pStencilAttachment;
    // The Port jitters G-buffer geometry BEFORE the first draw. Once a real
    // previous Bloodborne camera identifies this pass, apply the port's
    // Halton offset at the pass boundary, and restore it at pass end.
    if(!s.uiPhase && s.hasDepth && input->colorAttachmentCount>=2) {
        float jx=0,jy=0;
        if(bs4_port_jitter_for_pass(input->renderArea.extent,&jx,&jy)) {
            s.jitterActive=true;s.jitterX=jx;s.jitterY=jy;
            if(s.haveViewport && realSetViewport) {
                VkViewport p=s.viewport;p.x+=jx;p.y+=jy;
                realSetViewport(cb,0,1,&p);
            }
        }
    }
    if(s.uiPhase && s.originalUI && input->colorAttachmentCount==1 &&
       input->pColorAttachments && input->pColorAttachments[0].imageView==s.originalUI) {
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
        }
    }
    s.uiPass=false;
    if(s.jitterActive && realSetViewport) {
        realSetViewport(cb,0,1,&s.viewport);
        s.jitterActive=false;s.jitterX=s.jitterY=0;
    }
}
// Called before the first positively identified guest UI draw, while inside
// original dynamic rendering. Replaces the pass with a 720p guest HUD pass.
extern "C" bool bs4_port_ui_try_activate(VkCommandBuffer cb) {
    std::unique_lock lock{uiMutex};
    const auto it=cmds.find(cb);
    if(it==cmds.end() || !shaderBoundUI[cb])return false;
    State& s=it->second;
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
    if(!end_fn || !begin_fn || !realSetViewport || !realSetScissor)return false;

    // Only now is it safe to end the original game UI pass. The actual LDR
    // scene, matching G-buffer depth, and camera must all be present.
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
    VkFormat originalFmt=VK_FORMAT_UNDEFINED;
    if(s.hasDepth||s.hasStencil) {
        Bs4FsrCaptureImage originalDepth{};
        const VkImageView d=s.hasDepth?s.depth.imageView:s.stencil.imageView;
        if(bs4_fsr31_capture_image(d,&originalDepth))
            originalFmt=originalDepth.format;
    }
    Depth& depth=uiDepth[out];
    if(originalFmt!=VK_FORMAT_UNDEFINED && !depth.image)
        if(!createDepth(out,originalFmt,depth)) {
            VkRenderingInfo resume=s.guest;
            for(auto& a:s.color)a.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
            resume.pColorAttachments=s.color.data();begin_fn(cb,&resume);
            return false;
        }
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
    realSetViewport(cb,0,1,&vp);
    realSetScissor(cb,0,1,&sc);
    s.uiPhase=true;s.uiPass=true;s.originalUI=s.color[0].imageView;
    s.output=out;s.everRedirected=true;
    lastOutput[cb]=out;
    completedHud.erase(cb); // Do not present while guest is still drawing.
    if(!firstReport) {
        firstReport=true;
        std::fprintf(stderr,
            "[BS4_PORT] FIRST_REAL_RUNSCALED_UI scene=640x360 "
            "output=1280x720 shader_verified=1 guest_UI_preserved=1\n");
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
            bool eligible=false;
            for(uint32_t j=0;j<cis[i].stageCount;j++){
                const auto& st=cis[i].pStages[j];
                if(st.stage!=VK_SHADER_STAGE_VERTEX_BIT)continue;
                const auto h=guestHashes.find(st.module);
                if(h!=guestHashes.end()&&uiShader(h->second))eligible=true;
            }
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
        redirect=s.uiPass; if(redirect)out=scaled(*rect);
    }
    if(realSetScissor)
        realSetScissor(cb,first,count,redirect?&out:rect);
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
    uiDepth.clear();lastOutput.clear();completedHud.clear();
}
