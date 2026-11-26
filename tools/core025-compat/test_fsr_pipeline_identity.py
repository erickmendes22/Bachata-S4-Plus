#!/usr/bin/env python3
"""Verify vertex Info offsets by executing the original 025 debug-string loop.

Stop before formatting: verify exactly which native slot/hash/stage are passed
to the formatter, independently of our SDK adapter and debug-utils settings.
"""
import hashlib,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
b=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(b).hexdigest()=='373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59'
cases=0
for bias in (0,0x7000000000):
 for value in (0x34e8a281,0xa400228b,0x123456789abcdef0):
  u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
  for base,size in ((0x1278000,4096),(0x1264000,4096),(0x5000000,0x10000),(0x800000,4096)):
   u.mem_map(bias+base,size)
  u.mem_write(bias+0x127874c,b[0x127874c:0x127890c])
  pipeline,info,out=(bias+a for a in (0x5000000,0x5001000,0x5004000))
  u.mem_write(pipeline+0xa0,struct.pack('<Q',info))
  u.mem_write(info+0x1d38,struct.pack('<Q',value))
  u.mem_write(info+0x1d48,struct.pack('<I',3))
  u.reg_write(UC_ARM64_REG_X0,pipeline);u.reg_write(UC_ARM64_REG_X8,out)
  u.reg_write(UC_ARM64_REG_SP,bias+0x800f00);seen=[]
  def observe(uc,pc,size,user):
   if pc==bias+0x1264948:
    assert uc.reg_read(UC_ARM64_REG_X0)==3 and uc.reg_read(UC_ARM64_REG_X1)==value
    seen.append(True);uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,observe);u.emu_start(bias+0x127874c,bias+0x126494c,count=1000)
  assert seen==[True];cases+=1
print(json.dumps(dict(cases=cases,nativeVertexSlot='this+0xa0',infoHash='Info+0x1d38',
                     infoStage='Info+0x1d48',nativeCoreCompiled=False),indent=2))
