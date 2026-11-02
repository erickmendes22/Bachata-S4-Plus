#!/usr/bin/env python3
"""Restore GameHub A8xx primitive allocation threshold from exact original ELF.

Cross-device evidence (all byte-aligned within paired A8xx GPUProps profiles):
        GameHub fd_dev_info+0x2b4: 0x0000000f (A810, A830, A829, A840)
        Mesa V38 fd_dev_info+0x2a8: 0x00000007 (same GPUs)
GameHub original .so SHA256: 1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404

The property feeds SP_LB_PARAM_LIMIT.PRIMALLOCTHRESHOLD via tu_shader.cc.
This is a limited GameHub GPU profile restoration, NOT a claim to fix SotC
visual artifacts. The source check is intentionally fail-closed.
"""
from pathlib import Path
import sys
from textwrap import dedent
def apply(source:Path):
    s=source.read_text()
    start=s.find("a8xx_base = GPUProps(")
    end=s.find("\n# For a8xx, the chicken bit",start)
    if start<0 or end<=start:
        raise ValueError("Mesa A8xx GPUProps schema changed")
    block=s[start:end]
    old="        reg_size_vec4 = 96,\n        has_rt_workaround = False,"
    new="        reg_size_vec4 = 96,\n        # Exact original GameHub A8xx GPUProps; SP_LB_PARAM_LIMIT on shader draws.\n        # Native Mesa V38 inherits 7 from a7xx_gen3; GameHub encodes 15.\n        prim_alloc_threshold = 0xF,\n        has_rt_workaround = False,"
    if block.count(old)!=1 or "prim_alloc_threshold" in block:
        raise ValueError("A8xx GPUProps pin drift / already restored")
    if "A6XX_RB_LRZ_CNTL2" not in s and "REG_A7XX_RB_LRZ_CNTL2" not in s:
        raise ValueError("Unexpected Mesa GPU definitions")
    s=s[:start]+block.replace(old,new,1)+s[end:]
    assert s.count("prim_alloc_threshold = 0xF,")==1
    source.write_text(s)
    print("Restored original GameHub A8xx primitive allocation threshold=15.")
if __name__=="__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else Path("src/freedreno/common/freedreno_devices.py"))
