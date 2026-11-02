#!/usr/bin/env python3
"""Generate exact offsetof map for all known Mesa V38 fd_dev_info.props.

Read the SHA-pinned V38 header downloaded by the workflow. Do not use an
unmatched guessed version: file is from f28352d1179a4a85b4be286a883747bae2d3786b.
"""
from pathlib import Path
import re
import sys
header=Path(sys.argv[1]).read_text()
main=header.split("struct fd_dev_info {",1)[1]
props=main.split("magic_raw[64];",1)[1].split("} props;",1)[0]
fields=re.findall(r"^\s*(?:bool|uint(?:8|16|32|64)_t|int(?:8|16|32|64)_t|unsigned|float|int|size_t)\s+([A-Za-z_]\w*)\s*;",props,flags=re.M)
assert 90<=len(fields)<260, len(fields)
print('#include <stddef.h>')
print('#include <stdio.h>')
print('#include "freedreno_dev_info.h"')
print('#define P(x) printf("props.%s 0x%zx\\n",#x,offsetof(struct fd_dev_info,props.x))')
print('int main(void) {')
print('printf("ABI_V38 sizeof=0x%zx magic=0x%zx props=0x%zx quirks=0x%zx\\n",sizeof(struct fd_dev_info),offsetof(struct fd_dev_info,magic_raw),offsetof(struct fd_dev_info,props),offsetof(struct fd_dev_info,quirks));')
for f in fields:print(f'P({f});')
print('return 0; }')
