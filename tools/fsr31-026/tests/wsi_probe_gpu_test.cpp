// SPDX-License-Identifier: GPL-2.0-or-later
// Headless lavapipe regression: copy a known cyan image through the exact
// fence-backed WSI sampler and verify that GPU_FRAME_PROBE reports its RGB.
#include <vulkan/vulkan.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
extern "C" void bs4_wsi_probe_write(VkDevice,VkPhysicalDevice,VkCommandBuffer,VkImage,VkImageLayout,VkExtent2D,VkFormat);
extern "C" void bs4_wsi_probe_submitted1(VkQueue,uint32_t,const VkSubmitInfo*,PFN_vkQueueSubmit);
extern "C" void bs4_wsi_probe_poll();

#define CHECK(x) do {auto v=(x);if(v!=VK_SUCCESS){std::fprintf(stderr,"WSI_TEST_FAILED line=%d status=%d\\n",__LINE__,int(v));return 1;}}while(0)
int main(){
    VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};app.apiVersion=VK_API_VERSION_1_3;
    VkInstanceCreateInfo ici{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};ici.pApplicationInfo=&app;
    VkInstance instance{};CHECK(vkCreateInstance(&ici,nullptr,&instance));
    uint32_t count=0;CHECK(vkEnumeratePhysicalDevices(instance,&count,nullptr));
    if(!count)return 2;
    std::vector<VkPhysicalDevice> gpu(count);CHECK(vkEnumeratePhysicalDevices(instance,&count,gpu.data()));
    auto physical=gpu.front();
    uint32_t families=0;vkGetPhysicalDeviceQueueFamilyProperties(physical,&families,nullptr);
    std::vector<VkQueueFamilyProperties> props(families);vkGetPhysicalDeviceQueueFamilyProperties(physical,&families,props.data());
    uint32_t family=UINT32_MAX;
    for(uint32_t i=0;i<families;i++)if(props[i].queueFlags&VK_QUEUE_GRAPHICS_BIT){family=i;break;}
    if(family==UINT32_MAX)return 3;
    float priority=1;
    VkDeviceQueueCreateInfo qi{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    qi.queueFamilyIndex=family;qi.queueCount=1;qi.pQueuePriorities=&priority;
    VkPhysicalDeviceSynchronization2Features sync{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SYNCHRONIZATION_2_FEATURES};
    sync.synchronization2=VK_TRUE;
    VkDeviceCreateInfo di{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};di.pNext=&sync;
    di.queueCreateInfoCount=1;di.pQueueCreateInfos=&qi;
    VkDevice dev{};CHECK(vkCreateDevice(physical,&di,nullptr,&dev));
    VkQueue queue{};vkGetDeviceQueue(dev,family,0,&queue);
    VkCommandPoolCreateInfo pi{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};pi.queueFamilyIndex=family;
    VkCommandPool pool{};CHECK(vkCreateCommandPool(dev,&pi,nullptr,&pool));
    VkCommandBufferAllocateInfo ai{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
    ai.commandPool=pool;ai.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;ai.commandBufferCount=1;
    VkCommandBuffer cb{};CHECK(vkAllocateCommandBuffers(dev,&ai,&cb));
    VkImageCreateInfo imageci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
    imageci.imageType=VK_IMAGE_TYPE_2D;imageci.format=VK_FORMAT_R8G8B8A8_UNORM;
    imageci.extent={64,64,1};imageci.mipLevels=1;imageci.arrayLayers=1;
    imageci.samples=VK_SAMPLE_COUNT_1_BIT;imageci.tiling=VK_IMAGE_TILING_OPTIMAL;
    imageci.usage=VK_IMAGE_USAGE_TRANSFER_SRC_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    VkImage image{};CHECK(vkCreateImage(dev,&imageci,nullptr,&image));
    VkMemoryRequirements req{};vkGetImageMemoryRequirements(dev,image,&req);
    VkPhysicalDeviceMemoryProperties mem{};vkGetPhysicalDeviceMemoryProperties(physical,&mem);
    uint32_t memory=UINT32_MAX;
    for(uint32_t i=0;i<mem.memoryTypeCount;i++)if(req.memoryTypeBits&(1u<<i)){memory=i;break;}
    if(memory==UINT32_MAX)return 4;
    VkMemoryAllocateInfo mai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    mai.allocationSize=req.size;mai.memoryTypeIndex=memory;
    VkDeviceMemory alloc{};CHECK(vkAllocateMemory(dev,&mai,nullptr,&alloc));
    CHECK(vkBindImageMemory(dev,image,alloc,0));
    VkCommandBufferBeginInfo bi{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    CHECK(vkBeginCommandBuffer(cb,&bi));
    VkImageMemoryBarrier2 bar{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
    bar.srcStageMask=VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT;bar.dstStageMask=VK_PIPELINE_STAGE_2_TRANSFER_BIT;
    bar.dstAccessMask=VK_ACCESS_2_TRANSFER_WRITE_BIT;
    bar.oldLayout=VK_IMAGE_LAYOUT_UNDEFINED;bar.newLayout=VK_IMAGE_LAYOUT_GENERAL;bar.image=image;
    bar.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
    VkDependencyInfo dep{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
    dep.imageMemoryBarrierCount=1;dep.pImageMemoryBarriers=&bar;
    vkCmdPipelineBarrier2(cb,&dep);
    VkClearColorValue cyan{};cyan.float32[0]=0;cyan.float32[1]=1;cyan.float32[2]=1;cyan.float32[3]=1;
    VkImageSubresourceRange range{VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
    vkCmdClearColorImage(cb,image,VK_IMAGE_LAYOUT_GENERAL,&cyan,1,&range);
    bs4_wsi_probe_write(dev,physical,cb,image,VK_IMAGE_LAYOUT_GENERAL,{64,64},VK_FORMAT_R8G8B8A8_UNORM);
    CHECK(vkEndCommandBuffer(cb));
    VkSubmitInfo si{VK_STRUCTURE_TYPE_SUBMIT_INFO};si.commandBufferCount=1;si.pCommandBuffers=&cb;
    CHECK(vkQueueSubmit(queue,1,&si,VK_NULL_HANDLE));
    bs4_wsi_probe_submitted1(queue,1,&si,&vkQueueSubmit);
    CHECK(vkQueueWaitIdle(queue)); // synthetic test only, never a production GPU stall.
    bs4_wsi_probe_poll();
    std::puts("WSI_FENCED_PROBE_COMPLETE");
    vkDestroyImage(dev,image,nullptr);vkFreeMemory(dev,alloc,nullptr);
    vkDestroyCommandPool(dev,pool,nullptr);vkDestroyDevice(dev,nullptr);vkDestroyInstance(instance,nullptr);
    return 0;
}
