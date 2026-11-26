#!/usr/bin/env python3
"""Android-only low-resolution options for The Order's byte-verified 01.02 recipe.

The upstream script already scales every game output/viewport/scene dimension
and verifies each opcode before changing the derived PS4BOOT5 image. Only its
launcher-facing lower bound is reduced. No original game file is modified.
"""
from pathlib import Path
import sys

OLD = "MIN_WIDTH, MAX_WIDTH = 1280, 4880"
NEW = "MIN_WIDTH, MAX_WIDTH = 640, 4880"

def patch(path):
    file = Path(path)
    source = file.read_text(encoding="utf-8")
    if source.count(OLD) != 1:
        raise RuntimeError("Pinned upstream render-size bound changed; inspect before patching")
    if "def apply_prepared(boot, profile):" not in source or "verify_source_identity" not in source:
        raise RuntimeError("Upstream byte verification no longer matches pinned implementation")
    file.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
    print("Enabled experimental 1024/768/640 game render widths (byte-checked)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_android_resolution.py scripts/order1886_resolution.py")
    patch(sys.argv[1])
