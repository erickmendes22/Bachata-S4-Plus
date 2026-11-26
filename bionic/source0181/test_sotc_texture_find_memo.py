#!/usr/bin/env python3
"""Run the effective SotC image memo and registry methods with real slot/LRU code.

FindImage, MemoLookup, Register/Unregister, iteration, TouchImage, FindTexture,
UpdateImage, SlotVector and LeastRecentlyUsedCache come from --source. Vulkan
image construction, the format compatibility boundary, page storage and overlap
resolution are deterministic fixtures. Negative controls must compile and fail
at runtime; passing this host gate does not establish device gameplay parity.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile

def strip_includes(text):
    return re.sub(r"^\s*#(?:include|pragma)[^\n]*\n", "", text, flags=re.M)


def function(source, signature):
    """Extract both inline and out-of-line definitions, ignoring comment braces."""
    assert source.count(signature) == 1, signature
    begin = source.index(signature)
    brace = source.index("{", begin)
    depth, index, state = 1, brace + 1, ""
    while depth:
        char = source[index]
        if state == "line":
            if char == "\n":
                state = ""
        elif state == "block":
            if source[index:index + 2] == "*/":
                state = ""
                index += 1
        elif state in ('"', "'"):
            if char == "\\":
                index += 1
            elif char == state:
                state = ""
        elif source[index:index + 2] == "//":
            state = "line"
            index += 1
        elif source[index:index + 2] == "/*":
            state = "block"
            index += 1
        elif char in ('"', "'"):
            state = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    return source[begin:index]


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <mutex>
#include <numeric>
#include <ranges>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_set>
#include <utility>
#include <vector>
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define DEBUG_ASSERT(x) assert(x)
#define LOG_WARNING(...) ((void)0)
__REAL_COMMON__
namespace Common {
void* ReserveMemoryPages(std::size_t size) noexcept { return std::calloc(1, size); }
void CommitMemoryPages(void*, std::size_t) noexcept {}
void ReleaseMemoryPages(void* base, std::size_t) noexcept { std::free(base); }
struct ElfInfo {
    std::string serial = "CUSA08809";
    static ElfInfo& Instance() { static ElfInfo value; return value; }
    const std::string& GameSerial() const { return serial; }
};
}
namespace vk { enum class Format : u32 { eUndefined, RgbaUnorm, RgbaSrgb, R32Uint, Depth }; }
namespace AmdGpu { enum class ImageType : u64 { Color2D, Color3D, ColorCube }; }
struct CheckedMutex {
    bool held = false;
    void lock() { assert(!held); held = true; }
    void unlock() { assert(held); held = false; }
};
namespace VideoCore {
__REAL_IMAGE_FLAGS__
struct ImageInfo {
    VAddr guest_address = 0;
    u32 guest_size = 4096;
    Extent3D size{32, 32, 1};
    vk::Format pixel_format = vk::Format::RgbaUnorm;
    AmdGpu::ImageType type = AmdGpu::ImageType::Color2D;
    SubresourceExtent resources{4, 8};
    struct { bool is_tiled = false; } props;
};
struct ImageViewInfo { SubresourceRange range{}; };
struct ImageView { u64 owner_uid = 0; };
struct Image {
    inline static u64 next_uid = 1;
    ImageInfo info;
    ImageFlagBits flags = ImageFlagBits::CpuDirty;
    u64 image_uid = next_uid++;
    size_t lru_id = 0;
    u64 tick_accessed_last = 0;
    struct { bool needs_rebind = false; } binding;
    ImageView view{image_uid};
    unsigned view_calls = 0, refresh_calls = 0, uploads = 0, tracks = 0;
    Image(int, int, int, const ImageInfo& value) : info(value) {}
    ImageView& FindView(const ImageViewInfo&) { ++view_calls; return view; }
    __REAL_OVERLAPS__
};
bool IsVulkanFormatCompatible(vk::Format a, vk::Format b) {
    return a == b || ((a == vk::Format::RgbaUnorm || a == vk::Format::RgbaSrgb) &&
                     (b == vk::Format::RgbaUnorm || b == vk::Format::RgbaSrgb));
}
struct CheckedLru : Common::LeastRecentlyUsedCache<ImageId, u64> {
    using Base = Common::LeastRecentlyUsedCache<ImageId, u64>;
    CheckedMutex& mutex;
    unsigned touches = 0;
    explicit CheckedLru(CheckedMutex& value) : mutex(value) {}
    size_t Insert(ImageId id, u64 tick) { assert(mutex.held); return Base::Insert(id, tick); }
    void Free(size_t id) { assert(mutex.held); Base::Free(id); }
    void Touch(size_t id, u64 tick) { assert(mutex.held); ++touches; Base::Touch(id, tick); }
};
struct CheckedPages {
    CheckedMutex& mutex;
    std::map<u64, std::vector<ImageId>> data;
    unsigned searches = 0;
    explicit CheckedPages(CheckedMutex& value) : mutex(value) {}
    std::vector<ImageId>* find(u64 page) {
        assert(mutex.held); ++searches;
        auto it = data.find(page); return it == data.end() ? nullptr : &it->second;
    }
    std::vector<ImageId>& operator[](u64 page) { assert(mutex.held); return data[page]; }
};
struct TextureCache {
    __REAL_BINDING_TYPE__;
    struct ImageDesc { ImageInfo info; ImageViewInfo view_info; BindingType type = BindingType::Texture; };
    using ImageIds = std::vector<ImageId>;
    __REAL_TRAITS__;
    __REAL_MEMBERS__
    CheckedMutex mutex;
    CheckedPages page_table{mutex};
    CheckedLru lru_cache{mutex};
    Common::SlotVector<Image> slot_images{128};
    std::atomic<u64> target_registry_epoch{1};
    u64 total_used_memory = 0, gc_tick = 1;
    int instance = 0, runtime = 0, slot_image_views = 0;
    struct Scheduler { u64 tick = 1; u64 CurrentTick() const { return tick; } } scheduler;
    bool readback_linear_images = true;
    std::mutex download_images_mutex;
    std::unordered_set<ImageId> download_images;
    ImageId overlap_result{};
    int overlap_level = -1, overlap_layer = -1;
    unsigned overlaps = 0;
    std::tuple<ImageId, int, int> ResolveOverlap(const ImageInfo&, BindingType,
                                               ImageId, ImageId) {
        assert(mutex.held); ++overlaps;
        return {overlap_result, overlap_level, overlap_layer};
    }
    void RegisterImage(ImageId);
    void UnregisterImage(ImageId);
    void TouchImage(const Image&);
    ImageId FindImage(ImageDesc&, bool = false);
    ImageView& FindTexture(ImageId, const ImageDesc&);
    void TrackImage(ImageId id) { assert(mutex.held); ++slot_images[id].tracks; }
    void RefreshImage(Image& image) {
        assert(mutex.held); ++image.refresh_calls;
        if (True(image.flags & ImageFlagBits::Dirty)) {
            ++image.uploads; image.flags &= ~ImageFlagBits::Dirty;
        }
    }
    __REAL_UPDATE_IMAGE__
    __REAL_FOR_EACH_REGION__
    __REAL_FOR_EACH_PAGE__
    void FreeImage(ImageId id) { UnregisterImage(id); slot_images.Erase(id); }
    ImageId Add(const ImageInfo& info) {
        std::scoped_lock lock{mutex};
        auto id = slot_images.Insert(instance, runtime, slot_image_views, info);
        RegisterImage(id); return id;
    }
    void Retire(ImageId id, bool erase = false) {
        std::scoped_lock lock{mutex};
        UnregisterImage(id); if (erase) slot_images.Erase(id);
    }
    ImageId PeekMemo(const ImageInfo& info, bool exact = false) {
        std::scoped_lock lock{mutex}; return MemoLookup(info, exact);
    }
    std::vector<ImageId> OlderThan(u64 tick) {
        std::vector<ImageId> result;
        lru_cache.ForEachItemBelow(tick, [&](ImageId id) { result.push_back(id); });
        return result;
    }
};
__REAL_METHODS__
} // namespace VideoCore
using namespace VideoCore;
'''


TESTS = r'''
static TextureCache::ImageDesc Desc(VAddr address = 0x200000) {
    TextureCache::ImageDesc desc; desc.info.guest_address = address; return desc;
}
static ImageId Warm(TextureCache& cache, TextureCache::ImageDesc desc) {
    const auto first = cache.FindImage(desc);
    assert(cache.FindImage(desc) == first);
    assert(cache.PeekMemo(desc.info) == first);
    return first;
}
static void TestColdWarmEffects() {
    TextureCache cache;
    auto desc = Desc();
    auto id = Warm(cache, desc);
    const auto searches = cache.page_table.searches;
    cache.scheduler.tick = 41; cache.gc_tick = 9;
    desc.view_info.range.base = {2, 3};
    const auto touches = cache.lru_cache.touches;
    for (auto binding : {TextureCache::BindingType::Texture, TextureCache::BindingType::Storage,
                         TextureCache::BindingType::RenderTarget, TextureCache::BindingType::DepthTarget,
                         TextureCache::BindingType::VideoOut}) {
        desc.type = binding;
        assert(cache.FindImage(desc) == id);
        assert((desc.view_info.range.base == SubresourceBase{2, 3}));
    }
    assert(cache.page_table.searches == searches);
    assert(cache.slot_images[id].tick_accessed_last == 41);
    assert(cache.lru_cache.touches == touches + 5);
    assert(cache.OlderThan(8).empty());
    // CPU invalidation does not change identity. The caller must still upload
    // through the real FindTexture -> UpdateImage path after a memo hit.
    auto& image = cache.slot_images[id];
    image.flags |= ImageFlagBits::CpuDirty;
    desc.type = TextureCache::BindingType::Storage;
    assert(cache.FindImage(desc) == id);
    auto& view = cache.FindTexture(id, desc);
    assert(view.owner_uid == image.image_uid && image.view_calls == 1);
    assert(image.uploads == 1 && image.refresh_calls == 1 && image.tracks == 1);
    assert(False(image.flags & ImageFlagBits::Dirty));
    assert(True(image.flags & ImageFlagBits::GpuModified));
    assert(cache.download_images.contains(id));
}
static void TestRegistryGeneration() {
    TextureCache cache; auto desc = Desc(); auto first = Warm(cache, desc);
    const auto generation = cache.MemoGeneration(desc.info.guest_address);
    const auto global = cache.target_registry_epoch.load();
    auto other = Desc(0x600000);
    while (TextureCache::FindMemoAddressSlot(other.info.guest_address) ==
           TextureCache::FindMemoAddressSlot(desc.info.guest_address)) other.info.guest_address += 0x1000;
    cache.Add(other.info);
    assert(cache.target_registry_epoch.load() > global);
    assert(cache.MemoGeneration(desc.info.guest_address) == generation);
    const auto searches = cache.page_table.searches;
    assert(cache.FindImage(desc) == first && cache.page_table.searches == searches);
    // The last perfect match wins the page-vector scan. Inserting another at
    // the same base must invalidate the older memo before its next lookup.
    const auto last = cache.Add(desc.info);
    assert(last != first && cache.MemoGeneration(desc.info.guest_address) != generation);
    assert(cache.FindImage(desc) == last && cache.page_table.searches > searches);
    const auto after_insert = cache.MemoGeneration(desc.info.guest_address);
    cache.Retire(last); // allocation deliberately survives deferred retirement
    assert(cache.slot_images.IsAllocated(last));
    assert(cache.MemoGeneration(desc.info.guest_address) != after_insert);
    assert(cache.FindImage(desc) == first);
    const auto unrelated_generation = cache.MemoGeneration(other.info.guest_address);
    cache.Retire(first);
    assert(cache.MemoGeneration(other.info.guest_address) == unrelated_generation);
    const auto new_id = cache.FindImage(desc);
    assert(new_id != first && new_id != last);
}
static void TestLifetimeDefenses() {
    auto desc = Desc();
    {
        TextureCache cache; const auto id = Warm(cache, desc);
        const auto saved = cache.MemoSlot(desc.info, false);
        cache.Retire(id);
        // Deliberately present the old generation to exercise the independent
        // Registered check before the deferred slot destructor runs.
        cache.find_memo_address_generations[TextureCache::FindMemoAddressSlot(desc.info.guest_address)] = saved.generation;
        assert(!cache.PeekMemo(desc.info));
    }
    {
        TextureCache cache; const auto id = Warm(cache, desc);
        const auto saved = cache.MemoSlot(desc.info, false);
        cache.Retire(id, true);
        cache.find_memo_address_generations[TextureCache::FindMemoAddressSlot(desc.info.guest_address)] = saved.generation;
        assert(!cache.PeekMemo(desc.info)); // no read from the freed SlotVector element
        const auto reused = cache.Add(desc.info);
        assert(reused == id && cache.slot_images[reused].image_uid != saved.image_uid);
        cache.find_memo_address_generations[TextureCache::FindMemoAddressSlot(desc.info.guest_address)] = saved.generation;
        assert(!cache.PeekMemo(desc.info)); // identical info, different allocation identity
    }
    {
        TextureCache cache; const auto id = Warm(cache, desc);
        cache.slot_images[id].binding.needs_rebind = true;
        assert(!cache.PeekMemo(desc.info));
        const auto searches = cache.page_table.searches;
        assert(cache.FindImage(desc) == id && cache.page_table.searches > searches);
        assert(!cache.PeekMemo(desc.info));
        cache.slot_images[id].binding.needs_rebind = false;
        assert(cache.FindImage(desc) == id);
    }
}
static void TestKeysAndCapacity() {
    TextureCache cache; auto desc = Desc(); const auto id = Warm(cache, desc);
    const auto saved = cache.MemoSlot(desc.info, false);
    auto reject = [&](ImageInfo changed, bool exact = false) {
        // Force a direct-mapped collision: key checks, not a lucky hash, must
        // prevent reuse for a different descriptor.
        cache.MemoSlot(changed, exact) = saved;
        assert(!cache.PeekMemo(changed, exact));
    };
    auto changed = desc.info; ++changed.guest_address; reject(changed);
    changed = desc.info; ++changed.guest_size; reject(changed);
    changed = desc.info; ++changed.size.width; reject(changed);
    changed = desc.info; ++changed.size.height; reject(changed);
    changed = desc.info; ++changed.size.depth; reject(changed);
    changed = desc.info; changed.type = AmdGpu::ImageType::Color3D; reject(changed);
    changed = desc.info; changed.pixel_format = vk::Format::RgbaSrgb; reject(changed);
    reject(desc.info, true);
    cache.MemoSlot(desc.info, false) = saved;
    changed = desc.info; changed.resources.levels += 1;
    assert(!cache.PeekMemo(changed));
    // Mutable backing metadata is validated even when address generation and
    // UID are unchanged; the memo cannot invent an exact match.
    cache.slot_images[id].info.size.width += 1;
    assert(!cache.PeekMemo(desc.info));
    cache.slot_images[id].info = desc.info;
    assert(cache.PeekMemo(desc.info) == id);
    TextureCache compatible; auto srgb = Desc(0x900000);
    const auto original = compatible.Add(srgb.info);
    srgb.info.pixel_format = vk::Format::RgbaSrgb;
    assert(compatible.FindImage(srgb, false) == original);
    assert(compatible.FindImage(srgb, false) == original);
    assert(!compatible.PeekMemo(srgb.info, true));
    TextureCache scalar; auto one = Desc(0xa00000); one.info.size = {1, 1, 1};
    const auto one_id = scalar.Add(one.info); one.info.type = AmdGpu::ImageType::ColorCube;
    assert(scalar.FindImage(one) == one_id && scalar.FindImage(one) == one_id);
}
static void TestAliasAndCollision() {
    TextureCache cache; auto large = Desc(0x200000); large.info.guest_size = 32768;
    large.info.size = {128, 128, 1}; large.info.resources = {8, 8};
    const auto id = cache.Add(large.info);
    cache.overlap_result = id; cache.overlap_level = 2; cache.overlap_layer = 3;
    auto alias = Desc(0x201000);
    auto first = alias; auto second = alias;
    assert(cache.FindImage(first) == id);
    const auto visits = cache.page_table.searches;
    assert(cache.FindImage(second) == id && cache.page_table.searches > visits);
    assert((first.view_info.range.base == SubresourceBase{2, 3}));
    assert(second.view_info.range.base == first.view_info.range.base);
    assert(cache.overlaps == 2 && !cache.PeekMemo(alias.info));
    assert(!cache.MemoSlot(alias.info, false).image_id);

    TextureCache collision; auto desc = Desc(); const auto original = Warm(collision, desc);
    auto other = Desc(desc.info.guest_address + 0x1000);
    // A generation hash collision is conservative invalidation, never a new
    // image winner. Exercise it without depending on a particular hash value.
    for (u32 i = 0; i < 1000000; ++i, other.info.guest_address += 0x1000) {
        if (TextureCache::FindMemoAddressSlot(other.info.guest_address) ==
            TextureCache::FindMemoAddressSlot(desc.info.guest_address)) break;
    }
    assert(TextureCache::FindMemoAddressSlot(other.info.guest_address) ==
           TextureCache::FindMemoAddressSlot(desc.info.guest_address));
    collision.Add(other.info);
    assert(!collision.PeekMemo(desc.info));
    assert(collision.FindImage(desc) == original);
}
int main(int argc, char** argv) {
    if (argc > 1) Common::ElfInfo::Instance().serial = argv[1];
    const auto& serial = Common::ElfInfo::Instance().GameSerial();
    const char* config = std::getenv("BACHATA_SOTC_FIND_MEMO");
    const bool expected = (serial == "CUSA08809" || serial == "CUSA08034") &&
                          (!config || config[0] != '0');
    TextureCache gate; assert(gate.FindMemoEnabled() == expected);
    if (!expected) {
        auto desc = Desc(); const auto id = gate.Add(desc.info);
        for (unsigned i = 0; i < 4; ++i) {
            const auto visits = gate.page_table.searches;
            assert(gate.FindImage(desc) == id && gate.page_table.searches > visits);
            assert(!gate.MemoSlot(desc.info, false).image_id);
        }
        std::cout << "SOTC_TEXTURE_FIND_MEMO_DISABLED_PASS " << serial << '\n';
        return 0;
    }
    TestColdWarmEffects(); TestRegistryGeneration(); TestLifetimeDefenses();
    TestKeysAndCapacity(); TestAliasAndCollision();
    std::cout << "SOTC_TEXTURE_FIND_MEMO_REAL_METHODS_PASS " << serial << '\n';
}
'''


def program(root):
    source = (root / "video_core/texture_cache/texture_cache.cpp").read_text()
    header = (root / "video_core/texture_cache/texture_cache.h").read_text()
    image = (root / "video_core/texture_cache/image.h").read_text()
    common = "\n".join(strip_includes((root / name).read_text()) for name in (
        "common/types.h", "common/enum.h", "common/alignment.h", "common/slot_vector.h",
        "common/lru_cache.h", "video_core/texture_cache/types.h"))
    members = header[header.index("    // BACHATA_SOTC_TEXTURE_FIND_MEMO_V1"):
                     header.index("    Common::SlotVector<Image> slot_images;")]
    flags = image[image.index("enum ImageFlagBits :"):
                  image.index("struct UniqueImage")]
    methods = "\n".join(function(source, signature) for signature in (
        "static bool IsSotcMemoPerfectMatch(", "bool TextureCache::FindMemoEnabled(",
        "TextureCache::FindMemo& TextureCache::MemoSlot(", "u64 TextureCache::MemoGeneration(",
        "ImageId TextureCache::MemoLookup(", "ImageId TextureCache::FindImage(",
        "void TextureCache::RegisterImage(", "void TextureCache::UnregisterImage(",
        "void TextureCache::TouchImage(", "ImageView& TextureCache::FindTexture("))
    replacements = {
        "__REAL_COMMON__": common,
        "__REAL_IMAGE_FLAGS__": flags,
        "__REAL_OVERLAPS__": function(image, "    bool Overlaps("),
        "__REAL_BINDING_TYPE__": function(header, "    enum class BindingType :"),
        "__REAL_TRAITS__": function(header, "    struct Traits {"),
        "__REAL_MEMBERS__": members,
        "__REAL_UPDATE_IMAGE__": function(header, "    void UpdateImage("),
        "__REAL_FOR_EACH_REGION__": "template <typename Func>\n" + function(header, "    void ForEachImageInRegion("),
        "__REAL_FOR_EACH_PAGE__": "template <typename Func>\n" + function(header, "    static void ForEachPage("),
        "__REAL_METHODS__": methods,
    }
    code = PREAMBLE
    for token, value in replacements.items():
        assert code.count(token) == 1, token
        code = code.replace(token, value)
    return code + TESTS


def run(root):
    code = program(root)
    with tempfile.TemporaryDirectory(prefix="bachata-sotc-find-memo-") as directory:
        directory = Path(directory)

        def build(name, value):
            source = directory / (name + ".cpp")
            binary = directory / name
            source.write_text(value)
            subprocess.run(["c++", "-std=c++23", "-O1", "-Wall", "-Wextra", "-Werror", "-fmax-errors=8",
                            "-Wno-parentheses", "-Wno-unused-parameter",
                            "-fsanitize=undefined", "-fno-sanitize-recover=all",
                            str(source), "-o", str(binary)], check=True)
            return binary

        binary = build("sotc_find_memo", code)
        environment = dict(os.environ)
        environment.pop("BACHATA_SOTC_FIND_MEMO", None)
        for serial in ("CUSA08809", "CUSA08034", "CUSA00785", "CUSA00000"):
            subprocess.run([str(binary), serial], check=True, env=environment)
        environment["BACHATA_SOTC_FIND_MEMO"] = "0"
        subprocess.run([str(binary)], check=True, env=environment)
        environment.pop("BACHATA_SOTC_FIND_MEMO")

        # Compile genuine regressions of this implementation. Each one must be
        # rejected by the behavioral suite, rather than by a text-token check.
        controls = {
            "lost_register_generation": (
                "    ++find_memo_address_generations[FindMemoAddressSlot(image.info.guest_address)];\n",
                "", 1),
            "lost_uid": ("image.image_uid != memo.image_uid ||", "false ||", 1),
            "lost_registered": ("False(image.flags & ImageFlagBits::Registered) || image.binding.needs_rebind ||",
                                "image.binding.needs_rebind ||", 1),
            "lost_allocation_check": ("!slot_images.IsAllocated(memo.image_id)", "false", 1),
            "lost_rebind": (" || image.binding.needs_rebind ||", " ||", 1),
            "lost_capacity": ("        image.info.resources < info.resources ||\n", "", 1),
            "lost_tick": ("            image.tick_accessed_last = scheduler.CurrentTick();\n", "", 1),
            "lost_lru": ("            TouchImage(image);\n", "", 1),
        }
        for name, (old, new, count) in controls.items():
            assert code.count(old) >= count, name
            mutant = build(name, code.replace(old, new, count))
            result = subprocess.run([str(mutant)], env=environment, capture_output=True, text=True)
            assert result.returncode != 0, "negative control unexpectedly passed: " + name
            assert "Assertion" in result.stderr or "runtime error:" in result.stderr, result.stderr
        print(f"SOTC_TEXTURE_FIND_MEMO_NEGATIVE_CONTROLS_PASS {len(controls)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    arguments = parser.parse_args()
    root = arguments.source.resolve()
    if (root / "src").is_dir():
        root = root / "src"
    run(root)
