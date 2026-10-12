// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>

// Contract taken from the *scaled* path in ducvd89/Bloodborne-Android:
// gpu/shadps4/video_core/renderer_vulkan/vk_temporal_upscaler.cpp
// RunScaled(): LDR scene + corresponding depth + camera motion + jitter,
// reconstruct into an output-resolution RGBA8 UI surface. Run() is the
// separate HDR/native-AA route and MUST NOT be used here.
namespace BachataPortScaled {
constexpr bool LdrScene(VkFormat format) {
    return format == VK_FORMAT_R8G8B8A8_UNORM;
}
constexpr bool SceneAndOutput(VkFormat format, VkExtent2D scene, VkExtent2D out) {
    if (!LdrScene(format) || !scene.width || !scene.height ||
        !out.width || !out.height) return false;
    // Only native scale or spatially uniform reconstruction is valid.
    return scene.width <= out.width && scene.height <= out.height &&
        uint64_t(scene.width) * out.height == uint64_t(scene.height) * out.width;
}
constexpr bool MatchingDepth(VkExtent2D scene, VkExtent2D depth) {
    // In the port, SceneTargets::Read resolves to the actual raster extent.
    // Never guess that unrelated full-resolution depth belongs to the scene.
    return scene.width == depth.width && scene.height == depth.height;
}
constexpr VkFormat UiOutputFormat = VK_FORMAT_R8G8B8A8_UNORM;
constexpr uint32_t ContextFlags = 0; // LDR: NO HDR_COLOR_INPUT or AUTO_EXPOSURE.
} // namespace BachataPortScaled
