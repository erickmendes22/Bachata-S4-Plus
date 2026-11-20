#!/usr/bin/env bash
# Bachata S4+ experimental native Bionic core, derived from the working
# Uncharted Android port's generic FEX/PS4 memory/GPU components.
# This builds real Android ELF objects, NOT the original 0.2.5 binary and
# NOT (yet) a drop-in replacement for NativeRuntimeBridge.run.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-$ROOT/port}"
WORK="${WORK:-$ROOT/out/bionic}"
NDK="${NDK:?Set NDK to Android NDK r30 root}"
export NDK
mkdir -p "$WORK" "$WORK/stage/lib/arm64-v8a" "$WORK/stage/tools"
test -f "$PORT/gpu/CMakeLists.txt" || { echo "Missing port source: $PORT" >&2; exit 2; }
grep -q 'Pkg.ReleaseName = r30' "$NDK/source.properties" || { echo "NDK r30 is required" >&2; exit 2; }
for cmd in git cmake ninja python3 curl tar bison flex pkg-config glslangValidator; do
  command -v "$cmd" >/dev/null || { echo "Missing build tool: $cmd" >&2; exit 2; }
done
JOBS="${BACHATA_JOBS:-2}"
export CMAKE_BUILD_PARALLEL_LEVEL="$JOBS"
export MAKEFLAGS="-j$JOBS"
export DEPS="$WORK/deps"
# Components are pinned in the public port's android/scripts/build_all.sh.
FEX_REV=f2b679f6028ce1c38875233aecfcf5d3f8ebecec
ADRENOTOOLS_REV=8fae8ce254dfc1344527e05301e43f37dea2df80
fetch_rev() {
  local dir="$1" url="$2" rev="$3"
  if [[ ! -d "$dir/.git" ]]; then
    mkdir -p "$dir"
    git init -q "$dir"
    git -C "$dir" remote add origin "$url"
  fi
  if [[ "$(git -C "$dir" rev-parse HEAD 2>/dev/null || true)" != "$rev" ]]; then
    git -C "$dir" fetch -q --depth 1 origin "$rev"
    git -C "$dir" -c advice.detachedHead=false checkout -q --force "$rev"
  fi
}
echo "== [1/5] Android/Bionic dependencies"
# The port defaults to $(nproc), which can exhaust GitHub runner memory when
# FFmpeg and multiple C++ dependencies are compiled in parallel.
sed -i 's/^J=$(nproc)$/J=${BACHATA_JOBS:-2}/' "$PORT/android/scripts/port-arm64/android_deps.sh"
bash "$PORT/android/scripts/port-arm64/android_deps.sh"
echo "== [2/5] pinned FEXCore Android build"
FEX_DIR="$WORK/fex"
FEX_BUILD="$WORK/fex-android"
fetch_rev "$FEX_DIR" https://github.com/FEX-Emu/FEX.git "$FEX_REV"
git -C "$FEX_DIR" submodule update -q --init --depth 1 \
  External/fmt External/xxhash External/range-v3 External/unordered_dense \
  External/rpmalloc External/jemalloc_glibc External/vixl External/zydis \
  Source/Common/cpp-optparse
for patch in "$PORT"/android/scripts/port-arm64/patches/fex-*.patch; do
  if git -C "$FEX_DIR" apply --reverse --check "$patch" 2>/dev/null; then
    echo "already applied: $(basename "$patch")"
  else
    git -C "$FEX_DIR" apply --check "$patch"
    git -C "$FEX_DIR" apply "$patch"
  fi
done
SRC="$FEX_DIR" OUT="$FEX_BUILD" TUNE_CPU=cortex-a78 \
  bash "$PORT/android/scripts/port-arm64/build_fex_android.sh"
echo "== [3/5] Android Vulkan driver-loader support"
ADT_DIR="$WORK/libadrenotools"
ADT_BUILD="$WORK/adrenotools-android"
fetch_rev "$ADT_DIR" https://github.com/bylaws/libadrenotools.git "$ADRENOTOOLS_REV"
git -C "$ADT_DIR" submodule update -q --init --depth 1
cmake -S "$ADT_DIR" -B "$ADT_BUILD" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$NDK/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=33 -DCMAKE_BUILD_TYPE=Release
cmake --build "$ADT_BUILD" -j"$JOBS"
test -s "$ADT_BUILD/libadrenotools.a" || {
  echo "libadrenotools static library missing: custom Vulkan driver selection cannot work" >&2
  exit 3
}
echo "== [4/5] Native Bionic Vulkan + guest loader"
SRC="$PORT" OUT="$WORK/gpu-build" FEX_SOURCE_DIR="$FEX_DIR" \
  FEX_BUILD_DIR="$FEX_BUILD" ADRENOTOOLS_SOURCE_DIR="$ADT_DIR" \
  ADRENOTOOLS_BUILD_DIR="$ADT_BUILD" \
  bash "$PORT/android/scripts/port-arm64/build_gpu_android.sh" bbgpu main bbprepare bb-probe
echo "== [5/5] Stage the actual linked native components"
S="$WORK/stage"
for name in libbbgpu.so libmain.so libbbprepare.so; do
  test -s "$WORK/gpu-build/$name" || { echo "Missing $name" >&2; exit 4; }
  cp -f "$WORK/gpu-build/$name" "$S/lib/arm64-v8a/"
done
test -s "$WORK/gpu-build/bb-probe"
cp -f "$WORK/gpu-build/bb-probe" "$S/tools/ps4-bionic-probe"
for name in libSDL3.so libavformat.so libavcodec.so libavutil.so \
            libswscale.so libswresample.so; do
  lib="$DEPS/prefix/lib/$name"
  test -s "$lib" || { echo "Missing dependency: $lib" >&2; exit 4; }
  cp -Lf "$lib" "$S/lib/arm64-v8a/$name"
  # Android resolves DT_NEEDED against DT_SONAME (e.g. libavcodec.so.62),
  # not necessarily the unversioned linker name libavcodec.so.
  soname="$(readelf -d "$lib" | awk '/\(SONAME\)/ {sub(/.*\[/, ""); sub(/\].*/, ""); print; exit}')"
  if [[ -n "$soname" && "$soname" != "$name" ]]; then
    cp -Lf "$lib" "$S/lib/arm64-v8a/$soname"
  fi
done
cp -f "$NDK/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so" \
  "$S/lib/arm64-v8a/"
for file in "$S/lib/arm64-v8a/"*.so "$S/tools/ps4-bionic-probe"; do
  # A Bionic binary uses Android's dynamic loader and Android libc.
  readelf -h "$file" | grep -q 'AArch64' || { echo "Non-ARM64 ELF: $file" >&2; exit 5; }
  if readelf -d "$file" | grep -q 'Shared library: \[libc.so\]'; then
    if readelf -d "$file" | grep -Eq 'Shared library: \[libc.so.6\]|ld-linux-aarch64'; then
      echo "GLIBC dependency in Bionic artifact: $file" >&2
      exit 5
    fi
  fi
done
readelf -d "$S/lib/arm64-v8a/libmain.so" | grep -q 'Shared library: \[libc.so\]' || {
  echo "Main guest runtime is not linked against Android Bionic" >&2; exit 5;
}
readelf -d "$S/lib/arm64-v8a/libbbgpu.so" | grep -q 'Shared library: \[libc.so\]' || {
  echo "GPU runtime is not linked against Android Bionic" >&2; exit 5;
}
(
  cd "$S"
  find lib tools -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
)
cat > "$S/CORE_STATUS.txt" <<'EOF'
Bachata S4+ native ARM64/Bionic core (source-build milestone)
=============================================================
Contains: Android FEXCore guest loader, PS4 memory/HLE loader,
Vulkan renderer, PKG preparation library, native dependencies.
Reference: Uncharted Android source and Bachata 0.2.5 ABI inspection.

IMPORTANT: This core currently accepts the prepared BBPROBE5 boot
format used by the port, not a generic PS4 eboot.bin. It does NOT
implement NativeRuntimeBridge.run(Surface,Z,String[],String[],String,int)
and must NOT replace libbachata_native_runtime.so in a released APK.

Next integration: adapt the general shadPS4 eboot/HLE loader and direct
ANativeWindow presenter, then provide the exact NativeRuntimeBridge JNI
ABI, with official 0.2.5 APK used only as a reference.
EOF
echo "Bionic build staged at $S"
