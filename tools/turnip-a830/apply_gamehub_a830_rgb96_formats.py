#!/usr/bin/env python3
"""Restore GameHub A830 RGB96 sampled image and transfer support, safely.

GameHub working A830 log advertises R32G32B32_SFLOAT sampled and transfer,
where the pinned V38 reports all three features unavailable. The V38 hardware
format table already marks RGB32 UINT/SINT/FLOAT as texture-readable (VT_),
but tu_formats.cc withholds IMAGE support because CP_BLIT cannot render to
non-power-of-two cpp. The separate CP_MEMCPY-based transfer implementation
is applied by apply_gamehub_a830_rgb96_copy.py. Both scripts are mandatory.

fdl6_layout_image() supports 12-byte pixels in LINEAR mode only, and
fd6_view descriptor uses a 16-byte pitch alignment. We therefore FORCE
the image's physical tiling mode LINEAR, disable UBWC, reject unsupported
image usages and sample count above one. No changes for non-A830 devices.
"""
from pathlib import Path
import sys

def a830_expr(pdev):
    return ("(" + pdev + "->dev_id.chip_id == 0xffff44050000ull ||\n"
            "         " + pdev + "->dev_id.chip_id == 0xffff44050001ull ||\n"
            "         " + pdev + "->dev_id.chip_id == 0x44050001ull)")

RGB = """(vk_format == VK_FORMAT_R32G32B32_UINT ||
      vk_format == VK_FORMAT_R32G32B32_SINT ||
      vk_format == VK_FORMAT_R32G32B32_SFLOAT)"""

def fmt(path):
    s=path.read_text()
    before = """   /* Don't support anything but texel buffers for non-power-of-two formats
    * with 3 components. We'd need several workarounds for copying and
    * clearing them because they're not renderable.
    */
   if (supported_tex && !is_npot) {"""
    after = """   // GameHub A830 exposes sampled RGB96 and transfer, backed by a
   // linear 12-byte-pixel layout and CP_MEMCPY for buffer/image transfers.
   // RGB96 remains intentionally NON-renderable; there is no RGB96 RB format.
   const bool gamehub_a830_rgb96 =
      """+a830_expr("physical_device")+""" &&
      """+RGB+""";
   if (gamehub_a830_rgb96 && supported_tex) {
      optimal |= VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_BIT |
                 VK_FORMAT_FEATURE_2_TRANSFER_SRC_BIT |
                 VK_FORMAT_FEATURE_2_TRANSFER_DST_BIT |
                 VK_FORMAT_FEATURE_2_SAMPLED_IMAGE_FILTER_MINMAX_BIT;
   }

   /* Don't support anything but texel buffers for other non-power-of-two
    * formats. GameHub A830 RGB96 is the narrow, explicitly linear exception.
    */
   if (supported_tex && !is_npot) {"""
    if s.count(before)!=1:
        raise ValueError("V38 format support block drifted")
    s=s.replace(before, after, 1)
    anchor="""   if (info->type != VK_IMAGE_TYPE_2D &&
       vk_format_is_depth_or_stencil(info->format))
      return tu_image_unsupported_format(pImageFormatProperties);"""
    insertion="""   // RGB96 image support is implemented for 2D non-sparse, non-mutable
   // images only. Never advertise unsupported 3D/array sparse or MSAA.
   const bool gamehub_a830_rgb96_image =
      """+a830_expr("physical_device")+""" &&
      (info->format == VK_FORMAT_R32G32B32_UINT ||
       info->format == VK_FORMAT_R32G32B32_SINT ||
       info->format == VK_FORMAT_R32G32B32_SFLOAT);
   if (gamehub_a830_rgb96_image &&
       (info->type != VK_IMAGE_TYPE_2D ||
        (info->flags & (VK_IMAGE_CREATE_SPARSE_BINDING_BIT |
                        VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT)) ||
        info->tiling == VK_IMAGE_TILING_DRM_FORMAT_MODIFIER_EXT ||
        info->usage & (VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT |
                       VK_IMAGE_USAGE_STORAGE_BIT |
                       VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT |
                       VK_IMAGE_USAGE_FRAGMENT_DENSITY_MAP_BIT_EXT)))
      return tu_image_unsupported_format(pImageFormatProperties);

"""
    if s.count(anchor)!=1:
        raise ValueError("V38 RGB96 format query image guard drifted")
    s=s.replace(anchor,insertion+anchor,1)
    path.write_text(s)
    print("PASS: A830 RGB96 sampled+transfer image features and safety queries")

def img(path):
    s=path.read_text()
    before="""   /* No sense in tiling a 1D image, you'd just waste space and cache locality. */
   if (pCreateInfo->imageType == VK_IMAGE_TYPE_1D) {
      force_linear_tile = true;
   }"""
    after="""   // Original GameHub supports sampled RGB96 on A830. Physical RGB96
   // storage must be linear because cpp=12 cannot use tiled/UBWC layout.
   const uint64_t chip_id = device->physical_device->dev_id.chip_id;
   const bool gamehub_a830_rgb96 =
      (chip_id == 0xffff44050000ull || chip_id == 0xffff44050001ull ||
       chip_id == 0x44050001ull) &&
      (image->vk.format == VK_FORMAT_R32G32B32_UINT ||
       image->vk.format == VK_FORMAT_R32G32B32_SINT ||
       image->vk.format == VK_FORMAT_R32G32B32_SFLOAT);
   if (gamehub_a830_rgb96)
      force_linear_tile = true;

   /* No sense in tiling a 1D image, you'd just waste space and cache locality. */
   if (pCreateInfo->imageType == VK_IMAGE_TYPE_1D) {
      force_linear_tile = true;
   }"""
    if s.count(before)!=1: raise ValueError("V38 image linear guard drifted")
    s=s.replace(before,after,1)
    path.write_text(s)
    print("PASS: A830 RGB96 always linear (not UBWC/tiled)")

def main():
    base=Path(sys.argv[1]) if len(sys.argv)>1 else Path(".")
    fmt(base/"src/freedreno/vulkan/tu_formats.cc")
    img(base/"src/freedreno/vulkan/tu_image.cc")

if __name__=="__main__": main()
