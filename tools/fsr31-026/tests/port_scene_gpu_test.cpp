// SPDX-License-Identifier: GPL-2.0-or-later
// Executes the actual bridge, cropped scene/depth copies, camera shader and
// AMD FSR 3.1 dispatch on a software Vulkan device; this is not a device test.
#include <fstream>
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
int main(int argc,char** argv){
 setenv("BS4_FSR31_TEST_OWNER","025",1);
 const bool quality=argc>1&&std::strcmp(argv[1],"quality-1x")==0;
 const bool queued=argc>1&&std::strcmp(argv[1],"queued-cbs")==0;
 const bool computeProbe=argc>1&&std::strcmp(argv[1],"compute-state")==0;
 const bool stencil=argc>1&&std::strcmp(argv[1],"depth-stencil")==0;
 const uint32_t width=quality?1280:640,height=quality?720:360;
 const VkImageAspectFlags depthAspects=VK_IMAGE_ASPECT_DEPTH_BIT|(stencil?VK_IMAGE_ASPECT_STENCIL_BIT:0);
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
 allocate(color,VK_FORMAT_R8G8B8A8_UNORM,VK_IMAGE_ASPECT_COLOR_BIT,cv);allocate(depth,stencil?VK_FORMAT_D32_SFLOAT_S8_UINT:VK_FORMAT_D32_SFLOAT,VK_IMAGE_ASPECT_DEPTH_BIT,dv);
 VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};pci.queueFamilyIndex=choice.queueFamily;pci.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;VkCommandPool pool{};check(vkCreateCommandPool(device,&pci,nullptr,&pool));VkCommandBufferAllocateInfo cai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};cai.commandPool=pool;cai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cai.commandBufferCount=1;VkCommandBuffer cb{};check(vkAllocateCommandBuffers(device,&cai,&cb));ReadbackBuffer read{};assert(createReadbackBuffer(choice.device,device,1280*720*8,&read));
 VkBuffer probeBuffer{};VkDeviceMemory probeMemory{};VkDescriptorSet probeSet{};
 VkPipelineLayout probeLayout{};VkPipeline probePipeline{};
 auto nativeBind=(PFN_vkCmdBindPipeline)vkGetDeviceProcAddr(device,"vkCmdBindPipeline");
 auto nativeSets=(PFN_vkCmdBindDescriptorSets)vkGetDeviceProcAddr(device,"vkCmdBindDescriptorSets");
 auto nativeConstants=(PFN_vkCmdPushConstants)vkGetDeviceProcAddr(device,"vkCmdPushConstants");
 if(computeProbe){
  VkBufferCreateInfo bc{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};bc.size=4;bc.usage=VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
  check(vkCreateBuffer(device,&bc,nullptr,&probeBuffer));VkMemoryRequirements req{};vkGetBufferMemoryRequirements(device,probeBuffer,&req);
  VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=req.size;
  ai.memoryTypeIndex=findMemoryType(choice.device,req.memoryTypeBits,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
  check(vkAllocateMemory(device,&ai,nullptr,&probeMemory));check(vkBindBufferMemory(device,probeBuffer,probeMemory,0));
  void* initial{};check(vkMapMemory(device,probeMemory,0,4,0,&initial));*static_cast<uint32_t*>(initial)=0;vkUnmapMemory(device,probeMemory);
  VkDescriptorSetLayoutBinding binding{0,VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,1,VK_SHADER_STAGE_COMPUTE_BIT,nullptr};
  VkDescriptorSetLayoutCreateInfo sl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};sl.bindingCount=1;sl.pBindings=&binding;
  VkDescriptorSetLayout layout{};check(vkCreateDescriptorSetLayout(device,&sl,nullptr,&layout));
  VkDescriptorPoolSize size{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,1};VkDescriptorPoolCreateInfo dp{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};dp.maxSets=1;dp.poolSizeCount=1;dp.pPoolSizes=&size;
  VkDescriptorPool descriptors{};check(vkCreateDescriptorPool(device,&dp,nullptr,&descriptors));
  VkDescriptorSetAllocateInfo sa{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};sa.descriptorPool=descriptors;sa.descriptorSetCount=1;sa.pSetLayouts=&layout;
  check(vkAllocateDescriptorSets(device,&sa,&probeSet));VkDescriptorBufferInfo buffer{probeBuffer,0,4};VkWriteDescriptorSet write{VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};write.dstSet=probeSet;write.descriptorCount=1;write.descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;write.pBufferInfo=&buffer;
  vkUpdateDescriptorSets(device,1,&write,0,nullptr);
  VkPushConstantRange range{VK_SHADER_STAGE_ALL,0,4};VkPipelineLayoutCreateInfo pl{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};pl.setLayoutCount=1;pl.pSetLayouts=&layout;pl.pushConstantRangeCount=1;pl.pPushConstantRanges=&range;
  check(vkCreatePipelineLayout(device,&pl,nullptr,&probeLayout));
  std::ifstream input("/tmp/native-compute-probe.spv",std::ios::binary|std::ios::ate);assert(input);
  const auto bytes=input.tellg();std::vector<uint32_t> words((size_t(bytes)+3)/4);input.seekg(0);input.read(reinterpret_cast<char*>(words.data()),bytes);
  VkShaderModuleCreateInfo sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};sm.codeSize=size_t(bytes);sm.pCode=words.data();VkShaderModule module{};check(vkCreateShaderModule(device,&sm,nullptr,&module));
  VkComputePipelineCreateInfo cp{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};cp.stage={VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};cp.stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;cp.stage.module=module;cp.stage.pName="main";cp.layout=probeLayout;
  check(vkCreateComputePipelines(device,VK_NULL_HANDLE,1,&cp,nullptr,&probePipeline));vkDestroyShaderModule(device,module,nullptr);
 }
 auto trackedSubmit=(PFN_vkQueueSubmit)vkGetDeviceProcAddr(device,"vkQueueSubmit");
 std::array<VkCommandBuffer,12> batch{};if(queued){cai.commandBufferCount=batch.size();check(vkAllocateCommandBuffers(device,&cai,batch.data()));}
 VkImageLayout sourceLayout=VK_IMAGE_LAYOUT_UNDEFINED;
 for(unsigned frame=0;frame<12;frame++){
  if(queued)cb=batch[frame];
  check(vkResetCommandBuffer(cb,0));VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};check(vkBeginCommandBuffer(cb,&bi));
  layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,sourceLayout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);VkClearColorValue orange{{1.f,.25f,0.f,1.f}};VkImageSubresourceRange range{VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};vkCmdClearColorImage(cb,color.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&orange,1,&range);
  layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);VkRenderingAttachmentInfo att{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};att.imageView=cv;att.imageLayout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;att.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;att.storeOp=VK_ATTACHMENT_STORE_OP_STORE;VkRenderingInfo ri{VK_STRUCTURE_TYPE_RENDERING_INFO};ri.renderArea.extent={width,height};ri.layerCount=1;ri.colorAttachmentCount=1;ri.pColorAttachments=&att;vkCmdBeginRendering(cb,&ri);VkClearAttachment clear{};clear.aspectMask=VK_IMAGE_ASPECT_COLOR_BIT;clear.clearValue.color={{.1f,.2f,.9f,1.f}};VkClearRect rect{{{0,0},{width,height}},0,1};vkCmdClearAttachments(cb,1,&clear,1,&rect);vkCmdEndRendering(cb);layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
  layout(cb,depth.image,depthAspects,sourceLayout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);VkClearDepthStencilValue z{.5f,0};range.aspectMask=depthAspects;vkCmdClearDepthStencilImage(cb,depth.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&z,1,&range);layout(cb,depth.image,depthAspects,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
  std::array<float,216> camera{};camera[0]=3000;camera[1]=1.f/3000;camera[4]=float(width);camera[5]=float(height);
  for(int i=0;i<3;i++)camera[8+i*5]=camera[180+i*5]=1;
  camera[52]=2;camera[57]=3;camera[62]=1.0001f;camera[63]=-.1f;
  Bs4PortSceneFrame handoff{sizeof(handoff),1,frame+1,7,cb,dv,5,{1920,1080},camera.data(),sizeof(camera),1,-1,0,0};assert(bs4_fsr31_port_scene(&handoff));
  FfxVkPortableDeviceInfo owned{};owned.structSize=sizeof(owned);owned.instance=instance;owned.physicalDevice=choice.device;owned.device=device;owned.queue=queue;owned.queueFamilyIndex=choice.queueFamily;owned.getDeviceProcAddr=vkGetDeviceProcAddr;owned.synchronization2Enabled=VK_TRUE;owned.shaderStorageImageWriteWithoutFormatEnabled=VK_TRUE;
  const uint32_t expectedProbe=0x12340000u+frame;
  if(computeProbe){nativeBind(cb,VK_PIPELINE_BIND_POINT_COMPUTE,probePipeline);nativeSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,probeLayout,0,1,&probeSet,0,nullptr);nativeConstants(cb,probeLayout,VK_SHADER_STAGE_ALL,0,4,&expectedProbe);}
  const auto result=bs4_fsr31_generic_render(&owned,cb,cv,{width,height},{1280,720},4,0,1,dv);
  if(!frame){assert(!result);check(vkEndCommandBuffer(cb));VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cb;check(trackedSubmit(queue,1,&submit,nullptr));check(vkQueueWaitIdle(queue));sourceLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;bs4_fsr31_port_end_frame();continue;}
  if(queued&&frame==5){
   if(result){
    std::fputs("UNSAFE: fifth recorded temporal dispatch reused an unsubmitted slot\n",stderr);
    check(vkEndCommandBuffer(cb));VkSubmitInfo unsafe{VK_STRUCTURE_TYPE_SUBMIT_INFO};unsafe.commandBufferCount=5;unsafe.pCommandBuffers=batch.data()+1;
    trackedSubmit(queue,1,&unsafe,nullptr);vkQueueWaitIdle(queue);
    if(validationErrors)std::fputs("REPRODUCED: descriptor reuse invalidated a recorded native command buffer\n",stderr);
    return 42;
   }
   check(vkEndCommandBuffer(cb));
   VkSubmitInfo batchInfo{VK_STRUCTURE_TYPE_SUBMIT_INFO};batchInfo.commandBufferCount=4;batchInfo.pCommandBuffers=batch.data()+1;
   check(trackedSubmit(queue,1,&batchInfo,nullptr));check(vkQueueWaitIdle(queue));
   assert(validationErrors==0);std::puts("PASS four queued FSR CBs remain executable; fifth safely declines before slot reuse; zero validation errors");break;
  }
  assert(result);
  if(computeProbe){
   // Emulate the native cache: dispatch again WITHOUT rebinding the native
   // pipeline, sets or constants after the SDK's AMD compute passes.
   vkCmdDispatch(cb,1,1,1);VkMemoryBarrier2 memory{VK_STRUCTURE_TYPE_MEMORY_BARRIER_2};
   memory.srcStageMask=VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT;memory.srcAccessMask=VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT;
   memory.dstStageMask=VK_PIPELINE_STAGE_2_HOST_BIT;memory.dstAccessMask=VK_ACCESS_2_HOST_READ_BIT;
   VkDependencyInfo dep{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};dep.memoryBarrierCount=1;dep.pMemoryBarriers=&memory;vkCmdPipelineBarrier2(cb,&dep);
  }
  const auto view=reinterpret_cast<VkImageView>(result);VkImage out=bs4_fsr31_output_image(view);assert(out);
  layout(cb,out,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);VkBufferImageCopy copy{};copy.imageSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};copy.imageExtent={1280,720,1};vkCmdCopyImageToBuffer(cb,out,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,read.buffer,1,&copy);layout(cb,out,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);check(vkEndCommandBuffer(cb));
  if(queued){sourceLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;bs4_fsr31_port_end_frame();continue;}
  VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cb;check(trackedSubmit(queue,1,&submit,nullptr));check(vkQueueWaitIdle(queue));
  if(computeProbe){void* value{};check(vkMapMemory(device,probeMemory,0,4,0,&value));if(*static_cast<uint32_t*>(value)!=expectedProbe)std::fprintf(stderr,"native compute probe mismatch actual=%08x expected=%08x\n",*static_cast<uint32_t*>(value),expectedProbe);
   assert(*static_cast<uint32_t*>(value)==expectedProbe);vkUnmapMemory(device,probeMemory);std::printf("PASS cached native compute after AMD frame=%u value=%08x\n",frame,expectedProbe);}
  void* mapped{};check(vkMapMemory(device,read.memory,0,read.allocationSize,0,&mapped));if(!(read.memoryProperties&VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)){VkMappedMemoryRange mr{VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE};mr.memory=read.memory;mr.size=VK_WHOLE_SIZE;check(vkInvalidateMappedMemoryRanges(device,1,&mr));}auto half=(const uint16_t*)mapped;size_t blue=0;for(size_t i=0;i<1280*720;i++)blue+=(half[i*4+2]>0x3a66&&half[i*4+2]<0x3d00&&half[i*4]<0x34cd);assert(blue>1280*720*99/100);std::printf("PASS frame=%u real FSR3.1 camera dispatch blue_pixels=%zu/921600; upper-left scene/depth crop preserved\n",frame,blue);vkUnmapMemory(device,read.memory);sourceLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;bs4_fsr31_port_end_frame();
 }
 assert(validationErrors==0);std::puts("PASS: zero Vulkan validation errors; actual R13-based camera shader + AMD FSR dispatch");
 return 0;
}
