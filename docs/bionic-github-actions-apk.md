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

## Permanent original P36 signing — required

The original Bachata S4+ P36 private key and certificate are retained in the
user-owned ChatGPT Library as:

- `Bachata-S4-Plus-P36-signing-key.pem`
- `Bachata-S4-Plus-P36-signing-cert.pem`

**Never commit, upload or expose the private key on public GitHub.**

The P36 certificate was cryptographically confirmed to match the key and,
independently, the **official 0.2.7 GitHub Release** signer through GitHub
Actions run `44763248800`.

Expected P36 X.509 DER SHA256:

`d04ef2a865f8ed5ab8f98321be93ed2881eaa64f844fbaf480e18a8336620a72`

One-time GitHub setup by a repository administrator:
1. Open **Settings → Secrets and variables → Actions** in `erickmendes22/Bachata-S4-Plus`.
2. Create secret **`BACHATA_P36_PRIVATE_KEY`** containing the full private-key
   PEM text, including `BEGIN PRIVATE KEY` / `END PRIVATE KEY`.
3. Create secret **`BACHATA_P36_CERT`** containing the full certificate PEM
   text, including `BEGIN CERTIFICATE` / `END CERTIFICATE`.
4. Launch **Actions → Bachata S4+ Bionic APK ONLY → Run workflow** using the
   pinned successful native core run `44751437665` (default).

The GitHub Actions integration available here cannot write repository Actions
secrets. The repository owner must configure them once using the GitHub UI.

The APK-only workflow uses `apksigner --key/--cert` directly with the
permanent original PEM key; no password or PKCS#12 conversion is necessary.
The key and certificate exist only in the workflow runner's temporary files
and are deleted when signing finishes.

Safety checks:
- Abort before downloads if either secret is missing.
- Never generate a temporary/self-signed certificate.
- Validate the key matches the certificate.
- Validate the certificate matches the original P36 SHA256.
- Validate the official base APK 0.2.7 is P36-signed.
- Sign with the original P36 key and verify output signature matches P36.
- Fail the workflow rather than publish a non-updatable build.

No local build is involved. Only GitHub Actions compiles, assembles, aligns,
signs and verifies the APK.

## Validation gates

- Original 0.2.7 SHA-256 pinned and checked before any modification.
- Bionic shared libraries are real ARM64 ELF with Android `libc.so`.
- Native JNI adapter and generic Bionic core expose the exact run/stop entrypoints.
- FFmpeg shared-library SONAMEs must be unversioned `lib*.so` for APK extraction.
- DEX, AndroidManifest, runtime.zip and resources.arsc remain byte-identical.
- Original native-runtime JSON integrity values updated for replaced libraries.
- Zipalign and apksigner verification required before publishing installable APK.
- Compilation of C++ objects or a core ZIP **alone** is not a successful APK build.
