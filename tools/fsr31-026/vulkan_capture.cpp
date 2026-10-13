// SPDX-License-Identifier: GPL-2.0-or-later
// Capture real Vulkan image descriptions from the renderer. No guest shader
// hashes, no Mesa/Turnip private memory-layout reads.
#include "vulkan_capture.h"
extern "C" int bs4_fsr31_selected_preset();
#include "port_camera_constants.h"
#include <atomic>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <mutex>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cmath>
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
struct ScenePass {
    VkImageView color = VK_NULL_HANDLE;
    VkImageView depth = VK_NULL_HANDLE;
    VkExtent2D extent{};
    bool inside = false;
    bool ready = false;
    uint64_t frame = 0;
};
ScenePass latest_scene{};
std::unordered_map<VkCommandBuffer,VkImageView> prepared_outputs;
extern "C" int bs4_port_camera_range(VkCommandBuffer,float*,float*);
extern "C" int bs4_fsr31_supply_camera_range(VkCommandBuffer,float,float);
extern "C" uint64_t bs4_port_frame_generation();
extern "C" VkImageView bs4_port_current_scene(VkCommandBuffer,VkExtent2D*);
extern "C" VkImageView bs4_fsr31_prepare_resources(VkCommandBuffer,VkImageView,VkImageView,VkExtent2D,VkExtent2D);
std::unordered_map<VkCommandBuffer, ScenePass> command_scenes;
bool pre_ui_dispatch_logged=false;
bool pre_ui_eligible_logged=false;
using PreUiDispatch=int (*)(VkCommandBuffer,VkImageView,VkExtent2D,VkExtent2D,VkImage*);
extern "C" int bs4_fsr31_pre_ui_dispatch(VkCommandBuffer,VkImageView,
                VkImageView,VkExtent2D,VkExtent2D,VkImage*);
extern "C" int bs4_fsr31_supply_port_camera(
    VkCommandBuffer,VkImageView,const void*,uint32_t);
extern "C" void bs4_port_note_render(VkCommandBuffer,VkImageView,VkExtent2D,uint32_t);
extern "C" VkImageView bs4_port_camera_for_scene(
    VkCommandBuffer,VkExtent2D,void*,uint32_t);
extern "C" void bs4_port_reset_cb(VkCommandBuffer);
extern "C" PFN_vkVoidFunction bs4_port_wrap_proc(const char*,PFN_vkVoidFunction);
extern "C" PFN_vkVoidFunction bs4_port_ui_wrap_proc(const char*,PFN_vkVoidFunction);
extern "C" void bs4_port_ui_install_rendering(
 PFN_vkCmdBeginRendering,PFN_vkCmdEndRendering,
 PFN_vkCmdBeginRenderingKHR,PFN_vkCmdEndRenderingKHR);
extern "C" bool bs4_port_ui_redirect_begin(
 VkCommandBuffer,const VkRenderingInfo*,bool,VkRenderingInfo*);
extern "C" void bs4_port_ui_redirect_end(VkCommandBuffer);
extern "C" void bs4_port_ui_reset(VkCommandBuffer);
extern "C" VkImageView bs4_fsr31_output_view(VkImage);

PFN_vkBeginCommandBuffer original_begin_command{};
PFN_vkResetCommandBuffer original_reset_command{};
PFN_vkFreeCommandBuffers original_free_commands{};
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

/* An actual reduced scene (not a post-present downsample) is characterized
 * by a small render area, color image of matching size, and a completed
 * Vulkan dynamic-rendering pass. The transition to a larger output-image
 * pass is the earliest safe point to upscale before UI drawing begins.
 *
 * This never changes the guest's render dimensions. Unsupported cases leave
 * the original shadPS4 command sequence untouched.
 */
// The Android port's RunScaled never dispatches at vkCmdBeginRendering
// merely because an attachment is 1280x720. That old R13 hook was still
// consuming the completed scene before the positively identified HUD draw:
// CABE26EE proved the candidate was consumed without ANY temporal dispatch.
// This function now ONLY observes completed single-color RGBA8 LDR passes.
// A first recognized HUD *draw* (bs4_port_ui_try_activate) is the sole
// permitted FSR/composition trigger.
bool first_pre_ui_color(VkCommandBuffer cmd,const VkRenderingInfo* info,
                        VkRenderingInfo& modified,
                        std::vector<VkRenderingAttachmentInfo>& overrides) {
    (void)modified;
    (void)overrides;
    if(!cmd||!info||info->pNext||!info->colorAttachmentCount||
       !info->pColorAttachments||!info->pColorAttachments[0].imageView)
        return false;
    VkExtent2D real{};
    const VkImageView scene_depth=bs4_port_current_scene(cmd,&real);
    if(!scene_depth||real.width<64||real.height<64 ||
       real.width>1280||real.height>720)return false;
    Bs4FsrCaptureImage d{};
    if(!bs4_fsr31_capture_image(scene_depth,&d))return false;
    // One bounded observation for each attachment count after real camera
    // discovery; never modify the guest pass when selection fails.
    static std::atomic<uint32_t> observed_counts{0};
    const uint32_t bit=1u<<std::min(info->colorAttachmentCount,31u);
    if(!(observed_counts.fetch_or(bit)&bit)) {
        Bs4FsrCaptureImage c{};bs4_fsr31_capture_image(info->pColorAttachments[0].imageView,&c);
        std::fprintf(stderr,"[BS4_PORT_STAGE] camera=%ux%u color_count=%u fmt=%u allocation=%ux%u depth=%ux%u usage=%x\n",real.width,real.height,info->colorAttachmentCount,unsigned(c.format),c.size.width,c.size.height,d.size.width,d.size.height,unsigned(c.usage));
    }
    if(info->colorAttachmentCount!=1)return false;
    const uint32_t w=real.width,h=real.height;
    const uint64_t frame=bs4_port_frame_generation();
    const VkImageView view=info->pColorAttachments[0].imageView;
    std::lock_guard lock{mutex};
    const auto v=views.find(view);
    if(v==views.end() || v->second.format!=VK_FORMAT_R8G8B8A8_UNORM)
        return false;
    const auto img=images.find(v->second.image);
    if(img==images.end() ||
       !(img->second.usage & VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT) ||
       !(img->second.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT) ||
       img->second.size.width!=d.size.width || img->second.size.height!=d.size.height ||
       img->second.size.width<w || img->second.size.height<h)
        return false;
    auto& stage=command_scenes[cmd];
    stage.color=view;
    stage.depth=scene_depth;
    stage.frame=frame; // actual G-buffer identity and camera frame
    stage.extent={w,h};
    stage.inside=true;
    stage.ready=false;
    return false; // NEVER change the guest rendering or its attachments
}

void scene_rendering_ended(VkCommandBuffer command) {
    std::lock_guard lock{mutex};
    const auto it=command_scenes.find(command);
    if(it!=command_scenes.end()&&it->second.inside) {
        it->second.ready=true;
        it->second.inside=false;
        latest_scene=it->second;
    }
}
} // namespace
/* Read-only preflight: MUST succeed before guest vkCmdEndRendering is
 * recorded. CABE26EE had no successful FSR dispatch; the old R23 path
 * nevertheless risked ending/restarting the original HUD pass. */
extern "C" int bs4_port_can_prepare_ui(VkCommandBuffer cb) {
    if(!cb)return 0;
    ScenePass scene{};
    {
        std::lock_guard lock{mutex};
        const auto it=command_scenes.find(cb);
        scene=it==command_scenes.end()?latest_scene:it->second;
        if((!scene.ready&&!scene.inside) || !scene.color || scene.extent.width<64 ||
           scene.extent.width>1280 || scene.extent.height<64 ||
           scene.extent.height>720)return 0;
        const auto color_view=views.find(scene.color);
        if(color_view==views.end() ||
           color_view->second.format!=VK_FORMAT_R8G8B8A8_UNORM)
            return 0;
        const auto color=images.find(color_view->second.image);
        if(color==images.end() ||
           !(color->second.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT))
            return 0;
    }
    if(scene.frame!=bs4_port_frame_generation())return 0;
    if(bs4_fsr31_selected_preset()<0)return 0;
    BachataCamera::Push push{};
    const VkImageView depth=bs4_port_camera_for_scene(
        cb,scene.extent,&push,sizeof(push));
    if(!depth)return 0;
    Bs4FsrCaptureImage c{},d{};
    if(!bs4_fsr31_capture_image(scene.color,&c) ||
       !bs4_fsr31_capture_image(depth,&d))return 0;
    if(c.format!=VK_FORMAT_R8G8B8A8_UNORM ||
       c.size.width<scene.extent.width || c.size.height<scene.extent.height ||
       c.size.width!=d.size.width || c.size.height!=d.size.height ||
       depth!=scene.depth || !(d.aspects & VK_IMAGE_ASPECT_DEPTH_BIT) ||
       !(d.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT))return 0;
    if(!bs4_fsr31_supply_port_camera(cb,depth,&push,sizeof(push)))return 0;
    float near=0,far=0;
    if(!bs4_port_camera_range(cb,&near,&far) ||
       !bs4_fsr31_supply_camera_range(cb,near,far))return 0;
    const VkImageView output=bs4_fsr31_prepare_resources(
        cb,scene.color,depth,scene.extent,{1280,720});
    if(!output)return 0;
    std::lock_guard lock{mutex};prepared_outputs[cb]=output;
    return 1;
}
extern "C" VkImageView bs4_port_prepared_output(VkCommandBuffer cb){
    std::lock_guard lock{mutex};const auto it=prepared_outputs.find(cb);
    return it==prepared_outputs.end()?VK_NULL_HANDLE:it->second;
}
extern "C" VkImageView bs4_port_scene_color(VkCommandBuffer cb){
    const uint64_t frame=bs4_port_frame_generation();
    std::lock_guard lock{mutex};const auto it=command_scenes.find(cb);
    const auto& scene=it==command_scenes.end()?latest_scene:it->second;
    return (scene.ready||scene.inside)&&scene.frame==frame?scene.color:VK_NULL_HANDLE;
}
/* Port-style temporal scene for the first positively identified HUD draw.
 * Called OUTSIDE Vulkan dynamic rendering; no speculative guest target blit.
 */
extern "C" __attribute__((visibility("default"))) VkImageView
bs4_port_prepare_ui(VkCommandBuffer cb) {
    if(!cb)return VK_NULL_HANDLE;
    ScenePass scene{};
    {
        std::lock_guard lock{mutex};
        const auto it=command_scenes.find(cb);
        scene=it==command_scenes.end()?latest_scene:it->second;
        if((!scene.ready&&!scene.inside)||!scene.color)return VK_NULL_HANDLE;
        const auto v=views.find(scene.color);
        if(v==views.end() || v->second.format!=VK_FORMAT_R8G8B8A8_UNORM)
            return VK_NULL_HANDLE;
    }
    if(scene.frame!=bs4_port_frame_generation())return VK_NULL_HANDLE;
    BachataCamera::Push p{};
    const VkImageView depth=bs4_port_camera_for_scene(
        cb,scene.extent,&p,sizeof(p));
    if(!depth || !bs4_fsr31_supply_port_camera(
        cb,depth,&p,sizeof(p)))return VK_NULL_HANDLE;
    float near=0,far=0;
    if(!bs4_port_camera_range(cb,&near,&far) ||
       !bs4_fsr31_supply_camera_range(cb,near,far))return VK_NULL_HANDLE;
    VkImage rendered=VK_NULL_HANDLE;
    const VkExtent2D target{1280,720};
    if(!bs4_fsr31_pre_ui_dispatch(
        cb,scene.color,depth,scene.extent,target,&rendered))
        return VK_NULL_HANDLE;
    VkImageView result=bs4_fsr31_output_view(rendered);
    if(result) {
        std::lock_guard lock{mutex};
        auto& current=command_scenes[cb];
        if(current.color==scene.color)current.ready=false;
        if(latest_scene.color==scene.color)latest_scene.ready=false;
        prepared_outputs.erase(cb);
    }
    return result;
}

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
    // Guest games commonly render depth at a resolution different from
    // VideoOut (e.g. dynamic resolution, 3D scene vs 1080p UI). Requiring
    // exact 1920x1080 was the proven R10 fallback reason 5.
    uint64_t best=0;
    uint32_t tracked_depth=0,used_depth=0,transfer_depth=0;
    uint64_t closest_area=0;
    VkExtent2D closest{};
    VkFormat closest_format=VK_FORMAT_UNDEFINED;
    VkImageUsageFlags closest_usage=0;
    for (const auto& [handle,img] : images) {
        if (!(img.usage & VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT)) continue;
        tracked_depth++;
        if (!img.last_depth_use) continue;
        used_depth++;
        const uint64_t area=uint64_t(img.size.width)*img.size.height;
        if (area>closest_area) {
            closest_area=area;
            closest=img.size;closest_format=img.format;closest_usage=img.usage;
        }
        if (!(img.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT)) continue;
        transfer_depth++;
        if (!expected.width || !expected.height || !img.size.height) continue;
        const float actual=float(img.size.width)/float(img.size.height);
        const float desired=float(expected.width)/float(expected.height);
        if (std::abs(actual-desired)>0.085f*desired) continue;
        if (img.last_depth_use<=best) continue;
        best=img.last_depth_use;
        *out={handle,img.format,img.size,img.usage,img.layout,
              VK_IMAGE_ASPECT_DEPTH_BIT};
    }
    static bool reported_any=false;
    static bool reported_missing=false;
    if (best && !reported_any) {
        reported_any=true;
        std::fprintf(stderr,
          "[BS4_FSR31] depth selected real=%ux%u fmt=%u usage=0x%x expected=%ux%u\\n",
          out->size.width,out->size.height,unsigned(out->format),
          unsigned(out->usage),expected.width,expected.height);
    } else if (!best && !reported_missing) {
        reported_missing=true;
        std::fprintf(stderr,
          "[BS4_FSR31] depth candidates tracked=%u rendered=%u transferable=%u "
          "largest=%ux%u fmt=%u usage=0x%x expected=%ux%u\\n",
          tracked_depth,used_depth,transfer_depth,
          closest.width,closest.height,unsigned(closest_format),
          unsigned(closest_usage),expected.width,expected.height);
    }
    return best ? 1 : 0;
}

extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_begin_command(
        VkCommandBuffer cb,const VkCommandBufferBeginInfo* info) {
    if (!original_begin_command) return VK_ERROR_INITIALIZATION_FAILED;
    const auto status=original_begin_command(cb,info);
    if(status==VK_SUCCESS){std::lock_guard lock{mutex};command_scenes.erase(cb);}
    bs4_port_reset_cb(cb);
    bs4_port_ui_reset(cb);
    return status;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_reset_command(
        VkCommandBuffer cb,VkCommandBufferResetFlags flags) {
    if(!original_reset_command)return VK_ERROR_INITIALIZATION_FAILED;
    const auto status=original_reset_command(cb,flags);
    if(status==VK_SUCCESS){std::lock_guard lock{mutex};command_scenes.erase(cb);}
    bs4_port_reset_cb(cb);
    bs4_port_ui_reset(cb);
    return status;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_free_commands(
        VkDevice device,VkCommandPool pool,uint32_t count,const VkCommandBuffer* cb) {
    if(cb&&count){std::lock_guard lock{mutex};
        for(uint32_t i=0;i<count;++i){command_scenes.erase(cb[i]);
            bs4_port_reset_cb(cb[i]);
            bs4_port_ui_reset(cb[i]);}}
    if(original_free_commands)original_free_commands(device,pool,count,cb);
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
    // Dispatch BEFORE recording the UI depth attachment; otherwise generic
    // FSR3 would select the newly-starting UI depth instead of scene depth.
    VkRenderingInfo modified{};
    std::vector<VkRenderingAttachmentInfo> overrides;
    const bool composite=first_pre_ui_color(cb,info,modified,overrides);
    record_rendering(info);
    if(info)bs4_port_note_render(cb,
        info->pDepthAttachment?info->pDepthAttachment->imageView:VK_NULL_HANDLE,
        info->renderArea.extent,info->colorAttachmentCount);
    bs4_port_ui_install_rendering(original_begin_rendering,original_end_rendering,
       original_begin_rendering_khr,original_end_rendering_khr);
    VkRenderingInfo redirected{};
    const VkRenderingInfo* guest=composite?&modified:info;
    const bool host_redirect=bs4_port_ui_redirect_begin(cb,guest,false,&redirected);
    if(original_begin_rendering)
        original_begin_rendering(cb,host_redirect?&redirected:guest);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering(VkCommandBuffer cb) {
    if(original_end_rendering) original_end_rendering(cb);
    bs4_port_ui_redirect_end(cb);
    scene_rendering_ended(cb);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_barrier2(
    VkCommandBuffer cb,const VkDependencyInfo* dep) {
    if(dep) update_layout(dep->imageMemoryBarrierCount,dep->pImageMemoryBarriers);
    if(original_barrier2) original_barrier2(cb,dep);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_begin_rendering_khr(
    VkCommandBuffer cb,const VkRenderingInfo* info) {
    // Dispatch BEFORE recording the UI depth attachment; otherwise generic
    // FSR3 would select the newly-starting UI depth instead of scene depth.
    VkRenderingInfo modified{};
    std::vector<VkRenderingAttachmentInfo> overrides;
    const bool composite=first_pre_ui_color(cb,info,modified,overrides);
    record_rendering(info);
    if(info)bs4_port_note_render(cb,
        info->pDepthAttachment?info->pDepthAttachment->imageView:VK_NULL_HANDLE,
        info->renderArea.extent,info->colorAttachmentCount);
    bs4_port_ui_install_rendering(original_begin_rendering,original_end_rendering,
       original_begin_rendering_khr,original_end_rendering_khr);
    VkRenderingInfo redirected{};
    const VkRenderingInfo* guest=composite?&modified:info;
    const bool host_redirect=bs4_port_ui_redirect_begin(cb,guest,true,&redirected);
    if(original_begin_rendering_khr)
        original_begin_rendering_khr(cb,host_redirect?&redirected:guest);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering_khr(VkCommandBuffer cb) {
    if(original_end_rendering_khr) original_end_rendering_khr(cb);
    bs4_port_ui_redirect_end(cb);
    scene_rendering_ended(cb);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_barrier2_khr(
    VkCommandBuffer cb,const VkDependencyInfo* dep) {
    if(dep)update_layout(dep->imageMemoryBarrierCount,dep->pImageMemoryBarriers);
    if(original_barrier2_khr)original_barrier2_khr(cb,dep);
}
// Vulkan-hpp may resolve device commands through vkGetInstanceProcAddr,
// rather than vkGetDeviceProcAddr. Both paths must be intercepted.
extern "C" PFN_vkVoidFunction bs4_fsr31_wrap_vulkan_proc(
        const char* name, PFN_vkVoidFunction proc) {
    if(!name||!proc)return proc;
    #define BS4_WRAP_GIPA(method,symbol,target) \
        if(std::strcmp(name,symbol)==0) { \
            method=reinterpret_cast<decltype(method)>(proc); \
            return reinterpret_cast<PFN_vkVoidFunction>(target); \
        }
    BS4_WRAP_GIPA(original_begin_command,"vkBeginCommandBuffer",&bs4_cap_begin_command)
    BS4_WRAP_GIPA(original_reset_command,"vkResetCommandBuffer",&bs4_cap_reset_command)
    BS4_WRAP_GIPA(original_free_commands,"vkFreeCommandBuffers",&bs4_cap_free_commands)
    BS4_WRAP_GIPA(original_create_image,"vkCreateImage",&bs4_cap_create_image)
    BS4_WRAP_GIPA(original_destroy_image,"vkDestroyImage",&bs4_cap_destroy_image)
    BS4_WRAP_GIPA(original_create_image_view,"vkCreateImageView",&bs4_cap_create_image_view)
    BS4_WRAP_GIPA(original_destroy_image_view,"vkDestroyImageView",&bs4_cap_destroy_image_view)
    BS4_WRAP_GIPA(original_begin_rendering,"vkCmdBeginRendering",&bs4_cap_begin_rendering)
    BS4_WRAP_GIPA(original_end_rendering,"vkCmdEndRendering",&bs4_cap_end_rendering)
    BS4_WRAP_GIPA(original_barrier2,"vkCmdPipelineBarrier2",&bs4_cap_barrier2)
    BS4_WRAP_GIPA(original_begin_rendering_khr,"vkCmdBeginRenderingKHR",&bs4_cap_begin_rendering_khr)
    BS4_WRAP_GIPA(original_end_rendering_khr,"vkCmdEndRenderingKHR",&bs4_cap_end_rendering_khr)
    BS4_WRAP_GIPA(original_barrier2_khr,"vkCmdPipelineBarrier2KHR",&bs4_cap_barrier2_khr)
    #undef BS4_WRAP_GIPA
    return bs4_port_wrap_proc(name,bs4_port_ui_wrap_proc(name,proc));
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
    BS4_WRAP(original_begin_command,"vkBeginCommandBuffer",&bs4_cap_begin_command)
    BS4_WRAP(original_reset_command,"vkResetCommandBuffer",&bs4_cap_reset_command)
    BS4_WRAP(original_free_commands,"vkFreeCommandBuffers",&bs4_cap_free_commands)
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
    return bs4_port_wrap_proc(name,bs4_port_ui_wrap_proc(name,proc));
}
