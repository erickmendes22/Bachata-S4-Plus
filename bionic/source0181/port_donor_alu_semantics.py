#!/usr/bin/env python3
"""Restore the donor's complete floating-point and atomic shader contracts.

Reference: The Order Android effective shader tree at 756a4f0/c53cd01.
This adapts instruction semantics to the existing 0.18.1 renderer. It does not
replace CPU/FEX code, cube lowering, 1D-image atomic coordinates or cache IO.
"""
from pathlib import Path
import re


LEGACY_FUNCTIONS = r'''// Legacy multiply-add and clamped operations adapted from theorder1886-port
// d5ee454 (GPL-2.0-or-later). A zero operand yields +0, even with Inf/NaN.
IR::F32 Translator::FPMulLegacy(const IR::F32& a, const IR::F32& b) {
    const IR::F32 zero{ir.Imm32(0.0f)};
    const IR::U1 either_zero{ir.LogicalOr(ir.FPEqual(a, zero), ir.FPEqual(b, zero))};
    return IR::F32{ir.Select(either_zero, zero, ir.FPMul(a, b))};
}

void Translator::V_MUL_LEGACY_F32(const GcnInst& inst) {
    SetDst(inst.dst[0], FPMulLegacy(GetSrc<IR::F32>(inst.src[0]), GetSrc<IR::F32>(inst.src[1])));
}

void Translator::V_MAC_LEGACY_F32(const GcnInst& inst) {
    const IR::F32 product{FPMulLegacy(GetSrc<IR::F32>(inst.src[0]), GetSrc<IR::F32>(inst.src[1]))};
    SetDst(inst.dst[0], ir.FPAdd(product, GetSrc<IR::F32>(inst.dst[0])));
}

void Translator::V_MAD_LEGACY_F32(const GcnInst& inst) {
    const IR::F32 product{FPMulLegacy(GetSrc<IR::F32>(inst.src[0]), GetSrc<IR::F32>(inst.src[1]))};
    SetDst(inst.dst[0], ir.FPAdd(product, GetSrc<IR::F32>(inst.src[2])));
}

IR::F32 Translator::ClampInfToMax(const IR::F32& value) {
    constexpr float max = std::numeric_limits<float>::max();
    const IR::F32 signed_max{
        ir.Select(ir.FPLessThan(value, ir.Imm32(0.0f)), ir.Imm32(-max), ir.Imm32(max))};
    return IR::F32{ir.Select(ir.FPIsInf(value), signed_max, value)};
}'''


ATOMIC_HELPER = r'''// OpSelect evaluates both atomics. Exclusive branches perform exactly one
// mutation and return that operation's previous value (donor/upstream a5ecab35b).
template <typename NegFn, typename NonNegFn>
Id AtomicF32MinMaxFallback(EmitContext& ctx, Id value, NegFn&& emit_neg, NonNegFn&& emit_non_neg) {
    const Id u32_value = ctx.OpBitcast(ctx.U32[1], value);
    const Id sign_bit_set = ctx.OpINotEqual(
        ctx.U1[1],
        ctx.OpBitFieldUExtract(ctx.U32[1], u32_value, ctx.ConstU32(31u), ctx.ConstU32(1u)),
        ctx.u32_zero_value);
    const Id neg_label = ctx.OpLabel();
    const Id non_neg_label = ctx.OpLabel();
    const Id merge_label = ctx.OpLabel();
    ctx.OpSelectionMerge(merge_label, spv::SelectionControlMask::MaskNone);
    ctx.OpBranchConditional(sign_bit_set, neg_label, non_neg_label);
    ctx.AddLabel(neg_label);
    const Id neg_result = EmitBitCastF32U32(ctx, emit_neg(u32_value));
    ctx.OpBranch(merge_label);
    ctx.AddLabel(non_neg_label);
    const Id non_neg_result = EmitBitCastF32U32(ctx, emit_non_neg(u32_value));
    ctx.OpBranch(merge_label);
    ctx.AddLabel(merge_label);
    return ctx.OpPhi(ctx.F32[1], neg_result, neg_label, non_neg_result, non_neg_label);
}
'''


TRINARY_FUNCTIONS = {
    "EmitFPMinTri32": r'''Id EmitFPMinTri32(EmitContext& ctx, Id a, Id b, Id c) {
    // GCN DX10 rules ignore a NaN operand; plain FMin leaves it undefined.
    return ctx.OpNMin(ctx.F32[1], a, ctx.OpNMin(ctx.F32[1], b, c));
}''',
    "EmitFPMaxTri32": r'''Id EmitFPMaxTri32(EmitContext& ctx, Id a, Id b, Id c) {
    return ctx.OpNMax(ctx.F32[1], a, ctx.OpNMax(ctx.F32[1], b, c));
}''',
    "EmitFPMedTri32": r'''Id EmitFPMedTri32(EmitContext& ctx, Id a, Id b, Id c) {
    const Id is_nan{ctx.OpLogicalOr(
        ctx.U1[1], ctx.OpIsNan(ctx.U1[1], a),
        ctx.OpLogicalOr(ctx.U1[1], ctx.OpIsNan(ctx.U1[1], b), ctx.OpIsNan(ctx.U1[1], c)))};
    const Id mmx{ctx.OpFMin(ctx.F32[1], ctx.OpFMax(ctx.F32[1], a, b), c)};
    const Id med3{ctx.OpFMax(ctx.F32[1], ctx.OpFMin(ctx.F32[1], a, b), mmx)};
    return ctx.OpSelect(ctx.F32[1], is_nan, EmitFPMinTri32(ctx, a, b, c), med3);
}''',
}


def function_span(source: str, signature: str):
    """Locate a complete top-level definition, preserving unrelated functions."""
    if source.count(signature) != 1:
        raise RuntimeError(f"ALU definition drift: {signature} ({source.count(signature)})")
    begin = source.index(signature)
    end = source.index("\n}", begin) + 2
    return begin, end


def apply(root: Path):
    sh = root / "src/shader_recompiler"

    def replace(source, old, new, count=1):
        if source.count(old) != count:
            raise RuntimeError(f"ALU contract anchor drift {old[:100]!r}: {source.count(old)}")
        return source.replace(old, new)

    alu = sh / "frontend/translate/vector_alu.cpp"
    source = alu.read_text()
    source = replace(source, '#include "shader_recompiler/frontend/opcodes.h"',
                     '#include <limits>\n#include "shader_recompiler/frontend/opcodes.h"')
    for opcode, callee in (("V_MAC_LEGACY_F32", "V_MAC_F32"),
                           ("V_MAD_LEGACY_F32", "V_MAD_F32")):
        source = replace(source, f"case Opcode::{opcode}:\n        return {callee}(inst);",
                         f"case Opcode::{opcode}:\n        return {opcode}(inst);")
    for opcode, previous, intrinsic in (("V_LOG_CLAMP_F32", "V_LOG_F32", "FPLog2"),
                                         ("V_RCP_CLAMP_F32", "V_RCP_F32", "FPRecip"),
                                         ("V_RSQ_CLAMP_F32", "V_RSQ_F32", "FPRecipSqrt")):
        source = replace(source, f"case Opcode::{opcode}:\n        return {previous}(inst);",
                         f"case Opcode::{opcode}:\n        return SetDst(inst.dst[0], "
                         f"ClampInfToMax(ir.{intrinsic}(GetSrc<IR::F32>(inst.src[0]))));")
    source = replace(source,
                     "case Opcode::V_RSQ_LEGACY_F32:\n        return V_RSQ_F32(inst);",
                     """case Opcode::V_RSQ_LEGACY_F32: {
        const IR::F32 src0{GetSrc<IR::F32>(inst.src[0])};
        const IR::F32 zero{ir.Imm32(0.0f)};
        return SetDst(inst.dst[0], IR::F32{ir.Select(ir.FPEqual(src0, zero), zero,
                                                     ClampInfToMax(ir.FPRecipSqrt(src0)))});
    }""")
    a, b = function_span(source, "void Translator::V_MUL_LEGACY_F32(")
    source = source[:a] + LEGACY_FUNCTIONS + source[b:]

    # Explicitly distinguish ordered comparisons from their negated/unordered
    # GCN counterparts. Retain the existing EXEC masking in both implementations.
    calls = re.compile(r"(case Opcode::(V_CMPX?_(\w+)_F(32|64)):\n        return "
                       r"V_CMP_F\4\(ConditionOp::\w+, )(true|false)(, inst\);)")
    def comparison(match):
        ordered = "false" if match[3].startswith("N") else "true"
        return match[1] + ordered + ", " + match[5] + match[6]
    source, comparisons = calls.subn(comparison, source)
    if comparisons != 40:
        raise RuntimeError(f"ALU comparison dispatch drift: {comparisons}, expected 40")
    for width in (32, 64):
        signature = f"void Translator::V_CMP_F{width}("
        a, b = function_span(source, signature)
        body = source[a:b]
        body = replace(body, "ConditionOp op, bool set_exec,", "ConditionOp op, bool ordered, bool set_exec,")
        for op in ("FPEqual", "FPNotEqual", "FPGreaterThan", "FPLessThan", "FPLessThanEqual", "FPGreaterThanEqual"):
            body = replace(body, f"ir.{op}(src0, src1)", f"ir.{op}(src0, src1, ordered)")
        if width == 32:
            body = replace(body, "case ConditionOp::F:\n            return ir.Imm1(false);",
                           "case ConditionOp::F:\n            return ir.Imm1(false);\n"
                           "        case ConditionOp::TRU:\n            return ir.Imm1(true);")
        source = source[:a] + body + source[b:]
    alu.write_text(source)

    decl = sh / "frontend/translate/translate.h"
    source = decl.read_text()
    source = replace(source, "    void V_MUL_LEGACY_F32(const GcnInst& inst);",
                     """    void V_MUL_LEGACY_F32(const GcnInst& inst);
    IR::F32 FPMulLegacy(const IR::F32& a, const IR::F32& b);
    IR::F32 ClampInfToMax(const IR::F32& value);
    void V_MAC_LEGACY_F32(const GcnInst& inst);
    void V_MAD_LEGACY_F32(const GcnInst& inst);""")
    for width in (32, 64):
        source = replace(source, f"void V_CMP_F{width}(ConditionOp op, bool set_exec,",
                         f"void V_CMP_F{width}(ConditionOp op, bool ordered, bool set_exec,")
    decl.write_text(source)

    atomic = sh / "backend/spirv/emit_spirv_atomic.cpp"
    source = atomic.read_text()
    source = replace(source, "} // Anonymous namespace", ATOMIC_HELPER + "} // Anonymous namespace")
    for kind in ("Buffer", "Image"):
        for op in ("Min", "Max"):
            name = f"Emit{kind}AtomicF{op}32"
            a, b = function_span(source, f"Id {name}(")
            body = source[a:b]
            marker = "\n    const auto u32_value = ctx.OpBitcast"
            if body.count(marker) != 1:
                raise RuntimeError(f"Atomic fallback drift: {name}")
            # Preserve the extension-backed native operation preceding fallback.
            body = body[:body.index(marker)]
            arg = "address" if kind == "Buffer" else "coords"
            neg, non_neg = ("UMax", "SMin") if op == "Min" else ("UMin", "SMax")
            body += f"""
    return AtomicF32MinMaxFallback(
        ctx, value, [&](Id v) {{ return Emit{kind}Atomic{neg}32(ctx, inst, handle, {arg}, v); }},
        [&](Id v) {{ return Emit{kind}Atomic{non_neg}32(ctx, inst, handle, {arg}, v); }});
}}"""
            source = source[:a] + body + source[b:]
    atomic.write_text(source)

    floating = sh / "backend/spirv/emit_spirv_floating_point.cpp"
    source = floating.read_text()
    for name, definition in TRINARY_FUNCTIONS.items():
        a, b = function_span(source, f"Id {name}(")
        source = source[:a] + definition + source[b:]
    floating.write_text(source)

    # Old SPIR-V and driver PSOs embody the previous arithmetic. Reject those
    # through the existing serialization checks; keep cache data for other ABIs.
    directory = root / "src/video_core/renderer_vulkan"
    ser = directory / "vk_pipeline_serialization.cpp"
    source = ser.read_text()
    source, count = re.subn(r"(ShaderBinaryVersion = )(\d+)u;",
                           lambda m: m[1] + str(int(m[2]) + 1) + "u;", source)
    if count != 1:
        raise RuntimeError("ALU shader cache version drift")
    ser.write_text(source)
    live = directory / "order_live_pso_cache.h"
    if live.exists():
        versions = "-".join(re.search(rf"{n} = (\d+)u;", source)[1] for n in
                            ("ShaderMetaVersion", "ShaderBinaryVersion", "PipelineKeyVersion"))
        contents, count = re.subn(r"live-pso-v1-\d+-\d+-\d+", "live-pso-v1-" + versions,
                                  live.read_text())
        if count != 1:
            raise RuntimeError("ALU live PSO cache namespace drift")
        live.write_text(contents)
    return {"legacy": "zero-safe MUL/MAC/MAD and RSQ, finite clamped operations",
            "comparisons": "ordered/unordered F32/F64, preserve EXEC mask",
            "atomics": "one exclusive integer fallback operation and previous-value Phi",
            "trinary": "donor DX10 NaN min3/max3/med3",
            "cache": "reject prior SPIR-V and live PSO ABI", "cpu": "FEX unchanged"}
