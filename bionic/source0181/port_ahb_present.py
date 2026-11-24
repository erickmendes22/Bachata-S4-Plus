"""Opt-in AHB/SurfaceControl same-process swapchain with WSI fallback."""
from pathlib import Path
import shutil

def apply(root:Path):
    prefix="src/video_core/renderer_vulkan/"
    for name in ("ahb_release_slots.h","vk_ahb_present.h"):
        shutil.copyfile(Path(__file__).with_name(name),root/(prefix+name))
    def edit(rel,old,new):
        p=root/(prefix+rel)
        s=p.read_text()
        if s.count(old)!=1: raise RuntimeError("AHB present source drift "+rel+": "+old[:100])
        p.write_text(s.replace(old,new,1))
    edit("vk_instance.h","    bool supports_memory_budget{};",
         "    bool supports_memory_budget{};\n    bool android_ahb_present{};")
    edit("vk_instance.h","    bool CanReportMemoryUsage() const {",
         "    bool SupportsAndroidAhbPresent() const { return android_ahb_present; }\n\n    bool CanReportMemoryUsage() const {")
    edit("vk_instance.cpp","boost::container::static_vector<const char*, 32> enabled_extensions;",
         "boost::container::static_vector<const char*, 48> enabled_extensions;")
    edit("vk_instance.cpp","    // Optional\n    maintenance_5",
r'''#ifdef __ANDROID__
    // All three extensions and SYNC_FD import/export are mandatory.
    const bool ahb_mem=add_extension(VK_ANDROID_EXTERNAL_MEMORY_ANDROID_HARDWARE_BUFFER_EXTENSION_NAME);
    const bool ahb_foreign=add_extension(VK_EXT_QUEUE_FAMILY_FOREIGN_EXTENSION_NAME);
    const bool ahb_sync=add_extension(VK_KHR_EXTERNAL_SEMAPHORE_FD_EXTENSION_NAME);
    const auto sync_props=physical_device.getExternalSemaphoreProperties({
        .handleType=vk::ExternalSemaphoreHandleTypeFlagBits::eSyncFd});
    const auto sync_required=vk::ExternalSemaphoreFeatureFlagBits::eExportable|
                             vk::ExternalSemaphoreFeatureFlagBits::eImportable;
    android_ahb_present=ahb_mem&&ahb_foreign&&ahb_sync&&
        (sync_props.externalSemaphoreFeatures&sync_required)==sync_required;
#endif
    // Optional
    maintenance_5''')
    sh="vk_swapchain.h";sc="vk_swapchain.cpp"
    edit(sh,"#include <mutex>","#include <mutex>\n#include <memory>\n#include <utility>")
    edit(sh,"class Scheduler;","class Scheduler;\n#ifdef __ANDROID__\nclass AndroidAhbPresent;\n#endif")
    edit(sh,'''    vk::Image Image() const {
        return images[image_index];
    }

    vk::ImageView ImageView() const {
        return images_view[image_index];
    }''',
'''    vk::Image Image() const;
    vk::ImageView ImageView() const;
    std::pair<u32,u32> AcquireQueues() const;
    std::pair<u32,u32> ReleaseQueues() const;
    vk::ImageLayout PresentLayout() const;''')
    edit(sh,'''    [[nodiscard]] vk::Semaphore GetImageAcquiredSemaphore() const {
        return image_acquired[frame_index];
    }

    [[nodiscard]] vk::Semaphore GetPresentReadySemaphore() const {
        return present_ready[image_index];
    }''',
'''    [[nodiscard]] vk::Semaphore GetImageAcquiredSemaphore() const;
    [[nodiscard]] vk::Semaphore GetPresentReadySemaphore() const;''')
    edit(sh,"    bool supports_hdr = false; // SC supports HDR output",
'''    bool supports_hdr = false; // SC supports HDR output
#ifdef __ANDROID__
    std::unique_ptr<AndroidAhbPresent> ahb;
    bool ahb_disabled{};
#endif''')
    edit(sc,'#include "video_core/renderer_vulkan/vk_swapchain.h"',
r'''#include "video_core/renderer_vulkan/vk_swapchain.h"
#ifdef __ANDROID__
#include "video_core/renderer_vulkan/vk_ahb_present.h"
#include "android_surface.h"
#endif''')
    edit(sc,"    SetSurfaceProperties();",
r'''#ifdef __ANDROID__
    // Experimental branch: require explicit opt-in until device validation.
    // Preserve the existing WSI format so ImGui/HDR/screenshot contracts stay valid.
    const char* enable=std::getenv("BACHATA_AHB_PRESENT");
    if(!ahb_disabled&&enable&&enable[0]=='1'&&!BachataCompat::Sotc608()&&
       !needs_hdr&&!supports_hdr&&surface_format.format==vk::Format::eR8G8B8A8Unorm&&
       instance.SupportsAndroidAhbPresent()) {
        auto candidate=std::make_unique<AndroidAhbPresent>(instance);
        auto* native=BachataAndroid::surface.load(std::memory_order_acquire);
        if(candidate->Create(native,width,height)){
            ahb=std::move(candidate);
            extent=vk::Extent2D{width,height};
            image_count=AndroidAhbPresent::Count;image_index=0;frame_index=0;
            LOG_INFO(Render_Vulkan,"BACHATA_AHB_SURFACECONTROL_ACTIVE {}x{}",width,height);
            return;
        }
        ahb_disabled=true;
        LOG_WARNING(Render_Vulkan,"AHB initialization rejected; retaining Android WSI");
    }
#endif
    SetSurfaceProperties();''')
    edit(sc,"bool Swapchain::AcquireNextImage() {",
r'''vk::Image Swapchain::Image() const {
#ifdef __ANDROID__
    if(ahb)return ahb->Image(image_index);
#endif
    return images[image_index];
}
vk::ImageView Swapchain::ImageView() const {
#ifdef __ANDROID__
    if(ahb)return ahb->View(image_index);
#endif
    return images_view[image_index];
}
vk::Semaphore Swapchain::GetImageAcquiredSemaphore() const {
#ifdef __ANDROID__
    if(ahb)return ahb->Acquired(image_index);
#endif
    return image_acquired[frame_index];
}
vk::Semaphore Swapchain::GetPresentReadySemaphore() const {
#ifdef __ANDROID__
    if(ahb)return ahb->Ready(image_index);
#endif
    return present_ready[image_index];
}
std::pair<u32,u32> Swapchain::AcquireQueues() const {
#ifdef __ANDROID__
    if(ahb)return {VK_QUEUE_FAMILY_FOREIGN_EXT,instance.GetGraphicsQueueFamilyIndex()};
#endif
    return {VK_QUEUE_FAMILY_IGNORED,VK_QUEUE_FAMILY_IGNORED};
}
std::pair<u32,u32> Swapchain::ReleaseQueues() const {
#ifdef __ANDROID__
    if(ahb)return {instance.GetGraphicsQueueFamilyIndex(),VK_QUEUE_FAMILY_FOREIGN_EXT};
#endif
    return {VK_QUEUE_FAMILY_IGNORED,VK_QUEUE_FAMILY_IGNORED};
}
vk::ImageLayout Swapchain::PresentLayout() const {
#ifdef __ANDROID__
    if(ahb)return vk::ImageLayout::eGeneral;
#endif
    return vk::ImageLayout::ePresentSrcKHR;
}
bool Swapchain::AcquireNextImage() {
#ifdef __ANDROID__
    if(ahb) {
        if(ahb->Acquire(image_index))return true;
        ahb_disabled=true;
        LOG_WARNING(Render_Vulkan,"AHB release timeout; recreate Android WSI");
        return false;
    }
#endif''')
    edit(sc,"bool Swapchain::Present() {",
r'''bool Swapchain::Present() {
#ifdef __ANDROID__
    if(ahb) {
        if(!ahb->Present(image_index)){
            ahb_disabled=true;
            LOG_WARNING(Render_Vulkan,"AHB present failed; recreate Android WSI");
            return false;
        }
        frame_index=(frame_index+1)%image_count;
        return true;
    }
#endif''')
    edit(sc,"    for (auto& image_view : images_view) {",
r'''#ifdef __ANDROID__
    ahb.reset();
#endif
    for (auto& image_view : images_view) {''')
    edit(sc,"        device.destroySwapchainKHR(swapchain);",
         "        device.destroySwapchainKHR(swapchain);\n        swapchain=vk::SwapchainKHR{};")
    p="vk_presenter.cpp"
    edit(p,"    const vk::Image swapchain_image = swapchain.Image();",
         "    const auto acquire_queues=swapchain.AcquireQueues();\n    const auto release_queues=swapchain.ReleaseQueues();\n    const vk::Image swapchain_image = swapchain.Image();")
    edit(p,'''                .oldLayout = vk::ImageLayout::eUndefined,
                .newLayout = vk::ImageLayout::eColorAttachmentOptimal,
                .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
                .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
                .image = swapchain_image,''',
'''                .oldLayout = vk::ImageLayout::eUndefined,
                .newLayout = vk::ImageLayout::eColorAttachmentOptimal,
                .srcQueueFamilyIndex = acquire_queues.first,
                .dstQueueFamilyIndex = acquire_queues.second,
                .image = swapchain_image,''')
    edit(p,'''            .newLayout = vk::ImageLayout::ePresentSrcKHR,
            .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
            .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
            .image = swapchain_image,''',
'''            .newLayout = swapchain.PresentLayout(),
            .srcQueueFamilyIndex = release_queues.first,
            .dstQueueFamilyIndex = release_queues.second,
            .image = swapchain_image,''')
    edit(p,"    info.AddWait(swapchain.GetImageAcquiredSemaphore());",
         "    if (const auto acquired=swapchain.GetImageAcquiredSemaphore()) info.AddWait(acquired);")
    return {"transport":"three imported AHBs, foreign queue ownership, sync-file import/export, same-process SurfaceControl",
            "scope":"opt-in BACHATA_AHB_PRESENT=1; SDR RGBA only; WSI fallback on init or release failure",
            "remaining":"guest-sized compositor buffers and overlay-free direct blit"}
