// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>

namespace Bachata::Serialization {

// Reverse-source metadata version. Version 3 is reserved for the first layout
// that persists FragmentRuntimeInfo::is_vs_direct/prim_type and AUX-GS blobs.
inline constexpr std::uint32_t ShaderMetaVersion = 3;
inline constexpr std::uint32_t AuxiliaryShaderBlobVersion = 1;

} // namespace Bachata::Serialization
