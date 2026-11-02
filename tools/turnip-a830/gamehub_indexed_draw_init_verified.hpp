#pragma once
#include <cstdint>
namespace gamehub::a8xx {
// AArch64 original GameHub 0x99bdbc..0x99be14; SHA256-pinned ELF.
// Relevant loads: GPU+0x262, GPU[0] (generation), runtime+0x326.
// Do NOT equate runtime+0x326 with drirc+0x4e, a different structure.
struct IndexedDrawInit { uint32_t limit; uint8_t enhanced_indexed_draws; };
constexpr IndexedDrawInit reconstruct_indexed_draw_init(
    uint8_t split_quirk, uint8_t gpu_generation, uint8_t runtime_0x326) noexcept {
    if (split_quirk != 1) return {0x600u, 0u};
    const uint8_t enabled = gpu_generation > 7 ? runtime_0x326 : 0u;
    return {enabled ? 0x1800u : 0x600u, enabled};
}
// This is a verified init policy, not a complete implementation of
// vkCmdDrawIndexed splitting. Unidentified runtime fields must not be
// wired to GameHub's game-specific dri flags without callsite proof.
} // namespace gamehub::a8xx
