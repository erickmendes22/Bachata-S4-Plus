// SPDX-License-Identifier: GPL-2.0-or-later
#include "bachata/fragment_input_layout.h"
#include "bachata/per_vertex_aux_gs.h"

#include "shader_recompiler/info.h"
#include "shader_recompiler/profile.h"
#include "shader_recompiler/runtime_info.h"

namespace Bachata::PerVertexFallback {

FragmentInputLayout BuildFragmentInputLayout(const Shader::Profile& profile,
                                             const Shader::Info& info,
                                             const Shader::RuntimeInfo& runtime_info) {
    FragmentInputLayout out{};
    const auto locs = ComputeLocations(profile, info, runtime_info);
    const auto& fs = runtime_info.fs_info;
    const bool expand = CanExpand(profile, runtime_info);
    const bool has_clip = fs.clip_distance_emulation;
    const std::uint32_t count = fs.num_inputs - (has_clip ? 1u : 0u);

    for (std::uint32_t i = 0; i < count; ++i) {
        if (fs.inputs[i].IsDefault()) {
            continue;
        }
        auto& slot = out.slots[i];
        slot.active = true;
        slot.per_vertex =
            info.fs_interpolation[i].primary == Shader::Qualifier::PerVertex;
        slot.base_location = locs.slot_loc[i];
        slot.location_count = slot.per_vertex && expand ? 3u : 1u;
    }

    out.has_bary_coord = expand && fs.addr_flags.persp_center_ena;
    out.bary_coord_location = locs.bary_coord_loc;
    return out;
}

} // namespace Bachata::PerVertexFallback
