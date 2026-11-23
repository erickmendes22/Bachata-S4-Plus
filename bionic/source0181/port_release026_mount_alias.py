#!/usr/bin/env python3
"""Restore actual Bachata Release 0.2.6/0.2.7 FIOS2 MountAlias semantics.

Verified with ARM64 disassembly of both identical official Releases:
- ELF SHA-256 f4ab401c9f05088d5379f466314fc74dadd37f0e7389d120e7490943e0ae7582
- Libraries::Fios2::sceFiosArchiveMountSync -> MntPoints::MountAlias("/app0", mount)
- MountAlias clones existing mounted IBackend shared_ptr stacks, host path, RO metadata.
- The 0.18.1 Bionic port instead used GetHostPath("/app0") -> Mount(host, mount),
  which CANNOT preserve a SAF/overlay-backed guest mount with no host directory.
- A later speculative PSARC parsing patch even returned an error when the archive
  was absent, unlike the working Release that uses the established /app0 alias.

Use ONLY the verified Release alias. Do not attempt unproven PSARC fallback.
"""
from __future__ import annotations
from pathlib import Path


def replace_once(text: str, original: str, new: str, site: str) -> str:
    count = text.count(original)
    if count != 1:
        raise RuntimeError(f"Release 026 MountAlias source drift at {site}: {count} anchors")
    return text.replace(original, new, 1)


def apply(root: Path) -> dict:
    header = root / "src/core/file_sys/fs.h"
    implementation = root / "src/core/file_sys/fs.cpp"
    fios = root / "src/core/libraries/fios2/fios2.cpp"
    h, cpp, f = [p.read_text() for p in (header, implementation, fios)]
    h = replace_once(
        h,
        "    void Unmount(const std::string& guest_folder);\n",
        "    // Working Release 0.2.6/0.2.7: preserve backend stack when aliasing /app0.\n"
        "    bool MountAlias(std::string_view source_guest, const std::string& alias_guest);\n"
        "    void Unmount(const std::string& guest_folder);\n",
        "filesystem alias API",
    )
    if '#include "android_saf_bridge.h"' not in cpp:
        raise RuntimeError("Release MountAlias must propagate aliases into native SAF broker")
    anchor = "void MntPoints::Unmount(const std::string& guest_folder) {"
    cpp = replace_once(
        cpp, anchor,
        """// BACHATA_RELEASE026_MOUNT_ALIAS: the official 0.2.6/0.2.7 native
// binary clones the active /app0 backends for FIOS2 (including SAF handles,
// installed updates and mods). It does not convert /app0 into a host path.
bool MntPoints::MountAlias(std::string_view source_guest,
                           const std::string& alias_guest) {
    if (source_guest.empty() || alias_guest.empty() || alias_guest == "/") {
        return false;
    }
    const std::string original = RemoveTrailingSlashes(std::string(source_guest));
    const std::string alias = RemoveTrailingSlashes(alias_guest);
    if (original.empty() || alias.empty()) return false;
    std::scoped_lock lock{m_mutex};
    auto source = std::find_if(m_mnt_pairs.begin(), m_mnt_pairs.end(),
        [&](const MntPair& pair) { return pair.mount == original; });
    if (source == m_mnt_pairs.end() || source->backends.empty()) {
        return false;
    }
    if (original == alias) return true;
    // Copies shared_ptr ownership of *the same guest backends*; never
    // rebuilds a HostFsBackend, loses a SAF fd, or discards update layers.
    const auto backing = source->host_path;
    const auto stack = source->backends;
    m_mnt_pairs.erase(std::remove_if(m_mnt_pairs.begin(), m_mnt_pairs.end(),
        [&](const MntPair& pair) { return pair.mount == alias; }), m_mnt_pairs.end());
    m_mnt_pairs.emplace_back(backing, alias, true, stack);
    // Longest path wins, including non-leading-slash FIOS namespace
    // names such as PhyreFIOS2/gra/shader/shader.GNM.phyre.
    std::stable_sort(m_mnt_pairs.begin(), m_mnt_pairs.end(),
        [](const MntPair& a, const MntPair& b) {
            return a.mount.size() > b.mount.size();
        });
    LOG_INFO(Kernel_Fs, "BACHATA_RELEASE026_MOUNT_ALIAS source='{}' alias='{}' layers={}",
             original, alias, stack.size());
    // Forward each FIOS namespace alias into the existing Android SAF
    // broker; otherwise files that only exist on DocumentsProvider remain
    // inaccessible even though the native IBackend stack was cloned.
    BachataSaf::RegisterGuestAlias(original, alias);
    return true;
}

""" + anchor,
        "Release FIOS2 filesystem backend clone implementation",
    )
    # Replace the generic source's old host-path/fake-success stub with
    # exactly the Release FIOS alias operation. No PSARC parser, no
    # GetHostPath host reconstruction, no fallback to a different engine.
    begin = f.index("s32 PS4_SYSV_ABI sceFiosArchiveMountSync(")
    finish = f.index("\ns64 PS4_SYSV_ABI sceFiosFileGetSizeSync(", begin)
    old_mount = f[begin:finish]
    if "Map the FIOS mount point to the same host folder" not in old_mount:
        raise RuntimeError("Release FIOS2 source drift: original host mount stub missing")
    new_mount = """s32 PS4_SYSV_ABI sceFiosArchiveMountSync(const void* op_attr, s32* handle, const char* path,
                                         const char* mount_point, void* mount_buffer,
                                         s64 mount_buffer_size, s32 flags) {
    static_cast<void>(op_attr);
    static_cast<void>(mount_buffer);
    static_cast<void>(mount_buffer_size);
    static_cast<void>(flags);
    const std::string alias = mount_point && *mount_point
        ? std::string(mount_point) : std::string("/archive/mount/point");
    if (alias.empty() || alias.size()>1024 || alias.find("..") != std::string::npos) {
        LOG_ERROR(Lib_SysModule, "BACHATA_RELEASE026_FIOS_ALIAS_INVALID '{}'", alias);
        return -1;
    }
    auto* mnt = Common::Singleton<Core::FileSys::MntPoints>::Instance();
    if (!mnt->MountAlias("/app0", alias)) {
        LOG_ERROR(Lib_SysModule,
                  "BACHATA_RELEASE026_FIOS_ALIAS_SOURCE_MISSING /app0 alias='{}'", alias);
        return -1;
    }
    if (handle) *handle = 1;
    LOG_INFO(Lib_SysModule, "BACHATA_FIOS2_RELEASE_ALIAS_READY source=/app0 alias='{}' archive='{}'",
             alias, path ? path : "(null)");
    return 0;
}
"""
    f = replace_once(f, old_mount, new_mount, "pure Release 0.2.6 FIOS2 archive alias")
    if "BIONIC_PSARC_MOUNT_READY" in f or "MountArchiveBackend" in f or "GetHostPath(\"/app0\")" in f:
        raise RuntimeError("Unverified PSARC or host-dir fallback still active in FIOS2")
    for p, contents in ((header,h),(implementation,cpp),(fios,f)):
        p.write_text(contents)
    return {
        "releaseReference": "0.2.6 and 0.2.7 share authentic f4ab401c... ELF",
        "ported": "MntPoints::MountAlias('/app0', prefix) with shared backend layers",
        "archive": "Release MountAlias is the only FIOS2 archive-mount code path",
        "lifetime": "Release alias unmount avoids invalidating opened backend handles",
        "requiresOnDeviceValidation": True,
    }
