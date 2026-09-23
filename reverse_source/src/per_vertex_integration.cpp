// SPDX-License-Identifier: GPL-2.0-or-later
#include "bachata/per_vertex_integration.h"
#include "bachata/per_vertex_aux_gs.h"

#include "shader_recompiler/profile.h"
#include "shader_recompiler/runtime_info.h"

namespace Bachata::PerVertexFallback {

bool ShouldPreservePerVertex(const Shader::Profile& profile,
                             const Shader::RuntimeInfo& runtime_info) {
    return profile.supports_amd_shader_explicit_vertex_parameter ||
           profile.supports_fragment_shader_barycentric ||
           CanExpand(profile, runtime_info);
}

bool ShouldInitializeBarycentrics(const Shader::Profile& profile,
                                  const Shader::RuntimeInfo& runtime_info) {
    return ShouldPreservePerVertex(profile, runtime_info);
}

bool HandleInterpMovEligibility(const Shader::Profile& profile,
                                const Shader::RuntimeInfo& runtime_info) {
    return ShouldPreservePerVertex(profile, runtime_info);
}

} // namespace Bachata::PerVertexFallback
