#!/usr/bin/env python3
"""Reconstruct the A830 indexed draw segmentation observed in functional GameHub ELF.

Original ELF sha256: 1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
AArch64:
  0x99bda8..0x99be14: A830 indexed draw quirk init, limit 0x600/0x1800
  0x94c42c..0x94c47c: enabled && instanceCount==1 && count>limit,
                       triangle list, no primitive restart, shader guards
  0x94c7bc..0x94c93c: CP_DRAW_INDX_OFFSET repeated with chunk count and
                       firstIndex offset (without replaying full draw-state).
The exact runtime byte at +0x326 is private to GameHub and is not the
V38 driconf option. Use the enabled 0x1800 path only on A830 and apply
conservative shader guards. No changes for other chips or multi-draw.
"""
from pathlib import Path
import sys

SOURCE = Path("src/freedreno/vulkan/tu_cmd_buffer.cc")

BEFORE = """   tu6_draw_common<CHIP>(cmd, cs, true, indexCount);

   tu_cs_emit_pkt7(cs, CP_DRAW_INDX_OFFSET, 7);
   tu_cs_emit(cs, tu_draw_initiator(cmd, DI_SRC_SEL_DMA));
   tu_cs_emit(cs, instanceCount);
   tu_cs_emit(cs, indexCount);
   tu_cs_emit(cs, firstIndex);
   tu_cs_emit_qw(cs, cmd->state.index_va);
   tu_cs_emit(cs, cmd->state.max_index_count);

   trace_end_draw(&cmd->rp_trace, cs);
}
TU_GENX(tu_CmdDrawIndexed);"""

AFTER = """   tu6_draw_common<CHIP>(cmd, cs, true, indexCount);

   // Original GameHub A830 (ELF 0x94c42c..0x94c93c) segments certain
   // large triangle-list indexed draws. Pinned Mesa V38 lacks this path.
   // Preserve one Vulkan draw call, one state setup, and one trace event.
   // It is unsafe to split primitive ID users, tessellation, GS, transform
   // feedback, primitive-restart draws, or instanced draws.
   const uint64_t chip_id = cmd->device->physical_device->dev_id.chip_id;
   const bool is_a830 = chip_id == 0xffff44050000ull ||
                        chip_id == 0xffff44050001ull ||
                        chip_id == 0x44050001ull;
   const auto *vs = cmd->state.shaders[MESA_SHADER_VERTEX]->variant;
   const auto *fs = cmd->state.shaders[MESA_SHADER_FRAGMENT]->variant;
   const bool can_split =
      CHIP >= A8XX && is_a830 && indexCount > 0x1800u && instanceCount == 1 &&
      cmd->vk.dynamic_graphics_state.ia.primitive_topology ==
         VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST &&
      !cmd->vk.dynamic_graphics_state.ia.primitive_restart_enable &&
      !cmd->state.shaders[MESA_SHADER_TESS_CTRL]->variant &&
      !cmd->state.shaders[MESA_SHADER_TESS_EVAL]->variant &&
      !cmd->state.shaders[MESA_SHADER_GEOMETRY]->variant &&
      !cmd->state.rp.xfb_used && vs && !vs->reads_primid &&
      (!fs || !fs->reads_primid);

   if (can_split) {
      // 0x1800 indices is divisible by three: triangle boundaries preserved.
      for (uint32_t start = 0; start < indexCount;) {
         const uint32_t count = MIN2(indexCount - start, 0x1800u);
         tu_cs_emit_pkt7(cs, CP_DRAW_INDX_OFFSET, 7);
         tu_cs_emit(cs, tu_draw_initiator(cmd, DI_SRC_SEL_DMA));
         tu_cs_emit(cs, instanceCount);
         tu_cs_emit(cs, count);
         tu_cs_emit(cs, firstIndex + start);
         tu_cs_emit_qw(cs, cmd->state.index_va);
         tu_cs_emit(cs, cmd->state.max_index_count);
         start += count;
      }
   } else {
      tu_cs_emit_pkt7(cs, CP_DRAW_INDX_OFFSET, 7);
      tu_cs_emit(cs, tu_draw_initiator(cmd, DI_SRC_SEL_DMA));
      tu_cs_emit(cs, instanceCount);
      tu_cs_emit(cs, indexCount);
      tu_cs_emit(cs, firstIndex);
      tu_cs_emit_qw(cs, cmd->state.index_va);
      tu_cs_emit(cs, cmd->state.max_index_count);
   }

   trace_end_draw(&cmd->rp_trace, cs);
}
TU_GENX(tu_CmdDrawIndexed);"""

def apply(path: Path):
    s = path.read_text()
    if s.count(BEFORE) != 1 or AFTER in s:
        raise ValueError("Pinned Mesa V38 draw path mismatch/duplicate; fail closed")
    s = s.replace(BEFORE, AFTER, 1)
    path.write_text(s)
    assert s.count("Original GameHub A830 (ELF 0x94c42c..0x94c93c)") == 1
    print("PASS: GameHub A830 conditional indexed draw segmentation ported")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE)
