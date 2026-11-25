    static constexpr u64 ARENA_CHUNK_SIZE = 64_MB;
    struct ArenaChunk {
        vk::DeviceMemory memory;
        u32 memory_type{};
        u64 used_blocks{};
        std::map<u64, u64> free_runs; ///< first block -> number of free blocks
    };
    std::vector<std::unique_ptr<ArenaChunk>> arena_chunks;
    std::unordered_map<VkDeviceMemory, ArenaChunk*> chunk_by_memory;
    /// Memory and first block for blocks of arena backing (video memory, else system memory).
    std::pair<vk::DeviceMemory, u64> AllocateArenaBlocks(u64 blocks);
    void FreeArenaBlocks(vk::DeviceMemory memory, u64 start, u64 blocks);
    /// sotc: unbinds resident block ranges (zeroing their page table entries) and frees the
    /// allocations left without blocks. The GPU must no longer use them.
    void UnbindResident(std::span<const Backing> released);
    /// sotc: per arena block, the use epoch (seconds, wrapping, 0 = never) of its last bind.
    u16* block_last_use{};
    /// sotc: blocks MaybeEvictCold gave back and nothing bound again yet.
    IntervalList<> evicted_ranges;
    /// sotc: evicted blocks a shader faulted back in; never evicted again.
    IntervalList<> pinned_ranges;
    /// sotc: resident ranges (by first block) whose read-back did not match guest memory,
    /// tried again after this.
    std::unordered_map<u64, std::chrono::steady_clock::time_point> evict_retry;
    /// sotc: arena memory in use (blocks handed out of the chunks), in bytes.
    u64 ArenaUsedBytes() const noexcept;
    struct ResidentHit {
        u64 version{~u64{0}};
        u64 first{};
        u64 end{};
        u16 epoch{};
    };
    std::array<ResidentHit, 64> resident_cache{};
    u16 use_epoch{1};
    /// sotc: sets use_epoch from the clock (once per submit and per eviction check).
    void AdvanceUseEpoch(std::chrono::steady_clock::time_point now) noexcept {
        const auto seconds =
            std::chrono::duration_cast<std::chrono::seconds>(now - epoch_start).count();
        use_epoch = static_cast<u16>(seconds % 65535 + 1); // 0 = never bound
    }
    std::chrono::steady_clock::time_point epoch_start{};
    std::chrono::steady_clock::time_point next_evict_check{};
    /// sotc: an eviction whose read-back is recorded; compared and unbound once the GPU is done.
    struct EvictPiece {
        VAddr addr;
        u64 size;
        u64 offset; ///< in the download
    };
    struct EvictChoice {
        u64 key; ///< first block of the resident range
        u64 bytes;
        std::vector<EvictPiece> pieces;
        boost::container::small_vector<Backing, 4> ranges;
    };
    struct PendingEviction {
        std::vector<EvictChoice> chosen;
        Vulkan::StagingBufferRef download;
        u64 tick{};
        std::chrono::steady_clock::time_point deadline{};
    };
    std::optional<PendingEviction> pending_eviction;
    bool FinishEviction(std::chrono::steady_clock::time_point now, u16 idle_epochs, bool wait);

    std::optional<u32> arena_fallback_memory_type_index;
