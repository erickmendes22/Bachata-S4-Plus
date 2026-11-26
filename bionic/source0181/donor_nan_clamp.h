// SPDX-License-Identifier: GPL-2.0-or-later
// Effective SotC 732cb37d3470 / 0366868550 and Order c53cd01d0329 / 756a4f0cc603.
#pragma once

#include <cstdlib>
#include "common/elf_info.h"

namespace Shader::DonorNanClamp {
inline bool MinMax() {
    const auto serial = Common::ElfInfo::Instance().GameSerial();
    if (serial != "CUSA08809" && serial != "CUSA08034") return false;
    // The SotC donor opts out when the variable exists, including value "0".
    static const bool enabled = std::getenv("SHADPS4_IEEE_MINMAX") == nullptr;
    return enabled;
}

inline bool Saturate() {
    // Order applies DX10 NaN-to-zero only to the output saturation modifier;
    // its ordinary min/max and general clamp keep the existing F operations.
    return Common::ElfInfo::Instance().GameSerial() == "CUSA00785" || MinMax();
}
} // namespace Shader::DonorNanClamp
