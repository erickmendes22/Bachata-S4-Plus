"""Bring the dedicated port's identity display path and driver cache to 0.18.1.

The Android WSI remains in place: do not pretend its native window is an AHB
socket peer. The intermediate game image is guest-sized when FSR is off.
Reference: Order c063ff15dfc5/639d7d024aa7, GoW3 239b7df8145e.
"""
from pathlib import Path
import shutil


def edit(root, rel, old, new):
    p = root / rel
    text = p.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"Bionic display/cache source drift {rel}: {old[:100]}")
    p.write_text(text.replace(old,new,1))


def apply(root: Path):
    base = "src/video_core/renderer_vulkan/"
    ph, pc = base+"vk_presenter.h", base+"vk_presenter.cpp"
    edit(root, ph, "    vk::ImageView image_view;", "    vk::ImageView image_view;\n    vk::ImageView opaque_sampled_view{};")
    edit(root, ph, "    Frame* GetRenderFrame();", "    Frame* GetRenderFrame(u32 width = 0, u32 height = 0);")
    edit(root, pc, "        device.destroyImageView(frame.image_view);",
         """        if (frame.opaque_sampled_view) device.destroyImageView(frame.opaque_sampled_view);
        device.destroyImageView(frame.image_view);""")
    edit(root, pc, "    if (frame->image_view) {",
         """    if (frame->opaque_sampled_view) {
        device.destroyImageView(frame->opaque_sampled_view);
        frame->opaque_sampled_view = vk::ImageView{};
    }
    if (frame->image_view) {""")
    edit(root, pc, "    frame->imgui_texture = ImGui::Vulkan::AddTexture(view, vk::ImageLayout::eShaderReadOnlyOptimal);",
         """    // Separate attachment and sampled views: a color attachment requires
    // identity swizzles. ImGui must still see opaque alpha when a copy
    // preserves the guest's original (possibly zero) alpha bytes.
#ifdef __ANDROID__
    if (!BachataCompat::Sotc608()) {
        auto sampled_info = view_info;
        sampled_info.components.a = vk::ComponentSwizzle::eOne;
        frame->opaque_sampled_view = Check<"create opaque display view">(device.createImageView(sampled_info));
        view = frame->opaque_sampled_view;
    }
#endif
    frame->imgui_texture = ImGui::Vulkan::AddTexture(view, vk::ImageLayout::eShaderReadOnlyOptimal);""")
    edit(root, pc, """    texture_cache.UpdateImage(image_id);

    Frame* frame = GetRenderFrame();""",
         """    texture_cache.UpdateImage(image_id);

    // BACHATA_GUEST_SIZED_INTERMEDIATE: without FSR, Android needs only
    // one scaling operation, in the final composition, not a device-sized
    // intermediate followed by another sampled pass. The guest image
    // size, not the screen size, is authoritative.
    u32 frame_width = 0, frame_height = 0;
#ifdef __ANDROID__
    static const bool report_profile = [] {
        LOG_INFO(Render_Vulkan,"BACHATA_SOTC_608_PROFILE enabled={}",BachataCompat::Sotc608());
        return true;
    }();
    (void)report_profile;
    if (!BachataCompat::Sotc608() && !fsr_settings.enable) {
        const auto& size = texture_cache.GetImage(image_id).info.size;
        frame_width = size.width;
        frame_height = size.height;
    }
#endif
    Frame* frame = GetRenderFrame(frame_width, frame_height);""")
    edit(root, pc, "Frame* Presenter::GetRenderFrame() {",
         "Frame* Presenter::GetRenderFrame(u32 width, u32 height) {")
    edit(root, pc, """    if (frame->width != expected_frame_width || frame->height != expected_frame_height ||
        frame->is_hdr != swapchain.GetHDR()) {
        RecreateFrame(frame, expected_frame_width, expected_frame_height);
    }""",
         """    if (!width || !height) {
        width = expected_frame_width;
        height = expected_frame_height;
    }
    if (frame->width != width || frame->height != height ||
        frame->is_hdr != swapchain.GetHDR()) {
        RecreateFrame(frame, width, height);
    }""")
    edit(root, pc, "    pp_pass.Render(cmdbuf, image_view, image_size, *frame, pp_settings);",
         r"""    bool identity_copy = false;
    bool identity_blit = false;
#ifdef __ANDROID__
    // BACHATA_IDENTITY_DISPLAY: at unit gamma, SRGB sampling followed by
    // the postprocess SRGB encode is an identity operation on RGB bytes.
    // Check the *actual* Vulkan backing, not merely the guest descriptor.
    if (!BachataCompat::Sotc608() && !fsr_settings.enable && !frame->is_hdr && !pp_settings.hdr &&
        !pp_settings.srgb_input && pp_settings.gamma == 1.0f &&
        frame->width == image_size.width && frame->height == image_size.height &&
        image.backing) {
        const auto& src = image.backing->image.image_ci;
        const auto dst = swapchain.GetSurfaceFormat().format;
        const bool rgba = view_info.format == vk::Format::eR8G8B8A8Srgb &&
            (src.format == vk::Format::eR8G8B8A8Srgb || src.format == vk::Format::eR8G8B8A8Unorm);
        const bool bgra = view_info.format == vk::Format::eB8G8R8A8Srgb &&
            (src.format == vk::Format::eB8G8R8A8Srgb || src.format == vk::Format::eB8G8R8A8Unorm);
        const bool compatible = src.samples == vk::SampleCountFlagBits::e1 &&
            src.imageType == vk::ImageType::e2D && src.extent.width == image_size.width &&
            src.extent.height == image_size.height &&
            bool(src.usage & vk::ImageUsageFlagBits::eTransferSrc);
        identity_copy = compatible &&
            ((rgba && dst == vk::Format::eR8G8B8A8Unorm) ||
             (bgra && dst == vk::Format::eB8G8R8A8Unorm));
        if (compatible && !identity_copy &&
            ((bgra && src.format == vk::Format::eB8G8R8A8Unorm && dst == vk::Format::eR8G8B8A8Unorm) ||
             (rgba && src.format == vk::Format::eR8G8B8A8Unorm && dst == vk::Format::eB8G8R8A8Unorm))) {
            // Never blit an SRGB backing to UNORM: that decodes the RGB.
            const auto physical = instance.GetPhysicalDevice();
            identity_blit =
                bool(physical.getFormatProperties(src.format).optimalTilingFeatures &
                     vk::FormatFeatureFlagBits::eBlitSrc) &&
                bool(physical.getFormatProperties(dst).optimalTilingFeatures &
                     vk::FormatFeatureFlagBits::eBlitDst);
        }
    }
#endif
    if (identity_copy || identity_blit) {
        runtime.Transit(&image, vk::ImageLayout::eTransferSrcOptimal,
                        vk::PipelineStageFlagBits2::eAllTransfer, vk::AccessFlagBits2::eTransferRead);
        runtime.FlushBarriers();
        const vk::ImageMemoryBarrier2 to_dst{
            .srcStageMask = vk::PipelineStageFlagBits2::eColorAttachmentOutput,
            .srcAccessMask = vk::AccessFlagBits2::eNone,
            .dstStageMask = vk::PipelineStageFlagBits2::eAllTransfer,
            .dstAccessMask = vk::AccessFlagBits2::eTransferWrite,
            .oldLayout = vk::ImageLayout::eColorAttachmentOptimal,
            .newLayout = vk::ImageLayout::eTransferDstOptimal,
            .image = frame->image,
            .subresourceRange = frame_subresources,
        };
        cmdbuf.pipelineBarrier2({.imageMemoryBarrierCount = 1, .pImageMemoryBarriers = &to_dst});
        if (identity_blit) {
            const vk::ImageBlit region{
                .srcSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
                .srcOffsets = std::array{vk::Offset3D{0,0,0},
                    vk::Offset3D{s32(image_size.width),s32(image_size.height),1}},
                .dstSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
                .dstOffsets = std::array{vk::Offset3D{0,0,0},
                    vk::Offset3D{s32(image_size.width),s32(image_size.height),1}},
            };
            cmdbuf.blitImage(image.GetImage(), vk::ImageLayout::eTransferSrcOptimal,
                frame->image, vk::ImageLayout::eTransferDstOptimal, region, vk::Filter::eNearest);
        } else {
            const vk::ImageCopy region{
                .srcSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
                .dstSubresource = {vk::ImageAspectFlagBits::eColor, 0, 0, 1},
                .extent = {image_size.width, image_size.height, 1},
            };
            cmdbuf.copyImage(image.GetImage(), vk::ImageLayout::eTransferSrcOptimal,
                frame->image, vk::ImageLayout::eTransferDstOptimal, region);
        }
        const vk::ImageMemoryBarrier2 ready{
            .srcStageMask = vk::PipelineStageFlagBits2::eAllTransfer,
            .srcAccessMask = vk::AccessFlagBits2::eTransferWrite,
            .dstStageMask = vk::PipelineStageFlagBits2::eFragmentShader,
            .dstAccessMask = vk::AccessFlagBits2::eShaderRead,
            .oldLayout = vk::ImageLayout::eTransferDstOptimal,
            .newLayout = vk::ImageLayout::eGeneral,
            .image = frame->image,
            .subresourceRange = frame_subresources,
        };
        cmdbuf.pipelineBarrier2({.imageMemoryBarrierCount = 1, .pImageMemoryBarriers = &ready});
    } else {
        pp_pass.Render(cmdbuf, image_view, image_size, *frame, pp_settings);
    }
#ifdef __ANDROID__
    // Log only actual path/size changes, not every frame.
    struct DisplayPath { u32 sw,sh,dw,dh; bool copy,blit;
        bool operator==(const DisplayPath&) const = default; };
    static thread_local DisplayPath last{};
    const DisplayPath current{image_size.width,image_size.height,frame->width,frame->height,
                              identity_copy,identity_blit};
    if (last != current) {
        LOG_INFO(Render_Vulkan,
            "BACHATA_DISPLAY_PATH guest={}x{} intermediate={}x{} copy={} blit={}",
            current.sw,current.sh,current.dw,current.dh,current.copy,current.blit);
        last=current;
    }
#endif""")
    edit(root, pc, """                .srcAccessMask = vk::AccessFlagBits::eColorAttachmentWrite,
                .dstAccessMask = vk::AccessFlagBits::eColorAttachmentRead,
                .oldLayout = vk::ImageLayout::eGeneral,""",
         """                .srcAccessMask = vk::AccessFlagBits::eMemoryWrite,
                .dstAccessMask = vk::AccessFlagBits::eShaderRead,
                .oldLayout = vk::ImageLayout::eGeneral,""")
    edit(root, pc, """        cmdbuf.pipelineBarrier(vk::PipelineStageFlagBits::eColorAttachmentOutput,
                               vk::PipelineStageFlagBits::eColorAttachmentOutput,
                               vk::DependencyFlagBits::eByRegion, {}, {}, pre_barriers);""",
         """        cmdbuf.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
                               vk::PipelineStageFlagBits::eFragmentShader |
                               vk::PipelineStageFlagBits::eColorAttachmentOutput,
                               {}, {}, {}, pre_barriers);""")

    # Upstream's Vulkan cache is empty on each boot, and WarmUp actually
    # dereferences pipeline_cache before it is created. Use the donor's
    # validated cache file envelope, retain existing shader database.
    cache = base+"vk_pipeline_cache.cpp"
    header = base+"vk_pipeline_cache.h"
    shutil.copyfile(Path(__file__).with_name("driver_cache_file.h"),
                    root/(base+"driver_cache_file.h"))
    edit(root, cache, "#include <ranges>",
         '#include <ranges>\n#include <chrono>\n#include "common/thread.h"\n#include "common/elf_info.h"\n#include "video_core/renderer_vulkan/driver_cache_file.h"')
    edit(root, cache, """    WarmUp();

    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});
    ASSERT_MSG(cache_result == vk::Result::eSuccess, "Failed to create pipeline cache: {}",
               vk::to_string(cache_result));
    pipeline_cache = std::move(cache);
}

PipelineCache::~PipelineCache() = default;""",
         r"""    // BACHATA_DRIVER_CACHE: initialize the driver cache BEFORE warming
    // serialized compute/graphics pipelines which dereference this handle.
    std::vector<u8> bytes;
#ifdef __ANDROID__
    if (!BachataCompat::Sotc608() && EmulatorSettings.IsPipelineCacheEnabled()) {
        try {
            DriverCacheFile::Identity id{instance.GetVendorID(),instance.GetDeviceID(),
                                         instance.GetDriverVersion(),{}};
            const auto uuid = instance.GetPipelineCacheUUID();
            std::copy(uuid.begin(),uuid.end(),id.uuid.begin());
            const auto key=fmt::format("{:x}-{:x}-{:x}-{:016x}",id.vendor,id.device,id.driver,
                                      DriverCacheFile::Checksum(id.uuid));
            driver_cache_path=Common::FS::GetUserPath(Common::FS::PathType::CacheDir) /
                Common::ElfInfo::Instance().GameSerial() / "driver-v1" / key / "cache.bin";
            bytes=DriverCacheFile::Load(driver_cache_path,id);
        } catch (...) {
            driver_cache_path.clear();
        }
    }
#endif
    auto cache_create=instance.GetDevice().createPipelineCacheUnique({
        .initialDataSize=bytes.size(), .pInitialData=bytes.empty()?nullptr:bytes.data()});
    if (cache_create.result!=vk::Result::eSuccess && !bytes.empty()) {
        LOG_WARNING(Render_Vulkan,"Driver cache restore rejected; use empty cache");
        cache_create=instance.GetDevice().createPipelineCacheUnique({});
        bytes.clear();
    }
    ASSERT_MSG(cache_create.result == vk::Result::eSuccess, "Failed to create pipeline cache: {}",
               vk::to_string(cache_create.result));
    pipeline_cache=std::move(cache_create.value);
    LOG_INFO(Render_Vulkan,"BACHATA_DRIVER_CACHE loaded_bytes={}",bytes.size());
    WarmUp();
#ifdef __ANDROID__
    if (!driver_cache_path.empty()) {
        driver_cache_worker=std::jthread([this](std::stop_token stop) {
            Common::SetCurrentThreadName("Bachata:DriverCache");
            Common::SetCurrentThreadPriority(Common::ThreadPriority::Low);
            std::mutex sleep_mutex;
            std::unique_lock sleep_lock{sleep_mutex};
            while (!stop.stop_requested()) {
                driver_cache_wake.wait_for(sleep_lock,stop,std::chrono::seconds(30),[] { return false; });
                if (!stop.stop_requested()) SaveDriverCache();
            }
        });
    }
#endif
}

PipelineCache::~PipelineCache() {
    if (driver_cache_worker.joinable()) {
        driver_cache_worker.request_stop();
        driver_cache_wake.notify_all();
        driver_cache_worker.join();
    }
    SaveDriverCache();
}

void PipelineCache::SaveDriverCache() {
#ifdef __ANDROID__
    // BACHATA_DRIVER_CACHE_CHECKPOINT: donor GoW3 239b7df8145e.
    // Only a changed generation is snapshotted; Vulkan cache access is
    // serialized against actual pipeline creation, never against draws.
    // Filesystem writes happen outside the Vulkan lock.
    if (driver_cache_path.empty() || !pipeline_cache) return;
    try {
        DriverCacheFile::Identity id{instance.GetVendorID(),instance.GetDeviceID(),
                                     instance.GetDriverVersion(),{}};
        const auto uuid=instance.GetPipelineCacheUUID();
        std::copy(uuid.begin(),uuid.end(),id.uuid.begin());
        const auto& api=VULKAN_HPP_DEFAULT_DISPATCHER;
        const auto device=instance.GetDevice();
        std::vector<u8> bytes;
        u64 generation=0;
        {
            std::scoped_lock lock{driver_cache_vulkan_mutex};
            generation=driver_cache_generation;
            if (generation==driver_cache_saved_generation) return;
            size_t size=0;
            if (api.vkGetPipelineCacheData(device,*pipeline_cache,&size,nullptr)!=VK_SUCCESS ||
                size<32 || size>DriverCacheFile::MaxBytes) return;
            bytes.resize(size);
            if (api.vkGetPipelineCacheData(device,*pipeline_cache,&size,bytes.data())!=VK_SUCCESS ||
                size>bytes.size()) return;
            bytes.resize(size);
        }
        const u64 hash=DriverCacheFile::Checksum(bytes);
        if (hash==driver_cache_saved_hash && driver_cache_saved_generation!=0) {
            driver_cache_saved_generation=generation;
            return;
        }
        if (DriverCacheFile::Save(driver_cache_path,bytes,id)) {
            driver_cache_saved_generation=generation;
            driver_cache_saved_hash=hash;
            LOG_INFO(Render_Vulkan,"BACHATA_DRIVER_CACHE saved_bytes={}",bytes.size());
        }
    } catch (...) {
        LOG_WARNING(Render_Vulkan,"BACHATA_DRIVER_CACHE save skipped");
    }
#endif
}""")
    edit(root, header, "#include <variant>",
         "#include <variant>\n#include <filesystem>\n#include <mutex>\n#include <thread>\n#include <condition_variable>")
    edit(root, header, "    vk::UniquePipelineCache pipeline_cache;",
         """    vk::UniquePipelineCache pipeline_cache;
    std::filesystem::path driver_cache_path;
    std::mutex driver_cache_vulkan_mutex;
    std::condition_variable_any driver_cache_wake;
    std::jthread driver_cache_worker;
    u64 driver_cache_generation{1};
    u64 driver_cache_saved_generation{};
    u64 driver_cache_saved_hash{};
    void SaveDriverCache();""")
    # Only creation uses the driver cache object after WarmUp. Existing
    # pipeline hits never contend with the checkpoint worker.
    p=root/cache
    t=p.read_text()
    for first,last in (
        ("        it.value() = std::make_unique<GraphicsPipeline>(",
         "        RegisterPipelineData(graphics_key, pipeline_hash, sdata);"),
        ("        it.value() = std::make_unique<ComputePipeline>(",
         "        RegisterPipelineData(compute_key, sdata);"),
    ):
        start=t.index(first)
        end=t.index(last,start)
        body=t[start:end].rstrip()
        t=t[:start]+"""        {
            std::scoped_lock cache_lock{driver_cache_vulkan_mutex};
"""+ "\n".join("    "+line for line in body.splitlines())+"""
            ++driver_cache_generation;
        }

"""+t[end:]
    p.write_text(t)
    return {"display":"guest-sized intermediate without FSR, format-checked identity copy/blit, opaque sampling",
            "driverCache":"validated GoW3 cache file, initialize before warmup, periodic checkpoint and orderly shutdown",
            "notPorted":"AHardwareBuffer/SurfaceControl external semaphore protocol; native WSI retained"}
