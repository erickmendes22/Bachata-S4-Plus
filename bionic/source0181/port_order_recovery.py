"""Correct independently demonstrated descriptor contracts on 504db690.
No candidate snapshot reuse, no periodic cache checkpoint, no second core.
"""
from pathlib import Path
import re
def apply(root:Path):
    def edit(rel,old,new):
        path=root/rel
        s=path.read_text()
        if s.count(old)!=1: raise RuntimeError("Order recovery source drift "+rel+": "+old[:100])
        path.write_text(s.replace(old,new,1))
    rp="src/shader_recompiler/ir/passes/resource_patching_pass.cpp"
    # Two texture descriptors with different R128 width or depth interpretation
    # must not share a descriptor resource even if their fetch expression is equal.
    edit(rp,"return desc.sharp_fetch == existing.sharp_fetch && desc.is_array == existing.is_array &&",
         """return desc.sharp_fetch == existing.sharp_fetch && desc.is_array == existing.is_array &&
                   desc.is_r128 == existing.is_r128 && desc.is_depth == existing.is_depth &&""")
    # R128 is authoritative from the original MIMG opcode. Never read an
    # adjacent descriptor as the high half if IR discovery produced only 4 words.
    path=root/rp
    src=path.read_text()
    start=src.index("    ImageResource image_res = {")
    end=src.index("\n    };",start)+len("\n    };")
    src=src[:end]+"\n"+"""    const u32 expected_words=image_res.is_r128 ? 4u : 8u;
    if (resource.sharps[0].num_dwords!=expected_words) {
        LOG_WARNING(Render_Recompiler,
                    "BACHATA_TSHARP_WIDTH_MISMATCH shader={:#x} r128={} discovered={}",
                    info.pgm_hash,image_res.is_r128,resource.sharps[0].num_dwords);
        // Missing high words are not a valid 256-bit resource. Do not
        // reinterpret unknown data as a mapped texture.
        image_res.sharp_fetch.summary=SharpFetch<AmdGpu::Image>::Summary::Invalid;
    }
"""+src[end:]
    path.write_text(src)
    # Bounds and exact loaded-word provenance are needed at runtime, including
    # serialized shader metadata. Never infer R128 from the contents of T#.
    r="src/shader_recompiler/resource.h"
    edit(r,"    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {",
         """    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {
        const auto& flat=info.flattened_ud_buf;
        const u32 words=is_r128?4u:8u;
        const u64 element_off=u64{element}*array_stride_dw;
        if (array_size && element>=array_size) return AmdGpu::Image::Null(is_depth);
        for (u32 i=0;i<words;++i) {
            if (!(sharp_fetch.load_mask&(1u<<i))) continue;
            if (sharp_fetch.offsets[i]==UNKNOWN_LOCATION ||
                u64{sharp_fetch.offsets[i]}+element_off>=flat.size())
                return AmdGpu::Image::Null(is_depth);
        }
        // The SingleLoad path is valid only for a complete contiguous load.
        if (sharp_fetch.summary==SharpFetch<AmdGpu::Image>::Summary::SingleLoad) {
            if ((sharp_fetch.load_mask&((1u<<words)-1))!=((1u<<words)-1))
                return AmdGpu::Image::Null(is_depth);
            for (u32 i=1;i<words;++i)
                if (u32{sharp_fetch.offsets[i]}!=u32{sharp_fetch.offsets[0]}+i)
                    return AmdGpu::Image::Null(is_depth);
        }""")
    # Preserve the 504db690 fast path. If tracker and exact byte index
    # disagree, use the original ownership-aware readback for that page.
    bc="src/video_core/buffer_cache/buffer_cache.h"
    edit(bc,"    void TrackSrtSourcePage(VAddr page);",
         "    bool IsSrtPageGpuOwned(VAddr page);\\n    void TrackSrtSourcePage(VAddr page);")
    bc="src/video_core/buffer_cache/buffer_cache.cpp"
    edit(bc,"void BufferCache::TrackSrtSourcePage(VAddr page) {",
         """bool BufferCache::IsSrtPageGpuOwned(VAddr page) {
    return memory_tracker->IsRegionGpuModified(page,4096);
}
void BufferCache::TrackSrtSourcePage(VAddr page) {""")
    ras="src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    path=root/ras
    src=path.read_text()
    start=src.index("void Rasterizer::ReadBackGpuWrittenSrtSources")
    end=src.index("\n}\n",start)
    part=src[start:end]
    # The exact batch remains intact; add fallback only for missing provenance.
    needle="!buffer_cache.IsRangeGpuWritten(source,sizeof(u32))"
    if part.count(needle)!=1: raise RuntimeError("SRT exact source check drift")
    part=part.replace(needle,"(!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)) && !buffer_cache.IsSrtPageGpuOwned(page))",1)
    needle="        if (pages.empty() || !buffer_cache.DownloadSrtSourcePages(pages)) break;"
    if part.count(needle)!=1: raise RuntimeError("SRT batch completion drift")
    part=part.replace(needle,"""        if (pages.empty()) break;
        bool changed=buffer_cache.DownloadSrtSourcePages(pages);
        for (const VAddr page:pages) {
            if (!buffer_cache.IsSrtPageGpuOwned(page)) continue;
            buffer_cache.ReadMemory(page,PageSize,false,true);
            changed=true;
        }
        if (!changed) break;""",1)
    path.write_text(src[:start]+part+src[end:])
    # Avoid filesystem directory creation/lookup on every new permutation
    # when neither patching nor collection is enabled.
    pc="src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    edit(pc,'    auto patch = GetShaderPatch(info.pgm_hash, info.hw_stage, perm_idx, "spv");',
         """    std::optional<std::vector<u32>> patch;
    if (EmulatorSettings.IsPatchShaders() || EmulatorSettings.IsShaderCollect())
        patch=GetShaderPatch(info.pgm_hash,info.hw_stage,perm_idx,"spv");""")
    from port_vertex_unused_rates import apply as apply_rates
    apply_rates(root)
    p=root/"src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    s,n=re.subn(r"ShaderBinaryVersion = (\d+)u;",lambda m:f"ShaderBinaryVersion = {int(m.group(1))+103}u;",p.read_text())
    if n!=1: raise RuntimeError("shader cache version drift")
    p.write_text(s)
    return {"descriptor":"distinct R128/depth, full width and bounds checks",
            "srt":"retain batch, tracker-owned fallback; preserve pointer provenance",
            "spikes":"unused vertex rates and disabled shader patch lookup"}
