#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Use the pinned port's resolution writes, without custom allocation hooks.

This produces a candidate for integration; it does not establish the cause of
the 7EFCD0B7/6E3C385D crashes or replace an on-device game test.
"""
from copy import deepcopy
from pathlib import Path
import re
import xml.etree.ElementTree as ET

PREFIX = 'Decoupled 1080p UI ('
SIZES = [(1280, 720), (1152, 648), (960, 540), (640, 360)]
TEMPLATE = Path(__file__).with_name('port_resolution_template.xml')
FIELDS = {0x02196A6B: (0xB8, 1280, 'scene_w'),
          0x02196A7A: (0xB8, 720, 'scene_h'),
          0x02358554: (0xB8, 1280, 'ui_w'),
          0x0235855D: (0xB9, 720, 'ui_h')}

def writes(metadata):
    result = []
    for line in metadata.find('PatchList'):
        address = int(line.attrib['Address'], 0)
        kind, value = line.attrib['Type'], line.attrib['Value']
        if kind == 'bytes':
            data = bytes.fromhex(value)
        elif kind in ('bytes16', 'bytes32', 'bytes64'):
            data = int(value, 0).to_bytes(int(kind[5:]) // 8, 'little')
        else:
            raise ValueError(f'Unsupported write: {kind}')
        result.append((address, data))
    return result

def resolution(width, height):
    if (width, height) not in SIZES:
        raise ValueError('Unsupported preset size')
    template = ET.parse(TEMPLATE).getroot().find('Metadata')
    result = deepcopy(template)
    result.tail = None
    values = {'scene_w': width, 'scene_h': height,
              'ui_w': 1920, 'ui_h': 1080}
    found = set()
    for line in result.find('PatchList'):
        address = int(line.attrib['Address'], 0)
        if address not in FIELDS:
            continue
        opcode, expected, field = FIELDS[address]
        if address in found or line.attrib['Type'] != 'bytes32':
            raise ValueError('Unexpected template instruction')
        old = int(line.attrib['Value'], 0).to_bytes(4, 'little')
        if old != bytes([opcode]) + expected.to_bytes(3, 'little'):
            raise ValueError('Template opcode/immediate mismatch')
        data = bytes([opcode]) + values[field].to_bytes(3, 'little')
        line.set('Value', f'0x{int.from_bytes(data, "little"):08x}')
        found.add(address)
    if found != FIELDS.keys():
        raise ValueError('Missing scene/UI instructions')
    result.set('Name', f'{PREFIX}{width}x{height} render res)')
    result.set('Note', f'Port reference candidate: scene {width}x{height}, '
               '1920x1080 UI; native target allocation sizes preserved.')
    result.set('isEnabled', 'false')
    return result

def replace_profiles(text):
    # Preserve all unrelated patch bytes, ordering and saved selections.
    seen = set()
    pattern = re.compile(r'<Metadata\b[^>]*>.*?</Metadata>', re.S)
    def replace(match):
        metadata = ET.fromstring(match.group())
        name = metadata.get('Name', '')
        if not name.startswith(PREFIX):
            return match.group()
        size = re.fullmatch(r'Decoupled 1080p UI \((\d+)x(\d+) render res\)', name)
        if not size:
            raise ValueError('Unknown controlled resolution profile')
        dimensions = tuple(map(int, size.groups()))
        if dimensions in seen:
            raise ValueError('Duplicate controlled resolution profile')
        seen.add(dimensions)
        replacement = resolution(*dimensions)
        replacement.set('isEnabled', metadata.get('isEnabled', 'false'))
        return ET.tostring(replacement, encoding='unicode')
    result = pattern.sub(replace, text)
    if seen != set(SIZES):
        raise ValueError('Expected exactly four controlled profiles')
    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    args.destination.write_text(replace_profiles(args.source.read_text()))
