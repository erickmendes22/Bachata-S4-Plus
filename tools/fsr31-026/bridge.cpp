// SPDX-License-Identifier: GPL-2.0-or-later
// Native FSR 3.1 backend, using FireBurn/FSR-Vulkan c64f093.
// This is the *effect library* only. The existing core must supply real
// scene colour, depth, motion vectors, and jitter to the dispatch.
#include <ffx_vk_portable.h>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <fstream>
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
BS4_PUBLIC uint64_t bs4_fsr31_try_render(uint64_t fsr1OutputView,
    uint64_t fsrPassObject, uint64_t commandBuffer, uint64_t inputView,
    uint64_t renderExtent, uint64_t outputExtent, uint64_t settings, uint64_t hdr) {
    (void)fsr1OutputView;
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
    if (++polls % 120u == 1u) {
        enabled = false;
        for (const char* path : {
              "/data/user/0/com.bachatas4.android/shared_prefs/bs4_fsr31.xml",
              "/data/data/com.bachatas4.android/shared_prefs/bs4_fsr31.xml"}) {
            std::ifstream settings(path);
            if (!settings) continue;
            const std::string contents{std::istreambuf_iterator<char>{settings}, {}};
            if (contents.find("name=\"enabled\" value=\"true\"") != std::string::npos)
                enabled = true;
            break;
        }
    }
    if (!enabled) return 0;
    if (!valid || !ctx || !pending.available ||
        pending.info.commandBuffer != reinterpret_cast<VkCommandBuffer>(commandBuffer)) return 0;
    auto info = pending.info;
    const VkImageView view = pending.outputView;
    pending.available = false;
    if (ffxVkPortableValidateUpscaleDispatchInfo(&current,&info)) return 0;
    return ffxVkPortableUpscaleContextRecordDispatch(ctx,&info) == FFX_VK_PORTABLE_OK
        ? reinterpret_cast<uint64_t>(view) : 0;
}
