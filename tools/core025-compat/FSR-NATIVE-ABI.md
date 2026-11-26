# R27 existing core025: native scheduler evidence

Input SHA256: 373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59.
Addresses are ELF virtual addresses before PIE relocation. These observations
apply only to this hash. No native emulator was rebuilt or replaced.

`test_fsr_native_renderstate.py` executes the original scheduler worker at
0x12faa20 with Unicorn and intercepts its Vulkan BeginRendering callback.
Eight cases passed: zero/one/five/eight color attachments, depth/stencil
combinations, and zero/Android-like PIE bases. It checks actual VkRenderingInfo
and VkRenderingAttachmentInfo outputs, including image views, layouts, clears,
load/store operations, dimensions and layer count. This is an ABI test, not a
GPU test or an implemented OnDraw hook.

| Native RenderState field | Offset | Representation |
| --- | --- | --- |
| Color attachments | 0x000 | Eight entries, 0x20 bytes each |
| Color view/layout/clear/clear flag | entry + 0/8/12/28 | u64/u32/16 bytes/u32 |
| Depth/stencil view | 0x100 | u64 |
| Depth/stencil layout | 0x108 | u32 |
| Depth clear/stencil clear | 0x10c/0x110 | float/u32 |
| Depth enabled/clear, stencil enabled/clear | 0x11c–0x11f | Four bytes |
| Width/height | 0x120/0x124 | u32/u32 |
| Layers/color count | 0x128/0x12c | u32/u32 |

Native BeginRendering starts at 0x12f6828 and copies/compares 0x130 bytes.
EndRendering starts at 0x12f6e14. Native scheduler rendering flag is at this +
0x11d8, record-thread flag at this + 0x11e8, queue pointer at this + 0x11f0,
and direct command buffer at this + 0xf08. EndRendering clears the native
flag before either queuing or directly recording the Vulkan operation.
The record-thread begin callback is 0x12fac04 (a branch to 0x12faa20), and
the corresponding end callback is 0x12fac08. Queue operations must not be
replaced by unsynchronized Vulkan calls from the frontend thread.

The native cache can suppress a new BeginRendering when RenderState is
unchanged. Consequently, a Movie/UI draw on the existing LDR target cannot
be implemented by simply broadening the SDK's BeginRendering heuristic.
The positive same-target temporal composition case remains unimplemented.

## Verified SDK checkpoint

Commit: 3b30cef2eb63c7c853694290de5d01c0159492df.
GitHub SDK-only run: 38459496425, success.
ARM64 SDK SHA256: 11973b76b2c7815979503d8fc0d8353c48c76547bc1c80ebf238eaa7704de0c9.
Artifact archive SHA256: 14a83aba56fbb5856dc159802aa752cb1c3a7c2b4e7d1999e3d8404c41c2fc7c.

The separate-image GPU composition test preserves 2,068,600 background pixels
and 5,000 HUD pixels on frames 1–7, with no validation errors. Frame zero has
camera-history warmup and does not reconstruct the background.
The same-target preservation test keeps 225,400 background pixels and 5,000
HUD pixels on all eight frames, with no validation errors; it intentionally
does not dispatch FSR. Neither test proves Bloodborne/Adreno gameplay or fixes
the shared-target temporal integration gap. No APK was produced.
