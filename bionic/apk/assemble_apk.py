#!/usr/bin/env python3
"""Assemble a Bachata 0.2.7-based Bionic test APK on GitHub Actions only.

The APK is used solely as the Android frontend reference until the frontend
source migration is complete. New native core, adapter and ELF dependencies
must be compiled from the pinned GitHub source workflow.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

EXPECTED_BASE_SHA256 = "35c6fad39430e54aba561877953323e03b322a589a44442931317450e0b952d8"
BASE_RELEASE = "0.2.7"
NATIVE_DIR = "lib/arm64-v8a/"
NATIVE_MANIFEST = "assets/runtime/native-runtime.json"
REQUIRED_LIBRARIES = {"libbachata_native_runtime.so", "libbachata_bionic_core.so"}
CRITICAL_PRESERVED = {
    "AndroidManifest.xml",
    "assets/runtime/runtime.zip",
    "classes.dex",
    "resources.arsc",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def die(message: str) -> None:
    raise SystemExit(f"BIONIC APK ASSEMBLY FAILED: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--patched-classes8", type=Path, required=False,
                        help="Only the 0.2.7 native bridge SDL JNI loading fix")
    args = parser.parse_args()

    base_bytes_sha256 = hashlib.file_digest(args.base.open("rb"), "sha256").hexdigest()
    if base_bytes_sha256 != EXPECTED_BASE_SHA256:
        die(f"Base 0.2.7 SHA256 mismatch: {base_bytes_sha256}")

    libdir = args.stage / NATIVE_DIR
    if not libdir.is_dir():
        die(f"Missing compiled ARM64 stage: {libdir}")
    staged = {file.name: file for file in libdir.iterdir() if file.is_file()}
    missing = REQUIRED_LIBRARIES - staged.keys()
    if missing:
        die(f"Missing Bionic core or JNI bridge: {sorted(missing)}")
    for name in staged:
        if not re.fullmatch(r"lib[A-Za-z0-9_+.-]+\.so", name):
            die(f"Android PackageManager will not extract this ELF name: {name}")
    if "libbachata_release_legacy.so" in staged:
        die("Legacy fallback would disguise a failure of the new Bionic core")

    # Preserve all of the v0.2.7 UI, settings, DEX, drivers, patches,
    # icons and managed glibc runtime; overwrite ONLY compiled native libs
    # and the native-runtime checksum manifest.
    changed = {NATIVE_DIR + name: file.read_bytes() for name, file in staged.items()}
    if args.patched_classes8 is not None:
        patched_dex = args.patched_classes8.read_bytes()
        if not patched_dex.startswith(b"dex\\n") or len(patched_dex) < 1024:
            die("Patched classes8.dex is invalid")
        if b"SDL3" not in patched_dex:
            die("Rebuilt classes8.dex lacks the shared SDL3 initialization string")
        changed["classes8.dex"] = patched_dex
    with zipfile.ZipFile(args.base) as original:
        names = set(original.namelist())
        if not CRITICAL_PRESERVED.issubset(names) or NATIVE_MANIFEST not in names:
            die("APK 0.2.7 missing the expected Android frontend files")
        original_manifest = json.loads(original.read(NATIVE_MANIFEST))
        if original_manifest.get("abi") != "android-bionic-arm64":
            die("Unexpected native runtime manifest ABI")
        files = original_manifest.get("files")
        if not isinstance(files, list):
            die("Invalid native runtime manifest file list")
        # Maintain the original two-entry schema used by the 0.2.7 frontend.
        for item in files:
            filename = item.get("name")
            if filename in staged:
                item["size"] = len(changed[NATIVE_DIR + filename])
                item["sha256"] = sha256(changed[NATIVE_DIR + filename])
        if not any(entry.get("name") == "libbachata_native_runtime.so" for entry in files):
            die("Native runtime manifest lacks JNI adapter entry")
        changed[NATIVE_MANIFEST] = (
            json.dumps(original_manifest, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        changed["assets/bachata-bionic-build.json"] = (
            json.dumps({
                "baseRelease": BASE_RELEASE,
                "baseSha256": EXPECTED_BASE_SHA256,
                "revision": args.revision,
                "backend": "generic-shadps4-fex-android-bionic",
                "nativeCoreSha256": sha256(changed[NATIVE_DIR + "libbachata_bionic_core.so"]),
                "legacyFallback": False,
                "deviceTested": False,
            }, indent=2) + "\n"
        ).encode("utf-8")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, "w", allowZip64=True) as output:
            for info in original.infolist():
                if info.filename in changed:
                    data = changed.pop(info.filename)
                else:
                    data = original.read(info.filename)
                output.writestr(copy.copy(info), data)
            for name, data in sorted(changed.items()):
                output.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED,
                                compresslevel=6)

    # Re-open generated archive: detect corruption and verify complete
    # replacement without silently building a partial or stale APK.
    with zipfile.ZipFile(args.base) as original, zipfile.ZipFile(args.output) as result:
        if result.testzip() is not None:
            die("Corrupted APK zip entry")
        names = result.namelist()
        if len(names) != len(set(names)):
            die("Duplicate ZIP entries")
        for filename in CRITICAL_PRESERVED:
            if sha256(original.read(filename)) != sha256(result.read(filename)):
                die(f"Unexpected frontend change: {filename}")
        if args.patched_classes8 is not None:
            if result.read("classes8.dex") == original.read("classes8.dex"):
                die("Native runtime SDL3 JNI loader DEX was NOT updated")
            if result.read("classes8.dex") != args.patched_classes8.read_bytes():
                die("Patched classes8.dex did not match assembled DEX")
        for filename, staged_file in staged.items():
            if sha256(result.read(NATIVE_DIR + filename)) != sha256(staged_file.read_bytes()):
                die(f"Native .so not injected correctly: {filename}")
        manifest = json.loads(result.read(NATIVE_MANIFEST))
        for item in manifest["files"]:
            n = item["name"]
            if n in staged:
                if item["sha256"] != sha256(result.read(NATIVE_DIR + n)):
                    die(f"Native runtime integrity metadata mismatch: {n}")
        if result.read(NATIVE_DIR + "libbachata_native_runtime.so") == \
           original.read(NATIVE_DIR + "libbachata_native_runtime.so"):
            die("Old native runtime was not replaced")

    print(f"BIONIC_APK_PRE_SIGN_VALIDATED: {args.output} ({args.output.stat().st_size} bytes)")
    print("Only GitHub Actions may perform apk zipalign, signing and publication.")


if __name__ == "__main__":
    main()
