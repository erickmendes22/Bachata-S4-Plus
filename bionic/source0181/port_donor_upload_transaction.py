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
    t=one(t,'''    void ForEachUploadRange(VAddr cpu_addr, u64 size, bool is_written, auto&& func) {
        IteratePages<true>(
            cpu_addr, size, [&func, is_written](RegionManager* manager, u64 offset, u64 size) {
                if (is_written) {
                    manager->template ForEachModifiedRange<Type::CPU, StateOp::Clear, StateOp::Set>(
                        offset, size, func);
                } else {
                    manager
                        ->template ForEachModifiedRange<Type::CPU, StateOp::Clear, StateOp::None>(
                            offset, size, func);
                }
            });
    }''',
    '''    // BACHATA_UPLOAD_BEFORE_GPU_READ_PROTECT: dedicated ports preserve this
    // transaction because the FEX host reads guest VMAs, unlike upstream's
    // separate physical backing table.
    void ForEachUploadRange(VAddr cpu_addr, u64 size, bool is_written, auto&& func,
                            auto&& on_upload) {
        // Lock each touched write-region until the CPU snapshot is complete.
        // RAII also releases locks on an exceptional staging allocation.
        struct PendingWrite {
            RegionManager* manager;
            u64 offset;
            u64 size;
            Bounds bounds;
            PendingWrite(RegionManager* m,u64 o,u64 n)
                : manager(m),offset(o),size(n),bounds(m->GetBounds(o,n)) {
                manager->Lock(bounds);
            }
            ~PendingWrite() { manager->Unlock(bounds); }
            PendingWrite(const PendingWrite&)=delete;
            PendingWrite& operator=(const PendingWrite&)=delete;
        };
        std::deque<PendingWrite> writes;
        IteratePages<true>(
            cpu_addr,size,[&](RegionManager* manager,u64 offset,u64 bytes) {
                if (is_written) {
                    writes.emplace_back(manager,offset,bytes);
                    // Clear CPU dirty bits and protect CPU writes, but do NOT
                    // set GPU dirty/read protection until actual upload.
                    manager->template ForEachModifiedRange<Type::CPU,StateOp::Clear,
                                                           StateOp::None,false>(offset,bytes,func);
                } else {
                    manager->template ForEachModifiedRange<Type::CPU,StateOp::Clear,
                                                           StateOp::None>(offset,bytes,func);
                }
            });
        on_upload();
        for (auto& write : writes) {
            write.manager->template ChangeRegionState<StateOp::None,StateOp::Set,false>(
                write.offset,write.size);
        }
    }''','two phase upload and protected write publication')
    c=one(c,'''    memory_tracker->ForEachUploadRange(device_addr, size, is_written, [&](u64 addr, u64 size) {
        copies.emplace_back(total_size_bytes, addr, size);
        total_size_bytes += size;
    });
    if (!copies.empty()) {
        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);
        for (auto& copy : copies) {
            memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);
            copy.srcOffset += staging.offset;
            copy.dstOffset -= arena->cpu_addr;
        }
        staging.Flush();
        runtime.CopyBuffer(staging.buffer, arena, copies);
    }''',
    '''    const Buffer* source_buffer{};
    memory_tracker->ForEachUploadRange(device_addr,size,is_written,
        [&](u64 addr,u64 bytes) {
            copies.emplace_back(total_size_bytes,addr,bytes);
            total_size_bytes+=bytes;
        },
        [&] {
            if (copies.empty()) return;
            const auto staging=staging_pool.Request(total_size_bytes,MemoryType::HostUncached);
            for (auto& copy : copies) {
                memory->CopySparseMemory(copy.dstOffset,staging.mapped+copy.srcOffset,copy.size);
                copy.srcOffset+=staging.offset;
                copy.dstOffset-=arena->cpu_addr;
            }
            staging.Flush();
            source_buffer=staging.buffer;
        });
    // Region locks are released before recording Vulkan work. The staging
    // pool holds the snapshot until this GPU tick completes.
    if (source_buffer) runtime.CopyBuffer(source_buffer,arena,copies);''',
    'stage bytes before publishing GPU dirty state')
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
        "donor":"both dedicated ports, upload before GPU protection",
        "regression_removed":"1997f14 permission override, image guards, range clamps, staging waits",
        "order":"snapshot then GPU dirty/read protect, stable sparse region watcher pairing",
    }
