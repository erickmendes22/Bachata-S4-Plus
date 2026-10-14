// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "port_camera_constants.h"
#include <vulkan/vulkan.h>
// Called by the renderer at its completed G-buffer boundary. Signs come
// from RAW Gnm viewport scales; Vulkan viewport dimensions are insufficient.
// This API only copies input. It never writes the guest's mapped buffers.
struct Bs4PortSceneFrame {
    uint32_t structSize;
    uint32_t abiVersion; // 1
    uint64_t frameId;    // renderer display-frame sequence, not wall time/CB ID
    uint64_t sceneId;    // stable camera/depth identity, changes on scene cuts
    VkCommandBuffer command;
    VkImageView depth;
    uint32_t colorAttachmentCount;
    VkExtent2D renderArea;
    const void* constants;
    uint32_t constantsBytes;
    float viewportXSign, viewportYSign;
    float jitterX, jitterY; // shift ACTUALLY used to rasterize this scene
};
struct Bs4PortCameraDispatch {
    BachataCamera::Push motion{};
    float nearPlane{},farPlane{},verticalFov{};
    uint64_t frameId{};
    bool reset{};
};
extern "C" int bs4_fsr31_port_scene(const Bs4PortSceneFrame*);
extern "C" void bs4_fsr31_port_invalidate_after_gpu_drain();
void bs4_fsr31_port_end_frame();
bool bs4_fsr31_port_camera(VkCommandBuffer,VkImageView,VkExtent2D,
                           Bs4PortCameraDispatch&);
// A cross-CB motion handoff requires a previously submitted source.
void bs4_fsr31_port_authorize_submitted(VkCommandBuffer scene,
    VkCommandBuffer ui,VkImageView depth);
