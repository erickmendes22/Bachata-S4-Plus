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
        # protoc is a BUILD-HOST executable. In the Android cross-toolchain
        # protobuf::protoc would be an AArch64 binary and cannot run on Ubuntu.
        block=block.replace(
            "    COMMAND protobuf::protoc\n",
            '    COMMAND "${BACHATA_HOST_PROTOC_EXECUTABLE}"\n',
        )
        if "protobuf::protoc" in block:
            raise RuntimeError("Cross-compiled ARM64 protoc still in host generator")
        block=(
            'if(ANDROID)\n'
            '    # Do not trust a restored CMakeCache.txt: older builds cached\n'
            '    # /usr/bin/protoc even after host protoc 36 was installed.\n'
            '    find_program(BACHATA_HOST_PROTOC_EXECUTABLE NAMES protoc NO_CMAKE_FIND_ROOT_PATH)\n'
            '    if(NOT BACHATA_HOST_PROTOC_EXECUTABLE OR\n'
            '       NOT EXISTS "${BACHATA_HOST_PROTOC_EXECUTABLE}")\n'
            '        message(FATAL_ERROR "Missing host protoc for 0.18.1 shadNet: ${BACHATA_HOST_PROTOC_EXECUTABLE}")\n'
            '    endif()\n'
            '    execute_process(COMMAND "${BACHATA_HOST_PROTOC_EXECUTABLE}" --version\n'
            '        RESULT_VARIABLE BACHATA_PROTOC_RESULT\n'
            '        OUTPUT_VARIABLE BACHATA_PROTOC_VERSION OUTPUT_STRIP_TRAILING_WHITESPACE)\n'
            '    if(NOT BACHATA_PROTOC_RESULT EQUAL 0 OR\n'
            '       NOT BACHATA_PROTOC_VERSION STREQUAL "libprotoc 36.0-dev")\n'
            '        message(FATAL_ERROR "shadNet requires host protoc 36.0, got: ${BACHATA_HOST_PROTOC_EXECUTABLE} (${BACHATA_PROTOC_VERSION})")\n'
            '    endif()\n'
            '    message(STATUS "BACHATA_HOST_PROTOC_VERIFIED=${BACHATA_HOST_PROTOC_EXECUTABLE} (${BACHATA_PROTOC_VERSION})")\n'
            'endif()\n'
        )+block
        # This entire new component did not exist in the FEX 0.16.1 build.
        # All its real 0.18.1 source files must be restored, not stubbed.
        for ref in set(SOURCE.findall(block)):
            if not ensure_new_upstream_file(ref):
                missing_required.append({"group":"SHADNET","file":ref,"reason":"missing real upstream shadNet source"})
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
    # Restore the 0.18.1 host networking and zarchive static build targets.
    # The older FEX externals CMake file never declared those dependencies,
    # even though the upstream shader and filesystem code now require them.
    ext_file=root/"externals"/"CMakeLists.txt"
    ext_current=ext_file.read_text()
    ext_new=subprocess.check_output(
        ["git","-C",str(root),"show",UPSTREAM_0181+":externals/CMakeLists.txt"],
        text=True)
    if "add_subdirectory(protobuf" not in ext_current:
        section=ext_new[ext_new.index("# abseil (for protobuf)"):]
        ext_current=ext_current.rstrip()+"\n\n"+section
        changes.append({"group":"PROTOBUF_ZARCHIVE","externalUpstream0181":"added both libraries"})
    elif "add_library(ZArchive::zarchive" not in ext_current:
        section=ext_new[ext_new.index("# ZArchive (.zar archive support)"):]
        ext_current=ext_current.rstrip()+"\n\n"+section
        changes.append({"group":"ZARCHIVE","externalUpstream0181":"added zstd + zarchive"})
    ext_file.write_text(ext_current.rstrip()+"\n")
    # Android NDK CMake would otherwise generate a target AArch64 ImGui
    # font encoder and attempt to execute it on the Ubuntu x86_64 runner.
    # Use the real HOST binary already compiled in build-generic.sh.
    font_cmake=root/"src/imgui/renderer/CMakeLists.txt"
    font_text=font_cmake.read_text()
    font_target="add_executable(Dear_ImGui_FontEmbed ${CMAKE_SOURCE_DIR}/externals/imgui/misc/fonts/binary_to_compressed_c.cpp)"
    if font_text.count(font_target)!=1:
        raise RuntimeError("0.18.1 ImGui font target structure changed")
    font_text=font_text.replace(font_target,
        'if(ANDROID)\n'
        '    if(NOT EXISTS "${IMGUI_FONT_EMBED_EXECUTABLE}")\n'
        '        message(FATAL_ERROR "Host ImGui font encoder is missing")\n'
        '    endif()\n'
        '    add_executable(Dear_ImGui_FontEmbed IMPORTED GLOBAL)\n'
        '    set_target_properties(Dear_ImGui_FontEmbed PROPERTIES\n'
        '        IMPORTED_LOCATION "${IMGUI_FONT_EMBED_EXECUTABLE}")\n'
        'else()\n'
        '    '+font_target+'\n'
        'endif()',1)
    font_cmake.write_text(font_text)
    # glslang::glslang-standalone is an Android executable under NDK.
    # The host shader generator runs at BUILD time on the Linux runner and
    # must resolve its own x86_64 glslangValidator via NO_CMAKE_FIND_ROOT_PATH.
    shader_cmake=root/"src/video_core/host_shaders/CMakeLists.txt"
    shader_text=shader_cmake.read_text()
    marker="set(SHADER_INCLUDE ${CMAKE_CURRENT_BINARY_DIR}/include)"
    if shader_text.count(marker)!=1:
        raise RuntimeError("0.18.1 host shader CMake structure changed")
    shader_text=shader_text.replace(marker,
        'if(ANDROID)\n'
        '    find_program(BACHATA_HOST_GLSLANG_VALIDATOR\n'
        '        NAMES glslangValidator NO_CMAKE_FIND_ROOT_PATH REQUIRED)\n'
        '    set(GLSLANG_COMPILER "${BACHATA_HOST_GLSLANG_VALIDATOR}")\n'
        'endif()\n\n'+marker,1)
    shader_cmake.write_text(shader_text)
    changes.append({"group":"CROSS_COMPILE_BUILD_TOOLS",
        "hostTools":["ImGui font encoder x86_64","glslangValidator x86_64"]})
    if "add_subdirectory(protobuf" not in ext_current or "add_library(ZArchive::zarchive" not in ext_current:
        raise RuntimeError("Full 0.18.1 external zarchive and protobuf source targets missing")
    # The old ARM64 fork registered a separate per-file no-LTO rule for
    # vk_dispatch_reload.cpp. 0.18.1 no longer has this translation unit.
    # Drop BOTH the source entry (handled above) and its orphaned property
    # declaration; otherwise CMake still references a non-existent file.
    old_vk_dispatch_rule = '''set_source_files_properties(
    src/video_core/buffer_cache/vk_dispatch_reload.cpp
    PROPERTIES COMPILE_FLAGS "-fno-lto"
)
'''
    if not (root/"src/video_core/buffer_cache/vk_dispatch_reload.cpp").is_file():
        if old_vk_dispatch_rule in current:
            current = current.replace(old_vk_dispatch_rule, "", 1)
            changes.append({"group":"OBSOLETE_ARM64_DISPATCH_RULE",
                            "removed":"vk_dispatch_reload.cpp no-LTO registration"})
    # Removing obsolete 0.16.1 entries may leave whitespace-only lines.
    # Normalize trailing spaces before strict git diff --check preflight.
    current="\n".join(line.rstrip() for line in current.split("\n"))
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
