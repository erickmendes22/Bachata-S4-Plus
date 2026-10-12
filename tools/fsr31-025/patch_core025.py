#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Connect the existing 025 FsrPass to the SDK; never change core routing."""
import argparse,hashlib,struct,json
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
CREATE_CALL=0x128e79c
RENDER_CALL=0x1293b4c
CREATE=0x130b57c
RENDER=0x130f524
DLSYM=0x6c91a0
CREATE_HOOK=0x3e83e00
RENDER_HOOK=0x3e84000

def bl_target(data,pc):
 word=struct.unpack_from('<I',data,pc)[0]
 if word&0xfc000000!=0x94000000:raise ValueError('Expected BL')
 delta=word&0x3ffffff
 if delta&0x2000000:delta-=0x4000000
 return pc+delta*4

def patch(source,dest):
 original=Path(source).read_bytes();data=bytearray(original)
 with Path(source).open('rb') as f:
  elf=ELFFile(f)
  if elf['e_machine']!='EM_AARCH64':raise ValueError('Not ARM64')
  for address in [CREATE_HOOK,RENDER_HOOK]:
   assert any(s['p_type']=='PT_LOAD' and s['p_flags']&1 and s['p_vaddr']<=address and address+256<s['p_vaddr']+s['p_filesz'] and s['p_offset']==s['p_vaddr'] for s in elf.iter_segments())
  rel=elf.get_section_by_name('.rela.plt');syms=elf.get_section(rel['sh_link']);plt=elf.get_section_by_name('.plt')
  assert any(syms.get_symbol(r['r_info_sym']).name=='dlsym' and plt['sh_addr']+32+i*16==DLSYM for i,r in enumerate(rel.iter_relocations()))
 assert bl_target(data,CREATE_CALL)==CREATE
 assert bl_target(data,RENDER_CALL)==RENDER
 assert data[CREATE_CALL-20:CREATE_CALL-16].hex()=='60a23c91' # add x0,x19,#0xf28
 assert data[RENDER_CALL-8:RENDER_CALL-4].hex()=='80a23c91' # add x0,x20,#0xf28
 asm=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
 def write(pc,code,symbol=None):
  if symbol:code+=';symbol: .asciz "'+symbol+'"'
  encoded=bytes(asm.asm(code,addr=pc)[0]);assert len(encoded)<256
  assert not any(data[pc:pc+len(encoded)]),'Occupied cave'
  data[pc:pc+len(encoded)]=encoded
 # Native constructor always runs first; original loader/driver ownership stays intact.
 write(CREATE_HOOK,f'''stp x29,x30,[sp,#-112]!;mov x29,sp;
 stp x0,x1,[sp,#16];stp x2,x3,[sp,#32];stp x4,x5,[sp,#48];
 bl {CREATE};mov x0,xzr;adr x1,symbol;bl {DLSYM};cbz x0,no_attach;
 mov x16,x0;ldp x0,x1,[sp,#16];ldr x2,[sp,#40];ldr x3,[sp,#48];ldr w4,[sp,#56];blr x16;
 no_attach:ldp x29,x30,[sp],#112;ret''','bs4_fsr31_attach')
 # SDK returns zero unless it owns a completed temporal/UI frame. Preserve
 # the original FSR1 call and all integer arguments on every rejection.
 write(RENDER_HOOK,f'''stp x29,x30,[sp,#-112]!;mov x29,sp;
 stp x0,x1,[sp,#16];stp x2,x3,[sp,#32];stp x4,x5,[sp,#48];stp x6,x7,[sp,#64];
 mov x0,xzr;adr x1,symbol;bl {DLSYM};cbz x0,original;
 mov x16,x0;ldp x0,x1,[sp,#16];ldp x2,x3,[sp,#32];ldp x4,x5,[sp,#48];ldr x6,[sp,#64];blr x16;cbnz x0,done;
 original:ldp x0,x1,[sp,#16];ldp x2,x3,[sp,#32];ldp x4,x5,[sp,#48];ldr x6,[sp,#64];bl {RENDER};
 done:ldp x29,x30,[sp],#112;ret''','bs4_fsr31_try_render')
 for at,target in [(CREATE_CALL,CREATE_HOOK),(RENDER_CALL,RENDER_HOOK)]:data[at:at+4]=bytes(asm.asm(f'bl {target}',addr=at)[0])
 # First/Second Son controls already occupy the lower cave. Protect them.
 assert data[0x3e82000:0x3e83d00]==original[0x3e82000:0x3e83d00]
 Path(dest).write_bytes(data)
 return {'source_sha256':hashlib.sha256(original).hexdigest(),'patched_sha256':hashlib.sha256(data).hexdigest(),'constructor_call':hex(CREATE_CALL),'presenter_call':hex(RENDER_CALL),'native_controls_preserved':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('dest');a=p.parse_args();print(json.dumps(patch(a.source,a.dest),indent=2))
