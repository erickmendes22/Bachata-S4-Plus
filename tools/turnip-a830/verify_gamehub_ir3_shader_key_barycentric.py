#!/usr/bin/env python3
"""Validate executable GameHub IR3 barycentric + shader key differences.

Compare the original and functional DD ELF against the broken R11 compiled ELF,
using exact SHA256 and AArch64 machine words, not strings or C++ guesses.
The driver cannot be called equivalent without shader input/output comparison.
"""
import argparse,hashlib,json,struct
from pathlib import Path
EXPECTED={
  "gamehub":"1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404",
  "dd":"4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9",
  "r11":"ba10389c1b22cb74eda7e094693a14d7f270d26bc92b408d3964cc5f7d68f322",
}
# VA -> instruction word. Anchors are ELF-original and its matching DD fork.
ORIGINAL={
  0xac5ccc:0x52800f02, # mov w2, #120; complete shader key memcmp
  0xac5cf0:0x39410ea9, # ldrb w9, [variant,#0x43]; key[0x2b]
  0xade7d8:0x39410d09, # ldrb w9, [variant,#0x43]
  0xade7e8:0x7100093f, # cmp w9,#2
  0xade7f4:0x7100053f, # cmp w9,#1
  0xade8b8:0x52802001, # mov w1, #0x100 (IR3 ADD_F)
}
R11={
  0xa25c50:0x52800a02, # mov w2,#80
  0xa25cd0:0x52800a02, # mov w2,#80 (second equality test)
}

def vword(buf,addr):
    if buf[:4]!=b"\x7fELF" or buf[4]!=2 or buf[5]!=1:
        raise AssertionError("Expected AArch64 little endian ELF64")
    phoff=struct.unpack_from("<Q",buf,0x20)[0]
    phentsize,phnum=struct.unpack_from("<HH",buf,0x36)
    for n in range(phnum):
        ty,flags,off,va,paddr,fsz,msz,align=struct.unpack_from(
            "<IIQQQQQQ",buf,phoff+phentsize*n)
        if ty==1 and va<=addr and addr+4<=va+fsz:
            return struct.unpack_from("<I",buf,off+addr-va)[0]
    raise AssertionError(f"address 0x{addr:x} not in a LOAD segment")

def check(path,key,expect):
    b=Path(path).read_bytes()
    actual=hashlib.sha256(b).hexdigest()
    assert actual==EXPECTED[key],f"wrong {key} ELF: {actual}"
    for addr,value in expect.items():
        got=vword(b,addr)
        assert got==value,f"{key} at {addr:#x} != {value:08x}: {got:08x}"
    return len(expect)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gamehub",required=True,type=Path)
    p.add_argument("--gamehub-dd",required=True,type=Path)
    p.add_argument("--r11",required=True,type=Path)
    a=p.parse_args()
    n=check(a.gamehub,"gamehub",ORIGINAL)
    m=check(a.gamehub_dd,"dd",ORIGINAL)
    k=check(a.r11,"r11",R11)
    out={
       "original_and_gamehub_dd_shader_key_bytes":120,
       "r11_shader_key_bytes":80,
       "original_and_dd_key_mode_byte_offset":0x2b,
       "original_ir3_case":{"mode_1":"constant (1,0,0)",
                             "mode_2":"line weights (1 - (I+J), I+J, 0)",
                             "other":"three native IR3 input slots 0x100..0x102"},
       "exact_aarch64_words_verified":{"gamehub":n,"gamehub_dd":m,"r11":k},
       "not_verified":["field mode source in Vulkan graphics pipeline",
                       "whether SotC actual shaders execute this intrinsic",
                       "generated Adreno shader bytes",
                       "visual correctness of patched driver"],
    }
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
