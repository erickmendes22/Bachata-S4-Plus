// SPDX-License-Identifier: GPL-2.0-or-later
// Native, independent scene/UI target. Based on Bloodborne-Android's
// RunUiOnly + RedirectColor/RedirectDepth structure. Guest images are NEVER
// selected as the FSR output or overwritten by this class.
#pragma once
#include <array>
#include "video_core/renderer_vulkan/vk_instance.h"
#include "video_core/renderer_vulkan/vk_scheduler.h"
#include "video_core/texture_cache/image.h"
#include "video_core/texture_cache/types.h"

namespace Bachata::Fsr31 {
class PortUiSurface {
public:
    struct Display {
        vk::ImageView view{};
        vk::Extent2D size{};
    };
    PortUiSurface(const Vulkan::Instance& i, Vulkan::Scheduler& s)
        : instance(i), scheduler(s) {}
    PortUiSurface(const PortUiSurface&) = delete;
    PortUiSurface& operator=(const PortUiSurface&) = delete;

    bool Begin(VideoCore::Image& scene, VideoCore::ImageId scene_id,
               VideoCore::ImageId ui_id, const VideoCore::Image* depth,
               VideoCore::ImageId ui_depth_id, vk::Extent2D output) {
        if (!scene_id || !ui_id || !output.width || !output.height ||
            output.width > 3840 || output.height > 2160) return false;
        const auto src = scene.info.size;
        const auto format = scene.info.pixel_format;
        if (!src.width || !src.height ||
            (format != vk::Format::eR8G8B8A8Unorm &&
             format != vk::Format::eR8G8B8A8Srgb)) return false;
        // Avoid unavailable Vulkan blit operations. Fail closed, and let the
        // guest render normally instead of touching its render targets.
        const auto& props = instance.GetPhysicalDevice().getFormatProperties(format);
        if (!(props.optimalTilingFeatures & vk::FormatFeatureFlagBits::eBlitSrc) ||
            !(props.optimalTilingFeatures & vk::FormatFeatureFlagBits::eBlitDst))
            return false;
        const vk::Format df = depth ? depth->info.pixel_format :
                                             vk::Format::eD32SfloatS8Uint;
        if (!Ensure(output, format, df)) return false;
        scheduler.EndRendering();
        const auto cb = scheduler.CommandBuffer();
        scene.Transit(vk::ImageLayout::eTransferSrcOptimal,
                     vk::AccessFlagBits2::eTransferRead, {}, cb);
        auto b = Barrier(vk::Image(color), vk::ImageAspectFlagBits::eColor,
                         vk::ImageLayout::eUndefined,
                         vk::ImageLayout::eTransferDstOptimal);
        cb.pipelineBarrier2({.imageMemoryBarrierCount=1, .pImageMemoryBarriers=&b});
        vk::ImageBlit region{};
        region.srcSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1};
        region.srcOffsets = std::array{vk::Offset3D{0,0,0},
             vk::Offset3D{s32(src.width),s32(src.height),1}};
        region.dstSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1};
        region.dstOffsets = std::array{vk::Offset3D{0,0,0},
             vk::Offset3D{s32(output.width),s32(output.height),1}};
        cb.blitImage(scene.GetImage(), vk::ImageLayout::eTransferSrcOptimal,
                     vk::Image(color), vk::ImageLayout::eTransferDstOptimal,
                     region, vk::Filter::eLinear);
        b = Barrier(vk::Image(color), vk::ImageAspectFlagBits::eColor,
                    vk::ImageLayout::eTransferDstOptimal, vk::ImageLayout::eGeneral);
        cb.pipelineBarrier2({.imageMemoryBarrierCount=1, .pImageMemoryBarriers=&b});

        auto db = Barrier(vk::Image(uiDepth), DepthAspect(),
                          vk::ImageLayout::eUndefined,
                          vk::ImageLayout::eTransferDstOptimal);
        cb.pipelineBarrier2({.imageMemoryBarrierCount=1, .pImageMemoryBarriers=&db});
        cb.clearDepthStencilImage(vk::Image(uiDepth), vk::ImageLayout::eTransferDstOptimal,
                                  {.depth=1.f, .stencil=0}, db.subresourceRange);
        db = Barrier(vk::Image(uiDepth), DepthAspect(),
                     vk::ImageLayout::eTransferDstOptimal, vk::ImageLayout::eGeneral);
        cb.pipelineBarrier2({.imageMemoryBarrierCount=1, .pImageMemoryBarriers=&db});

        srcWidth=src.width; srcHeight=src.height;
        guestColor=ui_id; guestDepth=ui_depth_id;
        drawing=true; ready=true;
        return true;
    }
    bool RedirectColor(VideoCore::ImageId id) const {
        return drawing && id == guestColor;
    }
    bool RedirectDepth(VideoCore::ImageId id) const {
        return drawing && id && id==guestDepth;
    }
    bool Drawing() const {return drawing;}
    vk::ImageView ColorView() const {return colorView ? *colorView : vk::ImageView{};}
    vk::ImageView DepthView() const {return depthView ? *depthView : vk::ImageView{};}
    vk::Extent2D Size() const {return extent;}
    std::array<float,2> Scale(bool native) const {
        if (!extent.width || !extent.height || !srcWidth || !srcHeight) return {1.f,1.f};
        return {float(extent.width)/float(native?1920:srcWidth),
                float(extent.height)/float(native?1080:srcHeight)};
    }
    Display TakeDisplay() {
        if (!ready || !colorView) return {};
        ready=false;
        drawing=false;
        return {*colorView, extent};
    }
    void CancelFrame() {drawing=false;ready=false;guestColor={};guestDepth={};}

private:
    static vk::ImageMemoryBarrier2 Barrier(vk::Image image, vk::ImageAspectFlags aspect,
                  vk::ImageLayout previous, vk::ImageLayout next) {
        return {
            .srcStageMask=vk::PipelineStageFlagBits2::eAllCommands,
            .srcAccessMask=vk::AccessFlagBits2::eMemoryRead | vk::AccessFlagBits2::eMemoryWrite,
            .dstStageMask=vk::PipelineStageFlagBits2::eAllCommands,
            .dstAccessMask=vk::AccessFlagBits2::eMemoryRead | vk::AccessFlagBits2::eMemoryWrite,
            .oldLayout=previous, .newLayout=next, .image=image,
            .subresourceRange={aspect,0,1,0,1}
        };
    }
    vk::ImageAspectFlags DepthAspect() const {
        return vk::ImageAspectFlagBits::eDepth |
            (depthFormat==vk::Format::eD32SfloatS8Uint ||
             depthFormat==vk::Format::eD24UnormS8Uint
             ? vk::ImageAspectFlags(vk::ImageAspectFlagBits::eStencil)
             : vk::ImageAspectFlags{});
    }
    bool Ensure(vk::Extent2D output, vk::Format cf, vk::Format df) {
        if (color && extent.width==output.width && extent.height==output.height &&
            colorFormat==cf && depthFormat==df) return true;
        // An old target can still be sampled by Presenter; drain before destroy.
        scheduler.Finish();
        colorView.reset(); depthView.reset();
        color.Destroy(); uiDepth.Destroy();
        color=VideoCore::UniqueImage(instance.GetDevice(),instance.GetAllocator());
        uiDepth=VideoCore::UniqueImage(instance.GetDevice(),instance.GetAllocator());
        color.Create({
            .imageType=vk::ImageType::e2D, .format=cf,
            .extent={output.width,output.height,1},
            .mipLevels=1,.arrayLayers=1,.samples=vk::SampleCountFlagBits::e1,
            .tiling=vk::ImageTiling::eOptimal,
            .usage=vk::ImageUsageFlagBits::eTransferDst |
                   vk::ImageUsageFlagBits::eTransferSrc |
                   vk::ImageUsageFlagBits::eSampled |
                   vk::ImageUsageFlagBits::eColorAttachment |
                   vk::ImageUsageFlagBits::eStorage,
            .initialLayout=vk::ImageLayout::eUndefined
        });
        uiDepth.Create({
            .imageType=vk::ImageType::e2D,.format=df,
            .extent={output.width,output.height,1},
            .mipLevels=1,.arrayLayers=1,.samples=vk::SampleCountFlagBits::e1,
            .tiling=vk::ImageTiling::eOptimal,
            .usage=vk::ImageUsageFlagBits::eTransferDst |
                   vk::ImageUsageFlagBits::eDepthStencilAttachment,
            .initialLayout=vk::ImageLayout::eUndefined
        });
        colorView=instance.GetDevice().createImageViewUnique({
            .image=vk::Image(color),.viewType=vk::ImageViewType::e2D,
            .format=cf,.subresourceRange={vk::ImageAspectFlagBits::eColor,0,1,0,1}
        }).value;
        colorFormat=cf;depthFormat=df;extent=output;
        depthView=instance.GetDevice().createImageViewUnique({
            .image=vk::Image(uiDepth),.viewType=vk::ImageViewType::e2D,
            .format=df,.subresourceRange={DepthAspect(),0,1,0,1}
        }).value;
        return bool(colorView) && bool(depthView);
    }
    const Vulkan::Instance& instance;
    Vulkan::Scheduler& scheduler;
    VideoCore::UniqueImage color{}, uiDepth{};
    vk::UniqueImageView colorView{},depthView{};
    vk::Extent2D extent{};
    vk::Format colorFormat=vk::Format::eUndefined,depthFormat=vk::Format::eUndefined;
    u32 srcWidth{},srcHeight{};
    VideoCore::ImageId guestColor{},guestDepth{};
    bool drawing{},ready{};
};
} // namespace Bachata::Fsr31
