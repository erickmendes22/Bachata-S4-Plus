#!/usr/bin/env python3
"""A830v1-specific memory-coherency workaround for Gen8 V38 Mesa.

The WinNative patchset already provides the fd_dev_info.disable_gmem flag
and runtime sysmem fallback, but the original V38 recipe only enables it for
A810/A829. A830 is documented as having GMEM corruption/page faults.
Avoid speculative texture prefetch on A830 (existing Gen2 workaround).
Fail if the target code differs; never touch other GPU profiles.
"""
from pathlib import Path
p = Path("src/freedreno/common/freedreno_devices.py")
s = p.read_text()
prefix = '''add_gpus([
        GPUId(chip_id=0xffff44050000, name="Adreno (TM) 830"),
        GPUId(chip_id=0xffff44050001, name="Adreno (TM) 830v1"),
        GPUId(chip_id=0x44050001, name="Adreno (TM) 830"), # KGSL
    ], A6xxGPUInfo(
        CHIP.A8XX,
        [a7xx_base, a7xx_gen3, a8xx_base, a8xx_gen1],'''
replacement=prefix.replace(
    "        [a7xx_base, a7xx_gen3, a8xx_base, a8xx_gen1],",
    """        [a7xx_base, a7xx_gen3, a8xx_base, a8xx_gen1, GPUProps(
            # A830 can produce corrupt images and write faults in GMEM.
            # Use the existing WinNative disable_gmem -> SYSMEM path.
            disable_gmem = True,
            # A810/Gen2 already avoid the experimental FS prefetch.
            has_fs_tex_prefetch = False,
        )],"""
)
assert s.count(prefix)==1, f"A830 profile mismatch: {s.count(prefix)}"
s=s.replace(prefix,replacement,1)
p.write_text(s)
print("A830v1 GMEM disabled; fragment texture prefetch disabled.")
print("All A810, A829, A840, A7xx profiles preserved.")
