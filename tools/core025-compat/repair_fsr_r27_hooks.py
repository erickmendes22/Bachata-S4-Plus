#!/usr/bin/env python3
"""Repair the retained 025's R27 regressions; do not compile a native core.

Inputs are exact shipped binaries. Compatibility/RB caves are restored from
pre-FSR R27. FSR call wrappers move to separate, verified empty RX padding.
Disabled FSR skips SDK lookup/callbacks. No guest heap panic is patched out.
"""
import hashlib, json, struct
from pathlib import Path
from keystone import Ks, KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN

STABLE_SHA = '373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59'
SHIPPED_SHA = 'c1cf8986c2a5f6f9f33d32a073eff797e2717b4848cd475c4d19f26dc7042bb2'
ATTACH_SITE = 0x128e79c
RENDER_SITE = 0x1293b4c
PIPELINE_SITE = 0x1277830
ATTACH_CAVE = 0x3e86000
RENDER_CAVE = 0x3e86400
PIPELINE_CAVE = 0x3e86800
GETENV = 0x6cb060
DLSYM = 0x6c91a0
ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
def asm(s, pc): return bytes(ks.asm(s, addr=pc)[0])
def sha(b): return hashlib.sha256(b).hexdigest()

def save():
    c = ['sub sp,sp,#224']
    c += [f'stp x{r},x{r+1},[sp,#{r*8}]' for r in range(0,8,2)]
    c += ['str x30,[sp,#64]', 'stp x8,x18,[sp,#208]']
    c += [f'stp q{r},q{r+1},[sp,#{80+r*16}]' for r in range(0,8,2)]
    return c
def args():
    c = [f'ldp x{r},x{r+1},[sp,#{r*8}]' for r in range(0,8,2)]
    c += ['ldp x8,x18,[sp,#208]']
    c += [f'ldp q{r},q{r+1},[sp,#{80+r*16}]' for r in range(0,8,2)]
    return c
def epilogue(): return ['ldr x30,[sp,#64]', 'add sp,sp,#224', 'ret']
def request_gate(mode_address, skip):
    # getenv and dlsym are arbitrary external ABI calls; original arguments
    # are restored after either one. Only the launcher contract 0..4 enables.
    return [f'adrp x0,{mode_address&~4095}',
            f'add x0,x0,#{mode_address&4095}', f'bl {GETENV}',
            f'cbz x0,{skip}', 'ldrb w9,[x0]', 'sub w9,w9,#48',
            'cmp w9,#4', f'b.hi {skip}', 'ldrb w9,[x0,#1]',
            f'cbnz w9,{skip}']
def lookup(symbol_address, skip):
    return ['mov x0,xzr', f'adrp x1,{symbol_address&~4095}',
            f'add x1,x1,#{symbol_address&4095}', f'bl {DLSYM}',
            f'cbz x0,{skip}', 'mov x9,x0']

def patch(shipped_path, stable_path, destination):
    original = Path(shipped_path).read_bytes()
    stable = Path(stable_path).read_bytes()
    assert sha(original)==SHIPPED_SHA and sha(stable)==STABLE_SHA
    assert len(original)==len(stable)
    b = bytearray(original)
    restored_sites = [0x114f84c,0x11a16a4,0x11a19ac,0x11b1444,0x1262064,0x12933e0]
    for site in restored_sites: b[site:site+4]=stable[site:site+4]
    # Old disconnected RB wrapper is zero in stable R27. Restore the real
    # native compatibility and connected Presenter RB code byte-for-byte.
    for start,end in [(0x3e82e00,0x3e82e30),(0x3e83e00,0x3e84240)]:
        b[start:end]=stable[start:end]
    # The old standalone Presenter hook was already absent; do not revive it.
    assert not any(original[0x3e85000:0x3e851c0])
    def put_wrapper(cave, code, symbol):
        assert not any(original[cave:cave+0x400]),hex(cave)
        symbol_address = cave+0x300
        mode_address = cave+0x340
        compiled = asm(';'.join(code(symbol_address,mode_address)),cave)
        assert len(compiled)<0x300
        b[cave:cave+len(compiled)] = compiled
        sym=symbol.encode()+b'\0';mode=b'BACHATA_FSR31_MODE\0'
        b[symbol_address:symbol_address+len(sym)]=sym
        b[mode_address:mode_address+len(mode)]=mode
    def attach(symbol,mode):
        c=save()+args()+['bl 0x130b57c','str x0,[sp,#72]']
        c+=request_gate(mode,'done')+lookup(symbol,'done')
        c+=['ldp x0,x1,[sp]', 'ldr x2,[sp,#24]',
            'ldr x3,[sp,#32]','ldr w4,[sp,#40]','blr x9']
        # Preserve the native constructor's returned object, even if attach
        # declines with -2. This is stricter than the old shipped wrapper.
        c+=['done:ldr x0,[sp,#72]','ldp x8,x18,[sp,#208]']+epilogue()
        return c
    def render(symbol,mode):
        c=save()+request_gate(mode,'original')+lookup(symbol,'original')
        c+=args()+['blr x9','cbnz x0,done','original:']+args()
        c+=['bl 0x130f524','done:']+epilogue()
        return c
    def pipeline(symbol,mode):
        c=save()+request_gate(mode,'original')+lookup(symbol,'original')
        c+=['ldr x0,[sp]','blr x9','original:']+args()
        c+=['ldr x30,[sp,#64]','add sp,sp,#224',
            'stp x29,x30,[sp,#-96]!','b 0x1277834']
        return c
    put_wrapper(ATTACH_CAVE,attach,'bs4_fsr31_attach')
    put_wrapper(RENDER_CAVE,render,'bs4_fsr31_try_render')
    put_wrapper(PIPELINE_CAVE,pipeline,'bs4_fsr31_native_pipeline')
    b[ATTACH_SITE:ATTACH_SITE+4]=asm(f'bl {ATTACH_CAVE}',ATTACH_SITE)
    b[RENDER_SITE:RENDER_SITE+4]=asm(f'bl {RENDER_CAVE}',RENDER_SITE)
    b[PIPELINE_SITE:PIPELINE_SITE+4]=asm(f'b {PIPELINE_CAVE}',PIPELINE_SITE)
    # Remove unreachable old native pipeline wrapper. Scheduler stays original.
    b[0x3e85800:0x3e859c0]=stable[0x3e85800:0x3e859c0]
    assert b[0x12f6828:0x12f682c]==stable[0x12f6828:0x12f682c]
    assert not any(b[0x3e85400:0x3e855c0])
    for site in restored_sites: assert b[site:site+4]==stable[site:site+4]
    assert b[0x3e83e00:0x3e84240]==stable[0x3e83e00:0x3e84240]
    allowed=[(p,p+4) for p in restored_sites+[ATTACH_SITE,RENDER_SITE,PIPELINE_SITE]]
    allowed += [(0x3e82e00,0x3e82e30),(0x3e83e00,0x3e84240),
                (0x3e85800,0x3e859c0),(ATTACH_CAVE,PIPELINE_CAVE+0x400)]
    assert all(a==v or any(lo<=i<hi for lo,hi in allowed)
               for i,(a,v) in enumerate(zip(original,b)))
    Path(destination).write_bytes(b)
    return {'inputSha256':SHIPPED_SHA,'stableR27Sha256':STABLE_SHA,
            'outputSha256':sha(b),'compatibilityAndRBRestored':True,
            'fsrOffSkipsSDKCallbacks':True,'nativeCoreCompiled':False,
            'heapPanicRootCauseProven':False,'deviceValidated':False}

if __name__=='__main__':
    import sys
    print(json.dumps(patch(*sys.argv[1:]),indent=2))
