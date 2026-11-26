#!/usr/bin/env python3
"""Keep Order CPU ReadConst snapshots in the existing fenced staging pool.

The previous Release snapshot adaptation allocates a BDA-capable, dedicated VMA
buffer for every binding. The current Order donor keeps constant copies in a
fenced ring. Suballocate held blocks from 0.18.1's StagingBufferPool; release full
blocks only after recording their consumer, since another binding can submit
and complete the reservation tick before that consumer is recorded.
"""
from pathlib import Path


ARENA = r'''// A buffer binding can trigger a stream wrap/readback and submit its old
// tick before the draw which consumes these bytes is recorded. Keep whole
// staging blocks held through recording, then retire at the consumer's tick.
class OrderReadConstArena {
public:
    explicit OrderReadConstArena(StagingBufferPool& pool_) : pool{pool_} {}
    ~OrderReadConstArena() {
        ASSERT(recording_depth == 0);
        RetireRecorded();
        if (current.buffer) pool.FreeDeferred(current);
    }

    void BeginRecording() { ++recording_depth; }
    void EndRecording() {
        ASSERT(recording_depth != 0);
        if (--recording_depth == 0) RetireRecorded();
    }

    StagingBufferRef Request(u64 size, u64 alignment) {
        ASSERT(recording_depth != 0 && size != 0 && alignment != 0);
        u64 begin = current.buffer ? Common::AlignUp(offset, alignment) : 0;
        if (!current.buffer || begin > current.size || size > current.size - begin) {
            if (current.buffer) pending.push_back(current);
            // Transfer ownership before Request can throw. The recording guard
            // must retire the old block exactly once even on allocation failure.
            current = {};
            offset = begin = 0;
            // Deferred is per 16-MiB block, never per small snapshot. No ring
            // reservation can overwrite a held block after an internal Flush.
            current = pool.Request(std::max<u64>(16_MB, size),
                VideoCore::MemoryType::HostUncached, alignment, true, false);
        }
        if (!current.mapped || begin > current.size || size > current.size - begin) return {};
        const StagingBufferRef result{
            .buffer = current.buffer,
            .offset = current.offset + begin,
            .size = size,
            .mapped = current.mapped + begin,
            .type = current.type,
        };
        offset = begin + size;
        return result;
    }

private:
    void RetireRecorded() {
        // Guard/destructor cleanup must not allocate, including when current
        // ends exactly full and pending has never allocated any storage.
        for (const auto& block : pending) pool.FreeDeferred(block);
        pending.clear();
        if (current.buffer && offset == current.size) {
            pool.FreeDeferred(current);
            current = {};
            offset = 0;
        }
    }

    StagingBufferPool& pool;
    StagingBufferRef current{};
    u64 offset{};
    u32 recording_depth{};
    std::vector<StagingBufferRef> pending;
};

struct OrderReadConstRecordScope {
    OrderReadConstRecordScope(std::unique_ptr<OrderReadConstArena>& owned,
                             StagingBufferPool& pool) {
        if (!BachataCompat::Order1886()) return;
        if (!owned) owned = std::make_unique<OrderReadConstArena>(pool);
        arena = owned.get();
        arena->BeginRecording();
    }
    ~OrderReadConstRecordScope() {
        if (arena) arena->EndRecording();
    }
    OrderReadConstArena* arena{};
};

'''


COST = r'''// BACHATA_ORDER_READCONST_POOL: compact per-thread windows, not per-draw logs.
struct OrderReadConstCostWindow {
    u64 start_us{}, calls{}, snapshots{}, bytes{}, cpu_us{}, max_us{};
    bool reported{};

    void Add(u64 now_us, u64 elapsed_us, u64 copied_bytes) {
        if (!start_us) start_us = now_us - elapsed_us;
        ++calls;
        snapshots += copied_bytes != 0;
        bytes += copied_bytes;
        cpu_us += elapsed_us;
        max_us = std::max(max_us, elapsed_us);
        if (reported && now_us - start_us < 2'000'000) return;
        const auto wall_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        LOG_INFO(Render_Vulkan,
            "BACHATA_ORDER_READCONST_COST storage=pool wall_ms={} window_us={} calls={} snapshots={} bytes={} cpu_us={} max_us={}",
            wall_ms, now_us - start_us, calls, snapshots, bytes, cpu_us, max_us);
        start_us = now_us;
        calls = snapshots = bytes = cpu_us = max_us = 0;
        reported = true;
    }
};

struct OrderReadConstCostSample {
    static u64 NowUs() {
        return std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();
    }
    const u64 begin_us = NowUs();
    u64 copied_bytes{};
    ~OrderReadConstCostSample() {
        const u64 end_us = NowUs();
        thread_local OrderReadConstCostWindow cost;
        cost.Add(end_us, end_us - begin_us, copied_bytes);
    }
};

'''


POOLED = r'''StagingBufferRef MakePooledReadConstSnapshot(
    const Instance& instance, Core::MemoryManager* memory, OrderReadConstArena& arena,
    VAddr address, u64 bytes) {
    OrderReadConstCostSample cost;
    if (bytes == 0 || bytes > 8_MB || address > UINT64_MAX - bytes) return {};
    void* map_start{};
    void* map_end{};
    u32 prot{};
    if (memory->QueryProtection(address, &map_start, &map_end, &prot) != 0 ||
        (prot & static_cast<u32>(Core::MemoryProt::CpuRead)) == 0 ||
        address < reinterpret_cast<VAddr>(map_start) ||
        address + bytes > reinterpret_cast<VAddr>(map_end)) return {};

    const u64 atom = std::max<u64>(1, instance.NonCoherentAtomSize());
    const u64 alloc_size = Common::AlignUp(std::max<u64>(bytes, atom), atom);
    const u64 alignment = std::max<u64>(atom, instance.StorageMinAlignment());
    const auto snapshot = arena.Request(alloc_size, alignment);
    if (!snapshot.mapped || snapshot.size < alloc_size) return {};
    memory->CopySparseMemory(address, snapshot.mapped, bytes);
    if (alloc_size > bytes) std::memset(snapshot.mapped + bytes, 0, alloc_size - bytes);
    snapshot.Flush();
    cost.copied_bytes = bytes;
    return snapshot;
}

'''


OLD_SELECTION = r'''                std::shared_ptr<VideoCore::Buffer> isolated;
                if (desc.used_as_readconst && !desc.is_written && size!=0 &&
                    !buffer_cache.IsRegionGpuModified(vsharp.base_address,size)) {
                    isolated=MakeReadConstSnapshot(instance,memory,vsharp.base_address,size);
                }
                const VideoCore::Buffer* buffer{};
                u64 offset{};
                if (isolated) {'''

NEW_SELECTION = r'''                std::shared_ptr<VideoCore::Buffer> isolated;
                StagingBufferRef pooled{};
                if (desc.used_as_readconst && !desc.is_written && size!=0 &&
                    !buffer_cache.IsRegionGpuModified(vsharp.base_address,size)) {
                    if (BachataCompat::Order1886()) {
                        ASSERT(order_readconst_arena);
                        pooled = MakePooledReadConstSnapshot(
                            instance, memory, *order_readconst_arena, vsharp.base_address, size);
                    } else {
                        isolated=MakeReadConstSnapshot(instance,memory,vsharp.base_address,size);
                    }
                }
                const VideoCore::Buffer* buffer{};
                u64 offset{};
                if (pooled.buffer) {
                    buffer = pooled.buffer;
                    offset = pooled.offset;
                } else if (isolated) {'''


def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Order ReadConst pool source drift {label}: {count}")
    return text.replace(old, new, 1)


def apply(root: Path) -> dict:
    path = root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    text = path.read_text()
    for include in (
        "#include <chrono>",
        "#include <vector>",
        '#include "common/bachata_compat_profile.h"',
        '#include "video_core/renderer_vulkan/vk_staging_buffer_pool.h"',
    ):
        if include not in text.splitlines():
            text = include + "\n" + text
    text = one(text, "static Shader::PushData MakeUserData(",
               ARENA + "static Shader::PushData MakeUserData(", "held-block arena")
    # Each scope starts before the first resource binding and covers all later
    # early returns, index/indirect processing and the actual consumer. Nested scope
    # exits cannot release an outer consumer's pending blocks.
    scope = ("    OrderReadConstRecordScope readconst_recording{\n"
             "        order_readconst_arena, runtime.GetStagingPool()};\n")
    for name in ("Draw", "DrawIndirect", "DispatchDirect", "DispatchIndirect"):
        start = text.index("void Rasterizer::" + name + "(")
        binding = text.index("    if (!BindResources(pipeline)) {", start)
        text = text[:binding] + scope + text[binding:]
    text = one(text, "std::shared_ptr<VideoCore::Buffer> MakeReadConstSnapshot(",
               COST + POOLED + "std::shared_ptr<VideoCore::Buffer> MakeReadConstSnapshot(",
               "immutable CPU snapshot helper")
    text = one(text, OLD_SELECTION, NEW_SELECTION, "snapshot storage selection")
    path.write_text(text)
    header = root / "src/video_core/renderer_vulkan/vk_rasterizer.h"
    h = one(header.read_text(), "class Runtime;",
            "class Runtime;\nclass OrderReadConstArena;", "arena forward declaration")
    h = one(h, "    Runtime& runtime;", "    Runtime& runtime;\n"
            "    std::unique_ptr<OrderReadConstArena> order_readconst_arena;",
            "arena ownership before runtime destruction")
    header.write_text(h)
    return {
        "ported": "Order CPU ReadConst snapshot storage in the existing fenced staging pool",
        "preserved": "bytes, VMA/readability, 8 MiB limit, padding, flush, GPU-authoritative fallback",
        "lifetime": "held 16 MiB blocks through draw/dispatch record; FreeDeferred at final tick",
        "scope": "CUSA00785 on Android; legacy snapshot behavior retained for other games",
        "measurement": "BACHATA_ORDER_READCONST_COST first sample and at most once every 2 seconds",
    }
