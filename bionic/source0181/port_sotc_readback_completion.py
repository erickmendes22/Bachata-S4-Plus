#!/usr/bin/env python3
"""Complete the active SotC readback contracts on the retained Bionic/FEX core.

Reference: SotC effective 732cb37d, GatherDownloads/ApplyDownloads and
FinishAsyncReadback. Default hot mode is 1, partial completion is enabled;
deferred sparse release is explicitly OFF and is not enabled here.
Guest backing writes retain the existing FEX physical mapping API.
"""
from pathlib import Path


def apply(root):
    root = Path(root)
    base = root / "src/video_core/buffer_cache"

    def edit(path, old, new):
        text = path.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"SotC readback completion {path.name}: expected one {old[:100]!r}")
        path.write_text(text.replace(old, new, 1))

    header = base / "buffer_cache.h"
    edit(header, "#include <deque>", "#include <deque>\n#include <chrono>")
    edit(header, """    struct AsyncReadback {
        BachataReadback::Pending validity{};
        const Buffer* arena{};
        std::vector<vk::BufferCopy> copies;
        Vulkan::StagingBufferRef staging{};
        u64 tick{};
    };""", """    struct ReadbackItem {
        BachataReadback::Pending validity{};
        const Buffer* arena{};
        std::vector<vk::BufferCopy> copies;
        std::vector<BachataReadback::Span> gpu_ranges;
        bool hot{};
    };
    struct AsyncReadback {
        BachataReadback::Pending validity{};
        const Buffer* arena{};
        std::vector<ReadbackItem> items;
        Vulkan::StagingBufferRef staging{};
        u64 tick{};
    };
    struct HotReadback {
        BachataReadback::Span span{};
        std::chrono::steady_clock::time_point last_request{};
    };
    std::vector<HotReadback> hot_readbacks;
    void GatherReadbackItem(AsyncReadback& rb,const Buffer* arena,
                            BachataReadback::Span span,bool hot,u64& bytes);
    void GatherHotReadbacks(AsyncReadback& rb,u64& bytes);
    void ClearEmptyReadback(BachataReadback::Span span);""")

    tracker = base / "memory_tracker.h"
    edit(tracker, "    /// Mark region as modified from the CPU", r"""    /// Apply speculative GPU data only while the guest has not written the page.
    /// Check and physical-backing copy share the region lock. A FEX write fault
    /// waits for that lock, so the guest's newer bytes always land last.
    template <typename Func>
    u64 WriteUnlessCpuModified(VAddr cpu_addr,u64 size,Func&& write) {
        if(!size || cpu_addr >= (1ULL<<MAX_CPU_PAGE_BITS) ||
           size > (1ULL<<MAX_CPU_PAGE_BITS)-cpu_addr) return size;
        u64 skipped=0;
        u64 page_index=cpu_addr>>HIGHER_PAGE_BITS;
        u64 offset=cpu_addr&HIGHER_PAGE_MASK;
        for(u64 remaining=size;remaining; ++page_index,offset=0) {
            const u64 length=std::min(HIGHER_PAGE_SIZE-offset,remaining);
            const VAddr base=page_index<<HIGHER_PAGE_BITS;
            remaining-=length;
            auto* manager=top_tier[page_index].load(std::memory_order_acquire);
            if(!manager) { write(base+offset,length);continue; }
            const auto bounds=manager->GetBounds(offset,length);
            manager->Lock(bounds);
            const u64 end=offset+length;
            u64 run=offset;
            for(u64 page=offset;page<end;) {
                const auto next=std::min((page&~(BYTES_PER_PAGE-1))+BYTES_PER_PAGE,end);
                if(manager->template IsRegionModified<Type::CPU>(page,next-page)) {
                    if(page>run)write(base+run,page-run);
                    run=next;
                    skipped+=next-page;
                }
                page=next;
            }
            if(end>run)write(base+run,end-run);
            manager->Unlock(bounds);
        }
        return skipped;
    }

    /// Mark region as modified from the CPU""")

    source = base / "buffer_cache.cpp"
    edit(source, "    for(auto* readback:inflight_readbacks)readback->validity.Mark({addr,addr+size});",
         """    for(auto* readback:inflight_readbacks) {
        readback->validity.Mark({addr,addr+size});
        for(auto& item:readback->items)item.validity.Mark({addr,addr+size});
    }""")
    text = source.read_text()
    start = text.index("void BufferCache::BeginAsyncReadback(")
    end = text.index("void BufferCache::ReadMemory(", start)
    text = text[:start] + READBACK_IMPLEMENTATION + text[end:]
    source.write_text(text)

    # The GPU-side synchronous path must use the same resident filtering,
    # held staging, late CPU check and publication order as the default path.
    edit(source, """void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {
    MarkReadbacksDirty(device_addr,size);""", """void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if(serial=="CUSA08809" || serial=="CUSA08034") {
        // A callback during Flush can invalidate a snapshot. Keep the requested
        // pages protected and retry; never let an SRT read see stale backing.
        for(;;) {
            AsyncReadback rb{};
            BeginAsyncReadback(rb,device_addr,size,0);
            if(!rb.tick)return;
            scheduler.WaitSubmitted(rb.tick,false);
            scheduler.GetWorkSemaphore()->Wait(rb.tick);
            if(FinishAsyncReadback(rb))return;
        }
    }
    MarkReadbacksDirty(device_addr,size);""")
    edit(source, """    MarkReadbacksDirty(first<<block_shift,(end-first)<<block_shift);
    boost::container::small_vector<Backing,16> released;""", """    MarkReadbacksDirty(first<<block_shift,(end-first)<<block_shift);
    const BachataReadback::Span released_span{first<<block_shift,end<<block_shift};
    std::erase_if(hot_readbacks,[&](const HotReadback& hot){
        return hot.span.Overlaps(released_span);
    });
    boost::container::small_vector<Backing,16> released;""")

    return {
        "donor": "SotC effective 732cb37d GatherDownloads/ApplyDownloads/FinishAsyncReadback",
        "hotReadback": "default mode 1, same resident arena, <=64KiB copied per hot item, TTL 2s",
        "lateCpuCheck": "atomic check/copy under the existing FEX RegionManager lock",
        "partialCompletion": "clean items applied; dirty hot items retained GPU-owned; requested window retried",
        "residentFilter": "both asynchronous and synchronous target paths intersect sparse resident ranges",
        "ownership": "held staging; backing copied before subtract/unprotect",
        "cpuBackend": "FEX unchanged",
        "deferredSparseRelease": "donor default off, unchanged",
        "coldEviction": "separate active donor contract; not claimed by this overlay",
    }


READBACK_IMPLEMENTATION = r'''namespace {
int BachataSotcHotReadbackMode() {
    static const int mode=[] {
        const char* value=std::getenv("SOTC_RB_HOT");
        return value?std::clamp(std::atoi(value),0,2):1;
    }();
    return mode;
}
}

void BufferCache::GatherReadbackItem(AsyncReadback& rb,const Buffer* arena,
                                    BachataReadback::Span span,bool hot,u64& bytes) {
    ReadbackItem item{};
    item.validity.pages=span;
    item.arena=arena;
    item.hot=hot;
    const auto initial=bytes;
    u64 copied=0;
    memory_tracker->ForEachDownloadRange<false>(span.begin,span.end-span.begin,
        [&](u64 address,u64 size) {
            const auto gather=[&](VAddr from,VAddr to) {
                if(from>=to)return;
                // Track precisely which page runs this item accepted. Hot
                // pages skipped as CPU-dirty retain their byte provenance.
                item.gpu_ranges.push_back({from,to});
                gpu_modified_ranges.ForEachInRange(from,to-from,[&](VAddr start,VAddr end) {
                    // A sparse block released since its GPU mark is not data:
                    // never issue a copy that reads an unbound arena hole.
                    resident_ranges.ForEachInRange(start>>block_shift,
                        ((end-1)>>block_shift)+1,[&](const Backing& backing) {
                            const VAddr a=std::max(start,backing.start<<block_shift);
                            const VAddr b=std::min(end,backing.end<<block_shift);
                            if(a>=b)return;
                            item.copies.push_back(vk::BufferCopy{
                                .srcOffset=a-arena->cpu_addr,.dstOffset=bytes,.size=b-a});
                            bytes=Common::AlignUp(bytes+b-a,u64{64});
                            copied+=b-a;
                        });
                });
            };
            if(!hot) { gather(address,address+size);return; }
            VAddr run=address;
            const auto end=address+size;
            for(VAddr page=address;page<end;) {
                const auto next=std::min<VAddr>(Common::AlignDown(page,4_KB)+4_KB,end);
                if(memory_tracker->IsRegionCpuModified(page,next-page)) {
                    gather(run,page);
                    run=next;
                }
                page=next;
            }
            gather(run,end);
        });
    if(hot && (item.copies.empty() ||
               (BachataSotcHotReadbackMode()==1 && copied>64_KB))) {
        bytes=initial;
        return;
    }
    // Keep an empty requested item: if it has lost all resident bytes, its
    // stale read-watch must be lifted when the batch completes.
    rb.items.push_back(std::move(item));
}

void BufferCache::GatherHotReadbacks(AsyncReadback& rb,u64& bytes) {
    const int mode=BachataSotcHotReadbackMode();
    if(!mode)return;
    const auto now=std::chrono::steady_clock::now();
    constexpr auto lifetime=std::chrono::seconds(2);
    std::erase_if(hot_readbacks,[&](const HotReadback& hot){
        return now-hot.last_request>lifetime;
    });
    const auto requested=rb.validity.pages;
    bool known=false;
    for(auto& hot:hot_readbacks) {
        if(hot.span.begin==requested.begin && hot.span.end==requested.end) {
            hot.last_request=now;
            known=true;
            continue;
        }
        // Do not copy overlapping windows twice into the same batch.
        if(requested.Overlaps(hot.span))continue;
        const auto first=hot.span.begin>>ARENA_PAGE_BITS;
        const auto last=(hot.span.end-1)>>ARENA_PAGE_BITS;
        const auto* arena=address_space[first];
        if(!arena || address_space[last]!=arena || (mode==1 && arena!=rb.arena))continue;
        if(!gpu_modified_ranges.Intersects(hot.span.begin,hot.span.end-hot.span.begin))continue;
        GatherReadbackItem(rb,arena,hot.span,true,bytes);
    }
    if(!known) {
        const auto narrow=ReadbackWindow(rb.arena,requested.begin,1,0);
        const u64 granule=narrow.end-narrow.begin;
        const size_t limit=64*std::clamp<u64>(granule?512_KB/granule:1,1,4);
        if(hot_readbacks.size()<limit)hot_readbacks.push_back({requested,now});
        else {
            auto oldest=std::min_element(hot_readbacks.begin(),hot_readbacks.end(),
                [](const HotReadback& a,const HotReadback& b){return a.last_request<b.last_request;});
            *oldest={requested,now};
        }
    }
}

void BufferCache::ClearEmptyReadback(BachataReadback::Span span) {
    // Called only after a requested gather found zero resident GPU bytes.
    // Byte provenance for already-unbound pages cannot satisfy another fault.
    MarkReadbacksDirty(span.begin,span.end-span.begin);
    gpu_modified_ranges.Subtract(span.begin,span.end-span.begin);
    memory_tracker->UnmarkRegionAsGpuModified(span.begin,span.end-span.begin,false);
}

void BufferCache::BeginAsyncReadback(AsyncReadback& rb,VAddr addr,u64 size,u64 stream) {
    const auto first=addr>>block_shift;
    const auto last=(addr+size-1)>>block_shift;
    rb.arena=GetArena(first,last);
    const auto span=ReadbackWindow(rb.arena,addr,size,stream);
    if(span.begin>=span.end)return;
    rb.validity.pages=span;
    u64 bytes=0;
    GatherReadbackItem(rb,rb.arena,span,false,bytes);
    // No pending copy owns the bytes before its Finish: an empty gather really
    // has no resident GPU data and must not leave a permanent protection fault.
    if(!bytes) {
        ClearEmptyReadback(span);
        return;
    }
    GatherHotReadbacks(rb,bytes);
    rb.staging=staging_pool.Request(bytes,MemoryType::HostCached,0,true);
    for(auto& item:rb.items) {
        for(auto& copy:item.copies)copy.dstOffset+=rb.staging.offset;
        runtime.CopyBuffer(item.arena,rb.staging.buffer,item.copies);
    }
    rb.tick=scheduler.CurrentTick();
    // Flush can run completion callbacks; register before it.
    inflight_readbacks.push_back(&rb);
    scheduler.Flush();
}

bool BufferCache::FinishAsyncReadback(AsyncReadback& rb) {
    std::erase(inflight_readbacks,&rb);
    bool complete=true;
    if(rb.validity.dirty)complete=false;
    rb.staging.Invalidate();
    for(const auto& item:rb.items) {
        if(item.validity.dirty) {
            if(!item.hot)complete=false;
            // A dirtied hot item keeps both provenance and GPU protection.
            // Its later real read starts a new copy; it never stalls this one.
            continue;
        }
        const auto span=item.validity.pages;
        MarkReadbacksDirty(span.begin,span.end-span.begin);
        for(const auto& copy:item.copies) {
            const auto address=item.arena->cpu_addr+copy.srcOffset;
            const auto* source=rb.staging.mapped+(copy.dstOffset-rb.staging.offset);
            const auto write=[&](VAddr at,u64 length) {
                memory->WriteSparseBacking(at,source+(at-address),length);
            };
            if(item.hot)memory_tracker->WriteUnlessCpuModified(address,copy.size,write);
            else write(address,copy.size);
        }
        // Never advertise CPU ownership while its bytes are still in flight.
        for(const auto range:item.gpu_ranges)
            gpu_modified_ranges.Subtract(range.begin,range.end-range.begin);
        memory_tracker->UnmarkRegionAsGpuModified(span.begin,span.end-span.begin,false);
    }
    staging_pool.FreeDeferred(rb.staging);
    return complete;
}
'''
