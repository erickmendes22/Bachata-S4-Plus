#!/usr/bin/env python3
"""Restore the Release 0.2.6 SRT GPU-written source-page refresh chain.

Verified from the authentic 0.2.6/0.2.7 ARM64 ELF:
 Rasterizer::ReadBackGpuWrittenSrtSources loops page-aligned SRT inputs,
 checks BufferCache GPU modifications, downloads modified pages, and
 refreshes the flattened shader resource table for up to four passes.
 This port uses modern 0.18.1 BufferCache::ReadMemory to download a
 GPU-modified mapped page on the GPU command-processing thread, where
 SendCommand<true> must not recursively enqueue itself.

No guest RAM copy is used for GPU-written pages until the GPU's actual
tracked memory has been downloaded and its fence has completed.
"""
from pathlib import Path

def sub(s, old, new, label):
    n=s.count(old)
    if n != 1:
        raise RuntimeError(f"Release SRT GPU page source drift {label}: {n}")
    return s.replace(old,new,1)

def apply(root: Path) -> dict:
    srt_h=root/"src/shader_recompiler/ir/passes/srt.h"
    srt_cpp=root/"src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp"
    info_h=root/"src/shader_recompiler/info.h"
    bc_h=root/"src/video_core/buffer_cache/buffer_cache.h"
    bc_cpp=root/"src/video_core/buffer_cache/buffer_cache.cpp"
    raster_h=root/"src/video_core/renderer_vulkan/vk_rasterizer.h"
    raster_cpp=root/"src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    sh=srt_h.read_text();sc=srt_cpp.read_text()
    ih=info_h.read_text();rh=raster_h.read_text();rc=raster_cpp.read_text()
    bh=bc_h.read_text();bc=bc_cpp.read_text()

    sh=sub(sh,
           "void RunSrtWalker(SrtWalkerCode code, const u32* user_data, u32* flat_dst);",
           "void RunSrtWalker(SrtWalkerCode code, const u32* user_data, u32* flat_dst,\n"
           "                  VAddr* source_addresses);",
           "SRT source-tracking API")

    sc=sub(sc,
           "void RunSrtWalker(SrtWalkerCode code, const u32* user_data, u32* flat) {",
           "void RunSrtWalker(SrtWalkerCode code, const u32* user_data, u32* flat,\n"
           "                  VAddr* source_addresses) {",
           "guest-bytecode source address capture")
    sc=sub(sc,
           """                if (!TryReadGuest(address, flat, value)) {
                    /* Revalidate changing guest SRT memory every dispatch; do not permanently poison opcode. */
                    LOG_WARNING(Render_Recompiler,
                                "BIONIC_PORTABLE_SRT_BAD_READ: opcode={} address={:#x}",
                                i / 3, address);
                    value = 0;
                }
                flat[b] = value;""",
           """                const bool guest_read_ok = TryReadGuest(address, flat, value);
                if (!guest_read_ok) {
                    /* Revalidate changing guest SRT memory every dispatch; do not permanently poison opcode. */
                    LOG_WARNING(Render_Recompiler,
                                "BIONIC_PORTABLE_SRT_BAD_READ: opcode={} address={:#x}",
                                i / 3, address);
                    value = 0;
                }
                flat[b] = value;""",
           "read source exactly once")
    sc=sub(sc,
           """        case SrtOp::CopyImm:
        case SrtOp::CopyExpr: {
            const u32 off = op == SrtOp::CopyImm ? a : values[--nv];
            const bool null = cur < 0x10000ULL;""",
           """        case SrtOp::CopyImm:
        case SrtOp::CopyExpr: {
            const u32 off = op == SrtOp::CopyImm ? a : values[--nv];
            if (source_addresses) source_addresses[b]=0;
            const bool null = cur < 0x10000ULL;""",
           "source address initialize")
    sc=sub(sc,
           """                flat[b] = value;
            }
            continue;
        }
        case SrtOp::PopPtr:""",
           """                flat[b] = value;
                // Revisit this page if the GPU writes it later; never substitute
                // a stale CPU descriptor while the GPU version is newer.
                if (source_addresses && guest_read_ok)
                    source_addresses[b] = address;
            }
            continue;
        }
        case SrtOp::PopPtr:""",
           "track validated SRT data source")
    ih=sub(ih,
           "    std::vector<u32> flattened_ud_buf;\n",
           "    std::vector<u32> flattened_ud_buf;\n"
           "    // Release 0.2.6: guest source page for each flattened SRT DWORD.\n"
           "    // Derived each refresh; never serialized as a host pointer.\n"
           "    std::vector<VAddr> srt_guest_sources;\n",
           "Shader::Info transient SRT guest pages")
    ih=sub(ih,
           """        flattened_ud_buf.resize(srt_info.flattened_bufsize_dw);
        ASSERT(user_data.size() <= NUM_USER_DATA_REGS);""",
           """        flattened_ud_buf.resize(srt_info.flattened_bufsize_dw);
        srt_guest_sources.assign(flattened_ud_buf.size(), 0);
        ASSERT(user_data.size() <= NUM_USER_DATA_REGS);""",
           "refresh SRT guest source vector")
    ih=sub(ih,
           "RunSrtWalker(srt_info.walker_func, user_data.data(), flattened_ud_buf.data());",
           "RunSrtWalker(srt_info.walker_func, user_data.data(), flattened_ud_buf.data(),\n"
           "                         srt_guest_sources.data());",
           "call source-aware walker")

    # Official Release checks the exact DWORD write provenance, then
    # tracks the containing SRT page so later GPU writes cannot be lost
    # to a coarser page-local memory tracker. Uses the existing modern
    # 0.18 RangeSet rather than creating a parallel region allocator.
    bh=sub(bh,
           "    [[nodiscard]] bool IsRegionGpuModified(VAddr addr, size_t size);",
           "    [[nodiscard]] bool IsRegionGpuModified(VAddr addr, size_t size);\\n"
           "    [[nodiscard]] bool IsRangeGpuWritten(VAddr addr, size_t size);\\n"
           "    void TrackSrtSourcePage(VAddr page);",
           "Release GPU-written SRT range/page tracking declarations")
    bh=sub(bh,
           "    RangeSet gpu_modified_ranges;",
           "    RangeSet gpu_modified_ranges;\\n"
           "    RangeSet srt_source_pages;",
           "track pages referenced by guest shader descriptors")
    bc=sub(bc,
           """bool BufferCache::IsRegionGpuModified(VAddr addr, size_t size) {
    return memory_tracker->IsRegionGpuModified(addr, size);
}""",
           """bool BufferCache::IsRegionGpuModified(VAddr addr, size_t size) {
    // The original Release preserves GPU-write provenance of SRT pages
    // independently of the broad page-level memory tracker.
    return memory_tracker->IsRegionGpuModified(addr, size) ||
           (srt_source_pages.Intersects(addr, size) &&
            gpu_modified_ranges.Intersects(addr, size));
}

// BACHATA_RELEASE026_SRT_GPU_RANGE_TRACKING
bool BufferCache::IsRangeGpuWritten(VAddr addr, size_t size) {
    if (size==0 || addr>UINT64_MAX-size) return false;
    return gpu_modified_ranges.Intersects(addr,size) ||
           memory_tracker->IsRegionGpuModified(addr,size);
}
void BufferCache::TrackSrtSourcePage(VAddr page) {
    if (page<0x10000 || page>=0x10000000000ULL) return;
    srt_source_pages.Add(page & ~u64{4095},4096);
}""",
           "Release GPU source tracking implementation")

    rh=sub(rh,
           "    bool BindResources(const Pipeline* pipeline);\n",
           "    // Release 0.2.6 GPU-to-CPU SRT source page refresh.\n"
           "    void ReadBackGpuWrittenSrtSources(const Shader::Info& stage);\n"
           "    bool BindResources(const Pipeline* pipeline);\n",
           "Rasterizer SRT readback method")
    rc=sub(rc,
           """        if (!stage) {
            continue;
        }
        set_writes.resize(set_writes.size() + stage->buffers.size()""",
           """        if (!stage) {
            continue;
        }
        ReadBackGpuWrittenSrtSources(*stage);
        set_writes.resize(set_writes.size() + stage->buffers.size()""",
           "readback SRT source pages BEFORE binding any GPU descriptors")
    rc=sub(rc, '#include "common/debug.h"\n',
           '#include <unordered_set>\n#include "common/debug.h"\n',
           "deduplicate GPU-modified SRT source pages")
    rc=sub(rc,
           "bool Rasterizer::BindResources(const Pipeline* pipeline) {",
           r"""// BACHATA_RELEASE026_SRT_GPU_PAGE_READBACK
// Official Release performs up to four passes: a write may update a
// descriptor pointing at another GPU-written SRT page. Re-evaluate the
// SRT sources only after the required page has been downloaded.
void Rasterizer::ReadBackGpuWrittenSrtSources(const Shader::Info& stage) {
    constexpr u64 PageSize=4096;
    constexpr u64 PageMask=~u64{PageSize-1};
    if(stage.srt_guest_sources.empty()) return;
    for(unsigned pass=0;pass<4;++pass) {
        bool changed=false;
        std::unordered_set<VAddr> visited;
        for(const auto source:stage.srt_guest_sources) {
            if(source<0x10000 || source>=0x10000000000ULL)continue;
            const VAddr page=source&PageMask;
            if(!visited.insert(page).second)continue;
            if(!buffer_cache.IsRegionGpuModified(page,PageSize))continue;
            if(!IsMapped(page,PageSize))continue;
            // The actual Release first checks exact 4-byte SRT operand
            // writer state, not only the larger 4KiB backing region.
            if(!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)))continue;
            buffer_cache.TrackSrtSourcePage(page);
            // Called on the Liverpool GPU command thread. ReadMemory's
            // assume_locks=true calls DownloadMemory directly, avoiding
            // a recursive SendCommand<true> and waiting for the actual GPU
            // copy/fence to complete before RefreshFlatBuf reads the page.
            buffer_cache.ReadMemory(page,PageSize,false,true);
            changed=true;
        }
        if(!changed)break;
        auto& writable=const_cast<Shader::Info&>(stage);
        writable.RefreshFlatBuf();
        LOG_INFO(Render_Vulkan,
                 "BACHATA_RELEASE026_SRT_GPU_PAGES_REFRESHED pass={} pages={}",
                 pass,visited.size());
    }
}

bool Rasterizer::BindResources(const Pipeline* pipeline) {""",
           "Release SRT GPU-written source page readback")
    # No fallback that silently replaces GPU bytes with stale CPU memory.
    if "BACHATA_RELEASE026_SRT_GPU_PAGE_READBACK" not in rc:
        raise RuntimeError("No active Shader::Info-to-BufferCache GPU page readback")
    for path,txt in ((srt_h,sh),(srt_cpp,sc),(info_h,ih),
                     (bc_h,bh),(bc_cpp,bc),(raster_h,rh),(raster_cpp,rc)):
        path.write_text(txt)
    return {
        "ported":"Release SRT source addresses and GPU-written page-aware refresh",
        "sourceTracking":"BufferCache IsRangeGpuWritten + TrackSrtSourcePage backed by modern RangeSet",
        "provenance":"guest VMAs captured per SRT dword; no invented addresses",
        "gpuDownload":"real 0.18.1 BufferCache ReadMemory + GPU fence",
        "passes":4,
        "notPorted":"additional release image-readback paths and full Arm64SrtEmitter JIT",
    }
