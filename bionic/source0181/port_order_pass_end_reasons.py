"""Account only real closures of open Order passes, by producer and owner.

No new wait, barrier, submission or rendering decision is introduced. The
existing render-pass counters remain unchanged. Presenter annotations are a
separate final overlay so the presentation/FIFO family owns that source flow.
"""
from pathlib import Path


HEADER = r'''#pragma once

namespace Vulkan {
enum class OrderPassEndReason : unsigned {
    Unspecified, RenderState, Submission, BufferCopy, BufferFill, InlineData,
    ImageRefresh, ImageUpload, ImageDownload, ImageCopy, ImageAlias, Resolve,
    ImageClear, BackingSamples, Barrier, Dispatch, IndirectClamp, Tiling,
    Blit, FaultBuffer, PipelineRetire, Present, Count
};
} // namespace Vulkan
'''


COUNTER = r'''// BACHATA_ORDER_PASS_END_REASON: only EndRendering's open-pass branch
// calls this function. Buckets belong to a scheduler AND the calling thread.
// No clock or log per draw, per no-op EndRendering, or per sampled decision.
static void CountOrderPassEndReason(const void* owner, OrderPassEndReason reason) {
    struct Window {
        const void* owner{};
        std::array<u64, static_cast<unsigned>(OrderPassEndReason::Count)> counts{};
        std::chrono::steady_clock::time_point start{};
        u64 total{};
        u32 unchecked{};
        void Emit(std::chrono::steady_clock::time_point now) {
            if (!total) return;
            const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(now-start).count();
            const auto wall = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
            LOG_INFO(Render_Vulkan,
                "BACHATA_ORDER_PASS_END_REASON owner={} thread={} wall_ms={} window_us={} total={} "
                "other={} state={} submit={} buffer_copy={} buffer_fill={} inline_data={} "
                "image_refresh={} image_upload={} image_download={} image_copy={} image_alias={} "
                "resolve={} image_clear={} backing_samples={} barrier={} dispatch={} "
                "indirect_clamp={} tiling={} blit={} faults={} pipeline_retire={} present={}",
                reinterpret_cast<std::uintptr_t>(owner), std::hash<std::thread::id>{}(std::this_thread::get_id()),
                wall, elapsed, total, counts[0], counts[1], counts[2], counts[3], counts[4],
                counts[5], counts[6], counts[7], counts[8], counts[9], counts[10], counts[11],
                counts[12], counts[13], counts[14], counts[15], counts[16], counts[17],
                counts[18], counts[19], counts[20], counts[21]);
            counts.fill(0);total=0;unchecked=0;start=now;
        }
    };
    thread_local std::array<Window, 8> windows{};
    Window* window{};
    for (auto& candidate : windows) {
        if (candidate.owner == owner) { window=&candidate;break; }
        if (!candidate.owner && !window) window=&candidate;
    }
    if (!window) {
        // More than eight scheduler owners on one thread is exceptional. Emit
        // the displaced bucket rather than mixing its counts with another owner.
        window=&windows[0];window->Emit(std::chrono::steady_clock::now());
    }
    if (window->owner != owner) {
        window->owner=owner;window->start=std::chrono::steady_clock::now();
    }
    ++window->counts[static_cast<unsigned>(reason)];++window->total;
    if (++window->unchecked < 1024) return;
    window->unchecked=0;
    const auto now=std::chrono::steady_clock::now();
    if (now-window->start >= std::chrono::seconds(5)) window->Emit(now);
}

'''


CALLS = {
    "video_core/renderer_vulkan/vk_scheduler.cpp": {
        "void Scheduler::BeginRendering(": "RenderState",
        "void Scheduler::EndSession()": "Submission",
    },
    "video_core/renderer_vulkan/vk_runtime.cpp": {
        "void Runtime::CopyBuffer(": "BufferCopy",
        "void Runtime::FillBuffer(": "BufferFill",
        "void Runtime::InlineData(": "InlineData",
        "void Runtime::UploadImage(": "ImageUpload",
        "void Runtime::DownloadImage(": "ImageDownload",
        "void Runtime::CopyAliasImage(": "ImageAlias",
        "void Runtime::CopyImage(": "ImageCopy",
        "void Runtime::CopyImageWithBuffer(": "ImageCopy",
        "void Runtime::CopyMip(": "ImageCopy",
        "void Runtime::CopyDepthStencil(": "ImageCopy",
        "void Runtime::ResolveImage(": "Resolve",
        "void Runtime::ClearImage(": "ImageClear",
        "void Runtime::SetBackingSamples(": "BackingSamples",
        "void Runtime::FlushBarriers()": "Barrier",
    },
    "video_core/renderer_vulkan/vk_rasterizer.cpp": {
        "void Rasterizer::DispatchDirect(": "Dispatch",
        "void Rasterizer::DispatchIndirect(": "Dispatch",
        "std::vector<Rasterizer::ClampedIndirectBatch> Rasterizer::ClampIndexedIndirect(": "IndirectClamp",
    },
    "video_core/texture_cache/texture_cache.cpp": {
        "void TextureCache::RefreshImage(": "ImageRefresh",
    },
    "video_core/texture_cache/tile_manager.cpp": {
        "std::pair<const Buffer*, u64> TileManager::DetileImage(": "Tiling",
    },
    "video_core/texture_cache/blit_helper.cpp": {
        "void BlitHelper::ReinterpretColorAsMsDepth(": "Blit",
        "void BlitHelper::CopyBetweenMsImages(": "Blit",
    },
    "video_core/buffer_cache/fault_manager.cpp": {
        "void FaultManager::ProcessFaultBuffer()": "FaultBuffer",
    },
    "video_core/renderer_vulkan/vk_pipeline_cache.cpp": {
        "void PipelineCache::ReclaimOrderGraphics()": "PipelineRetire",
    },
}


def function_span(text: str, signature: str) -> tuple[int, int]:
    if text.count(signature) != 1:
        raise RuntimeError(f"Pass-end reason function drift: {signature}")
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return start, end


def annotate(root: Path, calls: dict[str, dict[str, str]]) -> None:
    for name, functions in calls.items():
        path = root / "src" / name
        text = path.read_text()
        for signature, reason in functions.items():
            start, end = function_span(text, signature)
            body = text[start:end]
            if body.count("EndRendering();") != 1:
                raise RuntimeError(f"Pass-end reason caller drift: {name}: {signature}")
            replacement = body.replace("EndRendering();", "EndRendering(Vulkan::OrderPassEndReason::" + reason + ");")
            text = text[:start] + replacement + text[end:]
        path.write_text(text)


def apply(root):
    root = Path(root)
    path = root / "src/video_core/renderer_vulkan/order_render_pass_reasons.h"
    if path.exists():
        raise RuntimeError("Order pass-end reason overlay already applied")
    path.write_text(HEADER)
    header = root / "src/video_core/renderer_vulkan/vk_scheduler.h"
    text = header.read_text()
    old = "    void EndRendering();"
    if text.count(old) != 1:
        raise RuntimeError("Pass-end reason Scheduler declaration drift")
    text = '#include "video_core/renderer_vulkan/order_render_pass_reasons.h"\n' + text
    header.write_text(text.replace(old, "    void EndRendering(OrderPassEndReason reason = OrderPassEndReason::Unspecified);"))
    source = root / "src/video_core/renderer_vulkan/vk_scheduler.cpp"
    text = source.read_text()
    old = "enum class OrderRenderPassEvent : u32"
    assert text.count(old) == 1
    text = text.replace(old, COUNTER + old, 1)
    old = "void Scheduler::EndRendering() {"
    assert text.count(old) == 1
    text = text.replace(old, "void Scheduler::EndRendering(OrderPassEndReason reason) {", 1)
    old = "    if (UsesOrderRenderPassCoalescing()) CountOrderRenderPass(OrderRenderPassEvent::End);"
    assert text.count(old) == 1
    text = text.replace(old, old + "\n    if (UsesOrderRenderPassCoalescing()) CountOrderPassEndReason(this, reason);", 1)
    source.write_text(text)
    annotate(root, CALLS)
    return {"actual_open_passes_only": True, "clock_sampling": 1024,
            "window_seconds": 5, "group": "scheduler and calling thread",
            "presentation_annotations": "apply separately after present queue progress"}

