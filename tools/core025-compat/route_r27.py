#!/usr/bin/env python3
"""SHA-pinned dispatcher: Elden Ring -> 024, remove every 023 route."""
import hashlib,json,re
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
BASE='5c162129531b9446557c25c6a06ff5fe2a85f489c8d35d6faa5b929234735882'
ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
def assemble(s,pc):
 x=bytearray(ks.asm(s,addr=pc)[0]);targets=[int(t,16) for t in re.findall(r'adr x\d+,(0x[0-9a-f]+)',s)]
 ins=[i for i in Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(x,pc) if i.mnemonic=='adr'];assert len(ins)==len(targets)
 for i,target in zip(ins,targets):
  delta=target-i.address;assert -(1<<20)<=delta<(1<<20)
  imm=delta&0x1fffff;reg=int(i.op_str.split(',')[0][1:]);word=0x10000000|((imm&3)<<29)|((imm>>2)<<5)|reg
  x[i.address-pc:i.address-pc+4]=word.to_bytes(4,'little')
 return bytes(x)
def patch(src,dst):
 b=bytearray(Path(src).read_bytes());assert hashlib.sha256(b).hexdigest()==BASE
 def put(pc,s):
  x=assemble(s,pc);b[pc-0x10000:pc-0x10000+len(x)]=x
 # Replace old numeric BO/023 routing with exact Elden and existing Driveclub.
 for pc,reg,skip,resume in [(0x11800,'x13',0x103f4,0x10550),(0x11900,'x12',0x104bc,0x1076c)]:
  b[pc-0x10000:pc-0x10000+0x80]=bytes(0x80)
  put(pc,f'''mov w14,wzr;mov w15,#10;mov w16,wzr;
   digit:ldrb w17,[{reg},w16,uxtw];sub w17,w17,#48;cmp w17,#9;b.hi {skip};
   madd w14,w14,w15,w17;add w16,w16,#1;cmp w16,#5;b.lo digit;
   ldrb w17,[{reg},#5];sub w17,w17,#48;cmp w17,#9;b.ls {skip};
   cmp w14,#93;b.eq drive;mov w15,#18723;cmp w14,w15;b.eq elden;
   mov w15,#28527;cmp w14,w15;b.eq elden;mov w15,#28863;cmp w14,w15;b.ne {skip};
   elden:mov w12,#3;b {resume};drive:mov w12,#2;b {resume}''')
 put(0x10428,'b 0x11800');put(0x104f0,'b 0x11900')
 # Physically remove unreachable 023 comparisons and title-based BO2 hook.
 for start,end in [(0x11000,0x11080),(0x11100,0x11150),(0x1042c,0x10488),(0x104f4,0x1054c),(0x11240,0x112e8),(0x13500,0x13554)]:
  b[start-0x10000:end-0x10000]=bytes(end-start)
 # Keep Driveclub's validated absolute-game-path SFO recognition.
 put(0x11230,'adr x13,0x28d;b 0x105fc')
 put(0x11204,'cmp w12,#3;b.eq 0x11230;cmp w12,#2;b.eq 0x11220;adr x13,0x2eb;b 0x105fc')
 put(0x11160,'cmp w12,#2;b.eq 0x11174;cmp w12,#3;csel x1,x14,x8,eq;b 0x10668')
 assert b.count(b'shadps4-arm64-023')==1 and b.count(b'core=023')==1
 b=b.replace(b'shadps4-arm64-023',b'shadps4-arm64-024').replace(b'core=023',b'core=024')
 # Replace the BO2 heuristic with a bounded, typed TITLE_ID parser under override-root.
 b[0x3000:0x332e]=bytes(0x32e)
 code='sub sp,sp,#5,lsl #12;'
 for r in range(0,30,2):code+=f'stp x{r},x{r+1},[sp,#{r*8}];'
 code+='str x30,[sp,#240];ldr x19,[x0];add x20,x0,#8;mov x21,#1;'
 code+='''args:cmp x21,x19;b.hs done;ldr x22,[x20,x21,lsl #3];adr x23,0x13400;mov x25,#0;
 key:ldrb w9,[x22,x25];ldrb w10,[x23,x25];cmp w9,w10;b.ne next;cbz w9,root;add x25,x25,#1;b key;
 next:add x21,x21,#1;b args;
 root:add x21,x21,#1;cmp x21,x19;b.hs done;ldr x24,[x20,x21,lsl #3];add x23,sp,#0x200;mov x25,#0;
 path:cmp x25,#0x3c0;b.hs done;ldrb w9,[x24,x25];cbz w9,suffix;strb w9,[x23,x25];add x25,x25,#1;b path;
 suffix:adr x24,0x13410;mov x9,#0;
 suf:ldrb w10,[x24,x9];strb w10,[x23,x25];add x9,x9,#1;add x25,x25,#1;cbnz w10,suf;
 mov x0,#-100;mov x1,x23;mov x2,#0;mov x3,#0;mov x8,#56;svc #0;cmp x0,#0;b.lt done;mov x19,x0;
 add x1,sp,#0x800;mov x2,#0x4000;mov x8,#63;svc #0;mov x21,x0;mov x0,x19;mov x8,#57;svc #0;
 cmp x21,#20;b.lt done;add x22,sp,#0x800;ldr w9,[x22];mov w10,#0x5000;movk w10,#0x4653,lsl #16;cmp w9,w10;b.ne done;
 ldr w23,[x22,#8];ldr w24,[x22,#12];ldr w19,[x22,#16];cmp w19,#255;b.hi done;
 lsl x9,x19,#4;add x9,x9,#20;cmp x9,x21;b.hi done;cmp x23,x9;b.lo done;cmp x24,x23;b.lo done;cmp x24,x21;b.hs done;mov x25,#20;
 entry:cbz x19,done;ldrh w9,[x22,x25];add x9,x9,x23;add x10,x9,#9;cmp x10,x24;b.hi advance;
 ldr x10,[x22,x9];mov x11,#0x4954;movk x11,#0x4c54,lsl #16;movk x11,#0x5f45,lsl #32;movk x11,#0x4449,lsl #48;cmp x10,x11;b.ne advance;
 add x9,x9,#8;ldrb w9,[x22,x9];cbnz w9,advance;add x9,x25,#2;ldrh w9,[x22,x9];cmp w9,#0x204;b.ne done;
 add x9,x25,#4;ldr w10,[x22,x9];add x9,x25,#8;ldr w11,[x22,x9];cmp w10,#10;b.lo done;cmp w10,w11;b.hi done;
 add x9,x25,#12;ldr w9,[x22,x9];add x9,x9,x24;add x11,x9,x10;cmp x11,x21;b.hi done;
 add x9,x22,x9;ldrb w10,[x9,#9];cbnz w10,done;ldr x10,[x9];ldrb w11,[x9,#8];
 mov x12,#0x5543;movk x12,#0x4153,lsl #16;movk x12,#0x3831,lsl #32;movk x12,#0x3237,lsl #48;cmp x10,x12;b.ne id2;cmp w11,#51;b.eq matched;
 id2:movk x12,#0x3832,lsl #32;movk x12,#0x3235,lsl #48;cmp x10,x12;b.ne id3;cmp w11,#55;b.eq matched;
 id3:movk x12,#0x3638,lsl #48;cmp x10,x12;b.ne done;cmp w11,#51;b.ne done;
 matched:mov x9,#3;str x9,[sp,#96];b done;
 advance:add x25,x25,#16;sub x19,x19,#1;b entry;
 done:''' 
 for r in range(0,30,2):code+=f'ldp x{r},x{r+1},[sp,#{r*8}];'
 code+='ldr x30,[sp,#240];add sp,sp,#5,lsl #12;b 0x105e8'
 x=assemble(code,0x13000);assert len(x)<=0x400,len(x);b[0x3000:0x3000+len(x)]=x
 b[0x3400:0x3410]=b'--override-root\0';b[0x3410:0x3423]=b'/sce_sys/param.sfo\0'
 assert b'023' not in b and b'black ops' not in b
 Path(dst).write_bytes(b)
 return hashlib.sha256(b).hexdigest()
if __name__=='__main__':
 import sys
 print(patch(*sys.argv[1:]))
