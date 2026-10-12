#!/usr/bin/env python3
"""Fail-closed static ABI map for the exact BACHATA 0.2.6 ARM64 core024.

These verified locations identify the REAL C++ Rasterizer::PrepareRenderState
and its regular/indirect draw call-sites. No guest image is modified here.
Never apply to a core with another SHA256, even if the version string matches.
"""
from __future__ import annotations
import hashlib
import struct
import sys
from pathlib import Path

EXPECTED_SHA256 = "04294ca3223e26c864429f243a21fe8f9de99400074fb9bf8630109939490702"
PREPARE_RENDER_STATE = 0x12A7F5C
CALL_REGULAR_DRAW = 0x12A8FC8
CALL_INDIRECT_DRAW = 0x12AB6EC

def bl_target(pc: int, word: int) -> int | None:
    if word & 0xFC000000 != 0x94000000:
        return None
    offset = word & 0x03FFFFFF
    if offset & 0x02000000:
        offset -= 0x04000000
    return pc + offset * 4

def verify(path: Path) -> None:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, f"unexpected core BuildID/SHA256: {digest}"
    assert raw[:4] == b"\x7fELF"
    assert raw[0x12A7F5C:0x12A7F60] == bytes.fromhex("ff8304d1"), \
        "PrepareRenderState prologue unexpectedly changed"
    for pc in (CALL_REGULAR_DRAW, CALL_INDIRECT_DRAW):
        (word,) = struct.unpack_from("<I", raw, pc)
        assert bl_target(pc, word) == PREPARE_RENDER_STATE, \
            f"draw callsite {pc:#x} no longer calls rasterizer"
    # x19 holds the Rasterizer object in BOTH callers, and x20/x24 hold
    # the GraphicsPipeline for regular/indirect paths respectively.
    assert raw[0x12A8FC0:0x12A8FC8] == bytes.fromhex("e00313aae10314aa")
    assert raw[0x12AB6E4:0x12AB6EC] == bytes.fromhex("e00313aae10318aa")
    print("Confirmed core024; guest Rasterizer::PrepareRenderState "
          f"{PREPARE_RENDER_STATE:#x}, Draw {CALL_REGULAR_DRAW:#x}, "
          f"DrawIndirect {CALL_INDIRECT_DRAW:#x}")

if __name__ == "__main__":
    verify(Path(sys.argv[1]))
