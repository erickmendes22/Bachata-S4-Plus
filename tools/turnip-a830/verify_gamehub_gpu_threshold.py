#!/usr/bin/env python3
"""ELF-level A8xx primitive threshold verifier. Never rely on strings alone."""
import hashlib
from pathlib import Path
import struct,sys

ORIGINAL_SHA="1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404"
CHIP_IDS=(0xffff44010000,0xffff44050000,0xffff44050001,0x44050001,0x44030a20,0xffff44050a31)

def records(data):
    # Relocated .data.rel.ro descriptor records are {chip_id, name VA,
    # fd_dev_info VA, flags}. We require an actual Adreno string and A8XX chip.
    for off in range(0,len(data)-32,8):
        chip,name,info,flags=struct.unpack_from("<QQQQ",data,off)
        if chip not in CHIP_IDS:
            continue
        if not 0<name<len(data)-80 or not 0<info<len(data)-0x330:
            continue
        if not data[name:name+7]==b"Adreno " or data[info]!=8:
            continue
        value=data[info+0x2a8:info+0x2ac]
        yield chip,name,info,struct.unpack("<I",value)[0]

def check_gamehub(file):
    data=Path(file).read_bytes()
    assert hashlib.sha256(data).hexdigest()==ORIGINAL_SHA, "Not original GameHub"
    found={}
    for chip,name,info,threshold in records(data):
        # Extra 12 bytes before GPUProps in GameHub vs pinned V38.
        value=struct.unpack_from("<I",data,info+0x2b4)[0]
        found[chip]=value
        assert value==0xF,(hex(chip),value)
    assert {0xffff44050000,0xffff44050001,0x44050001}.issubset(found)
    print("PASS exact GameHub A830 primitives=15:",len(found),"A8xx IDs")

def check_v38(file):
    data=Path(file).read_bytes()
    found={}
    for chip,name,info,threshold in records(data):
        found[chip]=threshold
        assert threshold==0xF,(hex(chip),threshold)
    assert {0xffff44050000,0xffff44050001,0x44050001}.issubset(found),found
    print("PASS rebuilt V38 A830 primitives=15:",len(found),"A8xx IDs")
if __name__=="__main__":
    mode,path=sys.argv[1:]
    (check_gamehub if mode=="gamehub" else check_v38)(path)
