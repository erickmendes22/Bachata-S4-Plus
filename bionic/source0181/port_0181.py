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
import subprocess
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
    already_upstream=[]
    default_replace=mod.replace

    def record_replace(path:Path,old:str,new:str,count:int=1)->None:
        source=path.read_text(encoding="utf-8")
        actual=source.count(old)
        if actual!=count:
            # Modern 0.18.1 moved both page/cache locks to std::mutex when
            # PTHREAD_ADAPTIVE_MUTEX_INITIALIZER_NP is unavailable. Android
            # Bionic thus already has a valid concrete lock type here.
            if path.name == "region_manager.h" and "common/spin_lock.h" in old:
                if '#include "common/adaptive_mutex.h"' in source and \
                        "using LockType = std::mutex;" in source:
                    already_upstream.append(str(path))
                    return
            if path.name == "page_manager.cpp" and '#include "common/range_lock.h"' in old:
                if '#include "common/adaptive_mutex.h"' in source and \
                        "using Entry = std::mutex;" in source:
                    already_upstream.append(str(path))
                    return
            # The modern 0.18.1 IBackend VFS has a different directory
            # implementation. Its full SAF adapter runs after the generic
            # platform overlay; never apply the obsolete 0.16.1 text patch.
            if path.name == "fs.cpp" and path.parent.name == "file_sys":
                if "class MergedDirectory final" in source and "MntPoints::OpenDir(" in source:
                    if "callback(entry.path(), !entry.is_directory());" in old or \
                            "Pass 3: Any files that exist only in the mod directory" in old:
                        already_upstream.append(str(path)+" (0.18 VFS replacement pending)")
                        return
            misses.append({"source":str(path),"expected":count,"found":actual,
                           "anchor":old[:450],"replacement":new[:450]})
            return
        default_replace(path,old,new,count)

    mod.replace=record_replace
    error=None
    source_registry=None
    modern_fs_adapter=None
    arm64_host_adapter=None
    modern_api_adapter=None
    try:
        mod.apply(args.source.resolve(),base/"generic")
        if not misses:
            from modern_saf_port import apply as apply_modern_saf
            modern_fs_adapter=apply_modern_saf(args.source.resolve())
            from arm64_signal_port import apply as apply_arm64_signal
            arm64_host_adapter=apply_arm64_signal(args.source.resolve())
            # Reconcile every independent 0.16->0.18 public API found by
            # full NDK compilation, not just the first failing translation unit.
            from compatibility_port import apply as apply_modern_apis
            modern_api_adapter=apply_modern_apis(args.source.resolve())
            # Apply the checked effective-source delta only after all base overlays.
            donor_delta = Path(__file__).resolve().with_name("effective-sotc-donor.patch")
            subprocess.run(["git", "apply", "--check", str(donor_delta)], cwd=args.source.resolve(), check=True)
            subprocess.run(["git", "apply", str(donor_delta)], cwd=args.source.resolve(), check=True)
            from port_depth_layout_contract import apply as apply_depth_layout
            print("BACHATA_SOTC_DEPTH_LAYOUT_CONTRACT", apply_depth_layout(args.source.resolve()))
            print("BACHATA_EFFECTIVE_DONOR_DELTA_SOTC_APPLIED")
            from port_sotc_sampled_sets import apply as apply_sampled_sets
            apply_sampled_sets(args.source.resolve())
            from reconcile_cmake import reconcile
            source_registry=reconcile(args.source.resolve())
            print("REAL_SHADPS4_0181_CMAKE_REGISTRY_RECONCILED",source_registry["changedGroups"])
    except Exception as e:
        error=repr(e)
    report={
        "target":"real shadPS4 0.18.1 ARM64 Bionic",
        "sourcePatch":"bionic/generic/port_generic.py",
        "outdatedIntegrationAnchors":misses,
        "modernizedLockFallbacksVerified":already_upstream,
        "otherError":error,
        "cmakeSourceRegistry":source_registry,
        "modernFsSafAdapter":modern_fs_adapter,
        "arm64SignalAdapter":arm64_host_adapter,
        "modern0181ApiReconciliation":modern_api_adapter,
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
