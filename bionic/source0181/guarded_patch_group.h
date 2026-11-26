// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <span>
#include <string>
#include <vector>

namespace MemoryPatcher::GuardedGroup {
struct Write {
    std::size_t offset{};
    std::vector<std::uint8_t> expected;
    std::vector<std::uint8_t> value;
};

// Patches are applied during game load, before guest execution. Prepare and
// validate the entire group before the first write; commit performs no parsing
// or allocation and cannot fail after an earlier instruction was modified.
template <class IsMapped>
bool Apply(std::span<std::uint8_t> image, std::span<const Write> writes,
           IsMapped&& mapped, std::string& error) {
    if (image.empty() || writes.empty()) {
        error = "empty image or patch group";
        return false;
    }
    for (std::size_t i = 0; i < writes.size(); ++i) {
        const auto& write = writes[i];
        const auto size = write.value.size();
        if (size == 0 || size != write.expected.size() || write.offset > image.size() ||
            size > image.size() - write.offset) {
            error = "invalid byte count or image bounds";
            return false;
        }
        for (std::size_t j = 0; j < i; ++j) {
            const auto& previous = writes[j];
            if (write.offset < previous.offset + previous.value.size() &&
                previous.offset < write.offset + size) {
                error = "overlapping writes in patch group";
                return false;
            }
        }
        if (!mapped(write.offset, size)) {
            error = "patch range is not mapped";
            return false;
        }
        const auto* current = image.data() + write.offset;
        if (!std::equal(write.expected.begin(), write.expected.end(), current) &&
            !std::equal(write.value.begin(), write.value.end(), current)) {
            error = "instruction preimage mismatch";
            return false;
        }
    }
    for (const auto& write : writes) {
        std::memcpy(image.data() + write.offset, write.value.data(), write.value.size());
    }
    return true;
}
} // namespace MemoryPatcher::GuardedGroup
