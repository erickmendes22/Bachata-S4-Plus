#!/usr/bin/env python3
"""Integrate the full 0.21.1 FEX/HLE core with the Bachata Android JNI host.

The modern source already owns BSF1 SAF, IPC, FEX guest HLE, and the renderer.
Do not apply the legacy 0.16.1 libc/SAF/renderer overlays over them.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def once(path: Path, old: str, new: str) -> None:
    data = path.read_text()
    hits = data.count(old)
    if hits != 1:
        raise RuntimeError(f"{path}: expected one exact anchor, got {hits}: {old[:100]!r}")
    path.write_text(data.replace(old, new, 1))


def integrate(source: Path, overlay: Path) -> None:
    required = ("android_surface.h", "android_window.cpp", "android_native_core.cpp")
    for name in required:
        if not (overlay / name).is_file():
            raise RuntimeError(f"Missing Bachata JNI/native window implementation: {name}")

    main = source / "src/main.cpp"
    # NDK Bionic does not expose glibc execinfo; keep Linux backtraces, and
    # record host PC/LR/SP on Android. Do not alter FEX guest signal handling.
    if "#include <execinfo.h>" in main.read_text():
        once(main, "#include <execinfo.h>\n",
             "#ifndef __ANDROID__\n#include <execinfo.h>\n#endif\n")
    old_frames = (
        "        void* frames[64];\n"
        "        const int count = ::backtrace(frames, 64);\n"
        "        ::backtrace_symbols_fd(frames, count, fd);\n"
    )
    if old_frames in main.read_text():
        android_frames = """#ifdef __ANDROID__
        const auto* context = reinterpret_cast<const ucontext_t*>(uctx);
        if (context != nullptr) {
            char where[192];
            const int n = ::snprintf(where, sizeof(where),
                "BIONIC_021_CRASH pc=%#llx lr=%#llx sp=%#llx\\n",
                static_cast<unsigned long long>(context->uc_mcontext.pc),
                static_cast<unsigned long long>(context->uc_mcontext.regs[30]),
                static_cast<unsigned long long>(context->uc_mcontext.sp));
            if (n > 0 && n < static_cast<int>(sizeof(where)))
                ::write(fd, where, static_cast<size_t>(n));
        }
#else
"""
        once(main, old_frames, android_frames + old_frames + "#endif\n")

    # Keep upstream modern SAF, IPC, guest FEX and main CLI logic untouched.
    if "int BachataCoreMain(int argc, char* argv[])" not in main.read_text():
        once(main, "int main(int argc, char* argv[]) {",
             "int BachataCoreMain(int argc, char* argv[]) {")

    emulator = source / "src/emulator.cpp"
    if "BIONIC_021_RETURN_FROM_EMULATOR" not in emulator.read_text():
        once(emulator, "    std::quick_exit(0);\n}\n\nvoid Emulator::Restart(",
             """#if defined(__ANDROID__)
    // A Java-owned process must return to JNI before ANativeWindow_release.
    // BIONIC_021_RETURN_FROM_EMULATOR
    Shutdown();
    return;
#else
    std::quick_exit(0);
#endif
}

void Emulator::Restart(""")

    cmake = source / "CMakeLists.txt"
    data = cmake.read_text()
    if "BIONIC_021_ANDROID_NATIVE_CORE" in data:
        raise RuntimeError("Modern Bionic native core overlay already applied")

    if data.count("add_executable(shadps4\n") != 1:
        raise RuntimeError("0.21.1 core target has changed: cannot safely create Android .so")
    data = data.replace("add_executable(shadps4\n", "add_library(shadps4 SHARED\n", 1)

    window_src = "src/sdl_window.cpp"
    if data.count(window_src) < 1:
        raise RuntimeError("Missing 0.21.1 SDL frontend source")
    data = data.replace(window_src, "${BACHATA_ANDROID_WINDOW_SOURCE}")
    window_decl = 'set(BACHATA_ANDROID_WINDOW_SOURCE "' + str(overlay / "android_window.cpp") + '")\n'
    if data.count("if(NOT ENABLE_TESTS)\n") != 1:
        raise RuntimeError("Missing 0.21.1 main build target guard")
    data = data.replace("if(NOT ENABLE_TESTS)\n",
                        window_decl + "if(NOT ENABLE_TESTS)\n", 1)

    anchor = "create_target_directory_groups(shadps4)"
    if data.count(anchor) != 1:
        raise RuntimeError("Missing 0.21.1 target sources anchor")
    additions = (
        "# BIONIC_021_ANDROID_NATIVE_CORE\n"
        'target_sources(shadps4 PRIVATE "' + str(overlay / "android_native_core.cpp") + '")\n'
        'target_include_directories(shadps4 PRIVATE "' + str(overlay) + '")\n'
        "target_compile_definitions(shadps4 PRIVATE ANDROID=1)\n"
        "target_link_libraries(shadps4 PRIVATE android log)\n"
        'set_target_properties(shadps4 PROPERTIES OUTPUT_NAME "bachata_bionic_core")\n'
    )
    data = data.replace(anchor, additions + anchor, 1)

    old_link = "    target_link_libraries(shadps4 PRIVATE ${FEXCORE_GUEST_CPU_LIBRARIES} pthread dl)\n"
    if data.count(old_link) != 1:
        raise RuntimeError("0.21.1 FEX link dependencies changed")
    new_link = """    if(ANDROID)
        # Android Bionic provides pthread in libc; libpthread.so is a Linux shim.
        target_link_libraries(shadps4 PRIVATE ${FEXCORE_GUEST_CPU_LIBRARIES} dl)
    else()
        target_link_libraries(shadps4 PRIVATE ${FEXCORE_GUEST_CPU_LIBRARIES} pthread dl)
    endif()
"""
    data = data.replace(old_link, new_link, 1)
    cmake.write_text(data)
    assert "BIONIC_021_ANDROID_NATIVE_CORE" in data
    assert 'OUTPUT_NAME "bachata_bionic_core"' in data
    assert "src/sdl_window.cpp" not in data
    print("BIONIC_021_JNI_FULL_CORE_SOURCE_INTEGRATED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--overlay", default="bionic/generic", type=Path)
    args = ap.parse_args()
    integrate(args.source.resolve(), args.overlay.resolve())
