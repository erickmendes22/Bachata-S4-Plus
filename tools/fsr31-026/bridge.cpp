// SPDX-License-Identifier: GPL-2.0-or-later
// Native FSR 3.1 backend, using FireBurn/FSR-Vulkan c64f093.
// This is the *effect library* only. The existing core must supply real
// scene colour, depth, motion vectors, and jitter to the dispatch.
#include <ffx_vk_portable.h>
#include <cstdint>
#include <cmath>
#include <cstdio>
#include <mutex>
#include <fstream>
#include <cstdlib>
#include <string>
namespace {
std::mutex guard;
FfxVkPortableUpscaleContext* ctx = nullptr;
FfxVkPortableUpscaleCreateInfo current{};
bool valid = false;
}
#define BS4_PUBLIC extern "C" __attribute__((visibility("default")))
BS4_PUBLIC int bs4_fsr31_abi() { return 0x00030104; }
BS4_PUBLIC int bs4_fsr31_create(const FfxVkPortableDeviceInfo* dev,
                               const FfxVkPortableUpscaleCreateInfo* ci) {
    if (!dev || !ci) return FFX_VK_PORTABLE_ERROR_INVALID_POINTER;
    std::lock_guard<std::mutex> lock(guard);
    if (ctx) return FFX_VK_PORTABLE_ERROR_INVALID_ARGUMENT;
    if (ffxVkPortableValidateUpscaleCreateInfo(ci)) return FFX_VK_PORTABLE_ERROR_INVALID_ARGUMENT;
    const auto result = ffxVkPortableUpscaleContextCreate(dev, ci, &ctx);
    if (result == FFX_VK_PORTABLE_OK) {current=*ci;valid=true;}
    else {ctx=nullptr;valid=false;}
    return result;
}
BS4_PUBLIC int bs4_fsr31_record(const FfxVkPortableUpscaleDispatchInfo* di) {
    if (!di) return FFX_VK_PORTABLE_ERROR_INVALID_POINTER;
    std::lock_guard<std::mutex> lock(guard);
    if (!valid || !ctx) return FFX_VK_PORTABLE_ERROR_INVALID_ARGUMENT;
    if (ffxVkPortableValidateUpscaleDispatchInfo(&current,di)) return FFX_VK_PORTABLE_ERROR_INVALID_ARGUMENT;
    return ffxVkPortableUpscaleContextRecordDispatch(ctx, di);
}
BS4_PUBLIC int bs4_fsr31_destroy_after_gpu_drain() {
    std::lock_guard<std::mutex> lock(guard);
    if (!ctx) return FFX_VK_PORTABLE_OK;
    auto* prev=ctx;ctx=nullptr;valid=false;
    return ffxVkPortableUpscaleContextDestroy(prev);
}


// Host call from the original BACHATA FsrPass::Render callsite.
// Nonzero is returned ONLY if a producer registered genuine game temporal
// color/depth/motion input for this same VkCommandBuffer. Otherwise FSR1 runs.
namespace {
struct PendingFrame {
    FfxVkPortableUpscaleDispatchInfo info{};
    VkImageView outputView{};
    bool available = false;
};
PendingFrame pending;
}
BS4_PUBLIC int bs4_fsr31_supply_temporal_frame(
    const FfxVkPortableUpscaleDispatchInfo* info, VkImageView outputView) {
    if (!info || !outputView || info->structSize != sizeof(*info)) return 0;
    std::lock_guard<std::mutex> lock(guard);
    if (!valid || !ctx || !info->depth.image || !info->motionVectors.image ||
        !info->color.image || !info->output.image) return 0;
    if (ffxVkPortableValidateUpscaleDispatchInfo(&current, info)) return 0;
    pending.info = *info;
    pending.outputView = outputView;
    pending.available = true;
    return 1;
}
BS4_PUBLIC uint64_t bs4_fsr31_try_render(
    uint64_t fsrPassObject, uint64_t commandBuffer, uint64_t inputView,
    uint64_t renderExtent, uint64_t outputExtent, uint64_t settings, uint64_t hdr) {
    (void)fsrPassObject;
    (void)inputView;
    (void)renderExtent;
    (void)outputExtent;
    (void)settings;
    (void)hdr;
    std::lock_guard<std::mutex> lock(guard);
    // Preference written by BACHATA 0.2.6's native Android settings UI.
    // Its absence or unreadability leaves the existing FSR 1 path untouched.
    static unsigned polls = 0;
    static bool enabled = false;
    static int preset = 1; // 0 Native AA, 1 Quality, 2 Balanced, 3 Performance, 4 Ultra
    if (++polls % 120u == 1u) {
        enabled = false;
        preset = 1;
        // The runtime launcher explicitly forwards this preference into
        // GLIBC/FEX via BACHATA_FSR31_MODE. -1 = disabled, 0..4 = preset.
        // This also works when the Linux rootfs hides Android /data paths.
        if (const char* mode = std::getenv("BACHATA_FSR31_MODE")) {
            if (*mode >= '0' && *mode <= '4' && mode[1] == '\0') {
                enabled = true;
                preset = *mode - '0';
            }
        } else for (const char* path : {
              "/data/user/0/com.bachatas4.plusapp/shared_prefs/bs4_fsr31.xml",
              "/data/data/com.bachatas4.plusapp/shared_prefs/bs4_fsr31.xml"}) {
            std::ifstream settings(path);
            if (!settings) continue;
            const std::string contents{std::istreambuf_iterator<char>{settings}, {}};
            if (contents.find("name=\"enabled\" value=\"true\"") != std::string::npos)
                enabled = true;
            const std::string tag = "name=\"preset\" value=\"";
            const auto at = contents.find(tag);
            if (at != std::string::npos && at + tag.size() < contents.size()) {
                const char n = contents[at + tag.size()];
                if (n >= '0' && n <= '4') preset = n - '0';
            }
            break;
        }
    }
    if (!enabled) return 0;
    if (!valid || !ctx || !pending.available ||
        pending.info.commandBuffer != reinterpret_cast<VkCommandBuffer>(commandBuffer)) return 0;
    auto info = pending.info;
    // Preset scales are constraints on the *actual scene render extent*, never
    // post-presentation resizes.  Native AA = 1.0, Quality = 1.5,
    // Balanced ~=1.7, Performance = 2.0, Ultra = 3.0.
    // Until the game's producer supplies an image at the requested extent,
    // retain the original FSR1 renderer instead of mislabelling its output.
    const uint64_t ow = info.outputSize.width;
    const uint64_t oh = info.outputSize.height;
    const uint64_t rw = info.renderSize.width;
    const uint64_t rh = info.renderSize.height;
    static constexpr float ratios[] = {1.f,1.5f,1.7f,2.f,3.f};
    const float desired = ratios[preset];
    if (!rw || !rh || !ow || !oh ||
        (std::abs(float(ow) / float(rw) - desired) > 0.12f) ||
        (std::abs(float(oh) / float(rh) - desired) > 0.12f)) return 0;
    const VkImageView view = pending.outputView;
    pending.available = false;
    if (ffxVkPortableValidateUpscaleDispatchInfo(&current,&info)) return 0;
    return ffxVkPortableUpscaleContextRecordDispatch(ctx,&info) == FFX_VK_PORTABLE_OK
        ? reinterpret_cast<uint64_t>(view) : 0;
}

namespace {
FfxVkPortableDeviceInfo acquired_device{};
bool device_attached = false;
}
BS4_PUBLIC int bs4_fsr31_attach(void* fsr_pass, void* instance_object, VkDevice device,
                                 void* allocator, uint32_t swap_images) {
    (void)allocator;
    (void)swap_images;
    if (!fsr_pass || !instance_object || !device) return -1;
    std::lock_guard<std::mutex> lock(guard);
    // The original BACHATA core is unchanged in memory layout. vk::UniqueInstance
    // stores the raw VkInstance in its first pointer-sized field. Query real
    // physical devices through Vulkan instead of assuming a C++ member offset.
    const VkInstance instance = *static_cast<VkInstance*>(instance_object);
    if (!instance) return -2;
    uint32_t count = 0;
    VkResult err = vkEnumeratePhysicalDevices(instance, &count, nullptr);
    if (err != VK_SUCCESS || count != 1) {
        std::fprintf(stderr,
            "[BS4_FSR31] attach: expected one Vulkan physical device, result=%d count=%u\\n",
            int(err), count);
        return -3;
    }
    VkPhysicalDevice physical{};
    err = vkEnumeratePhysicalDevices(instance, &count, &physical);
    if (err != VK_SUCCESS || !physical) return -4;
    FfxVkPortableDeviceInfo info{};
    info.structSize = sizeof(info);
    info.instance = instance;
    info.physicalDevice = physical;
    info.device = device;
    info.getDeviceProcAddr = vkGetDeviceProcAddr;
    info.queue = VK_NULL_HANDLE;
    info.queueFamilyIndex = 0;
    info.synchronization2Enabled = VK_TRUE;
    VkPhysicalDeviceFeatures features{};
    vkGetPhysicalDeviceFeatures(physical, &features);
    // The BACHATA Vulkan device may not enable this optional capability.
    // Do not claim enabled features solely from physical-device support.
    info.shaderStorageImageWriteWithoutFormatEnabled = VK_FALSE;
    acquired_device = info;
    device_attached = true;
    VkPhysicalDeviceProperties props{};
    vkGetPhysicalDeviceProperties(physical, &props);
    std::fprintf(stderr,
        "[BS4_FSR31] attached core024 GPU=%s vendor=0x%x, driver=0x%x, "
        "shaderStorageImageWriteWithoutFormat-supported=%d\\n",
        props.deviceName, props.vendorID, props.driverVersion,
        int(features.shaderStorageImageWriteWithoutFormat));
    return 0;
}
BS4_PUBLIC int bs4_fsr31_attachment_ready() {
    std::lock_guard<std::mutex> lock(guard);
    return device_attached ? 1 : 0;
}
