#include "vulkan_capture.h"
// SPDX-License-Identifier: GPL-2.0-or-later
// Native FSR 3.1 backend, using FireBurn/FSR-Vulkan c64f093.
// This is the *effect library* only. The existing core must supply real
// scene colour, depth, motion vectors, and jitter to the dispatch.
#include <ffx_vk_portable.h>
extern "C" uint64_t bs4_fsr31_generic_render(const FfxVkPortableDeviceInfo* info,
    VkCommandBuffer cmd,VkImageView input,VkExtent2D inputSize,
    VkExtent2D outputSize,int preset,int hdr,int pre_ui,VkImageView forced_depth);
extern "C" VkImage bs4_fsr31_output_image(VkImageView);
#include <cstdint>
#include <cmath>
#include <cstdio>
#include <mutex>
#include <vector>
#include <fstream>
#include <dlfcn.h>
#include <atomic>
#include <algorithm>
#include <cstring>
#include <cstdlib>
#include <string>
namespace {
std::mutex guard;
FfxVkPortableUpscaleContext* ctx = nullptr;
FfxVkPortableUpscaleCreateInfo current{};
FfxVkPortableDeviceInfo acquired_device{};
bool device_attached = false;
std::atomic<VkInstance> fsr31_tracked_instance{VK_NULL_HANDLE};
std::atomic<VkPhysicalDevice> fsr31_tracked_physical{VK_NULL_HANDLE};
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
extern "C" void bs4_port_on_present();
extern "C" VkImageView bs4_port_ui_present(VkCommandBuffer);
extern "C" void bs4_port_ui_finish_present(VkCommandBuffer);
BS4_PUBLIC uint64_t bs4_fsr31_try_render(
    uint64_t fsrPassObject, uint64_t commandBuffer, uint64_t inputView,
    uint64_t renderExtent, uint64_t outputExtent, uint64_t settings, uint64_t hdr) {
    (void)fsrPassObject;
    (void)inputView;
    (void)renderExtent;
    (void)outputExtent;
    (void)settings;
    (void)hdr;
    // The port renders its final 720p HUD in the FSR output and gives that
    // image directly to the original FsrPass/Presenter. The game 1080p
    // attachment remains untouched. A partially prepared output is NEVER used.
    const auto cb=reinterpret_cast<VkCommandBuffer>(commandBuffer);
    if(const VkImageView ui=bs4_port_ui_present(cb);ui) {
        bs4_port_ui_finish_present(cb);
        bs4_port_on_present();
        return reinterpret_cast<uint64_t>(ui);
    }
    bs4_port_on_present();
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
    static bool logged_render = false;
    if (!logged_render) {
        logged_render = true;
        std::fprintf(stderr,
          "[BS4_FSR31] presenter hook enabled=%d preset=%d attached=%d input=%ux%u output=%ux%u\\n",
          int(enabled), preset, int(device_attached), unsigned(renderExtent), unsigned(renderExtent >> 32),
          unsigned(outputExtent), unsigned(outputExtent >> 32));
    }
    if (!enabled) return 0;
    // Presenter cannot infer scene motion or separate UI from a completed
    // VideoOut image. The discarded optical-flow path must never be revived.
    if(!valid || !ctx || !pending.available ||
       pending.info.commandBuffer!=reinterpret_cast<VkCommandBuffer>(commandBuffer))
        return 0;
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



/* Called strictly at the transition from the game's reduced 3D render
 * target to the first full-size UI render target. This uses the existing
 * FSR 3.1 backend and keeps the stock presenter as a fallback. */
BS4_PUBLIC int bs4_fsr31_pre_ui_dispatch(
        VkCommandBuffer command, VkImageView scene_color, VkImageView scene_depth,
        VkExtent2D scene_extent, VkExtent2D output_extent,
        VkImage* output_image) {
    if (!output_image) return 0;
    *output_image = VK_NULL_HANDLE;
    if (!command || !scene_color || !scene_depth || !scene_extent.width ||
        !scene_extent.height) return 0;
    FfxVkPortableDeviceInfo info{};
    int preset = -1;
    {
        std::lock_guard<std::mutex> lock(guard);
        if (!device_attached) return 0;
        info = acquired_device;
        if (const char* mode=std::getenv("BACHATA_FSR31_MODE")) {
            if (mode[0]>='0'&&mode[0]<='4'&&mode[1]==0)
                preset=mode[0]-'0';
        }
    }
    if (preset < 0) return 0;
    const auto upscaled = bs4_fsr31_generic_render(
        &info,command,scene_color,scene_extent,output_extent,preset,0,1,scene_depth);
    if (!upscaled) return 0;
    const auto image = bs4_fsr31_output_image(
        reinterpret_cast<VkImageView>(upscaled));
    if (!image) return 0;
    *output_image=image;
    static bool first=true;
    if(first) {
        first=false;
        std::fprintf(stderr,
          "[BS4_FSR31] FIRST_PRE_UI_DISPATCH scene=%ux%u output=%ux%u preset=%d\\n",
          scene_extent.width,scene_extent.height,
          output_extent.width,output_extent.height,preset);
    }
    return 1;
}

// CPU-only resource preparation. Returns the output that the next dispatch will use.
BS4_PUBLIC VkImageView bs4_fsr31_prepare_resources(
    VkCommandBuffer cb,VkImageView color,VkImageView depth,
    VkExtent2D scene,VkExtent2D output) {
    FfxVkPortableDeviceInfo info{};int preset=-1;
    {std::lock_guard<std::mutex> lock(guard);if(!device_attached)return VK_NULL_HANDLE;
     info=acquired_device;const char* mode=std::getenv("BACHATA_FSR31_MODE");
     if(mode&&mode[0]>='0'&&mode[0]<='4'&&mode[1]==0)preset=mode[0]-'0';}
    if(preset<0)return VK_NULL_HANDLE;
    return reinterpret_cast<VkImageView>(bs4_fsr31_generic_render(
        &info,cb,color,scene,output,preset,0,2,depth));
}

BS4_PUBLIC int bs4_fsr31_ui_device(
    VkDevice* out_device,VkPhysicalDevice* out_physical) {
    if(!out_device||!out_physical)return 0;
    std::lock_guard<std::mutex> lock(guard);
    if(!device_attached)return 0;
    *out_device=acquired_device.device;
    *out_physical=acquired_device.physicalDevice;
    return !!(*out_device) && !!(*out_physical);
}

BS4_PUBLIC int bs4_fsr31_attach(void* fsr_pass, void* instance_object, VkDevice device,
                                 void* allocator, uint32_t swap_images) {
    std::fprintf(stderr, "[BS4_FSR31] attach hook entered: fsr=%p instance=%p device=%p\\n", fsr_pass, instance_object, (void*)device);
    (void)allocator;
    (void)swap_images;
    const auto fail = [](int code) { std::fprintf(stderr, "[BS4_FSR31] attach failed code=%d\\n", code); return code; };
    if (!fsr_pass || !instance_object || !device) return fail(-1);
    std::lock_guard<std::mutex> lock(guard);
    // The Instance& argument is a C++ object, not a raw VkInstance.
    // R9 incorrectly dereferenced its first field, returning attach -2.
    // Use the real opaque handles intercepted through Vulkan instead.
    const VkInstance instance =
        fsr31_tracked_instance.load(std::memory_order_acquire);
    const VkPhysicalDevice physical =
        fsr31_tracked_physical.load(std::memory_order_acquire);
    if (!instance || !physical) {
        std::fprintf(stderr,
            "[BS4_FSR31] attach: intercepted Vulkan handles absent "
            "instance=%p physical=%p\\n",
            reinterpret_cast<void*>(instance), reinterpret_cast<void*>(physical));
        return fail(-2);
    }
    // Validate the physical-device handle against this Vulkan instance.
    uint32_t count = 0;
    const VkResult enumerate = vkEnumeratePhysicalDevices(instance, &count, nullptr);
    if (enumerate != VK_SUCCESS || !count || count > 128) return fail(-3);
    std::vector<VkPhysicalDevice> devices(count);
    const VkResult listed =
        vkEnumeratePhysicalDevices(instance, &count, devices.data());
    if (listed != VK_SUCCESS ||
        std::find(devices.begin(), devices.begin() + count, physical) ==
            devices.begin() + count) return fail(-4);
    FfxVkPortableDeviceInfo info{};
    info.structSize = sizeof(info);
    info.instance = instance;
    info.physicalDevice = physical;
    info.device = device;
    info.getDeviceProcAddr = vkGetDeviceProcAddr;
    // The portable SDK must receive the same live graphics queue family
    // selected by the host Vulkan device. A VK_NULL_HANDLE queue was a
    // definite bug in R5/R6 and makes FSR context creation invalid.
    uint32_t queue_count = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(physical, &queue_count, nullptr);
    if (!queue_count || queue_count > 128) return fail(-5);
    std::vector<VkQueueFamilyProperties> queue_properties(queue_count);
    vkGetPhysicalDeviceQueueFamilyProperties(physical, &queue_count,
                                               queue_properties.data());
    uint32_t family = queue_count;
    for (uint32_t i = 0; i < queue_count; ++i) {
        if ((queue_properties[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) &&
             queue_properties[i].queueCount) { family = i; break; }
    }
    if (family == queue_count) return fail(-6);
    VkQueue graphics_queue = VK_NULL_HANDLE;
    vkGetDeviceQueue(device, family, 0, &graphics_queue);
    if (!graphics_queue) return fail(-7);
    info.queue = graphics_queue;
    info.queueFamilyIndex = family;
    info.synchronization2Enabled = VK_TRUE;
    VkPhysicalDeviceFeatures features{};
    vkGetPhysicalDeviceFeatures(physical, &features);
    // The BACHATA Vulkan device may not enable this optional capability.
    // Do not claim enabled features solely from physical-device support.
    // Read only the actual vkCreateDevice interception result, never physical support.
    extern std::atomic<bool> fsr31_storage_feature_enabled;
    info.shaderStorageImageWriteWithoutFormatEnabled =
        fsr31_storage_feature_enabled.load() ? VK_TRUE : VK_FALSE;
    acquired_device = info;
    device_attached = true;
    VkPhysicalDeviceProperties props{};
    vkGetPhysicalDeviceProperties(physical, &props);
    Dl_info shared_library{};
    dladdr(reinterpret_cast<void*>(&bs4_fsr31_attach), &shared_library);
    std::fprintf(stderr, "[BS4_FSR31] module_base=%p gfx_queue_family=%u\\n",
                 shared_library.dli_fbase, family);
    std::fprintf(stderr,
        "[BS4_FSR31] attached core025 GPU=%s vendor=0x%x, driver=0x%x, "
        "shaderStorageImageWriteWithoutFormat-supported=%d\\n",
        props.deviceName, props.vendorID, props.driverVersion,
        int(features.shaderStorageImageWriteWithoutFormat));
    return 0;
}
BS4_PUBLIC int bs4_fsr31_attachment_ready() {
    std::lock_guard<std::mutex> lock(guard);
    return device_attached ? 1 : 0;
}

std::atomic<bool> fsr31_storage_feature_enabled{false};

namespace {
PFN_vkCreateDevice real_create_device = nullptr;
PFN_vkCreateInstance real_create_instance = nullptr;
using RealDlsym = void* (*)(void*, const char*);
RealDlsym real_dlsym() {
    // glibc's versioned lookup avoids recursion through our dlsym interposer.
    return reinterpret_cast<RealDlsym>(
        dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.34"));
}
PFN_vkGetInstanceProcAddr real_gipa() {
    static auto fn = reinterpret_cast<PFN_vkGetInstanceProcAddr>(
        dlvsym(RTLD_NEXT, "vkGetInstanceProcAddr", "GLIBC_2.34"));
    if (!fn) {
        if (auto ds = real_dlsym()) {
            fn = reinterpret_cast<PFN_vkGetInstanceProcAddr>(
                ds(RTLD_NEXT, "vkGetInstanceProcAddr"));
        }
    }
    return fn;
}
bool fsr31_requested() {
    const char* mode = std::getenv("BACHATA_FSR31_MODE");
    if(!(mode && mode[0]>='0' && mode[0]<='4' && mode[1]==0))return false;
    // The R15 dispatcher retains cores 020/023/024. Forwarding a preference
    // must never interpose their Vulkan renderer: only the patched 025 owns
    // this ABI. /proc/maps also works when invoked through the GLIBC loader.
    static const bool core025=[] {
        std::ifstream maps("/proc/self/maps");std::string line;
        while(std::getline(maps,line)) {
            const auto p=line.find("/shadps4-arm64-025");
            if(p==std::string::npos)continue;
            const auto end=p+sizeof("/shadps4-arm64-025")-1;
            if(end==line.size() || line[end]==' ')return true;
        }
        return false;
    }();
    return core025;
}
VKAPI_ATTR VkResult VKAPI_CALL fsr31_create_instance(
        const VkInstanceCreateInfo* requested,
        const VkAllocationCallbacks* allocator, VkInstance* output) {
    if (!real_create_instance) return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult result = real_create_instance(requested, allocator, output);
    if (result == VK_SUCCESS && output && *output) {
        fsr31_tracked_instance.store(*output, std::memory_order_release);
        std::fprintf(stderr,"[BS4_FSR31] intercepted vkCreateInstance success instance=%p\\n",
                     reinterpret_cast<void*>(*output));
    }
    return result;
}
VKAPI_ATTR VkResult VKAPI_CALL fsr31_create_device(
        VkPhysicalDevice physical, const VkDeviceCreateInfo* requested,
        const VkAllocationCallbacks* allocator, VkDevice* output) {
    if (!real_create_device || !requested)
        return VK_ERROR_INITIALIZATION_FAILED;
    if (!fsr31_requested())
        return real_create_device(physical, requested, allocator, output);
    VkPhysicalDeviceFeatures supported{};
    vkGetPhysicalDeviceFeatures(physical, &supported);
    if (!supported.shaderStorageImageWriteWithoutFormat) {
        std::fprintf(stderr, "[BS4_FSR31] GPU feature unsupported, using FSR1\\n");
        return real_create_device(physical, requested, allocator, output);
    }
    VkDeviceCreateInfo ci = *requested;
    VkPhysicalDeviceFeatures2 f2{};
    VkPhysicalDeviceFeatures legacy{};
    bool enabled = false;
    if (ci.pNext) {
        auto head = reinterpret_cast<const VkBaseInStructure*>(ci.pNext);
        if (head->sType == VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2) {
            f2 = *reinterpret_cast<const VkPhysicalDeviceFeatures2*>(head);
            f2.features.shaderStorageImageWriteWithoutFormat = VK_TRUE;
            ci.pNext = &f2;
            enabled = true;
        }
    } else if (ci.pEnabledFeatures) {
        legacy = *ci.pEnabledFeatures;
        legacy.shaderStorageImageWriteWithoutFormat = VK_TRUE;
        ci.pEnabledFeatures = &legacy;
        enabled = true;
    }
    if (!enabled) {
        std::fprintf(stderr,
            "[BS4_FSR31] unsupported device-create feature chain, unchanged\\n");
        return real_create_device(physical, requested, allocator, output);
    }
    VkResult result = real_create_device(physical, &ci, allocator, output);
    if (result == VK_SUCCESS && output && *output) {
        fsr31_tracked_physical.store(physical, std::memory_order_release);
        std::fprintf(stderr,"[BS4_FSR31] intercepted vkCreateDevice physical=%p device=%p\\n",
                     reinterpret_cast<void*>(physical),
                     reinterpret_cast<void*>(*output));
    }
    fsr31_storage_feature_enabled.store(result == VK_SUCCESS);
    std::fprintf(stderr, "[BS4_FSR31] vkCreateDevice feature enable result=%d\\n",
                 int(result));
    return result;
}
}

extern "C" PFN_vkVoidFunction bs4_fsr31_wrap_vulkan_proc(
    const char* name, PFN_vkVoidFunction proc);
extern "C" VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetDeviceProcAddr(VkDevice, const char*);
extern "C" VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vkGetInstanceProcAddr(
        VkInstance instance, const char* name) {
    const auto original = real_gipa();
    if (!original || !name) return nullptr;
    const auto out = original(instance, name);
    if (instance && fsr31_requested())
        fsr31_tracked_instance.store(instance, std::memory_order_release);
    if (std::strcmp(name, "vkCreateInstance") == 0 && out && fsr31_requested()) {
        real_create_instance = reinterpret_cast<PFN_vkCreateInstance>(out);
        return reinterpret_cast<PFN_vkVoidFunction>(&fsr31_create_instance);
    }
    if (std::strcmp(name, "vkGetDeviceProcAddr") == 0 && out && fsr31_requested())
        return reinterpret_cast<PFN_vkVoidFunction>(&vkGetDeviceProcAddr);
    if (std::strcmp(name, "vkCreateDevice") == 0 && out && fsr31_requested()) {
        real_create_device = reinterpret_cast<PFN_vkCreateDevice>(out);
        return reinterpret_cast<PFN_vkVoidFunction>(&fsr31_create_device);
    }
    return fsr31_requested() ? bs4_fsr31_wrap_vulkan_proc(name, out) : out;
}

extern "C" void* dlsym(void* handle, const char* symbol) {
    auto resolve = real_dlsym();
    if (!resolve) return nullptr;
    if (symbol && std::strcmp(symbol, "vkGetInstanceProcAddr") == 0 &&
        fsr31_requested()) {
        return reinterpret_cast<void*>(&vkGetInstanceProcAddr);
    }
    return resolve(handle, symbol);
}
