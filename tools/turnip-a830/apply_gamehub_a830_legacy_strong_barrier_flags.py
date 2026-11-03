#!/usr/bin/env python3
"""Restore GameHub A830 global cache visibility before V38 emits events.

Mesa 10b1ef466fae (2026-09-14) introduced two weaker flags:
CACHE_INVALIDATE_GMEM (UCHE GMEM aperture only) and SUBPASS_SLICE_FENCE
(per-slice RB wait). Original GameHub A830 uses strong global
CACHE_INVALIDATE and WAIT_FOR_IDLE ordering. Promote before emission
for A830 only; other GPUs and sysmem/GMEM selection are unchanged.

Do NOT stack the older legacy_subpass_sync/blit_clean_visibility patches.
"""
from pathlib import Path
import sys

OLD = """   if (TU_DEBUG(SYNCDRAW))
      flushes |= TU_CMD_FLAG_WAIT_MEM_WRITES |
                 TU_CMD_FLAG_WAIT_FOR_IDLE |
                 TU_CMD_FLAG_WAIT_FOR_ME;
"""
NEW = """   if (TU_DEBUG(SYNCDRAW))
      flushes |= TU_CMD_FLAG_WAIT_MEM_WRITES |
                 TU_CMD_FLAG_WAIT_FOR_IDLE |
                 TU_CMD_FLAG_WAIT_FOR_ME;

   // Restore the original GameHub A830 global subpass visibility.
   // Promote BEFORE any CCU/UCHE event is emitted: the existing Mesa
   // strong event paths maintain the original clean/invalidate/wait order.
   const uint64_t gamehub_strong_chip_id =
      cmd_buffer->device->physical_device->dev_id.chip_id;
   const bool gamehub_a830_legacy_strong_barrier_flags = CHIP >= A8XX &&
      (gamehub_strong_chip_id == 0xffff44050000ull ||
       gamehub_strong_chip_id == 0xffff44050001ull ||
       gamehub_strong_chip_id == 0x44050001ull);
   if (gamehub_a830_legacy_strong_barrier_flags) {
      if (flushes & TU_CMD_FLAG_CACHE_INVALIDATE_GMEM)
         flushes |= TU_CMD_FLAG_CACHE_INVALIDATE;
      if (flushes & TU_CMD_FLAG_SUBPASS_SLICE_FENCE)
         flushes |= TU_CMD_FLAG_WAIT_FOR_IDLE;
      flushes &= ~(TU_CMD_FLAG_CACHE_INVALIDATE_GMEM |
                   TU_CMD_FLAG_SUBPASS_SLICE_FENCE);
   }
"""

def apply(path: Path):
    s = path.read_text()
    if s.count(OLD) != 1:
        raise RuntimeError("Pinned Mesa tu6_emit_flushes debug flags drifted")
    if "gamehub_a830_legacy_subpass" in s or "gamehub_a830_legacy_blit_clean" in s:
        raise RuntimeError("Old R5/R6 cache patches must not be stacked")
    if "gamehub_a830_legacy_strong_barrier_flags" in s:
        raise RuntimeError("Already applied")
    for needle in ("TU_CMD_FLAG_CACHE_INVALIDATE_GMEM",
                   "TU_CMD_FLAG_SUBPASS_SLICE_FENCE",
                   "FD_SUBPASS_SLICE_FENCE", "TU_CMD_FLAG_BLIT_CACHE_CLEAN",
                   "tu6_emit_flushes("):
        if needle not in s:
            raise RuntimeError("Pinned Mesa cache source changed: " + needle)
    p = s.index("tu6_emit_flushes(")
    q = s.index(OLD)
    if not (p < q < p + 3000):
        raise RuntimeError("Promotion anchor outside of cache flush function")
    s = s.replace(OLD, NEW, 1)
    if s.index("gamehub_a830_legacy_strong_barrier_flags") > s.index(
           "if (flushes & (TU_CMD_FLAG_CCU_CLEAN_COLOR"):
        raise RuntimeError("Flag promotion occurred after event emission")
    path.write_text(s)
    print("PASS: original A830 strong global invalidate/wait order via V38 flush primitives")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv) > 1 else
          Path("src/freedreno/vulkan/tu_cmd_buffer.cc"))
