#!/usr/bin/env python3
"""Bring the actual donor absent-lane and inactive-light contracts to 0.18.1,
and batch real GPU-written SRT page downloads on the common Bionic GPU path.
"""
from pathlib import Path
import re
def one(s,a,b,label):
    if s.count(a)!=1:
        raise RuntimeError(f"render/perf source drift {label}: {s.count(a)}")
    return s.replace(a,b,1)
def apply(root:Path):
    p=root/'src/shader_recompiler/ir/passes/lower_wave64_pass.cpp'
    s=p.read_text()
    reduction="static const IR::Inst* SkipBitCasts(const IR::Value& value) {\n    if (value.IsImmediate()) {\n        return nullptr;\n    }\n    const IR::Inst* inst = value.Inst();\n    while (inst->GetOpcode() == IR::Opcode::BitCastU32F32 ||\n           inst->GetOpcode() == IR::Opcode::BitCastF32U32) {\n        if (inst->Arg(0).IsImmediate()) {\n            return nullptr;\n        }\n        inst = inst->Arg(0).Inst();\n    }\n    return inst;\n}\n\n/// Identity of the reduction step that produced value, when value = op(x, ShuffleXor(x, k)).\n/// Based on the wave64_missing_lane_identity workaround of Pink-shadPS4 (luizgustavs).\nstatic std::optional<u32> ReductionIdentity(const IR::Value& value) {\n    const IR::Inst* op = SkipBitCasts(value);\n    if (!op || op->NumArgs() != 2) {\n        return std::nullopt;\n    }\n    bool is_step = false;\n    for (u32 arg = 0; arg < 2; ++arg) {\n        const IR::Inst* shuffle = SkipBitCasts(op->Arg(arg));\n        const IR::Inst* other = SkipBitCasts(op->Arg(1 - arg));\n        is_step |= shuffle && other && shuffle->GetOpcode() == IR::Opcode::ShuffleXor &&\n                   SkipBitCasts(shuffle->Arg(0)) == other;\n    }\n    if (!is_step) {\n        return std::nullopt;\n    }\n    switch (op->GetOpcode()) {\n    case IR::Opcode::FPMin32:\n        return 0x7f800000u; // +inf\n    case IR::Opcode::FPMax32:\n        return 0xff800000u; // -inf\n    case IR::Opcode::FPMul32:\n        return 0x3f800000u; // 1.0\n    case IR::Opcode::UMin32:\n    case IR::Opcode::BitwiseAnd32:\n        return 0xffffffffu;\n    case IR::Opcode::SMin32:\n        return 0x7fffffffu;\n    case IR::Opcode::SMax32:\n        return 0x80000000u;\n    case IR::Opcode::IMul32:\n        return 1u;\n    case IR::Opcode::FPAdd32:\n    case IR::Opcode::IAdd32:\n    case IR::Opcode::UMax32:\n    case IR::Opcode::BitwiseOr32:\n    case IR::Opcode::BitwiseXor32:\n        return 0u;\n    default:\n        return std::nullopt;\n    }\n}\n\n"
    s=one(s,'void LowerWave64BallotPass(IR::Program& program, const RuntimeInfo& runtime_info,',
        reduction+'''// Donor SotC 5712cee31461: a missing reduction lane must contribute the
// identity, not an arbitrary stale register. Only the proven reduction shape
// is changed; do not invent values for general non-reduction lane reads.
static void FoldAbsentReductionLanes(IR::Program& program,u32 lanes) {
    if (!lanes) return;
    for (IR::Block* block:program.blocks) {
        for (IR::Inst& inst:block->Instructions()) {
            if (inst.GetOpcode()!=IR::Opcode::ReadLane || !inst.Arg(1).IsImmediate() ||
                inst.Arg(1).U32()<lanes) continue;
            const auto identity=ReductionIdentity(inst.Arg(0));
            if (identity) {
                LOG_INFO(Render_Recompiler,"BACHATA_ABSENT_REDUCTION_LANE shader={:#x} lane={} identity={:#x}",
                         program.info.pgm_hash,inst.Arg(1).U32(),*identity);
                inst.ReplaceUsesWithAndRemove(IR::Value{*identity});
            }
        }
    }
}

void LowerWave64BallotPass(IR::Program& program, const RuntimeInfo& runtime_info,''','wave reduction identity helper')
    s=one(s,'''    if (program.info.hw_stage != HwStage::Compute || profile.subgroup_size == 64) {
        return;
    }

    const auto [size_x, size_y, size_z] = runtime_info.hw.cs.workgroup_size;
    const u32 num_threads = size_x * size_y * size_z;
    if (num_threads <= 32) {
        return;
    }''',
        '''    if (program.info.hw_stage != HwStage::Compute) return;
    const auto [size_x,size_y,size_z]=runtime_info.hw.cs.workgroup_size;
    const u32 num_threads=size_x*size_y*size_z;
    if (profile.subgroup_size==64) {
        // Only the actual donor shader and workgroup are established.
        // Preserve the previously working upstream behavior everywhere else.
        if (program.info.pgm_hash==0x87cf9b8aULL && num_threads==32)
            FoldAbsentReductionLanes(program,32);
        return;
    }
    if (num_threads<=32) return;''','scope absent-lane identity to verified donor shader')
    p.write_text(s)

    # Exact dedicated Order 16-light guard (de566ea0a46e).
    # The donor checks the 708-DWORD layout. Keep that contract, additionally
    # require actual contiguous fetched T# DWORDs rather than assuming a
    # partially immediate descriptor has the same slot identity.
    p=root/'src/shader_recompiler/resource.h'
    s=p.read_text()
    s=one(s,'struct ImageResource {','''template<class InfoT>
constexpr bool Order1886UnusedLightImage(const InfoT& info,u32 offset) {
    if (info.pgm_hash!=0x804aeeadULL) return false;
    const auto& flat=info.flattened_ud_buf;
    if (flat.size()!=708) return false;
    const u32 count=flat[657],mask=flat[655];
    if (count>16) return false;
    if (offset>=68 && offset<196 && (offset-68)%8==0)
        return (offset-68)/8>=count;
    if (offset>=196 && offset<324 && (offset-196)%8==0) {
        const u32 light=(offset-196)/8;
        return light>=count || ((mask>>light)&1)==0;
    }
    return false;
}

struct ImageResource {''','exact light table guard')
    s=one(s,'''    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {
        AmdGpu::Image image{};''',
        '''    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {
        // BACHATA_ORDER_LIGHT_GUARD: only inactive ordinary sampled images
        // in the verified 708-DWORD table; never blank active light images.
        if (!array_size && !is_depth && !is_atomic && !is_written && !is_r128 &&
            post_op==SharpFetchPostOp::None &&
            mip_fallback_mode==MipStorageFallbackMode::None &&
            sharp_fetch.load_mask==0xff &&
            Order1886UnusedLightImage(info,sharp_fetch.offsets[0])) {
            bool contiguous=true;
            for (u32 i=1;i<8;++i)
                contiguous &= sharp_fetch.offsets[i]==sharp_fetch.offsets[0]+i;
            if (contiguous) return AmdGpu::Image::Null(false);
        }
        AmdGpu::Image image{};''','apply prior to shader type selection and binding')
    p.write_text(s)

    # Match the donor's precise source-write check, and batch downloads by
    # GPU submission, not by 4KiB source page / 512KiB fault window.
    p=root/'src/video_core/buffer_cache/buffer_cache.h'
    s=p.read_text()
    s=one(s,'    void TrackSrtSourcePage(VAddr page);',
        '    void TrackSrtSourcePage(VAddr page);\n    bool DownloadSrtSourcePages(std::span<const VAddr> pages);','batched readback API')
    s=one(s,'#include <deque>','#include <deque>\n#include <span>','span include')
    p.write_text(s)
    p=root/'src/video_core/buffer_cache/buffer_cache.cpp'
    s=p.read_text()
    s=one(s,'''    return gpu_modified_ranges.Intersects(addr,size) ||
           memory_tracker->IsRegionGpuModified(addr,size);''',
        '''    return gpu_modified_ranges.Intersects(addr,size);''','true byte-range provenance, not any nearby GPU write')
    s=one(s,'void BufferCache::TrackSrtSourcePage(VAddr page) {',
        '''// BACHATA_BATCH_SRT_READBACK: all pages in a pointer-graph pass share
// one staging allocation and one GPU completion. The normal CPU fault
// readback still uses its own widened window. Only bytes marked GPU-written
// are copied; adjacent CPU-owned descriptors remain untouched.
bool BufferCache::DownloadSrtSourcePages(std::span<const VAddr> pages) {
    struct Batch { const Buffer* arena; std::vector<vk::BufferCopy> copies; };
    std::vector<Batch> batches;
    std::vector<VAddr> completed_pages;
    u64 total=0;
    for (VAddr page:pages) {
        if (!gpu_modified_ranges.Intersects(page,4096)) continue;
        const auto* arena=address_space[page>>ARENA_PAGE_BITS];
        if (!arena) continue;
        auto it=std::ranges::find(batches,arena,&Batch::arena);
        if (it==batches.end()) { batches.push_back({arena,{}}); it=std::prev(batches.end()); }
        const auto previous_size=it->copies.size();
        gpu_modified_ranges.ForEachInRange(page,4096,[&](VAddr start,VAddr end) {
            it->copies.push_back({start-arena->cpu_addr,total,end-start});
            total=Common::AlignUp(total+end-start,64ULL);
        });
        if (it->copies.size()!=previous_size) completed_pages.push_back(page);
    }
    if (!total) return false;
    const auto download=staging_pool.Request(total,MemoryType::HostCached);
    for (auto& batch:batches) {
        for (auto& copy:batch.copies) copy.dstOffset+=download.offset;
        if (!batch.copies.empty()) runtime.CopyBuffer(batch.arena,download.buffer,batch.copies);
    }
    scheduler.Finish();
    download.buffer->Invalidate(download.offset,download.size);
    for (const auto& batch:batches)
        for (const auto& copy:batch.copies)
            memory->WriteSparseBacking(batch.arena->cpu_addr+copy.srcOffset,
                download.mapped+copy.dstOffset-download.offset,copy.size);
    for (VAddr page:completed_pages) {
        gpu_modified_ranges.Subtract(page,4096);
        memory_tracker->UnmarkRegionAsGpuModified(page,4096,false);
    }
    return true;
}

void BufferCache::TrackSrtSourcePage(VAddr page) {''','one staging copy/fence per graph pass')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    s=p.read_text()
    start=s.index('    for(unsigned pass=0;pass<4;++pass) {',s.index('void Rasterizer::ReadBackGpuWrittenSrtSources'))
    end=s.index('\n}\n',start)
    s=s[:start]+'''    std::unordered_set<VAddr> visited;
    for (unsigned pass=0;pass<4;++pass) {
        std::vector<VAddr> pages;
        for (const auto source:stage.srt_guest_sources) {
            if (source<0x10000 || source>=0x10000000000ULL) continue;
            const VAddr page=source&PageMask;
            // Do not mark a page visited on an unrelated, CPU-owned DWORD.
            if (!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)) ||
                visited.contains(page) || !IsMapped(page,PageSize)) continue;
            visited.insert(page);
            buffer_cache.TrackSrtSourcePage(page);
            pages.push_back(page);
        }
        if (pages.empty() || !buffer_cache.DownloadSrtSourcePages(pages)) break;
        auto& writable=const_cast<Shader::Info&>(stage);
        writable.RefreshFlatBuf();
        static std::atomic<u64> batches{0};
        const u64 n=batches.fetch_add(1,std::memory_order_relaxed)+1;
        if (n<=16 || n%512==0)
            LOG_INFO(Render_Vulkan,"BACHATA_RELEASE026_SRT_GPU_PAGES_REFRESHED pass={} pages={} batches={}",
                     pass,pages.size(),n);
    }'''+s[end:]
    # Keep resource correctness but rate-limit routine clamping on hot draws.
    s=one(s,'''                    LOG_ERROR(Render, "Clamped size from {} to {} for stage {:#x}",
                              vsharp.GetSize(), size, stage.pgm_hash);''',
        '''                    static std::atomic<u64> clamp_count{0};
                    const u64 n=clamp_count.fetch_add(1,std::memory_order_relaxed)+1;
                    if (n<=16 || n%1024==0)
                        LOG_WARNING(Render,"Clamped size from {} to {} for stage {:#x} count={}",
                                    vsharp.GetSize(),size,stage.pgm_hash,n);''','avoid synchronous log spam on bound sentinel ranges')
    p.write_text(s)

    # Try last-used module first: port the dedicated Order cache's hot-path
    # ordering, but preserve the corrected effective metadata checks.
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_cache.h'
    s=p.read_text()
    s=one(s,'    ModuleList modules{};',
        '    ModuleList modules{};\n    size_t last_used{};','last used module cache')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_cache.cpp'
    s=p.read_text()
    s=one(s,'''    for (size_t i=0;i<program->modules.size();++i) {
        auto& candidate=program->modules[i];''',
        '''    for (size_t k=0;k<program->modules.size();++k) {
        const size_t i=(program->last_used+k)%program->modules.size();
        auto& candidate=program->modules[i];''','likely permutation first')
    s=one(s,'''    if (auto& fetch=program->modules[perm_idx].spec.fetch_shader_data; !fetch.Empty())''',
        '''    program->last_used=perm_idx;
    if (auto& fetch=program->modules[perm_idx].spec.fetch_shader_data; !fetch.Empty())''','remember actual matched variant')
    # Current Order traces prove the driver crashes during pipeline creation.
    # Include exact flat shape in existing trace, without new broad logging.
    s=one(s,'''LOG_INFO(Render_Vulkan,"BACHATA_ORDER_VARIANT_CONTRACT perm={} buffers={} images={} samplers={}",
                 perm_idx,info.buffers.size(),info.images.size(),info.samplers.size());''',
        '''LOG_INFO(Render_Vulkan,"BACHATA_ORDER_VARIANT_CONTRACT perm={} buffers={} images={} samplers={} flat_dwords={}",
                 perm_idx,info.buffers.size(),info.images.size(),info.samplers.size(),info.flattened_ud_buf.size());''','verify exact donor layout')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp'
    s=p.read_text()
    s,n=re.subn(r'ShaderBinaryVersion = (\d+)u;',lambda m:f'ShaderBinaryVersion = {int(m.group(1))+3}u;',s)
    if n!=1: raise RuntimeError('shader binary version drift')
    p.write_text(s)
    return {"color":"SotC donor 0x87cf9b8a 32-thread reduction identity on wave64 only",
            "order":"exact donor 0x804aeead inactive light table guard",
            "performance":"precise SRT provenance, batch GPU download, last-used permutation, sampled logging"}
