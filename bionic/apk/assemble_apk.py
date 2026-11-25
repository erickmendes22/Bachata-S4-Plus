#!/usr/bin/env python3
"""Assemble a Bachata 0.2.7-based Bionic test APK on GitHub Actions only.

The APK is used solely as the Android frontend reference until the frontend
source migration is complete. New native core, adapter and ELF dependencies
must be compiled from the pinned GitHub source workflow.
"""
from __future__ import annotations

import argparse
import copy
import io
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from compact_runtime import compact_runtime, GLIBC_DROP, GLIBC_KEEP, RUNTIME_ZIP, RUNTIME_MANIFEST

EXPECTED_BASE_SHA256 = "35c6fad39430e54aba561877953323e03b322a589a44442931317450e0b952d8"
BASE_RELEASE = "0.2.7"
NATIVE_DIR = "lib/arm64-v8a/"
NATIVE_MANIFEST = "assets/runtime/native-runtime.json"
SOTC_CORE = "libbachata_sotc_core.so"
SOTC_REV = "68f4f41af02d9b9b0ceac73df5b361f2ab00c0ce"
REQUIRED_LIBRARIES = {"libbachata_native_runtime.so", "libbachata_bionic_core.so"}
CRITICAL_PRESERVED = {
    "AndroidManifest.xml",
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

    # Reject the old pinned native artifact even when the JNI adapter or DEX is
    # new. That artifact does NOT include the Android managed-path bootstrap
    # or the source-controlled custom Vulkan loader integration.
    source_revision_file = args.stage / "BIONIC_SOURCE_REVISION.txt"
    if not source_revision_file.is_file():
        die("Native core artifact predates full pre-boot integration; rebuild core first")
    core_source_revision = source_revision_file.read_text(encoding="ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", core_source_revision):
        die("Native core source revision metadata is invalid")
    core_binary = staged["libbachata_bionic_core.so"].read_bytes()
    core_sha = sha256(core_binary)
    if args.revision != core_source_revision:
        die(f"Native source revision mismatch: stage={core_source_revision}, "
            f"request={args.revision}")
    # This is the version the Android runtime installer checks before
    # reusing its extracted directory. The previous packaging script did
    # not update runtimeVersion, so every new APK reused the old 9ceb...
    # extracted root and old GUEST_RUNTIME_BUILD name.
    runtime_version = f"bachata-s4-plus-{BASE_RELEASE}-bionic-{core_sha[:16]}"
    parity_marker = "BACHATA_CORE_PARITY=20261123-SRT4-GPUPAGE1-CTYPE3-CE1-OWNEDCB-FIBER1-RUNTIME1-RELEASEFIOS2-SAFDIRECT2-GPUCLAMP1-BUDGET1-RCSNAP1-IFILE1-FIOSERR1"
    revision_marker = f"BACHATA_CORE_REVISION={core_source_revision}"
    for marker in (b"BIONIC_MANAGED_USER_PATH_READY", b"SDL_VULKAN_LIBRARY",
                   b"Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run",
                   parity_marker.encode("ascii"), revision_marker.encode("ascii")):
        if marker not in core_binary:
            die(f"Compiled native core is missing required current-build integration: {marker!r}")

    # The explicitly selected SotC core is the revised dedicated Bionic
    # binary, not a generic legacy fallback. Its actual SHA is part of the APK provenance.
    sotc = staged.get(SOTC_CORE)
    if not sotc or f"BACHATA_CORE_REVISION={SOTC_REV}".encode() not in sotc.read_bytes():
        die("Missing corrected SotC core")
    sotc_sha=sha256(sotc.read_bytes())

    # Preserve all of the v0.2.7 UI, settings, DEX, drivers, patches,
    # icons and managed glibc runtime; overwrite ONLY compiled native libs
    # and the native-runtime checksum manifest.
    changed = {NATIVE_DIR + name: file.read_bytes() for name, file in staged.items()}
    if args.patched_classes8 is not None:
        patched_dex = args.patched_classes8.read_bytes()
        if not patched_dex.startswith(b"dex\n") or len(patched_dex) < 1024:
            die("Patched classes8.dex is invalid")
        if b"bachata_bionic_core" not in patched_dex or b"bachata_sotc_core" not in patched_dex:
            die("Rebuilt classes8.dex does not register the real Bionic core JNI library")
        changed["classes8.dex"] = patched_dex
    with zipfile.ZipFile(args.base) as original:
        names = set(original.namelist())
        if not (CRITICAL_PRESERVED | {RUNTIME_ZIP, RUNTIME_MANIFEST}).issubset(names) or NATIVE_MANIFEST not in names:
            die("APK 0.2.7 missing the expected Android frontend files")
        compact_zip, compact_manifest = compact_runtime(
            original, runtime_version=runtime_version,
            core_revision=core_source_revision, core_sha256=core_sha)
        changed[RUNTIME_ZIP] = compact_zip
        changed[RUNTIME_MANIFEST] = compact_manifest
        original_manifest = json.loads(original.read(NATIVE_MANIFEST))
        if original_manifest.get("abi") != "android-bionic-arm64":
            die("Unexpected native runtime manifest ABI")
        files = original_manifest.get("files")
        if not isinstance(files, list):
            die("Invalid native runtime manifest file list")
        # Preserve the existing schema, add explicit integrity entry for the selected core.
        if not any(item.get("name")==SOTC_CORE for item in files):
            files.append({"name":SOTC_CORE,"size":sotc.stat().st_size,"sha256":sotc_sha})
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
                "nativeCoreSha256": core_sha,
                "runtimeVersion": runtime_version,
                "runtimeExtractionIdentity": "native-core-sha256",
                "nativeCoreMarker": parity_marker,
                "nativeCoreRevisionMarker": revision_marker,
                "nativeCoreSourceRevision": core_source_revision,
                "legacyFallback": False,
                "titleCoreOverrides":{"CUSA08809":SOTC_REV,"CUSA08034":SOTC_REV},
                "sotcCoreSha256":sotc_sha,
                "glibcFallback": "025",
                "removedGlibcVariants": ["020", "023", "024"],
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
        with zipfile.ZipFile(io.BytesIO(result.read(RUNTIME_ZIP))) as runtime:
            names_in_runtime = set(runtime.namelist())
            if GLIBC_KEEP not in names_in_runtime or GLIBC_DROP & names_in_runtime:
                die("Wrong glibc runtime variants in slimmed APK")
        new_runtime_manifest = json.loads(result.read(RUNTIME_MANIFEST))
        if new_runtime_manifest.get("runtimeVersion") != runtime_version:
            die("Installer runtimeVersion did not change with native core hash")
        original_runtime_version = json.loads(original.read(RUNTIME_MANIFEST)).get("runtimeVersion")
        if original_runtime_version == runtime_version:
            die("Installer may silently reuse old extracted runtime")
        with zipfile.ZipFile(io.BytesIO(result.read(RUNTIME_ZIP))) as packaged_runtime:
            guest_meta = json.loads(packaged_runtime.read("usr/share/bachata/guest-runtime.json"))
            if (guest_meta.get("revision") != "bionic-" + core_source_revision[:12] or
                    guest_meta.get("sha256") != core_sha):
                die("Guest runtime revision metadata was not refreshed")
            if f"revision=bionic-{core_source_revision[:12]}" not in (
                    packaged_runtime.read("usr/share/bachata/guest-runtime.txt").decode()):
                die("Text guest runtime marker still describes the old core")
            recorded = {x["path"]: x for x in new_runtime_manifest["files"]}
            for path in ("usr/share/bachata/guest-runtime.json",
                         "usr/share/bachata/guest-runtime.txt"):
                entry = recorded.get(path)
                data = packaged_runtime.read(path)
                if not entry or entry.get("sha256") != sha256(data) or entry.get("size") != len(data):
                    die(f"Runtime re-extraction file integrity mismatch: {path}")
        build_identity = json.loads(result.read("assets/bachata-bionic-build.json"))
        if (build_identity.get("runtimeVersion") != runtime_version or
                build_identity.get("nativeCoreSha256") != core_sha or
                build_identity.get("nativeCoreRevisionMarker") != revision_marker):
            die("APK build provenance and runtime installation identity disagree")
        if build_identity.get("sotcCoreSha256") != sha256(result.read(NATIVE_DIR+SOTC_CORE)):
            die("SotC pinned binary integrity mismatch")
        all_runtime_paths = {x.get("path") for x in new_runtime_manifest.get("files", [])}
        if GLIBC_KEEP not in all_runtime_paths or GLIBC_DROP & all_runtime_paths:
            die("Wrong glibc variants still referenced by manifest")
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

    print(f"BIONIC_RUNTIME_IDENTITY_VERIFIED: {runtime_version} / {revision_marker}")
    print(f"BIONIC_APK_PRE_SIGN_VALIDATED: {args.output} ({args.output.stat().st_size} bytes)")
    print("Only GitHub Actions may perform apk zipalign, signing and publication.")


if __name__ == "__main__":
    main()
