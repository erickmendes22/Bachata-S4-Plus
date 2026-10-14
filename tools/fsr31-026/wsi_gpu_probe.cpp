// SPDX-License-Identifier: GPL-2.0-or-later
// Independent, bounded GPU sampling of WSI images. Never wait on the render thread.
// The sample is recorded AFTER the game's last intercepted WSI writer and read only
// after a fence on the SAME queue that submitted that command buffer has signaled.
#include "gpu_frame_probe.h"
#include <atomic>
#include <cstdio>
#include <mutex>
#include <unordered_map>
#include <vector>

namespace {
struct Slot {
    Bs4GpuFrameProbe probe{};
    VkDevice device{};
    VkFence completion{};
    VkImage image{};
    bool submitted{};
};
std::mutex slots_mutex;
std::unordered_map<VkCommandBuffer, Slot> slots;
std::atomic<uint64_t> event_sequence{0};
std::atomic<unsigned> capture_failures{0};

void release_slot(Slot& slot) {
    if(slot.completion) vkDestroyFence(slot.device, slot.completion, nullptr);
    bs4_probe_release(slot.probe, slot.device);
}
void mark_submitted(VkQueue queue, VkCommandBuffer cb,
        PFN_vkQueueSubmit submit1, PFN_vkQueueSubmit2 submit2) {
    std::lock_guard lock{slots_mutex};
    auto it=slots.find(cb);
    if(it==slots.end() || it->second.submitted)return;
    auto& slot=it->second;
    VkFenceCreateInfo ci{VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
    if(vkCreateFence(slot.device,&ci,nullptr,&slot.completion)!=VK_SUCCESS) {
        ++capture_failures;
        std::fprintf(stderr,"[BS4_FSR31] WSI_PROBE_FENCE_CREATE_FAILED cb=%p\\n",
            reinterpret_cast<void*>(cb));
        return;
    }
    VkResult result=VK_ERROR_INITIALIZATION_FAILED;
    if(submit1){
        VkSubmitInfo info{VK_STRUCTURE_TYPE_SUBMIT_INFO};
        result=submit1(queue,1,&info,slot.completion);
    } else if(submit2) {
        VkSubmitInfo2 info{VK_STRUCTURE_TYPE_SUBMIT_INFO_2};
        result=submit2(queue,1,&info,slot.completion);
    }
    if(result==VK_SUCCESS) {
        slot.submitted=true;
    } else {
        ++capture_failures;
        std::fprintf(stderr,"[BS4_FSR31] WSI_PROBE_FENCE_SUBMIT_FAILED code=%d cb=%p\\n",
            int(result),reinterpret_cast<void*>(cb));
        vkDestroyFence(slot.device,slot.completion,nullptr);
        slot.completion=VK_NULL_HANDLE;
        slot.submitted=true; // Quarantine until process exit; original GPU work may still use memory.
        // Do not destroy or reuse this sample without a completion fence.
    }
}
} // namespace

extern "C" void bs4_wsi_probe_write(VkDevice device,VkPhysicalDevice physical,
        VkCommandBuffer cb,VkImage image,VkImageLayout layout,VkExtent2D extent,
        VkFormat format) {
    if(!device||!physical||!cb||!image)return;
    const auto index=event_sequence.fetch_add(1,std::memory_order_relaxed);
    if(index>=8 && index%64)return;
    std::lock_guard lock{slots_mutex};
    auto it=slots.find(cb);
    if(it==slots.end()) {
        if(slots.size()>=8)return;
        it=slots.emplace(cb,Slot{}).first;
        it->second.device=device;
        bs4_probe_begin(it->second.probe,device,physical,index,0);
        if(!it->second.probe.pending) {
            release_slot(it->second);
            slots.erase(it);
            return;
        }
    }
    auto& slot=it->second;
    if(slot.submitted||slot.device!=device)return;
    bs4_probe_image(slot.probe,cb,image,layout,extent,format,7);
    if(!(slot.probe.stages&(1u<<7))) {
        release_slot(slot);
        slots.erase(it);
        return;
    }
    slot.probe.wsiImage=image;
    slot.image=image;
    static unsigned shown=0;
    if(shown++<24)std::fprintf(stderr,
        "[BS4_FSR31] WSI_GPU_SAMPLE_RECORDED image=%p cb=%p format=%d\\n",
        reinterpret_cast<void*>(image),reinterpret_cast<void*>(cb),int(format));
}

extern "C" void bs4_wsi_probe_submitted1(VkQueue queue,uint32_t count,
        const VkSubmitInfo* infos,PFN_vkQueueSubmit original) {
    if(!infos||!original)return;
    for(uint32_t i=0;i<count;i++) {
        if(!infos[i].pCommandBuffers)continue;
        for(uint32_t j=0;j<infos[i].commandBufferCount;j++)
            mark_submitted(queue,infos[i].pCommandBuffers[j],original,nullptr);
    }
}
extern "C" void bs4_wsi_probe_submitted2(VkQueue queue,uint32_t count,
        const VkSubmitInfo2* infos,PFN_vkQueueSubmit2 original) {
    if(!infos||!original)return;
    for(uint32_t i=0;i<count;i++) {
        if(!infos[i].pCommandBufferInfos)continue;
        for(uint32_t j=0;j<infos[i].commandBufferInfoCount;j++)
            mark_submitted(queue,infos[i].pCommandBufferInfos[j].commandBuffer,nullptr,original);
    }
}
extern "C" void bs4_wsi_probe_poll() {
    std::lock_guard lock{slots_mutex};
    for(auto it=slots.begin();it!=slots.end();) {
        auto& slot=it->second;
        if(!slot.submitted||!slot.completion||vkGetFenceStatus(slot.device,slot.completion)!=VK_SUCCESS){
            ++it;continue;
        }
        bs4_probe_resolve(slot.probe,slot.device);
        release_slot(slot);
        it=slots.erase(it);
    }
}
extern "C" void bs4_wsi_probe_reset_unsubmitted(VkCommandBuffer cb) {
    std::lock_guard lock{slots_mutex};
    auto it=slots.find(cb);
    if(it!=slots.end()&&!it->second.submitted) {
        // Only safe after the application's command buffer was reset/rebegun,
        // and only if there was no successful queue submission.
        release_slot(it->second);
        slots.erase(it);
    }
}
