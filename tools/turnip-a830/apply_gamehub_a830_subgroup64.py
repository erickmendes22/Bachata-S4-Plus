#!/usr/bin/env python3
"""Restore the original GameHub A830 subgroup size advertisement (64 only).

Grounded in full working A830 driver logs (GameHub 26.2.99) versus the
previous V38 driver logs (26.99.99):
 GameHub: size 64, min 64, max 64, required stages ALL.
 V38:     size 64, min 32, max 64, required stages ALL.
Both compile the SotC guest shaders for wave64. Do not tamper with compiler
bitcode or force wave32/64 internally: only advertise what GameHub exposes.
The V38 requiredSubgroupSizeStages conditional remains untouched.
"""
from pathlib import Path
import sys

# These anchors are from the actual A8xx WinNative patch 0002 which is
# applied BEFORE this script. The upstream unpatched V38 has a different
# subgroup advertisement (pdevice->info->threadsize_base).
OLD = """   p->minSubgroupSize = tu_min_subgroup_size(pdevice);
   p->maxSubgroupSize = tu_subgroup_size(pdevice);
   p->maxComputeWorkgroupSubgroups = pdevice->info->max_waves *
      pdevice->info->threadsize_base / p->minSubgroupSize;"""

NEW = """   // GameHub A830 reports fixed 64-thread subgroups. WinNative's
   // half-wave emulation remains available for other Adreno devices, but
   // should not be exposed to applications selecting this A830 profile.
   const uint64_t chip_id = pdevice->dev_id.chip_id;
   const bool gamehub_a830_wave64 =
      chip_id == 0xffff44050000ull ||
      chip_id == 0xffff44050001ull ||
      chip_id == 0x44050001ull;
   p->maxSubgroupSize = tu_subgroup_size(pdevice);
   p->minSubgroupSize = gamehub_a830_wave64 ?
      p->maxSubgroupSize : tu_min_subgroup_size(pdevice);
   p->maxComputeWorkgroupSubgroups = pdevice->info->max_waves *
      pdevice->info->threadsize_base / p->minSubgroupSize;"""

def apply(path: Path):
    src=path.read_text()
    if src.count(OLD) != 1 or "gamehub_a830_wave64" in src:
        raise ValueError("Unexpected pinned Mesa 1.3 subgroup path or already patched")
    for needle in ("p->requiredSubgroupSizeStages =",
                   "p->minSubgroupSize == p->maxSubgroupSize",
                   "VK_SHADER_STAGE_COMPUTE_BIT | VK_SHADER_STAGE_FRAGMENT_BIT"):
        if needle not in src:
            raise ValueError("Missing existing subgroup constraint: "+needle)
    path.write_text(src.replace(OLD,NEW,1))
    print("PASS A830 GameHub 64/64 subgroup capability parity")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/vulkan/tu_device.cc"))
