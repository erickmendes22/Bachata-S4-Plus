#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
import sys,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from patch_core025 import *
b=Path(sys.argv[1]).read_bytes()
args=[0x100+i*0x100 for i in range(8)];regs=[UC_ARM64_REG_X0+i for i in range(8)]
def run(entry,lookup=True,sdk_result=0xabc):
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(0,0x4400000);u.mem_write(0,b[:0x435f6a4]);u.mem_map(0x6ff0000,0x10000);u.mem_map(0x7000000,0x20000);u.reg_write(UC_ARM64_REG_SP,0x7010000);u.reg_write(UC_ARM64_REG_LR,0x6fff000);calls=[]
 for r,a in zip(regs,args):u.reg_write(r,a)
 def cb(uc,pc,size,_):
  if pc==0x6fff000:uc.emu_stop();return
  if pc==DLSYM:
   pointer=uc.reg_read(UC_ARM64_REG_X1);name=bytes(uc.mem_read(pointer,32)).split(b'\0')[0].decode();calls.append(('dlsym',name));uc.reg_write(UC_ARM64_REG_X0,0x6fff100 if lookup else 0);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
  elif pc in [CREATE,RENDER,0x6fff100]:
   calls.append((pc,[uc.reg_read(r) for r in regs]));uc.reg_write(UC_ARM64_REG_X0,sdk_result if pc==0x6fff100 else 0xf00);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
 u.hook_add(UC_HOOK_CODE,cb);u.emu_start(entry,0,count=500)
 assert u.reg_read(UC_ARM64_REG_SP)==0x7010000
 return calls,u.reg_read(UC_ARM64_REG_X0)
c,result=run(RENDER_HOOK);assert result==0xabc and not any(x[0]==RENDER for x in c);assert next(x[1] for x in c if x[0]==0x6fff100)[:7]==args[:7]
for lookup,sdk in [(False,0),(True,0)]:
 c,result=run(RENDER_HOOK,lookup,sdk);assert result==0xf00;assert next(x[1] for x in c if x[0]==RENDER)[:7]==args[:7]
c,result=run(CREATE_HOOK);assert c[0][0]==CREATE;expected=[args[0],args[1],args[3],args[4],args[5]];assert next(x[1] for x in c if x[0]==0x6fff100)[:5]==expected
assert bl_target(b,CREATE_CALL)==CREATE_HOOK and bl_target(b,RENDER_CALL)==RENDER_HOOK
print('PASS: actual ARM64 hooks execute SDK/FSR1 paths, preserve every argument and stack, call native constructor first and attach exact 025 device ABI')
