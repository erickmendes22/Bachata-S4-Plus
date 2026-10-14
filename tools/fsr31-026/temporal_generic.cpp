// SPDX-License-Identifier: GPL-2.0-or-later
// Generic temporal FSR 3.1 path using real Vulkan color and depth resources.
// The motion shader estimates optical flow from consecutive color frames.
// Unlike game-specific forks, this path does not rely on guest shader hashes.
#include "vulkan_capture.h"
#include "ffx_vk_portable.h"
#include "flow_spv.h"
#include "camera_motion_spv.h"
#include "port_scene_frame.h"
#include "native_compute_state.h"
#include "gpu_frame_probe.h"
#include <cstdlib>
#include <vulkan/vulkan.h>
#include <algorithm>
#include <atomic>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <mutex>
#include <vector>
#include <cstring>
namespace {
struct Surface {
    VkImage image{};
    VkImageView view{};
    VkDeviceMemory memory{};
    VkFormat format{};
    VkExtent2D size{};
    VkImageUsageFlags usage{};
    VkImageAspectFlags aspect{},layout_aspect{};
    VkImageLayout layout = VK_IMAGE_LAYOUT_UNDEFINED;
};
struct Frame {
    Surface scene;
    Surface depth;
    Surface motion;
    Surface output;
    VkDescriptorSet descriptor{};
    Bs4GpuFrameProbe probe;
    // A ring slot remains owned by a command buffer until it is submitted
    // and the GPU completion fence signals. Never rewrite its descriptors,
    // scene, motion or output while the GPU can still reference them.
    VkFence completion{};
    VkCommandBuffer recordedBy{};
    bool recorded{},submitted{};
};
std::mutex mutex;
VkDevice device{};
VkPhysicalDevice physical{};
FfxVkPortableUpscaleContext* fsr{};
FfxVkPortableUpscaleCreateInfo config{};
VkDescriptorPool descriptors{};
VkDescriptorSetLayout desc_layout{};
VkPipelineLayout pipeline_layout{};
VkPipeline flow_pipeline{};
VkSampler sampler{};
std::vector<Frame> frames;
Surface previous;
size_t cursor=0;
bool has_previous=false,abandoned_history=false;
bool port_inputs=false;
std::atomic<uint64_t> ready_port_extent{0};
std::atomic<bool> real_dispatch_seen{false};
uint64_t frame_id=0,last_temporal_camera=0;
std::chrono::steady_clock::time_point last_frame{};
bool once_logged=false;
std::atomic<uint64_t> reported_reasons{0};
void report_once(unsigned reason, const char* description) {
    const uint64_t bit = uint64_t(1) << reason;
    if (!(reported_reasons.fetch_or(bit, std::memory_order_relaxed) & bit))
        std::fprintf(stderr, "[BS4_FSR31] generic fallback reason=%u %s\\n",
                     reason, description);
}

bool result(VkResult r, const char* name) {
    if(r==VK_SUCCESS) return true;
    std::fprintf(stderr,"[BS4_FSR31] %s failed=%d\n",name,int(r));
    return false;
}
uint32_t select_memory(uint32_t mask) {
    VkPhysicalDeviceMemoryProperties props{};
    vkGetPhysicalDeviceMemoryProperties(physical,&props);
    for(uint32_t pass=0;pass<2;++pass) {
        for(uint32_t i=0;i<props.memoryTypeCount;++i) {
            if(!(mask&(1u<<i)))continue;
            if(!pass && !(props.memoryTypes[i].propertyFlags&
                            VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT))continue;
            return i;
        }
    }
    return UINT32_MAX;
}
bool alloc(Surface& out,VkFormat format,VkExtent2D size,
           VkImageUsageFlags usage,VkImageAspectFlags aspect) {
    out.format=format;out.size=size;out.usage=usage;out.aspect=aspect;out.layout_aspect=aspect;
    // Combined depth/stencil images require joint layout transitions unless
    // separateDepthStencilLayouts was explicitly enabled. The sampled view
    // below remains depth-only; no optional device feature is assumed.
    if(format==VK_FORMAT_D32_SFLOAT_S8_UINT||format==VK_FORMAT_D24_UNORM_S8_UINT)
        out.layout_aspect=VK_IMAGE_ASPECT_DEPTH_BIT|VK_IMAGE_ASPECT_STENCIL_BIT;
    VkImageCreateInfo ci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
    ci.imageType=VK_IMAGE_TYPE_2D;
    ci.extent={size.width,size.height,1};
    ci.mipLevels=1;ci.arrayLayers=1;ci.format=format;
    ci.tiling=VK_IMAGE_TILING_OPTIMAL;ci.initialLayout=VK_IMAGE_LAYOUT_UNDEFINED;
    ci.usage=usage;ci.samples=VK_SAMPLE_COUNT_1_BIT;
    if(!result(vkCreateImage(device,&ci,nullptr,&out.image),"vkCreateImage"))return false;
    VkMemoryRequirements requirements{};
    vkGetImageMemoryRequirements(device,out.image,&requirements);
    const uint32_t mem=select_memory(requirements.memoryTypeBits);
    if(mem==UINT32_MAX)return false;
    VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    ai.allocationSize=requirements.size;ai.memoryTypeIndex=mem;
    if(!result(vkAllocateMemory(device,&ai,nullptr,&out.memory),"vkAllocateMemory"))return false;
    if(!result(vkBindImageMemory(device,out.image,out.memory,0),"vkBindImageMemory"))return false;
    VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
    vi.image=out.image;vi.viewType=VK_IMAGE_VIEW_TYPE_2D;vi.format=format;
    vi.subresourceRange={aspect,0,1,0,1};
    return result(vkCreateImageView(device,&vi,nullptr,&out.view),"vkCreateImageView");
}
void free_surface(Surface& s){
    if(s.view)vkDestroyImageView(device,s.view,nullptr);
    if(s.image)vkDestroyImage(device,s.image,nullptr);
    if(s.memory)vkFreeMemory(device,s.memory,nullptr);
    s={};
}
void barrier(VkCommandBuffer cb, VkImage image, VkImageAspectFlags aspect,
             VkImageLayout old_layout,VkImageLayout next_layout) {
    if(old_layout==next_layout)return;
    VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
    b.srcStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    b.srcAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;
    b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;
    b.oldLayout=old_layout;b.newLayout=next_layout;b.image=image;
    b.srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
    b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
    b.subresourceRange={aspect,0,1,0,1};
    VkDependencyInfo dependency{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};
    dependency.imageMemoryBarrierCount=1;
    dependency.pImageMemoryBarriers=&b;
    vkCmdPipelineBarrier2(cb,&dependency);
}
void transit(VkCommandBuffer cb,Surface& s,VkImageLayout next) {
    barrier(cb,s.image,s.layout_aspect,s.layout,next);s.layout=next;
}
void free_all() {
    ready_port_extent.store(0,std::memory_order_release);
    if(device)vkDeviceWaitIdle(device);
    if(fsr) {ffxVkPortableUpscaleContextDestroy(fsr);fsr=nullptr;}
    if(flow_pipeline)vkDestroyPipeline(device,flow_pipeline,nullptr);
    if(pipeline_layout)vkDestroyPipelineLayout(device,pipeline_layout,nullptr);
    if(desc_layout)vkDestroyDescriptorSetLayout(device,desc_layout,nullptr);
    if(descriptors)vkDestroyDescriptorPool(device,descriptors,nullptr);
    if(sampler)vkDestroySampler(device,sampler,nullptr);
    flow_pipeline={};pipeline_layout={};desc_layout={};
    descriptors={};sampler={};
    for(auto& f:frames){if(f.submitted)bs4_probe_resolve(f.probe,device);bs4_probe_release(f.probe,device);if(f.completion)vkDestroyFence(device,f.completion,nullptr);
        free_surface(f.scene);free_surface(f.depth);
        free_surface(f.motion);free_surface(f.output);}
    frames.clear();free_surface(previous);
    has_previous=false;abandoned_history=false;frame_id=0;last_temporal_camera=0;cursor=0;
}
bool build_compute(){
    VkDescriptorSetLayoutBinding bindings[3]{};
    for(uint32_t i=0;i<3;++i) {
        bindings[i].binding=i;bindings[i].descriptorCount=1;
        bindings[i].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;
        bindings[i].descriptorType=port_inputs?
            (i==1?VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE):
            (i==2?VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER);
    }
    VkDescriptorSetLayoutCreateInfo dci{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
    dci.bindingCount=3;dci.pBindings=bindings;
    if(!result(vkCreateDescriptorSetLayout(device,&dci,nullptr,&desc_layout),"layout"))return false;
    VkPushConstantRange range{VK_SHADER_STAGE_COMPUTE_BIT,0,
        uint32_t(port_inputs?sizeof(BachataCamera::Push):16)};
    VkPipelineLayoutCreateInfo pci{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    pci.setLayoutCount=1;pci.pSetLayouts=&desc_layout;
    pci.pushConstantRangeCount=1;pci.pPushConstantRanges=&range;
    if(!result(vkCreatePipelineLayout(device,&pci,nullptr,&pipeline_layout),"pipe layout"))return false;
    VkShaderModule module{};
    VkShaderModuleCreateInfo sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    sm.codeSize=port_inputs?sizeof(BS4_FSR31_CAMERA_SPV):sizeof(BS4_FSR31_FLOW_SPV);
    sm.pCode=port_inputs?BS4_FSR31_CAMERA_SPV:BS4_FSR31_FLOW_SPV;
    if(!result(vkCreateShaderModule(device,&sm,nullptr,&module),"flow shader"))return false;
    VkPipelineShaderStageCreateInfo stage{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};
    stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;stage.module=module;stage.pName="main";
    VkComputePipelineCreateInfo ci{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
    ci.stage=stage;ci.layout=pipeline_layout;
    auto r=vkCreateComputePipelines(device,VK_NULL_HANDLE,1,&ci,nullptr,&flow_pipeline);
    vkDestroyShaderModule(device,module,nullptr);
    if(!result(r,"flow compute pipeline"))return false;
    VkSamplerCreateInfo sci{VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
    sci.magFilter=VK_FILTER_LINEAR;sci.minFilter=VK_FILTER_LINEAR;
    sci.addressModeU=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeV=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeW=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    if(!result(vkCreateSampler(device,&sci,nullptr,&sampler),"motion sampler"))return false;
    VkDescriptorPoolSize sizes[]={
        {VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,16},
        {VK_DESCRIPTOR_TYPE_STORAGE_IMAGE,8},
        {VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,16}};
    VkDescriptorPoolCreateInfo pi{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
    pi.maxSets=6;pi.poolSizeCount=3;pi.pPoolSizes=sizes;
    return result(vkCreateDescriptorPool(device,&pi,nullptr,&descriptors),"flow descriptor pool");
}
FfxVkPortableImage describe(const Surface& s,FfxVkPortableResourceState state) {
    FfxVkPortableImage im{};
    im.structSize=sizeof(im);im.image=s.image;im.format=s.format;
    im.extent={s.size.width,s.size.height};
    im.mipCount=1;im.arrayLayers=1;im.usage=s.usage;
    im.aspect=s.aspect;im.state=state;return im;
}
bool allocate_for(FfxVkPortableDeviceInfo info, VkExtent2D render,VkExtent2D output,
                  VkFormat color_format,VkFormat depth_format) {
    // Recorded-but-unsubmitted CBs cannot be drained by vkDeviceWaitIdle.
    // Keep their slots alive; retry the resize after actual submission.
    for(const auto& slot:frames)if(slot.recorded)return false;
    free_all();
    config={};config.structSize=sizeof(config);
    config.maxRenderSize={render.width,render.height};
    config.maxOutputSize={output.width,output.height};
    if(!build_compute())return false;
    const VkImageUsageFlags sampled=VK_IMAGE_USAGE_SAMPLED_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT|
                                    VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
    const VkImageUsageFlags storage=VK_IMAGE_USAGE_STORAGE_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|
                                    VK_IMAGE_USAGE_TRANSFER_DST_BIT|VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
    frames.resize(4);
    for(auto& f:frames) {
        VkFenceCreateInfo fenceInfo{VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
        if(!result(vkCreateFence(device,&fenceInfo,nullptr,&f.completion),
                   "FSR completion fence"))return false;
        if(!alloc(f.scene,color_format,render,sampled,VK_IMAGE_ASPECT_COLOR_BIT) ||
           !alloc(f.depth,depth_format,render,sampled,VK_IMAGE_ASPECT_DEPTH_BIT) ||
           !alloc(f.motion,VK_FORMAT_R16G16_SFLOAT,render,storage,VK_IMAGE_ASPECT_COLOR_BIT) ||
           !alloc(f.output,VK_FORMAT_R8G8B8A8_UNORM,output,storage,VK_IMAGE_ASPECT_COLOR_BIT))
            return false;
        VkDescriptorSetAllocateInfo ai{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
        ai.descriptorPool=descriptors;ai.descriptorSetCount=1;ai.pSetLayouts=&desc_layout;
        if(!result(vkAllocateDescriptorSets(device,&ai,&f.descriptor),"descriptors"))return false;
    }
    if(!port_inputs && !alloc(previous,color_format,render,sampled,VK_IMAGE_ASPECT_COLOR_BIT))return false;
    const auto r=ffxVkPortableUpscaleContextCreate(&info,&config,&fsr);
    if(r!=FFX_VK_PORTABLE_OK) {
        std::fprintf(stderr,"[BS4_FSR31] FSR3.1 Vulkan context error=%d\n",int(r));
        return false;
    }
    if(port_inputs&&output.width==1280&&output.height==720)
        ready_port_extent.store((uint64_t(render.width)<<32)|render.height,std::memory_order_release);
    std::fprintf(stderr,"[BS4_FSR31] temporal context ready %ux%u->%ux%u\n",
         render.width,render.height,output.width,output.height);
    return true;
}
void flow(VkCommandBuffer cb,const Frame& f,VkExtent2D size,
          const Bs4PortCameraDispatch* camera) {
    VkDescriptorImageInfo resources[3]{};
    resources[0]={sampler,f.scene.view,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
    resources[1]={sampler,previous.view,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
    resources[2]={VK_NULL_HANDLE,f.motion.view,VK_IMAGE_LAYOUT_GENERAL};
    if(camera) {
        resources[0]={VK_NULL_HANDLE,f.depth.view,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
        resources[1]={VK_NULL_HANDLE,f.motion.view,VK_IMAGE_LAYOUT_GENERAL};
        resources[2]=resources[0]; // Port mode=0: object vectors unavailable
    }
    VkWriteDescriptorSet writes[3]{};
    for(uint32_t i=0;i<3;i++) {
        writes[i]={VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
        writes[i].dstSet=f.descriptor;writes[i].dstBinding=i;
        writes[i].descriptorType=camera?
            (i==1?VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE):
            (i==2?VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER);
        writes[i].descriptorCount=1;writes[i].pImageInfo=&resources[i];
    }
    vkUpdateDescriptorSets(device,3,writes,0,nullptr);
    vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,flow_pipeline);
    vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipeline_layout,
                            0,1,&f.descriptor,0,nullptr);
    struct Push{int width,height,first,pad;} pc{int(size.width),int(size.height),!has_previous,0};
    if(camera) vkCmdPushConstants(cb,pipeline_layout,VK_SHADER_STAGE_COMPUTE_BIT,
        0,sizeof(camera->motion),&camera->motion);
    else vkCmdPushConstants(cb,pipeline_layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),&pc);
    vkCmdDispatch(cb,(size.width+7)/8,(size.height+7)/8,1);
}
} // namespace

static uint64_t generic_render_impl(
    const FfxVkPortableDeviceInfo* owned,VkCommandBuffer cb,VkImageView input,
    VkExtent2D input_extent,VkExtent2D output_extent,int preset,int hdr,int pre_ui,
    VkImageView scene_depth_view,bool prepare_only) {
    if(!owned||!cb||!input||hdr||preset<0||preset>4){report_once(1,"missing arguments or HDR/preset unsupported");return 0;}
    if(!owned->shaderStorageImageWriteWithoutFormatEnabled){report_once(2,"storage image write without format disabled");return 0;}
    if(output_extent.width==0||output_extent.height==0 ||
       input_extent.width==0||input_extent.height==0) {
        report_once(3,"input/output extent zero");return 0;
    }
    const char* mode=std::getenv("BACHATA_FSR31_INPUT");
    const bool want_port=mode&&std::strcmp(mode,"port")==0;
    // R11 incorrectly downsized the fully rendered 1920x1080 scene to
    // 427x240 and then reconstructed 1280x720. This cannot improve game
    // performance and destroys visual detail. Host temporal upscaling must
    // consume the *actual* smaller scene image, never synthesize one.
    // Exactly matches the original shadPS4 FsrPass skip condition.
    if (input_extent.width >= output_extent.width &&
        input_extent.height >= output_extent.height &&
        !(want_port&&pre_ui&&input_extent.width==output_extent.width&&
          input_extent.height==output_extent.height)) {
        report_once(14, "source already >= presentation size; no forced downsample");
        return 0;
    }
    // Explicit opt-in while the native producer is integrated. This is not
    // enabled in a release APK until the R13 renderer supplies the contract.
    Bs4PortCameraDispatch camera{};
    if(want_port&&(!pre_ui||!bs4_fsr31_port_camera(cb,scene_depth_view,input_extent,camera))) {
        report_once(16,"native Port camera/depth handoff missing; no guessed temporal input");
        return 0;
    }
    Bs4FsrCaptureImage color{},depth{};
    if(!bs4_fsr31_capture_image_at(cb,input,&color)){report_once(4,"Vulkan color image view not captured");return 0;}
    if (pre_ui) {
        // Depth must originate in the same completed Vulkan render pass as
        // the selected reduced scene, not merely the globally newest image.
        if (!scene_depth_view || !bs4_fsr31_capture_image_at(cb,scene_depth_view,&depth) ||
            !(depth.aspects & VK_IMAGE_ASPECT_DEPTH_BIT)) {
            report_once(5,"pre-UI matching scene depth image not available");
            return 0;
        }
    } else if (!bs4_fsr31_capture_depth(input_extent,&depth)) {
        report_once(5,"depth image matching render extent not captured");
        return 0;
    }
    if(color.samples!=VK_SAMPLE_COUNT_1_BIT||depth.samples!=VK_SAMPLE_COUNT_1_BIT) {
        report_once(18,"multisampled temporal inputs require an explicit resolve");return 0;
    }
    if(want_port && (color.size.width<input_extent.width ||
                     color.size.height<input_extent.height)) {
        report_once(17,"Port scene rectangle exceeds color allocation");return 0;
    }
    if(!(color.usage&VK_IMAGE_USAGE_TRANSFER_SRC_BIT)){report_once(6,"color image lacks transfer-source usage");return 0;}
    if(!(depth.usage&VK_IMAGE_USAGE_TRANSFER_SRC_BIT)){report_once(7,"depth image lacks transfer-source usage");return 0;}
    // Begin with the formats available in the native FSR Vulkan backend.
    // The guest video output may use sRGB, 10-bit UNORM, or RGBA16f.
    // Convert color to a linear float16 intermediate; do not send
    // gamma-encoded UNORM output to the original float HDR pipeline through
    // vkCmdBlitImage; first verify that format supports blitting.
    VkFormatProperties color_props{},rgba_props{};
    vkGetPhysicalDeviceFormatProperties(owned->physicalDevice,color.format,&color_props);
    vkGetPhysicalDeviceFormatProperties(owned->physicalDevice,
                                         VK_FORMAT_R16G16B16A16_SFLOAT,&rgba_props);
    if (!(color_props.optimalTilingFeatures & VK_FORMAT_FEATURE_BLIT_SRC_BIT) ||
        !(rgba_props.optimalTilingFeatures & VK_FORMAT_FEATURE_BLIT_DST_BIT)) {
        std::fprintf(stderr,
          "[BS4_FSR31] color source fmt=%d size=%ux%u usage=0x%x "
          "blit_src=%d destination float16 blit_dst=%d\\n",int(color.format),
          color.size.width,color.size.height,unsigned(color.usage),
          !!(color_props.optimalTilingFeatures&VK_FORMAT_FEATURE_BLIT_SRC_BIT),
          !!(rgba_props.optimalTilingFeatures&VK_FORMAT_FEATURE_BLIT_DST_BIT));
        report_once(8,"color source/destination cannot be blitted to RGBA16F");
        return 0;
    }
    static bool reported_color=false;
    if(!reported_color) {
        reported_color=true;
        std::fprintf(stderr,
           "[BS4_FSR31] color source fmt=%d size=%ux%u usage=0x%x -> RGBA16F\\n",
           int(color.format),color.size.width,color.size.height,unsigned(color.usage));
    }
    if(depth.format!=VK_FORMAT_D32_SFLOAT &&
       depth.format!=VK_FORMAT_D32_SFLOAT_S8_UINT &&
       depth.format!=VK_FORMAT_D24_UNORM_S8_UINT){report_once(9,"depth pixel format unsupported");return 0;}
    if(!color.image||!depth.image){report_once(10,"null captured image handle");return 0;}
    if (pre_ui && (depth.size.width < input_extent.width ||
                   depth.size.height < input_extent.height)) {
        report_once(11,"scene depth extent smaller than scene render area");
        return 0;
    }
    VkFormatProperties depth_features{};
    vkGetPhysicalDeviceFormatProperties(owned->physicalDevice,depth.format,&depth_features);
    const bool depth_can_blit =
        (depth_features.optimalTilingFeatures & VK_FORMAT_FEATURE_BLIT_SRC_BIT) &&
        (depth_features.optimalTilingFeatures & VK_FORMAT_FEATURE_BLIT_DST_BIT);
    std::lock_guard lock{mutex};
    device=owned->device;physical=owned->physicalDevice;
    constexpr float ratio[]={1.f,1.5f,1.7f,2.f,3.f};
    // Use the guest's *real* render dimensions. The preset selects an
    // expected game render-scale; it cannot magically reduce GPU draw cost
    // after the game has already rendered its full-resolution frame.
    VkExtent2D internal{input_extent.width, input_extent.height};
    const float actual_x = float(output_extent.width)/float(internal.width);
    const float actual_y = float(output_extent.height)/float(internal.height);
    // The preset configures the guest's *internal* size. In pre-UI mode
    // the output is deliberately 720p: Ultra renders 640x360 -> 1280x720
    // (2x rather than the 3x ratio of a nominal 1080p Ultra preset).
    if (pre_ui) {
        if (actual_x < 1.0f || actual_y < 1.0f ||
            actual_x > 4.0f || actual_y > 4.0f ||
            std::abs(actual_x-actual_y)>0.06f) {
            report_once(15,"invalid pre-UI scene to 720p scale");
            return 0;
        }
    } else if (std::abs(actual_x-ratio[preset])>0.20f ||
               std::abs(actual_y-ratio[preset])>0.20f) {
        report_once(15,"actual scene dimensions do not match selected quality preset");
        return 0;
    }
    // A depth copy cannot be made from a mismatched guest depth target.
    // PS4 scene depth commonly has a different size than the displayed
    // VideoOut image. Its pixels are resampled to the same render extent as
    // the color intermediate (using nearest depth blit only if supported).
    if(!depth.size.width||!depth.size.height){report_once(11,"depth extent invalid");return 0;}
    if (!want_port && (internal.width!=depth.size.width || internal.height!=depth.size.height) &&
        !depth_can_blit){report_once(12,"scaled depth blit unsupported by GPU");return 0;}
    if(abandoned_history || !fsr || port_inputs!=want_port || config.maxRenderSize.width!=internal.width ||
       config.maxRenderSize.height!=internal.height ||
       config.maxOutputSize.width!=output_extent.width ||
       config.maxOutputSize.height!=output_extent.height ||
       frames[0].scene.format!=VK_FORMAT_R16G16B16A16_SFLOAT ||frames[0].depth.format!=depth.format) {
        port_inputs=want_port;
        if(!allocate_for(*owned,internal,output_extent,VK_FORMAT_R16G16B16A16_SFLOAT,depth.format)){report_once(13,"FSR resource or context creation failed");return 0;}
    }
    // Preparation performs resource validation/allocation only. It must not
    // advance the ring/history or record commands into an active render pass.
    if(prepare_only)return 1;
    if(want_port&&has_previous&&camera.frameId==last_temporal_camera){
        report_once(23,"temporal frame already recorded; do not advance AMD history twice");return 0;
    }
    // Select a frame only if never recorded or fully completed on the GPU.
    // vkGetFenceStatus is nonblocking: a busy ring skips FSR rather than
    // corrupting in-flight resources or blocking the emulation thread.
    for(auto& slot:frames)if(slot.submitted&&vkGetFenceStatus(device,slot.completion)==VK_SUCCESS)
        bs4_probe_resolve(slot.probe,device);
    Frame* available=nullptr;
    for(size_t i=0;i<frames.size();++i) {
        Frame& candidate=frames[(cursor+i)%frames.size()];
        if(candidate.recorded)continue;
        if(candidate.submitted) {
            const VkResult done=vkGetFenceStatus(device,candidate.completion);
            if(done!=VK_SUCCESS)continue;
            if(!result(vkResetFences(device,1,&candidate.completion),
                       "FSR completion fence reset"))continue;
            candidate.submitted=false;
        }
        available=&candidate;cursor=(cursor+i+1)%frames.size();break;
    }
    if(!available){
        report_once(19,"temporal slot busy: preserve original scene rather than overwrite in-flight GPU resources");
        return 0;
    }
    if(!bs4_native_compute_can_restore(cb)){report_once(22,"unsupported native compute state; keep original rendering");return 0;}
    struct RestoreNativeCompute {
        VkCommandBuffer cb;
        explicit RestoreNativeCompute(VkCommandBuffer c):cb(c){bs4_native_compute_enter_sdk();}
        ~RestoreNativeCompute(){bs4_native_compute_restore(cb);bs4_native_compute_leave_sdk();}
    } restore{cb};
    Frame& f=*available;
    // Copies/motion/probes already record GPU work before AMD can fail.
    // Reserve the slot now, even if the caller must take the native fallback.
    f.recordedBy=cb;f.recorded=true;
    bs4_probe_begin(f.probe,device,physical,frame_id,want_port?camera.frameId:0);
    transit(cb,f.scene,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    barrier(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,color.layout,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);
    bs4_probe_image(f.probe,cb,color.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,internal,color.format,0);
    VkImageBlit blit{};
    blit.srcSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
    blit.srcOffsets[1]=want_port?VkOffset3D{int32_t(internal.width),int32_t(internal.height),1}:
        VkOffset3D{int32_t(color.size.width),int32_t(color.size.height),1};
    blit.dstSubresource=blit.srcSubresource;
    blit.dstOffsets[1]={int32_t(internal.width),int32_t(internal.height),1};
    vkCmdBlitImage(cb,color.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
       f.scene.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&blit,VK_FILTER_LINEAR);
    barrier(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,color.layout);
    bs4_probe_image(f.probe,cb,f.scene.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,internal,f.scene.format,1);
    transit(cb,f.scene,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);

    transit(cb,f.depth,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    const VkImageAspectFlags depth_layout_aspects=
        (depth.format==VK_FORMAT_D32_SFLOAT_S8_UINT||depth.format==VK_FORMAT_D24_UNORM_S8_UINT)?
        VK_IMAGE_ASPECT_DEPTH_BIT|VK_IMAGE_ASPECT_STENCIL_BIT:VK_IMAGE_ASPECT_DEPTH_BIT;
    barrier(cb,depth.image,depth_layout_aspects,depth.layout,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);
    if(want_port || (internal.width==depth.size.width && internal.height==depth.size.height)) {
        VkImageCopy region{};
        region.srcSubresource={VK_IMAGE_ASPECT_DEPTH_BIT,0,0,1};
        region.dstSubresource=region.srcSubresource;
        region.extent={internal.width,internal.height,1};
        vkCmdCopyImage(cb,depth.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                       f.depth.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&region);
    } else {
        VkImageBlit resample{};
        resample.srcSubresource={VK_IMAGE_ASPECT_DEPTH_BIT,0,0,1};
        resample.srcOffsets[1]={int32_t(depth.size.width),int32_t(depth.size.height),1};
        resample.dstSubresource=resample.srcSubresource;
        resample.dstOffsets[1]={int32_t(internal.width),int32_t(internal.height),1};
        vkCmdBlitImage(cb,depth.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                       f.depth.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                       1,&resample,VK_FILTER_NEAREST);
    }
    barrier(cb,depth.image,depth_layout_aspects,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,depth.layout);
    transit(cb,f.depth,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    if(!has_previous && !want_port) {
        transit(cb,previous,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
        VkClearColorValue clear{};
        VkImageSubresourceRange sub{VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
        vkCmdClearColorImage(cb,previous.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&clear,1,&sub);
        transit(cb,previous,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    }
    transit(cb,f.motion,VK_IMAGE_LAYOUT_GENERAL);
    flow(cb,f,internal,want_port?&camera:nullptr);
    // Shader storage writes must be visible to the FSR 3.1 compute passes.
    barrier(cb,f.motion.image,VK_IMAGE_ASPECT_COLOR_BIT,
            VK_IMAGE_LAYOUT_GENERAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    f.motion.layout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    bs4_probe_image(f.probe,cb,f.motion.image,f.motion.layout,internal,f.motion.format,4);
    bs4_probe_image(f.probe,cb,f.depth.image,f.depth.layout,internal,f.depth.format,5);
    transit(cb,f.output,VK_IMAGE_LAYOUT_GENERAL);
    FfxVkPortableUpscaleDispatchInfo info{};
    info.structSize=sizeof(info);info.commandBuffer=cb;
    info.color=describe(f.scene,FFX_VK_PORTABLE_RESOURCE_STATE_COMPUTE_READ);
    info.depth=describe(f.depth,FFX_VK_PORTABLE_RESOURCE_STATE_COMPUTE_READ);
    info.motionVectors=describe(f.motion,FFX_VK_PORTABLE_RESOURCE_STATE_COMPUTE_READ);
    info.output=describe(f.output,FFX_VK_PORTABLE_RESOURCE_STATE_UNORDERED_ACCESS);
    info.exposure.structSize=sizeof(info.exposure);
    info.reactiveMask.structSize=sizeof(info.reactiveMask);
    info.transparencyAndCompositionMask.structSize=sizeof(info.transparencyAndCompositionMask);
    info.renderSize={internal.width,internal.height};
    info.outputSize={output_extent.width,output_extent.height};
    info.motionVectorScale={1,1};
    info.jitterOffset=want_port?FfxVkPortableFloat2{camera.motion.jitter[0],camera.motion.jitter[1]}:
                              FfxVkPortableFloat2{0,0};
    const auto now=std::chrono::steady_clock::now();
    float dt=16.6667f;
    if(frame_id)dt=std::clamp(
        std::chrono::duration<float,std::milli>(now-last_frame).count(),4.f,100.f);
    last_frame=now;
    info.frameTimeMilliseconds=dt;info.preExposure=1.0f;
    info.cameraNear=0.1f;info.cameraFar=1000.f;
    info.cameraVerticalFovRadians=1.0f;info.viewSpaceToMeters=1.0f;
    if(want_port) {
        info.cameraNear=camera.nearPlane;info.cameraFar=camera.farPlane;
        info.cameraVerticalFovRadians=camera.verticalFov;
    }
    info.sharpness=0.2f;info.enableSharpening=VK_TRUE;
    // Port OnDisplayPass resets after a displayed frame without an actual
    // dispatch. Camera capture alone is not an AMD history submission.
    const bool missed_temporal=want_port&&last_temporal_camera&&camera.frameId!=last_temporal_camera+1;
    info.reset=(!has_previous||(want_port&&camera.reset)||missed_temporal)?VK_TRUE:VK_FALSE;
    if(missed_temporal){static unsigned logged=0;if(logged++<8)std::fprintf(stderr,
        "[BS4_FSR31] HISTORY_RESET_AFTER_SKIPPED_DISPATCH previous=%llu current=%llu\n",
        (unsigned long long)last_temporal_camera,(unsigned long long)camera.frameId);}
    f.probe.historyReset=info.reset;
    info.frameId=frame_id++;
    auto result=ffxVkPortableUpscaleContextRecordDispatch(fsr,&info);
#ifdef BS4_FSR31_TEST_HARNESS
    // Fail after real commands were recorded: exercise partial-recording
    // ownership, not a validation failure before any GPU work exists.
    if(result==FFX_VK_PORTABLE_OK&&std::getenv("BS4_TEST_FAIL_AFTER_FSR_RECORD"))result=FFX_VK_PORTABLE_ERROR_INVALID_ARGUMENT;
#endif
    if(result!=FFX_VK_PORTABLE_OK) {
        abandoned_history=true;
        if(!once_logged) {
            std::fprintf(stderr,"[BS4_FSR31] FSR3 dispatch failed=%d\n",int(result));
            once_logged=true;
        }
        return 0;
    }
    bs4_probe_image(f.probe,cb,f.output.image,VK_IMAGE_LAYOUT_GENERAL,output_extent,f.output.format,2);
    transit(cb,f.output,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    if(!want_port) {
    transit(cb,previous,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    transit(cb,f.scene,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);
    VkImageCopy color_region{};
    color_region.srcSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
    color_region.dstSubresource=color_region.srcSubresource;
    color_region.extent={internal.width,internal.height,1};
    vkCmdCopyImage(cb,f.scene.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   previous.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&color_region);
    transit(cb,previous,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    transit(cb,f.scene,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    }
    f.recordedBy=cb;f.recorded=true;
    has_previous=true;real_dispatch_seen.store(true,std::memory_order_release);
    if(want_port)last_temporal_camera=camera.frameId;
    if(frame_id==1)
        std::fprintf(stderr,"[BS4_FSR31] real FSR3.1 dispatch recorded (%ux%u->%ux%u)\n",
             internal.width,internal.height,output_extent.width,output_extent.height);
    return reinterpret_cast<uint64_t>(f.output.view);
}

extern "C" __attribute__((visibility("default"))) uint64_t bs4_fsr31_generic_render(
    const FfxVkPortableDeviceInfo* owned,VkCommandBuffer cb,VkImageView input,
    VkExtent2D input_extent,VkExtent2D output_extent,int preset,int hdr,int pre_ui,
    VkImageView scene_depth_view) {
    return generic_render_impl(owned,cb,input,input_extent,output_extent,preset,hdr,pre_ui,scene_depth_view,false);
}
extern "C" __attribute__((visibility("default"))) int bs4_fsr31_generic_prepare(
    const FfxVkPortableDeviceInfo* owned,VkCommandBuffer cb,VkImageView input,
    VkExtent2D input_extent,VkExtent2D output_extent,int preset,VkImageView depth) {
    return generic_render_impl(owned,cb,input,input_extent,output_extent,preset,0,1,depth,true)!=0;
}
extern "C" bool bs4_fsr31_temporal_resources_ready(VkExtent2D size) {
    return size.width&&size.height&&ready_port_extent.load(std::memory_order_acquire)==
        ((uint64_t(size.width)<<32)|size.height);
}

extern "C" __attribute__((visibility("default"))) VkImage
bs4_fsr31_output_image(VkImageView view) {
    std::lock_guard lock{mutex};
    if (!view || !fsr) return VK_NULL_HANDLE;
    for (const auto& frame:frames)
        if (frame.output.view == view) return frame.output.image;
    return VK_NULL_HANDLE;
}

// Called by the real Vulkan submit interception, after successful submission.
// A separate zero-command submit uses the ORIGINAL queue function and signals
// the completion fence only after all previously submitted GPU work on queue.
// No scheduler/core recompilation, no own GPU queue, no present-time waits.
extern "C" void bs4_fsr31_temporal_submitted(VkQueue queue,VkCommandBuffer cb,
                                             PFN_vkQueueSubmit original,
                                             PFN_vkQueueSubmit2 original2) {
    if(!queue||!cb||(!original&&!original2))return;
    std::lock_guard lock{mutex};
    for(auto& f:frames) {
        if(!f.recorded||f.recordedBy!=cb)continue;
        VkResult status=VK_ERROR_INITIALIZATION_FAILED;
        if(original)status=original(queue,0,nullptr,f.completion);
        else status=original2(queue,0,nullptr,f.completion);
        if(status==VK_SUCCESS){
            f.recorded=false;f.submitted=true;f.recordedBy={};
        } else {
            // Never recycle the slot without proof that its pending GPU
            // commands have completed. A failed completion marker retains it.
            static bool warned=false;
            if(!warned){warned=true;
                std::fprintf(stderr,"[BS4_FSR31] completion fence submit failed=%d\\n",int(status));}
        }
    }
}
extern "C" void bs4_fsr31_temporal_reset_recording(VkCommandBuffer cb) {
    if(!cb)return;
    std::lock_guard lock{mutex};
    for(auto& f:frames)if(f.recorded&&f.recordedBy==cb){
        f.recorded=false;f.recordedBy={};f.probe.pending=false;abandoned_history=true;
    }
}

// A pre-HUD sample of the actual composited image. It is recorded in the
// same CB and protected by the same completion fence as its FSR output.
extern "C" void bs4_fsr31_probe_composite(VkCommandBuffer cb,VkImage image,VkImageLayout layout,VkExtent2D size,VkFormat format){
    std::lock_guard lock{mutex};
    for(auto& f:frames)if(f.recorded&&f.recordedBy==cb){bs4_probe_image(f.probe,cb,image,layout,size,format,3);return;}
}
extern "C" void bs4_fsr31_probe_completed(){
    std::lock_guard lock{mutex};
    for(auto& f:frames)if(f.submitted&&vkGetFenceStatus(device,f.completion)==VK_SUCCESS)bs4_probe_resolve(f.probe,device);
}

extern "C" void bs4_fsr31_probe_wsi(VkCommandBuffer cb,VkImage image,VkImageLayout layout,
        VkExtent2D extent,VkFormat format) {
    std::lock_guard lock{mutex};
    for(auto& f:frames)if(f.recorded&&f.recordedBy==cb&&f.probe.pending) {
        f.probe.wsiImage=image;
        bs4_probe_image(f.probe,cb,image,layout,extent,format,7);
        return;
    }
}
extern "C" void bs4_fsr31_probe_post_hud(VkCommandBuffer cb,VkImage image,VkImageLayout layout,VkExtent2D size,VkFormat format){
    std::lock_guard lock{mutex};
    for(auto& f:frames)if(f.recorded&&f.recordedBy==cb&&f.probe.pending&&f.probe.compositeImage==image){
        bs4_probe_image(f.probe,cb,image,layout,size,format,6);return;
    }
}


extern "C" bool bs4_fsr31_has_real_dispatch(){return real_dispatch_seen.load(std::memory_order_acquire);}
