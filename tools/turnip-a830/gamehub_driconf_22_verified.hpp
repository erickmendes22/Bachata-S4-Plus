#pragma once
#include <array>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>
namespace gamehub::a8xx {
struct DriBool { std::string_view name; uint8_t offset; };
inline constexpr std::array<DriBool,22> kGameHubDriBools{{
{"tu_dont_care_as_load",0x30},
{"disable_conservative_lrz",0x40},
{"tu_dont_reserve_descriptor_set",0x41},
{"tu_allow_oob_indirect_ubo_loads",0x42},
{"tu_enable_d24s8_border_color_workaround",0x43},
{"tu_enable_fast_border_color_for_undefined_formats",0x44},
{"tu_use_tex_coord_round_nearest_even_mode",0x45},
{"tu_ignore_frag_depth_direction",0x46},
{"tu_enable_softfloat32",0x47},
{"tu_emulate_alpha_to_coverage",0x48},
{"tu_override_uncached_as_cache_coherent",0x49},
{"tu_restrict_subgroup_size_64",0x4a},
{"tu_advertise_wave32_compat",0x4b},
{"tu_sync_renderpass_cache",0x4c},
{"tu_uncharted_legacy_adreno_compat",0x4d},
{"tu_split_indexed_draws",0x4e},
{"tu_compute_mesh_shader",0x4f},
{"tu_disable_mesh_shader",0x50},
{"tu_emulate_second_queue",0x51},
{"tu_enable_texel_buffer_emulation",0x5c},
{"tu_enable_ssbo_emulation",0x5d},
{"tu_allow_concurrent_binning",0x68},
}};
constexpr std::optional<bool> get_option(std::span<const uint8_t> bytes, std::string_view name) {
  for (const auto& f : kGameHubDriBools) {
    if (f.name==name) {
      if (bytes.size()<=f.offset) return std::nullopt;
      return (bytes[f.offset] & uint8_t(1)) != 0;
    }
  }
  return std::nullopt;
}
constexpr std::optional<bool> get_sync_renderpass_cache_option(std::span<const uint8_t> bytes) {
  // ORIGINAL ARM64 0x8dee00 and 0xcb6860..0xcb6868.
  // +0x4b was incorrectly used in an earlier artifact: it is Wave32.
  if (bytes.size() <= 0x4c) return std::nullopt;
  return (bytes[0x4c] & uint8_t(1)) != 0;
}
} // namespace gamehub::a8xx
