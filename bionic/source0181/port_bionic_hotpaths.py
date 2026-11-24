"""0.18.1 runtime defects evidenced by BS4-9319D72E / A24FBC66."""
from pathlib import Path


def edit(root, rel, old, new):
    p = root / rel
    s = p.read_text()
    if s.count(old) != 1:
        raise RuntimeError(f"Bionic hotpath source drift {rel}: {old[:100]}")
    p.write_text(s.replace(old, new, 1))


def apply(root: Path):
    fs = "src/core/libraries/kernel/file_system.cpp"
    edit(root, fs, "#include <sys/stat.h>",
         "#include <sys/stat.h>\n#ifdef __ANDROID__\n#include <sys/time.h>\n#include <cerrno>\n#endif")
    edit(root, fs, "s32 PS4_SYSV_ABI sceKernelFsync(s32 fd) {", r"""#ifdef __ANDROID__
// BS4-9319D72E SaveDataDialogThread: NLq2b1jOaN0 is sceKernelFutimes.
// Implement the actual file timestamp operation, not a success-only stub.
// Donor registration/ABI: shadPS4 5c3b6910, file_system.cpp.
s32 PS4_SYSV_ABI posix_futimes(s32 fd, const OrbisKernelTimeval* times) {
    if (times && (times[0].tv_usec < 0 || times[0].tv_usec >= 1000000 ||
                  times[1].tv_usec < 0 || times[1].tv_usec >= 1000000)) {
        *__Error() = POSIX_EINVAL;
        return -1;
    }
    auto* h = Common::Singleton<Core::FileSys::HandleTable>::Instance();
    auto* file = h->GetFile(fd);
    if (!file) { *__Error() = POSIX_EBADF; return -1; }
    std::scoped_lock lock{file->m_mutex};
    const auto type = file->type.load();
    if (type != Core::FileSys::FileType::Regular &&
        type != Core::FileSys::FileType::Directory) {
        *__Error() = POSIX_EINVAL; return -1;
    }
    bool read_only = false;
    auto* mnt = Common::Singleton<Core::FileSys::MntPoints>::Instance();
    const auto host_path = mnt->GetHostPath(file->m_guest_name, &read_only);
    if (read_only) { *__Error() = POSIX_EROFS; return -1; }
    struct timeval native_times[2]{};
    if (times) {
        for (unsigned i = 0; i < 2; ++i) {
            native_times[i].tv_sec = times[i].tv_sec;
            native_times[i].tv_usec = times[i].tv_usec;
        }
    }
    int result = -1;
    if (type == Core::FileSys::FileType::Regular) {
        auto* host = file->GetHostFile();
        if (!host) { *__Error() = POSIX_EROFS; return -1; }
        const int native_fd = static_cast<int>(host->GetFileMapping());
        result = ::futimes(native_fd, times ? native_times : nullptr);
    } else {
        if (host_path.empty()) { *__Error() = POSIX_EBADF; return -1; }
        result = ::utimes(host_path.c_str(), times ? native_times : nullptr);
    }
    if (result < 0) {
        SetPosixErrno(errno);
        return -1;
    }
    return 0;
}

s32 PS4_SYSV_ABI sceKernelFutimes(s32 fd, const OrbisKernelTimeval* times) {
    const s32 result = posix_futimes(fd, times);
    if (result < 0) return ErrnoToSceKernelError(*__Error());
    return result;
}
#endif

s32 PS4_SYSV_ABI sceKernelFsync(s32 fd) {""")
    edit(root, fs, '    LIB_FUNCTION("fTx66l5iWIA", "libkernel", 1, "libkernel", sceKernelFsync);',
         '''    LIB_FUNCTION("fTx66l5iWIA", "libkernel", 1, "libkernel", sceKernelFsync);
#ifdef __ANDROID__
    LIB_FUNCTION("NLq2b1jOaN0", "libkernel", 1, "libkernel", sceKernelFutimes);
    LIB_FUNCTION("+0EDo7YzcoU", "libkernel", 1, "libkernel", posix_futimes);
    LIB_FUNCTION("+0EDo7YzcoU", "libScePosix", 1, "libkernel", posix_futimes);
#endif''')
    sh = "src/shader_recompiler/ir/passes/srt.h"
    sc = "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp"
    ih = "src/shader_recompiler/info.h"
    edit(root, sh, "#pragma once", "#pragma once\n#include <vector>")
    edit(root, sh, "VAddr* source_addresses);", "std::vector<VAddr>& source_addresses);")
    edit(root, sc, "VAddr* source_addresses) {", "std::vector<VAddr>& source_addresses) {")
    edit(root, ih, "srt_guest_sources.data());", "srt_guest_sources);")
    edit(root, sc, "            if (source_addresses) source_addresses[b]=0;",
         "            source_addresses[b]=0;")
    edit(root, sc, "                if (source_addresses && guest_read_ok)",
         "                if (guest_read_ok)")
    # The old source list recorded CopyImm/CopyExpr DWORDs only, not the
    # address pair dereferenced by PushPtrImm/PushPtrExpr. Missing parents
    # make the GPU-to-CPU refresh inspect the stale pointer graph.
    edit(root, sc, "                cur = next & 0xFFFFFFFFFFFFULL;",
         """                // BACHATA_SRT_POINTER_PROVENANCE: both DWORDs of the
                // pointer are dependencies even if no Copy opcode reads them.
                const u64 local = reinterpret_cast<u64>(flat);
                if (!BachataCompat::Sotc608() && address >= 0x10000 && address < 0x10000000000ULL-7 &&
                    !(address >= local && address < local+16*sizeof(u32))) {
                    source_addresses.push_back(address);
                    source_addresses.push_back(address+sizeof(u32));
                }
                cur = next & 0xFFFFFFFFFFFFULL;""")
    # Use the same exact physical alias read as the scalar walker, but one
    # VMM lock for adjacent immediate reads with consecutive output slots.
    # If any page is unavailable, fall back to the original per-DWORD path.
    edit(root, sc, "            const bool null = cur < 0x10000ULL;\n            if (zeroed || null) {\n                flat[b] = 0;",
         """            const bool null = cur < 0x10000ULL;
            // BACHATA_SRT_CONTIGUOUS_READ: preserve each source address.
            if (!BachataCompat::Sotc608() && op == SrtOp::CopyImm &&
                !zeroed && !null && a < 0x3fffffe0u) {
                u32 count=1;
                for (; count<32; ++count) {
                    const u32 j=i+count*3;
                    if (static_cast<SrtOp>(std::atomic_ref<u32>(ops[j]).load(
                            std::memory_order_relaxed)) != SrtOp::CopyImm ||
                        ops[j+1]!=a+count || ops[j+2]!=b+count) break;
                }
                if (count>1) {
                    const u64 address=cur+u32(a<<2);
                    auto* memory=Core::Memory::Instance();
                    if (memory->TryReadBacking(address,flat+b,count*sizeof(u32))) {
                        for (u32 j=0;j<count;++j)
                            source_addresses[b+j]=address+j*sizeof(u32);
                        i+=(count-1)*3;
                        continue;
                    }
                }
            }
            if (zeroed || null) {
                flat[b] = 0;""")
    # Retain every compiled descriptor contract. Reject only candidates that
    # the existing StageSpecialization equality would reject anyway, before
    # executing SRT, walking VMA maps, or synchronizing GPU pages.
    pc = "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    edit(root, pc, "        auto& effective=*candidate.effective_info;",
         """        auto& effective=*candidate.effective_info;
        const auto& stored=candidate.spec;
        if (!BachataCompat::Sotc608()) {
            if ((!stored.buffers.empty() || !stored.images.empty() || !stored.samplers.empty()) &&
                stored.start!=start_binding) continue;
            // StageSpecialization only mutates runtime_info for tessellation.
            if (effective.sw_stage!=SwStage::TessellationControl &&
                effective.sw_stage!=SwStage::TessellationEval &&
                stored.runtime_info!=runtime_info) continue;
        }""")
    return {"save": "sceKernelFutimes actual timestamp HLE",
            "srt": "tracked parent pointer dwords; coalesced contiguous physical reads",
            "permutations": "reject provably incompatible bindings/runtime before SRT refresh"}
