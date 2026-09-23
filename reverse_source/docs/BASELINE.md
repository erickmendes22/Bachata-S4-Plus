# Reverse-engineered baseline

## Known runtime identity

Target: x86-64 `bin/shadps4` executed through Box64 on ARM64 Android.

The reconstruction starts from the behavior of the validated runtime, not from any claim that a matching original source tree exists.

## Confirmed Order: 1886 patches

### V5 — shader-specific null image path
Status: `RE_CONFIRMED`

For `CUSA00785`, shaders:
- `0xa7b66f58`
- `0xefaaab2b`

must be allowed to route affected image descriptors through the runtime's existing null/empty image behavior.

Historical Box64 lookup used `Shader::Info::pgm_hash` at the then-current `+0xC48` layout. Source reconstruction must use the field, never hard-code the offset.

### V6 — shadow/user-data fix
Status: `RE_CONFIRMED`

For shader `0x9846aaff`:

```cpp
push_data.ud_regs[1] = 0x7F80000F;
```

The successful binary port proved `PushData::ud_regs` starts after the four float viewport fields and that the second user-data dword is the intended target.

### V8 — depth overlap handling
Status: `RE_CONFIRMED`

The known problematic overlap observed historically was color `R32_SFLOAT`, 2x MSAA -> depth `D32_SFLOAT`, 2x MSAA.

Depth-overlap work alone did not fix the final dark image, but the currently validated V8 behavior must be preserved.

### V11 — SRT duplicate ReadConst propagation
Status: `RE_CONFIRMED` behavior, reconstructed implementation

The visual correction activates only when the title guard is correct. A direct pointer chain stored manually in unused `IR::Inst::Arg(2)` reproduced the old visual change but could later dereference a stale pointer and crash at address `0x70`.

The current baseline therefore keeps the same logical propagation with an external side table rather than an intrusive pointer chain.

## Experiments not to repeat as image-fix candidates

- generic V12 depth-overlap generalization
- V15 DMA + precise readback
- V16 Flat -> Smooth substitution
- V17 depth-range clamp change

None produced the final visual correction.
