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

# Build matching host Abseil without fetching other versions from the network.
cmake -S "$ABSL" -B "$OUT/host-absl-build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DCMAKE_CXX_STANDARD=17 -DABSL_ENABLE_INSTALL=ON \
  -DABSL_BUILD_TESTING=OFF -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
cmake --build "$OUT/host-absl-build" --target install -j "$JOBS"

cmake -S "$PROTOSRC" -B "$BUILD" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 \
  -DCMAKE_PREFIX_PATH="$PREFIX" \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -Dprotobuf_LOCAL_DEPENDENCIES_ONLY=ON \
  -Dprotobuf_FORCE_FETCH_DEPENDENCIES=OFF \
  -Dprotobuf_BUILD_TESTS=OFF -Dprotobuf_BUILD_EXAMPLES=OFF \
  -Dprotobuf_BUILD_CONFORMANCE=OFF -Dprotobuf_BUILD_SHARED_LIBS=OFF \
  -Dprotobuf_WITH_ZLIB=OFF
cmake --build "$BUILD" --target protoc -j "$JOBS"
test -x "$BUILD/protoc"
test "$("$BUILD/protoc" --version)" = "libprotoc 36.0"

# Reject ABI-incompatible generated code BEFORE launching 2200 NDK tasks.
mkdir -p "$OUT/host-protoc-smoketest"
"$BUILD/protoc" "--proto_path=$SRC/src/shadnet" \
  "--cpp_out=$OUT/host-protoc-smoketest" \
  "$SRC/src/shadnet/shadnet.proto"
test -s "$OUT/host-protoc-smoketest/shadnet.pb.cc"
test -s "$OUT/host-protoc-smoketest/shadnet.pb.h"
# Compile the real generated translation unit against the exact headers
# used by the shadPS4 fork. A matching --version is NOT an ABI guarantee.
"${HOST_CXX:-c++}" -std=c++23 -fsyntax-only \
  -I "$OUT/host-protoc-smoketest" -I "$PROTOSRC/src" \
  -I "$PROTOSRC/third_party/utf8_range" -I "$PREFIX/include" \
  "$OUT/host-protoc-smoketest/shadnet.pb.cc"
echo "BIONIC_SHADNET_GENERATED_CPP_HEADER_ABI_PASS"
if grep -Fq 'TcParser::MpUnknownFields' "$OUT/host-protoc-smoketest/shadnet.pb.cc"; then
  echo "::error::Pinned host protoc generated an unsupported protobuf parser ABI" >&2
  exit 3
fi
echo "BIONIC_HOST_PROTOC_PINNED_SOURCE_5917EE_VERIFIED=$BUILD/protoc"
