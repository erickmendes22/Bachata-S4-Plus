// SPDX-License-Identifier: GPL-2.0-or-later
// Completion belongs to GPU submissions, not CPU-side Presenter callbacks.
#include "temporal_lifetime.h"
#include <array>
#include <mutex>
#include <cstdio>
namespace {
struct Slot {VkDevice device{};VkCommandBuffer owner{};VkFence fence{};bool submitted{};};
std::array<Slot,4> slots{};
std::mutex guard;
bool abandoned=false;
}
bool bs4_temporal_acquire(size_t index,VkDevice device,VkCommandBuffer command) {
    std::lock_guard lock{guard};
    if(index>=slots.size()||!device||!command||abandoned)return false;
    auto& s=slots[index];
    if(s.owner) {
        // A recorded CB cannot be waited on: it has not reached a queue yet.
        if(!s.submitted)return false;
        const auto status=vkWaitForFences(s.device,1,&s.fence,VK_TRUE,100000000);
        if(status!=VK_SUCCESS)return false;
        if(vkResetFences(s.device,1,&s.fence)!=VK_SUCCESS)return false;
    }
    if(!s.fence) {
        VkFenceCreateInfo info{};info.sType=VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
        if(vkCreateFence(device,&info,nullptr,&s.fence)!=VK_SUCCESS)return false;
    }
    s.device=device;s.owner=command;s.submitted=false;
    return true;
}
void bs4_temporal_submitted(VkQueue queue,VkCommandBuffer command,
                           PFN_vkQueueSubmit submit,PFN_vkQueueSubmit2 submit2) {
    std::lock_guard lock{guard};
    for(auto& s:slots)if(s.owner==command&&!s.submitted) {
        // An empty submission after the original CB leaves its waits/signals
        // and caller-owned fence untouched. Our fence covers the whole CB,
        // including the output blit and native draws following AMD work.
        const auto status=submit?submit(queue,0,nullptr,s.fence):
                          submit2?submit2(queue,0,nullptr,s.fence):VK_ERROR_INITIALIZATION_FAILED;
        if(status==VK_SUCCESS)s.submitted=true;
        else {abandoned=true;std::fprintf(stderr,"[BS4_FSR31] completion fence submit failed=%d\n",int(status));}
    }
}
void bs4_temporal_reset_after_drain() {
    std::lock_guard lock{guard};
    for(auto& s:slots){if(s.fence)vkDestroyFence(s.device,s.fence,nullptr);s={};}
    abandoned=false;
}
void bs4_temporal_discard(VkCommandBuffer command) {
    std::lock_guard lock{guard};
    for(auto& s:slots)if(s.owner==command&&!s.submitted)abandoned=true;
}
bool bs4_temporal_abandoned(){std::lock_guard lock{guard};return abandoned;}
