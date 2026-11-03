#pragma once
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace gamehub::a830 {
// Original GameHub A830 ELF SHA-256:
// 1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
//
// AArch64 @ 0x8dedd4: ADRP x1, 0x8a000
// AArch64 @ 0x8dedd8: ADD x1, x1, #0xcaf -> "tu_sync_renderpass_cache"
// AArch64 @ 0x8dede8: BL option evaluator
// AArch64 @ 0x8dee00: STRB w8, [x19, #0x4c]
// AArch64 @ 0xcb6860: LDRB w8, [x0, #0x4c]; AND w0,w8,#1; RET.
//
// The previously provided "verified" C++ header incorrectly used +0x4b.
// That is the PREVIOUS flag (tu_advertise_wave32_compat).
// This accessor does not implement a GPU cache flush.
constexpr std::size_t sync_renderpass_cache_option_offset = 0x4c;
constexpr std::size_t advertise_wave32_option_offset = 0x4b;

inline std::optional<bool> read_sync_renderpass_cache(
    std::span<const std::uint8_t> options) {
    if (options.size() <= sync_renderpass_cache_option_offset)
        return std::nullopt;
    return (options[sync_renderpass_cache_option_offset] & 1u) != 0;
}
} // namespace gamehub::a830
