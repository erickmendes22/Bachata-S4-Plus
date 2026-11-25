// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <algorithm>
#include <cstdint>
namespace VideoCore::BachataReadback {
struct Span {
    std::uint64_t begin{}, end{};
    constexpr bool Overlaps(Span rhs) const noexcept {
        return begin<end && rhs.begin<rhs.end && begin<rhs.end && rhs.begin<end;
    }
};
struct Pending {
    Span pages{};
    bool dirty{};
    constexpr void Mark(Span changed) noexcept { dirty |= pages.Overlaps(changed); }
};
constexpr Span Window(std::uint64_t addr,std::uint64_t bytes,Span arena,
                      std::uint64_t narrow,std::uint64_t stream) noexcept {
    if(!bytes || addr<arena.begin || addr>=arena.end || bytes>arena.end-addr) return {};
    const std::uint64_t align=stream?65536:narrow;
    const auto start=std::max(addr&~(align-1),arena.begin);
    const auto requested=addr+bytes;
    const auto stop=std::min(arena.end,std::max(start+(stream?stream:narrow),(requested+4095)&~std::uint64_t{4095}));
    return {start,stop};
}
}
