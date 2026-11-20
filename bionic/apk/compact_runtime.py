#!/usr/bin/env python3
"""Keep one working glibc fallback in the packaged Bachata runtime.

The original runtime.zip carries four full copies of shadPS4 (020, 023, 024,
025). Retain the latest fallback 025 plus its launch shim, glibc libraries,
FEX, Winlator assets, patches, tools and X11 data. Update the official file
manifest so runtime installation integrity checks remain consistent.
"""
from __future__ import annotations

import copy
import io
import json
import zipfile

RUNTIME_ZIP = "assets/runtime/runtime.zip"
RUNTIME_MANIFEST = "assets/runtime/manifest.json"
GLIBC_KEEP = "host/shadps4-arm64-025"
GLIBC_DROP = {
    "host/shadps4-arm64-020",
    "host/shadps4-arm64-023",
    "host/shadps4-arm64-024",
}


def compact_runtime(outer: zipfile.ZipFile) -> tuple[bytes, bytes]:
    if RUNTIME_ZIP not in outer.namelist() or RUNTIME_MANIFEST not in outer.namelist():
        raise ValueError("Original glibc runtime ZIP/manifest missing")
    contents = outer.read(RUNTIME_ZIP)
    manifest = json.loads(outer.read(RUNTIME_MANIFEST))
    files = manifest.get("files")
    if not isinstance(files, list) or not all(isinstance(x, dict) for x in files):
        raise ValueError("Unsupported runtime manifest files schema")
    recorded = {x.get("path") for x in files}
    if not GLIBC_DROP.issubset(recorded) or GLIBC_KEEP not in recorded:
        raise ValueError("All 4 original glibc variants must be in runtime manifest")
    source = io.BytesIO(contents)
    output = io.BytesIO()
    with zipfile.ZipFile(source, "r") as z_in, zipfile.ZipFile(output, "w", allowZip64=True) as z_out:
        names = set(z_in.namelist())
        if not GLIBC_DROP.issubset(names) or GLIBC_KEEP not in names:
            raise ValueError("All 4 original glibc executables must be in runtime ZIP")
        for info in z_in.infolist():
            if info.filename in GLIBC_DROP:
                print("GLIBC_OLD_BINARY_REMOVED", info.filename,
                      "uncompressed", info.file_size, "compressed", info.compress_size)
                continue
            z_out.writestr(copy.copy(info), z_in.read(info.filename))
    manifest["files"] = [x for x in files if x.get("path") not in GLIBC_DROP]
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
    print("SINGLE_GLIBC_025_READY", "originalZIP", len(contents),
          "compactZIP", len(result), "manifestFiles", len(manifest["files"]))
    return result, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
