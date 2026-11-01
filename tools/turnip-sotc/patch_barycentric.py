#!/usr/bin/env python3
"""Backport experimental native KHR_fragment_shader_barycentric to A8xx IR3.

Fail closed on source drift. This is an IR3 implementation, not an extension
string spoof. Needs Vulkan CTS + Shadow of the Colossus hardware validation.
"""
from pathlib import Path

def replace_exact(path, old, new, name):
    p=Path(path)
    src=p.read_text()
    assert src.count(old)==1, f"{name}: expected exactly one anchor, got {src.count(old)}"
    p.write_text(src.replace(old,new,1))
    print("Applied:",name)

replace_exact("src/freedreno/vulkan/tu_device.cc",
    "      .KHR_fragment_shading_rate = device->info->props.has_attachment_shading_rate,",
    "      .KHR_fragment_shader_barycentric = device->info->chip >= A8XX,\n"
    "      .KHR_fragment_shading_rate = device->info->props.has_attachment_shading_rate,",
    "advertise VK_KHR_fragment_shader_barycentric for A8xx")
replace_exact("src/freedreno/vulkan/tu_device.cc",
    "   /* VK_KHR_fragment_shading_rate */\n"
    "   features->pipelineFragmentShadingRate",
    "   /* VK_KHR_fragment_shader_barycentric requires IR3 lowering below. */\n"
    "   features->fragmentShaderBarycentric = pdevice->info->chip >= A8XX;\n\n"
    "   /* VK_KHR_fragment_shading_rate */\n"
    "   features->pipelineFragmentShadingRate",
    "enable barycentric feature for A8xx")

lowering=r'''/* A8xx KHR_fragment_shader_barycentric implementation.
 * SPIR-V BaryCoordKHR / BaryCoordNoPerspKHR become 3-component NIR
 * barycentric intrinsics. IR3 supplies I,J as 2 components, so generate
 * K=1-I-J. The ordering is (K,I,J).
 *
 * PerVertexKHR inputs become load_input_vertex. Turn the requested vertex
 * into explicit barycentric interpolation of the original varying.
 * These semantics must pass Vulkan CTS on physical A830 prior to release.
 */
static bool
ir3_lower_khr_barycentrics_cb(nir_builder *b, nir_intrinsic_instr *intr,
                              void *data)
{
   nir_intrinsic_op op;
   switch (intr->intrinsic) {
   case nir_intrinsic_load_barycentric_coord_pixel:
      op=nir_intrinsic_load_barycentric_pixel;
      break;
   case nir_intrinsic_load_barycentric_coord_centroid:
      op=nir_intrinsic_load_barycentric_centroid;
      break;
   case nir_intrinsic_load_barycentric_coord_sample:
      op=nir_intrinsic_load_barycentric_sample;
      break;
   case nir_intrinsic_load_barycentric_coord_at_sample:
      op=nir_intrinsic_load_barycentric_at_sample;
      break;
   case nir_intrinsic_load_barycentric_coord_at_offset:
      op=nir_intrinsic_load_barycentric_at_offset;
      break;
   case nir_intrinsic_load_input_vertex: {
      b->cursor=nir_before_instr(&intr->instr);
      nir_def *v=intr->src[0].ssa;
      nir_def *zero=nir_imm_float(b,0.0f);
      nir_def *one=nir_imm_float(b,1.0f);
      nir_def *ij=nir_vec2(b,
         nir_bcsel(b,nir_ieq_imm(b,v,1),one,zero),
         nir_bcsel(b,nir_ieq_imm(b,v,2),one,zero));
      nir_def *out=nir_load_interpolated_input(
         b,intr->def.num_components,intr->def.bit_size,
         ij,intr->src[1].ssa,
         .base=nir_intrinsic_base(intr),
         .component=nir_intrinsic_component(intr),
         .dest_type=nir_intrinsic_dest_type(intr),
         .io_semantics=nir_intrinsic_io_semantics(intr));
      nir_def_replace(&intr->def,out);
      return true;
   }
   default:
      return false;
   }
   b->cursor=nir_before_instr(&intr->instr);
   unsigned mode=nir_intrinsic_interp_mode(intr);
   nir_def *ij;
   if (op==nir_intrinsic_load_barycentric_at_sample)
      ij=nir_load_barycentric_at_sample(b,intr->def.bit_size,
          intr->src[0].ssa,.interp_mode=mode);
   else if (op==nir_intrinsic_load_barycentric_at_offset)
      ij=nir_load_barycentric_at_offset(b,intr->def.bit_size,
          intr->src[0].ssa,.interp_mode=mode);
   else
      ij=nir_load_barycentric(b,op,mode);
   nir_def *i=nir_channel(b,ij,0);
   nir_def *j=nir_channel(b,ij,1);
   nir_def *k=nir_fsub(b,nir_imm_float(b,1.0f),nir_fadd(b,i,j));
   nir_def *coords[3]={k,i,j};
   nir_def_replace(&intr->def,nir_vec(b,coords,3));
   return true;
}
static bool
ir3_lower_khr_barycentrics(nir_shader *s)
{
   if (s->info.stage != MESA_SHADER_FRAGMENT)
      return false;
   return nir_shader_intrinsics_pass(s,ir3_lower_khr_barycentrics_cb,
                                     nir_metadata_control_flow,NULL);
}

'''
replace_exact("src/freedreno/ir3/ir3_nir.c",
    "void\nir3_finalize_nir(struct ir3_compiler *compiler,",
    lowering+"void\nir3_finalize_nir(struct ir3_compiler *compiler,",
    "implement barycoord and per-vertex lowering in IR3")
replace_exact("src/freedreno/ir3/ir3_nir.c",
    "   MESA_TRACE_FUNC();\n\n   struct nir_lower_tex_options tex_options = {",
    "   MESA_TRACE_FUNC();\n\n"
    "   NIR_PASS(_, s, ir3_lower_khr_barycentrics);\n\n"
    "   struct nir_lower_tex_options tex_options = {",
    "lower barycentrics before compiler optimizations")
replace_exact("src/freedreno/ir3/ir3_compiler_nir.c",
    "      nir_intrinsic_instr *baryc = nir_def_as_intrinsic(intr->src[0].ssa);\n"
    "      if (nir_intrinsic_interp_mode(baryc) == INTERP_MODE_NONE)\n"
    "         so->inputs[n].rasterflat = true;",
    "      if (nir_def_instr_type(intr->src[0].ssa) == nir_instr_type_intrinsic) {\n"
    "         nir_intrinsic_instr *baryc = nir_def_as_intrinsic(intr->src[0].ssa);\n"
    "         if (nir_intrinsic_has_interp_mode(baryc) &&\n"
    "             nir_intrinsic_interp_mode(baryc) == INTERP_MODE_NONE)\n"
    "            so->inputs[n].rasterflat = true;\n"
    "      }",
    "accept constant explicit interpolation coordinates in IR3")
print("SOURCE_PATCH_COMPLETE")
