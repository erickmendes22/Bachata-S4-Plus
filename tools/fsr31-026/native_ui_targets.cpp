// SPDX-License-Identifier: GPL-2.0-or-later
#include "native_ui_targets.h"
#include "native_scene_observer.h"
#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <unordered_map>
#include <cstdio>
extern "C" VkDevice bs4_fsr31_device();
extern "C" VkPhysicalDevice bs4_fsr31_physical_device();
namespace {
struct Surface {VkImage image{};VkImageView view{};VkDeviceMemory memory{};};
struct Targets {Surface color;std::map<VkFormat,Surface> depths;};
struct Scope {VkImage source{};VkImageView color{},depth{};VkExtent2D guest{};};
std::mutex mutex;
std::unordered_map<VkImage,Targets> targets;
std::unordered_map<VkCommandBuffer,Scope> scopes;
void destroy(Surface& s) {
    const auto device=bs4_fsr31_device();
    bs4_fsr31_untrack_ui_image(s.image,s.view);
    if(s.view)vkDestroyImageView(device,s.view,nullptr);
    if(s.image)vkDestroyImage(device,s.image,nullptr);
    if(s.memory)vkFreeMemory(device,s.memory,nullptr);s={};
}
bool create(Surface& out,VkFormat format,VkImageAspectFlags aspect) {
    const auto device=bs4_fsr31_device();
    const auto physical=bs4_fsr31_physical_device();
    if(!device||!physical)return false;
    VkImageCreateInfo ci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};ci.imageType=VK_IMAGE_TYPE_2D;
    ci.format=format;ci.extent={1280,720,1};ci.mipLevels=ci.arrayLayers=1;
    ci.samples=VK_SAMPLE_COUNT_1_BIT;ci.tiling=VK_IMAGE_TILING_OPTIMAL;
    ci.usage=VK_IMAGE_USAGE_TRANSFER_SRC_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|
        (aspect==VK_IMAGE_ASPECT_COLOR_BIT?VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT:VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT);
    if(aspect==VK_IMAGE_ASPECT_COLOR_BIT)ci.flags=VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT;
    if(vkCreateImage(device,&ci,nullptr,&out.image)!=VK_SUCCESS)return false;
    VkMemoryRequirements req{};vkGetImageMemoryRequirements(device,out.image,&req);
    VkPhysicalDeviceMemoryProperties props{};vkGetPhysicalDeviceMemoryProperties(physical,&props);
    uint32_t index=UINT32_MAX;
    for(uint32_t pass=0;pass<2&&index==UINT32_MAX;pass++)for(uint32_t i=0;i<props.memoryTypeCount;i++)
        if((req.memoryTypeBits&(1u<<i))&&(pass||(props.memoryTypes[i].propertyFlags&VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT))){index=i;break;}
    if(index==UINT32_MAX){destroy(out);return false;}
    VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=req.size;ai.memoryTypeIndex=index;
    if(vkAllocateMemory(device,&ai,nullptr,&out.memory)!=VK_SUCCESS||
       vkBindImageMemory(device,out.image,out.memory,0)!=VK_SUCCESS){destroy(out);return false;}
    VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};vi.image=out.image;
    vi.viewType=VK_IMAGE_VIEW_TYPE_2D;vi.format=format;vi.subresourceRange={aspect,0,1,0,1};
    if(vkCreateImageView(device,&vi,nullptr,&out.view)!=VK_SUCCESS){destroy(out);return false;}
    bs4_fsr31_track_ui_image(out.image,&ci,out.view,&vi);return true;
}
VkExtent2D hardware_viewport() {
    VkPhysicalDeviceProperties props{};vkGetPhysicalDeviceProperties(bs4_fsr31_physical_device(),&props);
    return {std::min(props.limits.maxViewportDimensions[0],16384u),std::min(props.limits.maxViewportDimensions[1],16384u)};
}
}
int bs4_native_ui_draw(VkCommandBuffer cb,const Bs4NativeRenderState& state) {
    const auto* mode=std::getenv("BACHATA_FSR31_NATIVE_UI");if(mode&&std::strcmp(mode,"0")==0)return 0;
    if(!bs4_fsr31_device()||!bs4_native_scene_dynamic_ready(cb))return 0;
    const auto hardware=hardware_viewport();Scope active{};
    {std::lock_guard lock{mutex};const auto it=scopes.find(cb);if(it!=scopes.end())active=it->second;}
    if(active.source) {
        Bs4FsrCaptureImage bound{};
        const bool same=state.colorCount==1&&bs4_fsr31_capture_image(reinterpret_cast<VkImageView>(state.colors[0].view),&bound)&&bound.image==active.source;
        // Always restore native values on other targets, including a draw for
        // which native dynamic-state caching emitted no new Vulkan commands.
        bs4_native_scene_apply_ui_scale(cb,active.guest,{1280,720},same,hardware);
        return same?1:0;
    }
    VkImageView color{},depth{};VkExtent2D extent{};Bs4NativeUiBoundary boundary{};
    Bs4FsrCaptureImage source{},nativeDepth{};
    if(!bs4_fsr31_capture_scene(cb,&color,&depth,&extent)||
       !bs4_native_scene_ui_state(cb,boundary)||boundary.color!=color||
       !bs4_fsr31_capture_image(color,&source)||source.format!=VK_FORMAT_R8G8B8A8_UNORM||
       !bs4_native_scene_can_ui_scale(cb,extent,{1280,720},hardware))return 0;
    VkFormat depthFormat=VK_FORMAT_UNDEFINED;
    if(boundary.depth) {
        if(!bs4_fsr31_capture_image(boundary.depth,&nativeDepth))return 0;
        depthFormat=nativeDepth.format;
    }
    // Allocate before changing the rendering instance. Lifetimes follow the
    // original texture-cache image; formats are retained rather than freeing
    // a depth target that an earlier queued frame could still reference.
    Surface uiColor{},uiDepth{};
    {
        std::lock_guard lock{mutex};auto& owned=targets[source.image];
        if(!owned.color.image&&!create(owned.color,source.format,VK_IMAGE_ASPECT_COLOR_BIT))return 0;
        uiColor=owned.color;
        if(depthFormat!=VK_FORMAT_UNDEFINED){auto& d=owned.depths[depthFormat];
            const bool stencil=depthFormat==VK_FORMAT_D32_SFLOAT_S8_UINT||depthFormat==VK_FORMAT_D24_UNORM_S8_UINT;
            if(!d.image&&!create(d,depthFormat,VK_IMAGE_ASPECT_DEPTH_BIT|(stencil?VK_IMAGE_ASPECT_STENCIL_BIT:0)))return 0;
            uiDepth=d;}
    }
    const int result=bs4_fsr31_run_scaled_ui(cb,uiColor.view,uiDepth.view);if(!result)return 0;
    {std::lock_guard lock{mutex};scopes[cb]={source.image,uiColor.view,uiDepth.view,extent};}
    bs4_native_scene_apply_ui_scale(cb,extent,{1280,720},true,hardware);
    static bool temporalLogged=false;
    if(result==2&&!temporalLogged){temporalLogged=true;std::fprintf(stderr,"[BS4_FSR31] FIRST_REAL_RUNSCALED_UI native025 owned_UI=1280x720\n");}
    return result;
}
void bs4_native_ui_reset(VkCommandBuffer cb){std::lock_guard lock{mutex};scopes.erase(cb);}
void bs4_native_ui_release(VkImage image) {
    Targets owned{};
    {std::lock_guard lock{mutex};const auto it=targets.find(image);if(it==targets.end())return;
        owned=std::move(it->second);targets.erase(it);
        for(auto s=scopes.begin();s!=scopes.end();)if(s->second.source==image)s=scopes.erase(s);else++s;}
    for(auto& d:owned.depths)destroy(d.second);destroy(owned.color);
}
bool bs4_native_ui_output(VkCommandBuffer cb,Bs4FsrCaptureImage& out) {
    VkImageView view{};{std::lock_guard lock{mutex};const auto it=scopes.find(cb);if(it==scopes.end())return false;view=it->second.color;}
    return bs4_fsr31_capture_image(view,&out);
}
