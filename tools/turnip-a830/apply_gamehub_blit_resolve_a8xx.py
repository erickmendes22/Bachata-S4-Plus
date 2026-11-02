#!/usr/bin/env python3
"""Recover original GameHub A8xx requested blit-cache clean semantics.

GameHub original ELF (SHA256 1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404):
- 0x95f038: tbnz w21, bit 11 -> 0x95f2e0
- 0x95f330: loads PM4 event 0x70460001, 0x1a (CCU_CLEAN_BLIT_CACHE).
The branch is not suppressed by subpass slice fence.
Keep A7xx and A6xx Mesa V38 behavior unchanged. Fail closed on source drift.
"""
from pathlib import Path
import sys
BEFORE = """       (!emit_subpass_slice_fence ||
         !cmd_buffer->device->physical_device->info->props.subpass_fence_cleans_resolve))"""
AFTER = """       (!emit_subpass_slice_fence ||
         /* Original GameHub A8xx emits the requested BLIT_CACHE_CLEAN even
          * with a subpass slice fence (ARM64 0x95f038..0x95f338). */
         CHIP >= A8XX ||
         !cmd_buffer->device->physical_device->info->props.subpass_fence_cleans_resolve))"""

def apply(path: Path):
    s = path.read_text()
    for marker in ("TU_CMD_FLAG_BLIT_CACHE_CLEAN", "tu6_emit_flushes",
                   "FD_CCU_CLEAN_BLIT_CACHE", "FD_SUBPASS_SLICE_FENCE"):
        if marker not in s:
            raise ValueError("Missing pinned Mesa marker: " + marker)
    if s.count(BEFORE) != 1 or s.count(AFTER) != 0:
        raise ValueError("Unexpected Mesa V38 source or duplicate patch")
    out = s.replace(BEFORE, AFTER, 1)
    path.write_text(out)
    print("PASS: selective A8xx blit clean restored from GameHub")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv) > 1 else
          Path("src/freedreno/vulkan/tu_cmd_buffer.cc"))
