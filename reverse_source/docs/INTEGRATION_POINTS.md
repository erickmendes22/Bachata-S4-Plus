# AUX-GS integration points

This document describes where the reconstructed modules connect to the still-unreconstructed runtime.

## 1. BuildRuntimeInfo(Fragment)

Populate:

```cpp
runtime_info.fs_info.is_vs_direct =
    regs.stage_enable.raw == AmdGpu::ShaderStageEnable::VgtStages::Vs;
runtime_info.fs_info.prim_type = graphics_key.prim_type;
```

These are source-level facts required by the AUX-GS eligibility gate.

## 2. Fragment translation

When initializing barycentric VGPRs, treat the fallback as equivalent to native AMD/KHR support for the supported case:

```cpp
if (profile.supports_amd_shader_explicit_vertex_parameter ||
    profile.supports_fragment_shader_barycentric ||
    Bachata::PerVertexFallback::CanExpand(profile, runtime_info)) {
    // initialize barycentric attributes
}
```

For `V_INTERP_MOV_F32`, preserve `Qualifier::PerVertex` when the same condition is true. Do **not** replace it with Smooth.

## 3. SPIR-V fragment inputs

Call `BuildFragmentInputLayout`.

A PerVertex slot consumes three consecutive locations only when the fallback is active. The injected barycentric vec2 uses `bary_coord_location`.

The fragment-side reader must reconstruct component selection from the three flat inputs and use the smooth barycentric input for I/J.

## 4. Fragment module compilation

After translating the fragment shader, if `NeedsAuxGS()` is true:

- generate SPIR-V with `EmitAuxGS()`;
- compile it to a VkShaderModule;
- store it in `AuxGsCache` using the exact runtime permutation hash;
- persist the SPIR-V as an AuxiliaryShader blob.

## 5. Graphics pipeline lookup

Before creating a new pipeline:

- if a real game GS exists: do nothing;
- otherwise lookup the FS permutation in `AuxGsCache`;
- if present, place the module in the Geometry stage slot.

## 6. Graphics pipeline creation

When an auxiliary module occupies the Geometry slot, add a Geometry pipeline shader stage even though the game supplied no GS.

The pipeline topology still originates from the guest primitive type. The fallback eligibility gate currently allows TriangleList only.

## 7. Cache serialization

Persist:
- the two new fragment runtime fields;
- AUX-GS SPIR-V keyed by fragment permutation;
- shader metadata version 3.

Old metadata must be rejected/rebuilt rather than interpreted with the new layout.
