#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Inject R16 core025-only linker --preload into verified R15 FEX dispatcher."""
import argparse,struct,hashlib
from pathlib import Path

EXEC_CALL_VA=0x10758
EXEC_CALL_OFFSET=0x758
PRELOAD_HOOK_VA=0x12400
PRELOAD_HOOK_OFFSET=0x2400
EXPECTED_BRANCH=0x1400062a  # R15 VA 0x10758 -> original dispatcher VA 0x12000
def patch(original,stub):
    b=bytearray(Path(original).read_bytes())
    hook=Path(stub).read_bytes()
    assert b[:4]==b'\x7fELF', 'Invalid original dispatcher'
    assert len(hook)<0x600, 'Hook exceeds reserved executable cave'
    assert struct.unpack_from('<I',b,EXEC_CALL_OFFSET)[0]==EXPECTED_BRANCH, 'Unexpected dispatcher version'
    assert not any(b[PRELOAD_HOOK_OFFSET:PRELOAD_HOOK_OFFSET+len(hook)]), 'Occupied cave'
    # Original 025/024/023/020 game selection remains byte-identical.
    b[PRELOAD_HOOK_OFFSET:PRELOAD_HOOK_OFFSET+len(hook)]=hook
    delta=PRELOAD_HOOK_VA-EXEC_CALL_VA
    assert delta%4==0 and -(1<<27)<=delta<(1<<27)
    struct.pack_into('<I',b,EXEC_CALL_OFFSET,0x14000000|((delta//4)&0x3ffffff))
    return bytes(b)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('original')
    parser.add_argument('compiled_hook')
    parser.add_argument('output')
    a=parser.parse_args()
    b=patch(a.original,a.compiled_hook)
    Path(a.output).write_bytes(b)
    print('R16 core025-only preload patched SHA256:',hashlib.sha256(b).hexdigest())
if __name__=='__main__':main()
