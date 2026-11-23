// SPDX-FileCopyrightText: Copyright 2024-2026 shadPS4 Emulator Project
// SPDX-FileCopyrightText: Copyright 2026 Mark Hall
// SPDX-License-Identifier: GPL-2.0-or-later

#include <algorithm>
#include <atomic>
#include <limits>
#include <cstring>
#include <deque>
#include <memory>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <boost/container/flat_map.hpp>
#include <queue>
#include "core/memory.h"
#include "common/io_file.h"
#include "common/logging/log.h"
#include "common/path_util.h"
#include "core/emulator_settings.h"
#include "shader_recompiler/info.h"
#include "shader_recompiler/ir/ir_emitter.h"
#include "shader_recompiler/ir/opcodes.h"
#include "shader_recompiler/ir/passes/srt.h"
#include "shader_recompiler/ir/program.h"
#include "shader_recompiler/ir/reg.h"
#include "shader_recompiler/ir/srt_gvn_table.h"
#include "shader_recompiler/ir/value.h"

// bbport: upstream JIT-compiles the SRT walker to x86-64 (Xbyak) and patches loads that fault
// into "zero the register" (Zydis, SIGSEGV handler). Here the walker is a portable bytecode run
// by an interpreter, on x86-64 and on the native arm64 GPU host alike. A load that faults is
// marked zeroed permanently after validation against the Android guest VMM.
// Instructions are three words: opcode (bit 31 = zeroed load), a, b. Offsets are in dwords.

namespace {

constexpr u32 SrtMagic = 0x31545253; // "SRT1"
constexpr u32 SrtZeroed = 1u << 31;
constexpr u32 SrtMaxStack = 64;

enum class SrtOp : u32 {
    End,
    Imm,         // push a
    LoadFlat,    // push flat[a] (user data registers and already-flattened values)
    Add,
    Sub,
    Mul,
    Shl,
    Shr,
    And,
    Or,
    Xor,
    Not,
    UMin,
    UMax,
    Bfe,         // pop count, offset, base: (base >> offset) & mask(count)
    PushPtrImm,  // push the current pointer; pointer = *(u64*)(pointer + a * 4) & 48 bits
    PushPtrExpr, // as PushPtrImm with a popped offset
    CopyImm,     // flat[b] = *(u32*)(pointer + a * 4)
    CopyExpr,    // flat[b] = *(u32*)(pointer + popped offset * 4)
    PopPtr,
};

constexpr const char* SrtOpName(SrtOp op) {
    constexpr const char* names[] = {"end", "imm", "load_flat", "add", "sub", "mul", "shl",
                                     "shr", "and", "or", "xor", "not", "umin", "umax", "bfe",
                                     "push_ptr_imm", "push_ptr_expr", "copy_imm", "copy_expr",
                                     "pop_ptr"};
    return static_cast<u32>(op) < std::size(names) ? names[static_cast<u32>(op)] : "?";
}

std::mutex g_walker_mutex;
std::deque<std::unique_ptr<u32[]>> g_walkers;

/// Whether a program is well formed and stays within the interpreter's stacks.
bool CheckProgram(const u32* code, size_t words) {
    if (words < 4 || code[0] != SrtMagic || (words - 1) % 3 != 0) {
        return false;
    }
    int values = 0, ptrs = 0;
    for (size_t i = 1; i < words; i += 3) {
        const auto op = static_cast<SrtOp>(code[i] & ~SrtZeroed);
        switch (op) {
        case SrtOp::End:
            return i + 3 == words && values == 0 && ptrs == 0;
        case SrtOp::Imm:
        case SrtOp::LoadFlat:
            ++values;
            break;
        case SrtOp::Not:
            if (values < 1) {
                return false;
            }
            break;
        case SrtOp::Bfe:
            if (values < 3) {
                return false;
            }
            values -= 2;
            break;
        case SrtOp::PushPtrImm:
            ++ptrs;
            break;
        case SrtOp::PushPtrExpr:
            --values;
            ++ptrs;
            break;
        case SrtOp::CopyImm:
            break;
        case SrtOp::CopyExpr:
            --values;
            break;
        case SrtOp::PopPtr:
            --ptrs;
            break;
        default:
            if (op > SrtOp::PopPtr || values < 2) {
                return false;
            }
            --values; // binary operators
            break;
        }
        if (values < 0 || ptrs < 0 || values > int(SrtMaxStack) || ptrs > int(SrtMaxStack)) {
            return false;
        }
    }
    return false;
}

Shader::SrtWalkerCode StoreWalker(const u32* code, size_t words) {
    ASSERT_MSG(CheckProgram(code, words), "Malformed SRT walker program");
    auto copy = std::make_unique<u32[]>(words);
    std::memcpy(copy.get(), code, words * sizeof(u32));
    std::scoped_lock lock{g_walker_mutex};
    return g_walkers.emplace_back(std::move(copy)).get();
}

// BIONIC_PORTABLE_SRT_GUEST_VMM: do not dereference unmapped PS4 addresses on native ARM64.
template <typename T>
bool TryReadGuest(u64 address, const u32* flat, T& value) {
    value = {};
    if (address == 0 || address > std::numeric_limits<std::uintptr_t>::max() - sizeof(T)) return false;
    const auto begin = static_cast<std::uintptr_t>(address);
    const auto end = begin + sizeof(T);
    const auto local = reinterpret_cast<std::uintptr_t>(flat);
    if (begin >= local && end <= local + 16 * sizeof(u32)) {
        std::memcpy(&value, reinterpret_cast<const void*>(begin), sizeof(T));
        return true;
    }
    if (begin < 0x10000) return false;
    void* map_begin{};
    void* map_end{};
    u32 prot{};
    auto* memory = Core::Memory::Instance();
    if (memory->QueryProtection(begin, &map_begin, &map_end, &prot) != 0 ||
        (prot & static_cast<u32>(Core::MemoryProt::CpuRead)) == 0 ||
        begin < reinterpret_cast<std::uintptr_t>(map_begin) ||
        end > reinterpret_cast<std::uintptr_t>(map_end)) return false;
    std::memcpy(&value, reinterpret_cast<const void*>(begin), sizeof(T));
    return true;
}

void DumpSrtProgram(const Shader::Info& info, const u32* code, size_t words) {
    using namespace Common::FS;

    const auto dump_dir = GetUserPath(PathType::ShaderDir) / "dumps";
    if (!std::filesystem::exists(dump_dir)) {
        std::filesystem::create_directories(dump_dir);
    }
    const auto filename = fmt::format("{}_{:#018x}.srtprogram.txt", info.hw_stage, info.pgm_hash);
    const auto file = IOFile{dump_dir / filename, FileAccessMode::Create, FileType::TextFile};
    for (size_t i = 1; i + 2 < words; i += 3) {
        file.WriteString(fmt::format("{:4}: {} {} {}\n", (i - 1) / 3,
                                     SrtOpName(static_cast<SrtOp>(code[i] & ~SrtZeroed)),
                                     code[i + 1], code[i + 2]));
    }
}

} // namespace

namespace Shader {

SrtWalkerCode RegisterWalkerCode(const u8* ptr, size_t size) {
    if (!ptr || size < 4 * sizeof(u32) || size > 8 * 1024 * 1024 ||
        size % sizeof(u32) != 0) return nullptr;
    std::vector<u32> code(size / sizeof(u32));
    std::memcpy(code.data(), ptr, size);
    if (!CheckProgram(code.data(), code.size())) {
        LOG_WARNING(Render_Recompiler, "BIONIC_PORTABLE_SRT_CACHE_REJECT: old x86 walker");
        return nullptr;
    }
    return StoreWalker(code.data(), code.size());
}

void RunSrtWalker(SrtWalkerCode code, const u32* user_data, u32* flat) {
    // Read initial SGPRs from the copied flat buffer. The source vector may
    // have fewer than 16 entries and must never be over-read.
    static_cast<void>(user_data);
    u32* const ops = const_cast<u32*>(code) + 1;
    u32 values[SrtMaxStack]{};
    u64 ptrs[SrtMaxStack]{};
    u32 nv = 0, np = 0;
    u64 cur = reinterpret_cast<u64>(flat);
    for (u32 i = 0;; i += 3) {
        const u32 word = std::atomic_ref<u32>(ops[i]).load(std::memory_order_relaxed);
        const bool zeroed = word & SrtZeroed;
        const auto op = static_cast<SrtOp>(word & ~SrtZeroed);
        const u32 a = ops[i + 1], b = ops[i + 2];
        u32 rhs;
        switch (op) {
        case SrtOp::End:
            return;
        case SrtOp::Imm:
            values[nv++] = a;
            continue;
        case SrtOp::LoadFlat:
            values[nv++] = flat[a];
            continue;
        case SrtOp::Not:
            values[nv - 1] = ~values[nv - 1];
            continue;
        case SrtOp::Bfe: {
            const u32 count = values[--nv], offset = values[--nv];
            const u32 mask = count >= 32 ? ~0u : (1u << count) - 1;
            values[nv - 1] = (values[nv - 1] >> (offset & 31)) & mask;
            continue;
        }
        case SrtOp::PushPtrImm:
        case SrtOp::PushPtrExpr: {
            const u32 off = op == SrtOp::PushPtrImm ? a : values[--nv];
            ptrs[np++] = cur;
            const bool null = cur < 0x10000ULL;
            if (zeroed || null) {
                cur = 0;
            } else {
                u64 next{};
                const u64 address = cur + u32(off << 2);
                if (!TryReadGuest(address, flat, next)) {
                    /* Revalidate changing guest SRT memory every dispatch; do not permanently poison opcode. */
                    LOG_WARNING(Render_Recompiler,
                                "BIONIC_PORTABLE_SRT_BAD_POINTER: opcode={} address={:#x}",
                                i / 3, address);
                    next = 0;
                }
                cur = next & 0xFFFFFFFFFFFFULL;
            }
            continue;
        }
        case SrtOp::CopyImm:
        case SrtOp::CopyExpr: {
            const u32 off = op == SrtOp::CopyImm ? a : values[--nv];
            const bool null = cur < 0x10000ULL;
            if (zeroed || null) {
                flat[b] = 0;
            } else {
                u32 value{};
                const u64 address = cur + u32(off << 2);
                if (!TryReadGuest(address, flat, value)) {
                    /* Revalidate changing guest SRT memory every dispatch; do not permanently poison opcode. */
                    LOG_WARNING(Render_Recompiler,
                                "BIONIC_PORTABLE_SRT_BAD_READ: opcode={} address={:#x}",
                                i / 3, address);
                    value = 0;
                }
                flat[b] = value;
            }
            continue;
        }
        case SrtOp::PopPtr:
            cur = ptrs[--np];
            continue;
        default:
            break;
        }
        rhs = values[--nv];
        u32& lhs = values[nv - 1];
        switch (op) {
        case SrtOp::Add:
            lhs += rhs;
            break;
        case SrtOp::Sub:
            lhs -= rhs;
            break;
        case SrtOp::Mul:
            lhs *= rhs;
            break;
        case SrtOp::Shl:
            lhs <<= rhs & 31;
            break;
        case SrtOp::Shr:
            lhs >>= rhs & 31;
            break;
        case SrtOp::And:
            lhs &= rhs;
            break;
        case SrtOp::Or:
            lhs |= rhs;
            break;
        case SrtOp::Xor:
            lhs ^= rhs;
            break;
        case SrtOp::UMin:
            lhs = std::min(lhs, rhs);
            break;
        case SrtOp::UMax:
            lhs = std::max(lhs, rhs);
            break;
        default:
            UNREACHABLE_MSG("Bad SRT walker opcode {}", static_cast<u32>(op));
        }
    }
}

} // namespace Shader

namespace {

using namespace Shader;

struct PassInfo {
    struct PointerListCompare {
        bool operator()(const IR::Value& a, const IR::Value& b) const {
            // Keep order with the following criteria:
            // 1. If immediate, sort by immediate value
            // 2. If not immediate, sort by instruction order
            // 3. Immediates come first, then instructions
            if (a.IsImmediate() && b.IsImmediate()) {
                return a.U32() < b.U32();
            } else if (!a.IsImmediate() && !b.IsImmediate()) {
                auto a_inst = a.Inst();
                auto b_inst = b.Inst();
                auto a_block = a_inst->GetParent();
                auto b_block = b_inst->GetParent();
                if (a_block != b_block) {
                    return a_block < b_block; // Sort by block address
                }

                auto it = a_block->Instructions().iterator_to(*a_inst);
                auto end = a_block->Instructions().end();
                for (; it != end; ++it) {
                    if (&*it == b_inst) {
                        return true;
                    }
                }
                return false;
            } else {
                return a.IsImmediate(); // Immediates come first
            }
        }
    };

    // map offset to inst
    using PtrUserList =
        boost::container::flat_map<IR::Value, Shader::IR::Inst*, PointerListCompare>;

    Optimization::SrtGvnTable gvn_table;
    // keys are GetUserData, ReadConst or ReadConstBuffer instructions that are used as pointers
    std::unordered_map<IR::Inst*, PtrUserList> pointer_uses;
    // GetUserData instructions corresponding to sgpr_base of SRT roots
    boost::container::small_flat_map<IR::ScalarReg, IR::Inst*, 1> srt_roots;

    // pick a single inst for a given value number
    std::unordered_map<u32, IR::Inst*> vn_to_inst;

    // Bumped during codegen to assign offsets to readconsts
    u16 dst_off_dw;

    PtrUserList* GetUsesAsPointer(IR::Inst* inst) {
        auto it = pointer_uses.find(inst);
        if (it != pointer_uses.end()) {
            return &it->second;
        }
        return nullptr;
    }

    // Return a single instruction that this instruction is identical to, according
    // to value number
    // The "original" is arbitrary. Here it's the first instruction found for a given value number
    IR::Inst* DeduplicateInstruction(IR::Inst* inst) {
        auto it = vn_to_inst.try_emplace(gvn_table.GetValueNumber(inst), inst);
        return it.first->second;
    }
};
} // namespace

namespace Shader::Optimization {

namespace {

static inline u16 GetFlatbufOffset(const IR::Inst* inst) {
    if (inst->GetOpcode() == IR::Opcode::ReadConstBuffer) {
        auto inst_info = inst->Flags<IR::BufferInstInfo>();
        return inst_info.flatbuf_off_dw;
    }
    if (inst->GetOpcode() == IR::Opcode::ReadConst) {
        return inst->Flags<u16>();
    }
    UNREACHABLE_MSG("Instruction not supported");
}

static inline void SetFlatbufOffset(IR::Inst* inst, u16 offset) {
    if (inst->GetOpcode() == IR::Opcode::ReadConstBuffer) {
        auto inst_info = inst->Flags<IR::BufferInstInfo>();
        inst_info.flatbuf_off_dw.Assign(offset);
        inst->SetFlags(inst_info);
        return;
    }
    if (inst->GetOpcode() == IR::Opcode::ReadConst) {
        inst->SetFlags(offset);
        return;
    }
    UNREACHABLE_MSG("Instruction not supported");
}

using Code = std::vector<u32>;

static void Emit(Code& c, SrtOp op, u32 a = 0, u32 b = 0) {
    c.insert(c.end(), {static_cast<u32>(op), a, b});
}

static bool ComputeOffset(Code& c, PassInfo& pass_info, const IR::Value& off_dw);

#define ABORT_ON_FAILURE(expr)                                                                     \
    if (!(expr)) {                                                                                 \
        return false;                                                                              \
    }

static bool EmitOperand(Code& c, PassInfo& pass_info, const IR::Value& value) {
    if (value.IsImmediate()) {
        Emit(c, SrtOp::Imm, value.U32());
        return true;
    }
    return ComputeOffset(c, pass_info, value);
}

// Operands are pushed in argument order; the operator combines them as arg0 op arg1.
static bool EmitOperator(Code& c, PassInfo& pass_info, IR::Inst* inst, SrtOp op) {
    ASSERT(!inst->AreAllArgsImmediates());
    for (size_t arg = 0; arg < inst->NumArgs(); ++arg) {
        ABORT_ON_FAILURE(EmitOperand(c, pass_info, inst->Arg(arg)));
    }
    Emit(c, op);
    return true;
}

static bool IsAllowedOffsetInstruction(const IR::Inst* inst) {
    switch (inst->GetOpcode()) {
    case IR::Opcode::GetUserData:
    case IR::Opcode::ReadConst:
    case IR::Opcode::ReadConstBuffer:
    case IR::Opcode::IAdd32:
    case IR::Opcode::ISub32:
    case IR::Opcode::IMul32:
    case IR::Opcode::ShiftLeftLogical32:
    case IR::Opcode::ShiftRightLogical32:
    case IR::Opcode::BitwiseAnd32:
    case IR::Opcode::BitwiseOr32:
    case IR::Opcode::BitwiseXor32:
    case IR::Opcode::BitwiseNot32:
    case IR::Opcode::UMin32:
    case IR::Opcode::UMax32:
    case IR::Opcode::BitFieldUExtract:
        return true;
    default:
        return false;
    }
}

// RELEASE026_SRT_UNIFORM_OFFSET_PROOF: A guest ReadLane may be evaluated
// on the CPU only for a wave-uniform value. Never guess a Phi predecessor.
static bool IsUniformSrtSource(const IR::Value& v, std::unordered_set<IR::Inst*>& active,
                               unsigned depth = 0) {
    if (depth > 64) return false;
    if (v.IsImmediate()) return true;
    auto* inst = v.TryInst();
    if (!inst || !active.insert(inst).second) return false;
    bool uniform = false;
    switch (inst->GetOpcode()) {
    case IR::Opcode::GetUserData:
        uniform = true;
        break;
    // BACHATA_SRT_UNIFORM_READCONST_PROOF: a ReadLane over a scalar
    // descriptor load is uniform when *all* pointer and offset operands
    // are proven uniform. Previous ARM64 code classified every ReadConst
    // as divergent, even the guest scalar SRT sources loaded by the CPU.
    // Do not use the first lane as an arbitrary replacement otherwise.
    case IR::Opcode::ReadConst:
    case IR::Opcode::ReadConstBuffer:
    case IR::Opcode::CompositeConstructU32x2: {
        uniform = inst->NumArgs() > 0;
        for (size_t i = 0; uniform && i < inst->NumArgs(); ++i)
            uniform = IsUniformSrtSource(inst->Arg(i), active, depth + 1);
        break;
    }
    case IR::Opcode::Phi: {
        uniform = inst->NumArgs() > 0;
        if (uniform) {
            const auto first = inst->Arg(0);
            for (size_t i = 1; uniform && i < inst->NumArgs(); ++i)
                uniform = inst->Arg(i) == first;
            if (uniform) uniform = IsUniformSrtSource(first, active, depth + 1);
        }
        break;
    }
    case IR::Opcode::BitCastU32F32:
    case IR::Opcode::BitCastF32U32:
    case IR::Opcode::BitwiseNot32:
        uniform = IsUniformSrtSource(inst->Arg(0), active, depth + 1);
        break;
    case IR::Opcode::IAdd32:
    case IR::Opcode::ISub32:
    case IR::Opcode::IMul32:
    case IR::Opcode::ShiftLeftLogical32:
    case IR::Opcode::ShiftRightLogical32:
    case IR::Opcode::BitwiseAnd32:
    case IR::Opcode::BitwiseOr32:
    case IR::Opcode::BitwiseXor32:
    case IR::Opcode::UMin32:
    case IR::Opcode::UMax32:
    case IR::Opcode::BitFieldUExtract:
        uniform = true;
        for (size_t i = 0; uniform && i < inst->NumArgs(); ++i)
            uniform = IsUniformSrtSource(inst->Arg(i), active, depth + 1);
        break;
    default:
        break; // Vector-register and lane-dependent values remain GPU work.
    }
    active.erase(inst);
    return uniform;
}

static bool ComputeOffset(Code& c, PassInfo& pass_info, const IR::Value& off_dw) {
    auto inst = off_dw.Inst();
    switch (inst->GetOpcode()) {
    case IR::Opcode::Phi: {
        if (inst->NumArgs() == 0) return false;
        const auto first = inst->Arg(0);
        for (size_t i = 1; i < inst->NumArgs(); ++i)
            if (inst->Arg(i) != first) return false;
        std::unordered_set<IR::Inst*> active{inst};
        if (!IsUniformSrtSource(first, active)) return false;
        return EmitOperand(c, pass_info, first);
    }
    case IR::Opcode::ReadFirstLane:
    case IR::Opcode::ReadLane: {
        std::unordered_set<IR::Inst*> active{inst};
        if (!IsUniformSrtSource(inst->Arg(0), active)) {
            LOG_WARNING(Render_Recompiler, "RELEASE026_SRT_NONUNIFORM_LANE_REQUIRES_GPU");
            return false; // no arbitrary predecessor or zero offset
        }
        return EmitOperand(c, pass_info, inst->Arg(0));
    }
    case IR::Opcode::BitCastU32F32:
    case IR::Opcode::BitCastF32U32:
        return EmitOperand(c, pass_info, inst->Arg(0));
    case IR::Opcode::GetUserData:
        Emit(c, SrtOp::LoadFlat, static_cast<u32>(inst->Arg(0).ScalarReg()));
        return true;
    case IR::Opcode::ReadConst:
    case IR::Opcode::ReadConstBuffer: {
        // ORDER1886_SRT_GVN_SLOT_PARITY: exact source commit 5fbd19fd.
        // A GVN duplicate may already have been assigned by a different root.
        auto* canonical = pass_info.DeduplicateInstruction(inst);
        u16 offset = GetFlatbufOffset(canonical);
        if (!offset) offset = GetFlatbufOffset(inst);
        if (!offset) return false;
        Emit(c, SrtOp::LoadFlat, offset);
        return true;
    }
    case IR::Opcode::IAdd32:
        return EmitOperator(c, pass_info, inst, SrtOp::Add);
    case IR::Opcode::ISub32:
        return EmitOperator(c, pass_info, inst, SrtOp::Sub);
    case IR::Opcode::IMul32:
        return EmitOperator(c, pass_info, inst, SrtOp::Mul);
    case IR::Opcode::ShiftLeftLogical32:
        return EmitOperator(c, pass_info, inst, SrtOp::Shl);
    case IR::Opcode::ShiftRightLogical32:
        return EmitOperator(c, pass_info, inst, SrtOp::Shr);
    case IR::Opcode::BitwiseAnd32:
        return EmitOperator(c, pass_info, inst, SrtOp::And);
    case IR::Opcode::BitwiseOr32:
        return EmitOperator(c, pass_info, inst, SrtOp::Or);
    case IR::Opcode::BitwiseXor32:
        return EmitOperator(c, pass_info, inst, SrtOp::Xor);
    case IR::Opcode::BitwiseNot32:
        return EmitOperator(c, pass_info, inst, SrtOp::Not);
    case IR::Opcode::UMin32:
        return EmitOperator(c, pass_info, inst, SrtOp::UMin);
    case IR::Opcode::UMax32:
        return EmitOperator(c, pass_info, inst, SrtOp::UMax);
    case IR::Opcode::BitFieldUExtract:
        return EmitOperator(c, pass_info, inst, SrtOp::Bfe);
    default:
        LOG_ERROR(Render_Recompiler, "Unexpected instruction for offset computation, {}",
                  magic_enum::enum_name(inst->GetOpcode()));
        return false;
    }
}

// An offset expression is built aside and appended only when complete.
static bool EmitOffset(Code& c, PassInfo& pass_info, const IR::Value& off_dw) {
    Code expr;
    ABORT_ON_FAILURE(ComputeOffset(expr, pass_info, off_dw));
    c.insert(c.end(), expr.begin(), expr.end());
    return true;
}

// ORDER1886_SRT_DEPENDENCY_WORKLIST: port commit c781ee89 and 14c1c755.
// An offset may depend on a read that is assigned later in the same subtree
// or a different SGPR root. Do not replace genuinely divergent lanes with zero.
static void VisitPointer(const IR::Value& off_dw, IR::Inst* subtree,
                         PassInfo& pass_info, Code& c) {
    if ((subtree->GetOpcode() == IR::Opcode::ReadConst &&
         subtree->Flags<u16>() == 0) ||
        (subtree->GetOpcode() == IR::Opcode::ReadConstBuffer &&
         subtree->Flags<IR::BufferInstInfo>().flatbuf_off_dw == 0)) return;
    Code prefix;
    if (off_dw.IsImmediate()) {
        Emit(prefix, SrtOp::PushPtrImm, off_dw.U32());
    } else if (EmitOffset(prefix, pass_info, off_dw)) {
        Emit(prefix, SrtOp::PushPtrExpr);
    } else {
        return; // Retry when another root has assigned the dependency.
    }
    const auto* uses = pass_info.GetUsesAsPointer(subtree);
    if (!uses) return;
    c.insert(c.end(), prefix.begin(), prefix.end());
    using Pending = std::pair<IR::Value, IR::Inst*>;
    std::vector<Pending> pending;
    pending.reserve(uses->size());
    for (const auto& [offset, use] : *uses) {
        auto* canonical = pass_info.DeduplicateInstruction(use);
        const u16 existing = GetFlatbufOffset(canonical);
        if (existing) {
            if (!GetFlatbufOffset(use)) SetFlatbufOffset(use, existing);
        } else if (GetFlatbufOffset(use)) {
            SetFlatbufOffset(canonical, GetFlatbufOffset(use));
        } else {
            pending.emplace_back(offset, use);
        }
    }
    for (size_t round = 0, max_rounds = pending.size();
         round < max_rounds && !pending.empty(); ++round) {
        bool progress = false;
        for (size_t i = 0; i < pending.size();) {
            const auto [offset, use] = pending[i];
            Code expr;
            if (!offset.IsImmediate() && !EmitOffset(expr, pass_info, offset)) {
                ++i; // The flatbuf slot is not available yet.
                continue;
            }
            if (offset.IsImmediate()) {
                Emit(c, SrtOp::CopyImm, offset.U32(), pass_info.dst_off_dw);
            } else {
                c.insert(c.end(), expr.begin(), expr.end());
                Emit(c, SrtOp::CopyExpr, 0, pass_info.dst_off_dw);
            }
            auto* canonical = pass_info.DeduplicateInstruction(use);
            SetFlatbufOffset(use, pass_info.dst_off_dw);
            if (canonical != use) SetFlatbufOffset(canonical, pass_info.dst_off_dw);
            ++pass_info.dst_off_dw;
            pending.erase(pending.begin() + i);
            progress = true;
        }
        if (!progress) break;
    }
    for (const auto& [offset, use] : *uses) {
        if (GetFlatbufOffset(use) && pass_info.GetUsesAsPointer(use))
            VisitPointer(offset, use, pass_info, c);
    }
    Emit(c, SrtOp::PopPtr);
}

static void GenerateSrtProgram(Info& info, PassInfo& pass_info) {
    if (pass_info.srt_roots.empty()) return;
    Code code{SrtMagic};
    pass_info.dst_off_dw = NUM_USER_DATA_REGS;
    ASSERT(pass_info.dst_off_dw == info.srt_info.flattened_bufsize_dw);
    // Fixed-point walk across all roots, not a one-time forward pass.
    const size_t limit = pass_info.pointer_uses.size() + 1;
    for (size_t round = 0; round < limit; ++round) {
        const u16 before = pass_info.dst_off_dw;
        for (const auto& [sgpr, root] : pass_info.srt_roots)
            VisitPointer(IR::Value(static_cast<u32>(sgpr)), root, pass_info, code);
        if (pass_info.dst_off_dw == before) break;
    }
    size_t unresolved = 0;
    for (const auto& [parent, uses] : pass_info.pointer_uses)
        for (const auto& [offset, use] : uses)
            if (!GetFlatbufOffset(use)) ++unresolved;
    if (unresolved) {
        static std::atomic<u32> report_count{0};
        const u32 report = report_count.fetch_add(1, std::memory_order_relaxed) + 1;
        if (report <= 16 || report % 128 == 0)
            LOG_WARNING(Render_Recompiler,
                "ORDER1886_SRT_UNRESOLVED: shader={:#x} count={} report={}",
                info.pgm_hash, unresolved, report);
    }
    Emit(code, SrtOp::End);
    info.srt_info.walker_func = StoreWalker(code.data(), code.size());
    info.srt_info.walker_func_size = code.size() * sizeof(u32);
    info.srt_info.flattened_bufsize_dw = pass_info.dst_off_dw;
    if (EmulatorSettings.IsDumpShaders()) DumpSrtProgram(info, code.data(), code.size());
}

static bool IsReadConstSource(const IR::Value base) {
    auto* inst = base.TryInst();
    if (!inst) {
        return false;
    }
    return inst->GetOpcode() == IR::Opcode::GetUserData ||
           inst->GetOpcode() == IR::Opcode::ReadConst ||
           inst->GetOpcode() == IR::Opcode::ReadConstBuffer;
}

void SimplifyReadConstAddressAdd(IR::Inst& inst) {
    // This handles the following pattern by combining the addition with the offset
    // s_add_u32    s12, s2, <offset>
    // s_addc_u32   s13, s3, 0
    // s_load_dword s16, s[12:13], 0x0

    if (inst.GetOpcode() != IR::Opcode::ReadConst) {
        return;
    }
    IR::Inst* addr = inst.Arg(0).Inst();
    IR::Inst* hi = addr->Arg(1).TryInst();
    IR::Inst* lo = addr->Arg(0).TryInst();
    if (!hi || !lo) {
        return;
    }

    if (lo->GetOpcode() != IR::Opcode::IAdd32 || hi->GetOpcode() != IR::Opcode::IAdd32) {
        return;
    }

    IR::Value add_offset;
    IR::Value base;
    if (base = lo->Arg(0); IsReadConstSource(base)) {
        add_offset = lo->Arg(1);
    } else if (base = lo->Arg(1); IsReadConstSource(base)) {
        add_offset = lo->Arg(0);
    } else {
        return;
    }

    IR::Inst* sel = hi->Arg(1).TryInst();
    if (!sel || sel->GetOpcode() != IR::Opcode::SelectU32) {
        return;
    }

    IR::Value sel_true = sel->Arg(1);
    IR::Value sel_false = sel->Arg(2);
    if (!sel_true.IsImmediate() || !sel_false.IsImmediate() || sel_true.U32() != 1 ||
        sel_false.U32() != 0) {
        return;
    }

    addr->SetArg(0, base);
    addr->SetArg(1, hi->Arg(0));
    for (auto [user, operand] : addr->Uses()) {
        ASSERT(user->GetOpcode() == IR::Opcode::ReadConst && operand == 0);
        IR::IREmitter ir{*user->GetParent(), IR::Block::InstructionList::s_iterator_to(*user)};
        IR::U32 offset = IR::U32{user->Arg(1)};
        IR::U32 dw_add_offset =
            add_offset.IsImmediate()
                ? ir.Imm32(add_offset.U32() >> 2u)
                : IR::U32{ir.ShiftRightLogical(IR::U32{add_offset}, ir.Imm32(2u))};
        if (offset.IsImmediate() && dw_add_offset.IsImmediate()) {
            user->SetArg(1, ir.Imm32(offset.U32() + dw_add_offset.U32()));
        } else {
            user->SetArg(1, ir.IAdd(offset, dw_add_offset));
        }
    }
}

} // Anonymous namespace

void FlattenExtendedUserdataPass(IR::Program& program) {
    auto& post_order = program.post_order_blocks;
    PassInfo pass_info;

    // traverse at end and assign offsets to duplicate readconsts, using
    // vn_to_inst as the source
    boost::container::small_vector<IR::Inst*, 32> all_readconsts, visited;
    std::queue<IR::Inst*> queue;

    for (auto it = post_order.rbegin(); it != post_order.rend(); it++) {
        IR::Block* block{*it};
        for (IR::Inst& inst : *block) {
            if (inst.GetOpcode() != IR::Opcode::ReadConst &&
                inst.GetOpcode() != IR::Opcode::ReadConstBuffer) {
                continue;
            }

            if (inst.GetOpcode() == IR::Opcode::ReadConstBuffer) {
                // Only flatten ReadConstBuffer if it was marked as a sharp source in the
                // resource discovery pass
                auto inst_info = inst.Flags<IR::BufferInstInfo>();
                if (!inst_info.sharp_source) {
                    continue;
                }
            }

            SimplifyReadConstAddressAdd(inst);

            all_readconsts.push_back(&inst);

            auto offset = inst.Arg(1);
            if (offset.IsImmediate()) {
                continue;
            }

            queue.push(offset.Inst());
            while (!queue.empty()) {
                IR::Inst* inst{queue.front()};
                queue.pop();

                if (inst->GetOpcode() == IR::Opcode::ReadConstBuffer) {
                    auto buffer_inst_info = inst->Flags<IR::BufferInstInfo>();
                    if (!buffer_inst_info.sharp_source.Value()) {
                        all_readconsts.push_back(inst);
                        auto offset = inst->Arg(1);
                        if (!offset.IsImmediate()) {
                            auto arg_inst = offset.Inst();
                            if (std::ranges::find(visited, arg_inst) == visited.end()) {
                                visited.push_back(arg_inst);
                                queue.push(arg_inst);
                            }
                        }
                    }
                    continue;
                }
                if (inst->GetOpcode() == IR::Opcode::GetUserData ||
                    inst->GetOpcode() == IR::Opcode::ReadConst ||
                    !IsAllowedOffsetInstruction(inst)) {
                    continue;
                }
                for (size_t arg = inst->NumArgs(); arg--;) {
                    const IR::Value arg_value = inst->Arg(arg);
                    if (arg_value.IsImmediate()) {
                        continue;
                    }
                    IR::Inst* arg_inst = arg_value.Inst();
                    if (std::ranges::find(visited, arg_inst) == visited.end()) {
                        visited.push_back(arg_inst);
                        queue.push(arg_inst);
                    }
                }
            }
        }
    }

    for (auto inst : all_readconsts) {
        if (pass_info.DeduplicateInstruction(inst) != inst) {
            // This is a duplicate of a readconst we've already visited
            continue;
        }

        IR::Inst* base = inst->Arg(0).Inst();
        if (auto* inst = base->Arg(0).TryInst();
            inst && inst->GetOpcode() == IR::Opcode::ReadFirstLane) {
            continue;
        }
        ASSERT_MSG(IsReadConstSource(base->Arg(0)), "ReadConst base low not from constant memory");
        ASSERT_MSG(IsReadConstSource(base->Arg(1)), "ReadConst base high not from constant memory");

        IR::Inst* ptr_lo = base->Arg(0).Inst();
        ptr_lo = pass_info.DeduplicateInstruction(ptr_lo);

        auto ptr_uses_kv = pass_info.pointer_uses.try_emplace(ptr_lo, PassInfo::PtrUserList{});
        PassInfo::PtrUserList& user_list = ptr_uses_kv.first->second;

        user_list[inst->Arg(1)] = inst;

        if (ptr_lo->GetOpcode() == IR::Opcode::GetUserData) {
            IR::ScalarReg ud_reg = ptr_lo->Arg(0).ScalarReg();
            pass_info.srt_roots[ud_reg] = ptr_lo;
        }
    }

    GenerateSrtProgram(program.info, pass_info);

    // Assign offsets to duplicate readconsts
    for (IR::Inst* readconst : all_readconsts) {
        ASSERT(pass_info.vn_to_inst.contains(pass_info.gvn_table.GetValueNumber(readconst)));
        IR::Inst* original = pass_info.DeduplicateInstruction(readconst);
        SetFlatbufOffset(readconst, GetFlatbufOffset(original));
    }

    program.info.RefreshFlatBuf();
}

} // namespace Shader::Optimization
