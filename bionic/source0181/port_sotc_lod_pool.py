#!/usr/bin/env python3
"""Resolve the active SotC LOD pool through FEX physical mappings.

The donor's pool offset belongs to its final direct-memory metadata region, not to
the constant virtual address at which the AOT runtime happens to map it.
Only the already active SotC LOD pressure policy consumes this query.
"""
from pathlib import Path


TAIL_DECL = r'''    struct DirectTailMapping {
        VAddr address{};
        PAddr physical{};
        u64 size{};
        u64 generation{};
        s32 memory_type{};
    };
    bool QueryDirectTailMapping(DirectTailMapping& result);

'''

TAIL_QUERY = r'''bool MemoryManager::QueryDirectTailMapping(DirectTailMapping& result) {
    result = {};
    std::shared_lock lock{mutex};
    if (!total_direct_size || dmem_map.empty() || vma_map.empty()) {
        return false;
    }
    const auto allocated = [](const PhysicalMemoryArea& area) {
        return area.dma_type == PhysicalMemoryType::Allocated ||
               area.dma_type == PhysicalMemoryType::Mapped;
    };
    auto tail = FindDmemArea(total_direct_size - 1);
    if (tail == dmem_map.end() || !allocated(tail->second) ||
        tail->second.base > total_direct_size ||
        tail->second.size != total_direct_size - tail->second.base) {
        return false;
    }
    // Map/unmap can split a physical region into Allocated/Mapped entries.
    // Recover a contiguous, same-type tail candidate before finding a VA.
    // dmem_map coalesces adjacent allocations; the caller must validate the
    // object's layout and cannot infer allocation identity from this query.
    const s32 memory_type = tail->second.memory_type;
    while (tail != dmem_map.begin()) {
        const auto previous = std::prev(tail);
        if (!allocated(previous->second) || previous->second.memory_type != memory_type ||
            previous->second.GetEnd() != tail->second.base) {
            break;
        }
        tail = previous;
    }
    const PAddr physical = tail->second.base;
    const u64 size = total_direct_size - physical;
    for (const auto& [key, vma] : vma_map) {
        if (vma.type != VMAType::Direct) {
            continue;
        }
        for (const auto& [offset, area] : vma.phys_areas) {
            if (physical < area.base || physical - area.base >= area.size ||
                offset >= vma.size || physical - area.base >= vma.size - offset) {
                continue;
            }
            const VAddr address = vma.base + offset + physical - area.base;
            if (address > UINT64_MAX - size) {
                continue;
            }
            VAddr cursor = address;
            PAddr expected = physical;
            u64 remaining = size;
            bool valid = true;
            while (remaining) {
                if (!IsValidMapping(cursor)) {
                    valid = false;
                    break;
                }
                const auto& part = FindVMA(cursor)->second;
                if (part.type != VMAType::Direct || cursor < part.base ||
                    cursor - part.base >= part.size) {
                    valid = false;
                    break;
                }
                const u64 bytes = std::min(remaining, part.size - (cursor - part.base));
                const bool covered = VisitPhysicalSpans(part, cursor, bytes,
                    [&](PAddr next, u64 count) {
                        valid = valid && next == expected;
                        expected += count;
                    });
                if (!covered || !valid) {
                    valid = false;
                    break;
                }
                cursor += bytes;
                remaining -= bytes;
            }
            if (valid) {
                result = {address, physical, size, mapping_generation.Load(), memory_type};
                return true;
            }
        }
    }
    return false;
}

'''

POOL_READER = r'''struct PoolSample {
    VAddr pool{};
    VAddr bitmap{};
    PAddr physical{};
    u64 words{};
    u64 pages{};
    u64 free{};
};

inline int PoolFreePercent(Core::MemoryManager* memory, PoolSample* sample = nullptr) {
    if (sample) *sample = {};
    Core::MemoryManager::DirectTailMapping mapping{};
    // The game allocates its CPU allocator metadata at the physical top of
    // direct memory. The donor maps it at 0x1000000000; FEX chooses its own VA.
    // The object offset is the donor's documented allocator layout, not an
    // address-space assumption. Never search arbitrary guest bytes for it.
    constexpr u64 PoolOffset = 0x140;
    constexpr u64 MetadataOffset = PoolOffset + 0x50;
    std::array<u64, 3> meta{};
    if (!memory->QueryDirectTailMapping(mapping) || mapping.memory_type != 0 ||
        (mapping.generation & 1) || mapping.size < MetadataOffset + sizeof(meta) ||
        mapping.address > UINT64_MAX - MetadataOffset - sizeof(meta)) {
        return -1;
    }
    const VAddr metadata = mapping.address + MetadataOffset;
    if (!memory->TryReadBacking(metadata, meta.data(), sizeof(meta))) return -1;
    const auto [bitmap, words, pages] = meta;
    const u64 maximum_pages = memory->GetTotalDirectSize() >> 16;
    // Keep the donor's capacity bound: an allocator may round its bitmap
    // storage up beyond ceil(pages / 64). Only real pages count as free.
    if (!words || words > 0x10000 ||
        !pages || pages > words * 64 || pages > maximum_pages ||
        (bitmap & 7) || bitmap < 0x10000 || bitmap >= (u64{1} << 40) ||
        words * sizeof(u64) > (u64{1} << 40) - bitmap) {
        return -1;
    }
    std::array<u64, 256> bits{};
    u64 free = 0;
    for (u64 i = 0; i < words;) {
        const u64 count = std::min<u64>(bits.size(), words - i);
        if (!memory->TryReadBacking(bitmap + i * sizeof(u64), bits.data(),
                                    count * sizeof(u64))) return -1;
        for (u64 j = 0; j < count; ++j) free += std::popcount(bits[j]);
        i += count;
    }
    // Separate safe backing reads must not accidentally combine allocations
    // from opposite sides of a concurrent unmap/remap or allocator reset.
    std::array<u64, 3> again{};
    if (!memory->TryReadBacking(metadata, again.data(), sizeof(again)) || again != meta ||
        memory->MappingGeneration() != mapping.generation) {
        return -1;
    }
    free = std::min(free, pages);
    if (sample) *sample = {mapping.address + PoolOffset, bitmap, mapping.physical,
                          words, pages, free};
    return static_cast<int>(free * 100 / pages);
}
'''


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise RuntimeError(f"SotC LOD pool drift ({label}): {text.count(old)}")
    return text.replace(old, new, 1)


def apply(root):
    src = Path(root) / "src"
    memory_h = src / "core/memory.h"
    memory_cpp = src / "core/memory.cpp"
    lod_h = src / "video_core/sotc_lod_stats.h"
    h = replace_once(memory_h.read_text(), "    bool TryReadBacking(VAddr address, void* data, u64 size);",
                     TAIL_DECL + "    bool TryReadBacking(VAddr address, void* data, u64 size);",
                     "physical tail query declaration")
    cpp = replace_once(memory_cpp.read_text(), "void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {",
                       TAIL_QUERY + "void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {",
                       "physical tail query implementation")
    lod = lod_h.read_text()
    first = lod.index("inline int PoolFreePercent(")
    last = lod.index("inline void Collect(", first)
    lod = lod[:first] + POOL_READER + lod[last:]
    lod = replace_once(lod, '#include "common/elf_info.h"',
                       '#include "common/elf_info.h"\n#include "common/logging/log.h"',
                       "compact pool evidence dependency")
    lod = replace_once(lod, "    static u64 coarser{};", """    static u64 coarser{};
    static VAddr reported_pool{};
    static int reported_status = -2;""", "pool report state")
    lod = replace_once(lod, "        const int free=PoolFreePercent(memory);", """        PoolSample sample{};
        const int free=PoolFreePercent(memory, &sample);
        const u64 previous_coarser = coarser;""", "resolved pool sample")
    lod = replace_once(lod, """            coarser=want;
        }
    }
    for(u32 i=0;i<256;++i) {""", """            coarser=want;
        }
        const int status = free < 0 ? -1 : 0;
        if (reported_status != status || reported_pool != sample.pool ||
            previous_coarser != coarser) {
            LOG_INFO(Render_Vulkan,
                     "BACHATA_SOTC_LOD_POOL status={} pool={:#x} physical={:#x} "
                     "bitmap={:#x} words={} pages={} free={} percent={} mip={}",
                     status, sample.pool, sample.physical, sample.bitmap, sample.words,
                     sample.pages, sample.free, free, 2 + coarser);
            reported_status = status;
            reported_pool = sample.pool;
        }
    }
    for(u32 i=0;i<256;++i) {""", "transition-only evidence")
    memory_h.write_text(h)
    memory_cpp.write_text(cpp)
    lod_h.write_text(lod)
    return {
        "sotcLodPool": "physical-tail allocation + documented object offset, no fixed guest VA",
        "lifetime": "complete Direct physical span, backing reads, metadata and mapping generation",
        "policy": "unchanged donor defaults and hysteresis; unknown pool never means zero free",
        "evidence": "BACHATA_SOTC_LOD_POOL only on discovery/status/mip transitions",
    }
