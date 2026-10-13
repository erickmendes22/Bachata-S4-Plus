// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "native_draw_handoff.h"
#include "vulkan_capture.h"
int bs4_native_ui_draw(VkCommandBuffer,const Bs4NativeRenderState&);
void bs4_native_ui_reset(VkCommandBuffer);
void bs4_native_ui_release(VkImage originalImage);
void bs4_native_ui_release_view(VkImageView);
bool bs4_native_ui_output(VkCommandBuffer,Bs4FsrCaptureImage&);

// Resolve only this command buffer's UI source, retaining the native view's
// format and component mapping. Unrelated views are unchanged.
VkImageView bs4_native_ui_sampled_view(VkCommandBuffer,VkImageView);
bool bs4_native_ui_rendering(VkCommandBuffer,const VkRenderingInfo*,VkRenderingInfo&,
                             VkRenderingAttachmentInfo&,VkRenderingAttachmentInfo&);
bool bs4_native_ui_barrier(VkCommandBuffer,const VkImageMemoryBarrier2&,VkImageMemoryBarrier2&);
