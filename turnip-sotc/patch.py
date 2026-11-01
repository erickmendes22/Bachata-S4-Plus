#!/usr/bin/env python3
"""A8xx experimental native KHR_fragment_shader_barycentric for Mesa Turnip."""
from pathlib import Path

def edit(file, old, new, label):
    p = Path(file)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit(f"FAIL (refuse unanchored edit) {file}: {label}: matches={s.count(old)}")
    p.write_text(s.replace(old, new, 1))
    print("APPLIED", label)

device="src/freedreno/vulkan/tu_device.cc"
nir="src/freedreno/ir3/ir3_nir.c"
compiler="src/freedreno/ir3/ir3_compiler_nir.c"

edit(device,
     "      .KHR_fragment_shading_rate = device->info->props.has_attachment_shading_rate,",
     "      .KHR_fragment_shader_barycentric = device->info->chip >= A8XX,\n"
     "      .KHR_fragment_shading_rate = device->info->props.has_attachment_shading_rate,",
     "Vulkan extension")
edit(device,
     "   /* VK_KHR_fragment_shading_rate */\n",
     "   /* KHR_fragment_shader_barycentric: IR3 native NIR lowering below. */\n"
     "   features->fragmentShaderBarycentric = pdevice->info->chip >= A8XX;\n\n"
     "   /* VK_KHR_fragment_shading_rate */\n",
     "Vulkan feature")

code=r"""
/* A8xx barycentric support: IR3 consumes IJ pairs, Vulkan wants XYZ.
 * PerVertexKHR uses corner-specific IJ via the existing bary.f path.
 * The strict triangle vertex order must be verified on device.
 */
static bool
ir3_nir_lower_khr_fs_barycentrics_cb(nir_builder *b,
                                     nir_intrinsic_instr *intr,
                                     void *data)
{
   nir_intrinsic_op bary_op;
   switch (intr->intrinsic) {
   case nir_intrinsic_load_barycentric_coord_pixel:
      bary_op = nir_intrinsic_load_barycentric_pixel;
      break;
   case nir_intrinsic_load_barycentric_coord_centroid:
      bary_op = nir_intrinsic_load_barycentric_centroid;
      break;
   case nir_intrinsic_load_barycentric_coord_sample:
      bary_op = nir_intrinsic_load_barycentric_sample;
      break;
   case nir_intrinsic_load_barycentric_coord_at_sample:
      bary_op = nir_intrinsic_load_barycentric_at_sample;
      break;
   case nir_intrinsic_load_barycentric_coord_at_offset:
      bary_op = nir_intrinsic_load_barycentric_at_offset;
      break;
   case nir_intrinsic_load_input_vertex: {
      b->cursor = nir_before_instr(&intr->instr);
      nir_def *v = intr->src[0].ssa;
      nir_def *zero = nir_imm_float(b, 0.0f);
      nir_def *one = nir_imm_float(b, 1.0f);
      nir_def *ij = nir_vec2(b,
         nir_bcsel(b, nir_ieq_imm(b, v, 1), one, zero),
         nir_bcsel(b, nir_ieq_imm(b, v, 2), one, zero));
      nir_def *result = nir_load_interpolated_input(
         b, intr->def.num_components, intr->def.bit_size,
         ij, intr->src[1].ssa,
         .base = nir_intrinsic_base(intr),
         .component = nir_intrinsic_component(intr),
         .dest_type = nir_intrinsic_dest_type(intr),
         .io_semantics = nir_intrinsic_io_semantics(intr));
      nir_def_rewrite_uses(&intr->def, result);
      return true;
   }
   default:
      return false;
   }

   b->cursor = nir_before_instr(&intr->instr);
   unsigned mode = nir_intrinsic_interp_mode(intr);
   nir_def *xy;
   if (bary_op == nir_intrinsic_load_barycentric_at_sample) {
      xy = nir_load_barycentric_at_sample(b, intr->def.bit_size,
         intr->src[0].ssa, .interp_mode = mode);
   } else if (bary_op == nir_intrinsic_load_barycentric_at_offset) {
      xy = nir_load_barycentric_at_offset(b, intr->def.bit_size,
         intr->src[0].ssa, .interp_mode = mode);
   } else {
      xy = nir_load_barycentric(b, bary_op, mode);
   }

   nir_def *i = nir_channel(b, xy, 0);
   nir_def *j = nir_channel(b, xy, 1);
   nir_def *k = nir_fsub(b, nir_imm_float(b, 1.0f), nir_fadd(b, i, j));
   nir_def *bary[3] = {k, i, j};
   nir_def_rewrite_uses(&intr->def, nir_vec(b, bary, 3));
   return true;
}

static bool
ir3_nir_lower_khr_fs_barycentrics(nir_shader *shader)
{
   if (shader->info.stage != MESA_SHADER_FRAGMENT)
      return false;
   return nir_shader_intrinsics_pass(shader,
      ir3_nir_lower_khr_fs_barycentrics_cb,
      nir_metadata_control_flow, NULL);
}

"""
edit(nir,
     "void\nir3_finalize_nir(struct ir3_compiler *compiler,",
     code + "void\nir3_finalize_nir(struct ir3_compiler *compiler,",
     "lower KHR input_vertex and barycentric_coord in IR3")
edit(nir,
     "   MESA_TRACE_FUNC();\n\n   struct nir_lower_tex_options tex_options = {",
     "   MESA_TRACE_FUNC();\n\n"
     "   NIR_PASS(_, s, ir3_nir_lower_khr_fs_barycentrics);\n\n"
     "   struct nir_lower_tex_options tex_options = {",
     "invoke native barycentric NIR lowering")
edit(compiler,
     """      nir_intrinsic_instr *baryc = nir_def_as_intrinsic(intr->src[0].ssa);
      if (nir_intrinsic_interp_mode(baryc) == INTERP_MODE_NONE)
         so->inputs[n].rasterflat = true;""",
     """      if (intr->src[0].ssa->parent_instr->type == nir_instr_type_intrinsic) {
         nir_intrinsic_instr *baryc = nir_def_as_intrinsic(intr->src[0].ssa);
         if (nir_intrinsic_has_interp_mode(baryc) &&
             nir_intrinsic_interp_mode(baryc) == INTERP_MODE_NONE)
            so->inputs[n].rasterflat = true;
      }""",
     "accept explicitly supplied per-vertex coordinates")
print("BARYCENTRIC_IMPLEMENTATION_PATCHED=1")
