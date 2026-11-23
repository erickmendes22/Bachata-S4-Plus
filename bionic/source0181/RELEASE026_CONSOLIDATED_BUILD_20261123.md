# Release 0.2.6 — integrated shared-core parity build

This build includes all of the following **core-wide** fixes, not individual CUSA patches:

- GPU graphics DCB/CCB ownership by suspended command coroutines, per Release 0.2.6.
- Independent Constant Engine submission FIFO, proper CE/DE counters and cross-coroutine PM4 lifetime.
- Snapshot PM4 packet lengths before guest buffer reuse, handle type-2 CE packets, distinguish chained indirect graphics buffers, release nested command coroutines.
- Genuine FEX x86 guest callbacks for libc `qsort`, with guest range checks, avoiding native Android comparator ABI.
- Dinkumware `_Log(double,int)` HLE, preserving SysV FP argument / return ABI.
- Fail-closed source version assertions and CI preflight requirements for these GPU and HLE paths.

Source integration preflight passed at GitHub Actions `45189937010`; this commit deliberately triggers full Android cross-compilation and P36 APK packaging. A successful compilation is not proof of game compatibility. Unresolved SRT `ReadLane`/`Phi`, CMask, Vulkan memory and SAF parity require functional equivalence work; do not claim them fixed without evidence.


## Real-device feedback — 2026-11-23 11:47 Brasília

- **CUSA08809 Shadow of the Colossus 1.00** (`918F23DF`):
  invoked NID `rcQCUr0EaRU` = `_Getptoupper` failed ENOSYS 38 and
  crashed before first frame. This is not the earlier qsort/_Log failure.
  Added guest-VMM owned 257-short Dinkumware `_Getpctype`,
  `_Getptolower` and `_Getptoupper` tables.
- **CUSA00785 The Order 1886 1.02** (`A3EF3608`):
  nine `Phi` SRT walker failures and invalid T# texture descriptors
  precede SIGSEGV in selected Turnip at +0xb77da0.
  Ported the coherent architecture-independent shader footer metadata,
  runtime-indexed `ReadConstArray` IR operation and SPIR-V loads from
  reviewed upstream shadPS4 PR #5624 (12-file Bionic-compatible source
  integration), keeping the native ARM64 guest-VMM SRT walker; bound
  input slots and metadata, bump stale shader binary cache generation.
- Native log marker
  `BACHATA_CORE_PARITY=20261123-SRT2-CTYPE3-CE1-OWNEDCB` distinguishes
  this rebuilt core from inherited frontend runtime version `9ceb...`
  and upstream source revision `be6...`. The signed APK also embeds
  `assets/bachata-bionic-build.json` with the actual native core SHA.

Passing source CI checks does not guarantee gameplay. Independent
Release 0.2.6 parity gaps still include CMask ownership, BufferCache
GPU dirty tracking and readback, Vulkan memory budgeting, SAF broker
semantics, and remaining FEX libc/HLE aliases. These remain unverified
and must not be reported as fixed by this build.
