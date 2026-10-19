# SotC GPU/graphics — core025 ARM64 experimental source port

Source baseline: zenithblue-oss/shadps4-arm64 at pinned commit
`be6bc2e9c60799e071dd2fafa6216e8d80ec619c`. The shipped native
core025 from R30 includes changes absent in that public tree, so this build
must **not** silently replace it or the user's saved patches.

Three opt-in fixes:
* `BACHATA_SOTC_LOD_STATS=1`: emulate PM4 IT_GET_LOD_STATS and T# counters,
  report mip **2** (not mip 0/1), saturating streaming priority.
* `BACHATA_SOTC_UNMAP_DROP=1`: synchronously retire GPU-modified regions on
  unmap, avoiding readbacks into freed guest heap. Keep readbacksMode=2 for
  actual GPU-to-CPU reads. Not yet tested in gameplay.
* `BACHATA_SOTC_LDS_LARGE_GROUPS=1`: experimental merge barriers for
  large compute workgroups, without unconditional divergent-block barriers.

They default to OFF. Enable only for game CUSA08809 v1.00 in the eventual
launcher; globally enabling unmap-drop could break other games. All guards
are independent, so LOD, unmap and large-LDS effects can be isolated.

**Not included**: full EOP deferral/scheduler semantics, unverified GPU
ahead-readback rings, dynamic ARM64 SRT offset emitter rework (the published
source lacks the exact core025 emitter), shader wave64 refactor, Turnip and
resolution changes. These must be validated separately.

GitHub Actions builds and uploads an isolated experimental AArch64 binary,
not an installable APK and not a drop-in replacement for R30.
