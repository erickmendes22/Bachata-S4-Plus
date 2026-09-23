// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <cstdint>

namespace Shader {
struct Info;
struct Profile;
struct RuntimeInfo;
}

namespace Bachata::PerVertexFallback {

struct FragmentInputSlotLayout {
    bool active{};
    bool per_vertex{};
    std::uint32_t base_location{};
    std::uint32_t location_count{};
};

struct FragmentInputLayout {
    std::array<FragmentInputSlotLayout, 32> slots{};
    bool has_bary_coord{};
    std::uint32_t bary_coord_location{};
};

FragmentInputLayout BuildFragmentInputLayout(const Shader::Profile& profile,
                                             const Shader::Info& info,
                                             const Shader::RuntimeInfo& runtime_info);

} // namespace Bachata::PerVertexFallback
