#!/usr/bin/env python3
"""Wire the actual Android native-window WSI into the shadPS4 0.21.1 renderer.

Only touch Android-specific branches; desktop WSI and the upstream Vulkan
renderer remain intact. Refuse unexpected source layouts instead of silently
claiming that the modern ARM64 port can present frames.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    data = path.read_text()
    hits = data.count(old)
    if hits != 1:
        raise RuntimeError(f"{path}: expected one Android WSI anchor, got {hits}: {old[:100]!r}")
    path.write_text(data.replace(old, new, 1))


def integrate(source: Path) -> None:
    header = source / "src/sdl_window.h"
    platform = source / "src/video_core/renderer_vulkan/vk_platform.cpp"

    hdr = header.read_text()
    if "WindowSystemType::Android" in hdr:
        raise RuntimeError("Android window type must be an enum entry, not a qualified use")
    if "    Android," not in hdr:
        replace_once(header, "    Headless,\n", "    Headless,\n    Android,\n")

    data = platform.read_text()
    # The NDK defines __ANDROID__. CMake's ANDROID is not necessarily a C++ macro.
    # Without this, the compiler can select Linux X11/Wayland WSI accidentally.
    legacy_selector = "#if defined(ANDROID)\\n#define VK_USE_PLATFORM_ANDROID_KHR"
    if legacy_selector in data:
        replace_once(platform, legacy_selector,
                     "#if defined(__ANDROID__) || defined(ANDROID)\\n#define VK_USE_PLATFORM_ANDROID_KHR")
        data = platform.read_text()
    if "#if defined(__ANDROID__) || defined(ANDROID)\\n#define VK_USE_PLATFORM_ANDROID_KHR" not in data:
        raise RuntimeError("Android Vulkan macro selector is not NDK compatible")
    if "#define VK_USE_PLATFORM_ANDROID_KHR" not in data:
        raise RuntimeError("Modern core lacks Android Vulkan platform feature macro")

    if "#include <android/native_window.h>" not in data:
        replace_once(platform, "#include <vector>\n",
                     "#if defined(__ANDROID__)\n#include <android/native_window.h>\n#endif\n#include <vector>\n")
        data = platform.read_text()

    if "vk::AndroidSurfaceCreateInfoKHR" not in data:
        location = data.index("vk::SurfaceKHR CreateSurface(")
        branch = data.index("#if defined(VK_USE_PLATFORM_WIN32_KHR)", location)
        if "WindowSystemType::Android" in data[location:branch]:
            raise RuntimeError("Unexpected partially integrated Android surface")
        insertion = """#if defined(VK_USE_PLATFORM_ANDROID_KHR)
    if (window_info.type == Frontend::WindowSystemType::Android) {
        const vk::AndroidSurfaceCreateInfoKHR android_ci = {
            .window = static_cast<ANativeWindow*>(window_info.render_surface),
        };
        if (android_ci.window == nullptr ||
            instance.createAndroidSurfaceKHR(&android_ci, nullptr, &surface) !=
                vk::Result::eSuccess) {
            LOG_CRITICAL(Render_Vulkan, "BIONIC_021_ANDROID_SURFACE_FAILED");
            UNREACHABLE();
        }
        LOG_INFO(Render_Vulkan, "BIONIC_021_ANDROID_SURFACE_READY");
    }
#elif defined(VK_USE_PLATFORM_WIN32_KHR)"""
        data = data[:branch] + data[branch:].replace(
            "#if defined(VK_USE_PLATFORM_WIN32_KHR)", insertion, 1)
        platform.write_text(data)

    data = platform.read_text()
    start = data.index("std::vector<const char*> GetInstanceExtensions(")
    end = data.index("std::vector<const char*> GetInstanceLayers(", start)
    extension_body = data[start:end]
    android_case = """#if defined(VK_USE_PLATFORM_ANDROID_KHR)
    case Frontend::WindowSystemType::Android:
        extensions.push_back(VK_KHR_ANDROID_SURFACE_EXTENSION_NAME);
        break;
#elif defined(VK_USE_PLATFORM_WIN32_KHR)"""
    if "case Frontend::WindowSystemType::Android:" not in extension_body:
        old = """    case Frontend::WindowSystemType::Headless:
        break;
#if defined(VK_USE_PLATFORM_WIN32_KHR)"""
        new = """    case Frontend::WindowSystemType::Headless:
        break;
""" + android_case
        if extension_body.count(old) != 1:
            raise RuntimeError("0.21.1 extension switch changed; refusing unreviewed WSI patch")
        data = data[:start] + extension_body.replace(old, new, 1) + data[end:]
        platform.write_text(data)

    data = platform.read_text()
    assert "vk::AndroidSurfaceCreateInfoKHR" in data
    assert "VK_KHR_ANDROID_SURFACE_EXTENSION_NAME" in data
    assert "BIONIC_021_ANDROID_SURFACE_READY" in data
    assert "WindowSystemType::Android" in data
    print("BIONIC_021_ANDROID_WSI_SOURCE_INTEGRATED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    integrate(ap.parse_args().source)
