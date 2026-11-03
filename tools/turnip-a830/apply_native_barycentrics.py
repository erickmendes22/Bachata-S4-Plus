#!/usr/bin/env python3
"""Restore the complete A8xx KHR barycentric NIR lowering from the tested
pre-DrawstateFix-v2 branch, without copying its unrelated A8xx regressions.

Source is Mesa f28352d in the StevenMXZ 2026-10-19 V38 recipe. Applying only
the extension-advertisement fields would be invalid: the NIR 3-component
BaryCoord and native per-vertex input support are required in tandem.
Do not assume this passes Vulkan CTS without physical device verification.
"""
from pathlib import Path

def apply(path, substitutions):
    p = Path(path)
    s = p.read_text()
    for old, new, label in substitutions:
        n = s.count(old)
        if n != 1:
            raise SystemExit(f"A830 KHR barycentrics: {path}: {label}: expected 1, found {n}")
        s = s.replace(old, new, 1)
    p.write_text(s)

def main():
    comp = "src/freedreno/ir3/ir3_compiler_nir.c"
    old = """      nir_intrinsic_instr *baryc = nir_def_as_intrinsic(intr->src[0].ssa);
      if (nir_intrinsic_interp_mode(baryc) == INTERP_MODE_NONE)
         so->inputs[n].rasterflat = true;"""
    new = """      /* A8xx lowering can supply explicitly constructed IJ coords instead
       * of a nir_intrinsic barycentric source. Do not reinterpret a vector as
       * a nir_intrinsic_instr. */
      if (nir_def_instr_type(intr->src[0].ssa) == nir_instr_type_intrinsic) {
         nir_intrinsic_instr *baryc = nir_def_as_intrinsic(intr->src[0].ssa);
         if (nir_intrinsic_has_interp_mode(baryc) &&
             nir_intrinsic_interp_mode(baryc) == INTERP_MODE_NONE)
            so->inputs[n].rasterflat = true;
      }"""
    apply(comp, [(old, new, "rasterflat guard")])

    lower = r"""
/* Qualcomm A8xx: SPIR-V BaryCoordKHR and BaryCoordNoPerspKHR arrive as
 * 3-component NIR intrinsics. Hardware exposes I,J; K=1-I-J. For per-vertex
 * inputs, select an exact vertex with IJ=(0,0),(1,0),(0,1). Keep the
 * original interpolant mode and metadata. This is an explicit lowering,
 * never just extension advertisement.
 */
static bool
ir3_lower_khr_barycentrics_cb(nir_builder *b, nir_intrinsic_instr *intr,
                              void *data)
{
   nir_intrinsic_op op;
   switch (intr->intrinsic) {
   case nir_intrinsic_load_barycentric_coord_pixel:
      op = nir_intrinsic_load_barycentric_pixel;
      break;
   case nir_intrinsic_load_barycentric_coord_centroid:
      op = nir_intrinsic_load_barycentric_centroid;
      break;
   case nir_intrinsic_load_barycentric_coord_sample:
      op = nir_intrinsic_load_barycentric_sample;
      break;
   case nir_intrinsic_load_barycentric_coord_at_sample:
      op = nir_intrinsic_load_barycentric_at_sample;
      break;
   case nir_intrinsic_load_barycentric_coord_at_offset:
      op = nir_intrinsic_load_barycentric_at_offset;
      break;
   /* GameHub A830 handles load_input_vertex in the IR3 compiler using
    * native OPC_LDLV. Do not emulate PerVertexKHR with BARY_F: that
    * interpolates values instead of fetching raw integer/float attributes.
    * apply_gamehub_ir3_native_pervertex.py adds the exact native path. */
   default:
      return false;
   }
   b->cursor = nir_before_instr(&intr->instr);
   unsigned mode = nir_intrinsic_interp_mode(intr);
   nir_def *ij;
   if (op == nir_intrinsic_load_barycentric_at_sample)
      ij = nir_load_barycentric_at_sample(b, intr->def.bit_size,
                                         intr->src[0].ssa, .interp_mode = mode);
   else if (op == nir_intrinsic_load_barycentric_at_offset)
      ij = nir_load_barycentric_at_offset(b, intr->def.bit_size,
                                         intr->src[0].ssa, .interp_mode = mode);
   else
      ij = nir_load_barycentric(b, op, mode);
   nir_def *i = nir_channel(b, ij, 0);
   nir_def *j = nir_channel(b, ij, 1);
   nir_def *k = nir_fsub(b, nir_imm_float(b, 1.0f), nir_fadd(b, i, j));
   nir_def *coords[3] = {k, i, j};
   nir_def_replace(&intr->def, nir_vec(b, coords, 3));
   return true;
}

static bool
ir3_lower_khr_barycentrics(nir_shader *s)
{
   if (s->info.stage != MESA_SHADER_FRAGMENT)
      return false;
   return nir_shader_intrinsics_pass(s, ir3_lower_khr_barycentrics_cb,
                                     nir_metadata_control_flow, NULL);
}

"""
    path = "src/freedreno/ir3/ir3_nir.c"
    apply(path, [
      ("void\nir3_finalize_nir(struct ir3_compiler *compiler,", lower + "void\nir3_finalize_nir(struct ir3_compiler *compiler,", "NIR pass implementation"),
      ("   MESA_TRACE_FUNC();\n\n   struct nir_lower_tex_options tex_options = {", "   MESA_TRACE_FUNC();\n\n   NIR_PASS(_, s, ir3_lower_khr_barycentrics);\n\n   struct nir_lower_tex_options tex_options = {", "invoke KHR NIR lowering")
    ])

    path = "src/freedreno/vulkan/tu_device.cc"
    apply(path, [
      ("      .KHR_format_feature_flags2 = true,\n      .KHR_fragment_shading_rate = ",
       "      .KHR_format_feature_flags2 = true,\n      .KHR_fragment_shader_barycentric = device->info->chip >= A8XX,\n      .KHR_fragment_shading_rate = ",
       "Vulkan extension advertise"),
      ("   features->dynamicRenderingLocalRead = true;\n\n   /* VK_KHR_fragment_shading_rate */",
       "   features->dynamicRenderingLocalRead = true;\n\n   /* VK_KHR_fragment_shader_barycentric: IR3 conversion in ir3_nir.c */\n   features->fragmentShaderBarycentric = pdevice->info->chip >= A8XX;\n\n   /* VK_KHR_fragment_shading_rate */",
       "feature enable"),
    ])
    for path, snippets in {
      "src/freedreno/ir3/ir3_nir.c": ("ir3_lower_khr_barycentrics_cb", "NIR_PASS(_, s, ir3_lower_khr_barycentrics);"),
      "src/freedreno/ir3/ir3_compiler_nir.c": ("nir_intrinsic_has_interp_mode(baryc)",),
      "src/freedreno/vulkan/tu_device.cc": (".KHR_fragment_shader_barycentric = device->info->chip >= A8XX,", "features->fragmentShaderBarycentric = pdevice->info->chip >= A8XX;"),
    }.items():
      s = Path(path).read_text()
      for fragment in snippets:
         if fragment not in s:
            raise SystemExit(f"A830 KHR barycentrics: missing postcondition {path}: {fragment}")
    print("A830 native barycentrics restored: extension, feature, IR3 NIR lowering and rasterflat guard")

if __name__ == "__main__":
    main()
