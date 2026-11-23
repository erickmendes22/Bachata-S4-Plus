#!/usr/bin/env python3
"""Prevent stale Bachata runtime names and guest build metadata from shipping.

Fast CI test: no Android SDK, APKtool, private signing key or native rebuild.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile

from compact_runtime import (
    GLIBC_DROP, GLIBC_KEEP, GUEST_BUILD_JSON, GUEST_BUILD_TXT,
    RUNTIME_MANIFEST, RUNTIME_ZIP, compact_runtime,
)

REVISION = "fedcba9876543210fedcba9876543210fedcba98"
CORE_SHA = hashlib.sha256(b"new-bionic-native-core-with-new-guest-fiber-implementation").hexdigest()
VERSION = "bachata-s4-plus-0.2.7-bionic-" + CORE_SHA[:16]
OLD_VERSION = "bachata-s4-plus-0.2.7-9ceb09280798"


def compressed_zip(entries: dict[str, bytes]) -> bytes:
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as z:
        for path, data in entries.items():
            z.writestr(path, data)
    return memory.getvalue()


def test() -> None:
    entry = {
        "variant": "built",
        "revision": "core024-c39-fe-clean-r28",
        "sha256": "f" * 64,
        "label": "old runtime",
    }
    contents = {
        **{p: b"old executable" for p in GLIBC_DROP},
        GLIBC_KEEP: b"retained glibc fallback",
        "host/shadps4-arm64-fex": b"original guest shim",
        GUEST_BUILD_JSON: (json.dumps(entry) + "\n").encode(),
        GUEST_BUILD_TXT: b"variant=built\nrevision=core024-c39-fe-clean-r28\n",
    }
    manifest = {
        "schemaVersion": 2,
        "runtimeVersion": OLD_VERSION,
        "protocolVersion": 1,
        "files": [
            {
                "path": path, "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            } for path, data in contents.items()
        ],
    }
    package = compressed_zip({
        RUNTIME_ZIP: compressed_zip(contents),
        RUNTIME_MANIFEST: json.dumps(manifest).encode(),
    })
    with zipfile.ZipFile(io.BytesIO(package)) as original:
        result_zip, result_manifest = compact_runtime(
            original, runtime_version=VERSION,
            core_revision=REVISION, core_sha256=CORE_SHA,
        )
        if not re.fullmatch(r"bachata-s4-plus-0\.2\.7-bionic-[a-f0-9]{16}", VERSION):
            raise AssertionError("Runtime identity did not include core digest")
        updated = json.loads(result_manifest)
        assert updated["runtimeVersion"] == VERSION
        assert updated["runtimeVersion"] != manifest["runtimeVersion"]
        assert updated["schemaVersion"] == manifest["schemaVersion"]
        all_paths = {x["path"] for x in updated["files"]}
        assert GLIBC_DROP.isdisjoint(all_paths)
        assert GLIBC_KEEP in all_paths

        with zipfile.ZipFile(io.BytesIO(result_zip)) as z:
            assert GLIBC_DROP.isdisjoint(z.namelist())
            assert GLIBC_KEEP in z.namelist()
            assert z.read("host/shadps4-arm64-fex") == contents["host/shadps4-arm64-fex"]
            meta = json.loads(z.read(GUEST_BUILD_JSON))
            assert meta["variant"] == "built"
            assert meta["revision"] == "bionic-" + REVISION[:12]
            assert meta["sha256"] == CORE_SHA
            assert "core024-" not in z.read(GUEST_BUILD_TXT).decode()
            assert "bionic-" + REVISION[:12] in z.read(GUEST_BUILD_TXT).decode()
            for item in updated["files"]:
                raw = z.read(item["path"])
                assert len(raw) == item["size"]
                assert hashlib.sha256(raw).hexdigest() == item["sha256"]

        try:
            compact_runtime(
                original, runtime_version=OLD_VERSION,
                core_revision=REVISION, core_sha256=CORE_SHA,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted unchanged/invalid extraction name")

    print("BACHATA_RUNTIME_REEXTRACTION_CONTRACT_PASS", VERSION, REVISION)


if __name__ == "__main__":
    test()
