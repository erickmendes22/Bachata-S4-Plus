#!/usr/bin/env python3
"""Keep compatible Order attachment passes open after consuming metadata clears.

Adapt the active donor BeginRendering group to the 0.18.1 recorder contract.
New clears use an owned deferred closure, never the recorder's unsupported
generic thunk for vkCmdClearAttachments' pointer arguments.
"""
from pathlib import Path


STATE_CONTRACT = '''struct RenderState {
    std::array<RenderAttachment, 8> color_attachments;
    RenderAttachment depth_stencil_attachment;
    u16 width;
    u16 height;
    u16 num_layers;
    u16 num_color_attachments;

    bool operator==(const RenderState& other) const noexcept {
        return std::memcmp(this, &other, sizeof(RenderState)) == 0;
    }
};'''


HELPERS = r'''// BACHATA_ORDER_RENDER_PASS: preserve the donor's complete attachment
// identity test. RenderState fixes storeOp=STORE, resolveMode=NONE, viewMask=0
// and renderArea.offset={0,0}; an identical view also fixes format and samples.
static bool UsesOrderRenderPassCoalescing() {
#ifdef __ANDROID__
    if (Common::ElfInfo::Instance().GameSerial() != "CUSA00785") return false;
    static const bool enabled = [] {
        const char* env = std::getenv("ORDER1886_COALESCE_CLEAR_PASS");
        return !env || env[0] != '0';
    }();
    return enabled;
#else
    return false;
#endif
}

static bool UsesOrderInlineAttachmentClear() {
    static const bool enabled = [] {
        const char* env = std::getenv("ORDER1886_INLINE_ATTACHMENT_CLEAR");
        return !env || env[0] != '0';
    }();
    return enabled;
}

// A loadOp clear on a new scope is retained when an attachment aspect is
// read-only. Do not introduce clearAttachments into an incompatible layout.
static bool OrderInlineClearLayoutCompatible(const RenderState& state) {
    for (u32 i = 0; i < state.num_color_attachments; ++i) {
        const auto& cb = state.color_attachments[i];
        if (!cb.is_clear || !cb.image_view) continue;
        if (cb.image_layout != vk::ImageLayout::eColorAttachmentOptimal &&
            cb.image_layout != vk::ImageLayout::eGeneral &&
            cb.image_layout != vk::ImageLayout::eAttachmentFeedbackLoopOptimalEXT) return false;
    }
    const auto& ds = state.depth_stencil_attachment;
    if (!ds.image_view) return true;
    if (ds.has_depth && ds.depth_clear &&
        ds.image_layout != vk::ImageLayout::eGeneral &&
        ds.image_layout != vk::ImageLayout::eDepthStencilAttachmentOptimal &&
        ds.image_layout != vk::ImageLayout::eDepthAttachmentOptimal &&
        ds.image_layout != vk::ImageLayout::eDepthAttachmentStencilReadOnlyOptimal) return false;
    if (ds.has_stencil && ds.stencil_clear &&
        ds.image_layout != vk::ImageLayout::eGeneral &&
        ds.image_layout != vk::ImageLayout::eDepthStencilAttachmentOptimal &&
        ds.image_layout != vk::ImageLayout::eStencilAttachmentOptimal &&
        ds.image_layout != vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal) return false;
    return true;
}

enum class OrderRenderPassEvent : u32 { Begin, End, Same, PostClear, InlineClear, Count };
static void CountOrderRenderPass(OrderRenderPassEvent event) {
    struct Window {
        std::array<u64, static_cast<u32>(OrderRenderPassEvent::Count)> counts{};
        std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
        u32 unchecked{};
    };
    thread_local Window window;
    ++window.counts[static_cast<u32>(event)];
    // No clock, allocation or logging on each draw. Observe a compact window
    // after 1024 pass decisions, with at most one line per five seconds/thread.
    if (++window.unchecked < 1024) return;
    window.unchecked = 0;
    const auto now = std::chrono::steady_clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(now-window.start).count();
    if (elapsed < 5'000'000) return;
    const auto wall_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    const auto& c = window.counts;
    LOG_INFO(Render_Vulkan,
        "BACHATA_ORDER_RENDER_PASS wall_ms={} window_us={} begins={} ends={} same={} "
        "post_clear={} inline_clear={}", wall_ms, elapsed, c[0], c[1], c[2], c[3], c[4]);
    window.start = now;
    window.counts = {};
}

'''


OLD_BEGIN = '''    if (is_rendering && render_state == new_state) {
        return;
    }
    EndRendering();
    is_rendering = true;
    render_state = new_state;
'''

NEW_BEGIN = r'''    const bool order_pass_coalescing = UsesOrderRenderPassCoalescing();
    if (is_rendering) {
        // A fresh metadata clear is a transaction even when its value and
        // attachments equal the last draw. A persistent depth-clear register,
        // without new metadata consumption, retains the existing behavior.
        if (render_state == new_state && !(order_pass_coalescing && metadata_clear_consumed)) {
            if (order_pass_coalescing) CountOrderRenderPass(OrderRenderPassEvent::Same);
            return;
        }
        if (order_pass_coalescing) {
            // Normalize only clear requests/values. Views, layouts, dimensions,
            // layers and attachment/aspect identities must remain identical.
            if (UsesOrderInlineAttachmentClear() && new_state.num_layers > 0 &&
                new_state.num_layers <= 16 && OrderInlineClearLayoutCompatible(new_state)) {
                RenderState compared = render_state;
                for (u32 i = 0; i < new_state.num_color_attachments; ++i) {
                    compared.color_attachments[i].is_clear = new_state.color_attachments[i].is_clear;
                    compared.color_attachments[i].clear_value = new_state.color_attachments[i].clear_value;
                }
                compared.depth_stencil_attachment.depth_clear = new_state.depth_stencil_attachment.depth_clear;
                compared.depth_stencil_attachment.stencil_clear = new_state.depth_stencil_attachment.stencil_clear;
                compared.depth_stencil_attachment.clear_value = new_state.depth_stencil_attachment.clear_value;
                if (compared == new_state) {
                    std::array<vk::ClearAttachment, 9> clears{};
                    u32 count = 0;
                    for (u32 i = 0; i < new_state.num_color_attachments; ++i) {
                        const auto& color = new_state.color_attachments[i];
                        if (!color.is_clear || !color.image_view) continue;
                        clears[count++] = vk::ClearAttachment{
                            .aspectMask = vk::ImageAspectFlagBits::eColor,
                            .colorAttachment = i,
                            .clearValue = vk::ClearValue{
                                .color = vk::ClearColorValue{.uint32 = color.clear_value}},
                        };
                    }
                    const auto& ds = new_state.depth_stencil_attachment;
                    vk::ImageAspectFlags aspects{};
                    if (ds.has_depth && ds.depth_clear) aspects |= vk::ImageAspectFlagBits::eDepth;
                    if (ds.has_stencil && ds.stencil_clear) aspects |= vk::ImageAspectFlagBits::eStencil;
                    if (aspects && ds.image_view) {
                        clears[count++] = vk::ClearAttachment{
                            .aspectMask = aspects,
                            .colorAttachment = 0,
                            .clearValue = vk::ClearValue{.depthStencil = vk::ClearDepthStencilValue{
                                .depth = std::bit_cast<float>(ds.clear_value[0]),
                                .stencil = ds.clear_value[1]}},
                        };
                    }
                    if (count) {
                        const vk::ClearRect rect{
                            .rect = {.offset = {0, 0}, .extent = {new_state.width, new_state.height}},
                            .baseArrayLayer = 0, .layerCount = new_state.num_layers,
                        };
                        // vkCmdClearAttachments has pointer arguments. Its
                        // arrays must remain owned until the recorder consumes
                        // the call; use the existing fake-to-real bridge.
                        RecordDeferred([clears, count, rect](vk::CommandBuffer cmdbuf) {
                            cmdbuf.clearAttachments(count, clears.data(), 1, &rect);
                        });
                        render_state = new_state;
                        CountOrderRenderPass(OrderRenderPassEvent::InlineClear);
                        return;
                    }
                }
            }
            bool requests_clear = new_state.depth_stencil_attachment.depth_clear ||
                                  new_state.depth_stencil_attachment.stencil_clear;
            for (u32 i = 0; i < new_state.num_color_attachments; ++i) {
                requests_clear |= new_state.color_attachments[i].is_clear != 0;
            }
            if (!requests_clear) {
                RenderState prior = render_state;
                for (u32 i = 0; i < new_state.num_color_attachments; ++i) {
                    prior.color_attachments[i].is_clear = 0;
                    prior.color_attachments[i].clear_value = new_state.color_attachments[i].clear_value;
                }
                prior.depth_stencil_attachment.depth_clear = false;
                prior.depth_stencil_attachment.stencil_clear = false;
                prior.depth_stencil_attachment.clear_value = new_state.depth_stencil_attachment.clear_value;
                if (prior == new_state) {
                    // The previous loadOp already cleared these attachments.
                    // Keep the tiles in the current pass, preserving all draws.
                    render_state = new_state;
                    CountOrderRenderPass(OrderRenderPassEvent::PostClear);
                    return;
                }
            }
        }
    }
    EndRendering();
    is_rendering = true;
    render_state = new_state;
    if (order_pass_coalescing) CountOrderRenderPass(OrderRenderPassEvent::Begin);
'''


def one(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"Order pass coalescing anchor drift: {label}: {text.count(old)}")
    return text.replace(old, new, 1)


def validate_contract(text: str, header: str) -> None:
    if header.count(STATE_CONTRACT) != 1:
        raise RuntimeError("Order pass coalescing: RenderState identity contract changed")
    begin = text.index("void Scheduler::BeginRendering(const RenderState& new_state) {")
    end = text.index("void Scheduler::EndRendering()", begin)
    rendering = text[begin:end]
    if (rendering.count(".storeOp = vk::AttachmentStoreOp::eStore,") != 3 or
        any(field in rendering for field in (".resolveMode", ".resolveImageView", ".resolveImageLayout",
                                              ".viewMask", ".flags")) or
        rendering.count(".offset = {0, 0},") != 1 or
        rendering.count(".layerCount = render_state.num_layers,") != 1):
        raise RuntimeError("Order pass coalescing: fixed STORE/resolve/viewMask/renderArea contract changed")


def apply(root: Path) -> dict:
    path = Path(root) / "src/video_core/renderer_vulkan/vk_scheduler.cpp"
    text = path.read_text()
    header = path.with_suffix(".h").read_text()
    validate_contract(text, header)
    if '#include "common/elf_info.h"' not in text:
        text = '#include "common/elf_info.h"\n' + text
    text = '#include <array>\n#include <bit>\n#include <chrono>\n#include <cstdlib>\n' + text
    text = one(text, "void Scheduler::BeginRendering(const RenderState& new_state) {",
               HELPERS + "void Scheduler::BeginRendering(const RenderState& new_state, bool metadata_clear_consumed) {", "helpers")
    text = one(text, OLD_BEGIN, NEW_BEGIN, "BeginRendering clear transition")
    text = one(text, "    is_rendering = false;\n    CommandBuffer().endRendering();",
               "    is_rendering = false;\n    CommandBuffer().endRendering();\n"
               "    if (UsesOrderRenderPassCoalescing()) CountOrderRenderPass(OrderRenderPassEvent::End);",
               "pass boundary observation")
    path.write_text(text)
    header = one(header, "    void BeginRendering(const RenderState& new_state);",
                 "    void BeginRendering(const RenderState& new_state, bool metadata_clear_consumed = false);",
                 "explicit fresh metadata transaction")
    path.with_suffix(".h").write_text(header)

    rasterizer = Path(root) / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    r = rasterizer.read_text()
    r = one(r, "RenderState Rasterizer::BeginRendering(const GraphicsPipeline* pipeline) {",
            "RenderState Rasterizer::BeginRendering(const GraphicsPipeline* pipeline, bool& metadata_clear_consumed) {\n"
            "    metadata_clear_consumed = false;", "clear consumption output")
    r = one(r, "        const bool is_clear = texture_cache.IsMetaCleared(col_buf.CmaskAddress(), slice);\n"
               "        texture_cache.TouchMeta(col_buf.CmaskAddress(), slice, false);",
            "        const bool is_clear = texture_cache.IsMetaCleared(col_buf.CmaskAddress(), slice);\n"
            "        metadata_clear_consumed |= texture_cache.TouchMeta(col_buf.CmaskAddress(), slice, false);",
            "CMask consumption")
    r = one(r, "                texture_cache.TouchMeta(htile_address, slice + layer, false);",
            "                // Call TouchMeta even when another attachment already consumed a clear.\n"
            "                metadata_clear_consumed |=\n"
            "                    texture_cache.TouchMeta(htile_address, slice + layer, false) && is_depth_clear;",
            "HTile consumption")
    old_state = "    const auto state = BeginRendering(pipeline);"
    old_begin = "    scheduler.BeginRendering(state);"
    if r.count(old_state) != 2 or r.count(old_begin) != 2:
        raise RuntimeError("Order pass coalescing: both direct/indirect draw consumers required")
    r = r.replace(old_state, "    bool metadata_clear_consumed = false;\n"
                            "    const auto state = BeginRendering(pipeline, metadata_clear_consumed);")
    r = r.replace(old_begin, "    scheduler.BeginRendering(state, metadata_clear_consumed);")
    rasterizer.write_text(r)
    rh = rasterizer.with_suffix(".h")
    rh.write_text(one(rh.read_text(), "    RenderState BeginRendering(const GraphicsPipeline* pipeline);",
                      "    RenderState BeginRendering(const GraphicsPipeline* pipeline, bool& metadata_clear_consumed);",
                      "rasterizer consumption output ABI"))
    return {"order_render_pass_coalescing": "metadata-clear-load + owned-inline-clear"}
