# Release 0.2.6 — integrated shared-core parity build

This build includes all of the following **core-wide** fixes, not individual CUSA patches:

- GPU graphics DCB/CCB ownership by suspended command coroutines, per Release 0.2.6.
- Independent Constant Engine submission FIFO, proper CE/DE counters and cross-coroutine PM4 lifetime.
- Snapshot PM4 packet lengths before guest buffer reuse, handle type-2 CE packets, distinguish chained indirect graphics buffers, release nested command coroutines.
- Genuine FEX x86 guest callbacks for libc `qsort`, with guest range checks, avoiding native Android comparator ABI.
- Dinkumware `_Log(double,int)` HLE, preserving SysV FP argument / return ABI.
- Fail-closed source version assertions and CI preflight requirements for these GPU and HLE paths.

Source integration preflight passed at GitHub Actions `45189937010`; this commit deliberately triggers full Android cross-compilation and P36 APK packaging. A successful compilation is not proof of game compatibility. Unresolved SRT `ReadLane`/`Phi`, CMask, Vulkan memory and SAF parity require functional equivalence work; do not claim them fixed without evidence.
