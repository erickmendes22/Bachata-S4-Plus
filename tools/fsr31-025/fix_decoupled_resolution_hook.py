#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Fix the proven EAX/ECX contract violation in the custom scene-size hook."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HOOK = 0x04D3BAF0
CALL = 0x01258F2C
OLD = bytes.fromhex('488B05D14BC000488B80900000008B8884000000C3')
# Read height before replacing the descriptor pointer in RAX with width.
NEW = OLD[:-1] + bytes.fromhex('8B8080000000C3')
CALL_BYTES = bytes.fromhex('E8BF2BAE030F1F440000')
ORIGINAL_CALL = bytes.fromhex('418B442450418B4C2454')

def fix(text):
    count = 0
    def replace(match):
        nonlocal count
        metadata = ET.fromstring(match.group())
        if not metadata.get('Name', '').startswith('Decoupled 1080p UI ('):
            return match.group()
        lines = list(metadata.find('PatchList'))
        hooks = [l for l in lines if int(l.get('Address'), 0) == HOOK]
        calls = [l for l in lines if int(l.get('Address'), 0) == CALL]
        if len(hooks) != 1 or len(calls) != 1:
            raise ValueError('Expected exactly one width/height hook and caller')
        if bytes.fromhex(calls[0].get('Value')) != CALL_BYTES:
            raise ValueError('Unexpected caller')
        data = bytes.fromhex(hooks[0].get('Value'))
        if data not in (OLD, NEW):
            raise ValueError('Unexpected hook; refusing to overwrite')
        for line in lines:
            if line is hooks[0]:
                continue
            start = int(line.get('Address'), 0)
            if line.get('Type') != 'bytes':
                raise ValueError('Unexpected custom patch write type')
            end = start + len(bytes.fromhex(line.get('Value')))
            if start < HOOK + len(NEW) and end > HOOK:
                raise ValueError('Extended hook would overlap another write')
        count += 1
        if data == NEW:
            return match.group()
        # Change only these bytes. Preserve metadata, formatting and selection.
        pattern = re.compile(r'(<Line\b[^>]*\bAddress="0x04D3BAF0"[^>]*\bValue=")'
                             + OLD.hex().upper() + r'(")')
        result, changed = pattern.subn(lambda m: m[1] + NEW.hex().upper() + m[2],
                                      match.group())
        if changed != 1:
            raise ValueError('Hook serialization did not match')
        return result
    result = re.sub(r'<Metadata\b[^>]*>.*?</Metadata>', replace, text, flags=re.S)
    if count != 4:
        raise ValueError('Expected four controlled resolution profiles')
    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    args.destination.write_text(fix(args.source.read_text()))
