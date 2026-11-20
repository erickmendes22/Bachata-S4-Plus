#!/usr/bin/env python3
"""Remove unused experimental Uncharted native cores; strip Android ELF debugging.

This runs on the *staged* binaries before native-runtime.json hashes are computed.
It never modifies the original native sources or removes an ELF dependency.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

BOOT_ROOTS = {
    "libbachata_bionic_core.so",
    "libbachata_native_runtime.so",
}
# Retain SDL3 as a runtime/JNI safety dependency even when built statically
# into the generic core; its extra size after stripping is modest.
PRESERVE_EXTRA = {"libSDL3.so", "libc++_shared.so"}
OBSOLETE_UNCHARTED_CORES = {
    "libbbgpu.so",
    "libbbprepare.so",
    "libmain.so",
}
BOOT_MARKERS = (
    b"BIONIC_MANAGED_USER_PATH_READY",
    b"BIONIC_VULKAN_LOADER_READY",
    b"Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run",
)


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE).stdout


def needed(path: Path) -> set[str]:
    lines = run("readelf", "-d", str(path)).splitlines()
    return {m.group(1) for line in lines
            if (m := re.search(r"\(NEEDED\).*Shared library: \[(.*?)\]", line))}


def public_symbols(path: Path) -> set[str]:
    result = set()
    for line in run("readelf", "--dyn-syms", "--wide", str(path)).splitlines():
        columns = line.split()
        if len(columns) >= 8 and columns[3] == "FUNC" and columns[4] == "GLOBAL" \
                and columns[6] != "UND":
            result.add(columns[7])
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", type=Path)
    ap.add_argument("--strip", required=True, type=Path)
    args = ap.parse_args()
    libdir = args.stage / "lib/arm64-v8a"
    libs = {p.name: p for p in libdir.glob("*.so") if p.is_file()}
    missing = BOOT_ROOTS - libs.keys()
    if missing:
        raise SystemExit(f"SLIM_ABORT: missing Bionic boot libraries {sorted(missing)}")
    graph = {name: needed(path) for name, path in libs.items()}
    roots = BOOT_ROOTS | (PRESERVE_EXTRA & libs.keys())
    reachable = set(roots)
    stack = list(roots)
    while stack:
        for dep in graph[stack.pop()]:
            if dep in libs and dep not in reachable:
                reachable.add(dep)
                stack.append(dep)
    obsolete_used = OBSOLETE_UNCHARTED_CORES & reachable
    if obsolete_used:
        raise SystemExit(f"SLIM_ABORT: legacy Uncharted cores ARE referenced: {sorted(obsolete_used)}")
    for name in sorted(OBSOLETE_UNCHARTED_CORES & libs.keys()):
        p = libs.pop(name)
        print(f"SLIM_REMOVED_OLD_CORE {name} bytes={p.stat().st_size}")
        p.unlink()
    # Retain other legitimate dependencies / manually dlopened libraries.
    core = libs["libbachata_bionic_core.so"]
    for m in BOOT_MARKERS:
        if m not in core.read_bytes():
            raise SystemExit(f"SLIM_ABORT: Bionic core missing marker {m!r}")
    initial_exports = public_symbols(core)
    initial_needs = needed(core)
    if not initial_exports:
        raise SystemExit("SLIM_ABORT: original core dynamic symbols are empty")
    strip = str(args.strip)
    for name, p in sorted(libs.items()):
        original_size = p.stat().st_size
        subprocess.run([strip, "--strip-debug", str(p)], check=True)
        print(f"SLIM_STRIPPED_ELF {name} old={original_size} new={p.stat().st_size}")
    if public_symbols(core) != initial_exports or needed(core) != initial_needs:
        raise SystemExit("SLIM_ABORT: stripping altered core dynamic exports/DT_NEEDED")
    print("SLIM_BOOT_CORE_EXPORTS_AND_DEPENDENCIES_PRESERVED")
    print("SLIM_STAGED_LIBRARIES", ",".join(sorted(libs)))


if __name__ == "__main__":
    main()
