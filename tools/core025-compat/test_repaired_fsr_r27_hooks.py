#!/usr/bin/env python3
"""Execute shipped/repaired ARM64 wrappers, not a rewritten callback model.

Only getenv, dlsym, SDK callbacks and native callees are modeled. Native
constructor/render calls record exact arguments. Not guest gameplay validation.
"""
import json,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
from repair_fsr_r27_hooks import ATTACH_SITE,RENDER_SITE,PIPELINE_SITE,GETENV,DLSYM

data=Path(sys.argv[1]).read_bytes();old=Path(sys.argv[2]).read_bytes();cases=0
# Negative control: execute the actual shipped constructor call with attach
# returning -2. Its caller receives that error instead of the native return.
for bias in [0,0x7000000000]:
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(bias,0x4800000);u.mem_write(bias,old)
 u.mem_map(0x22000000,0x200000);u.reg_write(UC_ARM64_REG_SP,0x22100000)
 u.reg_write(UC_ARM64_REG_LR,0x2200a000)
 observed=[]
 def control(uc,pc,size,_):
  if pc==bias+0x130b57c:
   uc.reg_write(UC_ARM64_REG_X0,0x456);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
  elif pc==bias+DLSYM:
   observed.append('sdk_lookup');uc.reg_write(UC_ARM64_REG_X0,0x22009000);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
  elif pc==0x22009000:
   observed.append('sdk_callback');uc.reg_write(UC_ARM64_REG_X0,(-2)&((1<<64)-1));uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
  elif pc==bias+ATTACH_SITE+4:uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,control);u.emu_start(bias+ATTACH_SITE,0,count=1000)
 assert observed==['sdk_lookup','sdk_callback']
 assert u.reg_read(UC_ARM64_REG_X0)==((-2)&((1<<64)-1))
for bias in [0,0x7000000000]:
 for site in [ATTACH_SITE,RENDER_SITE,PIPELINE_SITE]:
  for mode in [None,'','-1','0','1','2','3','4','5','10','false']:
   for outcome in ['absent','declined','active']:
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(bias,0x4800000);u.mem_write(bias,data)
    stack=0x22100000;env=0x22008000;callback=0x22009000
    u.mem_map(0x22000000,0x200000)
    # Every register is hostile after external calls. Full-width Q arguments
    # and x8 (indirect result), x18 are included, unlike the earlier tests.
    regs=[UC_ARM64_REG_X0+i for i in range(19)]
    qs=[UC_ARM64_REG_Q0+i for i in range(8)]
    gp=[0x33000000+i for i in range(19)]
    qp=[0x123456789abcdef00112233445566000+i for i in range(8)]
    for r,v in zip(regs,gp):u.reg_write(r,v)
    for r,v in zip(qs,qp):u.reg_write(r,v)
    u.reg_write(UC_ARM64_REG_SP,stack);u.reg_write(UC_ARM64_REG_LR,0x2200a000)
    calls=[];lookups=[];native=[]
    enabled=mode in ['0','1','2','3','4']
    def clobber():
     for i,r in enumerate(regs):u.reg_write(r,0xdead0000+i)
     for r in qs:u.reg_write(r,(1<<128)-1)
    def ret():u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
    def hook(uc,pc,size,_):
     if pc==bias+GETENV:
      assert bytes(uc.mem_read(uc.reg_read(UC_ARM64_REG_X0),19))==b'BACHATA_FSR31_MODE\0'
      clobber()
      if mode is None:uc.reg_write(UC_ARM64_REG_X0,0)
      else:uc.mem_write(env,mode.encode()+b'\0');uc.reg_write(UC_ARM64_REG_X0,env)
      ret()
     elif pc==bias+DLSYM:
      lookups.append(1);assert enabled
      clobber();uc.reg_write(UC_ARM64_REG_X0,0 if outcome=='absent' else callback);ret()
     elif pc==callback:
      assert enabled;calls.append(1)
      if site==ATTACH_SITE:assert [uc.reg_read(r) for r in regs[:5]]==[gp[0],gp[1],gp[3],gp[4],gp[5]]
      elif site==RENDER_SITE:
       assert [uc.reg_read(r) for r in regs[:9]]==gp[:9]
       assert [uc.reg_read(r) for r in qs]==qp
      else:assert uc.reg_read(UC_ARM64_REG_X0)==gp[0]
      clobber();uc.reg_write(UC_ARM64_REG_X0,(-2 & ((1<<64)-1)) if site==ATTACH_SITE else (0xabc if outcome=='active' else 0));ret()
     elif pc in [bias+0x130b57c,bias+0x130f524]:
      native.append(pc)
      assert [uc.reg_read(r) for r in regs[:9]]==gp[:9]
      assert uc.reg_read(UC_ARM64_REG_X18)==gp[18]
      assert [uc.reg_read(r) for r in qs]==qp
      clobber();uc.reg_write(UC_ARM64_REG_X0,0x456);ret()
     elif pc==bias+PIPELINE_SITE+4 and site==PIPELINE_SITE:
      assert [uc.reg_read(r) for r in regs[:9]]==gp[:9]
      assert uc.reg_read(UC_ARM64_REG_X18)==gp[18]
      assert [uc.reg_read(r) for r in qs]==qp
      assert uc.reg_read(UC_ARM64_REG_SP)==stack-96
      uc.emu_stop()
     elif pc==bias+site+4 and site!=PIPELINE_SITE:
      assert uc.reg_read(UC_ARM64_REG_SP)==stack
      expected=0xabc if site==RENDER_SITE and enabled and outcome=='active' else 0x456
      assert uc.reg_read(UC_ARM64_REG_X0)==expected
      uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(bias+site,0,count=1000)
    assert len(lookups)==int(enabled)
    assert len(calls)==int(enabled and outcome!='absent')
    if site==ATTACH_SITE:assert len(native)==1
    elif site==RENDER_SITE:assert len(native)==int(not(enabled and outcome=='active'))
    assert u.reg_read(UC_ARM64_REG_PC)==bias+site+4
    cases+=1
print(json.dumps({'arm64Cases':cases,'disabledSkipsSDKLookupAndCallback':True,
 'nativeCallArgumentsSIMDAndStackPreserved':True,
 'constructorReturnPreservedOnAttachFailure':True,
 'shippedConstructorReturnLossReproduced':True,
 'PIEBiases':['0','0x7000000000'],'guestHeapPanicValidated':False}))
