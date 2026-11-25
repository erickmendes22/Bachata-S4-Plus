"""SotC mip streaming parity, from the exact 732cb37 donor with Android LOD defaults.

Keep the 0.18.1 FEX memory manager and command processor. No AOT, no donor binary.
"""
from pathlib import Path

def apply(root):
    def edit(rel,old,new):
        p=root/"src"/rel
        s=p.read_text()
        if s.count(old)!=1: raise RuntimeError(f"SotC LOD anchor {rel}: {old[:100]} ({s.count(old)})")
        p.write_text(s.replace(old,new,1))
    h=root/"src/video_core/sotc_lod_stats.h"
    h.write_text("""// SPDX-License-Identifier: GPL-2.0-or-later
// Adapted from ShadowOfTheColossus-PC 732cb37, sotc_lod_stats.h.
// Android port defaults: linger=1, level=2, pool_low=8; GPU feedback off.
#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include "common/types.h"
#include "common/elf_info.h"
#include "core/memory.h"

namespace BachataSotcLod {
inline bool Enabled() {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    return serial=="CUSA08809"||serial=="CUSA08034";
}
inline std::array<std::atomic<u32>,256> counts{};
inline void Mark(u32 bank) {
    counts[bank&255].fetch_add(1,std::memory_order_relaxed);
}
inline int PoolFreePercent(Core::MemoryManager* memory) {
    constexpr VAddr pool=0x1000000140ULL;
    std::array<u64,3> meta{};
    if(!memory->TryReadBacking(pool+0x50,meta.data(),sizeof(meta))) return -1;
    const auto [bitmap,words,pages]=meta;
    if(!words||words>0x10000||!pages||pages>words*64||
       bitmap>UINT64_MAX-words*8) return -1;
    std::array<u64,256> bits{};
    u64 free=0;
    for(u64 i=0;i<words;) {
        const u64 n=std::min<u64>(bits.size(),words-i);
        if(!memory->TryReadBacking(bitmap+i*8,bits.data(),n*8))return -1;
        for(u64 k=0;k<n;++k)free+=std::popcount(bits[k]);
        i+=n;
    }
    return static_cast<int>(std::min(free,pages)*100/pages);
}
inline void Collect(Core::MemoryManager* memory,std::array<u64,256>& entries) {
    static u32 reports{};
    static u64 coarser{};
    if(reports++%30==0) {
        const int free=PoolFreePercent(memory);
        if(free>=0) {
            u64 want=coarser;
            if(free<3)want=2;
            else if(free<8)want=std::max<u64>(coarser,1);
            else if(coarser==2)want=1;
            if(want==1&&coarser==1&&free>16)want=0;
            coarser=want;
        }
    }
    for(u32 i=0;i<256;++i) {
        const u64 n=counts[i].exchange(0,std::memory_order_relaxed);
        // linger=1: sampled banks remain live for this report only.
        entries[i]=n?((2+coarser)<<56)|(std::min<u64>(n*256,0xffffff)<<32):u64{15}<<56;
    }
}
}
""")
    lp="video_core/amdgpu/liverpool.cpp"
    rp="video_core/renderer_vulkan/vk_rasterizer.cpp"
    edit(lp,'#include "video_core/amdgpu/liverpool.h"','#include "video_core/amdgpu/liverpool.h"\n#include "video_core/sotc_lod_stats.h"')
    edit(lp,'''            case PM4ItOpcode::GetLodStats: {
                LOG_WARNING(Render_Vulkan, "Unimplemented IT_GET_LOD_STATS");
                break;
            }''','''            case PM4ItOpcode::GetLodStats: {
                if(!BachataSotcLod::Enabled()) {
                    LOG_WARNING(Render_Vulkan,"Unimplemented IT_GET_LOD_STATS");
                    break;
                }
                if(count<3)break;
                const u32* d=reinterpret_cast<const u32*>(header)+1;
                const VAddr base=(VAddr{d[1]}<<6)|(VAddr{d[2]&3u}<<38);
                const u64 bytes=u64{d[0]}+0x20;
                std::array<u64,256> entries{};
                auto* memory=Core::Memory::Instance();
                BachataSotcLod::Collect(memory,entries);
                // Both bank tables are independently bounded by the actual packet.
                for(u32 half=0;half<2;++half) {
                    const u64 offset=0x40+half*sizeof(entries);
                    if(offset+sizeof(entries)>bytes||base>UINT64_MAX-offset-sizeof(entries))break;
                    if(!memory->TryWriteBacking(base+offset,entries.data(),sizeof(entries))) {
                        LOG_WARNING(Render_Vulkan,"SotC LOD output unmapped at {:#x}",base+offset);
                        break;
                    }
                }
                break;
            }''')
    edit(rp,'#include "video_core/renderer_vulkan/vk_rasterizer.h"','#include "video_core/renderer_vulkan/vk_rasterizer.h"\n#include "video_core/sotc_lod_stats.h"')
    edit(rp,'''                auto& [image_id, desc] = image_bindings.emplace_back(
                    std::piecewise_construct, std::tuple{}, std::tuple{element, image_desc});''','''                if(BachataSotcLod::Enabled()&&element.lod_hw_cnt_en)
                    BachataSotcLod::Mark(element.counter_bank_id);
                auto& [image_id, desc] = image_bindings.emplace_back(
                    std::piecewise_construct, std::tuple{}, std::tuple{element, image_desc});''')
    edit(rp,'''        if (texture_cache.IsMeta(tsharp.Address())) {''','''        if(BachataSotcLod::Enabled()&&tsharp&&tsharp.lod_hw_cnt_en)
            BachataSotcLod::Mark(tsharp.counter_bank_id);
        if (texture_cache.IsMeta(tsharp.Address())) {''')
    # Unmap semantics from donor: drop old writes, never read back a widened
    # window over the allocation being returned to the guest streaming pool.
    edit("video_core/buffer_cache/buffer_cache.h","    void ReleaseUnmappedArena(VAddr address, u64 size);",
         "    void ReleaseUnmappedArena(VAddr address, u64 size);\n    void DropGpuModified(VAddr address,u64 size);")
    edit("video_core/buffer_cache/buffer_cache.cpp","void BufferCache::ReleaseUnmappedArena(VAddr address, u64 size) {",
         """void BufferCache::DropGpuModified(VAddr address,u64 size) {
    liverpool->SendCommand<true>([this,address,size]{
        gpu_modified_ranges.Subtract(address,size);
        srt_source_pages.Subtract(address,size);
        memory_tracker->UnmarkRegionAsGpuModified(address,size,false);
        memory_tracker->MarkRegionAsCpuModified(address,size);
    });
}
void BufferCache::ReleaseUnmappedArena(VAddr address, u64 size) {""")
    edit(rp,'''void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    buffer_cache.InvalidateMemory(addr, size);
    texture_cache.UnmapMemory(addr, size);
    if (Common::ElfInfo::Instance().GameSerial() == "CUSA08809") {''',
         '''void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    if(BachataSotcLod::Enabled()) buffer_cache.DropGpuModified(addr,size);
    else buffer_cache.InvalidateMemory(addr,size);
    texture_cache.UnmapMemory(addr,size);
    if(BachataSotcLod::Enabled()) {''')
    edit("video_core/buffer_cache/buffer_cache.cpp",'#include "common/alignment.h"','#include "common/alignment.h"\n#include "common/elf_info.h"')
    edit("video_core/buffer_cache/buffer_cache.cpp","        constexpr u64 WindowSize = 512_KB;",
         """        const auto serial=Common::ElfInfo::Instance().GameSerial();
        const u64 WindowSize = (serial=="CUSA08809"||serial=="CUSA08034")?64_KB:512_KB;""")
    # Same-stream upload memo, precise lifetime via tick + ring wrap.
    edit("video_core/buffer_cache/buffer.h","    /// Tick of the most recent commit into this buffer, 0 if never used.",
         """    [[nodiscard]] u64 WrapGeneration() const noexcept { return wrap_generation; }
    /// Tick of the most recent commit into this buffer, 0 if never used.""")
    edit("video_core/buffer_cache/buffer.h","    u64 last_tick{};","    u64 last_tick{};\n    u64 wrap_generation{};")
    edit("video_core/buffer_cache/buffer.cpp","        invalidation_mark = current_watch_cursor;",
         "        ++wrap_generation;\n        invalidation_mark = current_watch_cursor;")
    edit(rp,'''                const u64 offset =
                    vk_buffer.Copy(stage.flattened_ud_buf.data(), ubo_size, alignment);''',
         '''                const auto& flat=stage.flattened_ud_buf;
                struct Line {
                    std::vector<u32> bytes;
                    vk::Buffer handle{};
                    u64 tick{},generation{},offset{};
                };
                static thread_local std::array<Line,8> memo{};
                static thread_local size_t next{};
                static thread_local u64 queries{},hits{};
                static thread_local bool probe=true;
                const bool eligible=BachataSotcLod::Enabled()&&ubo_size>=128&&ubo_size<=8192;
                if(eligible) {
                    const u64 phase=queries++&32767;
                    if(phase==0){probe=true;hits=0;}
                    else if(phase==4096)probe=hits*100>=4096*6;
                }
                u64 offset{};
                bool found=false;
                if(eligible&&probe) {
                    for(const auto& entry:memo) {
                        if(entry.handle==vk_buffer.Handle()&&entry.tick==scheduler.CurrentTick()&&
                           entry.generation==vk_buffer.WrapGeneration()&&
                           entry.bytes.size()==flat.size()&&
                           std::memcmp(entry.bytes.data(),flat.data(),ubo_size)==0) {
                            offset=entry.offset;found=true;++hits;break;
                        }
                    }
                }
                if(!found) {
                    offset=vk_buffer.Copy(flat.data(),ubo_size,alignment);
                    if(eligible&&probe) {
                        auto& entry=memo[next++%memo.size()];
                        entry.bytes.assign(flat.begin(),flat.end());
                        entry.handle=vk_buffer.Handle();
                        entry.tick=scheduler.CurrentTick();
                        entry.generation=vk_buffer.WrapGeneration();
                        entry.offset=offset;
                    }
                }''')
    return {"lod":"256 bank counters and bounded dual-table PM4 write, donor pool hysteresis",
            "unmap":"discard GPU dirty ranges instead of widening a readback over released memory",
            "readback":"64 KiB window only for SotC",
            "flatbuf":"exact full bytes, tick, buffer identity and wrap generation with adaptive lookup"}
