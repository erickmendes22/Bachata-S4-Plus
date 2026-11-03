#!/usr/bin/env python3
"""Enable exactly the five upstream Linux-only patches for Android, fail closed.
Source: Droid-Deck/Drivers c437d891164c5e31a65219a5451005875fab74ac.
Pinned Mesa: b1a8996cb336f8398b06583c399fae821523152d.
No custom IR3/per-vertex patches or GameHub-derived binary code included.
"""
from pathlib import Path
import json
import sys
p = Path(sys.argv[1])
want = [
    "linux/0001-tu-mesh-shader-emulation.patch",
    "linux/0002-ir3-half-wave-subgroups.patch",
    "linux/0003-ir3-a8xx-cube-direction-sanitize.patch",
    "linux/0004-tu-a8xx-bindless-invalidate.patch",
    "linux/0005-tu-kgsl-a8xx-ib-virtual-alias.patch",
]
entries = json.loads(p.read_text())
found = [e["file"] for e in entries if e["file"] in want]
assert found == want, f"Linux-only patch series drift: {found}"
for e in entries:
    if e["file"] in want:
        assert e["targets"] == ["linux"], f"patch was already ported: {e['file']}"
        e["targets"] = ["android", "linux"]
assert len([e for e in entries if e["file"] in want]) == 5
p.write_text(json.dumps(entries, indent=2) + "\n")
print("PORT ENABLED Linux-only patches for Android:", *want, sep="\n - ")
