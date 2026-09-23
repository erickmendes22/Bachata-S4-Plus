// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>
#include <optional>
#include <unordered_map>
#include <vector>

namespace Bachata::PerVertexFallback {

// VkShaderModule is deliberately represented as an opaque 64-bit handle here;
// the integration boundary converts it to/from the runtime's Vulkan wrapper.
using ShaderModuleHandle = std::uint64_t;

struct AuxShaderBlob {
    std::uint64_t permutation_hash{};
    std::vector<std::uint32_t> spirv;
};

class AuxGsCache {
public:
    bool Contains(std::uint64_t permutation_hash) const;
    void Store(std::uint64_t permutation_hash, ShaderModuleHandle module);
    std::optional<ShaderModuleHandle> Lookup(std::uint64_t permutation_hash) const;
    void Clear();

private:
    std::unordered_map<std::uint64_t, ShaderModuleHandle> modules_;
};

} // namespace Bachata::PerVertexFallback
