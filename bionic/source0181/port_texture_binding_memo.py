"""Order's active texture lookup memo family, adapted to 0.18/FEX ownership.

Donor: The-Order-1886_pc c53cd01 + Android 756a4f0 effective renderer.
Keep every descriptor/mapping validation and per-binding side effect in 0.18.
No PreparedStage, descriptor pointer borrowing, or speculative workers.
"""
from pathlib import Path


TEXTURE_METHODS = r'''
// BACHATA_ORDER_TEXTURE_BINDING_MEMO_V1
bool TextureCache::BindingMemoEnabled() const {
    static const bool configured = [] {
        const char* value = std::getenv("BACHATA_ORDER_TEXTURE_MEMO");
        return !value || std::atoi(value) != 0;
    }();
    return configured && Common::ElfInfo::Instance().GameSerial() == "CUSA00785";
}

u64 TextureCache::MemoImageUid(ImageId image_id) {
    std::scoped_lock lock{mutex};
    if (!image_id || !slot_images.IsAllocated(image_id)) return 0;
    const auto& image = slot_images[image_id];
    if (!(image.flags & ImageFlagBits::Registered) || image.binding.needs_rebind) return 0;
    return image.image_uid;
}

bool TextureCache::TryMemoImage(ImageId image_id, u64 uid, u64 generation) {
    if (!uid || generation != RegistryGeneration()) return false;
    std::scoped_lock lock{mutex};
    if (generation != RegistryGeneration() || !image_id ||
        !slot_images.IsAllocated(image_id)) return false;
    auto& image = slot_images[image_id];
    if (image.image_uid != uid || !(image.flags & ImageFlagBits::Registered) ||
        image.binding.needs_rebind) return false;
    // Preserve FindImage's accesses even though its region/overlap scan is skipped.
    image.tick_accessed_last = scheduler.CurrentTick();
    TouchImage(image);
    return true;
}

bool TextureCache::IsStructuralImageMiss(VAddr address, u64 size, u64 generation) {
    std::scoped_lock lock{mutex};
    if (!size || generation != RegistryGeneration()) return false;
    bool present = false;
    ForEachImageInRegion(address, size, [&](ImageId, Image& image) {
        // Eligibility (GpuModified/Dirty) can change without a registration.
        // Remember only absence, never a currently ineligible/ambiguous image.
        present |= image.info.guest_address == address;
    });
    return !present && generation == RegistryGeneration();
}
'''

RASTER_MEMBERS = r'''
    // Runtime-only caches: no shader/PSO ABI change. Bindings keep their own
    // descriptor values, including any mip/layer adjustment from FindImage.
    struct ImageDescCacheEntry {
        std::array<u64, 4> sharp{};
        u32 flags = ~0u;
        VideoCore::TextureCache::ImageDesc desc;
        VideoCore::TextureCache::ImageDesc found_desc;
        VideoCore::ImageId found_id{};
        u64 found_uid = 0;
        u64 found_generation = ~0ull;
        u64 last_use = 0;
    };
    using ImageDescMemo = std::array<ImageDescCacheEntry, 4096>;
    std::unique_ptr<ImageDescMemo> image_desc_cache;
    u64 desc_use_counter = 0;
    ImageDescCacheEntry& CachedImageDescEntry(const AmdGpu::Image& sharp,
                                            const Shader::ImageResource& res);
    VideoCore::TextureCache::ImageDesc CachedImageDesc(const AmdGpu::Image& sharp,
                                                      const Shader::ImageResource& res);
    VideoCore::ImageId FindBoundImage(const AmdGpu::Image& sharp,
                                    const Shader::ImageResource& res,
                                    VideoCore::TextureCache::ImageDesc& desc);

    struct TargetMemo {
        std::array<u8, 256> key{};
        u32 key_size = 0;
        u64 generation = ~0ull;
        u64 image_uid = 0;
        VideoCore::ImageId image_id{};
        VideoCore::TextureCache::ImageDesc desc;
    };
    std::array<TargetMemo, 64> target_memo{};
    std::array<TargetMemo, AmdGpu::NUM_COLOR_BUFFERS + 1> last_targets{};
    template <typename MakeDesc, typename... Parts>
    VideoCore::ImageId FindTargetMemoized(VideoCore::TextureCache::ImageDesc& desc,
                                         TargetMemo& last, MakeDesc&& make_desc,
                                         const Parts&... parts);
'''

RASTER_METHODS = r'''
Rasterizer::ImageDescCacheEntry& Rasterizer::CachedImageDescEntry(
    const AmdGpu::Image& sharp, const Shader::ImageResource& res) {
    std::array<u64, 4> key;
    static_assert(sizeof(key) == sizeof(sharp));
    std::memcpy(key.data(), &sharp, sizeof(key));
    const u32 flags = u32(res.is_written) | u32(res.is_depth) << 1 | u32(res.is_array) << 2;
    u64 hash = flags * 0x9E3779B97F4A7C15ull;
    for (u64 word : key) {
        hash = (hash ^ word) * 0xFF51AFD7ED558CCDull;
        hash ^= hash >> 32;
    }
    if (!image_desc_cache) image_desc_cache = std::make_unique<ImageDescMemo>();
    auto& cache = *image_desc_cache;
    auto* set = &cache[(hash % (cache.size() / 2)) * 2];
    const auto matches = [&](const ImageDescCacheEntry& entry) {
        return entry.flags == flags && entry.sharp == key;
    };
    auto* entry = matches(set[0]) ? &set[0] : matches(set[1]) ? &set[1]
                 : set[0].last_use <= set[1].last_use ? &set[0] : &set[1];
    if (!matches(*entry)) {
        entry->desc = VideoCore::TextureCache::ImageDesc{sharp, res};
        entry->sharp = key;
        entry->flags = flags;
        entry->found_uid = 0;
        entry->found_generation = ~0ull;
    }
    entry->last_use = ++desc_use_counter;
    return *entry;
}

VideoCore::TextureCache::ImageDesc Rasterizer::CachedImageDesc(
    const AmdGpu::Image& sharp, const Shader::ImageResource& res) {
    if (!texture_cache.BindingMemoEnabled()) return {sharp, res};
    return CachedImageDescEntry(sharp, res).desc;
}

VideoCore::ImageId Rasterizer::FindBoundImage(const AmdGpu::Image& sharp,
                                             const Shader::ImageResource& res,
                                             VideoCore::TextureCache::ImageDesc& desc) {
    if (!texture_cache.BindingMemoEnabled() ||
        res.mip_fallback_mode != Shader::MipStorageFallbackMode::None) {
        return texture_cache.FindImage(desc);
    }
    auto& entry = CachedImageDescEntry(sharp, res);
    const auto saved_key = entry.sharp;
    const u32 saved_flags = entry.flags;
    const u64 generation = texture_cache.RegistryGeneration();
    if (entry.found_generation == generation &&
        texture_cache.TryMemoImage(entry.found_id, entry.found_uid, generation)) {
        desc = entry.found_desc;
        return entry.found_id;
    }
    const auto image_id = texture_cache.FindImage(desc);
    // Lookup can create/merge/retire images and can drain allocation callbacks.
    // Never stamp a stale entry or reuse a recycled slot across that boundary.
    if (generation == texture_cache.RegistryGeneration() && entry.sharp == saved_key &&
        entry.flags == saved_flags) {
        const u64 uid = texture_cache.MemoImageUid(image_id);
        if (uid && generation == texture_cache.RegistryGeneration()) {
            entry.found_id = image_id;
            entry.found_uid = uid;
            entry.found_desc = desc;
            entry.found_generation = generation;
        }
    }
    return image_id;
}

template <typename MakeDesc, typename... Parts>
VideoCore::ImageId Rasterizer::FindTargetMemoized(
    VideoCore::TextureCache::ImageDesc& desc, TargetMemo& last, MakeDesc&& make_desc,
    const Parts&... parts) {
    if (!texture_cache.BindingMemoEnabled()) {
        make_desc();
        return texture_cache.FindImage(desc);
    }
    static_assert((sizeof(Parts) + ...) <= 256);
    std::array<u8, 256> key{};
    u32 key_size = 0;
    const auto append = [&](const auto& part) {
        std::memcpy(key.data() + key_size, &part, sizeof(part));
        key_size += sizeof(part);
    };
    (append(parts), ...);
    const u64 generation = texture_cache.RegistryGeneration();
    const auto matches = [&](const TargetMemo& memo) {
        return memo.key_size == key_size && memo.generation == generation &&
               std::memcmp(memo.key.data(), key.data(), key_size) == 0 &&
               texture_cache.TryMemoImage(memo.image_id, memo.image_uid, generation);
    };
    if (matches(last)) {
        desc = last.desc;
        return last.image_id;
    }
    u64 hash = 0xCBF29CE484222325ull;
    for (u32 i = 0; i < key_size; ++i) hash = (hash ^ key[i]) * 0x100000001B3ull;
    auto& memo = target_memo[hash % target_memo.size()];
    if (matches(memo)) {
        desc = memo.desc;
        last = memo;
        return memo.image_id;
    }
    make_desc();
    const auto image_id = texture_cache.FindImage(desc);
    if (generation == texture_cache.RegistryGeneration()) {
        const u64 uid = texture_cache.MemoImageUid(image_id);
        if (uid && generation == texture_cache.RegistryGeneration()) {
            memo.key = key;
            memo.key_size = key_size;
            memo.generation = generation;
            memo.image_uid = uid;
            memo.image_id = image_id;
            memo.desc = desc;
            last = memo;
        }
    }
    return image_id;
}
'''

BUFFER_METHOD = r'''
ImageId BufferCache::FindImageForTexelBuffer(VAddr address, u32 size) {
    if (!texture_cache.BindingMemoEnabled()) return texture_cache.FindImageFromRange(address, size);
    const u64 generation = texture_cache.RegistryGeneration();
    auto& miss = image_miss_cache[((address >> 6) ^ size * 0x9E3779B1u) % image_miss_cache.size()];
    if (miss.address == address && miss.size == size && miss.generation == generation) return {};
    const auto image_id = texture_cache.FindImageFromRange(address, size);
    if (!image_id && texture_cache.IsStructuralImageMiss(address, size, generation)) {
        miss = {address, size, generation};
    }
    return image_id;
}
'''


def apply(root: Path):
    root = Path(root)
    originals = {}
    updates = {}
    def edit(rel, old, new):
        source = updates.get(rel)
        if source is None:
            source = (root / rel).read_text()
            originals[rel] = source
        if source.count(old) != 1:
            raise RuntimeError(f'Texture memo anchor drift: {rel}: {old[:90]}')
        updates[rel] = source.replace(old, new, 1)

    th = 'src/video_core/texture_cache/texture_cache.h'
    tc = 'src/video_core/texture_cache/texture_cache.cpp'
    rh = 'src/video_core/renderer_vulkan/vk_rasterizer.h'
    rc = 'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    bh = 'src/video_core/buffer_cache/buffer_cache.h'
    bc = 'src/video_core/buffer_cache/buffer_cache.cpp'
    edit(th, '    TileManager& GetTileManager() noexcept {', '''    bool BindingMemoEnabled() const;
    u64 RegistryGeneration() const noexcept {
        return registry_generation.load(std::memory_order_acquire);
    }
    u64 MemoImageUid(ImageId image_id);
    bool TryMemoImage(ImageId image_id, u64 uid, u64 generation);
    bool IsStructuralImageMiss(VAddr address, u64 size, u64 generation);

    TileManager& GetTileManager() noexcept {''')
    edit(th, '    PageTable page_table;', '    std::atomic<u64> registry_generation{0};\n    PageTable page_table;')
    edit(tc, '#include <xxhash.h>', '#include <cstdlib>\n#include <xxhash.h>')
    edit(tc, 'void TextureCache::RegisterImage(ImageId image_id) {',
         TEXTURE_METHODS + '\nvoid TextureCache::RegisterImage(ImageId image_id) {')
    edit(tc, '    image.flags |= ImageFlagBits::Registered;\n',
         '    image.flags |= ImageFlagBits::Registered;\n    registry_generation.fetch_add(1, std::memory_order_release);\n')
    edit(tc, '    image.flags &= ~ImageFlagBits::Registered;\n',
         '    image.flags &= ~ImageFlagBits::Registered;\n    registry_generation.fetch_add(1, std::memory_order_release);\n')
    edit(rh, '    using ImageBindingInfo =', RASTER_MEMBERS + '\n    using ImageBindingInfo =')
    edit(rh, '#pragma once', '#pragma once\n#include <memory>')
    edit(rc, 'void Rasterizer::PrepareRenderState(const GraphicsPipeline* pipeline) {',
         RASTER_METHODS + '\nvoid Rasterizer::PrepareRenderState(const GraphicsPipeline* pipeline) {')
    edit(rc, '''        std::construct_at(&desc, col_buf, hint);
        image_id = bound_images.emplace_back(texture_cache.FindImage(desc));''', '''        const u32 tag = 1;
        image_id = bound_images.emplace_back(FindTargetMemoized(desc, last_targets[cb],
            [&] { std::construct_at(&desc, col_buf, hint); }, tag, col_buf, hint));''')
    edit(rc, '''        std::construct_at(&desc, regs.depth_buffer, regs.depth_view, regs.depth_control,
                          htile_address, hint);
        image_id = bound_images.emplace_back(texture_cache.FindImage(desc));''', '''        const u32 tag = 2;
        image_id = bound_images.emplace_back(FindTargetMemoized(desc,
            last_targets[AmdGpu::NUM_COLOR_BUFFERS], [&] {
                std::construct_at(&desc, regs.depth_buffer, regs.depth_view, regs.depth_control,
                                  htile_address, hint);
            }, tag, regs.depth_buffer, regs.depth_view, regs.depth_control, htile_address, hint));''')
    edit(rc, 'std::tuple{element, image_desc});', 'std::tuple{CachedImageDesc(element, image_desc)});')
    edit(rc, '''                image_id = texture_cache.FindImage(desc);
                auto* image = &texture_cache.GetImage(image_id);''', '''                image_id = FindBoundImage(element, image_desc, desc);
                auto* image = &texture_cache.GetImage(image_id);''')
    edit(rc, 'const VideoCore::TextureCache::ImageDesc probe{tsharp,image_desc};',
         'const auto probe = CachedImageDesc(tsharp, image_desc);')
    edit(rc, 'std::tuple{tsharp, image_desc});', 'std::tuple{CachedImageDesc(tsharp, image_desc)});')
    edit(rc, '''            image_id = texture_cache.FindImage(desc);
            auto* image = &texture_cache.GetImage(image_id);''', '''            image_id = FindBoundImage(tsharp, image_desc, desc);
            auto* image = &texture_cache.GetImage(image_id);''')
    edit(bh, '    const Vulkan::Instance& instance;', '''    ImageId FindImageForTexelBuffer(VAddr address, u32 size);
    struct ImageMiss {
        VAddr address = 0;
        u32 size = 0;
        u64 generation = ~0ull;
    };
    std::array<ImageMiss, 256> image_miss_cache{};

    const Vulkan::Instance& instance;''')
    edit(bh, '#include "common/types.h"',
         '#include "common/types.h"\n#include <array>\n#include "video_core/texture_cache/types.h"')
    edit(bc, 'bool BufferCache::SynchronizeMemoryFromImage(const Buffer* arena, VAddr device_addr, u32 size) {',
         BUFFER_METHOD + '\nbool BufferCache::SynchronizeMemoryFromImage(const Buffer* arena, VAddr device_addr, u32 size) {')
    edit(bc, '    const ImageId image_id = texture_cache.FindImageFromRange(device_addr, size);',
         '    const ImageId image_id = FindImageForTexelBuffer(device_addr, size);')
    # All source anchors must match before any source file changes.
    for rel, source in updates.items():
        if (root / rel).read_text() != originals[rel]:
            raise RuntimeError('Concurrent texture memo source edit: ' + rel)
    for rel, source in updates.items():
        (root / rel).write_text(source)
    return {'title': 'CUSA00785', 'consumers': ['CB/DB targets', 'sampled/storage T#', 'texel buffer misses'],
            'lifetime': 'registration generation + allocated slot + image UID + rebind check',
            'negativeCache': 'structural absence only; dirty/eligibility changes remain observable',
            'abi': 'FEX/0.18 descriptors by value; no shader or pipeline cache ABI change'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    print(apply(parser.parse_args().root))
