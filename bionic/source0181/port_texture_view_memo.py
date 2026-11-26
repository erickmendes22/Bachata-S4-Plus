"""Active donor view lookup caches without borrowed binding descriptors.

Both Android-effective donors use a last-view index per backing. Order also
passes a descriptor-owned ViewMemo to FindTexture on its normal binding path.
Keep FEX/0.18 backing sample conversion, refresh, storage metadata and retirement.
"""
from pathlib import Path


POLICY = r'''#pragma once
#include <cstdlib>
#include "common/elf_info.h"

namespace VideoCore {
// Only environment settings are static; a reused core can change titles.
inline bool OrderDescriptorViewMemoEnabled() {
    static const bool configured = [] {
        const char* value = std::getenv("BACHATA_ORDER_TEXTURE_VIEW_MEMO");
        return !value || value[0] != '0';
    }();
    return configured && Common::ElfInfo::Instance().GameSerial() == "CUSA00785";
}

inline bool ImageLastViewMemoEnabled() {
    if (OrderDescriptorViewMemoEnabled()) return true;
    static const bool configured = [] {
        const char* value = std::getenv("SOTC_TEX_BIND_P1");
        return !value || value[0] != '0';
    }();
    const auto& serial = Common::ElfInfo::Instance().GameSerial();
    return configured && (serial == "CUSA08809" || serial == "CUSA08034");
}
} // namespace VideoCore
'''


FIND_VIEW_OLD = r'''ImageView& Image::FindView(const ImageViewInfo& view_info, bool ensure_guest_samples) {
    if (ensure_guest_samples && backing->num_samples > 1 != info.num_samples > 1) {
        runtime->SetBackingSamples(this, info.num_samples);
    }
    const auto& view_infos = backing->image_view_infos;
    const auto it = std::ranges::find(view_infos, view_info);
    if (it != view_infos.end()) {
        const auto view_id = backing->image_view_ids[std::distance(view_infos.begin(), it)];
        return (*slot_image_views)[view_id];
    }
    const auto view_id = slot_image_views->Insert(runtime->GetInstance(), view_info, *this);
    backing->image_view_infos.emplace_back(view_info);
    backing->image_view_ids.emplace_back(view_id);
    return (*slot_image_views)[view_id];
}'''


FIND_VIEW = r'''ImageView& Image::FindView(const ImageViewInfo& view_info, bool ensure_guest_samples) {
    // Sample conversion may choose another backing. Its own index is checked
    // only after that transition, with the complete resolved view descriptor.
    if (ensure_guest_samples && backing->num_samples > 1 != info.num_samples > 1) {
        runtime->SetBackingSamples(this, info.num_samples);
    }
    const bool use_last_view = ImageLastViewMemoEnabled();
    const auto& view_infos = backing->image_view_infos;
    if (use_last_view && backing->last_view < view_infos.size() &&
        view_infos[backing->last_view] == view_info) {
        return (*slot_image_views)[backing->image_view_ids[backing->last_view]];
    }
    const auto it = std::ranges::find(view_infos, view_info);
    if (it != view_infos.end()) {
        const auto index = std::distance(view_infos.begin(), it);
        if (use_last_view) backing->last_view = static_cast<u32>(index);
        return (*slot_image_views)[backing->image_view_ids[index]];
    }
    const auto view_id = slot_image_views->Insert(runtime->GetInstance(), view_info, *this);
    if (use_last_view) backing->last_view = static_cast<u32>(view_infos.size());
    backing->image_view_infos.emplace_back(view_info);
    backing->image_view_ids.emplace_back(view_id);
    return (*slot_image_views)[view_id];
}'''


VIEW_MEMO = r'''    // BACHATA_ORDER_TEXTURE_VIEW_MEMO_V1: identities outlive neither the image,
    // its backing allocation nor the individual view slot.
    struct ViewMemo {
        ImageId image_id{};
        u64 image_uid{};
        const void* backing{};
        u64 backing_uid{};
        ImageViewId view_id{};
        u64 view_uid{};
        ImageViewInfo view_info{};
    };

'''


TEXTURE_METHODS = r'''
ImageView* TextureCache::TryViewMemo(ImageId image_id, const ImageViewInfo& view_info,
                                     const ViewMemo& memo) {
    std::scoped_lock lock{mutex};
    if (!image_id || !memo.view_id || !slot_images.IsAllocated(image_id)) return nullptr;
    const auto& image = slot_images[image_id];
    if (memo.image_id != image_id || memo.image_uid != image.image_uid ||
        !image.backing || memo.backing != image.backing ||
        memo.backing_uid != image.backing->backing_uid ||
        False(image.flags & ImageFlagBits::Registered) || image.binding.needs_rebind ||
        (image.backing->num_samples > 1) != (image.info.num_samples > 1) ||
        memo.view_info != view_info || !slot_image_views.IsAllocated(memo.view_id)) {
        return nullptr;
    }
    auto& view = slot_image_views[memo.view_id];
    return view.view_uid == memo.view_uid ? &view : nullptr;
}

void TextureCache::RememberViewMemo(ImageId image_id, const ImageViewInfo& view_info,
                                    const ImageView& view, ViewMemo& memo) {
    std::scoped_lock lock{mutex};
    memo = {};
    if (!image_id || !slot_images.IsAllocated(image_id)) return;
    const auto& image = slot_images[image_id];
    if (!image.backing || False(image.flags & ImageFlagBits::Registered) ||
        image.binding.needs_rebind) return;
    const auto index = image.backing->last_view;
    const auto& ids = image.backing->image_view_ids;
    if (index >= ids.size() || !slot_image_views.IsAllocated(ids[index]) ||
        &slot_image_views[ids[index]] != &view) return;
    // FindView may have switched backing or drained callbacks. Capture all
    // identities after it returns, never from the pre-refresh image state.
    memo = {image_id, image.image_uid, image.backing, image.backing->backing_uid,
            ids[index], view.view_uid, view_info};
}

'''


RASTER_MEMBERS = r'''
    struct ViewMemoToken {
        u32 index = ~0u;
        u64 identity = 0;
    };
    using DescriptorViewMemos = std::array<VideoCore::TextureCache::ViewMemo, 4096>;
    std::unique_ptr<DescriptorViewMemos> descriptor_view_memos;
    boost::container::small_vector<ViewMemoToken, 16> image_view_memo_tokens;
    void RememberImageViewToken(const AmdGpu::Image& sharp, const Shader::ImageResource& res);
    bool IsViewMemoTokenCurrent(ViewMemoToken token) const;
    VideoCore::ImageView& FindTextureWithViewMemo(VideoCore::ImageId image_id,
        const VideoCore::TextureCache::ImageDesc& desc, ViewMemoToken token);
'''


RASTER_METHODS = r'''
void Rasterizer::RememberImageViewToken(const AmdGpu::Image& sharp,
                                        const Shader::ImageResource& res) {
    if (!VideoCore::OrderDescriptorViewMemoEnabled() || !texture_cache.BindingMemoEnabled() ||
        image_bindings.empty() ||
        res.mip_fallback_mode != Shader::MipStorageFallbackMode::None) return;
    auto& entry = CachedImageDescEntry(sharp, res);
    if (!descriptor_view_memos) descriptor_view_memos = std::make_unique<DescriptorViewMemos>();
    image_view_memo_tokens.resize(image_bindings.size());
    image_view_memo_tokens.back() = {
        static_cast<u32>(&entry - image_desc_cache->data()), entry.view_memo_identity};
}

bool Rasterizer::IsViewMemoTokenCurrent(ViewMemoToken token) const {
    return token.identity && image_desc_cache && descriptor_view_memos &&
           token.index < image_desc_cache->size() &&
           (*image_desc_cache)[token.index].view_memo_identity == token.identity;
}

VideoCore::ImageView& Rasterizer::FindTextureWithViewMemo(VideoCore::ImageId image_id,
    const VideoCore::TextureCache::ImageDesc& desc, ViewMemoToken token) {
    if (!VideoCore::OrderDescriptorViewMemoEnabled() || !texture_cache.BindingMemoEnabled() ||
        !IsViewMemoTokenCurrent(token)) {
        return texture_cache.FindTexture(image_id, desc);
    }
    // The descriptor slot can be replaced by a later binding or a callback.
    // Work on a local value, then revalidate the token before storing it back.
    auto memo = (*descriptor_view_memos)[token.index];
    auto& view = texture_cache.FindTexture(image_id, desc, &memo);
    if (IsViewMemoTokenCurrent(token)) (*descriptor_view_memos)[token.index] = memo;
    return view;
}

'''


def apply(root):
    root = Path(root)
    if not (root / 'src').is_dir():
        raise RuntimeError('Texture view memo requires a core root containing src/')
    root = root / 'src'
    originals, updates = {}, {}

    def read(rel):
        if rel not in originals:
            originals[rel] = (root / rel).read_text()
            updates[rel] = originals[rel]
        return updates[rel]

    def edit(rel, old, new):
        source = read(rel)
        if source.count(old) != 1:
            raise RuntimeError(f'Texture view memo anchor {rel}: {source.count(old)}: {old[:100]}')
        updates[rel] = source.replace(old, new, 1)

    ih = 'video_core/texture_cache/image.h'
    ic = 'video_core/texture_cache/image.cpp'
    vh = 'video_core/texture_cache/image_view.h'
    vc = 'video_core/texture_cache/image_view.cpp'
    th = 'video_core/texture_cache/texture_cache.h'
    tc = 'video_core/texture_cache/texture_cache.cpp'
    rh = 'video_core/renderer_vulkan/vk_rasterizer.h'
    rc = 'video_core/renderer_vulkan/vk_rasterizer.cpp'
    policy_path = 'video_core/texture_cache/texture_view_memo_policy.h'
    order = 'BACHATA_ORDER_TEXTURE_BINDING_MEMO_V1' in read(tc)
    sotc = 'BACHATA_SOTC_TEXTURE_FIND_MEMO_V1' in read(th)
    if order == sotc:
        raise RuntimeError('Texture view memo requires exactly one active Order/SotC lookup family')
    if (root / policy_path).exists():
        raise RuntimeError('Texture view memo already applied')

    edit(ih, '        u32 num_samples;\n',
         '        u32 num_samples;\n        u32 last_view = ~0u;\n')
    edit(ic, '#include "video_core/texture_cache/image.h"',
         '#include "video_core/texture_cache/image.h"\n#include "video_core/texture_cache/texture_view_memo_policy.h"')
    edit(ic, FIND_VIEW_OLD, FIND_VIEW)

    if order:
        edit(ih, '    struct BackingImage {\n',
             '    struct BackingImage {\n        u64 backing_uid = global_backing_uid.Next();\n')
        edit(ih, '    static Common::IncrementalIdProvider<u64> global_image_uid;',
             '    static Common::IncrementalIdProvider<u64> global_backing_uid;\n'
             '    static Common::IncrementalIdProvider<u64> global_image_uid;')
        edit(ic, 'Common::IncrementalIdProvider<u64> Image::global_image_uid{};',
             'Common::IncrementalIdProvider<u64> Image::global_image_uid{};\n'
             'Common::IncrementalIdProvider<u64> Image::global_backing_uid{};')
        edit(vh, '#include "video_core/amdgpu/regs_depth.h"',
             '#include "common/incremental_id.h"\n#include "video_core/amdgpu/regs_depth.h"')
        edit(vh, '    ImageViewInfo info;\n',
             '    static Common::IncrementalIdProvider<u64> global_view_uid;\n'
             '    u64 view_uid = global_view_uid.Next();\n    ImageViewInfo info;\n')
        edit(vc, 'namespace VideoCore {\n',
             'namespace VideoCore {\n\nCommon::IncrementalIdProvider<u64> ImageView::global_view_uid{};\n')
        old_decl = '    [[nodiscard]] ImageView& FindTexture(ImageId image_id, const ImageDesc& desc);'
        edit(th, old_decl, VIEW_MEMO + '    [[nodiscard]] ImageView& FindTexture(ImageId image_id, const ImageDesc& desc,\n'
             '                                         ViewMemo* memo = nullptr);')
        edit(th, '    /// Touch the image in the LRU cache.\n',
             '    ImageView* TryViewMemo(ImageId image_id, const ImageViewInfo& view_info, const ViewMemo& memo);\n'
             '    void RememberViewMemo(ImageId image_id, const ImageViewInfo& view_info,\n'
             '                          const ImageView& view, ViewMemo& memo);\n\n'
             '    /// Touch the image in the LRU cache.\n')
        edit(tc, '#include "video_core/texture_cache/texture_cache.h"',
             '#include "video_core/texture_cache/texture_cache.h"\n'
             '#include "video_core/texture_cache/texture_view_memo_policy.h"')
        edit(tc, 'ImageView& TextureCache::FindTexture(ImageId image_id, const ImageDesc& desc) {',
             TEXTURE_METHODS + 'ImageView& TextureCache::FindTexture(ImageId image_id, const ImageDesc& desc, ViewMemo* memo) {')
        edit(tc, '    UpdateImage(image_id);\n    return image.FindView(desc.view_info);',
             '    UpdateImage(image_id);\n'
             '    if (memo && OrderDescriptorViewMemoEnabled()) {\n'
             '        if (auto* view = TryViewMemo(image_id, desc.view_info, *memo)) return *view;\n'
             '        auto& view = image.FindView(desc.view_info);\n'
             '        RememberViewMemo(image_id, desc.view_info, view, *memo);\n'
             '        return view;\n'
             '    }\n    return image.FindView(desc.view_info);')
        edit(rh, '        u64 found_generation = ~0ull;\n',
             '        u64 found_generation = ~0ull;\n        u64 view_memo_identity = 0;\n')
        # Keep the new store separate from ImageDescCache: bindings borrow no
        # descriptor or memo entry across refresh/allocation callbacks.
        anchor = '    boost::container::static_vector<ImageBindingInfo, Shader::NUM_IMAGES + Shader::NUM_IMAGE_ARRAY_DESCRIPTORS> image_bindings;'
        edit(rh, anchor, anchor + '\n' + RASTER_MEMBERS)
        edit(rc, '#include "video_core/texture_cache/texture_cache.h"',
             '#include "video_core/texture_cache/texture_cache.h"\n'
             '#include "video_core/texture_cache/texture_view_memo_policy.h"')
        edit(rc, '        entry->found_generation = ~0ull;\n',
             '        entry->found_generation = ~0ull;\n        entry->view_memo_identity = ++desc_use_counter;\n')
        edit(rc, 'void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {\n'
             '    image_bindings.clear();', RASTER_METHODS +
             'void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {\n'
             '    image_bindings.clear();\n    image_view_memo_tokens.clear();')
        for sharp, indent in (('element', '                '), ('tsharp', '            ')):
            old = indent + f'image_id = FindBoundImage({sharp}, image_desc, desc);'
            edit(rc, old, old + '\n' + indent + f'RememberImageViewToken({sharp}, image_desc);')
        edit(rc, '    for (auto& [image_id, desc] : image_bindings) {\n',
             '    for (u32 binding_index = 0; binding_index < image_bindings.size(); ++binding_index) {\n'
             '        auto& [image_id, desc] = image_bindings[binding_index];\n'
             '        auto view_token = binding_index < image_view_memo_tokens.size()\n'
             '            ? image_view_memo_tokens[binding_index] : ViewMemoToken{};\n')
        edit(rc, '                image_id = texture_cache.FindImage(desc);\n',
             '                image_id = texture_cache.FindImage(desc);\n                view_token = {};\n')
        edit(rc, '            auto& image_view = texture_cache.FindTexture(image_id, desc);',
             '            auto& image_view = FindTextureWithViewMemo(image_id, desc, view_token);')

    for rel, original in originals.items():
        if (root / rel).read_text() != original:
            raise RuntimeError('Concurrent texture view source edit: ' + rel)
    for rel, source in updates.items():
        (root / rel).write_text(source)
    (root / policy_path).write_text(POLICY)
    return {
        'core': 'order' if order else 'sotc',
        'lastView': 'complete ImageViewInfo after guest sample conversion; per backing index',
        'descriptorViewMemo': order,
        'lifetime': ('image UID + backing UID + view UID + allocated slots + Registered + descriptor token'
                     if order else 'backing owns its unchanged view list'),
        'abi': 'runtime only; no serialized shader/PSO changes',
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    print(apply(parser.parse_args().source))
