#!/usr/bin/env python3
"""Cross-check recovered renderpass conditions against original GameHub ELF.

Original libvulkan_freedreno.so, 14,257,760 bytes (NOT GameHub+DD variant).
Use the user's own extracted library as arg 1; never supply a guessed blob.
"""
from pathlib import Path
import hashlib,struct,sys
SHA="1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404"
def verify(filename):
    data=Path(filename).read_bytes()
    if len(data)!=14257760 or hashlib.sha256(data).hexdigest()!=SHA:
        raise ValueError("Not the original exact GameHub A830 ELF")
    for off,chip,name in [
        (0xd744d8,0xffff44050000,b"Adreno (TM) 830"),
        (0xd744f8,0xffff44050001,b"Adreno (TM) 830v1"),
        (0xd74518,0x44050001,b"Adreno (TM) 830"),
    ]:
        got,name_va,info_va,_=struct.unpack_from("<QQQQ",data,off)
        assert got==chip and data[name_va:name_va+len(name)+1]==name+b"\0"
        assert info_va==0x8946e4
        assert data[info_va]==8
        assert data[info_va+0x30a]==1
        assert data[info_va+0x30b]==1
        print(f"PASS GameHub {name.decode()}: {chip:#x}; quirks +30a=1 +30b=1")
    for va,reason in [
        (0x75c14,b"8x MSAA attachment format requires sysmem on A8xx"),
        (0xa87c1,b"multi-subpass MSAA without input attachments requires sysmem"),
    ]:
        assert data[va:va+len(reason)+1]==reason+b"\0"
    # .text PT_LOAD: VA - file offset = 0x4000. Validate actual opcodes.
    for va,insn in [
        (0x96539c,0xa9bb7bfd), # function entry
        (0x9653d8,0x7100213f), # A8xx generation >= 8
        (0x965424,0xb9400508), # attachment.samples
        (0x965428,0x7100211f), # cmp #8
        (0x965484,0x394c2949), # GPU feature +0x30a
        (0x965488,0x7100053f), # cmp #1
        (0x96577c,0x394c2d4a), # GPU feature +0x30b
        (0x965780,0x7100055f), # cmp #1
        (0x965874,0x710209df), # format == 130 (D32S8)
    ]:
        assert struct.unpack_from("<I",data,va-0x4000)[0]==insn,hex(va)
    print("PASS: source translation matches original ARM64 and device constants")
if __name__=="__main__":
    verify(sys.argv[1])
