#!/usr/bin/env python3
"""Restore active donor WQM, instance-ID and fetch-input semantics by title.

Order: Android 756a4f0cc603 / PC c53cd01d0329.
SotC: Android 0366868550bd / PC 732cb37d3470.
The 0.18.1 fetch parser, IR and FEX runtime stay in place; unrelated games keep
their existing input policy. Cache metadata includes the new fetch constants.
"""
from pathlib import Path
import re


POLICY = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdlib>
#include "common/elf_info.h"

namespace Shader::DonorInputs {
inline bool IsSotc() {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    return serial=="CUSA08809" || serial=="CUSA08034";
}
inline bool IsOrder() {
    return Common::ElfInfo::Instance().GameSerial()=="CUSA00785";
}
inline bool SotcRelativeInstanceIdEnabled() {
    // Match the donor's A/B switch; even "0" selects absolute IDs when present.
    static const bool enabled=std::getenv("SHADPS4_ABSOLUTE_INSTANCE_ID")==nullptr;
    return enabled;
}
inline bool SotcWqmEnabled() {
    static const bool enabled=[] {
        const char* value=std::getenv("SOTC_WQM_COPY");
        return value ? std::atoi(value)!=0 : true;
    }();
    return enabled;
}
}
'''


WQM = r'''        case Opcode::S_WQM_B64: {
            // SotC water writes VCC from EXEC; foliage needs all four lanes of
            // every touched quad alive for texture derivatives. Copying the
            // input mask without quad expansion does not implement S_WQM.
            if (!DonorInputs::IsSotc() || !DonorInputs::SotcWqmEnabled() ||
                (inst.dst[0].field == OperandField::ExecLo &&
                 inst.src[0].field == OperandField::ExecLo)) {
                break;
            }
            const IR::U1 bit{ir.InverseBallot(GetSrc64(inst.src[0]))};
            const IR::U32 v{ir.Select(bit, ir.Imm32(1u), ir.Imm32(0u))};
            const IR::U32 quad{ir.BitwiseOr(
                ir.BitwiseOr(ir.QuadBroadcast(v, ir.Imm32(0u)), ir.QuadBroadcast(v, ir.Imm32(1u))),
                ir.BitwiseOr(ir.QuadBroadcast(v, ir.Imm32(2u)), ir.QuadBroadcast(v, ir.Imm32(3u))))};
            const IR::U64 mask{ir.Ballot(ir.INotEqual(quad, ir.Imm32(0u)))};
            SetDst64(inst.dst[0], mask);
            ir.SetScc(ir.InverseBallot(mask));
            return;
        }'''


INSTANCE_ID = r'''        // Vulkan InstanceIndex includes firstInstance; GCN input VGPRs
        // start at zero. Preserve the two donors' fetch/indirect-SGPR policies.
        const auto hardware_instance_id = [&] {
            IR::U32 id = ir.GetAttributeU32(IR::Attribute::InstanceId);
            const bool relative_order = DonorInputs::IsOrder() && base_instance_sgpr == -1;
            const bool relative_sotc = DonorInputs::IsSotc() &&
                DonorInputs::SotcRelativeInstanceIdEnabled() &&
                !(base_instance_sgpr != -1 && fetch_data.Empty() &&
                  fetch_data.instance_offset_sgpr != -1);
            if (relative_order || relative_sotc) {
                id = ir.ISub(id, ir.GetAttributeU32(IR::Attribute::BaseInstance));
            }
            return id;
        };

'''


def apply(root: Path):
    root=Path(root)
    sh=root/"src/shader_recompiler"

    def edit(path, old, new, count=1):
        text=path.read_text()
        if text.count(old)!=count:
            raise RuntimeError(f"Shader input contract drift {path.name}: {old[:100]!r} ({text.count(old)})")
        path.write_text(text.replace(old,new))

    (sh/"frontend/donor_shader_input_policy.h").write_text(POLICY)
    include='#include "shader_recompiler/frontend/donor_shader_input_policy.h"\n'
    for name in ("translate/scalar_alu.cpp","translate/translate.cpp","fetch_shader.cpp"):
        path=sh/"frontend"/name
        text=path.read_text()
        path.write_text(include+text)

    edit(sh/"frontend/translate/scalar_alu.cpp",
         "        case Opcode::S_WQM_B64:\n            break;",WQM)

    translate=sh/"frontend/translate/translate.cpp"
    edit(translate,"        // v0: vertex ID, always present\n",
         INSTANCE_ID+"        // v0: vertex ID, always present\n")
    edit(translate,"ir.IDiv(ir.GetAttributeU32(IR::Attribute::InstanceId),",
         "ir.IDiv(hardware_instance_id(),",count=2)
    # The Order donor uses optional<FetchShaderData>. Its !fetch_data means
    # absent, corresponding to Empty() in 0.18.1, not !Empty(). SotC's pinned
    # source uses the existing condition and keeps that title policy.
    for offset in ("vertex", "instance"):
        edit(translate,
             f"if (!fetch_data.Empty() || fetch_data.{offset}_offset_sgpr == -1) {{",
             f"if ((DonorInputs::IsOrder() ? fetch_data.Empty() : !fetch_data.Empty()) ||\n"
             f"                    fetch_data.{offset}_offset_sgpr == -1) {{")
    edit(translate,
         '''            ir.SetVectorReg(dst_vreg++, instance_id);
        }
        break;
    }
    case SwStage::Fragment:''',
         '''            if (base_instance_sgpr == -1 &&
                (DonorInputs::IsOrder() ||
                 (DonorInputs::IsSotc() && DonorInputs::SotcRelativeInstanceIdEnabled()))) {
                instance_id = hardware_instance_id();
            }
            ir.SetVectorReg(dst_vreg++, instance_id);
        }
        break;
    }
    case SwStage::Fragment:''')

    fetch=sh/"frontend/fetch_shader.h"
    edit(fetch,"    s8 instance_offset_sgpr = -1; ///< SGPR of instance offset from VADDR\n",
         "    s8 instance_offset_sgpr = -1; ///< SGPR of instance offset from VADDR\n"
         "    SmallVector<u8, 4> one_vgprs; ///< SotC fetch constants (v_mov_b32 vN, 1.0).\n")
    edit(fetch,"        return attributes == other.attributes && vertex_offset_sgpr == other.vertex_offset_sgpr &&",
         "        return attributes == other.attributes && one_vgprs == other.one_vgprs &&\n"
         "               vertex_offset_sgpr == other.vertex_offset_sgpr &&")
    fetch_cpp=sh/"frontend/fetch_shader.cpp"
    edit(fetch_cpp,"    out_fetch_data.attributes.clear();",
         "    out_fetch_data.attributes.clear();\n    out_fetch_data.one_vgprs.clear();")
    edit(fetch_cpp,
         '            LOG_WARNING(Render_Recompiler, "Fetch shader has V{} = 1.0 which is ignored", vdst);',
         '''            if (DonorInputs::IsSotc()) {
                out_fetch_data.one_vgprs.push_back(u8(vdst));
            } else {
                LOG_WARNING(Render_Recompiler, "Fetch shader has V{} = 1.0 which is ignored", vdst);
            }''')
    edit(translate,
         '''            ir.SetVectorReg(dst_reg++, IR::F32{ir.CompositeExtract(swizzled, i)});
        }
    }
}

void Translator::LogMissingOpcode''',
         '''            ir.SetVectorReg(dst_reg++, IR::F32{ir.CompositeExtract(swizzled, i)});
        }
    }
    // A format load writes only its encoded component count. Preserve the
    // explicit 1.0 component supplied by the fetch shader (SotC donor).
    for (const u8 vgpr : fetch_data.one_vgprs) {
        ir.SetVectorReg(IR::VectorReg(vgpr), ir.Imm32(1.f));
    }
}

void Translator::LogMissingOpcode''')

    directory=root/"src/video_core/renderer_vulkan"
    serialization=directory/"vk_pipeline_serialization.cpp"
    edit(serialization,"    ar.Grow(6 + attributes.size() * sizeof(VertexAttribute));",
         "    ar.Grow(6 + attributes.size() * sizeof(VertexAttribute) + one_vgprs.size());")
    edit(serialization,"    fetch.Write(attributes);","    fetch.Write(attributes);\n    fetch.Write(one_vgprs);")
    edit(serialization,"    fetch.Read(attributes);","    fetch.Read(attributes);\n    fetch.Read(one_vgprs);")

    source=serialization.read_text()
    for version in ("ShaderBinaryVersion","ShaderMetaVersion"):
        source,count=re.subn(rf"({version} = )(\d+)u;",
                             lambda m:m[1]+str(int(m[2])+1)+"u;",source)
        if count!=1: raise RuntimeError(f"Shader input {version} cache drift")
    serialization.write_text(source)
    live=directory/"order_live_pso_cache.h"
    if live.exists():
        versions="-".join(re.search(rf"{n} = (\d+)u;",source)[1] for n in
                          ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
        text,count=re.subn(r"live-pso-v1-\d+-\d+-\d+","live-pso-v1-"+versions,live.read_text())
        if count!=1: raise RuntimeError("Shader input live PSO generation drift")
        live.write_text(text)
    return {"sotc":"whole-quad mask expansion, relative instance IDs, explicit fetch 1.0 inputs",
            "order":"relative hardware instance IDs with donor indirect-SGPR behavior",
            "fetch_cache":"constants serialized, deserialized, compared and cache versions invalidated",
            "other_games":"existing input policy preserved", "cpu":"FEX unchanged"}
