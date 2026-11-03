#!/usr/bin/env python3
"""Backport the *native* IR3 PerVertexKHR fetch path from working GameHub A830.

Evidence: original GameHub ELF SHA256 1a109bee... (and identical GameHub DD):
  - nir_intrinsic_load_input_vertex (NIR ID 455) and load_per_vertex_input
    (ID 502) share native input-handling control flow at 0xAD42B0.
  - 0xAD71C8 and 0xAD7354 emit opcode 0x31F, which is OPC_LDLV on this ISA.
  - Missing-index handling clamps vertex index to (primitive_vertices-1)
    in 0xAD70D8..0xAD70E8.
R11 instead transforms load_input_vertex to load_interpolated_input with
synthetic IJ, causing OPC_BARY_F. This can change raw PerVertexKHR input
bits (integer/nan/signed-zero) and invalid-vertex behavior on points/lines.

Only applies on IR3 gen8, for extension usage enabled on 8xx by
apply_native_barycentrics.py. No framebuffer or APK changes.
Source guards prevent wrong patch application. Actual A830 shader output
parity STILL requires testing; do not distribute a driver based solely on this.
"""
from pathlib import Path
import sys

def replace_once(s, old, new, label):
    count=s.count(old)
    if count!=1:
        raise RuntimeError(f"R11 pinned IR3 drift {label}: expected one, found {count}")
    return s.replace(old,new,1)

HELPER= r'''// Native A830 PerVertexKHR: fetch a specific un-interpolated vertex
// attribute. The working GameHub emits OPC_LDLV (0x31f), not OPC_BARY_F.
// The NIR load_input_vertex source is the uint vertex index; the existing
// vertex input offset/slot bookkeeping in setup_input remains unchanged.
static struct ir3_instruction_rpt
create_frag_input_vertex(struct ir3_context *ctx,
                         struct ir3_instruction *vertex,
                         unsigned n, unsigned ncomp)
{
   struct ir3_builder *build = &ctx->build;
   struct ir3_instruction_rpt values;
   for (unsigned i = 0; i < ncomp; i++) {
      struct ir3_instruction *offset = create_immed(build, n + i);
      values.rpts[i] = ir3_LDLV(build, offset, 0, vertex, 0);
      values.rpts[i]->cat6.type = TYPE_U32;
      values.rpts[i]->cat6.iim_val = 1;
   }
   return values;
}

'''

def apply(path:Path):
    s=path.read_text()
    s=replace_once(s, "static struct ir3_instruction *\ncreate_driver_param(",
                  HELPER+"static struct ir3_instruction *\ncreate_driver_param(",
                  "native LDLV helper")
    s=replace_once(s,
        """   case nir_intrinsic_load_interpolated_input:
   case nir_intrinsic_load_input:
      setup_input(ctx, intr);""",
        """   case nir_intrinsic_load_input_vertex:
   case nir_intrinsic_load_interpolated_input:
   case nir_intrinsic_load_input:
      setup_input(ctx, intr);""",
        "IR3 dispatch")
    s=replace_once(s,
       """   struct ir3_instruction *coord = NULL;

   if (intr->intrinsic == nir_intrinsic_load_interpolated_input)
      coord =
         ir3_create_collect(&ctx->build, ir3_get_src(ctx, &intr->src[0]), 2);

   compile_assert(ctx, nir_src_is_const(intr->src[coord ? 1 : 0]));

   unsigned frac = nir_intrinsic_component(intr);
   unsigned offset = nir_src_as_uint(intr->src[coord ? 1 : 0]);""",
       """   struct ir3_instruction *coord = NULL;
   struct ir3_instruction *gamehub_vertex = NULL;

   if (intr->intrinsic == nir_intrinsic_load_interpolated_input)
      coord =
         ir3_create_collect(&ctx->build, ir3_get_src(ctx, &intr->src[0]), 2);

   if (intr->intrinsic == nir_intrinsic_load_input_vertex) {
      // The extension is exposed on A8xx. This is not an interpolated
      // BARY_F input: emit an actual per-vertex LDLV load.
      compile_assert(ctx, ctx->compiler->gen >= 8 &&
                               ctx->so->type == MESA_SHADER_FRAGMENT);
      /* Never pass a dynamic GPR to LDLV's immediate operand.
       * The prior unsafe backport caused a device-lost regression. */
      compile_assert(ctx, nir_src_is_const(intr->src[0]) &&
                               nir_src_as_uint(intr->src[0]) < 3);
      gamehub_vertex =
         create_immed(&ctx->build, nir_src_as_uint(intr->src[0]));
   }

   const unsigned offset_src = (coord || gamehub_vertex) ? 1 : 0;
   compile_assert(ctx, nir_src_is_const(intr->src[offset_src]));

   unsigned frac = nir_intrinsic_component(intr);
   unsigned offset = nir_src_as_uint(intr->src[offset_src]);""",
       "native pervertex offset and input")
    s=replace_once(s,
       """      struct ir3_instruction_rpt instr =
         create_frag_input(ctx, coord, idx, ncomp);
      cp_instrs(ctx->last_dst, instr.rpts, ncomp);""",
       """      struct ir3_instruction_rpt instr =
         gamehub_vertex ? create_frag_input_vertex(ctx, gamehub_vertex, idx, ncomp)
                        : create_frag_input(ctx, coord, idx, ncomp);
      cp_instrs(ctx->last_dst, instr.rpts, ncomp);""",
       "raw vertex attribute fetch")
    s=replace_once(s,
        "   so->inputs[n].flat = !coord;",
        "   so->inputs[n].flat = !coord && !gamehub_vertex;",
        "native varying packing")
    assert s.count("create_frag_input_vertex(")==2
    assert s.count("case nir_intrinsic_load_input_vertex:")==1
    assert "ir3_LDLV(build, offset, 0, vertex, 0)" in s
    assert "create_immed(&ctx->build, nir_src_as_uint(intr->src[0]))" in s
    assert "so->inputs[n].flat = !coord && !gamehub_vertex;" in s
    assert "nir_src_is_const(intr->src[offset_src])" in s
    assert "ir3_BARY_F_rpt" in s  # normal interpolation unchanged
    path.write_text(s)
    print("A830 native PerVertexKHR LDLV source path integrated (source-only)")

if __name__=="__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/ir3/ir3_compiler_nir.c"))
