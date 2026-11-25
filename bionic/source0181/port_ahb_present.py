"""Target-title AHB/SurfaceControl transport; stable WSI fallback and real presented-frame accounting."""
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
    vk::ImageLayout PresentLayout() const;
    vk::ImageLayout AcquireLayout() const;''')
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
#include "common/elf_info.h"
static bool BachataAhbTarget(){
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const char* opt=std::getenv("BACHATA_AHB_PRESENT");
    return (!opt||opt[0]!='0')&&(serial=="CUSA00785"||serial=="CUSA08809"||serial=="CUSA08034");
}
#endif''')
    edit(sc,"    SetSurfaceProperties();",
r'''    SetSurfaceProperties();
#ifdef __ANDROID__
    // Use the same RGBA format and physical extent as WSI, keep HDR on WSI.
    if(!ahb_disabled&&BachataAhbTarget()&&!needs_hdr&&
       surface_format.format==vk::Format::eR8G8B8A8Unorm&&
       surface_format.colorSpace==vk::ColorSpaceKHR::eSrgbNonlinear&&
       transform==vk::SurfaceTransformFlagBitsKHR::eIdentity&&
       instance.SupportsAndroidAhbPresent()) {
        auto candidate=std::make_unique<AndroidAhbPresent>(instance);
        auto* native=static_cast<ANativeWindow*>(window.GetWindowInfo().render_surface);
        if(candidate->Create(native,extent.width,extent.height)){
            ahb=std::move(candidate);
            composite_alpha=vk::CompositeAlphaFlagBitsKHR::eOpaque;
            image_count=AndroidAhbPresent::Count;image_index=0;frame_index=0;
            LOG_INFO(Render_Vulkan,"BACHATA_AHB_SURFACECONTROL_ACTIVE {}x{}",width,height);
            return;
        }
        ahb_disabled=true;
        LOG_WARNING(Render_Vulkan,"AHB initialization rejected; retaining Android WSI");
    }
#endif''')
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
vk::ImageLayout Swapchain::AcquireLayout() const {
#ifdef __ANDROID__
    if(ahb)return ahb->AcquireLayout(image_index);
#endif
    return vk::ImageLayout::eUndefined;
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
'''                .oldLayout = swapchain.AcquireLayout(),
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
    edit(sc,"    // Try to find a suitable format.",r'''#ifdef __ANDROID__
    if(BachataAhbTarget()&&instance.SupportsAndroidAhbPresent()){
        for(const auto& f:formats){
            if(f.format==vk::Format::eR8G8B8A8Unorm&&f.colorSpace==vk::ColorSpaceKHR::eSrgbNonlinear){
                surface_format=f;return;
            }
        }
    }
#endif
    // Try to find a suitable format.''')
    edit("vk_scheduler.cpp",'''    static constexpr std::array<vk::PipelineStageFlags, 2> wait_stage_masks = {
        vk::PipelineStageFlagBits::eAllCommands,
        vk::PipelineStageFlagBits::eColorAttachmentOutput,
    };''','''    // A ready image can be sampled, copied or blitted before color attachment output.
    static constexpr std::array<vk::PipelineStageFlags, 4> wait_stage_masks = {
        vk::PipelineStageFlagBits::eAllCommands, vk::PipelineStageFlagBits::eAllCommands,
        vk::PipelineStageFlagBits::eAllCommands, vk::PipelineStageFlagBits::eAllCommands,
    };''')
    edit(p,'#include "common/debug.h"','#include "common/debug.h"\n#ifdef ENABLE_BACHATA_RUNTIME\n#include "platform/bachata/runtime_client.h"\n#endif')
    edit(p,'''    // Present to swapchain.
    {
        std::scoped_lock submit_lock{Scheduler::submit_mutex};
        if (!swapchain.Present()) {''','''    // Report new guest frames only after a successful presentation.
    bool presented=false;
    {
        std::scoped_lock submit_lock{Scheduler::submit_mutex};
        presented=swapchain.Present();
        if (!presented) {''')
    edit(p,'''    free_frame();
    if (!is_reusing_frame && is_game_frame) {''','''    free_frame();
#ifdef ENABLE_BACHATA_RUNTIME
    if(presented&&!is_reusing_frame&&is_game_frame) Platform::Bachata::ReportPresentedFrame();
#endif
    if (!is_reusing_frame && is_game_frame) {''')
    driver=root/"src/core/libraries/videoout/driver.cpp"
    old=driver.read_text()
    import re
    old,n=re.subn(r"#ifdef ENABLE_BACHATA_RUNTIME\n(?:    //[^\n]*\n)?    Platform::Bachata::ReportPresentedFrame\(\);\n#endif\n","",old)
    if n!=1: raise RuntimeError("duplicate or missing original frame report")
    driver.write_text(old)
    return {"transport":"three imported AHBs, foreign queue ownership, sync-file import/export, same-process SurfaceControl",
            "scope":"three target serials; BACHATA_AHB_PRESENT=0 opt-out; SDR RGBA, identity transform; WSI fallback",
            "remaining":"guest-sized compositor buffers; direct blit when supported by current presenter"}
