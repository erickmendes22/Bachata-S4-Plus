#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""R17 guard against FEX SIGSEGV at 0x130b57c from the R16 absolute BLR.

AArch64 PIE execution requires PC-relative BL (relocated with the loaded
executable base), never ldr x16, =0x130b57c; blr x16.
"""
import argparse
import struct
from pathlib import Path

BRANCHES = {
    0x3E83E14: 0x130B57C,  # original FsrPass Create
    0x3E83E20: 0x6C91A0,   # original dlsym PLT
    0x3E84020: 0x6C91A0,   # original dlsym PLT
    0x3E84054: 0x130F524,  # original FsrPass Render
}

def read_bl(data, pc):
    instruction = struct.unpack_from("<I", data, pc)[0]
    if instruction >> 26 != 0b100101:
        raise AssertionError(f"Not PC-relative BL at 0x{pc:x}: 0x{instruction:08x}")
    delta = instruction & 0x03ffffff
    if delta & (1 << 25):
        delta -= 1 << 26
    return pc + 4 * delta

def main():
    p = argparse.ArgumentParser()
    p.add_argument("core025", help="Patched real R15 host/shadps4-arm64-025")
    args = p.parse_args()
    data = Path(args.core025).read_bytes()
    assert data[:4] == b"\x7fELF"
    for pc, original in BRANCHES.items():
        assert read_bl(data, pc) == original, (hex(pc),hex(original))
        for runtime_base in (0, 0x5550000000, 0x7DD0000000):
            assert runtime_base + read_bl(data, pc) == runtime_base + original
    print("PASS R17: all four calls survive PIE relocation; no absolute guest jump")

if __name__ == "__main__":
    main()
