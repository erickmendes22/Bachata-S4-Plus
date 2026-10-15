# n054 follow-up: final-color identity and the actual HUD draw

The tested SDK is packaged as n055 with P36 v2/v3 signatures. This is not a
claim of physical-device cyan elimination. Base: 1878b8bb1d0b9fc82dd67e9f1f104a5264de8d1f.

## Evidence recovered from 91F991B9

The exact n054 source is recorded in releases/n054.json. Four fenced temporal
probes show native R=G=1.000 before the RGBA16F copy and AMD dispatch. The first
sample is native mean (1,1,0,0.992). Clone, reconstruction, pre-HUD and matched
WSI samples retain that saturation. SELECTED_SCENE_WRITER records a separate
640x360 RGBA8 allocation, vertex hash 8747a367, pixel hash a291c498 and
ui_same_backing=0. The diagnostic itself says final_color_identity_proven=0.

The reference port explicitly identifies vs 8747a367 as a lighting pass:
https://github.com/ducvd89/Bloodborne-Android/blob/d58769c8ae2f36b4f22db864b68e9bffc21a04d2/docs/CHANGES_2026-10-03.md
Its frame map distinguishes lighting from the final RGBA8 tonemap/UI target:
https://github.com/ducvd89/Bloodborne-Android/blob/d58769c8ae2f36b4f22db864b68e9bffc21a04d2/docs/upscaler.md
This supports rejecting the selected intermediate; it does not prove that all
phone corruption is caused by that one writer, or explain why that attachment
has RGBA8 format. No shader-hash blacklist, channel remapping or clamp is used.

The report also has temporal frame gaps, including 3052 -> 3581. It does not
record every final HUD draw, so it cannot prove which of those gaps reuse a
rendering instance. No causal assertion about all 529 missing frames is made.

## Implementation

Port OnDraw requires the scene LDR target to be the current HUD color target.
Reinstate that identity check. n054's cross-CB fixture accepted an unrelated
texture; that fixture now verifies refusal and no AMD dispatch. Actual separate
command buffers remain supported: submitted camera/depth can authorize a later
final-color/HUD draw on the same verified graphics queue.

Core025 Scheduler can suppress BeginRendering when RenderState does not change.
Observe the real graphics draw, on its Vulkan recording thread, after the Movie
pipeline is bound and before forwarding it. When the preceding executed draw
proves a full camera-sized scene in this very attachment, prepare the temporal
resources, end the stored rendering instance, reconstruct/compose and resume
with LOAD. This connects production Vulkan draw interception, without a native
scheduler callback, another core, or a core rebuild.

Own copies of rendering attachment data; retain separate depth and stencil
layouts/operations. Reject extension chains, secondary/suspended rendering,
multiview, layers, offsets, resolves and unstored attachments before END. Track
active queries through both Vulkan proc lookup routes and refuse interruption
inside a query. An explicit memory dependency preserves color/depth/stencil
between rendering instances, also on dispatch failure. A Movie writer retires
its pre-HUD candidate so queue submission cannot resurrect HUD-contaminated
pixels after a declined/warmup dispatch. Existing bounded probes are retained;
no additional device instrumentation or log budget is introduced.

## Executed local verification

Exact FireBurn/FSR-Vulkan c64f093404125e960813f95f1996c14780f0dd69 with the same
Port patches 0002/0003 and existing combined-depth/stencil patch. Host SDK built
with BS4_FSR31_TEST_HARNESS; real AMD FSR3.1 dispatch executes on lavapipe with
Khronos synchronization validation enabled. Every case checks its completion
marker, return code and absence of validation errors.

21 GPU scenarios passed:
- final draw/HUD in one rendering instance: seven consecutive temporal frames;
- submitted camera in a separate CB, final color/HUD in one later instance;
- final color/HUD in separate rendering instances;
- nonuniform two-color scene, FP16 path and Float16-without-Int16 fallback;
- depth/stencil retained at depth .25 and stencil 7 after all eight frames;
- active occlusion query refuses interruption and records no temporal dispatch;
- unrelated cross-CB intermediate rejected without temporal dispatch;
- depth reads/clears, partial/discarded color and local/cross-CB overwrites;
- negative controls remove the actual draw connection in same/cross-CB cases,
  or restore old final-color selection: all fail full-frame image assertions;
- partial/overwrite historical controls reproduce the stale-image defects.

Same-pass uniform output preserves exactly 2,068,600 background pixels and
5,000 HUD pixels after warmup. With the draw callback removed, only 225,400
background pixels remain: the real 640x360 rectangle minus the HUD. This
reproduces the missing production boundary rather than merely testing that the
SDK compiles or that a direct test-only native callback can dispatch.

Native observer tests, owned rendering snapshot tests and existing scene
transition checks also pass. ARM64 and the full existing GPU/WSI regression workflow also passed:
https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/38730560673
Source commit: 1586ddba0c3faa4653a32446553ad34124a6f53d.
ARM64 SDK SHA256: c68ebe3697661a14b26f2ca10ac7887d4f923180e4b8e6f3a04a7d556f56f304.
Artifact archive SHA256: 619b05a5b24885f7b47702c10bc4ced4ceab2267f5457d4f74f8a9a9dee953dc.
The downloaded artifact digest and all four new GPU logs were checked: eight
frames each, zero Vulkan validation errors. Production ARM64 strings contain
neither BS4_TEST_NO_DRAW_BOUNDARY nor BS4_TEST_ACCEPT_UNRELATED_SCENE.

The exact n054 APK was recovered and its SHA256 matches releases/n054.json.
Both embedded Bloodborne catalogs were read. The decoupled 640x360 preset
contains the 640/360 immediate substitutions and dimension-read hooks; no
explicit format-replacement operation was identified in that preset. Without
the actual Bloodborne guest executable, this byte-payload inspection cannot
establish the complete semantics of every patched guest call site.

## Remaining release gates

No device execution of this correction is available. The original report does
not prove that the final native target has a camera-sized viewport in every
problem scene, nor whether additional post-processing/format faults remain.
Thus phone cyan/saturation elimination and continuous temporal gameplay remain
unverified. The earlier R27 native compatibility-hook regression is documented
separately in N053-HOOK-REGRESSION.md and is not repaired by this SDK-only work.
The n055 APK includes these tested source corrections; do not describe physical
cyan elimination or all R27 stability problems as confirmed by synthetic tests.
Packaging details and exact APK/SDK/core hashes are recorded in releases/n055.json.
All 562 runtime entries, unchanged non-SDK payloads, stored ZIP alignment and
P36 v2/v3 signatures across SDK 24–36 were verified before delivery.
