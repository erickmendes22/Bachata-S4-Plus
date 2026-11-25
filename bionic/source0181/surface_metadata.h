// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include <cstdint>
#include <limits>
#include <map>
#include <mutex>
#include <optional>
#include <span>
#include <utility>

namespace VideoCore {

// Active metadata-state protocol from the effective The Order GPU donor.
// Bachata retains its ImageId/UID owner map separately. No synthetic HTILE
// buffer reads are enabled: that donor feature is off by default.
class SurfaceMetadata {
public:
    enum class Type { CMask, FMask, HTile };
    using ClearRange = std::pair<std::uint64_t, std::uint64_t>;

    void Register(std::uint64_t address, std::uint64_t owner, Type type,
                  std::uint32_t clear_mask = ~0u, std::uint32_t layers = 1,
                  bool stencil = false) {
        std::scoped_lock lock{mutex};
        const auto it = entries.find(address);
        if (it == entries.end() || it->second.owner != owner || it->second.type != type ||
            it->second.layers != layers || it->second.stencil != stencil) {
            WriteLocked(address, it != entries.end() && it->second.size ? it->second.size : 1);
            entries.insert_or_assign(address, Entry{owner, type, clear_mask, layers, stencil});
        }
    }

    void Erase(std::uint64_t address, std::uint64_t owner) {
        std::scoped_lock lock{mutex};
        const auto it = entries.find(address);
        if (it != entries.end() && it->second.owner == owner) {
            entries.erase(it);
        }
    }

    void Unmap(std::uint64_t address, std::uint64_t size) {
        if (!size) return;
        std::scoped_lock lock{mutex};
        for (auto it = entries.begin(); it != entries.end();) {
            const auto extent = it->second.size ? it->second.size : 1;
            if (address <= it->first ? it->first - address < size : address - it->first < extent) {
                it = entries.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::optional<Type> TypeAt(std::uint64_t address) const {
        std::scoped_lock lock{mutex};
        const auto it = entries.find(address);
        return it == entries.end() ? std::nullopt : std::optional{it->second.type};
    }

    bool IsCleared(std::uint64_t address, std::uint32_t slice) const {
        if (slice >= 32) return false;
        std::scoped_lock lock{mutex};
        const auto it = entries.find(address);
        return it != entries.end() && (it->second.clear_mask & (1u << slice));
    }

    bool Clear(std::uint64_t address, std::uint64_t size) {
        const ClearRange range{address, size};
        return ClearBatch(std::span{&range, 1});
    }

    // A dispatch is replaced only when every output can be represented.
    // Validate all ranges before changing any masks, so a rejected later
    // output cannot leave an earlier output falsely marked as cleared.
    bool ClearBatch(std::span<const ClearRange> ranges) {
        if (ranges.empty()) return false;
        std::scoped_lock lock{mutex};
        for (const auto& [address, size] : ranges) {
            if (!size || (address & 3) || (size & 3) ||
                size > std::numeric_limits<std::uint64_t>::max() - address) {
                return false;
            }
            const auto it = entries.find(address);
            if (it == entries.end()) return false;
            const auto& entry = it->second;
            if (entry.type == Type::HTile &&
                (entry.layers != 1 || size > std::numeric_limits<std::uint32_t>::max())) {
                return false;
            }
        }
        for (const auto& [address, size] : ranges) {
            WriteLocked(address, size);
        }
        for (const auto& [address, size] : ranges) {
            auto& entry = entries.find(address)->second;
            entry.clear_mask = ~0u;
            entry.size = size;
        }
        return true;
    }

    bool Touch(std::uint64_t address, std::uint32_t slice, bool clear) {
        std::scoped_lock lock{mutex};
        const auto it = entries.find(address);
        if (it == entries.end()) return false;
        auto& entry = it->second;
        if (slice >= 32) {
            entry.clear_mask = 0;
            return false;
        }
        const auto previous = entry.clear_mask;
        if (clear) entry.clear_mask |= 1u << slice;
        else entry.clear_mask &= ~(1u << slice);
        return previous != entry.clear_mask;
    }

    void Write(std::uint64_t address, std::uint64_t size) {
        if (!size) return;
        std::scoped_lock lock{mutex};
        WriteLocked(address, size);
    }

    void Fill(std::uint64_t address, std::uint64_t size, std::uint32_t value) {
        if (!size) return;
        std::scoped_lock lock{mutex};
        WriteLocked(address, size);
        const auto it = entries.find(address);
        // HTILE's low nibble distinguishes a clear value from expanded data.
        if (it == entries.end() || (it->second.type == Type::HTile && (value & 0xf))) return;
        auto& entry = it->second;
        entry.clear_mask = ~0u;
        entry.size = size <= std::numeric_limits<std::uint64_t>::max() - address ? size : 0;
    }

private:
    struct Entry {
        std::uint64_t owner;
        Type type;
        std::uint32_t clear_mask, layers;
        bool stencil;
        std::uint64_t size{};
    };

    void WriteLocked(std::uint64_t address, std::uint64_t size) {
        for (auto& [base, entry] : entries) {
            const auto extent = entry.size ? entry.size : 1;
            if (address <= base ? base - address < size : address - base < extent) {
                entry.clear_mask = 0;
            }
        }
    }

    mutable std::mutex mutex;
    std::map<std::uint64_t, Entry> entries;
};

} // namespace VideoCore
