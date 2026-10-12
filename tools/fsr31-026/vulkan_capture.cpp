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
#include <cmath>
#include <string>
#include <cstdint>
#include <cstdlib>
#include <cctype>
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
};
std::unordered_map<VkCommandBuffer, ScenePass> command_scenes;
/* Shader identity is supplied by the *existing core024* via Vulkan debug
 * object names: Vertex_0x0000000034e8a281, etc. Those are guest hashes, not
 * hashes fabricated from recompiled SPIR-V.
 * The known Bloodborne HUD hashes come from IFreemz's real pre-HUD path.
 * Unrecognized games retain the original R13 rendering unchanged. */
bool known_first_hud_shader(uint64_t hash) {
    return hash==0x34e8a281ULL || hash==0x81d336ceULL ||
           hash==0x09957251ULL || hash==0x24042a9bULL ||
           hash==0xa400228bULL;
}
std::unordered_map<VkShaderModule,uint64_t> vertex_module_hash;
std::unordered_map<VkPipeline,bool> known_ui_pipeline;
std::unordered_map<VkCommandBuffer,VkPipeline> graphics_pipeline_bound;
struct ActiveRendering {
    VkRenderingInfo info{};
    std::vector<VkRenderingAttachmentInfo> color;
    VkRenderingAttachmentInfo depth{},stencil{};
    bool has_depth=false,has_stencil=false,khr=false,attempted=false,valid=false;
};
std::unordered_map<VkCommandBuffer,ActiveRendering> active_rendering;
ActiveRendering copy_rendering(const VkRenderingInfo* in,bool khr) {
    ActiveRendering r{};
    if (!in || in->pNext || !in->pColorAttachments || !in->colorAttachmentCount)
        return r;
    r.info=*in;
    r.color.assign(in->pColorAttachments,in->pColorAttachments+in->colorAttachmentCount);
    if(in->pDepthAttachment){r.has_depth=true;r.depth=*in->pDepthAttachment;}
    if(in->pStencilAttachment){r.has_stencil=true;r.stencil=*in->pStencilAttachment;}
    r.khr=khr;r.valid=true;
    return r;
}

bool pre_ui_dispatch_logged=false;
bool pre_ui_eligible_logged=false;
using PreUiDispatch=int (*)(VkCommandBuffer,VkImageView,VkExtent2D,VkExtent2D,VkImage*);
extern "C" int bs4_fsr31_pre_ui_dispatch(VkCommandBuffer,VkImageView,
                VkImageView,VkExtent2D,VkExtent2D,VkImage*);

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
PFN_vkSetDebugUtilsObjectNameEXT original_object_name{};
PFN_vkCreateGraphicsPipelines original_create_graphics_pipelines{};
PFN_vkDestroyPipeline original_destroy_pipeline{};
PFN_vkCmdBindPipeline original_bind_pipeline{};
PFN_vkCmdDraw original_draw{};
PFN_vkCmdDrawIndexed original_draw_indexed{};
PFN_vkCmdDrawIndirect original_draw_indirect{};
PFN_vkCmdDrawIndexedIndirect original_draw_indexed_indirect{};

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
bool first_pre_ui_color(VkCommandBuffer cmd,const VkRenderingInfo* info,
                        VkRenderingInfo& modified,
                        std::vector<VkRenderingAttachmentInfo>& overrides,
                        bool verified_first_hud_draw) {
    if (!cmd || !info || !info->colorAttachmentCount ||
        !info->pColorAttachments || !info->pColorAttachments[0].imageView)
        return false;
    const uint32_t w=info->renderArea.extent.width;
    const uint32_t h=info->renderArea.extent.height;
    const auto view=info->pColorAttachments[0].imageView;
    ScenePass completed{};
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
        if (w>=600 && w<1280 && h>=320 && h<720) {
            const auto v=views.find(view);
            if (v!=views.end()) {
                const auto i=images.find(v->second.image);
                if (i!=images.end() &&
                    (i->second.usage & VK_IMAGE_USAGE_TRANSFER_SRC_BIT) &&
                    i->second.size.width>=w && i->second.size.width<=w+32 &&
                    i->second.size.height>=h && i->second.size.height<=h+32) {
                    stage.color=view;
                    stage.depth=info->pDepthAttachment?
                        info->pDepthAttachment->imageView:VK_NULL_HANDLE;
                    stage.extent={w,h};
                    stage.inside=true;
                    stage.ready=false;
                }
            }
            return false;
        }
        // The first 1080p pass was NOT necessarily the HUD in R14/R18:
        // lighting, bloom and post-processing also render at this extent.
        // Dispatch only at the first *recognized guest HUD shader draw*.
        if(!verified_first_hud_draw) return false;
        // Cross-CB ordering is not proven: scene must be complete on this CB.
        if(w<1280||h<700||!stage.ready||!stage.color||
           !stage.depth||stage.color==view)
            return false;
        const auto dst_v=views.find(view);
        if(dst_v==views.end())return false;
        const auto dst_i=images.find(dst_v->second.image);
        if(dst_i==images.end() ||
            !(dst_i->second.usage & VK_IMAGE_USAGE_TRANSFER_DST_BIT))
            return false;
        dst=dst_v->second.image;
        dst_previous_layout=dst_i->second.layout;
        dst_w=dst_i->second.size.width;
        dst_h=dst_i->second.size.height;
        completed=stage;
        stage.ready=false;
        stage.color=VK_NULL_HANDLE;
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
    if(!pre_ui_dispatch_logged){
        pre_ui_dispatch_logged=true;
        std::fprintf(stderr,
            "[BS4_FSR31] FIRST_PRE_UI_COMPOSITE FSR=1280x720 "
            "HUD_target=%ux%u\\n",w,h);
    }
    return true;
}
bool scene_ready_for_ui(const ActiveRendering& r,
     const decltype(command_scenes)::const_iterator& it) {
    if(it==command_scenes.end() || !it->second.ready ||
       !it->second.color || !it->second.depth)return false;
    const auto& c=it->second;
    // Require completed 3D scene with depth, at reduced input dimensions.
    if(c.extent.width<600 || c.extent.width>=1280 ||
       c.extent.height<320 || c.extent.height>=720)return false;
    if(r.info.renderArea.extent.width<1280 ||
       r.info.renderArea.extent.height<700)return false;
    // Some post passes have color attachments but no exact UI target.
    // Positive guest HUD shader identity is mandatory (checked by caller).
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

// The core024 shadPS4 shader compiler calls vkSetDebugUtilsObjectNameEXT with
// guest program names (Vertex_0x...); recover the guest hash before the
// Vulkan pipeline gets created. The SDK never changes the guest shader.
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_object_name(
    VkDevice device,const VkDebugUtilsObjectNameInfoEXT* info) {
    if(info && info->objectType==VK_OBJECT_TYPE_SHADER_MODULE &&
       info->pObjectName) {
        const char* p=std::strstr(info->pObjectName,"0x");
        if(p) {
            char* end=nullptr;
            const uint64_t hash=std::strtoull(p+2,&end,16);
            if(end!=p+2) {
                std::lock_guard lock{mutex};
                vertex_module_hash[(VkShaderModule)(uintptr_t)info->objectHandle]=hash;
            }
        }
    }
    return original_object_name?
           original_object_name(device,info):VK_ERROR_EXTENSION_NOT_PRESENT;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_create_graphics_pipelines(
    VkDevice device,VkPipelineCache cache,uint32_t count,
    const VkGraphicsPipelineCreateInfo* cis,const VkAllocationCallbacks* allocator,
    VkPipeline* output) {
    if(!original_create_graphics_pipelines)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult status=original_create_graphics_pipelines(
        device,cache,count,cis,allocator,output);
    if(output && cis && (status==VK_SUCCESS || status==VK_PIPELINE_COMPILE_REQUIRED)) {
        std::lock_guard lock{mutex};
        for(uint32_t i=0;i<count;i++) {
            if(!output[i])continue;
            bool ui=false;
            for(uint32_t j=0;j<cis[i].stageCount;j++) {
                const auto& st=cis[i].pStages[j];
                if(st.stage!=VK_SHADER_STAGE_VERTEX_BIT)continue;
                const auto it=vertex_module_hash.find(st.module);
                if(it!=vertex_module_hash.end() &&
                   known_first_hud_shader(it->second))ui=true;
            }
            known_ui_pipeline[output[i]]=ui;
            if(ui) {
                static bool logged=false;
                if(!logged) {
                    logged=true;
                    std::fprintf(stderr,
                        "[BS4_FSR31] first guest UI shader pipeline identified; "
                        "pre-HUD temporal path enabled\\n");
                }
            }
        }
    }
    return status;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_destroy_pipeline(
    VkDevice d,VkPipeline pipeline,const VkAllocationCallbacks* allocator) {
    {std::lock_guard lock{mutex};known_ui_pipeline.erase(pipeline);}
    if(original_destroy_pipeline)original_destroy_pipeline(d,pipeline,allocator);
}
thread_local VkCommandBuffer currently_bound_cb=VK_NULL_HANDLE;
thread_local bool currently_bound_ui_shader=false;
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_bind_pipeline(
    VkCommandBuffer cb,VkPipelineBindPoint point,VkPipeline pipeline) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS) {
        currently_bound_cb=cb;
        {
            std::lock_guard lock{mutex};
            const auto it=known_ui_pipeline.find(pipeline);
            currently_bound_ui_shader=it!=known_ui_pipeline.end() && it->second;
        }
    }
    if(original_bind_pipeline) original_bind_pipeline(cb,point,pipeline);
}

/* Called ONLY before a verified first guest HUD draw. Do not overwrite
 * arbitrary intermediate 1080p targets. Stop the active Vulkan dynamic
 * rendering pass, record real FSR3 640x360->1280x720 + composite, then
 * resume that exact pass with LOAD so all subsequent HUD draws are intact.
 *
 * This also avoids the R14/R18 error where the entire game scene appeared
 * corrupted while UI stayed legible. Unknown shaders pass through untouched.
 */
bool bs4_dispatch_at_first_ui_draw(VkCommandBuffer cb) {
    if(cb!=currently_bound_cb || !currently_bound_ui_shader)return false;
    ActiveRendering record{};
    {
        std::lock_guard lock{mutex};
        auto live=active_rendering.find(cb);
        auto scene=command_scenes.find(cb);
        if(live==active_rendering.end() || !live->second.valid ||
           live->second.attempted || !scene_ready_for_ui(live->second,scene))
           return false;
        live->second.attempted=true;
        record=live->second;
    }
    auto end_fn=record.khr?original_end_rendering_khr:original_end_rendering;
    auto begin_fn=record.khr?original_begin_rendering_khr:original_begin_rendering;
    if(!end_fn || !begin_fn)return false;
    // pNext chains and suspend/resume attachments cannot be safely replayed.
    if(record.info.pNext ||
       (record.info.flags & (VK_RENDERING_SUSPENDING_BIT |
                             VK_RENDERING_RESUMING_BIT)))return false;

    VkRenderingInfo resume=record.info;
    resume.pColorAttachments=record.color.data();
    for(auto& a:record.color)
        if(a.imageView)a.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
    if(record.has_depth) {
        record.depth.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        resume.pDepthAttachment=&record.depth;
    }
    if(record.has_stencil) {
        record.stencil.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        resume.pStencilAttachment=&record.stencil;
    }
    end_fn(cb);
    VkRenderingInfo modified{};
    std::vector<VkRenderingAttachmentInfo> overrides;
    const bool upscaled=first_pre_ui_color(cb,&resume,modified,overrides,true);
    // Regardless of dispatch outcome: this is a RESUMED render pass.
    // Clearing would destroy existing contents before drawing the HUD.
    if(upscaled)resume=modified;
    begin_fn(cb,&resume);
    if(upscaled){
        static bool once=false;
        if(!once){
            once=true;
            std::fprintf(stderr,
                "[BS4_FSR31] FIRST_GUEST_HUD_DRAW temporal applied "
                "without modifying an intermediate rendering pass\\n");
        }
    }
    return upscaled;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_draw(
    VkCommandBuffer cb,uint32_t vertexCount,uint32_t instanceCount,
    uint32_t firstVertex,uint32_t firstInstance) {
    bs4_dispatch_at_first_ui_draw(cb);
    if(original_draw)original_draw(cb,vertexCount,instanceCount,firstVertex,firstInstance);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_draw_indexed(
    VkCommandBuffer cb,uint32_t indexCount,uint32_t instanceCount,
    uint32_t firstIndex,int32_t vertexOffset,uint32_t firstInstance) {
    bs4_dispatch_at_first_ui_draw(cb);
    if(original_draw_indexed)original_draw_indexed(
        cb,indexCount,instanceCount,firstIndex,vertexOffset,firstInstance);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_draw_indirect(
    VkCommandBuffer cb,VkBuffer buffer,VkDeviceSize offset,uint32_t drawCount,uint32_t stride) {
    bs4_dispatch_at_first_ui_draw(cb);
    if(original_draw_indirect) original_draw_indirect(cb,buffer,offset,drawCount,stride);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_draw_indexed_indirect(
    VkCommandBuffer cb,VkBuffer buffer,VkDeviceSize offset,uint32_t drawCount,uint32_t stride) {
    bs4_dispatch_at_first_ui_draw(cb);
    if(original_draw_indexed_indirect)original_draw_indexed_indirect(
        cb,buffer,offset,drawCount,stride);
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
    if(status==VK_SUCCESS){std::lock_guard lock{mutex};command_scenes.erase(cb);active_rendering.erase(cb);graphics_pipeline_bound.erase(cb);}
    return status;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_cap_reset_command(
        VkCommandBuffer cb,VkCommandBufferResetFlags flags) {
    if(!original_reset_command)return VK_ERROR_INITIALIZATION_FAILED;
    const auto status=original_reset_command(cb,flags);
    if(status==VK_SUCCESS){std::lock_guard lock{mutex};command_scenes.erase(cb);active_rendering.erase(cb);graphics_pipeline_bound.erase(cb);}
    return status;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_free_commands(
        VkDevice device,VkCommandPool pool,uint32_t count,const VkCommandBuffer* cb) {
    if(cb&&count){std::lock_guard lock{mutex};
        for(uint32_t i=0;i<count;++i){
            command_scenes.erase(cb[i]);
            active_rendering.erase(cb[i]);
            graphics_pipeline_bound.erase(cb[i]);
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
    const bool composite=first_pre_ui_color(cb,info,modified,overrides,false);
    record_rendering(info);
    {std::lock_guard lock{mutex};
        auto scene=command_scenes.find(cb);
        if(scene!=command_scenes.end() && scene->second.ready)
            active_rendering[cb]=copy_rendering(info,false);
        else active_rendering.erase(cb);
    }
    if(original_begin_rendering)
        original_begin_rendering(cb,composite?&modified:info);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering(VkCommandBuffer cb) {
    if(original_end_rendering) original_end_rendering(cb);
    scene_rendering_ended(cb);
    {std::lock_guard lock{mutex};active_rendering.erase(cb);}
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
    const bool composite=first_pre_ui_color(cb,info,modified,overrides,false);
    record_rendering(info);
    {std::lock_guard lock{mutex};
        auto scene=command_scenes.find(cb);
        if(scene!=command_scenes.end() && scene->second.ready)
            active_rendering[cb]=copy_rendering(info,true);
        else active_rendering.erase(cb);
    }
    if(original_begin_rendering_khr)
        original_begin_rendering_khr(cb,composite?&modified:info);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_cap_end_rendering_khr(VkCommandBuffer cb) {
    if(original_end_rendering_khr) original_end_rendering_khr(cb);
    scene_rendering_ended(cb);
    {std::lock_guard lock{mutex};active_rendering.erase(cb);}
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
    return proc;
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
    return proc;
}
