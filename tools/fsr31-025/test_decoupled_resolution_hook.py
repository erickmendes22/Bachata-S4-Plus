#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
import struct
import xml.etree.ElementTree as ET
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
from unicorn.x86_const import *
from fix_decoupled_resolution_hook import HOOK, CALL, OLD, NEW, CALL_BYTES, ORIGINAL_CALL, fix

def execute(caller, helper, width, height):
    cpu = Uc(UC_ARCH_X86, UC_MODE_64)
    global_address = HOOK + 7 + struct.unpack_from('<i', helper, 3)[0]
    descriptor, window, original = 0x200010000, 0x200020000, 0x200030000
    stack, done = 0x70000000, 0x10000000
    for address in [CALL, HOOK, global_address, descriptor, window, original, stack, done]:
        cpu.mem_map(address & ~0xfff, 0x1000)
    cpu.mem_write(CALL, caller)
    cpu.mem_write(HOOK, helper)
    cpu.mem_write(global_address, struct.pack('<Q', descriptor))
    cpu.mem_write(descriptor + 0x90, struct.pack('<Q', window))
    cpu.mem_write(window + 0x80, struct.pack('<II', width, height))
    cpu.mem_write(original + 0x50, struct.pack('<II', width, height))
    cpu.mem_write(stack + 0x800, struct.pack('<Q', done))
    cpu.reg_write(UC_X86_REG_RSP, stack + 0x800)
    cpu.reg_write(UC_X86_REG_R12, original)
    cpu.mem_write(CALL + len(caller), b'\xc3')
    cpu.emu_start(CALL, done, count=64)
    assert cpu.reg_read(UC_X86_REG_RSP) == stack + 0x808
    assert cpu.reg_read(UC_X86_REG_R12) == original
    return cpu.reg_read(UC_X86_REG_RAX), cpu.reg_read(UC_X86_REG_RCX)

for width, height in [(1280,720), (1152,648), (960,540), (640,360)]:
    native = execute(ORIGINAL_CALL, b'\xc3' + OLD[1:], width, height)
    broken = execute(CALL_BYTES, OLD, width, height)
    repaired = execute(CALL_BYTES, NEW, width, height)
    assert native == repaired == (width, height)
    assert broken == (0x200020000, height)
    assert 1.0 / float(broken[0]) != 1.0 / float(width)
    print(f'PASS {width}x{height}: original hook width={broken[0]:#x} '
          f'(descriptor pointer); fixed EAX/ECX={repaired}; native contract/stack preserved')

text = '<Patch>'
for width, height in [(1280,720), (1152,648), (960,540), (640,360)]:
    text += (f'<Metadata Name="Decoupled 1080p UI ({width}x{height} render res)">'
             f'<PatchList><Line Type="bytes" Address="0x04D3BAF0" Value="{OLD.hex().upper()}"/>'
             f'<Line Type="bytes" Address="0x01258F2C" Value="{CALL_BYTES.hex().upper()}"/>'
             '</PatchList></Metadata>')
text += '</Patch>'
updated = fix(text)
assert updated == text.replace(OLD.hex().upper(), NEW.hex().upper())
assert fix(updated) == updated
try:
    fix(text.replace('Value="' + OLD.hex().upper(), 'Value="00' + OLD.hex().upper()))
except ValueError:
    pass
else:
    raise AssertionError('Unknown hook was overwritten')
print('PASS: only the four faulty helper byte strings change; unknown hooks rejected')
