#!/usr/bin/env python3
"""Port demonstrable release-era CMask/FMask/HTile owner tracking into shadPS4 0.18.1.

The pinned 0.18.1 source calls surface_metas.emplace(addr, type-only) then
unconditionally erases the same addr on DeleteImage. When render target B
reuses A's CMask address, emplace fails to transfer ownership; A's later
DeleteImage destroys B's metadata. That is a semantic bug, not an absent
export symbol or game-specific guess.

Modern shadPS4 (b7c0f18b) validates the owning ImageId AND unique image_uid
so slot reuse cannot resurrect stale CMask state. The functions below port
that concrete state contract while retaining the pinned 0.18.1 data types
(tsl::robin_map, Common::SlotVector, ImageFlagBits).
"""
from pathlib import Path

MARKER = "BACHATA_RELEASE026_META_OWNER_UID"

def once(s: str, before: str, after: str, label: str) -> str:
    count = s.count(before)
    if count != 1:
        raise RuntimeError(f"CMask ownership {label}: {count} pinned anchors")
    return s.replace(before, after, 1)

def patch_h(s: str) -> str:
    s=once(s,
        """    enum class MetaType {
        CMask,
        FMask,
        HTile,
    };

    /// Returns meta type if the specified address is a metadata surface.""",
        """    enum class MetaType {
        CMask,
        FMask,
        HTile,
    };

    // Read the active owner of an address-reused color mask. Avoid returning
    // a stale slot ID when an image has been destroyed and the slot recycled.
    [[nodiscard]] std::optional<ImageId> ResolveCMaskOwner(VAddr address) const;

    // A metadata surface must reference a live, registered image. This check
    // is shared by both renderpass clear/write paths and the CMask lookup.
    [[nodiscard]] bool HasLiveMeta(VAddr address) const {
        const auto it = surface_metas.find(address);
        if (it == surface_metas.end()) return false;
        const auto& meta = it.value();
        if (!meta.owner_id || !slot_images.IsAllocated(meta.owner_id)) return false;
        const auto& owner = slot_images[meta.owner_id];
        return owner.image_uid == meta.owner_uid &&
               True(owner.flags & ImageFlagBits::Registered);
    }

    /// Returns meta type if the specified address is a metadata surface.""",
        "live owner validation API")
    s=once(s,
        """    std::optional<MetaType> IsMeta(VAddr address) const {
        auto it = surface_metas.find(address);
        if (it != surface_metas.end()) {
            return it->second.type;
        }
        return std::nullopt;
    }""",
        """    std::optional<MetaType> IsMeta(VAddr address) const {
        if (!HasLiveMeta(address)) return std::nullopt;
        return surface_metas.find(address).value().type;
    }""",
        "IsMeta uses owning image")
    s=once(s,
        """        if (it != surface_metas.end()) {
            return it.value().clear_mask & (1u << slice);
        }
        return false;
    }""",
        """        if (slice < 32 && it != surface_metas.end() && HasLiveMeta(address)) {
            return (it.value().clear_mask & (1u << slice)) != 0;
        }
        return false;
    }""",
        "IsMetaCleared validates owner, bounds slice")
    s=once(s,
        """        if (it != surface_metas.end()) {
            it.value().clear_mask = u32(-1);
            return true;
        }
        return false;
    }""",
        """        if (it != surface_metas.end() && HasLiveMeta(address)) {
            it.value().clear_mask = -1;
            return true;
        }
        return false;
    }""",
        "ClearMeta validates owner")
    s=once(s,
        """        if (it != surface_metas.end()) {
            if (is_clear) {
                it.value().clear_mask |= 1u << slice;
            } else {
                it.value().clear_mask &= ~(1u << slice);
            }
            return true;
        }
        return false;
    }""",
        """        if (slice < 32 && it != surface_metas.end() && HasLiveMeta(address)) {
            if (is_clear) {
                it.value().clear_mask |= 1u << slice;
            } else {
                it.value().clear_mask &= ~(1u << slice);
            }
            return true;
        }
        return false;
    }""",
        "TouchMeta validates owner")
    s=once(s,
        """    void MarkAsMaybeDirty(ImageId image_id, Image& image);

    /// Removes the image and any image views/surface metas that reference it.""",
        """    void MarkAsMaybeDirty(ImageId image_id, Image& image);

    // Metadata ownership follows image UID, not merely an address or slot.
    void RegisterMeta(VAddr address, MetaDataInfo info);
    void UnregisterMeta(VAddr address, u64 owner_uid);

    /// Removes the image and any image views/surface metas that reference it.""",
        "register/unregister declaration")
    # MetaDataInfo is currently defined at end of class. Forward-declare
    # before RegisterMeta; the method parameter may have an incomplete type.
    s=once(s,
        """    void MarkAsMaybeDirty(ImageId image_id, Image& image);

    // Metadata ownership""",
        """    void MarkAsMaybeDirty(ImageId image_id, Image& image);

    struct MetaDataInfo;

    // Metadata ownership""",
        "MetaDataInfo forward declaration")
    s=once(s,
        """    struct MetaDataInfo {
        MetaType type;
        s32 clear_mask = -1;
    };""",
        """    struct MetaDataInfo {
        MetaType type;
        ImageId owner_id{};
        u64 owner_uid{};
        u32 num_samples = 1;
        s32 clear_mask = -1;
    };""",
        "metadata ownership fields")
    return s

def patch_cpp(s: str) -> str:
    s=once(s,
        """ImageView& TextureCache::FindRenderTarget(ImageId image_id, const ImageDesc& desc) {""",
        """// BACHATA_RELEASE026_META_OWNER_UID: a live image uniquely owns its
// compression/clear-state metadata; metadata-address reuse transfers it.
std::optional<ImageId> TextureCache::ResolveCMaskOwner(VAddr address) const {
    const auto it = surface_metas.find(address);
    if (it == surface_metas.end() || it.value().type != MetaType::CMask ||
        !HasLiveMeta(address)) {
        return std::nullopt;
    }
    return it.value().owner_id;
}

void TextureCache::RegisterMeta(VAddr address, MetaDataInfo info) {
    if (!address) return;
    const auto it = surface_metas.find(address);
    if (it == surface_metas.end()) {
        surface_metas.emplace(address, info);
        return;
    }
    auto& entry = it.value();
    if (entry.type != info.type || entry.owner_uid != info.owner_uid) {
        // Different image: old clear mask is invalid for the new owner.
        entry = info;
        return;
    }
    // Same image rebound: retain its clear state while refreshing samples.
    entry.owner_id = info.owner_id;
    entry.num_samples = info.num_samples;
}

void TextureCache::UnregisterMeta(VAddr address, u64 owner_uid) {
    if (!address) return;
    const auto it = surface_metas.find(address);
    if (it != surface_metas.end() && it.value().owner_uid == owner_uid) {
        surface_metas.erase(address);
    }
}

ImageView& TextureCache::FindRenderTarget(ImageId image_id, const ImageDesc& desc) {""",
        "owner-aware metadata primitives")
    s=once(s,
        """    // Register meta data for this color buffer
    if (desc.info.meta_info.cmask_addr) {
        surface_metas.emplace(desc.info.meta_info.cmask_addr,
                              MetaDataInfo{.type = MetaType::CMask});
        image.info.meta_info.cmask_addr = desc.info.meta_info.cmask_addr;
    }

    if (desc.info.meta_info.fmask_addr) {
        surface_metas.emplace(desc.info.meta_info.fmask_addr,
                              MetaDataInfo{.type = MetaType::FMask});
        image.info.meta_info.fmask_addr = desc.info.meta_info.fmask_addr;
    }
""",
        """    // Rebinding can transfer a CMask address from another image, or clear
    // the old association; neither may erase a different live owner's state.
    const VAddr cmask_addr = desc.info.meta_info.cmask_addr;
    if (image.info.meta_info.cmask_addr != cmask_addr) {
        UnregisterMeta(image.info.meta_info.cmask_addr, image.image_uid);
        image.info.meta_info.cmask_addr = cmask_addr;
    }
    if (cmask_addr) {
        RegisterMeta(cmask_addr, MetaDataInfo{
            .type = MetaType::CMask,
            .owner_id = image_id,
            .owner_uid = image.image_uid,
            .num_samples = image.info.num_samples,
        });
    }

    const VAddr fmask_addr = desc.info.meta_info.fmask_addr;
    if (image.info.meta_info.fmask_addr != fmask_addr) {
        UnregisterMeta(image.info.meta_info.fmask_addr, image.image_uid);
        image.info.meta_info.fmask_addr = fmask_addr;
    }
    if (fmask_addr) {
        RegisterMeta(fmask_addr, MetaDataInfo{
            .type = MetaType::FMask,
            .owner_id = image_id,
            .owner_uid = image.image_uid,
            .num_samples = image.info.num_samples,
        });
    }
""",
        "color-mask address reuse")
    s=once(s,
        """    // Register meta data for this depth buffer
    if (desc.info.meta_info.htile_addr) {
        surface_metas.emplace(desc.info.meta_info.htile_addr,
                              MetaDataInfo{.type = MetaType::HTile,
                                           .clear_mask = image.info.meta_info.htile_clear_mask});
        image.info.meta_info.htile_addr = desc.info.meta_info.htile_addr;
    }
""",
        """    // HTile ownership obeys the same image UID / rebind contract.
    const VAddr htile_addr = desc.info.meta_info.htile_addr;
    if (image.info.meta_info.htile_addr != htile_addr) {
        UnregisterMeta(image.info.meta_info.htile_addr, image.image_uid);
        image.info.meta_info.htile_addr = htile_addr;
    }
    if (htile_addr) {
        RegisterMeta(htile_addr, MetaDataInfo{
            .type = MetaType::HTile,
            .owner_id = image_id,
            .owner_uid = image.image_uid,
            .num_samples = image.info.num_samples,
            .clear_mask = image.info.meta_info.htile_clear_mask,
        });
    }
""",
        "HTile owner transition")
    s=once(s,
        """    if (meta_info.cmask_addr) {
        surface_metas.erase(meta_info.cmask_addr);
    }
    if (meta_info.fmask_addr) {
        surface_metas.erase(meta_info.fmask_addr);
    }
    if (meta_info.htile_addr) {
        surface_metas.erase(meta_info.htile_addr);
    }
""",
        """    if (meta_info.cmask_addr) {
        UnregisterMeta(meta_info.cmask_addr, image.image_uid);
    }
    if (meta_info.fmask_addr) {
        UnregisterMeta(meta_info.fmask_addr, image.image_uid);
    }
    if (meta_info.htile_addr) {
        UnregisterMeta(meta_info.htile_addr, image.image_uid);
    }
""",
        "prevent deleting another image's metadata")
    return s


def patch_buffer_cache(c: str) -> str:
    c=once(c,
        """    if (auto type = texture_cache.IsMeta(device_addr)) {
        if (*type == TextureCache::MetaType::HTile) {
            static constexpr u32 ZmaskUncompressed = 0xf;
            runtime.FillBuffer(arena, arena->Offset(device_addr), size, ZmaskUncompressed);
            return true;
        } else {
            LOG_WARNING(Render_Vulkan, "Unhandled metadata type {}", magic_enum::enum_name(*type));
        }
    }
""",
        """    // BACHATA_RELEASE026_CMASK_EXPANDED: a texturing/readback alias of a
    // compressed color-mask surface must produce the expanded CMask bit
    // pattern for this image's MSAA sample count, not treat it as a random
    // unmatched buffer or suppress its contents as 'Unhandled metadata'.
    if (const auto owner_id = texture_cache.ResolveCMaskOwner(device_addr)) {
        const Image& owner = texture_cache.GetImage(*owner_id);
        u32 expanded{};
        switch (owner.info.num_samples) {
        case 1: expanded = 0xFFFFFFFFu; break;
        case 2: expanded = 0xDDDDDDDDu; break;
        case 4: expanded = 0xEEEEEEEEu; break;
        case 8: expanded = 0xFFFFFFFFu; break;
        default:
            LOG_WARNING(Render_Vulkan, "Unsupported CMask sample count: addr={:#x}, samples={}",
                        device_addr, owner.info.num_samples);
            return false;
        }
        runtime.FillBuffer(arena, arena->Offset(device_addr), size, expanded);
        return true;
    }
    if (auto type = texture_cache.IsMeta(device_addr)) {
        if (*type == TextureCache::MetaType::HTile) {
            static constexpr u32 ZmaskUncompressed = 0xf;
            runtime.FillBuffer(arena, arena->Offset(device_addr), size, ZmaskUncompressed);
            return true;
        } else {
            LOG_WARNING(Render_Vulkan, "Unhandled metadata type {}",
                        magic_enum::enum_name(*type));
        }
    }
""",
        "CMask aliased texel expanded values")
    return c

def audit(header: str, cpp: str) -> None:
    req = {
        "header": [
            "ResolveCMaskOwner(VAddr address) const", "HasLiveMeta(VAddr address) const",
            "owner_id{}", "owner_uid{}", "num_samples = 1",
            "struct MetaDataInfo;", "void RegisterMeta(VAddr address",
        ],
        "cpp": [
            MARKER, "entry.owner_uid != info.owner_uid",
            "UnregisterMeta(meta_info.cmask_addr, image.image_uid)",
            "UnregisterMeta(meta_info.fmask_addr, image.image_uid)",
            "UnregisterMeta(meta_info.htile_addr, image.image_uid)",
            "RegisterMeta(cmask_addr, MetaDataInfo",
            "RegisterMeta(fmask_addr, MetaDataInfo",
            "RegisterMeta(htile_addr, MetaDataInfo",
        ]
    }
    missing = [k for k in req["header"] if k not in header] + [
        k for k in req["cpp"] if k not in cpp]
    obsolete = [
        old for old in (
            "surface_metas.emplace(desc.info.meta_info.cmask_addr",
            "surface_metas.erase(meta_info.cmask_addr);",
            "surface_metas.erase(meta_info.fmask_addr);",
            "surface_metas.erase(meta_info.htile_addr);",
        ) if old in cpp
    ]
    if missing or obsolete:
        raise RuntimeError(f"Owner parity: missing={missing} obsolete={obsolete}")

def apply(root: Path) -> dict:
    h = root / "src/video_core/texture_cache/texture_cache.h"
    c = root / "src/video_core/texture_cache/texture_cache.cpp"
    old_h, old_c = h.read_text(), c.read_text()
    if MARKER in old_c:
        audit(old_h, old_c)
        return {"status":"already-applied"}
    new_h, new_c = patch_h(old_h), patch_cpp(old_c)
    audit(new_h, new_c)
    bc = root / "src/video_core/buffer_cache/buffer_cache.cpp"
    old_bc = bc.read_text()
    new_bc = patch_buffer_cache(old_bc)
    if "BACHATA_RELEASE026_CMASK_EXPANDED" not in new_bc:
        raise RuntimeError("Missing BufferCache CMask expanded values")
    # This update must accompany owner tracking in the same source transaction.
    h.write_text(new_h)
    c.write_text(new_c)
    bc.write_text(new_bc)
    return {"status":"applied","subsystem":"texture-cache",
            "ownership":"ImageId + image_uid",
            "meta":["CMask","FMask","HTile"],
            "stale-cache-state":"invalidated on owner change",
            "unregister":"only current owner may remove",
            "cmask_alias":"real expanded patterns for 1/2/4/8 MSAA samples"}

if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(apply(a.source),sort_keys=True))
