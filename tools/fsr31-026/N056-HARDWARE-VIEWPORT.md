# N056: recognize core hardware-window scene rectangles

## Device evidence and limits

Diagnostic BS4-20261015-852B84AB runs n055 on NX789J/SM8750, Turnip
Adreno 830, Bloodborne CUSA03173 01.09. The SDK intercepts Vulkan and sees
640x360 camera/lighting intermediates and a later UI command buffer, but
records zero temporal contexts, dispatches, or pixel probes. The session was
stopped by the user; this log does not establish a native crash or whether
blue/saturation improved. It does not record the final target raw viewport.

Reference core source inspected at zenithblue-oss/shadps4-arm64
be6bc2e9c60799e071dd2fafa6216e8d80ec619c (the shipped binary is preserved,
not rebuilt from this checkout).

The n055 physical viewport predicate misses the core's clip-disabled path:
vk_rasterizer.cpp::UpdateViewports sets (0,0,min(maxViewportWidth,16384),
min(maxViewportHeight,16384)); emit_spirv_special.cpp::ConvertPositionToClipSpace
uses saved X/Y offset and scale push data to position the camera rectangle
inside that window. This is a concrete source-level integration gap, not yet
proof that it caused this device session's missing dispatch.

## Change

Save the first four raw push floats with each completed color writer. A later
HUD push cannot overwrite the candidate's rectangle. Keep ordinary camera
viewport selection, and additionally accept only an exact hardware window,
a finite camera-sized raw rectangle at origin, and one small fullscreen draw
(1 instance, at most 6 vertices). Keep same backing image as HUD, camera/depth
provenance, submission order, STORE, single sample and subresource checks.
No arbitrary RGBA8 intermediate is re-enabled. Add bounded PRE_UI_SCENE_BOUNDARY
logging so the actual target/viewport can be checked in a phone diagnostic.

The GPU fixture reproduces the core epilogue, then changes the upcoming HUD
push data to 1920x1080, while the completed writer remains 640x360. Exercise
both retained rendering and submitted camera command buffers. Negative
controls disable hardware-window recognition and must reproduce missing
full-frame reconstruction. Ordinary cases and unrelated-target rejection
remain in the existing suite. Software GPU results cannot establish device
color correctness, performance or stability.

Only the independent SDK changes; retained core025 and Android payloads stay
byte-identical. P36 packaging and validation are recorded after CI succeeds.

## Validation result

CI run 38742235627 at source c7e4706a67429c57f3903b76d44e0b511fb97780
passed ARM64 build, observer/rectangle tests and the complete software Vulkan
suite. Both window-same-pass and window-cross-cb show hardware_window=1,
640x360 saved scene push data despite the later 1920x1080 HUD push, real FSR
dispatch, 2,068,600 blue scene pixels plus 5,000 red HUD pixels on the 1920x1080
fixture, and zero validation errors. Physical-viewport-only negative controls
fail with the required missing reconstruction signature. Existing unrelated
intermediate, active query, depth/stencil, patterned and FP16 checks also pass.

ARM64 SDK SHA256: 2fb954e5de601a38670dcccc678338975d3d430bb66683cebc3cbf84bd397cea

Artifact 11976274382 SHA256:
ce6f457979a19875b6553f968a11c319815e44b24581e6de645cbf50d0703427.

These are synthetic integration results; no n056 phone test is available yet.

## Package

Bachata-S4-Plus-v0.2.6-R27-FSR31-CORE025-GLIBC-N056-P36.apk
(221572458 bytes), SHA256:
ca1204db51393cccb7b504d70eeef5d4df06488dcadb22946580dd547b590756.

Exact n055 base verified before replacement; all 562 runtime manifest hashes
verified; only host/libbachata_fsr31.so changes in runtime.zip. Core025 SHA256
c1cf8986c2a5f6f9f33d32a073eff797e2717b4848cd475c4d19f26dc7042bb2
and all Android DEX/manifest payloads are preserved. Official apksigner verifies
P36 v2 for SDK24-27 and v3 for SDK28-36. Signed entry payloads match the validated
unsigned APK; ZIP CRC, stored 4-byte and .so 16-KiB alignments pass.
