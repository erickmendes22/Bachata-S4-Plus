// SPDX-License-Identifier: GPL-2.0-or-later
#include <cassert>
#include <map>
#include <string>
#include "../fsr31-026/port_ui_redirect.cpp"
namespace {
const auto cb=(VkCommandBuffer)0x100;
const auto scene=(VkImageView)0x200,depthView=(VkImageView)0x300,out=(VkImageView)0x400;
// Separate real LDR scene and native-sized UI image: the R27 GPU test
// incorrectly used the SAME VkImage for both and missed the impossible check.
const auto ldr=(VkImageView)0x201;
bool ready=true,failDepth=false;
int ended=0,began=0,dispatches=0;
VkAttachmentLoadOp seenStencil=VK_ATTACHMENT_LOAD_OP_DONT_CARE;
VkAttachmentLoadOp seenDepth=VK_ATTACHMENT_LOAD_OP_DONT_CARE;
VkViewport seenViewport{};
VkRect2D seenScissor{};
unsigned countedViewports=0,countedScissors=0;
void VKAPI_PTR viewport_count(VkCommandBuffer,uint32_t count,const VkViewport* v){
    ++countedViewports;
    assert(count==1);
    seenViewport=*v;
}
void VKAPI_PTR scissor_count(VkCommandBuffer,uint32_t count,const VkRect2D* s){
    ++countedScissors;
    assert(count==1);
    seenScissor=*s;
}
void VKAPI_PTR begin(VkCommandBuffer,const VkRenderingInfo* info){++began;if(info->pStencilAttachment)seenStencil=info->pStencilAttachment->loadOp;if(info->pDepthAttachment)seenDepth=info->pDepthAttachment->loadOp;}
void VKAPI_PTR end(VkCommandBuffer){++ended;}
void VKAPI_PTR viewport(VkCommandBuffer,uint32_t,uint32_t,const VkViewport* v){seenViewport=*v;}
void VKAPI_PTR scissor(VkCommandBuffer,uint32_t,uint32_t,const VkRect2D* s){seenScissor=*s;}
VkResult VKAPI_PTR pipelines(VkDevice,VkPipelineCache,uint32_t n,const VkGraphicsPipelineCreateInfo*,const VkAllocationCallbacks*,VkPipeline* p){for(uint32_t i=0;i<n;i++)p[i]=(VkPipeline)0x500;return VK_SUCCESS;}
void start(bool withCount=false){
 cmds.clear();uiDepth.clear();currentUi={};shaderBoundUI.clear();lastOutput.clear();completedHud.clear();ended=began=dispatches=0;
 bs4_port_ui_install_rendering(begin,end,nullptr,nullptr);
 realSetViewport=withCount?nullptr:viewport;
 realSetScissor=withCount?nullptr:scissor;
 realSetViewportCount=nullptr;realSetScissorCount=nullptr;
 countedViewports=countedScissors=0;
 VkRenderingAttachmentInfo color{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};color.imageView=scene;color.imageLayout=VK_IMAGE_LAYOUT_GENERAL;color.storeOp=VK_ATTACHMENT_STORE_OP_STORE;color.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
 VkRenderingAttachmentInfo z{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};z.imageView=depthView;z.storeOp=VK_ATTACHMENT_STORE_OP_STORE;z.loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;
 VkRenderingInfo info{VK_STRUCTURE_TYPE_RENDERING_INFO};info.renderArea.extent={1920,1080};info.layerCount=1;info.colorAttachmentCount=1;info.pColorAttachments=&color;info.pDepthAttachment=info.pStencilAttachment=&z;VkRenderingInfo redirected{};assert(!bs4_port_ui_redirect_begin(cb,&info,false,&redirected));
 const VkViewport vp{0,0,1920,1080,0,1};
 const VkRect2D sc{{0,0},{1920,1080}};
 if(withCount) {
     const auto setV=reinterpret_cast<PFN_vkCmdSetViewportWithCount>(
         bs4_port_ui_wrap_proc("vkCmdSetViewportWithCount",
         reinterpret_cast<PFN_vkVoidFunction>(viewport_count)));
     const auto setS=reinterpret_cast<PFN_vkCmdSetScissorWithCount>(
         bs4_port_ui_wrap_proc("vkCmdSetScissorWithCount",
         reinterpret_cast<PFN_vkVoidFunction>(scissor_count)));
     assert(setV && setS);
     setV(cb,1,&vp);setS(cb,1,&sc);
     assert(cmds[cb].viewportWithCount && cmds[cb].scissorWithCount);
 } else {
     bs4_port_ui_viewport(cb,0,1,&vp);bs4_port_ui_scissor(cb,0,1,&sc);
 }
 VkPipelineDepthStencilStateCreateInfo ds{VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO};ds.stencilTestEnable=VK_TRUE;VkPipelineColorBlendAttachmentState blend{};blend.blendEnable=VK_TRUE;VkPipelineColorBlendStateCreateInfo bs{VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};bs.attachmentCount=1;bs.pAttachments=&blend;VkGraphicsPipelineCreateInfo ci{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};ci.pDepthStencilState=&ds;ci.pColorBlendState=&bs;VkPipeline p{};realCreatePipelines=pipelines;assert(bs4_port_ui_create_pipelines(nullptr,nullptr,1,&ci,nullptr,&p)==VK_SUCCESS);bs4_port_ui_bind_pipeline(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,p);
}
}
extern "C" uint64_t bs4_port_frame_generation(){return 1;}
extern "C" int bs4_fsr31_capture_image(VkImageView v,Bs4FsrCaptureImage* i){if(v==ldr){*i={(VkImage)0x601,VK_FORMAT_R8G8B8A8_UNORM,{640,360},VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT|VK_IMAGE_USAGE_TRANSFER_SRC_BIT,VK_IMAGE_LAYOUT_GENERAL,VK_IMAGE_ASPECT_COLOR_BIT};return 1;}if(v==scene){*i={(VkImage)0x600,VK_FORMAT_R8G8B8A8_UNORM,{1920,1080},VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT|VK_IMAGE_USAGE_TRANSFER_SRC_BIT,VK_IMAGE_LAYOUT_GENERAL,VK_IMAGE_ASPECT_COLOR_BIT};return 1;}if(v==depthView){*i={(VkImage)0x700,VK_FORMAT_D32_SFLOAT_S8_UINT,{1920,1080},VK_IMAGE_USAGE_TRANSFER_SRC_BIT,VK_IMAGE_LAYOUT_GENERAL,VK_IMAGE_ASPECT_DEPTH_BIT|VK_IMAGE_ASPECT_STENCIL_BIT};return 1;}return 0;}
extern "C" VkImageView bs4_port_scene_color(VkCommandBuffer){return ldr;}
extern "C" VkImageView bs4_port_current_scene(VkCommandBuffer,VkExtent2D* s){*s={640,360};return depthView;}
extern "C" int bs4_port_can_prepare_ui(VkCommandBuffer){return ready;}
extern "C" VkImageView bs4_port_prepared_output(VkCommandBuffer){return ready?out:VK_NULL_HANDLE;}
extern "C" VkImageView bs4_port_prepare_ui(VkCommandBuffer){++dispatches;return out;}
extern "C" VkImage bs4_fsr31_output_image(VkImageView v){return v==out?(VkImage)0x800:VK_NULL_HANDLE;}
extern "C" int bs4_fsr31_set_output_layout(VkImageView,VkImageLayout){return 1;}
extern "C" int bs4_fsr31_ui_device(VkDevice* d,VkPhysicalDevice* p){*d=(VkDevice)1;*p=(VkPhysicalDevice)1;return 1;}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL vkCreateImage(VkDevice,const VkImageCreateInfo*,const VkAllocationCallbacks*,VkImage* image){*image=(VkImage)0x900;return failDepth?VK_ERROR_OUT_OF_DEVICE_MEMORY:VK_SUCCESS;}
extern "C" VKAPI_ATTR void VKAPI_CALL vkGetImageMemoryRequirements(VkDevice,VkImage,VkMemoryRequirements* r){*r={4096,16,1};}
extern "C" VKAPI_ATTR void VKAPI_CALL vkGetPhysicalDeviceMemoryProperties(VkPhysicalDevice,VkPhysicalDeviceMemoryProperties* p){*p={};p->memoryTypeCount=1;p->memoryTypes[0].propertyFlags=VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL vkAllocateMemory(VkDevice,const VkMemoryAllocateInfo*,const VkAllocationCallbacks*,VkDeviceMemory* m){*m=(VkDeviceMemory)0xa00;return VK_SUCCESS;}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL vkBindImageMemory(VkDevice,VkImage,VkDeviceMemory,VkDeviceSize){return VK_SUCCESS;}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL vkCreateImageView(VkDevice,const VkImageViewCreateInfo*,const VkAllocationCallbacks*,VkImageView* v){*v=(VkImageView)0xb00;return VK_SUCCESS;}
extern "C" VKAPI_ATTR void VKAPI_CALL vkCmdPipelineBarrier2(VkCommandBuffer,const VkDependencyInfo*){}
int main(){
 ready=false;start();assert(!bs4_port_ui_try_activate(cb));assert(!ended&&!began&&!dispatches);
 ready=true;failDepth=true;start();assert(!bs4_port_ui_try_activate(cb));assert(!ended&&!began&&!dispatches);
 failDepth=false;start();assert(bs4_port_ui_try_activate(cb));assert(ended==1&&began==1&&dispatches==1);assert(seenStencil==VK_ATTACHMENT_LOAD_OP_CLEAR&&seenDepth==VK_ATTACHMENT_LOAD_OP_CLEAR);assert(seenViewport.width==1280&&seenViewport.height==720);assert(!bs4_port_ui_present(cb));bs4_port_ui_redirect_end(cb);assert(bs4_port_ui_present((VkCommandBuffer)0x101)==out);assert(bs4_port_ui_redirect_sampled((VkCommandBuffer)0x101,scene)==out);
 // Modern core025 Vulkan 1.3 dynamic-state commands must activate the
 // exact same FSR/UI transaction, scale only the HUD, and restore state.
 start(true);
 assert(bs4_port_ui_try_activate(cb));
 assert(seenViewport.width==1280 && seenViewport.height==720);
 assert(seenScissor.extent.width==1280 && seenScissor.extent.height==720);
 assert(countedViewports>=2 && countedScissors>=2);
 bs4_port_ui_redirect_end(cb);
 assert(seenViewport.width==1920 && seenViewport.height==1080);
 assert(seenScissor.extent.width==1920 && seenScissor.extent.height==1080);
 assert(bs4_port_ui_present((VkCommandBuffer)0x101)==out);
 // The 640x360 scene must be DISTINCT from the 1920x1080 guest UI, while
 // the latter gets redirected only after FSR success. A mistaken scene
 // alias must never be presented as the final full-size HUD image.
 assert(currentUi.color==(VkImage)0x600);
 assert(ldr!=scene);
 // A later stencil-only mask and a later color pass keep prior UI stencil.
 VkRenderingAttachmentInfo z{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};z.imageView=depthView;z.storeOp=VK_ATTACHMENT_STORE_OP_STORE;VkRenderingInfo mask{VK_STRUCTURE_TYPE_RENDERING_INFO};mask.renderArea.extent={1920,1080};mask.layerCount=1;mask.pDepthAttachment=mask.pStencilAttachment=&z;VkRenderingInfo redirected{};assert(bs4_port_ui_redirect_begin((VkCommandBuffer)0x101,&mask,false,&redirected));assert(redirected.colorAttachmentCount==0);assert(redirected.pStencilAttachment->loadOp==VK_ATTACHMENT_LOAD_OP_LOAD);assert(redirected.pDepthAttachment->loadOp==VK_ATTACHMENT_LOAD_OP_LOAD);
 puts("PASS: no guest pass interruption on missing FSR or failed proxy allocation; one real handoff; completed-only presentation; subsequent stencil masks preserved with LOAD");
}
