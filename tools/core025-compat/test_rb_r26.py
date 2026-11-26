#!/usr/bin/env python3
"""Execute real 025 stage classification and RB hook; model only libc getenv."""
import struct,json,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
data=Path(sys.argv[1]).read_bytes();old=Path(sys.argv[2]).read_bytes();n=0
for bias in [0,0x7000000000]:
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(bias,0x4800000);u.mem_write(bias,data)
    u.mem_map(0x20000000,0x200000);u.mem_map(0x22000000,0x200000)
    sp=0x22100000;ctx=0x20000000;env=0x20018000;stops=set();setting=None
    def code(uc,pc,size,_):
        if pc in stops:uc.emu_stop()
        elif pc==bias+0x6cb060:
            p=uc.reg_read(UC_ARM64_REG_X0);assert bytes(uc.mem_read(p,19))==b'BACHATA_RB_SWIZZLE\0'
            for i in range(19):uc.reg_write(UC_ARM64_REG_X0+i,0x88770000+i)
            for i in range(32):uc.reg_write(UC_ARM64_REG_Q0+i,(1<<128)-1)
            uc.reg_write(UC_ARM64_REG_NZCV,0x60000000)
            if setting is None:uc.reg_write(UC_ARM64_REG_X0,0)
            else:uc.mem_write(env,setting.encode()+b'\0');uc.reg_write(UC_ARM64_REG_X0,env)
            uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
    u.hook_add(UC_HOOK_CODE,code)
    for stage,endpoint in [(0,0x1262270),(0x45,0x126207c),(0x145,0x126207c),(0xad,0x12622f0),(0xb0,0x12621cc),(0x146,0x1262890)]:
        u.reg_write(UC_ARM64_REG_X21,ctx);u.mem_write(ctx+0x114,struct.pack('<I',stage));stops.clear();stops.update(bias+x for x in [0x1262270,0x126207c,0x12622f0,0x12621cc,0x1262890])
        u.emu_start(bias+0x1262064,0,count=1000);assert u.reg_read(UC_ARM64_REG_PC)==bias+endpoint;n+=1
    # Negative control is the exact core in the FSR R25 matching the diagnostic.
    u.mem_write(bias+0x1262064,old[0x1262064:0x1262068]);u.ctl_remove_cache(bias+0x1262064,bias+0x1262068);u.reg_write(UC_ARM64_REG_X21,ctx);u.mem_write(ctx+0x114,struct.pack('<I',325))
    u.emu_start(bias+0x1262064,0,count=1000);assert u.reg_read(UC_ARM64_REG_PC)==bias+0x1262890;n+=1
    u.mem_write(bias+0x1262064,data[0x1262064:0x1262068]);u.ctl_remove_cache(bias+0x1262064,bias+0x1262068)
    for setting in [None,'','0','false','False','1','true']:
        for initial in [(3,5),(5,3)]:
            for i in range(29):u.reg_write(UC_ARM64_REG_X0+i,0x33000000+i)
            u.reg_write(UC_ARM64_REG_X20,ctx);u.mem_write(ctx+0x4948,struct.pack('<Q',0x20008000))
            u.reg_write(UC_ARM64_REG_LR,0x22000080);u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_NZCV,0xa0000000)
            for i in range(32):u.reg_write(UC_ARM64_REG_Q0+i,(i+1)*0x123456789abcdef)
            before=[u.reg_read(UC_ARM64_REG_X0+i) for i in range(29)];q=[u.reg_read(UC_ARM64_REG_Q0+i) for i in range(32)]
            u.mem_write(sp+0x278,b'\xaa'*0x40);u.mem_write(sp+0x294,struct.pack('<I',initial[0]));u.mem_write(sp+0x29c,struct.pack('<I',initial[1]))
            stops.clear();stops.add(bias+0x12933e4);u.emu_start(bias+0x12933e0,0,count=2000)
            assert u.reg_read(UC_ARM64_REG_PC)==bias+0x12933e4
            expected=(5,3) if setting in ['1','true'] else initial
            assert tuple(struct.unpack('<I',u.mem_read(sp+p,4))[0] for p in [0x294,0x29c])==expected
            assert u.reg_read(UC_ARM64_REG_X0)==0x20008000
            assert [u.reg_read(UC_ARM64_REG_X0+i) for i in range(1,29)]==before[1:]
            assert [u.reg_read(UC_ARM64_REG_Q0+i) for i in range(32)]==q
            assert u.reg_read(UC_ARM64_REG_SP)==sp and u.reg_read(UC_ARM64_REG_NZCV)==0xa0000000
            assert u.reg_read(UC_ARM64_REG_LR)==0x22000080
            assert bytes(u.mem_read(sp+0x298,4))==b'\xaa'*4;n+=1
print(json.dumps({'cases':n,'realNativeStageSwitchExecuted':True,'diagnosticCoreReproduces325Rejection':True,'cleanCoreAccepts325':True,'rbGetenvModeledWithGpSimdFlagsClobber':True,'deviceValidated':False}))
