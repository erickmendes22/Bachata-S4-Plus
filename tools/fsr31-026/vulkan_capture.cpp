// SPDX-License-Identifier: GPL-2.0-or-later
// Capture real Vulkan image descriptions from the renderer. No guest shader
// hashes, no Mesa/Turnip private memory-layout reads.
#include "vulkan_capture.h"
#include <atomic>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <mutex>
#include <unordered_map>
#include <vector>
#include <algorithm>
namespace {
struct Image {
    VkFormat format = VK_FORMAT_UNDEFINED;
    VkExtent2D size{};
    VkImageUsageFlags usage{};
    VkImageLayout layout = VK_IMAGE_LAYOUT_UNDEFINED;
    VkImageAspectFlags aspects{};
    uint64_t last_depth_use{};
};
struct View {
    VkImage image = VK_NULL_HANDLE;
    VkImageAspectFlags aspects{};
    VkFormat format = VK_FORMAT_UNDEFINED;
};
std::mutex mutex;
std::unordered_map<VkImage, Image> images;
std::unordered_map<VkImageView, View> views;
uint64_t depth_counter{};
PFN_vkCreateImage original_create_image{};
PFN_vkDestroyImage original_destroy_image{};
PFN_vkCreateImageView original_create_image_view{};
PFN_vkDestroyImageView original_destroy_image_view{};
PFN_vkCmdBeginRendering original_begin_rendering{};
PFN_vkCmdEndRendering original_end_rendering{};
PFN_vkCmdPipelineBarrier2 original_barrier2{};
PFN_vkCmdBeginRenderingKHR original_begin_rendering_khr{};
PFN_vkCmdEndRenderingKHR original_end_rendering_khr{};
PFN_vkCmdPipelineBarrier2KHR original_barrier2_khr{};
using DlsymFn = void* (*)(void*, const char*);
PFN_vkGetDeviceProcAddr next_device_proc_addr() {
    static auto original = [] {
        auto resolve = reinterpret_cast<DlsymFn>(
            dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.34"));
        return resolve ? reinterpret_cast<PFN_vkGetDeviceProcAddr>(
            resolve(RTLD_NEXT, "vkGetDeviceProcAddr")) : nullptr;
    }();
    return original;
}
void update_layout(uint32_t count, const VkImageMemoryBarrier2* barriers) {
    if (!barriers || !count) return;
    std::lock_guard lock{mutex};
    for (uint32_t i = 0; i < count; ++i) {
        auto it = images.find(barriers[i].image);
        if (it != images.end()) it->second.layout = barriers[i].newLayout;
    }
}
void record_rendering(const VkRenderingInfo* info) {
    if (!info || !info->pDepthAttachment ||
        !info->pDepthAttachment->imageView) return;
    const auto view = info->pDepthAttachment->imageView;
    std::lock_guard lock{mutex};
    auto iv = views.find(view);
    if (iv == views.end()) return;
    auto img = images.find(iv->second.image);
    if (img == images.end()) return;
    if (!(img->second.usage & VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT))
        return;
    const auto& extent = info->renderArea.extent;
    if (img->second.size.width < extent.width ||
        img->second.size.height < extent.height) return;
    img->second.last_depth_use = ++depth_counter;
    img->second.layout = info->pDepthAttachment->imageLayout;
}
} // namespace
extern "C" int bs4_fsr31_capture_image(VkImageView view, Bs4FsrCaptureImage* out) {
    if (!out || !view) return 0;
    std::lock_guard lock{mutex};
    auto v=views.find(view);
    if(v==views.end()) return 0;
    auto i=images.find(v->second.image);
    if(i==images.end()) return 0;
    *out={v->second.image,v->second.format,i->second.size,
        i->second.usage,i->second.layout,v->second.aspects};
    return 1;
}
extern "C" int bs4_fsr31_capture_depth(VkExtent2D expected, Bs4FsrCaptureImage* out) {
    if(!out) return 0;
    std::lock_guard lock{mutex};
    uint64_t best=0;
    for(const auto& [handle, img] : images) {
        if(!img.last_depth_use || img.last_depth_use <= best) continue;
        if(img.size.width!=expected.width || img.size.height!=expected.height)
            continue;
        if(!(img.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT))continue;
        if(!(img.usage & VK_IMAGE_USAGE_SAMPLED_BIT))continue;
        best=img.last_depth_use;
        *out={handle,img.format,img.size,img.usage,img.layout,
            VK_IMAGE_ASPECT_DEPTH_BIT};
    }
    return best ? 1 : 0;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_create_image(
    VkDevice dev,const VkImageCreateInfo* ci,const VkAllocationCallbacks* ac,VkImage* img) {
    if(!original_create_image) return VK_ERROR_INITIALIZATION_FAILED;
    auto r=original_create_image(dev,ci,ac,img);
    if(r==VK_SUCCESS && ci && img) {
        std::lock_guard lock{mutex};
        images[*img]={ci->format,{ci->extent.width,ci->extent.height},ci->usage,
                      ci->initialLayout,{},0};
    }
    return r;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_destroy_image(
    VkDevice dev,VkImage img,const VkAllocationCallbacks* ac) {
    {std::lock_guard lock{mutex}; images.erase(img);}
    if(original_destroy_image) original_destroy_image(dev,img,ac);
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_create_image_view(
    VkDevice dev,const VkImageViewCreateInfo* ci,const VkAllocationCallbacks* ac,
    VkImageView* view) {
    if(!original_create_image_view) return VK_ERROR_INITIALIZATION_FAILED;
    auto r=original_create_image_view(dev,ci,ac,view);
    if(r==VK_SUCCESS && ci && view) {
        std::lock_guard lock{mutex};
        views[*view]={ci->image,ci->subresourceRange.aspectMask,ci->format};
    }
    return r;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_destroy_image_view(
    VkDevice dev,VkImageView view,const VkAllocationCallbacks* ac) {
    {std::lock_guard lock{mutex}; views.erase(view);}
    if(original_destroy_image_view) original_destroy_image_view(dev,view,ac);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_begin_rendering(
    VkCommandBuffer cb,const VkRenderingInfo* info) {
    record_rendering(info);
    if(original_begin_rendering) original_begin_rendering(cb,info);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering(VkCommandBuffer cb) {
    if(original_end_rendering) original_end_rendering(cb);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_barrier2(
    VkCommandBuffer cb,const VkDependencyInfo* dep) {
    if(dep) update_layout(dep->imageMemoryBarrierCount,dep->pImageMemoryBarriers);
    if(original_barrier2) original_barrier2(cb,dep);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_begin_rendering_khr(
    VkCommandBuffer cb,const VkRenderingInfo* info) {
    record_rendering(info);
    if(original_begin_rendering_khr) original_begin_rendering_khr(cb,info);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering_khr(VkCommandBuffer cb) {
    if(original_end_rendering_khr) original_end_rendering_khr(cb);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_barrier2_khr(
    VkCommandBuffer cb,const VkDependencyInfo* dep) {
    if(dep)update_layout(dep->imageMemoryBarrierCount,dep->pImageMemoryBarriers);
    if(original_barrier2_khr)original_barrier2_khr(cb,dep);
}
extern "C" VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetDeviceProcAddr(
    VkDevice device,const char* name) {
    const auto original=next_device_proc_addr();
    if(!original || !name)return nullptr;
    const auto proc=original(device,name);
    if(!proc)return nullptr;
    #define BS4_WRAP(method,symbol,target) \
        if(std::strcmp(name,symbol)==0) { \
            method=reinterpret_cast<decltype(method)>(proc); \
            return reinterpret_cast<PFN_vkVoidFunction>(target); \
        }
    BS4_WRAP(original_create_image,"vkCreateImage",&bs4_cap_create_image)
    BS4_WRAP(original_destroy_image,"vkDestroyImage",&bs4_cap_destroy_image)
    BS4_WRAP(original_create_image_view,"vkCreateImageView",&bs4_cap_create_image_view)
    BS4_WRAP(original_destroy_image_view,"vkDestroyImageView",&bs4_cap_destroy_image_view)
    BS4_WRAP(original_begin_rendering,"vkCmdBeginRendering",&bs4_cap_begin_rendering)
    BS4_WRAP(original_end_rendering,"vkCmdEndRendering",&bs4_cap_end_rendering)
    BS4_WRAP(original_barrier2,"vkCmdPipelineBarrier2",&bs4_cap_barrier2)
    BS4_WRAP(original_begin_rendering_khr,"vkCmdBeginRenderingKHR",&bs4_cap_begin_rendering_khr)
    BS4_WRAP(original_end_rendering_khr,"vkCmdEndRenderingKHR",&bs4_cap_end_rendering_khr)
    BS4_WRAP(original_barrier2_khr,"vkCmdPipelineBarrier2KHR",&bs4_cap_barrier2_khr)
    #undef BS4_WRAP
    return proc;
}
