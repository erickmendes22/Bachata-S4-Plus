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
  echo "::error::BIONIC_STATIC_FEXCORE_CACHE_INVALID: stage was accepted without FEXCore static library" >&2
  echo "::error::native_cache.sh must select repair_fex or rebuild before this expensive compile step" >&2
  exit 2
}

if [[ "${BIONIC_SOURCE0181_PREPATCHED:-0}" == 1 ]]; then
  # The upstream 0.18.1 source has already been merged with the FEX ARM64
  # host and patched using the version-aware Android/Bionic overlay.
  grep -Fq 'set(EMULATOR_VERSION_MINOR "18")' "$SRC/CMakeLists.txt"
  grep -Fq 'set(EMULATOR_VERSION_PATCH "1")' "$SRC/CMakeLists.txt"
  grep -Fq 'BIONIC_VULKAN_CUSTOM_BRIDGE_READY' "$SRC/src/video_core/renderer_vulkan/vk_platform.cpp"
  test -s "$SRC/src/core/fex/fex_guest_engine.cpp"
  echo BIONIC_REAL_SOURCE0181_ANDROID_OVERLAY_PREAPPLIED
else
  python3 "$ROOT/bionic/generic/port_generic.py" "$SRC"
fi
git -C "$SRC" diff --check
mkdir -p "$BUILD" "$STAGE"

# Dear ImGui font-to-C emitter is a build-time HOST tool. NDK targets cannot
# run on the Ubuntu Actions runner (and cross-CMake correctly forbids that).
HOST_FONT_EMBED="$BUILD/bachata-imgui-font-embed-host"
HOST_FONT_SOURCE="$SRC/externals/imgui/misc/fonts/binary_to_compressed_c.cpp"
if [[ ! -s "$HOST_FONT_SOURCE" ]]; then
  HOST_FONT_SOURCE="$SRC/externals/dear_imgui/misc/fonts/binary_to_compressed_c.cpp"
fi
test -s "$HOST_FONT_SOURCE" || { echo "Missing ImGui HOST font generator in 0.18.1 and 0.16.1 trees" >&2; exit 2; }
echo "BIONIC_IMGUI_FONT_HOST_SOURCE: $HOST_FONT_SOURCE"
"${HOST_CXX:-c++}" -std=c++17 -O2 "$HOST_FONT_SOURCE" -o "$HOST_FONT_EMBED"
"$HOST_FONT_EMBED" 2>&1 | head -1 || true
test -x "$HOST_FONT_EMBED"

# shadNet's protoc is a HOST tool. An older CMakeCache.txt can retain
# /usr/bin/protoc from a prior run even when that executable no longer exists.
# Explicitly overwrite the cached FILEPATH rather than relying on find_program.
PROTOC_CMAKE_ARGS=()
HOST_PROTOC=""
if [[ "${BIONIC_SOURCE0181_PREPATCHED:-0}" == 1 ]]; then
  HOST_PROTOC="$(command -v protoc || true)"
  test -n "$HOST_PROTOC" && test -x "$HOST_PROTOC" || {
    echo "::error::shadPS4 0.18.1 host protoc is not on PATH" >&2; exit 2;
  }
  HOST_PROTOC_VERSION="$("$HOST_PROTOC" --version)"
  case "$HOST_PROTOC_VERSION" in
    "libprotoc 36.0-dev") ;;
    *) echo "::error::shadPS4 0.18.1 requires pinned host protoc 36.0-dev: $HOST_PROTOC ($HOST_PROTOC_VERSION)" >&2; exit 2 ;;
  esac
  PROTOC_CMAKE_ARGS=("-DBACHATA_HOST_PROTOC_EXECUTABLE:FILEPATH=$HOST_PROTOC")
  echo "BIONIC_SHADNET_PROTOC_HOST=$HOST_PROTOC"
fi

cmake -S "$SRC" -B "$BUILD" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$NDK/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=33 -DANDROID_STL=c++_shared \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DENABLE_DISCORD_RPC=OFF -DENABLE_UPDATER=OFF -DENABLE_TESTS=OFF \
  -DENABLE_BACHATA_RUNTIME=ON -DENABLE_FEX_GUEST_CPU=ON \
  -DFEXCORE_GUEST_CPU_SOURCE_DIR="$FEX_SOURCE" \
  -DFEXCORE_GUEST_CPU_BUILD_DIR="$FEX_BUILD" \
  -DIMGUI_FONT_EMBED_EXECUTABLE="$HOST_FONT_EMBED" \
  "${PROTOC_CMAKE_ARGS[@]}" \
  -DBACHATA_ANDROID_FFMPEG_PREFIX="$WORK/deps/prefix" \
  -DCMAKE_PREFIX_PATH="$WORK/deps/prefix" \
  -DCMAKE_FIND_ROOT_PATH="$WORK/deps/prefix"

# Validate the generated Ninja rule and actually run protoc BEFORE launching
# thousands of unrelated Android C++ compilation tasks.
if [[ "${BIONIC_SOURCE0181_PREPATCHED:-0}" == 1 ]]; then
  grep -Fqx "BACHATA_HOST_PROTOC_EXECUTABLE:FILEPATH=$HOST_PROTOC" "$BUILD/CMakeCache.txt" || {
    echo "::error::CMake still has a stale host protoc FILEPATH" >&2; exit 3;
  }
  ninja -C "$BUILD" -t commands shadnet_proto_gen/shadnet.pb.cc |
    grep -F "$HOST_PROTOC" >/dev/null || {
      echo "::error::Generated shadNet rule is not using protoc 36.0" >&2; exit 3;
    }
  # Let Ninja retain the generated parser if source/protoc are unchanged.
  # Regenerating every run invalidates dependent C++ objects unnecessarily.
  ninja -C "$BUILD" shadnet_proto_gen/shadnet.pb.cc
  if grep -Fq 'TcParser::MpUnknownFields' "$BUILD/shadnet_proto_gen/shadnet.pb.cc"; then
    echo "::warning::Old protobuf generated ABI cached; forcing a single pinned regeneration"
    rm -f "$BUILD/shadnet_proto_gen/shadnet.pb.cc" "$BUILD/shadnet_proto_gen/shadnet.pb.h"
    ninja -C "$BUILD" shadnet_proto_gen/shadnet.pb.cc
    if grep -Fq 'TcParser::MpUnknownFields' "$BUILD/shadnet_proto_gen/shadnet.pb.cc"; then
      echo "::error::Generated protobuf ABI still mismatches pinned runtime" >&2
      exit 3
    fi
  fi
  test -s "$BUILD/shadnet_proto_gen/shadnet.pb.h" || {
    echo "::error::shadNet protobuf header not generated" >&2; exit 3;
  }
  test -s "$BUILD/shadnet_proto_gen/shadnet.pb.cc" || {
    echo "::error::shadNet protobuf source not generated" >&2; exit 3;
  }
  echo "BIONIC_SHADNET_HOST_PROTOC_36_GENERATION_PASS"
fi

# Diagnose true incremental invalidation before scheduling 400 C++ units.
# The previous run restored 42,958 unchanged inputs yet recompiled every TU.
# Keep actual Ninja reasons and cached object count so this is fixable.
cached_objects="$(find "$BUILD/CMakeFiles/shadps4.dir" -name '*.o' -type f 2>/dev/null | wc -l)"
echo "BIONIC_INCREMENTAL_CACHED_CPP_OBJECTS=$cached_objects"
ninja -C "$BUILD" -n -d explain shadps4 > "$WORK/ndk-ninja-incremental-explain.log" 2>&1 || true
grep -m 25 'ninja explain:' "$WORK/ndk-ninja-incremental-explain.log" || true
echo "BIONIC_INCREMENTAL_NINJA_DRY_RUN_LINES=$(wc -l < "$WORK/ndk-ninja-incremental-explain.log")"

# Strict fail-fast first: precompile the mixed FEX 0.16 / shadPS4 0.18 API
# units before any bulk compilation (vk_presenter previously failed at 387/427).
# These are real Ninja objects and are reused by the full shadPS4 target.
if [[ "${BIONIC_SOURCE0181_PREPATCHED:-0}" == "1" ]]; then
  priority_sources=(
    # Compile the actual Release-parity VFS and FIOS2 units first.
    # Host mocks are insufficient to verify the shadPS4 0.18.1 real ABI.
    src/core/file_sys/fs.cpp
    src/core/file_sys/backends/saf_fs_backend.cpp
    src/core/loader/elf.cpp
    src/core/module.cpp
    src/video_core/renderer_vulkan/vk_presenter.cpp
    src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp
    src/shader_recompiler/ir/passes/resource_patching_pass.cpp
    src/shader_recompiler/backend/spirv/spirv_emit_context.cpp
    src/shader_recompiler/recompiler.cpp
    src/video_core/renderer_vulkan/vk_pipeline_cache.cpp
    src/video_core/renderer_vulkan/vk_rasterizer.cpp
    src/video_core/buffer_cache/buffer_cache.cpp
    src/video_core/page_manager.cpp
    src/video_core/texture_cache/blit_helper.cpp
    src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp
    src/video_core/renderer_vulkan/vk_instance.cpp
    src/video_core/texture_cache/texture_cache.cpp
    src/video_core/renderer_vulkan/vk_platform.cpp
    src/core/libraries/gnmdriver/gnmdriver.cpp
    src/core/libraries/fios2/fios2.cpp
    src/core/libraries/sysmodule/sysmodule_internal.cpp
    src/core/guest_cpu/hle_call_adapter.cpp
    src/core/aerolib/stubs.cpp
    src/core/libraries/kernel/file_system.cpp
    src/core/libraries/kernel/threads/semaphore.cpp
    src/core/libraries/videoout/video_out.cpp
    src/core/libraries/videoout/driver.cpp
    src/core/memory.cpp
    src/core/libraries/libs.cpp
    src/input/controller.cpp
    src/emulator.cpp
    src/main.cpp
    src/common/logging/log.cpp
    src/core/libraries/kernel/memory.cpp
    src/core/libraries/camera/camera.cpp
    src/core/linker.cpp
  )
  ninja -C "$BUILD" -t targets all > "$WORK/ndk-ninja-targets.txt"
  # Inspect the ACTUAL generated compiler graph, not only CMake source text.
  # If the desktop SDL WindowSDL exists, linking would fail after ~400 TUs.
  if grep -Fq 'CMakeFiles/shadps4.dir/src/sdl_window.cpp.o:' "$WORK/ndk-ninja-targets.txt"; then
    echo "::error::BIONIC_SDL_DUPLICATE_LINK: desktop sdl_window.cpp object in Android core" >&2
    exit 3
  fi
  if ! grep -Fq 'android_window.cpp.o:' "$WORK/ndk-ninja-targets.txt"; then
    echo "::error::BIONIC_SDL_ANDROID_FRONTEND_MISSING: service-owned android_window.cpp" >&2
    exit 3
  fi
  echo "BIONIC_WINDOW_SOURCE_EXCLUSIVE_PASS"
  priority_objects=()
  for source in "${priority_sources[@]}"; do
    object="CMakeFiles/shadps4.dir/${source}.o"
    if ! grep -Fq "${object}:" "$WORK/ndk-ninja-targets.txt"; then
      echo "::error::Early ABI compiler gate missing $object" >&2
      exit 3
    fi
    priority_objects+=("$object")
  done
  # CMake places external overlay objects under an absolute-path-derived
  # Ninja target. Resolve the actual graph and require BOTH NGS2 donor files.
  # Compile them with the real pinned LibAtrac9/NDK ABI before the bulk target.
  for source in sotc_ngs2_mixer.c donor_parity_bridge.cpp android_libc_compat.cpp android_libc_boot.cpp android_fex_fiber.cpp; do
    mapfile -t overlay_matches < <(awk -v suffix="/${source}.o:" 'index($1,suffix) && substr($1,length($1)-length(suffix)+1)==suffix && $1 ~ /^CMakeFiles\/shadps4\.dir\// {sub(/:$/,"",$1);print $1}' "$WORK/ndk-ninja-targets.txt")
    if (( ${#overlay_matches[@]} != 1 )); then
      echo "::error::Early native ABI gate expected one object for $source, found ${#overlay_matches[@]}" >&2
      exit 3
    fi
    priority_objects+=("${overlay_matches[0]}")
  done
  echo "BIONIC_CPP_FAIL_FAST_START: ${#priority_objects[@]} critical C/C++ units before bulk build"
  set +e
  ninja -C "$BUILD" -j "$JOBS" -k 1 "${priority_objects[@]}" 2>&1 | tee "$WORK/ndk-cxx-early.log"
  early_status=${PIPESTATUS[0]}
  set -e
  if (( early_status != 0 )); then
    python3 "$ROOT/bionic/source0181/extract_native_errors.py" \
      "$WORK/ndk-cxx-early.log" "$WORK/ndk-errors-summary.txt"
    echo "::error::Early C++ ABI gate failed; bulk build cancelled."
    exit "$early_status"
  fi
  # The FEX libc jump overlay was compiled in the same gate above.
  echo "BIONIC_GUEST_LIBC_JUMP_COMPILER_PASS"
  echo "BIONIC_CPP_FAIL_FAST_PASS: ${#priority_objects[@]} reusable compiled objects"
  # A source-level declaration check is insufficient: ensure the actual
  # ARM64 objects export the exact two symbols missing in the previous link.
  NM="$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-nm"
  # Do NOT pipe llvm-nm into grep -q under pipefail: grep exits on its
  # first match, llvm-nm gets SIGPIPE (141), and a valid symbol fails CI.
  # Materialize the complete symbol table, then inspect the finished file.
  "$NM" -C --defined-only \
    "$BUILD/CMakeFiles/shadps4.dir/src/common/logging/log.cpp.o" \
    > "$WORK/ndk-logger-defined-symbols.txt"
  "$NM" -C --defined-only \
    "$BUILD/CMakeFiles/shadps4.dir/src/core/libraries/kernel/memory.cpp.o" \
    > "$WORK/ndk-kernel-defined-symbols.txt"
  if ! grep -Fq 'Common::Log::Terminate()' "$WORK/ndk-logger-defined-symbols.txt"; then
    grep -i -F 'Terminate' "$WORK/ndk-logger-defined-symbols.txt" || true
    echo "::error::FEX Terminate() truly absent from compiled modern logger" >&2
    exit 3
  fi
  if ! grep -Fq 'Libraries::Kernel::sceKernelMapNamedSystemFlexibleMemory(' \
      "$WORK/ndk-kernel-defined-symbols.txt"; then
    grep -i -F 'FlexibleMemory' "$WORK/ndk-kernel-defined-symbols.txt" || true
    echo "::error::0.18 System VMA HLE truly absent from compiled FEX kernel" >&2
    exit 3
  fi
  echo "BIONIC_LINKER_API_PRECHECK_PASS"
fi

# Stop the bulk C++ build on the first compiler error (never use -k 0).
# Keep already compiled C++ objects in ccache for the next attempt.
set +e
cmake --build "$BUILD" --target shadps4 -j "$JOBS" 2>&1 | tee "$WORK/ndk-cxx-full.log"
native_build_status=${PIPESTATUS[0]}
set -e
if (( native_build_status != 0 )); then
  python3 "$ROOT/bionic/source0181/extract_native_errors.py" \
    "$WORK/ndk-cxx-full.log" "$WORK/ndk-errors-summary.txt"
  echo "::error::Full C++ compilation reported every error in ndk-errors-summary.txt"
  exit "$native_build_status"
fi
CORE="$BUILD/libbachata_bionic_core.so"
test -s "$CORE" || { echo "Generic shadPS4 Android core not produced: $CORE" >&2; exit 3; }
readelf -h "$CORE" | grep -q AArch64
readelf -d "$CORE" | grep -q 'Shared library: \[libc.so\]'
! readelf -d "$CORE" | grep -q 'Shared library: \[libc.so.6\]'
readelf -Ws "$CORE" | grep -F 'Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run' > /dev/null
cp -f "$CORE" "$STAGE/"
# Bind the exact GitHub source revision to every generated core artifact.
# APK-only must reject stale binaries compiled before required boot fixes.
git -C "$ROOT" rev-parse HEAD > "$WORK/stage/BIONIC_SOURCE_REVISION.txt"
git -C "$SRC" rev-parse HEAD > "$WORK/stage/BIONIC_UPSTREAM_REVISION.txt"
echo "GENERIC_CORE_BUILD_SUCCESS: $STAGE/libbachata_bionic_core.so"
echo "BIONIC_SOURCE_REVISION: $(cat "$WORK/stage/BIONIC_SOURCE_REVISION.txt")"
