# Real shadPS4 0.18.1 Android/Bionic source integration

**This branch is NOT the binary-only transplant.** The base is the working
ARM64/FEX host `zenithblue-oss/shadps4-arm64@be6bc2e9c60799e071dd2fafa6216e8d80ec619c`,
merged against actual upstream shadPS4 0.18.1 source
`shadps4-emu/shadPS4@3912336fdfffbd5c99b59d92e997ea6ebd62216c`.

The historical 0.16.1 code supplies the ARM64/FEX guest execution, Android
Bionic JNI, SAF broker, Vulkan custom-driver loader and runtime control
interfaces. The PS4 shader recompiler, Vulkan rasterizer, texture and buffer
cache, and other emulator updates are rebased to 0.18.1.

Source merge: 351 paths, 111 conflicts; 84 resolved in favor of upstream
0.18.1, 27 intentionally retain the working platform host. Two old
spin-lock insertion patches were removed as obsolete because the newer
code uses a valid std::mutex fallback without the glibc adaptive initializer.

The source-only integration preflight passed in
[GitHub Actions #44924015436](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/44924015436).
The complete source + JNI/SAF preflight passed in
[GitHub Actions #44924226108](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/44924226108).

Next gate in THIS workflow: crosscompile actual ARM64 Android FEXCore,
link the real merged 0.18.1 renderer, validate ELF/JNI exports and source
version, then assemble and P36-sign the APK. These steps must succeed before
any APK can be called a source-integrated build. The signed APK alone cannot
prove successful Android game boot.

Release 0.2.6 private source:
`JICA98/Bachata-S4-Dev@v0.2.5-7-g99ceb85eb-dirty`.
That exact private source tree is not available publicly; the sources above
are a reproducible independent port, not a misrepresentation of private code.
