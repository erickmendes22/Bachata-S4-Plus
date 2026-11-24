#!/usr/bin/env bash
# Public protobuf 36.0 protoc is not compatible with the pinned 0.18.1 fork:
# it generates TcParser::MpUnknownFields, absent from that fork's library.
# Build host protoc from THE SAME git commit as Android's libprotobuf.
set -euo pipefail
ROOT="$(cd "$(dirname "$BASH_SOURCE")/../.." && pwd)"
SRC="$ROOT/generic-upstream"
OUT="$ROOT/out/bionic"
PROTOSRC="$SRC/externals/protobuf"
ABSL="$SRC/externals/abseil-cpp"
PREFIX="$OUT/host-protoc-prefix"
BUILD="$OUT/host-protoc-build"
JOBS="$(printenv BACHATA_HOST_JOBS || echo 6)"

test -f "$PROTOSRC/CMakeLists.txt"
test -f "$PROTOSRC/third_party/utf8_range/CMakeLists.txt"
test -f "$ABSL/CMakeLists.txt"
actual="$(git -C "$PROTOSRC" rev-parse HEAD)"
test "$actual" = "5917ee224a7e47383a78acc129628511fe210dff" || {
  echo "::error::Host protobuf SHA differs from Android libprotobuf: $actual" >&2
  exit 2
}

# Inspect restored host objects and archives, not just one C++ generator.
cache_report="$(python3 "$ROOT/bionic/source0181/repair_host_cache.py" \
  "$BUILD" "$OUT/host-absl-build" "$PREFIX")"
printf '%s\n' "$cache_report"
removed="$(printf '%s\n' "$cache_report" | sed -n 's/^BIONIC_HOST_CACHE_REMOVED=//p')"
[[ "$removed" =~ ^[0-9]+$ ]]
if (( removed > 0 )); then
  rm -f "$BUILD/protoc" "$BUILD/protoc-36.0.0" "$BUILD/libprotoc.a"
  export CCACHE_RECACHE=1
fi

build_host() {
  cmake -S "$ABSL" -B "$OUT/host-absl-build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_CXX_STANDARD=17 -DABSL_ENABLE_INSTALL=ON \
    -DABSL_BUILD_TESTING=OFF -DCMAKE_CXX_COMPILER_LAUNCHER=ccache || return
  cmake --build "$OUT/host-absl-build" --target install -j "$JOBS" || return
  cmake -S "$PROTOSRC" -B "$BUILD" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_PREFIX_PATH="$PREFIX" \
    -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DCMAKE_C_COMPILER_LAUNCHER=ccache \
    -Dprotobuf_LOCAL_DEPENDENCIES_ONLY=ON \
    -Dprotobuf_FORCE_FETCH_DEPENDENCIES=OFF \
    -Dprotobuf_BUILD_TESTS=OFF -Dprotobuf_BUILD_EXAMPLES=OFF \
    -Dprotobuf_BUILD_CONFORMANCE=OFF -Dprotobuf_BUILD_SHARED_LIBS=OFF \
    -Dprotobuf_WITH_ZLIB=OFF || return
  cmake --build "$BUILD" --target libprotoc -j "$JOBS" || return
  # GNU nm can exit 0 despite invalid archive members. Reject stderr too.
  nm -C --defined-only "$BUILD/libprotoc.a" > "$OUT/host-protoc-symbols.txt" \
    2> "$OUT/host-protoc-nm-errors.txt" || return
  if grep -v ': no symbols$' "$OUT/host-protoc-nm-errors.txt" | grep -q .; then
    cat "$OUT/host-protoc-nm-errors.txt" >&2
    return 2
  fi
  for name in MakeRepeatedMessageGenerator MakeSinguarMessageGenerator MakeOneofMessageGenerator; do
    if ! grep -Fq "$name(" "$OUT/host-protoc-symbols.txt"; then
      echo "::error::Pinned protobuf libprotoc archive lacks definition $name" >&2
      return 2
    fi
  done
  echo "BIONIC_PROTOC_CPP_GENERATOR_ABI_READY"
  cmake --build "$BUILD" --target protoc -j "$JOBS" || return
}

verify_host() {
  test -x "$BUILD/protoc" || return
  test -s "$PREFIX/include/absl/base/config.h" || return
  PROTOC_VERSION="$("$BUILD/protoc" --version)" || return
  echo "BIONIC_HOST_PROTOC_VERSION=$PROTOC_VERSION"
  [[ "$PROTOC_VERSION" == "libprotoc 36.0-dev" ]] || return 2
  mkdir -p "$OUT/host-protoc-smoketest" || return
  rm -f "$OUT/host-protoc-smoketest/shadnet.pb."{cc,h} || return
  "$BUILD/protoc" "--proto_path=$SRC/src/shadnet" \
    "--cpp_out=$OUT/host-protoc-smoketest" "$SRC/src/shadnet/shadnet.proto" || return
  test -s "$OUT/host-protoc-smoketest/shadnet.pb.cc" || return
  test -s "$OUT/host-protoc-smoketest/shadnet.pb.h" || return
  "${HOST_CXX:-c++}" -std=c++23 -fsyntax-only \
    -I "$OUT/host-protoc-smoketest" -I "$PROTOSRC/src" \
    -I "$PROTOSRC/third_party/utf8_range" -I "$PREFIX/include" \
    "$OUT/host-protoc-smoketest/shadnet.pb.cc" || return
  if grep -Fq 'TcParser::MpUnknownFields' "$OUT/host-protoc-smoketest/shadnet.pb.cc"; then
    echo "::error::Pinned host protoc generated an unsupported protobuf parser ABI" >&2
    return 3
  fi
  echo "BIONIC_SHADNET_GENERATED_CPP_HEADER_ABI_PASS"
}

had_cache=0
[[ -f "$BUILD/CMakeCache.txt" ]] && had_cache=1
if (( removed == 0 )) && verify_host; then
  echo "BIONIC_HOST_PROTOC_CACHED_MATCHING_FORK"
elif build_host && verify_host; then
  echo "BIONIC_HOST_PROTOC_INCREMENTAL_REPAIRED"
elif (( had_cache )); then
  # Recovery is restricted to host prerequisites, not Android/NDK/FEX.
  echo "BIONIC_HOST_PROTOC_CACHE_RECOVERY: rebuild host-only prerequisites"
  rm -rf "$BUILD" "$OUT/host-absl-build" "$PREFIX"
  export CCACHE_RECACHE=1
  build_host
  verify_host
else
  echo "::error::Host protoc build/ABI failed without restored cache" >&2
  exit 2
fi
echo "BIONIC_HOST_PROTOC_PINNED_SOURCE_5917EE_VERIFIED=$BUILD/protoc"
