#!/usr/bin/env python3
"""Optional GPU unmap and LDS barrier adaptations from tomasmosca/shadPS4-sotc.
Applied to zenithblue ARM64 source; never patch the shipped stripped ELF.
"""
from pathlib import Path
import argparse

def once(s, old, new, label):
    n=s.count(old)
    if n!=1:
        raise RuntimeError(f"{label}: expected one anchor, found {n}")
    return s.replace(old,new)

def patch(root):
    files=[
        root/"src/video_core/buffer_cache/buffer_cache.h",
        root/"src/video_core/buffer_cache/buffer_cache.cpp",
        root/"src/video_core/renderer_vulkan/vk_rasterizer.cpp",
        root/"src/shader_recompiler/ir/passes/shared_memory_barrier_pass.cpp",
    ]
    h,b,r,l=[p.read_text() for p in files]
    h=once(h,"    void InvalidateMemory(VAddr device_addr, u64 size);",
"""    void InvalidateMemory(VAddr device_addr, u64 size);
    // Drop stale GPU writes on SotC guest deallocation; not a regular readback.
    void DropGpuModifiedOnUnmap(VAddr device_addr, u64 size);""","buffer interface")
    b=once(b,"void BufferCache::ReadMemory(VAddr device_addr, u64 size, bool is_write) {",
"""void BufferCache::DropGpuModifiedOnUnmap(VAddr device_addr, u64 size) {
    if (size == 0) return;
    // Ordered on Liverpool's GPU command queue; no global change to readback mode.
    liverpool->SendCommand<true>([this, device_addr, size] {
        gpu_modified_ranges.Subtract(device_addr, size);
        memory_tracker->UnmarkRegionAsGpuModified(device_addr, size);
        memory_tracker->MarkRegionAsCpuModified(device_addr, size);
    });
}

void BufferCache::ReadMemory(VAddr device_addr, u64 size, bool is_write) {""","buffer implementation")
    r=once(r,
"""void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    buffer_cache.InvalidateMemory(addr, size);""",
"""void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    // Set only for Shadow of the Colossus; all other games retain their original
    // CPU/GPU consistency and precise readbacks.
    static const bool sotc_drop = [] {
        const char* v = std::getenv("BACHATA_SOTC_UNMAP_DROP");
        return v && v[0] == '1';
    }();
    if (sotc_drop) buffer_cache.DropGpuModifiedOnUnmap(addr, size);
    else buffer_cache.InvalidateMemory(addr, size);""","unmap gate")
    l=once(l,"#include <unordered_set>","#include <cstdlib>\n#include <unordered_set>","LDS std include")
    l=once(l,
"""    if (shared_memory_size == 0 || threadgroup_size != GcnSubgroupSize ||
        !profile.needs_lds_barriers) {""",
"""    static const bool sotc_large_lds = [] {
        const char* v = std::getenv("BACHATA_SOTC_LDS_LARGE_GROUPS");
        return v && v[0] == '1';
    }();
    const bool large_group = sotc_large_lds && threadgroup_size > GcnSubgroupSize;
    if (shared_memory_size == 0 || (threadgroup_size != GcnSubgroupSize && !large_group) ||
        !profile.needs_lds_barriers) {""","large LDS group gate")
    l=once(l,
"""        if (node.type == Type::Block && divergence_depth == 0) {
            EmitBarrierInBlock(node.data.block);
        }""",
"""        if (node.type == Type::Block && divergence_depth == 0 && !large_group) {
            EmitBarrierInBlock(node.data.block);
        }""","prevent divergent block barriers")
    for p,s in zip(files,[h,b,r,l]):p.write_text(s)
    print("PASS: guarded SotC GPU unmap + large group LDS merge barriers")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    patch(ap.parse_args().source)
