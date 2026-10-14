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
void bs4_native_scene_register_pipeline(VkPipelineLayout,uint64_t vertexHash);
bool bs4_native_scene_dynamic_ready(VkCommandBuffer);
bool bs4_native_scene_apply_ui_scale(VkCommandBuffer,VkExtent2D guest,VkExtent2D output,
                                    bool scaled,VkExtent2D hardwareViewport);

bool bs4_native_scene_can_ui_scale(VkCommandBuffer,VkExtent2D guest,VkExtent2D output,
                                  VkExtent2D hardwareViewport);

// Recording provenance only: no Vulkan calls, no synthetic target identity.
struct Bs4SceneWriter {
    VkCommandBuffer command{};
    uint64_t frame{},vertexHash{},fragmentHash{},renderEpoch{};
    VkExtent2D area{};
    VkViewport viewport{};VkRect2D scissor{};bool scissorValid{};
    uint32_t vertices{},instances{},colorCount{};
    VkImageView sampled[8]{};
    uint32_t sampledCount{};
    bool sampledOverflow{};
};
bool bs4_native_scene_writer(VkImageView,Bs4SceneWriter&);
void bs4_native_scene_forget_view(VkImageView);


bool bs4_native_scene_active_writer(VkCommandBuffer,VkImageView,Bs4SceneWriter&);
