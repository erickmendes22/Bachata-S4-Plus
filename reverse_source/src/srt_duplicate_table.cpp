// SPDX-License-Identifier: GPL-2.0-or-later
#include "bachata/srt_duplicate_table.h"
#include "shader_recompiler/ir/value.h"

namespace Bachata {

void SrtDuplicateTable::Reset() {
    duplicates_.clear();
}

void SrtDuplicateTable::RecordReplacement(Shader::IR::Inst* survivor,
                                          Shader::IR::Inst* replaced) {
    if (!survivor || !replaced || survivor == replaced) {
        return;
    }
    duplicates_[survivor].push_back(replaced);
}

void SrtDuplicateTable::PropagateFlags(Shader::IR::Inst* survivor,
                                       std::uint32_t flags) const {
    if (!survivor) {
        return;
    }
    survivor->SetFlags<std::uint32_t>(flags);
    const auto it = duplicates_.find(survivor);
    if (it == duplicates_.end()) {
        return;
    }
    for (Shader::IR::Inst* duplicate : it->second) {
        if (duplicate) {
            duplicate->SetFlags<std::uint32_t>(flags);
        }
    }
}

} // namespace Bachata
