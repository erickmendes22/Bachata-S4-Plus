#!/usr/bin/env python3
"""Execute actual patched ARM64 at zero and Android-like PIE biases."""
import json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *

data=Path(sys.argv[1]).read_bytes(); count=0
for bias in [0,0x7000000000]:
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(bias,0x4800000);u.mem_write(bias,data)
    u.mem_map(0x20000000,0x100000);u.mem_map(0x22000000,0x200000)
    sp=0x22100000;ctx=0x20000000;vec=0x20001000;buf=0x20002000;ids=0x20003000
    stops=set();calls=[]
    def hook(uc,pc,size,_):
        if pc in stops: uc.emu_stop()
        elif pc==bias+0x11a2ac0:
            calls.append((uc.reg_read(UC_ARM64_REG_W0),uc.reg_read(UC_ARM64_REG_W1)))
            uc.reg_write(UC_ARM64_REG_X0,0x1234);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
        elif pc==bias+0x158ccec:
            # EndInstruction interns constants through the external C++ heap.
            # Test the original native constant/literal writer before interning.
            assert struct.unpack('<IIII',uc.mem_read(buf,16))==(43,7,101,0)
            uc.reg_write(UC_ARM64_REG_X0,101);uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    def setup():
        for i in range(29):u.reg_write(UC_ARM64_REG_X0+i,0x550000+i)
        u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_X29,sp)
        u.reg_write(UC_ARM64_REG_LR,0x22001000)
        calls.clear()
    def run(pc,ends):
        global count
        stops.clear();stops.update(bias+x for x in ends)
        
        try:u.emu_start(bias+pc,0,count=5000)
        except Exception as e:raise AssertionError((hex(pc),hex(u.reg_read(UC_ARM64_REG_PC)),hex(u.reg_read(UC_ARM64_REG_X26)))) from e
        assert u.reg_read(UC_ARM64_REG_PC) in stops
        count+=1
    for stage in [0,0x45,0xac,0x145,0x146,0xffffffff]:
        setup();u.reg_write(UC_ARM64_REG_X21,ctx);u.mem_write(ctx+0x114,struct.pack('<I',stage))
        run(0x1262064,[0x1262068]);assert u.reg_read(UC_ARM64_REG_W8)==(0x45 if stage==0x145 else stage)
    for site,accept,skip,second in [(0x11a16a4,0x11a16ac,0x11a13e8,False),(0x11a19ac,0x11a19b4,0x11a199c,True)]:
        for domain in [0,1,2,3,0xffffffff]:
            for attr in range(9):
                setup();u.reg_write(UC_ARM64_REG_W0,domain);u.reg_write(UC_ARM64_REG_W26,attr-(1 if second and attr else 0));u.reg_write(UC_ARM64_REG_W22,1 if second and attr else 0)
                run(site,[accept,skip]);ok=domain<3 and attr<[2,4,6][domain]
                assert u.reg_read(UC_ARM64_REG_PC)==bias+(accept if ok else skip)
                assert calls==([(domain,attr)] if ok else [])
                if ok:assert u.reg_read(UC_ARM64_REG_X0)==0x1234
    for attr in [66,90,93,100]:
        setup();u.reg_write(UC_ARM64_REG_X1,attr)
        run(0x114f84c,[0x114f850]);assert u.reg_read(UC_ARM64_REG_X8)==attr-66
    # Execute original native ConstU32, including literal write and EndInstruction.
    for attr in [91,92]:
        setup();u.mem_write(ctx,b'\0'*0x400);u.mem_write(vec,b'\0'*0x100);u.mem_write(buf,b'\xff'*0x1000)
        u.mem_write(ctx+0xd8,struct.pack('<Q',vec));u.mem_write(ctx+0x190,struct.pack('<I',7))
        u.mem_write(vec,struct.pack('<QQQ',ids,buf,buf+0x1000));u.mem_write(ids,struct.pack('<I',100))
        u.reg_write(UC_ARM64_REG_X0,ctx);u.reg_write(UC_ARM64_REG_X1,attr)
        stops.clear();stops.add(0x22001000);u.emu_start(bias+0x114f838,0,count=5000)
        assert u.reg_read(UC_ARM64_REG_PC)==0x22001000, (hex(u.reg_read(UC_ARM64_REG_PC)),hex(u.reg_read(UC_ARM64_REG_LR)))
        words=struct.unpack('<IIII',u.mem_read(buf,16))
        assert words==(43,7,101,0),words
        assert u.reg_read(UC_ARM64_REG_SP)==sp
        count+=1
    # Undef leaves source/flags unchanged; other producers use original handling.
    for opcode in [10,11,45,78,401,999]:
        setup();u.mem_write(ctx,b'\0'*0x100);u.mem_write(ctx+0x14,struct.pack('<I',opcode));u.mem_write(ctx+0x20,struct.pack('<Q',0x123))
        u.reg_write(UC_ARM64_REG_X26,ctx)
        run(0x11b1440,[0x11b1448,0x11b1410])
        assert u.reg_read(UC_ARM64_REG_PC)==bias+(0x11b1410 if opcode==78 else 0x11b1448)
        assert struct.unpack('<Q',u.mem_read(ctx+0x20,8))[0]==0x123
        assert u.reg_read(UC_ARM64_REG_X26)==ctx
print(json.dumps({'arm64Cases':count,'pieBiases':['0','0x7000000000'],'nativeConstU32AndLiteralWriterExecuted':True,'constantInterningModeled':True,'deviceValidated':False}))
