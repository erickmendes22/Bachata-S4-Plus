#!/usr/bin/env python3
"""Compare NIR intrinsic ABI in original GameHub, working GameHub DD, R11.

This is a *binary-structure* comparison: NIR opcode names and intrinsic
metadata, NOT proof that a real game shader executes any particular intrinsic.
It reads the ELF's .rodata and .data.rel.ro directly, with no disassembler
dependencies, and rejects unexpected binary revisions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

EXPECTED = {
    "gamehub": "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404",
    "gamehub_dd": "4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9",
    "r11": "ba10389c1b22cb74eda7e094693a14d7f270d26bc92b408d3964cc5f7d68f322",
}
INTRINSIC_ENTRY_BYTES = 136  # established from adjacent sorted ELF name pointers

def elf_sections(b):
    assert b[:4] == b"\x7fELF" and b[4] == 2 and b[5] == 1, "Expected ELF64 little-endian"
    shoff = struct.unpack_from("<Q", b, 0x28)[0]
    shentsize, shnum, shstr = struct.unpack_from("<HHH", b, 0x3a)
    sections = [struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * shentsize)
                for i in range(shnum)]
    st = sections[shstr]
    name_table = b[st[4]:st[4]+st[5]]
    return {name_table[s[0]:].split(b"\0", 1)[0].decode(): s for s in sections}

def analyze(path, expected_sha):
    b = Path(path).read_bytes()
    actual = hashlib.sha256(b).hexdigest()
    assert actual == expected_sha, f"Unexpected ELF {path}: {actual}"
    sections = elf_sections(b)
    data = sections[".data.rel.ro"]
    rodata = sections[".rodata"]

    def get_name(off):
        if not data[4] <= off <= data[4] + data[5] - 8:
            return None
        value = struct.unpack_from("<Q", b, off)[0]
        if not rodata[3] <= value < rodata[3] + rodata[5]:
            return None
        in_file = rodata[4] + value - rodata[3]
        raw = b[in_file:in_file+100].split(b"\0", 1)[0]
        if not 3 <= len(raw) <= 95 or any(c < 32 or c > 126 for c in raw):
            return None
        return raw.decode()

    needle = b"ddx\0"
    ropos = b.find(needle, rodata[4], rodata[4]+rodata[5])
    assert ropos >= 0, "NIR ddx name not found"
    row = b.find(struct.pack("<Q", rodata[3] + ropos-rodata[4]),
                 data[4], data[4]+data[5])
    assert row >= 0, "NIR metadata table not found"
    while True:
        prior = get_name(row-INTRINSIC_ENTRY_BYTES)
        current = get_name(row)
        if prior is None or current is None or prior >= current:
            break
        row -= INTRINSIC_ENTRY_BYTES

    out = {}
    while True:
        name = get_name(row)
        if name is None or (out and name <= list(out)[-1]):
            break
        if name in out:
            raise AssertionError("Duplicate NIR intrinsic: " + name)
        out[name] = b[row+8:row+INTRINSIC_ENTRY_BYTES].hex()
        row += INTRINSIC_ENTRY_BYTES
    assert 900 < len(out) < 1050, f"Unexpected intrinsic table length: {len(out)}"
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gamehub", type=Path, required=True)
    p.add_argument("--gamehub-dd", type=Path, required=True)
    p.add_argument("--r11", type=Path, required=True)
    args = p.parse_args()
    original = analyze(args.gamehub, EXPECTED["gamehub"])
    dd = analyze(args.gamehub_dd, EXPECTED["gamehub_dd"])
    r11 = analyze(args.r11, EXPECTED["r11"])
    assert original == dd, "Working GameHub DD changed NIR metadata: revisit binary identification"

    missing = sorted(original.keys() - r11.keys())
    added = sorted(r11.keys() - original.keys())
    changed = sorted(name for name in original.keys() & r11.keys()
                     if original[name] != r11[name])
    assert len(original) == 958 and len(r11) == 967
    assert len(missing) == 6 and len(added) == 15 and len(changed) == 3
    print(json.dumps({
        "validated_sha256": EXPECTED,
        "original_and_working_dd_nir_tables_identical": True,
        "gamehub_intrinsics": len(original),
        "r11_intrinsics": len(r11),
        "present_in_gamehub_missing_in_r11": missing,
        "present_in_r11_missing_in_gamehub": added,
        "shared_entries_with_different_metadata": changed,
        "not_proven": [
            "A missing intrinsic necessarily produces a different shader",
            "Any missing intrinsic executes in Shadow of the Colossus",
            "Shader execution output or rendering parity"
        ]
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
