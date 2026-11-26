// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include <array>
#include <atomic>
#include <cstdint>
#include <span>
#include <string_view>

namespace Common::OrderFramePacing {

// Recognize the complete instruction after the selected patch has run. A UI
// selection or a patch name alone is not proof that the executable was patched.
inline constexpr std::uint64_t InstructionRva = 0x4507be;
inline constexpr std::array<std::uint8_t, 10> PatchedInstruction{
    0xc7, 0x05, 0x8c, 0x05, 0x17, 0x01, 0x01, 0x00, 0x00, 0x00};
inline std::atomic<std::uint32_t> profile{0};

inline bool Configure(std::string_view serial, std::string_view version,
                      std::span<const std::uint8_t> instruction) {
    std::uint32_t next = 0;
#ifdef __ANDROID__
    if (serial == "CUSA00785") {
        next = 1;
        if (version == "01.02" && instruction.size() == PatchedInstruction.size()) {
            bool match = true;
            for (std::size_t i = 0; i < instruction.size(); ++i) {
                match &= instruction[i] == PatchedInstruction[i];
            }
            if (match) next |= 2;
        }
    }
#else
    (void)serial;
    (void)version;
    (void)instruction;
#endif
    profile.store(next, std::memory_order_release);
    return (next & 2) != 0;
}

inline bool IsTarget() {
    return (profile.load(std::memory_order_acquire) & 1) != 0;
}

inline std::uint32_t FrameLimit() {
    return (profile.load(std::memory_order_acquire) & 2) ? 60 : 0;
}

} // namespace Common::OrderFramePacing
