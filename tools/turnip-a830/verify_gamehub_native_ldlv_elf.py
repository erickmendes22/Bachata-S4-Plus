#!/usr/bin/env python3
"""Verify exact machine instructions for GameHub's native PerVertexKHR fetch.

This is solely machine-code anchoring, not proof of GPU image correctness.
Same fragment IR3 instruction sequence is in both *functional* GameHub ELFs.
"""
import argparse,hashlib,json,struct
from pathlib import Path
ELFS={
"original":"1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404",
"dd":"4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9",
}
OPS={
0xad70cc:0x92400108, # and x8,x8,#1
0xad70d4:0x92403d08, # and x8,x8,#0xffff
0xad70dc:0x39410d29, # mode = uint8_t(variant[0x43])
0xad70e0:0x51000529, # mode - 1
0xad70e4:0x6b09011f, # compare requested vertex
0xad70e8:0x1a893108, # clamp to mode-1 (unsigned)
0xad71c8:0x528063e1, # mov w1,#0x31f : native OPC_LDLV
0xad7354:0x528063e1, # mov w1,#0x31f : native OPC_LDLV
}
def read_word(b,addr):
    assert b[:4]==b"\x7fELF" and b[4]==2 and b[5]==1
    phoff=struct.unpack_from("<Q",b,0x20)[0]
    ent,n=struct.unpack_from("<HH",b,0x36)
    for i in range(n):
        typ,flags,offset,va,paddr,filesz,memsz,align=struct.unpack_from(
            "<IIQQQQQQ",b,phoff+i*ent)
        if typ==1 and va<=addr and addr+4<=va+filesz:
            return struct.unpack_from("<I",b,offset+addr-va)[0]
    raise AssertionError("Unmapped address: "+hex(addr))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("original",type=Path)
    p.add_argument("dd",type=Path)
    a=p.parse_args()
    for label,path in [("original",a.original),("dd",a.dd)]:
        b=path.read_bytes()
        assert hashlib.sha256(b).hexdigest()==ELFS[label]
        for addr,expected in OPS.items():
            actual=read_word(b,addr)
            assert actual==expected,(label,hex(addr),hex(expected),hex(actual))
    print(json.dumps({
      "verified_words_per_ELF":len(OPS),
      "working_gamehub_versions":"identical IR3 native PerVertexKHR opcodes",
      "per_vertex_opcode":"OPC_LDLV=0x31f",
      "primitive_mode_source":"variant+0x43",
      "dynamic_vertex_clamp":"unsigned min(index, mode-1)",
      "unresolved":"exact pipeline write of variant+0x43 and GPU shader output equality"
    },indent=2))
if __name__=="__main__":main()
