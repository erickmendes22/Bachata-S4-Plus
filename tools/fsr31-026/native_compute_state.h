// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>
PFN_vkVoidFunction bs4_native_compute_wrap(const char*,PFN_vkVoidFunction);
bool bs4_native_compute_can_restore(VkCommandBuffer);
void bs4_native_compute_restore(VkCommandBuffer);
void bs4_native_compute_reset(VkCommandBuffer);

void bs4_native_compute_enter_sdk();
void bs4_native_compute_leave_sdk();
bool bs4_native_compute_in_sdk();
