#!/usr/bin/env python3
"""Restore the verified A830 Vulkan device-extension delta vs GameHub.

Evidence:
 * ShadowOfTheColossus-Logs-20261101-213952.zip (working GameHub 26.2.99)
   does not list VK_EXT_depth_range_unrestricted as unavailable.
 * ShadowOfTheColossus-Logs-20261102-161751.zip (V38 26.99.99) does.
 * GameHub original libvulkan_freedreno.so SHA256:
   1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
 * V38 Mesa f28352 tu_pipeline.cc:2586-2681 already emits unclamped depth
   viewport scales, offsets and Z clamp registers directly as floats.

This enables the standard Vulkan device extension only for documented A830
chip IDs. It does NOT clamp, change math, force depth mode, or touch the APK.
"""
from pathlib import Path
import sys

OLD = """      .EXT_depth_clamp_zero_one = true,
      .EXT_depth_clip_control = true,"""
NEW = """      .EXT_depth_clamp_zero_one = true,
      // GameHub A830 supports EXT_depth_range_unrestricted; V38 omitted
      // advertising it despite already emitting floating Z viewport ranges.
      // Keep the advertised capability narrowly scoped to original A830 IDs.
      .EXT_depth_range_unrestricted =
         device->dev_id.chip_id == 0xffff44050000ull ||
         device->dev_id.chip_id == 0xffff44050001ull ||
         device->dev_id.chip_id == 0x44050001ull,
      .EXT_depth_clip_control = true,"""

def apply(path: Path):
    s = path.read_text()
    if s.count(OLD) != 1 or ".EXT_depth_range_unrestricted =" in s:
        raise ValueError("Pinned Mesa V38 extension table changed or already patched")
    if "GRAS_CL_VIEWPORT_ZOFFSET" in s:
        raise ValueError("unexpected source: source guard refers to device table only")
    out = s.replace(OLD, NEW, 1)
    assert out.count(".EXT_depth_range_unrestricted =") == 1
    path.write_text(out)
    print("PASS GameHub A830 VK_EXT_depth_range_unrestricted advertised on 3 A830 IDs")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv) > 1 else
          Path("src/freedreno/vulkan/tu_device.cc"))
