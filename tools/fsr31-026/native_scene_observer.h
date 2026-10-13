// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>
extern "C" PFN_vkVoidFunction bs4_native_scene_wrap(const char*,PFN_vkVoidFunction);
void bs4_native_scene_begin(VkCommandBuffer,const VkRenderingInfo*);
void bs4_native_scene_end(VkCommandBuffer);
void bs4_native_scene_reset(VkCommandBuffer);
void bs4_native_scene_present();
// Returns the depth and render dimensions captured in this command buffer.
bool bs4_native_scene_camera(VkCommandBuffer,VkImageView*,VkExtent2D*);

bool bs4_native_scene_ui_boundary(VkCommandBuffer);
