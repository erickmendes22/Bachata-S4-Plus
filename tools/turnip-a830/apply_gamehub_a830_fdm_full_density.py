#!/usr/bin/env python3
"""Port verified GameHub A830 full-density FDM behavior into pinned Mesa V38.

Original user's GameHub ELF SHA256:
1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404

At 0xA3608C..0xA360B8 (original ARM64):
  cbz x21  -> default area computation
  ldr ... device->info
  ldrb w8, [x8, #0x309]  // fd_dev_info::fdm_requires_full_density
  tbz w8, #0, 0xA360B8   // if false sample FDM texture
  otherwise initialize raw_areas to 1.0 (0xA36170..0xA361AC)
A830, A830v1, KGSL chip profile sets offset 0x309 to 1.
This matches Mesa V38 tu_tile_config.cc::tu_calc_frag_area() and leaves
FDM metadata intact; ONLY avoids variable density for those A830 IDs.
"""
from pathlib import Path
import sys

BEFORE = """   struct tu_frag_area raw_areas[views];
   if (fdm) {
      for (unsigned i = 0; i < views; i++) {"""
AFTER = """   struct tu_frag_area raw_areas[views];
   // Recovered GameHub A830 quirk: fd_dev_info+0x309 is 1, so
   // tu_calc_frag_area uses full density rather than sampling FDM.
   // Other chips and renderpasses without FDM retain V38 behavior.
   const uint64_t chip_id = cmd->device->physical_device->dev_id.chip_id;
   const bool gamehub_a830_full_density =
      chip_id == 0xffff44050000ull ||
      chip_id == 0xffff44050001ull ||
      chip_id == 0x44050001ull;
   if (fdm && !gamehub_a830_full_density) {
      for (unsigned i = 0; i < views; i++) {"""

def apply(path: Path):
    s=path.read_text()
    if s.count(BEFORE)!=1 or "gamehub_a830_full_density" in s:
        raise ValueError("Pinned Mesa V38 tile config drift/already patched")
    for guard in ("tu_fragment_density_map_sample(fdm,", "tu_calc_frag_area(",
                  "raw_areas[i].width = raw_areas[i].height = 1.0f;",
                  "tu_calc_tile_config("):
        if guard not in s: raise ValueError("Missing pinned image path: "+guard)
    s=s.replace(BEFORE,AFTER,1)
    assert s.count("if (fdm && !gamehub_a830_full_density)") == 1
    path.write_text(s)
    print("PASS: A830 GameHub FDM full-density policy integrated")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/freedreno/vulkan/tu_tile_config.cc"))
