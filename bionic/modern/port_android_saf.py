#!/usr/bin/env python3
"""Wire Bachata's real BSF1 SAF transport into all shadPS4 0.21.1 VFS operations.

shadPS4 0.21.1 calls MntPoints::Exists/Open/Stat/OpenDir through the IBackend
stack. Its older MountSaf only populated MntPair::saf, leaving backends empty
and making /app0/eboot.bin invisible despite a connected SAF broker.
"""
from pathlib import Path
import argparse


def once(file: Path, original: str, replacement: str) -> None:
    source = file.read_text()
    count = source.count(original)
    if count != 1:
        raise RuntimeError(f"{file}: expected one 0.21.1 anchor; found {count}: {original[:95]!r}")
    file.write_text(source.replace(original, replacement, 1))


def port(root: Path, overlay: Path) -> None:
    if not (overlay / "android_saf_stack.h").is_file():
        raise RuntimeError("Missing modern IBackend-to-BSF1 adapter header")
    base = root / "src/core/file_sys"
    saf_h = base / "saf_fs_backend.h"
    once(saf_h,
         "    std::filesystem::path Resolve(std::string_view guest_path);\n",
         "    std::filesystem::path Resolve(std::string_view guest_path);\n"
         "    // BIONIC_021_SAF_BROKER_METADATA: no fd OPEN for directory listing or stat.\n"
         "    bool StatEntry(std::string_view guest_path, SafEntry& entry) const;\n"
         "    bool ListEntries(std::string_view guest_path, std::vector<SafEntry>& entries) const;\n")

    saf_cpp = base / "saf_fs_backend.cpp"
    functions = r"""
// BIONIC_021_SAF_BROKER_METADATA: the same BSF1 broker supplies metadata,
// while files are opened lazily and independently via the existing fd hook.
bool SafFsBackend::StatEntry(std::string_view guest_path, SafEntry& out) const {
    if (!Matches(guest_path)) return false;
    const std::string rel = RelativePath(guest_path);
    const auto fallback = FallbackPath(guest_path);
    std::error_code ec;
    if (!fallback.empty() && std::filesystem::exists(fallback, ec) && !ec) {
        out = SafEntry{};
        out.name = std::filesystem::path(guest_path).filename().string();
        out.is_directory = std::filesystem::is_directory(fallback, ec);
        if (ec) return false;
        if (!out.is_directory) {
            out.size = std::filesystem::file_size(fallback, ec);
            if (ec) return false;
        }
        return true;
    }
    if (rel.empty()) {
        if (!client) return false;
        // Some DocumentsProviders expose the tree root only to READDIR.
        SafEntry root_entry;
        if (client->Stat("", root_entry)) {
            out = std::move(root_entry);
            return out.is_directory;
        }
        std::vector<SafEntry> children;
        if (client->ReadDir("", children) || client->ReadDir(".", children)) {
            out = SafEntry{};
            out.is_directory = true;
            return true;
        }
        return false;
    }
    return client && client->Stat(rel, out);
}

bool SafFsBackend::ListEntries(std::string_view guest_path,
                               std::vector<SafEntry>& out) const {
    if (!Matches(guest_path)) return false;
    const std::string rel = RelativePath(guest_path);
    out.clear();
    bool available = false;
    if (client) {
        available = client->ReadDir(rel, out);
        if (!available && rel.empty()) available = client->ReadDir(".", out);
    }

    // Directly staged eboot/sce_sys files have precedence, but they must
    // NEVER hide other game assets that exist only through the SAF broker.
    const auto fallback = FallbackPath(guest_path);
    std::error_code ec;
    if (!fallback.empty() && std::filesystem::is_directory(fallback, ec) && !ec) {
        available = true;
        for (const auto& item : std::filesystem::directory_iterator(fallback, ec)) {
            if (ec) break;
            SafEntry entry{};
            entry.name = item.path().filename().string();
            entry.is_directory = item.is_directory(ec);
            if (ec) { ec.clear(); continue; }
            if (!entry.is_directory) {
                entry.size = item.file_size(ec);
                if (ec) { ec.clear(); continue; }
            }
            auto existing = std::find_if(out.begin(), out.end(),
                [&](const SafEntry& candidate) { return candidate.name == entry.name; });
            if (existing == out.end()) out.push_back(std::move(entry));
            else *existing = std::move(entry);
        }
    }
    return available;
}

"""
    once(saf_cpp,
         "bool SafFsBackend::Iterate(\n",
         functions + "bool SafFsBackend::Iterate(\n")
    once(saf_cpp, "#include <system_error>\n",
         "#include <algorithm>\n#include <system_error>\n")

    fs = base / "fs.cpp"
    once(fs, '#include "core/file_sys/fs.h"\n',
         '#include "core/file_sys/fs.h"\n#include "android_saf_stack.h"\n')
    old = (
        "    pair.saf = std::move(backend);\n"
        "    m_mnt_pairs.emplace_back(std::move(pair));\n"
    )
    new = (
        "    pair.saf = std::move(backend);\n"
        "    // BIONIC_021_SAF_VFS_MOUNT: 0.21.1 uses IBackend for EVERY game\n"
        "    // operation, not just GetHostPath/IterateDirectory. Preserve the\n"
        "    // original SAF marker for host-path mirroring, and add the bridge\n"
        "    // to the real VFS backend stack for Exists/Open/Stat/OpenDir.\n"
        "    pair.backends.push_back(std::make_shared<SafStackBackend>(\n"
        "        pair.saf, guest_folder_sanitized));\n"
        "    m_mnt_pairs.erase(std::remove_if(m_mnt_pairs.begin(), m_mnt_pairs.end(),\n"
        "        [&](const MntPair& existing) { return existing.mount == guest_folder_sanitized; }),\n"
        "        m_mnt_pairs.end());\n"
        "    m_mnt_pairs.emplace_back(std::move(pair));\n"
        "    std::stable_sort(m_mnt_pairs.begin(), m_mnt_pairs.end(),\n"
        "        [](const MntPair& a, const MntPair& b) { return a.mount.size() > b.mount.size(); });\n"
        "    LOG_INFO(Kernel_Fs, \"BIONIC_021_SAF_VFS_MOUNT_READY {}\", guest_folder_sanitized);\n"
    )
    once(fs, old, new)

    # 0.21.1 still runs its legacy SAF Iterate() on paths used by
    # getdents and trophy scans. The old version preferred a staged folder
    # exclusively and thereby HID every sibling served only by SAF.
    # Use the same merged BSF1 READDIR + staged view as OpenDir.
    iter_source = saf_cpp.read_text()
    begin = iter_source.find("bool SafFsBackend::Iterate(\n")
    end = iter_source.find("\n} // namespace Core::FileSys", begin)
    if begin < 0 or end < 0 or iter_source.count("bool SafFsBackend::Iterate(\n") != 1:
        raise RuntimeError("Modern SafFsBackend::Iterate signature changed")
    iteration = """bool SafFsBackend::Iterate(
    std::string_view guest_path,
    const std::function<void(const std::filesystem::path&, bool)>& callback) {
    // BIONIC_021_SAF_MERGED_DIRECTORY: no staged-only early return.
    std::vector<SafEntry> entries;
    if (!ListEntries(guest_path, entries)) return false;
    for (const auto& entry : entries) {
        if (entry.name.empty() || entry.name == "." || entry.name == ".." ||
            entry.name.find('/') != std::string::npos ||
            entry.name.find('\\\\') != std::string::npos) continue;
        std::string child{guest_path};
        if (!child.ends_with('/')) child.push_back('/');
        child += entry.name;
        const auto resolved = Resolve(child);
        if (!resolved.empty()) callback(resolved, !entry.is_directory);
    }
    return true;
}
"""
    saf_cpp.write_text(iter_source[:begin] + iteration + iter_source[end:])

    # Report genuine SAF failures to the Java frontend instead of crashing
    # with an assertion after the VFS mount. Do not fake a valid eboot.
    emulator = root / "src/emulator.cpp"
    old_assert = ('    ASSERT_MSG(mnt->Exists(guest_eboot_path), '
                  '"Guest app\\'s main executable {} does not exist",\\n'
                  '               guest_eboot_path);\\n')
    new_assert = """#if defined(__ANDROID__) && defined(ENABLE_BACHATA_RUNTIME)
    if (!mnt->Exists(guest_eboot_path)) {
        LOG_ERROR(Loader, "BIONIC_021_SAF_EBOOT_UNAVAILABLE: VFS path {} not reachable",
                  guest_eboot_path);
        if (onRuntimeError) onRuntimeError("CONTENT_UNAVAILABLE");
        if (onRuntimeStopped) onRuntimeStopped(1);
        return;
    }
    LOG_INFO(Loader, "BIONIC_021_SAF_EBOOT_RESOLVED {}", guest_eboot_path);
#else
    ASSERT_MSG(mnt->Exists(guest_eboot_path), "Guest app's main executable {} does not exist",
               guest_eboot_path);
#endif
"""
    once(emulator, old_assert, new_assert)

    # Android native sources are outside the rehydrated upstream checkout.
    # Add exactly this source directory as an include for the shadPS4 target.
    cmake = root / "CMakeLists.txt"
    once(cmake, "set_target_properties(shadps4 PROPERTIES OUTPUT_NAME \"bachata_bionic_core\")\n",
         "set_target_properties(shadps4 PROPERTIES OUTPUT_NAME \"bachata_bionic_core\")\n"
         + 'target_include_directories(shadps4 PRIVATE "' + str(overlay.resolve()) + '")\n')
    print("BIONIC_021_SAF_FULL_VFS_CONNECTED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--overlay", type=Path, default=Path("bionic/modern"))
    args = ap.parse_args()
    port(args.source.resolve(), args.overlay.resolve())
