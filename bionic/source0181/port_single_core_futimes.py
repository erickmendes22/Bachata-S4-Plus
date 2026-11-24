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
    return {"save":"native timestamp HLE"}
