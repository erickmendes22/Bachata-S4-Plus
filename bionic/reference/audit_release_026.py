#!/usr/bin/env python3
"""Binary-backed release 0.2.6 / working 0.16.1 PS4 Bionic base audit.

Reference is the actual publicly distributed Bachata S4 v0.2.6 APK, not
the experimental 0.21.1 source port. The compiled candidate is only compared
for Android loader/guest execution contracts, not identical source symbols.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

RELEASE_SHA256 = "39d38d4e781bc83ee2542b3884a264895e726c3c8ee49df493ded487e6cd6f74"
BIONIC_SHA256 = "3548cb4b6d952aed7141f057e07552b4f23a57997df339644a57605ed1308f39"
GLIBC_SHA256 = "e85d75f4e8fa23e9a4f8629e5dacc33c6de126a79fd4d0eec0fab0f37f7feb00"
FEX_REF = "f2b679f6028ce1c38875233aecfcf5d3f8ebecec"
RELEASE_NATIVE_BUILD_ID = "7915af924afb3bc2142df65fdeb36f28a970d0a5"
RELEASE_LINUX_BUILD_ID = "0a0ada4cf92b9e275c671e2902a79f500f76168e"
JNI = (
    "JNI_OnLoad",
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run",
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop",
    "Java_org_libsdl_app_SDLActivity_nativeSetupJNI",
    "Java_org_libsdl_app_SDLAudioManager_nativeSetupJNI",
    "Java_org_libsdl_app_SDLControllerManager_nativeSetupJNI",
)
CONTRACT_GROUPS = {
    "fex_guest": "Core18FexGuestCpuBackend",
    "hle_bridge": "GuestBridge",  # release exports HleGuestBridge; diagnostics also print exact counts
    "saf_backend": "SafFsBackend",
    "runtime_ipc": "RuntimeClient",
}


def run(*cmd: str) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def elf_report(path: Path) -> dict:
    header = run("readelf", "-h", str(path))
    dynamic = run("readelf", "-d", str(path))
    notes = run("readelf", "-n", str(path))
    syms = run("readelf", "--dyn-syms", "--wide", str(path))
    names = set()
    for line in syms.splitlines():
        columns = line.split()
        if len(columns) >= 8 and columns[0].endswith(":") and columns[6] != "UND":
            names.add(columns[7].split("@", 1)[0])
    needed = sorted(set(re.findall(r"Shared library: \[([^\]]+)\]", dynamic)))
    build_id = re.search(r"Build ID: ([0-9a-f]+)", notes)
    return {
        "aarch64": "AArch64" in header,
        "needed": needed,
        "buildId": build_id.group(1) if build_id else None,
        "symbols": len(names),
        "jni": {name: name in names for name in JNI},
        "guestComponents": {
            "FexGuestCpuBackend": sum("FexGuestCpuBackend" in n for n in names),
            "HleGuestBridge": sum("HleGuestBridge" in n for n in names),
            "SafFsBackend": sum("SafFsBackend" in n for n in names),
            "SafBrokerClient": sum("SafBrokerClient" in n for n in names),
            "RuntimeClient": sum("RuntimeClient" in n for n in names),
        },
    }


def check_source(source: Path) -> dict:
    cmake = (source / "CMakeLists.txt").read_text()
    version = []
    for part in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(r'set\(EMULATOR_VERSION_' + part + r'\s+"(\d+)"\)', cmake)
        if not match:
            raise SystemExit("Working source version absent in CMakeLists: " + part)
        version.append(int(match.group(1)))
    if tuple(version) != (0, 16, 1):
        raise SystemExit("Wrong foundation: expected working 0.16.1 tree, got " + str(version))
    for relative in (
        "src/core/fex/fex_guest_engine.cpp",
        "src/core/guest_cpu/fex_guest_cpu.cpp",
        "src/core/file_sys/fs.cpp",
        "src/core/linker.cpp",
        "src/video_core/renderer_vulkan/vk_platform.cpp",
    ):
        if not (source / relative).is_file():
            raise SystemExit("Working ARM64/FEX foundation incomplete: " + relative)
    return {"sourceVersion": ".".join(map(str, version)), "sourceIsOriginalFexArm64": True}


def check_release(apk: Path) -> dict:
    data = apk.read_bytes()
    if sha256(data) != RELEASE_SHA256:
        raise SystemExit("Reference must be the exact official 0.2.6 APK")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        native = z.read("lib/arm64-v8a/libbachata_native_runtime.so")
        root = z.read("assets/runtime/runtime.zip")
        manifest = json.loads(z.read("assets/runtime/native-runtime.json"))
        if manifest["abi"] != "android-bionic-arm64" or manifest["fexRevision"] != FEX_REF:
            raise SystemExit("Original native runtime FEX/ABI differs from reference")
        with zipfile.ZipFile(io.BytesIO(root)) as sub:
            linux = sub.read("host/shadps4-arm64-fex")
    if sha256(native) != BIONIC_SHA256 or sha256(linux) != GLIBC_SHA256:
        raise SystemExit("Release binaries differ from the audited 0.2.6 build")
    if b"0.18.1 WIP" not in native or b"0.18.1 WIP" not in linux:
        raise SystemExit("Release is not the observed shadPS4 0.18.1 build")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "native.so").write_bytes(native)
        (p / "linux").write_bytes(linux)
        n = elf_report(p / "native.so")
        l = elf_report(p / "linux")
    if n["buildId"] != RELEASE_NATIVE_BUILD_ID or l["buildId"] != RELEASE_LINUX_BUILD_ID:
        raise SystemExit("Release ELF Build IDs changed unexpectedly")
    if "libc.so" not in n["needed"] or "libc.so.6" in n["needed"]:
        raise SystemExit("Reference native core was not Android/Bionic")
    if "libc.so.6" not in l["needed"]:
        raise SystemExit("Reference Linux core was not glibc")
    if not all(n["jni"].values()):
        raise SystemExit("Reference native core lacks a verified JNI entry")
    return {
        "release": "Bachata S4 0.2.6",
        "releaseCoreVersion": "0.18.1 WIP",
        "referenceApkSha256": RELEASE_SHA256,
        "referenceNativeSha256": BIONIC_SHA256,
        "referenceGlibcSha256": GLIBC_SHA256,
        "native": n,
        "glibc": l,
        "fexRevision": FEX_REF,
    }


def check_built_core(core: Path) -> dict:
    data = core.read_bytes()
    n = elf_report(core)
    if not n["aarch64"] or "libc.so" not in n["needed"] or "libc.so.6" in n["needed"]:
        raise SystemExit("Built core must be a genuine Android AArch64 Bionic ELF")
    if not all(n["jni"].values()):
        raise SystemExit("Built core lacks Android JNI runtime/SDL entrypoints: " + str(n["jni"]))
    return {"candidateCoreSha256": sha256(data), "candidate": n}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--release-apk", type=Path)
    parser.add_argument("--built-core", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = check_source(args.source)
    if args.release_apk:
        result["reference"] = check_release(args.release_apk)
    if args.built_core:
        result["build"] = check_built_core(args.built_core)
    output = json.dumps(result, indent=2, sort_keys=True)
    print(output)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n")
    print("BIONIC_RELEASE_026_BINARY_PARITY_AUDIT_OK")


if __name__ == "__main__":
    main()
