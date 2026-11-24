#!/usr/bin/env python3
"""Follow-up for actual 3bf1f449 logs, Order watcher crash and Shadow RAM.

The historical dedicated port uses an allocated PageState for all tracked pages,
and forbids CPU reads AND writes during pending GPU readbacks. Keep the mobile
sparse table, but guarantee the same state lifecycle. Reject an image whose
entire span is not GPU-mapped, not just an invalid base. Large staging uploads
are streamed in fixed-size batches with completed GPU fences, not truncated.
"""
from pathlib import Path

def one(s,a,b,label):
    if s.count(a)!=1: raise RuntimeError(f"watcher/staging source drift: {label}: {s.count(a)}")
    return s.replace(a,b,1)

def apply(root: Path):
    p=root/'src/video_core/page_manager.cpp'
    s=p.read_text()
    s=one(s,'#include <algorithm>','#include <algorithm>\n#include <mutex>','page reservation lock include')
    s=one(s,'            return ReadPerm() | WritePerm();',
        '            // Dedicated port PageState: a pending GPU readback blocks writes too.\n'
        '            return num_read_watchers ? Core::MemoryPermission::None : ReadPerm() | WritePerm();',
        'donor permission contract')
    s=one(s,'''        end = std::min(end, VAddr{1} << ADDRESS_BITS) - 1;
        const size_t start_page = begin >> PM_PAGE_BITS;''',
        '''        end = std::min(end, VAddr{1} << ADDRESS_BITS);
        if (begin >= end) return;
        // Map callbacks can run on separate guest CPU threads while GPU tracking
        // enters an unmapped hole. Serialize ObjectPool/reserve publication.
        std::scoped_lock guard{page_reservation_mutex};
        --end;
        const size_t start_page = begin >> PM_PAGE_BITS;''','atomic sparse-table reservation')
    s=one(s,'    Common::MultiLevelPageTable<PageTraits> cached_pages;',
        '    std::mutex page_reservation_mutex;\n    Common::MultiLevelPageTable<PageTraits> cached_pages;',
        'reservation lock member')
    s=one(s,'''                        aligned_addr, aligned_end);
            EnsurePages(aligned_addr, aligned_end);
        }

        for (u64 page = page_start; page != page_end; ++page) {''',
        '''                        aligned_addr, aligned_end);
        }
        // The donor has a PageState for every tracked page. In the sparse
        // version do not silently skip a Track because a VMA has not called
        // OnGpuMap yet; a subsequent Untrack would underflow.
        if (page_start >= page_end || page_end > NUM_ADDRESS_PAGES) return;
        EnsurePages(aligned_addr, aligned_end);

        for (u64 page = page_start; page != page_end; ++page) {''','always reserve ordinary watcher range')
    s=one(s,'''        const u64 page_end = bounds.end_word * PAGES_PER_WORD + bounds.end_page + 1;

        Core::MemoryPermission perms{};''',
        '''        const u64 page_end = bounds.end_word * PAGES_PER_WORD + bounds.end_page + 1;
        if (page_start >= page_end || base_page + page_end > NUM_ADDRESS_PAGES) return;
        // BACHATA_PAGE_WATCHER_PAIRING: region masks previously skipped missing
        // sparse leaves, even though the RegionManager marked its bits tracked.
        EnsurePages((base_page+page_start)<<PM_PAGE_BITS,
                    (base_page+page_end)<<PM_PAGE_BITS);

        Core::MemoryPermission perms{};''','always reserve region watcher range')
    # Reservation occurs before these loops. Do not unlock a page never locked.
    s=one(s,'''            PageState* state = cached_pages.find(page);
            if (!state) {
                continue;
            }

            locks[page].lock();''',
        '''            PageState* state = cached_pages.find(page);
            ASSERT(state);
            locks[page].lock();''','paired ordinary watcher update')
    s=one(s,'''            PageState* state = cached_pages.find(base_page + page);
            if (!state) {
                continue;
            }

            locks[base_page + page].lock();''',
        '''            PageState* state = cached_pages.find(base_page + page);
            ASSERT(state);
            locks[base_page + page].lock();''','paired region watcher update')
    p.write_text(s)

    # The previous log shows an image watcher on 0x2563d8000..0x2d47c8000,
    # not fully mapped; base-only checks allowed this ~2 GiB descriptor.
    # Donor checks device image limits and binds a typed null for invalid slots.
    p=root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    s=p.read_text()
    s=one(s,'''        const Shader::MipStorageFallbackMode mip_fallback_mode = image_desc.mip_fallback_mode;
        const u32 num_bindings = image_desc.NumBindings(stage);

        for (auto i = 0; i < num_bindings; i++) {''',
        '''        const Shader::MipStorageFallbackMode mip_fallback_mode = image_desc.mip_fallback_mode;
        const u32 num_bindings = image_desc.NumBindings(stage);
        const auto limits = instance.GetPhysicalDevice().getProperties().limits;
        const auto null_all = [&] {
            for (u32 i=0;i<num_bindings;++i) {
                auto& [unused_id, null_desc] = image_bindings.emplace_back(
                    std::piecewise_construct,std::tuple{},std::tuple{});
                null_desc.type = image_desc.is_written
                    ? VideoCore::TextureCache::BindingType::Storage
                    : VideoCore::TextureCache::BindingType::Texture;
            }
            image_descriptor_array_sizes.push_back(num_bindings);
        };
        const bool volume = tsharp.GetBaseType() == AmdGpu::ImageType::Color3D;
        const u32 dimension_limit = volume ? limits.maxImageDimension3D : limits.maxImageDimension2D;
        if (tsharp.NumLayers() > limits.maxImageArrayLayers ||
            tsharp.width >= dimension_limit || tsharp.height >= dimension_limit ||
            (volume && tsharp.depth >= dimension_limit)) {
            LOG_WARNING(Render_Vulkan,"BACHATA_IMAGE_DIMENSION_REJECT shader={:#x} address={:#x}",
                        stage.pgm_hash,tsharp.Address());
            null_all();
            continue;
        }
        // Calculate the actual tiled/mipped footprint before FindImage allocates
        // or installs page watchers. IsMapped preserves legitimate GPU PRT areas.
        const VideoCore::TextureCache::ImageDesc candidate{tsharp,image_desc};
        const auto& span = candidate.info;
        if (!span.guest_size || !IsMapped(span.guest_address,span.guest_size)) {
            static std::atomic<u32> invalid_span_reports{};
            const u32 report=invalid_span_reports.fetch_add(1,std::memory_order_relaxed);
            if (report<16 || report%256==0)
                LOG_WARNING(Render_Vulkan,
                    "BACHATA_IMAGE_SPAN_REJECT shader={:#x} address={:#x} bytes={:#x} layers={}",
                    stage.pgm_hash,span.guest_address,span.guest_size,span.resources.layers);
            null_all();
            continue;
        }

        for (auto i = 0; i < num_bindings; i++) {''','validate full T# image footprint')
    s=one(s,'#include "common/elf_info.h"','#include <atomic>\n#include "common/elf_info.h"','image guard rate limit')
    s=one(s,'''            const bool shadow = Common::ElfInfo::Instance().GameSerial() == "CUSA08809";
            const u64 mapped = vsharp.base_address
                ? ((readconst || shadow) ? memory->ClampGpuRangeSize(vsharp.base_address, vsharp.GetSize())''',
        '''            const auto serial = Common::ElfInfo::Instance().GameSerial();
            const bool exact_range = serial == "CUSA08809" || serial == "CUSA00785";
            const u64 mapped = vsharp.base_address
                ? ((readconst || exact_range) ? memory->ClampGpuRangeSize(vsharp.base_address, vsharp.GetSize())''','validate every Order storage buffer')
    p.write_text(s)

    # ImageInfo::guest_size is u32. Do not allow arithmetic wrap to produce a
    # misleading small footprint for a nonsensical many-layer T#.
    p=root/'src/video_core/texture_cache/image_info.cpp'
    s=p.read_text()
    s=one(s,'''        mip_info.size *= num_slices;
        mip_info.offset = guest_size;
        guest_size += mip_info.size;''',
        '''        const u64 mip_bytes = u64{mip_info.size} * num_slices;
        if (mip_bytes > UINT32_MAX || mip_bytes > UINT32_MAX - u64{guest_size}) {
            guest_size = 0; // invalid footprint, rejected before resource binding
            return;
        }
        mip_info.size = static_cast<u32>(mip_bytes);
        mip_info.offset = guest_size;
        guest_size += mip_info.size;''','prevent wrapped tiled-image footprint')
    p.write_text(s)

    # Shadow still requested 2.56 GiB of sparse GPU residency, and a single
    # upload duplicates that span in a dedicated host-visible staging buffer.
    # Preserve all bytes, but stream large CPU->GPU uploads through reusable
    # 16MiB ring blocks and fence them before reuse. No invented buffer bound.
    p=root/'src/video_core/buffer_cache/buffer_cache.cpp'
    s=p.read_text()
    s=one(s,'''    if (!copies.empty()) {
        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);
        for (auto& copy : copies) {
            memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);
            copy.srcOffset += staging.offset;
            copy.dstOffset -= arena->cpu_addr;
        }
        staging.Flush();
        runtime.CopyBuffer(staging.buffer, arena, copies);
    }''',
        '''    if (total_size_bytes > 64_MB) {
        // BACHATA_CHUNKED_LARGE_BUFFER_UPLOAD: staging must not duplicate
        // the full multi-GiB guest heap. Complete each 16MiB upload before
        // reusing the ring, preserving destination offsets and all bytes.
        constexpr u64 batch_size = 16_MB;
        boost::container::small_vector<vk::BufferCopy, 16> batch;
        u64 used=0;
        auto staging=staging_pool.Request(batch_size,MemoryType::HostUncached);
        const auto submit_batch=[&] {
            if (batch.empty()) return;
            staging.Flush();
            runtime.CopyBuffer(staging.buffer,arena,batch);
            scheduler.Finish();
            batch.clear();
            used=0;
        };
        for (const auto& copy : copies) {
            for (u64 offset=0;offset<copy.size;) {
                if (used==batch_size) {
                    submit_batch();
                    staging=staging_pool.Request(batch_size,MemoryType::HostUncached);
                }
                const u64 bytes=std::min<u64>(batch_size-used,copy.size-offset);
                const VAddr address=copy.dstOffset+offset;
                memory->CopySparseMemory(address,staging.mapped+used,bytes);
                batch.emplace_back(staging.offset+used,address-arena->cpu_addr,bytes);
                used+=bytes;
                offset+=bytes;
            }
        }
        submit_batch();
        LOG_INFO(Render,"BACHATA_CHUNKED_LARGE_BUFFER_UPLOAD bytes={} address={:#x}",
                 total_size_bytes,device_addr);
    } else if (!copies.empty()) {
        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);
        for (auto& copy : copies) {
            memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);
            copy.srcOffset += staging.offset;
            copy.dstOffset -= arena->cpu_addr;
        }
        staging.Flush();
        runtime.CopyBuffer(staging.buffer, arena, copies);
    }''','bounded staging working set')
    p.write_text(s)
    return {"watchers":"reserve paired page state before Track/Untrack; retain assertions",
            "images":"device dimension and full GPU mapping guards; no blanket null shader",
            "memory":"all bytes streamed in bounded staging; retains sparse arena release"}
