// SPDX-License-Identifier: GPL-2.0-or-later
// Executes the actual bridge, cropped scene/depth copies, camera shader and
// AMD FSR 3.1 dispatch on a software Vulkan device; this is not a device test.
#define FFX_VK_PORTABLE_ONLY
#define main sdk_smoke_main
#include "tests/fsr3_vk_backend_smoke.cpp"
#undef main
#include "../fsr31-026/vulkan_capture.h"
#include "../fsr31-026/port_camera_constants.h"
#include <cassert>
#include <fstream>
#include <atomic>
extern "C" uint64_t bs4_fsr31_try_render(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
extern "C" VkImageView bs4_port_ui_present(VkCommandBuffer);
extern "C" VkImage bs4_fsr31_output_image(VkImageView);
extern "C" int bs4_fsr31_attach(void*,void*,VkDevice,void*,uint32_t);
extern "C" int bs4_fsr31_supply_port_camera(VkCommandBuffer,VkImageView,const void*,uint32_t);
extern "C" VkImageView bs4_fsr31_prepare_resources(VkCommandBuffer,VkImageView,VkImageView,VkExtent2D,VkExtent2D);
extern "C" int bs4_fsr31_pre_ui_dispatch(VkCommandBuffer,VkImageView,VkImageView,VkExtent2D,VkExtent2D,VkImage*);
extern "C" int bs4_fsr31_set_output_layout(VkImageView,VkImageLayout);
extern "C" VkImageView bs4_fsr31_output_view(VkImage);
static void check(VkResult r){if(r!=VK_SUCCESS){std::fprintf(stderr,"Vulkan error=%d\n",r);std::abort();}}
static PFN_vkCmdPipelineBarrier2 trackedBarrier;
static void layout(VkCommandBuffer cb,VkImage image,VkImageAspectFlags aspect,VkImageLayout from,VkImageLayout to){
 VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};b.srcStageMask=b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;b.srcAccessMask=b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;b.oldLayout=from;b.newLayout=to;b.image=image;b.srcQueueFamilyIndex=b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.subresourceRange={aspect,0,1,0,1};VkDependencyInfo d{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};d.imageMemoryBarrierCount=1;d.pImageMemoryBarriers=&b;trackedBarrier(cb,&d);
}
static std::atomic<unsigned> boundsErrors{0},validationErrors{0};
static VKAPI_ATTR VkBool32 VKAPI_CALL validation(VkDebugUtilsMessageSeverityFlagBitsEXT severity,VkDebugUtilsMessageTypeFlagsEXT,const VkDebugUtilsMessengerCallbackDataEXT* data,void*) {
 if(severity==VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT && data && validationErrors.fetch_add(1)<20)std::fprintf(stderr,"VULKAN_VALIDATION_ERROR %s\n",data->pMessage);
 if(severity==VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT && data && data->pMessageIdName && (std::strstr(data->pMessageIdName,"06079") || std::strstr(data->pMessageIdName,"06080"))) {++boundsErrors;std::fprintf(stderr,"BOUNDS_VALIDATION_ERROR %s\n",data->pMessage);}
 return VK_FALSE;
}
int main(int argc,char** argv){
 assert(argc==4 || argc==5 || argc==6);
 const bool oversized=argc==6;
 const VkExtent2D allocation=argc>=5?VkExtent2D{640,360}:VkExtent2D{1920,1080};
 const VkExtent2D passArea=oversized?VkExtent2D{1920,1080}:allocation;
 setenv("BACHATA_FSR31_MODE","4",1);
 VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};app.apiVersion=VK_API_VERSION_1_3;VkInstanceCreateInfo ici{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};ici.pApplicationInfo=&app;const char* debugExtension=VK_EXT_DEBUG_UTILS_EXTENSION_NAME;ici.enabledExtensionCount=1;ici.ppEnabledExtensionNames=&debugExtension;VkInstance instance{};
 const char* validationLayer="VK_LAYER_KHRONOS_validation";if(oversized){ici.enabledLayerCount=1;ici.ppEnabledLayerNames=&validationLayer;}
 auto createInstance=(PFN_vkCreateInstance)vkGetInstanceProcAddr(nullptr,"vkCreateInstance");check(createInstance(&ici,nullptr,&instance));
 VkDebugUtilsMessengerEXT messenger{};if(oversized){VkDebugUtilsMessengerCreateInfoEXT debug{VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};debug.messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;debug.messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT;debug.pfnUserCallback=validation;auto createDebug=(PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(instance,"vkCreateDebugUtilsMessengerEXT");assert(createDebug);check(createDebug(instance,&debug,nullptr,&messenger));}
 const auto choice=choosePhysicalDevice(instance);assert(choice.device);VkPhysicalDeviceVulkan13Features v13{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES};v13.synchronization2=v13.dynamicRendering=VK_TRUE;VkPhysicalDeviceFeatures2 f2{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2};f2.pNext=&v13;f2.features.shaderStorageImageWriteWithoutFormat=VK_TRUE;
 float priority=1;VkDeviceQueueCreateInfo qci{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};qci.queueFamilyIndex=choice.queueFamily;qci.queueCount=1;qci.pQueuePriorities=&priority;VkDeviceCreateInfo dci{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};dci.pNext=&f2;dci.queueCreateInfoCount=1;dci.pQueueCreateInfos=&qci;VkDevice device{};
 auto createDevice=(PFN_vkCreateDevice)vkGetInstanceProcAddr(instance,"vkCreateDevice");check(createDevice(choice.device,&dci,nullptr,&device));assert(bs4_fsr31_attach((void*)1,(void*)1,device,nullptr,3)==0);
 VkQueue queue{};vkGetDeviceQueue(device,choice.queueFamily,0,&queue);trackedBarrier=(PFN_vkCmdPipelineBarrier2)vkGetDeviceProcAddr(device,"vkCmdPipelineBarrier2");
 auto makeImage=(PFN_vkCreateImage)vkGetDeviceProcAddr(device,"vkCreateImage");auto makeView=(PFN_vkCreateImageView)vkGetDeviceProcAddr(device,"vkCreateImageView");
 TestImage color{},depth{};VkImageView cv{},dv{};
 auto allocate=[&](TestImage& t,VkFormat format,VkImageAspectFlags aspect,VkImageView& view){
  auto& ci=t.createInfo;ci={VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};ci.imageType=VK_IMAGE_TYPE_2D;ci.format=format;ci.extent={allocation.width,allocation.height,1};ci.mipLevels=ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;ci.tiling=VK_IMAGE_TILING_OPTIMAL;ci.usage=VK_IMAGE_USAGE_TRANSFER_SRC_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|(aspect==VK_IMAGE_ASPECT_COLOR_BIT?VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT:VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT);check(makeImage(device,&ci,nullptr,&t.image));VkMemoryRequirements req{};vkGetImageMemoryRequirements(device,t.image,&req);VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=req.size;ai.memoryTypeIndex=findMemoryType(choice.device,req.memoryTypeBits,VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);check(vkAllocateMemory(device,&ai,nullptr,&t.memory));check(vkBindImageMemory(device,t.image,t.memory,0));VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};vi.image=t.image;vi.viewType=VK_IMAGE_VIEW_TYPE_2D;vi.format=format;vi.subresourceRange={aspect,0,1,0,1};check(makeView(device,&vi,nullptr,&view));
 };
 allocate(color,VK_FORMAT_R8G8B8A8_UNORM,VK_IMAGE_ASPECT_COLOR_BIT,cv);allocate(depth,VK_FORMAT_D32_SFLOAT,VK_IMAGE_ASPECT_DEPTH_BIT,dv);
 VkCommandPoolCreateInfo pci{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};pci.queueFamilyIndex=choice.queueFamily;pci.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;VkCommandPool pool{};check(vkCreateCommandPool(device,&pci,nullptr,&pool));VkCommandBufferAllocateInfo cai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};cai.commandPool=pool;cai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cai.commandBufferCount=1;VkCommandBuffer cb{};check(vkAllocateCommandBuffers(device,&cai,&cb));ReadbackBuffer read{};assert(createReadbackBuffer(choice.device,device,1280*720*4,&read));

 auto beginRendering=(PFN_vkCmdBeginRendering)vkGetDeviceProcAddr(device,"vkCmdBeginRendering");
 auto endRendering=(PFN_vkCmdEndRendering)vkGetDeviceProcAddr(device,"vkCmdEndRendering");
 auto viewport=(PFN_vkCmdSetViewportWithCount)vkGetDeviceProcAddr(device,"vkCmdSetViewportWithCount");
 auto scissor=(PFN_vkCmdSetScissorWithCount)vkGetDeviceProcAddr(device,"vkCmdSetScissorWithCount");
 auto draw=(PFN_vkCmdDraw)vkGetDeviceProcAddr(device,"vkCmdDraw");
 auto bindPipeline=(PFN_vkCmdBindPipeline)vkGetDeviceProcAddr(device,"vkCmdBindPipeline");
 auto bindSets=(PFN_vkCmdBindDescriptorSets)vkGetDeviceProcAddr(device,"vkCmdBindDescriptorSets");
 auto updateSets=(PFN_vkUpdateDescriptorSets)vkGetDeviceProcAddr(device,"vkUpdateDescriptorSets");
 auto mapMemory=(PFN_vkMapMemory)vkGetDeviceProcAddr(device,"vkMapMemory");
 auto bindBuffer=(PFN_vkBindBufferMemory)vkGetDeviceProcAddr(device,"vkBindBufferMemory");
 auto beginCommand=(PFN_vkBeginCommandBuffer)vkGetDeviceProcAddr(device,"vkBeginCommandBuffer");
 auto resetCommand=(PFN_vkResetCommandBuffer)vkGetDeviceProcAddr(device,"vkResetCommandBuffer");
 VkBufferCreateInfo bci{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};bci.size=864;bci.usage=VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT;VkBuffer ubo{};check(vkCreateBuffer(device,&bci,nullptr,&ubo));
 VkMemoryRequirements req{};vkGetBufferMemoryRequirements(device,ubo,&req);VkMemoryAllocateInfo mai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};mai.allocationSize=req.size;mai.memoryTypeIndex=findMemoryType(choice.device,req.memoryTypeBits,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);VkDeviceMemory umem{};check(vkAllocateMemory(device,&mai,nullptr,&umem));check(bindBuffer(device,ubo,umem,0));void* cameraMemory{};check(mapMemory(device,umem,0,864,0,&cameraMemory));
 std::array<float,216> camera{};camera[0]=3000;camera[1]=1.f/3000;camera[4]=640;camera[5]=360;camera[52]=1.4f;camera[57]=2.5f;camera[62]=1.00002f;camera[63]=-.05f;for(int i=0;i<3;i++)camera[8+i*4+i]=camera[180+i*4+i]=1;std::memcpy(cameraMemory,camera.data(),864);
 VkDescriptorSetLayoutBinding binding{0,VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,1,VK_SHADER_STAGE_VERTEX_BIT,nullptr};VkDescriptorSetLayoutCreateInfo lci{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};lci.bindingCount=1;lci.pBindings=&binding;VkDescriptorSetLayout setLayout{};check(vkCreateDescriptorSetLayout(device,&lci,nullptr,&setLayout));
 VkDescriptorPoolSize poolSize{VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,1};VkDescriptorPoolCreateInfo dpci{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};dpci.maxSets=1;dpci.poolSizeCount=1;dpci.pPoolSizes=&poolSize;VkDescriptorPool dpool{};check(vkCreateDescriptorPool(device,&dpci,nullptr,&dpool));VkDescriptorSetAllocateInfo dsai{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};dsai.descriptorPool=dpool;dsai.descriptorSetCount=1;dsai.pSetLayouts=&setLayout;VkDescriptorSet set{};check(vkAllocateDescriptorSets(device,&dsai,&set));VkDescriptorBufferInfo cameraInfo{ubo,0,864};VkWriteDescriptorSet write{VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};write.dstSet=set;write.descriptorCount=1;write.descriptorType=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;write.pBufferInfo=&cameraInfo;updateSets(device,1,&write,0,nullptr);
 VkPipelineLayoutCreateInfo plci{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};plci.setLayoutCount=1;plci.pSetLayouts=&setLayout;VkPipelineLayout pipelineLayout{};check(vkCreatePipelineLayout(device,&plci,nullptr,&pipelineLayout));
 auto shader=[&](const char* path){std::ifstream file(path,std::ios::binary|std::ios::ate);assert(file);const auto size=(size_t)file.tellg();std::vector<uint32_t> words(size/4);file.seekg(0);file.read((char*)words.data(),size);VkShaderModuleCreateInfo smci{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};smci.codeSize=size;smci.pCode=words.data();VkShaderModule module{};check(vkCreateShaderModule(device,&smci,nullptr,&module));return module;};
 VkPipelineShaderStageCreateInfo stages[2]{};for(auto& stage:stages){stage.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;stage.pName="main";}stages[0].stage=VK_SHADER_STAGE_VERTEX_BIT;stages[0].module=shader(argv[1]);stages[1].stage=VK_SHADER_STAGE_FRAGMENT_BIT;stages[1].module=shader(argv[2]);
 VkPipelineVertexInputStateCreateInfo vertexInput{VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};VkPipelineInputAssemblyStateCreateInfo assembly{VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};assembly.topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
 VkPipelineViewportStateCreateInfo viewState{VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};VkPipelineRasterizationStateCreateInfo raster{VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};raster.polygonMode=VK_POLYGON_MODE_FILL;raster.lineWidth=1;raster.cullMode=VK_CULL_MODE_NONE;VkPipelineMultisampleStateCreateInfo ms{VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};ms.rasterizationSamples=VK_SAMPLE_COUNT_1_BIT;
 VkPipelineColorBlendAttachmentState blend{};blend.colorWriteMask=15;blend.blendEnable=VK_FALSE;VkPipelineColorBlendStateCreateInfo blending{VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};blending.attachmentCount=1;blending.pAttachments=&blend;
 const VkDynamicState dynamicStates[]{VK_DYNAMIC_STATE_VIEWPORT_WITH_COUNT,VK_DYNAMIC_STATE_SCISSOR_WITH_COUNT};VkPipelineDynamicStateCreateInfo dynamic{VK_STRUCTURE_TYPE_PIPELINE_DYNAMIC_STATE_CREATE_INFO};dynamic.dynamicStateCount=2;dynamic.pDynamicStates=dynamicStates;
 const VkFormat format=VK_FORMAT_R8G8B8A8_UNORM;VkPipelineRenderingCreateInfo rendering{VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO};rendering.colorAttachmentCount=1;rendering.pColorAttachmentFormats=&format;
 VkGraphicsPipelineCreateInfo graphics{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};graphics.pNext=&rendering;graphics.stageCount=2;graphics.pStages=stages;graphics.pVertexInputState=&vertexInput;graphics.pInputAssemblyState=&assembly;graphics.pViewportState=&viewState;graphics.pRasterizationState=&raster;graphics.pMultisampleState=&ms;graphics.pColorBlendState=&blending;graphics.pDynamicState=&dynamic;graphics.layout=pipelineLayout;graphics.pDepthStencilState=nullptr;
 auto makePipeline=(PFN_vkCreateGraphicsPipelines)vkGetDeviceProcAddr(device,"vkCreateGraphicsPipelines");VkPipeline pipeline{};check(makePipeline(device,VK_NULL_HANDLE,1,&graphics,nullptr,&pipeline));
 // Exercise the actual core-style shader-name -> pipeline -> bind chain.
 auto nameShader=(PFN_vkSetDebugUtilsObjectNameEXT)vkGetDeviceProcAddr(device,"vkSetDebugUtilsObjectNameEXT");assert(nameShader);
 VkDebugUtilsObjectNameInfoEXT name{VK_STRUCTURE_TYPE_DEBUG_UTILS_OBJECT_NAME_INFO_EXT};name.objectType=VK_OBJECT_TYPE_SHADER_MODULE;name.objectHandle=(uint64_t)(uintptr_t)stages[0].module;name.pObjectName="Vertex_0x0000000034e8a281_0";nameShader(device,&name);
 // Recreate after naming, as shadPS4 does when compiling its pipelines.
 check(makePipeline(device,VK_NULL_HANDLE,1,&graphics,nullptr,&pipeline));
 stages[0].module=shader(argv[1]);stages[1].module=shader(argv[3]);
 name.objectHandle=(uint64_t)(uintptr_t)stages[0].module;name.pObjectName="Vertex_0x00000000deadbeef_0";nameShader(device,&name);
 VkPipeline postPipeline{};check(makePipeline(device,VK_NULL_HANDLE,1,&graphics,nullptr,&postPipeline));
 std::array<TestImage,4> mrtImages{};std::array<VkImageView,4> mrtViews{};for(int i=0;i<4;i++)allocate(mrtImages[i],format,VK_IMAGE_ASPECT_COLOR_BIT,mrtViews[i]);
 VkImageLayout colorLayout=VK_IMAGE_LAYOUT_UNDEFINED,depthLayout=VK_IMAGE_LAYOUT_UNDEFINED;
 for(unsigned frame=0;frame<3;frame++){
  check(resetCommand(cb,0));VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};check(beginCommand(cb,&bi));
  layout(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,depthLayout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);VkImageSubresourceRange range{VK_IMAGE_ASPECT_DEPTH_BIT,0,1,0,1};VkClearDepthStencilValue z{.5f,0};vkCmdClearDepthStencilImage(cb,depth.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&z,1,&range);layout(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL);
  layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,colorLayout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);range.aspectMask=VK_IMAGE_ASPECT_COLOR_BIT;VkClearColorValue orange{{1,.25f,0,1}};vkCmdClearColorImage(cb,color.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&orange,1,&range);layout(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);
  std::array<VkRenderingAttachmentInfo,5> colors{};for(int i=0;i<5;i++){auto& a=colors[i];a.sType=VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO;a.imageView=i?mrtViews[i-1]:cv;a.imageLayout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;a.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;a.storeOp=VK_ATTACHMENT_STORE_OP_STORE;if(i)layout(cb,mrtImages[i-1].image,VK_IMAGE_ASPECT_COLOR_BIT,frame?VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL:VK_IMAGE_LAYOUT_UNDEFINED,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);}
  VkRenderingAttachmentInfo d{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};d.imageView=dv;d.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;d.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;d.storeOp=VK_ATTACHMENT_STORE_OP_STORE;VkRenderingInfo ri{VK_STRUCTURE_TYPE_RENDERING_INFO};ri.renderArea.extent=passArea;ri.layerCount=1;ri.colorAttachmentCount=5;ri.pColorAttachments=colors.data();ri.pDepthAttachment=&d;beginRendering(cb,&ri);
  VkViewport vp{0,0,640,360,0,1};VkRect2D sc{{0,0},{640,360}};viewport(cb,1,&vp);scissor(cb,1,&sc);bindSets(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,pipelineLayout,0,1,&set,0,nullptr);endRendering(cb);
  ri.colorAttachmentCount=1;ri.pDepthAttachment=nullptr;ri.renderArea.extent={640,360};beginRendering(cb,&ri);VkClearAttachment clear{};clear.aspectMask=VK_IMAGE_ASPECT_COLOR_BIT;clear.clearValue.color={{.1f,.2f,.9f,1}};VkClearRect rect{{{0,0},{640,360}},0,1};vkCmdClearAttachments(cb,1,&clear,1,&rect);endRendering(cb);
  // Native-sized postprocessing precedes the genuine Scaleform HUD. It
  // must finish on its original target without prematurely dispatching FSR.
  ri.renderArea.extent=passArea;beginRendering(cb,&ri);vp.width=1920;vp.height=1080;sc.extent={1920,1080};viewport(cb,1,&vp);scissor(cb,1,&sc);bindPipeline(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,postPipeline);draw(cb,3,1,0,0);endRendering(cb);assert(!bs4_port_ui_present(cb));
  beginRendering(cb,&ri);vp.width=1920;vp.height=1080;sc.extent={1920,1080};viewport(cb,1,&vp);scissor(cb,1,&sc);bindPipeline(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,pipeline);draw(cb,3,1,0,0);endRendering(cb);
  const auto view=(VkImageView)(uintptr_t)bs4_fsr31_try_render(0,(uint64_t)(uintptr_t)cb,(uint64_t)(uintptr_t)cv,(uint64_t(1080)<<32)|1920,(uint64_t(720)<<32)|1280,0,0);
  if(frame==0)assert(!view);else assert(view);
  if(view){const auto output=bs4_fsr31_output_image(view);assert(output);layout(cb,output,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);bs4_fsr31_set_output_layout(view,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);VkBufferImageCopy copy{};copy.imageSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};copy.imageExtent={1280,720,1};vkCmdCopyImageToBuffer(cb,output,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,read.buffer,1,&copy);}
  Bs4FsrCaptureImage currentColor{},currentDepth{};assert(bs4_fsr31_capture_image(cv,&currentColor)&&bs4_fsr31_capture_image(dv,&currentDepth));colorLayout=currentColor.layout;depthLayout=currentDepth.layout;
  check(vkEndCommandBuffer(cb));VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cb;check(vkQueueSubmit(queue,1,&submit,nullptr));check(vkQueueWaitIdle(queue));
  if(view){void* pixels{};check(vkMapMemory(device,read.memory,0,read.allocationSize,0,&pixels));if(!(read.memoryProperties&VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)){VkMappedMemoryRange mr{VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE};mr.memory=read.memory;mr.size=VK_WHOLE_SIZE;check(vkInvalidateMappedMemoryRanges(device,1,&mr));}const auto bytes=(const uint8_t*)pixels;size_t blue=0,red=0;for(size_t i=0;i<1280*720;i++){blue+=bytes[i*4+2]>180&&bytes[i*4]<80;red+=bytes[i*4]>200&&bytes[i*4+2]<40;}assert(blue>1280*720*98/100);assert(red>1000);std::printf("PASS frame=%u actual hooks: non-UI fullscreen pass preserved -> identified HUD; mapped camera -> LDR -> FSR3.1 -> opaque native UI -> Presenter; blue=%zu red=%zu null_static_depth=1 physical_scene=%ux%u\n",frame,blue,red,allocation.width,allocation.height);vkUnmapMemory(device,read.memory);}
 }
 assert(boundsErrors.load()==0);
 assert(validationErrors.load()==0);
 if(oversized)std::puts("PASS: reproduced R23 1920x1080 render areas on physical 640x360 attachments through live hooks; FSR and HUD correct; zero bounds validation errors");
 return 0;
}
