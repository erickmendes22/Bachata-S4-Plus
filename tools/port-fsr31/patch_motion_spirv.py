#!/usr/bin/env python3
"""Integrate Bloodborne Port SPIR-V object velocity into core025 shader recompiler."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
def edit(path,changes):
    f=root/path;s=f.read_text()
    for old,new in changes:
        n=s.count(old)
        if n!=1: raise RuntimeError(f"{path} source mismatch {n}: {old[:100]!r}")
        s=s.replace(old,new)
    f.write_text(s)
base="src/shader_recompiler/backend/spirv/"
edit(base+"spirv_emit_context.h",[(
    "    Id output_position{};",
    """    Id motion_out_cur{};
    Id motion_out_prev{};
    Id motion_in_cur{};
    Id motion_in_prev{};
    Id motion_frag_out{};
    [[nodiscard]] bool VertexMotion() const {
        return stage==Stage::Vertex && runtime_info.vs_info.motion_vectors &&
            MotionVectors::positions_address && MotionVectors::params_address;
    }
    [[nodiscard]] bool FragmentMotion() const {
        return stage==Stage::Fragment && runtime_info.fs_info.motion_vectors;
    }
    Id output_position{};"""
)])
edit(base+"spirv_emit_context.cpp",[
    ("            if (needs_clip_distance_emulation) {",
    """            if(VertexMotion()) {
                motion_out_cur=DefineOutput(F32[4],MotionVectors::CurrentLocation);
                motion_out_prev=DefineOutput(F32[4],MotionVectors::PreviousLocation);
                Name(motion_out_cur,"motion_cur");
                Name(motion_out_prev,"motion_prev");
            }
            if (needs_clip_distance_emulation) {"""),
    ("""            ++num_render_targets;
        }
        // Dual source blending""",
    """            ++num_render_targets;
        }
        if(FragmentMotion() &&
           !Sirit::ValidId(frag_outputs[MotionVectors::Output].id)) {
            motion_frag_out=DefineOutput(F32[4],MotionVectors::Output);
            motion_in_cur=DefineInput(F32[4],MotionVectors::CurrentLocation);
            motion_in_prev=DefineInput(F32[4],MotionVectors::PreviousLocation);
            Name(motion_frag_out,"motion_vector");
        }
        // Dual source blending""")
])
edit(base+"emit_spirv.cpp",[(
    "    if (info.uses_dma) {",
    "    if (info.uses_dma || ctx.VertexMotion()) {"
)])
motion=(Path(__file__).parent/"port_emit_motion.inc").read_text()
assert "static void EmitVertexMotion" in motion and "static void EmitFragmentMotion" in motion
edit(base+"emit_spirv_special.cpp",[(
    "void EmitEpilogue(EmitContext& ctx) {",
    motion+"""void EmitEpilogue(EmitContext& ctx) {
    if(Sirit::ValidId(ctx.motion_out_cur)) EmitVertexMotion(ctx);
    if(Sirit::ValidId(ctx.motion_frag_out)) EmitFragmentMotion(ctx);
"""
)])
print("PASS: Port SPIR-V object vertex history + fragment motion vectors compiled into core025 source")
