# Shadow of the Colossus — R35 graphics investigation (NOT A RELEASE)

The only compiled result at this stage is a **SHA-pinned experimental ELF** derived from the R34 that the user confirmed boots. No APK has been created from this branch.

## Proven limitation of R34

Its existing scalar TSharp LOD mark hook at `0x12DFD5C` does not cover texture-array elements. The special texture-array path enters at `0x12E41D4`, and after verifying bindability reaches `0x12E4798`. In the SotC PC port, both scalar TSharps and each bindable array element call `SotcLod::Mark(counter_bank_id)` if `lod_hw_cnt_en` is set.

`r35_array_lod.S` adds this missing path using the existing CUSA08809 gate and bank array, without touching FPS, audio, resolutions, SRT, or GPU-unmap code. It replays the displaced `ldr x12,[sp,#0x68]`.

## Binary/static validation

Base R34 ELF SHA-256: `2b76f3d27f3471b2159151c25afc5f42cd541b9537c26b62583f192972f4b290`

Experimental ELF SHA-256: `4498dd84c2b781f3a7637280013c55f90c8d68a7260c8d7f7ebe61f1b1edb8c0`

- 94 changed bytes, restricted to original branch at `0x12E4798` and code cave `0x435FD50..0x435FDB0`.
- Static checks pass: original instruction replay, CUSA gate, BSS bank address, AArch64 branch and ADRP targets, 256 counter-bank IDs and all memory/ELF boundaries.
- SNDX payload, scalar LOD handler, and GPU-unmap handler are **byte-for-byte identical** to R34.
- This does **not** prove the graphics are corrected on a real device.

## Unresolved and blocking

R34 diagnostic `BS4-20261019-A8727C7B` contains 16 compiler errors (8 `SelectF32/IEqual32` and 8 `CompositeExtractU32x2/IAddCarry32`). Actual optimized ARM64 code logs `flatten_extended_userdata_pass.cpp:1113`, whereas the public Zenith source pinned in our clean-build workflows has only 662 lines and a different implementation. Do not blindly transplant incompatible function bytes or mask the warnings. The full original optimized compiler source or a precisely verified binary ABI port is required.

The public source's `BufferCache::ReadMemory` uses synchronous `SendCommand<true>` and `Scheduler::Finish`, so porting the PC fork's `MarkInflightReadbacksDirty` without confirming matching async machinery is not justified.

**Do not publish an APK as a functional R35 based only on these static tests.**
