// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>

namespace AmdGpu {
enum class PrimitiveType : std::uint32_t;
}

namespace Bachata {

// Source-level fields reconstructed for the fragment runtime metadata.
// These correspond to information that the AUX-GS fallback needs and must be
// populated by the graphics register -> RuntimeInfo builder.
struct FragmentRuntimeExtensions {
    bool is_vs_direct{};
    AmdGpu::PrimitiveType prim_type{};
};

} // namespace Bachata
