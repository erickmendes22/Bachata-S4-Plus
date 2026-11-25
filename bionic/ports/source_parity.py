#!/usr/bin/env python3
"""Inventory effective code, not patch names; no donor CPU/runtime substitution."""
import argparse
import collections
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

SCOPE = ("shader_recompiler/", "video_core/", "core/libraries/videoout/",
         "core/libraries/gnmdriver/", "core/memory.cpp", "core/memory.h",
         "core/libraries/kernel/memory.cpp", "core/libraries/kernel/memory.h",
         "core/libraries/kernel/file_system.cpp", "core/libraries/pad/",
         "core/libraries/audio/", "common/arch.h", "common/signal_context.cpp")
EXT = {".cpp", ".h", ".hpp", ".c", ".inc", ".glsl", ".vert", ".frag", ".comp"}
def inventory(root):
    return {str(p.relative_to(root)):p for p in root.rglob("*")
            if p.is_file() and p.suffix in EXT and
            str(p.relative_to(root)).startswith(SCOPE)}
def subsystem(path):
    if path.startswith("shader_recompiler/"): return "shader/SRT/specialization"
    if "present" in path or "swapchain" in path or "/videoout/" in path: return "presentation/frame pacing"
    if "pipeline" in path or "cache_storage" in path: return "pipeline/cache"
    if "texture_cache" in path: return "texture/metadata"
    if "buffer_cache" in path or "page_manager" in path: return "buffer/readback"
    if "/amdgpu/" in path or "gnmdriver" in path: return "PM4/command processing"
    if "scheduler" in path or "semaphore" in path: return "Vulkan synchronization"
    if "memory" in path: return "memory mapping"
    if "rasterizer" in path or "draw" in path: return "draw/binding"
    return "other GPU or host boundary"
def symbols(root, files):
    if not files: return {}
    result = subprocess.run(["ctags","--output-format=json","--fields=+neK","--sort=no",
        "--languages=C,C++","--kinds-C++=f","--kinds-C=f","-f","-",*files],
        cwd=root, check=True, text=True, capture_output=True)
    out=collections.defaultdict(list)
    for line in result.stdout.splitlines():
        obj=json.loads(line)
        if obj.get("_type")!="tag" or "line" not in obj: continue
        name=(obj.get("scope","")+"::"+obj["name"]).lstrip(":")
        out[obj["path"]].append((name,obj["line"],obj.get("end",obj["line"])))
    return out
def scan(label,donor,host,out):
    a,b=inventory(donor),inventory(host)
    assert len(a)>100 and len(b)>100, (label,len(a),len(b))
    sa,sb=symbols(donor,sorted(a)),symbols(host,sorted(b))
    rows=[]; diffs=out/label;diffs.mkdir(parents=True)
    for p in sorted(a.keys()|b.keys()):
        x=a[p].read_text(errors="replace") if p in a else ""
        y=b[p].read_text(errors="replace") if p in b else ""
        ax={};by={}
        for name,i,j in sa.get(p,[]): ax.setdefault(name,[]).append("\n".join(x.splitlines()[i-1:j]))
        for name,i,j in sb.get(p,[]): by.setdefault(name,[]).append("\n".join(y.splitlines()[i-1:j]))
        row={"file":p,"subsystem":subsystem(p),"state":"same" if x==y else
             "different" if p in a and p in b else "donor-only" if p in a else "bachata-only",
             "donor_sha256":hashlib.sha256(x.encode()).hexdigest() if p in a else None,
             "bachata_sha256":hashlib.sha256(y.encode()).hexdigest() if p in b else None,
             "donor_only_symbols":sorted(ax.keys()-by.keys()),
             "bachata_only_symbols":sorted(by.keys()-ax.keys()),
             "changed_common_symbols":sorted(k for k in ax.keys()&by.keys() if ax[k]!=by[k])}
        rows.append(row)
        if row["state"]!="same":
            f=diffs/(p+".diff");f.parent.mkdir(parents=True,exist_ok=True)
            f.write_text("".join(difflib.unified_diff(y.splitlines(True),x.splitlines(True),
                fromfile="Bachata/"+p,tofile="Donor/"+p,n=5)))
    return {"files":rows,"counts":dict(collections.Counter(r["state"] for r in rows)),
            "subsystems":{s:dict(collections.Counter(r["state"] for r in rows if r["subsystem"]==s))
             for s in sorted({r["subsystem"] for r in rows})}}
def main():
    p=argparse.ArgumentParser()
    for name in ("order-donor","order-bachata","sotc-donor","sotc-bachata","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    result={label:scan(label,getattr(a,label+"_donor"),getattr(a,label+"_bachata"),a.out)
            for label in ("order","sotc")}
    (a.out/"inventory.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({k:{"counts":v["counts"],"subsystems":v["subsystems"]} for k,v in result.items()},indent=2))
if __name__=="__main__": main()
