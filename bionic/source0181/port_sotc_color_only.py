#!/usr/bin/env python3
"""Only the actual SotC donor color correction on the exact gameplay source."""
from pathlib import Path
import re
def one(s,a,b,label):
    if s.count(a)!=1:
        raise RuntimeError(f"render/perf source drift {label}: {s.count(a)}")
    return s.replace(a,b,1)
def apply(root:Path):
    p=root/'src/shader_recompiler/ir/passes/lower_wave64_pass.cpp'
    s=p.read_text()
    reduction="static const IR::Inst* SkipBitCasts(const IR::Value& value) {\n    if (value.IsImmediate()) {\n        return nullptr;\n    }\n    const IR::Inst* inst = value.Inst();\n    while (inst->GetOpcode() == IR::Opcode::BitCastU32F32 ||\n           inst->GetOpcode() == IR::Opcode::BitCastF32U32) {\n        if (inst->Arg(0).IsImmediate()) {\n            return nullptr;\n        }\n        inst = inst->Arg(0).Inst();\n    }\n    return inst;\n}\n\n/// Identity of the reduction step that produced value, when value = op(x, ShuffleXor(x, k)).\n/// Based on the wave64_missing_lane_identity workaround of Pink-shadPS4 (luizgustavs).\nstatic std::optional<u32> ReductionIdentity(const IR::Value& value) {\n    const IR::Inst* op = SkipBitCasts(value);\n    if (!op || op->NumArgs() != 2) {\n        return std::nullopt;\n    }\n    bool is_step = false;\n    for (u32 arg = 0; arg < 2; ++arg) {\n        const IR::Inst* shuffle = SkipBitCasts(op->Arg(arg));\n        const IR::Inst* other = SkipBitCasts(op->Arg(1 - arg));\n        is_step |= shuffle && other && shuffle->GetOpcode() == IR::Opcode::ShuffleXor &&\n                   SkipBitCasts(shuffle->Arg(0)) == other;\n    }\n    if (!is_step) {\n        return std::nullopt;\n    }\n    switch (op->GetOpcode()) {\n    case IR::Opcode::FPMin32:\n        return 0x7f800000u; // +inf\n    case IR::Opcode::FPMax32:\n        return 0xff800000u; // -inf\n    case IR::Opcode::FPMul32:\n        return 0x3f800000u; // 1.0\n    case IR::Opcode::UMin32:\n    case IR::Opcode::BitwiseAnd32:\n        return 0xffffffffu;\n    case IR::Opcode::SMin32:\n        return 0x7fffffffu;\n    case IR::Opcode::SMax32:\n        return 0x80000000u;\n    case IR::Opcode::IMul32:\n        return 1u;\n    case IR::Opcode::FPAdd32:\n    case IR::Opcode::IAdd32:\n    case IR::Opcode::UMax32:\n    case IR::Opcode::BitwiseOr32:\n    case IR::Opcode::BitwiseXor32:\n        return 0u;\n    default:\n        return std::nullopt;\n    }\n}\n\n"
    s=one(s,'void LowerWave64BallotPass(IR::Program& program, const RuntimeInfo& runtime_info,',
        reduction+'''// Donor SotC 5712cee31461: a missing reduction lane must contribute the
// identity, not an arbitrary stale register. Only the proven reduction shape
// is changed; do not invent values for general non-reduction lane reads.
static void FoldAbsentReductionLanes(IR::Program& program,u32 lanes) {
    if (!lanes) return;
    for (IR::Block* block:program.blocks) {
        for (IR::Inst& inst:block->Instructions()) {
            if (inst.GetOpcode()!=IR::Opcode::ReadLane || !inst.Arg(1).IsImmediate() ||
                inst.Arg(1).U32()<lanes) continue;
            const auto identity=ReductionIdentity(inst.Arg(0));
            if (identity) {
                LOG_INFO(Render_Recompiler,"BACHATA_ABSENT_REDUCTION_LANE shader={:#x} lane={} identity={:#x}",
                         program.info.pgm_hash,inst.Arg(1).U32(),*identity);
                inst.ReplaceUsesWithAndRemove(IR::Value{*identity});
            }
        }
    }
}

void LowerWave64BallotPass(IR::Program& program, const RuntimeInfo& runtime_info,''','wave reduction identity helper')
    s=one(s,'''    if (program.info.hw_stage != HwStage::Compute || profile.subgroup_size == 64) {
        return;
    }

    const auto [size_x, size_y, size_z] = runtime_info.hw.cs.workgroup_size;
    const u32 num_threads = size_x * size_y * size_z;
    if (num_threads <= 32) {
        return;
    }''',
        '''    if (program.info.hw_stage != HwStage::Compute) return;
    const auto [size_x,size_y,size_z]=runtime_info.hw.cs.workgroup_size;
    const u32 num_threads=size_x*size_y*size_z;
    if (program.info.pgm_hash==0x87cf9b8aULL && num_threads==32 && profile.subgroup_size>=32)\n        FoldAbsentReductionLanes(program,32);\n    if (profile.subgroup_size==64) {
        // Only the actual donor shader and workgroup are established.
        // Preserve the previously working upstream behavior everywhere else.
        return;
    }
    if (num_threads<=32) return;''','scope absent-lane identity to verified donor shader')
    p.write_text(s)

    # Preserve all unrelated binary/meta versions from 608a1ac, including
    # the 1332 working pipelines in 66F3F9ED. Only the affected shader
    # receives a new per-shader generation; no global cache invalidation.
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp'
    s=p.read_text()
    key='Serialization::ShaderBinaryVersion + (AmdGpu::BachataOrderNoMsaa() ? 64u : 0u)'
    s=one(s,'meta.Write('+key+');',
        'meta.Write('+key+' + (info.pgm_hash==0x87cf9b8aULL ? 101u : 0u));','targeted writer')
    s=one(s,'    if (binary_version != '+key+') {',
        '    if (binary_version != '+key+' && binary_version != '+key+' + 101u) {','accept both version generations')
    s=one(s,'    return info.Deserialize(ar) && effective_info.Deserialize(ar);',
        '''    if (!info.Deserialize(ar) || !effective_info.Deserialize(ar)) return false;
    return binary_version == Serialization::ShaderBinaryVersion +
        (AmdGpu::BachataOrderNoMsaa() ? 64u : 0u) +
        (info.pgm_hash==0x87cf9b8aULL ? 101u : 0u);''','reject only old affected shader')
    s=one(s,'            bool result{};\n            if (is_compute) {',
        '            infos.fill(nullptr);\n            modules.fill(nullptr);\n            runtime_infos.fill({});\n            fetch_shader=nullptr;\n            bool result{};\n            if (is_compute) {','reset partially loaded stages')
    p.write_text(s)
    return {"color":"donor 5712cee31461, target reduction; preserve all unrelated caches"}
