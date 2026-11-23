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

## Coherent CMask ownership + metadata-buffer alias correction

- Source port `port_release026_cmask_owner.py` records current
  `ImageId` and `image_uid` for CMask, FMask and HTile, transfers owner
  on address reuse and invalidates the prior owner's clear mask. Metadata
  removal is owner-checked; the `IsMeta`, `IsMetaCleared`, `ClearMeta`
  and `TouchMeta` operations reject stale/unregistered owners and invalid
  slice indices. A stale image cannot erase another live image’s CMask.
- Real `BufferCache::SynchronizeMemoryFromImage` CMask path now fills the
  alias with expanded sample-dependent patterns, matching modern shadPS4:
  samples=1/8 `0xFFFFFFFF`, samples=2 `0xDDDDDDDD`, samples=4
  `0xEEEEEEEE`. Unknown sample counts fail instead of fabricated bits.
- All modifications are applied to the pinned 0.18.1 source with
  fail-closed assertions and coherent source API checks in preflight.
- Source integration CI passed at run `45204246272` after replacing
  the only initial strict-anchor mismatch; none of this proves gameplay.

## First native compiler gate: single pinned-0.18.1 API incompatibility corrected

GitHub Actions run `45204565565` compiled the incremental target but
stopped at precisely one C++ error: `flatten_extended_userdata_pass.cpp`
was using upstream-2026 `profile.support_bda` absent in the pinned
0.18.1 `Shader::Profile`. The pinned version's
`CollectShaderInfoPass/EmitReadConst` are controlled by the
`IsDirectMemoryAccessEnabled()` setting directly; the SRT port now
uses that exact API. A redundant `u8 > 256` comparison was also
removed. The fast source/ABI recheck passed in run `45206833645`.
No gameplay claim is made by a successful compile.


## Critical FEX HLE gap: real libSceFiber guest x86 context switching

- The test `E35154E3` was run on the actual 20261123 core. Among its 823
  `ENOSYS (38)` calls, 801 were `libSceFiber` functions
  `sceFiberInitialize`, `sceFiberOptParamInitialize`, `sceFiberRun`,
  `sceFiberGetInfo` and `sceFiberRename`. This behavior was not
  affected by qsort, _Log, CMask or the independent CE FIFO.
- Pinned shadPS4 0.18.1 registers `libSceFiber.sprx` ONLY under
  `ARCH_X86_64`; ARM64/FEX therefore fell through to generated
  `UnsupportedHleCallAdapter` NIDs. This is an **actual structural
  HLE registration bug**, independent of any device GPU generation.
- New `bionic/generic/android_fex_fiber.cpp` supplies all **15 PS4
  libSceFiber NIDs**, including Run/Switch/ReturnToThread, by saving and
  restoring the FEX guest x86 GPR/XMM/RSP state at the syscall/RET boundary,
  not calling x86 assembler from the ARM64 host and not faking successes.
  Verifies guest memory ranges, alignment and fiber state. Wired into
  `ModulesToLoad` under `SHADPS4_ENABLE_FEX_GUEST_CPU` and the actual
  CMake target. Desktop x86 implementation is unchanged.
- Additional invoked `libc` NIDs `strcasecmp`, `strncasecmp`,
  `strstr` and `strspn` are implemented with validation of the game
  guest's memory before dereferencing it.
- A compile-and-run host ABI test `test_fex_fiber.py` is mandatory
  in the fast CI preflight. It simulates a new fiber entry, a Switch
  to a second fiber, its return to the first suspended context, and
  ReturnToThread while checking the original guest callee-saved
  registers and user-visible return argument.
- **Successful** fast source/ABI audit:
  `45217475240`. THIS IS NOT A DEVICE GAMEPLAY VALIDATION.

Two newly tested games on Snapdragon 8 Gen 3 were reported not
starting, but their CUSA IDs and diagnostics have not been supplied in
this conversation. Do not attribute their failure to fiber, SRT, or
Turnip without that evidence.


## SM8650 Snapdragon 8 Gen 3: CUSA00552 and CUSA05170 (2026-11-23 17:36 UTC)

Evidence: `bachata-diagnostic-BS4-20261123-E15EE7A3.zip`
(The Last of Us Remastered, CUSA00552) and
`bachata-diagnostic-BS4-20261123-91E5B622.zip`
(Dragon Quest Builders, CUSA05170). Both execute signed
Bionic `d8a9b6cabc93`, runtime
`bachata-s4-plus-0.2.7-bionic-ad2cd33dc3c15503`, driver
`turnip-bd457b30f195cf93`. There is no stale-extraction mismatch.

CUSA05170's observed FIOS2 behavior proved a real common-core bug:
`sceFiosArchiveMountSync` returned success and a fake handle=1
without opening `/app0/build.psarc`, instead mounting the
`/app0` directory at `PhyreFIOS2`. Hence subsequent opens for
`PhyreFIOS2/gra/shader/shader.GNM.phyre`,
`apricot.GNM.phyre`, and `vulgar/build_account.en.dic` failed,
followed by Phyre `initApplication ... (9)` and SIGSEGV.

Real common-code replacement: `PsarcBackend` (PSAR header + big
endian TOC + zlib block-size metadata) parses the archive manifest
and reads requested compressed blocks lazily through
`Core::FileSys::IFile` (including SAF-backed guest files), without
extracting gigabytes or fabricating asset bytes. FIOS2 returns success
only after a real valid archive was opened and indexed; missing or
unsupported archives log explicit failures. Mounted file operations,
stat, directory traversal, metadata, seek, reading, and unmount use
actual backend state. No game-specific patches. Fast host compilation
test verifies multiblock zlib, random reads, folder enumeration and
invalid archive rejection. Initial test warning was corrected;
latest source CI `45232500010` passes.

CUSA00552 independently faults at guest RIP `0x800e1e2d0`, host
read of 0x20, before any observed SRT/PSARC workload. That is NOT
proof of an archive or driver bug. Host PC points into JIT-generated
FEX memory. To avoid another speculative HLE change, the fatal
handler now maps the actual guest RIP against loaded PS4
modules and records `BIONIC_GUEST_CRASH_MODULE` with the module
base and RIP-relative offset for the next diagnosis. This changes
only fatal logging, not graphics or FEX execution.

The runtimeVersion and core marker remain automatically computed
from actual ELF/commit by the previous verified packaging pipeline.
This build requires repeat full ARM64 compile and P36 signature;
successful static CI is not proof of gameplay.
