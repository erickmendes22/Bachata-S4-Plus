#!/usr/bin/env python3
"""Port Release 0.2.6 GPU address-domain clamping, with mapped VMA bounds.

Unlike the generic ClampRangeSize() helper, invalid 40-bit GPU pointers
and gaps in the VMA map cannot be treated as a contiguous multi-GB region.
The old helper could also assert before it checked IsMapped().  This is
an ARM64 common-core fix, not a per-game workaround.
"""
from pathlib import Path

def replace_one(s: str, old: str, new: str, label: str) -> str:
    n=s.count(old)
    if n!=1:raise RuntimeError(f"GPU range parity source drift: {label}: {n}")
    return s.replace(old,new,1)

def apply(root: Path) -> dict:
    header=root/"src/core/memory.h"
    impl=root/"src/core/memory.cpp"
    h=header.read_text()
    c=impl.read_text()
    h=replace_one(h,
        "    u64 ClampRangeSize(VAddr virtual_addr, u64 size);\n",
        "    // Release 0.2.6: clamp guest GPU ranges at 40-bit and mapped VMA boundaries.\n"
        "    u64 ClampGpuRangeSize(VAddr virtual_addr, u64 size);\n"
        "    u64 ClampRangeSize(VAddr virtual_addr, u64 size);\n",
        "memory manager API")
    start=c.index("u64 MemoryManager::ClampRangeSize(VAddr virtual_addr, u64 size) {")
    finish=c.index("\nvoid MemoryManager::SetPrtArea(",start)
    original=c[start:finish]
    if "static constexpr u64 MinSizeToClamp = 1_GB;" not in original:
        raise RuntimeError("Expected pinned FEX memory manager buffer-range implementation")
    replacement=r"""// BACHATA_RELEASE026_GPU_RANGE_CLAMP: only valid guest-mapped GPU pages may
// back a Vulkan buffer. A descriptor that requests SIZE_MAX (e.g. sign
// extension of a negative size) must not cross into arbitrary host memory.
u64 MemoryManager::ClampGpuRangeSize(VAddr address, u64 requested) {
    static constexpr u64 GpuAddressLimit = 0x10000000000ULL; // 40-bit PS4 GART
    if (requested == 0 || address < 0x10000 || address >= GpuAddressLimit)
        return 0;
    const u64 capped = std::min<u64>(requested, GpuAddressLimit - address);
    std::shared_lock lock{mutex};
    if (!IsValidMapping(address)) return 0;
    auto it = FindVMA(address);
    if (it == vma_map.end() || !it->second.IsMapped()) return 0;
    u64 position = address;
    u64 result = 0;
    while (it != vma_map.end() && result < capped) {
        const auto& region = it->second;
        if (!region.IsMapped() || position < region.base ||
            position >= region.base + region.size) break;
        const u64 bytes = std::min<u64>(capped - result,
                                       region.base + region.size - position);
        result += bytes;
        position += bytes;
        if (result == capped) break;
        ++it;
        if (it == vma_map.end() || it->second.base != position) break;
    }
    if (result != requested) {
        LOG_WARNING(Kernel_Vmm,
                    "BACHATA_RELEASE026_GPU_RANGE_CLAMP addr={:#x} request={:#x} valid={:#x}",
                    address, requested, result);
    }
    return result;
}

u64 MemoryManager::ClampRangeSize(VAddr virtual_addr, u64 size) {
    static constexpr u64 MinSizeToClamp = 1_GB;
    // Keep the cheap fast path for small verified shader/buffer requests.
    // Multi-GB or overflowed GPU descriptors always validate the VMA span.
    if (size < MinSizeToClamp) return size;
    return ClampGpuRangeSize(virtual_addr, size);
}
"""
    c=c[:start]+replacement+c[finish:]
    if "BACHATA_RELEASE026_GPU_RANGE_CLAMP" not in c:
        raise RuntimeError("GPU range implementation missing")
    header.write_text(h)
    impl.write_text(c)
    return {
        "ported": "Core::MemoryManager::ClampGpuRangeSize",
        "connected": "ClampRangeSize >=1GiB routes through mapped 40-bit range clamp",
        "noUnsafeFallback": True,
    }
