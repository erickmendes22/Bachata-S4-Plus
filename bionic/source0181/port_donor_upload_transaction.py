#!/usr/bin/env python3
"""Port the dedicated games' upload-before-GPU-protection transaction.

References: ShadowOfTheColossus-Android-Aot@6556a9f and
gow3_android_daedalus_fork@524e74a, buffer_cache/{memory_tracker.h,buffer_cache.cpp}.
Unlike the upstream 0.18.1 MemoryManager, the retained FEX ARM64
CopySparseMemory reads the guest VMA directly under the VMM shared lock.
Enabling GPU read protection before that copy can fault back into the
same cache from its own GPU worker. Preserve the donor order and keep
RegionManager locks across the CPU snapshot, not across Vulkan recording.

Do not reintroduce the other 1997f14 changes (permission policy, storage
clamps, image null overrides, or chunked upload scheduler waits).
"""
from pathlib import Path

def one(s,a,b,label):
    if s.count(a)!=1:
        raise RuntimeError(f"upload transaction source drift {label}: {s.count(a)}")
    return s.replace(a,b,1)

def apply(root: Path):
    tracker=root/'src/video_core/buffer_cache/memory_tracker.h'
    cache=root/'src/video_core/buffer_cache/buffer_cache.cpp'
    page=root/'src/video_core/page_manager.cpp'
    t=tracker.read_text()
    c=cache.read_text()
    p=page.read_text()
    # Keep the tested permission policy. Pair the sparse leaf bookkeeping
    # only now that the upload cannot read a freshly GPU-protected page.
    p=one(p,'#include <algorithm>','#include <algorithm>\n#include <mutex>','reservation mutex include')
    p=one(p,'''        end = std::min(end, VAddr{1} << ADDRESS_BITS) - 1;
        const size_t start_page = begin >> PM_PAGE_BITS;''',
        '''        end = std::min(end, VAddr{1} << ADDRESS_BITS);
        if (begin >= end) return;
        std::scoped_lock guard{page_reservation_mutex};
        --end;
        const size_t start_page = begin >> PM_PAGE_BITS;''','serialized allocation of watcher leaves')
    p=one(p,'    Common::MultiLevelPageTable<PageTraits> cached_pages;',
        '    std::mutex page_reservation_mutex;\n    Common::MultiLevelPageTable<PageTraits> cached_pages;',
        'reservation mutex member')
    p=one(p,'''        const u64 page_end = bounds.end_word * PAGES_PER_WORD + bounds.end_page + 1;

        Core::MemoryPermission perms{};''',
        '''        const u64 page_end = bounds.end_word * PAGES_PER_WORD + bounds.end_page + 1;
        // A RegionManager dirty bit transition must have a matching PageState.
        // The dedicated ports preallocate all leaves; here allocate on demand.
        if (page_start >= page_end || base_page + page_end > NUM_ADDRESS_PAGES) return;
        EnsurePages((base_page+page_start)<<PM_PAGE_BITS,
                    (base_page+page_end)<<PM_PAGE_BITS);

        Core::MemoryPermission perms{};''','pair region tracking before the first transition')
    p=one(p,'''            PageState* state = cached_pages.find(base_page + page);
            if (!state) {
                continue;
            }

            locks[base_page + page].lock();''',
        '''            PageState* state = cached_pages.find(base_page + page);
            ASSERT(state);
            locks[base_page + page].lock();''','no silently dropped region transitions')
    # Ordinary image tracking retains its existing semantics; do not change
    # read/write permission calculation or add a new global image filter.
    for f,s in ((tracker,t),(cache,c),(page,p)):
        f.write_text(s)
    return {
        "donor":"both dedicated ports, physical backing alias via follow-up",
        "regression_removed":"1997f14 permission override, image guards, range clamps, staging waits",
        "order":"stable sparse region watcher pairing; direct physical alias bypasses guest protection",
    }
