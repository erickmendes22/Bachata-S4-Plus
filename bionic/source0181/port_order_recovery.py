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
    edit(rp,"    auto image = image_res.GetSharp(info);",
         """    const u32 expected_words=image_res.is_r128 ? 4u : 8u;
    if (resource.sharps[0].num_dwords!=expected_words) {
        LOG_WARNING(Render_Recompiler,
                    "BACHATA_TSHARP_WIDTH_MISMATCH shader={:#x} r128={} discovered={}",
                    info.pgm_hash,image_res.is_r128,resource.sharps[0].num_dwords);
        // Missing high words are not a valid 256-bit resource. Do not
        // reinterpret unknown data as a mapped texture.
        image_res.sharp_fetch.summary=SharpFetch<AmdGpu::Image>::Summary::Invalid;
    }
    auto image = image_res.GetSharp(info);""")
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
    # Existing exact write tracking drops page-level producer provenance.
    # The legacy tracker is the authority for GPU ownership, even when the
    # byte-range side index is incomplete. Use the ordinary precise readback.
    bc="src/video_core/buffer_cache/buffer_cache.cpp"
    edit(bc,"    return gpu_modified_ranges.Intersects(addr,size);",
         """    return gpu_modified_ranges.Intersects(addr,size) ||
           memory_tracker->IsRegionGpuModified(addr,size);""")
    ras="src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    path=root/ras
    s=path.read_text()
    begin=s.index("    std::unordered_set<VAddr> visited;",s.index("void Rasterizer::ReadBackGpuWrittenSrtSources"))
    end=s.index("\n}\n",begin)
    s=s[:begin]+"""    for(unsigned pass=0;pass<4;++pass) {
        std::unordered_set<VAddr> visited;
        bool changed=false;
        for(const auto source:stage.srt_guest_sources) {
            if(source<0x10000 || source>=0x10000000000ULL) continue;
            const VAddr page=source&PageMask;
            if(visited.contains(page) ||
               !buffer_cache.IsRangeGpuWritten(source,sizeof(u32)) ||
               !IsMapped(page,PageSize)) continue;
            visited.insert(page);
            buffer_cache.TrackSrtSourcePage(page);
            buffer_cache.ReadMemory(page,PageSize,false,true);
            changed=true;
        }
        if(!changed)break;
        auto& writable=const_cast<Shader::Info&>(stage);
        writable.RefreshFlatBuf();
    }"""+s[end:]
    path.write_text(s)
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
            "srt":"restore tracker-owned readback path; preserve pointer provenance",
            "spikes":"unused vertex rates and disabled shader patch lookup"}
