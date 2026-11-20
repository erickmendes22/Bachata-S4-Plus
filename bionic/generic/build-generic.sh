#!/usr/bin/env bash
# Build the FULL game-generic shadPS4 HLE/PS4 linker/FEX source as Android/Bionic .so.
# Run only AFTER bionic/build-core.sh has built the pinned Android FEX libraries.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="${GENERIC_SHADPS4_SOURCE:-$ROOT/generic-upstream}"
WORK="${WORK:-$ROOT/out/bionic}"
NDK="${NDK:?NDK r30 must be provided}"
FEX_BUILD="$WORK/fex-android"
FEX_SOURCE="$WORK/fex"
BUILD="$WORK/shadps4-generic-android"
STAGE="$WORK/stage/lib/arm64-v8a"
JOBS="${BACHATA_JOBS:-2}"

test -f "$SRC/src/core/linker.cpp" || { echo "Generic PS4 linker absent" >&2; exit 2; }
test -f "$SRC/externals/CMakeLists.txt" || { echo "shadPS4 externals absent" >&2; exit 2; }
test -f "$SRC/externals/sdl3/CMakeLists.txt" || { echo "Recursive submodules required" >&2; exit 2; }
test -s "$FEX_BUILD/FEXCore/Source/libFEXCore.a" || {
  echo "Bionic FEXCore not built by build-core.sh" >&2; exit 2;
}

python3 "$ROOT/bionic/generic/port_generic.py" "$SRC"
git -C "$SRC" diff --check
mkdir -p "$BUILD" "$STAGE"

# Dear ImGui font-to-C emitter is a build-time HOST tool. NDK targets cannot
# run on the Ubuntu Actions runner (and cross-CMake correctly forbids that).
HOST_FONT_EMBED="$BUILD/bachata-imgui-font-embed-host"
HOST_FONT_SOURCE="$SRC/externals/dear_imgui/misc/fonts/binary_to_compressed_c.cpp"
test -s "$HOST_FONT_SOURCE" || { echo "Missing Dear ImGui host font generator" >&2; exit 2; }
"${HOST_CXX:-c++}" -std=c++17 -O2 "$HOST_FONT_SOURCE" -o "$HOST_FONT_EMBED"
"$HOST_FONT_EMBED" 2>&1 | head -1 || true
test -x "$HOST_FONT_EMBED"

cmake -S "$SRC" -B "$BUILD" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$NDK/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=33 -DANDROID_STL=c++_shared \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DENABLE_DISCORD_RPC=OFF -DENABLE_UPDATER=OFF -DENABLE_TESTS=OFF \
  -DENABLE_BACHATA_RUNTIME=ON -DENABLE_FEX_GUEST_CPU=ON \
  -DFEXCORE_GUEST_CPU_SOURCE_DIR="$FEX_SOURCE" \
  -DFEXCORE_GUEST_CPU_BUILD_DIR="$FEX_BUILD" \
  -DIMGUI_FONT_EMBED_EXECUTABLE="$HOST_FONT_EMBED" \
  -DCMAKE_PREFIX_PATH="$WORK/deps/prefix" \
  -DCMAKE_FIND_ROOT_PATH="$WORK/deps/prefix"

# Keep compiling independent translation units after an error so one run reveals
# ALL Android portability failures instead of the first failing source.
cmake --build "$BUILD" --target shadps4 -j "$JOBS" -- -k 0
CORE="$BUILD/libbachata_bionic_core.so"
test -s "$CORE" || { echo "Generic shadPS4 Android core not produced: $CORE" >&2; exit 3; }
readelf -h "$CORE" | grep -q AArch64
readelf -d "$CORE" | grep -q 'Shared library: \[libc.so\]'
! readelf -d "$CORE" | grep -q 'Shared library: \[libc.so.6\]'
readelf -Ws "$CORE" | grep -q 'Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run'
cp -f "$CORE" "$STAGE/"
echo "GENERIC_CORE_BUILD_SUCCESS: $STAGE/libbachata_bionic_core.so"
