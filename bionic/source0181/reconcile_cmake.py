#!/usr/bin/env python3
"""Reconcile real 0.18.1 CMake source lists with proven ARM64/FEX host."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

REGISTRY = re.compile(r"(?ms)^set\(([A-Z][A-Z0-9_]*)[ \t]+([^\n)]*)\n(.*?)^\)")
SOURCE = re.compile(r"src/[A-Za-z0-9_./+-]+\.(?:c|cc|cpp|h|hpp)\b")
SPECIAL_GENERATED = {"src/common/scm_rev.cpp"}
UPSTREAM_0181 = "3912336fdfffbd5c99b59d92e997ea6ebd62216c"


def cmake_groups(content: str) -> dict:
    return {m.group(1):m for m in REGISTRY.finditer(content) if SOURCE.search(m.group(0))}


def reconcile(root: Path) -> dict:
    cmake = root / "CMakeLists.txt"
    current = cmake.read_text()
    upstream = subprocess.check_output(
        ["git","-C",str(root),"show",UPSTREAM_0181+":CMakeLists.txt"],text=True)
    old_groups = cmake_groups(current)
    upstream_groups = cmake_groups(upstream)
    changes=[]
    missing_required=[]
    restored_from_upstream=[]
    replacements=[]
    def ensure_new_upstream_file(ref: str) -> bool:
        target=root/ref
        if target.is_file():
            return True
        # The 0.16.1 port deliberately chooses 'ours' for some directories
        # during a Git merge. Preserve host overrides, but restore NEW
        # upstream 0.18.1 source files that never existed in that host.
        p=subprocess.run(["git","-C",str(root),"show",UPSTREAM_0181+":"+ref],
                         capture_output=True)
        if p.returncode:
            return False
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(p.stdout)
        restored_from_upstream.append(ref)
        return True
    for group,m in old_groups.items():
        block=m.group(0)
        upstream_group=upstream_groups.get(group)
        old_refs=list(dict.fromkeys(SOURCE.findall(block)))
        new_refs=list(dict.fromkeys(SOURCE.findall(upstream_group.group(0)))) if upstream_group else []
        corrected=block
        removed=[]
        added=[]
        for ref in old_refs:
            if ref in SPECIAL_GENERATED or (root/ref).is_file():continue
            if ref in new_refs:
                missing_required.append({"group":group,"file":ref,"reason":"upstream expects source missing in merge"})
                continue
            corrected=corrected.replace(ref,"",1)
            removed.append(ref)
        for ref in new_refs:
            if ref in SPECIAL_GENERATED:
                continue
            if not ensure_new_upstream_file(ref):
                missing_required.append({"group":group,"file":ref,"reason":"upstream source absent from Git revision"})
                continue
            if ref in old_refs:continue
            if ref not in corrected:added.append(ref)
        if added:
            at=corrected.rfind("\n)")
            if at<0:raise RuntimeError("Malformed group "+group)
            corrected=corrected[:at]+"\n"+"\n".join("           "+x for x in added)+corrected[at:]
        if added or removed:
            replacements.append((m.start(),m.end(),corrected))
            changes.append({"group":group,"obsoleteRemoved":removed,"upstream0181Added":added})
    for start,end,body in reversed(replacements):
        current=current[:start]+body+current[end:]

    if "${SHADNET}" not in current and "src/shadnet/client.cpp" in upstream:
        begin=upstream.index("# shadNet protobuf generation")
        finish=upstream.index("if (APPLE)",begin)
        block=upstream[begin:finish]
        # The Android JNI overlay converts upstream executable into a shared ELF.
        marker="if(NOT ENABLE_TESTS)\n\nadd_library(shadps4 SHARED"
        if current.count(marker)!=1:raise RuntimeError("shadPS4 executable declaration changed")
        current=current.replace(marker,block+marker,1)
        marker2="    ${EMULATOR}\n    src/main.cpp"
        if current.count(marker2)!=1:raise RuntimeError("shadPS4 source list changed")
        current=current.replace(marker2,"    ${EMULATOR}\n    ${SHADNET}\n    src/main.cpp",1)
        label="create_target_directory_groups(shadps4)"
        if current.count(label)!=1:raise RuntimeError("shadPS4 target declaration changed")
        current=current.replace(label,
            label+'\ntarget_link_libraries(shadps4 PRIVATE libprotobuf ZArchive::zarchive)\n'
            'target_include_directories(shadps4 PRIVATE "${SHADNET_PROTO_OUT}")',1)
        changes.append({"group":"SHADNET","upstream0181Added":["protobuf generator","client.cpp","server_probe.cpp"]})
    if missing_required:
        raise RuntimeError("Missing required 0.18.1 sources: "+json.dumps(missing_required[:24]))
    cmake.write_text(current)
    unresolved=[x for x in set(SOURCE.findall(current))
                if x not in SPECIAL_GENERATED and not (root/x).is_file()]
    if unresolved:raise RuntimeError("Obsolete CMake file list: "+str(sorted(unresolved)[:30]))
    if "src/common/bit_array.h" in current:
        raise RuntimeError("Old 0.16.1 bit_array.h source still registered")
    if "src/shader_recompiler/ir/passes/lower_wave64_pass.cpp" not in current:
        raise RuntimeError("0.18.1 shader pass not linked")
    return {
      "originalGroups":len(old_groups),
      "upstreamGroups":len(upstream_groups),
      "changedGroups":len(changes),
      "adjustments":changes,
      "missingUpstreamSourcesRestored":restored_from_upstream,
      "sourceVersion":"0.18.1",
      "FexHostKept":(root/"src/core/fex/fex_guest_engine.cpp").is_file(),
      "shadNetCompiled":"${SHADNET_PROTO_OUT}/shadnet.pb.cc" in current,
    }
