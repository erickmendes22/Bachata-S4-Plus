// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "native_draw_handoff.h"
#include "vulkan_capture.h"
int bs4_native_ui_draw(VkCommandBuffer,const Bs4NativeRenderState&);
void bs4_native_ui_reset(VkCommandBuffer);
void bs4_native_ui_release(VkImage originalImage);
bool bs4_native_ui_output(VkCommandBuffer,Bs4FsrCaptureImage&);
