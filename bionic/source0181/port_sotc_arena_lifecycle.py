"""Adapt SotC's active arena allocation/eviction contract to the FEX buffer cache.

Effective donor: PC 732cb37d3470 + Android stage 0366868550. The included
methods preserve the donor's cold comparison, pin-on-fault and sparse ordering.
FEX backing aliases and the existing Android coherent first upload remain in use.
"""
from pathlib import Path


def apply(root: Path):
    root = Path(root)
    here = Path(__file__).parent

    def edit(rel, old, new):
        p = root / rel
        s = p.read_text()
        if s.count(old) != 1:
            raise RuntimeError(f"SotC arena lifecycle anchor drift: {rel}: {old[:100]}")
        p.write_text(s.replace(old, new, 1))

    bc = "src/video_core/buffer_cache/buffer_cache.cpp"
    bh = "src/video_core/buffer_cache/buffer_cache.h"
    tc = "src/video_core/texture_cache/texture_cache.cpp"
    th = "src/video_core/texture_cache/texture_cache.h"
    edit(bh, "#include <deque>", "#include <deque>\n#include <chrono>\n#include <map>\n#include <optional>\n#include <span>")
    edit(bh, "    void TickFrame();", """    void TickFrame();
    bool MaybeEvictCold(std::chrono::steady_clock::time_point now);
    void NoteFaultRebind(VAddr addr, u64 size);""")
    edit(bh, "    void EnsureResident(const Buffer* arena, u64 first_block, u64 last_block);",
         """    const Buffer* EnsureResident(const Buffer* arena, u64 first_block, u64 last_block);
    void EnsureResidentLegacy(const Buffer* arena, u64 first_block, u64 last_block);""")
    edit(bh, "    u32 arena_memory_type_index{};",
         (here / "inherited_shader/donor_sotc_arena_members.inc").read_text() +
         "\n    u32 arena_memory_type_index{};")
    edit(bc, "    blocks_per_arena_page_shift = ARENA_PAGE_BITS - block_shift;",
         """    blocks_per_arena_page_shift = ARENA_PAGE_BITS - block_shift;
    block_last_use = static_cast<u16*>(
        std::calloc(u64{blocks_per_arena_page} * NUM_ARENA_PAGES, sizeof(u16)));
    ASSERT_MSG(block_last_use, "No memory for the arena use table");
    epoch_start = std::chrono::steady_clock::now();
    const auto& properties = instance.GetMemoryProperties();
    for (u32 i = 0; i < properties.memoryTypeCount; ++i) {
        const auto& heap = properties.memoryHeaps[properties.memoryTypes[i].heapIndex];
        if (((reqs.memoryTypeBits >> i) & 1) &&
            !(heap.flags & vk::MemoryHeapFlagBits::eDeviceLocal)) {
            arena_fallback_memory_type_index = i;
            break;
        }
    }""")
    edit(bc, "BufferCache::~BufferCache() = default;", """BufferCache::~BufferCache() {
    std::free(block_last_use);
}""")
    edit(bc, "void BufferCache::EnsureResident(const Buffer* arena, u64 first_block, u64 last_block) {",
         "void BufferCache::EnsureResidentLegacy(const Buffer* arena, u64 first_block, u64 last_block) {")
    edit(bc, "    EnsureResident(arena, first_block, last_block);",
         "    arena = EnsureResident(arena, first_block, last_block);")
    edit(bc, "void BufferCache::TickFrame() {",
         (here / "inherited_shader/donor_sotc_arena_methods.inc").read_text() +
         "\nvoid BufferCache::TickFrame() {")
    # Keep the existing Android unmap/readback transaction, sharing the allocator's free path.
    p = root / bc
    s = p.read_text()
    start = s.index("        const auto handle=static_cast<VkDeviceMemory>(range.memory);", s.index("void BufferCache::ReleaseUnmappedArena"))
    end = s.index("\n    }\n    // 0.18.1 IntervalList", start)
    s = s[:start] + "        FreeArenaBlocks(range.memory, range.offset, range.end - range.start);" + s[end:]
    p.write_text(s)
    edit(bc, """    scheduler.Finish();
    // Donor ReleaseBlocks: Finish may have run deferred fault rebinds.
    // Never put those binds and their unbinds in the same sparse batch.
    collect();
    if(!pending_binds.empty())scheduler.Flush();""", """    // Finish can run completed fault callbacks that publish more sparse binds.
    // Retire each new batch before collecting the ranges to unbind: a Flush
    // after collect() could otherwise rebind a hole omitted by that snapshot.
    do {
        scheduler.Finish();
    } while (!pending_binds.empty());
    collect();""")
    edit(bc, "void BufferCache::SubmitPendingArenaBinds(Vulkan::SubmitInfo& info) {",
         """void BufferCache::SubmitPendingArenaBinds(Vulkan::SubmitInfo& info) {
    AdvanceUseEpoch(std::chrono::steady_clock::now());""")
    edit(bc, "    if (first>=end) return;\n    MarkReadbacksDirty(first<<block_shift,(end-first)<<block_shift);",
         """    if (first>=end) return;
    SubtractArenaIntervals(evicted_ranges, first, end);
    SubtractArenaIntervals(pinned_ranges, first, end);
    MarkReadbacksDirty(first<<block_shift,(end-first)<<block_shift);""")
    # Reserve the donor's four-page VA groups only for SotC. No physical memory is allocated here.
    edit(bc, """            const u64 base_block = Common::AlignDownPow2<u64>(first_block, blocks_per_arena_page);
            const u64 num_pages = last_page - first_page + 1;
            const auto* new_arena =
                &arenas.emplace_back(instance, base_block << block_shift,
                                     num_pages << ARENA_PAGE_BITS, MemoryType::Sparse);
            address_space[first_page] = new_arena;
            address_space[last_page] = new_arena;""", """            static const u64 configured_group = [] {
                const char* v = std::getenv("SOTC_ARENA_GROUP");
                const u64 n = v ? std::strtoull(v, nullptr, 10) : 4;
                return n && n <= NUM_ARENA_PAGES && std::has_single_bit(n) ? n : u64{1};
            }();
            const u64 group = IsSotcArena() ? configured_group : 1;
            u64 group_first = first_page & ~(group - 1);
            u64 group_last = group_first + group - 1;
            for (u64 page = group_first; page <= group_last; ++page) {
                if (page >= NUM_ARENA_PAGES || address_space[page]) {
                    group_first = first_page;
                    group_last = last_page;
                    break;
                }
            }
            if (last_page > group_last) {
                group_first = first_page;
                group_last = last_page;
            }
            const u64 num_pages = group_last - group_first + 1;
            const auto* new_arena =
                &arenas.emplace_back(instance, group_first << ARENA_PAGE_BITS,
                                     num_pages << ARENA_PAGE_BITS, MemoryType::Sparse);
            for (u64 page = group_first; page <= group_last; ++page) address_space[page] = new_arena;""")
    edit("src/video_core/buffer_cache/fault_manager.cpp",
         "            (void)buffer_cache.ObtainBuffer(start, end - start, false);",
         """            buffer_cache.NoteFaultRebind(start, end - start);
            (void)buffer_cache.ObtainBuffer(start, end - start, false);""")
    # OnSubmit is invoked after command/DrawPipe ordering has been reclaimed.
    edit("src/video_core/renderer_vulkan/vk_rasterizer.cpp",
         "    buffer_cache.TickFrame();",
         """    buffer_cache.TickFrame();
    if (!scheduler.IsRendering()) {
        buffer_cache.MaybeEvictCold(std::chrono::steady_clock::now());
    }""")
    edit(th, "    void RunGarbageCollector();", """    void RunGarbageCollector();
    void EmergencyCollect();""")
    # RefreshImage reaches the arena allocator while owning the image-cache mutex.
    # Trying a non-recursive mutex already owned by this thread is not a portable
    # recursion check, and collection could invalidate the image being refreshed.
    # Preserve the donor's depth/defer contract, then use try_lock for contention.
    edit(th, "#include <mutex>", "#include <atomic>\n#include <mutex>")
    edit(th, "    std::mutex mutex;", """    inline static thread_local u32 arena_refresh_depth{};
    std::atomic_bool arena_emergency_pending{};
    std::mutex mutex;""")
    edit(tc, "void TextureCache::RefreshImage(Image& image) {", """void TextureCache::RefreshImage(Image& image) {
    ++arena_refresh_depth;
    SCOPE_EXIT { --arena_refresh_depth; };""")
    edit(tc, "void TextureCache::RunGarbageCollector() {", """void TextureCache::EmergencyCollect() {
    if (arena_refresh_depth != 0) {
        arena_emergency_pending.store(true, std::memory_order_relaxed);
        return;
    }
    std::unique_lock lock{mutex, std::try_to_lock};
    if (!lock.owns_lock()) {
        arena_emergency_pending.store(true, std::memory_order_relaxed);
        return;
    }
    size_t remaining = 512;
    const u64 age = std::min<u64>(4, gc_tick);
    lru_cache.ForEachItemBelow(gc_tick - age, [&](ImageId image_id) {
        if (remaining == 0) return true;
        auto& image = slot_images[image_id];
        if (image.SafeToDownload()) {
            if (image.info.IsTiled()) return false;
            DownloadImageMemory(image_id);
        }
        FreeImage(image_id);
        --remaining;
        return false;
    });
}

void TextureCache::RunGarbageCollector() {
    if (arena_emergency_pending.exchange(false, std::memory_order_relaxed)) {
        EmergencyCollect();
    }""")
    return {"donor": "SotC 732cb37d3470 + Android stage 0366868550",
            "allocation": "64 MiB chunks, coalesced free runs, exact/fallback retry",
            "residency": "versioned hits, last-use epochs, four-page VA groups",
            "eviction": "1536 MiB threshold, 30 s idle, asynchronous compare, 64 MiB batches",
            "safety": "held staging, no GPU-dirty eviction, full sparse ordering, pin GPU fault rebind",
            "cpu": "FEX backing aliases and coherent first uploads preserved"}
