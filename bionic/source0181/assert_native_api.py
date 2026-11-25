#!/usr/bin/env python3
"""Cheap structural C++ contract checks before ~2200 Android build units.

This does not replace C++ compilation. It prevents the exact class of
0.16.1 / 0.18.1 source-mixing regressions observed in the full NDK logs.
"""
from __future__ import annotations
import argparse
import ast
import re
import subprocess
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
        "src/core/libraries/kernel/file_system.cpp": ("deci_tty_device.h", "NLq2b1jOaN0", "sceKernelFutimes", "::futimes(native_fd"),
        "src/core/libraries/kernel/file_system.h": (
            "s64 PS4_SYSV_ABI posix_read(", "s32 PS4_SYSV_ABI posix_unlink(",
            "s32 PS4_SYSV_ABI posix_rename(", "s64 PS4_SYSV_ABI sceKernelLseek(",
            "s32 PS4_SYSV_ABI sceKernelFstat("),
        "src/core/libraries/kernel/threads/semaphore.cpp": (
            ".Insert(", ".IsAllocated(", ".Erase(",
            "orbis_sems.ResizeDestructive(0xFFFFu);"),
        "src/core/libraries/libs.cpp": (
            "ForceRegisterLib(sym);",
            "BIONIC_BOOT_STAGE=LIBC_HLE_END",
            "libSceNpCommerce.sprx",
            '"libSceFiber.sprx", Libraries::Fiber::RegisterFexFiberBridge',
            "#elif defined(SHADPS4_ENABLE_FEX_GUEST_CPU)"),
        "src/core/loader/elf.h": (
            "void Open(std::unique_ptr<Core::FileSys::IFile> handle);",
            "Core::FileSys::FileReader m_f{};"),
        "src/core/loader/elf.cpp": (
            "void Elf::Open(std::unique_ptr<Core::FileSys::IFile> owned)",
            "m_f.Reset(std::move(owned));",),
        "src/core/module.h": (
            "std::unique_ptr<Core::FileSys::IFile> source, u32& max_tls_index"),
        "src/core/module.cpp": ("BACHATA_RELEASE026_MODULE_IFILE",
                                "elf.Open(std::move(source));"),
        "src/core/linker.cpp": ("BACHATA_RELEASE026_LOADER_IFILE",
                                "std::make_unique<Module>(memory,elf_name,std::move(source),max_tls_index)",),
        "src/core/file_sys/fs.h": ("std::unique_ptr<IFile> handle;",
                                    "GetHostFile() const",
                                    "bool MountAlias(std::string_view source_guest"),
        "src/core/file_sys/fs.cpp": (
            "BACHATA_RELEASE026_MOUNT_ALIAS",
            "MntPoints::MountAlias(std::string_view",
            "const auto stack = source->backends",
            "BachataSaf::RegisterGuestAlias(original, alias)",
            "BACHATA_RELEASE026_SAF_BACKEND",
            "return OpenSafGuestFile(*corrected)"),
        "src/core/file_sys/backends/saf_fs_backend.cpp": (
            "BACHATA_RELEASE026_SAF_FD_OPEN",
            "OpenSafGuestFile(", "::pread(", "BachataSaf::OpenFd("),
        "src/core/libraries/fios2/fios2.cpp": (
            "BACHATA_FIOS2_RELEASE_ALIAS_READY",
            'mnt->MountAlias("/app0", alias)',
            "BACHATA_RELEASE026_FIOS_ALIAS_SOURCE_MISSING",
            "BACHATA_RELEASE026_FIOS_ASYNC_INVALID_OP",
            "if (out_handle != nullptr) *out_handle = -1;"),
        "src/core/memory.cpp": ("file->GetHostFile()", "file->GetSize()",
                                 "BACHATA_RELEASE026_GPU_RANGE_CLAMP",
                                 "ClampGpuRangeSize(VAddr address, u64 requested)",
                                 "BACHATA_PHYSICAL_BACKING_ALIAS", "BACHATA_SPARSE_COPY_ONCE", "VisitPhysicalSpans",
                                 "bool MemoryManager::TryReadBacking", "BACHATA_SPARSE_READBACK"),
        "src/core/libraries/videoout/driver.cpp": ("BIONIC_PRESENT_IDLE_SKIP",
                                                    "PrepareBlankFrame(true)"),
        "src/imgui/renderer/imgui_impl_sdl3.cpp": (
            "controllers[0]->ReadState()", "pressed(Button::Cross)",
            "pressed(Button::Circle)", "ImGuiBackendFlags_HasGamepad"),
        "src/video_core/renderer_vulkan/vk_scheduler.cpp": (
            "BACHATA_SINGLE_SUBMIT_POLL", "PopPendingOperations(BachataCompat::Sotc608())",
            "work_semaphore.Refresh();"),
        "src/core/libraries/videoout/driver.h": ("bool SubmitFlip(VideoOutPort*",),
        "src/core/libraries/videoout/video_out.cpp": (
            "driver->SubmitFlip(port, buf_id, flip_arg, true);",),
        "src/core/libraries/pad/pad.h": ("ORBIS_PAD_MAX_DATA_NUM",),
        "src/core/libraries/gnmdriver/gnmdriver.cpp": (
            "VideoOut::sceVideoOutSubmitEopFlip(vo_handle, buf_idx, flip_mode,",),
        "src/video_core/renderer_vulkan/vk_presenter.cpp": (
            "#include <png.h>", "png_write_image(",
            "BACHATA_FIRST_GAME_PRESENT_OK",
            "draw_scheduler.WaitSubmitted(frame->ready_tick,false);",
            "GetSplashPath()", "DecodePngFile(splash_path)",
            "BACHATA_GUEST_SIZED_INTERMEDIATE", "BACHATA_IDENTITY_DISPLAY",
            "BACHATA_DISPLAY_PATH", "opaque_sampled_view", "BACHATA_SOTC_608_PROFILE"),
        "src/core/libraries/sysmodule/sysmodule_internal.h": (
            "g_need_scelibc", "g_need_fios2"),
        "src/core/libraries/sysmodule/sysmodule_internal.cpp": (
            "BIONIC_FIOS2_HLE_FALLBACK", "Fios2::RegisterLib(",
            "libSceFios2.use-hle", "linker->RelocateAllImports();"),
        "src/video_core/renderer_vulkan/vk_instance.h": ("IsShaderSubgroupClockSupported",
                                                         "IsMultisampleStorageImageSupported",
                                                         "IsImageViewMinLodSupported",
                                                         "GetMaxSamplerAllocationCount",
                                                         "GetLiveGpuMemoryBudget() const",
                                                         "GetGpuMemoryTelemetry() const"),
        "src/video_core/renderer_vulkan/vk_instance.cpp": ("BIONIC_VULKAN_DEVICE",
                                                          "BACHATA_RELEASE026_GPU_LIVE_BUDGET",
                                                          "vmaGetHeapBudgets("),
        "src/video_core/renderer_vulkan/vk_rasterizer.cpp": (
            "BACHATA_RELEASE026_IMAGE_SWIZZLE_GUARD",
            "!swizzle_selector_valid",
            "BACHATA_RELEASE026_SRT_GPU_PAGE_READBACK",
            "SRT was synchronized before this exact permutation was selected.",
            "buffer_cache.IsRangeGpuWritten(source,sizeof(u32))", "buffer_cache.DownloadSrtSourcePages(pages)",
            "buffer_cache.TrackSrtSourcePage(page)",
            "buffer_cache.DownloadSrtSourcePages(pages)",
            "writable.RefreshFlatBuf();",
            "BACHATA_RELEASE026_READCONST_SNAPSHOT",
            "MakeReadConstSnapshot(", "desc.used_as_readconst",
            "!buffer_cache.IsRegionGpuModified(",
            "scheduler.DeferOperation("),
        "src/video_core/renderer_vulkan/vk_platform.cpp": (
            "BIONIC_VULKAN_CUSTOM_BRIDGE_READY", "BIONIC_VULKAN_CUSTOM_REQUIRED"),
        "src/common/elf_info.h": ("GetNpCommIds()", "GetSplashPath()"),
        "src/imgui/imgui_texture.h": ("DecodePngFile(",),
        "src/common/logging/log.cpp": ("void Terminate() {", "std::current_exception()",
                                      "std::quick_exit(", "TERMINATE_WITH_UNKNOWN_EXCEPTION"),
        "src/core/memory.h": ("System = 9,", "u64 ClampGpuRangeSize("),
        "src/core/libraries/kernel/memory.h": (
            "s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory(",),
        "src/core/libraries/kernel/memory.cpp": (
            "s32 PS4_SYSV_ABI sceKernelMapNamedSystemFlexibleMemory(",
            "Core::VMAType::System",
            'LIB_FUNCTION("kc+LEEIYakc", "libkernel", 1, "libkernel", sceKernelMapNamedSystemFlexibleMemory);'),
        "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp": (
            "RELEASE026_SRT_UNIFORM_OFFSET_PROOF",
            "RELEASE026_SRT_NONUNIFORM_LANE_REQUIRES_GPU",
            "IR::Opcode::Phi", "IR::Opcode::ReadLane",
            "BIONIC_PORTABLE_SRT_GUEST_VMM", "BIONIC_PORTABLE_SRT_BAD_POINTER",
            "BIONIC_PORTABLE_SRT_BAD_READ", "TryReadGuest(",
            "if (guest_read_ok)", "BACHATA_SRT_POINTER_PROVENANCE",
            "BACHATA_SRT_CONTIGUOUS_READ",
            "GenerateSrtProgram(program.info, pass_info);",
            "SrtOp::CopyExpr", "SrtOp::PushPtrExpr",
            "BACHATA_SRT_RUNTIME_ARRAY_5624", "PrepareSrtReadArrays",
            "IR::Opcode::ReadConstArray"),
        "src/shader_recompiler/ir/passes/srt.h": ("SrtWalkerCode", "RunSrtWalker(",
                                                  "std::vector<VAddr>& source_addresses"),
        "src/shader_recompiler/resource.h": ("bool used_as_readconst{};",),
        "src/shader_recompiler/ir/passes/resource_patching_pass.cpp": (
            "buffer.used_as_readconst |= desc.used_as_readconst;",
            ".used_as_readconst = inst.GetOpcode() == IR::Opcode::ReadConstBuffer"),
        "src/shader_recompiler/ir/opcodes.inc": ("OPCODE(ReadConstArray,",),
        "src/shader_recompiler/params.h": ("FindSrtPointer(", "ShaderInputUsageSlot"),
        "src/video_core/amdgpu/regs_shader.h": ("ReadShaderResourceTable(",),
        "src/shader_recompiler/backend/spirv/emit_spirv_context_get_set.cpp":
            ("EmitReadConstArray(",),
        "src/shader_recompiler/info.h": ("RunSrtWalker(srt_info.walker_func,",
                                       "srt_guest_sources.assign(", "srt_guest_sources);"),
        "src/video_core/amdgpu/liverpool.h": (
            "using CmdBuffer = std::pair<std::vector<u32>, std::vector<u32>>;",
            "std::shared_ptr<CmdBuffer> owned_buffers = {}",
            "std::queue<Task::Handle> ce_submits"),
        "src/video_core/amdgpu/liverpool.cpp": (
            "BACHATA_RELEASE026_OWNED_DCB_CCB",
            "BACHATA_RELEASE026_CE_QUEUE_PARITY",
            "owned.first.assign(dcb.begin(), dcb.end());",
            "owned.second.assign(ccb.begin(), ccb.end());",
            "std::make_shared<CmdBuffer>",
            "ProcessCeUpdate(ccb, owned_buffers)"),
        "src/video_core/texture_cache/texture_cache.h": (
            "ResolveCMaskOwner(VAddr address) const", "HasLiveMeta(VAddr address) const",
            "owner_uid{}", "num_samples = 1"),
        "src/video_core/texture_cache/texture_cache.cpp": (
            "BACHATA_RELEASE026_META_OWNER_UID", "RegisterMeta(cmask_addr",
            "UnregisterMeta(meta_info.cmask_addr, image.image_uid)",
            "telemetry.live_budget",
            "GetGpuMemoryTelemetry()"),
        "src/video_core/buffer_cache/buffer_cache.h": (
            "bool IsRangeGpuWritten(VAddr addr, size_t size);",
            "void TrackSrtSourcePage(VAddr page);",
            "SynchronizedRanges srt_source_pages;", "std::shared_lock l{mutex};ranges.ForEachInRange"),
        "src/video_core/page_manager.cpp": (
            "EnsurePages((base_page+page_start)<<PM_PAGE_BITS,", "page_reservation_mutex",
            "BACHATA_WATCHER_PAIRING", "EnsurePages(aligned_addr, aligned_end);"),
        "src/video_core/buffer_cache/buffer_cache.cpp": (
            "BACHATA_EMPTY_READBACK_RELEASE", "memory->WriteSparseBacking(",
            "BACHATA_RELEASE026_SRT_GPU_RANGE_TRACKING",
            "gpu_modified_ranges.Intersects(addr,size)",
            "srt_source_pages.Add(page & ~u64{4095},4096)",
            "BACHATA_RELEASE026_CMASK_EXPANDED",
            "0xDDDDDDDDu", "0xEEEEEEEEu",
            "texture_cache.ResolveCMaskOwner(device_addr)"),
        "src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp": (
            "std::vector<u32> portable_code(", "if (!walker_func) {",
            "ShaderMetaVersion = 222u;", "return info.Deserialize(ar) && effective_info.Deserialize(ar);"),
        "src/core/guest_cpu/hle_call_adapter.cpp": (
            "BIONIC_GUEST_X86_NONLOCAL_JUMP", "gNQ1V2vfXDE",
            "lKEN2IebgJ0", "guest_setjmp[]", "guest_longjmp[]",
            "do_setjmp", "do_longjmp", "written = 16;"),
        "src/common/cstring.h": ("#include <algorithm>",),
        "src/core/file_format/psf.cpp": ("#include <algorithm>",),
        "src/main.cpp": ("BachataSaf::Configure", "controller->ApplyRemoteState(",
                         "controller->PollState()"),
        "src/emulator.cpp": (
            "BIONIC_BOOT_STAGE=GUEST_LIBC_OBJECTS_END",
            "EmulatorSettings.IsLogAppend()",
            "BACHATA_CORE_PARITY=20261123-SRT4-GPUPAGE1-CTYPE3-CE1-OWNEDCB-FIBER1-RUNTIME1-RELEASEFIOS2-SAFDIRECT2-GPUCLAMP1-BUDGET1-RCSNAP1-IFILE1-FIOSERR1",
            "BACHATA_CORE_REVISION="),
        "src/imgui/big_picture/big_picture.cpp": ("emulator->Restart(runEbootPath)",),
        "src/core/signals.cpp": ("BIONIC_HOST_FAULT_MODULE",
                                 "BIONIC_GUEST_CRASH_MODULE",
                                 "FindByAddress(guest_rip)",),
    }
    forbidden = {
        "src/core/module.cpp": ("elf.Open(file);",),
        "src/core/linker.cpp": (
            "std::make_unique<Module>(memory, elf_name, max_tls_index)",),
        "src/core/libraries/fios2/fios2.cpp": (
            'mnt->Mount(app0_host, guest_mount, true);',
            'Map the FIOS mount point to the same host folder',
            "BIONIC_PSARC_MOUNT_READY",
            "MountArchiveBackend(",
            "GetHostPath(\"/app0\")"),
        "src/core/file_sys/fs.cpp": (
            'if (auto remote = BachataSaf::Resolve(*corrected))',),
        "src/core/libraries/libs.cpp": ('"core/libraries/np/np_commerce.h"',),
        "src/core/libraries/kernel/file_system.cpp": ("deci_tty6_device.h",),
        "src/core/memory.cpp": ("file->f.",),
        "src/video_core/amdgpu/liverpool.cpp": (
            "cblock.Reset();", "!ce_task.handle.done()",
            "dcb copy buffer out of reserved space",
            "ccb copy buffer out of reserved space"),
        "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp": (
            "FlattenExtendedUserdataPass unimplemented for target architecture.",
            "runtime_fault_recover", "bbport_threads.h",
            "std::atomic_ref<u32>(ops[i]).fetch_or(SrtZeroed"),
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
    # The runtime installer and the binary must never disagree on which
    # source revision was compiled. Embed the checked-out Git commit (not the
    # 0.2.7 frontend's inherited 9ceb... revision) into the native log.
    source_repo = Path(__file__).resolve().parents[2]
    git_sha = subprocess.check_output(
        ["git", "-C", str(source_repo), "rev-parse", "HEAD"], text=True
    ).strip()
    emulator_source = (root / "src/emulator.cpp").read_text()
    if not re.fullmatch(r"[0-9a-f]{40}", git_sha) or (
            f"BACHATA_CORE_REVISION={git_sha}" not in emulator_source):
        issues.append("Native ELF marker does not match the actual source Git revision")
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
    # An API marker alone would miss initialization in the wrong function.
    sem = (root / "src/core/libraries/kernel/threads/semaphore.cpp").read_text()
    registration = sem.split("void RegisterSemaphore(Core::Loader::SymbolsResolver* sym) {", 1)
    if len(registration) != 2 or not registration[1].lstrip().startswith(
            "// Initialize modern SlotVector before guest semaphores are created.\n"
            "    orbis_sems.ResizeDestructive(0xFFFFu);"):
        issues.append("FEX semaphore pool is not initialized at HLE registration")
    # CUSA08809: the imports must be resolved under libSceLibcInternal,
    # not by unrelated libc aliases which leave ENOSYS 38.
    libc_boot = (Path(__file__).resolve().parent.parent / "generic/android_libc_boot.cpp").read_text()
    for marker in ('BACHATA_RELEASE026_LIBCINTERNAL_REAL_NIDS',
                   'LIB_FUNCTION("8zTFvBIAIN8", "libSceLibcInternal"',
                   'LIB_FUNCTION("GMpvxPFW924", "libSceLibcInternal"',
                   'GuestInternalVprintf(', 'GuestInternalMemset('):
        if marker not in libc_boot:
            issues.append("FEX libcInternal ABI missing: " + marker)
    for marker in ('BACHATA_FEX_LIBCINTERNAL_IMPORTS_READY',
                   'INTERNAL_ALIAS("gQX+4GDQjpM", GuestMalloc)',
                   'INTERNAL_ALIAS("tIhsqj0qsFE", GuestFree)',
                   'INTERNAL_ALIAS("Q2V+iqvjgC0", GuestVsnprintf)',
                   'INTERNAL_ALIAS("Q3VBxCXhUHs", GuestInternalMemcpy)'):
        if marker not in libc_boot:
            issues.append("Critical Shadow libcInternal import missing " + marker)
    srt_source = (root / "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp").read_text()
    for marker in ("BACHATA_SRT_UNIFORM_READCONST_PROOF",
                   "case IR::Opcode::CompositeConstructU32x2:",
                   "case IR::Opcode::ReadConstBuffer:"):
        if marker not in srt_source:
            issues.append("SRT wave uniform constant source proof missing " + marker)
    # Verify the source-proven guest-read callback exists at the actual IR
    # barrier, not only in the rasterizer's later binding path.
    rsrc = (root / "src/shader_recompiler/recompiler.cpp").read_text()
    hdr = (root / "src/video_core/renderer_vulkan/vk_pipeline_cache.h").read_text()
    pc = (root / "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp").read_text()
    raster_src = (root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    for marker, blob in (
        ("BACHATA_ORDER1886_PRE_RESOURCE_SRT_SYNC", rsrc),
        ("if (guest_reads_done) guest_reads_done();", rsrc),
        ("void SetSrtSync(std::function<void(Shader::Info&)> callback)", hdr),
        ("if (srt_sync) srt_sync(info);", pc),
        ("pipeline_cache.SetSrtSync(", raster_src),
    ):
        if marker not in blob:
            issues.append("The Order SRT pre-resource synchronization missing: " + marker)
    srt_impl = (root / "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp").read_text()
    if "flat_multimap<IR::Value" not in srt_impl:
        issues.append("The Order duplicate-offset ReadConst chains still lost by flat_map")
    if "user_list.emplace(inst->Arg(1), inst);" not in srt_impl or "user_list[" in srt_impl:
        issues.append("The Order SRT multimap must preserve duplicates with emplace, not operator[]")

    for need in ("ORDER1886_SRT_DEPENDENCY_WORKLIST", "ORDER1886_SRT_GVN_SLOT_PARITY",
                 "ORDER1886_SRT_UNRESOLVED", "const size_t limit = pass_info.pointer_uses.size() + 1"):
        if need not in srt_impl:
            issues.append("Missing source-backed Order SRT dependency fix " + need)
    actual_libs = (root / "src/core/libraries/libs.cpp").read_text()
    if "BACHATA_SHADOW_PREFER_GUEST_FIOS2" not in actual_libs:
        issues.append("Early HLE still hijacks Shadow PSARC archive loader")
    actual_raster = (root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    if "BACHATA_SURFACE_FORMAT_TABLE_CHECK" not in actual_raster:
        issues.append("Unsupported AMD SurfaceFormat combinations still assert")
    # Confirm the actual CUSA08809 ShareUtility import is served, not ENOSYS.
    if ('BACHATA_SOTC_SHAREUTILITY_HLE_FROM_PORT' not in libc_boot or
        'LIB_FUNCTION("j7DlalBzHh8", "libSceShareUtility", 1,' not in libc_boot):
        issues.append("Shadow sceShareUtilityInitializeEx2 source-verified HLE missing")
    # The Order source-ported nonuniform shader data path must be fully linked.
    order_source = (root / "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp").read_text()
    order_resource = (root / "src/shader_recompiler/resource.h").read_text()
    order_recompiler = (root / "src/shader_recompiler/recompiler.cpp").read_text()
    order_rasterizer = (root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    order_spv = (root / "src/shader_recompiler/backend/spirv/spirv_emit_context.cpp").read_text()
    for needle, source in (
        ("ORDER1886_GPU_DYNAMIC_READCONST", order_source),
        ("LowerDynamicReadConstPass(IR::Program& program)", order_source),
        ("BufferType::ReadConst", order_resource),
        ("readconst_size_bytes", order_resource),
        ("LowerDynamicReadConstPass(program)", order_recompiler),
        ("const bool readconst = desc.buffer_type == Shader::BufferType::ReadConst", order_rasterizer),
        ("buffer.buffer_type != BufferType::ReadConst", order_spv),
    ):
        if needle not in source:
            issues.append("The Order divergent GPU ReadConst incomplete: " + needle)
    # Both donor paths must be connected, not merely copied into the repository.
    if "RegisterBachataSotcNgs2(sym)" not in actual_libs:
        issues.append("Shadow donor NGS2 mixer not registered before ELF relocation")
    if "IsBachataMappedImageBase(image.Address())" not in order_resource:
        issues.append("Order pre-specialization mapped image validation missing")
    if "null_desc.type = image_desc.is_written" not in order_rasterizer:
        issues.append("Order null image storage/sample binding contract missing")
    if "memory->ClampGpuRangeSize(vsharp.base_address, vsharp.GetSize())" not in order_rasterizer:
        issues.append("Order bounded GPU ReadConst lacks exact VMA clamp")
    # The frequently called PS4 libc _Sin NID requires Dinkumware quadrant ABI.
    libc_overlay = Path(__file__).resolve().parent.parent / "generic/android_libc_compat.cpp"
    libc_text = libc_overlay.read_text()
    if ('LIB_FUNCTION("MUjC4lbHrK4", "libSceLibcInternal"' not in libc_text or
        'GuestFflush(OrbisFILE* file)' not in libc_text):
        issues.append("FEX libcInternal fflush OrbisFILE bridge missing")
    if ('AddPrintfAlias(sym, "hcuQgD53UxM", PrintKind::Printf, "libSceLibcInternal")' not in libc_text or
        'LIB_FUNCTION("wLlFkwG9UcQ", "libSceLibcInternal"' not in libc_text):
        issues.append("Real namespace printf/time HLE exports missing")
    early_fios = (root / "src/core/libraries/libs.cpp").read_text()
    if ('BACHATA_FIOS2_EARLY_HLE_READY' not in early_fios or
        'Libraries::Fios2::RegisterLib(sym);' not in early_fios):
        issues.append("Early complete FIOS2 HLE registration absent")
    if ('ALIAS("cCXjU72Z0Ow", Fex__Sin)' not in libc_text or
        'double PS4_SYSV_ABI Fex__Sin(double x, unsigned qoff)' not in libc_text):
        issues.append("PS4 _Sin quadrant HLE alias absent from Android FEX")
    # Fiber functions were previously all ENOSYS because x86-only
    # shadPS4 fibers were deliberately omitted on Android ARM64.
    fiber = Path(__file__).resolve().parent.parent / "generic/android_fex_fiber.cpp"
    if not fiber.is_file():
        issues.append("Android native FEX guest fiber state bridge missing")
    else:
        fiber_source = fiber.read_text()
        required_nids = (
            "hVYD7Ou2pCQ", "asjUJJ+aa8s", "a0LLrZWac0M",
            "uq2Y5BFz0PE", "JzyT91ucGDc", "PFT2S-tJ7Uk",
            "B0ZX2hx9DMw", "avfGJ94g36Q", "ZqhZFuzKT6U",
        )
        for nid in required_nids:
            if nid not in fiber_source:
                issues.append("FEX fiber NID missing: " + nid)
        for marker in ("RegisterFexFiberBridge", "f.gpr[RSP]=r.rsp",
                       "std::make_shared<FiberBridge>", "Start(f,next,*incoming)"):
            if marker not in fiber_source:
                issues.append("FEX fiber true guest state logic missing: " + marker)
    # Catch CMake duplicate definitions *before* initializing NDK/FEX/cache.
    cmake = (root / "CMakeLists.txt").read_text()
    if "psarc_fs.cpp" in cmake:
        issues.append("Speculative PSARC engine still linked alongside verified Release MountAlias")
    if "saf_fs_backend.cpp" not in cmake:
        issues.append("Release direct SAF guest IFile missing from native core link")
    bridge = Path(__file__).resolve().parent.parent / "generic/android_saf_bridge.cpp"
    if not bridge.is_file() or (
            "BACHATA_RELEASE026_SAF_DIRECT_FD" not in bridge.read_text() or
            "BACHATA_RELEASE026_SAF_ALIAS" not in bridge.read_text() or
            "SourceGuestPath(path)" not in bridge.read_text()):
        issues.append("Android SAF direct provider fd or FIOS mount alias translation missing")
    if "android_fex_fiber.cpp" not in cmake:
        issues.append("FEX native fiber HLE absent from native core link")
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
