# R22 device regression: 7EFCD0B7 / 6E3C385D

R22 did not fix the reported visual corruption or crashes. Both diagnostics
identify runtime `bachata-s4-r022-0.2.6-r`, capture the 640x360 camera, and
record a real FSR 3.1 dispatch followed by shader-identified UI composition
with vertex shader `34e8a281`. Thus the new boundary check was exercised;
its successful execution does not establish correct game rendering.

`7EFCD0B7` has the rgba8f patch enabled and faults in GXRenderThread at
`eboot.bin+0x20859c7`. `6E3C385D` has that patch disabled and reports
DLRegularHeap.cpp(710), invalid/already-freed block, before faulting in
Game:Main at `eboot.bin+0x2085962`. Both contain the invalid pointer value
`0x3c00000000000000`. Its byte representation also decodes as RGBA16F
`(0, 0, 0, 1)`. This is a diagnostic clue; it does not prove an image
download or identify the writer. Do not attribute this regression to the
rgba8f toggle or treat the detected heap failure as the original write.

## Verified implementation divergence

The controlled Decoupled 1080p UI profile in R22 contains 26 custom writes,
including target creation changes and code caves. It is not the resolution
patch used by the pinned Android port. The reference uses the community
1280x720 template with 66 writes and modifies four scene/UI immediate fields;
its fixed native allocation dimensions remain 1920x1080.

`tools/fsr31-025/port_resolution_patch.py` prepares replacement controlled
profiles using the exact template from ducvd89/Bloodborne-Android commit
`d58769c8ae2f36b4f22db864b68e9bffc21a04d2`. Existing unrelated patches,
profile names and enabled selections are preserved. No custom allocation
or cave writes are retained. This candidate is not installed by merely
building the SDK; packaging must explicitly apply it to each runtime
Bloodborne.xml. It has not been validated with the game on the device.

Local validation passed for the real R22 runtime XML and a generated fixture:
four preset write lists, native allocation/UI dimensions, preservation of
unrelated patches/selections, and repeat-application stability. An independent
comparison with the pinned port's `scripts/patches.py::resolution_writes`
produced byte-identical write lists for all four presets. Its writes do not
conflict with the other active patches recorded in 6E3C385D.

The cause of the heap overwrite remains unproved. The diagnostics do not
contain the game's executable bytes, the damaged heap contents, or the
preceding writes. No previously uploaded eboot has been identified as this
Bloodborne installation. Static investigation of the two failing allocator
sites and the custom target-creation edits needs its original eboot.bin.
Do not publish another APK as a crash fix on the strength of these static
patch checks or synthetic Vulkan tests.
