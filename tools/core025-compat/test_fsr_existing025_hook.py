#!/usr/bin/env python3
import sys,json
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from hook_fsr_existing025 import SITE,ORIGINAL,CAVE,SYMBOL
b=Path(sys.argv[1]).read_bytes();checks=0
for bias in [0,0x7000000000]:
 for kind in ['absent','declined','recorded']:
  u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
  for base in [SITE&~4095,ORIGINAL&~4095,CAVE&~4095,0x6c9000,0x5000000,0x800000]:u.mem_map(bias+base,4096)
  u.mem_write(bias+SITE,b[SITE:SITE+4]);u.mem_write(bias+CAVE,b[CAVE:CAVE+0x1c0]);u.mem_write(bias+0x5000000,b'\xc0\x03\x5f\xd6')
  original=[0x12121212+n for n in range(8)];stack=bias+0x800f00;end=bias+0x5000100
  u.reg_write(UC_ARM64_REG_SP,stack);u.reg_write(UC_ARM64_REG_X30,end)
  regs=[UC_ARM64_REG_X0+n for n in range(8)];qs=[UC_ARM64_REG_Q0+n for n in range(8)]
  for n,r in enumerate(regs):u.reg_write(r,original[n])
  for n,r in enumerate(qs):u.reg_write(r,0x11223344556677889900112233445500+n)
  called=[]
  def clobber():
   for n,r in enumerate(regs):u.reg_write(r,0xdead0000+n)
   for r in qs:u.reg_write(r,0)
  def hook(uc,pc,size,user):
   if pc==bias+0x6c91a0:
    assert uc.reg_read(UC_ARM64_REG_X0)==0
    p=uc.reg_read(UC_ARM64_REG_X1);assert bytes(uc.mem_read(p,21))==b'bs4_fsr31_try_render\0'
    clobber();uc.reg_write(UC_ARM64_REG_X0,0 if kind=='absent' else bias+0x5000000);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
   elif pc==bias+0x5000000:
    assert [uc.reg_read(r) for r in regs]==original
    called.append('sdk');clobber();uc.reg_write(UC_ARM64_REG_X0,0xabc if kind=='recorded' else 0);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
   elif pc==bias+ORIGINAL:
    assert [uc.reg_read(r) for r in regs]==original
    assert [uc.reg_read(r) for r in qs]==[0x11223344556677889900112233445500+n for n in range(8)]
    called.append('original');uc.reg_write(UC_ARM64_REG_X0,0x456);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
   elif pc==bias+SITE+4:uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(bias+SITE,end,count=300)
  assert called==({'absent':['original'],'declined':['sdk','original'],'recorded':['sdk']}[kind])
  assert u.reg_read(UC_ARM64_REG_X0)==(0xabc if kind=='recorded' else 0x456)
  assert u.reg_read(UC_ARM64_REG_SP)==stack and u.reg_read(UC_ARM64_REG_X30)==bias+SITE+4
  checks+=1
print(json.dumps({'cases':checks,'sdkAbsentOrDeclinedPreservesOriginal':True,'SDKResultForwarded':True,'PIEBiases':[0,hex(0x7000000000)],'nativeCoreCompiled':False},indent=2))
