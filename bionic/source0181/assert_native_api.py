#!/usr/bin/env python3
"""Cheap structural C++ contract checks before ~2200 Android build units.

This does not replace C++ compilation. It prevents the exact class of
0.16.1 / 0.18.1 source-mixing regressions observed in the full NDK logs.
"""
from __future__ import annotations
import argparse
import ast
import re
from pathlib import Path

def audit(root: Path) -> None:
    # Duplicate dict keys silently override old checks. That hid the prior
    # vk_presenter assertions, so reject duplicate keys in the audit itself.
    tree = ast.parse(Path(__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            if len(keys) != len(set(keys)):
                raise SystemExit("DUPLICATE_ABI_AUDIT_DICTIONARY_KEY")
    required = {
        "src/input/controller.cpp": ("GameController::ApplyRemoteState(", "PushStateLocked(timestamp);"),
        "src/input/controller.h": ("void ApplyRemoteState(", "void PollState();"),
        "src/common/ring_buffer_queue.h": ("void Clear()",),
        "src/core/debug_state.h": ("void IncDrawCall()", "void IncDispatch()",
                                   "GetDrawCallsAvg()", "GetDispatchesAvg()"),
        "src/core/libraries/kernel/file_system.cpp": ("deci_tty_device.h",),
        "src/core/libraries/kernel/file_system.h": (
            "s64 PS4_SYSV_ABI posix_read(", "s32 PS4_SYSV_ABI posix_unlink(",
            "s32 PS4_SYSV_ABI posix_rename(", "s64 PS4_SYSV_ABI sceKernelLseek(",
            "s32 PS4_SYSV_ABI sceKernelFstat("),
        "src/core/libraries/kernel/threads/semaphore.cpp": (".Insert(", ".IsAllocated(", ".Erase("),
        "src/core/libraries/libs.cpp": ("ForceRegisterLib(sym);",
                                        "BIONIC_BOOT_STAGE=LIBC_HLE_END",
                                        "libSceNpCommerce.sprx"),
        "src/core/file_sys/fs.h": ("std::unique_ptr<IFile> handle;", "GetHostFile() const"),
        "src/core/memory.cpp": ("file->GetHostFile()", "file->GetSize()"),
        "src/core/libraries/videoout/driver.cpp": ("BIONIC_PRESENT_IDLE_SKIP",
                                                    "PrepareBlankFrame(true)"),
        "src/core/libraries/videoout/driver.h": ("bool SubmitFlip(VideoOutPort*",),
        "src/core/libraries/videoout/video_out.cpp": (
            "driver->SubmitFlip(port, buf_id, flip_arg, true);",),
        "src/core/libraries/pad/pad.h": ("ORBIS_PAD_MAX_DATA_NUM",),
        "src/core/libraries/gnmdriver/gnmdriver.cpp": (
            "VideoOut::sceVideoOutSubmitEopFlip(vo_handle, buf_idx, flip_mode,",),
        "src/video_core/renderer_vulkan/vk_presenter.cpp": (
            "#include <png.h>", "png_write_image(",
            "GetSplashPath()", "DecodePngFile(splash_path)"),
        "src/core/libraries/sysmodule/sysmodule_internal.h": (
            "g_need_scelibc", "g_need_fios2"),
        "src/video_core/renderer_vulkan/vk_instance.h": ("IsShaderSubgroupClockSupported",
                                                         "IsMultisampleStorageImageSupported",
                                                         "IsImageViewMinLodSupported",
                                                         "GetMaxSamplerAllocationCount"),
        "src/video_core/renderer_vulkan/vk_instance.cpp": ("BIONIC_VULKAN_DEVICE",),
        "src/video_core/renderer_vulkan/vk_platform.cpp": (
            "BIONIC_VULKAN_CUSTOM_BRIDGE_READY", "BIONIC_VULKAN_CUSTOM_REQUIRED"),
        "src/common/elf_info.h": ("GetNpCommIds()", "GetSplashPath()"),
        "src/imgui/imgui_texture.h": ("DecodePngFile(",),
        "src/common/logging/log.cpp": ("void Terminate() {", "std::current_exception()",
                                      "std::quick_exit(", "TERMINATE_WITH_UNKNOWN_EXCEPTION"),
        "src/core/memory.h": ("System = 9,",),
        "src/core/libraries/kernel/memory.h": (
            "s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory(",),
        "src/core/libraries/kernel/memory.cpp": (
            "s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory(",
            "Core::VMAType::System",
            'LIB_FUNCTION("kc+LEEIYakc", "libkernel", 1, "libkernel", sceKernelMapNamedSystemFlexibleMemory);'),
        "src/common/cstring.h": ("#include <algorithm>",),
        "src/core/file_format/psf.cpp": ("#include <algorithm>",),
        "src/main.cpp": ("BachataSaf::Configure", "controller->ApplyRemoteState(",
                         "controller->PollState()"),
        "src/emulator.cpp": ("BIONIC_BOOT_STAGE=GUEST_LIBC_OBJECTS_END",
                              "EmulatorSettings.IsLogAppend()"),
        "src/imgui/big_picture/big_picture.cpp": ("emulator->Restart(runEbootPath)",),
        "src/core/signals.cpp": ("BIONIC_HOST_FAULT_MODULE",),
    }
    forbidden = {
        "src/core/libraries/libs.cpp": ('"core/libraries/np/np_commerce.h"',),
        "src/core/libraries/kernel/file_system.cpp": ("deci_tty6_device.h",),
        "src/core/memory.cpp": ("file->f.",),
        "src/core/libraries/kernel/threads/semaphore.cpp": (
            "PthreadCancelInterrupt(", "critical_count.fetch_add("),
        "src/core/libraries/videoout/driver.cpp": ("liverpool->EnqueueCommand(",),
        "src/core/libraries/gnmdriver/gnmdriver.cpp": ("next_flip_token", "flip_token"),
        "src/video_core/renderer_vulkan/vk_presenter.cpp": (
            "#include <stb_image_write.h>", "stbi_write_png_to_func(",
            "GetSplashData(", '"video_core/amdgpu/stall_log.h"'),
        "src/core/libraries/videoout/video_out.cpp": ("FlipLabelTracker::kInvalidGeneration",),
        "src/core/libraries/videoout/driver.h": ("lock_generation",),
        "src/video_core/renderer_vulkan/vk_instance.cpp": ('"video_core/renderer_vulkan/legacy_vertex_attributes.h"',),
        "src/main.cpp": ("Common::Log::g_should_append", "controller->Gyro(0);",
                         "controller->Acceleration(0);", "controller->accel_poll_rate"),
        "src/sdl_window.cpp": ("controller->UpdateAxisSmoothing()", "controller->Gyro(0);"),
    }
    issues = []
    for rel, markers in required.items():
        path = root / rel
        if not path.is_file():
            issues.append(f"{rel}: absent")
            continue
        txt = path.read_text()
        issues.extend(f"{rel}: expected {mark!r}" for mark in markers if mark not in txt)
    for rel, markers in forbidden.items():
        path = root / rel
        if not path.is_file():
            continue
        txt = path.read_text()
        issues.extend(f"{rel}: obsolete {mark!r}" for mark in markers if mark in txt)
    # Catch CMake duplicate definitions *before* initializing NDK/FEX/cache.
    cmake = (root / "CMakeLists.txt").read_text()
    if re.search(r"(?m)^\\s*src/sdl_window\\.cpp\\s*$", cmake):
        issues.append("CMakeLists.txt: desktop SDL source conflicts with android_window.cpp")
    if cmake.count("${BACHATA_ANDROID_WINDOW_SOURCE}") < 2:
        issues.append("CMakeLists.txt: Android SDL source not included in native target")
    if 'set(BACHATA_ANDROID_WINDOW_SOURCE "' not in cmake:
        issues.append("CMakeLists.txt: Android frontend implementation not registered")
    # Catch duplicate/missing method definitions that would otherwise fail
    # only at final ELF link after 400 compilation units.
    for rel, signature in (
        ("src/common/logging/log.cpp", "void Terminate() {"),
        ("src/core/libraries/kernel/memory.cpp",
         "s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory("),
    ):
        count = (root / rel).read_text().count(signature)
        if count != 1:
            issues.append(f"{rel}: expected one actual definition {signature}, got {count}")
    if issues:
        raise SystemExit("SOURCE_ABI_REGRESSIONS_FOUND:\n" + "\n".join(issues))
    print("SHADPS4_0181_ANDROID_FEX_INTERFACE_CONTRACTS_PASS",
          sum(map(len, required.values())) + sum(map(len, forbidden.values())))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    audit(parser.parse_args().source)
