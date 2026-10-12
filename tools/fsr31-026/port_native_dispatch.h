// SPDX-License-Identifier: GPL-2.0-or-later
// Cross-library ABI shared by the ARM64 rasterizer and FSR-Vulkan bridge.
// The exact Vulkan images and camera matrices belong to this guest frame.
// Do not derive them by observing a random host render-area.
#pragma once
#include <cstdint>
#include <vulkan/vulkan.h>
#include "port_camera_motion_math.h"

namespace Bachata::Fsr31 {
struct NativePreUiDispatch {
    VkImage color{};
    VkFormat colorFormat{};
    VkImageUsageFlags colorUsage{};
    VkExtent2D colorSize{};
    VkImageLayout colorLayout{};
    VkImage depth{};
    VkFormat depthFormat{};
    VkImageUsageFlags depthUsage{};
    VkExtent2D depthSize{};
    VkImageLayout depthLayout{};
    VkImage output{};
    VkFormat outputFormat{};
    VkExtent2D outputSize{};
    MotionPush motion{};
    std::uint32_t cameraValid{};
    std::uint32_t reserved{};
};
using PreUiDispatchFn = int(*)(VkInstance, VkPhysicalDevice, VkDevice, VkQueue,
                               std::uint32_t, VkCommandBuffer,
                               const NativePreUiDispatch*);
} // namespace Bachata::Fsr31
