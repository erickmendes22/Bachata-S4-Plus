"""Adapt the effective Order donor's complete same-address image alias protocol.

The Vulkan recorder and all existing FEX guest-memory access remain in Bachata.
No guest readback setting is changed. Applied after texture/view memo overlays.
"""
from pathlib import Path

HELPERS = r'''std::optional<Extent3D> GetOrderAliasCopyExtent(const ImageInfo& src, const ImageInfo& dst) {
    const bool same_layout =
        src.guest_address == dst.guest_address && src.num_bits == dst.num_bits &&
        src.num_samples == dst.num_samples && !src.props.is_depth && !dst.props.is_depth &&
        src.props.is_block == dst.props.is_block && src.props.is_pow2 == dst.props.is_pow2 &&
        src.type == dst.type && src.pitch == dst.pitch && src.tile_mode == dst.tile_mode &&
        src.array_mode == dst.array_mode && src.bank_swizzle == dst.bank_swizzle &&
        src.alt_tile == dst.alt_tile;
    if (!same_layout) {
        return std::nullopt;
    }

    if (src.pixel_format == dst.pixel_format && src.resources.levels == 1 &&
        dst.resources.levels == 1 && src.resources.layers >= dst.resources.layers &&
        src.size.width >= dst.size.width && src.size.height >= dst.size.height &&
        src.size.depth >= dst.size.depth) {
        return dst.size;
    }

    const bool can_copy_intersection = !src.props.is_block && src.resources.levels == 1 &&
                                       dst.resources.levels == 1 && src.resources.layers == 1 &&
                                       dst.resources.layers == 1 && src.size.depth == 1 &&
                                       dst.size.depth == 1 && src.size.width == dst.size.width &&
                                       IsVulkanFormatCompatible(src.pixel_format, dst.pixel_format);
    if (!can_copy_intersection) {
        return std::nullopt;
    }

    return Extent3D{
        .width = src.size.width,
        .height = std::min(src.size.height, dst.size.height),
        .depth = 1,
    };
}

static bool Covers(const Extent3D& extent, const ImageInfo& info) {
    return extent.width == info.size.width && extent.height == info.size.height &&
           extent.depth == info.size.depth;
}

static bool CanAlias(const Image& lhs, const Image& rhs) {
    // An alias may become the next GPU writer. Accept a group only when the
    // protocol can reconcile writes in either direction (not just read a
    // contained layer/volume once). The observed 736/720 single-layer pair
    // supports the intersection in both directions.
    return GetOrderAliasCopyExtent(lhs.info, rhs.info) && GetOrderAliasCopyExtent(rhs.info, lhs.info);
}

static void CountOrderAliasCopy(const Image& src, const Image& dst, const Extent3D& extent) {
    struct Window {
        u64 copies{}, bytes{};
        std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
        u32 unchecked{};
        bool reported{};
    };
    thread_local Window window;
    ++window.copies;
    window.bytes += u64{extent.width} * extent.height * extent.depth *
                    std::min(src.info.resources.layers, dst.info.resources.layers) *
                    (src.info.num_bits / 8);
    if (window.reported && ++window.unchecked < 64) return;
    window.unchecked = 0;
    const auto now = std::chrono::steady_clock::now();
    const auto us = std::chrono::duration_cast<std::chrono::microseconds>(now-window.start).count();
    if (window.reported && us < 5'000'000) return;
    LOG_INFO(Render_Vulkan,
        "BACHATA_ORDER_IMAGE_ALIAS window_us={} copies={} bytes={} last={}x{}x{} src_uid={} dst_uid={}",
        us, window.copies, window.bytes, extent.width, extent.height, extent.depth,
        src.image_uid, dst.image_uid);
    window.start = now;
    window.copies = window.bytes = 0;
    window.reported = true;
}
'''

POLICY = r'''// BACHATA_ORDER_IMAGE_ALIAS: same-address GPU images retain a current authority.
bool TextureCache::ImageAliasesEnabled() const {
#ifdef __ANDROID__
    return Common::ElfInfo::Instance().GameSerial() == "CUSA00785";
#else
    return false;
#endif
}
'''

METHODS = r'''template <typename Func>
void TextureCache::ForEachAlias(const Image& image, Func&& func) {
    const auto page = page_table.find(image.info.guest_address >> Traits::PAGE_BITS);
    if (page == nullptr) {
        return;
    }
    for (const ImageId candidate_id : *page) {
        Image& candidate = slot_images[candidate_id];
        if (&candidate != &image && candidate.info.guest_address == image.info.guest_address &&
            CanAlias(candidate, image)) {
            func(candidate_id, candidate);
        }
    }
}

void TextureCache::SynchronizeAlias(ImageId image_id) {
    if (!ImageAliasesEnabled()) return;
    Image& dst = slot_images[image_id];
    if (False(dst.flags & ImageFlagBits::Aliased)) {
        return;
    }
    const auto state_it = alias_states.find(dst.info.guest_address);
    if (state_it == alias_states.end()) {
        return;
    }
    AliasState& state = state_it.value();
    if (!IsLiveImage(state.backing, state.backing_uid)) {
        if (!IsLiveImage(state.writer, state.writer_uid)) {
            state.ResetAuthority();
            return;
        }
        state.backing = state.writer, state.backing_uid = state.writer_uid;
        state.writer = {}, state.writer_uid = 0;
    }
    if (state.writer == image_id && state.writer_uid == dst.image_uid) {
        return;
    }
    if (!CommitAliasWriter(state)) {
        state.ResetAuthority();
        return;
    }
    Image& current = slot_images[state.backing];
    const std::optional extent = GetOrderAliasCopyExtent(current.info, dst.info);
    if (state.backing == image_id || current.alias_generation <= dst.alias_generation || !extent) {
        return;
    }
    CopyAlias(state.backing, image_id, *extent);
    dst.alias_generation = current.alias_generation;
    const std::optional reverse = GetOrderAliasCopyExtent(dst.info, current.info);
    if (reverse && Covers(*reverse, current.info) && !Covers(*extent, dst.info)) {
        state.backing = image_id, state.backing_uid = dst.image_uid;
    }
}

void TextureCache::SynchronizeAliasDownload(ImageId image_id) {
    if (!ImageAliasesEnabled()) return;
    Image& image = slot_images[image_id];
    if (const auto it = alias_states.find(image.info.guest_address); it != alias_states.end()) {
        // A download of the partial writer must first merge it into the larger
        // authority. Otherwise retiring that writer can lose the untouched tail.
        if (!CommitAliasWriter(it.value())) it.value().ResetAuthority();
    }
    SynchronizeAlias(image_id);
}

bool TextureCache::CommitAliasWriter(AliasState& state) {
    if (!state.writer) {
        return true;
    }
    if (!IsLiveImage(state.writer, state.writer_uid) ||
        !IsLiveImage(state.backing, state.backing_uid)) {
        return false;
    }
    Image& writer = slot_images[state.writer];
    Image& backing = slot_images[state.backing];
    if (state.writer != state.backing && writer.alias_generation > backing.alias_generation) {
        const std::optional extent = GetOrderAliasCopyExtent(writer.info, backing.info);
        if (!extent) {
            return false;
        }
        CopyAlias(state.writer, state.backing, *extent);
        backing.alias_generation = writer.alias_generation;
    }
    state.writer = {}, state.writer_uid = 0;
    return true;
}

void TextureCache::CopyAlias(ImageId src_id, ImageId dst_id, const Extent3D& extent) {
    Image& dst = slot_images[dst_id];
    runtime.CopyAliasImage(&slot_images[src_id], &dst, {extent.width, extent.height, extent.depth});
    dst.flags |= ImageFlagBits::GpuModified;
    dst.flags &= ~ImageFlagBits::Dirty;
    CountOrderAliasCopy(slot_images[src_id], dst, extent);
}

void TextureCache::PublishAliasWrite(ImageId image_id) {
    if (!ImageAliasesEnabled()) return;
    std::scoped_lock lock{mutex};
    Image& image = slot_images[image_id];
    image.alias_generation = ++alias_generation;
    if (False(image.flags & ImageFlagBits::Aliased)) {
        return;
    }
    AliasState& state = alias_states[image.info.guest_address];
    if (IsLiveImage(state.backing, state.backing_uid) &&
        !CanAlias(image, slot_images[state.backing])) {
        state.ResetAuthority();
    }
    if (IsLiveImage(state.backing, state.backing_uid) && state.backing != image_id) {
        Image& backing = slot_images[state.backing];
        const auto extent = GetOrderAliasCopyExtent(image.info, backing.info);
        if (extent && !Covers(*extent, backing.info)) {
            // A newly registered larger image may still contain only CPU data.
            // Initialize its untouched tail before publishing a partial GPU writer.
            RefreshImage(backing);
        }
    }
    state.members = std::max(state.members, 2u);
    if (state.writer == image_id && state.writer_uid == image.image_uid) {
        return;
    }
    if (IsLiveImage(state.backing, state.backing_uid)) {
        const ImageInfo& backing = slot_images[state.backing].info;
        const std::optional extent = GetOrderAliasCopyExtent(image.info, backing);
        if (extent && Covers(*extent, backing)) {
            state.backing = image_id, state.backing_uid = image.image_uid;
        } else {
            state.writer = image_id, state.writer_uid = image.image_uid;
        }
    } else {
        state.backing = image_id, state.backing_uid = image.image_uid;
    }
}

void TextureCache::InvalidateAlias(Image& image) {
    if (!ImageAliasesEnabled()) return;
    image.alias_generation = 0;
    if (True(image.flags & ImageFlagBits::Aliased)) {
        if (const auto it = alias_states.find(image.info.guest_address); it != alias_states.end()) {
            it.value().ResetAuthority();
        }
    }
}

void TextureCache::NoteAliasWriteback(const Image& image) {
    if (!ImageAliasesEnabled() || False(image.flags & ImageFlagBits::Aliased)) return;
    // A GC writeback can publish a newer union of partial GPU writers. The
    // other cached images must reconsider these guest bytes if the authority
    // is retired next. This is deliberately not done on a partial unmap:
    // UnmapImages preserved those survivors directly on the GPU instead.
    ForEachAlias(image, [&](ImageId, Image& candidate) {
        if (candidate.alias_generation < image.alias_generation)
            candidate.flags |= ImageFlagBits::CpuDirty;
    });
}

'''

MEMBERS = r'''    struct AliasState {
        u64 backing_uid{};
        u64 writer_uid{};
        ImageId backing{};
        ImageId writer{};
        u32 members{};
        void ResetAuthority() {
            const u32 count = members;
            *this = {};
            members = count;
        }
    };
    tsl::robin_map<VAddr, AliasState> alias_states;
    u64 alias_generation{};
    [[nodiscard]] bool IsLiveImage(ImageId image_id, u64 image_uid) const {
        return image_id && slot_images.IsAllocated(image_id) &&
               slot_images[image_id].image_uid == image_uid &&
               True(slot_images[image_id].flags & ImageFlagBits::Registered);
    }
    template <typename Func> void ForEachAlias(const Image& image, Func&& func);
    void SynchronizeAlias(ImageId image_id);
    void SynchronizeAliasDownload(ImageId image_id);
    bool CommitAliasWriter(AliasState& state);
    void CopyAlias(ImageId src, ImageId dst, const Extent3D& extent);
    void InvalidateAlias(Image& image);
    void NoteAliasWriteback(const Image& image);
    void RegisterAlias(ImageId image_id);
    void UnregisterAlias(ImageId image_id);
    void UnmapImages(VAddr cpu_addr, size_t size, bool preserve_aliases);
'''

UNMAP = r'''void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {
    UnmapImages(cpu_addr, size, false);
}

'''

UNMAP_DISPATCH = r'''    if (!preserve_aliases && ImageAliasesEnabled() &&
        std::ranges::any_of(deleted_images, [&](ImageId id) {
            return True(slot_images[id].flags & ImageFlagBits::Aliased);
        })) {
        // Decide and retire the non-alias path under this same lock. A new
        // registration cannot slip between a separate probe and retirement.
        // Never wait for the GPU owner while holding the texture lifetime lock.
        lk.unlock();
        // MemoryManager performs early GPU unmap before its VMA writer lock.
        // SendCommand handles CP/Draw inline and queues external callers.
        liverpool->SendCommand<true>([this, cpu_addr, size] {
            UnmapImages(cpu_addr, size, true);
        });
        return;
    }
'''

PRESERVE_UNMAP = UNMAP_DISPATCH + r'''    if (preserve_aliases) {
        ImageIds survivors;
        for (const ImageId id : deleted_images) {
            ForEachAlias(slot_images[id], [&](ImageId candidate, const Image& image) {
                if (!image.Overlaps(cpu_addr, size) &&
                    std::ranges::find(survivors, candidate) == survivors.end()) {
                    survivors.push_back(candidate);
                }
            });
        }
        // No RefreshImage or guest reads here. Copy the current GPU authority
        // to each wholly surviving range before unregistering any backing.
        for (const ImageId id : survivors) SynchronizeAlias(id);
    }
'''

REGISTER = r'''    if (ImageAliasesEnabled()) {
        AliasState* state{};
        u32 aliases{};
        bool inserted{};
        ForEachAlias(image, [&](ImageId candidate_id, Image& candidate) {
            if (!state) {
                auto result = alias_states.try_emplace(image.info.guest_address);
                state = std::addressof(result.first.value());
                inserted = result.second;
            }
            ++aliases;
            candidate.flags |= ImageFlagBits::Aliased;
            // A partial writer may be newer than the backing that preserves
            // its untouched tail. Registering another view must not promote
            // that writer before CommitAliasWriter has merged the two.
            if (!IsLiveImage(state->backing, state->backing_uid) ||
                (inserted && slot_images[state->backing].alias_generation <
                                 candidate.alias_generation)) {
                state->backing = candidate_id, state->backing_uid = candidate.image_uid;
            }
        });
        if (state) {
            image.flags |= ImageFlagBits::Aliased;
            state->members = inserted ? aliases + 1 : state->members + 1;
        }

    }

'''

DELETE = r'''    const auto alias_it = True(image.flags & ImageFlagBits::Aliased)
                              ? alias_states.find(image.info.guest_address)
                              : alias_states.end();
    if (alias_it != alias_states.end()) {
        AliasState& state = alias_it.value();
        // No copy here (DeleteImage also runs on guest threads through UnmapMemory,
        // which must not record commands); the aliases then re-read guest memory.
        if ((state.writer == image_id && state.writer_uid == image.image_uid) ||
            (state.backing == image_id && state.backing_uid == image.image_uid)) {
            state.ResetAuthority();
        }
        if (state.members <= 2) {
            ForEachAlias(image, [](ImageId, Image& candidate) {
                candidate.flags &= ~ImageFlagBits::Aliased;
            });
            alias_states.erase(alias_it);
        } else {
            --state.members;
        }
    }

'''

RUNTIME_COPY = r'''void Runtime::CopyAliasImage(VideoCore::Image* src, VideoCore::Image* dst,
                             const vk::Extent3D& extent) {
    SetBackingSamples(src, src->info.num_samples);
    SetBackingSamples(dst, dst->info.num_samples);
    scheduler.EndRendering();
    const u32 layers = std::min(src->info.resources.layers, dst->info.resources.layers);
    const vk::ImageCopy region{
        .srcSubresource{.aspectMask = vk::ImageAspectFlagBits::eColor, .layerCount = layers},
        .dstSubresource{.aspectMask = vk::ImageAspectFlagBits::eColor, .layerCount = layers},
        .extent = extent,
    };
    bool needs_flush =
        Transit(src, vk::ImageLayout::eTransferSrcOptimal, vk::PipelineStageFlagBits2::eCopy,
                vk::AccessFlagBits2::eTransferRead);
    needs_flush |= Transit(dst, vk::ImageLayout::eTransferDstOptimal,
                           vk::PipelineStageFlagBits2::eCopy, vk::AccessFlagBits2::eTransferWrite);
    if (needs_flush) {
        FlushBarriers();
    }
    scheduler.RecordDeferred([src_image = src->GetImage(), dst_image = dst->GetImage(),
                      region](vk::CommandBuffer cmdbuf) {
        cmdbuf.copyImage(src_image, vk::ImageLayout::eTransferSrcOptimal, dst_image,
                         vk::ImageLayout::eTransferDstOptimal, region);
    });
}'''

def apply(root):
    root = Path(root)
    def edit(name, old, new):
        path = root / "src" / name
        text = path.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"Order image alias source drift: {name}: {old[:100]!r}")
        path.write_text(text.replace(old, new, 1))
    tc = "video_core/texture_cache/texture_cache.cpp"
    th = "video_core/texture_cache/texture_cache.h"
    ih = "video_core/texture_cache/image.h"
    rh = "video_core/renderer_vulkan/vk_runtime.h"
    rc = "video_core/renderer_vulkan/vk_runtime.cpp"
    edit(tc, "#include <cstdlib>", "#include <cstdlib>\n#include <algorithm>\n#include <chrono>")
    edit(ih, "    Picked = 1 << 7,", "    Aliased = 1 << 8, ///< same-address image alias group\n    Picked = 1 << 7,")
    edit(ih, "    u64 image_uid{};", "    u64 image_uid{};\n    u64 alias_generation{};")
    edit(th, "    void UpdateImage(ImageId image_id) {", "    bool ImageAliasesEnabled() const;\n    void PublishAliasWrite(ImageId image_id);\n\n    void UpdateImage(ImageId image_id) {")
    edit(th, "        RefreshImage(image);\n    }", "        RefreshImage(image);\n        SynchronizeAlias(image_id);\n    }")
    edit(th, "    std::mutex mutex;", MEMBERS+"\n    std::mutex mutex;")
    registry = ("void TextureCache::RegisterAlias(ImageId image_id) {\n"
                "    Image& image = slot_images[image_id];\n" + REGISTER + "}\n\n"
                "void TextureCache::UnregisterAlias(ImageId image_id) {\n"
                "    Image& image = slot_images[image_id];\n" + DELETE + "}\n\n")
    edit(tc, "TextureCache::TextureCache(", HELPERS+"\n\n"+POLICY+"\n"+METHODS+registry+"\nTextureCache::TextureCache(")
    edit(tc, "    image.lru_id = lru_cache.Insert(image_id, gc_tick);\n", "    image.lru_id = lru_cache.Insert(image_id, gc_tick);\n    RegisterAlias(image_id);\n")
    edit(tc, "    // Remove any registered meta areas.\n", "    UnregisterAlias(image_id);\n\n    // Remove any registered meta areas.\n")
    edit(tc, "void TextureCache::TouchImage(const Image& image) {\n", "void TextureCache::TouchImage(const Image& image) {\n    if (False(image.flags & ImageFlagBits::Registered)) return;\n")
    edit(tc, "            image.flags |= ImageFlagBits::CpuDirty;", "            InvalidateAlias(image);\n            image.flags |= ImageFlagBits::CpuDirty;")
    edit(tc, "        image.flags |= ImageFlagBits::GpuDirty;", "        InvalidateAlias(image);\n        image.flags |= ImageFlagBits::GpuDirty;")
    edit(tc, "        image.hash = hash;\n    }", "        image.hash = hash;\n        // A write elsewhere on an untracked page can later modify this image\n        // without another fault. A confirmed changed hash supersedes the GPU alias.\n        InvalidateAlias(image);\n    }")
    edit(tc, "void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {", UNMAP+"void TextureCache::UnmapImages(VAddr cpu_addr, size_t size, bool preserve_aliases) {")
    edit(tc, "    std::scoped_lock lk{mutex};\n\n    ImageIds deleted_images;", "    std::unique_lock lk{mutex};\n\n    ImageIds deleted_images;")
    edit(tc, "    for (const ImageId id : deleted_images) {", PRESERVE_UNMAP+"    for (const ImageId id : deleted_images) {")
    edit(tc, "    if (!readback_linear_images) return;\n    const bool deferred=", "    if (!readback_linear_images) return;\n    std::scoped_lock image_lock{mutex};\n    const bool deferred=")
    edit(tc, "        if(!image.SafeToDownload()) continue;\n", "        SynchronizeAliasDownload(image_id);\n        if(!image.SafeToDownload()) continue;\n")
    edit(tc, "        const bool download = image.SafeToDownload();", "        SynchronizeAliasDownload(image_id);\n        const bool download = image.SafeToDownload();")
    edit(tc, "    if (False(image.flags & ImageFlagBits::GpuModified)) {", "    SynchronizeAliasDownload(image_id);\n    sync |= ImageAliasesEnabled() && True(image.flags & ImageFlagBits::Aliased);\n    if (False(image.flags & ImageFlagBits::GpuModified)) {")
    edit(tc, "        Core::Memory::Instance()->TryWriteBacking(std::bit_cast<u8*>(image.info.guest_address),\n                                                  download.mapped, download_size);", "        if (Core::Memory::Instance()->TryWriteBacking(\n                std::bit_cast<u8*>(image.info.guest_address), download.mapped, download_size)) {\n            NoteAliasWriteback(image);\n        }")
    edit(tc, "    UpdateImage(image_id);\n    if (memo && OrderDescriptorViewMemoEnabled())", "    UpdateImage(image_id);\n    if (desc.type == BindingType::Storage) PublishAliasWrite(image_id);\n    if (memo && OrderDescriptorViewMemoEnabled())")
    edit(tc, "    image.usage.render_target = 1u;\n    UpdateImage(image_id);", "    image.usage.render_target = 1u;\n    UpdateImage(image_id);\n    PublishAliasWrite(image_id);")
    edit(rh, "    void CopyImage(VideoCore::Image* src, VideoCore::Image* dst);", "    void CopyAliasImage(VideoCore::Image* src, VideoCore::Image* dst, const vk::Extent3D& extent);\n    void CopyImage(VideoCore::Image* src, VideoCore::Image* dst);")
    edit(rc, "void Runtime::CopyImage(VideoCore::Image* src, VideoCore::Image* dst) {", RUNTIME_COPY+"\n\nvoid Runtime::CopyImage(VideoCore::Image* src, VideoCore::Image* dst) {")
    bc = "video_core/buffer_cache/buffer_cache.cpp"
    if '#include "common/bachata_compat_profile.h"' not in (root / "src" / bc).read_text():
        raise RuntimeError("Order image alias requires the explicit Order policy include")
    edit(bc, "    if (is_texel_buffer && !is_written) {\n        SynchronizeMemoryFromImage(arena, device_addr, size);\n    }", "    // SynchronizeMemory already refreshes a read-only texel binding.\n    if (is_texel_buffer && !is_written && !BachataCompat::Order1886()) {\n        SynchronizeMemoryFromImage(arena, device_addr, size);\n    }")
    edit(bc, "    Image& image = texture_cache.GetImage(image_id);\n    ASSERT_MSG(device_addr == image.info.guest_address,", "    if (texture_cache.ImageAliasesEnabled()) texture_cache.UpdateImage(image_id);\n    Image& image = texture_cache.GetImage(image_id);\n    ASSERT_MSG(device_addr == image.info.guest_address,")
    return {"title":"CUSA00785 Android", "group":"same-address image alias authority and GPU copies",
            "readback_mode":"unchanged", "cpu_backend":"existing ARM64+Bionic+FEX"}
