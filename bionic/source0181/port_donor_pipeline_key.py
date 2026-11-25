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
            // In this 0.18.1 FEX renderer GetUserData reads the per-stage
            // Flatbuf descriptor, not a packed push-constant SGPR offset.
            // A genuinely resource-free stage has no Flatbuf dependency.
            // If inconsistent metadata advertises one, require identical bindings.
            return (!info->has_flatbuf && !other.info->has_flatbuf) || start==other.start;
        }""")
    p.write_text(s)
    # Bump incompatible metadata, since earlier SPIR-V might contain an
    # incorrect push-constant offset from a reused resource-free variant.
    # Version and cache path are determined by the preceding donor contract.
    return {"graphics_key":"byte-preserving copy and zero-reset",
            "resource_free_shader":"FEX per-stage Flatbuf binding contract; no donor-only push-constant ABI",
            "cpu":"FEX","fps":"original"}
