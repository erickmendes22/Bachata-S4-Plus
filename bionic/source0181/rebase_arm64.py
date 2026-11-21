#!/usr/bin/env python3
"""Integrate actual upstream 0.18.1 PS4 GPU/HLE with proven ARM64 FEX host.

The 0.16.1 host adds Android/FEX/Bachata transport code absent in upstream.
Git's common ancestor is authoritative. Conflicts are resolved by subsystem,
never by stamping 0.18.1 on a 0.16.1 monolithic binary. The audit explicitly
records retained older code that still requires 0.18.1 API adaptation.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

UPSTREAM = "3912336fdfffbd5c99b59d92e997ea6ebd62216c"
WORKING = "be6bc2e9c60799e071dd2fafa6216e8d80ec619c"

# Legacy host interfaces are required for native FEX, socket/SAF, Vulkan WSI.
# Newer emulated GPU/shader engine and unrelated PS4 HLE use upstream 0.18.1.
KEEP_WORKING = (
    "CMakeLists.txt",
    ".gitmodules",
    "src/main.cpp",
    "src/emulator.cpp",
    "src/emulator.h",
    "src/core/linker.cpp",
    "src/core/memory.cpp",
    "src/core/address_space.cpp",
    "src/core/signals.cpp",
    "src/core/loader/",
    "src/core/file_sys/",
    "src/core/libraries/libs.cpp",
    "src/core/libraries/libs.h",
    "src/core/libraries/kernel/",
    "src/core/libraries/sysmodule/sysmodule_internal.cpp",
    "src/core/libraries/videoout/driver.cpp",
    "src/core/libraries/avplayer/avplayer_source.cpp",
    "src/common/path_util.h",
    "src/common/memory_patcher.cpp",
    "src/video_core/renderer_vulkan/vk_instance.cpp",
    "src/video_core/renderer_vulkan/vk_instance.h",
    "src/video_core/renderer_vulkan/vk_presenter.cpp",
)
# Even when the 0.16.1 ARM64 host stays in place, 0.18.1 shader and GPU files
# win on conflicts. They must be reconnected to retained platform interfaces.
USE_NEW = (
    "src/shader_recompiler/",
    "src/video_core/amdgpu/",
    "src/video_core/buffer_cache/",
    "src/video_core/renderer_vulkan/",
    "src/video_core/texture_cache/",
    "src/core/libraries/",
    "src/imgui/",
    "src/shadnet/",
    "externals/",
    "documents/",
    "tests/",
    "README.md",
)
HOST_CRITICAL = (
    "src/core/guest_cpu/fex_guest_cpu.cpp",
    "src/core/guest_cpu/fex_hle_bridge.cpp",
    "src/core/fex/fex_guest_engine.cpp",
    "src/platform/bachata/runtime_client.cpp",
    "src/video_core/renderer_vulkan/vk_platform.cpp",
    "src/core/linker.cpp",
)


def git(root: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr[-1600:]}")
    return p.stdout


def policy(path: str) -> str:
    if any(path == p or (p.endswith("/") and path.startswith(p)) for p in KEEP_WORKING):
        return "ours"
    if any(path == p or (p.endswith("/") and path.startswith(p)) for p in USE_NEW):
        return "theirs"
    return "theirs"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    actual_base = git(root, "rev-parse", "HEAD").strip()
    if actual_base != WORKING:
        raise RuntimeError("Working FEX port revision changed: "+actual_base)
    actual_upstream = git(root, "rev-parse", "FETCH_HEAD").strip()
    if actual_upstream != UPSTREAM:
        raise RuntimeError("Upstream shadPS4 0.18.1 revision changed: "+actual_upstream)
    ancestor = git(root, "merge-base", "HEAD", "FETCH_HEAD").strip()
    if not ancestor:
        raise RuntimeError("No real common ancestor for ARM64/PS4 source")
    merge = subprocess.run(["git", "-C", str(root), "merge", "--no-commit", "--no-ff", "FETCH_HEAD"],
                           capture_output=True, text=True)
    conflicts = git(root, "diff", "--name-only", "--diff-filter=U").splitlines()
    resolution = []
    for path in conflicts:
        chosen = policy(path)
        unmerged = git(root, "ls-files", "-u", "--", path).splitlines()
        # Gitlink conflicts cannot be resolved with git add on an uninitialized
        # submodule working tree: copy the selected commit SHA into the index.
        links = [line.split() for line in unmerged if line.startswith("160000 ")]
        if links:
            chosen_stage = "2" if chosen == "ours" else "3"
            matches = [item for item in links if item[2] == chosen_stage]
            if not matches:
                raise RuntimeError("Selected submodule conflict stage unavailable: "+path)
            git(root, "update-index", "--add", "--cacheinfo", "160000," + matches[0][1] + "," + path)
            resolution.append({"path":path,"strategy":chosen,"gitlink":matches[0][1]})
            continue
        r = subprocess.run(["git", "-C", str(root), "checkout", "--"+chosen, "--",path],
                           capture_output=True, text=True)
        if r.returncode:
            # Correctly handle modify/delete conflicts, including deleted tests.
            p = root / path
            if not p.exists():
                git(root, "rm", "-f", "--ignore-unmatch", "--",path)
            else:
                git(root, "add", "--",path)
        else:
            git(root, "add", "--",path)
        resolution.append({"path":path,"strategy":chosen})
    still = git(root, "diff", "--name-only", "--diff-filter=U").splitlines()
    if still:
        raise RuntimeError("Unresolved merge conflicts: "+str(still[:20]))
    # New shadPS4 0.18.1 dependencies were introduced as Git submodules.
    # The older ARM64 'ours' merge can omit gitlinks even when .gitmodules is
    # reconciled. Restore exact official gitlinks BEFORE recursive checkout.
    required_0181_gitlinks = {
        "externals/abseil-cpp": "76bb24329e8bf5f39704eb10d21b9a80befa7c81",
        "externals/protobuf": "5917ee224a7e47383a78acc129628511fe210dff",
        "externals/zarchive": "965b66c8d67b6b7e30fd63b3b75aa91a99ff303b",
        "externals/zstd": "5c7b7bad26808e6b40ac3b3d0075466e27738a9d",
    }
    for path, expected_sha in required_0181_gitlinks.items():
        original=git(root, "ls-tree", UPSTREAM, "--", path).strip()
        if original != f"160000 commit {expected_sha}\\t{path}".replace("\\t", "\t"):
            raise RuntimeError(f"Upstream 0.18.1 gitlink changed: {path}: {original}")
        git(root, "update-index", "--add", "--cacheinfo",
            f"160000,{expected_sha},{path}")
    print("REAL_SOURCE0181_GITLINKS_PINNED", sorted(required_0181_gitlinks))
    # CMake has extra ARM64/FEX support missing in upstream; we keep it but
    # explicitly move the version metadata to the actual 0.18.1 engine.
    cmake_file = root/"CMakeLists.txt"
    cmake = cmake_file.read_text()
    for part,value in (("MAJOR","0"),("MINOR","18"),("PATCH","1")):
        p = rf'(set\(EMULATOR_VERSION_{part} ")\d+("\))'
        updated,n = re.subn(p,lambda m: m.group(1)+value+m.group(2),cmake)
        if n != 1:
            raise RuntimeError(f"No unique version anchor: {part}")
        cmake = updated
    cmake_file.write_text(cmake)
    git(root, "add", "CMakeLists.txt")
    new_shader = git(root, "show", f"{UPSTREAM}:src/shader_recompiler/recompiler.cpp")
    merged_shader = (root/"src/shader_recompiler/recompiler.cpp").read_text()
    if merged_shader != new_shader:
        raise RuntimeError("Upstream 0.18.1 recompiler was not actually integrated")
    for rel in HOST_CRITICAL:
        if not (root/rel).is_file():
            raise RuntimeError("Missing FEX/Bachata or Vulkan host interface: "+rel)
    if "<<<<<<<" in cmake or ">>>>>>>" in cmake:
        raise RuntimeError("Conflict markers survived in CMakeLists")
    unmerged = git(root, "ls-files", "-u").strip()
    if unmerged:
        raise RuntimeError("Unmerged index entries remain")
    report = {
        "workingOriginal":WORKING,
        "upstreamRevision":UPSTREAM,
        "ancestor":ancestor,
        "coreVersion":"0.18.1",
        "conflictsResolved":len(resolution),
        "decisions":resolution,
        "retainedOldFexHostNeedsApiPort":True,
        "newShaderRecompilerExactlyUpstream0181":True,
        "note":"Source integration prepared; actual NDK link and Android boot still required",
    }
    (output/"rebase-report.json").write_text(json.dumps(report,indent=2)+"\n")
    (output/"source-status.txt").write_text(git(root,"status","--short"))
    (output/"source-diffstat.txt").write_text(git(root,"diff","--cached","--stat"))
    print("SOURCE_SHADPS4_0181_REAL_ENGINE_FEX_PORT_GRAFTED",len(resolution))
    print(json.dumps({"ancestor":ancestor,"resolved":len(resolution),
                      "strategies":{"ours":sum(x["strategy"]=="ours" for x in resolution),
                                    "theirs":sum(x["strategy"]=="theirs" for x in resolution)}}))
if __name__ == "__main__":
    main()
