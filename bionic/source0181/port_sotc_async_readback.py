#!/usr/bin/env python3
"""Adapt SotC's two-phase readback and sparse release ordering to retained FEX.
Donor 732cb37d3470d2dad2cc99da19283253c96b53fc, BufferCache::BeginAsyncReadback /
FinishAsyncReadback / ReadbackWindow / ReleaseBlocks. Retain real FEX backing access.
A dirty overlapping snapshot is retried rather than applied; no GPU ownership
or page protection is removed while its bytes are still in flight.
"""
from pathlib import Path
def edit(root,name,old,new):
    p=root/name; s=p.read_text()
    if s.count(old)!=1: raise RuntimeError(f"{name}: expected one match for {old[:120]!r}, got {s.count(old)}")
    p.write_text(s.replace(old,new,1))
def apply(root):
    root=Path(root)
    base="src/video_core/buffer_cache/"
    h=base+"buffer_cache.h"; c=base+"buffer_cache.cpp"
    edit(root,h,'#include "video_core/renderer_vulkan/vk_semaphore.h"','#include "video_core/renderer_vulkan/vk_semaphore.h"\n#include "video_core/renderer_vulkan/vk_staging_buffer_pool.h"\n#include "video_core/buffer_cache/bachata_readback_span.h"')
    edit(root,h,'    void DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size);', '''    void DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size);
    struct AsyncReadback {
        BachataReadback::Pending validity{};
        const Buffer* arena{};
        std::vector<vk::BufferCopy> copies;
        Vulkan::StagingBufferRef staging{};
        u64 tick{};
    };
    std::vector<AsyncReadback*> inflight_readbacks;
    void MarkReadbacksDirty(VAddr addr,u64 size);
    void BeginAsyncReadback(AsyncReadback& readback,VAddr addr,u64 size,u64 stream);
    bool FinishAsyncReadback(AsyncReadback& readback);
    void CompleteGuestWrite(VAddr addr,u64 size);
    BachataReadback::Span ReadbackWindow(const Buffer* arena,VAddr addr,u64 size,u64 stream) const;''')
    (root/(base+"bachata_readback_span.h")).write_text(Path(__file__).with_name("bachata_readback_span.h").read_text())
    edit(root,c,'#include <algorithm>','#include <algorithm>\n#include <bit>\n#include <cstdlib>')
    edit(root,c,'void BufferCache::ReadMemory(VAddr device_addr, u64 size, bool is_write, bool assume_locks) {', '''BachataReadback::Span BufferCache::ReadbackWindow(const Buffer* arena,VAddr addr,u64 size,u64 stream) const {
    static const u64 narrow=[] {
        const char* v=std::getenv("SOTC_RB_NARROW");
        const u64 kib=v?std::strtoull(v,nullptr,10):1;
        if(!kib)return 512_KB;
        return std::bit_floor(kib==1?u64{64}:std::clamp<u64>(kib,4,512))*1_KB;
    }();
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const bool target=serial=="CUSA08809"||serial=="CUSA08034";
    const u64 bytes=target && EmulatorSettings.GetReadbacksMode()==GpuReadbacksMode::Precise?narrow:512_KB;
    return BachataReadback::Window(addr,size,{arena->cpu_addr,arena->cpu_addr+arena->size_bytes},bytes,stream);
}
void BufferCache::MarkReadbacksDirty(VAddr addr,u64 size) {
    if(!size || size>UINT64_MAX-addr)return;
    for(auto* readback:inflight_readbacks)readback->validity.Mark({addr,addr+size});
}
void BufferCache::CompleteGuestWrite(VAddr addr,u64 size) {
    const auto lo=Common::AlignDown(addr,4_KB);
    const auto hi=Common::AlignUp(addr+size,4_KB);
    if(memory_tracker->IsRegionGpuModified(addr,size)) {
        if(gpu_modified_ranges.Intersects(lo,hi-lo))return;
        memory_tracker->UnmarkRegionAsGpuModified(lo,hi-lo,false);
    }
    memory_tracker->MarkRegionAsCpuModified(addr,size);
}
void BufferCache::BeginAsyncReadback(AsyncReadback& rb,VAddr addr,u64 size,u64 stream) {
    const auto first=addr>>block_shift;
    const auto last=(addr+size-1)>>block_shift;
    rb.arena=GetArena(first,last);
    const auto span=ReadbackWindow(rb.arena,addr,size,stream);
    if(span.begin>=span.end)return;
    rb.validity.pages=span;
    u64 bytes=0;
    memory_tracker->ForEachDownloadRange<false>(span.begin,span.end-span.begin,[&](u64 a,u64 n){
        gpu_modified_ranges.ForEachInRange(a,n,[&](VAddr start,VAddr end){
            rb.copies.push_back(vk::BufferCopy{.srcOffset=start-rb.arena->cpu_addr,
                                              .dstOffset=bytes,.size=end-start});
            bytes=Common::AlignUp(bytes+end-start,u64{64});
        });
    });
    if(!bytes) {
        // A stale GPU page without any byte provenance must not trap forever.
        // Do not clear a page that still has pending GPU writes.
        if(!gpu_modified_ranges.Intersects(span.begin,span.end-span.begin))
            memory_tracker->UnmarkRegionAsGpuModified(span.begin,span.end-span.begin,false);
        return;
    }
    rb.staging=staging_pool.Request(bytes,MemoryType::HostCached,0,true);
    for(auto& copy:rb.copies)copy.dstOffset+=rb.staging.offset;
    runtime.CopyBuffer(rb.arena,rb.staging.buffer,rb.copies);
    rb.tick=scheduler.CurrentTick();
    // Register before Flush, whose completion callbacks can change ownership.
    inflight_readbacks.push_back(&rb);
    scheduler.Flush();
}
bool BufferCache::FinishAsyncReadback(AsyncReadback& rb) {
    std::erase(inflight_readbacks,&rb);
    if(rb.validity.dirty) {
        staging_pool.FreeDeferred(rb.staging);
        return false;
    }
    const auto span=rb.validity.pages;
    // Applying one snapshot changes provenance of overlapping snapshots.
    MarkReadbacksDirty(span.begin,span.end-span.begin);
    rb.staging.Invalidate();
    for(const auto& copy:rb.copies)
        memory->WriteSparseBacking(rb.arena->cpu_addr+copy.srcOffset,
            rb.staging.mapped+(copy.dstOffset-rb.staging.offset),copy.size);
    // Only publish CPU ownership after the real FEX backing contains the data.
    gpu_modified_ranges.Subtract(span.begin,span.end-span.begin);
    memory_tracker->UnmarkRegionAsGpuModified(span.begin,span.end-span.begin,false);
    staging_pool.FreeDeferred(rb.staging);
    return true;
}
void BufferCache::ReadMemory(VAddr device_addr, u64 size, bool is_write, bool assume_locks) {
    if(!size || device_addr >= (1ULL<<40) || size > (1ULL<<40)-device_addr)return;''')
    edit(root,c,'''    if ((serial=="CUSA08809"||serial=="CUSA08034") && !assume_locks) {
        thread_local VAddr last_end=0;
        thread_local u64 last_size=0;
        constexpr u64 base=64_KB, maximum=1024_KB;''','''    const bool target=serial=="CUSA08809"||serial=="CUSA08034";
    static const u64 maximum=[] {
        const char* v=std::getenv("SOTC_RB_STREAM_MAX_KB");
        return std::clamp<u64>(v?std::strtoull(v,nullptr,10):1024,64,4096)*1_KB;
    }();
    if (target && !assume_locks && !is_write) {
        thread_local VAddr last_end=0;
        thread_local u64 last_size=0;
        constexpr u64 base=64_KB;''')
    edit(root,c,'''        // GPU-modified ranges come as many small scattered islands,
        // so the download is widened to a window around the request
        const auto serial=Common::ElfInfo::Instance().GameSerial();
        const u64 WindowSize = (serial=="CUSA08809"||serial=="CUSA08034")?64_KB:512_KB;
        const VAddr arena_end = arena->cpu_addr + arena->size_bytes;
        const VAddr window_start =
            std::max<VAddr>(Common::AlignDown(device_addr, WindowSize), arena->cpu_addr);
        const VAddr window_end = std::min<VAddr>(
            std::max<VAddr>(window_start + (stream?stream:WindowSize), device_addr + size), arena_end);
        DownloadMemory(arena, window_start, window_end - window_start);
        if (is_write) {
            memory_tracker->MarkRegionAsCpuModified(device_addr, size);
        }''','''        const auto span=ReadbackWindow(arena,device_addr,size,stream);
        if(span.begin<span.end)DownloadMemory(arena,span.begin,span.end-span.begin);
        if(is_write)CompleteGuestWrite(device_addr,size);''')
    edit(root,c,'''    if (assume_locks) {
        flush_request();
    } else {
        liverpool->SendCommand<true>(std::move(flush_request));
    }
}

void BufferCache::DownloadMemory''','''    if (assume_locks) {
        flush_request();
        return;
    }
    static const bool async=[]{
        const char* v=std::getenv("SOTC_RB_ASYNC");return !v||v[0]!='0';
    }();
    if(target && async && !liverpool->PrepareGpuSideFault()) {
        // Keep GPU command processing available while the faulting guest thread waits.
        // Retry overlapping rewrites twice; a sustained rewrite uses the original sync path.
        for(unsigned attempt=0;attempt<3;++attempt) {
            AsyncReadback rb{};
            bool no_data=false;
            liverpool->SendCommand<true>([&]{
                BeginAsyncReadback(rb,device_addr,size,stream);
                no_data=!rb.tick;
                if(no_data && is_write)CompleteGuestWrite(device_addr,size);
            });
            if(no_data)return;
            scheduler.WaitSubmitted(rb.tick,false);
            scheduler.GetWorkSemaphore()->Wait(rb.tick);
            bool complete=false;
            liverpool->SendCommand<true>([&]{
                complete=FinishAsyncReadback(rb);
                if(complete && is_write)CompleteGuestWrite(device_addr,size);
            });
            if(complete)return;
        }
    }
    liverpool->SendCommand<true>(std::move(flush_request));
}

void BufferCache::DownloadMemory''')
    edit(root,c,'void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {\n','void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {\n    MarkReadbacksDirty(device_addr,size);\n')
    edit(root,c,'    if (is_written) {\n        gpu_modified_ranges.Add(device_addr, size);','    if (is_written) {\n        MarkReadbacksDirty(device_addr,size);\n        gpu_modified_ranges.Add(device_addr, size);')
    edit(root,c,'    liverpool->SendCommand<true>([this,address,size]{\n        gpu_modified_ranges.Subtract(address,size);','    liverpool->SendCommand<true>([this,address,size]{\n        MarkReadbacksDirty(address,size);\n        gpu_modified_ranges.Subtract(address,size);')
    edit(root,c,'''    boost::container::small_vector<Backing,16> released;
    resident_ranges.ForEachInRange(first,end,[&](const Backing& backing) {
        const u64 a=std::max(first,backing.start), b=std::min(end,backing.end);
        if (a<b) released.push_back(backing.SubRange(a,b));
    });
    if (released.empty()) return;
    scheduler.Finish();
    for (const auto& range : released) {''','''    MarkReadbacksDirty(first<<block_shift,(end-first)<<block_shift);
    boost::container::small_vector<Backing,16> released;
    const auto collect=[&]{
        released.clear();
        resident_ranges.ForEachInRange(first,end,[&](const Backing& backing) {
            const u64 a=std::max(first,backing.start), b=std::min(end,backing.end);
            if (a<b) released.push_back(backing.SubRange(a,b));
        });
    };
    collect();
    if (released.empty()) return;
    scheduler.Finish();
    // Donor ReleaseBlocks: Finish may have run deferred fault rebinds.
    // Never put those binds and their unbinds in the same sparse batch.
    collect();
    if(!pending_binds.empty())scheduler.Flush();
    for (const auto& range : released) {''')
    return {"donor":"732cb37d3470d2dad2cc99da19283253c96b53fc","twoPhaseReadback":True,"heldStaging":True,"overlapDirtyRetry":True,"preciseNarrowWindow":True,"streamMaximumKiB":1024,"recollectSparseReleaseAfterFinish":True,"cpuBackend":"FEX","limitations":"conservative whole-window requeue; donor hot readback aggregation and optional deferred eviction not ported"}
