#!/usr/bin/env bash
# Assemble a real modern shadPS4 0.21.1 Android/Bionic core into the original
# Bachata S4+ 0.2.7 frontend. Do NOT substitute an older 0.18.1 Bionic .so.
set -euo pipefail
: "${BACHATA_P36_PRIVATE_KEY:?original Bachata P36 signing secret required}"
: "${BACHATA_P36_CERT:?original Bachata P36 cert secret required}"
: "${BACHATA_MODERN_SOURCE_SHA:?compiled 0.21.1 Git commit required}"
: "${ANDROID_HOME:?Android SDK required}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
NDK="$ANDROID_HOME/ndk/30.0.14904198"
CXX="$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android33-clang++"
BT="$ANDROID_HOME/build-tools/36.0.0"
OUT="$ROOT/out/bionic-modern"
STAGE="$OUT/stage"
LIBDIR="$STAGE/lib/arm64-v8a"
APK="$OUT/apk"
mkdir -p "$LIBDIR" "$APK"
CORE="$OUT/build/libbachata_bionic_core.so"
test -s "$CORE" || { echo "::error::No shadPS4 0.21.1 Bionic native core"; exit 2; }
test "${#BACHATA_MODERN_SOURCE_SHA}" -eq 40
cp -f "$CORE" "$LIBDIR/"
# Reuse the ORIGINAL JNI service handoff, which configures cwd, logs, and
# Turnip environment before loading this real core from the Java ClassLoader.
"$CXX" -std=c++17 -O2 -Wall -Wextra -Werror -fPIC -shared \
  bionic/jni/bachata_native_bridge.cpp \
  -o "$LIBDIR/libbachata_native_runtime.so" -landroid -llog -ldl
for component in avformat avcodec avutil avfilter swresample swscale; do
  f="$OUT/deps/prefix/lib/lib$component.so"
  test -s "$f" || { echo "::error::Missing NDK FFmpeg $f"; exit 2; }
  cp -Lf "$f" "$LIBDIR/lib$component.so"
done
cp -f "$NDK/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so" "$LIBDIR/"
printf '%s\n' "$BACHATA_MODERN_SOURCE_SHA" > "$STAGE/BIONIC_SOURCE_REVISION.txt"
printf '%s\n' "shadPS4 0.21.1 Bionic ARM64, compiled core; source $BACHATA_MODERN_SOURCE_SHA" > "$STAGE/CORE_STATUS.txt"

# Check globally defined (not undefined or local) JNI exports. SDL.setupJNI
# is called by the original Bachata JNI adapter after the new core is loaded.
for symbol in \
  JNI_OnLoad \
  Java_org_libsdl_app_SDLActivity_nativeSetupJNI \
  Java_org_libsdl_app_SDLAudioManager_nativeSetupJNI \
  Java_org_libsdl_app_SDLControllerManager_nativeSetupJNI \
  Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run \
  Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop; do
  if ! readelf --dyn-syms --wide "$CORE" |
      awk -v symbol="$symbol" '$4=="FUNC" && $5=="GLOBAL" && $7!="UND" && $8==symbol {found=1} END {exit !found}'; then
    echo "::error::Modern Bionic core lacks required JNI export $symbol"
    exit 3
  fi
done
bash bionic/apk/normalize_elf.sh "$LIBDIR"
python3 bionic/apk/prepare_slim_native.py "$STAGE" --modern \
  --strip "$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip"

# Use the verified, unchanged original frontend. No new UI or temporary signer.
curl -fL --retry 4 --retry-delay 3 \
  'https://github.com/erickmendes22/Bachata-S4-Plus/releases/download/0.2.7/Bachata-S4-Plus-v0.2.7.apk' \
  -o "$APK/base.apk"
echo '35c6fad39430e54aba561877953323e03b322a589a44442931317450e0b952d8  '"$APK/base.apk" | sha256sum -c -
curl -fL --retry 4 --retry-delay 3 \
  'https://github.com/iBotPeaches/Apktool/releases/download/v2.12.1/apktool_2.12.1.jar' \
  -o "$APK/apktool.jar"
java -Xmx5G -jar "$APK/apktool.jar" d -f -r "$APK/base.apk" -o "$APK/decoded" \
  > "$APK/apktool-decompile.log" 2>&1
python3 bionic/apk/patch_frontend.py "$APK/decoded"
java -Xmx5G -jar "$APK/apktool.jar" b "$APK/decoded" -o "$APK/patch-smali.apk" \
  > "$APK/apktool-build.log" 2>&1
unzip -p "$APK/patch-smali.apk" classes8.dex > "$APK/classes8-bionic.dex"
test -s "$APK/classes8-bionic.dex"
python3 bionic/apk/assemble_modern_apk.py --base "$APK/base.apk" --stage "$STAGE" \
  --output "$APK/unsigned.apk" --patched-classes8 "$APK/classes8-bionic.dex" \
  --revision "$BACHATA_MODERN_SOURCE_SHA"

# Original P36 identity only, with no generated signing key or certificate.
"$BT/zipalign" -f -P 16 4 "$APK/unsigned.apk" "$APK/aligned.apk"
KEY="$APK/p36-private.pem"
KEY_PKCS8="$APK/p36-private.pk8"
CERT="$APK/p36-cert.pem"
trap 'rm -f "$KEY" "$KEY_PKCS8" "$CERT"' EXIT
umask 077
printf '%s\n' "$BACHATA_P36_PRIVATE_KEY" > "$KEY"
printf '%s\n' "$BACHATA_P36_CERT" > "$CERT"
EXPECTED=d04ef2a865f8ed5ab8f98321be93ed2881eaa64f844fbaf480e18a8336620a72
ACTUAL="$(openssl x509 -in "$CERT" -outform DER | sha256sum | cut -d' ' -f1)"
test "$ACTUAL" = "$EXPECTED" || { echo "::error::P36 signer mismatch"; exit 4; }
key_public="$(openssl pkey -in "$KEY" -pubout -outform DER | sha256sum | cut -d' ' -f1)"
cert_public="$(openssl x509 -in "$CERT" -pubkey -noout | openssl pkey -pubin -outform DER | sha256sum | cut -d' ' -f1)"
test "$key_public" = "$cert_public" || { echo "::error::P36 signing key mismatch"; exit 4; }
openssl pkcs8 -topk8 -nocrypt -in "$KEY" -outform DER -out "$KEY_PKCS8"
"$BT/apksigner" verify --verbose --print-certs "$APK/base.apk" > "$APK/base-signer.txt"
grep -Fq "$EXPECTED" "$APK/base-signer.txt" || { echo "::error::Wrong base APK signer"; exit 4; }
SIGNED="$APK/Bachata-S4Plus-shadPS4-0211-Bionic-P36.apk"
"$BT/apksigner" sign --key "$KEY_PKCS8" --cert "$CERT" \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out "$SIGNED" "$APK/aligned.apk"
"$BT/apksigner" verify --verbose --print-certs "$SIGNED" | tee "$APK/apksigner-verification.txt"
grep -Fq "$EXPECTED" "$APK/apksigner-verification.txt" || { echo "::error::Signed APK is not P36"; exit 4; }
sha256sum "$SIGNED" > "$APK/SHA256SUMS"
echo BIONIC_021_GENUINE_CORE_P36_APK_READY
