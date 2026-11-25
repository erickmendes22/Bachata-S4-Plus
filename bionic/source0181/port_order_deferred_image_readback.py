"""Order GPU readback publication with donor page watching adapted to FEX.
No guest CPU access can race a pending image download. WP-only userfaultfd
cannot trap reads, therefore keep synchronous batching on that backend.
"""
from pathlib import Path

def apply(root: Path):
    def edit(rel,a,b):
        p=root/"src"/rel
        s=p.read_text()
        if s.count(a)!=1: raise RuntimeError("deferred readback drift "+rel+": "+a[:110])
        p.write_text(s.replace(a,b,1))
    ph="video_core/page_manager.h"
    pc="video_core/page_manager.cpp"
    th="video_core/texture_cache/texture_cache.h"
    tc="video_core/texture_cache/texture_cache.cpp"
    bc="video_core/buffer_cache/buffer_cache.cpp"
    rc="video_core/renderer_vulkan/vk_rasterizer.cpp"
    edit(ph,"void UpdatePageWatchers(VAddr addr, u64 size, PageOp write_op) const;",
         "void UpdatePageWatchers(VAddr addr, u64 size, PageOp op, bool read = false) const;\n    bool SupportsReadWatchers() const;")
    edit(pc,"            return ReadPerm() | WritePerm();",
         "            return num_read_watchers ? Core::MemoryPermission::None : ReadPerm() | WritePerm();")
    edit(pc,'ASSERT_MSG(num_read_watchers == 0, "Too many watchers");',
         'ASSERT_MSG(num_read_watchers < 255, "Too many read watchers");')
    edit(pc,"    virtual void Protect(VAddr address, size_t size, Core::MemoryPermission perms) = 0;",
         "    virtual void Protect(VAddr address, size_t size, Core::MemoryPermission perms) = 0;\n    virtual bool SupportsReadWatchers() const { return false; }")
    edit(pc,"    void UpdatePageWatchers(VAddr addr, u64 size, PageOp write_op) {",
         "    void UpdatePageWatchers(VAddr addr, u64 size, PageOp write_op, bool read) {")
    edit(pc,"            ASSERT_MSG(write_op != PageOp::Untrack || state->num_write_watchers>0,",
         "            ASSERT_MSG(write_op != PageOp::Untrack || (read ? state->num_read_watchers : state->num_write_watchers)>0,")
    edit(pc,"            const auto new_perms = state->Update(write_op);",
         "            const auto new_perms = state->Update(write_op,!read,write_op,read);")
    edit(pc,"struct SignalImpl : public PageManager::Impl {",
         "struct SignalImpl : public PageManager::Impl {\n    bool SupportsReadWatchers() const override { return true; }")
    edit(pc,"void PageManager::UpdatePageWatchers(VAddr addr, u64 size, PageOp write_op) const {\n    impl->UpdatePageWatchers(addr, size, write_op);\n}",
         "void PageManager::UpdatePageWatchers(VAddr addr, u64 size, PageOp op, bool read) const {\n    impl->UpdatePageWatchers(addr, size, op, read);\n}\nbool PageManager::SupportsReadWatchers() const {return impl->SupportsReadWatchers();}")
    edit(th,'#include <mutex>','#include <mutex>\n#include <deque>\n#include <atomic>\n#include "video_core/renderer_vulkan/vk_staging_buffer_pool.h"')
    edit(th,"    void ProcessDownloadImages();",
         """    void ProcessDownloadImages();
    // GPU thread can resolve directly; faulting guest threads enqueue and wait.
    bool ResolveImageReadbacks(VAddr address, u64 size, bool on_gpu);
    void CancelImageReadbacks(VAddr address, u64 size);""")
    edit(th,"    std::mutex download_images_mutex;",
         """    std::mutex download_images_mutex;
    struct DeferredImageCopy {
        VAddr address;
        u64 size, tick;
        Vulkan::StagingBufferRef staging;
        bool valid;
        bool OverlapsPage(VAddr addr,u64 bytes) const {
            return bytes && addr<=UINT64_MAX-bytes && address<=UINT64_MAX-size &&
                (addr>>12)<=((address+size-1)>>12) &&
                (address>>12)<=((addr+bytes-1)>>12);
        }
    };
    std::deque<DeferredImageCopy> deferred_images;
    std::mutex deferred_images_mutex;
    std::atomic<bool> has_deferred_images{};
    u64 deferred_image_bytes{};
    bool DeferredImageReadbackEnabled() const;
    void RetireImageReadbacks();""")
    edit(tc,'#include "common/elf_info.h"','#include "common/elf_info.h"\n#include "common/bachata_compat_profile.h"\n#include "video_core/amdgpu/liverpool.h"')
    edit(tc,"TextureCache::~TextureCache() = default;",
         """bool TextureCache::DeferredImageReadbackEnabled() const {
    return BachataCompat::Order1886() && readback_linear_images && tracker.SupportsReadWatchers();
}
void TextureCache::RetireImageReadbacks() {
    // Caller holds deferred_images_mutex. Publish copies in submission order.
    while(!deferred_images.empty()&&scheduler.IsFree(deferred_images.front().tick)) {
        auto& copy=deferred_images.front();
        if(copy.valid) {
            copy.staging.Invalidate();
            Core::Memory::Instance()->TryWriteBacking(
                std::bit_cast<u8*>(copy.address),copy.staging.mapped,copy.size);
            tracker.UpdatePageWatchers(copy.address,copy.size,PageOp::Untrack,true);
        }
        runtime.GetStagingPool().FreeDeferred(copy.staging);
        deferred_image_bytes-=copy.size;
        deferred_images.pop_front();
    }
    has_deferred_images.store(!deferred_images.empty(),std::memory_order_release);
}
bool TextureCache::ResolveImageReadbacks(VAddr address,u64 size,bool on_gpu) {
    if(!has_deferred_images.load(std::memory_order_acquire))return false;
    {
        std::scoped_lock lk{deferred_images_mutex};
        if(std::ranges::none_of(deferred_images,[&](const auto& c){return c.valid&&c.OverlapsPage(address,size);}))
            return false;
    }
    const auto resolve=[&] {
        std::scoped_lock lk{deferred_images_mutex};
        u64 tick=0;
        for(const auto& copy:deferred_images)
            if(copy.valid&&copy.OverlapsPage(address,size))tick=copy.tick;
        if(tick) {
            scheduler.Wait(tick);
            RetireImageReadbacks();
        }
    };
    if(on_gpu)resolve();
    else liverpool->SendCommand<true>(resolve);
    return true;
}
void TextureCache::CancelImageReadbacks(VAddr address,u64 size) {
    if(!has_deferred_images.load(std::memory_order_acquire))return;
    std::scoped_lock lk{deferred_images_mutex};
    for(auto& copy:deferred_images) {
        if(copy.valid&&copy.OverlapsPage(address,size)) {
            tracker.UpdatePageWatchers(copy.address,copy.size,PageOp::Untrack,true);
            copy.valid=false;
        }
    }
}
TextureCache::~TextureCache() {
    if(!deferred_images.empty()) {
        scheduler.Finish();
        std::scoped_lock lk{deferred_images_mutex};
        RetireImageReadbacks();
    }
}""")
    edit(tc,"    if (!readback_linear_images) return;\n    const auto serial=",
         """    if (!readback_linear_images) return;
    const bool deferred=DeferredImageReadbackEnabled();
    // Lock order matches DeleteImage: texture lifetime, download list,
    // then deferred readback state. Resolve/cancel never take these first locks.
    if(deferred) {
        std::scoped_lock lk{deferred_images_mutex};
        RetireImageReadbacks();
    }
    const auto serial=""")
    edit(tc,"        constexpr u64 batch_budget=32ull*1024*1024;\n        if(pending_bytes+bytes>batch_budget) flush();",
         """        constexpr u64 batch_budget=32ull*1024*1024;
        constexpr u64 deferred_budget=64ull*1024*1024;
        const bool use_deferred=deferred&&bytes<=deferred_budget&&
            Core::Memory::Instance()->ClampGpuRangeSize(image.info.guest_address,bytes)==bytes;
        std::unique_lock readback_lock{deferred_images_mutex,std::defer_lock};
        if(use_deferred) {
            readback_lock.lock();
            if(deferred_images.size()>=64||deferred_image_bytes>deferred_budget-bytes) {
                scheduler.Finish();
                RetireImageReadbacks();
            }
        } else if(pending_bytes+bytes>batch_budget) flush();""")
    edit(tc,"        pending.push_back({image.info.guest_address,static_cast<u32>(bytes),staging});\n        pending_bytes+=bytes;",
         """        if(use_deferred) {
            tracker.UpdatePageWatchers(image.info.guest_address,bytes,PageOp::Track,true);
            deferred_images.push_back({image.info.guest_address,bytes,scheduler.CurrentTick(),staging,true});
            deferred_image_bytes+=bytes;
            has_deferred_images.store(true,std::memory_order_release);
        } else {
            pending.push_back({image.info.guest_address,static_cast<u32>(bytes),staging});
            pending_bytes+=bytes;
        }""")
    edit(tc,"void TextureCache::DownloadImageMemory(ImageId image_id, bool sync) {\n    Image& image = slot_images[image_id];",
         "void TextureCache::DownloadImageMemory(ImageId image_id, bool sync) {\n    Image& image = slot_images[image_id];\n    ResolveImageReadbacks(image.info.guest_address,image.info.guest_size,true);")
    edit(tc,"void TextureCache::InvalidateMemoryFromGPU(VAddr address, size_t max_size) {\n    std::scoped_lock lock{mutex};",
         "void TextureCache::InvalidateMemoryFromGPU(VAddr address, size_t max_size) {\n    ResolveImageReadbacks(address,max_size,true);\n    std::scoped_lock lock{mutex};")
    edit(tc,"void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {\n    std::scoped_lock lk{mutex};",
         "void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {\n    CancelImageReadbacks(cpu_addr,size);\n    std::scoped_lock lk{mutex};")
    edit(tc,"void TextureCache::DeleteImage(ImageId image_id) {\n    Image& image = slot_images[image_id];",
         "void TextureCache::DeleteImage(ImageId image_id) {\n    Image& image = slot_images[image_id];\n    CancelImageReadbacks(image.info.guest_address,image.info.guest_size);")
    edit(tc,"void TextureCache::RefreshImage(Image& image) {\n    if (False(image.flags & ImageFlagBits::Dirty) || image.info.num_samples > 1) {\n        return;\n    }",
         "void TextureCache::RefreshImage(Image& image) {\n    if (False(image.flags & ImageFlagBits::Dirty) || image.info.num_samples > 1) {\n        return;\n    }\n    ResolveImageReadbacks(image.info.guest_address,image.info.guest_size,true);")
    edit(bc,"                                                        bool is_written, bool is_texel_buffer) {\n    // For read-only buffers",
         "                                                        bool is_written, bool is_texel_buffer) {\n    texture_cache.ResolveImageReadbacks(device_addr,size,true);\n    // For read-only buffers")
    edit(bc,"std::pair<const Buffer*, u64> BufferCache::ObtainBufferForImage(VAddr device_addr, u32 size) {",
         "std::pair<const Buffer*, u64> BufferCache::ObtainBufferForImage(VAddr device_addr, u32 size) {\n    texture_cache.ResolveImageReadbacks(device_addr,size,true);")
    edit(bc,"        memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);",
         "        texture_cache.ResolveImageReadbacks(copy.dstOffset,copy.size,true);\n            memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);")
    edit(bc,"void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {",
         "void BufferCache::DownloadMemory(const Buffer* arena, VAddr device_addr, u64 size) {\n    texture_cache.ResolveImageReadbacks(device_addr,size,true);")
    edit(rc,"    buffer_cache.InvalidateMemory(addr, size, assume_locks);",
         "    texture_cache.ResolveImageReadbacks(addr,size,assume_locks);\n    buffer_cache.InvalidateMemory(addr, size, assume_locks);")
    edit(rc,"    buffer_cache.ReadMemory(addr, size, false, assume_locks);",
         "    const bool image_resolved=texture_cache.ResolveImageReadbacks(addr,size,assume_locks);\n    if(!image_resolved||buffer_cache.IsRegionGpuModified(addr,size))\n        buffer_cache.ReadMemory(addr, size, false, assume_locks);")
    edit(rc,"    for (unsigned pass=0;pass<4;++pass) {\n        std::vector<VAddr> pages;",
         "    for (unsigned pass=0;pass<4;++pass) {\n        std::vector<VAddr> pages;\n        bool image_resolved=false;")
    edit(rc,"            const VAddr page=source&PageMask;\n            // Do not mark a page visited",
         "            const VAddr page=source&PageMask;\n            image_resolved|=texture_cache.ResolveImageReadbacks(page,PageSize,true);\n            // Do not mark a page visited")
    edit(rc,"        if (pages.empty() || !buffer_cache.DownloadSrtSourcePages(pages)) break;",
         "        const bool buffer_resolved=!pages.empty()&&buffer_cache.DownloadSrtSourcePages(pages);\n        if(!image_resolved&&!buffer_resolved) break;")
    return {"readback":"64-entry 64-MiB page-watched image queue, ordered retirement",
            "coherence":"resolve before guest read/write, uploads, SRT and partial GPU writes; cancel on unmap",
            "scope":"Order signal tracking only; synchronous batch when read-fault tracking unavailable"}
