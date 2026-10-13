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

The native renderer producer is NOT connected yet. An exported API alone is not
an implementation in the running application. The current core's internal scene
state must call it with verified camera/depth/viewport/jitter data and a frame
boundary. No inference from Vulkan viewport size can replace raw Gnm signs.
Actual applied jitter, object motion, reactive masking and proper native HUD
routing remain integration work. R13's original heuristic pre-UI boundary and
composition also need game validation before a release.

CPU contract tests and an ARM64 build do not demonstrate functional FSR on the
phone or prove that the R23 heap crash is gone. No APK is produced from this
checkpoint, and the baseline runtime must not be renamed as a new version.
