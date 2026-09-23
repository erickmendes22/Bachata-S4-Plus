// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>

namespace Shader {
struct Info;
struct Profile;
struct RuntimeInfo;
namespace IR {
enum class Attribute : std::uint32_t;
}
namespace Gcn {
class Translator;
struct GcnInst;
}
}

namespace Bachata::PerVertexFallback {

// Translation-side helpers. They are intentionally separated from the
// upstream-style Translator so the reverse-source tree can be integrated
// incrementally without pretending to own unreconstructed code.

bool ShouldPreservePerVertex(const Shader::Profile& profile,
                             const Shader::RuntimeInfo& runtime_info);

bool ShouldInitializeBarycentrics(const Shader::Profile& profile,
                                  const Shader::RuntimeInfo& runtime_info);

// Returns true when V_INTERP_MOV_F32 must keep PerVertex semantics instead of
// degrading to Flat.
bool HandleInterpMovEligibility(const Shader::Profile& profile,
                                const Shader::RuntimeInfo& runtime_info);

} // namespace Bachata::PerVertexFallback
