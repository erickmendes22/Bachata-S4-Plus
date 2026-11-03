#!/usr/bin/env python3
"""A830 Android native buffer safety: unknown DRM modifier must not become tiled.

Mesa pinned source tu_image.cc defaults to TILE6_3/format-dependent UBWC when
modifier is DRM_FORMAT_MOD_INVALID; an unknown 1-plane Android gralloc buffer
may actually be linear. Limit fallback to Android NATIVE_BUFFER (ANB), single
plane, row-pitch known, and A830. Regular Vulkan images, explicitly compressed
buffers, multi-plane formats and non-A830 GPUs are untouched.

This is a narrowly scoped candidate motivated by a reproduced Adreno 830
gralloc INVALID->tiled display-output bug. It is NOT proof that SotC's
ghosting/flicker originates here. Do not build a tester driver merely from
successful source guards.
"""
import sys
from pathlib import Path

OLD = """      plane_layouts = a_plane_layouts;
      modifier = eci.drmFormatModifier;
   }

   result = TU_CALLX(device, tu_image_init)(device, image, pCreateInfo,
                                             modifier, plane_layouts,"""

NEW = """      plane_layouts = a_plane_layouts;
      modifier = eci.drmFormatModifier;

      // Mesa otherwise falls through to TILE6_3 for UNKNOWN DRM modifier.
      // Imported ANB is NOT a driver-owned optimally tiled Vulkan image.
      // If the Android gralloc metadata backend cannot identify a simple
      // single-plane allocation, conservatively use its explicit row pitch
      // as LINEAR instead of writing UBWC metadata into a display buffer.
      // Known compressed modifiers are never changed.
      const uint64_t gamehub_anb_chip_id =
         device->physical_device->dev_id.chip_id;
      const bool gamehub_a830_unknown_anb_linear =
         (gamehub_anb_chip_id == 0xffff44050000ull ||
          gamehub_anb_chip_id == 0xffff44050001ull ||
          gamehub_anb_chip_id == 0x44050001ull) &&
         modifier == DRM_FORMAT_MOD_INVALID &&
         eci.drmFormatModifierPlaneCount == 1 &&
         a_plane_layouts[0].offset == 0 &&
         a_plane_layouts[0].rowPitch > 0;
      if (gamehub_a830_unknown_anb_linear) {
         modifier = DRM_FORMAT_MOD_LINEAR;
      }
   }

   result = TU_CALLX(device, tu_image_init)(device, image, pCreateInfo,
                                             modifier, plane_layouts,"""

def apply(path: Path):
    s=path.read_text()
    if s.count(OLD)!=1:
        raise RuntimeError("Cannot locate verified pinned Mesa ANB import: drift")
    if "gamehub_a830_unknown_anb_linear" in s:
        raise RuntimeError("Already applied")
    assert s.find("if (vk_image_is_android_native_buffer(&image->vk))")>=0
    s=s.replace(OLD,NEW,1)
    p=s.index("gamehub_a830_unknown_anb_linear")
    assert s.rfind("if (vk_image_is_android_native_buffer(&image->vk))",0,p)>=0
    assert p<s.index("TU_CALLX(device, tu_image_init)",p)
    path.write_text(s)
    print("PASS: A830 only; unknown ANB modifier with one known plane -> LINEAR")

if __name__=="__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/vulkan/tu_image.cc"))
