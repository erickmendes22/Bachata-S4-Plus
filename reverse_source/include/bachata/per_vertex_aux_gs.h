// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <cstdint>
#include <vector>

namespace Shader {
struct Info;
struct Profile;
struct RuntimeInfo;
}

namespace Bachata::PerVertexFallback {

struct Locations {
    std::array<std::uint32_t, 32> slot_loc{};
    std::uint32_t bary_coord_loc{};
};

std::uint32_t UnsupportedBarycentricMask(const Shader::RuntimeInfo& runtime_info);
bool CanExpand(const Shader::Profile& profile, const Shader::RuntimeInfo& runtime_info);
bool NeedsAuxGS(const Shader::Profile& profile, const Shader::Info& info,
                const Shader::RuntimeInfo& runtime_info);
Locations ComputeLocations(const Shader::Profile& profile, const Shader::Info& info,
                           const Shader::RuntimeInfo& runtime_info);
std::vector<std::uint32_t> EmitAuxGS(const Shader::Profile& profile, const Shader::Info& info,
                                     const Shader::RuntimeInfo& runtime_info);

} // namespace Bachata::PerVertexFallback
