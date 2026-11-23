# Source-first parity: Shadow of the Colossus and The Order 1886

Date: 2026-11-23. Bachata 0.18.1 Bionic FEX branch; both PS4 titles run from guest ELF, not from their separate host-only loaders. Do not mix their guest ABI with host C stdio or desktop Xbyak without adaptation.

## Shadow of the Colossus — source evidence

- Repo: `erickmendes22/ShadowOfTheColossus-Android-Aot@6556a9f15747395c13b48a058394b00866989b6e`.
- `src/sotc_import_names.inc` identifies actual PS4 NIDs for malloc `gQX+4GDQjpM`, free `tIhsqj0qsFE`, memcpy `Q3VBxCXhUHs`, memset `8zTFvBIAIN8` and vsnprintf `Q2V+iqvjgC0`, as well as FIOS2 FHOpen/ArchiveMount/OpGetError.
- `scripts/link_libc.py` links the *real game's libc.prx* by NID, module, library and version; lookup by NID alone is insufficient. The dedicated standalone port is not an in-place shadPS4 HLE implementation and must not replace the Bionic FEX linker.
- `src/runtime_sotc.c` implements title-specific `sceLibcHeapGetTraceInfo` and sysmodule/DiscMap helpers; only port ABI-correct functions when the actual Bachata HLE or its log proves a missing function. Do not insert unconditional return-0 stubs.
- Bachata changes: the `62bd48cadd9f380c9a0ca127493744cbddad19df` source revision registers the guest libcInternal imports with native FEX ABI and registers native FIOS2 before ELF import relocation unless a title-specific LLE library is staged. The preflight and full compile succeeded in Actions run 45286132671; gameplay remains to be verified.

## The Order 1886 — source evidence and adaptation

- Source: `erickmendes22/gow3_android_daedalus_fork@524e74a3b3a67135e02a1b7e68d2b83359da9e96`, branch `fix/order1886-adreno830-pervertex-interpolation`.
- The dedicated port's `the-order-1886-android/overlay/gpu/shadps4/video_core/renderer_vulkan/vk_pipeline_cache.cpp` calls a guest-read sync callback *between* SRT flattening and resource patching, before shader specialization caches resource descriptors.
- Its `vk_rasterizer.cpp` calls `ReadBackGpuWrittenSrtSources`; the accompanying `buffer_cache.cpp` batches 4KiB SRT pages and uses one completion fence instead of a fence per page, and `order1886_arm64_srt.inc` can trace guest SRT source addresses.
- Previous Bachata Bionic code read back dirty SRT pages only during `Rasterizer::BindResources`, **after** `ResourcePatchingPass` had already consumed descriptor values. The delayed readback can leave corrupted resources in the compiled shader even if the bytes become correct later.
- `port_order1886_srt_pipeline_sync.py` ports the missing callback into the 0.18.1 Bionic `TranslateProgram`, `PipelineCache` and `Rasterizer`. It reuses the existing VMM-checked portable SRT walker and page-refresh tracking rather than transplanting incompatible older Xbyak code.
- Limitations: This addresses sync timing, not every nonuniform `ReadLane`/`Phi` offset. The original 0.2.6/0.2.7 ARM64 emitter's remaining semantics and additional image-to-buffer readbacks still require evidence/porting. A signed APK does not prove rendering is fixed.

## Verification and rollback

- Source-first gate requires markers in native `recompiler.cpp`, `vk_pipeline_cache.h/.cpp` and `vk_rasterizer.cpp`, with unique source anchors.
- Core's source revision is stamped into runtime logs. Shader metadata and binary versions are bumped to avoid stale cached SRT descriptors.
- Full native cross-compilation and original P36 signing are required. If gameplay fails, correlate source revision, first SRT/ENOSYS error, source page reads and Vulkan crash; never equate compiler success to game fix.
