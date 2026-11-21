#!/usr/bin/env python3
"""Package the REAL official 0.18.1 Bionic runtime into Bachata S4+ v0.2.7.

This is a binary transplant of the proven release, NOT a source compilation
of the public 0.16.1 port and NOT the experimental 0.21.1 transplant.
The original developer source (Bachata-S4-Dev ...dirty) is not public.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

RELEASE_APK_SHA256 = "39d38d4e781bc83ee2542b3884a264895e726c3c8ee49df493ded487e6cd6f74"
PLUS_APK_SHA256 = "35c6fad39430e54aba561877953323e03b322a589a44442931317450e0b952d8"
RELEASE_NATIVE_SHA256 = "3548cb4b6d952aed7141f057e07552b4f23a57997df339644a57605ed1308f39"
RELEASE_CXX_SHA256 = "8fed70ee5cf18534beebe28b525af8e422d08de3a241ccd3db7856f47048eda0"
RELEASE_NATIVE_BUILD_ID = "7915af924afb3bc2142df65fdeb36f28a970d0a5"
RELEASE_FEX_REVISION = "f2b679f6028ce1c38875233aecfcf5d3f8ebecec"
PREFIX = "lib/arm64-v8a/"
NATIVE = PREFIX + "libbachata_native_runtime.so"
CXX = PREFIX + "libc++_shared.so"
NATIVE_MANIFEST = "assets/runtime/native-runtime.json"
PROVENANCE = "assets/bachata-native-0181-provenance.json"
REQUIRED_JNI = (
    "JNI_OnLoad",
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run",
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop",
    "Java_org_libsdl_app_SDLActivity_nativeSetupJNI",
    "Java_org_libsdl_app_SDLAudioManager_nativeSetupJNI",
    "Java_org_libsdl_app_SDLControllerManager_nativeSetupJNI",
)
MUST_PRESERVE = (
    "AndroidManifest.xml",
    "classes.dex",
    "classes8.dex",
    "resources.arsc",
    "assets/runtime/runtime.zip",
    "assets/runtime/manifest.json",
    PREFIX + "libbachata_custom_vulkan.so",
    PREFIX + "libmain_hook.so",
    PREFIX + "libhook_impl.so",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_sha(path: Path, expected: str, label: str) -> None:
    with path.open("rb") as handle:
        actual = hashlib.file_digest(handle, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError(f"{label} APK SHA-256 differs: {actual} != {expected}")


def check_native_elf(native: bytes) -> dict:
    if sha(native) != RELEASE_NATIVE_SHA256:
        raise RuntimeError("Native core is not the official release 0.18.1 ELF")
    for marker in (b"0.18.1 WIP", b"v0.2.5-7-g99ceb85eb-dirty",
                   b"https://github.com/JICA98/Bachata-S4-Dev.git",
                   b"FexGuestCpuBackend", b"SafFsBackend", b"SafBrokerClient"):
        if marker not in native:
            raise RuntimeError(f"Official core lacks expected release marker {marker!r}")
    if bytes.fromhex(RELEASE_NATIVE_BUILD_ID) not in native:
        raise RuntimeError("Native 0.18.1 ELF GNU Build ID differs")
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "libbachata_native_runtime.so"
        path.write_bytes(native)
        head = subprocess.check_output(["readelf", "-h", str(path)], text=True)
        dynamic = subprocess.check_output(["readelf", "-d", str(path)], text=True)
        syms = subprocess.check_output(["readelf", "-W", "-s", str(path)], text=True)
    if "AArch64" not in head:
        raise RuntimeError("Official native runtime is not ARM64 ELF")
    needed = re.findall(r"Shared library: \[([^\]]+)\]", dynamic)
    if "libc.so" not in needed or "libc++_shared.so" not in needed or "libc.so.6" in needed:
        raise RuntimeError("Official native runtime is not Android/Bionic")
    found = set()
    for line in syms.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[0].endswith(":") and fields[6] != "UND":
            found.add(fields[7].split("@", 1)[0])
    missing = set(REQUIRED_JNI) - found
    if missing:
        raise RuntimeError("Official native runtime lacks JNI export(s): " + repr(missing))
    return {"needed": needed, "jniExports": sorted(set(REQUIRED_JNI)), "buildId": RELEASE_NATIVE_BUILD_ID}


def build(base: Path, release: Path, out: Path, report_out: Path) -> None:
    verify_sha(base, PLUS_APK_SHA256, "Original Bachata S4+ v0.2.7")
    verify_sha(release, RELEASE_APK_SHA256, "Official Bachata S4 v0.2.6")
    with zipfile.ZipFile(release) as official:
        native = official.read(NATIVE)
        cxx = official.read(CXX)
        official_manifest = json.loads(official.read(NATIVE_MANIFEST))
    if sha(cxx) != RELEASE_CXX_SHA256:
        raise RuntimeError("Official 0.18.1 libc++_shared.so is not exact reference")
    elf = check_native_elf(native)
    if official_manifest.get("abi") != "android-bionic-arm64" or \
            official_manifest.get("fexRevision") != RELEASE_FEX_REVISION:
        raise RuntimeError("Official release ABI or FEX revision changed")
    overrides = {NATIVE: native, CXX: cxx}
    with zipfile.ZipFile(base) as original:
        names = original.namelist()
        name_set = set(names)
        if len(names) != len(name_set):
            raise RuntimeError("Base APK contains duplicate ZIP entries")
        missing = set(MUST_PRESERVE) | set(overrides) | {NATIVE_MANIFEST} - name_set
        # Union subtraction must apply to the entire required set.
        missing = (set(MUST_PRESERVE) | set(overrides) | {NATIVE_MANIFEST}) - name_set
        if missing:
            raise RuntimeError(f"Original 0.2.7 frontend missing required files: {sorted(missing)}")
        if PREFIX + "libbachata_bionic_core.so" in name_set:
            raise RuntimeError("Base release has a separate experimental 0.16.1 core")
        manifest = json.loads(original.read(NATIVE_MANIFEST))
        if manifest.get("abi") != "android-bionic-arm64":
            raise RuntimeError("Original S4+ Android native manifest is not Bionic")
        manifest["fexRevision"] = RELEASE_FEX_REVISION
        file_entries = {x["name"]: x for x in manifest.get("files", [])}
        for filename, data in (
            ("libbachata_native_runtime.so", native),
            ("libc++_shared.so", cxx),
        ):
            if filename not in file_entries:
                raise RuntimeError(f"Original native manifest does not track {filename}")
            file_entries[filename]["size"] = len(data)
            file_entries[filename]["sha256"] = sha(data)
        overrides[NATIVE_MANIFEST] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
        provenance = {
            "apkBase": "Bachata S4+ 0.2.7",
            "apkBaseSha256": PLUS_APK_SHA256,
            "nativeDonor": "JICA98/Bachata-S4 v0.2.6",
            "nativeDonorApkSha256": RELEASE_APK_SHA256,
            "nativeCoreVersion": "shadPS4 0.18.1 WIP",
            "sourceProvenance": "JICA98/Bachata-S4-Dev v0.2.5-7-g99ceb85eb-dirty",
            "nativeCoreSha256": RELEASE_NATIVE_SHA256,
            "nativeBuildId": RELEASE_NATIVE_BUILD_ID,
            "libcxxSha256": RELEASE_CXX_SHA256,
            "fexRevision": RELEASE_FEX_REVISION,
            "sourceRecompiled": False,
            "androidGameBootVerified": False,
            "replacedPaths": [NATIVE, CXX, NATIVE_MANIFEST],
            "preservesOriginalPlusFrontend": True,
            "preservesOriginalPlusGlibcFallback": True,
            "separateExperimentalCore": False,
            "abiAudit": elf,
        }
        overrides[PROVENANCE] = (json.dumps(provenance, indent=2, ensure_ascii=False) + "\n").encode()
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", allowZip64=True) as assembled:
            for info in original.infolist():
                data = overrides.pop(info.filename, None)
                if data is None:
                    data = original.read(info.filename)
                assembled.writestr(copy.copy(info), data)
            for filename, data in overrides.items():
                assembled.writestr(filename, data, compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(base) as original, zipfile.ZipFile(out) as result:
        if result.testzip() is not None:
            raise RuntimeError("Output APK ZIP integrity failure")
        if len(result.namelist()) != len(set(result.namelist())):
            raise RuntimeError("Output ZIP has duplicate entries")
        assert sha(result.read(NATIVE)) == RELEASE_NATIVE_SHA256
        assert sha(result.read(CXX)) == RELEASE_CXX_SHA256
        assert b"0.18.1 WIP" in result.read(NATIVE)
        assert "libbachata_bionic_core.so" not in result.namelist()
        for name in MUST_PRESERVE:
            if sha(original.read(name)) != sha(result.read(name)):
                raise RuntimeError(f"Unexpectedly modified base 0.2.7 feature: {name}")
        for name in result.namelist():
            if name not in {NATIVE, CXX, NATIVE_MANIFEST, PROVENANCE} \
                    and name in original.namelist() \
                    and original.getinfo(name).CRC != result.getinfo(name).CRC:
                raise RuntimeError(f"Unexpectedly changed original v0.2.7 ZIP entry: {name}")
        native_info = json.loads(result.read(NATIVE_MANIFEST))
        assert next(x for x in native_info["files"] if x["name"] == "libbachata_native_runtime.so")["sha256"] == RELEASE_NATIVE_SHA256
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n")
    print(f"BIONIC_OFFICIAL_0181_RELEASE_CORE_INSTALLED sha256={RELEASE_NATIVE_SHA256}")
    print(f"BIONIC_OFFICIAL_0181_LIBCXX_EXACT sha256={RELEASE_CXX_SHA256}")
    print("BIONIC_PLUS_027_UI_GLIBC_DRIVER_HOOKS_PRESERVED")
    print(f"BIONIC_OFFICIAL_0181_UNSIGNED_APK_READY path={out} bytes={out.stat().st_size}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True, type=Path)
    p.add_argument("--release", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    args = p.parse_args()
    build(args.base, args.release, args.output, args.report)
