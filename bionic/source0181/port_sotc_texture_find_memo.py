"""SotC's active internal perfect-match image lookup memo for the 0.18 cache.

The Android-effective donor uses FindImage -> MemoLookup for all callers. Keep
the existing target memo, image uploads, views and layout transitions intact.
Only a result of the unmodified perfect-match scan may enter this memo; overlap
results can rewrite mip/layer state and must continue through ResolveOverlap.
"""
from pathlib import Path


MEMBERS = r'''
    // BACHATA_SOTC_TEXTURE_FIND_MEMO_V1: lookup results only, never Vulkan views.
    struct FindMemo {
        VAddr guest_address{};
        u32 guest_size{};
        Extent3D size{};
        vk::Format pixel_format{};
        AmdGpu::ImageType type{};
        bool exact_fmt{};
        u64 generation{};
        ImageId image_id{};
        u64 image_uid{};
    };
    static constexpr size_t NumFindMemos = 1024;
    static constexpr size_t NumFindMemoAddressGenerations = 4096;
    std::array<FindMemo, NumFindMemos> find_memos{};
    std::array<u64, NumFindMemoAddressGenerations> find_memo_address_generations{};
    static size_t FindMemoAddressSlot(VAddr address) {
        return static_cast<size_t>((u64{address >> 8} * 0x9E3779B97F4A7C15ULL) >> 52);
    }
    bool FindMemoEnabled() const;
    FindMemo& MemoSlot(const ImageInfo& info, bool exact_fmt);
    u64 MemoGeneration(VAddr address) const;
    // All lookup/generation accesses run under the existing texture mutex.
    ImageId MemoLookup(const ImageInfo& info, bool exact_fmt);

'''


METHODS = r'''
// Match the existing perfect-match scan, including compatible formats and the
// 1x1x1 type exception. A lookup memo does not decide whether contents are dirty:
// FindTexture/UpdateImage still perform uploads and binding side effects.
static bool IsSotcMemoPerfectMatch(const ImageInfo& cached, const ImageInfo& requested,
                                  bool exact_fmt) {
    return cached.guest_address == requested.guest_address &&
           cached.guest_size == requested.guest_size && cached.size == requested.size &&
           IsVulkanFormatCompatible(cached.pixel_format, requested.pixel_format) &&
           (cached.type == requested.type || requested.size == Extent3D{1, 1, 1}) &&
           (!exact_fmt || cached.pixel_format == requested.pixel_format);
}

bool TextureCache::FindMemoEnabled() const {
    static const bool configured = [] {
        const char* value = std::getenv("BACHATA_SOTC_FIND_MEMO");
        return !value || value[0] != '0';
    }();
    const auto& serial = Common::ElfInfo::Instance().GameSerial();
    return configured && (serial == "CUSA08809" || serial == "CUSA08034");
}

TextureCache::FindMemo& TextureCache::MemoSlot(const ImageInfo& info, bool exact_fmt) {
    const u64 hash = (u64{info.guest_address} * 0x9E3779B97F4A7C15ULL) ^
                     (u64{info.guest_size} * 0xC2B2AE3D27D4EB4FULL) ^
                     (u64(info.pixel_format) << 7) ^ (u64{info.size.width} << 23) ^
                     (u64{info.size.height} << 41) ^ u64{exact_fmt};
    return find_memos[(hash ^ (hash >> 31)) % NumFindMemos];
}

u64 TextureCache::MemoGeneration(VAddr address) const {
    // All perfect matches share the first page and guest base. Page-vector
    // erase preserves insertion order, so changes at other bases cannot alter
    // their winner. Hash collisions only cause an extra full lookup.
    return find_memo_address_generations[FindMemoAddressSlot(address)];
}

ImageId TextureCache::MemoLookup(const ImageInfo& info, bool exact_fmt) {
    const auto& memo = MemoSlot(info, exact_fmt);
    if (memo.generation != MemoGeneration(info.guest_address) ||
        memo.guest_address != info.guest_address || memo.guest_size != info.guest_size ||
        memo.size != info.size || memo.pixel_format != info.pixel_format ||
        memo.type != info.type || memo.exact_fmt != exact_fmt || !memo.image_id ||
        !slot_images.IsAllocated(memo.image_id)) {
        return {};
    }
    const auto& image = slot_images[memo.image_id];
    // Unregister precedes deferred slot destruction. Neither a surviving slot
    // nor a new occupant of that slot grants the old memo a lifetime extension.
    if (image.image_uid != memo.image_uid ||
        False(image.flags & ImageFlagBits::Registered) || image.binding.needs_rebind ||
        image.info.resources < info.resources ||
        !IsSotcMemoPerfectMatch(image.info, info, exact_fmt)) {
        return {};
    }
    return memo.image_id;
}

'''


LOOKUP = r'''
    const bool use_find_memo = FindMemoEnabled();
    if (use_find_memo) {
        if (const auto memo_id = MemoLookup(info, exact_fmt)) {
            auto& image = slot_images[memo_id];
            image.tick_accessed_last = scheduler.CurrentTick();
            TouchImage(image);
            return memo_id;
        }
    }
'''


REMEMBER = r'''
    // Only the perfect-match loop above can populate this memo. Overlap
    // resolution below may change desc.view_info or replace another image.
    if (use_find_memo && image_id) {
        const auto& image = slot_images[image_id];
        if (!(image.info.resources < info.resources) &&
            True(image.flags & ImageFlagBits::Registered) && !image.binding.needs_rebind) {
            MemoSlot(info, exact_fmt) = FindMemo{
                info.guest_address, info.guest_size, info.size, info.pixel_format, info.type,
                exact_fmt, MemoGeneration(info.guest_address), image_id, image.image_uid};
        }
    }

'''


def apply(root):
    root = Path(root)
    if (root / "src").is_dir():
        root = root / "src"
    header = "video_core/texture_cache/texture_cache.h"
    source = "video_core/texture_cache/texture_cache.cpp"
    originals = {rel: (root / rel).read_text() for rel in (header, source)}
    updates = dict(originals)

    def edit(rel, old, new):
        count = updates[rel].count(old)
        if count != 1:
            raise RuntimeError(f"SotC texture find memo anchor {rel}: {count}: {old[:100]}")
        updates[rel] = updates[rel].replace(old, new, 1)

    edit(header, "#include <atomic>", "#include <array>\n#include <atomic>")
    edit(header, "    Common::SlotVector<Image> slot_images;",
         MEMBERS + "    Common::SlotVector<Image> slot_images;")
    edit(source, "#include <xxhash.h>", "#include <cstdlib>\n#include <xxhash.h>")
    edit(source, "ImageId TextureCache::FindImage(ImageDesc& desc, bool exact_fmt) {",
         METHODS + "ImageId TextureCache::FindImage(ImageDesc& desc, bool exact_fmt) {")
    edit(source, """    std::scoped_lock lock{mutex};
    ImageIds image_ids;
    ForEachImageInRegion(info.guest_address, info.guest_size,""", """    std::scoped_lock lock{mutex};
""" + LOOKUP + """    ImageIds image_ids;
    ForEachImageInRegion(info.guest_address, info.guest_size,""")
    edit(source, "    // Try to resolve overlaps (if any)",
         REMEMBER + "    // Try to resolve overlaps (if any)")
    edit(source, "    image.flags |= ImageFlagBits::Registered;\n",
         "    ++find_memo_address_generations[FindMemoAddressSlot(image.info.guest_address)];\n"
         "    image.flags |= ImageFlagBits::Registered;\n")
    edit(source, "    image.flags &= ~ImageFlagBits::Registered;\n",
         "    ++find_memo_address_generations[FindMemoAddressSlot(image.info.guest_address)];\n"
         "    image.flags &= ~ImageFlagBits::Registered;\n")
    for rel in updates:
        if (root / rel).read_text() != originals[rel]:
            raise RuntimeError("Concurrent SotC texture memo source edit: " + rel)
    for rel, value in updates.items():
        (root / rel).write_text(value)
    return {
        "titles": ["CUSA08809", "CUSA08034"],
        "scope": "internal FindImage perfect matches for every binding caller",
        "invalidation": "per-address registration generation, allocated slot, UID, rebind",
        "effects": "scheduler tick and LRU on hits; existing upload/view/layout paths retained",
        "exclusions": "overlap results, target memo duplication, unused stage replay",
        "abi": "runtime lookup only; no shader or pipeline cache ABI change",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    print(apply(parser.parse_args().root))
