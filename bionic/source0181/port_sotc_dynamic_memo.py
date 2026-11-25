"""SotC draw-side exact-state memo, adapted to the single-threaded FEX GPU command path.

Unlike donor DrawRelSerial, this tracks the bytes of the actual fields read by the
0.18.1 Update*State functions. No hash collision, no new draw thread, no change to
register writes. Scheduler.Commit still runs after every draw, including after
command-buffer changes and host blits that invalidate dynamic state.
"""
from pathlib import Path

def apply(root: Path):
    h=root/"src/video_core/renderer_vulkan/vk_rasterizer.h"
    c=root/"src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    def replace(p,a,b):
        s=p.read_text()
        if s.count(a)!=1: raise RuntimeError(f"draw memo source drift: {p}: {a[:100]}")
        p.write_text(s.replace(a,b,1))
    replace(h, '#include "common/recursive_lock.h"',
        '#include <vector>\n#include "common/recursive_lock.h"')
    replace(h, '    bool attachment_feedback_loop{};',
        '''    // The dynamic state values live in Scheduler; Invalidate only marks dirty.
    mutable std::vector<u8> dynamic_inputs;
    mutable bool dynamic_inputs_valid{};
    bool attachment_feedback_loop{};''')
    replace(c, '#include <algorithm>', '#include <algorithm>\n#include <cstring>\n#include <type_traits>')
    replace(c,'''void Rasterizer::UpdateDynamicState(const GraphicsPipeline* pipeline, const bool is_indexed) const {
    UpdateViewportScissorState();
    UpdateDepthStencilState();
    UpdatePrimitiveState(is_indexed);
    UpdateRasterizationState();
    UpdateColorBlendingState(pipeline);

    auto& dynamic_state = scheduler.GetDynamicState();
    dynamic_state.Commit(instance, scheduler.CommandBuffer());
}''','''void Rasterizer::UpdateDynamicState(const GraphicsPipeline* pipeline, const bool is_indexed) const {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const bool enabled=serial=="CUSA08809"||serial=="CUSA08034";
    bool same=false;
    if(enabled) {
        const auto& regs=liverpool->regs;
        size_t offset=0;
        same=dynamic_inputs_valid;
        const auto add=[&](const auto& value) {
            using T=std::remove_cvref_t<decltype(value)>;
            static_assert(std::is_trivially_copyable_v<T>);
            const size_t end=offset+sizeof(T);
            if(dynamic_inputs.size()<end) {dynamic_inputs.resize(end);same=false;}
            auto* dst=dynamic_inputs.data()+offset;
            if(!same||std::memcmp(dst,&value,sizeof(T))!=0) {
                std::memcpy(dst,&value,sizeof(T));
                same=false;
            }
            offset=end;
        };
        // Exactly the inputs consumed by UpdateViewportScissorState,
        // UpdateDepthStencilState, UpdatePrimitiveState, UpdateRasterizationState
        // and UpdateColorBlendingState in this pinned source tree.
        add(regs.screen_scissor);add(regs.window_scissor);add(regs.generic_scissor);
        add(regs.window_offset);add(regs.polygon_control);add(regs.viewport_control);
        add(regs.viewports);add(regs.viewport_depths);add(regs.viewport_scissors);
        add(regs.clipper_control);add(regs.mode_control);add(regs.primitive_type);
        add(regs.depth_control);add(regs.depth_buffer);add(regs.depth_render_control);
        add(regs.depth_bounds_min);add(regs.depth_bounds_max);add(regs.poly_offset);
        add(regs.stencil_control);add(regs.stencil_ref_front);add(regs.stencil_ref_back);
        add(regs.enable_primitive_restart);add(regs.primitive_restart_index);
        add(regs.line_control);add(regs.blend_constants);
        add(pipeline->GetGraphicsKey().write_masks);
        add(attachment_feedback_loop);add(is_indexed);
        dynamic_inputs_valid=true;
    } else {
        dynamic_inputs_valid=false;
    }
    if(!same) {
        UpdateViewportScissorState();
        UpdateDepthStencilState();
        UpdatePrimitiveState(is_indexed);
        UpdateRasterizationState();
        UpdateColorBlendingState(pipeline);
    }
    // Rebind after command buffer reset or a host blit even on a memo hit.
    auto& dynamic_state = scheduler.GetDynamicState();
    dynamic_state.Commit(instance, scheduler.CommandBuffer());
}''')
    return {"scope":"SotC serials only","comparison":"exact input bytes, no hash, no stale guest pointer",
            "commit":"every draw; respects scheduler invalidation"}
