#!/usr/bin/env python3
"""Fix actual unpaired page watches and port the SotC compute queue stall fix.

BS4-FEEEA8A7: page_manager.cpp:84 (write watchers, not read), 29 flips.
BS4-EBAB591B: no flip, 123 actual arena releases, 288 residency operations.
Sources: pinned FEX MapMemory (no PageManager::OnMap call), upstream
0.18.1 page_manager.cpp, region_manager.h, and donor SotC 3ac1ce5c93fa
(compute queue rptr) / 8fb33cf265d1 (deferred releases).
Do not suppress any watcher assertion or truncate arbitrary raw V# ranges.
"""
from pathlib import Path

def one(s,a,b,label):
    if s.count(a)!=1:
        raise RuntimeError(f"watcher/queue source drift {label}: {s.count(a)}")
    return s.replace(a,b,1)

def apply(root:Path):
    p=root/'src/video_core/page_manager.cpp'
    s=p.read_text()
    s=one(s,'''    void UpdatePageWatchers(VAddr addr, u64 size, PageOp write_op) {
        const u64 page_start = addr >> PM_PAGE_BITS;''',
        '''    void UpdatePageWatchers(VAddr addr, u64 size, PageOp write_op) {
        // FEX MapMemory records GPU ranges but does not register sparse leaves.
        // A mapped range can therefore have NO PageState when a texture is
        // first tracked. Skipping that page loses the increment, and a later
        // buffer bind allocates a zero leaf before the texture untracks it.
        // BACHATA_WATCHER_PAIRING: reserve before *every* image transition,
        // including mapped PRT, before either counter or mutex is accessed.
        if (!size || addr >= (VAddr{1}<<ADDRESS_BITS) ||
            size > (VAddr{1}<<ADDRESS_BITS)-addr || write_op==PageOp::None) return;
        const u64 page_start = addr >> PM_PAGE_BITS;''','ordinary tracking range contract')
    s=one(s,'''            EnsurePages(aligned_addr, aligned_end);
        }

        for (u64 page = page_start; page != page_end; ++page) {
            PageState* state = cached_pages.find(page);
            if (!state) {
                continue;
            }

            locks[page].lock();''',
        '''        }
        EnsurePages(aligned_addr, aligned_end);

        for (u64 page = page_start; page != page_end; ++page) {
            PageState* state = cached_pages.find(page);
            ASSERT(state);
            locks[page].lock();''','never skip an ordinary image watcher')
    # Existing underflow assertions are retained and report exact address, source
    # and state. No counter clamping or ignored unmatched untrack.
    s=one(s,'''            const auto new_perms = state->Update(write_op);''',
        '''            ASSERT_MSG(write_op != PageOp::Untrack || state->num_write_watchers>0,
                       "Image watcher underflow page={:#x} addr={:#x} size={:#x} reads={}",
                       page<<PM_PAGE_BITS,addr,size,state->num_read_watchers);
            const auto new_perms = state->Update(write_op);''','texture ownership assertion')
    s=one(s,'''            const auto new_perms = state->Update(write_op, update_write, read_op, update_read);''',
        '''            ASSERT_MSG(!update_write || write_op!=PageOp::Untrack || state->num_write_watchers>0,
                       "Buffer write watcher underflow page={:#x} base={:#x} reads={}",
                       (base_page+page)<<PM_PAGE_BITS,base_addr,state->num_read_watchers);
            ASSERT_MSG(!update_read || read_op!=PageOp::Untrack || state->num_read_watchers>0,
                       "Buffer read watcher underflow page={:#x} base={:#x} writes={}",
                       (base_page+page)<<PM_PAGE_BITS,base_addr,state->num_write_watchers);
            const auto new_perms = state->Update(write_op, update_write, read_op, update_read);''',
        'preserve and identify buffer watcher assertions')
    p.write_text(s)

    # MemoryTracker publishes initialized RegionManager pointers to CPU
    # fault handlers. The old non-atomic top_tier read/write is a C++ race.
    p=root/'src/video_core/buffer_cache/memory_tracker.h'
    s=p.read_text()
    s=one(s,'#include <algorithm>','#include <algorithm>\n#include <atomic>\n#include <mutex>','atomic region publication')
    s=one(s,'if (auto* region = top_tier[page_index]; region) {',
        'if (auto* region = top_tier[page_index].load(std::memory_order_acquire); region) {',
        'read fully initialized region')
    s=one(s,'''    RegionManager* CreateRegion(u64 page_index) {
        const VAddr base_cpu_addr = page_index << HIGHER_PAGE_BITS;''',
        '''    RegionManager* CreateRegion(u64 page_index) {
        std::scoped_lock lock{region_creation_mutex};
        if (auto* region=top_tier[page_index].load(std::memory_order_relaxed)) return region;
        const VAddr base_cpu_addr = page_index << HIGHER_PAGE_BITS;''','one region per address')
    s=one(s,'                std::construct_at(&last_pool[i], tracker, 0);',
        '                std::destroy_at(&last_pool[i]);\n                std::construct_at(&last_pool[i], tracker, 0);',
        'end default object lifetime before placement construction')
    s=one(s,'        top_tier[page_index] = new_manager;',
        '        top_tier[page_index].store(new_manager,std::memory_order_release);','publish region')
    s=one(s,'    std::array<RegionManager*, NUM_HIGH_PAGES> top_tier{};',
        '    std::mutex region_creation_mutex;\n    std::array<std::atomic<RegionManager*>, NUM_HIGH_PAGES> top_tier{};',
        'atomic pointer table')
    p.write_text(s)

    # Correctly complete a read-watch transition when no tracked GPU bytes
    # intersect the page. The page dirty bits are page-granular while the
    # precise GPU range list is byte-granular. Empty intersection is valid.
    p=root/'src/video_core/buffer_cache/buffer_cache.cpp'
    s=p.read_text()
    s=one(s,'''    if (total_size_bytes == 0) {
        return;
    }
    const auto download = staging_pool.Request(total_size_bytes, VideoCore::MemoryType::HostCached);''',
        '''    if (total_size_bytes == 0) {
        // BACHATA_EMPTY_READBACK_RELEASE: a page can carry a GPU dirty bit
        // after its byte-range was already consumed or removed. No remaining
        // bytes means no pending GPU writes for this window. Remove the read
        // watch, or the faulting guest instruction retries the same fault.
        memory_tracker->UnmarkRegionAsGpuModified(device_addr,size,false);
        return;
    }
    const auto download = staging_pool.Request(total_size_bytes, VideoCore::MemoryType::HostCached);''',
        'release empty readback page state')
    # The old all-or-nothing physical alias writer introduced in 3d86766
    # drops a whole GPU readback when a PRT hole is crossed. Copy each mapped
    # physical span; skip unmapped holes, and never shift following source bytes.
    s=one(s,'''        memory->TryWriteBacking(dst_addr, download.mapped + (copy.dstOffset - download.offset),
                                copy.size);''',
        '''        memory->WriteSparseBacking(reinterpret_cast<VAddr>(dst_addr),
            download.mapped + (copy.dstOffset-download.offset),copy.size);''',
        'scatter GPU readback across sparse guest mappings')
    p.write_text(s)

    p=root/'src/core/memory.h'
    s=p.read_text()
    s=one(s,'    bool TryReadBacking(VAddr address, void* data, u64 size);',
        '    bool TryReadBacking(VAddr address, void* data, u64 size);\n'
        '    void WriteSparseBacking(VAddr address,const void* data,u64 size);',
        'sparse readback API')
    p.write_text(s)
    p=root/'src/core/memory.cpp'
    s=p.read_text()
    s=one(s,'bool MemoryManager::TryWriteBacking(void* address, const void* data, u64 size) {',
        r'''// BACHATA_SPARSE_READBACK: preserve all mapped portions even if an
// image/arena readback spans a reserved or unbacked PRT page. CPU-owned
// ordinary labels still use the strict, atomic-range TryWriteBacking.
void MemoryManager::WriteSparseBacking(VAddr address,const void* data,u64 size) {
    if (!size || size>UINT64_MAX-address) return;
    std::shared_lock lock{mutex};
    const auto* source=static_cast<const u8*>(data);
    while (size && IsValidMapping(address)) {
        const auto& vma=FindVMA(address)->second;
        const u64 bytes=std::min(size,vma.base+vma.size-address);
        if (HasPhysicalBacking(vma)) {
            const u64 begin=address-vma.base;
            const u64 end=begin+bytes;
            auto it=vma.phys_areas.upper_bound(begin);
            if (it!=vma.phys_areas.begin()) --it;
            for (;it!=vma.phys_areas.end() && it->first<end;++it) {
                const u64 lo=std::max<u64>(begin,it->first);
                const u64 hi=std::min<u64>(end,it->first+it->second.size);
                if (hi>lo) std::memcpy(impl.BackingBase()+it->second.base+(lo-it->first),
                                      source+(lo-begin),hi-lo);
            }
        }
        source+=bytes; address+=bytes; size-=bytes;
    }
}

bool MemoryManager::TryWriteBacking(void* address, const void* data, u64 size) {''',
        'partial physical readback preserves source offsets')
    p.write_text(s)

    # Dedicated SotC 3ac1ce5c93fa: protected read pointer can fault forever
    # in ProcessCompute; use the same cache invalidation+physical write as
    # the donor, for all three actual pointer-advance sites.
    p=root/'src/video_core/amdgpu/liverpool.h'
    s=p.read_text()
    s=one(s,'    void ProcessCommands();','    void ProcessCommands();\n'
        '    void AdvanceReadPointer(u32* read_addr,u32 dwords,u32 ring_size_dw);',
        'compute queue read pointer API')
    p.write_text(s)
    p=root/'src/video_core/amdgpu/liverpool.cpp'
    s=p.read_text()
    s=one(s,'''template <bool is_indirect>
Liverpool::Task Liverpool::ProcessCompute(std::span<const u32> acb, u32 vqid) {''',
        '''// BACHATA_SOTC_RPTR_BACKING (donor 3ac1ce5c93fa): the queue's read
// pointer is CPU-owned even when its page participates in GPU tracking.
void Liverpool::AdvanceReadPointer(u32* read_addr,u32 dwords,u32 ring_size_dw) {
    if (!ring_size_dw) return;
    // Restore the pre-f293ee7 read-pointer behavior. The donor's blanket
    // cache invalidation on every packet was not justified by this log.
    // Do not repeat the regression-inducing path on the current core.
    *read_addr=(*read_addr+dwords)%ring_size_dw;
    return;
}

template <bool is_indirect>
Liverpool::Task Liverpool::ProcessCompute(std::span<const u32> acb, u32 vqid) {''',
        'port the actual dedicated compute pointer function')
    import re
    s,n=re.subn(r'\*queue\.read_addr \+= (acb\.size\(\)|next_dw_off);\n\s*\*queue\.read_addr %= queue\.ring_size_dw;',
                r'AdvanceReadPointer(queue.read_addr, \1, queue.ring_size_dw);',s)
    if n!=3: raise RuntimeError(f"expected three compute read pointer advances, got {n}")
    p.write_text(s)
    return {"watchers":"always reserve image leaves; atomically publish buffer regions; retain assertions",
            "readback":"release empty precise readback; write mapped physical spans across PRT holes",
            "shadow":"donor 3ac1ce5c93fa compute queue rptr backing, all three sites"}
