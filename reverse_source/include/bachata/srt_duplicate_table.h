// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>
#include <unordered_map>
#include <vector>

namespace Shader::IR {
class Inst;
}

namespace Bachata {

class SrtDuplicateTable {
public:
    void Reset();
    void RecordReplacement(Shader::IR::Inst* survivor, Shader::IR::Inst* replaced);
    void PropagateFlags(Shader::IR::Inst* survivor, std::uint32_t flags) const;

private:
    std::unordered_map<Shader::IR::Inst*, std::vector<Shader::IR::Inst*>> duplicates_;
};

} // namespace Bachata
