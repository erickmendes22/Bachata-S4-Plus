# N056: recognize core hardware-window scene rectangles

## Device evidence and limits

Diagnostic BS4-20261015-852B84AB runs n055 on NX789J/SM8750, Turnip
Adreno 830, Bloodborne CUSA03173 01.09. The SDK intercepts Vulkan and sees
640x360 camera/lighting intermediates and a later UI command buffer, but
records zero temporal contexts, dispatches, or pixel probes. The session was
stopped by the user; this log does not establish a native crash or whether
blue/saturation improved. It does not record the final target raw viewport.

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
