#!/usr/bin/env python3
"""SotC gameplay baseline: donor color, fragment descriptor arrays, native frame events.
Source preflight run 45615431758 passed the complete 0.18.1 overlay application.
The current donor also uses the read-only buffer window and debug clamp logging.
Device rendering and performance must still be measured.
"""
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

    # Current standalone SotC enables stage_fragment_tsharp.py. Keep the
    # existing nonuniform feature gate, bounds/null slot and vertex exclusion.
    p=root/'src/shader_recompiler/ir/passes/resource_patching_pass.cpp'
    s=p.read_text()
    s=one(s,'const u32 array_size = info.hw_stage == HwStage::Compute && profile.supports_nonuniform_image_arrays ? DynamicTsharpArraySize() : 0;',
        '''const bool table_stage = info.hw_stage == HwStage::Compute ||
                             info.hw_stage == HwStage::Fragment;
    const u32 array_size = table_stage && profile.supports_nonuniform_image_arrays
                               ? DynamicTsharpArraySize() : 0;''',
        'SotC Android fragment material TSharp tables')
    assert 'MatchSharpTable(resource.sharps[0])' in s
    assert 'NumArrayDescriptors(info) + array_size + 1' in s
    p.write_text(s)

    # Restore the same guest-flip protocol used by the working main core.
    # An imported upstream implementation may already contain the hook.
    # Never report an extra frame, vblank or the idle UI redraw.
    p=root/'src/core/libraries/videoout/driver.cpp'
    s=p.read_text()
    hook='Platform::Bachata::ReportPresentedFrame();'
    if s.count(hook)==0:
        s=one(s,'    presenter->Present(req.frame);',
            '    presenter->Present(req.frame);\n#ifdef ENABLE_BACHATA_RUNTIME\n    '+hook+'\n#endif',
            'SotC guest flip event')
    elif s.count(hook)!=1:
        raise RuntimeError('Duplicate native frame report')
    if '#include "platform/bachata/runtime_client.h"' not in s:
        s=one(s,'#include "imgui/renderer/imgui_core.h"',
            '#include "imgui/renderer/imgui_core.h"\n#ifdef ENABLE_BACHATA_RUNTIME\n#include "platform/bachata/runtime_client.h"\n#endif',
            'SotC runtime event include')
    assert s.index('presenter->Present(req.frame);') < s.index(hook)
    p.write_text(s)

    # Current PC donor aaf95c06deec0: near-4GiB read-only descriptors
    # are unbounded, not necessarily corrupt; don't repeatedly log them
    # at ERROR/WARNING or allocate their full VMA remainder.
    p=root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    s=p.read_text()
    s=one(s,'            const u64 bounded = std::min(mapped, limit);',
        '''            u64 bounded = std::min(mapped, limit);
            // Exact SotC donor read-only window policy. Never truncate
            // writes or GPU ReadConst snapshots; preserve explicit mapping
            // and Vulkan device limits.
            if (shadow && !readconst && !desc.is_written &&
                (vsharp.GetSize() >= 0xFFFF0000ULL || bounded > (256ULL << 20))) {
                constexpr u64 donor_window = 64ULL << 20;
                bounded = std::min(bounded, donor_window);
            }''','SotC donor read-only unbounded buffer window')
    s=one(s,'''                    LOG_ERROR(Render, "Clamped size from {} to {} for stage {:#x}",
                              vsharp.GetSize(), size, stage.pgm_hash);''',
        '''                    LOG_DEBUG(Render, "Clamped size from {} to {} for stage {:#x}",
                              vsharp.GetSize(), size, stage.pgm_hash);''',
        'donor routine clamp log severity')
    # The old loop discarded the entire page on the first CPU-only DWORD
    # before checking the remaining GPU-authored DWORDs. Check exact source
    # provenance before deduplication, preserving the original download.
    s=one(s,'''            if(!visited.insert(page).second)continue;
            if(!buffer_cache.IsRegionGpuModified(page,PageSize))continue;''',
        '''            if(visited.contains(page))continue;
            if(!buffer_cache.IsRegionGpuModified(page,PageSize))continue;''',
        'SRT dedup after valid source')
    s=one(s,'''            if(!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)))continue;
            buffer_cache.TrackSrtSourcePage(page);''',
        '''            if(!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)))continue;
            visited.insert(page);
            buffer_cache.TrackSrtSourcePage(page);''',
        'record actual GPU-written source')
    s=one(s,'''        LOG_INFO(Render_Vulkan,
                 "BACHATA_RELEASE026_SRT_GPU_PAGES_REFRESHED pass={} pages={}",
                 pass,visited.size());''',
        '''        LOG_DEBUG(Render_Vulkan,
                 "BACHATA_RELEASE026_SRT_GPU_PAGES_REFRESHED pass={} pages={}",
                 pass,visited.size());''','avoid repeated SRT logging')
    p.write_text(s)
    p=root/'src/core/memory.cpp'
    s=p.read_text()
    s=one(s,'''        LOG_WARNING(Kernel_Vmm,
                    "BACHATA_RELEASE026_GPU_RANGE_CLAMP addr={:#x} request={:#x} valid={:#x}",''',
        '''        LOG_DEBUG(Kernel_Vmm,
                    "BACHATA_RELEASE026_GPU_RANGE_CLAMP addr={:#x} request={:#x} valid={:#x}",''',
        'routine range clamp debug logging')
    p.write_text(s)
    p=root/'src/video_core/amdgpu/liverpool.cpp'
    s=p.read_text()
    s=one(s,'                LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");',
        '''                static bool reported = false;
                if (!reported) {
                    reported = true;
                    LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION (reported once)");
                }''','current donor warning-once behavior')
    p.write_text(s)

    # Preserve all unrelated binary/meta versions from 608a1ac, including
    # the working non-fragment pipelines in 66F3F9ED. Only affected shaders
    # receives a new per-shader generation; no global cache invalidation.
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp'
    s=p.read_text()
    key='Serialization::ShaderBinaryVersion + (AmdGpu::BachataOrderNoMsaa() ? 64u : 0u)'
    s=one(s,'meta.Write('+key+');',
        'meta.Write('+key+' + (info.pgm_hash==0x87cf9b8aULL ? 101u : (info.hw_stage==Shader::HwStage::Fragment ? 102u : 0u)));','targeted writer')
    s=one(s,'    if (binary_version != '+key+') {',
        '    if (binary_version != '+key+' && binary_version != '+key+' + 101u && binary_version != '+key+' + 102u) {','accept both version generations')
    s=one(s,'    return info.Deserialize(ar) && effective_info.Deserialize(ar);',
        '''    if (!info.Deserialize(ar) || !effective_info.Deserialize(ar)) return false;
    return binary_version == Serialization::ShaderBinaryVersion +
        (AmdGpu::BachataOrderNoMsaa() ? 64u : 0u) +
        (info.pgm_hash==0x87cf9b8aULL ? 101u : (info.hw_stage==Shader::HwStage::Fragment ? 102u : 0u));''','reject old fragment or affected color shader')
    s=one(s,'            bool result{};\n            if (is_compute) {',
        '            infos.fill(nullptr);\n            modules.fill(nullptr);\n            runtime_infos.fill({});\n            fetch_shader=nullptr;\n            bool result{};\n            if (is_compute) {','reset partially loaded stages')
    p.write_text(s)
    return {"color":"donor 5712cee31461, target reduction", "textures":"current Android fragment TSharp arrays; vertex excluded; feature gated", "fps":"one native guest-flip event; no duplicate", "cache":"invalidate affected fragment modules; preserve other stages", "buffers":"donor read-only unbounded window, mapped/storage bounds, debug log", "srt":"exact source before page dedup; no dropped GPU writes"}
