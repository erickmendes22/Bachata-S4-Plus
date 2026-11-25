"""SotC texture pool ownership fixes from the actual 0.2.0 GPU source.

Reference 732cb37d3470 + Android staging 0366868550. Preserve FEX,
guest mapping, existing metadata ownership and all DMA synchronization.
"""
from pathlib import Path

def apply(root: Path):
    def edit(rel, old, new):
        p = root / rel
        s = p.read_text()
        if s.count(old) != 1:
            raise RuntimeError("SotC texture coherence anchor drift: " + rel + ": " + old[:100])
        p.write_text(s.replace(old,new,1))
    tc="src/video_core/texture_cache/texture_cache.cpp"
    th="src/video_core/texture_cache/texture_cache.h"
    r="src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    edit(tc, """    RefreshImage(new_image);
    runtime.CopyImage(&src_image, &new_image);""",
    """    // SotC donor: a CPU-dirty source belongs to an earlier streaming-pool
    // occupant. Copying it after RefreshImage destroys newly uploaded bytes.
    const bool carry_gpu_data = src_image.SafeToDownload();
    RefreshImage(new_image);
    if (carry_gpu_data) {
        runtime.CopyImage(&src_image, &new_image);
    }""")
    edit(th,"void InvalidateMemoryFromGPU(VAddr address, size_t max_size);",
         "void InvalidateMemoryFromGPU(VAddr address, size_t max_size, bool any_overlap = false);")
    edit(tc, """void TextureCache::InvalidateMemoryFromGPU(VAddr address, size_t max_size) {
    std::scoped_lock lock{mutex};""",
    """void TextureCache::InvalidateMemoryFromGPU(VAddr address, size_t max_size, bool any_overlap) {
    std::scoped_lock lock{mutex};
    if (max_size == 0) return;
    if (any_overlap) {
        ForEachImageInRegion(address, max_size, [&](ImageId, Image& image) {
            if (image.Overlaps(address, max_size)) {
                image.flags |= ImageFlagBits::GpuDirty;
            }
        });
        return;
    }""")
    edit(r,"    runtime.FillBuffer(buffer, offset, num_bytes, value);",
    """    if (!is_gds) {
        texture_cache.InvalidateMemoryFromGPU(address, num_bytes, true);
    }
    runtime.FillBuffer(buffer, offset, num_bytes, value);""")
    edit(r,"    texture_cache.InvalidateMemoryFromGPU(dst, num_bytes);",
    """    if (!dst_gds) {
        texture_cache.InvalidateMemoryFromGPU(dst, num_bytes, true);
    }""")
    # The set has two producers; both are gated by this immutable flag.
    edit(tc,"void TextureCache::ProcessDownloadImages() {",
         """void TextureCache::ProcessDownloadImages() {
    if (!readback_linear_images) return;""")
    return {"textureExpansion":"GPU-owned clean contents only, never overwrite fresh CPU upload",
            "dma":"overlap invalidation on GPU copy/fill; preserve shader exact-base policy",
            "readback":"skip empty linear-download lock only when producers disabled",
            "reference":"SotC PC #5444 and actual 0.2.0 donor DMA pool fixes",
            "cpu":"FEX unchanged"}
