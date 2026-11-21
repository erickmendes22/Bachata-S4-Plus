#!/usr/bin/env python3
"""Fix two independently observed 0.21.1 Android/FEX runtime contracts.

1. SAF streams are opened through the broker's independent fd. Query their
   size through *that fd*, not a /proc/self/fd mirror symlink that can become
   stale when the broker's cached descriptor is evicted/reused.
2. The CUSA00785 trace reports ENOTSUP (95) on sceKernelSignalSema's FEX
   HLE operation. Register an explicitly typed, ordinary AArch64 shim with
   only the two integer arguments supported by the bridge; preserve the
   native/x86 path and the original Orbis semaphore behavior.
"""
import argparse
from pathlib import Path


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text()
    n = text.count(before)
    if n != 1:
        raise RuntimeError(f"{path}: expected one pinned 0.21.1 anchor; got {n}")
    path.write_text(text.replace(before, after, 1))


def fix_io_file(root: Path) -> None:
    p = root / "src/common/io_file.cpp"
    replace_once(
        p,
        "#else\n#include <unistd.h>\n#endif",
        "#else\n#include <sys/stat.h>\n#include <unistd.h>\n#endif",
    )
    replace_once(
        p,
        """bool IOFile::Flush() const {
    if (!IsOpen()) {
        return false;
    }

    errno = 0;
""",
        """bool IOFile::Flush() const {
    if (!IsOpen()) {
        return false;
    }
    // BIONIC_021_SAF_READONLY_FLUSH: a broker-backed input stream has no
    // unwritten data; fflush on read-only Android fdopen() can fail EBADF.
    if (file_access_mode == FileAccessMode::Read) {
        return true;
    }

    errno = 0;
""",
    )
    replace_once(
        p,
        """    // Flush any unwritten buffered data into the file prior to retrieving the file size.
    std::fflush(file);

    std::error_code ec;
""",
        """    // BIONIC_021_SAF_FSTAT_OPEN_FD: /proc/self/fd/N mirrors may become
    // stale after broker FD-cache eviction. Never query the size of a
    // *different* fd by following the mirror's path.
#ifndef _WIN32
    if (file_access_mode != FileAccessMode::Read) {
        std::fflush(file);
    }
    struct stat opened_file{};
    if (::fstat(::fileno(file), &opened_file) == 0 &&
        S_ISREG(opened_file.st_mode) && opened_file.st_size >= 0) {
        return static_cast<u64>(opened_file.st_size);
    }
#else
    std::fflush(file);
#endif

    std::error_code ec;
""",
    )
    print("BIONIC_021_SAF_IO_OPEN_FD_SIZE_AND_READONLY_FLUSH_FIXED")


def fix_fex_semaphore(root: Path) -> None:
    p = root / "src/core/libraries/kernel/threads/semaphore.cpp"
    replace_once(
        p,
        '    LIB_FUNCTION("4czppHBiriw", "libkernel", 1, "libkernel", sceKernelSignalSema);',
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BIONIC_021_FEX_SIGNAL_SEMA_TYPED_HLE: the Android FEX trace reported
    // EOPNOTSUPP/ENOTSUP (95) for this HLE operation. Force the bridge to
    // register a plain two-integer signature; keep all guest-side semantics
    // and error codes in the actual sceKernelSignalSema implementation.
    LIB_FUNCTION("4czppHBiriw", "libkernel", 1, "libkernel",
                 +[](u32 sem, s32 signal_count) -> s32 {
                     return sceKernelSignalSema(sem, signal_count);
                 });
#else
    LIB_FUNCTION("4czppHBiriw", "libkernel", 1, "libkernel", sceKernelSignalSema);
#endif""",
    )
    print("BIONIC_021_FEX_SIGNAL_SEMA_TYPED_HLE_REGISTERED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    root = parser.parse_args().source.resolve()
    fix_io_file(root)
    fix_fex_semaphore(root)


if __name__ == "__main__":
    main()
