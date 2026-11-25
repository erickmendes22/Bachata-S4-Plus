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
    if (profile.subgroup_size==64) {
        // Only the actual donor shader and workgroup are established.
        // Preserve the previously working upstream behavior everywhere else.
        if (num_threads>0 && num_threads<64)
            FoldAbsentReductionLanes(program,num_threads);
        return;
    }
    if (num_threads<=32) return;''','match actual donor reduction shape, not fixed shader hash')
    p.write_text(s)

    p=root/'src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp'
    s=p.read_text()
    s,n=re.subn(r'ShaderBinaryVersion = (\d+)u;',lambda m:f'ShaderBinaryVersion = {int(m.group(1))+101}u;',s)
    if n!=1: raise RuntimeError("shader binary cache version drift")
    p.write_text(s)
    # Warmup must not dereference an uninitialized Vulkan cache handle.
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_cache.cpp'
    s=p.read_text()
    s=one(s,'    WarmUp();\n\n    auto [cache_result, cache]', '    auto [cache_result, cache]', 'initialize before warmup')
    s=one(s,'    pipeline_cache = std::move(cache);\n}', '    pipeline_cache = std::move(cache);\n    WarmUp();\n}', 'warmup after cache exists')
    p.write_text(s)
    # Restore only the actual guest flip event, not the later scheduler policy.
    p=root/'src/core/libraries/videoout/driver.cpp'
    s=p.read_text()
    s=one(s,'#include "imgui/renderer/imgui_core.h"', '#include "imgui/renderer/imgui_core.h"\n#ifdef ENABLE_BACHATA_RUNTIME\n#include "platform/bachata/runtime_client.h"\n#endif','frame protocol include')
    s=one(s,'    presenter->Present(req.frame);','    presenter->Present(req.frame);\n#ifdef ENABLE_BACHATA_RUNTIME\n    Platform::Bachata::ReportPresentedFrame();\n#endif','report actual guest presentation')
    p.write_text(s)
    return {"color":"SotC donor 5712cee31461, actual reduction identities for short compute workgroups on wave64"}
