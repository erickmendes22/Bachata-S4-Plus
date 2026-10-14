# 0FCC8FD0: confirmed guest heap panic and retained-core regression

Device report 0FCC8FD0 identifies runtime n052, Bloodborne CUSA00900 01.09,
Adreno830, FEX025. User stop is false. Native log explicitly contains
DLRegularHeap.cpp(710), invalid/already-freed block, DL_PANIC and guest RIP
eboot.bin+0x20b56d2. This is the same panic location and guest register set as
n051's CD65FC3C. In this run FSR preference is disabled; SDK attachment fails
with -2 and there are no intercepted-device, temporal-dispatch, native scene
writer or GPU probe records. Log reduction did not cure the device panic.

The RIP is the deliberate termination after the heap checker has reported
failure; it does not by itself identify the invalid free or earlier write.
No invalid-block address or guest caller stack was captured. Do not patch out
DL_PANIC or attribute the failure to log count, FSR GPU dispatch, driver device
loss, low memory or FPS patch names on this evidence.

## Newly verified native-core regression

Compare exact pre-FSR R27 core025 SHA373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59
with the shipped n040..n052 core025 SHAc1cf8986c2a5f6f9f33d32a073eff797e2717b4848cd475c4d19f26dc7042bb2.
Contrary to earlier integration claims, the latter does not retain the R27
compatibility/RB changes. These native sites reverted to unpatched instructions:

| Site | R27 behavior missing in the FSR binary |
| --- | --- |
| 0x1262064 | map stage0x145 to0x45 |
| 0x11a16a4,0x11a19ac | HullShaderTransform unsupported-region guards |
| 0x114f84c | off-chip attributes use native ConstU32(0) |
| 0x11b1444 | Undef producer guard |
| 0x12933e0 | actual025 Presenter RB override |

The FSR constructor wrapper uses0x3e83e00, which is R27's stage-fix cave.
The FSR Presenter wrapper uses0x3e84000, which is R27's Undef-fix cave.
Consequently simply restoring the missing branches would jump into unrelated
FSR function wrappers. The old disconnected RB wrapper also reappeared.

The shipped constructor callback replaces the native constructor return with
the SDK attach result; the diagnostic's -2 is therefore forwarded to its caller.
The caller shown in disassembly subsequently overwritesx0, so this alone is NOT
proof of the reported heap panic. The shipped callbacks also still execute on
the disabled FSR path. Capture-free is not callback-free.

## Implemented correction, not released as a crash fix

repair_fsr_r27_hooks.py uses both SHA-pinned binaries. Restore the six native
sites and exact compatibility/connected-RB cave bytes from pre-FSR R27, remove
the disconnected wrapper, and move FSR attach/render/pipeline wrappers to
separate verified-zero RX padding0x3e86000/0x3e86400/0x3e86800. Native core025
is patched, never rebuilt. The discarded Scheduler hook remains absent.

Gate SDK lookup/callbacks on the launcher's exact FSR mode0..4. Disabled or
invalid modes follow original native constructor/render/pipeline execution.
Preserve native arguments, x8/x18, SIMD arguments, stack alignment and the
constructor return when SDK attach fails. SDK code, game executable, heap
checker, DEX, patches, dispatcher and legacy cores are not modified here.

Corrected native binary SHA8d62ee2d6abf57c0d667c814cf454ab7606c70a0f3519ac4ffc7e7ba10f17b34.
Every changed byte is checked against an explicit whitelist. No APK delivered.

## Executed validation

* 198 actual ARM64 wrapper cases, two PIE biases: modes absent/empty/-1/0..4/5/10/
  false; SDK absent/declined/active; exact native argument/SIMD/stack contracts,
  disabled callback exclusion and native constructor return preservation.
* Exact shipped constructor negative control reproduces callback return -2
  replacing the native result, at both PIE biases.
* 216 native compatibility cases execute restored stages, native ConstU32
  literal writer and Undef guard; original constant interning is modeled.
* 42 native stage/RB cases preserve GP/SIMD/flags under hostile getenv results.
  The exact shipped binary is the negative control rejecting stage325.
* Running the compatibility suite on the shipped FSR binary fails its restored
  stage contract, independently confirming the R27 regression.

These are meaningful native-hook regression tests; they do not run Bloodborne's
guest heap or establish that its panic has been eliminated. The available
eboot(20261014-150143).bin belongs to God of War III and must not be used to
locate Bloodborne01.09's allocator/panic instructions. Actual Bloodborne eboot
is needed to verify guest call sites and any bounded fault-only instrumentation.
The physical crash cannot be certified from synthetic Vulkan/ARM64 fixtures.
