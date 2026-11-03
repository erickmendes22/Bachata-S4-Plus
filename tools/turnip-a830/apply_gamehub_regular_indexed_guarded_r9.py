#!/usr/bin/env python3
"""Backport the guarded regular indexed draw split from *functional* GameHub.

ELF 1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
AArch64 0x94c42c..0x94c93c, 0x99bdbc..0x99be14.

Unlike the earlier FAILED R1 attempt:
  * the original checks VS -> has_no_side_effects: x8+0x5ee == 1;
  * VS -> num_sampler_prefetch: x8+0x6f4 == 0;
  * FS -> reads_primid: x8+0x560 bit 0 == 0.
  * only triangle list, no restart, one instance, no GS.
R1 only filtered gl_PrimitiveID and was not faithful to the ELF. The
original limits are 0x600 or 0x1800 depending on a separate runtime bit
in physical_device+0x326. Keep the A830 enhanced 0x1800 limit, and
refuse any ambiguous shader state. Do not change draws on other chips.

The V38 IR3 compiler only filled has_no_side_effects for FS, whereas
the original GameHub writes that byte for all stages from NIR
info.writes_memory (0xacc00c); populate it for VS as well.
"""

from pathlib import Path
import sys

SHADER_FILE=Path("src/freedreno/ir3/ir3_compiler_nir.c")
DRAW_FILE=Path("src/freedreno/vulkan/tu_cmd_buffer.cc")

OLD_SHADERS="""   if (so->type == MESA_SHADER_FRAGMENT) {
      so->empty = is_empty(ir) && so->outputs_count == 0 &&
                  so->num_sampler_prefetch == 0;
      so->has_no_side_effects = !ctx->s->info.writes_memory;
      so->has_no_ds_effects = !so->has_kill && !so->writes_pos &&"""
NEW_SHADERS="""   /* GameHub A830 original compiler: the shader-side-effect flag is
    * initialized for VS too. The original regular indexed split checks
    * this property on the vertex shader (ELF 0x94c73c).
    */
   so->has_no_side_effects = !ctx->s->info.writes_memory;

   if (so->type == MESA_SHADER_FRAGMENT) {
      so->empty = is_empty(ir) && so->outputs_count == 0 &&
                  so->num_sampler_prefetch == 0;
      so->has_no_ds_effects = !so->has_kill && !so->writes_pos &&"""

OLD_DRAW="""   tu6_draw_common<CHIP>(cmd, cs, true, indexCount);

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

NEW_DRAW="""   tu6_draw_common<CHIP>(cmd, cs, true, indexCount);

   // GameHub A830 direct indexed path: original ELF 0x94c42c-0x94c93c.
   // This is NOT the unrelated Qualcomm *indirect* draw workaround.
   // One state setup and one trace span, but several identical CP packets.
   const uint64_t gamehub_chip_id = cmd->device->physical_device->dev_id.chip_id;
   const bool gamehub_is_a830 =
      gamehub_chip_id == 0xffff44050000ull ||
      gamehub_chip_id == 0xffff44050001ull ||
      gamehub_chip_id == 0x44050001ull;
   const uint32_t gamehub_split_limit = 0x1800u;

   const auto *gamehub_vs = cmd->state.shaders[MESA_SHADER_VERTEX]->variant;
   const auto *gamehub_fs = cmd->state.shaders[MESA_SHADER_FRAGMENT]->variant;

   const bool gamehub_can_split_regular_indexed =
      CHIP >= A8XX && gamehub_is_a830 &&
      indexCount > gamehub_split_limit && instanceCount == 1u &&
      firstIndex <= UINT32_MAX - indexCount &&
      cmd->vk.dynamic_graphics_state.ia.primitive_topology ==
         VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST &&
      !cmd->vk.dynamic_graphics_state.ia.primitive_restart_enable &&
      !cmd->state.rp.xfb_used &&
      !cmd->state.shaders[MESA_SHADER_TESS_CTRL]->variant &&
      !cmd->state.shaders[MESA_SHADER_TESS_EVAL]->variant &&
      !cmd->state.shaders[MESA_SHADER_GEOMETRY]->variant &&
      gamehub_vs &&
      gamehub_vs->has_no_side_effects &&
      gamehub_vs->num_sampler_prefetch == 0 &&
      (!gamehub_fs || !gamehub_fs->reads_primid);

   if (gamehub_can_split_regular_indexed) {
      // The original packet stream increments firstIndex, not the IB base
      // or vertexOffset, and never repeats tu6_draw_common inside the loop.
      for (uint32_t gamehub_start = 0; gamehub_start < indexCount;) {
         uint32_t gamehub_count =
            MIN2(indexCount - gamehub_start, gamehub_split_limit);
         tu_cs_emit_pkt7(cs, CP_DRAW_INDX_OFFSET, 7);
         tu_cs_emit(cs, tu_draw_initiator(cmd, DI_SRC_SEL_DMA));
         tu_cs_emit(cs, 1u);
         tu_cs_emit(cs, gamehub_count);
         tu_cs_emit(cs, firstIndex + gamehub_start);
         tu_cs_emit_qw(cs, cmd->state.index_va);
         tu_cs_emit(cs, cmd->state.max_index_count);
         gamehub_start += gamehub_count;
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

def apply(shader:Path,draw:Path):
    s=shader.read_text()
    t=draw.read_text()
    if s.count(OLD_SHADERS)!=1 or t.count(OLD_DRAW)!=1:
        raise RuntimeError("Pinned Mesa IR3/indexed-draw source drift or already patched")
    s=s.replace(OLD_SHADERS,NEW_SHADERS,1)
    t=t.replace(OLD_DRAW,NEW_DRAW,1)
    for must in ["has_no_side_effects", "num_sampler_prefetch == 0",
                 "!gamehub_fs->reads_primid", "gamehub_split_limit"]:
        if must not in t:
            raise RuntimeError("Incomplete GameHub guarded indexed patch: "+must)
    shader.write_text(s)
    draw.write_text(t)
    print("PASS: exact original three shader guards + regular-indexed A830 draw limit integrated")

if __name__=="__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else SHADER_FILE,
          Path(sys.argv[2]) if len(sys.argv)>2 else DRAW_FILE)
