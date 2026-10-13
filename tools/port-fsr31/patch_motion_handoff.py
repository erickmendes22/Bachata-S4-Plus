#!/usr/bin/env python3
"""Connect core025 native ObjectMotion RT7 to the immutable-image Port FSR3 bridge.

Called only after patch_motion_raster.py has created ObjectMotion and the G-buffer
per-draw tracking. No synthesized flow, no modification to PS4 guest targets.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
header=root/"src/video_core/renderer_vulkan/vk_rasterizer.h"
cpp=root/"src/video_core/renderer_vulkan/vk_rasterizer.cpp"
def update(path,changes):
    src=path.read_text()
    for old,new,expected in changes:
        n=src.count(old)
        if n!=expected:raise RuntimeError(f"{path.name}: source mismatch {n}/{expected} {old[:72]!r}")
        src=src.replace(old,new)
    path.write_text(src)
update(header,[(
    "    u64 object_motion_generation{~u64{0}};",
    """    u64 object_motion_generation{~u64{0}};
    u32 object_motion_width{};
    u32 object_motion_height{};
    bool object_motion_handed_off{};""",1
)])
update(cpp,[
("namespace Vulkan {\n\nstatic Shader::PushData MakeUserData",
"""namespace Vulkan {

// The exact ten Bloodborne Scaleform VS hashes from Port ui_composition.h.
static constexpr bool PortMovieShader(u64 hash) {
    return hash==0x34e8a281 || hash==0x81d336ce ||
           hash==0x09957251 || hash==0x24042a9b ||
           hash==0xa400228b || hash==0xbb4d5f8c ||
           hash==0xe94b5b06 || hash==0x9951d199 ||
           hash==0x44072322 || hash==0xa334a845;
}

static Shader::PushData MakeUserData""",1),
("                object_motion.OnFrameStart();\n                object_motion_generation=current;",
"""                object_motion.OnFrameStart();
                object_motion_generation=current;
                object_motion_handed_off=false;
                object_motion_width=object_motion_height=0;""",2),
("""    if(pipeline->GetGraphicsKey().motion_vectors && object_motion.Enabled())
        object_motion.Attach(state,state.width,state.height);""",
"""    if(pipeline->GetGraphicsKey().motion_vectors && object_motion.Enabled()) {
        object_motion.Attach(state,state.width,state.height);
        object_motion_width=state.width;
        object_motion_height=state.height;
    }""",2),
("""    const auto [vertex_offset, instance_offset] = GetDrawOffsets(regs, vs_info, fetch_shader);
    if(pipeline->GetGraphicsKey().motion_vectors""",
"""    const auto [vertex_offset, instance_offset] = GetDrawOffsets(regs, vs_info, fetch_shader);
    // Transition the extra G-buffer motion attachment BEFORE the Port's first
    // identified UI draw triggers FSR, while preserving the command ordering.
    if(object_motion.Enabled() && !object_motion_handed_off &&
       object_motion_width && object_motion_height &&
       PortMovieShader(vs_info.pgm_hash)) {
        scheduler.EndRendering();
        bool valid=false;
        const auto object_view=object_motion.PrepareRead(
            object_motion_width,object_motion_height,valid);
        if(valid && object_view) {
            using SupplyFn=int(*)(VkCommandBuffer,VkImageView,VkExtent2D);
            static auto supply=reinterpret_cast<SupplyFn>(
                dlsym(RTLD_DEFAULT,"bs4_fsr31_supply_port_object"));
            if(supply) {
                const auto cb=scheduler.CommandBuffer();
                object_motion_handed_off=
                    supply(static_cast<VkCommandBuffer>(cb),
                           static_cast<VkImageView>(object_view),
                           VkExtent2D{object_motion_width,object_motion_height})!=0;
            }
        }
    }
    if(pipeline->GetGraphicsKey().motion_vectors""",1)
])
print("PASS: Port RT7 native-to-FSR Vulkan handoff at first verified UI shader")
