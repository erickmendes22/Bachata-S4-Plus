#!/usr/bin/env python3
"""Port the dedicated The Order 1886 bounded GPU ReadConst path, end-to-end.
Donor: erickmendes22/gow3_android_daedalus_fork@524e74a3
/order1886_arm64_srt.inc:LowerDynamicReadConstPass, resource.h, vk_rasterizer.cpp.
Do not emulate GPU-divergent lanes or invent null-texture shader hashes.
"""
from pathlib import Path

def sub(src, a, b, name):
    n = src.count(a)
    if n != 1:
        raise RuntimeError(f"ORDER_GPU_READCONST source drift {name}: {n}")
    return src.replace(a,b,1)

DYNAMIC = r"""
// ORDER1886_GPU_DYNAMIC_READCONST: retain GPU-varying ReadLane/Phi index by
// turning unresolved scalar SRT loads into bounded storage-buffer accesses.
namespace Shader::Optimization {
namespace {
constexpr u32 OrderMaxReadConstBytes = 4 * 1024 * 1024;
static u64 BoundedReadConstIndex(const IR::Value& value, u32 depth = 0) {
    constexpr u64 unknown = OrderMaxReadConstBytes/4 - 1;
    if (value.IsImmediate()) return std::min<u64>(value.U32(), unknown);
    const auto* inst = value.TryInst();
    if (!inst || depth > 24) return unknown;
    const auto bound = [&](size_t i) { return BoundedReadConstIndex(inst->Arg(i), depth + 1); };
    switch (inst->GetOpcode()) {
    case IR::Opcode::IAdd32: return std::min(unknown, bound(0) + bound(1));
    case IR::Opcode::IMul32: return std::min(unknown, bound(0) * bound(1));
    case IR::Opcode::BitwiseAnd32: return std::min(bound(0), bound(1));
    case IR::Opcode::UMin32: return std::min(bound(0), bound(1));
    case IR::Opcode::UMax32: return std::max(bound(0), bound(1));
    case IR::Opcode::ShiftLeftLogical32:
        if (inst->Arg(1).IsImmediate() && inst->Arg(1).U32() < 20)
            return std::min(unknown, bound(0) << inst->Arg(1).U32());
        return unknown;
    case IR::Opcode::ShiftRightLogical32:
        if (inst->Arg(1).IsImmediate() && inst->Arg(1).U32() < 32)
            return bound(0) >> inst->Arg(1).U32();
        return unknown;
    default: return unknown;
    }
}
static bool ReadConstUniformBase(const IR::Value& address,
                                 SharpFetch<AmdGpu::Buffer>& fetch) {
    const auto* pair = address.TryInst();
    if (!pair || pair->GetOpcode() != IR::Opcode::CompositeConstructU32x2) return false;
    for (u32 i=0; i<2; ++i) {
        const auto v = pair->Arg(i);
        if (v.IsImmediate()) {
            fetch.immediates[i] = v.U32();
            continue;
        }
        const auto* source = v.TryInst();
        if (!source) return false;
        if (source->GetOpcode() == IR::Opcode::GetUserData)
            fetch.offsets[i] = static_cast<SharpLocation>(source->Arg(0).ScalarReg());
        else if (source->GetOpcode() == IR::Opcode::ReadConst ||
                 source->GetOpcode() == IR::Opcode::ReadConstBuffer) {
            const u16 off=GetFlatbufOffset(source);
            if (!off) return false;
            fetch.offsets[i]=off;
        } else return false; // no invented per-lane base address
        fetch.load_mask |= 1u << i;
    }
    return true;
}
} // namespace

void LowerDynamicReadConstPass(IR::Program& program) {
    auto& info = program.info;
    const u32 initial_buffers = info.buffers.size();
    u32 lowered=0, remaining=0;
    // ResourcePatchingPass has already consumed every image/sampler/vertex descriptor.
    for (auto* block : program.post_order_blocks) {
        for (IR::Inst& inst : *block) {
            if (inst.GetOpcode() != IR::Opcode::ReadConst ||
                GetFlatbufOffset(&inst) != 0) continue;
            SharpFetch<AmdGpu::Buffer> fetch{};
            if (!ReadConstUniformBase(inst.Arg(0), fetch)) {
                ++remaining; // maintain real varying pointer; never return arbitrary zero
                continue;
            }
            const u32 bytes = static_cast<u32>(std::min<u64>(
                OrderMaxReadConstBytes, (BoundedReadConstIndex(inst.Arg(1)) + 1) * 4));
            u32 binding=0;
            for (; binding < info.buffers.size(); ++binding) {
                auto& resource = info.buffers[binding];
                if (resource.buffer_type == BufferType::ReadConst &&
                    resource.sharp_fetch == fetch) {
                    resource.readconst_size_bytes =
                        std::max(resource.readconst_size_bytes, bytes);
                    break;
                }
            }
            if (binding == info.buffers.size()) {
                if (binding >= NUM_BUFFERS) { ++remaining; continue; }
                info.buffers.push_back({
                    .sharp_fetch=fetch,
                    .used_types=IR::Type::U32,
                    .buffer_type=BufferType::ReadConst,
                    .readconst_size_bytes=bytes,
                });
            }
            IR::IREmitter ir{*block, IR::Block::InstructionList::s_iterator_to(inst)};
            const auto load=ir.ReadConstBuffer(ir.Imm32(binding), IR::U32{inst.Arg(1)}, {});
            inst.ReplaceUsesWith(load);
            ++lowered;
        }
    }
    if (lowered || remaining)
        LOG_INFO(Render_Recompiler,
            "ORDER1886_GPU_DYNAMIC_READCONST shader={:#x} lowered={} new_gpu_buffers={} unresolved={}",
            info.pgm_hash, lowered, info.buffers.size()-initial_buffers, remaining);
}
} // namespace Shader::Optimization
"""

def apply(root: Path) -> dict:
    files = {
        key: root / path for key,path in {
          'srt': 'src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp',
          'resource': 'src/shader_recompiler/resource.h',
          'passes': 'src/shader_recompiler/ir/passes/ir_passes.h',
          'recompiler': 'src/shader_recompiler/recompiler.cpp',
          'raster': 'src/video_core/renderer_vulkan/vk_rasterizer.cpp',
          'spv': 'src/shader_recompiler/backend/spirv/spirv_emit_context.cpp',
        }.items()
    }
    code = {k:p.read_text() for k,p in files.items()}
    if "ORDER1886_SRT_DEPENDENCY_WORKLIST" not in code['srt']:
        raise RuntimeError("Order dynamic GPU reads need the dependency-safe ARM64 SRT walker")
    code['srt'] += DYNAMIC

    s=code['resource']
    s=sub(s,'#pragma once\n', '#pragma once\n#include <bit>\n#include <array>\n', 'bit includes')
    s=sub(s,'    ClipPlanes,\n};\n\nstruct BufferResource {',
          '    ClipPlanes,\n    ReadConst,\n};\n\nstruct BufferResource {', 'new typed ReadConst descriptor')
    s=sub(s,'    u32 post_op_dw1_mask{};\n\n    bool IsSpecial() const noexcept {',
          '    u32 post_op_dw1_mask{};\n    u32 readconst_size_bytes{};\n\n    bool IsSpecial() const noexcept {',
          'bounded size')
    s=sub(s,'return buffer_type != BufferType::Guest;',
          'return buffer_type != BufferType::Guest && buffer_type != BufferType::ReadConst;',
          'actual GPU resource binding')
    s=sub(s,'        AmdGpu::Buffer buffer;\n        if (!sharp_fetch.Fetch(info.flattened_ud_buf.data(), &buffer)) {',
          '''        AmdGpu::Buffer buffer{};
        if (buffer_type == BufferType::ReadConst) {
            // The low/high DWORDs form an address, not a native V# descriptor.
            // Only uniform BASE; the DWORD INDEX stays on the GPU.
            const auto& flat = info.flattened_ud_buf;
            for (u32 i=0;i<2;++i) {
                if ((sharp_fetch.load_mask & (1u<<i)) &&
                    sharp_fetch.offsets[i]>=flat.size()) return AmdGpu::Buffer::Null();
            }
            if (!sharp_fetch.Fetch(flat.data(), &buffer)) return AmdGpu::Buffer::Null();
            const auto words=std::bit_cast<std::array<u32,4>>(buffer);
            const u64 address=u64(words[0]) | (u64(words[1])<<32);
            // PS4 guest VMA addresses are 40-bit. Reject unassigned SRT pointers.
            if (!address || address >= (1ULL<<40)) return AmdGpu::Buffer::Null();
            buffer={};
            buffer.base_address=address;
            buffer.num_records=readconst_size_bytes;
            return buffer;
        }
        if (!sharp_fetch.Fetch(info.flattened_ud_buf.data(), &buffer)) {''',
          'uniform pointer fetch without allocating dummy texture')
    code['resource']=s

    code['passes']=sub(code['passes'],
       'void ResourcePatchingPass(Shader::Info& info, const ResourceDiscoveryList& sharp_usages,',
       'void LowerDynamicReadConstPass(IR::Program& program);\n'
       'void ResourcePatchingPass(Shader::Info& info, const ResourceDiscoveryList& sharp_usages,',
       'actual IR pass declaration')
    code['recompiler']=sub(code['recompiler'],
       '    Shader::Optimization::ResourcePatchingPass(program.info, resources, profile);\n',
       '    Shader::Optimization::ResourcePatchingPass(program.info, resources, profile);\n'
       '    Shader::Optimization::LowerDynamicReadConstPass(program);\n',
       'run after descriptor lowering')
    s=code['raster']
    s=sub(s,'            if (vsharp.base_address == 0 || vsharp.GetSize() == 0) {',
        '''            const bool readconst = desc.buffer_type == Shader::BufferType::ReadConst;
            const u64 mapped = vsharp.base_address
                ? (readconst ? memory->ClampGpuRangeSize(vsharp.base_address, vsharp.GetSize())
                             : memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize())) : 0;
            if (vsharp.base_address == 0 || vsharp.GetSize() == 0 ||
                (readconst && ((vsharp.base_address & 3) != 0 || mapped < 4))) {''',
        'validate ReadConst mapping before Vulkan binds')
    s=sub(s,
       '                const u64 size = memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize());',
       '                const u64 size = readconst ? (mapped & ~u64{3}) :\n'
       '                    memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize());',
       'bind GPU-written bytes at valid DWORD extent')
    code['raster']=s
    # The donor explicitly carries push-constant byte offsets into ReadConst
    # storage loads. Without this, the shader indexes the aligned Vulkan
    # region origin rather than the actual 4-byte-aligned guest pointer.
    code['spv']=sub(code['spv'],
        'if (buffer.buffer_type != BufferType::Guest) {',
        'if (buffer.buffer_type != BufferType::Guest &&\n'
        '            buffer.buffer_type != BufferType::ReadConst) {',
        'Order ReadConst Vulkan shader dynamic buffer byte offset')
    for k,p in files.items(): p.write_text(code[k])
    return {
        'ported': 'Order ARM64 bounded GPU ReadConst: IR, descriptors, Vulkan bindings',
        'donor': 'gow3_android_daedalus_fork@524e74a',
        'notClaimed': 'GPU-varying *base* addresses or unproven image-table contents',
    }
