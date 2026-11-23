# Bachata S4+ Release 0.2.6 GPU/PS4 core parity audit (2026-11-23)

This document records a direct, function-level comparison of two actual Android
AArch64 ELF libraries, **not** merely a source-string or APK filename comparison.

## Source identity

| Field | Release 0.2.6 | Latest source-ported 0.18.1 |
|---|---|---|
| Native library | `libbachata_native_runtime.so` | `libbachata_bionic_core.so` |
| Bytes | 87365424 | 473636576 |
| SHA256 | `3548cb4b6d952aed7141f057e07552b4f23a57997df339644a57605ed1308f39` | `c68102278d59f01eb0f4f0372952e7fc487f272481ea6a590d8e2a9865a735ff` |
| Origin | Original binary, private source `JICA98/Bachata-S4-Dev` | GitHub Actions [45110585911](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/45110585911) |
| PS4 base | modified 0.18.1 WIP | merged public 0.18.1 WIP |

## Confirmed GPU-copy discrepancy (patched at shared core)

`AmdGpu::Liverpool::CopyCmdBuffers`:

- Release ELF at `0x371b538` (156 bytes) allocates one 48-byte holder with
  two `std::vector<u32>` instances, and fills each using a vector assignment.
- Source-ported ELF at `0x320c1a4` (560 bytes) uses fixed-size shared
  `mapped_queues[GfxQueueId].dcb_buffer/ccb_buffer` and asserts on
  `capacity >= buffer_offset + input_size`.
- Diagnostic `BS4-20261123-0DEB19BC` ends with exact
  `liverpool.cpp:1137 CopyCmdBuffers: Assertion Failed!`.
- Re-reserving the shared vectors while GPU coroutines still own spans can
  cause use-after-free. This is a *core lifetime bug*, not a game-specific patch.
- `port_release026_cmd_buffers.py` copies the inputs into independently-owned
  vectors which are *moved into each ProcessGraphics coroutine frame* and held
  until the task is destroyed. It removes global staging and resets, preserving
  the existing public `ReserveCopyBufferSpace` call as a compatibility no-op.
- The preflight verifies exact pinned anchors and forbids the old assertion.
  **Device runtime resolution remains unverified until a signed APK is tested.**

## Release-only dynamic symbols to audit (NOT fixed by the buffer patch)

- `AmdGpu::Liverpool::ProcessCeQueue` — global constant engine, command chains.
- `VideoCore::TextureCache::ResolveCMaskOwner` — CMask image ownership.
- `VideoCore::BufferCache::AddGpuModified` — data ownership and coherency.
- `VideoCore::BufferCache::BeginUploadBatch` — upload synchronization.
- `Shader::Backend::SPIRV::EmitContext::EmitBdaLoad32` — buffer device addressing.
- `Vulkan::Instance::GetLiveGpuMemoryBudget` and `ProbeImageSize` — memory limits.
- `Core::FileSys::SafFsBackend` and `SafBrokerClient` — release SAF broker
  (the source port uses a separate `BachataSaf` implementation).

Missing exported symbols are not proof of missing functionality; private,
inlined and non-exported implementations require actual behavioral/code analysis.

## Remaining faults in the test log

- 38 SRT walker failures: 15 `ReadLane`, 8 `Phi` unexpected opcodes.
  These must not be replaced with zero or discarded without verifying SSA/lane
  semantics: missing SRT offsets can alter shader resources.
- 90 reported unresolved FEX libc HLE imports with temporary `ENOSYS`
  veneers. Log imports alone do not imply the functions were actually invoked.
  Guest callbacks, variadics, FILE and time structs need correct guest ABI.

The CI must keep FEX/SAF/Vulkan native libraries intact and reuse verified
cache artifacts. Stop at fast preflight if the source integration fails; the
large Android build is intentionally opt-in via `[build-apk]`.

This commit requests one signed Android test build **after** the source preflight
on merge commit `6176203d0e959034000eec9f77ae5912cdbb4dfc` succeeded.
