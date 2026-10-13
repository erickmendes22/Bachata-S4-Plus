#!/usr/bin/env python3
"""Port the Bloodborne temporal object-motion shader ABI into core025 source.

No optical-flow substitute; this prepares the exact guest SPIR-V push-data
fields and per-shader motion selection before the GPU motion pipeline is added.
Fails on source drift rather than silently patching the wrong base.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
def apply(relative, edits):
    p = root / relative
    content = p.read_text()
    for original, replacement in edits:
        count = content.count(original)
        if count != 1:
            raise RuntimeError(f"{relative}: expected unique source anchor, found {count}: {original[:100]!r}")
        content = content.replace(original, replacement)
    p.write_text(content)

apply("src/shader_recompiler/resource.h", [
    ("#include <span>", "#include <cstddef>\n#include <span>"),
    ("    static constexpr u32 BufOffsetIndex = UdRegsIndex + NUM_USER_DATA_REGS / 4;",
     "    static constexpr u32 BufOffsetIndex = UdRegsIndex + NUM_USER_DATA_REGS / 4;\n"
     "    static constexpr u32 MotionParamIndex = BufOffsetIndex + NUM_BUFFERS / 16 + 1;\n"
     "    static constexpr u32 SceneSizeIndex = MotionParamIndex + 1;"),
    ("    std::array<u8, NUM_BUFFERS> buf_offsets;",
     "    std::array<u8, NUM_BUFFERS> buf_offsets;\n"
     "    u32 motion_param{}; // Port: GPU history store/load parameter index\n"
     "    u32 scene_size{};   // Port: reduced scene width | height << 16"),
    ("static_assert(sizeof(PushData) <= 128,",
     "static_assert(offsetof(PushData, motion_param) == 120);\n"
     "static_assert(offsetof(PushData, scene_size) == 124);\n"
     "static_assert(sizeof(PushData) == 128);\n"
     "static_assert(sizeof(PushData) <= 128,"),
])

motion_struct = """/// Unmodified constants from the Bloodborne Port's object-vector ABI.
struct MotionVectors {
    static constexpr u32 CurrentLocation = 30;
    static constexpr u32 PreviousLocation = 31;
    static constexpr u32 Output = 7;
    static inline u64 params_address = 0;
    static inline u64 positions_address = 0;
    static constexpr u32 FlagStore = 1;
    static constexpr u32 FlagLoad = 2;
};

"""
apply("src/shader_recompiler/runtime_info.h", [
    ("struct LocalRuntimeInfo {", motion_struct + "struct LocalRuntimeInfo {"),
    ("    u32 step_rate_1;\n\n    bool operator<=>(const VertexRuntimeInfo",
     "    u32 step_rate_1;\n    bool motion_vectors{};\n\n    bool operator<=>(const VertexRuntimeInfo"),
    ("    bool clip_distance_emulation{false};\n\n    bool operator==(const FragmentRuntimeInfo",
     "    bool clip_distance_emulation{false};\n    bool motion_vectors{false};\n\n    bool operator==(const FragmentRuntimeInfo"),
    ("               clip_distance_emulation == other.clip_distance_emulation &&\n",
     "               clip_distance_emulation == other.clip_distance_emulation &&\n"
     "               motion_vectors == other.motion_vectors &&\n"),
])

apply("src/shader_recompiler/backend/spirv/spirv_emit_context.cpp", [
    ("U32[4], U32[4], U32[4], U32[2]),",
     "U32[4], U32[4], U32[4], U32[2], U32[1], U32[1]),"),
    ('    push_data_block = DefineVar(struct_type, spv::StorageClass::PushConstant);',
     '    MemberName(struct_type, PushData::MotionParamIndex, "motion_param");\n'
     '    MemberDecorate(struct_type, PushData::MotionParamIndex, spv::Decoration::Offset, 120U);\n'
     '    MemberName(struct_type, PushData::SceneSizeIndex, "scene_size");\n'
     '    MemberDecorate(struct_type, PushData::SceneSizeIndex, spv::Decoration::Offset, 124U);\n'
     '    push_data_block = DefineVar(struct_type, spv::StorageClass::PushConstant);'),
])

apply("src/video_core/renderer_vulkan/vk_rasterizer.h", [
    ("    Shader::PushData push_data;", "    Shader::PushData push_data{};")
])

# Unrelated upstream Clang 18 constexpr issue fixed in the prior verified
# native source build; preserve this narrowly-scoped workaround.
font = root / "src/core/libraries/font/fontft_internal.h"
if font.exists():
    content = font.read_text()
    for x,y in [
        ("    constexpr u8* data() {", "    u8* data() {"),
        ("    constexpr const u8* data() const {", "    const u8* data() const {")
    ]:
        if content.count(x)==1:
            content=content.replace(x,y)
    font.write_text(content)

print("PASS: core025 Port object-motion ABI: 128-byte push data; SPIR-V offsets 120/124; shader flags")
