// SPDX-License-Identifier: GPL-2.0-or-later
// Capture real Vulkan image descriptions from the renderer. No guest shader
// hashes, no Mesa/Turnip private memory-layout reads.
#include "vulkan_capture.h"
#include "native_scene_observer.h"
#include "native_compute_state.h"
#include "temporal_lifetime.h"
#include "port_scene_frame.h"
#include "native_ui_targets.h"
extern "C" int bs4_fsr31_owner_requested();
#include <cstdlib>
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
    VkSampleCountFlagBits samples{};
};
struct View {
    VkImage image = VK_NULL_HANDLE;
    VkImageAspectFlags aspects{};
    VkFormat format = VK_FORMAT_UNDEFINED;
    VkImageViewCreateInfo description{};
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
    bool khr = false;
};
std::unordered_map<VkCommandBuffer, ScenePass> command_scenes;
// A cross-command scene is never used at mere render-pass completion.
// It must have passed through a successful queue submit first.
ScenePass submitted_scene{};
VkCommandBuffer submitted_owner{};
VkQueue submitted_queue{};
bool multiple_queues=false;
extern "C" int bs4_fsr31_single_graphics_queue();
bool pre_ui_dispatch_logged=false;
bool pre_ui_eligible_logged=false;
using PreUiDispatch=int (*)(VkCommandBuffer,VkImageView,VkExtent2D,VkExtent2D,VkImage*);
extern "C" int bs4_fsr31_pre_ui_dispatch(VkCommandBuffer,VkImageView,
                VkImageView,VkExtent2D,VkExtent2D,VkImage*);
extern "C" int bs4_fsr31_pre_ui_prepare(VkCommandBuffer,VkImageView,
                VkImageView,VkExtent2D,VkExtent2D);
extern "C" VkPhysicalDevice bs4_fsr31_physical_device();

PFN_vkBeginCommandBuffer original_begin_command{};
PFN_vkResetCommandBuffer original_reset_command{};
PFN_vkFreeCommandBuffers original_free_commands{};
PFN_vkQueueSubmit original_queue_submit{};
PFN_vkQueueSubmit2 original_queue_submit2{};
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
void mirrored_ui_barriers(VkCommandBuffer cb,const VkDependencyInfo* dep,PFN_vkCmdPipelineBarrier2 original) {
    if(!dep||!original||!dep->pImageMemoryBarriers)return;
    std::vector<VkImageMemoryBarrier2> mirrored;
    for(uint32_t i=0;i<dep->imageMemoryBarrierCount;i++) {
        VkImageMemoryBarrier2 b{};if(bs4_native_ui_barrier(cb,dep->pImageMemoryBarriers[i],b))mirrored.push_back(b);
    }
    if(mirrored.empty())return;
    VkDependencyInfo info{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};info.dependencyFlags=dep->dependencyFlags;
    info.imageMemoryBarrierCount=mirrored.size();info.pImageMemoryBarriers=mirrored.data();
    original(cb,&info);update_layout(info.imageMemoryBarrierCount,info.pImageMemoryBarriers);
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

// A native pass must fit its actual attachments. Reduce only a proven scene:
// valid native camera, origin zero, and a first color allocated at its render
// size. Native-sized HUD and unrelated small passes remain unchanged.
bool checked_scene_area(VkCommandBuffer cb,const VkRenderingInfo* original,VkRenderingInfo& checked) {
    const char* mode=std::getenv("BACHATA_FSR31_INPUT");
    if(!mode||std::strcmp(mode,"port")||!original||original->pNext||
       original->viewMask||original->layerCount!=1||
       original->renderArea.offset.x||original->renderArea.offset.y||
       !original->colorAttachmentCount||!original->pColorAttachments)return false;
    VkImageView depth{};VkExtent2D camera{};
    if(!bs4_native_scene_camera(cb,&depth,&camera))return false;
    std::lock_guard lock{mutex};
    auto valid=[&](const VkRenderingAttachmentInfo& att,bool first) {
        if(!att.imageView)return !first;
        if(att.resolveMode||att.resolveImageView)return false;
        auto view=views.find(att.imageView);if(view==views.end())return false;
        auto image=images.find(view->second.image);if(image==images.end())return false;
        return image->second.size.width>=camera.width&&image->second.size.height>=camera.height&&
               (!first||(image->second.size.width==camera.width&&image->second.size.height==camera.height));
    };
    for(uint32_t i=0;i<original->colorAttachmentCount;i++)
        if(!valid(original->pColorAttachments[i],i==0))return false;
    if(original->pDepthAttachment&&!valid(*original->pDepthAttachment,false))return false;
    if(original->pStencilAttachment&&!valid(*original->pStencilAttachment,false))return false;
    const auto area=original->renderArea.extent;
    if(area.width<camera.width||area.height<camera.height||
       (area.width==camera.width&&area.height==camera.height))return false;
    checked=*original;checked.renderArea.extent=camera;
    static bool logged=false;if(!logged){logged=true;std::fprintf(stderr,
        "[BS4_R13_PORT] native scene render area %ux%u -> %ux%u camera_and_attachments_verified=1\n",
        area.width,area.height,camera.width,camera.height);}
    return true;
}

/* An actual reduced scene (not a post-present downsample) is characterized
 * by a small render area, color image of matching size, and a completed
 * Vulkan dynamic-rendering pass. The transition to a larger output-image
 * pass is the earliest safe point to upscale before UI drawing begins.
 *
 * This never changes the guest's render dimensions. Unsupported cases leave
 * the original shadPS4 command sequence untouched.
 */
bool first_pre_ui_color(VkCommandBuffer cmd,const VkRenderingInfo* info,
                        VkRenderingInfo& modified,
                        std::vector<VkRenderingAttachmentInfo>& overrides) {
    if (!cmd || !info || !info->colorAttachmentCount ||
        !info->pColorAttachments || !info->pColorAttachments[0].imageView)
        return false;
    const bool port=std::getenv("BACHATA_FSR31_INPUT")&&
        std::strcmp(std::getenv("BACHATA_FSR31_INPUT"),"port")==0;
    VkImageView camera_depth{};VkExtent2D camera_size{};
    const bool camera_ready=port&&bs4_native_scene_camera(cmd,&camera_depth,&camera_size);
    const uint32_t w=info->renderArea.extent.width;
    const uint32_t h=info->renderArea.extent.height;
    const auto view=info->pColorAttachments[0].imageView;
    ScenePass completed{};
    VkCommandBuffer accepted_origin{};
    VkImage dst=VK_NULL_HANDLE, src=VK_NULL_HANDLE;
    const VkImageLayout dst_layout=info->pColorAttachments[0].imageLayout;
    VkImageLayout dst_previous_layout=VK_IMAGE_LAYOUT_UNDEFINED;
    uint32_t dst_w=0,dst_h=0;
    {
        std::lock_guard lock{mutex};
        auto& stage=command_scenes[cmd];
        // Never activate on menu frames that did not contain a 3D scene.
        // Support 640x360, 960x540, 1152x648; 1280x720 does not need
        // temporal upscale if the requested presentation is also 720p.
        // The camera must identify THIS rendering extent before replacing
        // the previously completed low-resolution scene. A 1280x720 UI
        // pass is not automatically another game scene: doing so discarded
        // the 640x360 scene ahead of the native UI handoff.
        if (w>=600 && h>=320 &&
            ((w<1280&&h<720)||
             (port&&w==1280&&h==720&&!bs4_native_scene_ui_boundary(cmd))) &&
            (!port||(camera_ready&&camera_size.width==w&&camera_size.height==h))) {
            // A new scene replaces the previous candidate even when its
            // camera, format or allocation is rejected. Never compose stale
            // scene contents into a later HUD pass.
            stage={};
            if(port&&info->colorAttachmentCount!=1)return false;
            if(port&&(!camera_ready||camera_size.width!=w||camera_size.height!=h))return false;
            const auto v=views.find(view);
            if (v!=views.end()) {
                const auto i=images.find(v->second.image);
                if (i!=images.end() &&
                    (i->second.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT) &&
                    (!port||i->second.format==VK_FORMAT_R8G8B8A8_UNORM) &&
                    i->second.size.width>=w && i->second.size.width<=w+32 &&
                    i->second.size.height>=h && i->second.size.height<=h+32) {
                    stage.color=view;
                    stage.depth=port?camera_depth:(info->pDepthAttachment?
                        info->pDepthAttachment->imageView:VK_NULL_HANDLE);
                    stage.extent={w,h};
                    stage.inside=true;
                    stage.ready=false;
                    static bool firstLdr=false;
                    if(!firstLdr) {
                        firstLdr=true;
                        std::fprintf(stderr,
                            "[BS4_FSR31] FIRST_LDR_SCENE_CAPTURE scene=%ux%u "
                            "source=%p depth=%p command=%p\\n",
                            w,h,reinterpret_cast<void*>(stage.color),
                            reinterpret_cast<void*>(stage.depth),reinterpret_cast<void*>(cmd));
                    }
                }
            }
            return false;
        }
        // This is the first full-size UI pass following a completed small
        // 3D scene on the SAME command buffer. Cross-CB ordering is unknown:
        // never issue Vulkan commands based on unproven inter-CB ordering.
        if(port&&!bs4_native_scene_ui_boundary(cmd))return false;
        if(w<1280||h<700)return false;
        ScenePass eligible=stage;
        // A scene on a different CB is eligible only after real submission
        // to the one verified graphics queue. A merely recorded/ended source
        // is NOT synchronized with this UI command buffer.
        if((!eligible.ready||!eligible.color||!eligible.depth||eligible.color==view)&&
           submitted_owner&&submitted_owner!=cmd&&submitted_scene.ready&&
           submitted_scene.color&&submitted_scene.depth&&!multiple_queues&&
           bs4_fsr31_single_graphics_queue()) {
            eligible=submitted_scene;
            accepted_origin=submitted_owner;
            static bool loggedCross=false;
            if(!loggedCross) {
                loggedCross=true;
                std::fprintf(stderr,
                    "[BS4_FSR31] FIRST_SUBMITTED_CROSS_CB scene_cmd=%p ui_cmd=%p queue=%p\\n",
                    reinterpret_cast<void*>(submitted_owner),reinterpret_cast<void*>(cmd),
                    reinterpret_cast<void*>(submitted_queue));
            }
        }
        if(!eligible.ready||!eligible.color||!eligible.depth||eligible.color==view)
            return false;
        const auto dst_v=views.find(view);
        if(dst_v==views.end())return false;
        const auto dst_i=images.find(dst_v->second.image);
        if(dst_i==images.end() ||
            (port&&dst_i->second.format!=VK_FORMAT_R8G8B8A8_UNORM) ||
            !(dst_i->second.usage & VK_IMAGE_USAGE_TRANSFER_DST_BIT))
            return false;
        dst=dst_v->second.image;
        dst_previous_layout=dst_i->second.layout;
        dst_w=dst_i->second.size.width;
        dst_h=dst_i->second.size.height;
        completed=eligible;
    }
    if (!pre_ui_eligible_logged) {
        pre_ui_eligible_logged=true;
        std::fprintf(stderr,
           "[BS4_FSR31] pre-UI candidate scene=%ux%u output=%ux%u "
           "ui_target=%ux%u\\n",
           completed.extent.width,completed.extent.height,w,h,dst_w,dst_h);
    }
    if(dst_w<w||dst_h<h)return false;
    // Output is 720p just like the Android Bloodborne port. The UI target
    // may still be 1080p until the guest's UI resolution is independently
    // decoupled; resample the upscaled background without changing HUD draws.
    const VkExtent2D upscale_extent{1280,720};
    // Reuse the original G-buffer's real motion, but only after its source
    // CB was successfully submitted on the sole graphics queue.
    if(accepted_origin)
        bs4_fsr31_port_authorize_submitted(accepted_origin,cmd,completed.depth);
    VkImage upscaled=VK_NULL_HANDLE;
    if(!bs4_fsr31_pre_ui_dispatch(cmd,completed.color,completed.depth,
                                    completed.extent,upscale_extent,&upscaled)||!upscaled)
        return false;
    // Pre-UI barrier + blit: both images are outside a rendering instance.
    // Return the UI attachment to its original layout before vkCmdBeginRendering.
    VkImageMemoryBarrier2 bars[2]{};
    for(auto& b:bars) {
        b.sType=VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2;
        b.srcStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
        b.srcAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|
                        VK_ACCESS_2_MEMORY_WRITE_BIT;
        b.dstStageMask=VK_PIPELINE_STAGE_2_TRANSFER_BIT;
        b.dstAccessMask=VK_ACCESS_2_TRANSFER_READ_BIT|
                        VK_ACCESS_2_TRANSFER_WRITE_BIT;
        b.srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        b.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
    }
    bars[0].image=upscaled;
    bars[0].oldLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    bars[0].newLayout=VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    bars[1].image=dst;
    // An UNDEFINED attachment would discard the newly upscaled background.
    // Switch it to a valid color attachment layout before the HUD begins.
    const VkImageLayout ui_layout =
        dst_layout==VK_IMAGE_LAYOUT_UNDEFINED ?
        VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL : dst_layout;
    // AttachmentInfo::imageLayout is the layout required *during* the UI
    // pass, not necessarily the current image layout before its first draw.
    // The Vulkan barrier tracker stores the preceding transition.
    bars[1].oldLayout=dst_previous_layout;
    bars[1].newLayout=VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    VkDependencyInfo dep{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
    dep.imageMemoryBarrierCount=2;
    dep.pImageMemoryBarriers=bars;
    vkCmdPipelineBarrier2(cmd,&dep);
    VkImageBlit blit{};
    blit.srcSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
    blit.srcOffsets[1]={1280,720,1};
    blit.dstSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
    blit.dstOffsets[1]={int32_t(w),int32_t(h),1};
    vkCmdBlitImage(cmd,upscaled,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
        dst,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&blit,VK_FILTER_LINEAR);
    for(auto& b:bars) {
        std::swap(b.oldLayout,b.newLayout);
        b.srcStageMask=VK_PIPELINE_STAGE_2_TRANSFER_BIT;
        b.srcAccessMask=VK_ACCESS_2_TRANSFER_READ_BIT|
                        VK_ACCESS_2_TRANSFER_WRITE_BIT;
        b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
        b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|
                        VK_ACCESS_2_MEMORY_WRITE_BIT;
    }
    bars[1].newLayout=ui_layout;
    vkCmdPipelineBarrier2(cmd,&dep);
    {
        std::lock_guard lock{mutex};
        const auto current=images.find(dst);
        if(current!=images.end())current->second.layout=ui_layout;
    }
    // The background is now populated. Preserve it when the game's UI
    // starts drawing; otherwise a CLEAR loadOp would erase the FSR result.
    modified=*info;
    overrides.assign(info->pColorAttachments,
                     info->pColorAttachments+info->colorAttachmentCount);
    overrides[0].loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
    overrides[0].imageLayout=ui_layout;
    modified.pColorAttachments=overrides.data();
    // Consume only after dispatch and composition have been recorded. A
    // rejected preparation must leave the completed candidate available.
    {
        std::lock_guard lock{mutex};
        const auto it=command_scenes.find(cmd);
        if(it!=command_scenes.end()&&it->second.ready&&
           it->second.color==completed.color&&it->second.depth==completed.depth)
            it->second={};
        // Never reuse a previously submitted scene from a different CB.
        if(submitted_scene.color==completed.color&&
           submitted_scene.depth==completed.depth){
            submitted_scene={};submitted_owner={};
        }
    }
    if(!pre_ui_dispatch_logged){
        pre_ui_dispatch_logged=true;
        std::fprintf(stderr,
            "[BS4_FSR31] FIRST_PRE_UI_COMPOSITE FSR=1280x720 "
            "HUD_target=%ux%u\\n",w,h);
    }
    return true;
}
void scene_rendering_ended(VkCommandBuffer command) {
    std::lock_guard lock{mutex};
    const auto it=command_scenes.find(command);
    if(it!=command_scenes.end()&&it->second.inside) {
        it->second.ready=true;
        it->second.inside=false;
    }
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
        i->second.usage,i->second.layout,v->second.aspects,i->second.samples};
    return 1;
}

// A native scheduler callback is useful only after a real low-resolution
// scene has been identified.  During loading/menu screens n035 enqueued
// thousands of callbacks without ever reaching the temporal renderer.
extern "C" int bs4_fsr31_any_scene_ready() {
    std::lock_guard lock{mutex};
    for(const auto& [cmd,stage]:command_scenes)
        if(stage.color&&stage.depth&&(stage.inside||stage.ready)&&
           stage.extent.width>=600&&stage.extent.width<1280&&
           stage.extent.height>=320&&stage.extent.height<720)
            return 1;
    return 0;
}
extern "C" int bs4_fsr31_capture_scene(VkCommandBuffer cb,VkImageView* color,VkImageView* depth,VkExtent2D* extent) {
    if(!color||!depth||!extent)return 0;
    std::lock_guard lock{mutex};const auto it=command_scenes.find(cb);
    if(it==command_scenes.end()||!it->second.color||(!it->second.inside&&!it->second.ready))return 0;
    *color=it->second.color;*depth=it->second.depth;*extent=it->second.extent;return 1;
}
extern "C" int bs4_fsr31_capture_view(VkImageView view,VkImageViewCreateInfo* out) {
    if(!out)return 0;std::lock_guard lock{mutex};const auto it=views.find(view);
    if(it==views.end())return 0;*out=it->second.description;return 1;
}
extern "C" void bs4_fsr31_track_ui_image(VkImage image,const VkImageCreateInfo* ci,
    VkImageView view,const VkImageViewCreateInfo* vi) {
    if(!image||!ci||!view||!vi)return;std::lock_guard lock{mutex};
    if(!images.count(image))images[image]={ci->format,{ci->extent.width,ci->extent.height},
        ci->usage,ci->initialLayout,{},0,ci->samples};
    views[view]={image,vi->subresourceRange.aspectMask,vi->format,*vi};
}
extern "C" void bs4_fsr31_untrack_ui_image(VkImage image,VkImageView view) {
    std::lock_guard lock{mutex};images.erase(image);views.erase(view);
}

extern "C" int bs4_fsr31_run_scaled_ui(VkCommandBuffer cb,VkImageView uiColor,VkImageView uiDepth) {
    ScenePass scene{};
    {
        std::lock_guard lock{mutex};const auto it=command_scenes.find(cb);
        if(it==command_scenes.end())return 0;scene=it->second;
    }
    Bs4NativeUiBoundary boundary{};
    Bs4FsrCaptureImage source{},target{},depthTarget{};
    if(!scene.color||(!scene.inside&&!scene.ready)||
       // HUD may share the 3D image or use a separate attachment.
       // native_ui_draw validates that the boundary belongs to this draw.
       !bs4_native_scene_ui_state(cb,boundary)||!boundary.color||
       !bs4_fsr31_capture_image(scene.color,&source)||
       !bs4_fsr31_capture_image(uiColor,&target)||source.image==target.image||
       source.format!=VK_FORMAT_R8G8B8A8_UNORM||target.format!=source.format||
       target.size.width!=1280||target.size.height!=720||
       source.samples!=VK_SAMPLE_COUNT_1_BIT||target.samples!=VK_SAMPLE_COUNT_1_BIT||
       source.size.width<scene.extent.width||source.size.height<scene.extent.height||
       !(source.usage&VK_IMAGE_USAGE_TRANSFER_SRC_BIT)||
       !(target.usage&VK_IMAGE_USAGE_TRANSFER_DST_BIT)||
       !(target.usage&VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT))return 0;
    const auto physical=bs4_fsr31_physical_device();if(!physical)return 0;
    VkFormatProperties features{};vkGetPhysicalDeviceFormatProperties(physical,target.format,&features);
    if(!(features.optimalTilingFeatures&VK_FORMAT_FEATURE_BLIT_SRC_BIT)||
       !(features.optimalTilingFeatures&VK_FORMAT_FEATURE_BLIT_DST_BIT)||
       !(features.optimalTilingFeatures&VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT))return 0;
    if(boundary.depth) {
        Bs4FsrCaptureImage originalDepth{};
        if(!uiDepth||!bs4_fsr31_capture_image(boundary.depth,&originalDepth)||
           !bs4_fsr31_capture_image(uiDepth,&depthTarget)||
           originalDepth.format!=depthTarget.format||
           originalDepth.samples!=VK_SAMPLE_COUNT_1_BIT||depthTarget.samples!=VK_SAMPLE_COUNT_1_BIT||
           depthTarget.size.width!=1280||depthTarget.size.height!=720||
           !(depthTarget.usage&VK_IMAGE_USAGE_TRANSFER_DST_BIT)||
           !(depthTarget.usage&VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT))return 0;
    }
    auto end=scene.khr?reinterpret_cast<PFN_vkCmdEndRendering>(original_end_rendering_khr):original_end_rendering;
    auto begin=scene.khr?reinterpret_cast<PFN_vkCmdBeginRendering>(original_begin_rendering_khr):original_begin_rendering;
    if(!begin||(scene.inside&&!end))return 0;
    // All UI targets and copy fallback prerequisites are validated first.
    // A missing temporal history/context takes RunUiOnly's copy path; it
    // never reopens the original reduced LDR pass with speculative LOAD.
    const bool temporal=scene.depth&&bs4_fsr31_pre_ui_prepare(cb,scene.color,
        scene.depth,scene.extent,{1280,720});
    if(scene.inside){end(cb);scene_rendering_ended(cb);bs4_native_scene_end(cb);}
    VkImage upscaled{};
    const bool dispatched=temporal&&bs4_fsr31_pre_ui_dispatch(cb,scene.color,
        scene.depth,scene.extent,{1280,720},&upscaled);
    const VkImage background=dispatched?upscaled:source.image;
    const VkImageLayout old=dispatched?VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL:source.layout;
    auto transition=[&](VkImage image,VkImageAspectFlags aspect,VkImageLayout previous,VkImageLayout next){
        VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
        b.srcStageMask=b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
        b.srcAccessMask=b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;
        b.oldLayout=previous;b.newLayout=next;b.image=image;
        b.srcQueueFamilyIndex=b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        b.subresourceRange={aspect,0,1,0,1};VkDependencyInfo dep{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
        dep.imageMemoryBarrierCount=1;dep.pImageMemoryBarriers=&b;vkCmdPipelineBarrier2(cb,&dep);
    };
    transition(background,VK_IMAGE_ASPECT_COLOR_BIT,old,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);
    transition(target.image,VK_IMAGE_ASPECT_COLOR_BIT,target.layout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    VkImageBlit blit{};blit.srcSubresource=blit.dstSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
    blit.srcOffsets[1]=dispatched?VkOffset3D{1280,720,1}:
        VkOffset3D{int32_t(scene.extent.width),int32_t(scene.extent.height),1};
    blit.dstOffsets[1]={1280,720,1};
    vkCmdBlitImage(cb,background,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,target.image,
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&blit,VK_FILTER_LINEAR);
    transition(background,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,old);
    transition(target.image,VK_IMAGE_ASPECT_COLOR_BIT,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL);
    VkRenderingAttachmentInfo color{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
    color.imageView=uiColor;color.imageLayout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
    color.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;color.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
    VkRenderingAttachmentInfo depth{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
    VkRenderingInfo info{VK_STRUCTURE_TYPE_RENDERING_INFO};info.renderArea.extent={1280,720};
    info.layerCount=1;info.colorAttachmentCount=1;info.pColorAttachments=&color;
    if(boundary.depth) {
        const bool stencil=depthTarget.format==VK_FORMAT_D32_SFLOAT_S8_UINT||depthTarget.format==VK_FORMAT_D24_UNORM_S8_UINT;
        const VkImageAspectFlags aspects=VK_IMAGE_ASPECT_DEPTH_BIT|(stencil?VK_IMAGE_ASPECT_STENCIL_BIT:0);
        transition(depthTarget.image,aspects,depthTarget.layout,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
        const VkClearDepthStencilValue clear{1.f,0};const VkImageSubresourceRange range{aspects,0,1,0,1};
        vkCmdClearDepthStencilImage(cb,depthTarget.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&clear,1,&range);
        transition(depthTarget.image,aspects,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL);
        depth.imageView=uiDepth;depth.imageLayout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
        depth.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;depth.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
        info.pDepthAttachment=&depth;if(stencil)info.pStencilAttachment=&depth;
    }
    begin(cb,&info);
    {
        std::lock_guard lock{mutex};command_scenes.erase(cb);
        const auto c=images.find(target.image);if(c!=images.end())c->second.layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
        const auto d=images.find(depthTarget.image);if(d!=images.end())d->second.layout=VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL;
    }
    // Record the actual dispatch *and* the VkImage passed to the HUD blit.
    // A preset, device attach or low-resolution camera is not FSR proof.
    static bool firstTemporalTarget=false,firstCopyFallback=false;
    if(dispatched&&!firstTemporalTarget) {
        firstTemporalTarget=true;
        std::fprintf(stderr,
            "[BS4_FSR31] FIRST_TEMPORAL_HUD_TARGET dispatch=1 "
            "scene=%ux%u reconstructed=1280x720 src=%p dst=%p "
            "ui_view=%p command=%p blit_recorded=1\\n",
            scene.extent.width,scene.extent.height,
            reinterpret_cast<void*>(background),reinterpret_cast<void*>(target.image),
            reinterpret_cast<void*>(uiColor),reinterpret_cast<void*>(cb));
    } else if(!dispatched&&!firstCopyFallback) {
        firstCopyFallback=true;
        std::fprintf(stderr,
            "[BS4_FSR31] HUD_COPY_ONLY prepare=%d dispatch=0 scene=%ux%u "
            "dst=%p\\n",int(temporal),scene.extent.width,scene.extent.height,
            reinterpret_cast<void*>(target.image));
    }
    return dispatched?2:1; // 2: real temporal background; 1: Port UI copy fallback
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
              VK_IMAGE_ASPECT_DEPTH_BIT,img.samples};
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

// Record queue ordering without altering any VkSubmitInfo or GPU command.
static void observe_submission(VkQueue queue,uint32_t count,const VkSubmitInfo* infos) {
    if(!queue||!infos||!bs4_fsr31_single_graphics_queue())return;
    std::lock_guard lock{mutex};
    if(submitted_queue&&submitted_queue!=queue){multiple_queues=true;submitted_scene={};submitted_owner={};return;}
    submitted_queue=queue;
    if(multiple_queues)return;
    for(uint32_t i=0;i<count;++i)for(uint32_t n=0;n<infos[i].commandBufferCount;++n) {
        const auto cmd=infos[i].pCommandBuffers[n];
        const auto it=command_scenes.find(cmd);
        if(it!=command_scenes.end()&&it->second.ready&&it->second.color&&it->second.depth) {
            submitted_scene=it->second;submitted_owner=cmd;
            static bool logged=false;if(!logged){logged=true;std::fprintf(stderr,
                "[BS4_FSR31] FIRST_SUBMITTED_LDR_SCENE source=%p command=%p queue=%p\\n",
                reinterpret_cast<void*>(submitted_scene.color),
                reinterpret_cast<void*>(cmd),reinterpret_cast<void*>(queue));}
        }
    }
}
static void observe_submission2(VkQueue queue,uint32_t count,const VkSubmitInfo2* infos) {
    if(!queue||!infos||!bs4_fsr31_single_graphics_queue())return;
    std::lock_guard lock{mutex};
    if(submitted_queue&&submitted_queue!=queue){multiple_queues=true;submitted_scene={};submitted_owner={};return;}
    submitted_queue=queue;
    if(multiple_queues)return;
    for(uint32_t i=0;i<count;++i)for(uint32_t n=0;n<infos[i].commandBufferInfoCount;++n) {
        const auto cmd=infos[i].pCommandBufferInfos[n].commandBuffer;
        const auto it=command_scenes.find(cmd);
        if(it!=command_scenes.end()&&it->second.ready&&it->second.color&&it->second.depth) {
            submitted_scene=it->second;submitted_owner=cmd;
            static bool logged=false;if(!logged){logged=true;std::fprintf(stderr,
                "[BS4_FSR31] FIRST_SUBMITTED_LDR_SCENE source=%p command=%p queue=%p\\n",
                reinterpret_cast<void*>(submitted_scene.color),
                reinterpret_cast<void*>(cmd),reinterpret_cast<void*>(queue));}
        }
    }
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_queue_submit(VkQueue q,uint32_t count,
       const VkSubmitInfo* infos,VkFence fence) {
    if(!original_queue_submit)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult result=original_queue_submit(q,count,infos,fence);
    if(result==VK_SUCCESS){
        for(uint32_t i=0;i<count;++i)for(uint32_t n=0;n<infos[i].commandBufferCount;++n)
            bs4_temporal_submitted(q,infos[i].pCommandBuffers[n],original_queue_submit,nullptr);
        observe_submission(q,count,infos);
    }
    return result;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_queue_submit2(VkQueue q,uint32_t count,
       const VkSubmitInfo2* infos,VkFence fence) {
    if(!original_queue_submit2)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult result=original_queue_submit2(q,count,infos,fence);
    if(result==VK_SUCCESS){
        for(uint32_t i=0;i<count;++i)for(uint32_t n=0;n<infos[i].commandBufferInfoCount;++n)
            bs4_temporal_submitted(q,infos[i].pCommandBufferInfos[n].commandBuffer,nullptr,original_queue_submit2);
        observe_submission2(q,count,infos);
    }
    return result;
}
extern "C" void bs4_fsr31_capture_present() {
    std::lock_guard lock{mutex};
    submitted_scene={};submitted_owner={};submitted_queue={};multiple_queues=false;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_begin_command(
        VkCommandBuffer cb,const VkCommandBufferBeginInfo* info) {
    if (!original_begin_command) return VK_ERROR_INITIALIZATION_FAILED;
    const auto status=original_begin_command(cb,info);
    if(status==VK_SUCCESS){bs4_temporal_discard(cb);bs4_native_compute_reset(cb);bs4_native_ui_reset(cb);bs4_native_scene_reset(cb);std::lock_guard lock{mutex};command_scenes.erase(cb);
        if(submitted_owner==cb){submitted_owner=VK_NULL_HANDLE;submitted_scene={};}}
    return status;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_reset_command(
        VkCommandBuffer cb,VkCommandBufferResetFlags flags) {
    if(!original_reset_command)return VK_ERROR_INITIALIZATION_FAILED;
    const auto status=original_reset_command(cb,flags);
    if(status==VK_SUCCESS){bs4_temporal_discard(cb);bs4_native_compute_reset(cb);bs4_native_ui_reset(cb);bs4_native_scene_reset(cb);std::lock_guard lock{mutex};command_scenes.erase(cb);
        if(submitted_owner==cb){submitted_owner=VK_NULL_HANDLE;submitted_scene={};}}
    return status;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_free_commands(
        VkDevice device,VkCommandPool pool,uint32_t count,const VkCommandBuffer* cb) {
    if(cb&&count){
        for(uint32_t i=0;i<count;++i){bs4_temporal_discard(cb[i]);bs4_native_compute_reset(cb[i]);bs4_native_ui_reset(cb[i]);bs4_native_scene_reset(cb[i]);}
        std::lock_guard lock{mutex};
        for(uint32_t i=0;i<count;++i){
            command_scenes.erase(cb[i]);
            if(submitted_owner==cb[i]){submitted_owner={};submitted_scene={};}
        }}
    if(original_free_commands)original_free_commands(device,pool,count,cb);
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_create_image(
    VkDevice dev,const VkImageCreateInfo* ci,const VkAllocationCallbacks* ac,VkImage* img) {
    if(!original_create_image) return VK_ERROR_INITIALIZATION_FAILED;
    auto r=original_create_image(dev,ci,ac,img);
    if(r==VK_SUCCESS && ci && img) {
        std::lock_guard lock{mutex};
        images[*img]={ci->format,{ci->extent.width,ci->extent.height},ci->usage,
                      ci->initialLayout,{},0,ci->samples};
    }
    return r;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_destroy_image(
    VkDevice dev,VkImage img,const VkAllocationCallbacks* ac) {
    bs4_native_ui_release(img);
    {std::lock_guard lock{mutex};
        if(submitted_scene.color){
            const auto v=views.find(submitted_scene.color);
            if(v!=views.end()&&v->second.image==img){submitted_owner={};submitted_scene={};}
        }
        images.erase(img);
    }
    if(original_destroy_image) original_destroy_image(dev,img,ac);
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_create_image_view(
    VkDevice dev,const VkImageViewCreateInfo* ci,const VkAllocationCallbacks* ac,
    VkImageView* view) {
    if(!original_create_image_view) return VK_ERROR_INITIALIZATION_FAILED;
    auto r=original_create_image_view(dev,ci,ac,view);
    if(r==VK_SUCCESS && ci && view) {
        std::lock_guard lock{mutex};
        views[*view]={ci->image,ci->subresourceRange.aspectMask,ci->format,*ci};
    }
    return r;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_destroy_image_view(
    VkDevice dev,VkImageView view,const VkAllocationCallbacks* ac) {
    bs4_native_ui_release_view(view);
    {std::lock_guard lock{mutex}; views.erase(view);}
    if(original_destroy_image_view) original_destroy_image_view(dev,view,ac);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_begin_rendering(
    VkCommandBuffer cb,const VkRenderingInfo* info) {
    VkRenderingInfo redirected{};VkRenderingAttachmentInfo redirectedColor{},redirectedDepth{},redirectedStencil{};
    if(bs4_native_ui_rendering(cb,info,redirected,redirectedColor,redirectedDepth,redirectedStencil)) {
        record_rendering(&redirected);
        if(original_begin_rendering)original_begin_rendering(cb,&redirected);return;
    }
    // Dispatch BEFORE recording the UI depth attachment; otherwise generic
    // FSR3 would select the newly-starting UI depth instead of scene depth.
    bs4_native_scene_begin(cb,info);
    VkRenderingInfo checked{};
    if(checked_scene_area(cb,info,checked))info=&checked;
    VkRenderingInfo modified{};
    std::vector<VkRenderingAttachmentInfo> overrides;
    const bool composite=first_pre_ui_color(cb,info,modified,overrides);
    bs4_native_scene_begin(cb,info);
    record_rendering(info);
    if(original_begin_rendering)
        original_begin_rendering(cb,composite?&modified:info);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering(VkCommandBuffer cb) {
    if(original_end_rendering) original_end_rendering(cb);
    scene_rendering_ended(cb);
    bs4_native_scene_end(cb);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_barrier2(
    VkCommandBuffer cb,const VkDependencyInfo* dep) {
    mirrored_ui_barriers(cb,dep,original_barrier2);
    if(dep) update_layout(dep->imageMemoryBarrierCount,dep->pImageMemoryBarriers);
    if(original_barrier2) original_barrier2(cb,dep);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_begin_rendering_khr(
    VkCommandBuffer cb,const VkRenderingInfo* info) {
    VkRenderingInfo redirected{};VkRenderingAttachmentInfo redirectedColor{},redirectedDepth{},redirectedStencil{};
    if(bs4_native_ui_rendering(cb,info,redirected,redirectedColor,redirectedDepth,redirectedStencil)) {
        record_rendering(&redirected);
        if(original_begin_rendering_khr)original_begin_rendering_khr(cb,&redirected);return;
    }
    // Dispatch BEFORE recording the UI depth attachment; otherwise generic
    // FSR3 would select the newly-starting UI depth instead of scene depth.
    bs4_native_scene_begin(cb,info);
    VkRenderingInfo checked{};
    if(checked_scene_area(cb,info,checked))info=&checked;
    VkRenderingInfo modified{};
    std::vector<VkRenderingAttachmentInfo> overrides;
    const bool composite=first_pre_ui_color(cb,info,modified,overrides);
    {
        std::lock_guard lock{mutex};const auto it=command_scenes.find(cb);
        if(it!=command_scenes.end()&&it->second.inside)it->second.khr=true;
    }
    bs4_native_scene_begin(cb,info);
    record_rendering(info);
    if(original_begin_rendering_khr)
        original_begin_rendering_khr(cb,composite?&modified:info);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering_khr(VkCommandBuffer cb) {
    if(original_end_rendering_khr) original_end_rendering_khr(cb);
    scene_rendering_ended(cb);
    bs4_native_scene_end(cb);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_barrier2_khr(
    VkCommandBuffer cb,const VkDependencyInfo* dep) {
    mirrored_ui_barriers(cb,dep,reinterpret_cast<PFN_vkCmdPipelineBarrier2>(original_barrier2_khr));
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
            if(proc!=reinterpret_cast<PFN_vkVoidFunction>(target))\
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
    BS4_WRAP_GIPA(original_queue_submit,"vkQueueSubmit",&bs4_cap_queue_submit)
    BS4_WRAP_GIPA(original_queue_submit2,"vkQueueSubmit2",&bs4_cap_queue_submit2)
    BS4_WRAP_GIPA(original_queue_submit2,"vkQueueSubmit2KHR",&bs4_cap_queue_submit2)
    BS4_WRAP_GIPA(original_end_rendering_khr,"vkCmdEndRenderingKHR",&bs4_cap_end_rendering_khr)
    BS4_WRAP_GIPA(original_barrier2_khr,"vkCmdPipelineBarrier2KHR",&bs4_cap_barrier2_khr)
    #undef BS4_WRAP_GIPA
    return bs4_native_compute_wrap(name,bs4_native_scene_wrap(name,proc));
}
extern "C" VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetDeviceProcAddr(
    VkDevice device,const char* name) {
    const auto original=next_device_proc_addr();
    if(!original || !name)return nullptr;
    const auto proc=original(device,name);
    if(!proc)return nullptr;
    if(!bs4_fsr31_owner_requested())return proc;
    #define BS4_WRAP(method,symbol,target) \
        if(std::strcmp(name,symbol)==0) { \
            if(proc!=reinterpret_cast<PFN_vkVoidFunction>(target))\
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
    BS4_WRAP(original_queue_submit,"vkQueueSubmit",&bs4_cap_queue_submit)
    BS4_WRAP(original_queue_submit2,"vkQueueSubmit2",&bs4_cap_queue_submit2)
    BS4_WRAP(original_queue_submit2,"vkQueueSubmit2KHR",&bs4_cap_queue_submit2)
    BS4_WRAP(original_end_rendering_khr,"vkCmdEndRenderingKHR",&bs4_cap_end_rendering_khr)
    BS4_WRAP(original_barrier2_khr,"vkCmdPipelineBarrier2KHR",&bs4_cap_barrier2_khr)
    #undef BS4_WRAP
    return bs4_native_compute_wrap(name,bs4_native_scene_wrap(name,proc));
}
