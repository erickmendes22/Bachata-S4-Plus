// SPDX-License-Identifier: MIT
#pragma once

#include <atomic>
#include <cstdint>

namespace Core::Fex {

// The pinned FEX backend returns CNTVCT << TSCScale for both RDTSC and
// RDTSCP. Publish its actual CPUID 0x15 ratio, not a guessed SoC frequency.
class GuestTscClock {
public:
    bool Configure(std::uint32_t denominator, std::uint32_t numerator,
                   std::uint32_t crystal_hz) noexcept {
        if (!denominator || !numerator || !crystal_hz || numerator % denominator)
            return false;
        const auto multiplier = numerator / denominator;
        if (!multiplier || (multiplier & (multiplier - 1))) return false;
        parameters.store((std::uint64_t{multiplier} << 32) | crystal_hz,
                         std::memory_order_release);
        return true;
    }

    std::uint64_t Frequency(std::uint64_t fallback) const noexcept {
        const auto p = parameters.load(std::memory_order_acquire);
        return p ? std::uint64_t{static_cast<std::uint32_t>(p)} * (p >> 32) : fallback;
    }

    std::uint64_t Ticks(std::uint64_t native_ticks) const noexcept {
        const auto p = parameters.load(std::memory_order_acquire);
        // Unsigned wraparound is the same as the emulated 64-bit RDTSC.
        return native_ticks * (p ? p >> 32 : 1);
    }

private:
    std::atomic<std::uint64_t> parameters{};
};

inline GuestTscClock guest_tsc_clock;

} // namespace Core::Fex
