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
FEX_HOST = "be6bc2e9c60799e071dd2fafa6216e8d80ec619c"

# These implementation units have no Android-specific hooks and must match
# the 0.18.1 interfaces that consume them, not their 0.16.1 ancestors.
MATCH_0181 = (
    "src/core/debug_state.h",
    "src/core/debug_state.cpp",
    "src/common/ring_buffer_queue.h",
    "src/core/libraries/libs.cpp",
    "src/core/libraries/kernel/file_system.cpp",
    "src/core/libraries/kernel/file_system.h",
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

    # Modern file_system.cpp still implements these FEX AeroLib/Fios2 entrypoints,
    # but their declarations were dropped from the newer file_system.h.
    kernel_h = root / "src/core/libraries/kernel/file_system.h"
    require_replace(kernel_h,
        "s64 PS4_SYSV_ABI posix_lseek(s32 fd, s64 offset, s32 whence);\n",
        "s64 PS4_SYSV_ABI posix_lseek(s32 fd, s64 offset, s32 whence);\n"
        "s64 PS4_SYSV_ABI posix_read(s32 fd, void* buf, u64 nbytes);\n"
        "s32 PS4_SYSV_ABI posix_unlink(const char* path);\n"
        "s32 PS4_SYSV_ABI posix_rename(const char* from, const char* to);\n"
        "s64 PS4_SYSV_ABI sceKernelLseek(s32 fd, s64 offset, s32 whence);\n"
        "s32 PS4_SYSV_ABI sceKernelFstat(s32 fd, OrbisKernelStat* sb);\n",
        "real modern kernel I/O declarations")
    result["portedInterfaces"].append("0.18 kernel I/O declarations matching real HLE implementations")

    # GnmDriver's old six-argument VideoOut flip and token layout are obsolete.
    # Bring the whole upstream 0.18.1 PM4 caller instead of dropping an argument.
    restore(root, "src/core/libraries/gnmdriver/gnmdriver.cpp")
    result["restoredMatchingImplementations"].append(
        "src/core/libraries/gnmdriver/gnmdriver.cpp")

    # Modern Ime and pad APIs were incorrectly linked against old 0.16
    # implementations. Preserve their new headers and complete methods.
    # These HLE family interfaces changed together. Updating an individual
    # .cpp is insufficient: 0.16 VideoOut::SubmitFlip accepts a fifth lock
    # generation argument while 0.18 removed it from BOTH header and caller.
    # Restore complete modern source families, then graft back Android hooks.
    modern_hle_families = (
        "src/core/libraries/ime",
        "src/core/libraries/pad",
        "src/core/libraries/sysmodule",
        "src/core/libraries/videoout",
    )
    subprocess.run(
        ["git", "-C", str(root), "restore", "--source", UPSTREAM,
         "--worktree", "--", *modern_hle_families],
        check=True)
    result["restoredMatchingImplementations"].extend(
        family + "/*" for family in modern_hle_families)

    # The pinned FEX pthread.h has an int critical_count and no
    # PthreadCancelInterrupt(). Modern 0.18 semaphore.cpp expects an atomic
    # critical_count and that new interrupt API, so it cannot be linked to
    # the native ARM64/Bionic kernel host. Retain the proven FEX semaphore
    # implementation and adapt only its SlotVector calls to modern names.
    sem_rel = "src/core/libraries/kernel/threads/semaphore.cpp"
    sem = root / sem_rel
    sem.write_bytes(subprocess.check_output(
        ["git", "-C", str(root), "show", FEX_HOST + ":" + sem_rel]))
    require_replace(sem, ".insert(std::move(", ".Insert(std::move(",
                    "FEX semaphore new SlotVector Insert")
    sem_text = sem.read_text()
    replaced = sem_text.count("orbis_sems.is_allocated(")
    if replaced < 4:
        raise RuntimeError("FEX sem structure unexpected (is_allocated count)")
    sem_text = sem_text.replace("orbis_sems.is_allocated(", "orbis_sems.IsAllocated(")
    if sem_text.count("orbis_sems.erase(") != 1:
        raise RuntimeError("FEX sem erase API unexpected")
    sem_text = sem_text.replace("orbis_sems.erase(", "orbis_sems.Erase(")
    sem.write_text(sem_text)
    # FEX's old SlotVector initialized capacity in its constructor; modern
    # 0.18 starts empty. .Insert() therefore hits AddChunk() with max_chunks=0.
    # Upstream registers MAX_ORBIS_SEMAPHORES = std::numeric_limits<u16>::max().
    require_replace(
        sem,
        "void RegisterSemaphore(Core::Loader::SymbolsResolver* sym) {\n",
        "void RegisterSemaphore(Core::Loader::SymbolsResolver* sym) {\n"
        "    // Initialize modern SlotVector before guest semaphores are created.\n"
        "    orbis_sems.ResizeDestructive(0xFFFFu);\n",
        "FEX kernel semaphore pool must initialize 0.18 SlotVector")
    result["fexAdaptersKept"].append("FEX pthread semaphores with 0.18 SlotVector API")
    result["portedInterfaces"].append("FEX semaphore SlotVector allocation and 65535-entry initialization")

    # Modern sysmodule replaced the working FEX Fios2 module selector and
    # attempts LLE even when /app0/sce_module/libSceFios2.prx is absent.
    # Retain game/staged LLE when available; use real FEX Fios2 HLE if not.
    sysmodule = root / "src/core/libraries/sysmodule/sysmodule_internal.cpp"
    prefix_include(sysmodule, '#include "core/libraries/fios2/fios2.h"',
                   "FEX Fios2 fallback implementation")
    require_replace(
        sysmodule,
        "    s32 start_result = 0;\n"
        "    // Most of the logic the actual module has here is to get the correct location of this module.\n",
        """    s32 start_result = 0;
    // Index 3 is libSceFios2 in the actual PS4 sysmodule table.
    if (index == 3) {
        const auto dir = EmulatorSettings.GetSysModulesDir() / game_info->GameSerial();
        const auto staged = dir / "libSceFios2.sprx";
        const bool use_hle = std::filesystem::exists(dir / "libSceFios2.use-hle");
        if (!use_hle) {
            const std::filesystem::path path = std::filesystem::exists(staged)
                ? staged : std::filesystem::path("/app0/sce_module/libSceFios2.prx");
            const s32 handle = linker->LoadAndStartModule(path, argc, argv, &start_result);
            if (handle >= 0) {
                mod.handle = handle;
                ++mod.is_loaded;
                if (res_out != nullptr) {
                    *res_out = start_result;
                }
                return ORBIS_OK;
            }
        }
        LOG_INFO(Lib_SysModule, "BIONIC_FIOS2_HLE_FALLBACK title={}", game_info->GameSerial());
        Fios2::RegisterLib(&linker->GetHLESymbols());
        linker->RelocateAllImports();
        static s32 fios_hle_handle = 90;
        mod.handle = fios_hle_handle++;
        ++mod.is_loaded;
        if (res_out != nullptr) {
            *res_out = ORBIS_OK;
        }
        return ORBIS_OK;
    }
    // Most of the logic the actual module has here is to get the correct location of this module.
""",
        "restore Fios2 HLE on absent LLE module")
    result["portedInterfaces"].append("Fios2 LLE preference with working FEX HLE fallback")

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

    # FIOS2 HLE was registered only when sceSysmoduleLoadModule was called.
    # The real games import FIOS2 during ELF relocation, before that call.
    # Boot registration must precede guest import relocation on Bionic.
    prefix_include(libs, '#include "core/libraries/fios2/fios2.h"',
                   "FIOS2 HLE module before guest ELF relocation")
    require_replace(
        libs,
        '        Libraries::LibcInternal::ForceRegisterLib(sym);\n',
        '        Libraries::LibcInternal::ForceRegisterLib(sym);\n'
        '        // BACHATA_FIOS2_EARLY_HLE_READY: do not leave real FIOS2 NIDs ENOSYS.\n'
        '        // BACHATA_SHADOW_PREFER_GUEST_FIOS2: CUSA08809 loaded shadow.cwks\n'
        '        // before early FIOS2 HLE was added. ArchiveMountSync only aliases\n'
        '        // /app0; it does not provide the contents of any PSARC archive.\n'
        '        const bool shadow_guest_archive =\n'
        '            game_specific_modules_path.filename() == "CUSA08809" ||\n'
        '            game_specific_modules_path.filename() == "CUSA05170";\n'
        '        const bool fios_lle_staged =\n'
        '            std::filesystem::exists(game_specific_modules_path / "libSceFios2.sprx") &&\n'
        '            !std::filesystem::exists(game_specific_modules_path / "libSceFios2.use-hle");\n'
        '        // CUSA05170 loaded libSceFios2.prx successfully but early HLE\n'
        '        // hijacked ArchiveMountSync, leaving PhyreFIOS2 empty.\n'
        '        if (shadow_guest_archive)\n'
        '            LOG_INFO(Lib_Kernel, "BACHATA_GUEST_FIOS2_ARCHIVE_PREFERRED");\n'
        '        if (!fios_lle_staged && !shadow_guest_archive) {\n'
        '            Libraries::Fios2::RegisterLib(sym);\n'
        '            LOG_INFO(Lib_Kernel, "BACHATA_FIOS2_EARLY_HLE_READY");\n'
        '        }\n',
        "register actual FIOS2 HLE before linker relocation")
    result["portedInterfaces"].append("FIOS2 complete HLE NIDs early on FEX, unless LLE staged")

    # Real libSceFiber: shadPS4 desktop's x86 assembly is guarded by
    # ARCH_X86_64. The ARM64 FEX guest needs its own x86 frame switching
    # adapter, otherwise FIVE high-frequency Shadow of the Colossus HLE NIDs
    # silently become UnsupportedHleCallAdapter / ENOSYS.
    require_replace(
        libs,
        '#include "core/libraries/fiber/fiber.h"\n',
        '#include "core/libraries/fiber/fiber.h"\n'
        'namespace Libraries::Fiber {\n'
        'void RegisterFexFiberBridge(Core::Loader::SymbolsResolver* sym);\n'
        '}\n',
        "FEX guest fiber registration API")
    require_replace(
        libs,
        '#ifdef ARCH_X86_64\n'
        '            {"libSceFiber.sprx", Libraries::Fiber::RegisterLib},\n'
        '#endif\n',
        '#ifdef ARCH_X86_64\n'
        '            {"libSceFiber.sprx", Libraries::Fiber::RegisterLib},\n'
        '#elif defined(SHADPS4_ENABLE_FEX_GUEST_CPU)\n'
        '            {"libSceFiber.sprx", Libraries::Fiber::RegisterFexFiberBridge},\n'
        '#endif\n',
        "FEX guest fiber non-ENOSYS module table")

    from pathlib import Path as _Path
    fiber_source = _Path(__file__).resolve().parents[1] / "generic" / "android_fex_fiber.cpp"
    if not fiber_source.is_file():
        raise RuntimeError("FEX fiber implementation missing: " + str(fiber_source))
    cmake = root / "CMakeLists.txt"
    native_libc = fiber_source.with_name("android_libc_compat.cpp")
    require_replace(
        cmake,
        'target_sources(shadps4 PRIVATE "' + str(native_libc) + '")\n',
        'target_sources(shadps4 PRIVATE "' + str(native_libc) + '")\n'
        'target_sources(shadps4 PRIVATE "' + str(fiber_source) + '")\n',
        "link FEX x86-state fiber HLE into ARM64 Bionic native core")
    result["portedInterfaces"].append(
        "15 real libSceFiber NIDs on FEX: Initialize/Run/Switch/"
        "ReturnToThread with guest register and stack continuations")

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

    # Android already links PNG::PNG. Modern desktop stb_image_write.h is not
    # in the NDK include path; keep the existing proven libpng screenshot
    # implementation from the same working ARM64 FEX tree.
    presenter = root / "src/video_core/renderer_vulkan/vk_presenter.cpp"
    modern_png = presenter.read_text()
    old_png = subprocess.check_output(
        ["git", "-C", str(root), "show",
         FEX_HOST + ":src/video_core/renderer_vulkan/vk_presenter.cpp"]
    ).decode("utf-8")
    def write_png_block(source: str) -> str:
        if source.count("static bool WritePng(") != 1:
            raise RuntimeError("Missing or duplicate WritePng")
        start = source.index("static bool WritePng(")
        end = source.index("\n}\n", start) + 3
        return source[start:end]
    newer = write_png_block(modern_png)
    older = write_png_block(old_png)
    if "stbi_write_png_to_func(" not in newer or "png_write_image(" not in older:
        raise RuntimeError("Unexpected screenshot ABI for PNG compatibility port")
    require_replace(presenter, newer, older, "real libpng screenshot writer")
    require_replace(presenter, "#include <stb_image_write.h>", "#include <png.h>",
                    "Android PNG include")
    # FEX's Android ElfInfo owns a splash path, not upstream's desktop-only
    # splash_data vector. Keep modern Vulkan but load the real FEX game asset.
    require_replace(
        presenter,
        "const auto& splash_data = Common::ElfInfo::Instance().GetSplashData();",
        "const auto& splash_path = Common::ElfInfo::Instance().GetSplashPath();",
        "0.18 Vulkan splash image FEX ElfInfo path")
    require_replace(
        presenter, "if (!splash_data.empty()) {",
        "if (!splash_path.empty()) {", "Android splash path guard")
    require_replace(
        presenter,
        "ImGui::RefCountedTexture::DecodePngTexture(splash_data)",
        "ImGui::RefCountedTexture::DecodePngFile(splash_path)",
        "Android FEX splash file decoder")
    result["portedInterfaces"].append("0.18 Vulkan presenter with real Android libpng and FEX splash path")

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


    # The 0.18 logger declares Terminate() but dropped its definition even
    # though the preserved FEX Linker installs it as std::terminate_handler.
    # Reintroduce the original real FEX exception logger/quick-exit handler.
    log_cpp = root / "src/common/logging/log.cpp"
    original_log = subprocess.check_output(
        ["git", "-C", str(root), "show",
         FEX_HOST + ":src/common/logging/log.cpp"], text=True)
    start = original_log.index("void Terminate() {")
    stop = original_log.index("\nvoid UpdateSinks() {", start)
    terminate_impl = original_log[start:stop]
    if "std::quick_exit" not in terminate_impl or "std::current_exception" not in terminate_impl:
        raise RuntimeError("Original FEX Terminate handler unexpectedly absent")
    require_replace(log_cpp, "#include <cstdlib>\n",
                    "#include <cstdlib>\n#include <exception>\n#include <utility>\n",
                    "modern exception logger includes")
    # Original enum values are observable process return codes; do not change.
    enum_start = original_log.index("enum class ShadPs4ReturnCode : u32 {")
    enum_end = original_log.index("\n};", enum_start) + 3
    return_codes = original_log[enum_start:enum_end]
    require_replace(log_cpp, "namespace Common::Log {\n",
                    return_codes + "\n\nnamespace Common::Log {\n",
                    "FEX terminate error codes")
    require_replace(log_cpp, "void UpdateSinks() {\n",
                    terminate_impl + "\nvoid UpdateSinks() {\n",
                    "original FEX exception terminate implementation")
    result["portedInterfaces"].append("actual 0.16 FEX terminate handler in 0.18 logger")

    # The 0.18 camera links a new libkernel export whose declaration was
    # merged but whose *implementation* remained old FEX 0.16. Port the
    # authentic 0.18 HLE body, including System VMA mapping and its guest NID.
    # This must not be aliased to flexible memory (different accounting).
    mem_h = root / "src/core/memory.h"
    require_replace(mem_h, "    File = 8,\n", "    File = 8,\n    System = 9,\n",
                    "modern System VMA type on native FEX allocator")
    kernel_header = root / "src/core/libraries/kernel/memory.h"
    require_replace(
        kernel_header,
        "s32 PS4_SYSV_ABI sceKernelMapFlexibleMemory(void** addr_in_out, u64 len, s32 prot, s32 flags);\n",
        "s32 PS4_SYSV_ABI sceKernelMapFlexibleMemory(void** addr_in_out, u64 len, s32 prot, s32 flags);\n"
        "s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory(void** addr_in_out, u64 len, s32 prot,\n"
        "                                                       s32 flags, const char* name);\n",
        "modern System flexible memory public declaration")
    kernel_cpp = root / "src/core/libraries/kernel/memory.cpp"
    modern_kernel = subprocess.check_output(
        ["git", "-C", str(root), "show",
         UPSTREAM + ":src/core/libraries/kernel/memory.cpp"], text=True)
    start = modern_kernel.index("s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory(")
    stop = modern_kernel.index("\ns32 PS4_SYSV_ABI sceKernelQueryMemoryProtection(", start)
    authentic_kernel_function = modern_kernel[start:stop]
    if ("Core::VMAType::System" not in authentic_kernel_function or
            "memory->MapMemory(" not in authentic_kernel_function):
        raise RuntimeError("Missing genuine 0.18 system memory implementation")
    require_replace(
        kernel_cpp, "s32 PS4_SYSV_ABI sceKernelQueryMemoryProtection(",
        authentic_kernel_function + "s32 PS4_SYSV_ABI sceKernelQueryMemoryProtection(",
        "real 0.18 System VMA HLE implementation")
    require_replace(
        kernel_cpp,
        '    LIB_FUNCTION("mL8NDH86iQI", "libkernel", 1, "libkernel", sceKernelMapNamedFlexibleMemory);\n',
        '    LIB_FUNCTION("mL8NDH86iQI", "libkernel", 1, "libkernel", sceKernelMapNamedFlexibleMemory);\n'
        '    LIB_FUNCTION("kc+LEEIYakc", "libkernel", 1, "libkernel", sceKernelMapNamedSystemFlexibleMemory);\n',
        "register real System flexible memory PS4 export")
    result["portedInterfaces"].append("actual 0.18 named System VMA HLE and guest NID on FEX")

    # Restore PS4 guest x86 non-local jumps: setjmp is NOT an ARM host HLE.
    from guest_jump_abi import apply as apply_guest_nonlocal_jump
    result["fexGuestNonLocalJumps"] = apply_guest_nonlocal_jump(root)
    result["portedInterfaces"].append("PS4 FreeBSD x86 setjmp/longjmp guest-native FEX veneers")

    # The original 0.18.1 FlattenExtendedUserdataPass is x86/Xbyak-only.
    # ARM64 previously reached UNREACHABLE_MSG during the first compute shader.
    # Use the complete portable bytecode SRT walker (GPL-2.0+, Mark Hall 2026),
    # adapted to our PS4 guest VMM, not a no-op that loses shader resources.
    srt = root / "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp"
    original_srt = srt.read_text()
    if ("#ifdef ARCH_X86_64" not in original_srt or
        "FlattenExtendedUserdataPass unimplemented for target architecture." not in original_srt):
        raise RuntimeError("Expected pinned 0.18.1 x86-only SRT source")
    native_srt = Path(__file__).with_name("flatten_extended_userdata_arm64.cpp").read_text()
    if ("BIONIC_PORTABLE_SRT_GUEST_VMM" not in native_srt or
        "GenerateSrtProgram(program.info, pass_info);" not in native_srt or
        "SrtOp::CopyExpr" not in native_srt):
        raise RuntimeError("Incomplete ARM64 SRT resource walker")
    srt.write_text(native_srt)

    srt_h = root / "src/shader_recompiler/ir/passes/srt.h"
    require_replace(
        srt_h,
        "using PFN_SrtWalker = void PS4_SYSV_ABI (*)(const u32* /*user_data*/, u32* /*flat_dst*/);\n"
        "PFN_SrtWalker RegisterWalkerCode(const u8* ptr, size_t size);",
        "using SrtWalkerCode = const u32*; // portable bytecode, not x86 JIT\n"
        "SrtWalkerCode RegisterWalkerCode(const u8* ptr, size_t size);\n"
        "void RunSrtWalker(SrtWalkerCode code, const u32* user_data, u32* flat_dst);",
        "portable SRT ABI header")
    require_replace(srt_h, "    PFN_SrtWalker walker_func{};",
                    "    SrtWalkerCode walker_func{};",
                    "portable SRT pointer type")

    shader_info = root / "src/shader_recompiler/info.h"
    require_replace(shader_info,
                    "srt_info.walker_func(user_data.data(), flattened_ud_buf.data());",
                    "RunSrtWalker(srt_info.walker_func, user_data.data(), flattened_ud_buf.data());",
                    "actually execute ARM64 portable walker")

    serialized = root / "src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    require_replace(serialized,
                    "srt.Write(reinterpret_cast<void*>(walker_func), walker_func_size);",
                    "std::vector<u32> portable_code(walker_func, walker_func + "
                    "walker_func_size / sizeof(u32));\n"
                    "        srt.Write(portable_code.data(), walker_func_size);",
                    "serialize portable SRT code")
    require_replace(serialized,
                    "        walker_func = RegisterWalkerCode(ar.CurrPtr(), walker_func_size);\n"
                    "        ar.Advance(walker_func_size);",
                    "        walker_func = RegisterWalkerCode(ar.CurrPtr(), walker_func_size);\n"
                    "        if (!walker_func) {\n"
                    "            return false; // invalidate previous x86 JIT shader cache\n"
                    "        }\n"
                    "        ar.Advance(walker_func_size);",
                    "deserialization of incompatible x86 pipeline cache")
    result["portedInterfaces"].append(
        "Portable ARM64 SRT with proven-uniform Phi/ReadLane and VMM-validated reads; "
        "legacy x86 pipeline cache rejected")

    # Version 6 persisted host x86 code for SRT walkers. Force a new metadata
    # namespace and make deserialization failure propagate all the way to the
    # pipeline cache loader. Otherwise a rejected walker silently looks valid.
    require_replace(serialized,
                    "static constexpr u32 ShaderMetaVersion = 6u;",
                    "static constexpr u32 ShaderMetaVersion = 14u;",
                    "portable SRT shader metadata cache generation")
    require_replace(serialized,
                    "    info.Deserialize(ar);\n    return true;\n",
                    "    return info.Deserialize(ar);\n",
                    "propagate incompatible SRT cache deserialization")
    result["portedInterfaces"].append(
        "ShaderMetaVersion 14; invalidate old shaders without dynamic GPU ReadConst storage resources")

    # The 0.2.6 release ELF owns each copied DCB/CCB pair; upstream 0.18.1
    # instead aborts when the shared 2-MiB queue staging space is exhausted.
    from port_release026_cmd_buffers import apply as apply_owned_cmd_buffers
    result["release026GpuCommandBufferParity"] = apply_owned_cmd_buffers(root)
    result["portedInterfaces"].append(
        "Bachata 0.2.6 owned PM4 DCB/CCB buffers retained by each GPU coroutine")

    from port_release026_ce_engine import apply as apply_ce_engine
    result["release026CeSchedulerParity"] = apply_ce_engine(root)
    result["portedInterfaces"].append(
        "Release 0.2.6 CE FIFO: separate tasks, IB chaining, packet snapshot, "
        "shared command data lifetime")

    # Shader SRT dynamic indexing is a coherent 12-file IR/SPIR-V port,
    # not a forced zero/unsupported-Phi fallback and not an x86 JIT dependency.
    from port_srt_dynamic_readconst import apply as apply_dynamic_srt
    result["release026SrtDynamicIndexParity"] = apply_dynamic_srt(root)
    result["portedInterfaces"].append(
        "Bachata SRT: bounded metadata layout, ReadConstArray runtime index, "
        "native ARM64 portable walker and stale shader cache generation")

    # The app's 0.2.7 runtime template and upstream's pinned Git SHA are not
    # the revision of the rebuilt Bionic native core. Emit an explicit marker
    # from the *actual* emulated process so each diagnostic proves what ran.
    # Every native core revision must carry its *real* source commit in the
    # guest-visible log. This is also verified against the packaged ELF by
    # assemble_apk.py; never reuse a fixed BACHATA_CORE_PARITY marker.
    repo_dir = Path(__file__).resolve().parents[2]
    source_revision = subprocess.check_output(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"], text=True
    ).strip()
    if len(source_revision) != 40 or any(ch not in "0123456789abcdef" for ch in source_revision):
        raise RuntimeError("Invalid Bionic native core source Git revision")
    parity_marker = "BACHATA_CORE_PARITY=20261123-SRT4-GPUPAGE1-CTYPE3-CE1-OWNEDCB-FIBER1-RUNTIME1-RELEASEFIOS2-SAFDIRECT2-GPUCLAMP1-BUDGET1-RCSNAP1-IFILE1-FIOSERR1"
    revision_marker = "BACHATA_CORE_REVISION=" + source_revision
    emulator = root / "src/emulator.cpp"
    before = '    LOG_INFO(Loader, "Revision {}", Common::g_scm_rev);\n'
    require_replace(
        emulator,
        before,
        before + f'    LOG_INFO(Loader, "{parity_marker}");\n'
               + f'    LOG_INFO(Loader, "{revision_marker}");\n',
        "revision-accurate native core parity and source markers")

    from port_release026_cmask_owner import apply as apply_meta_owners
    result["release026CmaskOwnerParity"] = apply_meta_owners(root)
    result["portedInterfaces"].append(
        "Release 0.2.6 metadata: CMask/FMask/HTile live owner UID "
        "validation, address reuse and clear-mask preservation")

    from port_release026_gpu_range import apply as apply_gpu_range
    result["release026GpuMappedRange"] = apply_gpu_range(root)
    result["portedInterfaces"].append(
        "PS4 40-bit GPU ClampGpuRangeSize, mapped VMA boundary validation "
        "for oversized guest buffer ranges")

    from port_release026_gpu_live_budget import apply as apply_gpu_live_budget
    result["release026LiveGpuMemoryBudget"] = apply_gpu_live_budget(root)
    result["portedInterfaces"].append(
        "Release live Vulkan memory budget and VMA usage telemetry; texture GC "
        "adjusts to actual Android memory pressure")

    from port_release026_readconst_snapshot import apply as apply_readconst_snapshot
    result["release026ReadConstSnapshot"] = apply_readconst_snapshot(root)
    # Track actual GPU-written guest descriptor pages before creating Vulkan bindings.
    from port_release026_srt_page_readback import apply as apply_srt_gpu_pages
    result["release026GpuWrittenSrtPageReadback"] = apply_srt_gpu_pages(root)
    # Port the missing pre-resource-patching callback from the actual The Order Android source.
    from port_order1886_srt_pipeline_sync import apply as apply_order_srt_sync
    result["order1886PreResourceSrtSync"] = apply_order_srt_sync(root)
    from port_order1886_gpu_dynamic_readconst import apply as apply_order_gpu
    result["order1886DynamicGpuReadConst"] = apply_order_gpu(root)
    # The Order 1886 can carry an invalid texture channel selector after a
    # nonuniform SRT read. Reject that descriptor before image-view creation;
    # never substitute identity swizzles or abort the whole emulator.
    from port_release026_image_swizzle import apply as apply_image_swizzle
    result["release026BadImageSwizzleGuard"] = apply_image_swizzle(root)
    from port_donor_parity import apply as apply_donor_parity
    result["shadowOrderDonorParity"] = apply_donor_parity(root)
    from port_historical_donor_fixes import apply as apply_historical_donor_fixes
    result["shadowOrderHistoricalParity"] = apply_historical_donor_fixes(root)
    from port_donor_upload_transaction import apply as apply_upload_transaction
    result["donorUploadTransaction"] = apply_upload_transaction(root)
    from port_backing_and_uma import apply as apply_backing_uma
    result["backingAndUmaParity"] = apply_backing_uma(root)
    from port_sotc_tsharp_arrays import apply as apply_sotc_tsharp_arrays
    result["sotcTsharpArrays"] = apply_sotc_tsharp_arrays(root)
    from port_watcher_pairing_and_rptr import apply as apply_watcher_rptr
    result["watcherPairingAndRptr"] = apply_watcher_rptr(root)
    from port_compiled_descriptor_contract import apply as apply_compiled_descriptor_contract
    result["compiledDescriptorContract"] = apply_compiled_descriptor_contract(root)
    # Restore the independently tested 608a1ac SotC behavior without
    # undoing The Order fixes for every other title.
    from port_sotc_608_profile import install as install_sotc_profile
    install_sotc_profile(root)
    from port_sotc_render_and_common_performance import apply as apply_sotc_render_perf
    result["sotcRenderAndCommonPerformance"] = apply_sotc_render_perf(root)
    from port_bionic_runtime_parity import apply as apply_bionic_runtime_parity
    result["bionicRuntimeParity"] = apply_bionic_runtime_parity(root)
    from port_bionic_hotpaths import apply as apply_bionic_hotpaths
    result["bionicHotpaths"] = apply_bionic_hotpaths(root)
    from port_bionic_present_cache import apply as apply_present_cache
    result["bionicPresentCache"] = apply_present_cache(root)
    from port_single_core_pthread import apply as apply_pthread_opaque
    result["pthreadOpaque"] = apply_pthread_opaque(root)
    from port_confirmed_order_recovery import apply as apply_order
    result["confirmedOrderRecovery"] = apply_order(root)
    from port_order_memory_lifetime import apply as apply_order_memory_lifetime
    result["orderMemoryLifetime"] = apply_order_memory_lifetime(root)
    from port_order_shader_workers import apply as apply_order_shader_workers
    result["orderShaderWorkers"] = apply_order_shader_workers(root)
    from port_ahb_present import apply as apply_ahb_present
    result["ahbPresent"] = apply_ahb_present(root)
    from port_target_batched_readback import apply as apply_target_batched_readback
    result["targetBatchedReadback"] = apply_target_batched_readback(root)
    result["portedInterfaces"].append(
        "Release ReadConst GPU buffer isolation: IR provenance, host-visible "
        "CPU snapshot, scheduler-held lifetime; GPU-authored data stays in GPU cache")

    # Working official Release 0.2.6/0.2.7 does not parse PSARC here.
    # The former generic parser was a speculative divergence; remove it
    # instead of leaving it enabled as a fallback.
    from port_release026_mount_alias import apply as apply_release026_alias
    result["release026Fios2MountAlias"] = apply_release026_alias(root)
    # Correct false-success queries for a failed FIOS async operation.
    from port_release026_fios_async_errors import apply as apply_fios_async_errors
    result["release026FiosAsyncErrorSemantics"] = apply_fios_async_errors(root)
    result["portedInterfaces"].append(
        "Official 0.2.6/0.2.7 FIOS2 MountAlias guest backend parity: "
        "SAF/updates/mods preserved; no host-mount/PSARC alternate code")

    # The verified Release ELF also has SafFsBackend::Open and SafBrokerClient,
    # whereas our new VFS only reopened short-lived /proc/self/fd symlinks.
    # Restore directly owned Android BSF1 broker FDs, lazily and generically.
    from port_release026_saf_backend import apply as apply_release026_saf_backend
    result["release026SafIFileBackend"] = apply_release026_saf_backend(root)
    result["portedInterfaces"].append(
        "Release SAF broker direct fd backed IFile, independent positional reads, "
        "case-insensitive fallback on actual game files; no unnecessary full copy")

    # The retained FEX 0.16 Module/Elf loader still reopened every binary
    # through host filesystem paths. The verified Release and modern 0.18.1
    # both accept a moved IFile; preserve this for mounted app0/SAF modules
    # without changing ARM64 guest initialization or relocation semantics.
    from port_release026_ifile_loader import apply as apply_release026_ifile
    result["release026GuestIFileLoader"] = apply_release026_ifile(root)
    result["portedInterfaces"].append(
        "Release guest IFile-based ELF/Module/Linker boot; SAF game modules "
        "own their fd and host-only system modules use HostFile IFile")


    # CUSA00552 crashes before first frame at x86 RIP 0x800e1e2d0 and
    # host SIGSEGV reading 0x20. The current host PC is JIT-generated code,
    # so dladdr cannot name the game module. Symbolize the GUEST RIP against
    # the loaded PS4 executable/module and log its relative offset instead.
    # This changes only the fatal/crash path, not normal execution.
    signals = root / "src/core/signals.cpp"
    prefix_include(signals, '#include "core/linker.h"', "crash module linker API")
    prefix_include(signals, '#include "core/module.h"', "crash module address API")
    prefix_include(signals, '#include "common/singleton.h"', "crash module singleton")
    old_signal = ('                LOG_CRITICAL(Debug, '
                  '"FEX guest state at fault: rip={:#x} rax={:#x}", guest_rip,\n'
                  '                             guest_rax);')
    new_signal = (old_signal +
                  '\n                if (auto* module = '
                  'Common::Singleton<Core::Linker>::Instance()->FindByAddress(guest_rip)) {\n'
                  '                    LOG_CRITICAL(Debug, '
                  '"BIONIC_GUEST_CRASH_MODULE file={} module_base={:#x} rip_offset={:#x}",\n'
                  '                                 module->file.string(), '
                  'module->GetBaseAddress(), guest_rip - module->GetBaseAddress());\n'
                  '                }')
    require_replace(signals, old_signal, new_signal,
                    "symbolize guest RIP inside the original PS4 game module")
    result["portedInterfaces"].append(
        "FEX fatal guest RIP mapped to PS4 eboot/prx module+offset; "
        "no speculative game-specific GPU or libc changes")

    return result
