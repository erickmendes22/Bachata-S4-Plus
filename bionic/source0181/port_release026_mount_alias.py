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

Prefer exactly the Release alias; try PSARC only if /app0 is not mounted.
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
        "    void MountArchiveBackend(std::shared_ptr<IBackend> backend, const std::string& guest_folder);\n",
        "    // Working Release 0.2.6/0.2.7: preserve backend stack when aliasing /app0.\n"
        "    bool MountAlias(std::string_view source_guest, const std::string& alias_guest);\n"
        "    void MountArchiveBackend(std::shared_ptr<IBackend> backend, const std::string& guest_folder);\n",
        "filesystem alias API",
    )
    anchor = "void MntPoints::MountArchiveBackend(std::shared_ptr<IBackend> backend,\n"
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
    return true;
}

""" + anchor,
        "Release FIOS2 filesystem backend clone implementation",
    )
    # Original 0.2.6 and 0.2.7 ignore the archive path when /app0 is already
    # mounted, and MountAlias("/app0", prefix) instead.  Do that BEFORE
    # speculative PSARC header parsing.  Preserve the parser as a genuine
    # fallback if no /app0 source exists (never fake a successful mount).
    f = replace_once(
        f,
        """    if (!handle || !path || !*path || !mount_point || !*mount_point) {
        LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_MOUNT_BAD_ARGS");
        return -1;
    }""",
        """    if (!handle) {
        LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_MOUNT_BAD_ARGS no handle");
        return -1;
    }""",
        "restore optional archive path and prefix like Release",
    )
    f = replace_once(
        f,
        """    const std::string archive_path(path);
    const std::string guest_mount(mount_point);""",
        """    const std::string archive_path(path ? path : "");
    const std::string guest_mount(mount_point && *mount_point
                                  ? mount_point : "/archive/mount/point");""",
        "Release FIOS2 default namespace",
    )
    f = replace_once(
        f,
        """    auto source = mnt->Open(archive_path);
    if (!source) {""",
        """    // Official Release behavior: alias existing guest /app0 backends.
    // The previous 0.18.1 port incorrectly required a physical host
    // directory, which breaks SAF mounts and archive-relative paths.
    if (mnt->MountAlias("/app0", guest_mount)) {
        const s32 id=g_archive_next_handle.fetch_add(1);
        {
            std::lock_guard lock{g_archive_mutex};
            g_archive_mounts[id]=guest_mount;
            g_release_alias_handles.insert(id);
        }
        *handle=id;
        LOG_INFO(Lib_SysModule,
                 "BACHATA_FIOS2_RELEASE_ALIAS_READY archive='{}' alias='{}' handle={}",
                 archive_path,guest_mount,id);
        return 0;
    }
    // Only when no /app0 guest backend exists should an actual
    // PSARC archive be attempted, without pretending a failure succeeded.
    auto source = archive_path.empty() ? std::unique_ptr<Core::FileSys::IFile>{}
                                        : mnt->Open(archive_path);
    if (!source) {""",
        "alias first, PSARC fallback",
    )
    f = replace_once(
        f,
        """std::unordered_map<s32,std::string> g_archive_mounts;
std::atomic<s32> g_archive_next_handle{1000};""",
        """std::unordered_map<s32,std::string> g_archive_mounts;
std::unordered_set<s32> g_release_alias_handles;
std::atomic<s32> g_archive_next_handle{1000};""",
        "track release alias handle lifecycle",
    )
    f = replace_once(
        f,
        '#include <atomic>\n',
        '#include <atomic>\n#include <unordered_set>\n',
        "alias handle std::unordered_set include",
    )
    f = replace_once(
        f,
        """    std::string mount;
    {
        std::lock_guard lock{g_archive_mutex};
        auto it=g_archive_mounts.find(handle);
        if (it==g_archive_mounts.end()) return -1;
        mount=std::move(it->second);
        g_archive_mounts.erase(it);
    }
    Common::Singleton<Core::FileSys::MntPoints>::Instance()->Unmount(mount);
    LOG_INFO(Lib_SysModule,"BIONIC_PSARC_UNMOUNT_DONE handle={} mount='{}'",handle,mount);""",
        """    std::string mount;
    bool release_alias=false;
    {
        std::lock_guard lock{g_archive_mutex};
        auto it=g_archive_mounts.find(handle);
        if (it==g_archive_mounts.end()) return -1;
        mount=std::move(it->second);
        g_archive_mounts.erase(it);
        release_alias=g_release_alias_handles.erase(handle)>0;
    }
    // The 0.2.6 Release's FIOS2 unmount is a no-op for alias-backed
    // mounts; do not invalidate files still opened under the alias.
    if (!release_alias) {
        Common::Singleton<Core::FileSys::MntPoints>::Instance()->Unmount(mount);
    }
    LOG_INFO(Lib_SysModule,"BACHATA_FIOS2_RELEASE_UNMOUNT handle={} alias={} mount='{}'",
             handle,release_alias,mount);""",
        "preserve working release alias unmount semantics",
    )
    for p, contents in ((header,h),(implementation,cpp),(fios,f)):
        p.write_text(contents)
    return {
        "releaseReference": "0.2.6 and 0.2.7 share authentic f4ab401c... ELF",
        "ported": "MntPoints::MountAlias('/app0', prefix) with shared backend layers",
        "archive": "Preserve Release guest alias first, PSARC as explicit fallback",
        "lifetime": "Release alias unmount avoids invalidating opened backend handles",
        "requiresOnDeviceValidation": True,
    }
