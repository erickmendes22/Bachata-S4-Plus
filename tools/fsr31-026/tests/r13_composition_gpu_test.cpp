// SPDX-License-Identifier: GPL-2.0-or-later
// Cross-command-buffer test preserves actual submission order; no synthetic camera handoff.
// Actual camera observer -> R13 pre-UI boundary -> AMD dispatch -> original
// guest UI attachment. GPU clears stand in for scene/HUD draws in this test;
// it does not execute Bloodborne or prove stability on Adreno.
#define FFX_VK_PORTABLE_ONLY
#define main sdk_smoke_main
#include "tests/fsr3_vk_backend_smoke.cpp"
#undef main
#include "../native_scene_observer.h"
#include "../port_scene_frame.h"
#include "../vulkan_capture.h"
#include "../native_ui_targets.h"
#include <array>
#include <cassert>
extern "C" int bs4_fsr31_attachment_ready();
extern "C" void bs4_fsr31_native_begin(void*,const void*,uintptr_t);
extern "C" void bs4_fsr31_native_pipeline(const void*);
extern "C" int bs4_fsr31_pre_ui_prepare(VkCommandBuffer,VkImageView,VkImageView,VkExtent2D,VkExtent2D);
static unsigned errors=0;
static VKAPI_ATTR VkBool32 VKAPI_CALL validate(VkDebugUtilsMessageSeverityFlagBitsEXT s,VkDebugUtilsMessageTypeFlagsEXT,const VkDebugUtilsMessengerCallbackDataEXT* d,void*) {if(s&VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT){errors++;std::fprintf(stderr,"VALIDATION: %s\n",d->pMessage);}return VK_FALSE;}
static void checked(VkResult r){assert(r==VK_SUCCESS);}
static PFN_vkCmdPipelineBarrier2 barrier;
static void transition(VkCommandBuffer cb,VkImage image,VkImageAspectFlags aspect,VkImageLayout old,VkImageLayout next) {
 VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};b.srcStageMask=b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;b.srcAccessMask=b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;b.oldLayout=old;b.newLayout=next;b.image=image;b.srcQueueFamilyIndex=b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.subresourceRange={aspect,0,1,0,1};VkDependencyInfo d{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};d.imageMemoryBarrierCount=1;d.pImageMemoryBarriers=&b;barrier(cb,&d);
}
int main(int argc,char** argv){
 const bool partial=argc==2&&std::strcmp(argv[1],"partial-same-layout")==0;
 const bool discarded=argc==2&&std::strcmp(argv[1],"discarded-color")==0;
 const bool depthAccess=argc==2&&std::strcmp(argv[1],"depth-access")==0;
 const bool depthClear=argc==2&&std::strcmp(argv[1],"depth-clear")==0;
 const bool localWrite=argc==2&&std::strcmp(argv[1],"same-cb-overwrite")==0;
 const bool automatic=argc==2&&std::strcmp(argv[1],"owned-ui")==0;
 const bool rewrite=argc==2&&std::strcmp(argv[1],"cross-cb-rewrite")==0;
 const bool cross=rewrite||(argc==2&&std::strcmp(argv[1],"cross-cb")==0);
 const bool runScaled=automatic||(argc==2&&std::strcmp(argv[1],"run-scaled-ui")==0);
 setenv("BACHATA_FSR31_NATIVE_UI",(cross||localWrite||depthAccess||depthClear||partial||discarded)?"0":"1",1);
 const bool shared=runScaled||(argc==2&&std::strcmp(argv[1],"shared-target")==0);
 const uint32_t uiWidth=runScaled?1280:(shared?640:1920),uiHeight=runScaled?720:(shared?360:1080);
 setenv("BS4_FSR31_TEST_OWNER","025",1);
 setenv("BACHATA_FSR31_MODE","4",1);unsetenv("BACHATA_FSR31_INPUT");
 const char* layer="VK_LAYER_KHRONOS_validation";const char* ext=VK_EXT_DEBUG_UTILS_EXTENSION_NAME;
 VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};app.apiVersion=VK_API_VERSION_1_3;
 VkDebugUtilsMessengerCreateInfoEXT debug{VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};debug.messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;debug.messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT|VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT;debug.pfnUserCallback=validate;
 VkInstanceCreateInfo ici{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};ici.pApplicationInfo=&app;ici.pNext=&debug;ici.enabledLayerCount=1;ici.ppEnabledLayerNames=&layer;ici.enabledExtensionCount=1;ici.ppEnabledExtensionNames=&ext;VkInstance instance{};auto createInstance=(PFN_vkCreateInstance)vkGetInstanceProcAddr(nullptr,"vkCreateInstance");checked(createInstance(&ici,nullptr,&instance));assert(std::getenv("BACHATA_FSR31_INPUT")&&std::strcmp(std::getenv("BACHATA_FSR31_INPUT"),"port")==0);VkDebugUtilsMessengerEXT messenger{};auto createDebug=(PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(instance,"vkCreateDebugUtilsMessengerEXT");checked(createDebug(instance,&debug,nullptr,&messenger));
 const auto choice=choosePhysicalDevice(instance);assert(choice.device);
 VkPhysicalDeviceVulkan13Features f13{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES};f13.synchronization2=f13.dynamicRendering=VK_TRUE;
 VkPhysicalDeviceFeatures2 f2{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2};f2.pNext=&f13;f2.features.shaderStorageImageWriteWithoutFormat=VK_TRUE;
 float priority=1;VkDeviceQueueCreateInfo qci{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};qci.queueFamilyIndex=choice.queueFamily;qci.queueCount=1;qci.pQueuePriorities=&priority;VkDeviceCreateInfo dci{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};dci.pNext=&f2;dci.queueCreateInfoCount=1;dci.pQueueCreateInfos=&qci;const char* pushExt=VK_KHR_PUSH_DESCRIPTOR_EXTENSION_NAME;dci.enabledExtensionCount=1;dci.ppEnabledExtensionNames=&pushExt;VkDevice device{};auto createDevice=(PFN_vkCreateDevice)vkGetInstanceProcAddr(instance,"vkCreateDevice");checked(createDevice(choice.device,&dci,nullptr,&device));assert(bs4_fsr31_attachment_ready()==1);
 VkQueue queue{};vkGetDeviceQueue(device,choice.queueFamily,0,&queue);
 auto createImage=(PFN_vkCreateImage)vkGetDeviceProcAddr(device,"vkCreateImage");auto createView=(PFN_vkCreateImageView)vkGetDeviceProcAddr(device,"vkCreateImageView");barrier=(PFN_vkCmdPipelineBarrier2)vkGetDeviceProcAddr(device,"vkCmdPipelineBarrier2");auto begin=(PFN_vkCmdBeginRendering)vkGetDeviceProcAddr(device,"vkCmdBeginRendering");auto end=(PFN_vkCmdEndRendering)vkGetDeviceProcAddr(device,"vkCmdEndRendering");auto beginCommand=(PFN_vkBeginCommandBuffer)vkGetDeviceProcAddr(device,"vkBeginCommandBuffer");auto resetCommand=(PFN_vkResetCommandBuffer)vkGetDeviceProcAddr(device,"vkResetCommandBuffer");auto setViewport=(PFN_vkCmdSetViewport)vkGetDeviceProcAddr(device,"vkCmdSetViewport");auto setScissor=(PFN_vkCmdSetScissor)vkGetDeviceProcAddr(device,"vkCmdSetScissor");auto pushConstants=(PFN_vkCmdPushConstants)vkGetDeviceProcAddr(device,"vkCmdPushConstants");auto pushDescriptors=(PFN_vkCmdPushDescriptorSetKHR)vkGetDeviceProcAddr(device,"vkCmdPushDescriptorSetKHR");auto objectName=(PFN_vkSetDebugUtilsObjectNameEXT)vkGetDeviceProcAddr(device,"vkSetDebugUtilsObjectNameEXT");
 struct Image {VkImage image{};VkDeviceMemory memory{};VkImageView view{};VkImageLayout layout=VK_IMAGE_LAYOUT_UNDEFINED;};
 auto image=[&](VkFormat format,VkImageAspectFlags aspect,uint32_t w,uint32_t h){Image out{};VkImageCreateInfo ci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};ci.imageType=VK_IMAGE_TYPE_2D;ci.format=format;ci.extent={w,h,1};ci.mipLevels=ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;ci.tiling=VK_IMAGE_TILING_OPTIMAL;ci.usage=VK_IMAGE_USAGE_TRANSFER_SRC_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|(aspect==VK_IMAGE_ASPECT_COLOR_BIT?VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT:VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT);checked(createImage(device,&ci,nullptr,&out.image));VkMemoryRequirements req{};vkGetImageMemoryRequirements(device,out.image,&req);VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=req.size;ai.memoryTypeIndex=findMemoryType(choice.device,req.memoryTypeBits,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);checked(vkAllocateMemory(device,&ai,nullptr,&out.memory));checked(vkBindImageMemory(device,out.image,out.memory,0));VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};vi.image=out.image;vi.viewType=VK_IMAGE_VIEW_TYPE_2D;vi.format=format;vi.subresourceRange={aspect,0,1,0,1};checked(createView(device,&vi,nullptr,&out.view));return out;};
 std::array<Image,5> colors;for(auto& c:colors)c=image(VK_FORMAT_R8G8B8A8_UNORM,VK_IMAGE_ASPECT_COLOR_BIT,640,360);auto depth=image(VK_FORMAT_D32_SFLOAT,VK_IMAGE_ASPECT_DEPTH_BIT,640,360);auto scene=image(VK_FORMAT_R8G8B8A8_UNORM,VK_IMAGE_ASPECT_COLOR_BIT,640,360);auto ui=shared&&!runScaled?scene:image(VK_FORMAT_R8G8B8A8_UNORM,VK_IMAGE_ASPECT_COLOR_BIT,uiWidth,uiHeight);auto uiDepth=runScaled?image(VK_FORMAT_D32_SFLOAT,VK_IMAGE_ASPECT_DEPTH_BIT,1280,720):Image{};
 auto allocate=(PFN_vkAllocateMemory)vkGetDeviceProcAddr(device,"vkAllocateMemory");auto map=(PFN_vkMapMemory)vkGetDeviceProcAddr(device,"vkMapMemory");auto bind=(PFN_vkBindBufferMemory)vkGetDeviceProcAddr(device,"vkBindBufferMemory");
 VkBufferCreateInfo bc{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};bc.size=864;bc.usage=VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT;VkBuffer uniform{};checked(vkCreateBuffer(device,&bc,nullptr,&uniform));VkMemoryRequirements br{};vkGetBufferMemoryRequirements(device,uniform,&br);VkMemoryAllocateInfo ba{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ba.allocationSize=br.size;ba.memoryTypeIndex=findMemoryType(choice.device,br.memoryTypeBits,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);VkDeviceMemory bm{};checked(allocate(device,&ba,nullptr,&bm));checked(bind(device,uniform,bm,0));void* data{};checked(map(device,bm,0,VK_WHOLE_SIZE,0,&data));std::array<float,216> camera{};camera[0]=3000;camera[1]=1.f/3000;camera[4]=640;camera[5]=360;for(int i=0;i<3;i++)camera[8+i*5]=camera[180+i*5]=1;camera[52]=2;camera[57]=3;camera[62]=1.0001f;camera[63]=-.1f;std::memcpy(data,camera.data(),sizeof(camera));
 VkDescriptorSetLayoutBinding binding{0,VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,1,VK_SHADER_STAGE_VERTEX_BIT,nullptr};VkDescriptorSetLayoutCreateInfo sl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};sl.flags=VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR;sl.bindingCount=1;sl.pBindings=&binding;VkDescriptorSetLayout setLayout{};checked(vkCreateDescriptorSetLayout(device,&sl,nullptr,&setLayout));VkPushConstantRange range{VK_SHADER_STAGE_VERTEX_BIT,0,120};VkPipelineLayoutCreateInfo pl{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};pl.setLayoutCount=1;pl.pSetLayouts=&setLayout;pl.pushConstantRangeCount=1;pl.pPushConstantRanges=&range;VkPipelineLayout geometry{},movie{};checked(vkCreatePipelineLayout(device,&pl,nullptr,&geometry));checked(vkCreatePipelineLayout(device,&pl,nullptr,&movie));std::array<unsigned char,0xc0> nativePipeline{};std::array<unsigned char,0x1d50> nativeVertexInfo{};
 const uintptr_t vertexInfo=reinterpret_cast<uintptr_t>(nativeVertexInfo.data());const uint64_t movieHash=0x34e8a281;
 std::memcpy(nativePipeline.data()+0x60,&movie,sizeof(movie));std::memcpy(nativePipeline.data()+0xa0,&vertexInfo,8);std::memcpy(nativeVertexInfo.data()+0x1d38,&movieHash,8);
 bs4_fsr31_native_pipeline(nativePipeline.data()); // no vkSetDebugUtilsObjectName for this layout

 VkDescriptorBufferInfo uniformInfo{uniform,0,864};VkWriteDescriptorSet write{VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};write.dstBinding=0;write.descriptorCount=1;write.descriptorType=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;write.pBufferInfo=&uniformInfo;std::array<float,30> raw{};raw[0]=320;raw[1]=180;raw[2]=320;raw[3]=-180;VkViewport viewport{0,360,640,-360,0,1};
 VkCommandPoolCreateInfo pc{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};pc.queueFamilyIndex=choice.queueFamily;pc.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;VkCommandPool pool{};checked(vkCreateCommandPool(device,&pc,nullptr,&pool));VkCommandBufferAllocateInfo cbai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};cbai.commandPool=pool;cbai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cbai.commandBufferCount=1;VkCommandBuffer cb{};checked(vkAllocateCommandBuffers(device,&cbai,&cb));
 VkCommandBuffer uiCb{};if(cross)checked(vkAllocateCommandBuffers(device,&cbai,&uiCb));
 VkImageView aliasScene{};
 if(rewrite){
    VkImageViewCreateInfo av{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    av.image=scene.image;av.viewType=VK_IMAGE_VIEW_TYPE_2D;
    av.format=VK_FORMAT_R8G8B8A8_UNORM;
    av.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
    checked(createView(device,&av,nullptr,&aliasScene));
 }
 auto submitProc=(PFN_vkQueueSubmit)vkGetDeviceProcAddr(device,"vkQueueSubmit");assert(submitProc);
 ReadbackBuffer read{};assert(createReadbackBuffer(choice.device,device,uiWidth*uiHeight*4,&read));
 for(unsigned frame=0;frame<8;frame++){
  checked(resetCommand(cb,0));VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};checked(beginCommand(cb,&bi));pushDescriptors(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,geometry,0,1,&write);pushConstants(cb,geometry,VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());setViewport(cb,0,1,&viewport);if(automatic){VkRect2D scissor{{0,0},{640,360}};setScissor(cb,0,1,&scissor);}
  std::array<VkRenderingAttachmentInfo,5> attachments{};for(unsigned i=0;i<5;i++){transition(cb,colors[i].image,VK_IMAGE_ASPECT_COLOR_BIT,colors[i].layout,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);attachments[i]={VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};attachments[i].imageView=colors[i].view;attachments[i].imageLayout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;attachments[i].loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;attachments[i].storeOp=VK_ATTACHMENT_STORE_OP_STORE;attachments[i].clearValue.color={{.1f,.2f,.9f,1.f}};colors[i].layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;}
  transition(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,depth.layout,VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL);VkRenderingAttachmentInfo da{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};da.imageView=depth.view;da.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;da.loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;da.storeOp=VK_ATTACHMENT_STORE_OP_STORE;da.clearValue.depthStencil={.5f,0};VkRenderingInfo ri{VK_STRUCTURE_TYPE_RENDERING_INFO};ri.renderArea.extent={1920,1080};ri.layerCount=1;ri.colorAttachmentCount=5;ri.pColorAttachments=attachments.data();ri.pDepthAttachment=&da;begin(cb,&ri);end(cb);depth.layout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
  VkImageView observed{};VkExtent2D observedSize{};assert(bs4_native_scene_camera(cb,&observed,&observedSize)&&observed==depth.view&&observedSize.width==640);
  transition(cb,scene.image,VK_IMAGE_ASPECT_COLOR_BIT,scene.layout,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);VkRenderingAttachmentInfo ldr=attachments[0];ldr.imageView=scene.view;if(discarded)ldr.storeOp=VK_ATTACHMENT_STORE_OP_DONT_CARE;ri.colorAttachmentCount=1;ri.pColorAttachments=&ldr;ri.pDepthAttachment=nullptr;begin(cb,&ri);if(!shared)end(cb);scene.layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
  if(partial){
   // No barrier: begin another pass in the unchanged COLOR_ATTACHMENT
   // layout, write only the upper half, and leave the rest intact.
   VkRenderingAttachmentInfo top=ldr;top.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
   ri.renderArea.extent={640,180};ri.pColorAttachments=&top;begin(cb,&ri);
   VkClearAttachment cyan{};cyan.aspectMask=VK_IMAGE_ASPECT_COLOR_BIT;
   cyan.clearValue.color={{0.f,1.f,1.f,1.f}};
   VkClearRect topRect{{{0,0},{640,180}},0,1};vkCmdClearAttachments(cb,1,&cyan,1,&topRect);end(cb);
   ri.renderArea.extent={1920,1080};ri.pColorAttachments=&ldr;
  }
  if(partial||discarded){
   VkImageView c{},d{};VkExtent2D size{};
   if(!std::getenv("BS4_TEST_KEEP_PARTIAL_SCENE"))assert(!bs4_fsr31_capture_scene(cb,&c,&d,&size));
  }
  if(depthAccess||depthClear){
   VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};b.image=depth.image;
   b.oldLayout=depth.layout;b.newLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_READ_ONLY_OPTIMAL;
   b.srcStageMask=b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
   b.srcAccessMask=b.dstAccessMask=VK_ACCESS_2_DEPTH_STENCIL_ATTACHMENT_READ_BIT|VK_ACCESS_2_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;
   b.srcQueueFamilyIndex=b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.subresourceRange={VK_IMAGE_ASPECT_DEPTH_BIT,0,1,0,1};
   VkDependencyInfo dep{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};dep.imageMemoryBarrierCount=1;dep.pImageMemoryBarriers=&b;barrier(cb,&dep);depth.layout=b.newLayout;
   VkImageView c{},d{};VkExtent2D size{};assert(bs4_fsr31_capture_scene(cb,&c,&d,&size));
   if(depthClear){
    transition(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,depth.layout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    VkClearDepthStencilValue value{1.f,0};VkImageSubresourceRange range{VK_IMAGE_ASPECT_DEPTH_BIT,0,1,0,1};
    auto clear=(PFN_vkCmdClearDepthStencilImage)vkGetDeviceProcAddr(device,"vkCmdClearDepthStencilImage");clear(cb,depth.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&value,1,&range);depth.layout=VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    assert(!bs4_fsr31_capture_scene(cb,&c,&d,&size));
   }
  }
  if(localWrite){
   transition(cb,scene.image,VK_IMAGE_ASPECT_COLOR_BIT,scene.layout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
   VkClearColorValue cyan{{0.f,1.f,1.f,1.f}};VkImageSubresourceRange range{VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
   vkCmdClearColorImage(cb,scene.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&cyan,1,&range);
   transition(cb,scene.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);scene.layout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
   VkImageView staleColor{},staleDepth{};VkExtent2D staleSize{};
   if(!std::getenv("BS4_TEST_KEEP_REWRITTEN_LOCAL_SCENE"))assert(!bs4_fsr31_capture_scene(cb,&staleColor,&staleDepth,&staleSize));
  }
  // Cross-CB: first submit the 3D command buffer on the single graphics
  // queue; only then record the UI in another command buffer.
  const VkCommandBuffer sceneCb=cb;
  if(cross) {
    checked(vkEndCommandBuffer(cb));
    VkSubmitInfo first{VK_STRUCTURE_TYPE_SUBMIT_INFO};
    first.commandBufferCount=1;first.pCommandBuffers=&sceneCb;
    checked(submitProc(queue,1,&first,nullptr));checked(vkQueueWaitIdle(queue));
    cb=uiCb;checked(resetCommand(cb,0));VkCommandBufferBeginInfo biUi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};checked(beginCommand(cb,&biUi));
  }
  if(rewrite){
    // A later guest render pass overwrites the submitted LDR color image.
    VkRenderingAttachmentInfo aliasLdr=ldr;aliasLdr.imageView=aliasScene;
    ri.renderArea.extent={640,360};ri.pColorAttachments=&aliasLdr;
    begin(cb,&ri);end(cb);
    ri.renderArea.extent={1920,1080};ri.pColorAttachments=&ldr;
  }
  // Separate-target case starts a new UI pass. Shared-target case reuses
  // the existing rendering instance, as the native scheduler may do.
  // This is a preservation test, not proof of shared-target FSR support.
  pushConstants(cb,movie,VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());assert(bs4_native_scene_ui_boundary(cb));
  if(cross) {
    // The actual native shader is identified on this second CB. It does
    // not enqueue scheduler callbacks or pretend to record scene pixels.
    Bs4NativeRenderState separateHud{};
    separateHud.width=uiWidth;separateHud.height=uiHeight;separateHud.layers=1;
    separateHud.colorCount=1;separateHud.colors[0].view=reinterpret_cast<uint64_t>(ui.view);
    bs4_native_scene_draw_state(cb,separateHud);
  }
  // In shared mode this is inside the original LDR rendering instance.
  // Validation catches any GPU command accidentally emitted by preparation.
  if(!cross&&!localWrite&&!depthClear&&!partial&&!discarded)assert(bool(bs4_fsr31_pre_ui_prepare(cb,scene.view,depth.view,{640,360},{1280,720}))==bool(frame));
  std::array<unsigned char,0x1200> nativeScheduler{};const uint64_t nativeCommand=reinterpret_cast<uint64_t>(cb);std::memcpy(nativeScheduler.data()+0xf08,&nativeCommand,8);
  Bs4NativeRenderState nativeState{};nativeState.width=shared?640:uiWidth;nativeState.height=shared?360:uiHeight;nativeState.layers=1;nativeState.colorCount=1;nativeState.colors[0].view=reinterpret_cast<uint64_t>(shared?scene.view:ui.view);if(runScaled){nativeState.depthEnabled=1;nativeState.depth=reinterpret_cast<uint64_t>(depth.view);}
  if(!cross&&!localWrite&&!depthClear&&!partial&&!discarded)bs4_fsr31_native_begin(nativeScheduler.data(),&nativeState,0);
  Bs4NativeUiBoundary nativeBoundary{};
  if(!cross&&!localWrite&&!depthClear&&!partial&&!discarded)assert(bs4_native_scene_ui_state(cb,nativeBoundary)&&nativeBoundary.color==(shared?scene.view:ui.view)&&nativeBoundary.guestExtent.width==nativeState.width);
  if(automatic){
   Bs4FsrCaptureImage owned{};assert(bs4_native_ui_output(cb,owned));
   ui.image=owned.image;ui.view=bs4_native_ui_sampled_view(cb,scene.view);ui.layout=owned.layout;
   // Native scheduler ends and later reopens the same original attachment.
   // The automatic layer must keep the 720p UI image, with LOAD contents.
   end(cb);ldr.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;ri.renderArea.extent={640,360};ri.pColorAttachments=&ldr;begin(cb,&ri);
   const auto alias=bs4_native_ui_sampled_view(cb,scene.view);assert(alias!=scene.view);
   VkImageViewCreateInfo originalView{},aliasView{};
   assert(bs4_fsr31_capture_view(scene.view,&originalView)&&bs4_fsr31_capture_view(alias,&aliasView));
   assert(aliasView.image==ui.image&&aliasView.format==originalView.format&&
          !std::memcmp(&aliasView.components,&originalView.components,sizeof(originalView.components)));
   assert(bs4_native_ui_sampled_view(cb,colors[0].view)==colors[0].view);
  }else if(runScaled){
   // Every rejection must keep the original rendering instance live. The
   // next successful handoff/clear would fail validation if it ended early.
   assert(!bs4_fsr31_run_scaled_ui(cb,scene.view,uiDepth.view));
   assert(!bs4_fsr31_run_scaled_ui(cb,ui.view,VK_NULL_HANDLE));
   assert(!bs4_fsr31_run_scaled_ui(cb,ui.view,depth.view));
   assert(bs4_fsr31_run_scaled_ui(cb,ui.view,uiDepth.view)==(frame?2:1));
  }
  if(!shared)transition(cb,ui.image,VK_IMAGE_ASPECT_COLOR_BIT,ui.layout,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);VkRenderingAttachmentInfo hud=ldr;hud.imageView=ui.view;hud.storeOp=VK_ATTACHMENT_STORE_OP_STORE;hud.clearValue.color=(localWrite||depthClear||partial||discarded)?VkClearColorValue{{.1f,.2f,.9f,1.f}}:VkClearColorValue{{0,0,0,1}};ri.pColorAttachments=&hud;if(!shared)begin(cb,&ri);
  VkClearAttachment red{};red.aspectMask=VK_IMAGE_ASPECT_COLOR_BIT;red.clearValue.color={{1,0,0,1}};VkClearRect rect{{{0,0},{100,50}},0,1};vkCmdClearAttachments(cb,1,&red,1,&rect);end(cb);
  transition(cb,automatic?scene.image:ui.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);VkBufferImageCopy copy{};copy.imageSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};copy.imageExtent={uiWidth,uiHeight,1};vkCmdCopyImageToBuffer(cb,ui.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,read.buffer,1,&copy);ui.layout=VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;if((shared&&!runScaled)||automatic)scene.layout=ui.layout;checked(vkEndCommandBuffer(cb));VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cb;checked(submitProc(queue,1,&submit,nullptr));checked(vkQueueWaitIdle(queue));void* pixels{};checked(vkMapMemory(device,read.memory,0,read.allocationSize,0,&pixels));if(!(read.memoryProperties&VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)){VkMappedMemoryRange r{VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE};r.memory=read.memory;r.size=VK_WHOLE_SIZE;checked(vkInvalidateMappedMemoryRanges(device,1,&r));}const auto rgba=(const unsigned char*)pixels;size_t blue=0,redPixels=0,cyan=0;for(size_t i=0;i<size_t(uiWidth)*uiHeight;i++){blue+=rgba[i*4+2]>180&&rgba[i*4]<80&&rgba[i*4+1]<150;cyan+=rgba[i*4+2]>200&&rgba[i*4+1]>200&&rgba[i*4]<80;redPixels+=rgba[i*4]>240&&rgba[i*4+1]<10&&rgba[i*4+2]<10;}assert(redPixels==5000);if(localWrite&&std::getenv("BS4_TEST_KEEP_REWRITTEN_LOCAL_SCENE")&&frame&&cyan>size_t(uiWidth)*uiHeight/2){
 std::fprintf(stderr,"REPRODUCED stale local scene: cyan=%zu native blue=%zu HUD=%zu preserved\n",cyan,blue,redPixels);vkUnmapMemory(device,read.memory);return 42;}
 if(partial&&std::getenv("BS4_TEST_KEEP_PARTIAL_SCENE")&&frame&&cyan>size_t(uiWidth)*uiHeight/4){
 std::fprintf(stderr,"REPRODUCED stale partial scene: cyan=%zu native blue=%zu HUD=%zu preserved\n",cyan,blue,redPixels);vkUnmapMemory(device,read.memory);return 43;}
 if(localWrite||depthClear||partial||discarded){assert(cyan==0&&blue==size_t(uiWidth)*uiHeight-5000);}else if(rewrite)assert(blue==0);else if(frame||shared)assert(blue==size_t(uiWidth)*uiHeight-5000);std::printf("PASS composition frame=%u blue=%zu red=%zu native_UI_image_preserved=1 shared_target=%u\n",frame,blue,redPixels,unsigned(shared));vkUnmapMemory(device,read.memory);bs4_fsr31_port_end_frame();bs4_native_scene_present();if(cross)cb=sceneCb;
 }
 assert(errors==0);if(automatic){std::puts("PASS automatic native025 UI allocation and dispatch, seven temporal frames, HUD preserved, zero Vulkan errors");return 0;}if(runScaled){std::puts("PASS native same-target UI handoff: camera warmup copy and seven real FSR dispatches into prepared 720p UI target, scene and HUD preserved, zero Vulkan errors");return 0;}if(shared){std::puts("PASS shared-target preservation only: existing rendering instance and HUD intact; temporal shared-target composition remains unsupported");return 0;}std::puts("PASS R13 pre-UI composition: native camera producer, bounds, confirmed movie boundary, real AMD FSR, original guest HUD and zero Vulkan errors");return 0;
}
