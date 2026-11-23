#!/usr/bin/env python3
"""Restore Release 0.2.6/0.2.7's real broker-fd-backed file opening.

The genuine Release exports SafFsBackend::Open and SafBrokerClient::Stat
(ELF f4ab401c...), while the Bionic port uses a /proc/self/fd symlink
workaround in MntPoints::Open. The new backend implements a POSIX
descriptor-backed IFile and case-insensitive game paths directly through
the existing Android BSF1 broker. This is a common-core change, not a
Shadow of the Colossus-specific path patch.
"""
from pathlib import Path


def only(data: str, old: str, new: str, title: str) -> str:
    count=data.count(old)
    if count!=1:raise RuntimeError(f"Release SAF native backend drift {title}: {count}")
    return data.replace(old,new,1)


def apply(root: Path) -> dict:
    fs=root/"src/core/file_sys/fs.cpp"
    cmake=root/"CMakeLists.txt"
    header_src=Path(__file__).with_name("saf_fs_backend.h")
    cpp_src=Path(__file__).with_name("saf_fs_backend.cpp")
    header_dst=root/"src/core/file_sys/backends/saf_fs_backend.h"
    cpp_dst=root/"src/core/file_sys/backends/saf_fs_backend.cpp"
    if header_dst.exists() or cpp_dst.exists():
        raise RuntimeError("Refusing duplicate shadPS4 SAF IFile implementation")
    if not header_src.is_file() or not cpp_src.is_file():
        raise RuntimeError("Missing native SAF descriptor backend units")
    bridge=Path(__file__).resolve().parents[1]/"generic"/"android_saf_bridge.cpp"
    bridge_h=bridge.with_suffix(".h")
    if "BACHATA_RELEASE026_SAF_DIRECT_FD" not in bridge.read_text():
        raise RuntimeError("Native Android BSF1 descriptor broker not implemented")
    if "std::optional<int> OpenFd(std::string_view guest_path)" not in bridge_h.read_text():
        raise RuntimeError("Direct Android BSF1 fd API not declared")

    text=fs.read_text()
    text=only(text,
        '#include "core/file_sys/backends/host_fs.h"\n',
        '#include "core/file_sys/backends/host_fs.h"\n'
        '#include "core/file_sys/backends/saf_fs_backend.h"\n',
        "direct SAF guest IFile header")
    old="""    if (!writable) {
        if (auto remote = BachataSaf::Resolve(*corrected)) {
            auto file = std::make_unique<HostFile>(*remote, mode, true);
            if (file->IsOpen()) return file;
        }
    }
#endif
    return nullptr;
}
"""
    new="""    if (!writable) {
        // BACHATA_RELEASE026_SAF_BACKEND: The real Release opens
        // independent file descriptors through SafFsBackend/SafBrokerClient.
        // Do not silently substitute a /proc/self/fd symlink HostFile path.
        return OpenSafGuestFile(*corrected);
    }
#endif
    return nullptr;
}
"""
    text=only(text,old,new,"direct provider fd instead of primary symlink")
    c=cmake.read_text()
    # The Release FIOS2 path does not register the speculative PSARC
    # archive backend. Attach the broker IFile unit to the actual native core.
    anchor='target_sources(shadps4 PRIVATE "'+str(
        Path(__file__).resolve().parents[1]/"generic"/"android_fex_fiber.cpp")+'")\n'
    c=only(c,anchor,
        anchor+'target_sources(shadps4 PRIVATE "'+str(cpp_dst)+'")\n',
        "link real SAF IFile into native Android shadPS4")
    fs.write_text(text)
    cmake.write_text(c)
    header_dst.write_text(header_src.read_text())
    cpp_dst.write_text(cpp_src.read_text())
    return {
        "reference":"authentic Bachata Release 0.2.6/0.2.7 ARM64 core",
        "difference":"SafFsBackend::Open existed, Bionic had a symlink-based fallback",
        "change":"Broker direct fd backed IFile with pread/seek/stat/map/RAII close",
        "guestPaths":"Android document-provider case-insensitive lookup on exact failure",
        "fallback":"None: Release direct broker IFile replaces old symlink read path",
        "gameSpecific":False,
    }
