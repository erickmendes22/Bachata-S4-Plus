#!/usr/bin/env python3
"""Attach RB override to the actual 025 Presenter, with its actual stack layout."""
import argparse,hashlib,json,struct
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile
ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
def asm(code,pc):return bytes(ks.asm(code,addr=pc)[0])
def patch(source,dest):
    original=Path(source).read_bytes();data=bytearray(original)
    assert hashlib.sha256(original).hexdigest()=='5e0670d761e96fc768b928cbd87e68943cd5204ff737d89ea1bbaee93160c510'
    assert original[0x12933e0:0x12933e4]==asm('ldr x0,[x20,#0x4948]',0x12933e0)
    assert original[0x12933d8:0x12933e0]==asm('str w8,[sp,#0x294];str w9,[sp,#0x29c]',0x12933d8)
    with open(source,'rb') as f:
        elf=ELFFile(f);rel=elf.get_section_by_name('.rela.plt');syms=elf.get_section(rel['sh_link']);plt=elf.get_section_by_name('.plt')
        assert any(syms.get_symbol(r['r_info_sym']).name=='getenv' and plt['sh_addr']+32+i*16==0x6cb060 for i,r in enumerate(rel.iter_relocations()))
    code=['sub sp,sp,#0x2b0']
    for i in range(0,18,2):code.append(f'stp x{i},x{i+1},[sp,#{i*8}]')
    code.append('stp x18,x30,[sp,#0x90]')
    for i in range(0,32,2):code.append(f'stp q{i},q{i+1},[sp,#{0xa0+i*16}]')
    adr_index=len(code)+2
    code+=['mrs x8,nzcv','str x8,[sp,#0x2a0]','nop','bl 0x6cb060',
           'cbz x0,restore','ldrb w8,[x0]','cbz w8,restore','cmp w8,#48','b.eq restore',
           'cmp w8,#102','b.eq restore','cmp w8,#70','b.eq restore',
           'mov w8,#5','str w8,[sp,#0x544]','mov w8,#3','str w8,[sp,#0x54c]',
           'restore:ldr x8,[sp,#0x2a0]','msr nzcv,x8']
    for i in range(0,32,2):code.append(f'ldp q{i},q{i+1},[sp,#{0xa0+i*16}]')
    for i in range(0,18,2):code.append(f'ldp x{i},x{i+1},[sp,#{i*8}]')
    code+=['ldp x18,x30,[sp,#0x90]','add sp,sp,#0x2b0','ldr x0,[x20,#0x4948]','b 0x12933e4']
    cave=0x3e84100;blob=bytearray(asm(';'.join(code),cave))
    delta=0x3e82f00-(cave+4*adr_index)
    assert -(1<<20)<=delta<(1<<20)
    struct.pack_into('<I',blob,4*adr_index,0x10000000|((delta&3)<<29)|(((delta>>2)&0x7ffff)<<5))
    assert len(blob)<0x200 and not any(original[cave:cave+len(blob)])
    data[cave:cave+len(blob)]=blob;data[0x12933e0:0x12933e4]=asm(f'b {cave}',0x12933e0)
    # Remove the old, disconnected copied wrapper with stale 024 destinations.
    data[0x3e82e00:0x3e82e30]=b'\0'*0x30
    assert data[0x3e82000:0x3e82e00]==original[0x3e82000:0x3e82e00]
    assert data[0x3e83e00:0x3e84100]==original[0x3e83e00:0x3e84100]
    Path(dest).write_bytes(data)
    return {'inputSha256':hashlib.sha256(original).hexdigest(),'outputSha256':hashlib.sha256(data).hexdigest(),'site':hex(0x12933e0),'cave':hex(cave),'getenv':hex(0x6cb060),'componentOffsets':['0x294','0x29c'],'oldDisconnectedWrapperRemoved':True,'callerGpSimdNzcvPreserved':True}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('dest');p.add_argument('report');a=p.parse_args();Path(a.report).write_text(json.dumps(patch(a.source,a.dest),indent=2)+'\n')
