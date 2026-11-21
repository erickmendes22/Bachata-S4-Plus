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

## Release APK reference (actual 0.2.6 artifact inspected)

The user-supplied `bachatas4-0.2.6-release.apk` contains TWO genuine
shadPS4 0.18.1 builds, not just a glibc launcher:

- Native Android Bionic: `lib/arm64-v8a/libbachata_native_runtime.so`,
  87,365,424 bytes. Dynamic symbols include `FexGuestCpuBackend`,
  `HleGuestBridge`, `SafBrokerClient`, `SafFsBackend`,
  `PublishHostRange` and `RuntimeClient`.
- Linux Debian/glibc: `assets/runtime/runtime.zip` →
  `host/shadps4-arm64-fex`, 77,093,296 bytes. This binary depends on
  `ld-linux-aarch64.so.1`, `libc.so.6` and other GNU/Linux libraries.
- Both embed `0.18.1 WIP`. Both use the FEX revision
  `f2b679f6028ce1c38875233aecfcf5d3f8ebecec` in the APK manifests.
- Separate Turnip 27.0 glibc/Bionic packages exist, along with the original
  `libbachata_custom_vulkan.so`, `libmain_hook.so`, `libhook_impl.so`.
- The embedded runtime manifest identifies Debian protocol version 2;
  the native runtime manifest specifies `android-bionic-arm64`.

The migration's source-only report now audits this release's **behavioral
contracts** independently of the old Bionic 0.16.1 line-by-line patches.
A missing source marker is a compatibility task, *not* permission to install
a fake/stub implementation. Successful marker checks are not a compiled or
tested Android Bionic 0.21.1 core.

No private APK or extracted native binaries are committed to this repository.
