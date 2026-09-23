// SPDX-License-Identifier: GPL-2.0-or-later
#include "bachata/pipeline_aux_gs.h"
#include "bachata/per_vertex_aux_gs.h"

#include "shader_recompiler/info.h"
#include "shader_recompiler/profile.h"
#include "shader_recompiler/runtime_info.h"

namespace Bachata::PerVertexFallback {

namespace {
std::uint64_t Mix(std::uint64_t a, std::uint64_t b) {
    // Local deterministic combiner; replace with the reconstructed runtime's
    // exact HashCombine once that utility is recovered.
    a ^= b + 0x9e3779b97f4a7c15ULL + (a << 6) + (a >> 2);
    return a;
}
} // namespace

std::uint64_t PermutationHash(std::uint64_t pgm_hash, std::uint32_t permutation_index) {
    return Mix(pgm_hash, permutation_index);
}

PipelineAuxDecision DecideAuxGs(const Shader::Profile& profile,
                               const Shader::Info& info,
                               const Shader::RuntimeInfo& runtime_info,
                               std::uint32_t permutation_index,
                               bool has_real_geometry_shader,
                               const AuxGsCache& cache) {
    PipelineAuxDecision out{};
    out.permutation_hash = PermutationHash(info.pgm_hash, permutation_index);

    if (has_real_geometry_shader) {
        return out;
    }

    out.cached_module = cache.Lookup(out.permutation_hash);
    if (out.cached_module) {
        out.inject = true;
        return out;
    }

    if (NeedsAuxGS(profile, info, runtime_info)) {
        out.generate = true;
        out.inject = true;
    }
    return out;
}

} // namespace Bachata::PerVertexFallback
