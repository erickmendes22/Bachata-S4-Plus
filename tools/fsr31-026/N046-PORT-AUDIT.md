# n046: Port integration audit after 13BF1B79

## Device evidence and scope

The n045 report 13BF1B79 still records a real temporal AMD dispatch (640x360 -> 1280x720) and pre-UI composition into a 1920x1080 HUD target. The screenshot is cyan/white. The session is CANCELLED_BY_USER, with no guest heap panic; the generic BACKEND_CRASHED field alone is not a crash finding. n045's reused-attachment guard logged a full 640x360 pass, not evidence of the partial-pass synthetic reproduction. Neither that reproduction nor an initial dispatch marker proves the cause of this phone corruption or validates every presented frame.

Reference: ducvd89/Bloodborne-Android d58769c8ae2f36b4f22db864b68e9bffc21a04d2. FSR backend: FireBurn/FSR-Vulkan c64f093404125e960813f95f1996c14780f0dd69, verified against the Port's gitlink. Its patches 0002 and 0003 are already applied by our workflow; omitted 0001 affects FSR 4 timing/statistics, not FSR 3.1. The existing native core025 is retained, not rebuilt.

## Differences checked

| Area | Port | Shipped n045 / n046 status | Implication |
|---|---|---|---|
| AMD backend revision | c64f093, patched for device-local memory | Same revision and relevant Port patches | No evidence that another FSR version is the fix |
| Scaled LDR context | flags=0, preExposure=1, positive jitter, far=3000 | Same values | Do not flip jitter/HDR flags speculatively |
| Scene identity | OnDraw requires the LDR target to equal the current UI color target, and excludes display buffers | Reduced stored RGBA8 candidate matched by camera/backing extent, submitted cross-CB to a different 1080p HUD target | Dimensions and submission ordering do not prove the same scene/target identity |
| Color resource | The real tonemapped RGBA8 image or its SceneTargets proxy goes to FSR | Native RGBA8 is blitted to an owned RGBA16F clone first | Extra conversion/copy; pixel samples now distinguish native corruption from clone corruption. UNORM-to-float preserves numeric values; it does not decode gamma |
| Reduced render targets | SceneTargets keeps proxy/native coherence for raster, compute, sampling and native access | Guest resolution patch, Vulkan capture and layout ledger; no equivalent full SceneTargets ownership model | Must not claim complete Port resource parity |
| UI/display composition | Owned output-sized color/depth, stencil-only masks, target/sample redirection through the display pass | Production uses pre-UI blit into the native 1080p attachment. Owned-UI code is exercised only by explicit test harness calls | The independent function tests do not prove the production draw hook or display redirection |
| Native hook coverage | OnDraw is part of the renderer | Exact APK core025 has the original prologue at 0x12f6828, a zero draw-hook cave at 0x3e85400, no bs4_fsr31_native_begin symbol. SDK also gates scheduler insertion off in production | No FIRST_REAL_RUNSCALED_UI should be inferred. Re-enabling the previously discarded scheduler callback would reintroduce a known regression |
| Frame boundary | OnDisplayPass in the renderer command stream | vkQueuePresentKHR observer / process frame counter | Different timing model; input/camera-frame provenance must be checked |
| Jitter coverage | Scene geometry through the rasterizer | Direct/indexed draws; indirect G-buffer draws were unshifted | n046 shifts proven indirect G-buffer geometry and restores the viewport; does not guess GPU vertex counts for post-processes |
| Temporal history | Reset after an actual frame without dispatch | Camera history previously advanced even when the AMD dispatch was skipped | n046 resets using the last actual temporal camera frame and prevents advancing history twice for one camera frame |
| Motion | Camera reprojection plus object-motion shader replay when valid | Camera only, mode=0 | Animated characters/foliage have incomplete motion. This is a quality gap, not proof of the cyan cause |
| Reactive masks | Opaque snapshot / reactive-composition mask pipeline | No masks | Another quality/transparency gap; do not attribute full-scene saturation to it without resource evidence |
| Device capabilities | Passes the actually enabled FP16/subgroup capabilities | Optional flags default to disabled in acquired_device | n046 forwards only the capabilities actually enabled in vkCreateDevice, as the Port does; no new optional feature is enabled. Both FP32 and actually enabled FP16 are tested |
| Testing | Frame/texture dumps, shader tests, GPU validation | Mostly uniform-clear scene fixtures and normal validation | Uniform output and zero ordinary VUID errors do not exclude data hazards or establish frame quality |

## Changes and evidence collection

n046 corrects the skipped-dispatch history rule, indirect G-buffer jitter and live device-capability propagation. It adds readonly samples at six GPU stages: native color, RGBA16F clone, FSR output, pre-HUD composition, motion vectors and depth. Each stage has a 3x3 grid of 8x8 tiles (576 pixels); four existing fenced slots need about 108 KiB of host buffers, plus allocation alignment. Samples are read only when the actual submission fence completes. No per-frame device-idle wait, scheduler operation, image recoloring, RGB workaround or guest-memory write is added. Reporting is bounded to 96 lines, sampling the first 512 real dispatches and then one in sixteen.

GPU_FRAME_PROBE reports cyan/white counts, nonfinite values, top/bottom counts, mean RGBA, motion range, depth range, actual formats, camera frame, dispatch sequence and history reset. This samples resources; it does not prove every displayed pixel or catch every transient event. It captures the UI background before HUD draws, not the final Android surface.

Interpretation: native cyan points upstream of the FSR copy; a normal native input but cyan clone points to the conversion/resource stage; normal inputs with cyan FSR output point to the reconstruction/history/backend stage; normal output with cyan pre-HUD target points to composition. If all sampled stages are normal during visible corruption, inspect later HUD/display/presenter operations rather than blaming the AMD dispatch. Nonfinite motion/depth gives a separate input-contract lead.

Coverage now includes a patterned two-color scene and Vulkan synchronization validation, in addition to real AMD dispatch, cross-CB ordering, depth/stencil, abandoned recording, partial overwrite and owned-UI algorithm tests. The latter remain function-level coverage: the production native draw hook is absent. Phone cyan elimination is not claimed.

The owned-UI path has **not** been activated by reintroducing its old scheduler hook. An actual Vulkan-draw connection needs a correct current-rendering boundary, full color/depth/stencil handling, GPU-safe UI lifetime, and sampled-image/display redirection across CBs. Existing same-CB scope tests do not establish these production contracts; activating the old callback merely because its standalone test passes would repeat the regression. The six-stage samples locate whether the current visible cyan originates before or inside reconstruction, at pre-HUD composition, or later in the display path.

FP16 validation found an additional dependency: generated AMD FP16 SPIR-V declares Int16 in some passes. The adapter therefore permits that shader path only when both shaderFloat16 and shaderInt16 were actually enabled. Tests cover both enabled (real FP16 reconstruction) and Float16-only (safe FP32 reconstruction, no invalid shader capabilities). A failed initial test caught the dependency before packaging; no APK using that failed configuration was delivered.

Final source: bff61ce221a3a7a4c59ba5767d08975e9d799625. Successful ARM64/software-Vulkan run: https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/38568242720. No phone test of n046 has been completed.

Another inspected failure path was unsafe: copies/motion were already recorded before AMD returned an error, but the slot was marked owned only after success. n046 reserves the slot before the first GPU command and drains/rebuilds partial history after failure. A GPU test forces failure after a real AMD recording and verifies that the real queue receives the slot's completion marker; the following frames rebuild and reconstruct successfully. This is not asserted as the cause of 13BF1B79, which has no such dispatch-failure marker.
