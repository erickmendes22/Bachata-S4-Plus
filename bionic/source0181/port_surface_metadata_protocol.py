"""Restore the effective Order donor's active metadata write/clear protocol.

Retain Bachata's ImageId/UID ownership and arena-backed buffers. Synthetic
HTILE reads are not enabled (the donor's ORDER1886_HTILE default is off).
The batch clear additionally commits state only after every output validates.
SotC already has its donor's single-output gate and must not use this overlay.
"""
from pathlib import Path
import shutil


def apply(root):
    root = Path(root)

    def edit(name, old, new):
        path = root / name
        text = path.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"Order metadata source drift {name}: {old[:100]!r}")
        path.write_text(text.replace(old, new, 1))

    th = "src/video_core/texture_cache/texture_cache.h"
    tc = "src/video_core/texture_cache/texture_cache.cpp"
    rasterizer = "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    buffer_cache = "src/video_core/buffer_cache/buffer_cache.cpp"
    shutil.copyfile(Path(__file__).with_name("surface_metadata.h"),
                    root / "src/video_core/texture_cache/surface_metadata.h")
    edit(th, '#include "video_core/texture_cache/sampler.h"',
         '#include "video_core/texture_cache/sampler.h"\n'
         '#include "video_core/texture_cache/surface_metadata.h"')
    edit(th, '''    enum class MetaType {
        CMask,
        FMask,
        HTile,
    };''', '''    using MetaType = SurfaceMetadata::Type;''')
    edit(th, '''        return owner.image_uid == meta.owner_uid &&
               True(owner.flags & ImageFlagBits::Registered);''',
         '''        return owner.image_uid == meta.owner_uid &&
               True(owner.flags & ImageFlagBits::Registered) &&
               surface_metadata.TypeAt(address).has_value();''')
    old = (root / th).read_text()
    start = old.index("    /// Returns true if a slice of the specified metadata surface has been cleared.")
    end = old.index("    /// Runs the garbage collector.", start)
    edit(th, old[start:end], '''    /// Returns true if a slice of the specified metadata surface has been cleared.
    bool IsMetaCleared(VAddr address, u32 slice) const {
        return HasLiveMeta(address) && surface_metadata.IsCleared(address, slice);
    }

    /// Commit a metadata-only dispatch after validating every live destination.
    bool ClearMetaBatch(std::span<const SurfaceMetadata::ClearRange> ranges) {
        for (const auto& range : ranges) {
            if (!HasLiveMeta(range.first)) return false;
        }
        return surface_metadata.ClearBatch(ranges);
    }

    void FillMeta(VAddr address, u64 size, u32 value) {
        surface_metadata.Fill(address, size, value);
    }

    void NoteMetaShaderWrite(VAddr address, u64 size) {
        surface_metadata.Write(address, size);
    }

    /// Updates only the addressed slice, retaining read-only depth state.
    bool TouchMeta(VAddr address, u32 slice, bool is_clear) {
        return HasLiveMeta(address) && surface_metadata.Touch(address, slice, is_clear);
    }

''')
    edit(th, '''        s32 clear_mask = -1;
    };
    tsl::robin_map<VAddr, MetaDataInfo> surface_metas;''',
         '''        s32 clear_mask = -1;
        u32 layers = 1;
        bool stencil = false;
    };
    // Keep live ImageId/UID ownership for CMask lookup independently of the
    // synchronized metadata state used by CPU writes and GPU dispatches.
    tsl::robin_map<VAddr, MetaDataInfo> surface_metas;
    SurfaceMetadata surface_metadata;''')
    edit(tc, '''void TextureCache::RegisterMeta(VAddr address, MetaDataInfo info) {
    if (!address) return;''', '''void TextureCache::RegisterMeta(VAddr address, MetaDataInfo info) {
    if (!address) return;
    surface_metadata.Register(address, info.owner_uid, info.type,
                              static_cast<u32>(info.clear_mask), info.layers, info.stencil);''')
    edit(tc, '''void TextureCache::UnregisterMeta(VAddr address, u64 owner_uid) {
    if (!address) return;''', '''void TextureCache::UnregisterMeta(VAddr address, u64 owner_uid) {
    if (!address) return;
    surface_metadata.Erase(address, owner_uid);''')
    edit(tc, '''            .clear_mask = image.info.meta_info.htile_clear_mask,
''', '''            .clear_mask = image.info.meta_info.htile_clear_mask,
            .layers = image.info.resources.layers,
            .stencil = static_cast<bool>(desc.info.props.has_stencil),
''')
    edit(tc, '''void TextureCache::InvalidateMemory(VAddr addr, size_t size) {
''', '''void TextureCache::InvalidateMemory(VAddr addr, size_t size) {
    surface_metadata.Write(addr, size);
''')
    edit(tc, '''void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {
''', '''void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {
    surface_metadata.Unmap(cpu_addr, size);
''')
    edit(tc, '''    if (desc.type == BindingType::Storage) {
        image.flags |= ImageFlagBits::GpuModified;''',
         '''    if (desc.type == BindingType::Storage) {
        surface_metadata.Write(image.info.guest_address, image.info.guest_size);
        image.flags |= ImageFlagBits::GpuModified;''')
    # Scope this insertion to ObtainBuffer's write block. Other overlays may
    # add MarkReadbacksDirty in the same block before or after this overlay.
    text = (root / buffer_cache).read_text()
    start = text.index("std::pair<const Buffer*, u64> BufferCache::ObtainBuffer(")
    end = text.index("std::pair<const Buffer*, u64> BufferCache::ObtainBufferForImage(", start)
    body = text[start:end]
    anchor = "    if (is_written) {\n"
    if body.count(anchor) != 1:
        raise RuntimeError("Order metadata ObtainBuffer write-block drift")
    edit(buffer_cache, body, body.replace(anchor, anchor +
         "        texture_cache.NoteMetaShaderWrite(device_addr, size);\n", 1))

    text = (root / rasterizer).read_text()
    start = text.index("bool Rasterizer::IsComputeMetaClear(")
    end = text.index("bool Rasterizer::IsComputeImageCopy(", start)
    edit(rasterizer, text[start:end], '''bool Rasterizer::IsComputeMetaClear(const Pipeline* pipeline) {
    if (!pipeline->IsCompute()) return false;
    const auto& info = pipeline->GetStage(Shader::SwStage::Compute);
    // Retain the donor's tiled-write heuristic; never drop a storage-image
    // output when replacing a metadata-only buffer dispatch.
    if (info.has_bitwise_xor) return false;
    for (const auto& desc : info.images) {
        if (desc.is_written) return false;
    }
    boost::container::small_vector<VideoCore::SurfaceMetadata::ClearRange, 8> outputs;
    for (const auto& desc : info.buffers) {
        if (desc.IsSpecial()) {
            if (desc.is_written) return false;
            continue;
        }
        const auto sharp = desc.GetSharp(info);
        const VAddr address = sharp.base_address;
        if (!desc.is_written) {
            // Metadata reads identify a copy/inspection shader, not a clear.
            if (texture_cache.IsMeta(address)) return false;
            continue;
        }
        const auto size = sharp.GetSize();
        if (memory->ClampRangeSize(address, size) != size) return false;
        outputs.emplace_back(address, size);
    }
    // No state changes on a partial match: every output must be live metadata
    // of a supported extent before the original dispatch may be skipped.
    if (!texture_cache.ClearMetaBatch({outputs.data(), outputs.size()})) return false;
    LOG_TRACE(Render_Vulkan, "Metadata update skipped");
    return true;
}

''')
    edit(rasterizer, '''        const bool is_stencil_clear = regs.depth_render_control.stencil_clear_enable;
        texture_cache.TouchMeta(htile_address, slice, false);''',
         '''        const bool is_stencil_clear = regs.depth_render_control.stencil_clear_enable;
        if (regs.depth_control.depth_enable && regs.depth_control.depth_write_enable) {
            for (u32 layer = 0; layer < image_view.info.range.extent.layers; ++layer) {
                texture_cache.TouchMeta(htile_address, slice + layer, false);
            }
        }''')
    edit(rasterizer, '''        texture_cache.ClearMeta(address);
        if (!buffer_cache.IsRegionGpuModified(address, num_bytes)) {''',
         '''        if (!buffer_cache.IsRegionGpuModified(address, num_bytes)) {''')
    edit(rasterizer, '''            std::fill(buffer, buffer + (num_bytes / sizeof(u32)), value);
            return;''',
         '''            std::fill(buffer, buffer + (num_bytes / sizeof(u32)), value);
            texture_cache.FillMeta(address, num_bytes, value);
            return;''')
    edit(rasterizer, '''    runtime.FillBuffer(buffer, offset, num_bytes, value);
''', '''    runtime.FillBuffer(buffer, offset, num_bytes, value);
    if (!is_gds) texture_cache.FillMeta(address, num_bytes, value);
''')
    edit(rasterizer, '''            std::memcpy(std::bit_cast<void*>(dst), std::bit_cast<void*>(src), num_bytes);
            return;''',
         '''            std::memcpy(std::bit_cast<void*>(dst), std::bit_cast<void*>(src), num_bytes);
            texture_cache.NoteMetaShaderWrite(dst, num_bytes);
            return;''')
    # Invalidate metadata before any deferred copy can unprotect a CPU write.
    edit(rasterizer, '''    texture_cache.ResolveImageReadbacks(addr,size,assume_locks);
''', '''    texture_cache.NoteMetaShaderWrite(addr, size);
    texture_cache.ResolveImageReadbacks(addr,size,assume_locks);
''')
    edit(rasterizer, '''void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
''', '''void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    texture_cache.NoteMetaShaderWrite(addr, size);
''')
    return {"target": "Order only; SotC retains donor single-output gate",
            "metadata": "donor CPU/GPU writes, storage images, copy/fill, unmap, depth layers",
            "computeClear": "validate all outputs before atomic metadata-state commit",
            "ownership": "existing ImageId/UID and arena registration preserved",
            "htileReadSubstitution": "disabled, matching donor default"}
