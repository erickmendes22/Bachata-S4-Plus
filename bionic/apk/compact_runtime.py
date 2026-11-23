#!/usr/bin/env python3
"""Keep one working glibc fallback in the packaged Bachata runtime.

The original runtime.zip carries four full copies of shadPS4 (020, 023, 024,
025). Retain the latest fallback 025 plus its launch shim, glibc libraries,
FEX, Winlator assets, patches, tools and X11 data. Update the official file
manifest so runtime installation integrity checks remain consistent.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import re
import zipfile

RUNTIME_ZIP = "assets/runtime/runtime.zip"
RUNTIME_MANIFEST = "assets/runtime/manifest.json"
GUEST_BUILD_JSON = "usr/share/bachata/guest-runtime.json"
GUEST_BUILD_TXT = "usr/share/bachata/guest-runtime.txt"
GLIBC_KEEP = "host/shadps4-arm64-025"
GLIBC_DROP = {
    "host/shadps4-arm64-020",
    "host/shadps4-arm64-023",
    "host/shadps4-arm64-024",
}


def compact_runtime(
    outer: zipfile.ZipFile, *, runtime_version: str,
    core_revision: str, core_sha256: str,
) -> tuple[bytes, bytes]:
    """Change the *installer's* runtime identity when the native core changes.

    Otherwise a same-name APK install can retain the old extracted root and
    its old GUEST_RUNTIME_BUILD marker even if the APK contains a newer .so.
    """
    if not re.fullmatch(r"bachata-s4-plus-0\\.2\\.7-bionic-[0-9a-f]{16}", runtime_version):
        raise ValueError("Bionic runtime name must contain the native ELF digest")
    if not re.fullmatch(r"[0-9a-f]{40}", core_revision):
        raise ValueError("Invalid core source revision for runtime manifest")
    if not re.fullmatch(r"[0-9a-f]{64}", core_sha256):
        raise ValueError("Invalid core ELF SHA-256 for runtime manifest")
    if RUNTIME_ZIP not in outer.namelist() or RUNTIME_MANIFEST not in outer.namelist():
        raise ValueError("Original glibc runtime ZIP/manifest missing")
    contents = outer.read(RUNTIME_ZIP)
    manifest = json.loads(outer.read(RUNTIME_MANIFEST))
    old_runtime_version = manifest.get("runtimeVersion")
    if not isinstance(old_runtime_version, str) or not old_runtime_version:
        raise ValueError("Original runtime manifest lacks runtimeVersion")
    if old_runtime_version == runtime_version:
        raise ValueError("Native core changed but installer runtimeVersion was reused")
    manifest["runtimeVersion"] = runtime_version
    files = manifest.get("files")
    if not isinstance(files, list) or not all(isinstance(x, dict) for x in files):
        raise ValueError("Unsupported runtime manifest files schema")
    recorded = {x.get("path") for x in files}
    if not GLIBC_DROP.issubset(recorded) or GLIBC_KEEP not in recorded:
        raise ValueError("All 4 original glibc variants must be in runtime manifest")
    source = io.BytesIO(contents)
    output = io.BytesIO()
    guest_revision = "bionic-" + core_revision[:12]
    new_label = "Bachata S4+ native Bionic shadPS4 0.18.1 + FEX; glibc 025 fallback"
    with zipfile.ZipFile(source, "r") as z_in, zipfile.ZipFile(output, "w", allowZip64=True) as z_out:
        names = set(z_in.namelist())
        if not GLIBC_DROP.issubset(names) or GLIBC_KEEP not in names:
            raise ValueError("All 4 original glibc executables must be in runtime ZIP")
        if not {GUEST_BUILD_JSON, GUEST_BUILD_TXT}.issubset(names):
            raise ValueError("Official guest-runtime identity metadata missing")
        guest_info = json.loads(z_in.read(GUEST_BUILD_JSON))
        # Preserve the original 'built' schema used by Kotlin diagnostics;
        # only its identity fields change to describe the active native core.
        if guest_info.get("variant") != "built":
            raise ValueError("Unexpected guest runtime build metadata variant")
        guest_info["revision"] = guest_revision
        guest_info["sha256"] = core_sha256
        guest_info["label"] = new_label
        changed_metadata = {
            GUEST_BUILD_JSON: (json.dumps(guest_info, indent=2, ensure_ascii=False) + "\\n").encode("utf-8"),
            GUEST_BUILD_TXT: (
                "variant=built\\n" +
                f"revision={guest_revision}\\n" +
                f"sha256={core_sha256}\\n" +
                f"label={new_label}\\n"
            ).encode("utf-8"),
        }
        for info in z_in.infolist():
            if info.filename in GLIBC_DROP:
                print("GLIBC_OLD_BINARY_REMOVED", info.filename,
                      "uncompressed", info.file_size, "compressed", info.compress_size)
                continue
            z_out.writestr(copy.copy(info),
                           changed_metadata.get(info.filename, z_in.read(info.filename)))
    manifest["files"] = [x for x in files if x.get("path") not in GLIBC_DROP]
    for item in manifest["files"]:
        path = item.get("path")
        if path in changed_metadata:
            data = changed_metadata[path]
            item["size"] = len(data)
            item["sha256"] = hashlib.sha256(data).hexdigest()
    if not {GUEST_BUILD_JSON, GUEST_BUILD_TXT}.issubset(
            {x.get("path") for x in manifest["files"]}):
        raise ValueError("Guest-runtime metadata not tracked by extraction manifest")
    for item in manifest["files"]:
        if item.get("path") in GLIBC_DROP:
            raise ValueError("Removed executable retained in runtime manifest")
    # Do not mutate aggregate component metadata: only individual removed files
    # in the authoritative 'files' table change; all other file hashes remain.
    with zipfile.ZipFile(io.BytesIO(output.getvalue())) as z:
        if z.testzip() is not None:
            raise ValueError("Compacted glibc runtime ZIP failed CRC")
        if GLIBC_DROP & set(z.namelist()):
            raise ValueError("Obsolete glibc executables still packaged")
        if GLIBC_KEEP not in z.namelist():
            raise ValueError("The only required glibc executable was lost")
        if "host/shadps4-arm64-fex" not in z.namelist():
            raise ValueError("Original glibc/FEX launch shim was lost")
        for x in manifest["files"]:
            # Do not rehash all 600 files here; the archive entry CRC and each
            # unchanged per-file manifest hash are verified by the installer.
            if x.get("path") and x["path"] not in z.namelist():
                raise ValueError("Runtime manifest references removed file: " + x["path"])
    result = output.getvalue()
    with zipfile.ZipFile(io.BytesIO(result)) as check:
        for path, data in changed_metadata.items():
            if check.read(path) != data:
                raise ValueError("Updated guest runtime marker missing from archive: " + path)
    print("BIONIC_RUNTIME_REEXTRACTION_REQUIRED", "old", old_runtime_version,
          "new", runtime_version, "core", guest_revision)
    print("SINGLE_GLIBC_025_READY", "originalZIP", len(contents),
          "compactZIP", len(result), "manifestFiles", len(manifest["files"]))
    return result, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
