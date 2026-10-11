// SPDX-License-Identifier: GPL-2.0-or-later
// Native FSR 3.1 backend, using FireBurn/FSR-Vulkan c64f093.
// This is the *effect library* only. The existing core must supply real
// scene colour, depth, motion vectors, and jitter to the dispatch.
#include <ffx_vk_portable.h>
#include <cstdint>
#include <cstdio>
#include <mutex>
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
