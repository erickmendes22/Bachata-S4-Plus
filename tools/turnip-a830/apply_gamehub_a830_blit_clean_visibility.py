#!/usr/bin/env python3
"""Restore A830 explicit blit cache clean when legacy-subpass replacement is used.

In original GameHub Mesa 26.2, TU_CMD_FLAG_BLIT_CACHE_CLEAN on A7xx+ causes
FD_CCU_CLEAN_BLIT_CACHE. In V38 this is optimized away if a SUBPASS_SLICE_FENCE
is pending and info->props.subpass_fence_cleans_resolve is true.

The prior GameHub R5 patch replaces A830 SUBPASS_SLICE_FENCE with
FD_CACHE_INVALIDATE + WFI but leaves the resolve-clean optimization intact.
These are NOT equivalent events. Restore the clean for A830 only.
This fixes the previous integration's command-stream inconsistency;
it does not prove removal of SotC ghosting/flicker without device validation.
"""
from pathlib import Path
import sys

BEFORE = """   if (CHIP >= A7XX && (flushes & TU_CMD_FLAG_BLIT_CACHE_CLEAN) &&
       /* On newer HW SUBPASS_FENCE implicitly waits for resolve events to
        * finish, so we don't need this if we're emitting it.
        */
       (!emit_subpass_slice_fence ||
         !cmd_buffer->device->physical_device->info->props.subpass_fence_cleans_resolve))"""
AFTER = """   // A830 GameHub R5 does NOT emit FD_SUBPASS_SLICE_FENCE: it replaces
   // the event with CACHE_INVALIDATE + WFI. Never skip the clean based
   // on a *non-emitted* sliced fence.
   const uint64_t gamehub_blit_chip_id =
      cmd_buffer->device->physical_device->dev_id.chip_id;
   const bool gamehub_a830_legacy_blit_clean = CHIP >= A8XX &&
      (gamehub_blit_chip_id == 0xffff44050000ull ||
       gamehub_blit_chip_id == 0xffff44050001ull ||
       gamehub_blit_chip_id == 0x44050001ull);
   if (CHIP >= A7XX && (flushes & TU_CMD_FLAG_BLIT_CACHE_CLEAN) &&
       (gamehub_a830_legacy_blit_clean ||
        !emit_subpass_slice_fence ||
        !cmd_buffer->device->physical_device->info->props.subpass_fence_cleans_resolve))"""

def apply(path: Path):
    s=path.read_text()
    if s.count(BEFORE)!=1:
        raise ValueError("Expected original V38 blit-cache condition exactly once")
    if s.count("gamehub_a830_legacy_subpass") != 2:
        raise ValueError("Missing prerequisite A830 legacy-subpass replacement")
    if "gamehub_a830_legacy_blit_clean" in s:
        raise ValueError("Already patched")
    s=s.replace(BEFORE,AFTER,1)
    if "FD_CCU_CLEAN_BLIT_CACHE" not in s or "FD_SUBPASS_SLICE_FENCE" not in s:
        raise ValueError("Unexpected V38 cache event source")
    path.write_text(s)
    print("PASS: A830 original explicit BLIT_CACHE_CLEAN restored; other chips unchanged")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/vulkan/tu_cmd_buffer.cc"))
