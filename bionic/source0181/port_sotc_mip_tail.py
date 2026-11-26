"""Adapt SotC's active read-only mip-tail family to the 0.18/FEX cache.

Donor: PC 732cb37d3470 + Android 0366868550, SOTC_MIP_TAIL default 2.
Keep the newer 0.18 layout/overflow code and its deferred Vulkan lifetime.
Apply after port_sotc_texture_find_memo. No renderer or CPU runtime replacement.
"""
from pathlib import Path


POLICY = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdlib>
#include "common/elf_info.h"
#include "common/types.h"

namespace VideoCore {
// BACHATA_SOTC_MIP_TAIL_V1: 0 off, 1 streamed T#, 2 all eligible read-only T#.
inline u32 SotcMipTailMode() {
    const auto& serial = Common::ElfInfo::Instance().GameSerial();
    if (serial != "CUSA08809" && serial != "CUSA08034") return 0;
    static const u32 mode = [] {
        const char* value = std::getenv("SOTC_MIP_TAIL");
        return value && (value[0] == '0' || value[0] == '1' || value[0] == '2')
            ? static_cast<u32>(value[0] - '0') : 2u;
    }();
    return mode;
}
} // namespace VideoCore
'''


INFO_CACHE = r'''
namespace {
// The raw T# and is_depth are all descriptor inputs to ImageInfo. Neo mode is
// included because it also selects the tiling layout. No cache for other titles.
struct SotcTsharpInfoEntry {
    std::array<u64, 4> sharp{};
    bool is_depth{};
    bool neo_mode{};
    bool valid{};
    u8 rebase_state{};
    ImageInfo info;
    ImageInfo rebased;
};

SotcTsharpInfoEntry& SotcTsharpInfoSlot(const AmdGpu::Image& image, bool is_depth, bool& hit) {
    static constexpr size_t NumEntries = 512;
    static thread_local std::unique_ptr<std::array<SotcTsharpInfoEntry, NumEntries>> cache =
        std::make_unique<std::array<SotcTsharpInfoEntry, NumEntries>>();
    std::array<u64, 4> sharp;
    static_assert(sizeof(image) == sizeof(sharp));
    std::memcpy(sharp.data(), &image, sizeof(sharp));
    const bool neo_mode = Libraries::Kernel::sceKernelIsNeoMode();
    const u64 hash = (sharp[0] * 0x9E3779B97F4A7C15ULL) ^
                     (sharp[1] * 0xC2B2AE3D27D4EB4FULL) ^
                     (sharp[2] * 0x165667B19E3779F9ULL) ^
                     (sharp[3] * 0x27D4EB2F165667C5ULL) ^ u64{is_depth} ^
                     (u64{neo_mode} << 1);
    auto& entry = (*cache)[(hash ^ (hash >> 29)) % NumEntries];
    hit = entry.valid && entry.is_depth == is_depth && entry.neo_mode == neo_mode &&
          entry.sharp == sharp;
    if (!hit) {
        entry.sharp = sharp;
        entry.is_depth = is_depth;
        entry.neo_mode = neo_mode;
        entry.valid = false;
        entry.rebase_state = 0;
    }
    return entry;
}
} // namespace

'''


REBASE = r'''
std::optional<ImageInfo> ImageInfo::CachedRebase(const AmdGpu::Image& image,
                                               const Shader::ImageResource& resource) {
    if (!SotcMipTailMode()) return std::nullopt;
    bool hit;
    auto& entry = SotcTsharpInfoSlot(image, resource.is_depth, hit);
    if (!hit) static_cast<void>(ImageInfo{image, resource});
    if (entry.rebase_state == 0) {
        entry.rebased = entry.info;
        entry.rebase_state = entry.rebased.RebaseToMip(image.base_level) ? 1 : 2;
    }
    return entry.rebase_state == 1 ? std::optional{entry.rebased} : std::nullopt;
}

bool ImageInfo::RebaseToMip(u32 base) {
    // Macro tiling depends on the original mip index; its newer 0.18
    // macro-to-micro fallback must not be replaced by the donor's older math.
    if (!guest_size || base == 0 || base >= resources.levels ||
        AmdGpu::IsMacroTiled(array_mode) || alt_tile || bank_swizzle != 0 ||
        props.is_volume || props.is_depth || num_samples != 1 || num_bits < 8) {
        return false;
    }
    const ImageInfo full = *this;
    const u32 dropped = full.mips_layout[base].offset;
    if (dropped >= full.guest_size || guest_address > UINT64_MAX - dropped) return false;
    guest_address += dropped;
    size.width = std::max(size.width >> base, 1u);
    size.height = std::max(size.height >> base, 1u);
    size.depth = std::max(size.depth >> base, 1u);
    pitch = std::max(pitch >> base, 1u);
    resources.levels -= base;
    UpdateSize();
    bool same = guest_size != 0 && guest_size == full.guest_size - dropped;
    for (u32 mip = 0; same && mip < resources.levels; ++mip) {
        const auto& tail = mips_layout[mip];
        const auto& original = full.mips_layout[base + mip];
        same = tail.size == original.size && tail.pitch == original.pitch &&
               tail.height == original.height && tail.offset == original.offset - dropped;
    }
    // DetileImage dispatches complete groups of 64 elements.
    if (!same || (props.is_tiled && (guest_size / (num_bits / 8)) % 64 != 0)) {
        *this = full;
        return false;
    }
    sotc_first_mip = static_cast<u8>(base);
    sotc_dropped_bytes = dropped;
    return true;
}

'''


WRITE_HELPER = r'''
// Copies/clears can first acquire GPU data outside FindImage. A tail decision
// must see those writes even when no image was registered or unregistered.
inline std::atomic<u64> sotc_mip_tail_gpu_epoch{1};
void NoteSotcMipTailWrite(const Image& image);
inline void MarkMipTailWriterIntent(Image& image) {
    if (!SotcMipTailMode()) return;
    if (!image.binding.mip_tail_writer && False(image.flags & ImageFlagBits::GpuModified)) {
        // Eligibility changed before the actual GPU write (two-pass binding).
        sotc_mip_tail_gpu_epoch.fetch_add(1, std::memory_order_relaxed);
    }
    image.binding.mip_tail_writer = 1u;
}
inline void MarkMipTailGpuModified(Image& image) {
    if (False(image.flags & ImageFlagBits::GpuModified) && SotcMipTailMode()) {
        sotc_mip_tail_gpu_epoch.fetch_add(1, std::memory_order_relaxed);
        if (image.info.sotc_first_mip) NoteSotcMipTailWrite(image);
    }
    image.flags |= ImageFlagBits::GpuModified;
}

'''


TAIL_METHODS = r'''
// Always derive the view from the original T#, including the re-find pass.
static void SetSotcMipTailView(TextureCache::ImageDesc& desc, int view_mip) {
    const u32 original_base = desc.rebase_mip;
    const u32 base = view_mip > 0 ? u32(view_mip) : desc.rebased_now ? 0u : original_base;
    const u32 shift = desc.rebased_now && original_base > base ? original_base - base : 0u;
    desc.view_info.range.base.level = base;
    desc.view_info.min_lod = desc.orig_min_lod > 256 * shift
        ? desc.orig_min_lod - 256 * shift : 0u;
}

void TextureCache::ImageDesc::InitMipTail(const AmdGpu::Image& image,
                                         const Shader::ImageResource& resource) {
    const u32 mode = SotcMipTailMode();
    const auto image_type = image.GetType();
    if (!mode || type != BindingType::Texture || resource.is_depth ||
        resource.mip_fallback_mode != Shader::MipStorageFallbackMode::None ||
        image_type == AmdGpu::ImageType::Color3D ||
        image_type == AmdGpu::ImageType::Color2DMsaa ||
        image_type == AmdGpu::ImageType::Color2DMsaaArray || image.base_level == 0 ||
        image.base_level > image.last_level || (mode == 1 && !image.lod_hw_cnt_en)) {
        return;
    }
    rebase_mip = static_cast<u8>(image.base_level);
    orig_min_lod = static_cast<u16>(image.min_lod);
    orig_base_layer = view_info.range.base.layer;
    other_info = ImageInfo::CachedRebase(image, resource);
}

bool TextureCache::IsMipTailIdle(const Image& image) const {
    return !image.binding.is_bound && !image.binding.is_target &&
           !image.binding.mip_tail_writer &&
           scheduler.CurrentTick() - image.tick_accessed_last > 32;
}

void TextureCache::FreeMipTail(ImageId image_id) {
    auto& image = slot_images[image_id];
    ASSERT_MSG(image.info.sotc_first_mip && False(image.flags & ImageFlagBits::GpuModified),
               "Only unmodified read-only mip tails may be retired without readback");
    if (image.binding.is_bound || image.binding.is_target) image.binding.needs_rebind = 1u;
    // FreeImage unregisters immediately; backing/views are destroyed by the
    // existing scheduler deferred operation after their submission completes.
    FreeImage(image_id);
}

bool TextureCache::DecideMipTail(ImageDesc& desc, bool exact_fmt) {
    // A previous overlap may have borrowed a slice of a larger array. A re-find
    // starts from the original T# layer before applying the new overlap result.
    desc.view_info.range.base.layer = desc.orig_base_layer;
    if (desc.rebased_now) {
        std::swap(desc.info, *desc.other_info);
        desc.rebased_now = false;
    }
    if (!desc.other_info) return false;
    const auto use_tail = [&desc] {
        std::swap(desc.info, *desc.other_info);
        desc.rebased_now = true;
        return true;
    };
    const auto& tail = *desc.other_info;
    if (FindMemoEnabled()) {
        if (MemoLookup(tail, exact_fmt, false)) return use_tail();
        if (MemoLookup(desc.info, exact_fmt, false)) return false;
    }
    ImageIds ids;
    ForEachImageInRegion(tail.guest_address, tail.guest_size,
                         [&](ImageId id, Image&) { ids.push_back(id); });
    ImageId match{};
    for (const auto id : ids) {
        const auto& image = slot_images[id];
        if (!image.binding.needs_rebind &&
            IsSotcMemoPerfectMatch(image.info, tail, exact_fmt) &&
            !(image.info.resources < tail.resources)) match = id;
    }
    bool writer = false;
    for (const auto id : ids) {
        const auto& image = slot_images[id];
        // 0.18 discovers storage in the first pass and marks it GPU-written in
        // FindTexture in the second pass. Do not create a tail in that interval.
        writer |= id != match && (True(image.flags & ImageFlagBits::GpuModified) ||
                  image.binding.is_target || image.binding.mip_tail_writer);
    }
    if (writer) {
        if (match && slot_images[match].info.sotc_first_mip &&
            False(slot_images[match].flags & ImageFlagBits::GpuModified)) FreeMipTail(match);
        return false;
    }
    if (match) return use_tail();
    bool live_full = false;
    ForEachImageInRegion(desc.info.guest_address, 1, [&](ImageId, Image& image) {
        live_full |= image.info.guest_address == desc.info.guest_address && !IsMipTailIdle(image);
    });
    return live_full ? false : use_tail();
}

void TextureCache::PruneMipTails(ImageId image_id) {
    const auto& info = slot_images[image_id].info;
    if (!info.sotc_first_mip) return;
    const VAddr chain = info.guest_address - info.sotc_dropped_bytes;
    ImageIds stale;
    ForEachImageInRegion(chain, u64{info.guest_size} + info.sotc_dropped_bytes,
                         [&](ImageId id, Image& other) {
        if (id != image_id && other.info.sotc_first_mip &&
            other.info.guest_address - other.info.sotc_dropped_bytes == chain &&
            IsMipTailIdle(other) && False(other.flags & ImageFlagBits::GpuModified)) {
            stale.push_back(id);
        }
    });
    for (const auto id : stale) FreeMipTail(id);
}

'''


LOOKUP = r'''
    const bool tail_candidate = desc.rebase_mip != 0 && SotcMipTailMode() != 0;
    if (tail_candidate) DecideMipTail(desc, exact_fmt);
    const bool memo_writer = SotcMipTailMode() && desc.type != BindingType::Texture;
    const bool use_find_memo = FindMemoEnabled();
    if (use_find_memo) {
        if (const auto memo_id = MemoLookup(info, exact_fmt, memo_writer)) {
            auto& image = slot_images[memo_id];
            image.tick_accessed_last = scheduler.CurrentTick();
            if (memo_writer) MarkMipTailWriterIntent(image);
            TouchImage(image);
            if (tail_candidate) SetSotcMipTailView(desc, -1);
            return memo_id;
        }
    }
'''


def apply(root: Path):
    root = Path(root)

    def edit(rel, old, new, expected=1):
        path = root / rel
        text = path.read_text()
        if text.count(old) != expected:
            raise RuntimeError(f'SotC mip-tail anchor drift: {rel}: {old[:100]!r}')
        path.write_text(text.replace(old, new))

    tc = 'src/video_core/texture_cache/texture_cache.cpp'
    th = 'src/video_core/texture_cache/texture_cache.h'
    ic = 'src/video_core/texture_cache/image_info.cpp'
    ih = 'src/video_core/texture_cache/image_info.h'
    imgh = 'src/video_core/texture_cache/image.h'
    imgc = 'src/video_core/texture_cache/image.cpp'
    rt = 'src/video_core/renderer_vulkan/vk_runtime.cpp'
    (root / 'src/video_core/texture_cache/sotc_mip_tail_policy.h').write_text(POLICY)
    edit(ih, '#include "common/types.h"', '#include <optional>\n#include "common/types.h"')
    edit(ih, '    void UpdateSize();', '''    void UpdateSize();
    bool RebaseToMip(u32 base);
    static std::optional<ImageInfo> CachedRebase(const AmdGpu::Image& image,
                                                const Shader::ImageResource& resource);''')
    edit(ih, '    u32 stencil_size{};', '''    u32 stencil_size{};
    // Original-chain mip at level zero; zero denotes the unchanged full chain.
    u8 sotc_first_mip{};
    u32 sotc_dropped_bytes{};''')
    edit(ic, '#include "common/assert.h"', '''#include <array>
#include <cstring>
#include <memory>
#include "video_core/texture_cache/sotc_mip_tail_policy.h"
#include "common/assert.h"''')
    ctor = 'ImageInfo::ImageInfo(const AmdGpu::Image& image, const Shader::ImageResource& desc) noexcept {'
    edit(ic, ctor, INFO_CACHE + ctor + '''
    SotcTsharpInfoEntry* cached = nullptr;
    if (SotcMipTailMode()) {
        bool hit;
        cached = &SotcTsharpInfoSlot(image, desc.is_depth, hit);
        if (hit) {
            *this = cached->info;
            return;
        }
    }''')
    edit(ic, '''    alt_tile = Libraries::Kernel::sceKernelIsNeoMode() && image.alt_tile_mode;
    UpdateSize();
}''', '''    alt_tile = Libraries::Kernel::sceKernelIsNeoMode() && image.alt_tile_mode;
    UpdateSize();
    if (cached) {
        cached->info = *this;
        cached->valid = true;
    }
}''')
    edit(ic, 'bool ImageInfo::IsCompatible(const ImageInfo& info) const {',
         REBASE + 'bool ImageInfo::IsCompatible(const ImageInfo& info) const {')
    edit(imgh, '#include <deque>', '#include <atomic>\n#include <deque>')
    edit(imgh, '#include "video_core/texture_cache/image_info.h"',
         '#include "video_core/texture_cache/image_info.h"\n#include "video_core/texture_cache/sotc_mip_tail_policy.h"')
    edit(imgh, '        u32 force_general : 1;', '        u32 force_general : 1;\n        u32 mip_tail_writer : 1;')
    edit(imgh, '} // namespace VideoCore', WRITE_HELPER + '} // namespace VideoCore')
    edit(imgc, '} // namespace VideoCore', '''void NoteSotcMipTailWrite(const Image& image) {
    // Preserve unexpected GPU data; never silently discard a written tail.
    static std::atomic<u32> shown{0};
    if (shown.fetch_add(1, std::memory_order_relaxed) < 8) {
        LOG_ERROR(Render_Vulkan, "BACHATA_MIP_TAIL_WRITE addr={:#x} original_mip={}",
                  image.info.guest_address, image.info.sotc_first_mip);
    }
}

} // namespace VideoCore''')
    edit(th, '        BindingType type{BindingType::Texture};', '''        BindingType type{BindingType::Texture};
        u8 rebase_mip{};
        bool rebased_now{};
        u16 orig_min_lod{};
        u32 orig_base_layer{};
        std::optional<ImageInfo> other_info;
        void InitMipTail(const AmdGpu::Image& image, const Shader::ImageResource& resource);''')
    edit(th, '              type{desc.is_written ? BindingType::Storage : BindingType::Texture} {}',
         '''              type{desc.is_written ? BindingType::Storage : BindingType::Texture} {
            InitMipTail(image, desc);
        }''')
    edit(th, '        bool exact_fmt{};', '        bool exact_fmt{};\n        bool writer{};')
    edit(th, '        u64 image_uid{};', '''        u64 image_uid{};
        u64 gpu_epoch{};
        u64 alias_generation{};''')
    edit(th, '    FindMemo& MemoSlot(const ImageInfo& info, bool exact_fmt);',
         '    FindMemo& MemoSlot(const ImageInfo& info, bool exact_fmt, bool writer = false);')
    edit(th, '    ImageId MemoLookup(const ImageInfo& info, bool exact_fmt);', '''    ImageId MemoLookup(const ImageInfo& info, bool exact_fmt, bool writer = false);
    bool DecideMipTail(ImageDesc& desc, bool exact_fmt);
    bool IsMipTailIdle(const Image& image) const;
    void FreeMipTail(ImageId image_id);
    void PruneMipTails(ImageId image_id);''')
    edit(tc, 'TextureCache::FindMemo& TextureCache::MemoSlot(const ImageInfo& info, bool exact_fmt) {',
         'TextureCache::FindMemo& TextureCache::MemoSlot(const ImageInfo& info, bool exact_fmt, bool writer) {')
    edit(tc, '(u64{info.size.height} << 41) ^ u64{exact_fmt};',
         '(u64{info.size.height} << 41) ^ u64{exact_fmt} ^ (u64{writer} << 1);')
    edit(tc, '''ImageId TextureCache::MemoLookup(const ImageInfo& info, bool exact_fmt) {
    const auto& memo = MemoSlot(info, exact_fmt);''', '''ImageId TextureCache::MemoLookup(const ImageInfo& info, bool exact_fmt, bool writer) {
    const auto& memo = MemoSlot(info, exact_fmt, writer);''')
    edit(tc, '        memo.type != info.type || memo.exact_fmt != exact_fmt || !memo.image_id ||',
         '        memo.type != info.type || memo.exact_fmt != exact_fmt || memo.writer != writer || !memo.image_id ||')
    edit(tc, '''    return memo.image_id;
}''', '''    // Tail eligibility and writer retirement depend on overlapping images at
    // other bases as well as the ordinary perfect-match address generation.
    if ((info.sotc_first_mip || image.info.sotc_first_mip || writer) &&
        (memo.alias_generation != TargetRegistryEpoch() ||
         memo.gpu_epoch != sotc_mip_tail_gpu_epoch.load(std::memory_order_relaxed))) return {};
    if (writer && image.info.sotc_first_mip) return {};
    return memo.image_id;
}''')
    from port_sotc_texture_find_memo import LOOKUP as MEMO_LOOKUP
    edit(tc, MEMO_LOOKUP, LOOKUP)
    edit(tc, '''    ImageIds image_ids;
    ForEachImageInRegion(info.guest_address, info.guest_size,
                         [&](ImageId image_id, Image& image) { image_ids.push_back(image_id); });''', '''    ImageIds image_ids;
    ImageIds tails;
    ForEachImageInRegion(info.guest_address, info.guest_size, [&](ImageId id, Image& image) {
        if (memo_writer && image.info.sotc_first_mip &&
            False(image.flags & ImageFlagBits::GpuModified)) tails.push_back(id);
        else image_ids.push_back(id);
    });
    for (const auto id : tails) FreeMipTail(id);''')
    edit(tc, '''            MemoSlot(info, exact_fmt) = FindMemo{
                info.guest_address, info.guest_size, info.size, info.pixel_format, info.type,
                exact_fmt, MemoGeneration(info.guest_address), image_id, image.image_uid};''',
         '''            MemoSlot(info, exact_fmt, memo_writer) = FindMemo{
                info.guest_address, info.guest_size, info.size, info.pixel_format, info.type,
                exact_fmt, memo_writer, MemoGeneration(info.guest_address), image_id, image.image_uid,
                sotc_mip_tail_gpu_epoch.load(std::memory_order_relaxed), TargetRegistryEpoch()};''')
    edit(tc, '''        image_id = slot_images.Insert(instance, runtime, slot_image_views, info);
        RegisterImage(image_id);
    }

    Image& image = slot_images[image_id];
    image.tick_accessed_last = scheduler.CurrentTick();''', '''        image_id = slot_images.Insert(instance, runtime, slot_image_views, info);
        RegisterImage(image_id);
        if (tail_candidate) PruneMipTails(image_id);
    }

    Image& image = slot_images[image_id];
    if (memo_writer) MarkMipTailWriterIntent(image);
    image.tick_accessed_last = scheduler.CurrentTick();''')
    edit(tc, '''    // If the image requested is a subresource of the image from cache record its location.
    if (view_mip > 0) {''', '''    // If the image requested is a subresource of the image from cache record its location.
    if (tail_candidate) {
        SetSotcMipTailView(desc, view_mip);
    } else if (view_mip > 0) {''')
    edit(tc, 'ImageId TextureCache::FindImage(ImageDesc& desc, bool exact_fmt) {',
         TAIL_METHODS + 'ImageId TextureCache::FindImage(ImageDesc& desc, bool exact_fmt) {')
    # Range lookups feed compute-copy/clear optimizations and must not write tails.
    pos = (root / tc).read_text().index('ImageId TextureCache::FindImageFromRange(')
    text = (root / tc).read_text()
    end = text.index('\nImageView& TextureCache::FindTexture', pos)
    block = text[pos:end]
    old = 'if (image.info.guest_address != address) {'
    assert block.count(old) == 1
    block = block.replace(old, 'if (image.info.guest_address != address || image.info.sotc_first_mip) {')
    (root / tc).write_text(text[:pos] + block + text[end:])
    edit(tc, '                if (image.info.guest_address != desc.info.stencil_addr) {',
         '                if (image.info.guest_address != desc.info.stencil_addr || image.info.sotc_first_mip) {')
    # Same chain-base shader writes invalidate a rebased range; DMA already uses
    # the existing any_overlap=true path. Ordinary full images retain their policy.
    pos = (root / tc).read_text().index('void TextureCache::InvalidateMemoryFromGPU(')
    text = (root / tc).read_text()
    end = text.index('\nvoid TextureCache::UnmapMemory', pos)
    block = text[pos:end]
    old = 'if (image.info.guest_address != address) {'
    assert block.count(old) == 1
    block = block.replace(old, '''if (image.info.guest_address != address &&
            (!image.info.sotc_first_mip ||
             image.info.guest_address - image.info.sotc_dropped_bytes != address)) {''')
    (root / tc).write_text(text[:pos] + block + text[end:])
    edit(tc, '''    if (True(image.flags & ImageFlagBits::MaybeCpuDirty) &&
        False(image.flags & ImageFlagBits::CpuDirty)) {''', '''    // A write to another mip of a small tail need not change its first texels.
    // Reupload the tail on a maybe-dirty fault instead of trusting that prefix.
    if (True(image.flags & ImageFlagBits::MaybeCpuDirty) &&
        False(image.flags & ImageFlagBits::CpuDirty) && !image.info.sotc_first_mip) {''')
    edit(tc, 'image.flags |= ImageFlagBits::GpuModified;', 'MarkMipTailGpuModified(image);', expected=3)
    edit(rt, '    dst->flags |= (src->flags & VideoCore::ImageFlagBits::GpuModified);', '''    if (True(src->flags & VideoCore::ImageFlagBits::GpuModified)) {
        VideoCore::MarkMipTailGpuModified(*dst);
    }''', expected=3)
    edit(rt, '    dst->flags |= VideoCore::ImageFlagBits::GpuModified;',
         '    VideoCore::MarkMipTailGpuModified(*dst);', expected=3)
    # Target reuse and overlap propagation may publish a writer without a new
    # FindImage call. Publish its eligibility change before any tail memo probe.
    edit(tc, '        img.binding.is_target=1;', '''        MarkMipTailWriterIntent(img);
        img.binding.is_target=1;''')
    edit(tc, '                        GetImage(merged_image_id).binding.is_target = 1u;',
         '''                        auto& merged = GetImage(merged_image_id);
                        MarkMipTailWriterIntent(merged);
                        merged.binding.is_target = 1u;''')
    edit('src/video_core/renderer_vulkan/vk_rasterizer.cpp',
         '        image.binding.is_target = 1u;',
         '''        VideoCore::MarkMipTailWriterIntent(image);
        image.binding.is_target = 1u;''', expected=2)
    edit(tc, '''void TextureCache::TouchImage(const Image& image) {
    lru_cache.Touch(image.lru_id, gc_tick);
}''', '''void TextureCache::TouchImage(const Image& image) {
    // A deferred slot can still be inspected solely to observe needs_rebind.
    // UnregisterImage already released its LRU node, possibly reused since.
    if (True(image.flags & ImageFlagBits::Registered)) {
        lru_cache.Touch(image.lru_id, gc_tick);
    }
}''')
    return {'sotc_mip_tail': 'Mode2; exact layout; writer/alias epochs; deferred retirement; CPU refresh'}
