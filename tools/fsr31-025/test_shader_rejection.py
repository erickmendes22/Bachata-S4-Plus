#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
import sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from patch_shader_rejection import SITE,DLSYM
b=Path(sys.argv[1]).read_bytes()
for present in [False,True]:
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(0,0x5000000);u.mem_write(0,b);u.mem_map(0x6ff0000,0x10000);u.mem_map(0x7000000,0x20000)
 u.reg_write(UC_ARM64_REG_SP,0x7010000);u.reg_write(UC_ARM64_REG_NZCV,0xa0000000)
 before={}
 for i in range(19):before[UC_ARM64_REG_X0+i]=0x1000+i;u.reg_write(UC_ARM64_REG_X0+i,0x1000+i)
 for i in range(8):before[UC_ARM64_REG_Q0+i]=((0xabc+i)<<64)|i;u.reg_write(UC_ARM64_REG_Q0+i,before[UC_ARM64_REG_Q0+i])
 calls=[]
 def hook(uc,pc,size,_):
  if pc==SITE+4:uc.emu_stop();return
  if pc==DLSYM:
   name=bytes(uc.mem_read(uc.reg_read(UC_ARM64_REG_X1),40)).split(b'\0')[0];assert name==b'bs4_fsr31_shader_rejected';assert uc.reg_read(UC_ARM64_REG_X0)==0
   uc.reg_write(UC_ARM64_REG_X0,0x6fff100 if present else 0);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR));return
  if pc==0x6fff100:
   calls.append(uc.reg_read(UC_ARM64_REG_X0));lr=uc.reg_read(UC_ARM64_REG_LR)
   for i in range(19):uc.reg_write(UC_ARM64_REG_X0+i,0xdead)
   for i in range(8):uc.reg_write(UC_ARM64_REG_Q0+i,0)
   uc.reg_write(UC_ARM64_REG_NZCV,0);uc.reg_write(UC_ARM64_REG_PC,lr)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(SITE,0,count=200)
 assert calls==([0x1000] if present else [])
 assert u.reg_read(UC_ARM64_REG_SP)==0x7010000 and u.reg_read(UC_ARM64_REG_NZCV)==0xa0000000
 for reg,value in before.items():assert u.reg_read(reg)==(5 if reg==UC_ARM64_REG_X8 else value),(present,reg)
print('PASS: rejected-shader hook preserves registers, vectors, flags and stack; original assertion path retained with SDK present/absent')
