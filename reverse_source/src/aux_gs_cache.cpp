// SPDX-License-Identifier: GPL-2.0-or-later
#include "bachata/aux_gs_cache.h"

namespace Bachata::PerVertexFallback {

bool AuxGsCache::Contains(std::uint64_t permutation_hash) const {
    return modules_.contains(permutation_hash);
}

void AuxGsCache::Store(std::uint64_t permutation_hash, ShaderModuleHandle module) {
    modules_[permutation_hash] = module;
}

std::optional<ShaderModuleHandle> AuxGsCache::Lookup(std::uint64_t permutation_hash) const {
    const auto it = modules_.find(permutation_hash);
    if (it == modules_.end()) {
        return std::nullopt;
    }
    return it->second;
}

void AuxGsCache::Clear() {
    modules_.clear();
}

} // namespace Bachata::PerVertexFallback
