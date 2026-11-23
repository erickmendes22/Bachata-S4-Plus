#!/usr/bin/env python3
"""Port coherent dynamic PS4 SRT indexing to the Bachata 0.18.1 Android ARM64 core.

Source: reviewed shadPS4 upstream PR #5624 (13-file implementation):
https://github.com/shadps4-emu/shadPS4/pull/5624
Pinned shadPS4 0.18.1 matches the upstream patch's source anchors except for
the cache format version. The x86-only SRT walker MUST NOT be copied to ARM64.
Instead, its architecture-independent bounded metadata snapshot / ReadConstArray
logic is grafted onto the existing Bionic VMM-safe bytecode walker.

No per-title patches, no dummy offset-0 substitutions for Phi/ReadLane.
Fail fast on any source drift BEFORE compiling FEX + shadPS4.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

UPSTREAM_PR = "https://github.com/shadps4-emu/shadPS4/pull/5624"
MARKER = "BACHATA_SRT_RUNTIME_ARRAY_5624"
DIFFS = json.loads(r'''{"src/shader_recompiler/backend/spirv/emit_spirv_context_get_set.cpp":"@@ -70,6 +70,10 @@ Id EmitReadConstBuffer(EmitContext& ctx, u32 handle, Id index) {\n     return result;\n }\n \n+Id EmitReadConstArray(EmitContext& ctx, u32 base, Id offset) {\n+    return ctx.EmitFlatbufferLoad(ctx.OpIAdd(ctx.U32[1], ctx.ConstU32(base), offset));\n+}\n+\n Id EmitGetAttribute(EmitContext& ctx, IR::Attribute attr, u32 comp, u32 index) {\n     if (IR::IsParam(attr)) {\n         const u32 param_index{u32(attr) - u32(IR::Attribute::Param0)};","src/shader_recompiler/backend/spirv/emit_spirv_instructions.h":"@@ -65,6 +65,7 @@ void EmitGetMaskLaneVariable(EmitContext& ctx);\n void EmitSetScc(EmitContext& ctx);\n Id EmitReadConst(EmitContext& ctx, IR::Inst* inst, Id addr, Id offset);\n Id EmitReadConstBuffer(EmitContext& ctx, u32 handle, Id index);\n+Id EmitReadConstArray(EmitContext& ctx, u32 base, Id offset);\n Id EmitLoadBufferU8(EmitContext& ctx, IR::Inst* inst, u32 handle, Id address);\n Id EmitLoadBufferU16(EmitContext& ctx, IR::Inst* inst, u32 handle, Id address);\n Id EmitLoadBufferU32(EmitContext& ctx, IR::Inst* inst, u32 handle, Id address);","src/shader_recompiler/info.h":"@@ -100,6 +100,7 @@ struct Info : InfoPersistent {\n     };\n \n     std::span<const u32> user_data;\n+    std::optional<ShaderParams> params;\n     std::vector<u32> flattened_ud_buf;\n     PersistentSrtInfo srt_info;\n \n@@ -161,8 +162,8 @@ struct Info : InfoPersistent {\n \n     Info() = default;\n     Info(HwStage stage_, SwStage l_stage_, ShaderParams params)\n-        : InfoPersistent(stage_, l_stage_, params.hash), pgm_base{params.Base()},\n-          user_data{params.user_data} {}\n+        : InfoPersistent(stage_, l_stage_, params.hash), user_data{params.user_data},\n+          params{params}, pgm_base{params.Base()} {}\n \n     template <typename T>\n     inline T ReadUdSharp(u32 sharp_idx) const noexcept {","src/shader_recompiler/ir/ir_emitter.cpp":"@@ -473,6 +473,10 @@ U32 IREmitter::ReadConst(const Value& base, const U32& offset) {\n     return Inst<U32>(Opcode::ReadConst, base, offset);\n }\n \n+U32 IREmitter::ReadConstArray(const U32& base, const U32& offset) {\n+    return Inst<U32>(Opcode::ReadConstArray, base, offset);\n+}\n+\n U32 IREmitter::ReadConstBuffer(const Value& handle, const U32& index, BufferInstInfo info) {\n     return Inst<U32>(Opcode::ReadConstBuffer, Flags{info}, handle, index);\n }","src/shader_recompiler/ir/ir_emitter.h":"@@ -125,6 +125,7 @@ class IREmitter {\n     [[nodiscard]] T SharedAtomicDec(const U32& address, bool is_gds);\n \n     [[nodiscard]] U32 ReadConst(const Value& base, const U32& offset);\n+    [[nodiscard]] U32 ReadConstArray(const U32& base, const U32& offset);\n     [[nodiscard]] U32 ReadConstBuffer(const Value& handle, const U32& index, BufferInstInfo info);\n \n     [[nodiscard]] U8 LoadBufferU8(const Value& handle, const Value& address, BufferInstInfo info);","src/shader_recompiler/ir/opcodes.inc":"@@ -15,6 +15,7 @@ OPCODE(DebugPrint,                                          Void,           Stri\n \n // Constant memory operations\n OPCODE(ReadConst,                                           U32,            U32x2,          U32,                                                            )\n+OPCODE(ReadConstArray,                                       U32,            U32,            U32,                                                            )\n OPCODE(ReadConstBuffer,                                     U32,            Opaque,         U32,                                                            )\n \n // Barriers","src/shader_recompiler/ir/passes/ir_passes.h":"@@ -31,7 +31,8 @@ void LowerHardwareIntrinsics(IR::Program& program);\n void LowerPhisToRegsPass(IR::Program& program);\n void DeadCodeEliminationPass(IR::Program& program);\n void ConstantPropagationPass(IR::BlockList& program);\n-void FlattenExtendedUserdataPass(IR::Program& program);\n+void FlattenExtendedUserdataPass(IR::Program& program, const ResourceDiscoveryList& resources,\n+                                 const Profile& profile);\n void ReadLaneEliminationPass(IR::Program& program);\n ResourceDiscoveryList ResourceDiscoverPass(IR::Program& program, const Profile& profile);\n void ResourcePatchingPass(Shader::Info& info, const ResourceDiscoveryList& sharp_usages,","src/shader_recompiler/ir/passes/shader_info_collection_pass.cpp":"@@ -225,6 +225,9 @@ void Visit(Info& info, const IR::Inst& inst, Profile const& profile) {\n     case IR::Opcode::Memtime:\n         info.uses_shader_clock = true;\n         break;\n+    case IR::Opcode::ReadConstArray:\n+        AddFlatbuf(info);\n+        break;\n     case IR::Opcode::ReadConst:\n         AddFlatbuf(info);\n         if (inst.Flags<u32>() == 0) {","src/shader_recompiler/params.h":"@@ -3,11 +3,33 @@\n \n #pragma once\n \n+#include <optional>\n #include <span>\n+#include <vector>\n #include \"common/types.h\"\n \n namespace Shader {\n \n+enum class ShaderInputUsageType : u8 {\n+    ImmShaderResourceTable = 0x0A,\n+};\n+\n+/**\n+ * The shader binary footer stores the input usage slots immediately\n+ * before the chunk usage masks referenced by BinaryInfo::chunk_usage_base_offset_in_dw.\n+ */\n+struct alignas(4) ShaderInputUsageSlot {\n+    u8 usage_type;\n+    u8 api_slot;\n+    u8 start_register;\n+    u8 flags;\n+\n+    [[nodiscard]] constexpr ShaderInputUsageType UsageType() const noexcept {\n+        return static_cast<ShaderInputUsageType>(usage_type);\n+    }\n+};\n+static_assert(sizeof(ShaderInputUsageSlot) == 4);\n+\n /**\n  * Compilation parameters used to identify and locate a guest shader program.\n  */\n@@ -18,6 +40,96 @@ struct ShaderParams {\n     std::span<const u32> code;\n     u64 hash;\n \n+    std::vector<u8> srt_metadata;\n+    u32 srt_user_data_base{};\n+\n+    struct SrtPointer {\n+        u32 size_in_dwords;\n+        std::span<const u8> layout;\n+    };\n+\n+    struct SrtElement {\n+        u32 size_in_bytes;\n+        u32 metadata_bytes;\n+    };\n+\n+    static std::optional<SrtElement> ReadSrtElement(std::span<const u8> layout) {\n+        if (layout.empty()) {\n+            return std::nullopt;\n+        }\n+        const u8 type = layout.front();\n+        if (type == 0x82 || type == 0xca || type == 0xda || type == 0xea || type == 0xfa) {\n+            return layout.size() >= 9 ? std::optional{SrtElement{8, 9}} : std::nullopt;\n+        }\n+        if (type == 0x0c) {\n+            return SrtElement{16, 1};\n+        }\n+        if ((type & 0xf) == 0xf) {\n+            return SrtElement{32, 1};\n+        }\n+        if ((type & 0xf) != 1 && (type & 0xf) != 9) {\n+            return std::nullopt;\n+        }\n+        const u32 size_code = type >> 4;\n+        if (size_code <= 6) {\n+            return SrtElement{1u << size_code, 1};\n+        }\n+        if (size_code == 7) {\n+            return SrtElement{12, 1};\n+        }\n+        if (size_code == 8 && layout.size() >= 3) {\n+            return SrtElement{(u32(layout[1]) | u32(layout[2]) << 8) + 1, 3};\n+        }\n+        return std::nullopt;\n+    }\n+\n+    static std::optional<SrtPointer> FindSrtPointer(std::span<const u8> layout, u32 first_dword) {\n+        const u64 target = u64(first_dword) * sizeof(u32);\n+        u64 byte_offset{};\n+        for (size_t pos = 0; pos < layout.size() && byte_offset <= target;) {\n+            const u8 type = layout[pos];\n+            if (type == 0xca || type == 0xda || type == 0xea || type == 0xfa) {\n+                if (layout.size() - pos < 9) {\n+                    return std::nullopt;\n+                }\n+                const auto read_u32 = [&](size_t offset) {\n+                    return u32(layout[offset]) | (u32(layout[offset + 1]) << 8) |\n+                           (u32(layout[offset + 2]) << 16) | (u32(layout[offset + 3]) << 24);\n+                };\n+                if (byte_offset == target) {\n+                    const u32 offset = read_u32(pos + 1);\n+                    const u32 dwords = read_u32(pos + 5);\n+                    if (dwords == 0 || offset < 9 || offset >= layout.size() - pos) {\n+                        return std::nullopt;\n+                    }\n+                    return SrtPointer{dwords, layout.subspan(pos + offset)};\n+                }\n+            }\n+            const auto element = ReadSrtElement(layout.subspan(pos));\n+            if (!element) {\n+                return std::nullopt;\n+            }\n+            byte_offset += element->size_in_bytes;\n+            pos += element->metadata_bytes;\n+        }\n+        return std::nullopt;\n+    }\n+\n+    std::optional<SrtPointer> FindSrtPointer(u32 user_data_reg,\n+                                             std::span<const u32> pointer_offsets = {}) const {\n+        if (user_data_reg < srt_user_data_base) {\n+            return std::nullopt;\n+        }\n+        auto pointer = FindSrtPointer(srt_metadata, user_data_reg - srt_user_data_base);\n+        for (const u32 offset : pointer_offsets) {\n+            if (!pointer || pointer->size_in_dwords < 2 || offset > pointer->size_in_dwords - 2) {\n+                return std::nullopt;\n+            }\n+            pointer = FindSrtPointer(pointer->layout, offset);\n+        }\n+        return pointer;\n+    }\n+\n     VAddr Base() const noexcept {\n         return reinterpret_cast<VAddr>(code.data());\n     }","src/shader_recompiler/recompiler.cpp":"@@ -196,7 +196,7 @@ IR::Program TranslateProgram(const std::span<const u32>& code, Pools& pools, Inf\n     Shader::Optimization::RingAccessElimination(program, runtime_info);\n     Shader::IR::DumpProgram(program, info, \"pre-res-discover.\");\n     auto resources = Shader::Optimization::ResourceDiscoverPass(program, profile);\n-    Shader::Optimization::FlattenExtendedUserdataPass(program);\n+    Shader::Optimization::FlattenExtendedUserdataPass(program, resources, profile);\n     Shader::IR::DumpProgram(program, info, \"pre-res-patch.\");\n     Shader::Optimization::ResourcePatchingPass(program.info, resources, profile);\n     Shader::Optimization::LowerBufferFormatToRaw(program);","src/video_core/amdgpu/regs_shader.h":"@@ -3,6 +3,8 @@\n \n #pragma once\n \n+#include <cstring>\n+\n #include \"common/assert.h\"\n #include \"common/types.h\"\n #include \"shader_recompiler/params.h\"\n@@ -247,14 +249,49 @@ static constexpr const BinaryInfo& SearchBinaryInfo(const u32* code) {\n     UNREACHABLE_MSG(\"Shader binary info not found.\");\n }\n \n-static constexpr Shader::ShaderParams GetParams(const auto& sh) {\n+static void ReadShaderResourceTable(Shader::ShaderParams& params, const BinaryInfo& bininfo,\n+                                    VAddr info_address, auto&& read_memory) {\n+    if (!bininfo.is_srt) {\n+        return;\n+    }\n+    const VAddr code_address = params.Base();\n+    const size_t slots_size = bininfo.num_input_usage_slots * sizeof(Shader::ShaderInputUsageSlot);\n+    const size_t footer_prefix = bininfo.chunk_usage_base_offset_in_dw * sizeof(u32) + slots_size;\n+    if (info_address < code_address || footer_prefix > info_address - code_address) {\n+        return;\n+    }\n+    const VAddr slots_address = info_address - footer_prefix;\n+    if (bininfo.length > slots_address - code_address) {\n+        return;\n+    }\n+    std::array<Shader::ShaderInputUsageSlot, 256> slots;\n+    read_memory(slots_address, reinterpret_cast<u8*>(slots.data()), slots_size);\n+    for (const auto& slot : std::span{slots}.first(bininfo.num_input_usage_slots)) {\n+        if (slot.UsageType() == Shader::ShaderInputUsageType::ImmShaderResourceTable) {\n+            params.srt_metadata.resize(slots_address - code_address - bininfo.length);\n+            read_memory(code_address + bininfo.length, params.srt_metadata.data(),\n+                        params.srt_metadata.size());\n+            params.srt_user_data_base = slot.start_register;\n+            break;\n+        }\n+    }\n+}\n+\n+static Shader::ShaderParams GetParams(const auto& sh) {\n     const auto* code = sh.template Address<u32*>();\n     const auto& bininfo = SearchBinaryInfo(code);\n-    return {\n+    Shader::ShaderParams params = {\n         .user_data = sh.user_data,\n         .code = std::span{code, bininfo.length / sizeof(u32)},\n         .hash = bininfo.shader_hash,\n     };\n+    ReadShaderResourceTable(params, bininfo, std::bit_cast<VAddr>(&bininfo),\n+                            [](VAddr address, u8* dest, u64 size) {\n+                                if (size != 0) {\n+                                    std::memcpy(dest, std::bit_cast<const void*>(address), size);\n+                                }\n+                            });\n+    return params;\n }\n \n } // namespace AmdGpu"}''')
ARM64_EXTENSION = r'''struct ReadConstArray {
    IR::Inst* user;
    IR::Inst* first_dword;
};

struct SrtReadSource {
    u32 reg;
    std::vector<u32> pointer_offsets;

    bool operator==(const SrtReadSource&) const = default;
};

static std::optional<SrtReadSource> FindSrtReadSource(IR::Value value) {
    std::vector<u32> pointer_offsets;
    while (auto* address = value.TryInst()) {
        if (address->GetOpcode() != IR::Opcode::CompositeConstructU32x2) {
            break;
        }
        auto* lo = address->Arg(0).TryInst();
        auto* hi = address->Arg(1).TryInst();
        if (!lo || !hi) {
            break;
        }
        if (lo->GetOpcode() == IR::Opcode::GetUserData &&
            hi->GetOpcode() == IR::Opcode::GetUserData) {
            const u32 reg = u32(lo->Arg(0).ScalarReg());
            if (reg + 1 >= NUM_USER_DATA_REGS || u32(hi->Arg(0).ScalarReg()) != reg + 1) {
                break;
            }
            std::ranges::reverse(pointer_offsets);
            return SrtReadSource{reg, std::move(pointer_offsets)};
        }
        if (lo->GetOpcode() != IR::Opcode::ReadConst || hi->GetOpcode() != IR::Opcode::ReadConst ||
            lo->Arg(0) != hi->Arg(0) || !lo->Arg(1).IsImmediate() || !hi->Arg(1).IsImmediate() ||
            u64(lo->Arg(1).U32()) + 1 != hi->Arg(1).U32()) {
            break;
        }
        pointer_offsets.push_back(lo->Arg(1).U32());
        value = lo->Arg(0);
    }
    return std::nullopt;
}

static std::vector<ReadConstArray> PrepareSrtReadArrays(IR::Program& program,
                                                        const ResourceDiscoveryList& resources,
                                                        const Profile& profile) {
    std::vector<ReadConstArray> arrays;
    // The pinned shadPS4 0.18.1 Profile has no support_bda member.
    // Direct readconst specialization in this source is controlled solely
    // by IsDirectMemoryAccessEnabled() (see EmitReadConst / CollectShaderInfo).
    static_cast<void>(profile);
    if (!program.info.params || EmulatorSettings.IsDirectMemoryAccessEnabled()) {
        return arrays;
    }
    std::vector<IR::Inst*> reads;
    for (auto* block : program.blocks) {
        for (auto& inst : *block) {
            if (inst.GetOpcode() == IR::Opcode::ReadConst) {
                reads.push_back(&inst);
            }
        }
    }
    const u32 max_dwords = std::numeric_limits<SharpLocation>::max();
    size_t reserved_dwords = NUM_USER_DATA_REGS + reads.size();
    struct Snapshot {
        SrtReadSource source;
        IR::Inst* first_dword;
    };
    std::vector<Snapshot> snapshots;
    std::unordered_set<const IR::Inst*> descriptor_sources;
    for (const auto& resource : resources) {
        for (const auto& sharp : resource.sharps) {
            for (u32 i = 0; i < sharp.num_dwords; ++i) {
                if (const auto* inst = sharp.dwords[i].TryInst()) {
                    descriptor_sources.insert(inst);
                }
            }
        }
        if (resource.user->GetOpcode() == IR::Opcode::ImageSampleRaw) {
            if (const auto* inst = resource.sharps[1].post_op_data.lod_prod.TryInst()) {
                descriptor_sources.insert(inst);
            }
        }
    }

    for (auto* read : reads) {
        if (read->Arg(1).IsImmediate() || descriptor_sources.contains(read)) {
            continue;
        }
        const auto source = FindSrtReadSource(read->Arg(0));
        if (!source) {
            continue;
        }
        const auto pointer =
            program.info.params->FindSrtPointer(source->reg, source->pointer_offsets);
        if (!pointer) {
            continue;
        }
        auto snapshot = std::ranges::find(snapshots, *source, &Snapshot::source);
        if (snapshot == snapshots.end()) {
            if (reserved_dwords >= max_dwords ||
                pointer->size_in_dwords > max_dwords - reserved_dwords) {
                continue;
            }
            reserved_dwords += pointer->size_in_dwords;
            IR::IREmitter ir{*read->GetParent(), IR::Block::InstructionList::s_iterator_to(*read)};
            IR::Inst* first_dword{};
            for (u32 dw = 0; dw < pointer->size_in_dwords; ++dw) {
                auto value = ir.ReadConst(read->Arg(0), ir.Imm32(dw));
                if (dw == 0) {
                    first_dword = value.Inst();
                }
            }
            snapshots.push_back({*source, first_dword});
            snapshot = std::prev(snapshots.end());
        }
        arrays.push_back({read, snapshot->first_dword});
    }
    return arrays;
}
'''

def replace_one(s: str, old: str, new: str, label: str) -> str:
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"SRT runtime indices: {label}: expected one anchor, got {n}")
    return s.replace(old, new, 1)

def hunks(diff: str):
    for hunk in re.split(r"(?m)^@@[^\n]*@@[^\n]*\n", diff)[1:]:
        old, new = [], []
        for line in hunk.splitlines():
            if not line or line[0] not in " +-":
                continue
            if line[0] != "+":
                old.append(line[1:])
            if line[0] != "-":
                new.append(line[1:])
        if not old:
            raise RuntimeError("SRT patch contains unanchored hunk")
        yield "\n".join(old), "\n".join(new)

def apply_diff(s: str, diff: str, path: str) -> str:
    for i, (old, new) in enumerate(hunks(diff)):
        s = replace_one(s, old, new, f"{path} hunk {i}")
    return s

def patch_arm64_walker(c: str) -> str:
    if "BIONIC_PORTABLE_SRT_GUEST_VMM" not in c:
        raise RuntimeError("Not the current Bionic guest-VMM SRT walker")
    c = replace_one(c, "#include <unordered_map>\n",
                    "#include <unordered_map>\n#include <unordered_set>\n",
                    "ARM64 unordered_set")
    c = replace_one(c,
        '#include "shader_recompiler/ir/opcodes.h"\n',
        '#include "shader_recompiler/ir/opcodes.h"\n'
        '#include "shader_recompiler/ir/passes/resource_pass.h"\n',
        "ARM64 resource pass")
    c = replace_one(c,
        '#include "shader_recompiler/ir/value.h"\n',
        '#include "shader_recompiler/ir/value.h"\n'
        '#include "shader_recompiler/profile.h"\n',
        "ARM64 profile header")
    c = replace_one(c,
        "} // Anonymous namespace\n",
        "// " + MARKER + " — architecture-independent SRT snapshot path.\n"
        + ARM64_EXTENSION + "\n} // Anonymous namespace\n",
        "portable SRT helper placement")
    c = replace_one(c,
        "void FlattenExtendedUserdataPass(IR::Program& program) {",
        "void FlattenExtendedUserdataPass(IR::Program& program,\n"
        "                                 const ResourceDiscoveryList& resources,\n"
        "                                 const Profile& profile) {",
        "walker API")
    c = replace_one(c,
        "    PassInfo pass_info;\n",
        "    PassInfo pass_info;\n"
        "    const auto arrays = PrepareSrtReadArrays(program, resources, profile);\n",
        "prepare dynamic array snapshots")
    c = replace_one(c,
        "            if (inst.GetOpcode() == IR::Opcode::ReadConstBuffer) {\n"
        "                // Only flatten ReadConstBuffer if it was marked as a sharp source",
        "            // These runtime-indexed reads are replaced after snapshot collection;\n"
        "            // do not incorrectly evaluate their Phi/ReadLane indices on the CPU.\n"
        "            if (std::ranges::find(arrays, &inst, &ReadConstArray::user) != arrays.end()) {\n"
        "                continue;\n"
        "            }\n\n"
        "            if (inst.GetOpcode() == IR::Opcode::ReadConstBuffer) {\n"
        "                // Only flatten ReadConstBuffer if it was marked as a sharp source",
        "skip dynamic reads during CPU walker")
    c = replace_one(c,
        "    program.info.RefreshFlatBuf();\n",
        "    for (const auto& array : arrays) {\n"
        "        array.user->ReplaceOpcode(IR::Opcode::ReadConstArray);\n"
        "        array.user->SetArg(0, IR::Value{u32(GetFlatbufOffset(array.first_dword))});\n"
        "        array.user->SetFlags(0u);\n"
        "    }\n\n"
        "    program.info.RefreshFlatBuf();\n",
        "preserve runtime index in IR")
    return c

def apply(root: Path) -> dict:
    updated: dict[Path, str] = {}
    for relative, diff in DIFFS.items():
        path = root / relative
        old = path.read_text(encoding="utf-8")
        if "BACHATA_SRT_RUNTIME_ARRAY_5624" in old:
            raise RuntimeError(f"Unexpected previously patched generic file: {relative}")
        updated[path] = apply_diff(old, diff, relative)
    srt_path = root / "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp"
    updated[srt_path] = patch_arm64_walker(srt_path.read_text(encoding="utf-8"))

    # Shader binaries produced by the old flattened layout are incompatible.
    # Existing 0.18.1 source uses 13, but our Bionic overlay also bumps the
    # independent shader metadata format. Enforce a fresh cache generation.
    serializer = root / "src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    txt = serializer.read_text(encoding="utf-8")
    pattern = r"(ShaderBinaryVersion\s*=\s*)(\d+)(u;)"
    m = re.search(pattern, txt)
    if not m or len(re.findall(pattern, txt)) != 1:
        raise RuntimeError("SRT runtime index: missing one ShaderBinaryVersion")
    version = max(int(m.group(2)) + 1, 20)
    updated[serializer] = txt[:m.start()] + m.group(1) + str(version) + m.group(3) + txt[m.end():]

    regs_path = root / "src/video_core/amdgpu/regs_shader.h"
    regs = updated[regs_path]
    # num_input_usage_slots is u8 in the pinned BinaryInfo; its maximum is
    # 255 and cannot overflow the 256-element input usage buffer. Do not emit
    # a tautological comparison warning against 256 into the NDK build.
    regs = replace_one(regs,
        "            params.srt_metadata.resize(slots_address - code_address - bininfo.length);\n",
        "            // Corrupted SRT metadata must never request unbounded host memory.\n"
        "            if (slots_address - code_address - bininfo.length > 64 * 1024) return;\n"
        "            params.srt_metadata.resize(slots_address - code_address - bininfo.length);\n",
        "bound SRT metadata snapshot bytes")
    updated[regs_path] = regs

    all_text = "\n".join(updated.values())
    for marker in ("ReadConstArray", "PrepareSrtReadArrays", "FindSrtPointer",
                   "ShaderInputUsageSlot", "Snapshot", "shader_resource_table"):
        if marker == "shader_resource_table":
            continue
        if marker not in all_text:
            raise RuntimeError(f"SRT parity missing key representation {marker}")
    if MARKER not in updated[srt_path]:
        raise RuntimeError("ARM64 indexed SRT path missing")
    # Do not write even one source file until ALL 12 transformations validate.
    for path, data in updated.items():
        path.write_text(data, encoding="utf-8")
    return {"status": "applied", "sourcePR": UPSTREAM_PR,
            "changedFiles": len(updated), "shaderBinaryVersion": version,
            "architecture": "native ARM64 SRT walker + dynamic GPU IR indices",
            "fallback": "CPU dynamic offset not replaced by zero"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.source), sort_keys=True))
