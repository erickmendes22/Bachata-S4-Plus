"""SotC Android stage specialization reuse from stage_sotc_stage_spec_cpu.py.
The 0.18.1 Bachata keeps a separate effective SRT layout for EACH permutation.
Memoize each candidate's exact decision, not the donor's single-program Info.
Always refresh and synchronize SRTs; never skip binding or change match order.
"""
from pathlib import Path

HEADER=r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <algorithm>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>
namespace BachataSotcSpec {
template<class Runtime, class Bindings> struct Memo {
    std::vector<std::uint32_t> flat, user;
    Runtime runtime{};
    Bindings start{};
    std::uint64_t base{}, mapping{};
    bool valid{}, matches{};

    std::optional<bool> Lookup(const Runtime& rt, const Bindings& bindings,
                               std::uint64_t pgm, std::uint64_t generation,
                               std::span<const std::uint32_t> current_flat,
                               std::span<const std::uint32_t> current_user) const {
        if (!valid || (generation&1) || mapping!=generation || base!=pgm ||
            runtime!=rt || start!=bindings ||
            !std::ranges::equal(flat,current_flat) || !std::ranges::equal(user,current_user))
            return std::nullopt;
        return matches;
    }

    void Store(const Runtime& rt, const Bindings& bindings, std::uint64_t pgm,
               std::uint64_t generation, std::span<const std::uint32_t> current_flat,
               std::span<const std::uint32_t> current_user, bool result) {
        valid=false;
        if (generation&1) return;
        flat.assign(current_flat.begin(), current_flat.end());
        user.assign(current_user.begin(), current_user.end());
        runtime=rt;start=bindings;base=pgm;mapping=generation;matches=result;valid=true;
    }
};
}
'''


def apply(root: Path):
    path=Path(root)/'src/video_core/renderer_vulkan'
    (path/'sotc_stage_spec_memo.h').write_text(HEADER)
    def edit(file,a,b):
        p=path/file;s=p.read_text()
        if s.count(a)!=1:raise RuntimeError(f'SotC stage specialization drift {p}: {a[:120]}')
        p.write_text(s.replace(a,b,1))
    edit('vk_pipeline_cache.h','#include "shader_recompiler/specialization.h"',
         '#include "shader_recompiler/specialization.h"\n#include "video_core/renderer_vulkan/sotc_stage_spec_memo.h"')
    edit('vk_pipeline_cache.h','        std::unique_ptr<Shader::Info> effective_info;',
         '''        std::unique_ptr<Shader::Info> effective_info;
        // Aggregate replacement/serialization constructs a fresh, invalid memo.
        BachataSotcSpec::Memo<Shader::RuntimeInfo,Shader::Backend::Bindings> stage_spec_memo{};''')
    edit('vk_pipeline_cache.cpp','#include "common/elf_info.h"',
         '#include "common/elf_info.h"\n#include "core/memory.h"\n#include <cstdlib>')
    edit('vk_pipeline_cache.cpp','    const auto start_binding = binding;\n    // The first program\'s SRT layout',
         '''    const auto start_binding = binding;
    static const bool sotc_spec_enabled=[] {
        const char* v=std::getenv("SOTC_STAGE_SPEC_MEMO"); return !v || v[0]!='0';
    }();
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const bool memo_eligible=sotc_spec_enabled && !EmulatorSettings.IsShaderCollect() &&
        (serial=="CUSA08809" || serial=="CUSA08034") &&
        (sw_stage==SwStage::Fragment || sw_stage==SwStage::Compute);
    auto* memory=Core::Memory::Instance();
    // The first program's SRT layout''')
    edit('vk_pipeline_cache.cpp','''        effective.pgm_base=params.Base();
        effective.user_data=params.user_data;
        effective.RefreshFlatBuf();
        if (srt_sync) srt_sync(effective);
        auto candidate_spec=Shader::StageSpecialization(effective,runtime_info,profile,start_binding);
        if (!(candidate.spec==candidate_spec)) continue;''', '''        const u64 before=memo_eligible?memory->MappingGeneration():0;
        effective.pgm_base=params.Base();
        effective.user_data=params.user_data;
        effective.RefreshFlatBuf();
        if (srt_sync) srt_sync(effective);
        // GetSharp can consult live guest image mappings. A remap during
        // either SRT refresh or lookup invalidates the entire memo attempt.
        const u64 after=memo_eligible?memory->MappingGeneration():0;
        const bool stable=memo_eligible && before==after && !(after&1);
        auto& memo=candidate.stage_spec_memo;
        auto cached=stable?memo.Lookup(runtime_info,start_binding,effective.pgm_base,after,
                                      effective.flattened_ud_buf,effective.user_data):std::nullopt;
        if (cached && (memory->MappingGeneration()!=after ||
            (sw_stage==SwStage::Compute && memo.runtime.hw.cs.shared_memory_size!=runtime_info.hw.cs.shared_memory_size)))
            cached.reset();
        bool matches;
        if (cached.has_value()) {
            matches=*cached;
        } else {
            auto candidate_spec=Shader::StageSpecialization(effective,runtime_info,profile,start_binding);
            matches=candidate.spec==candidate_spec;
            memo.valid=false;
            if (stable && memory->MappingGeneration()==after)
                memo.Store(runtime_info,start_binding,effective.pgm_base,after,
                           effective.flattened_ud_buf,effective.user_data,matches);
        }
        if (!matches) continue;''')
    edit('vk_pipeline_cache.cpp','                m.module = CompileSPV(spv_code, d);',
         '                m.module = CompileSPV(spv_code, d);\n                m.stage_spec_memo.valid = false;')
