#!/usr/bin/env python3
"""Attach the SDK ABI at the existing core025 Presenter FsrPass call.
No native core compilation. Preserve R27 compatibility/RB and every other byte.
"""
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
import hashlib,json
BASE='373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59'
SITE=0x1293b4c;ORIGINAL=0x130f524;CAVE=0x3e85000;SYMBOL=0x3e85180
ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
def asm(s,pc):return bytes(ks.asm(s,addr=pc)[0])
def patch(src,dst):
 b=bytearray(Path(src).read_bytes());assert hashlib.sha256(b).hexdigest()==BASE
 assert b[SITE:SITE+4]==asm(f'bl {ORIGINAL}',SITE)
 assert not any(b[CAVE:CAVE+0x1c0])
 # A real function call, not a mid-function jump: preserve original args,
 # LR, SIMD arguments and stack alignment across dlsym and SDK dispatch.
 code='sub sp,sp,#224;'
 for r in range(0,8,2):code+=f'stp x{r},x{r+1},[sp,#{r*8}];'
 code+='str x30,[sp,#64];'
 for r in range(0,8,2):code+=f'stp q{r},q{r+1},[sp,#{80+r*16}];'
 code+=f'''mov x0,xzr;adrp x1,{SYMBOL&~4095};add x1,x1,#{SYMBOL&4095};bl 0x6c91a0;
 cbz x0,original;mov x9,x0;'''
 for r in range(0,8,2):code+=f'ldp x{r},x{r+1},[sp,#{r*8}];'
 code+='blr x9;cbnz x0,done;original:'
 for r in range(0,8,2):code+=f'ldp x{r},x{r+1},[sp,#{r*8}];'
 for r in range(0,8,2):code+=f'ldp q{r},q{r+1},[sp,#{80+r*16}];'
 code+=f'bl {ORIGINAL};done:ldr x30,[sp,#64];add sp,sp,#224;ret'
 x=asm(code,CAVE);assert len(x)<SYMBOL-CAVE
 b[CAVE:CAVE+len(x)]=x;sym=b'bs4_fsr31_try_render\0';b[SYMBOL:SYMBOL+len(sym)]=sym;b[SITE:SITE+4]=asm(f'bl {CAVE}',SITE)
 Path(dst).write_bytes(b)
 return {'baseCore025Sha256':BASE,'patchedCore025Sha256':hashlib.sha256(b).hexdigest(),'site':hex(SITE),'original':hex(ORIGINAL),'sdkSymbol':'bs4_fsr31_try_render','nativeCoreCompiled':False,'deviceValidated':False}
if __name__=='__main__':
 import sys
 print(json.dumps(patch(*sys.argv[1:]),indent=2))
