# Bachata Bionic: provenance, audit and build baseline (2026-11-21)

This branch intentionally resumes the **functional ARM64/FEX 0.16.1 source** at
`zenithblue-oss/shadps4-arm64@be6bc2e9c60799e071dd2fafa6216e8d80ec619c`,
not the experimental whole-tree 0.21.1 transplant.

The exact Android APK `bachatas4-0.2.6-release.apk` has SHA-256
`39d38d4e781bc83ee2542b3884a264895e726c3c8ee49df493ded487e6cd6f74`.
Its original native and Linux ARM64 ELF files contain:
- **shadPS4 0.18.1 WIP**, `JICA98/Bachata-S4-Dev`
- `v0.2.5-7-g99ceb85eb-dirty`
- FEX `f2b679f6028ce1c38875233aecfcf5d3f8ebecec`
- Bionic ELF build id `7915af924afb3bc2142df65fdeb36f28a970d0a5`
- Linux ELF build id `0a0ada4cf92b9e275c671e2902a79f500f76168e`

`bionic/reference/audit_release_026.py` hashes the actual official APK
and two ELF binaries, asserts native Android versus glibc NEEDED contracts,
probes the source's pinned 0.16.1 version and core FEX modules, and checks
the six JNI exports. The fast GitHub preflight successfully passed in run
[#44917703442](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/44917703442).

Differences **not** proven identical:
- Public 0.16.1 uses a separate `BachataSaf` integration; official 0.18.1
  uses `SafFsBackend`/`SafBrokerClient` exported native types.
- Custom Vulkan driver selection must preserve the original APK's
  `libbachata_custom_vulkan.so`, `libmain_hook.so`, `libhook_impl.so`.
- The core binary built from 0.16.1 is *not* the official private 0.18.1
  source, even when the JNI loader ABI matches.
- Android game launch and gameplay still require a device diagnostic.

This commit deliberately triggers a new full **[build-apk]** run of the
previously successful 0.16.1 compilation path, followed by original P36 APK
signing. No game boot is claimed without an Android test.
