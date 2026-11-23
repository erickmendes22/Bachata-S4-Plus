#!/usr/bin/env python3
"""Use the actual PSARC archive in generic FIOS2, not the app0 directory.

The pinned native ARM64 FEX fallback always mapped '/app0' as an archive and
returned success even when '/app0/build.psarc' was unreadable. CUSA05170
(Dragon Quest Builders) consequently cannot open its PhyreFIOS2 shaders.

This source patch adds a zlib PSARC read-only IBackend that can read from a
guest IFile (works with SAF), and a real FIOS2 mount/handle lifecycle.
It does not alter game content or silently extract large archives to RAM.
"""
from pathlib import Path

def replace_one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"PSARC source drift: {label}: expected 1 anchor, got {count}")
    return text.replace(old, new, 1)

def apply(root: Path) -> dict:
    original_files: dict[Path, str] = {}
    path_h = root / "src/core/file_sys/fs.h"
    path_cpp = root / "src/core/file_sys/fs.cpp"
    fios = root / "src/core/libraries/fios2/fios2.cpp"
    cmake = root / "CMakeLists.txt"
    src_h = Path(__file__).with_name("psarc_fs.h")
    src_cpp = Path(__file__).with_name("psarc_fs.cpp")
    dst_h = root / "src/core/file_sys/backends/psarc_fs.h"
    dst_cpp = root / "src/core/file_sys/backends/psarc_fs.cpp"
    for p in (path_h,path_cpp,fios,cmake):
        original_files[p] = p.read_text()
    if dst_h.exists() or dst_cpp.exists():
        raise RuntimeError("PSARC files already exist: refusing duplicate core patch")
    if not src_h.is_file() or not src_cpp.is_file():
        raise RuntimeError("Missing PSARC streaming reader sources")

    h = replace_one(original_files[path_h],
        "    void Unmount(const std::string& guest_folder);\n",
        "    void MountArchiveBackend(std::shared_ptr<IBackend> backend, "
        "const std::string& guest_folder);\n"
        "    void Unmount(const std::string& guest_folder);\n",
        "FS archive backend mount declaration")

    cpp = replace_one(original_files[path_cpp],
        "void MntPoints::Unmount(const std::string& guest_folder) {",
        """// BACHATA_FIOS2_REAL_PSARC_MOUNT: archive content is a read-only virtual
// backend, NOT the host /app0 folder. Its source may be a SAF-backed IFile.
void MntPoints::MountArchiveBackend(std::shared_ptr<IBackend> backend,
                                    const std::string& guest_folder) {
    if (!backend || guest_folder.empty() || guest_folder == "/") {
        return;
    }
    std::scoped_lock lock{m_mutex};
    const auto guest = RemoveTrailingSlashes(guest_folder);
    // Replace the same mount point instead of leaving stale duplicate
    // mappings when the game's archive mount is repeated.
    m_mnt_pairs.erase(std::remove_if(m_mnt_pairs.begin(), m_mnt_pairs.end(),
        [&](const MntPair& m){return m.mount == guest;}),m_mnt_pairs.end());
    std::vector<std::shared_ptr<IBackend>> backends;
    backends.push_back(std::move(backend));
    m_mnt_pairs.emplace_back(std::filesystem::path{},guest,true,std::move(backends));
}

void MntPoints::Unmount(const std::string& guest_folder) {""",
        "FS virtual archive mount implementation")

    f = replace_one(original_files[fios],
        '#include "core/file_sys/fs.h"\n',
        '#include "core/file_sys/fs.h"\n'
        '#include "core/file_sys/backends/psarc_fs.h"\n'
        '#include <atomic>\n',
        "Fios2 PSARC headers")
    f = replace_one(f,
        "s32 AllocateOpHandle(s64 actual_count) {",
        """std::mutex g_archive_mutex;
std::unordered_map<s32,std::string> g_archive_mounts;
std::atomic<s32> g_archive_next_handle{1000};
s32 AllocateOpHandle(s64 actual_count) {""",
        "real archive handles")
    begin = f.index("s32 PS4_SYSV_ABI sceFiosArchiveMountSync(")
    end = f.index("\ns64 PS4_SYSV_ABI sceFiosFileGetSizeSync(", begin)
    old = f[begin:end]
    if "Map the FIOS mount point to the same host folder" not in old:
        raise RuntimeError("Expected prior dangerous fake PSARC mount was already changed")
    new = """s32 PS4_SYSV_ABI sceFiosArchiveMountSync(const void* op_attr, s32* handle,
                                         const char* path, const char* mount_point,
                                         void* mount_buffer, s64 mount_buffer_size, s32 flags) {
    static_cast<void>(op_attr);
    static_cast<void>(mount_buffer);
    static_cast<void>(mount_buffer_size);
    static_cast<void>(flags);
    if (!handle || !path || !*path || !mount_point || !*mount_point) {
        LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_MOUNT_BAD_ARGS");
        return -1;
    }
    auto* mnt=Common::Singleton<Core::FileSys::MntPoints>::Instance();
    const std::string archive_path(path);
    const std::string guest_mount(mount_point);
    if (guest_mount.find("..") != std::string::npos || guest_mount.size()>1024) {
        LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_MOUNT_BAD_PREFIX");
        return -1;
    }
    auto source = mnt->Open(archive_path);
    if (!source) {
        // No fake mount. The extracted folder may be incomplete or the game
        // may be missing its actual PSARC asset. Report the exact input path.
        LOG_ERROR(Lib_SysModule,
                  "BIONIC_PSARC_ARCHIVE_UNAVAILABLE path='{}' mount='{}'",
                  archive_path, guest_mount);
        return -1;
    }
    auto backend=std::make_shared<Core::FileSys::PsarcBackend>(std::move(source));
    if (!backend->IsOpen()) {
        LOG_ERROR(Lib_SysModule,
                  "BIONIC_PSARC_ARCHIVE_UNSUPPORTED_OR_CORRUPT path='{}'",
                  archive_path);
        return -1;
    }
    mnt->MountArchiveBackend(backend,guest_mount);
    const s32 id=g_archive_next_handle.fetch_add(1);
    {
        std::lock_guard lock{g_archive_mutex};
        g_archive_mounts[id]=guest_mount;
    }
    *handle=id;
    LOG_INFO(Lib_SysModule,
             "BIONIC_PSARC_MOUNT_READY path='{}' mount='{}' handle={}",
             archive_path,guest_mount,id);
    return 0;
}
"""
    f=replace_one(f,old,new,"real FIOS2 archive mounting")
    f=replace_one(f,
        """s32 PS4_SYSV_ABI sceFiosArchiveUnmount(const void* op_attr, s32 handle) {
    static_cast<void>(op_attr);
    static_cast<void>(handle);
    LOG_INFO(Lib_SysModule, "[FIOS-HLE][ArchiveUnmount] handle={} (no-op)", handle);
    return 0;
}""",
        """s32 PS4_SYSV_ABI sceFiosArchiveUnmount(const void* op_attr, s32 handle) {
    static_cast<void>(op_attr);
    std::string mount;
    {
        std::lock_guard lock{g_archive_mutex};
        auto it=g_archive_mounts.find(handle);
        if (it==g_archive_mounts.end()) return -1;
        mount=std::move(it->second);
        g_archive_mounts.erase(it);
    }
    Common::Singleton<Core::FileSys::MntPoints>::Instance()->Unmount(mount);
    LOG_INFO(Lib_SysModule,"BIONIC_PSARC_UNMOUNT_DONE handle={} mount='{}'",handle,mount);
    return 0;
}""",
        "real archive unmount and cleanup")
    c = original_files[cmake]
    overlay_dir = Path(__file__).resolve()
    # Absolute overlay src is in the checkout; do not compile an old
    # preexisting archive parser from the pinned upstream source.
    src = str(dst_cpp)
    anchor = 'target_sources(shadps4 PRIVATE "' + str(
        Path(__file__).resolve().parents[1] / "generic" / "android_fex_fiber.cpp"
    ) + '")\n'
    c = replace_one(c,anchor,anchor +
        'target_sources(shadps4 PRIVATE "' + src + '")\n',
        "native core PSARC linker registration")

    # Commit all changes only after the source structure is validated.
    if "BACHATA_FIOS2_REAL_PSARC_MOUNT" not in cpp or (
        "BIONIC_PSARC_MOUNT_READY" not in f):
        raise RuntimeError("PSARC source interface integrity check failed")
    for path,content in ((path_h,h),(path_cpp,cpp),(fios,f),(cmake,c)):
        path.write_text(content)
    dst_h.write_text(src_h.read_text())
    dst_cpp.write_text(src_cpp.read_text())
    return {"result":"applied",
            "archive":"real PSARC zlib TOC with lazy block reads",
            "sourceFile":"MntPoints::Open works with SAF",
            "mount":"IBackend instead of fake app0 alias",
            "unmount":"real handle cleanup",
            "scope":"all games, no title-specific patches"}
