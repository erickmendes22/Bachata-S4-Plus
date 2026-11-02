#!/usr/bin/env python3
"""Backport conservative A830 subpass visibility to the pinned Turnip V38.

Evidence:
- Exact GameHub original libvulkan_freedreno.so SHA256:
  1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
- ARM64 basic cache-flush path 0x95ef54..0x95f550 has the old explicit
  CACHE_INVALIDATE, CCU clean, WAIT_FOR_IDLE and WAIT_FOR_ME path.
- Mesa 26.2 tu_cmd_buffer.cc::tu6_emit_flushes has no
  FD_SUBPASS_SLICE_FENCE path, while the pinned V38 uses this newer,
  weaker slice fence instead of a full global visibility synchronization.
- Previous BLIT_CACHE_CLEAN experiment cannot affect the A830 conditional
  because compiled subpass_fence_cleans_resolve == 0 (offset +0x30d).

This change is conservative, not an assertion that an A830 slice fence is
incorrect per spec: for A830 only, replace the *new* slice fence path with
cache invalidation plus a full wait. The existing read/write hazard planner,
CCU CLEAN/INVALIDATE ordering, and SYS/GMEM mode condition remain unchanged.
No global forced sysmem, no changes on other GPUs.
"""
from pathlib import Path
import sys

BEFORE = """      if (CHIP >= A8XX) {
         tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_LABEL);
         tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_SUBPASS_SLICE_FENCE);
         tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_LABEL);
      } else {
         tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_SUBPASS_FENCE);
      }"""
AFTER = """      if (CHIP >= A8XX) {
         // Restore GameHub-compatible full visibility on A830 where the
         // optimized V38 slice-fence path differs from the original driver.
         // The cache planner already emitted required CCU cleans above.
         // This is the remaining full invalidation and completion wait.
         const uint64_t chip_id = cmd_buffer->device->physical_device->dev_id.chip_id;
         const bool gamehub_a830_legacy_subpass =
            chip_id == 0xffff44050000ull ||
            chip_id == 0xffff44050001ull ||
            chip_id == 0x44050001ull;
         if (gamehub_a830_legacy_subpass) {
            tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_CACHE_INVALIDATE);
            tu_cs_emit_wfi(cs);
         } else {
            tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_LABEL);
            tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_SUBPASS_SLICE_FENCE);
            tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_LABEL);
         }
      } else {
         tu_emit_event_write<CHIP>(cmd_buffer, cs, FD_SUBPASS_FENCE);
      }"""

def apply(path: Path):
    s=path.read_text()
    if s.count(BEFORE)!=1 or "gamehub_a830_legacy_subpass" in s:
        raise ValueError("Pinned V38 subpass fence sequence changed or duplicate")
    for marker in ("tu6_emit_flushes(struct tu_cmd_buffer *cmd_buffer",
                   "TU_CMD_FLAG_CCU_CLEAN_COLOR", "TU_CMD_FLAG_CCU_CLEAN_DEPTH",
                   "TU_CMD_FLAG_CACHE_INVALIDATE_GMEM", "TU_CMD_FLAG_WAIT_FOR_IDLE",
                   "if (emit_subpass_slice_fence)",
                   "tu_cond_exec_end(cs);"):
        if marker not in s:
            raise ValueError("Required cache barrier guard missing: "+marker)
    s=s.replace(BEFORE,AFTER,1)
    path.write_text(s)
    assert s.count("gamehub_a830_legacy_subpass") == 2
    print("PASS: A830 full subpass cache visibility backport with source guards")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/vulkan/tu_cmd_buffer.cc"))
