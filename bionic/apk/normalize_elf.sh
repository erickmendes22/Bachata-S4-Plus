#!/usr/bin/env bash
# Normalize the Android FFmpeg DT_SONAME and DT_NEEDED library names:
# Android PackageManager must extract native libs as lib*.so.
set -euo pipefail
LIBDIR="$1"
test -d "$LIBDIR"
command -v patchelf >/dev/null
command -v readelf >/dev/null

shopt -s nullglob
for component in avutil swresample swscale avcodec avformat avfilter; do
  base="lib$component.so"
  f="$LIBDIR/$base"
  test -s "$f" || { echo "Missing native FFmpeg component $base" >&2; exit 1; }
  soname="$(patchelf --print-soname "$f")"
  if [[ -n "$soname" && "$soname" != "$base" ]]; then
    patchelf --set-soname "$base" "$f"
    for target in "$LIBDIR"/*.so; do
      if patchelf --print-needed "$target" | grep -Fxq "$soname"; then
        patchelf --replace-needed "$soname" "$base" "$target"
      fi
    done
  fi
  rm -f "$LIBDIR/$base".*
done

for f in "$LIBDIR"/*.so; do
  readelf -h "$f" | grep -q 'AArch64' || {
    echo "Non AArch64 ELF: $f" >&2; exit 1;
  }
  if readelf -d "$f" | grep -Eq 'Shared library: \[(libc.so.6|ld-linux-aarch64.so)'; then
    echo "Linux/glibc dependency in Android artifact $f" >&2; exit 1;
  fi
done

for f in libbachata_native_runtime.so libbachata_bionic_core.so; do
  test -s "$LIBDIR/$f" || { echo "Missing $f" >&2; exit 2; }
  for method in run stop; do
    if ! readelf -Ws "$LIBDIR/$f" |
      grep -q "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_$method$"; then
      echo "Required JNI symbol missing: $f $method" >&2; exit 2
    fi
  done
done
echo 'BIONIC_ELF_NORMALIZED: versionless FFmpeg and exact JNI ABI'
