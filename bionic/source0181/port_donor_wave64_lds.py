#!/usr/bin/env python3
"""Adapt donor LDS synchronization and Wave64/ReadLane as complete title policies.

SotC: staged 0366868550bd / PC 732cb37d3470. Order: staged 756a4f0 / PC c53cd01.
Retain the previous 0.18.1 policy for every other game and all FEX CPU paths.
"""
from pathlib import Path
import re
import shutil


POLICY_HEADER = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <unordered_set>
#include <vector>
#include "common/elf_info.h"
#include "shader_recompiler/ir/program.h"
#include "shader_recompiler/profile.h"

namespace Shader::Optimization {
inline bool BachataDonorIsSotc() {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    return serial=="CUSA08809" || serial=="CUSA08034";
}
inline bool BachataDonorIsOrder() {
    return Common::ElfInfo::Instance().GameSerial()=="CUSA00785";
}
namespace DonorSotcWave64 {
std::vector<IR::Block*> FindWave64UniformBlocks(
    const IR::Program&, const std::unordered_set<const IR::Inst*>* uniform_insts=nullptr);
bool Wave64UniformBranchesEnabled();
void SetWave64UniformBranchesDefault(bool enabled);
void LowerWave64BallotPass(IR::Program&, const RuntimeInfo&, const Profile&);
void SharedMemoryBarrierPass(IR::Program&, const RuntimeInfo&, const Profile&);
}
namespace DonorOrderLds {
void SharedMemoryBarrierPass(IR::Program&, const RuntimeInfo&, const Profile&);
}
}
'''


def apply(root: Path):
    sh = root / "src/shader_recompiler"
    def edit(path, old, new, count=1):
        source=path.read_text()
        if source.count(old)!=count:
            raise RuntimeError(f"Wave64/LDS contract drift {path.name}: {old[:100]!r} ({source.count(old)})")
        path.write_text(source.replace(old,new))
    passes=sh/"ir/passes"
    (passes/"donor_wave64_policy.h").write_text(POLICY_HEADER)
    for name in ("donor_sotc_wave64.inc","donor_sotc_lds.inc","donor_order_lds.inc"):
        shutil.copyfile(Path(__file__).parent/"inherited_shader"/name,passes/name)

    # Complete IR chain: opcode, side-effect retention, IR builder, SPIR-V builder.
    opcodes=sh/"ir/opcodes.inc"
    line="OPCODE(SubgroupBarrier,                                     Void,                                                                                           )"
    source=opcodes.read_text()
    anchor=next(x for x in source.splitlines() if x.startswith("OPCODE(WorkgroupMemoryBarrier,"))
    edit(opcodes,anchor,anchor+"\n"+line)
    edit(sh/"ir/microinstruction.cpp","    case Opcode::WorkgroupMemoryBarrier:",
         "    case Opcode::WorkgroupMemoryBarrier:\n    case Opcode::SubgroupBarrier:")
    edit(sh/"ir/ir_emitter.h","    void WorkgroupMemoryBarrier();",
         "    void SubgroupBarrier();\n    void WorkgroupMemoryBarrier();")
    edit(sh/"ir/ir_emitter.cpp","void IREmitter::WorkgroupMemoryBarrier() {",
         "void IREmitter::SubgroupBarrier() {\n    Inst(Opcode::SubgroupBarrier);\n}\n\n"
         "void IREmitter::WorkgroupMemoryBarrier() {")
    edit(sh/"backend/spirv/emit_spirv_instructions.h","void EmitWorkgroupMemoryBarrier(EmitContext& ctx);",
         "void EmitSubgroupBarrier(EmitContext& ctx);\nvoid EmitWorkgroupMemoryBarrier(EmitContext& ctx);")
    edit(sh/"backend/spirv/emit_spirv_barriers.cpp","void EmitWorkgroupMemoryBarrier(EmitContext& ctx) {",
         """// GCN lanes communicate through LDS in lockstep. Pin host memory ordering
// without waiting on unrelated waves in the same workgroup.
void EmitSubgroupBarrier(EmitContext& ctx) {
    const auto semantics{static_cast<u32>(spv::MemorySemanticsMask::AcquireRelease |
                                          spv::MemorySemanticsMask::WorkgroupMemory)};
    ctx.OpMemoryBarrier(ctx.ConstU32(static_cast<u32>(spv::Scope::Subgroup)),
                        ctx.ConstU32(semantics));
}

void EmitWorkgroupMemoryBarrier(EmitContext& ctx) {""")

    wave=passes/"lower_wave64_pass.cpp"
    lds=passes/"shared_memory_barrier_pass.cpp"
    for path in (wave,lds):
        edit(path,'#include "shader_recompiler/profile.h"',
             '#include "shader_recompiler/profile.h"\n'
             '#include "shader_recompiler/ir/passes/donor_wave64_policy.h"')
    edit(wave,"""void LowerWave64BallotPass(IR::Program& program, const RuntimeInfo& runtime_info,
                           const Profile& profile) {""",
         """void LowerWave64BallotPass(IR::Program& program, const RuntimeInfo& runtime_info,
                           const Profile& profile) {
    if (BachataDonorIsSotc()) {
        DonorSotcWave64::LowerWave64BallotPass(program,runtime_info,profile);
        return;
    }""")
    edit(lds,"""void SharedMemoryBarrierPass(IR::Program& program, const RuntimeInfo& runtime_info,
                             const Profile& profile) {""",
         """void SharedMemoryBarrierPass(IR::Program& program, const RuntimeInfo& runtime_info,
                             const Profile& profile) {
    if (BachataDonorIsSotc()) {
        DonorSotcWave64::SharedMemoryBarrierPass(program,runtime_info,profile);
        return;
    }
    if (BachataDonorIsOrder()) {
        DonorOrderLds::SharedMemoryBarrierPass(program,runtime_info,profile);
        return;
    }""")
    with wave.open("a") as output:
        output.write('\n#include "shader_recompiler/ir/passes/donor_sotc_wave64.inc"\n')
    with lds.open("a") as output:
        output.write('\n#include "shader_recompiler/ir/passes/donor_sotc_lds.inc"\n'
                     '#include "shader_recompiler/ir/passes/donor_order_lds.inc"\n')

    directory=root/"src/video_core/renderer_vulkan"
    ser=directory/"vk_pipeline_serialization.cpp"
    source,count=re.subn(r"(ShaderBinaryVersion = )(\d+)u;",
                         lambda m:m[1]+str(int(m[2])+1)+"u;",ser.read_text())
    if count!=1: raise RuntimeError("Wave64/LDS cache version drift")
    ser.write_text(source)
    live=directory/"order_live_pso_cache.h"
    if live.exists():
        versions="-".join(re.search(rf"{n} = (\d+)u;",source)[1] for n in
                          ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
        contents,count=re.subn(r"live-pso-v1-\d+-\d+-\d+","live-pso-v1-"+versions,live.read_text())
        if count!=1: raise RuntimeError("Wave64/LDS live PSO version drift")
        live.write_text(contents)
    return {"sotc":"full donor absent-lane identity, uniform ReadLane/ballot fixed point, partial/multi-wave LDS",
            "order":"donor subgroup LDS ordering outside full-wave workgroups",
            "other_games":"existing 0.18.1 policy preserved", "cpu":"FEX unchanged",
            "cache":"prior shader/PSO generations rejected"}
