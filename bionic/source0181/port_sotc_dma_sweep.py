"""SotC donor DMA residency-version and dirty-word sweep.

Adapt the actual 732cb37+0366868 effective renderer to the existing
atomic FEX MemoryTracker. Do not import donor fault-grace or write-ahead
until their guest-fault semantics are validated independently.
"""
from pathlib import Path

def apply(root:Path):
    v=root/"src/video_core/buffer_cache"
    def edit(name,a,b,n=1):
        p=v/name;s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"SotC DMA sweep {name}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    edit("region_manager.h","    static constexpr Bounds GetBounds(u64 offset, u64 size) {",
         """    // Each CPU-dirty transition marks its 256 KiB word. Exchange
    // hands ownership of the pending sweep bits to the GPU command owner.
    u64 TakeSweepWords() noexcept {
        return sweep_words.exchange(0,std::memory_order_acq_rel);
    }
    VAddr CpuAddress() const noexcept { return cpu_addr; }

    static constexpr Bounds GetBounds(u64 offset, u64 size) {""")
    edit("region_manager.h","        cpu_addr = new_cpu_addr;","        cpu_addr = new_cpu_addr;\n        sweep_words.store(~u64{0},std::memory_order_relaxed);")
    edit("region_manager.h","                write_prot[index]=~prev & mask;",
         """                write_prot[index]=~prev & mask;
                if (write_prot[index])
                    sweep_words.fetch_or(u64{1}<<index,std::memory_order_release);""")
    edit("region_manager.h","    RegionBits cpu;\n    RegionBits gpu;",
         "    RegionBits cpu;\n    RegionBits gpu;\n    std::atomic<u64> sweep_words{~u64{0}};")
    edit("memory_tracker.h","    /// Call 'func' for each GPU modified range",
         """    // The allocated-region list is published under the existing creation
    // mutex. No GPU work or reentrant tracker call may occur in the callback.
    template<class F> void ForEachSweepSpan(F&& fn) {
        std::scoped_lock guard{region_creation_mutex};
        for (auto* manager:live_managers) {
            u64 words=manager->TakeSweepWords();
            while(words) {
                const unsigned first=std::countr_zero(words);
                const unsigned count=std::countr_one(words>>first);
                fn(manager->CpuAddress()+u64(first)*BYTES_PER_WORD,
                   u64(count)*BYTES_PER_WORD);
                words=first+count>=64?0:words&(~u64{0}<<(first+count));
            }
        }
    }

    /// Call 'func' for each GPU modified range""")
    edit("memory_tracker.h","        top_tier[page_index].store(new_manager,std::memory_order_release);",
         """        live_managers.push_back(new_manager);
        top_tier[page_index].store(new_manager,std::memory_order_release);""")
    edit("memory_tracker.h","    std::mutex region_creation_mutex;",
         "    std::mutex region_creation_mutex;\n    std::vector<RegionManager*> live_managers;")
    edit("buffer_cache.h","    IntervalList<Backing> resident_ranges;",
         """    IntervalList<Backing> resident_ranges;
    u64 resident_version{};
    u64 dma_runs_version=~u64{0};
    size_t dma_runs_arenas{};
    std::vector<std::pair<VAddr,u64>> dma_runs;
    std::vector<std::pair<VAddr,u64>> dma_spans;""")
    edit("buffer_cache.cpp","        resident_ranges.Add(backing);",
         "        resident_ranges.Add(backing);\n        ++resident_version;")
    edit("buffer_cache.cpp","    resident_ranges=std::move(retained);",
         "    resident_ranges=std::move(retained);\n    ++resident_version;")
    old="""void BufferCache::SynchronizeDmaBuffers() {
    fault_process_pending = true;
    for (const auto& range : resident_ranges) {
        const u64 page = range.start >> (ARENA_PAGE_BITS - block_shift);
        const VAddr device_addr = range.start << block_shift;
        const u64 size = (range.end - range.start) << block_shift;
        SynchronizeMemory(address_space[page], device_addr, size, false, false);
    }
}"""
    edit("buffer_cache.cpp",old,r'''void BufferCache::SynchronizeDmaBuffers() {
    fault_process_pending = true;
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if (serial!="CUSA08809" && serial!="CUSA08034") {
        for (const auto& range : resident_ranges) {
            const u64 page = range.start >> (ARENA_PAGE_BITS - block_shift);
            const VAddr device_addr = range.start << block_shift;
            const u64 size = (range.end - range.start) << block_shift;
            SynchronizeMemory(address_space[page], device_addr, size, false, false);
        }
        return;
    }
    // Same resident bytes, same arena, bounded merged runs. A changed
    // resident set must always see old CPU dirty bits, even if their
    // dirty-word notifications were consumed while nonresident.
    const bool full=dma_runs_version!=resident_version || dma_runs_arenas!=arenas.size();
    if(full) {
        dma_runs_version=resident_version;
        dma_runs_arenas=arenas.size();
        dma_runs.clear();
        constexpr u64 cap=16_MB;
        for(const auto& range:resident_ranges) {
            const VAddr addr=range.start<<block_shift;
            const u64 size=(range.end-range.start)<<block_shift;
            if(!dma_runs.empty()) {
                auto& run=dma_runs.back();
                if(run.first+run.second==addr && run.second<=cap &&
                   size<=cap-run.second &&
                   address_space[run.first>>ARENA_PAGE_BITS]==address_space[addr>>ARENA_PAGE_BITS]) {
                    run.second+=size;
                    continue;
                }
            }
            dma_runs.emplace_back(addr,size);
        }
    }
    dma_spans.clear();
    memory_tracker->ForEachSweepSpan([&](VAddr addr,u64 size) {
        if(!full) dma_spans.emplace_back(addr,size);
    });
    if(full) {
        for(const auto& [addr,size]:dma_runs)
            SynchronizeMemory(address_space[addr>>ARENA_PAGE_BITS],addr,size,false,false);
        return;
    }
    std::ranges::sort(dma_spans);
    size_t first=0;
    for(const auto& [addr,size]:dma_runs) {
        const auto end=addr+size;
        while(first<dma_spans.size() &&
              dma_spans[first].first+dma_spans[first].second<=addr) ++first;
        if(first==dma_spans.size()) break;
        VAddr lo=~u64{0},hi=0;
        for(size_t k=first;k<dma_spans.size()&&dma_spans[k].first<end;++k) {
            lo=std::min(lo,std::max(addr,dma_spans[k].first));
            hi=std::max(hi,std::min(end,dma_spans[k].first+dma_spans[k].second));
        }
        if(lo<hi) SynchronizeMemory(address_space[addr>>ARENA_PAGE_BITS],lo,hi-lo,false,false);
    }
}''')
    return {"resident_invalidation":"both add and release, arena migration",
            "dma_merge":"adjacent same-arena spans <=16MiB",
            "dirty_sweep":"atomic 256KiB notification, full on residency change",
            "other_titles":"original full sweep","cpu":"FEX","fps":"unchanged"}
