#!/usr/bin/env python3
"""Reconcile actual 0.18.1 engine interfaces after the FEX/Bionic overlay.

Do NOT replace FEX memory, linker, runtime CLI, or Android Vulkan loader
with unrelated desktop implementations. Port their specific 0.18.1 APIs.
All replacements fail closed on unknown source versions; no silent stubs.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

UPSTREAM = "3912336fdfffbd5c99b59d92e997ea6ebd62216c"

# These implementation units have no Android-specific hooks and must match
# the 0.18.1 interfaces that consume them, not their 0.16.1 ancestors.
MATCH_0181 = (
    "src/common/ring_buffer_queue.h",
    "src/core/libraries/libs.cpp",
    "src/core/libraries/kernel/file_system.cpp",
    "src/core/libraries/kernel/threads/semaphore.cpp",
    "src/core/libraries/pad/pad.cpp",
    "src/core/libraries/sysmodule/sysmodule_internal.cpp",
    "src/video_core/renderer_vulkan/vk_instance.cpp",
    "src/video_core/renderer_vulkan/vk_instance.h",
    "src/video_core/renderer_vulkan/vk_presenter.cpp",
    "src/video_core/renderer_vulkan/vk_presenter.h",
    "src/core/libraries/videoout/driver.cpp",
)


def require_replace(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    found = text.count(old)
    if found != 1:
        raise RuntimeError(f"0.18.1 {label}: expected unique anchor, found {found}, file={path}")
    path.write_text(text.replace(old, new, 1))


def prefix_include(path: Path, header: str, label: str) -> None:
    source = path.read_text()
    if header in source:
        return
    if "#include " not in source:
        raise RuntimeError("Missing header placement in " + str(path))
    idx = source.index("#include ")
    path.write_text(source[:idx] + header + "\n" + source[idx:])


def restore(root: Path, path: str) -> None:
    p = root / path
    data = subprocess.check_output(
        ["git", "-C", str(root), "show", UPSTREAM + ":" + path])
    if not data:
        raise RuntimeError("Upstream source empty: " + path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def apply(root: Path) -> dict:
    result = {"sourceVersion": "0.18.1", "restoredMatchingImplementations": [],
              "fexAdaptersKept": ["linker", "address space", "memory manager",
                                  "Android Vulkan loader", "Bachata runtime CLI"],
              "portedInterfaces": []}
    for rel in MATCH_0181:
        restore(root, rel)
        result["restoredMatchingImplementations"].append(rel)

    # Modern Ime and pad APIs were incorrectly linked against old 0.16
    # implementations. Preserve their new headers and complete methods.
    subprocess.run(
        ["git", "-C", str(root), "restore", "--source", UPSTREAM,
         "--worktree", "--", "src/core/libraries/ime"],
        check=True)
    result["restoredMatchingImplementations"].append("src/core/libraries/ime/*")

    # The 0.18 version removes FEX's crucial boot markers when restoring libs.
    # Reattach all checkpoints to the REAL 0.18 registration implementation.
    libs = root / "src/core/libraries/libs.cpp"
    prefix_include(libs, '#include "common/logging/log.h"', "HLE log")
    # Upstream 0.18 uses a per-module registration table instead of the
    # old single "Kernel::RegisterLib; LibcInternal::ForceRegisterLib" block.
    # Keep that genuine upstream table, but run the FEX libc HLE registration
    # before the PS4 module loader so the guest gets its allocator exports.
    require_replace(
        libs,
        "        for (auto mod : ModulesToLoad) {\n",
        '#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n'
        '        LOG_INFO(Lib_Kernel, "BIONIC_BOOT_STAGE=KERNEL_HLE_BEGIN");\n'
        '        Common::Log::Flush();\n'
        '#endif\n'
        "        for (auto mod : ModulesToLoad) {\n",
        "0.18 HLE table startup")
    require_replace(
        libs,
        "        }\n    }\n}\n\n} // namespace Libraries\n",
        "        }\n"
        '#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n'
        '        LOG_INFO(Lib_Kernel, "BIONIC_BOOT_STAGE=KERNEL_HLE_END");\n'
        '        Common::Log::Flush();\n'
        '        Libraries::LibcInternal::ForceRegisterLib(sym);\n'
        '        LOG_INFO(Lib_Kernel, "BIONIC_BOOT_STAGE=LIBC_HLE_END");\n'
        '        Common::Log::Flush();\n'
        '#endif\n'
        "    }\n}\n\n} // namespace Libraries\n",
        "FEX libc exports after 0.18 HLE modules")
    prefix_include(libs, '#include "core/libraries/libc_internal/libc_internal.h"',
                   "FEX libc internal exports")
    result["portedInterfaces"].append("0.18.1 HLE registration + FEX boot diagnostics")

    # Modern input has timestamp-based State and PollState(), but the Android
    # controller socket must keep an atomic button/axes/touch snapshot.
    controller_h = root / "src/input/controller.h"
    require_replace(
        controller_h,
        "    void UpdateAcceleration(const float acceleration[3]);\n",
        "    void UpdateAcceleration(const float acceleration[3]);\n"
        "    void ApplyRemoteState(Libraries::Pad::OrbisPadButtonDataOffset buttons,\n"
        "                          const std::array<int, 6>& axes, bool touch_down,\n"
        "                          float touch_x, float touch_y);\n",
        "Bachata controller API")
    controller_cpp = root / "src/input/controller.cpp"
    require_replace(
        controller_cpp,
        "void GameController::PollState() {\n",
        """// Android BACHATA/1 input; one lock and one queued PS4 pad state per packet.
void GameController::ApplyRemoteState(OrbisPadButtonDataOffset buttons,
                                      const std::array<int, 6>& axes, bool touch_down,
                                      float touch_x, float touch_y) {
    std::lock_guard lock{m_state_mutex};
    const u64 timestamp = Libraries::Kernel::sceKernelGetProcessTime();
    if (!m_state.connected) {
        m_state.connected = true;
        ++m_state.connected_count;
        if (m_state.connected_count == 0) m_state.connected_count = 1;
    }
    m_state.buttonsState = buttons;
    for (int index = 0; index < 6; ++index) {
        m_state.OnAxis(static_cast<Input::Axis>(index), axes[index], timestamp, false);
    }
    const bool was_down = m_state.touchpad[0].state;
    if (touch_down && !was_down) {
        m_state.touchpad[0].ID = m_next_touch_id;
        m_next_touch_id = m_next_touch_id == 127 ? 1 : m_next_touch_id + 1;
        m_touch_down_timestamp = timestamp;
    } else if (!touch_down && was_down) {
        m_touch_down_timestamp = 0;
    }
    m_state.OnTouchpad(0, touch_down, touch_x, touch_y);
    PushStateLocked(timestamp);
}

void GameController::PollState() {
""", "atomic Android input bridge")
    result["portedInterfaces"].append("Android pad buttons, axes, touch and gyro on 0.18 State")

    # Old SDL polling functions referenced the removed Gyro/Acceleration and
    # UpdateAxisSmoothing methods. PollState() performs all three, plus
    # orientation integration, under the new m_state_mutex.
    sdl = root / "src/sdl_window.cpp"
    require_replace(
        sdl,
        "    controller->UpdateAxisSmoothing();\n"
        "    controller->Gyro(0);\n"
        "    controller->Acceleration(0);\n",
        "    controller->PollState();\n", "SDL gamepad timer")

    main = root / "src/main.cpp"
    require_replace(main,
        '    app.add_flag("--log-append", Common::Log::g_should_append);',
        '    bool bachata_append_log = false;\n'
        '    app.add_flag("--log-append", bachata_append_log);',
        "0.18 CLI log option")
    require_replace(main,
        "    Common::Log::g_should_append |= EmulatorSettings.IsLogAppend();",
        "    bachata_append_log |= EmulatorSettings.IsLogAppend();",
        "0.18 removed global logger flag")
    require_replace(main,
        '    LOG_INFO(Debug, "Run: {}", std::span(argv, argc));',
        '    LOG_INFO(Debug, "Run: {}", fmt::join(std::span(argv, argc), " "));',
        "fmt span formatting")
    prefix_include(main, "#include <fmt/ranges.h>", "main log ranges")
    require_replace(main,
        "        BigPictureMode::Launch(argv[0]);",
        "        BigPictureMode::Launch(argv[0], false);",
        "0.18 BigPicture API")
    require_replace(main,
        "                controller->Gyro(0);\n"
        "                controller->Acceleration(0);\n",
        "                controller->PollState();\n",
        "0.18 motion orientation integration")
    require_replace(main,
        "                if (controller->accel_poll_rate == 0.0f) {\n"
        "                    controller->accel_poll_rate = 60.0f;\n"
        "                }\n",
        "", "removed 0.16 sensor poll-rate field")
    result["portedInterfaces"].append("0.18 logging, CLI and SDL input callbacks")

    # 0.18 BigPicture Relaunch is absent from the FEX 0.16 host emulator.
    # Reuse its fully implemented Restart(eboot) implementation on desktop.
    # On Android the UI is controlled by Java, not a second native subprocess.
    big_picture = root / "src/imgui/big_picture/big_picture.cpp"
    require_replace(big_picture,
        '            emulator->Relaunch(\n'
        '                {"--log-append", "--game", Common::FS::PathToUTF8String(runEbootPath)});',
        '            emulator->Restart(runEbootPath);',
        "BigPicture restart on ARM64 FEX")

    # The host must retain its ARM64 mapping generation and SIGBUS tail fix;
    # only port accesses to the 0.18 IFile backend rather than .f (removed).
    mem = root / "src/core/memory.cpp"
    require_replace(mem,
        "    handle = file->f.GetFileMapping();\n\n"
        "    if (False(file->f.GetAccessMode() & Common::FS::FileAccessMode::Write) &&\n"
        "        False(file->f.GetAccessMode() & Common::FS::FileAccessMode::Append)) {",
        "    auto* host_file = file->GetHostFile();\n"
        "    if (!host_file) {\n"
        '        LOG_ERROR(Kernel_Vmm, "File backend cannot expose host mmap for fd {}", fd);\n'
        "        return ORBIS_KERNEL_ERROR_EBADF;\n"
        "    }\n"
        "    handle = host_file->GetFileMapping();\n\n"
        "    if (False(host_file->GetAccessMode() & Common::FS::FileAccessMode::Write) &&\n"
        "        False(host_file->GetAccessMode() & Common::FS::FileAccessMode::Append)) {",
        "0.18 IFile GetHostFile mmap")
    require_replace(mem, "    const u64 file_size = file->f.GetSize();",
                    "    const u64 file_size = file->GetSize();",
                    "0.18 IFile size")
    result["portedInterfaces"].append("FEX/Android mappings to modern IFile handles")

    # The pinned old FEX code used fmt::ptr with an obsolete transitive
    # include from fmt/core.h. New fmt requires its actual declarations.
    for relative in ("src/core/address_space.cpp", "src/core/module.cpp",
                     "src/core/signals.cpp"):
        prefix_include(root / relative, "#include <fmt/format.h>", "fmt::ptr")
    for relative in ("src/common/cstring.h", "src/core/file_format/psf.cpp"):
        prefix_include(root / relative, "#include <algorithm>", "C++23 ranges algorithms")
    result["portedInterfaces"].append("explicit fmt and C++ ranges includes")

    # Preserve FEX's old fields for loading games (splash_path), but supply
    # the new API used by upstream 0.18.1 Network Platform registration.
    elf = root / "src/common/elf_info.h"
    require_replace(elf, "    std::filesystem::path game_folder{};\n",
                    "    std::filesystem::path game_folder{};\n"
                    "    std::vector<std::string> npCommIds{};\n",
                    "npCommIds storage")
    require_replace(elf,
        "    [[nodiscard]] const std::map<s32, std::string>& GetTrophyIndexMap() const {\n",
        "    [[nodiscard]] const std::vector<std::string>& GetNpCommIds() const {\n"
        "        return npCommIds;\n"
        "    }\n\n"
        "    void SetNpCommIds(std::vector<std::string> ids) {\n"
        "        npCommIds = std::move(ids);\n"
        "    }\n\n"
        "    [[nodiscard]] const std::map<s32, std::string>& GetTrophyIndexMap() const {\n",
        "0.18 NP comm IDs")
    result["portedInterfaces"].append("0.18 NP comm IDs with old FEX game loader")

    # New logging requires an explicit append boolean. Keep old FEX startup
    # checkpoints and loader behavior; do not overwrite emulator.cpp with the
    # Linux/x86_64 desktop implementation.
    emulator = root / "src/emulator.cpp"
    require_replace(emulator,
        '    Common::Log::Switch((!id.empty() && EmulatorSettings.IsLogSeparate()) ? id + ".log"\n'
        '                                                                          : "shad_log.txt");',
        '    Common::Log::Switch((!id.empty() && EmulatorSettings.IsLogSeparate()) ? id + ".log"\n'
        '                                                                          : "shad_log.txt",\n'
        '                        EmulatorSettings.IsLogAppend());',
        "0.18 per-game log switch")
    result["portedInterfaces"].append("FEX emulator log API")

    # Keep a real 0.18 Vulkan subsystem: replacing only rasterizer and cache
    # while retaining 0.16 instance/presenter caused missing extensions,
    # removed legacy_vertex_attributes.h and missing stall_log.h.
    # vk_platform.cpp is deliberately NOT restored: it holds the Android
    # driver/AdrenoTools loader and strict custom Turnip selection.
    inst = root / "src/video_core/renderer_vulkan/vk_instance.cpp"
    require_replace(inst,
        "    vendor_name = driver.driverName.data();\n",
        "    vendor_name = driver.driverName.data();\n"
        '#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n'
        '    LOG_WARNING(Render_Vulkan, "BIONIC_VULKAN_DEVICE driver_id={} name={} vendor={:#x}",\n'
        '                static_cast<unsigned>(driver_id), driver.driverName.data(), properties.vendorID);\n'
        '#endif\n',
        "Android Vulkan physical device checkpoint")
    result["portedInterfaces"].append("complete modern Vulkan instance/presenter with Android loader")

    # Modern videoout already integrates with its matching Liverpool queue;
    # retain only the intended Android no-idle-present behavior if the marker
    # exists, rather than restoring the entire obsolete 0.16 video queue.
    driver = root / "src/core/libraries/videoout/driver.cpp"
    prefix_include(driver, "#include <atomic>", "Android present guard")
    require_replace(driver,
        "                    if (!main_port.is_open) {\n"
        "                        DrawBlankFrame();\n"
        "                    } else if (ImGui::Core::MustKeepDrawing()) {\n",
        "                    if (!main_port.is_open) {\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "                        // No GPU present before Android VideoOut opens.\n"
        "                        static std::atomic<bool> once{false};\n"
        "                        if (!once.exchange(true)) {\n"
        '                            LOG_INFO(Lib_VideoOut, "BIONIC_PRESENT_IDLE_SKIP");\n'
        "                        }\n"
        "#else\n"
        "                        DrawBlankFrame();\n"
        "#endif\n"
        "                    } else if (ImGui::Core::MustKeepDrawing()) {\n",
        "0.18 Android pre-VideoOut present guard")
    driver_text = driver.read_text()
    result["modernVideooutUsesLiverpoolQueue"] = "EnqueueCommand(" not in driver_text
    if not result["modernVideooutUsesLiverpoolQueue"]:
        raise RuntimeError("Modern 0.18 VideoOut unexpectedly uses old Liverpool queue")

    return result
