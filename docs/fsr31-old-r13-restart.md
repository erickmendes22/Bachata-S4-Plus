# Old R13 FSR restart on current core025

The user explicitly requests ONLY the old R13 FSR implementation as the base.
Core024 is not the target or a replacement executable. The target remains the
current core025. `tools/fsr31-026/old-r13-baseline.json` locks the recovered
old APK/SDK and current native executable hashes. The old R13 source baseline
is e1811c2; binary reproducibility against its SDK is not yet demonstrated.

Both supplied R23 diagnostics (56634D86 and D8BFEA40) still report the same
DLRegularHeap.cpp:710 failure and eboot.bin+0x2085962 despite the repaired width
helper. That repair did not establish the cause or solve the corruption.

This branch starts at old R13, not at the later defective Vulkan interception.
No port_ui_redirect.cpp, speculative HUD pass suspension, descriptor substitution,
or later custom bounds guard is carried into this branch. The R13 FSR algorithm,
pre-UI boundary and default SDK behavior are retained during integration.
Only the Vulkan owner restriction is retargeted to core025.

## Implemented foundation

The pinned Port camera shader is copied byte-for-byte. An explicit versioned
renderer handoff copies genuine 864-byte constants, scene/depth identity,
raw Gnm viewport signs, and the jitter actually used to rasterize. Its history
rejects stale/reused command buffers, wrong depth, unrelated cameras and invalid
constants. Camera gaps and scene cuts reset history; the first camera warms it.
The current/previous matrices reconstruct pixel motion from scene depth, with
the Port's viewport orientation, near plane, far=3000 and vertical FOV.

The SDK consumes this handoff in explicit `BACHATA_FSR31_INPUT=port` mode.
There is no optical-flow substitute in that mode. The baseline optical path
remains unchanged by default until integration is complete. The Port mode crops
the actual rendered scene rectangle rather than resampling an entire oversized
allocation, and does not allocate/copy previous color for optical motion.
It records only at the old R13 boundary outside a rendering instance.

## Not complete / no APK release

The producer is now connected to native uniform descriptors and the core025
120-byte graphics PushData. Its first four floats are accepted ONLY when their
viewport offsets/scales agree with the actual recorded viewport. This is a
runtime check of the field interpretation, not a sign guessed from image size.
The native executable resolves vkCmdPushConstants at table+0x360 and records the
120-byte block at 0x1277b68..0x1277b78 and 0x1278a40..0x1278a58 (hash locked).

The observer never replaces guest descriptors or writes mapped buffers. It
selects a >=5 MRT/depth G-buffer and verifies the 864-byte camera signature.
Mapped range lengths are checked, including VK_WHOLE_SIZE allocation bounds.
History advances at the current core025 Presenter hook; reused CBs are reset.

A Port Halton viewport shift is applied to supported scene geometry only, when
the actual viewport matches the camera render dimensions and uses its depth.
The original unshifted viewport is restored immediately after every draw, so
native state caching stays valid. That recorded shift is passed to FSR; it is
never claimed applied when the geometry was not shifted. First-frame warmup
is unshifted. Unsupported indirect geometry remains unshifted.

Object motion, reactive masking and proper native HUD routing remain integration
work. The observer has not been validated against new device logs yet. R13's original heuristic pre-UI boundary and
composition also need game validation before a release.

CPU contract tests and an ARM64 build do not demonstrate functional FSR on the
phone or prove that the R23 heap crash is gone. No APK is produced from this
checkpoint, and the baseline runtime must not be renamed as a new version.

## First GPU validation caught an inherited R13 bug

Run 38397303759 executes the camera shader and real AMD dispatch. Vulkan
validation rejects copying/blitting the R13 output because its creation usage
omits TRANSFER_SRC (VUID 01212 / srcImage-00186). The old pre-UI composition
already needs that usage. It is now added at allocation, rather than silencing
validation. The test restores the output layout after readback and runs 12
frames to exercise output-slot reuse. This proves an invalid Vulkan usage;
it does not prove that this was the device's DLRegularHeap crash cause.

## Complete composition test (38401776893)

The old-R13 path now captures native constants before BeginRendering. Known
movie VS identity is obtained from the graphics pipeline layout supplied by
native BindResources before the rendering instance starts. The pinned Port
movie hash list is copied unchanged. No pass is ended/reopened by the SDK.
The native viewport WithCount family is preserved when applying/restoring
jitter. A proven reduced scene's render area is corrected only when native
camera and actual attachment sizes agree; unsupported areas are untouched.

The real SDK test passes 11 dispatches at 640x360 -> 1280x720 and 11 at
1280x720 -> 1280x720 temporal AA. The complete composition test runs eight
frames through the native descriptor camera observer, R13 scene boundary,
real camera shader and AMD dispatch, then the original guest UI image. Its
first frame warms history. All seven subsequent frames retain 2,068,600 blue
scene pixels and 5,000 red HUD pixels in the 1920x1080 original UI attachment.
No Vulkan validation errors occur. GPU clears represent scene/HUD draws;
these tests do not execute Bloodborne or reproduce the Adreno/FEX heap fault.

The updated SDK selects Port inputs by default only for current core025 and
an enabled Android-forwarded mode, before native Vulkan tables are resolved.
An explicit input override is preserved. Other core routes stay unchanged.
No DEX changes are needed for the existing preset UI/environment bridge.
