#!/usr/bin/env python3
"""Verify the *original* GameHub A830 gralloc return path and source contract.

Usage:
  python3 tools/turnip-a830/verify_gamehub_gralloc_result_semantics.py
  python3 tools/turnip-a830/verify_gamehub_gralloc_result_semantics.py /path/to/original/libvulkan_freedreno.so

Requires only Python stdlib. This does not test GPU behavior.
"""
import ast
import hashlib
from pathlib import Path
import struct
import sys

ORIGINAL_SHA256 = "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404"

# Opcodes verified with llvm-objdump, *original* stripped ARM64 ELF:
# 0xca2f04: legacy basic-info call
# 0xca2f08: if legacy return !=0, jump directly to epilogue with error
# 0xca313c: metadata failure -> return success, without writing new fields
# 0xca316c/70: only successful overlay stores FourCC/modifier
ORIGINAL_OPCODES = {
    0xCA2F04: 0x97FFFB1E,  # bl 0xca1b7c
    0xCA2F08: 0x350011C0,  # cbnz w0, 0xca3140
    0xCA2F1C: 0x528000E1,  # mov w1, #7 (FourCC)
    0xCA3034: 0x52800101,  # mov w1, #8 (modifier)
    0xCA313C: 0x2A1F03E0,  # mov w0, wzr
    0xCA316C: 0xB90002F9,  # str w25, [x23]
    0xCA3170: 0xF90006E8,  # str x8, [x23,#8]
}

def elf_word_at_vaddr(buf: bytes, addr: int) -> int:
    if buf[:4] != b"\\x7fELF" or buf[4] != 2 or buf[5] != 1:
        raise AssertionError("Expected little-endian ELF64")
    phoff = struct.unpack_from("<Q", buf, 0x20)[0]
    phentsize, phnum = struct.unpack_from("<HH", buf, 0x36)
    for i in range(phnum):
        ph = phoff + i * phentsize
        ptype, _, offset, vaddr, _, filesz, _, _ = struct.unpack_from(
            "<IIQQQQQQ", buf, ph
        )
        if ptype == 1 and vaddr <= addr and addr + 4 <= vaddr + filesz:
            return struct.unpack_from("<I", buf, offset + addr - vaddr)[0]
    raise AssertionError(f"Cannot map executable address 0x{addr:x}")

def validate_original(path: Path) -> None:
    buf = path.read_bytes()
    actual_sha = hashlib.sha256(buf).hexdigest()
    assert actual_sha == ORIGINAL_SHA256, f"Wrong source ELF: {actual_sha}"
    for address, expected in ORIGINAL_OPCODES.items():
        actual = elf_word_at_vaddr(buf, address)
        assert actual == expected, (
            f"Original ELF mismatch at 0x{address:x}: "
            f"expected 0x{expected:08x}, got 0x{actual:08x}"
        )
    print(f"PASS original ELF: SHA256 and {len(ORIGINAL_OPCODES)} AArch64 opcodes")

def validate_patch(path: Path) -> None:
    tree = ast.parse(path.read_text())
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)]
    candidates = [n for n in assignments
                  if any(isinstance(t, ast.Name) and t.id == "AFTER_BASIC"
                         for t in n.targets)]
    assert len(candidates) == 1, "Expected one source patch template"
    source = ast.literal_eval(candidates[0].value)
    prefix = source.split("   // Keep V38 IMapper5", 1)[0]
    assert prefix.count("gr->gamehub_legacy->ops.get_buffer_basic_info") == 1
    failure = prefix.index("if (ret != 0)\n         return ret;")
    inherited = prefix.index("*out = inherited;")
    metadata = prefix.index("if (got_metadata) {")
    complete = prefix.index("return 0;\n   }", metadata)
    assert failure < inherited < metadata < complete
    assert "get_fourcc_from_hal_format" not in prefix
    assert "*out = inherited;" not in prefix[metadata:]
    assert prefix.count("out->drm_fourcc = mapped_fourcc;") == 1
    assert prefix.count("out->modifier = mapped_modifier;") == 1
    assert "if (!gr->mapper)\n      return -EINVAL;" in source
    print("PASS template: legacy result retained, error propagated, overlay only on metadata success")

if __name__ == "__main__":
    source = Path(__file__).with_name("apply_gamehub_gralloc_metadata_parity.py")
    validate_patch(source)
    if len(sys.argv) == 2:
        validate_original(Path(sys.argv[1]))
    elif len(sys.argv) != 1:
        raise SystemExit("usage: verify_gamehub_gralloc_result_semantics.py [original.so]")
