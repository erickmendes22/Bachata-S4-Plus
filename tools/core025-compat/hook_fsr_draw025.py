#!/usr/bin/env python3
"""Connect the existing 025 draw boundary to the SDK without rebuilding it.

Input already contains the separately tested R27 Presenter hook. The SDK
receives the original scheduler/state and ELF base, then native execution
continues with every original argument intact. No render-pass code is skipped.
"""
import hashlib
import json
from pathlib import Path
from keystone import Ks, KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN

BASE='4b6c0a860918f9d22fb7856f45326b764a12c6c7e930a84197f5dc7a7fe2b132'
ENTRY=0x12f6828
CAVE=0x3e85400
SYMBOL=0x3e85580
ks=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN)
def asm(s,pc):return bytes(ks.asm(s,addr=pc)[0])
def patch(source,destination):
    b=bytearray(Path(source).read_bytes())
    assert hashlib.sha256(b).hexdigest()==BASE
    original=asm('stp x29,x30,[sp,#-48]!',ENTRY)
    assert b[ENTRY:ENTRY+4]==original
    assert not any(b[CAVE:CAVE+0x1c0])
    code='sub sp,sp,#224;'
    for r in range(0,8,2):code+=f'stp x{r},x{r+1},[sp,#{r*8}];'
    code+='str x30,[sp,#64];'
    for r in range(0,8,2):code+=f'stp q{r},q{r+1},[sp,#{80+r*16}];'
    code+=f'mov x0,xzr;adrp x1,{SYMBOL&~4095};add x1,x1,#{SYMBOL&4095};bl 0x6c91a0;cbz x0,original;mov x9,x0;'
    code+='ldp x0,x1,[sp];'
    code+=f'adrp x2,{ENTRY&~4095};add x2,x2,#{ENTRY&4095};movz x10,#{ENTRY&65535};movk x10,#{ENTRY>>16},lsl #16;sub x2,x2,x10;blr x9;original:'
    for r in range(0,8,2):code+=f'ldp x{r},x{r+1},[sp,#{r*8}];'
    for r in range(0,8,2):code+=f'ldp q{r},q{r+1},[sp,#{80+r*16}];'
    code+=f'ldr x30,[sp,#64];add sp,sp,#224;stp x29,x30,[sp,#-48]!;b {ENTRY+4}'
    wrapper=asm(code,CAVE);assert len(wrapper)<SYMBOL-CAVE
    b[ENTRY:ENTRY+4]=asm(f'b {CAVE}',ENTRY)
    b[CAVE:CAVE+len(wrapper)]=wrapper
    name=b'bs4_fsr31_native_begin\0';b[SYMBOL:SYMBOL+len(name)]=name
    Path(destination).write_bytes(b)
    return {'inputSha256':BASE,'outputSha256':hashlib.sha256(b).hexdigest(),
            'entry':hex(ENTRY),'sdkSymbol':name[:-1].decode(),
            'originalRenderPassCodePreserved':True,'nativeCoreCompiled':False}
if __name__=='__main__':
    import sys
    print(json.dumps(patch(*sys.argv[1:]),indent=2))
