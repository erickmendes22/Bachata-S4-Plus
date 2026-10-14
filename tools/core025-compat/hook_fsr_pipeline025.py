#!/usr/bin/env python3
"""Supply the existing native 025 vertex hash without relying on debug names."""
import hashlib,json
from pathlib import Path
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN
BASE='1c1c70c98fe128e15d6bf654f5bf4d1663714414b491deda80abaac0ede5d41e'
ENTRY=0x1277830;CAVE=0x3e85800;SYMBOL=0x3e85980
ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
def asm(s,pc):return bytes(ks.asm(s,addr=pc)[0])
def patch(source,destination):
 b=bytearray(Path(source).read_bytes());assert hashlib.sha256(b).hexdigest()==BASE
 original=asm('stp x29,x30,[sp,#-96]!',ENTRY);assert b[ENTRY:ENTRY+4]==original
 assert not any(b[CAVE:CAVE+0x1c0]);code='sub sp,sp,#224;'
 for r in range(0,8,2):code+=f'stp x{r},x{r+1},[sp,#{r*8}];'
 code+='str x30,[sp,#64];'
 for r in range(0,8,2):code+=f'stp q{r},q{r+1},[sp,#{80+r*16}];'
 code+=f'mov x0,xzr;adrp x1,{SYMBOL&~4095};add x1,x1,#{SYMBOL&4095};bl 0x6c91a0;cbz x0,original;mov x9,x0;ldr x0,[sp];blr x9;original:'
 for r in range(0,8,2):code+=f'ldp x{r},x{r+1},[sp,#{r*8}];'
 for r in range(0,8,2):code+=f'ldp q{r},q{r+1},[sp,#{80+r*16}];'
 code+=f'ldr x30,[sp,#64];add sp,sp,#224;stp x29,x30,[sp,#-96]!;b {ENTRY+4}'
 wrapper=asm(code,CAVE);assert len(wrapper)<SYMBOL-CAVE
 b[ENTRY:ENTRY+4]=asm(f'b {CAVE}',ENTRY);b[CAVE:CAVE+len(wrapper)]=wrapper
 name=b'bs4_fsr31_native_pipeline\0';b[SYMBOL:SYMBOL+len(name)]=name
 Path(destination).write_bytes(b)
 return dict(inputSha256=BASE,outputSha256=hashlib.sha256(b).hexdigest(),nativeCoreCompiled=False)
if __name__=='__main__':
 import sys
 print(json.dumps(patch(*sys.argv[1:]),indent=2))
