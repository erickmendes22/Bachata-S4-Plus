#!/usr/bin/env python3
"""Adapt the effective Order ADDR64/ReadConst contract to the 0.18.1 FEX core.

Donor: Order Android 756a4f0cc603 + PC c53cd01d0329, including the active
portable order1886_arm64_srt.inc. Keep Bachata's guest VMM walker, descriptor
arrays and uniformity proofs. The new MUBUF dispatch is title-scoped; the
correct range analysis is shared by both cores' existing GPU ReadConst path.
"""
from pathlib import Path
import re


POLICY = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "common/elf_info.h"

namespace Shader {
inline bool BachataReadConstOrder() {
    return Common::ElfInfo::Instance().GameSerial() == "CUSA00785";
}
} // namespace Shader
'''

CPU_OFFSET = r'''// Use exactly the portable walker's supported operations. ReadLane/Phi
// may execute on the CPU only when the existing uniformity proof permits it.
static bool IsCpuSrtOffset(const IR::Value& value, u32 depth = 0) {
    if (value.IsImmediate()) return true;
    const auto* inst = value.TryInst();
    if (!inst || depth >= 32) return false;
    switch (inst->GetOpcode()) {
    case IR::Opcode::GetUserData:
    case IR::Opcode::ReadConst:
    case IR::Opcode::ReadConstBuffer:
        return true; // ComputeOffset still requires the dependency's flat slot.
    case IR::Opcode::BitCastU32F32:
    case IR::Opcode::BitCastF32U32:
        return IsCpuSrtOffset(inst->Arg(0), depth + 1);
    case IR::Opcode::ReadFirstLane:
    case IR::Opcode::ReadLane: {
        std::unordered_set<IR::Inst*> active{value.TryInst()};
        return IsUniformSrtSource(inst->Arg(0), active);
    }
    case IR::Opcode::Phi: {
        if (inst->NumArgs() == 0) return false;
        const auto first = inst->Arg(0);
        for (size_t i = 1; i < inst->NumArgs(); ++i) {
            if (inst->Arg(i) != first) return false;
        }
        return IsCpuSrtOffset(first, depth + 1);
    }
    default:
        if (!IsAllowedOffsetInstruction(inst)) return false;
        for (size_t i = 0; i < inst->NumArgs(); ++i) {
            if (!IsCpuSrtOffset(inst->Arg(i), depth + 1)) return false;
        }
        return true;
    }
}

'''

FLATTEN_CHECK = r'''// A per-lane vector pointer must remain a GPU read. Only proven uniform
// constant-memory bases and CPU-evaluable offsets enter the SRT walker.
static bool CanFlattenReadConst(const IR::Inst* inst) {
    if (!IsCpuSrtOffset(inst->Arg(1))) return false;
    const auto* base = inst->Arg(0).TryInst();
    if (!base || base->GetOpcode() != IR::Opcode::CompositeConstructU32x2) return false;
    if (IR::IsReadConstAddr64(inst) && !inst->Arg(1).IsImmediate()) return false;
    return IsReadConstSource(base->Arg(0)) && IsReadConstSource(base->Arg(1));
}

'''

BOUNDS = r'''static u64 ReadConstIndexUpperBound(const IR::Value& value, u32 depth = 0) {
    // Unknown is the full U32 domain, not the fallback binding size. Applying
    // >> 2 to an early 4 MiB cap incorrectly shrinks the binding to 1 MiB.
    constexpr u64 unknown = std::numeric_limits<u32>::max();
    if (value.IsImmediate()) return value.U32();
    const auto* inst = value.TryInst();
    if (!inst || depth >= 32) return unknown;
    const auto bound = [&](size_t i) {
        return ReadConstIndexUpperBound(inst->Arg(i), depth + 1);
    };
    switch (inst->GetOpcode()) {
    case IR::Opcode::IAdd32: return std::min(unknown, bound(0) + bound(1));
    case IR::Opcode::IMul32: return std::min(unknown, bound(0) * bound(1));
    case IR::Opcode::BitwiseAnd32: return std::min(bound(0), bound(1));
    case IR::Opcode::UMin32: return std::min(bound(0), bound(1));
    case IR::Opcode::UMax32: return std::max(bound(0), bound(1));
    case IR::Opcode::ShiftLeftLogical32:
        if (inst->Arg(1).IsImmediate() && inst->Arg(1).U32() < 32)
            return std::min(unknown, bound(0) << inst->Arg(1).U32());
        return unknown;
    case IR::Opcode::ShiftRightLogical32:
        if (inst->Arg(1).IsImmediate() && inst->Arg(1).U32() < 32)
            return bound(0) >> inst->Arg(1).U32();
        return unknown;
    default: return unknown;
    }
}

static std::optional<u32> ReadConstByteSpan(const IR::Value& index) {
    const u64 bytes = (ReadConstIndexUpperBound(index) + 1) * sizeof(u32);
    if (bytes > std::numeric_limits<u32>::max()) return std::nullopt;
    return static_cast<u32>(bytes);
}'''


def function_span(source, signature):
    if source.count(signature) != 1:
        raise RuntimeError(f"ReadConst definition drift: {signature}")
    begin = source.index(signature)
    end = source.index("\n}", begin) + 2
    return begin, end


def apply(root):
    root = Path(root)
    shader = root / "src/shader_recompiler"

    def edit(path, old, new):
        text = path.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"ReadConst source drift {path.name}: {old[:100]!r}")
        path.write_text(text.replace(old, new, 1))

    (shader / "readconst_policy.h").write_text(POLICY)
    header = shader / "ir/ir_emitter.h"
    edit(header, "namespace Shader::IR {\n", '''namespace Shader::IR {

// Keep the ADDR64 provenance above the low flat-buffer offset bits.
constexpr u64 ReadConstAddr64Flag = u64{1} << 32;
[[nodiscard]] inline bool IsReadConstAddr64(const Inst* inst) {
    return inst->GetOpcode() == Opcode::ReadConst &&
           (inst->Flags<u64>() & ReadConstAddr64Flag) != 0;
}
''')
    edit(header, "    [[nodiscard]] U32 ReadConst(const Value& base, const U32& offset);",
         "    [[nodiscard]] U32 ReadConst(const Value& base, const U32& offset);\n"
         "    [[nodiscard]] U32 ReadConstAddr64(const Value& base, const U32& offset);")
    emitter = shader / "ir/ir_emitter.cpp"
    edit(emitter, '''U32 IREmitter::ReadConst(const Value& base, const U32& offset) {
    return Inst<U32>(Opcode::ReadConst, base, offset);
}
''', '''U32 IREmitter::ReadConst(const Value& base, const U32& offset) {
    return Inst<U32>(Opcode::ReadConst, base, offset);
}

U32 IREmitter::ReadConstAddr64(const Value& base, const U32& offset) {
    // The ordinary Inst builder forwards only 32 flag bits.
    const U32 value = ReadConst(base, offset);
    value.Inst()->SetFlags(ReadConstAddr64Flag);
    return value;
}
''')

    vector = shader / "frontend/translate/vector_memory.cpp"
    edit(vector, '#include "shader_recompiler/frontend/translate/translate.h"',
         '#include "shader_recompiler/frontend/translate/translate.h"\n'
         '#include "shader_recompiler/readconst_policy.h"')
    text = vector.read_text()
    begin, end = function_span(text, "void Translator::BUFFER_LOAD(")
    body = text[begin:end]
    dst = "    const IR::VectorReg dst_reg{inst.src[1].code};\n"
    if body.count(dst) != 1:
        raise RuntimeError("ReadConst BUFFER_LOAD destination drift")
    body = body.replace(dst, "", 1)
    anchor = "    const IR::U32 soffset{GetSrc(inst.src[3])};\n"
    if body.count(anchor) != 1:
        raise RuntimeError("ReadConst BUFFER_LOAD scalar offset drift")
    body = body.replace(anchor, anchor + dst + '''
    // Order particle records use a 64-bit VGPR pointer with a null V# base.
    // Keep its varying component in the shader; bind only the uniform base.
    if (BachataReadConstOrder() && mubuf.addr64 && !is_inst_typed &&
        !is_buffer_typed && scalar_width == 32) {
        const IR::Value base =
            ir.CompositeConstruct(ir.GetVectorReg(vaddr), ir.GetVectorReg(vaddr + 1));
        const IR::U32 dword_offset{ir.ShiftRightLogical(
            IR::U32{ir.IAdd(ir.Imm32(u32(mubuf.offset)), soffset)}, ir.Imm32(2))};
        for (u32 i = 0; i < num_dwords; ++i) {
            ir.SetVectorReg(dst_reg + i, ir.ReadConstAddr64(
                base, IR::U32{ir.IAdd(dword_offset, ir.Imm32(i))}));
        }
        return;
    }
''', 1)
    vector.write_text(text[:begin] + body + text[end:])

    flatten = shader / "ir/passes/flatten_extended_userdata_pass.cpp"
    edit(flatten, "#include <limits>", "#include <limits>\n#include <optional>")
    edit(flatten, '#include "shader_recompiler/info.h"',
         '#include "shader_recompiler/info.h"\n'
         '#include "shader_recompiler/readconst_policy.h"')
    edit(flatten, '''    if (inst->GetOpcode() == IR::Opcode::ReadConst) {
        inst->SetFlags(offset);
        return;
    }''', '''    if (inst->GetOpcode() == IR::Opcode::ReadConst) {
        // Explicitly preserve ADDR64 provenance when assigning/clearing a slot.
        inst->SetFlags((inst->Flags<u64>() & ~u64{0xffff}) | u64{offset});
        return;
    }''')
    text = flatten.read_text()
    _, end = function_span(text, "static bool IsUniformSrtSource(")
    flatten.write_text(text[:end] + "\n\n" + CPU_OFFSET + text[end:])
    text = flatten.read_text()
    _, end = function_span(text, "static bool IsReadConstSource(")
    flatten.write_text(text[:end] + "\n\n" + FLATTEN_CHECK + text[end:])
    edit(flatten, '''    for (auto* read : reads) {
        if (read->Arg(1).IsImmediate() || descriptor_sources.contains(read)) {''',
         '''    for (auto* read : reads) {
        // ADDR64 data reads are bounded GPU buffers, never CPU SRT snapshots.
        if (IR::IsReadConstAddr64(read) || read->Arg(1).IsImmediate() ||
            descriptor_sources.contains(read)) {''')
    edit(flatten, '''        IR::Inst* base = inst->Arg(0).Inst();
        if (auto* inst = base->Arg(0).TryInst();
            inst && inst->GetOpcode() == IR::Opcode::ReadFirstLane) {
            continue;
        }
        ASSERT_MSG(IsReadConstSource(base->Arg(0)), "ReadConst base low not from constant memory");
        ASSERT_MSG(IsReadConstSource(base->Arg(1)), "ReadConst base high not from constant memory");''',
         '''        if (!CanFlattenReadConst(inst)) continue;
        IR::Inst* base = inst->Arg(0).Inst();''')
    edit(flatten, '''         subtree->Flags<IR::BufferInstInfo>().flatbuf_off_dw == 0)) return;
    Code prefix;''', '''         subtree->Flags<IR::BufferInstInfo>().flatbuf_off_dw == 0)) return;
    if (!IsCpuSrtOffset(off_dw)) return;
    Code prefix;''')
    text = flatten.read_text()
    begin, end = function_span(text, "static u64 BoundedReadConstIndex(")
    flatten.write_text(text[:begin] + BOUNDS + text[end:])
    edit(flatten, '''            if (!ReadConstUniformBase(inst.Arg(0), fetch)) {
                ++remaining; // maintain real varying pointer; never return arbitrary zero
                continue;
            }
            const u32 bytes = static_cast<u32>(std::min<u64>(
                OrderMaxReadConstBytes, (BoundedReadConstIndex(inst.Arg(1)) + 1) * 4));''',
         '''            if (!ReadConstUniformBase(inst.Arg(0), fetch)) {
                if (IR::IsReadConstAddr64(&inst) &&
                    !EmulatorSettings.IsDirectMemoryAccessEnabled()) {
                    // Donor behavior for an unsupported ADDR64 base without DMA:
                    // an explicit null read, never an unrelated flat-buffer word.
                    LOG_ERROR(Render_Recompiler,
                              "Shader {:#x}: ADDR64 base is not uniform constant memory, reading zero",
                              info.pgm_hash);
                    IR::IREmitter ir{*block, IR::Block::InstructionList::s_iterator_to(inst)};
                    inst.ReplaceUsesWith(ir.Imm32(0));
                    continue;
                }
                if (BachataReadConstOrder()) {
                    ASSERT_MSG(EmulatorSettings.IsDirectMemoryAccessEnabled(),
                               "Unsupported dynamic ReadConst: no bounded uniform base");
                }
                ++remaining;
                continue; // A valid DMA path keeps the original GPU pointer.
            }
            const u32 bytes = ReadConstByteSpan(inst.Arg(1)).value_or(OrderMaxReadConstBytes);''')
    edit(flatten, '''                if (binding >= NUM_BUFFERS) { ++remaining; continue; }''',
         '''                if (binding >= NUM_BUFFERS) {
                    ASSERT_MSG(!BachataReadConstOrder(),
                               "Dynamic ReadConst exceeds buffer binding limit");
                    ++remaining;
                    continue;
                }''')

    # The SRT value numbering key previously covered only the low 32 bits.
    # Keep ordinary resource keys unchanged apart from a zero tag field.
    gvn = shader / "ir/srt_gvn_table.h"
    edit(gvn, "        iv.reserve(2 + inst->NumArgs());", "        iv.reserve(3 + inst->NumArgs());")
    edit(gvn, "        for (auto i = 0; i < inst->NumArgs(); i++) {",
         "        for (size_t i = 0; i < inst->NumArgs(); ++i) {")
    edit(gvn, "        iv.push_back(inst->Flags<u32>());", '''        iv.push_back(inst->Flags<u32>());
        iv.push_back(inst->GetOpcode() == IR::Opcode::ReadConst
                         ? static_cast<u32>(inst->Flags<u64>() >> 32) : 0u);''')

    # Walkers, descriptor extents, generated code and driver PSO layouts all
    # change together. Runtime cache naming must run after this overlay.
    renderer = root / "src/video_core/renderer_vulkan"
    serialization = renderer / "vk_pipeline_serialization.cpp"
    text = serialization.read_text()
    for name in ("ShaderMetaVersion", "ShaderBinaryVersion", "PipelineKeyVersion"):
        text, count = re.subn(rf"({name} = )(\d+)u;",
                             lambda m: m[1] + str(int(m[2]) + 1) + "u;", text)
        if count != 1:
            raise RuntimeError("ReadConst cache generation drift: " + name)
    serialization.write_text(text)
    live = renderer / "order_live_pso_cache.h"
    if live.exists():
        versions = "-".join(re.search(rf"{name} = (\d+)u;", text)[1] for name in
                            ("ShaderMetaVersion", "ShaderBinaryVersion", "PipelineKeyVersion"))
        contents, count = re.subn(r"live-pso-v1-\d+-\d+-\d+", "live-pso-v1-" + versions,
                                  live.read_text())
        if count != 1:
            raise RuntimeError("ReadConst live PSO cache generation drift")
        live.write_text(contents)
    return {"cores": "Order and SotC shared ReadConst fixes; new ADDR64 dispatch only CUSA00785",
            "bounds": "U32 range analysis, exact representable bytes, 4 MiB unknown fallback",
            "cpuFlatten": "preserve portable FEX walker and proven uniform offsets only",
            "tag": "high ADDR64 flag retained by slot assignment and SRT value numbering",
            "arrays": "existing ReadConstArray/SharpTable retained; ADDR64 stays on GPU",
            "unsupportedAddr64": "donor explicit zero without DMA; DMA keeps original pointer",
            "cache": "increment metadata, SPIR-V and PSO generations"}
