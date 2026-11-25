// Adapted from SotC PC 732cb37d3470 + Android staging 0366868550.
// SPDX-License-Identifier: GPL-2.0-or-later
namespace {
bool IsSotcArena() {
    const auto serial = Common::ElfInfo::Instance().GameSerial();
    return serial == "CUSA08809" || serial == "CUSA08034";
}
template <class T>
void SubtractArenaIntervals(IntervalList<T>& source, u64 first, u64 end) {
    IntervalList<T> retained;
    retained.Reserve(source.Size() + 1);
    for (const auto& range : source) {
        if (range.end <= first || range.start >= end) retained.Add(range);
        else {
            if (range.start < first) retained.Add(range.SubRange(range.start, first));
            if (range.end > end) retained.Add(range.SubRange(end, range.end));
        }
    }
    source = std::move(retained);
}
} // namespace

const Buffer* BufferCache::EnsureResident(const Buffer* arena, u64 first_block, u64 last_block) {
    if (!IsSotcArena()) {
        EnsureResidentLegacy(arena, first_block, last_block);
        return arena;
    }
    // sotc: binds check the same ranges thousands of times a frame, each a search of ~2,600
    // resident ranges (~2% of the command processor): ranges found resident are remembered
    // (64 slots by first block) until the resident set changes (resident_version).
    // sotc: the bind keeps its blocks out of MaybeEvictCold for SOTC_ARENA_EVICT_IDLE_S. A
    // cached range is stamped as a whole once per epoch (a 64 MiB binding is 1,024 blocks).
    const auto stamp = [this](u64 first, u64 end) {
        for (u64 block = first; block < end; ++block) {
            block_last_use[block] = use_epoch;
        }
    };
    auto& cached = resident_cache[(first_block * 0x9E3779B97F4A7C15ull) >> 58];
    if (cached.version == resident_version && first_block >= cached.first &&
        last_block < cached.end) {
        if (cached.epoch != use_epoch) {
            stamp(cached.first, cached.end);
            cached.epoch = use_epoch;
        }
        return arena;
    }
    stamp(first_block, last_block + 1);
    u32 resident_blocks{};
    IntervalList bind_ranges;
    resident_ranges.ForEachGap(first_block, last_block + 1, [&](u64 start, u64 end) {
        resident_blocks += end - start;
        bind_ranges.Add({start, end});
    });

    if (bind_ranges.Empty()) {
        cached = {resident_version, first_block, last_block + 1, use_epoch};
        return arena;
    }
    if (!evicted_ranges.Empty()) {
        for (const auto& range : bind_ranges) {
            SubtractArenaIntervals(evicted_ranges, range.start, range.end);
        }
    }



    // Memory first: running out of it may submit work (see AllocateArenaBlocks), which must not
    // happen with half of the binds queued.
    const u64 allocation_version = resident_version;
    boost::container::small_vector<std::pair<vk::DeviceMemory, u64>, 8> placements;
    for (const auto& range : bind_ranges) {
        placements.push_back(AllocateArenaBlocks(range.end - range.start));
    }

    // OOM recovery may run completed fault callbacks. They can fill one of these
    // gaps or migrate its VA arena while our reservations are still unpublished.
    // Return only the blocks reserved here; callbacks allocated disjoint offsets,
    // even when they share the same chunk. Then recompute gaps against their binds.
    const Buffer* current_arena = GetArena(first_block, last_block);
    if (resident_version != allocation_version || current_arena != arena) {
        size_t placement_index = 0;
        for (const auto& range : bind_ranges) {
            const auto [memory, offset] = placements[placement_index++];
            FreeArenaBlocks(memory, offset, range.end - range.start);
        }
        return EnsureResident(current_arena, first_block, last_block);
    }

    boost::container::small_vector<vk::BufferCopy, 8> copies;
    const auto staging =
        staging_pool.Request(resident_blocks * sizeof(vk::DeviceAddress), MemoryType::HostUncached);

    ArenaBinds* binds = BindsForArena(arena);
    auto* bda_addrs = reinterpret_cast<vk::DeviceAddress*>(staging.mapped);
    u64 offset = staging.offset;
    size_t placement_index = 0;
    for (const auto& range : bind_ranges) {
        const auto [device_memory, memory_block] = placements[placement_index++];
        Backing backing;
        backing.start = range.start;
        backing.end = range.end;
        backing.memory = device_memory;
        backing.offset = memory_block;
        resident_ranges.Add(backing);
        ++resident_version; // sotc: invalidates the merged DMA runs

        LOG_INFO(Render, "Making range start={}, end={} resident", backing.start, backing.end);

        const auto& bind = binds->binds.emplace_back(vk::SparseMemoryBind{
            .resourceOffset = (range.start << block_shift) - arena->cpu_addr,
            .size = (range.end - range.start) << block_shift,
            .memory = device_memory,
            .memoryOffset = memory_block << block_shift,
        });

        for (u32 block = 0; block < bind.size; block += block_size) {
            *(bda_addrs++) = arena->BufferDeviceAddress() + bind.resourceOffset + block;
        }
        const u64 copy_size = (backing.end - backing.start) * sizeof(vk::DeviceAddress);
        copies.emplace_back(offset, backing.start * sizeof(vk::DeviceAddress), copy_size);
        offset += copy_size;
    }

    staging.Flush();
    runtime.CopyBuffer(staging.buffer, bda_pagetable_buffer.get(), copies);
    return arena;
}

std::pair<vk::DeviceMemory, u64> BufferCache::AllocateArenaBlocks(u64 blocks) {
    // Room in a chunk of video memory, then in a chunk of system memory.
    const auto take = [&](u32 memory_type) -> std::optional<std::pair<vk::DeviceMemory, u64>> {
        for (auto& chunk : arena_chunks) {
            if (chunk->memory_type != memory_type) {
                continue;
            }
            for (auto it = chunk->free_runs.begin(); it != chunk->free_runs.end(); ++it) {
                if (it->second < blocks) {
                    continue;
                }
                const auto [start, length] = *it;
                chunk->free_runs.erase(it);
                if (length > blocks) {
                    chunk->free_runs.emplace(start + blocks, length - blocks);
                }
                chunk->used_blocks += blocks;
                return std::make_pair(chunk->memory, start);
            }
        }
        return std::nullopt;
    };
    vk::Result last_result = vk::Result::eSuccess;
    const auto grow = [&](u32 memory_type, bool exact = false)
        -> std::optional<std::pair<vk::DeviceMemory, u64>> {
        // exact: only the asked size, for a nearly full card that has no 64 MiB left (#137).
        const u64 chunk_blocks = exact ? blocks : std::max<u64>(ARENA_CHUNK_SIZE >> block_shift, blocks);
        const vk::MemoryAllocateInfo alloc_info = {
            .allocationSize = chunk_blocks << block_shift,
            .memoryTypeIndex = memory_type,
        };
        const auto [result, memory] = instance.GetDevice().allocateMemory(alloc_info);
        if (result != vk::Result::eSuccess) {
            last_result = result;
            return std::nullopt;
        }


        auto& chunk = arena_chunks.emplace_back(std::make_unique<ArenaChunk>());
        chunk->memory = memory;
        if (coherent_arena_upload && memory_type == arena_memory_type_index) {
            fresh_backings.push_back(memory);
        }
        chunk->memory_type = memory_type;
        chunk->free_runs.emplace(0, chunk_blocks);
        chunk_by_memory.emplace(static_cast<VkDeviceMemory>(memory), chunk.get());
        return take(memory_type);
    };
    if (auto placed = take(arena_memory_type_index)) {
        return *placed;
    }
    if (auto placed = grow(arena_memory_type_index)) {
        return *placed;
    }
    if (arena_fallback_memory_type_index) {
        // Keep running from system memory (slower GPU access) instead of aborting.
        static bool warned = false;
        if (!std::exchange(warned, true)) {
            LOG_WARNING(Render, "Video memory exhausted, placing new buffer memory in system RAM");
        }
        if (auto placed = take(*arena_fallback_memory_type_index)) {
            return *placed;
        }
        if (auto placed = grow(*arena_fallback_memory_type_index)) {
            return *placed;
        }
    }
    // Drop old cached images, wait for the GPU so their memory is really released, try again.
    LOG_WARNING(Render,
                "Video memory exhausted, collecting cached images (asked {} KB; in use {} MB of {} "
                "MB; arenas {} chunks, {} MB)",
                (blocks << block_shift) >> 10, instance.GetDeviceMemoryUsage() >> 20,
                instance.GetTotalMemoryBudget() >> 20, arena_chunks.size(),
                ArenaUsedBytes() >> 20);
    texture_cache.EmergencyCollect();
    scheduler.Finish();
    scheduler.PopPendingOperations();
    // Nested fault handling may have grown a chunk, or completed frees may have
    // returned a run. Reuse it before reserving another whole chunk.
    if (auto placed = take(arena_memory_type_index)) {
        return *placed;
    }
    if (auto placed = grow(arena_memory_type_index)) {
        return *placed;
    }
    // sotc: still no room for a whole chunk (#137: 6 GB cards): the asked size alone, then
    // system memory, before giving up.
    if (auto placed = grow(arena_memory_type_index, true)) {
        return *placed;
    }
    if (arena_fallback_memory_type_index) {
        if (auto placed = take(*arena_fallback_memory_type_index)) {
            return *placed;
        }
        if (auto placed = grow(*arena_fallback_memory_type_index, true)) {
            return *placed;
        }
    }
    // sotc: why the driver refused (a 1.3 MB request with half the video memory free, 12 GB card,
    // 15 GB of RAM: AjncSystem #385). Windows refuses allocations when the commit limit (RAM + page
    // file) is reached, whatever the card has free.
    LOG_CRITICAL(Render, "Arena allocation of {} KB refused: {}; in use {} MB of {} MB",
                 (blocks << block_shift) >> 10, vk::to_string(last_result),
                 instance.GetDeviceMemoryUsage() >> 20, instance.GetTotalMemoryBudget() >> 20);
    LOG_CRITICAL(Render, "Out of video and system memory for buffers; lower the video memory use "
                         "setting in the launcher (Economy)");
    ASSERT_MSG(false, "Failed to allocate buffer arena memory");
    return {};
}

u64 BufferCache::ArenaUsedBytes() const noexcept {
    u64 blocks = 0;
    for (const auto& chunk : arena_chunks) {
        blocks += chunk->used_blocks;
    }
    return blocks << block_shift;
}

void BufferCache::FreeArenaBlocks(vk::DeviceMemory memory, u64 start, u64 blocks) {
    const auto found = chunk_by_memory.find(static_cast<VkDeviceMemory>(memory));
    if (found == chunk_by_memory.end()) {
        // Non-SotC callers retain the original exact-allocation lifetime.
        const auto handle = static_cast<VkDeviceMemory>(memory);
        auto legacy = backing_blocks.find(handle);
        if (legacy != backing_blocks.end()) {
            legacy->second -= std::min(legacy->second, blocks);
            if (legacy->second == 0) {
                backing_blocks.erase(legacy);
                scheduler.DeferOperation([device = instance.GetDevice(), memory] {
                    device.freeMemory(memory);
                });
            }
        }
        return;
    }
    ArenaChunk& chunk = *found->second;
    chunk.used_blocks -= std::min(chunk.used_blocks, blocks);
    // Give the run back, merged with free neighbours.
    auto next = chunk.free_runs.lower_bound(start);
    if (next != chunk.free_runs.end() && next->first == start + blocks) {
        blocks += next->second;
        next = chunk.free_runs.erase(next);
    }
    if (next != chunk.free_runs.begin()) {
        const auto prev = std::prev(next);
        if (prev->first + prev->second == start) {
            start = prev->first;
            blocks += prev->second;
            chunk.free_runs.erase(prev);
        }
    }
    chunk.free_runs.emplace(start, blocks);
    if (chunk.used_blocks != 0) {
        return;
    }
    // Empty: give the memory back. The unbind is submitted before this tick's work, which
    // waits for it.

    chunk_by_memory.erase(found);
    std::erase_if(arena_chunks, [&](const auto& c) {
        if (c->memory != memory) {
            return false;
        }

        return true;
    });
    scheduler.DeferOperation([device = instance.GetDevice(), memory] { device.freeMemory(memory); });
}

void BufferCache::UnbindResident(std::span<const Backing> released) {
    for (const Backing& range : released) {
        // Split at arena page boundaries, each page may belong to a different arena.
        for (u64 start = range.start; start < range.end;) {
            const u64 page = start >> blocks_per_arena_page_shift;
            const u64 end = std::min(range.end, (page + 1) << blocks_per_arena_page_shift);
            if (const Buffer* arena = address_space[page]) {
                BindsForArena(arena)->binds.push_back(vk::SparseMemoryBind{
                    .resourceOffset = (start << block_shift) - arena->cpu_addr,
                    .size = (end - start) << block_shift,
                    .memory = {},
                    .memoryOffset = 0,
                });
            }
            start = end;
        }
        // Shaders reach arena memory through the BDA page table; a null entry faults the block
        // back in (fault buffer) instead of touching unbound memory.
        runtime.FillBuffer(bda_pagetable_buffer.get(), range.start * sizeof(vk::DeviceAddress),
                           (range.end - range.start) * sizeof(vk::DeviceAddress), 0u);
        FreeArenaBlocks(range.memory, range.offset, range.end - range.start);
    }
}

bool BufferCache::MaybeEvictCold(std::chrono::steady_clock::time_point now) {
    if (!IsSotcArena()) return false;
    // sotc: the game keeps its 4 GiB direct memory pool mapped and hands its addresses out
    // again and again, so arena blocks became resident once and stayed: ~45 MB/min in the
    // attract demo, over the 6 GB card's budget after ~40 minutes. Once resident arena memory
    // passes SOTC_ARENA_EVICT_MB (default 1536, 0 = never), allocations (4 MiB slabs or exact
    // ones) whose blocks were not bound for SOTC_ARENA_EVICT_IDLE_S (default 30) seconds and
    // hold no GPU-modified data go back, coldest first, up to SOTC_ARENA_EVICT_STEP_MB (default
    // 64) per check (every 2 s). Their guest pages are marked CPU-modified, so the next bind
    // uploads them again.
    // The arena does not always match guest memory on pages the tracker calls clean (attract
    // demo: 0-13,000 of 2,000-65,000 pages per run; mostly not image memory). Uploading guest
    // memory over those blanked whole scenes, so each allocation is read back first and goes
    // only when every page that is not CPU-modified is equal (a mismatch is tried again after
    // 60 s). Shaders reading arena memory through pointers fault an evicted block back in (one
    // frame of zeros); blocks that came back that way stay resident from then on.
    static const u64 limit = [] {
        const char* v = std::getenv("SOTC_ARENA_EVICT_MB");
        return (v ? std::strtoull(v, nullptr, 10) : 1536ull) << 20;
    }();
    static const u64 step = [] {
        const char* v = std::getenv("SOTC_ARENA_EVICT_STEP_MB");
        return std::max<u64>(v ? std::strtoull(v, nullptr, 10) : 64ull, 1) << 20;
    }();
    static const u16 idle_epochs = [] {
        const char* v = std::getenv("SOTC_ARENA_EVICT_IDLE_S");
        return static_cast<u16>(std::clamp<unsigned long>(v ? std::strtoul(v, nullptr, 10) : 30ul,
                                                          2ul, 30000ul));
    }();
    if (pending_eviction) {
        AdvanceUseEpoch(now);
        return FinishEviction(now, idle_epochs, false);
    }
    if (now < next_evict_check) {
        return false;
    }
    next_evict_check = now + std::chrono::seconds(2);
    AdvanceUseEpoch(now);
    const u64 resident = ArenaUsedBytes();
    if (limit == 0 || resident <= limit) {
        return false;
    }

    // sotc: with the 64 MiB chunks the unit is a resident range (its blocks go back to their
    // chunk, and a chunk left empty to the driver), not a whole allocation.
    struct Candidate {
        u16 age{0xFFFF}; // youngest block
        bool keep{};
        u64 bytes{};
        boost::container::small_vector<Backing, 4> ranges;
    };
    std::unordered_map<u64, Candidate> candidates;
    std::erase_if(evict_retry, [&](const auto& entry) { return entry.second <= now; });
    std::vector<std::pair<u16, u64>> order;
    for (const Backing& range : resident_ranges) {
        auto& candidate = candidates[range.start];
        for (u64 block = range.start; block < range.end && !candidate.keep; ++block) {
            const u16 age = static_cast<u16>(use_epoch - block_last_use[block]);
            candidate.age = std::min(candidate.age, age);
            candidate.keep = age < idle_epochs;
        }
        const VAddr addr = range.start << block_shift;
        const u64 size = (range.end - range.start) << block_shift;
        candidate.keep = candidate.keep || pinned_ranges.Overlaps(range.start, range.end) ||
                         memory_tracker->IsRegionGpuModified(addr, size) ||
                         gpu_modified_ranges.Intersects(addr, size) ||
                         evict_retry.contains(range.start) || size > step;
        candidate.bytes = size;
        candidate.ranges.push_back(range);
        if (!candidate.keep) {
            order.emplace_back(candidate.age, range.start);
        }
    }
    if (order.empty()) {
        next_evict_check = now + std::chrono::seconds(10); // all of it in use: look again later
        return false;
    }
    std::ranges::sort(order, std::greater{});

    // Read the coldest allocations back, up to `step` bytes of blocks.
    std::vector<EvictChoice> chosen;
    u64 total = 0;
    for (const auto& [age, key] : order) {
        if (total >= step || resident - total <= limit / 8 * 7) {
            break;
        }
        const Candidate& candidate = candidates[key];
        if (candidate.bytes > step - total) continue;
        EvictChoice& pick = chosen.emplace_back(EvictChoice{key, candidate.bytes, {}, candidate.ranges});
        for (const Backing& range : candidate.ranges) {
            // Split at arena page boundaries, each page may belong to a different arena.
            for (u64 start = range.start; start < range.end;) {
                const u64 page = start >> blocks_per_arena_page_shift;
                const u64 end = std::min(range.end, (page + 1) << blocks_per_arena_page_shift);
                pick.pieces.push_back({start << block_shift, (end - start) << block_shift, total});
                total += (end - start) << block_shift;
                start = end;
            }
        }
    }
    const auto download = staging_pool.Request(total, MemoryType::HostCached, 0, true);
    for (const EvictChoice& pick : chosen) {
        for (const EvictPiece& piece : pick.pieces) {
            const Buffer* arena = address_space[piece.addr >> ARENA_PAGE_BITS];
            if (!arena) {
                continue; // never resident: the comparison fails and the allocation stays
            }
            const vk::BufferCopy copy{arena->Offset(piece.addr), download.offset + piece.offset,
                                      piece.size};
            runtime.CopyBuffer(arena, download.buffer, std::span{&copy, 1});
        }
    }
    pending_eviction = PendingEviction{std::move(chosen), download, scheduler.CurrentTick(),
                                       now + std::chrono::seconds(5)};
    // sotc: SOTC_EVICT_ASYNC=0 waits for the read-back here, as before: scheduler.Finish() on the
    // command processor, ~50 ms per 64 MiB run, one late frame each.
    static const bool async = [] {
        const char* v = std::getenv("SOTC_EVICT_ASYNC");
        return !v || v[0] != '0';
    }();
    return async ? false : FinishEviction(now, idle_epochs, true);
}

bool BufferCache::FinishEviction(std::chrono::steady_clock::time_point now, u16 idle_epochs,
                                 bool wait) {
    // sotc: the unbind's sparse batch does not wait for earlier submits, so it goes only once
    // every command buffer submitted so far (the read-back's included) is done. The GPU catches
    // up within a frame or two at the benchmark scenes; after 5 s, or with `wait`, Finish() it.
    PendingEviction& pending = *pending_eviction;
    for (;;) {
        if (!scheduler.IsFree(pending.tick) || !scheduler.IsFree(scheduler.CurrentTick() - 1)) {
            if (!wait && now < pending.deadline) {
                return false;
            }
            scheduler.Finish();
            continue;
        }
        if (pending_binds.empty()) break;
        // Finish/Flush callbacks may rebind or dirty the same backing. Submit and
        // retire their bind batch before checking guards or comparing its bytes.
        // Async eviction keeps the download held while this new submit is busy.
        scheduler.Flush();
    }

    const auto& download = pending.download;
    download.buffer->Invalidate(download.offset, download.size);

    std::vector<Backing> released;
    std::array<u8, 4096> guest;
    for (const EvictChoice& pick : pending.chosen) {
        // Bound again, or written by the GPU, after the read-back was recorded: stays.
        bool keep = false;
        for (const Backing& range : pick.ranges) {
            for (u64 block = range.start; block < range.end && !keep; ++block) {
                keep = static_cast<u16>(use_epoch - block_last_use[block]) < idle_epochs;
            }
            const VAddr addr = range.start << block_shift;
            const u64 size = (range.end - range.start) << block_shift;
            keep = keep || pinned_ranges.Overlaps(range.start, range.end) ||
                   memory_tracker->IsRegionGpuModified(addr, size) || gpu_modified_ranges.Intersects(addr, size);
        }
        if (keep) {
            continue;
        }
        bool equal = true;
        for (const EvictPiece& piece : pick.pieces) {
            for (u64 at = 0; at < piece.size && equal; at += guest.size()) {
                const VAddr addr = piece.addr + at;
                if (memory_tracker->IsRegionCpuModified(addr, guest.size())) {
                    continue; // uploaded at the next bind anyway
                }
                // FEX copies through backing aliases and zeroes sparse holes without
                // dereferencing protected/unmapped guest pages.
                memory->CopySparseMemory(addr, guest.data(), guest.size());
                equal = std::memcmp(download.mapped + piece.offset + at, guest.data(),
                                    guest.size()) == 0;
            }
        }
        if (!equal) {
            evict_retry.emplace(pick.key, now + std::chrono::seconds(60));

            continue;
        }
        released.insert(released.end(), pick.ranges.begin(), pick.ranges.end());
    }
    staging_pool.FreeDeferred(download);
    pending_eviction.reset();
    // Completion callbacks may have changed the backing/offset. No submit may
    // intervene between these final guards and publishing the separate unbind.
    std::erase_if(released, [&](const Backing& range) {
        bool same = false;
        resident_ranges.ForEachInRange(range.start, range.end, [&](const Backing& now_range) {
            same |= now_range.start <= range.start && range.end <= now_range.end &&
                    now_range.memory == range.memory &&
                    now_range.offset + range.start - now_range.start == range.offset;
        });
        return !same;
    });
    for (const Backing& range : released) {
        const VAddr addr = range.start << block_shift;
        const u64 size = (range.end - range.start) << block_shift;
        MarkReadbacksDirty(addr, size);
        memory_tracker->MarkRegionAsCpuModified(addr, size);
        evicted_ranges.Add({range.start, range.end});

        std::erase_if(hot_readbacks, [&](const HotReadback& hot) {
            return hot.span.Overlaps(BachataReadback::Span{addr, addr + size});
        });
        SubtractArenaIntervals(resident_ranges, range.start, range.end);
    }
    if (!released.empty()) {
        UnbindResident(released);
        ++resident_version; // sotc: invalidates the merged DMA runs and the resident cache
        // A bind of the same blocks recorded before the next submit would share one sparse
        // bind batch with the unbind; submit the unbind on its own.
        scheduler.Flush();
    }

    return true;
}

void BufferCache::NoteFaultRebind(VAddr addr, u64 size) {
    if (!IsSotcArena()) return;
    const u64 first_block = addr >> block_shift;
    const u64 end_block = (addr + size + block_size - 1) >> block_shift;
    evicted_ranges.ForEachInRange(first_block, end_block, [&](const Interval& evicted) {
        const u64 start = std::max(first_block, evicted.start);
        const u64 end = std::min(end_block, evicted.end);
        pinned_ranges.Add({start, end});

    });
}
