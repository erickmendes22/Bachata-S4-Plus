#!/usr/bin/env python3
"""Separate infrastructure inherited from PC donors, Android adaptation and regressions.
Never treat textual identity as functional parity; never import a CPU runtime.
"""
import argparse, collections, hashlib, json
from pathlib import Path
from source_parity import inventory, symbols, subsystem, EXT

def functions(root):
    assert root.is_dir(), root
    files=inventory(root)
    assert len(files)>100, (root,len(files))
    tags=symbols(root,sorted(files))
    out={}
    for path,p in files.items():
        lines=p.read_text(errors="replace").splitlines()
        by=collections.defaultdict(list)
        for name,i,j in tags.get(path,[]):
            if "__anon" in name: continue
            code="\n".join(lines[i-1:j])
            by[name].append(hashlib.sha256(code.encode()).hexdigest())
        out[path]={name:sorted(v) for name,v in by.items()}
    return out

def classify(pc,android,base,current):
    rows=[]
    for path in sorted(pc.keys()|android.keys()|base.keys()|current.keys()):
        p,a,b,c=(d.get(path,{}) for d in (pc,android,base,current))
        for name in sorted(p.keys()|a.keys()|b.keys()|c.keys()):
            pv,av,bv,cv=(d.get(name) for d in (p,a,b,c))
            if not av or av==cv: continue
            origin="inherited-PC" if pv==av else "Android-modified" if pv else "Android-added"
            state="regressed-from-exact-match" if bv==av else "unchanged-gap" if bv==cv else "changed-but-not-identical"
            rows.append({"file":path,"symbol":name,"subsystem":subsystem(path),
                         "origin":origin,"state":state,"current_missing":cv is None,
                         "baseline_missing":bv is None,"pc":pv,"android":av,"baseline":bv,"current":cv})
    return rows

def main():
    p=argparse.ArgumentParser()
    for label in ("order","sotc"):
        for suffix in ("pc","android","current","baseline","shim"):
            p.add_argument(f"--{label}-{suffix}",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    results={}
    for label in ("order","sotc"):
        pc,android,base,current=(functions(getattr(a,label+"_"+k)) for k in ("pc","android","baseline","current"))
        rows=classify(pc,android,base,current)
        shim=getattr(a,label+"_shim")
        assert shim.is_dir(), shim
        shim_files=[str(f.relative_to(shim)) for f in shim.rglob("*") if f.is_file() and f.suffix in EXT]
        results[label]={"functions":rows,"origin_counts":dict(collections.Counter(r["origin"] for r in rows)),
                        "state_counts":dict(collections.Counter(r["state"] for r in rows)),
                        "shim_files_separate_CPU_boundary_audit":sorted(shim_files)}
        (a.out/(label+".json")).write_text(json.dumps(results[label],indent=2))
    left={(r["file"],r["symbol"]):r for r in results["order"]["functions"]}
    right={(r["file"],r["symbol"]):r for r in results["sotc"]["functions"]}
    common=[]
    for key in sorted(left.keys()&right.keys()):
        x,y=left[key],right[key]
        common.append({"file":key[0],"symbol":key[1],"subsystem":x["subsystem"],
                       "same_donor_implementation":x["android"]==y["android"],
                       "both_inherited_PC":x["origin"]==y["origin"]=="inherited-PC",
                       "order_origin":x["origin"],"sotc_origin":y["origin"]})
    (a.out/"shared-gaps.json").write_text(json.dumps(common,indent=2))
    summary={k:{"origins":v["origin_counts"],"states":v["state_counts"],
                "shim_files":len(v["shim_files_separate_CPU_boundary_audit"])} for k,v in results.items()}
    summary["common"]={"count":len(common),"same_donor":sum(x["same_donor_implementation"] for x in common),
                       "both_inherited":sum(x["both_inherited_PC"] for x in common)}
    (a.out/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
