# Pre-FSR 0.2.6 / native core025 compatibility

R25 starts with the official pre-FSR `Bachata-S4-Plus-v0.2.6.apk`.
Its Android DEX, application resources, native Android libraries, legacy cores,
patch XML and all runtime entries are preserved. Only the FEX dispatcher is
replaced with the pre-FSR CORE025 R15 dispatcher and native core025 is added.
No FSR3 library, Android selector, native FSR3 hooks, or preload interception
is present. Runtime `bachata-s4-r025-0.2.6-r` forces fresh extraction.

## Spider-Man

Four native fixes from the shipped working core024 are missing in clean 025:

* Normalize graphics `stage_en 0x145` to `0x45`.
* Guard both HullShaderTransform attribute-region calls, retaining original
  native helper calls for valid isoline/triangle/quad regions.
* Emit native ConstU32(0) for attributes OffChipLdsBase/IsOffChipLds (91/92).

025 already includes the domain-shader no-LDS fallback at `0x11a4618`, which
searches ReadConstBuffer (opcode 11), resolves its V# through `0x11a55c4`,
records the real tessellation constants and initializes runtime information.
The old 024 stack-slot-based second-pass implementation is not duplicated.

## MediEvil

No VMM port is needed for the old confirmed issue. 024 originally reserved
user base `0x1000000000`, size `0x3000000000`, ending at `0x4000000000`;
the prior MediEvil fix extended the end to `0x4100000000`.
Clean 025 reserves user size `0x4000000000` and usable end `0x5000000000`.
The requested range `0x4000000000..0x4008000000` is already covered.
Verified constructor constants are `0x8cf68c`, `0x8cfba0`, `0x8d0164`.
This establishes coverage of that VMM fix, not device gameplay validation.

## Elden Ring

Clean 025 already recursively unwraps ReadFirstLane during native buffer,
image and sampler discovery (`0x11b1718`, `0x11b1ab8`, `0x11b1bf4`).
Only the safe C37 UndefU32 producer behavior is carried: an undefined dword
has no ReadConstBuffer producer to mark; retain its descriptor value unchanged.
Do not convert it to zero or import experimental cache, queue, or buffer caps.
This does not assert that all older Elden Ring experiments are required or
that every game crash is resolved.

## Validation

`test_core.py` executes 216 ARM64 cases at two PIE biases. It covers the
original native ConstU32 and literal writer, while constant interning through
the external C++ heap is modeled. Original valid region-helper calls and
skip destinations are checked. Undef leaves descriptor and flags intact.
Packaging checks every manifest SHA/size and byte identity of all untouched
APK/runtime entries. P36 APK signature is verified for V2 SDK24-27 and V3
SDK28-36. Device gameplay remains untested in this environment.

The SHA-pinned native 025 has inFAMOUS control hooks which are preserved.
No core024 executable code or offsets are substituted into 025.
