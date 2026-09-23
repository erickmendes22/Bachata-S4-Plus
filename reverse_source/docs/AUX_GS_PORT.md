# AUX-GS / per-vertex fallback port

Reference: public shadPS4 commit
`7db6e4ba56b98841624ab776aaa56763f10bdc89`.

This commit specifically documents The Order: 1886 as relying on direct P0/P10/P20 reads plus manual barycentric interpolation.

## Why the existing Bachata-equivalent path is insufficient

The current source-equivalent behavior recognizes `V_INTERP_MOV_F32` and `Qualifier::PerVertex`, but preserves per-vertex semantics only when the host exposes:

- `VK_AMD_shader_explicit_vertex_parameter`, or
- `VK_KHR_fragment_shader_barycentric`.

Without either feature, it degrades the input to `Flat`.

Changing Flat -> Smooth alone was already tested historically and did not fix the image, because Smooth cannot restore the three independent packed per-vertex values P0/P10/P20.

## Full port requirements

The fallback must be implemented as one coherent feature:

1. Add `is_vs_direct` and `prim_type` to fragment runtime metadata.
2. Permit PerVertex translation only when the fallback gate is eligible.
3. Restore barycentric input registers for the supported `persp_center` case.
4. Expand each PerVertex FS attribute into three flat interface locations.
5. Generate an auxiliary geometry shader that forwards P0/P10/P20 and emits smooth I/J coordinates.
6. Compile/cache the auxiliary GS alongside the fragment permutation.
7. Inject it into the Geometry stage only for pipelines with no real game GS.
8. Include the extra GS stage in graphics pipeline construction.
9. Persist/reload the auxiliary shader in the shader cache.
10. Bump the reconstructed shader metadata version.

## Eligibility gate

Only:
- direct VS -> FS
- TriangleList
- no AMD explicit vertex parameter
- no KHR fragment barycentric
- only supported persp-center barycentrics
- no clip-distance emulation

Unsupported cases must retain the previous fallback and emit a diagnostic warning.

## Validation plan for CUSA00785

Before judging visuals, logs must prove:
- fallback gate accepted the affected fragment shader;
- an AUX-GS was generated;
- the graphics pipeline contains the generated GS;
- P0/P10/P20 attributes occupy distinct locations;
- barycentric I/J input is initialized;
- current V5/V6/V8/V11 behaviors remain active.

Only after those checks should an APK be used for visual comparison.
