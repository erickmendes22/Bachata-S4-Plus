// SPDX-License-Identifier: GPL-2.0-or-later
// SotC effective donor 732cb37d3470 / Android staging 0366868550.
#pragma once

#include <cstdint>

namespace Shader::DonorEarlyDepth {
constexpr bool RegisterPolicy(bool enabled, std::uint32_t z_order, std::uint8_t mrtz_mask) {
    return enabled && (z_order == 1 || z_order == 3) && (mrtz_mask & 7) == 0;
}

constexpr bool ShaderPolicy(bool requested, bool storage_writes, bool discard,
                            bool depth, bool stencil, bool sample_mask) {
    return requested && storage_writes && !discard && !depth && !stencil && !sample_mask;
}
} // namespace Shader::DonorEarlyDepth
