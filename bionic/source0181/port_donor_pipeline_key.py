"""Exact donor key semantics: byte-stable graphics keys and SGPR-only shaders.

Reference JulioCacko/The-Order-1886_pc c53cd01 and inherited 91aa3ac.
Retain FEX and the existing per-permutation effective resource Info.
"""
from pathlib import Path

def apply(root:Path):
    p=root/"src/video_core/renderer_vulkan/vk_graphics_pipeline.h"
    s=p.read_text()
    old="""    GraphicsPipelineKey() {
        std::memset(this, 0, sizeof(*this));
    }"""
    assert s.count(old)==1
    s=s.replace(old,"""    GraphicsPipelineKey() {
        std::memset(static_cast<void*>(this),0,sizeof(*this));
    }
    // Hash and equality cover padding too. Preserve every byte on copy.
    GraphicsPipelineKey(const GraphicsPipelineKey& other) noexcept {
        std::memcpy(static_cast<void*>(this),&other,sizeof(*this));
    }
    GraphicsPipelineKey& operator=(const GraphicsPipelineKey& other) noexcept {
        if (this!=&other)
            std::memcpy(static_cast<void*>(this),&other,sizeof(*this));
        return *this;
    }""")
    p.write_text(s)
    p=root/"src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    s=p.read_text()
    old="    std::memset(&graphics_key, 0, sizeof(GraphicsPipelineKey));"
    assert s.count(old)==1
    p.write_text(s.replace(old,"    graphics_key=GraphicsPipelineKey{};"))
    p=root/"src/shader_recompiler/specialization.h"
    s=p.read_text()
    old="""        if (buffers.empty() && images.empty() && fmasks.empty() && samplers.empty() &&
            other.buffers.empty() && other.images.empty() && other.fmasks.empty() && other.samplers.empty()) {
            return true;
        }"""
    assert s.count(old)==1
    s=s.replace(old,"""        if (buffers.empty() && images.empty() && fmasks.empty() && samplers.empty() &&
            other.buffers.empty() && other.images.empty() && other.fmasks.empty() && other.samplers.empty()) {
            // A resource-free shader can still read SGPR push constants.
            // Their compiled offset is part of the translation contract.
            return start.user_data == other.start.user_data ||
                   (!info->ud_mask.mask && !other.info->ud_mask.mask);
        }""")
    p.write_text(s)
    # Bump incompatible metadata, since earlier SPIR-V might contain an
    # incorrect push-constant offset from a reused resource-free variant.
    # Version and cache path are determined by the preceding donor contract.
    return {"graphics_key":"byte-preserving copy and zero-reset",
            "resource_free_shader":"correct user-data offset matching",
            "cpu":"FEX","fps":"original"}
