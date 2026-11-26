#!/usr/bin/env python3
"""Port proven core024 compatibility behavior to the pre-FSR core025 binary.

All addresses are specific to the SHA-pinned native 025, never to core024.
Uses only PC-relative branches and verified unused RX padding.
"""
import argparse, hashlib, json
from pathlib import Path
from keystone import Ks, KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN
from elftools.elf.elffile import ELFFile

BASE_SHA = 'a083905c30725156eb7ee384079243b3346683a0aa3f5055fbb73a974364faf2'
KS = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
def assemble(code, pc):
    return bytes(KS.asm(code, addr=pc)[0])
def patch(source, dest):
    original = Path(source).read_bytes()
    assert hashlib.sha256(original).hexdigest() == BASE_SHA
    assert b'bs4_fsr31' not in original
    data = bytearray(original); changes = []
    with open(source, 'rb') as f:
        elf = ELFFile(f)
        assert elf['e_machine'] == 'EM_AARCH64'
        assert any(s['p_type']=='PT_LOAD' and s['p_flags']==5 and
                   s['p_offset']==s['p_vaddr']==0 and
                   s['p_filesz'] > 0x3e84800 for s in elf.iter_segments())
    def put(pc, code, expected=None):
        b = assemble(code, pc)
        old = original[pc:pc+len(b)]
        if expected is None: assert not any(old), hex(pc)
        else: assert old == assemble(expected, pc), (hex(pc),old.hex())
        data[pc:pc+len(b)] = b
        changes.append({'offset':hex(pc),'old':old.hex(),'new':b.hex()})

    # PipelineCache::RefreshGraphicsStages: native 025 changed the register layout.
    put(0x3e83e00, '''ldr w8,[x21,#0x114];cmp w8,#0x145;
        b.ne normal;mov w8,#0x45;normal:b 0x1262068''')
    put(0x1262064, 'b 0x3e83e00', 'ldr w8,[x21,#0x114]')

    # HullShaderTransform: skip unsupported patch-constant regions, not shaders.
    # Every valid region still calls the original native GetAttributeRegionKind.
    for site,cave,first,ok,skip in [
        (0x11a16a4,0x3e83e80,'mov w1,w26',0x11a16ac,0x11a13e8),
        (0x11a19ac,0x3e83f00,'add w1,w22,w26',0x11a19b4,0x11a199c)]:
        put(cave, f'''{first};cmp w0,#0;b.eq isoline;
            cmp w0,#1;b.eq triangle;cmp w0,#2;b.ne reject;
            cmp w1,#6;b.lo accept;b reject;
            isoline:cmp w1,#2;b.lo accept;b reject;
            triangle:cmp w1,#4;b.lo accept;b reject;
            accept:bl 0x11a2ac0;b {ok};reject:b {skip}''')
        put(site, f'b {cave}', first)

    # EmitGetAttributeU32: OffChipLdsBase/IsOffChipLds become native ConstU32(0).
    # The original emitter's own 8-byte Literal operand lives at sp+0x38.
    put(0x3e83f80, '''cmp x1,#91;b.eq zero;cmp x1,#92;b.eq zero;
        sub x8,x1,#0x42;b 0x114f850;
        zero:ldr w1,[x0,#0x190];str wzr,[sp,#0x38];
        strb wzr,[sp,#0x40];add x2,sp,#0x38;
        bl 0x158d75c;b 0x114f984''')
    put(0x114f84c, 'b 0x3e83f80', 'sub x8,x1,#0x42')

    # Elden Ring C37's safe Undef handling: no producer can be marked for
    # UndefU32; keep its descriptor value intact. Do not synthesize a zero.
    # 025 already unwraps nested ReadFirstLane during buffer/image discovery.
    put(0x3e84000, '''cmp w8,#78;b.ne normal;b 0x11b1410;
        normal:cmp w8,#10;b 0x11b1448''')
    put(0x11b1444, 'b 0x3e84000', 'cmp w8,#10')
    for pc in [0x11b1718,0x11b1ab8,0x11b1bf4]:
        assert original[pc:pc+4]==assemble('cmp w14,#0x191',pc)

    # Native domain fallback (11a4618) and VMM cap (8cfba0,8d0164) already
    # supersede the old 024 fixes. Do not duplicate old stack/frame/VMM logic.
    for pc,code in [(0x11a46c0,'cmp w8,#0xb'),
                    (0x8cf68c,'mov x9,#0x4000000000'),
                    (0x8cfba0,'mov x1,#0x5000000000'),
                    (0x8d0164,'mov x20,#0x5000000000')]:
        assert original[pc:pc+4]==assemble(code,pc)
    # Preserve inFAMOUS native input hooks and every other core025 byte.
    assert data[0x3e82000:0x3e83d00] == original[0x3e82000:0x3e83d00]
    Path(dest).write_bytes(data)
    return {'baseSha256':BASE_SHA,'coreSha256':hashlib.sha256(data).hexdigest(),
            'changes':changes,'fsrHooks':False,
            'medievil':'native 025 upper usable cap 0x5000000000 already includes required range',
            'domainShader':'native 025 ReadConstBuffer fallback retained',
            'eldenRing':'native recursive ReadFirstLane retained; only safe Undef producer guard ported, no descriptor substitution',
            'deviceValidated':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('dest');p.add_argument('report');a=p.parse_args()
    Path(a.report).write_text(json.dumps(patch(a.source,a.dest),indent=2)+'\n')
