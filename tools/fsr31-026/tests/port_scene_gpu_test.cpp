// SPDX-License-Identifier: GPL-2.0-or-later
// Executes the actual bridge, cropped scene/depth copies, camera shader and
// AMD FSR 3.1 dispatch on a software Vulkan device; this is not a device test.
#define FFX_VK_PORTABLE_ONLY
#define main sdk_smoke_main
#include "tests/fsr3_vk_backend_smoke.cpp"
#undef main
#include "../vulkan_capture.h"
#include "../port_scene_frame.h"
#include "../port_camera_constants.h"
#include <cassert>
extern "C" int bs4_fsr31_attach(void*,void*,VkDevice,void*,uint32_t);
extern "C" uint64_t bs4_fsr31_generic_render(const FfxVkPortableDeviceInfo*,VkCommandBuffer,VkImageView,VkExtent2D,VkExtent2D,int,int,int,VkImageView);
extern "C" VkImage bs4_fsr31_output_image(VkImageView);
static unsigned validationErrors=0;
static VKAPI_ATTR VkBool32 VKAPI_CALL portDebugCallback(VkDebugUtilsMessageSeverityFlagBitsEXT severity,VkDebugUtilsMessageTypeFlagsEXT,const VkDebugUtilsMessengerCallbackDataEXT* data,void*) {
 if(severity&VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT){validationErrors++;std::fprintf(stderr,"VALIDATION: %s\n",data->pMessage);}return VK_FALSE;
}
static void check(VkResult r){if(r!=VK_SUCCESS){std::fprintf(stderr,"Vulkan error=%d\n",r);std::abort();}}
static PFN_vkCmdPipelineBarrier2 trackedBarrier;
static void layout(VkCommandBuffer cb,VkImage image,VkImageAspectFlags aspect,VkImageLayout from,VkImageLayout to){
 VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};b.srcStageMask=b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;b.srcAccessMask=b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;b.oldLayout=from;b.newLayout=to;b.image=image;b.srcQueueFamilyIndex=b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.subresourceRange={aspect,0,1,0,1};VkDependencyInfo d{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};d.imageMemoryBarrierCount=1;d.pImageMemoryBarriers=&b;trackedBarrier(cb,&d);
}
int main(int argc,char**){
 setenv("BS4_FSR31_TEST_OWNER","025",1);
 const uint32_t width=argc>1?1280:640,height=argc>1?720:360;
 setenv("BACHATA_FSR31_MODE","4",1);setenv("BACHATA_FSR31_INPUT","port",1);
 VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};app.apiVersion=VK_API_VERSION_1_3;VkInstanceCreateInfo ici{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};ici.pApplicationInfo=&app;
 const char* layer="VK_LAYER_KHRONOS_validation";const char* extension=VK_EXT_DEBUG_UTILS_EXTENSION_NAME;ici.enabledLayerCount=1;ici.ppEnabledLayerNames=&layer;ici.enabledExtensionCount=1;ici.ppEnabledExtensionNames=&extension;
 VkDebugUtilsMessengerCreateInfoEXT dbg{VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};dbg.messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;dbg.messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT|VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT|VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;dbg.pfnUserCallback=portDebugCallback;ici.pNext=&dbg;VkInstance instance{};
 auto createInstance=(PFN_vkCreateInstance)vkGetInstanceProcAddr(nullptr,"vkCreateInstance");check(createInstance(&ici,nullptr,&instance));
 VkDebugUtilsMessengerEXT messenger{};auto createDebug=(PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(instance,"vkCreateDebugUtilsMessengerEXT");check(createDebug(instance,&dbg,nullptr,&messenger));
 const auto choice=choosePhysicalDevice(instance);assert(choice.device);VkPhysicalDeviceVulkan13Features v13{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES};v13.synchronization2=v13.dynamicRendering=VK_TRUE;VkPhysicalDeviceFeatures2 f2{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2};f2.pNext=&v13;f2.features.shaderStorageImageWriteWithoutFormat=VK_TRUE;
 float priority=1;VkDeviceQueueCreateInfo qci{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};qci.queueFamilyIndex=choice.queueFamily;qci.queueCount=1;qci.pQueuePriorities=&priority;VkDeviceCreateInfo dci{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};dci.pNext=&f2;dci.queueCreateInfoCount=1;dci.pQueueCreateInfos=&qci;VkDevice device{};
 auto createDevice=(PFN_vkCreateDevice)vkGetInstanceProcAddr(instance,"vkCreateDevice");check(createDevice(choice.device,&dci,nullptr,&device));assert(bs4_fsr31_attach((void*)1,(void*)1,device,nullptr,3)==0);
 VkQueue queue{};vkGetDeviceQueue(device,choice.queueFamily,0,&queue);trackedBarrier=(PFN_vkCmdPipelineBarrier2)vkGetDeviceProcAddr(device,"vkCmdPipelineBarrier2");
 auto makeImage=(PFN_vkCreateImage)vkGetDeviceProcAddr(device,"vkCreateImage");auto makeView=(PFN_vkCreateImageView)vkGetDeviceProcAddr(device,"vkCreateImageView");
 TestImage color{},depth{};VkImageView cv{},dv{};
 auto allocate=[&](TestImage& t,VkFormat format,VkImageAspectFlags aspect,VkImageView& view){
  auto& ci=t.createInfo;ci={VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};ci.imageType=VK_IMAGE_TYPE_2D;ci.format=format;ci.extent={1920,1080,1};ci.mipLevels=ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;ci.tiling=VK_IMAGE_TILING_OPTIMAL;ci.usage=VK_IMAGE_USAGE_TRANSFER_SRC_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|(aspect==VK_IMAGE_ASPECT_COLOR_BIT?VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT:VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT);check(makeImage(device,&ci,nullptr,&t.image));VkMemoryRequirements req{};vkGetImageMemoryRequirements(device,t.image,&req);VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=req.size;ai.memoryTypeIndex=findMemoryType(choice.device,req.memoryTypeBits,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);check(vkAllocateMemory(device,&ai,nullptr,&t.memory));check(vkBindImageMemory(device,t.image,t.memory,0));VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};vi.image=t.image;vi.viewType=VK_IMAGE_VIEW_TYPE_2D;vi.format=format;vi.subresourceRange={aspect,0,1,0,1};check(makeView(device,&vi,nullptr,&view));
 };
 allocate(color,VK_FORMAT_R8G8B8A8_UNORM,VK_IMAGE_ASPECT_COLOR_BIT,cv);allocate(depth,VK_FORMAT_D32_SFLOAT,VK_IMAGE_ASPECT_DEPTH_BIT,dv);
 VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};pci.queueFamilyIndex=choice.queueFamily;pci.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;VkCommandPool pool{};check(vkCreateCommandPool(device,&pci,nullptr,&pool));VkCommandBufferAllocateInfo cai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};cai.commandPool=pool;cai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cai.commandBufferCount=1;VkCommandBuffer cb{};check(vkAllocateCommandBuffers(device,&cai,&cb));ReadbackBuffer read{};assert(createReadbackBuffer(choice.device,device,1280*720*8,&read));
 VkImageLayout sourceLayout=VK_IMAGE_LAYOUT_UNDEFINED;
 for(unsigned frame=0;frame<12;frame++){
  check(vkResetCommandBuffer(cb,0));VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};check(vkBeginCommandBuffer(cb,&bi));
  layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,sourceLayout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);VkClearColorValue orange{{1.f,.25f,0.f,1.f}};VkImageSubresourceRange range{VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};vkCmdClearColorImage(cb,color.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&orange,1,&range);
  layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);VkRenderingAttachmentInfo att{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};att.imageView=cv;att.imageLayout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;att.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;att.storeOp=VK_ATTACHMENT_STORE_OP_STORE;VkRenderingInfo ri{VK_STRUCTURE_TYPE_RENDERING_INFO};ri.renderArea.extent={width,height};ri.layerCount=1;ri.colorAttachmentCount=1;ri.pColorAttachments=&att;vkCmdBeginRendering(cb,&ri);VkClearAttachment clear{};clear.aspectMask=VK_IMAGE_ASPECT_COLOR_BIT;clear.clearValue.color={{.1f,.2f,.9f,1.f}};VkClearRect rect{{{0,0},{width,height}},0,1};vkCmdClearAttachments(cb,1,&clear,1,&rect);vkCmdEndRendering(cb);layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
  layout(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,sourceLayout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);VkClearDepthStencilValue z{.5f,0};range.aspectMask=VK_IMAGE_ASPECT_DEPTH_BIT;vkCmdClearDepthStencilImage(cb,depth.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&z,1,&range);layout(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
  std::array<float,216> camera{};camera[0]=3000;camera[1]=1.f/3000;camera[4]=float(width);camera[5]=float(height);
  for(int i=0;i<3;i++)camera[8+i*5]=camera[180+i*5]=1;
  camera[52]=2;camera[57]=3;camera[62]=1.0001f;camera[63]=-.1f;
  Bs4PortSceneFrame handoff{sizeof(handoff),1,frame+1,7,cb,dv,5,{1920,1080},camera.data(),sizeof(camera),1,-1,0,0};assert(bs4_fsr31_port_scene(&handoff));
  FfxVkPortableDeviceInfo owned{};owned.structSize=sizeof(owned);owned.instance=instance;owned.physicalDevice=choice.device;owned.device=device;owned.queue=queue;owned.queueFamilyIndex=choice.queueFamily;owned.getDeviceProcAddr=vkGetDeviceProcAddr;owned.synchronization2Enabled=VK_TRUE;owned.shaderStorageImageWriteWithoutFormatEnabled=VK_TRUE;
  const auto result=bs4_fsr31_generic_render(&owned,cb,cv,{width,height},{1280,720},4,0,1,dv);
  if(!frame){assert(!result);check(vkEndCommandBuffer(cb));VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cb;check(vkQueueSubmit(queue,1,&submit,nullptr));check(vkQueueWaitIdle(queue));sourceLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;bs4_fsr31_port_end_frame();continue;}
  assert(result);const auto view=reinterpret_cast<VkImageView>(result);VkImage out=bs4_fsr31_output_image(view);assert(out);
  layout(cb,out,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);VkBufferImageCopy copy{};copy.imageSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};copy.imageExtent={1280,720,1};vkCmdCopyImageToBuffer(cb,out,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,read.buffer,1,&copy);layout(cb,out,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);check(vkEndCommandBuffer(cb));VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cb;check(vkQueueSubmit(queue,1,&submit,nullptr));check(vkQueueWaitIdle(queue));
  void* mapped{};check(vkMapMemory(device,read.memory,0,read.allocationSize,0,&mapped));if(!(read.memoryProperties&VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)){VkMappedMemoryRange mr{VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE};mr.memory=read.memory;mr.size=VK_WHOLE_SIZE;check(vkInvalidateMappedMemoryRanges(device,1,&mr));}auto half=(const uint16_t*)mapped;size_t blue=0;for(size_t i=0;i<1280*720;i++)blue+=(half[i*4+2]>0x3a66&&half[i*4+2]<0x3d00&&half[i*4]<0x34cd);assert(blue>1280*720*99/100);std::printf("PASS frame=%u real FSR3.1 camera dispatch blue_pixels=%zu/921600; upper-left scene/depth crop preserved\n",frame,blue);vkUnmapMemory(device,read.memory);sourceLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;bs4_fsr31_port_end_frame();
 }
 assert(validationErrors==0);std::puts("PASS: zero Vulkan validation errors; actual R13-based camera shader + AMD FSR dispatch");
 return 0;
}
