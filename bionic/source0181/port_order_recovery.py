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
    # Restore the exact high-FPS base SRT batch path. The broad fallback in
    # 273b5e3 did not resolve rejected descriptors and regressed measured FPS.
    # Fix cache replay contamination independently of descriptor interpretation.
    ser="src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    edit(ser,"""            bool result{};
            if (is_compute) {""",
         """            // A prior rejected archive entry may have loaded only some stages.
            // Never inherit its shader/module/runtime state in the next pipeline.
            infos.fill(nullptr);
            modules.fill(nullptr);
            runtime_infos.fill({});
            fetch_shader=nullptr;
            bool result{};
            if (is_compute) {""")
    # Capture exact T# source locations only on actual footprint rejection.
    ras="src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    edit(ras,"""                LOG_WARNING(Render_Vulkan,
                    "BACHATA_ORDER_IMAGE_SPAN_REJECT shader={:#x} addr={:#x} size={:#x}",
                    stage.pgm_hash,info.guest_address,info.guest_size);""",
         """                static u32 rejected_sharps=0;
                const u32 reject_n=++rejected_sharps;
                if (reject_n<=32 || reject_n%512==0) {
                    LOG_WARNING(Render_Vulkan,
                        "BACHATA_ORDER_IMAGE_SPAN_REJECT shader={:#x} addr={:#x} size={:#x} r128={} mask={:#x} flat={} offsets={} count={}",
                        stage.pgm_hash,info.guest_address,info.guest_size,image_desc.is_r128,
                        image_desc.sharp_fetch.load_mask,stage.flattened_ud_buf.size(),
                        image_desc.sharp_fetch.offsets,reject_n);
                }""")
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
            "srt":"restore exact 504db690 batch; no broad fallback",
            "spikes":"unused vertex rates and disabled shader patch lookup"}
