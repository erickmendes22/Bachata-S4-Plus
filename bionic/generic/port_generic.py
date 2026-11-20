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

    cmake = upstream / "CMakeLists.txt"
    replace(cmake, "add_executable(shadps4\n",
            "add_library(shadps4 SHARED\n")
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
        'target_include_directories(shadps4 PRIVATE "' + str(overlay) + '")\n'
        'target_link_libraries(shadps4 PRIVATE android log)\n'
        'set_target_properties(shadps4 PROPERTIES OUTPUT_NAME "bachata_bionic_core")\n'
        + anchor, 1)
    cmake.write_text(source, encoding="utf-8")

    for file in ("android_surface.h", "android_window.cpp", "android_native_core.cpp"):
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
