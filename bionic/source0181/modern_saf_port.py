#!/usr/bin/env python3
"""Port Bachata's zero-copy Android SAF broker to the shadPS4 0.18.1 VFS.

The 0.18.1 mount layer is backend-based (IBackend/IFile). Old FEX 0.16.1
IterateDirectory text patches do NOT implement Open/Exists/IsDirectory/OpenDir
in this API; those must be bridged explicitly or /app0 sees only staged files.
Never copy whole games under app data and never synthesize missing content.
"""
from __future__ import annotations
from pathlib import Path


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"modern VFS {label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def update_method(source: str, start: str, end: str, old: str, new: str) -> str:
    lo = source.find(start)
    if lo < 0:
        raise RuntimeError("modern VFS method absent: " + start)
    hi = source.find(end, lo + len(start))
    if hi < 0:
        raise RuntimeError("modern VFS method end absent: " + end)
    method = source[lo:hi]
    method = replace_once(method, old, new, start)
    return source[:lo] + method + source[hi:]


def apply(root: Path) -> dict:
    fs = root / "src/core/file_sys/fs.cpp"
    header = root / "src/core/file_sys/fs.h"
    text = fs.read_text(encoding="utf-8")
    head = header.read_text(encoding="utf-8")
    required = (
        "class MergedDirectory final", "MntPoints::OpenDir(",
        "std::shared_ptr<IBackend> MntPoints::CreateBackend(",
        "BachataSaf::Resolve(corrected_path)",
    )
    for marker in required:
        if marker not in text:
            raise RuntimeError("0.18.1 VFS/SAF integration missing " + marker)
    if "std::vector<std::shared_ptr<IBackend>> backends" not in head:
        raise RuntimeError("0.18.1 backend-based VFS header not selected")
    if '#include "android_saf_bridge.h"' not in text:
        raise RuntimeError("Bachata SAF bridge include not applied")

    # The old IterateDirectory adapter relied on local staging paths and
    # cannot be applied verbatim to the new layered backend iterator.
    text = update_method(
        text,
        "void MntPoints::IterateDirectory(std::string_view guest_directory,",
        "bool MntPoints::Exists(std::string_view guest_path)",
        "    }\n}\n",
        """    }
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    std::vector<BachataSaf::Entry> remote_entries;
    if (BachataSaf::List(corrected, remote_entries)) {
        for (const auto& entry : remote_entries) {
            if (!emitted.insert(emit_key(entry.name)).second) continue;
            // Preserve lazy file opening; never open all directory entries.
            callback(base_host / entry.name, !entry.directory);
        }
    }
#endif
}
""",
    )
    # Cheap STAT for all paths absent from native staging and update layers.
    text = update_method(
        text, "bool MntPoints::Exists(std::string_view guest_path)",
        "bool MntPoints::IsDirectory(std::string_view guest_path)",
        "    return false;\n}\n",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    return BachataSaf::StatPath(*corrected);
#else
    return false;
#endif
}
""",
    )
    text = update_method(
        text, "bool MntPoints::IsDirectory(std::string_view guest_path)",
        "std::unique_ptr<IFile> MntPoints::Open(std::string_view guest_path, bool writable)",
        "    return false;\n}\n",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    bool is_directory = false;
    return BachataSaf::StatPath(*corrected, &is_directory) && is_directory;
#else
    return false;
#endif
}
""",
    )
    # Retain the layered native backend path (game updates/mods first); only
    # fall back to an independent provider descriptor for a missing read.
    text = update_method(
        text,
        "std::unique_ptr<IFile> MntPoints::Open(std::string_view guest_path,\n",
        "std::unique_ptr<IDirectory> MntPoints::OpenDir(std::string_view guest_path)",
        "    return nullptr;\n}\n",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    if (!writable) {
        if (auto remote = BachataSaf::Resolve(*corrected)) {
            auto file = std::make_unique<HostFile>(*remote, mode, true);
            if (file->IsOpen()) return file;
        }
    }
#endif
    return nullptr;
}
""",
    )
    text = update_method(
        text,
        "std::unique_ptr<IDirectory> MntPoints::OpenDir(std::string_view guest_path)",
        "std::optional<std::vector<u8>> MntPoints::ReadFile(std::string_view guest_path)",
        "    if (!found) {\n        return nullptr;\n    }\n",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    std::vector<BachataSaf::Entry> remote_entries;
    if (BachataSaf::List(*corrected, remote_entries)) {
        found = true;
        for (const auto& remote : remote_entries) {
            const auto key =
                NeedsCaseInsensitiveSearch ? Common::ToLower(remote.name) : remote.name;
            if (!seen.insert(key).second) continue;
            entries.push_back(DirEntry{remote.name, remote.directory, remote.size});
        }
    }
#endif
    if (!found) {
        return nullptr;
    }
""",
    )
    fs.write_text(text, encoding="utf-8")
    return {
        "filesystemSource": "shadPS4 0.18.1 backend-based VFS",
        "backedMethods": ["GetHostPath", "IterateDirectory", "Exists",
                          "IsDirectory", "Open", "OpenDir", "ReadFile via Open"],
        "remoteContentByteCopied": False,
        "usesIndependentProviderFd": True,
    }
