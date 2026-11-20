// SPDX-License-Identifier: GPL-2.0-or-later
// Android/Bionic FEX fallback for PS4 libc imports not implemented by the
// pinned generic shadPS4 build. These are guest ABI entry points, NOT Bionic
// libc exports, and must be registered through the existing HLE bridge.
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include "core/libraries/libs.h"
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
#include "core/guest_cpu/hle_call_adapter.h"

namespace Libraries::LibcInternal {
namespace {
// The guest CRT initializes environment and its shutdown registry before the
// game has a frame. No host process environment should be replaced here.
int PS4_SYSV_ABI FexInitEnv(void*, void*) { return 0; }

// The core already defers __cxa_atexit guest destruction to guest termination.
// Likewise do not execute guest atexit functions in the Android host process.
int PS4_SYSV_ABI FexAtexit(void (*callback)()) { return callback ? 0 : -1; }

// CRT iostream constructors run in many game and PRX static initializers.
// Avoid returning -ENOSYS as a function pointer or object state. This is a
// limited boot-compatibility shim, not a full emulation of the PS4 iostream CRT.
void PS4_SYSV_ABI FexIostreamInit(void*) {}

// Do not call host C++ operator new on a guest ABI allocation path: it can
// throw across the FEX bridge. Use a stable pointer-returning C allocator,
// publish its range for typed HLE validation, and pair all known new/delete
// variants to avoid allocator mixing. A null result remains a real OOM.
void* PS4_SYSV_ABI FexOperatorNew(std::size_t size) {
    const auto bytes = size ? size : 1;
    void* pointer = std::malloc(bytes);
    if (pointer) {
        (void)Core::GuestCpu::PublishHostRange(pointer, bytes, true);
    }
    return pointer;
}

void PS4_SYSV_ABI FexOperatorDelete(void* pointer) {
    if (!pointer) return;
    (void)Core::GuestCpu::RevokeHostRange(pointer);
    std::free(pointer);
}

void* PS4_SYSV_ABI FexMemmove(void* destination, const void* source, std::size_t length) {
    return std::memmove(destination, source, length);
}
} // namespace

void RegisterFexLibcBootAliases(Core::Loader::SymbolsResolver* sym) {
    // NIDs are imported from libc#libc by The Order (CUSA00785 1.02).
    // Explicit ABI registration avoids the generic FEX -ENOSYS veneer.
    LIB_FUNCTION("bzQExy189ZI", "libc", 1, "libc", FexInitEnv);
    LIB_FUNCTION("8G2LB+A3rzg", "libc", 1, "libc", FexAtexit);
    LIB_FUNCTION("sqWytnhYdEg", "libc", 1, "libc", FexIostreamInit);
    LIB_FUNCTION("-Bl9-SZ2noc", "libc", 1, "libc", FexIostreamInit);
    LIB_FUNCTION("+P6FRGH4LfA", "libc", 1, "libc", FexMemmove);
    LIB_FUNCTION("fJnpuVVBbKk", "libc", 1, "libc", FexOperatorNew);
    LIB_FUNCTION("hdm0YfMa7TQ", "libc", 1, "libc", FexOperatorNew);
    LIB_FUNCTION("z+P+xCnWLBk", "libc", 1, "libc", FexOperatorDelete);
    LIB_FUNCTION("MLWl90SFWNE", "libc", 1, "libc", FexOperatorDelete);
}
} // namespace Libraries::LibcInternal
#endif
