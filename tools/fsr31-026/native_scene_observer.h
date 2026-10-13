// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>
#include "native_draw_handoff.h"
extern "C" PFN_vkVoidFunction bs4_native_scene_wrap(const char*,PFN_vkVoidFunction);
void bs4_native_scene_begin(VkCommandBuffer,const VkRenderingInfo*);
void bs4_native_scene_end(VkCommandBuffer);
void bs4_native_scene_reset(VkCommandBuffer);
void bs4_native_scene_present();
// Returns the depth and render dimensions captured in this command buffer.
bool bs4_native_scene_camera(VkCommandBuffer,VkImageView*,VkExtent2D*);

bool bs4_native_scene_ui_boundary(VkCommandBuffer);

struct Bs4NativeUiBoundary {
    uint64_t frame;
    VkImageView color,depth;
    VkExtent2D guestExtent;
    float rawViewport[4];
};
void bs4_native_scene_draw_state(VkCommandBuffer,const Bs4NativeRenderState&);
bool bs4_native_scene_ui_state(VkCommandBuffer,Bs4NativeUiBoundary&);
