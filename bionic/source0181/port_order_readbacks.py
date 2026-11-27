"""Transfer the Order deferred readback / SRT / sun-cascade pipeline to Bionic FEX.

Donor: The-Order-1886_pc c53cd01d032995fe622033623ab64b4cf6b02233,
BufferCache::DeferReadback, ApplyDeferredReadbacks, WaitDeferredReadbacks,
WaitDeferredSrtPages, KeepPageSynchronized, RecordSunCopies, DeliverSunCopies.
Unlike the donor's byte-snapshot merge, FEX retains GPU page ownership until
publication, so CPU faults and SRT reads see the latest authoritative data.
"""
from pathlib import Path


def apply(root):
    src=Path(root)/'src'
    def edit(rel, old, new):
        p=src/rel
        s=p.read_text()
        assert s.count(old)==1,(rel,old[:100],s.count(old))
        p.write_text(s.replace(old,new,1))
    bc='video_core/buffer_cache/buffer_cache.cpp'
    bh='video_core/buffer_cache/buffer_cache.h'
    mt='video_core/buffer_cache/memory_tracker.h'
    tx='video_core/texture_cache/texture_cache.h'
    ra='video_core/renderer_vulkan/vk_rasterizer.cpp'
    edit(bh,'#include "video_core/renderer_vulkan/vk_semaphore.h"', '#include "video_core/renderer_vulkan/vk_semaphore.h"\n#include "video_core/renderer_vulkan/vk_staging_buffer_pool.h"')
    edit(bh,'    void TickFrame();','''    void TickFrame();
    void KeepOrderSunPage(VAddr address,u64 size);
    void RecordOrderSunCopies();
    void UnmapOrderReadbacks(VAddr address,u64 size);''')
    edit(bh,'    SynchronizedRanges srt_source_pages;', '''    SynchronizedRanges srt_source_pages;

    // Only the GPU command owner accesses these batches. A page stays GPU
    // dirty and protected until all of its current byte ranges are published.
    struct OrderReadbackPage {
        VAddr address{};
        const Buffer* arena{};
        std::vector<vk::BufferCopy> copies;
        bool valid{true};
    };
    struct OrderReadbackBatch {
        u64 tick{}, generation{};
        Vulkan::StagingBufferRef staging{};
        std::vector<OrderReadbackPage> pages;
    };
    std::deque<OrderReadbackBatch> order_readbacks;
    RangeSet order_sun_pages;
    void ApplyOrderReadbacks();
    void DirtyOrderReadbacks(VAddr address,u64 size);
    u64 OrderReadbackTick(VAddr address,u64 size) const;
    bool WaitOrderReadbacks(u64 tick);
    void DeferOrderReadbacks(std::span<const VAddr> pages);
    void ReadOrderWindow(const Buffer* arena,VAddr address,u64 size,bool is_write);''')
    edit(mt,'    /// Mark region as modified from the CPU','''    // The check, copy and release are one page-protection transaction.
    // An unsuccessful speculative publication retains GPU ownership.
    bool PublishOrderPage(VAddr page,auto&& publish) {
        if (readbacks_mode!=GpuReadbacksMode::Precise || (page & (BYTES_PER_PAGE-1)) ||
            page >= (1ULL<<MAX_CPU_PAGE_BITS)) return false;
        auto* region=top_tier[page>>HIGHER_PAGE_BITS].load(std::memory_order_acquire);
        if (!region) return false;
        const u64 offset=page&HIGHER_PAGE_MASK;
        const auto bounds=region->GetBounds(offset,BYTES_PER_PAGE);
        region->Lock(bounds);
        const bool success=!region->template IsRegionModified<Type::CPU>(offset,BYTES_PER_PAGE) &&
            region->template IsRegionModified<Type::GPU>(offset,BYTES_PER_PAGE) && publish();
        if (success) region->template ChangeRegionState<StateOp::None,StateOp::Clear,false>(offset,BYTES_PER_PAGE);
        region->Unlock(bounds);
        return success;
    }

    /// Mark region as modified from the CPU''')
    edit(tx,'    bool ResolveImageReadbacks(VAddr address, u64 size, bool on_gpu);','''    bool ResolveImageReadbacks(VAddr address, u64 size, bool on_gpu);
    // Speculative buffer publication must not race an image alias registration.
    // A contended texture cache simply leaves the page on the exact read path.
    bool WithOrderBufferPage(VAddr page,auto&& action) {
        std::unique_lock lock{mutex,std::try_to_lock};
        if (!lock.owns_lock()) return false;
        bool overlap=false;
        ForEachImageInRegion(page,4096,[&](ImageId,Image&){overlap=true;return true;});
        return !overlap && action();
    }''')
    edit('core/memory.h','    bool TryWriteBacking(void* address, const void* data, u64 size);','''    bool TryWriteBacking(void* address, const void* data, u64 size);
    bool TryWriteBackingAtGeneration(VAddr address,const void* data,u64 size,u64 generation);''')
    p=src/'core/memory.cpp';s=p.read_text();start=s.index('bool MemoryManager::TryWriteBacking(');end=s.index('\nPAddr MemoryManager::PoolExpand',start)
    method=s[start:end].replace('bool MemoryManager::TryWriteBacking(void* address, const void* data, u64 size)', 'bool MemoryManager::TryWriteBackingAtGeneration(VAddr base,const void* data,u64 size,u64 generation)').replace('    const VAddr base=std::bit_cast<VAddr>(address);\n','').replace('    std::shared_lock lk{mutex};','    std::shared_lock lk{mutex};\n    if ((generation&1) || mapping_generation.Load()!=generation) return false;')
    p.write_text(s[:end]+'\n'+method+s[end:])
    edit(bc,'BufferCache::~BufferCache() = default;', '''BufferCache::~BufferCache() {
    // Staging pool retains each released allocation until its recording tick completes.
    for (const auto& batch:order_readbacks) staging_pool.FreeDeferred(batch.staging);
}

void BufferCache::DirtyOrderReadbacks(VAddr address,u64 size) {
    if (!size || size>UINT64_MAX-address) return;
    for (auto& batch:order_readbacks) for (auto& page:batch.pages)
        if (page.valid && page.address<address+size && address<page.address+4096) page.valid=false;
}

u64 BufferCache::OrderReadbackTick(VAddr address,u64 size) const {
    if (!size || size>UINT64_MAX-address) return 0;
    u64 tick=0;
    for (const auto& batch:order_readbacks) for (const auto& page:batch.pages)
        if (page.valid && page.address<address+size && address<page.address+4096)
            tick=std::max(tick,batch.tick);
    return tick;
}

void BufferCache::ApplyOrderReadbacks() {
    while (!order_readbacks.empty() && scheduler.IsFree(order_readbacks.front().tick)) {
        auto batch=std::move(order_readbacks.front());
        order_readbacks.pop_front();
        if (batch.generation==memory->MappingGeneration()) {
            batch.staging.Invalidate();
            for (const auto& page:batch.pages) {
                if (!page.valid) continue;
                texture_cache.WithOrderBufferPage(page.address,[&] {
                    return memory_tracker->PublishOrderPage(page.address,[&] {
                        for (const auto& copy:page.copies) {
                            if (!memory->TryWriteBackingAtGeneration(page.arena->cpu_addr+copy.srcOffset,
                                batch.staging.mapped+copy.dstOffset-batch.staging.offset,copy.size,batch.generation))
                                return false;
                        }
                        gpu_modified_ranges.Subtract(page.address,4096);
                        return true;
                    });
                });
            }
        }
        staging_pool.FreeDeferred(batch.staging);
    }
}

bool BufferCache::WaitOrderReadbacks(u64 tick) {
    if (!tick) return false;
    if (!scheduler.IsFree(tick)) scheduler.Wait(tick);
    ApplyOrderReadbacks();
    return true;
}

void BufferCache::DeferOrderReadbacks(std::span<const VAddr> pages) {
    ApplyOrderReadbacks();
    if (EmulatorSettings.GetReadbacksMode()!=GpuReadbacksMode::Precise || order_readbacks.size()>=8) return;
    OrderReadbackBatch batch{};
    batch.generation=memory->MappingGeneration();
    if (batch.generation&1) return;
    u64 bytes=0;
    for (VAddr address:pages) {
        if ((address&4095) || address >= (1ULL<<40) ||
            OrderReadbackTick(address,4096) || !gpu_modified_ranges.Intersects(address,4096) ||
            !memory_tracker->IsRegionGpuModified(address,4096) ||
            memory_tracker->IsRegionCpuModified(address,4096) ||
            !texture_cache.WithOrderBufferPage(address,[]{return true;})) continue;
        const auto* arena=address_space[address>>ARENA_PAGE_BITS];
        if (!arena) continue;
        OrderReadbackPage page{address,arena,{},true};
        const u64 previous=bytes;
        bool complete=true;
        gpu_modified_ranges.ForEachInRange(address,4096,[&](VAddr first,VAddr end) {
            if (first>=end) return;
            // Vulkan copies require DWORD granularity. The authoritative
            // synchronous path handles uncommon unaligned spans unchanged.
            if ((first&3) || ((end-first)&3)) {complete=false;return;}
            resident_ranges.ForEachGap(first>>block_shift,((end-1)>>block_shift)+1,
                [&](u64,u64){complete=false;});
            page.copies.push_back({first-arena->cpu_addr,bytes,end-first});
            bytes=Common::AlignUp(bytes+end-first,64ULL);
        });
        if (!complete || page.copies.empty() || bytes>4_MB) {
            bytes=previous;
            if (bytes>4_MB-4096) break;
            continue;
        }
        batch.pages.push_back(std::move(page));
    }
    if (!bytes) return;
    batch.staging=staging_pool.Request(bytes,MemoryType::HostCached,0,true);
    for (auto& page:batch.pages) {
        for (auto& copy:page.copies) copy.dstOffset+=batch.staging.offset;
        runtime.CopyBuffer(page.arena,batch.staging.buffer,page.copies);
    }
    batch.tick=scheduler.CurrentTick();
    order_readbacks.push_back(std::move(batch));
}

void BufferCache::ReadOrderWindow(const Buffer* arena,VAddr address,u64 size,bool is_write) {
    const VAddr first=Common::AlignDown(address,4_KB), end=Common::AlignUp(address+size,4_KB);
    // Keep the donor's 512 KiB look-ahead, but do not release neighbouring
    // pages to the guest before their GPU writes are actually visible.
    if (end-first<=512_KB && EmulatorSettings.GetReadbacksMode()==GpuReadbacksMode::Precise) {
        ApplyOrderReadbacks();
        std::vector<VAddr> pages;
        const VAddr window=std::max<VAddr>(arena->cpu_addr,Common::AlignDown(address,512_KB));
        const VAddr limit=std::min<VAddr>(arena->cpu_addr+arena->size_bytes,std::max<VAddr>(window+512_KB,end));
        for (VAddr page=window;page<limit;page+=4096) pages.push_back(page);
        DeferOrderReadbacks(pages);
        WaitOrderReadbacks(OrderReadbackTick(first,end-first));
    }
    // Only faulting pages may be released. The exact read path preserves
    // image/metadata aliases, writes that superseded a snapshot, and holes.
    DownloadMemory(arena,first,end-first);
    if (is_write) memory_tracker->MarkRegionAsCpuModified(address,size);
}

void BufferCache::KeepOrderSunPage(VAddr address,u64 size) {
    if (!BachataCompat::Order1886() || !address || !size || size>512_KB ||
        address >= (1ULL<<40) || size>(1ULL<<40)-address) return;
    const auto first=Common::AlignDown(address,4_KB);
    order_sun_pages.Add(first,Common::AlignUp(address+size,4_KB)-first);
}

void BufferCache::RecordOrderSunCopies() {
    if (!BachataCompat::Order1886()) return;
    std::vector<VAddr> pages;
    order_sun_pages.ForEach([&](VAddr first,VAddr end){
        for (VAddr page=first;page<end && pages.size()<512;page+=4096)
            if (gpu_modified_ranges.Intersects(page,4096)) pages.push_back(page);
    });
    DeferOrderReadbacks(pages);
}

void BufferCache::UnmapOrderReadbacks(VAddr address,u64 size) {
    if (!BachataCompat::Order1886() || !size || size>UINT64_MAX-address) return;
    const auto first=Common::AlignDown(address,4_KB);
    const auto end=Common::AlignUp(address+size,4_KB);
    DirtyOrderReadbacks(first,end-first);
    order_sun_pages.Subtract(first,end-first);
}
''')
    edit(bc,'void BufferCache::TickFrame() {','void BufferCache::TickFrame() {\n    if (BachataCompat::Order1886()) ApplyOrderReadbacks();')
    edit(bc,'    const auto flush_request = [this, device_addr, size, is_write] {','''    if (!size || device_addr >= (1ULL<<40) || size>(1ULL<<40)-device_addr) return;
    const auto flush_request = [this, device_addr, size, is_write] {''')
    edit(bc,'        // GPU-modified ranges come as many small scattered islands,','''        if (BachataCompat::Order1886()) {
            ReadOrderWindow(arena,device_addr,size,is_write);
            return;
        }
        // GPU-modified ranges come as many small scattered islands,''')
    edit(bc,'void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {','''void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {
    DirtyOrderReadbacks(device_addr,size);''')
    edit(bc,'        gpu_modified_ranges.Add(device_addr, size);','        DirtyOrderReadbacks(device_addr,size);\n        gpu_modified_ranges.Add(device_addr, size);')
    edit(bc,'bool BufferCache::DownloadSrtSourcePages(std::span<const VAddr> pages) {','''bool BufferCache::DownloadSrtSourcePages(std::span<const VAddr> pages) {
    u64 pending=0;
    if (BachataCompat::Order1886()) {
        for (VAddr page:pages) pending=std::max(pending,OrderReadbackTick(page,4096));
    }
    const bool resolved=WaitOrderReadbacks(pending);''')
    edit(bc,'        if (!gpu_modified_ranges.Intersects(page,4096)) continue;\n        const auto* arena=address_space[page>>ARENA_PAGE_BITS];','''        if (!gpu_modified_ranges.Intersects(page,4096)) continue;
        DirtyOrderReadbacks(page,4096);
        const auto* arena=address_space[page>>ARENA_PAGE_BITS];''')
    edit(bc,'    if (!total) return false;','    if (!total) return resolved;')
    edit(bc,'        copies.emplace_back(total_size_bytes, addr, size);','        DirtyOrderReadbacks(addr,size);\n        copies.emplace_back(total_size_bytes, addr, size);')
    edit(bc,'bool BufferCache::SynchronizeMemoryFromImage(const Buffer* arena, VAddr device_addr, u32 size) {','''bool BufferCache::SynchronizeMemoryFromImage(const Buffer* arena, VAddr device_addr, u32 size) {
    DirtyOrderReadbacks(device_addr,size);''')
    edit(bc,'    if (!size || address >= (1ULL<<40) || size > (1ULL<<40)-address) return;\n    const u64 first=Common::AlignUp(address,u64{block_size})>>block_shift;', '''    if (!size || address >= (1ULL<<40) || size > (1ULL<<40)-address) return;
    DirtyOrderReadbacks(address,size);
    const u64 first=Common::AlignUp(address,u64{block_size})>>block_shift;''')
    edit(ra,'    ResetBindings(true);\n}\n\nvoid Rasterizer::DispatchIndirect', '''    ResetBindings(true);
    if (BachataCompat::Order1886() && cs.pgm_hash==0x7b1b18c9ULL) buffer_cache.RecordOrderSunCopies();
}

void Rasterizer::DispatchIndirect''')
    edit(ra,'                if (desc.is_written) {\n                    // Raw storage-buffer writes', '''                if (desc.is_written) {
                    if (BachataCompat::Order1886() && (stage.uses_buffer_atomic_float_min_max ||
                        stage.pgm_hash==0x7550d841ULL || stage.pgm_hash==0x7b1b18c9ULL))
                        buffer_cache.KeepOrderSunPage(vsharp.base_address,size);
                    // Raw storage-buffer writes''')
    edit(ra,'    texture_cache.UnmapMemory(addr, size);\n    if (Common::ElfInfo', '''    texture_cache.UnmapMemory(addr, size);
    if (BachataCompat::Order1886()) liverpool->SendCommand<true>([this,addr,size]{buffer_cache.UnmapOrderReadbacks(addr,size);});
    if (Common::ElfInfo''')
