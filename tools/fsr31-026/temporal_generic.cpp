// SPDX-License-Identifier: GPL-2.0-or-later
// Generic temporal FSR 3.1 path using real Vulkan color and depth resources.
// The motion shader estimates optical flow from consecutive color frames.
// Unlike game-specific forks, this path does not rely on guest shader hashes.
#include "vulkan_capture.h"
#include "port_runscaled_contract.h"
#include "ffx_vk_portable.h"
#include "flow_spv.h"
#include "port_camera_motion_spv.h"
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
    VkImageAspectFlags aspect{};
    VkImageLayout layout = VK_IMAGE_LAYOUT_UNDEFINED;
};
struct Frame {
    VkDescriptorSet port_motion_descriptor{};
    Surface scene;
    Surface depth;
    Surface motion;
    Surface output;
    VkDescriptorSet descriptor{};
};
std::mutex mutex;
// Exact GLSL push layout from ducvd89/Bloodborne-Android camera_motion.comp.
// The renderer must supply *real* scene camera/projection/jitter at its G-buffer
// boundary; we must not fabricate them from optical-flow estimates.
struct PortCameraPush {
    float reproject[12],proj[4],prev_proj[4],size[2],jitter[2],previous_jitter[2];
    uint32_t mode;
};
static_assert(sizeof(PortCameraPush)==108);
struct PortCameraFrame {
    PortCameraPush push{};
    VkCommandBuffer command=VK_NULL_HANDLE;
    VkImageView depth=VK_NULL_HANDLE;
    bool valid=false;
};
PortCameraFrame port_camera{};
VkDescriptorSetLayout port_desc_layout{};
VkPipelineLayout port_pipeline_layout{};
VkPipeline port_pipeline{};
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
bool has_previous=false;
uint64_t frame_id=0;
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
    out.format=format;out.size=size;out.usage=usage;out.aspect=aspect;
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
    barrier(cb,s.image,s.aspect,s.layout,next);s.layout=next;
}
void free_all() {
    if(device)vkDeviceWaitIdle(device);
    if(fsr) {ffxVkPortableUpscaleContextDestroy(fsr);fsr=nullptr;}
    if(port_pipeline)vkDestroyPipeline(device,port_pipeline,nullptr);
    if(port_pipeline_layout)vkDestroyPipelineLayout(device,port_pipeline_layout,nullptr);
    if(port_desc_layout)vkDestroyDescriptorSetLayout(device,port_desc_layout,nullptr);
    port_pipeline={};port_pipeline_layout={};port_desc_layout={};
    if(flow_pipeline)vkDestroyPipeline(device,flow_pipeline,nullptr);
    if(pipeline_layout)vkDestroyPipelineLayout(device,pipeline_layout,nullptr);
    if(desc_layout)vkDestroyDescriptorSetLayout(device,desc_layout,nullptr);
    if(descriptors)vkDestroyDescriptorPool(device,descriptors,nullptr);
    if(sampler)vkDestroySampler(device,sampler,nullptr);
    flow_pipeline={};pipeline_layout={};desc_layout={};
    descriptors={};sampler={};
    for(auto& f:frames){free_surface(f.scene);free_surface(f.depth);
        free_surface(f.motion);free_surface(f.output);}
    frames.clear();free_surface(previous);
    has_previous=false;frame_id=0;cursor=0;
}
bool build_compute(){
    VkDescriptorSetLayoutBinding bindings[3]{};
    for(uint32_t i=0;i<3;++i) {
        bindings[i].binding=i;bindings[i].descriptorCount=1;
        bindings[i].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;
        bindings[i].descriptorType=i==2?VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:
                                        VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
    }
    VkDescriptorSetLayoutCreateInfo dci{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
    dci.bindingCount=3;dci.pBindings=bindings;
    if(!result(vkCreateDescriptorSetLayout(device,&dci,nullptr,&desc_layout),"layout"))return false;
    VkPushConstantRange range{VK_SHADER_STAGE_COMPUTE_BIT,0,16};
    VkPipelineLayoutCreateInfo pci{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    pci.setLayoutCount=1;pci.pSetLayouts=&desc_layout;
    pci.pushConstantRangeCount=1;pci.pPushConstantRanges=&range;
    if(!result(vkCreatePipelineLayout(device,&pci,nullptr,&pipeline_layout),"pipe layout"))return false;
    VkShaderModule module{};
    VkShaderModuleCreateInfo sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    sm.codeSize=sizeof(BS4_FSR31_FLOW_SPV);
    sm.pCode=BS4_FSR31_FLOW_SPV;
    if(!result(vkCreateShaderModule(device,&sm,nullptr,&module),"flow shader"))return false;
    VkPipelineShaderStageCreateInfo stage{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};
    stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;stage.module=module;stage.pName="main";
    VkComputePipelineCreateInfo ci{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
    ci.stage=stage;ci.layout=pipeline_layout;
    auto r=vkCreateComputePipelines(device,VK_NULL_HANDLE,1,&ci,nullptr,&flow_pipeline);
    vkDestroyShaderModule(device,module,nullptr);
    if(!result(r,"flow compute pipeline"))return false;
    // Actual depth-based motion shader from the Android port, with the
    // unchanged push layout and depth/object/storage bindings.
    VkDescriptorSetLayoutBinding port_bindings[3]{};
    for(uint32_t i=0;i<3;++i){
        port_bindings[i].binding=i;port_bindings[i].descriptorCount=1;
        port_bindings[i].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;
        port_bindings[i].descriptorType=(i==1)?
            VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
    }
    VkDescriptorSetLayoutCreateInfo port_dci{
        VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
    port_dci.bindingCount=3;port_dci.pBindings=port_bindings;
    if(!result(vkCreateDescriptorSetLayout(device,&port_dci,nullptr,
                                           &port_desc_layout),"port motion layout"))
        return false;
    VkPushConstantRange port_push{VK_SHADER_STAGE_COMPUTE_BIT,0,
                                  uint32_t(sizeof(PortCameraPush))};
    VkPipelineLayoutCreateInfo port_pci{
        VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    port_pci.setLayoutCount=1;port_pci.pSetLayouts=&port_desc_layout;
    port_pci.pushConstantRangeCount=1;port_pci.pPushConstantRanges=&port_push;
    if(!result(vkCreatePipelineLayout(device,&port_pci,nullptr,
                                      &port_pipeline_layout),"port pipeline layout"))
        return false;
    VkShaderModule port_module{};
    VkShaderModuleCreateInfo port_sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    port_sm.codeSize=sizeof(BS4_PORT_CAMERA_MOTION_SPV);
    port_sm.pCode=BS4_PORT_CAMERA_MOTION_SPV;
    if(!result(vkCreateShaderModule(device,&port_sm,nullptr,
                                    &port_module),"port camera shader"))
        return false;
    VkComputePipelineCreateInfo port_ci{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
    port_ci.stage={VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};
    port_ci.stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;
    port_ci.stage.module=port_module;
    port_ci.stage.pName="main";
    port_ci.layout=port_pipeline_layout;
    auto port_result=vkCreateComputePipelines(device,VK_NULL_HANDLE,1,
                   &port_ci,nullptr,&port_pipeline);
    vkDestroyShaderModule(device,port_module,nullptr);
    if(!result(port_result,"port camera pipeline"))return false;
    VkSamplerCreateInfo sci{VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
    sci.magFilter=VK_FILTER_LINEAR;sci.minFilter=VK_FILTER_LINEAR;
    sci.addressModeU=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeV=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    sci.addressModeW=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    if(!result(vkCreateSampler(device,&sci,nullptr,&sampler),"motion sampler"))return false;
    VkDescriptorPoolSize sizes[]={
        {VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,16},
        {VK_DESCRIPTOR_TYPE_STORAGE_IMAGE,16},
        {VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,12}};
    VkDescriptorPoolCreateInfo pi{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
    pi.maxSets=10;pi.poolSizeCount=3;pi.pPoolSizes=sizes;
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
                  VkFormat color_format,VkFormat depth_format,VkFormat output_format) {
    free_all();
    config={};config.structSize=sizeof(config);
    config.flags=BachataPortScaled::ContextFlags; // Scaled RunScaled: LDR, never HDR.
    config.maxRenderSize={render.width,render.height};
    config.maxOutputSize={output.width,output.height};
    if(!build_compute())return false;
    const VkImageUsageFlags sampled=VK_IMAGE_USAGE_SAMPLED_BIT|VK_IMAGE_USAGE_TRANSFER_DST_BIT|
                                    VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
    const VkImageUsageFlags storage=VK_IMAGE_USAGE_STORAGE_BIT|VK_IMAGE_USAGE_SAMPLED_BIT|
                                    VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    frames.resize(4);
    for(auto& f:frames) {
        if(!alloc(f.scene,color_format,render,sampled,VK_IMAGE_ASPECT_COLOR_BIT) ||
           !alloc(f.depth,depth_format,render,sampled,VK_IMAGE_ASPECT_DEPTH_BIT) ||
           !alloc(f.motion,VK_FORMAT_R16G16_SFLOAT,render,storage,VK_IMAGE_ASPECT_COLOR_BIT) ||
           !alloc(f.output,output_format,output,
                   storage|VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT|
                           VK_IMAGE_USAGE_TRANSFER_SRC_BIT,
                   VK_IMAGE_ASPECT_COLOR_BIT))
            return false;
        VkDescriptorSetAllocateInfo ai{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
        ai.descriptorPool=descriptors;ai.descriptorSetCount=1;ai.pSetLayouts=&desc_layout;
        if(!result(vkAllocateDescriptorSets(device,&ai,&f.descriptor),"descriptors"))return false;
        ai.pSetLayouts=&port_desc_layout;
        if(!result(vkAllocateDescriptorSets(device,&ai,&f.port_motion_descriptor),
                   "port camera descriptors"))return false;
    }
    if(!alloc(previous,color_format,render,sampled,VK_IMAGE_ASPECT_COLOR_BIT))return false;
    const auto r=ffxVkPortableUpscaleContextCreate(&info,&config,&fsr);
    if(r!=FFX_VK_PORTABLE_OK) {
        std::fprintf(stderr,"[BS4_FSR31] FSR3.1 Vulkan context error=%d\n",int(r));
        return false;
    }
    std::fprintf(stderr,"[BS4_FSR31] temporal context ready %ux%u->%ux%u\n",
         render.width,render.height,output.width,output.height);
    return true;
}
void flow(VkCommandBuffer cb,const Frame& f,VkExtent2D size) {
    VkDescriptorImageInfo resources[3]{};
    resources[0]={sampler,f.scene.view,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
    resources[1]={sampler,previous.view,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
    resources[2]={VK_NULL_HANDLE,f.motion.view,VK_IMAGE_LAYOUT_GENERAL};
    VkWriteDescriptorSet writes[3]{};
    for(uint32_t i=0;i<3;i++) {
        writes[i]={VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
        writes[i].dstSet=f.descriptor;writes[i].dstBinding=i;
        writes[i].descriptorType=i==2?VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:
                                         VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER;
        writes[i].descriptorCount=1;writes[i].pImageInfo=&resources[i];
    }
    vkUpdateDescriptorSets(device,3,writes,0,nullptr);
    vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,flow_pipeline);
    vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,pipeline_layout,
                            0,1,&f.descriptor,0,nullptr);
    struct Push{int width,height,first,pad;} pc{int(size.width),int(size.height),!has_previous,0};
    vkCmdPushConstants(cb,pipeline_layout,VK_SHADER_STAGE_COMPUTE_BIT,0,sizeof(pc),&pc);
    vkCmdDispatch(cb,(size.width+7)/8,(size.height+7)/8,1);
}
// No optical-flow inference here: the exact shader shipped in the port
// reconstructs motion from G-buffer depth + current/previous matrices.
void record_port_camera_motion(VkCommandBuffer cb,const Frame& f,
                               const PortCameraPush& camera,VkExtent2D extent) {
    VkDescriptorImageInfo info[3]{};
    info[0]={VK_NULL_HANDLE,f.depth.view,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
    info[1]={VK_NULL_HANDLE,f.motion.view,VK_IMAGE_LAYOUT_GENERAL};
    // In mode=0 this binding is not sampled, but Vulkan still requires it.
    info[2]=info[0];
    VkWriteDescriptorSet writes[3]{};
    for(uint32_t i=0;i<3;++i) {
        writes[i]={VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
        writes[i].dstSet=f.port_motion_descriptor;
        writes[i].dstBinding=i;
        writes[i].descriptorCount=1;
        writes[i].descriptorType=(i==1)?
            VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
        writes[i].pImageInfo=&info[i];
    }
    vkUpdateDescriptorSets(device,3,writes,0,nullptr);
    vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,port_pipeline);
    vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,
                            port_pipeline_layout,0,1,
                            &f.port_motion_descriptor,0,nullptr);
    vkCmdPushConstants(cb,port_pipeline_layout,VK_SHADER_STAGE_COMPUTE_BIT,
                       0,sizeof(camera),&camera);
    vkCmdDispatch(cb,(extent.width+7)/8,(extent.height+7)/8,1);
}
} // namespace

// Explicit port renderer/guest camera handoff. The R13 core024 does NOT yet
// call this; no "port quality" is claimed unless it is connected and validated.
extern "C" __attribute__((visibility("default"))) int bs4_fsr31_supply_port_camera(
    VkCommandBuffer cb,VkImageView scene_depth,const void* camera_push,
    uint32_t byte_size) {
    if(!cb || !scene_depth || !camera_push || byte_size!=sizeof(PortCameraPush))
        return 0;
    PortCameraPush next{};
    std::memcpy(&next,camera_push,sizeof(next));
    if(next.mode!=0 || !std::isfinite(next.proj[0]) ||
       !std::isfinite(next.proj[1]) || std::abs(next.proj[1])<1e-4f ||
       next.size[0]<64 || next.size[1]<64 ||
       next.size[0]>8192 || next.size[1]>8192) return 0;
    for(float value:next.reproject)if(!std::isfinite(value))return 0;
    std::lock_guard lock{mutex};
    port_camera={next,cb,scene_depth,true};
    return 1;
}

extern "C" __attribute__((visibility("default"))) uint64_t bs4_fsr31_generic_render(
    const FfxVkPortableDeviceInfo* owned,VkCommandBuffer cb,VkImageView input,
    VkExtent2D input_extent,VkExtent2D output_extent,int preset,int hdr,int pre_ui,
    VkImageView scene_depth_view) {
    if(!owned||!cb||!input||hdr||preset<0||preset>4){report_once(1,"missing arguments or HDR/preset unsupported");return 0;}
    if(!owned->shaderStorageImageWriteWithoutFormatEnabled){report_once(2,"storage image write without format disabled");return 0;}
    if(output_extent.width==0||output_extent.height==0 ||
       input_extent.width==0||input_extent.height==0) {
        report_once(3,"input/output extent zero");return 0;
    }
    // R11 incorrectly downsized the fully rendered 1920x1080 scene to
    // 427x240 and then reconstructed 1280x720. This cannot improve game
    // performance and destroys visual detail. Host temporal upscaling must
    // consume the *actual* smaller scene image, never synthesize one.
    // Exactly matches the original shadPS4 FsrPass skip condition.
    if (input_extent.width >= output_extent.width &&
        input_extent.height >= output_extent.height) {
        report_once(14, "source already >= presentation size; no forced downsample");
        return 0;
    }
    Bs4FsrCaptureImage color{},depth{};
    if(!bs4_fsr31_capture_image(input,&color)){report_once(4,"Vulkan color image view not captured");return 0;}
    if (pre_ui) {
        // RunScaled must consume an LDR color target, NEVER G-buffer HDR fmt=122.
        // This is a strict port-equivalent producer contract, not a size guess.
        if (!BachataPortScaled::SceneAndOutput(color.format,input_extent,output_extent)) {
            report_once(16,"port RunScaled requires genuine RGBA8 LDR scene");return 0;
        }
        // Depth must originate in the same completed Vulkan render pass as
        // the selected reduced scene, not merely the globally newest image.
        if (!scene_depth_view || !bs4_fsr31_capture_image(scene_depth_view,&depth) ||
            !(depth.aspects & VK_IMAGE_ASPECT_DEPTH_BIT)) {
            report_once(5,"pre-UI matching scene depth image not available");
            return 0;
        }
        if (!BachataPortScaled::MatchingDepth(input_extent,depth.size)) {
            report_once(17,"RunScaled LDR/depth raster extents mismatch");return 0;
        }
    } else if (!bs4_fsr31_capture_depth(input_extent,&depth)) {
        report_once(5,"depth image matching render extent not captured");
        return 0;
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
                                         pre_ui?VK_FORMAT_R8G8B8A8_UNORM:
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
    // Port RunScaled must receive real G-buffer camera data from core024.
    // Never fake motion with image search/optical flow (R20 visual artifact).
    if(pre_ui && (!port_camera.valid || port_camera.command!=cb ||
                  port_camera.depth!=scene_depth_view ||
                  std::abs(port_camera.push.size[0]-input_extent.width)>0.5f ||
                  std::abs(port_camera.push.size[1]-input_extent.height)>0.5f)) {
        report_once(18,"port camera/depth/jitter not supplied by core024");
        return 0;
    }
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
    if ((internal.width!=depth.size.width || internal.height!=depth.size.height) &&
        !depth_can_blit){report_once(12,"scaled depth blit unsupported by GPU");return 0;}
    const VkFormat target_format=pre_ui?BachataPortScaled::UiOutputFormat:
                                     VK_FORMAT_R16G16B16A16_SFLOAT;
    const VkFormat working_color=pre_ui?VK_FORMAT_R8G8B8A8_UNORM:
                                        VK_FORMAT_R16G16B16A16_SFLOAT;
    if(!fsr || config.maxRenderSize.width!=internal.width ||
       config.maxRenderSize.height!=internal.height ||
       config.maxOutputSize.width!=output_extent.width ||
       config.maxOutputSize.height!=output_extent.height ||
       frames[0].scene.format!=working_color ||
       frames[0].output.format!=target_format ||frames[0].depth.format!=depth.format) {
        if(!allocate_for(*owned,internal,output_extent,working_color,depth.format,target_format)){report_once(13,"FSR resource or context creation failed");return 0;}
    }
    Frame& f=frames[cursor++%frames.size()];
    transit(cb,f.scene,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    barrier(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,color.layout,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);
    VkImageBlit blit{};
    blit.srcSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
    blit.srcOffsets[1]={int32_t(color.size.width),int32_t(color.size.height),1};
    blit.dstSubresource=blit.srcSubresource;
    blit.dstOffsets[1]={int32_t(internal.width),int32_t(internal.height),1};
    vkCmdBlitImage(cb,color.image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
       f.scene.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&blit,VK_FILTER_LINEAR);
    barrier(cb,color.image,VK_IMAGE_ASPECT_COLOR_BIT,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,color.layout);
    transit(cb,f.scene,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);

    transit(cb,f.depth,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
    barrier(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,depth.layout,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL);
    if(internal.width==depth.size.width && internal.height==depth.size.height) {
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
    barrier(cb,depth.image,VK_IMAGE_ASPECT_DEPTH_BIT,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,depth.layout);
    transit(cb,f.depth,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    if(!has_previous) {
        transit(cb,previous,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL);
        VkClearColorValue clear{};
        VkImageSubresourceRange sub{VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
        vkCmdClearColorImage(cb,previous.image,VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,&clear,1,&sub);
        transit(cb,previous,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    }
    transit(cb,f.motion,VK_IMAGE_LAYOUT_GENERAL);
    if(pre_ui) {
        record_port_camera_motion(cb,f,port_camera.push,internal);
    } else {
        flow(cb,f,internal); // legacy FsrPass spatial-hook path unchanged
    }
    // Shader storage writes must be visible to the FSR 3.1 compute passes.
    barrier(cb,f.motion.image,VK_IMAGE_ASPECT_COLOR_BIT,
            VK_IMAGE_LAYOUT_GENERAL,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
    f.motion.layout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
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
    info.jitterOffset=pre_ui?
        FfxVkPortableFloat2{port_camera.push.jitter[0],
                            port_camera.push.jitter[1]}:
        FfxVkPortableFloat2{0,0};
    const auto now=std::chrono::steady_clock::now();
    float dt=16.6667f;
    if(frame_id)dt=std::clamp(
        std::chrono::duration<float,std::milli>(now-last_frame).count(),4.f,100.f);
    last_frame=now;
    info.frameTimeMilliseconds=dt;info.preExposure=1.0f;
    info.cameraNear=pre_ui?
        -port_camera.push.proj[3]/port_camera.push.proj[2]:0.1f;
    info.cameraFar=pre_ui?3000.0f:1000.0f;
    info.cameraVerticalFovRadians=pre_ui?
        2.0f*std::atan(1.0f/std::abs(port_camera.push.proj[1])):1.0f;
    info.viewSpaceToMeters=1.0f;
    info.sharpness=0.2f;info.enableSharpening=VK_TRUE;
    info.reset=has_previous?VK_FALSE:VK_TRUE;info.frameId=frame_id++;
    const auto result=ffxVkPortableUpscaleContextRecordDispatch(fsr,&info);
    if(result!=FFX_VK_PORTABLE_OK) {
        if(!once_logged) {
            std::fprintf(stderr,"[BS4_FSR31] FSR3 dispatch failed=%d\n",int(result));
            once_logged=true;
        }
        return 0;
    }
    transit(cb,f.output,VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL);
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
    has_previous=true;
    if(pre_ui)port_camera.valid=false;
    if(frame_id==1)
        std::fprintf(stderr,"[BS4_FSR31] real FSR3.1 dispatch recorded (%ux%u->%ux%u)\n",
             internal.width,internal.height,output_extent.width,output_extent.height);
    return reinterpret_cast<uint64_t>(f.output.view);
}

extern "C" __attribute__((visibility("default"))) VkImage
bs4_fsr31_output_image(VkImageView view) {
    std::lock_guard lock{mutex};
    if (!view || !fsr) return VK_NULL_HANDLE;
    for (const auto& frame:frames)
        if (frame.output.view == view) return frame.output.image;
    return VK_NULL_HANDLE;
}


// The renderer hook temporarily uses an FSR output as a 720p color attachment
// for guest HUD draws, before returning it to the Presenter sampled layout.
extern "C" __attribute__((visibility("default"))) int
bs4_fsr31_set_output_layout(VkImageView view,VkImageLayout next) {
    std::lock_guard lock{mutex};
    for(auto& f:frames) {
        if(f.output.view==view && f.output.image) {
            f.output.layout=next;return 1;
        }
    }
    return 0;
}
