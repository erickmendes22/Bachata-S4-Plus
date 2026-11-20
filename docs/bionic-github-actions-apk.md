# Bachata S4+ Bionic — GitHub Actions APK build

## Branch and source of truth

Branch: `feature/bionic-arm64-core-20261119`.
No native emulator or APK builds need to run on the developer's Android device or local PC.

Native C++/JNI source maintained in this repo:
- `bionic/generic/`: game-generic shadPS4 Android window, JNI, HLE/FEX integration
- `bionic/jni/`: exact `NativeRuntimeBridge.run/stop` handoff
- `bionic/apk/normalize_elf.sh`: Android DT_SONAME and JNI validation
- `bionic/apk/assemble_apk.py`: APK 0.2.7 frontend preservation and native-library injection

Pinned public C++ sources are checked out by the workflow:
- `zenithblue-oss/shadps4-arm64`, source commit `be6bc2e9c60799e071dd2fafa6216e8d80ec619c`
- `erickmendes22/uncharted-android`, Android/FEX reference commit `148656bc7ae1b8b482d95e33d49f0729421ff477`

## Build

Run `.github/workflows/bachata-bionic-generic-source.yml` on the feature branch.
The `full-ps4-bionic` job compiles core and JNI with Android NDK r30.
The `assemble-bionic-apk` job then downloads the **fixed** 0.2.7 release
APK, checks its SHA-256, normalizes native ELF SONAMEs, inserts the freshly
compiled libraries, updates native runtime hashes, aligns and signs APK,
and publishes artifact `Bachata-S4Plus-0.2.7-Bionic-TEST-APK`.

This is an *experimental APK for testing native Bionic*, not an approved release.
It is not evidence that games boot, that custom drivers work, or that performance
is improved. Verify on real ARM64 Android hardware with logs.

## Important distinction: frontend source migration

The 0.2.7 APK itself contains DEX and compiled Android resources; **this
intermediate APK job does not compile the entire 0.2.7 Kotlin/Compose frontend
from source**. It preserves the exact 0.2.7 frontend from the tagged APK.
For complete maintainable source-builds, the next migration is to incorporate
the Android Gradle frontend sources (where legally licensed) from the public
`dev-Ali2008/onRps4-runtime/runtime/sources/shadps4/android/BachataS4`
and synchronize changes made in 0.2.7. Do not assume that the older public
frontend is binary- or feature-identical to 0.2.7, and do not import the closed
onRps4-Android release binary as source.

## Signing / upgrading installed releases

The workflow uses four **GitHub Actions Secrets** for durable signing, never
a private keystore committed to source control:
- `BACHATA_SIGNING_KEYSTORE_BASE64`
- `BACHATA_SIGNING_STORE_PASSWORD`
- `BACHATA_SIGNING_KEY_ALIAS`
- `BACHATA_SIGNING_KEY_PASSWORD`

With all four configured, the job signs with that certificate. **Only when the
certificate matches the installed 0.2.7 certificate** can Android update the
existing installation without uninstalling (subject to Android version code
rules). If no secrets are present, a **fresh temporary TEST certificate** is
generated, which is **not updatable** across CI executions and cannot upgrade
an installed 0.2.7 release. Back up saves before a clean install. Partial
signing-secret configuration fails the job rather than silently switching keys.

Never publish temporary-test-signed APKs as production updates.

## Validation gates

- Original 0.2.7 SHA-256 pinned and checked before any modification.
- Bionic shared libraries are real ARM64 ELF with Android `libc.so`.
- Native JNI adapter and generic Bionic core expose the exact run/stop entrypoints.
- FFmpeg shared-library SONAMEs must be unversioned `lib*.so` for APK extraction.
- DEX, AndroidManifest, runtime.zip and resources.arsc remain byte-identical.
- Original native-runtime JSON integrity values updated for replaced libraries.
- Zipalign and apksigner verification required before publishing installable APK.
- Compilation of C++ objects or a core ZIP **alone** is not a successful APK build.
