#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from port_resolution_patch import resolution, writes, replace_profiles, TEMPLATE, SIZES

original = ET.parse(TEMPLATE).getroot().find('Metadata')
reference = dict(writes(original))
assert len(reference) == 66
# Independent expected machine instructions from the port's scene/UI fields.
for width, height in SIZES:
    actual = dict(writes(resolution(width, height)))
    expected = dict(reference)
    for address, opcode, value in [(0x02196A6B, 0xB8, width),
                                   (0x02196A7A, 0xB8, height),
                                   (0x02358554, 0xB8, 1920),
                                   (0x0235855D, 0xB9, 1080)]:
        expected[address] = bytes([opcode]) + value.to_bytes(3, 'little')
    assert actual == expected
    # Allocation/cave edits from the previous integration must never return.
    assert 0x02697AEA not in actual and 0x04D3BAD4 not in actual
    assert actual[0x019E83AF] == bytes.fromhex('b8800700')
    assert actual[0x01FFD4D1] == bytes.fromhex('b8380400')

if len(sys.argv) > 1:
    text = Path(sys.argv[1]).read_text()
else:
    text = '<Patch><TitleID><ID>CUSA00900</ID></TitleID>'
    text += '<Metadata Name="Other patch" isEnabled="true"><PatchList/></Metadata>'
    for width, height in SIZES:
        text += (f'<Metadata Name="Decoupled 1080p UI ({width}x{height} render res)" '
                 f'isEnabled="{str(width==640).lower()}"><PatchList>'
                 '<Line Type="bytes" Address="0x02697AEA" Value="E900000000"/>'
                 '</PatchList></Metadata>')
    text += '</Patch>'
updated = replace_profiles(text)
before, after = ET.fromstring(text), ET.fromstring(updated)
assert ET.tostring(before.find('TitleID')) == ET.tostring(after.find('TitleID'))
before_meta = list(before.iter('Metadata'))
after_meta = list(after.iter('Metadata'))
assert len(before_meta) == len(after_meta)
for a, b in zip(before_meta, after_meta):
    if not a.get('Name', '').startswith('Decoupled 1080p UI ('):
        assert ET.tostring(a) == ET.tostring(b)
    else:
        assert a.get('Name') == b.get('Name')
        assert a.get('isEnabled', 'false') == b.get('isEnabled', 'false')
        assert len(writes(b)) == 66
assert replace_profiles(updated) == updated
print('PASS: exact port writes for all four presets; native allocations and '
      '1080p UI preserved; no custom allocation/cave edits; other patches '
      'and selections unchanged; repeat application stable')
