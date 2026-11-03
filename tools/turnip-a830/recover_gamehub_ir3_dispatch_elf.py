#!/usr/bin/env python3
"""Reconstruct *executable* IR3 NIR-intrinsic dispatch from GameHub original.

Unlike comparing names, this reads the actual AArch64 switch jump table
at 0x122236: case ID (u16 offset) -> 0xAD42B0 + offset*4.
Input MUST have the original exact ELF SHA. All addresses are VAs/offsets
for that exact stripped ELF with load bias 0; no gadget approximation.
This only reconstructs dispatch and requires further semantic lowering work.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct

ORIGINAL_SHA = "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404"
MIN_CASE = 0x26
TABLE_VA = 0x122236
PC_BASE = 0xAD42B0
CASES = {
    "ddx_3d_ir3": (114, 0xAD4A2C),
    "ddy_3d_ir3": (118, 0xAD4A2C),
    "load_barycentric_coord_ir3": (301, 0xAD60CC),
    "load_frag_coord_gmem_ir3": (384, 0xAD7648),
    "load_sample_pos_from_id_ir3": (601, 0xAD47DC),
    "select_barycentric_at_center_ir3": (824, 0xAD5A9C),
}
ELF_SECTION_BYTES = 136

def sections(buf):
    so = struct.unpack_from("<Q", buf, 0x28)[0]
    ent, count, namesection = struct.unpack_from("<HHH",buf,0x3a)
    t=[struct.unpack_from("<IIQQQQIIQQ",buf,so+ent*i) for i in range(count)]
    n=t[namesection]
    string_table=buf[n[4]:n[4]+n[5]]
    return {string_table[x[0]:].split(b"\0",1)[0].decode(): x for x in t}

def names_from_exact_elf(b):
    secs=sections(b);r=secs[".rodata"];d=secs[".data.rel.ro"]
    def one(off):
        if not d[4]<=off<=d[4]+d[5]-8:return None
        p=struct.unpack_from("<Q",b,off)[0]
        if not r[3]<=p<r[3]+r[5]:return None
        raw=b[r[4]+p-r[3]:r[4]+p-r[3]+96].split(b"\0",1)[0]
        if not 3<=len(raw)<=95 or not all(32<=v<127 for v in raw):return None
        return raw.decode()
    needle=b.find(b"ddx\0",r[4],r[4]+r[5])
    assert needle>=0
    name_va=r[3]+needle-r[4]
    q=b.find(struct.pack("<Q",name_va),d[4],d[4]+d[5])
    assert q>=0
    while one(q-ELF_SECTION_BYTES) and one(q-ELF_SECTION_BYTES)<one(q):
        q-=ELF_SECTION_BYTES
    result=[]
    while one(q) and (not result or one(q)>result[-1]):
        result.append(one(q))
        q+=ELF_SECTION_BYTES
    assert len(result)==958
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("gamehub_original",type=Path)
    p=parser.parse_args()
    b=p.gamehub_original.read_bytes()
    assert hashlib.sha256(b).hexdigest()==ORIGINAL_SHA
    all_names=names_from_exact_elf(b)
    result={}
    for name,(expected_id,expected_handler) in CASES.items():
        id=all_names.index(name)
        assert id==expected_id,(name,id)
        delta=struct.unpack_from("<H",b,TABLE_VA+2*(id-MIN_CASE))[0]
        handler=PC_BASE+4*delta
        assert handler==expected_handler,(name,hex(handler))
        result[name]={"nir_intrinsic_enum":id,"handler_va":hex(handler),
                      "goes_to_unhandled_intrinsic":handler==0xAD7648}
    assert result["ddx_3d_ir3"]["handler_va"]==result["ddy_3d_ir3"]["handler_va"]
    assert result["load_sample_pos_from_id_ir3"]["handler_va"]=="0xad47dc"
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
