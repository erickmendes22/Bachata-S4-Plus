#!/usr/bin/env python3
"""A830-only Turnip GMEM safety path for Mesa f28352d (V38), not a global
TU_DEBUG=sysmem override and not an APK-side setting.

The A830 has reported damaged render targets / page write faults in GMEM.
Prefer sysmem for A830 by default while preserving explicit TU_DEBUG=gmem
as a revert switch. A840 shares 0x4405 as family prefix but uses different
low 16 bits, so compare the FULL low 32 bits.
"""
from pathlib import Path
import argparse

GPU_IDS = (0x44050000, 0x44050001)
ANCHOR = '''   if (TU_DEBUG(SYSMEM)) {
      cmd->state.rp.force_render_mode_reason = "TU_DEBUG(SYSMEM)";
      return true;
   }
'''
NEW = '''
   /* A830: GMEM framebuffer stores can corrupt the rendered image through
    * page write faults (documented by the A8xx Turnip maintainer).
    * Do not force this on A840 (chip_id=0xffff44050a31 / 0xffff44050a21)
    * or on the other A8xx models. Can opt out with TU_DEBUG=gmem.
    * This changes the DRIVER render mode, not SotC or FEX settings.
    */
   const uint32_t a830_chip_id =
      static_cast<uint32_t>(cmd->device->physical_device->dev_id.chip_id);
   if (!TU_DEBUG(GMEM) &&
       (a830_chip_id == 0x44050000u || a830_chip_id == 0x44050001u)) {
      cmd->state.rp.force_render_mode_reason =
         "A830 GMEM page-write workaround: use SYSMEM";
      return true;
   }
'''

def modify(path: Path):
    s=path.read_text()
    start=s.find("static bool\nuse_sysmem_rendering(")
    end=s.find("\n/* Optimization: there is no reason to load gmem",start)
    if start<0 or end<0:
        raise ValueError("Mesa V38 use_sysmem_rendering not found")
    fn=s[start:end]
    if fn.count(ANCHOR)!=1:
        raise ValueError("Unexpected V38 TU_DEBUG(SYSMEM) decision path")
    for test in ("if (cmd->state.rp.has_tess)", "if (TU_DEBUG(GMEM))",
                 "cmd->device->autotune->get_optimal_mode"):
        if test not in fn:
            raise ValueError("Lost V38 renderpass semantics: "+test)
    if "A830 GMEM page-write workaround" in fn:
        raise ValueError("Patch already applied")
    s=s[:start] + fn.replace(ANCHOR,ANCHOR+NEW,1) + s[end:]
    path.write_text(s)
    print("A830 SYSMEM safety integrated, A840 untouched, TU_DEBUG=gmem opt-out")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    modify(p.parse_args().source)
