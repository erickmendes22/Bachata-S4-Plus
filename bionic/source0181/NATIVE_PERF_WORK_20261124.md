# Isolated native performance work
Base 5c28eed, main APK 45495287078 continues independently.
- Checked ARM64 SRT JIT: donor arithmetic emitter, existing SRT1 bytecode, checked physical memory callbacks, exact dependency addresses, grouped copies, W^X pages and interpreter fallback. No SotC JIT.
- Physical upload: two CPU lanes under one VMM read lock, validate all spans first, workers use only memfd backing, join before staging flush. This is not deferred submission: the guest snapshot is not allowed to outlive the VMM lock. Donor full deferred uploads require separate hazard/ownership and scheduler changes.
- CI tests host emitter, native ARM64 machine code under qemu and worker copies. No FPS or Android device result claimed.
