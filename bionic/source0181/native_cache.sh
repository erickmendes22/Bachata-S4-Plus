#!/usr/bin/env bash
# Cross-run native prerequisite cache, independently of shadPS4 C++ objects.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="${WORK:-$ROOT/out/bionic}"
PORT="${PORT:-$ROOT/port}"
NDK="${NDK:-${ANDROID_HOME:?ANDROID_HOME required}/ndk/30.0.14904198}"
STAGE="$WORK/stage"
MARKER="$STAGE/BACHATA_NATIVE_PREREQS_ID"
FEX_REV=f2b679f6028ce1c38875233aecfcf5d3f8ebecec
ADT_REV=8fae8ce254dfc1344527e05301e43f37dea2df80
LEGACY_PORT_REV=148656bc7ae1b8b482d95e33d49f0729421ff477
test -s "$NDK/source.properties"
PORT_REV="$(git -C "$PORT" rev-parse HEAD)"
FINGERPRINT="$(
  { git -C "$ROOT" hash-object bionic/build-core.sh
    printf '%s\n' "$PORT_REV"
    sha256sum "$NDK/source.properties"
  } | sha256sum | cut -d' ' -f1
)"
fex_ok() {
  # The linker requires this archive even if the APK runtime stage is valid.
  test -s "$WORK/fex-android/FEXCore/Source/libFEXCore.a" || return 1
  [[ "$(git -C "$WORK/fex" rev-parse HEAD 2>/dev/null || true)" == "$FEX_REV" ]] || return 1
}
deps_ok() {
  # Native CMake needs development libs+headers; the APK stage contains
  # only runtime copies and is insufficient to configure shadPS4.
  local prefix="$WORK/deps/prefix" lib header
  for lib in avformat avcodec avutil avfilter swscale swresample; do
    test -s "$prefix/lib/lib${lib}.so" || return 1
  done
  for header in libavformat/avformat.h libavcodec/avcodec.h \
                libavutil/avutil.h libavfilter/avfilter.h \
                libswscale/swscale.h libswresample/swresample.h; do
    test -s "$prefix/include/$header" || return 1
  done
}
stage_ok() {
  local lib
  for lib in libbbgpu.so libmain.so libbbprepare.so libSDL3.so \
      libavformat.so libavcodec.so libavutil.so libavfilter.so \
      libswscale.so libswresample.so libc++_shared.so; do
    test -s "$STAGE/lib/arm64-v8a/$lib" || return 1
  done
  test -s "$STAGE/tools/ps4-bionic-probe" || return 1
  readelf -h "$STAGE/lib/arm64-v8a/libmain.so" | grep -q AArch64 || return 1
  readelf -d "$STAGE/lib/arm64-v8a/libmain.so" | grep -Fq 'Shared library: [libc.so]' || return 1
}
restage_ok() {
  local lib
  [[ "$PORT_REV" == "$LEGACY_PORT_REV" ]] || return 1
  [[ "$(git -C "$WORK/fex" rev-parse HEAD 2>/dev/null || true)" == "$FEX_REV" ]] || return 1
  [[ "$(git -C "$WORK/libadrenotools" rev-parse HEAD 2>/dev/null || true)" == "$ADT_REV" ]] || return 1
  test -s "$WORK/adrenotools-android/libadrenotools.a" || return 1
  fex_ok || return 1
  deps_ok || return 1
  for lib in libbbgpu.so libmain.so libbbprepare.so bb-probe; do
    test -s "$WORK/gpu-build/$lib" || return 1
  done
  for lib in libSDL3.so libavformat.so libavcodec.so libavutil.so \
      libavfilter.so libswscale.so libswresample.so; do
    test -s "$WORK/deps/prefix/lib/$lib" || return 1
  done
  readelf -h "$WORK/gpu-build/libmain.so" | grep -q AArch64 || return 1
  readelf -d "$WORK/gpu-build/libmain.so" | grep -Fq 'Shared library: [libc.so]' || return 1
}
case "${1:-}" in
  check)
    if stage_ok && fex_ok && deps_ok; then
      if [[ -s "$MARKER" && "$(cat "$MARKER")" == "$FINGERPRINT" ]]; then
        echo ready
      elif restage_ok; then
        echo restage
      else
        echo rebuild
      fi
    elif stage_ok && ! fex_ok && [[ "$(git -C "$PORT" rev-parse HEAD 2>/dev/null || true)" == "$LEGACY_PORT_REV" ]]; then
      echo repair_fex
    elif stage_ok && fex_ok && ! deps_ok; then
      echo repair_ffmpeg
    elif restage_ok; then
      echo restage
    else
      echo rebuild
    fi ;;
  stamp)
    stage_ok || { echo "::error::Native stage incomplete, refusing to cache" >&2; exit 2; }
    fex_ok || { echo "::error::FEXCore libFEXCore.a missing: cannot cache invalid prerequisites" >&2; exit 2; }
    deps_ok || { echo "::error::FFmpeg development headers/shared libraries missing: refuse cache stamp" >&2; exit 2; }
    printf '%s\n' "$FINGERPRINT" > "$MARKER"
    echo "BIONIC_NATIVE_PREREQS_VERIFIED=$FINGERPRINT" >&2 ;;
  *) echo "Usage: $0 check|stamp" >&2; exit 2 ;;
esac
