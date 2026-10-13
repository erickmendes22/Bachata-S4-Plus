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

## Executable investigation: a proven width/height hook defect

The subsequently supplied SELF executable has SHA256
`d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9`.
Its uncompressed executable PT_LOAD is SELF entry 1, file offset `0x28eb0`,
virtual offset zero; the game's load base is `0x400000`.

Both crash sites are inside the free/coalescing function starting at
`0x24858a0`. At `0x2485962` it reads a free-list link from `[rax+0x10]`;
at `0x24859c7` it writes the merged-block link to `[rdx-2]`. The invalid
values are heap block metadata, rather than an FSR API return value.
The preceding writer is still not identified by these crash snapshots.

The integration replaces two original instructions at `0x01258F2C`:
`mov eax,[r12+0x50]; mov ecx,[r12+0x54]`, width and height. Its injected
helper at `0x04D3BAF0` reads the global descriptor into RAX and height into
ECX, then returns. It never loads width into EAX. The immediate continuation
at `0x01258F36` converts RAX to float and at `0x01258F48` divides by that
value to calculate inverse width. Other half/quarter pixel constants also
use it. This is a proven integration error feeding a pointer as a dimension.

`fix_decoupled_resolution_hook.py` adds `mov eax,[rax+0x80]` AFTER the
height read and before RET. No other patch bytes or selections change.
The helper grows from 21 to 27 bytes and fits before the next patched range.
Its caller's relative CALL remains unchanged. CPU emulation of the actual
x86-64 caller/helper reproduces the wrong pointer return, and verifies exact
native width/height return registers, R12 and stack preservation after the
fix for all four presets. This targeted repair takes precedence over the
broader reference-profile candidate described above; that candidate is not
applied alongside it.

This proves the faulty hook and its repair. It does not yet establish that
the hook caused the heap overwrite, or that either device crash is fixed.

## R23 outcome: 56634D86 / D8BFEA40

Both diagnostics show runtime R23 and the repaired 27-byte helper actually
applied at 80984816. Both still fault at `eboot.bin+0x2085962`, with block
`0x254c80000`, header `0x254c7fff0`, and invalid links
`0x3c00000000000000`. The same failure after the repaired instruction rules
out that instruction repair as a sufficient fix. The main regression remains.

The earlier GPU integration tests did not exercise 1920x1080 render areas
with physically 640x360 attachments. That shape violates Vulkan rendering
attachment bounds (VkRenderingInfo VUID-pNext-06079/06080), but the device
logs do not associate the reported 1920x1080 rejected passes with the
later captured 640x360 image in the same event. Do not claim that these
logs alone establish that shape on the device or that it caused the heap
overwrite.

The new bounds guard and regression test cover that missing case, including
mip-relative attachment extents and both core/KHR dynamic rendering hooks.
The CI negative control runs the same test against the R23 capture source;
the positive control uses the guarded source with Vulkan validation.
This is source/test work, not a validated device crash fix. No subsequent
APK is authorized for delivery as a fix while the reported failure persists
or its resolution remains unproved.
