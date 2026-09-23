# Bachata S4+ reverse-source reconstruction

This tree reconstructs a compilable source model for the **Bachata S4+ Box64 shadPS4 runtime** from validated binary behavior and diagnostics.

It is **not** claimed to be the original source of the historical Bachata binary.

## Rules

- Preserve behavior already validated on-device before refactoring.
- Mark every reconstructed function as one of:
  - `RE_CONFIRMED`: behavior/offset verified from the shipped ELF or diagnostics.
  - `SOURCE_EQUIVALENT`: high-level equivalent inferred from binary behavior and public shadPS4 sources.
  - `EXPERIMENTAL`: not yet behaviorally validated.
- Game-specific fixes remain gated to their title ID.
- Do not silently mix later failed experiments into the known-good baseline.

## Current validated Order: 1886 baseline

The current behavioral baseline is:

`V5 + V6 FIX2 + V8 + V11 SAFETABLE`

Validated properties:

- Box64 reaches gameplay.
- V5 null/empty image handling is active for shaders `0xa7b66f58` and `0xefaaab2b`.
- V6 writes `0x7F80000F` to `PushData::ud_regs[1]` for shader `0x9846aaff`.
- V8 preserves gameplay while handling the known depth-overlap path.
- V11/SRT duplicate propagation is active through a safe side table.
- Visual state: geometry is visible, but lighting/composition remains dark/incomplete.

## Next target

Port the complete auxiliary geometry shader fallback from shadPS4 commit
`7db6e4ba56b98841624ab776aaa56763f10bdc89`, adapted to this reconstructed runtime.

The public upstream implementation is a reference for architecture and behavior. The Bachata runtime source in this directory is reconstructed independently from the validated binary base.
