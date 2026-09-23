// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>
#include <optional>

#include "bachata/aux_gs_cache.h"

namespace Shader {
struct Info;
struct Profile;
struct RuntimeInfo;
}

namespace Bachata::PerVertexFallback {

struct PipelineAuxDecision {
    bool generate{};
    bool inject{};
    std::uint64_t permutation_hash{};
    std::optional<ShaderModuleHandle> cached_module;
};

std::uint64_t PermutationHash(std::uint64_t pgm_hash, std::uint32_t permutation_index);

PipelineAuxDecision DecideAuxGs(const Shader::Profile& profile,
                               const Shader::Info& info,
                               const Shader::RuntimeInfo& runtime_info,
                               std::uint32_t permutation_index,
                               bool has_real_geometry_shader,
                               const AuxGsCache& cache);

} // namespace Bachata::PerVertexFallback
