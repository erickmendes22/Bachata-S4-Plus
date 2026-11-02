#!/usr/bin/env python3
"""GameHub A830 RGB96 linear image transfers: a complete CP_MEMCPY fallback.

The hardware texture format table already has RGB32 FLOAT TEX,
but the 2D blitter cannot output 12-byte (RGB96) pixels and the V38
format feature gate denies sampled and TRANSFER_SRC/DST to these formats.
These operations use the CP_MEMCPY command packet used by Mesa's
tu_device.cc trace copies. No 2D/3D render target is advertised.
Linear 2D image layout, non-UBWC, 1x sample count, no sparse or mutable
forms are REQUIRED and checked before use.
"""
from pathlib import Path
import sys

HELPERS = r'''
// GameHub A830 RGB96 image fallback. The original GameHub driver
// advertises sampled/transfer for these formats; V38's R2D destination has
// no corresponding RB color format. 2D images are stored in linear memory.
static bool
tu_gamehub_a830_rgb96(struct tu_cmd_buffer *cmd, VkFormat format)
{
   const uint64_t chip_id = cmd->device->physical_device->dev_id.chip_id;
   return (chip_id == 0xffff44050000ull ||
           chip_id == 0xffff44050001ull ||
           chip_id == 0x44050001ull) &&
          (format == VK_FORMAT_R32G32B32_SFLOAT);
}

static void
tu_gamehub_a830_memcpy(struct tu_cs *cs, uint64_t dst_va,
                        uint64_t src_va, uint64_t bytes)
{
   // Both source and destination are 4-byte aligned: 3 x 32-bit texels.
   // Keep individual packet sizes bounded even for very wide images.
   while (bytes) {
      const uint32_t n = static_cast<uint32_t>(MIN2(bytes, 0x30000ull));
      tu_cs_emit_pkt7(cs, CP_MEMCPY, 5);
      tu_cs_emit(cs, n / 4);
      tu_cs_emit_qw(cs, src_va);
      tu_cs_emit_qw(cs, dst_va);
      dst_va += n;
      src_va += n;
      bytes -= n;
   }
}

static void
tu_gamehub_a830_rgb96_transfer_barrier(struct tu_cmd_buffer *cmd)
{
   // Subsequent shaders must not sample stale image data, and CP writes
   // must complete before dependent commands consume the destination.
   cmd->state.cache.flush_bits |=
      TU_CMD_FLAG_WAIT_MEM_WRITES | TU_CMD_FLAG_CACHE_INVALIDATE;
}

static void
tu_gamehub_a830_rgb96_buffer_image(struct tu_cmd_buffer *cmd,
                                    struct tu_buffer *buffer,
                                    struct tu_image *image,
                                    const VkBufferImageCopy2 *info,
                                    bool buffer_to_image)
{
   const auto *layout = &image->layout[0];
   const unsigned level = info->imageSubresource.mipLevel;
   const uint32_t pitch = fdl_pitch(layout, level);
   const uint32_t buffer_width = info->bufferRowLength ?
                                  info->bufferRowLength : info->imageExtent.width;
   const uint32_t buffer_height = info->bufferImageHeight ?
                                   info->bufferImageHeight : info->imageExtent.height;
   const uint64_t src_pitch = static_cast<uint64_t>(buffer_width) * 12;
   const uint64_t src_layer_size = src_pitch * buffer_height;
   const uint64_t buffer_base = vk_buffer_address(&buffer->vk, info->bufferOffset);
   const uint32_t layers = vk_image_subresource_layer_count(
      &image->vk, &info->imageSubresource);
   for (uint32_t i = 0; i < layers; i++) {
      const uint32_t layer = info->imageSubresource.baseArrayLayer + i;
      const uint64_t image_base = image->iova +
         fdl_surface_offset(layout, level, layer) +
         static_cast<uint64_t>(info->imageOffset.y) * pitch +
         static_cast<uint64_t>(info->imageOffset.x) * 12;
      const uint64_t buffer_layer = buffer_base + i * src_layer_size;
      for (uint32_t y = 0; y < info->imageExtent.height; y++) {
         const uint64_t image_row = image_base + static_cast<uint64_t>(y) * pitch;
         const uint64_t buffer_row = buffer_layer + static_cast<uint64_t>(y) * src_pitch;
         tu_gamehub_a830_memcpy(&cmd->cs,
                                buffer_to_image ? image_row : buffer_row,
                                buffer_to_image ? buffer_row : image_row,
                                static_cast<uint64_t>(info->imageExtent.width) * 12);
      }
   }
   tu_gamehub_a830_rgb96_transfer_barrier(cmd);
}

static void
tu_gamehub_a830_rgb96_image_image(struct tu_cmd_buffer *cmd,
                                  struct tu_image *src, struct tu_image *dst,
                                  const VkImageCopy2 *info)
{
   const auto *src_layout = &src->layout[0];
   const auto *dst_layout = &dst->layout[0];
   const uint32_t src_level = info->srcSubresource.mipLevel;
   const uint32_t dst_level = info->dstSubresource.mipLevel;
   const uint32_t src_pitch = fdl_pitch(src_layout, src_level);
   const uint32_t dst_pitch = fdl_pitch(dst_layout, dst_level);
   const uint32_t layers =
      vk_image_subresource_layer_count(&src->vk, &info->srcSubresource);
   for (uint32_t i=0; i<layers; ++i) {
      const uint32_t src_layer = info->srcSubresource.baseArrayLayer + i;
      const uint32_t dst_layer = info->dstSubresource.baseArrayLayer + i;
      const uint64_t src_base = src->iova +
         fdl_surface_offset(src_layout, src_level, src_layer) +
         static_cast<uint64_t>(info->srcOffset.y) * src_pitch +
         static_cast<uint64_t>(info->srcOffset.x) * 12;
      const uint64_t dst_base = dst->iova +
         fdl_surface_offset(dst_layout, dst_level, dst_layer) +
         static_cast<uint64_t>(info->dstOffset.y) * dst_pitch +
         static_cast<uint64_t>(info->dstOffset.x) * 12;
      for (uint32_t y=0; y<info->extent.height; ++y) {
         tu_gamehub_a830_memcpy(&cmd->cs,
            dst_base + static_cast<uint64_t>(y) * dst_pitch,
            src_base + static_cast<uint64_t>(y) * src_pitch,
            static_cast<uint64_t>(info->extent.width) * 12);
      }
   }
   tu_gamehub_a830_rgb96_transfer_barrier(cmd);
}

static void
tu_gamehub_a830_rgb96_clear(struct tu_cmd_buffer *cmd,
                            struct tu_image *image,
                            const VkClearColorValue *color,
                            uint32_t range_count,
                            const VkImageSubresourceRange *ranges)
{
   // 256 RGB32 texels per read-only CP_MEMCPY staging block. The source
   // stays alive as part of command buffer's suballocated GPU storage.
   constexpr uint32_t texels = 256;
   struct tu_cs_memory tmp;
   VkResult result = tu_cs_alloc(&cmd->sub_cs, texels * 3, 1, &tmp);
   if (result != VK_SUCCESS) {
      vk_command_buffer_set_error(&cmd->vk, result);
      return;
   }
   auto *pattern = static_cast<uint32_t *>(tmp.map);
   for (uint32_t i=0; i<texels; ++i) {
      pattern[i*3+0] = color->uint32[0];
      pattern[i*3+1] = color->uint32[1];
      pattern[i*3+2] = color->uint32[2];
   }

   const auto *layout = &image->layout[0];
   for (uint32_t r=0; r<range_count; ++r) {
      const auto &range = ranges[r];
      const uint32_t levels = vk_image_subresource_level_count(&image->vk, &range);
      const uint32_t layers = vk_image_subresource_layer_count(&image->vk, &range);
      for (uint32_t mip=range.baseMipLevel; mip<range.baseMipLevel+levels; ++mip) {
         const uint32_t width = u_minify(image->vk.extent.width,mip);
         const uint32_t height = u_minify(image->vk.extent.height,mip);
         const uint32_t pitch = fdl_pitch(layout,mip);
         for (uint32_t li=0; li<layers; ++li) {
            const uint64_t base = image->iova +
               fdl_surface_offset(layout,mip,range.baseArrayLayer+li);
            for (uint32_t y=0; y<height; ++y) {
               for (uint32_t x=0; x<width; x+=texels) {
                  uint32_t n = MIN2(width-x, texels);
                  tu_gamehub_a830_memcpy(&cmd->cs,
                     base + static_cast<uint64_t>(y)*pitch + static_cast<uint64_t>(x)*12,
                     tmp.iova, static_cast<uint64_t>(n)*12);
               }
            }
         }
      }
   }
   tu_gamehub_a830_rgb96_transfer_barrier(cmd);
}

'''

def apply(path: Path):
    s=path.read_text()
    if "tu_gamehub_a830_rgb96_buffer_image" in s:
        raise ValueError("RGB96 already patched")
    if s.count("static const VkOffset2D blt_no_coord = { ~0, ~0 };") != 1:
        raise ValueError("Missing V38 header anchor")
    s=s.replace("static const VkOffset2D blt_no_coord = { ~0, ~0 };",
                "static const VkOffset2D blt_no_coord = { ~0, ~0 };\n"+HELPERS,1)

    before="""{
   struct tu_cs *cs = &cmd->cs;
   uint32_t layers = MAX2(info->imageExtent.depth,
                          vk_image_subresource_layer_count(&dst_image->vk,"""
    after="""{
   if (tu_gamehub_a830_rgb96(cmd, dst_image->vk.format)) {
      tu_gamehub_a830_rgb96_buffer_image(cmd, src_buffer, dst_image, info, true);
      return;
   }
   struct tu_cs *cs = &cmd->cs;
   uint32_t layers = MAX2(info->imageExtent.depth,
                          vk_image_subresource_layer_count(&dst_image->vk,"""
    if s.count(before)!=1: raise ValueError("RGB96 buffer->image anchor mismatch")
    s=s.replace(before,after,1)

    before="""{
   struct tu_cs *cs = &cmd->cs;
   uint32_t layers = MAX2(info->imageExtent.depth,
                          vk_image_subresource_layer_count(&src_image->vk,"""
    after="""{
   if (tu_gamehub_a830_rgb96(cmd, src_image->vk.format)) {
      tu_gamehub_a830_rgb96_buffer_image(cmd, dst_buffer, src_image, info, false);
      return;
   }
   struct tu_cs *cs = &cmd->cs;
   uint32_t layers = MAX2(info->imageExtent.depth,
                          vk_image_subresource_layer_count(&src_image->vk,"""
    if s.count(before)!=1: raise ValueError("RGB96 image->buffer anchor mismatch")
    s=s.replace(before,after,1)

    before="""{
   const struct blit_ops *ops = &r2d_ops<CHIP>;
   struct tu_cs *cs = &cmd->cs;

   if (dst_image->layout[0].nr_samples > 1)"""
    after="""{
   if (tu_gamehub_a830_rgb96(cmd, src_image->vk.format) &&
       tu_gamehub_a830_rgb96(cmd, dst_image->vk.format)) {
      tu_gamehub_a830_rgb96_image_image(cmd, src_image, dst_image, info);
      return;
   }
   const struct blit_ops *ops = &r2d_ops<CHIP>;
   struct tu_cs *cs = &cmd->cs;

   if (dst_image->layout[0].nr_samples > 1)"""
    if s.count(before)!=1: raise ValueError("RGB96 image->image anchor mismatch")
    s=s.replace(before,after,1)

    before="""   bool use_generic_clear = use_generic_clear_for_image_clear(cmd, image);
   if (use_generic_clear) {"""
    after="""   if (tu_gamehub_a830_rgb96(cmd, image->vk.format)) {
      tu_gamehub_a830_rgb96_clear(cmd, image, pColor, rangeCount, pRanges);
      trace_end_clear_color_image(&cmd->trace, &cmd->cs);
      return;
   }

   bool use_generic_clear = use_generic_clear_for_image_clear(cmd, image);
   if (use_generic_clear) {"""
    if s.count(before)!=1: raise ValueError("RGB96 clear anchor mismatch")
    s=s.replace(before,after,1)

    path.write_text(s)
    print("PASS: A830 RGB96 transfers (buffer/image/image) and color clear")

if __name__=="__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/vulkan/tu_clear_blit.cc"))
