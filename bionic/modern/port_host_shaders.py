#!/usr/bin/env python3
"""Select the Linux host shader generator when cross-compiling the 0.21.1 renderer.

shadPS4's modern host_shaders CMake expects glslang-standalone from the
target build, but the Android target cannot execute an AArch64 binary on the
Ubuntu GitHub Actions runner. Keep every modern shader and use the native
Linux glslangValidator with the same --target-env/--vn/--depfile arguments.
"""
import argparse
from pathlib import Path

ANCHOR = """if (TARGET glslang-standalone)
    set(GLSLANG_COMPILER glslang-standalone)
elseif (TARGET glslang::glslang-standalone)
    set(GLSLANG_COMPILER glslang::glslang-standalone)
endif()"""

PATCHED = """if (ANDROID AND CMAKE_CROSSCOMPILING)
    # BIONIC_021_HOST_SHADER_COMPILER: run on the build HOST, not guest ARM64.
    find_program(BACHATA_HOST_GLSLANG_VALIDATOR
        NAMES glslangValidator
        PATHS /usr/bin /usr/local/bin
        NO_DEFAULT_PATH REQUIRED)
    set(GLSLANG_COMPILER "\${BACHATA_HOST_GLSLANG_VALIDATOR}")
elseif (TARGET glslang-standalone)
    set(GLSLANG_COMPILER glslang-standalone)
elseif (TARGET glslang::glslang-standalone)
    set(GLSLANG_COMPILER glslang::glslang-standalone)
endif()"""

def main(root: Path):
    p=root/"src/video_core/host_shaders/CMakeLists.txt"
    src=p.read_text()
    if "BIONIC_021_HOST_SHADER_COMPILER" in src:
        raise RuntimeError("Host shader compiler already adapted")
    count=src.count(ANCHOR)
    if count != 1:
        raise RuntimeError(f"{p}: expected one modern GLSLANG_COMPILER block, found {count}")
    p.write_text(src.replace(ANCHOR, PATCHED, 1))
    print("BIONIC_021_HOST_SHADER_COMPILER_INTEGRATED")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    main(ap.parse_args().source)
