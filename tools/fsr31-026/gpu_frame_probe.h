// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>
#include <cstdint>
// Eight 3x3 grids of 8x8 tiles, not full screenshots. Owned by the existing
// temporal slot and read only after that slot's submission fence completes.
struct Bs4GpuFrameProbe {
    VkBuffer buffer{};VkDeviceMemory memory{};void* mapped{};
    bool coherent{},failed{},pending{};uint32_t stages{};
    uint64_t frame{},cameraFrame{};bool historyReset{};
    VkFormat formats[8]{};
    VkExtent2D extents[8]{};
    uint64_t writeSerial{},presentSequence{};uint32_t presentIndex{};
    bool finalWriteMatched{};VkResult presentResult=VK_NOT_READY;
    VkImage wsiImage{};
    VkImage compositeImage{};
};
void bs4_probe_begin(Bs4GpuFrameProbe&,VkDevice,VkPhysicalDevice,uint64_t,uint64_t);
void bs4_probe_image(Bs4GpuFrameProbe&,VkCommandBuffer,VkImage,VkImageLayout,VkExtent2D,VkFormat,unsigned);
void bs4_probe_resolve(Bs4GpuFrameProbe&,VkDevice);
void bs4_probe_release(Bs4GpuFrameProbe&,VkDevice);

