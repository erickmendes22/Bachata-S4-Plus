#!/usr/bin/env python3
"""Collect ALL former 0.16.1 Bionic integration anchors changed by shadPS4 0.18.1.

The original overlay intentionally insists on pinned source anchors. In 0.18.1
some patches are already upstream, some require API adaptation. Never pretend
a missing integration anchor is a successfully ported runtime feature.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    args=p.parse_args()
    base=Path(__file__).resolve().parents[1]
    file=base/"generic"/"port_generic.py"
    spec=importlib.util.spec_from_file_location("bachata_original_bionic_port",file)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load original complete Bionic patchset")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    misses=[]
    default_replace=mod.replace

    def record_replace(path:Path,old:str,new:str,count:int=1)->None:
        source=path.read_text(encoding="utf-8")
        actual=source.count(old)
        if actual!=count:
            misses.append({"source":str(path),"expected":count,"found":actual,
                           "anchor":old[:450],"replacement":new[:450]})
            return
        default_replace(path,old,new,count)

    mod.replace=record_replace
    error=None
    try:
        mod.apply(args.source.resolve(),base/"generic")
    except Exception as e:
        error=repr(e)
    report={
        "target":"real shadPS4 0.18.1 ARM64 Bionic",
        "sourcePatch":"bionic/generic/port_generic.py",
        "outdatedIntegrationAnchors":misses,
        "otherError":error,
        "auditPassed":not misses and error is None,
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(f"SHADPS4_0181_ANDROID_FEX_PORT_UNRESOLVED_ANCHORS={len(misses)}")
    for a in misses:
        print("UNRESOLVED",a["source"],repr(a["anchor"][:110]))
    if error:
        print("ADDITIONAL_INTEGRATION_ERROR",error)
    if misses or error:
        raise SystemExit(2)
    print("SHADPS4_0181_BIONIC_PORT_ALL_ANCHORS_APPLIED")


if __name__=="__main__":
    main()
