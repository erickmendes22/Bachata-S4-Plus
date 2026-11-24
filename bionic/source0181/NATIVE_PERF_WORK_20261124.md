# Isolated native performance work
Base 5c28eed, main APK 45495287078 continues independently.
- Checked ARM64 SRT JIT: donor arithmetic emitter, existing SRT1 bytecode, checked physical memory callbacks, exact dependency addresses, grouped copies, W^X pages and interpreter fallback. No SotC JIT.
- Physical upload: two CPU lanes under one VMM read lock, validate all spans first, workers use only memfd backing, join before staging flush. This is not deferred submission: the guest snapshot is not allowed to outlive the VMM lock. Donor full deferred uploads require separate hazard/ownership and scheduler changes.
- CI tests host emitter, native ARM64 machine code under qemu and worker copies. No FPS or Android device result claimed.

- AHB/SurfaceControl in-process transport: three imported RGBA8 AHBs, SYNC_FD acquire/release, foreign queue family barriers, no socket. Experimental opt-in; falls back to WSI on unsupported format, HDR, init/import/export/release failure. Retains full-size existing ImGui composition. Needs Android runtime test before default enablement.

- Intern SRT bytecode by exact length and bytes, cap generated RX mappings at 32 MiB and use interpreter if budget exhausted. Avoid duplicate code for permutations/archive metadata.
- Vertex specialization: only ignore unused instance step rates (translator reads rate 0 iff num_input_vgprs>0 and rate 1 iff >1); retain actual fetch attribute divisors, runtime fields, descriptor contracts and strict cache equality. This eliminates a provably redundant key dimension but does not establish that it is the cause of every observed Order recompilation.
