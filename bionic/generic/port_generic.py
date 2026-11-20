#!/usr/bin/env python3
"""Apply the Android/Bionic WSI/JNI frontend to a pinned *generic* shadPS4 source.

This is not a proprietary source reconstruction and does not use Uncharted's
BBPROBE5 loader. Assertions fail closed if upstream changes an integration site.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def replace(path: Path, old: str, new: str, count: int = 1) -> None:
    source = path.read_text(encoding="utf-8")
    actual = source.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} anchor(s), got {actual}: {old[:90]!r}")
    path.write_text(source.replace(old, new), encoding="utf-8")


def apply(upstream: Path, overlay: Path) -> None:
    if not (upstream / "src/core/fex/fex_guest_engine.cpp").is_file():
        raise RuntimeError("generic shadPS4 with FEX guest engine required; not a game port")
    if not (upstream / "src/core/linker.cpp").is_file():
        raise RuntimeError("generic PS4 linker missing")

    window_h = upstream / "src/sdl_window.h"
    replace(window_h, "    Headless,\n    Windows,",
            "    Headless,\n    Android,\n    Windows,")

    platform = upstream / "src/video_core/renderer_vulkan/vk_platform.cpp"
    replace(
        platform,
        "#if defined(VK_USE_PLATFORM_WIN32_KHR)\n"
        "    if (window_info.type == Frontend::WindowSystemType::Windows) {",
        "#if defined(VK_USE_PLATFORM_ANDROID_KHR)\n"
        "    if (window_info.type == Frontend::WindowSystemType::Android) {\n"
        "        const vk::AndroidSurfaceCreateInfoKHR info{\n"
        "            .window = static_cast<ANativeWindow*>(window_info.render_surface),\n"
        "        };\n"
        "        if (instance.createAndroidSurfaceKHR(&info, nullptr, &surface) !=\n"
        "            vk::Result::eSuccess) {\n"
        "            LOG_CRITICAL(Render_Vulkan, \"Failed to create Android Vulkan surface\");\n"
        "            UNREACHABLE();\n"
        "        }\n"
        "    }\n"
        "#elif defined(VK_USE_PLATFORM_WIN32_KHR)\n"
        "    if (window_info.type == Frontend::WindowSystemType::Windows) {",
    )
    replace(
        platform,
        "    case Frontend::WindowSystemType::Headless:\n"
        "        break;\n"
        "#if defined(VK_USE_PLATFORM_WIN32_KHR)",
        "    case Frontend::WindowSystemType::Headless:\n"
        "        break;\n"
        "#if defined(VK_USE_PLATFORM_ANDROID_KHR)\n"
        "    case Frontend::WindowSystemType::Android:\n"
        "        extensions.push_back(VK_KHR_ANDROID_SURFACE_EXTENSION_NAME);\n"
        "        break;\n"
        "#elif defined(VK_USE_PLATFORM_WIN32_KHR)",
    )
    # The Android frontend's SDL_VULKAN_LIBRARY is an optional *candidate*,
    # not a guarantee of a Vulkan loader. In particular, a Mesa/Turnip ICD
    # normally exports vk_icdGetInstanceProcAddr while Android's system
    # loader exports vkGetInstanceProcAddr. The previous implementation
    # unconditionally dlsym'ed only the latter, then asserted at boot.
    # Resolve both APIs, log rejected candidates, and retry the Android
    # system loader so a missing/inaccessible custom ICD does not prevent
    # the app from starting the native renderer.
    replace(
        platform,
        "#include <vector>\n",
        "#include <cstdlib>\n#include <dlfcn.h>\n#include <vector>\n",
    )
    replace(
        platform,
        '    static vk::detail::DynamicLoader dl;\n'
        '    VULKAN_HPP_DEFAULT_DISPATCHER.init(\n'
        '        dl.getProcAddress<PFN_vkGetInstanceProcAddr>("vkGetInstanceProcAddr"));',
        '#if defined(__ANDROID__)\n'
        '    static PFN_vkGetInstanceProcAddr get_instance_proc = []() -> PFN_vkGetInstanceProcAddr {\n'
        '        const char* requested = std::getenv("SDL_VULKAN_LIBRARY");\n'
        '        const char* candidates[] = {requested, "libvulkan.so", "/system/lib64/libvulkan.so"};\n'
        '        for (const char* path : candidates) {\n'
        '            if (!path || !path[0]) continue;\n'
        '            void* handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);\n'
        '            if (!handle) {\n'
        '                const char* error = dlerror();\n'
        '                LOG_WARNING(Render_Vulkan, "BIONIC_VULKAN_LOADER_OPEN_FAIL path={} error={}",\n'
        '                            path, error ? error : "unknown");\n'
        '                continue;\n'
        '            }\n'
        '            auto proc = reinterpret_cast<PFN_vkGetInstanceProcAddr>(\n'
        '                dlsym(handle, "vkGetInstanceProcAddr"));\n'
        '            const char* api = "vkGetInstanceProcAddr";\n'
        '            if (!proc) {\n'
        '                proc = reinterpret_cast<PFN_vkGetInstanceProcAddr>(\n'
        '                    dlsym(handle, "vk_icdGetInstanceProcAddr"));\n'
        '                api = "vk_icdGetInstanceProcAddr";\n'
        '            }\n'
        '            if (proc) {\n'
        '                LOG_INFO(Render_Vulkan, "BIONIC_VULKAN_LOADER_READY path={} api={} fallback={}",\n'
        '                         path, api, requested && std::strcmp(path, requested) != 0);\n'
        '                // Retain handle: Vulkan-Hpp dispatcher stores pointers into this ELF.\n'
        '                return proc;\n'
        '            }\n'
        '            LOG_WARNING(Render_Vulkan,\n'
        '                        "BIONIC_VULKAN_LOADER_EXPORT_MISSING path={} (both APIs)", path);\n'
        '            dlclose(handle);\n'
        '        }\n'
        '        LOG_CRITICAL(Render_Vulkan, "No usable Android Vulkan loader or ICD found");\n'
        '        return nullptr;\n'
        '    }();\n'
        '#else\n'
        '    static vk::detail::DynamicLoader dl;\n'
        '    const auto get_instance_proc =\n'
        '        dl.getProcAddress<PFN_vkGetInstanceProcAddr>("vkGetInstanceProcAddr");\n'
        '#endif\n'
        '    ASSERT_MSG(get_instance_proc != nullptr,\n'
        '               "Vulkan loader missing vkGetInstanceProcAddr");\n'
        '    VULKAN_HPP_DEFAULT_DISPATCHER.init(get_instance_proc);',
    )

    # The Android 0.2.7 frontend sends an independent SAF broker session
    # alongside its BACHATA/1 control socket. The upstream generic CLI did
    # not recognize these flags. CLI11 preserves them as extras, which hit
    # main.cpp's "unhandled flags" guard before any ELF file can be loaded.
    # Keep the two values separate from the control socket; do not interpret
    # the abstract SAF socket name as a filesystem pathname.
    main = upstream / "src/main.cpp"
    replace(
        main,
        "    std::optional<std::filesystem::path> patchSessionPath;\n",
        "    std::optional<std::filesystem::path> patchSessionPath;\n"
        "    std::optional<std::string> bachataSafSocket;\n"
        "    std::optional<std::string> bachataSafToken;\n",
    )
    replace(
        main,
        '    app.add_option("--patch-session", patchSessionPath,\n'
        '                   "Managed patch launch session file (frozen snapshot staged by Android)");\n',
        '    app.add_option("--patch-session", patchSessionPath,\n'
        '                   "Managed patch launch session file (frozen snapshot staged by Android)");\n'
        '    app.add_option("--bachata-saf-socket", bachataSafSocket,\n'
        '                   "Android SAF game-content broker abstract socket name");\n'
        '    app.add_option("--bachata-saf-token", bachataSafToken,\n'
        '                   "Android SAF game-content broker per-session token");\n',
    )
    # Do not silently accept an unmatched SAF session. Both values are
    # required together; the native override-root path remains the ordinary
    # host file path until the separate SAF file transport is implemented.
    replace(
        main,
        '    if (bachataStorageRoot.has_value()) {\n',
        '    if (bachataSafSocket.has_value() != bachataSafToken.has_value()) {\n'
        '        std::cerr << "Both --bachata-saf-socket and --bachata-saf-token are required\\n";\n'
        '        runtime_client.SendError("CONTENT_INVALID");\n'
        '        runtime_client.SendStopped(1);\n'
        '        return 1;\n'
        '    }\n'
        '    if (bachataStorageRoot.has_value()) {\n',
    )
    # The frontend deliberately uses -g eboot.bin rather than an absolute
    # path; its --override-root is the actual selected game directory.
    # Resolve this before the generic desktop 'find game ID' fallback, which
    # would otherwise search unrelated install folders from the app cwd.
    replace(
        main,
        '    std::filesystem::path ebootPath(*gamePath);\n'
        '    if (!std::filesystem::exists(ebootPath)) {\n',
        '    std::filesystem::path ebootPath(*gamePath);\n'
        '#ifdef ENABLE_BACHATA_RUNTIME\n'
        '    if (!ebootPath.is_absolute() && overrideRoot.has_value()) {\n'
        '        const auto managedEboot = *overrideRoot / ebootPath;\n'
        '        if (std::filesystem::is_regular_file(managedEboot)) {\n'
        '            ebootPath = managedEboot;\n'
        '        }\n'
        '    }\n'
        '#endif\n'
        '    if (!std::filesystem::exists(ebootPath)) {\n',
    )

    replace(upstream / "src/main.cpp",
            "int main(int argc, char* argv[]) {",
            "int BachataCoreMain(int argc, char* argv[]) {")

    # Critical: an emulator linked inside a Java process must not quick_exit(0)
    # after the window closes; allow JNI to release its ANativeWindow reference.
    replace(
        upstream / "src/emulator.cpp",
        "    std::quick_exit(0);\n}\n\nvoid Emulator::Restart(",
        "#ifdef __ANDROID__\n"
        "    Shutdown();\n"
        "    return;\n"
        "#else\n"
        "    std::quick_exit(0);\n"
        "#endif\n"
        "}\n\nvoid Emulator::Restart(",
    )

    # Bionic does not expose the glibc sigisemptyset helper, and Android's
    # pthread_t is integer-valued rather than the glibc pointer typedef.
    # Preserve desktop behavior and scan the actual POSIX mask on Android.
    exception = upstream / "src/core/libraries/kernel/threads/exception.cpp"
    replace(
        exception,
        "        if (!sigisemptyset(&native_oact.sa_mask)) {\n",
        "#if defined(__ANDROID__)\n"
        "        bool has_masked_signals = false;\n"
        "        for (int native_signum = 1; native_signum <= SIGRTMAX; ++native_signum) {\n"
        "            if (sigismember(&native_oact.sa_mask, native_signum) == 1) {\n"
        "                has_masked_signals = true;\n"
        "                break;\n"
        "            }\n"
        "        }\n"
        "        if (has_masked_signals) {\n"
        "#else\n"
        "        if (!sigisemptyset(&native_oact.sa_mask)) {\n"
        "#endif\n",
    )
    replace(
        exception,
        "    const auto pthr = reinterpret_cast<pthread_t>(thread->native_thr.GetHandle());\n",
        "#if defined(__ANDROID__)\n"
        "    const auto pthr = static_cast<pthread_t>(thread->native_thr.GetHandle());\n"
        "#else\n"
        "    const auto pthr = reinterpret_cast<pthread_t>(thread->native_thr.GetHandle());\n"
        "#endif\n",
    )

    # libuuid is a glibc/Linux dependency; Android Bionic provides a secure
    # arc4random_buf() implementation. Produce RFC 4122 UUIDv4 bytes without
    # linking libuuid, preserving desktop behavior and the PS4's 16-byte ABI.
    kernel = upstream / "src/core/libraries/kernel/kernel.cpp"
    replace(
        kernel,
        "#ifdef _WIN64\n"
        "#include <Rpc.h>\n"
        "#else\n"
        "#include <uuid/uuid.h>\n"
        "#endif\n",
        "#ifdef _WIN64\n"
        "#include <Rpc.h>\n"
        "#elif defined(__ANDROID__)\n"
        "#include <stdlib.h>\n"
        "#else\n"
        "#include <uuid/uuid.h>\n"
        "#endif\n",
    )
    replace(
        kernel,
        "    if (UuidCreate(&uuid) != RPC_S_OK) {\n"
        "        return ORBIS_KERNEL_ERROR_EFAULT;\n"
        "    }\n"
        "#else\n"
        "    uuid_t uuid;\n"
        "    uuid_generate(uuid);\n"
        "#endif\n",
        "    if (UuidCreate(&uuid) != RPC_S_OK) {\n"
        "        return ORBIS_KERNEL_ERROR_EFAULT;\n"
        "    }\n"
        "#elif defined(__ANDROID__)\n"
        "    u8 uuid[sizeof(OrbisKernelUuid)];\n"
        "    arc4random_buf(uuid, sizeof(uuid));\n"
        "    uuid[6] = (uuid[6] & 0x0f) | 0x40; // RFC 4122 version 4\n"
        "    uuid[8] = (uuid[8] & 0x3f) | 0x80; // RFC 4122 variant\n"
        "#else\n"
        "    uuid_t uuid;\n"
        "    uuid_generate(uuid);\n"
        "#endif\n",
    )

    # Android NDK libc++ has no std::chrono::current_zone. Bionic's
    # localtime_r provides the UTC offset for the requested game timestamp.
    time_file = upstream / "src/core/libraries/kernel/time.cpp"
    replace(
        time_file,
        "#else\n"
        "#if defined(__APPLE__) || defined(__FreeBSD__)\n"
        "    // std::chrono::current_zone() not available yet.\n",
        "#elif defined(__ANDROID__)\n"
        "    struct tm local_tm {};\n"
        "    if (local_time == nullptr || localtime_r(&time, &local_tm) == nullptr) {\n"
        "        return ORBIS_KERNEL_ERROR_EINVAL;\n"
        "    }\n"
        "    const s64 utc_offset = static_cast<s64>(local_tm.tm_gmtoff);\n"
        "    const u64 daylight_seconds = local_tm.tm_isdst > 0 ? 3600ULL : 0ULL;\n"
        "    *local_time = static_cast<time_t>(static_cast<s64>(time) + utc_offset);\n"
        "    if (st != nullptr) {\n"
        "        st->t = time;\n"
        "        st->west_sec = static_cast<u32>(utc_offset);\n"
        "        st->dst_sec = static_cast<u32>(daylight_seconds);\n"
        "    }\n"
        "    if (dst_sec != nullptr) {\n"
        "        *dst_sec = daylight_seconds;\n"
        "    }\n"
        "#else\n"
        "#if defined(__APPLE__) || defined(__FreeBSD__)\n"
        "    // std::chrono::current_zone() not available yet.\n",
    )

    # epoll_pwait2 is unavailable to NDK API 33. Avoid truncating a positive
    # sub-millisecond guest wait to zero: epoll_pwait accepts millisecond waits.
    network = upstream / "src/core/libraries/network/net.cpp"
    replace(
        network,
        "    if (should_wait) {\n"
        "#ifdef __linux__\n"
        "        const timespec epoll_timeout",
        "    if (should_wait) {\n"
        "#if defined(__ANDROID__)\n"
        "        const int timeout_ms = timeout < 0 ? -1 :\n"
        "            timeout / 1000 + (timeout % 1000 != 0);\n"
        "        result = epoll_pwait(epoll->epoll_fd, native_events.data(), maxevents,\n"
        "                             timeout_ms, nullptr);\n"
        "#elif defined(__linux__)\n"
        "        const timespec epoll_timeout",
    )

    # Android defines __unix__ but does NOT define the glibc adaptive mutex
    # initializer. The fallback Common::SpinLock must actually be included,
    # or buffer/page tracker templates fail to instantiate (cascading errors).
    region = upstream / "src/video_core/buffer_cache/region_manager.h"
    replace(
        region,
        '#include "common/adaptive_mutex.h"\n'
        "#else\n"
        '#include "common/spin_lock.h"\n'
        "#endif\n"
        '#include "common/debug.h"\n',
        '#include "common/adaptive_mutex.h"\n'
        "#else\n"
        '#include "common/spin_lock.h"\n'
        "#endif\n"
        "#ifdef __ANDROID__\n"
        '#include "common/spin_lock.h"\n'
        "#endif\n"
        '#include "common/debug.h"\n',
    )
    page_manager = upstream / "src/video_core/page_manager.cpp"
    replace(
        page_manager,
        '#include "common/range_lock.h"\n',
        '#include "common/range_lock.h"\n'
        "#ifdef __ANDROID__\n"
        '#include "common/spin_lock.h"\n'
        "#endif\n",
    )

    # Do not link Linux ARM64 FFmpeg .a prebuilts into an Android/Bionic .so:
    # these archives contain non-PIC relocations and target the wrong libc.
    # Use the NDK-built, shared FFmpeg 9 libraries AND their matching headers.
    externals = upstream / "externals/CMakeLists.txt"
    replace(
        externals,
        "# FFmpeg\n"
        "if (NOT TARGET FFmpeg::ffmpeg)\n"
        "    add_subdirectory(ffmpeg-core)\n"
        "    add_library(FFmpeg::ffmpeg ALIAS ffmpeg)\n"
        "endif()\n",
        "# FFmpeg\n"
        "if (ANDROID)\n"
        "    if (NOT BACHATA_ANDROID_FFMPEG_PREFIX)\n"
        "        message(FATAL_ERROR \"Android FFmpeg shared-library prefix not provided\")\n"
        "    endif()\n"
        "    add_library(ffmpeg INTERFACE)\n"
        "    target_include_directories(ffmpeg INTERFACE \"${BACHATA_ANDROID_FFMPEG_PREFIX}/include\")\n"
        "    foreach(component avformat avcodec swscale avutil avfilter swresample)\n"
        "        set(ffmpeg_so \"${BACHATA_ANDROID_FFMPEG_PREFIX}/lib/lib${component}.so\")\n"
        "        if (NOT EXISTS \"${ffmpeg_so}\")\n"
        "            message(FATAL_ERROR \"Android FFmpeg library missing: ${ffmpeg_so}\")\n"
        "        endif()\n"
        "        target_link_libraries(ffmpeg INTERFACE \"${ffmpeg_so}\")\n"
        "    endforeach()\n"
        "    add_library(FFmpeg::ffmpeg ALIAS ffmpeg)\n"
        "elseif (NOT TARGET FFmpeg::ffmpeg)\n"
        "    add_subdirectory(ffmpeg-core)\n"
        "    add_library(FFmpeg::ffmpeg ALIAS ffmpeg)\n"
        "endif()\n",
    )


    # FEX must resolve the actual guest-imported "libc" namespace. The
    # shipped FEX libc __cxa_atexit alias was registered under
    # libSceLibcInternal only, leaving libc#libc imports on -ENOSYS.
    cxa = upstream / "src/core/libraries/libc_internal/libc_internal_cxa.cpp"
    replace(
        cxa,
        '    LIB_FUNCTION("tsvEmnenz48", "libSceLibcInternal", 1, "libSceLibcInternal",\n',
        '    LIB_FUNCTION("tsvEmnenz48", "libc", 1, "libc", fex_libc_cxa_atexit);\n'
        '    LIB_FUNCTION("tsvEmnenz48", "libSceLibcInternal", 1, "libSceLibcInternal",\n',
    )
    libc = upstream / "src/core/libraries/libc_internal/libc_internal.cpp"
    replace(
        libc,
        "namespace Libraries::LibcInternal {\n",
        "namespace Libraries::LibcInternal {\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "void RegisterFexLibcBootAliases(Core::Loader::SymbolsResolver* sym);\n"
        "#endif\n",
    )
    replace(
        libc,
        "    RegisterFexLibcCxaAliases(sym);\n",
        "    RegisterFexLibcCxaAliases(sym);\n"
        "    RegisterFexLibcBootAliases(sym);\n",
    )


    # The FEX x86 guest must see guest VMM addresses for all PS4 FILE
    # structures and buffers. Keep upstream desktop new/malloc untouched.
    io = upstream / "src/core/libraries/libc_internal/libc_internal_io.cpp"
    replace(io, "namespace Libraries::LibcInternal {\n",
        "namespace Libraries::LibcInternal {\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "void* FexLibcGuestAllocate(std::size_t size);\n"
        "void FexLibcGuestFree(void* pointer);\n"
        "#endif\n")
    replace(io, "            file = new OrbisFILE();\n",
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "            file = static_cast<OrbisFILE*>(FexLibcGuestAllocate(sizeof(OrbisFILE)));\n"
        "#else\n"
        "            file = new OrbisFILE();\n"
        "#endif\n")
    replace(io, "        free(file);\n",
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "        FexLibcGuestFree(file);\n"
        "#else\n"
        "        free(file);\n"
        "#endif\n")
    replace(io, "        u8* new_buffer = std::bit_cast<u8*>(std::malloc(0x10000));\n",
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "        u8* new_buffer = static_cast<u8*>(FexLibcGuestAllocate(0x10000));\n"
        "#else\n"
        "        u8* new_buffer = std::bit_cast<u8*>(std::malloc(0x10000));\n"
        "#endif\n")
    replace(io, "            std::free(file->_Buf);\n",
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "            FexLibcGuestFree(file->_Buf);\n"
        "#else\n"
        "            std::free(file->_Buf);\n"
        "#endif\n")
    replace(io, "        *Kernel::__Error() = POSIX_ENOMEM;\n    }\n\n    // Preserve mode and index\n",
        "        *Kernel::__Error() = POSIX_ENOMEM;\n        return nullptr;\n    }\n\n    // Preserve mode and index\n")



    # Four synchronous boot checkpoints to attribute an early Android exit
    # to kernel HLE vs libc HLE vs guest VMM, not to the last buffered line.
    libs = upstream / "src/core/libraries/libs.cpp"
    replace(
        libs,
        '#include "common/arch.h"\n',
        '#include "common/arch.h"\n#include "common/logging/log.h"\n',
    )
    replace(
        libs,
        "    Libraries::Kernel::RegisterLib(sym);\n"
        "    Libraries::LibcInternal::ForceRegisterLib(sym);\n",
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    LOG_INFO(Lib_Kernel, \"BIONIC_BOOT_STAGE=KERNEL_HLE_BEGIN\");\n"
        "    Common::Log::Flush();\n"
        "#endif\n"
        "    Libraries::Kernel::RegisterLib(sym);\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    LOG_INFO(Lib_Kernel, \"BIONIC_BOOT_STAGE=KERNEL_HLE_END\");\n"
        "    Common::Log::Flush();\n"
        "#endif\n"
        "    Libraries::LibcInternal::ForceRegisterLib(sym);\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    LOG_INFO(Lib_Kernel, \"BIONIC_BOOT_STAGE=LIBC_HLE_END\");\n"
        "    Common::Log::Flush();\n"
        "#endif\n",
    )

    # Registration only fills the HLE resolver. Delay libc global guest-VMM
    # allocation until after registration and before the eboot's relocations.
    emulator = upstream / "src/emulator.cpp"
    replace(
        emulator,
        "#include \"core/libraries/kernel/kernel.h\"\n",
        "#include \"core/libraries/kernel/kernel.h\"\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "#include \"core/libraries/libc_internal/libc_internal.h\"\n"
        "#endif\n",
    )
    replace(
        upstream / "src/core/libraries/libc_internal/libc_internal.h",
        "void ForceRegisterLib(Core::Loader::SymbolsResolver* sym);\n",
        "void ForceRegisterLib(Core::Loader::SymbolsResolver* sym);\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "void RegisterFexLibcGuestObjects(Core::Loader::SymbolsResolver* sym);\n"
        "#endif\n",
    )
    replace(
        emulator,
        "    Libraries::InitHLELibs(&linker->GetHLESymbols());\n\n"
        "    // Load the module with the linker\n",
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    LOG_INFO(Loader, \"BIONIC_BOOT_STAGE=HLE_REGISTER_BEGIN\");\n"
        "    Common::Log::Flush();\n"
        "#endif\n"
        "    Libraries::InitHLELibs(&linker->GetHLESymbols());\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    LOG_INFO(Loader, \"BIONIC_BOOT_STAGE=HLE_REGISTER_END\");\n"
        "    Common::Log::Flush();\n"
        "    LOG_INFO(Loader, \"BIONIC_BOOT_STAGE=GUEST_LIBC_OBJECTS_BEGIN\");\n"
        "    Common::Log::Flush();\n"
        "    Libraries::LibcInternal::RegisterFexLibcGuestObjects(&linker->GetHLESymbols());\n"
        "    LOG_INFO(Loader, \"BIONIC_BOOT_STAGE=GUEST_LIBC_OBJECTS_END\");\n"
        "    Common::Log::Flush();\n"
        "#endif\n"
        "    // Load the module with the linker\n",
    )
    cmake = upstream / "CMakeLists.txt"
    replace(cmake, "add_executable(shadps4\n",
            "add_library(shadps4 SHARED\n")
    # pthread_* is provided by Bionic libc.so; -lpthread does not exist on Android.
    # Leave desktop Linux and other host platforms unchanged.
    replace(
        cmake,
        "    target_link_libraries(shadps4 PRIVATE ${FEXCORE_GUEST_CPU_LIBRARIES} pthread dl)\n",
        "    if (ANDROID)\n"
        "        target_link_libraries(shadps4 PRIVATE ${FEXCORE_GUEST_CPU_LIBRARIES} dl)\n"
        "    else()\n"
        "        target_link_libraries(shadps4 PRIVATE ${FEXCORE_GUEST_CPU_LIBRARIES} pthread dl)\n"
        "    endif()\n",
    )

    source = cmake.read_text(encoding="utf-8")
    n = source.count("src/sdl_window.cpp")
    if n < 1:
        raise RuntimeError("upstream shadPS4 SDL frontend source not found in CMake")
    source = source.replace("src/sdl_window.cpp", "${BACHATA_ANDROID_WINDOW_SOURCE}")
    # Keep the upstream's entire core/HLE/renderer source sets; replace only its
    # desktop frontend, and use the JNI entrypoint to invoke BachataCoreMain.
    anchor = "if(NOT ENABLE_TESTS)\n"
    if source.count(anchor) != 1:
        raise RuntimeError("unable to locate native shadPS4 build target")
    source = source.replace(anchor,
        'set(BACHATA_ANDROID_WINDOW_SOURCE "' + str(overlay / "android_window.cpp") + '")\n' +
        anchor, 1)
    anchor = "create_target_directory_groups(shadps4)"
    if source.count(anchor) != 1:
        raise RuntimeError("unable to attach Android native bridge to shadPS4")
    source = source.replace(anchor,
        'target_sources(shadps4 PRIVATE "' + str(overlay / "android_native_core.cpp") + '")\n'
        'target_sources(shadps4 PRIVATE "' + str(overlay / "android_libc_boot.cpp") + '")\n'
        'target_sources(shadps4 PRIVATE "' + str(overlay / "android_libc_compat.cpp") + '")\n'
        'target_include_directories(shadps4 PRIVATE "' + str(overlay) + '")\n'
        'target_link_libraries(shadps4 PRIVATE android log)\n'
        'set_target_properties(shadps4 PROPERTIES OUTPUT_NAME "bachata_bionic_core")\n'
        + anchor, 1)
    cmake.write_text(source, encoding="utf-8")

    for file in ("android_surface.h", "android_window.cpp", "android_native_core.cpp", "android_libc_boot.cpp", "android_libc_compat.cpp"):
        if not (overlay / file).is_file():
            raise RuntimeError(f"missing Android source: {file}")
    print("OK: generic shadPS4 core source patched for Android native surface and JNI")
    print("NOTE: source patch != verified full Bionic core build or playable APK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("upstream", type=Path)
    parser.add_argument("--overlay", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    apply(args.upstream.resolve(), args.overlay.resolve())


if __name__ == "__main__":
    main()
