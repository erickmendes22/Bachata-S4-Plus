#!/usr/bin/env python3
"""Restore protected-memory alias semantics from 0.18.1 and dedicated ports.

References: actual pinned FEX MemoryManager::CopySparseMemory / TryWriteBacking,
upstream 0.18.1 physical backing reads, SotC 7308102b and dedicated Order
f42cf7a1/ae6bd6e9. No change to PageState permission calculation or GPU readback mode.
"""
from pathlib import Path

def one(s,a,b,label):
    if s.count(a)!=1: raise RuntimeError(f"backing/graphics parity drift {label}: {s.count(a)}")
    return s.replace(a,b,1)

def apply(root:Path):
    h=root/'src/core/memory.h'
    p=root/'src/core/memory.cpp'
    a=h.read_text();s=p.read_text()
    a=one(a,'    bool TryWriteBacking(void* address, const void* data, u64 size);',
        '    bool TryReadBacking(VAddr address, void* data, u64 size);\n'
        '    bool TryWriteBacking(void* address, const void* data, u64 size);','physical backing API')
    a=one(a,'bool HasPhysicalBacking(VirtualMemoryArea vma)',
        'bool HasPhysicalBacking(const VirtualMemoryArea& vma)','avoid copying physical map for each VMA')
    start=s.index('void MemoryManager::CopySparseMemory(')
    end=s.index('\nPAddr MemoryManager::PoolExpand(',start)
    old=s[start:end]
    assert 'std::bit_cast<const u8*>(virtual_addr)' in old and 'memcpy(backing, data, copy_size)' in old
    s=s[:start]+r'''// BACHATA_PHYSICAL_BACKING_ALIAS: GPU transfers must not fault into guest
// page tracking. The retained ARM64 FEX VMA has a second memfd view;
// translate through the physical areas rather than the protected guest VA.
namespace {
template<class F>
bool VisitPhysicalSpans(const Core::VirtualMemoryArea& vma, VAddr address, u64 size,
                        F&& visit) {
    u64 offset=address-vma.base;
    while (size) {
        auto it=vma.phys_areas.upper_bound(offset);
        if (it==vma.phys_areas.begin()) return false;
        --it;
        if (offset<it->first || offset-it->first>=it->second.size) return false;
        const u64 in_area=offset-it->first;
        const u64 bytes=std::min(size,it->second.size-in_area);
        visit(it->second.base+in_area,bytes);
        offset+=bytes;
        size-=bytes;
    }
    return true;
}
}

void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {
    std::shared_lock lk{mutex};
    while (size) {
        if (!IsValidMapping(address)) {
            std::memset(dest,0,size);
            return;
        }
        const auto it=FindVMA(address);
        const auto& vma=it->second;
        const u64 bytes=std::min<u64>(size,vma.base+vma.size-address);
        if (HasPhysicalBacking(vma)) {
            if (BachataCompat::Sotc608()) {
                std::memset(dest,0,bytes);
                const u64 begin=address-vma.base;
                const u64 end=begin+bytes;
                auto part=vma.phys_areas.upper_bound(begin);
                if (part!=vma.phys_areas.begin()) --part;
                for (;part!=vma.phys_areas.end() && part->first<end;++part) {
                    const u64 lo=std::max<u64>(begin,part->first);
                    const u64 hi=std::min<u64>(end,part->first+part->second.size);
                    if (hi>lo) std::memcpy(dest+lo-begin,
                        impl.BackingBase()+part->second.base+lo-part->first,hi-lo);
                }
            } else {
            // BACHATA_SPARSE_COPY_ONCE: write each destination byte once.
            // Previously every physical byte was first memset then memcpy.
            // PRT holes are still zeroed, including interior and trailing holes.
            const u64 begin=address-vma.base;
            const u64 end=begin+bytes;
            u64 cursor=begin;
            auto part=vma.phys_areas.upper_bound(begin);
            if (part!=vma.phys_areas.begin()) --part;
            for (;part!=vma.phys_areas.end() && part->first<end;++part) {
                const u64 lo=std::max<u64>(cursor,part->first);
                const u64 hi=std::min<u64>(end,part->first+part->second.size);
                if (hi<=lo) continue;
                if (lo>cursor) std::memset(dest+cursor-begin,0,lo-cursor);
                std::memcpy(dest+lo-begin,
                    impl.BackingBase()+part->second.base+lo-part->first,hi-lo);
                cursor=hi;
            }
            if (cursor<end) std::memset(dest+cursor-begin,0,end-cursor);
            }
        } else if (vma.IsMapped()) {
            // Non-physical file mappings retain their original copy behavior.
            std::memcpy(dest,std::bit_cast<const u8*>(address),bytes);
        } else {
            std::memset(dest,0,bytes);
        }
        address+=bytes;
        dest+=bytes;
        size-=bytes;
    }
}

// Validate every physical span before touching output/guest memory. In
// particular, a write crossing noncontiguous physical areas must advance
// the SOURCE as well as the destination (old FEX repeated the first bytes).
bool MemoryManager::TryReadBacking(VAddr address, void* data, u64 size) {
    if (!size) return true;
    std::shared_lock lk{mutex};
    const auto visit=[&](auto&& copy) {
        VAddr pos=address;
        u64 remaining=size;
        while (remaining) {
            if (!IsValidMapping(pos)) return false;
            const auto& vma=FindVMA(pos)->second;
            if (!HasPhysicalBacking(vma)) return false;
            const u64 bytes=std::min(remaining,vma.base+vma.size-pos);
            if (!VisitPhysicalSpans(vma,pos,bytes,copy)) return false;
            pos+=bytes; remaining-=bytes;
        }
        return true;
    };
    if (size>UINT64_MAX-address) return false;
    // Typical SRT reads are a DWORD or a contiguous descriptor/table.
    // Validate and copy a single physical area without two VMA walks.
    if (!BachataCompat::Sotc608() && IsValidMapping(address)) {
        const auto& vma=FindVMA(address)->second;
        if (HasPhysicalBacking(vma) && address>=vma.base &&
            size<=vma.base+vma.size-address) {
            const u64 offset=address-vma.base;
            auto part=vma.phys_areas.upper_bound(offset);
            if (part!=vma.phys_areas.begin()) {
                --part;
                const u64 in_area=offset-part->first;
                if (in_area<part->second.size && size<=part->second.size-in_area) {
                    std::memcpy(data,impl.BackingBase()+part->second.base+in_area,size);
                    return true;
                }
            }
        }
    }
    if (!visit([](PAddr,u64){})) return false;
    auto* out=static_cast<u8*>(data);
    return visit([&](PAddr phys,u64 n) {
        std::memcpy(out,impl.BackingBase()+phys,n); out+=n;
    });
}

bool MemoryManager::TryWriteBacking(void* address, const void* data, u64 size) {
    if (!size) return true;
    const VAddr base=std::bit_cast<VAddr>(address);
    if (size>UINT64_MAX-base) return false;
    std::shared_lock lk{mutex};
    const auto visit=[&](auto&& copy) {
        VAddr pos=base;
        u64 remaining=size;
        while (remaining) {
            if (!IsValidMapping(pos)) return false;
            const auto& vma=FindVMA(pos)->second;
            if (!HasPhysicalBacking(vma)) return false;
            const u64 bytes=std::min(remaining,vma.base+vma.size-pos);
            if (!VisitPhysicalSpans(vma,pos,bytes,copy)) return false;
            pos+=bytes; remaining-=bytes;
        }
        return true;
    };
    if (!visit([](PAddr,u64){})) return false;
    const auto* src=static_cast<const u8*>(data);
    return visit([&](PAddr phys,u64 n) {
        std::memcpy(impl.BackingBase()+phys,src,n); src+=n;
    });
}
'''+s[end:]
    h.write_text(a);p.write_text(s)

    # cf4089f8: a descriptor containing immediate DWORDs is not a contiguous
    # load even if its default offset array happens to be consecutive.
    p=root/'src/shader_recompiler/ir/passes/resource_patching_pass.cpp'
    s=p.read_text()
    s=one(s,'    if (sharp_fetch.summary != Summary::Invalid) {',
        '    const u32 all_loaded=(1u<<sharp.num_dwords)-1;\n'
        '    if (sharp_fetch.summary != Summary::Invalid && sharp_fetch.load_mask == all_loaded) {',
        'donor mixed immediate descriptor fetch')
    p.write_text(s)

    # The old Order PushUd constant override does not match this ABI.
    # Do not mutate persistent shader descriptors.
    p=root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    s=p.read_text()
    s=one(s,'    std::memcpy(snapshot->mapped_data.data(),reinterpret_cast<const void*>(address),bytes);',
        '    memory->CopySparseMemory(address,snapshot->mapped_data.data(),bytes);',
        'ReadConst snapshot through physical backing')
    s=one(s,'''        const Shader::MipStorageFallbackMode mip_fallback_mode = image_desc.mip_fallback_mode;
        const u32 num_bindings = image_desc.NumBindings(stage);

        for (auto i = 0; i < num_bindings; i++) {''',
        '''        const Shader::MipStorageFallbackMode mip_fallback_mode = image_desc.mip_fallback_mode;
        const u32 num_bindings = image_desc.NumBindings(stage);

        // Dedicated Order image guard. The latest 3bf1f449 crash tracked
        // 0x2563d8000..0x2d47c8000, beyond its GPU mapping. Validate the
        // whole tiled footprint before FindImage allocates or tracks it.
        // The base-only test is insufficient, and PRT regions are retained
        // by Rasterizer::IsMapped rather than requiring physical residency.
        if (Common::ElfInfo::Instance().GameSerial()=="CUSA00785") {
            const VideoCore::TextureCache::ImageDesc probe{tsharp,image_desc};
            const auto& info=probe.info;
            if (!info.guest_size || !IsMapped(info.guest_address,info.guest_size)) {
                LOG_WARNING(Render_Vulkan,
                    "BACHATA_ORDER_IMAGE_SPAN_REJECT shader={:#x} addr={:#x} size={:#x}",
                    stage.pgm_hash,info.guest_address,info.guest_size);
                for (u32 i=0;i<num_bindings;++i) {
                    auto& [unused_id,null_desc]=image_bindings.emplace_back(
                        std::piecewise_construct,std::tuple{},std::tuple{});
                    null_desc.type=image_desc.is_written
                        ? VideoCore::TextureCache::BindingType::Storage
                        : VideoCore::TextureCache::BindingType::Texture;
                }
                image_descriptor_array_sizes.push_back(num_bindings);
                continue;
            }
        }
        for (auto i = 0; i < num_bindings; i++) {''','Order full image footprint before allocation')
    p.write_text(s)
    p=root/'src/video_core/texture_cache/image_info.cpp'
    s=p.read_text()
    s=one(s,'''        mip_info.size *= num_slices;
        mip_info.offset = guest_size;
        guest_size += mip_info.size;''',
        '''        const u64 mip_bytes=u64{mip_info.size}*num_slices;
        if (mip_bytes>UINT32_MAX || mip_bytes>UINT32_MAX-u64{guest_size}) {
            guest_size=0;
            return;
        }
        mip_info.size=static_cast<u32>(mip_bytes);
        mip_info.offset=guest_size;
        guest_size+=mip_info.size;''','reject overflowed texture footprint')
    p.write_text(s)

    # UMA: a newly allocated HOST_VISIBLE|HOST_COHERENT sparse backing can
    # receive its first CPU snapshot directly. No second multi-GiB staging
    # allocation, no scheduler.Finish inside BindResources, and no memory
    # imported or pinned from a changing guest VMA. Subsequent updates use
    # the ordinary ordered Vulkan transfer path.
    p=root/'src/video_core/buffer_cache/buffer_cache.h'
    h=p.read_text()
    h=one(h,'    std::unordered_map<VkDeviceMemory, u64> backing_blocks;',
        '    std::unordered_map<VkDeviceMemory, u64> backing_blocks;\n'
        '    std::vector<vk::DeviceMemory> fresh_backings;\n'
        '    bool coherent_arena_upload{};\n'
        '    bool UploadFreshBacking(VAddr address, u64 size);',
        'first-upload allocation ownership')
    p.write_text(h)
    p=root/'src/video_core/buffer_cache/buffer_cache.cpp'
    s=p.read_text()
    s=one(s,'''            .value();

    const u64 bda_pagetable_size =''',
        '''            .value();
    if (instance.IsIntegrated()) {
        constexpr auto wanted=vk::MemoryPropertyFlagBits::eDeviceLocal |
                              vk::MemoryPropertyFlagBits::eHostVisible |
                              vk::MemoryPropertyFlagBits::eHostCoherent;
        if (const auto type=FindMemoryType(instance.GetMemoryProperties(),wanted,reqs.memoryTypeBits)) {
            arena_memory_type_index=*type;
            coherent_arena_upload=true;
        }
    }

    const u64 bda_pagetable_size =''','select coherent device-local UMA memory only if supported')
    s=one(s,'''    backing_blocks.emplace(static_cast<VkDeviceMemory>(device_memory), resident_blocks);''',
        '''    backing_blocks.emplace(static_cast<VkDeviceMemory>(device_memory), resident_blocks);
    if (coherent_arena_upload) fresh_backings.push_back(device_memory);''','register new unsubmitted allocation')
    s=one(s,'''    EnsureResident(arena, first_block, last_block);
    SynchronizeMemory(arena, device_addr, size, is_written, is_texel_buffer);''',
        '''    fresh_backings.clear();
    EnsureResident(arena, first_block, last_block);
    SynchronizeMemory(arena, device_addr, size, is_written, is_texel_buffer);
    fresh_backings.clear();''','first upload lifetime limited to one ObtainBuffer')
    s=one(s,'''bool BufferCache::SynchronizeMemory(const Buffer* arena, VAddr device_addr, u32 size,
                                    bool is_written, bool is_texel_buffer) {''',
        '''bool BufferCache::UploadFreshBacking(VAddr address,u64 size) {
    if (!coherent_arena_upload || fresh_backings.empty() || !size) return false;
    // Only an entire freshly allocated range is eligible. Do not map or
    // overwrite any allocation already used by previously recorded draws.
    const u64 first=address>>block_shift;
    const u64 end=(address+size+block_size-1)>>block_shift;
    struct Part { vk::DeviceMemory memory; VAddr address; u64 bytes; u64 offset; };
    std::vector<Part> parts;
    u64 covered=0;
    bool valid=true;
    resident_ranges.ForEachInRange(first,end,[&](const Backing& backing) {
        if (std::ranges::find(fresh_backings,backing.memory)==fresh_backings.end()) {
            valid=false; return;
        }
        const VAddr lo=std::max<VAddr>(address,backing.start<<block_shift);
        const VAddr hi=std::min<VAddr>(address+size,backing.end<<block_shift);
        if (hi<=lo) return;
        const u64 offset=(backing.offset<<block_shift)+lo-(backing.start<<block_shift);
        parts.push_back({backing.memory,lo,hi-lo,offset});
        covered+=hi-lo;
    });
    if (!valid || covered!=size) return false;
    const auto device=instance.GetDevice();
    for (const auto& part:parts) {
        const auto [result,mapped]=device.mapMemory(part.memory,0,VK_WHOLE_SIZE);
        if (result!=vk::Result::eSuccess || !mapped) return false;
        memory->CopySparseMemory(part.address,static_cast<u8*>(mapped)+part.offset,part.bytes);
        device.unmapMemory(part.memory);
    }
    // Coherent host writes occur before the queue submission that binds
    // and consumes these pages. A later normal transfer will use barriers.
    return true;
}

bool BufferCache::SynchronizeMemory(const Buffer* arena, VAddr device_addr, u32 size,
                                    bool is_written, bool is_texel_buffer) {''','direct first upload into coherent UMA allocation')
    s=one(s,'''    if (!copies.empty()) {
        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);''',
        '''    if (total_size_bytes>64_MB && coherent_arena_upload && !fresh_backings.empty()) {
        // Keep existing data and all non-eligible spans in the old staging path.
        // This reduces the working set without truncating raw GCN buffers.
        u64 saved=0;
        copies.erase(std::remove_if(copies.begin(),copies.end(),[&](const vk::BufferCopy& copy) {
            if (!UploadFreshBacking(copy.dstOffset,copy.size)) return false;
            saved+=copy.size;
            return true;
        }),copies.end());
        if (saved) {
            total_size_bytes=0;
            for (auto& copy:copies) {
                copy.srcOffset=total_size_bytes;
                total_size_bytes+=copy.size;
            }
            LOG_INFO(Render,"BACHATA_UMA_FIRST_UPLOAD bytes={} remaining_staging={}",
                     saved,total_size_bytes);
        }
    }
    if (!copies.empty()) {
        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);''','avoid multi-GiB staging duplicates')
    p.write_text(s)
    return {"memory":"physical aliases, corrected cross-area reads/writes, coherent UMA first uploads",
            "graphics":"mixed immediate V#/T#/S# fetch, full Order image extent, overflow guard",
            "regression":"no changes to page permissions, no mid-bind waits, no arbitrary range clipping"}
