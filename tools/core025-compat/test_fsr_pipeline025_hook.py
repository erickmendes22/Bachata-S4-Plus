#!/usr/bin/env python3
"""Execute the actual patched 025 draw entry, checking native ABI preservation."""
import json
import sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from hook_fsr_pipeline025 import ENTRY,CAVE,SYMBOL
b=Path(sys.argv[1]).read_bytes();cases=0
for bias in (0,0x7000000000):
 for present in (False,True):
  u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
  for base in (ENTRY&~4095,CAVE&~4095,0x6c9000,0x5000000,0x800000):u.mem_map(bias+base,4096)
  u.mem_write(bias+ENTRY,b[ENTRY:ENTRY+4]);u.mem_write(bias+CAVE,b[CAVE:CAVE+0x1c0])
  args=[0x10101010+n for n in range(8)];simd=[0xabcdef01234567890000000000000000+n for n in range(8)]
  regs=[UC_ARM64_REG_X0+n for n in range(8)];qs=[UC_ARM64_REG_Q0+n for n in range(8)]
  stack=bias+0x800f00;link=bias+0x5000200;calls=[]
  u.reg_write(UC_ARM64_REG_SP,stack);u.reg_write(UC_ARM64_REG_X29,0xbeef);u.reg_write(UC_ARM64_REG_X30,link)
  for r,v in zip(regs,args):u.reg_write(r,v)
  for r,v in zip(qs,simd):u.reg_write(r,v)
  def clobber(uc):
   for r in regs:uc.reg_write(r,0xdead)
   for r in qs:uc.reg_write(r,0)
  def run(uc,pc,size,user):
   if pc==bias+0x6c91a0:
    assert uc.reg_read(UC_ARM64_REG_X0)==0
    p=uc.reg_read(UC_ARM64_REG_X1);assert bytes(uc.mem_read(p,len(b'bs4_fsr31_native_pipeline\0')))==b'bs4_fsr31_native_pipeline\0'
    clobber(uc);uc.reg_write(UC_ARM64_REG_X0,bias+0x5000000 if present else 0)
    uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
   elif pc==bias+0x5000000:
    assert uc.reg_read(UC_ARM64_REG_X0)==args[0] 
    calls.append(True);clobber(uc)
    uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
   elif pc==bias+ENTRY+4:
    assert [uc.reg_read(r) for r in regs]==args
    assert [uc.reg_read(r) for r in qs]==simd
    assert uc.reg_read(UC_ARM64_REG_SP)==stack-96
    import struct
    assert struct.unpack('<QQ',uc.mem_read(stack-96,16))==(0xbeef,link)
    uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,run);u.emu_start(bias+ENTRY,link,count=300)
  assert calls==([True] if present else []);cases+=1
print(json.dumps({'cases':cases,'originalSchedulerArgumentsAndProloguePreserved':True,
                  'nativeVertexIdentityHookVerified':True,'nativeCoreCompiled':False},indent=2))
