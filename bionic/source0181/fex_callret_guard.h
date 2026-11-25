// SPDX-License-Identifier: MIT
// FEX f2b679f6028ce1c38875233aecfcf5d3f8ebecec: non-ARM64EC REG_CALLRET_SP=x25.
// Same reset location as ThreadManager::GetCallRetStackInfo and Windows CallRetStack.
#pragma once
#include <cstdint>
namespace BachataFex {
constexpr bool IsCallRetGuardAccess(std::uint64_t base,std::uint64_t size,std::uint64_t page,
                                    std::uint64_t fault,std::uint64_t sp,std::uint32_t instruction) {
    if(!base || base<page || !size || size>UINT64_MAX-base ||
       page>UINT64_MAX-base-size) return false;
    if(!((fault>=base-page&&fault<base)||(fault>=base+size&&fault<base+size+page)))
        return false;
    // Actual ARM64 encodings from pinned FEX BranchOps.cpp:
    // stp Rt,Rt2,[x25,#-16]! and ldp Rt,Rt2,[x25],#16.
    constexpr std::uint32_t mask=0xffff83e0u;
    const auto op=instruction&mask;
    if(op==0xa9bf0320u) return sp>=16 && fault>=sp-16 && fault<sp;
    if(op==0xa8c10320u) return fault>=sp && fault-sp<16;
    return false;
}
}
