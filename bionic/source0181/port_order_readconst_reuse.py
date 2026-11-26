#!/usr/bin/env python3
"""Route large Order constant sources through the existing tracked buffer cache.

The donor copies only small read-only resources into its constant ring. The
previous snapshot adaptation copied even multi-MiB CPU-owned V# resources on
every binding, bypassing MemoryTracker's dirty-page upload transaction.
"""
from pathlib import Path


METRICS = r'''// BACHATA_ORDER_READCONST_REUSE: count actual cache uploads, not an
// address-only memo or an assumption that a repeated binding was unchanged.
static_assert(VideoCore::BufferCache::ReadConstStreamThreshold() == 16_KB);
struct OrderReadConstReuseWindow {
    u64 start_us{}, bindings{}, requested_bytes{}, snapshot_bindings{}, snapshot_bytes{};
    u64 cache_upload_bytes{}, bind_us{}, max_us{};
    bool reported{};

    void Add(u64 now, u64 elapsed, u64 bytes, bool snapshot, u64 uploaded) {
        if (!start_us) start_us = now - elapsed;
        ++bindings;
        requested_bytes += bytes;
        snapshot_bindings += snapshot;
        snapshot_bytes += snapshot ? bytes : 0;
        cache_upload_bytes += uploaded;
        bind_us += elapsed;
        max_us = std::max(max_us, elapsed);
        if (reported && now - start_us < 2'000'000) return;
        const auto wall_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        LOG_INFO(Render_Vulkan,
            "BACHATA_ORDER_READCONST_REUSE wall_ms={} window_us={} bindings={} requested_bytes={} "
            "snapshot_bindings={} snapshot_bytes={} cache_bindings={} cache_upload_bytes={} "
            "bind_us={} max_us={}",
            wall_ms, now - start_us, bindings, requested_bytes, snapshot_bindings,
            snapshot_bytes, bindings - snapshot_bindings, cache_upload_bytes, bind_us, max_us);
        start_us = now;
        bindings = requested_bytes = snapshot_bindings = snapshot_bytes = 0;
        cache_upload_bytes = bind_us = max_us = 0;
        reported = true;
    }
};

struct OrderReadConstReuseSample {
    OrderReadConstReuseSample(VideoCore::BufferCache& cache_, bool active_, u64 bytes_)
        : cache{cache_}, active{active_}, bytes{bytes_},
          begin{active ? OrderReadConstCostSample::NowUs() : 0},
          uploaded_before{active ? cache.ReadConstUploadBytes() : 0} {}
    ~OrderReadConstReuseSample() {
        if (!active) return;
        const u64 now = OrderReadConstCostSample::NowUs();
        thread_local OrderReadConstReuseWindow window;
        window.Add(now, now - begin, bytes, snapshot,
                   cache.ReadConstUploadBytes() - uploaded_before);
    }
    VideoCore::BufferCache& cache;
    const bool active;
    const u64 bytes, begin, uploaded_before;
    bool snapshot{};
};

'''


def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Order ReadConst reuse source drift {label}: {count}")
    return text.replace(old, new, 1)


def apply(root: Path) -> dict:
    path = root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    text = path.read_text()
    text = one(text, "void Rasterizer::BindBuffers(",
               METRICS + "void Rasterizer::BindBuffers(", "measurement helpers")
    text = one(text,
               '            const bool shadow = Common::ElfInfo::Instance().GameSerial() == "CUSA08809";\n',
               '            const bool shadow = Common::ElfInfo::Instance().GameSerial() == "CUSA08809";\n'
               '            const bool order_readconst = BachataCompat::Order1886() && desc.used_as_readconst;\n',
               "strict source range policy")
    text = one(text, "((readconst || shadow) ? memory->ClampGpuRangeSize",
               "((readconst || shadow || order_readconst) ? memory->ClampGpuRangeSize",
               "constant-source VMA clamp")
    text = one(text,
               '                // Prefer the Release\'s immutable constant-source snapshot\n',
               '                OrderReadConstReuseSample readconst_reuse{\n'
               '                    buffer_cache, order_readconst && !desc.is_written, size};\n'
               '                // Prefer the Release\'s immutable constant-source snapshot\n',
               "tracked binding observation")
    old = '''                    if (BachataCompat::Order1886()) {
                        ASSERT(order_readconst_arena);
                        pooled = MakePooledReadConstSnapshot(
                            instance, memory, *order_readconst_arena, vsharp.base_address, size);
                    } else {'''
    new = '''                    if (BachataCompat::Order1886()) {
                        // The donor ring copies only small CPU constants. Large
                        // aligned sources retain the full descriptor span in
                        // ObtainBuffer: only CPU-dirty pages upload again.
                        // Keep an immutable aligned copy for non-DWORD bases;
                        // rounding their offset would change shader addresses.
                        if (size <= VideoCore::BufferCache::ReadConstStreamThreshold() ||
                            (vsharp.base_address & 3) != 0) {
                            ASSERT(order_readconst_arena);
                            pooled = MakePooledReadConstSnapshot(
                                instance, memory, *order_readconst_arena, vsharp.base_address, size);
                        }
                    } else {'''
    text = one(text, old, new, "small snapshot / tracked large binding")
    text = one(text,
               "                bound_buffers.emplace_back(buffer, offset, size, desc.is_written);\n",
               "                bound_buffers.emplace_back(buffer, offset, size, desc.is_written);\n"
               "                readconst_reuse.snapshot = pooled.buffer != nullptr;\n",
               "observe actual snapshot selection")
    path.write_text(text)

    header = root / "src/video_core/buffer_cache/buffer_cache.h"
    h = header.read_text()
    h = one(h, "#include <deque>", "#include <atomic>\n#include <deque>",
            "explicit atomic upload observation")
    h = one(h, "    [[nodiscard]] bool IsRegionCpuModified(VAddr addr, size_t size);",
            "    [[nodiscard]] static constexpr u64 ReadConstStreamThreshold() noexcept {\n"
            "        return STREAM_THRESHOLD;\n"
            "    }\n\n"
            "    // CPU bytes gathered by the real dirty-page upload transaction.\n"
            "    [[nodiscard]] u64 ReadConstUploadBytes() const noexcept {\n"
            "        return cpu_upload_bytes.load(std::memory_order_relaxed);\n"
            "    }\n\n"
            "    [[nodiscard]] bool IsRegionCpuModified(VAddr addr, size_t size);",
            "upload observation accessor")
    h = one(h, "    StreamBuffer stream_buffer;", "    std::atomic<u64> cpu_upload_bytes{};\n"
            "    StreamBuffer stream_buffer;", "upload byte counter")
    header.write_text(h)
    source = root / "src/video_core/buffer_cache/buffer_cache.cpp"
    c = source.read_text()
    c = one(c, "    }, [&] {\n    if (total_size_bytes>64_MB",
            "    }, [&] {\n    cpu_upload_bytes.fetch_add(total_size_bytes, std::memory_order_relaxed);\n"
            "    if (total_size_bytes>64_MB", "count actual dirty pages")
    source.write_text(c)
    return {
        "ported": "Order donor small-copy threshold and tracked reuse of large ReadConst sources",
        "scope": "CUSA00785 Android only; other games retain immutable snapshots",
        "range": "strict VMA/storage range; no truncation to the 16 KiB copy threshold",
        "reuse": "existing MemoryTracker dirty pages and BufferCache GPU provenance",
        "preserved": "FEX physical alias, small/unaligned held snapshots, CPU/GPU invalidations",
        "measurement": "BACHATA_ORDER_READCONST_REUSE actual upload bytes and binding cost per 2 s",
    }
