# Bachata Bionic modernization target: shadPS4 **0.21.1**

The existing Bionic core is pinned to zenithblue-oss/shadps4-arm64
`be6bc2e9` (shadPS4 0.16.1). This branch preserves the known working Bionic
APK+SAF+Turnip flow while migrating the **full** HLE, renderer, shader compiler,
kernel, memory manager, libraries and FEX guest CPU to 0.21.1.

Source of the newer ARM64 baseline:
- `zgj3880888/shadps4-arm64-021` `0e713b0d`, an applied port of
  shadPS4 0.21.1 on `Nyces/shadps4-arm64` `3d4ff9a9`.
- The candidate ARM64 0.21.1 core was built successfully by Actions run
  `43049822293` on 2026-11-11; **this is a Debian/glibc ARM64 build**,
  not proof of Bionic compatibility.
- Upstream shadPS4 main at `264d6b71` identifies as 0.21.1 as of 2026-11-21.
- `WizzardSK/shadps4-libretro` `2cf3df31` has a separate ARM64 FEX implementation
  on the 0.20.1 generation and is a useful cross-reference, not the target.

`bachata-bionic-modern-core.yml` runs only source validation. **It must not
compile a complete core or upload/recycle the 0.16.1 APK.** Its first objective
is a reliable report of old 0.16 integration anchors that need replacement.

Implementation requirements before any new APK:
1. Rebase Bionic Vulkan/AdrenoTools to new WSI and vk instance interfaces.
2. Adapt native Android window and JNI entry into 0.21.1 CMake/SDL structure.
3. Carry over SAF broker and read/seek semantics, not fallback placeholders.
4. Bring guest-visible libc heap, argv, HLE adapter ABI and sysmodule fixes.
5. Verify relocated signal handlers and FEX guest CPU control flow.
6. Bring entire new Vulkan rasterizer, shader recompiler and VMM as a unit,
   with explicit adaptations, rather than cherry-picking The Order patches.
7. Validate real ARM64/Bionic compilation and original P36 signed APK.
8. Test multiple titles on-device; no title-specific first-frame success gate.

Failures stay in the modern branch; do not regress the existing Bionic branch.
