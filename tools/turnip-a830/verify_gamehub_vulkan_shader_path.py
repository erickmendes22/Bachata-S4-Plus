#!/usr/bin/env python3
"""Verify GameHub original/DD and R11 *executable* Vulkan IR3 shader path.

Source checks use SHA256 and AArch64 instruction words directly from ELF
LOAD segments. Not a claim that shader outputs are equivalent.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

HASHES = {
    "original": "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404",
    "gamehub_dd": "4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9",
    "r11": "ba10389c1b22cb74eda7e094693a14d7f270d26bc92b408d3964cc5f7d68f322",
}
GH = {
    # Real Vulkan graphics path initializes the complete 120-byte key
    # to zero: 8 + 3*32 + 16 = 120, then passes &key at 0x9e77ec.
    0x9e775c: 0xf81803bf,  # stur xzr,[fp,-0x80] (remaining eight bytes)
    0x9e7760: 0xad3903a0,  # stp q0,q0,[fp,-0xe0]
    0x9e7764: 0xad3a03a0,  # stp q0,q0,[fp,-0xc0]
    0x9e7768: 0xad3b03a0,  # stp q0,q0,[fp,-0xa0]
    0x9e776c: 0x3c9103a0,  # stur q0,[fp,-0xf0]
    0x9e77d0: 0xd103c3a5,  # sub x5,fp,#0xf0 (key pointer)
    0x9e77ec: 0x9400eb67,  # bl GameHub Vulkan shader create
    0xa2317c: 0x94028b08,  # Shader from NIR: real Vulkan call
    0xa2318c: 0x94028a33,  # Create IR3 shader variant: real Vulkan call
    0xac5ccc: 0x52800f02,  # memcmp: 120 bytes
    0xac5ce0: 0x39410aa8,  # key[0x2a] from variant[0x42]
    0xac5cec: 0x3940af08,  # load key[0x2b]
    0xac5cf0: 0x39410ea9,  # load variant[0x43]
    0xac7e40: 0x3c818281,  # copy key quad
    0xac7e44: 0x3c828280,  # copy key quad
    0xac7e50: 0x3c838281,  # copy key quad
    0xade7d8: 0x39410d09,  # barycentric load variant[0x43]
    0xade7e8: 0x7100093f,  # barycentric compare mode with 2
}
R11 = {0xa25c50: 0x52800a02, 0xa25cd0: 0x52800a02}

def instruction_at(buf, addr):
    assert buf[:4] == b"\x7fELF" and buf[4] == 2 and buf[5] == 1
    phoff = struct.unpack_from("<Q", buf, 0x20)[0]
    phent, phnum = struct.unpack_from("<HH", buf, 0x36)
    for i in range(phnum):
        kind, flags, offset, vaddr, paddr, filesz, memsz, align = (
            struct.unpack_from("<IIQQQQQQ", buf, phoff + i * phent))
        if kind == 1 and vaddr <= addr and addr + 4 <= vaddr + filesz:
            return struct.unpack_from("<I", buf, offset + addr - vaddr)[0]
    raise AssertionError("ELF address not mapped: " + hex(addr))

def verify(path, key, expected):
    buf = Path(path).read_bytes()
    actual_sha = hashlib.sha256(buf).hexdigest()
    assert actual_sha == HASHES[key], f"Wrong {key} ELF: {actual_sha}"
    for addr, opcode in expected.items():
        actual = instruction_at(buf, addr)
        assert actual == opcode, (key, hex(addr), hex(opcode), hex(actual))
    return len(expected)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--gamehub-dd", type=Path, required=True)
    p.add_argument("--r11", type=Path, required=True)
    args = p.parse_args()
    counts = {
        "original": verify(args.original, "original", GH),
        "gamehub_dd": verify(args.gamehub_dd, "gamehub_dd", GH),
        "r11": verify(args.r11, "r11", R11),
    }
    print(json.dumps({
        "verified_instructions": counts,
        "original_and_dd_vulkan_variant_key_bytes": 120,
        "r11_variant_key_bytes": 80,
        "original_barycentric_mode_byte": "variant+0x43 = key+0x2b",
        "one_vulkan_path_initializes_full_key_to_zero": True,
        "not_verified": [
            "Shader inputs/output match for a real Shadow of the Colossus material",
            "Source of key[0x2b] in the Vulkan pipeline for a real primitive",
            "Visual correctness of a future patched driver",
        ]
    }, indent=2))
if __name__ == "__main__":
    main()
