#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Capture an already-rejected shader; never suppress its native assertion."""
import struct,hashlib,argparse
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
SITE=0x10c1dbc
CAVE=0x3e84400
DLSYM=0x6c91a0

def patch(source,dest):
 original=Path(source).read_bytes();data=bytearray(original)
 assert data[SITE:SITE+4]==struct.pack('<I',0x528000a8),"Unexpected shader-failure instruction"
 with Path(source).open('rb') as f:
  elf=ELFFile(f);assert elf['e_machine']=='EM_AARCH64'
  assert any(s['p_type']=='PT_LOAD' and s['p_flags']&1 and s['p_vaddr']<=CAVE and CAVE+512<s['p_vaddr']+s['p_filesz'] and s['p_offset']==s['p_vaddr'] for s in elf.iter_segments())
 k=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
 a='sub sp,sp,#320;'
 for i in range(0,18,2):a+=f'stp x{i},x{i+1},[sp,#{i*8}];'
 a+='stp x18,x30,[sp,#144];mrs x18,nzcv;str x18,[sp,#160];'
 for i in range(0,8,2):a+=f'stp q{i},q{i+1},[sp,#{176+i*16}];'
 a+=f'mov x0,xzr;adr x1,symbol;bl {DLSYM};cbz x0,restore;mov x16,x0;ldr x0,[sp];blr x16;restore:'
 for i in range(0,8,2):a+=f'ldp q{i},q{i+1},[sp,#{176+i*16}];'
 a+='ldr x18,[sp,#160];msr nzcv,x18;'
 for i in range(0,18,2):a+=f'ldp x{i},x{i+1},[sp,#{i*8}];'
 a+='ldp x18,x30,[sp,#144];add sp,sp,#320;mov w8,#5;ret;symbol: .asciz "bs4_fsr31_shader_rejected"'
 blob=bytes(k.asm(a,addr=CAVE)[0]);assert len(blob)<512 and not any(data[CAVE:CAVE+len(blob)])
 data[CAVE:CAVE+len(blob)]=blob;data[SITE:SITE+4]=bytes(k.asm(f'bl {CAVE}',addr=SITE)[0])
 assert data[0x3e82000:0x3e84300]==original[0x3e82000:0x3e84300]
 Path(dest).write_bytes(data);return hashlib.sha256(data).hexdigest()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('dest');a=p.parse_args();print(patch(a.source,a.dest))
