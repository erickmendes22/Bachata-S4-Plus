"""Exact FEX direct-memory release intervals and SotC reservation fast path.

The physical request end must never move when skipping a free hole. Likewise,
unmapping aliases must intersect the actual physical extent, not use the
request length starting at the alias base. The donor direct_release implements
that intersection. Fresh virtual reservations must not invalidate or drain a
GPU range that has never been registered. Preserve all real GPU overlaps.
"""
from pathlib import Path

HEADER = r'''#pragma once
#include <algorithm>
#include <cstdint>
#include <limits>

namespace BachataDmem {
using U64 = std::uint64_t;
struct Range { U64 begin{}, end{}; };
constexpr Range Intersect(U64 begin,U64 end,U64 base,U64 bytes) {
    if (begin>=end || bytes==0 || bytes>std::numeric_limits<U64>::max()-base) return {};
    const auto lo=std::max(begin,base),hi=std::min(end,base+bytes);
    return hi>lo?Range{lo,hi}:Range{};
}
// The map must cover the entire range with existing unmapped VMA records.
// Unknown/gap/overflow is NOT proof that no backing exists.
template<class Map>
bool EntirelyUnmapped(const Map& map,U64 addr,U64 size) {
    if(!size || size>std::numeric_limits<U64>::max()-addr) return false;
    const U64 end=addr+size;
    auto it=map.upper_bound(addr);
    if(it==map.begin()) return false;
    --it;
    while(addr<end && it!=map.end()) {
        const auto& area=it->second;
        if(addr<area.base || addr-area.base>=area.size || area.IsMapped() ||
           area.size>std::numeric_limits<U64>::max()-area.base) return false;
        addr=std::min(end,static_cast<U64>(area.base+area.size));
        ++it;
    }
    return addr==end;
}
}
'''

def once(s,a,b):
    if s.count(a)!=1: raise RuntimeError("exact DMEM anchor drift: "+a[:100])
    return s.replace(a,b,1)

def function(s,marker,transform):
    start=s.index(marker)
    opening=s.index("{",start)
    depth=1
    end=opening+1
    while depth:
        depth+=(s[end]=="{")-(s[end]=="}")
        end+=1
    return s[:start]+transform(s[start:end])+s[end:]

def apply(root:Path):
    root=Path(root)/"src"
    p=root/"core/memory.cpp"
    s=p.read_text()
    s='#include "core/bachata_dmem_ranges.h"\n'+s
    if '#include "common/elf_info.h"' not in s:
        s='#include "common/elf_info.h"\n'+s
    (root/"core/bachata_dmem_ranges.h").write_text(HEADER)
    def release(body):
        body=once(body,
            '    if (phys_addr > total_direct_size || (is_checked && phys_addr + size > total_direct_size)) {',
            '''    if (!size) return ORBIS_OK;
    if (phys_addr >= total_direct_size ||
        (is_checked && size > total_direct_size - phys_addr)) {''')
        body=once(body,'    // If this is a checked free, then all direct memory in range must be allocated.',
            '''    const PAddr request_end=phys_addr+std::min<u64>(size,total_direct_size-phys_addr);
    // If this is a checked free, then all direct memory in range must be allocated.''')
        a=body.index('    u64 remaining_size = size;')
        b=body.index('    // Release any dmem mappings that reference this physical block.',a)
        body=body[:a]+'''    auto phys_handle = FindDmemArea(phys_addr);
    for (; phys_handle != dmem_map.end() && phys_handle->second.base < request_end; ++phys_handle) {
        const auto& area=phys_handle->second;
        const auto overlap=BachataDmem::Intersect(phys_addr,request_end,area.base,area.size);
        if(overlap.begin==overlap.end) continue;
        if(area.dma_type==PhysicalMemoryType::Free) {
            if(is_checked) {
                LOG_ERROR(Kernel_Vmm, "Attempting to release a free dmem area");
                return ORBIS_KERNEL_ERROR_ENOENT;
            }
            continue;
        }
        free_list.emplace_back(overlap.begin,overlap.end-overlap.begin);
    }

'''+body[b:]
        a=body.index('            if (phys_addr + size > phys_mapping.base')
        b=body.index('            }\n',a)+len('            }\n')
        body=body[:a]+'''            const auto overlap=BachataDmem::Intersect(
                phys_addr,request_end,phys_mapping.base,phys_mapping.size);
            if(overlap.begin!=overlap.end) {
                const VAddr addr_in_vma=mapping.base+offset_in_vma+overlap.begin-phys_mapping.base;
                remove_list.emplace_back(addr_in_vma,overlap.end-overlap.begin);
            }
'''+body[b:]
        return body
    s=function(s,'s32 MemoryManager::Free(',release)
    # Use both the VMA map and the renderer's actual registration set.
    # PRT / partial overlaps keep the normal invalidation and fence path.
    def avoid_empty_gpu_unmap(body):
        return once(body,'''    if (IsValidGpuMapping(virtual_addr, size)) {
        rasterizer->UnmapMemory(virtual_addr, size);
    }''','''    if (IsValidGpuMapping(virtual_addr, size)) {
        bool skip_unmapped=false;
        const auto serial=Common::ElfInfo::Instance().GameSerial();
        if(serial=="CUSA08809"||serial=="CUSA08034") {
            std::shared_lock read_lock{mutex};
            skip_unmapped=BachataDmem::EntirelyUnmapped(vma_map,virtual_addr,size);
        }
        if(!skip_unmapped || rasterizer->HasMappedOverlap(virtual_addr,size)) {
            rasterizer->UnmapMemory(virtual_addr, size);
        }
    }''')
    s=function(s,'s32 MemoryManager::MapMemory(',avoid_empty_gpu_unmap)
    s=function(s,'s32 MemoryManager::UnmapMemory(',avoid_empty_gpu_unmap)
    p.write_text(s)
    h=root/"video_core/renderer_vulkan/vk_rasterizer.h"
    h.write_text(once(h.read_text(),"    bool IsMapped(VAddr addr, u64 size);",
        "    bool IsMapped(VAddr addr, u64 size);\n    bool HasMappedOverlap(VAddr addr, u64 size);"))
    r=root/"video_core/renderer_vulkan/vk_rasterizer.cpp"
    r.write_text(once(r.read_text(),"bool Rasterizer::IsMapped(VAddr addr, u64 size) {",
        '''bool Rasterizer::HasMappedOverlap(VAddr addr, u64 size) {
    if(!size || size>std::numeric_limits<u64>::max()-addr) return true;
    const auto range=decltype(mapped_ranges)::interval_type::right_open(addr,addr+size);
    Common::RecursiveSharedLock lock{mapped_ranges_mutex};
    return boost::icl::intersects(mapped_ranges,range);
}

bool Rasterizer::IsMapped(VAddr addr, u64 size) {'''))
    print("BACHATA_DMEM_EXACT_RANGE / SOTC_EMPTY_GPU_UNMAP applied")
    return {"physical_free":"bounded intersection; holes never extend request; checked errors unchanged",
            "aliases":"exact overlap only",
            "sotc":"skip GPU invalidation only for completely unmapped VMA plus no renderer overlap",
            "preserved":"real mapping, partial overlap, PRT, GPU synchronization and FEX"}
