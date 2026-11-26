#!/usr/bin/env python3
"""Execute the existing 025 scheduler worker to verify its actual render ABI.

No copied C++ layout, binary modification or native compilation. This verifies
the worker's conversion only; it does not establish a safe OnDraw hook.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_SP

BASE = '373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59'
WORKER = 0x12faa20
raw = Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(raw).hexdigest() == BASE
cases = 0
for bias in (0, 0x7000000000):
    for colors, depth, stencil in ((1, False, False), (5, True, False), (8, True, True), (0, False, True)):
        u = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        for address, size in ((WORKER & ~4095, 4096), (0x4719000, 4096),
                              (0x5000000, 4096), (0x5010000, 4096),
                              (0x5020000, 4096), (0x5030000, 0x10000)):
            u.mem_map(bias + address, size)
        u.mem_write(bias + WORKER, raw[WORKER:0x12fac04])
        table, callback, state = (bias + v for v in (0x5000000, 0x5010000, 0x5020000))
        command = 0x123456789
        u.mem_write(bias + 0x4719200, struct.pack('<Q', table))
        u.mem_write(table + 0x630, struct.pack('<Q', callback))
        payload = bytearray(0x130)
        for i in range(colors):
            struct.pack_into('<QI4fI', payload, i * 0x20,
                             0x1000 + i, 2, .1, .2, .3, 1., i % 2)
        struct.pack_into('<QIfI', payload, 0x100, 0x2000, 3, .5, 7)
        struct.pack_into('<4B', payload, 0x11c, depth, 1, stencil, 0)
        struct.pack_into('<4I', payload, 0x120, 640, 360, 1, colors)
        u.mem_write(state, bytes(payload))
        u.reg_write(UC_ARM64_REG_X0, state)
        u.reg_write(UC_ARM64_REG_X1, command)
        u.reg_write(UC_ARM64_REG_SP, bias + 0x503f000)
        seen = []
        def check(uc, pc, size, user):
            if pc != callback:
                return
            assert uc.reg_read(UC_ARM64_REG_X0) == command
            info = bytes(uc.mem_read(uc.reg_read(UC_ARM64_REG_X1), 72))
            assert struct.unpack_from('<4i', info, 20) == (0, 0, 640, 360)
            assert struct.unpack_from('<3I', info, 36) == (1, 0, colors)
            attachments, dp, sp = struct.unpack_from('<3Q', info, 48)
            assert bool(dp) == depth and bool(sp) == stencil
            for i in range(colors):
                a = bytes(uc.mem_read(attachments + i * 72, 72))
                assert struct.unpack_from('<QI', a, 16) == (0x1000 + i, 2)
                assert struct.unpack_from('<II', a, 44) == (i % 2, 0)
                assert a[52:68] == payload[i * 32 + 12:i * 32 + 28]
            if dp:
                a = bytes(uc.mem_read(dp, 72))
                assert struct.unpack_from('<QI', a, 16) == (0x2000, 3)
                assert struct.unpack_from('<II', a, 44) == (1, 0)
                assert struct.unpack_from('<f', a, 52)[0] == .5
            if sp:
                a = bytes(uc.mem_read(sp, 72))
                assert struct.unpack_from('<II', a, 44) == (0, 0)
                assert struct.unpack_from('<I', a, 56)[0] == 7
            seen.append(True)
            uc.emu_stop()
        u.hook_add(UC_HOOK_CODE, check)
        u.emu_start(bias + WORKER, callback + 4, count=1000)
        assert seen == [True]
        cases += 1
print(json.dumps({'cases': cases, 'nativeRenderStateBytes': 304,
                  'colorStride': 32, 'workerConversionVerified': True,
                  'OnDrawIntegrationVerified': False, 'nativeCoreCompiled': False}, indent=2))
