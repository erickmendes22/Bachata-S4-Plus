#pragma once
#include <vulkan/vulkan.h>
#include <cstddef>
bool bs4_temporal_acquire(size_t slot,VkDevice device,VkCommandBuffer command);
void bs4_temporal_submitted(VkQueue,VkCommandBuffer,PFN_vkQueueSubmit,PFN_vkQueueSubmit2);
void bs4_temporal_reset_after_drain();
void bs4_temporal_discard(VkCommandBuffer);
bool bs4_temporal_abandoned();
