"""Reuse an unchanged, still-open Order attachment transaction, as in the donor.

The native FEX memory/metadata paths remain authoritative.  Unlike an address
memo, a hit validates live image/backing/view identities and dirty state under
the texture-cache mutex.  No synchronization dependency is removed.
"""
from pathlib import Path


SCHEDULER_API = r'''
    // BACHATA_ORDER_RENDER_STATE_MEMO: an ended/restarted scope is a new transaction.
    [[nodiscard]] bool IsRenderingWith(const RenderState& state) const noexcept {
        return is_rendering && render_state == state;
    }
    [[nodiscard]] u64 RenderingSerial() const noexcept { return rendering_serial; }
'''


CACHE_API = r'''
    struct RenderStateImage {
        ImageId image_id{};
        ImageViewInfo view_info{};
        vk::ImageView handle{};
        vk::ImageLayout layout{};
        vk::AccessFlags2 access{};
        VAddr clear_address{}, fmask_address{}, stencil_address{};
        u32 samples{}, stencil_size{};
        bool depth{};
    };
    struct RenderStateImageMemo {
        ViewMemo view{};
        ImageId stencil_id{};
        u64 stencil_uid{};
    };
    bool CheckRenderStateImages(std::span<const RenderStateImage> targets,
        std::span<RenderStateImageMemo> memo, u64 generation, bool remember);
'''


CACHE_METHOD = r'''
// BACHATA_ORDER_RENDER_STATE_IMAGES: this lock covers the entire validation,
// including UID/retirement, dirty writes, backing changes and metadata owners.
// It never records commands, waits for another owner, or performs a guest copy.
bool TextureCache::CheckRenderStateImages(std::span<const RenderStateImage> targets,
    std::span<RenderStateImageMemo> memo, u64 generation, bool remember) {
    if (targets.size() != memo.size() || generation != RegistryGeneration()) return false;
    std::scoped_lock lock{mutex};
    if (generation != RegistryGeneration()) return false;
    for (u32 i = 0; i < targets.size(); ++i) {
        const auto& target = targets[i];
        auto& token = memo[i];
        if (remember) token = {};
        if (!target.image_id) {
            if (token.view.image_id) return false;
            continue;
        }
        if (!slot_images.IsAllocated(target.image_id)) return false;
        const auto& image = slot_images[target.image_id];
        constexpr auto rejected = ImageFlagBits::Dirty | ImageFlagBits::Aliased;
        if (False(image.flags & ImageFlagBits::Registered) || True(image.flags & rejected) ||
            False(image.flags & ImageFlagBits::GpuModified) || image.binding.is_bound ||
            image.binding.needs_rebind || !image.backing ||
            image.track_addr != image.info.guest_address ||
            image.track_addr_end != image.info.guest_address + image.info.guest_size ||
            image.backing->num_samples != target.samples) return false;

        const auto& range = target.view_info.range;
        if (!range.extent.levels || !range.extent.layers ||
            range.base.level >= image.info.resources.levels ||
            range.base.layer >= image.info.resources.layers ||
            range.extent.levels > image.info.resources.levels - range.base.level ||
            range.extent.layers > image.info.resources.layers - range.base.layer) return false;
        const auto matches_state = [&](const Image::State& state) {
            return state.layout == target.layout && state.access_mask == target.access;
        };
        // A partial transition can change one mip without changing the backing
        // pointer. Check the selected subresources, not only the aggregate state.
        const auto& subresources = image.backing->subresource_states;
        if (subresources.empty()) {
            if (!matches_state(image.backing->state)) return false;
        } else {
            for (u32 level = range.base.level; level < range.base.level + range.extent.levels; ++level)
                for (u32 layer = range.base.layer; layer < range.base.layer + range.extent.layers; ++layer) {
                    const u64 index = u64{level} * image.info.resources.layers + layer;
                    if (index >= subresources.size() || !matches_state(subresources[index])) return false;
                }
        }

        const auto own_metadata = [&](VAddr address, MetaType type) {
            if (!address) return true;
            const auto it = surface_metas.find(address);
            return it != surface_metas.end() && it.value().owner_id == target.image_id &&
                   it.value().owner_uid == image.image_uid && it.value().type == type &&
                   surface_metadata.TypeAt(address) == type;
        };
        if (!own_metadata(target.clear_address, target.depth ? MetaType::HTile : MetaType::CMask) ||
            !own_metadata(target.fmask_address, MetaType::FMask)) return false;
        // A new clear with identical registers still has to be consumed by the
        // original transaction. Do not clear this bit on a failed cache probe.
        for (u32 layer = range.base.layer; layer < range.base.layer + range.extent.layers; ++layer)
            if (target.clear_address && surface_metadata.IsCleared(target.clear_address, layer)) return false;

        if (remember) {
            const auto& ids = image.backing->image_view_ids;
            ImageViewId selected{};
            for (const auto id : ids) {
                if (!slot_image_views.IsAllocated(id)) continue;
                const auto& view = slot_image_views[id];
                if (view.info == target.view_info && *view.image_view == target.handle) {
                    selected = id;
                    break;
                }
            }
            if (!selected) return false;
            const auto& view = slot_image_views[selected];
            token.view = {target.image_id, image.image_uid, image.backing,
                image.backing->backing_uid, selected, view.view_uid, target.view_info};
            if (target.stencil_address) {
                ForEachImageInRegion(target.stencil_address, target.stencil_size,
                    [&](ImageId id, Image& companion) {
                        if (companion.info.guest_address == target.stencil_address &&
                            companion.depth_id == target.image_id && companion.depth_uid == image.image_uid &&
                            True(companion.flags & ImageFlagBits::Registered)) {
                            token.stencil_id = id;
                            token.stencil_uid = companion.image_uid;
                        }
                    });
                if (!token.stencil_id) return false;
            }
        } else {
            const auto& view = token.view;
            if (view.image_id != target.image_id || view.image_uid != image.image_uid ||
                view.backing != image.backing || view.backing_uid != image.backing->backing_uid ||
                view.view_info != target.view_info || !view.view_id ||
                !slot_image_views.IsAllocated(view.view_id)) return false;
            const auto& live_view = slot_image_views[view.view_id];
            if (live_view.view_uid != view.view_uid || live_view.info != target.view_info ||
                *live_view.image_view != target.handle) return false;
            if (target.stencil_address) {
                if (!IsLiveImage(token.stencil_id, token.stencil_uid)) return false;
                const auto& companion = slot_images[token.stencil_id];
                if (companion.info.guest_address != target.stencil_address ||
                    companion.depth_id != target.image_id || companion.depth_uid != image.image_uid) return false;
            }
        }
    }
    // No partial effects before every attachment was accepted. Preserve the
    // access/LRU effects of UpdateImage without re-registering unchanged metadata.
    if (!remember) for (const auto& target : targets) {
        if (!target.image_id) continue;
        auto& image = slot_images[target.image_id];
        image.tick_accessed_last = scheduler.CurrentTick();
        TouchImage(image);
    }
    return true;
}

'''


RASTER_MEMBERS = r'''
    RenderState BeginRenderingFull(const GraphicsPipeline* pipeline, bool& metadata_clear_consumed);
    struct OrderBeginSignature {
        std::array<VideoCore::ImageId, AmdGpu::NUM_COLOR_BUFFERS + 1> ids{};
        std::array<VideoCore::ImageViewInfo, AmdGpu::NUM_COLOR_BUFFERS + 1> views{};
        std::array<u32, AmdGpu::NUM_COLOR_BUFFERS> samples{};
        std::array<VAddr, AmdGpu::NUM_COLOR_BUFFERS> cmask{}, fmask{};
        u64 generation{};
        VAddr htile{}, stencil_address{};
        u32 mrt_mask{}, num_samples{}, depth_control{}, depth_samples{}, stencil_size{};
        bool depth_valid{}, stencil_valid{};
        bool metadata_addresses_match=true;
        bool operator==(const OrderBeginSignature&) const = default;
    };
    OrderBeginSignature MakeOrderBeginSignature(const GraphicsPipeline* pipeline) const;
    std::array<VideoCore::TextureCache::RenderStateImage, AmdGpu::NUM_COLOR_BUFFERS + 1>
        OrderRenderStateImages(const OrderBeginSignature& signature, const RenderState& state) const;
    struct OrderBeginMemo {
        bool valid{};
        u64 rendering_serial{}, tick{};
        OrderBeginSignature signature{};
        RenderState state{};
        std::array<VideoCore::TextureCache::RenderStateImageMemo, AmdGpu::NUM_COLOR_BUFFERS + 1> images{};
    } order_begin_memo;
'''


RASTER_METHODS = r'''
static bool OrderRenderStateMemoEnabled() {
#ifdef __ANDROID__
    return Common::ElfInfo::Instance().GameSerial() == "CUSA00785";
#else
    return false;
#endif
}

enum class OrderBeginEvent { Hit, Cold, Boundary, Signature, Resources, ClearOrBarrier, Count };
static void CountOrderBeginMemo(const void* owner, OrderBeginEvent event, bool stored) {
    struct Window {
        const void* owner{};
        std::array<u64, static_cast<u32>(OrderBeginEvent::Count)> counts{};
        u64 stored{}, total{};
        u32 unchecked{};
        std::chrono::steady_clock::time_point start{};
    };
    thread_local std::array<Window, 8> windows{};
    Window* current{};
    for (auto& item : windows) {
        if (item.owner == owner) { current = &item; break; }
        if (!item.owner && !current) current = &item;
    }
    if (!current) current = &windows[0];
    if (current->owner != owner) {
        *current = {};
        current->owner = owner;
        current->start = std::chrono::steady_clock::now();
    }
    auto& w = *current;
    ++w.counts[static_cast<u32>(event)]; ++w.total; w.stored += stored;
    if (++w.unchecked < 1024) return;
    w.unchecked = 0;
    const auto now = std::chrono::steady_clock::now();
    const auto us = std::chrono::duration_cast<std::chrono::microseconds>(now-w.start).count();
    if (us < 5'000'000) return;
    const auto wall = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    LOG_INFO(Render_Vulkan,
        "BACHATA_ORDER_RENDER_STATE_MEMO owner={} wall_ms={} window_us={} calls={} "
        "hits={} cold={} boundary={} signature={} resources={} clear_or_barrier={} stored={}",
        reinterpret_cast<std::uintptr_t>(owner), wall, us, w.total, w.counts[0], w.counts[1],
        w.counts[2], w.counts[3], w.counts[4], w.counts[5], w.stored);
    w.counts = {}; w.total = w.stored = 0; w.start = now;
}

Rasterizer::OrderBeginSignature Rasterizer::MakeOrderBeginSignature(const GraphicsPipeline* pipeline) const {
    const auto& key = pipeline->GetGraphicsKey();
    const auto& regs = liverpool->DrawRegs();
    OrderBeginSignature signature;
    for (u32 cb = 0; cb < u32(std::bit_width(key.mrt_mask)) && cb < AmdGpu::NUM_COLOR_BUFFERS; ++cb) {
        signature.ids[cb] = cb_descs[cb].first;
        if (!signature.ids[cb]) continue;
        signature.views[cb] = cb_descs[cb].second.view_info;
        signature.samples[cb] = key.color_samples[cb];
        signature.cmask[cb] = cb_descs[cb].second.info.meta_info.cmask_addr;
        signature.metadata_addresses_match &=
            regs.color_buffers[cb].CmaskAddress() == signature.cmask[cb];
        signature.fmask[cb] = cb_descs[cb].second.info.meta_info.fmask_addr;
    }
    signature.ids[AmdGpu::NUM_COLOR_BUFFERS] = db_desc.first;
    if (db_desc.first) {
        signature.views[AmdGpu::NUM_COLOR_BUFFERS] = db_desc.second.view_info;
        signature.htile = db_desc.second.info.meta_info.htile_addr;
        signature.metadata_addresses_match &=
            regs.depth_htile_data_base.GetAddress() == signature.htile;
        signature.stencil_address = db_desc.second.info.stencil_addr;
        signature.stencil_size = db_desc.second.info.stencil_size;
        signature.depth_samples = db_desc.second.info.num_samples;
    }
    signature.mrt_mask = key.mrt_mask;
    signature.num_samples = key.num_samples;
    static_assert(sizeof(regs.depth_control) == sizeof(signature.depth_control));
    std::memcpy(&signature.depth_control, &regs.depth_control, sizeof(signature.depth_control));
    signature.depth_valid = regs.depth_buffer.DepthValid();
    signature.stencil_valid = regs.depth_buffer.StencilValid();
    signature.generation = texture_cache.RegistryGeneration();
    return signature;
}

std::array<VideoCore::TextureCache::RenderStateImage, AmdGpu::NUM_COLOR_BUFFERS + 1>
Rasterizer::OrderRenderStateImages(const OrderBeginSignature& signature, const RenderState& state) const {
    std::array<VideoCore::TextureCache::RenderStateImage, AmdGpu::NUM_COLOR_BUFFERS + 1> images{};
    for (u32 cb = 0; cb < AmdGpu::NUM_COLOR_BUFFERS; ++cb) {
        auto& target = images[cb];
        target.image_id = signature.ids[cb];
        if (!target.image_id) continue;
        target.view_info = signature.views[cb];
        target.handle = state.color_attachments[cb].image_view;
        target.layout = state.color_attachments[cb].image_layout;
        target.access = vk::AccessFlagBits2::eColorAttachmentWrite | vk::AccessFlagBits2::eColorAttachmentRead;
        target.clear_address = signature.cmask[cb];
        target.fmask_address = signature.fmask[cb];
        target.samples = signature.samples[cb];
    }
    auto& depth = images[AmdGpu::NUM_COLOR_BUFFERS];
    depth.image_id = signature.ids[AmdGpu::NUM_COLOR_BUFFERS];
    if (depth.image_id) {
        depth.view_info = signature.views[AmdGpu::NUM_COLOR_BUFFERS];
        depth.handle = state.depth_stencil_attachment.image_view;
        depth.layout = state.depth_stencil_attachment.image_layout;
        depth.access = vk::AccessFlagBits2::eDepthStencilAttachmentWrite | vk::AccessFlagBits2::eDepthStencilAttachmentRead;
        depth.clear_address = signature.htile;
        depth.samples = signature.depth_samples;
        depth.stencil_address = signature.stencil_address;
        depth.stencil_size = signature.stencil_size;
        depth.depth = true;
    }
    return images;
}

RenderState Rasterizer::BeginRendering(const GraphicsPipeline* pipeline, bool& metadata_clear_consumed) {
    if (!OrderRenderStateMemoEnabled()) {
        order_begin_memo.valid = false;
        return BeginRenderingFull(pipeline, metadata_clear_consumed);
    }
    metadata_clear_consumed = false;
    const auto& regs = liverpool->DrawRegs();
    auto signature = MakeOrderBeginSignature(pipeline);
    const bool forced = needs_barrier || !signature.metadata_addresses_match ||
                        regs.depth_render_control.depth_clear_enable ||
                        regs.depth_render_control.stencil_clear_enable;
    auto& memo = order_begin_memo;
    OrderBeginEvent event = OrderBeginEvent::Cold;
    if (forced) event = OrderBeginEvent::ClearOrBarrier;
    else if (memo.valid) {
        if (memo.tick != scheduler.CurrentTick() || memo.rendering_serial != scheduler.RenderingSerial() ||
            !scheduler.IsRenderingWith(memo.state)) event = OrderBeginEvent::Boundary;
        else if (signature != memo.signature) event = OrderBeginEvent::Signature;
        else {
            const auto targets = OrderRenderStateImages(signature, memo.state);
            if (texture_cache.CheckRenderStateImages(targets, memo.images, signature.generation, false)) {
                attachment_feedback_loop = false;
                CountOrderBeginMemo(this, OrderBeginEvent::Hit, false);
                return memo.state;
            }
            event = OrderBeginEvent::Resources;
        }
    }
    memo.valid = false;
    const auto state = BeginRenderingFull(pipeline, metadata_clear_consumed);
    bool clears = state.depth_stencil_attachment.depth_clear || state.depth_stencil_attachment.stencil_clear;
    for (u32 i = 0; i < state.num_color_attachments; ++i) clears |= state.color_attachments[i].is_clear != 0;
    if (!attachment_feedback_loop && !clears && !metadata_clear_consumed) {
        // Rebind/refresh can change identities during the full path.
        signature = MakeOrderBeginSignature(pipeline);
        const auto targets = OrderRenderStateImages(signature, state);
        if (signature.metadata_addresses_match &&
            texture_cache.CheckRenderStateImages(targets, memo.images, signature.generation, true)) {
            memo.signature = signature;
            memo.state = state;
            memo.rendering_serial = scheduler.RenderingSerial();
            memo.tick = scheduler.CurrentTick();
            memo.valid = true;
        }
    }
    CountOrderBeginMemo(this, event, memo.valid);
    return state;
}

'''


def once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"Order render-state memo anchor drift: {label}")
    return text.replace(old, new, 1)


def apply(root):
    root = Path(root) / "src"
    names = ("video_core/renderer_vulkan/vk_scheduler.h", "video_core/renderer_vulkan/vk_scheduler.cpp",
             "video_core/texture_cache/texture_cache.h", "video_core/texture_cache/texture_cache.cpp",
             "video_core/renderer_vulkan/vk_rasterizer.h", "video_core/renderer_vulkan/vk_rasterizer.cpp")
    files = {name: (root / name).read_text() for name in names}
    if any("BACHATA_ORDER_RENDER_STATE_MEMO" in text for text in files.values()):
        raise RuntimeError("Order render-state memo already applied")
    sh, sc, th, tc, rh, rc = names
    files[sh] = once(files[sh], "    /// Starts a new rendering scope with provided state.\n",
                     SCHEDULER_API + "\n    /// Starts a new rendering scope with provided state.\n", "scheduler API")
    files[sh] = once(files[sh], "    bool is_rendering = false;", "    bool is_rendering = false;\n    u64 rendering_serial{};", "scope serial")
    files[sc] = once(files[sc], "    is_rendering = true;", "    is_rendering = true;\n    ++rendering_serial;", "new rendering scope")
    files[th] = once(files[th], "    /// Updates image contents if it was modified by CPU.\n",
                     CACHE_API + "\n    /// Updates image contents if it was modified by CPU.\n", "texture API")
    if "#include <span>" not in files[th]: files[th] = "#include <span>\n" + files[th]
    files[tc] = once(files[tc], "void TextureCache::RegisterImage(ImageId image_id) {",
                     CACHE_METHOD + "void TextureCache::RegisterImage(ImageId image_id) {", "texture method")
    anchor = "    RenderState BeginRendering(const GraphicsPipeline* pipeline, bool& metadata_clear_consumed);"
    files[rh] = once(files[rh], anchor, anchor + "\n" + RASTER_MEMBERS, "raster members")
    signature = "RenderState Rasterizer::BeginRendering(const GraphicsPipeline* pipeline, bool& metadata_clear_consumed) {"
    files[rc] = once(files[rc], signature, RASTER_METHODS + signature.replace("BeginRendering(", "BeginRenderingFull("), "full transaction")
    if '#include "common/elf_info.h"' not in files[rc]: files[rc] = '#include "common/elf_info.h"\n' + files[rc]
    for name in names:
        (root / name).write_text(files[name])
    print("BACHATA_ORDER_RENDER_STATE_MEMO overlay applied")
    return {"marker": "BACHATA_ORDER_RENDER_STATE_MEMO", "files": list(names),
            "policy": "Android CUSA00785", "invalidation": "scope/tick/UID/backing/view/dirty/metadata"}


if __name__ == "__main__":
    import sys
    apply(sys.argv[1])
