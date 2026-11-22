#!/usr/bin/env python3
"""Preserve Ninja incremental dependency timestamps across ephemeral CI checkouts.

A cache archive restores .o and .ninja_deps with old mtimes. Recreating the
identical source checkout afterwards makes every source file newer than its .o,
so Ninja recompiles all units despite their contents being unchanged.

This restores prior source mtimes ONLY when SHA-256 and byte size both match
the saved source; changed, new, missing, symlinked or oversized files retain
their fresh checkout timestamps and trigger normal Ninja rebuilds.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
MANIFEST = Path("out/bionic/shadps4-generic-android/.bachata-input-times-v1.json")
SOURCE_ROOTS = ("generic-upstream", "bionic/generic")
MAX_FILE_BYTES = 8 * 1024 * 1024
VERSION = 1


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_files(project: Path):
    for relative_root in SOURCE_ROOTS:
        root = project / relative_root
        if not root.is_dir():
            continue
        for folder, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".ccache")]
            for filename in files:
                path = Path(folder) / filename
                if path.is_symlink() or filename == ".git" or filename.endswith(".pyc"):
                    continue
                try:
                    stat = path.stat()
                except FileNotFoundError:
                    continue
                if not path.is_file() or stat.st_size > MAX_FILE_BYTES:
                    continue
                yield path, str(path.relative_to(project)), stat


def snapshot(project: Path, manifest: Path) -> int:
    if not (project / "generic-upstream" / "CMakeLists.txt").exists():
        print("BIONIC_INCREMENTAL_SNAPSHOT_SKIPPED: source not present")
        return 0
    entries = {}
    for path, rel, stat in source_files(project):
        entries[rel] = [stat.st_size, hash_file(path), stat.st_mtime_ns]
    full = project / manifest
    full.parent.mkdir(parents=True, exist_ok=True)
    temp = full.with_suffix(".tmp")
    temp.write_text(json.dumps({"version": VERSION, "files": entries},
                               separators=(",", ":"), sort_keys=True) + "\n")
    temp.replace(full)
    print(f"BIONIC_INCREMENTAL_SNAPSHOT: {len(entries)} content-hashed native inputs")
    return len(entries)


def restore(project: Path, manifest: Path) -> int:
    full = project / manifest
    if not full.is_file():
        print("BIONIC_INCREMENTAL_COLD_START: no prior source hash manifest")
        return 0
    try:
        saved = json.loads(full.read_text())
    except (OSError, ValueError) as exc:
        print(f"BIONIC_INCREMENTAL_COLD_START: invalid manifest {exc}")
        return 0
    if saved.get("version") != VERSION or not isinstance(saved.get("files"), dict):
        print("BIONIC_INCREMENTAL_COLD_START: outdated manifest")
        return 0
    entries = saved["files"]
    matched = changed = untracked = 0
    for path, rel, stat in source_files(project):
        previous = entries.get(rel)
        if not isinstance(previous, list) or len(previous) != 3:
            untracked += 1
            continue
        prev_size, prev_hash, prev_time = previous
        if stat.st_size != prev_size or hash_file(path) != prev_hash:
            changed += 1
            continue
        if not isinstance(prev_time, int) or prev_time <= 0:
            changed += 1
            continue
        if stat.st_mtime_ns != prev_time:
            os.utime(path, ns=(stat.st_atime_ns, prev_time))
        matched += 1
    print(f"BIONIC_INCREMENTAL_RESTORED: unchanged={matched} "
          f"changed={changed} new={untracked}; changed inputs keep fresh mtimes")
    return matched


def selftest() -> None:
    with tempfile.TemporaryDirectory(prefix="bachata-incremental-") as temp:
        project = Path(temp)
        src = project / "generic-upstream/src/game.cpp"
        include = project / "bionic/generic/android_host.h"
        src.parent.mkdir(parents=True)
        include.parent.mkdir(parents=True)
        (project / "generic-upstream/CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.21)\n")
        src.write_text("int main() {return 0;}\n")
        include.write_text("#pragma once\n")
        origin = 1_700_000_000_000_000_000
        os.utime(src, ns=(origin, origin))
        os.utime(include, ns=(origin, origin))
        manifest = MANIFEST
        assert snapshot(project, manifest) == 3
        future = origin + 20_000_000_000
        os.utime(src, ns=(future, future))
        include.write_text("#pragma once\n// altered ABI\n")
        os.utime(include, ns=(future, future))
        assert restore(project, manifest) == 2
        assert src.stat().st_mtime_ns == origin
        assert include.stat().st_mtime_ns == future
        assert restore(project, manifest) == 2
        print("BIONIC_INCREMENTAL_SELFTEST_PASS")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) == 2 else ""
    if action == "restore":
        restore(PROJECT, MANIFEST)
    elif action == "snapshot":
        snapshot(PROJECT, MANIFEST)
    elif action == "selftest":
        selftest()
    else:
        raise SystemExit("usage: incremental_inputs.py restore|snapshot|selftest")
