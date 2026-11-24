#!/usr/bin/env python3
"""Compare generated renderer C++ rather than trusting Python profile labels."""
from pathlib import Path
import hashlib,sys
reference,candidate=map(Path,sys.argv[1:3])
roots=("src/video_core","src/shader_recompiler","src/core/memory.cpp","src/core/memory.h")
def inventory(root):
    out={}
    for rel in roots:
        p=root/rel
        for f in ([p] if p.is_file() else p.rglob("*")):
            if f.is_file():
                out[str(f.relative_to(root))]=hashlib.sha256(f.read_bytes()).hexdigest()
    return out
a,b=inventory(reference),inventory(candidate)
changed={p for p in a.keys()|b.keys() if a.get(p)!=b.get(p)}
allowed={"src/shader_recompiler/resource.h"}
if changed!=allowed:
    raise SystemExit(f"Renderer reference drift: {sorted(changed)}; expected {sorted(allowed)}")
# Confirm only the known light-table helper and guard differ, not any unrelated
# shader resource representation or descriptor binding semantics.
p="src/shader_recompiler/resource.h"
old=(reference/p).read_text()
new=(candidate/p).read_text()
start=new.index("template<class InfoT>\nconstexpr bool Order1886UnusedLightImage")
end=new.index("struct ImageResource {",start)
new=new[:start]+new[end:]
start=new.index("        // BACHATA_ORDER_LIGHT_GUARD:")
end=new.index("        AmdGpu::Image image{};",start)
new=new[:start]+new[end:]
if new!=old:raise SystemExit("Unexpected resource contract divergence")
print("SINGLE_CORE_REFERENCE_RENDERER_PASS",len(a),"files; only exact Order light guard differs")
