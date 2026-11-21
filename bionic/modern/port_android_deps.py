#!/usr/bin/env python3
"""Integrate real Android FFmpeg/OpenAL dependencies without regressing 0.21.1 HLE."""
import argparse
from pathlib import Path

def one(path, old, new):
    content = path.read_text()
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one dependency anchor, got {count}")
    path.write_text(content.replace(old, new, 1))

def main(source):
    path = source / "externals/CMakeLists.txt"
    one(path, """# FFmpeg
if (NOT TARGET FFmpeg::ffmpeg)
    add_subdirectory(ffmpeg-core)
    add_library(FFmpeg::ffmpeg ALIAS ffmpeg)
endif()""", """# FFmpeg
if (ANDROID)
    # BIONIC_021_NDK_FFMPEG
    if (NOT BACHATA_ANDROID_FFMPEG_PREFIX)
        message(FATAL_ERROR "Android FFmpeg root must be provided")
    endif()
    add_library(ffmpeg INTERFACE)
    target_include_directories(ffmpeg INTERFACE "${BACHATA_ANDROID_FFMPEG_PREFIX}/include")
    foreach(component avformat avcodec swscale avutil avfilter swresample)
        set(ffmpeg_so "${BACHATA_ANDROID_FFMPEG_PREFIX}/lib/lib${component}.so")
        if (NOT EXISTS "${ffmpeg_so}")
            message(FATAL_ERROR "NDK FFmpeg missing: ${ffmpeg_so}")
        endif()
        target_link_libraries(ffmpeg INTERFACE "${ffmpeg_so}")
    endforeach()
    add_library(FFmpeg::ffmpeg ALIAS ffmpeg)
elseif (NOT TARGET FFmpeg::ffmpeg)
    add_subdirectory(ffmpeg-core)
    add_library(FFmpeg::ffmpeg ALIAS ffmpeg)
endif()""")
    one(path, """elseif (APPLE)
    set(ALSOFT_BACKEND_COREAUDIO ON CACHE BOOL "" FORCE)
else()
    set(ALSOFT_BACKEND_ALSA ON CACHE BOOL "" FORCE)""", """elseif (APPLE)
    set(ALSOFT_BACKEND_COREAUDIO ON CACHE BOOL "" FORCE)
elseif (ANDROID)
    # BIONIC_021_OPENAL_NO_LINUX_AUDIO
    set(ALSOFT_BACKEND_ALSA OFF CACHE BOOL "" FORCE)
    set(ALSOFT_BACKEND_PULSEAUDIO OFF CACHE BOOL "" FORCE)
    set(ALSOFT_BACKEND_PIPEWIRE OFF CACHE BOOL "" FORCE)
else()
    set(ALSOFT_BACKEND_ALSA ON CACHE BOOL "" FORCE)""")
    print("BIONIC_021_NDK_LINK_DEPENDENCIES_READY")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    main(p.parse_args().source)
