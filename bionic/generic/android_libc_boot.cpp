// SPDX-License-Identifier: GPL-2.0-or-later
// FEX HLE for PS4 libc imports whose LLE provider was not loaded.
// Unlike host malloc, the heap is backed by guest VMM flexible mappings so
// guest x86 code can dereference returned addresses.
#include <algorithm>
#include <bit>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <limits>
#include <mutex>
#include <string>
#include <vector>

#include "core/libraries/libs.h"
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
#include "common/va_ctx.h"
#include "core/guest_cpu/hle_call_adapter.h"
#include "core/libraries/libc_internal/mspace.h"
#include "core/libraries/libc_internal/printf.h"
#include "core/memory.h"

namespace Libraries::LibcInternal {
namespace {
constexpr std::size_t GuestPageSize = 0x4000;
constexpr std::size_t GuestArenaSize = 8 * 1024 * 1024;
struct GuestArena {
    void* base{};
    std::size_t capacity{};
    void* handle{};
};
std::mutex guest_heap_mutex;
std::vector<GuestArena> guest_arenas;

bool IsGuestMapped(const void* pointer, std::size_t count, bool writable) {
    if (count == 0) return true;
    if (!pointer) return false;
    const auto address = reinterpret_cast<std::uintptr_t>(pointer);
    if (address > std::numeric_limits<std::uintptr_t>::max() - count) return false;
    auto* memory = Core::Memory::Instance();
    void *begin{}, *end{};
    u32 prot{};
    if (memory->QueryProtection(address, &begin, &end, &prot) != 0 ||
        address < reinterpret_cast<std::uintptr_t>(begin) ||
        count > reinterpret_cast<std::uintptr_t>(end) - address) return false;
    const u32 mask = static_cast<u32>(writable ? Core::MemoryProt::CpuWrite :
                                              Core::MemoryProt::CpuRead);
    return (prot & mask) != 0;
}

GuestArena* FindOwnedArena(void* pointer) {
    const auto address = reinterpret_cast<std::uintptr_t>(pointer);
    for (auto& arena : guest_arenas) {
        const auto first = reinterpret_cast<std::uintptr_t>(arena.base);
        if (address >= first && address - first < arena.capacity) return &arena;
    }
    return nullptr;
}

// Call with guest_heap_mutex held. All arenas are mapped through the PS4 VMM;
// the Mspace allocator owns the suballocations and handles concurrency.
void* GuestAllocateLocked(std::size_t bytes, std::size_t alignment = 16) {
    if (!alignment || !std::has_single_bit(alignment) ||
        bytes > std::numeric_limits<std::size_t>::max() - alignment - GuestPageSize) {
        return nullptr;
    }
    bytes = std::max<std::size_t>(bytes, 1);
    for (auto& arena : guest_arenas) {
        void* result = MspaceMemalign(arena.handle, alignment, bytes);
        if (result) return result;
    }
    const std::size_t needed = bytes + alignment;
    const std::size_t wanted = std::max(GuestArenaSize, needed);
    const std::size_t cap = (wanted + GuestPageSize - 1) & ~(GuestPageSize - 1);
    auto* memory = Core::Memory::Instance();
    if (cap > memory->GetAvailableFlexibleSize()) return nullptr;
    void* base = nullptr;
    if (memory->MapMemory(&base, 0, cap, Core::MemoryProt::CpuReadWrite,
                          Core::MemoryMapFlags::NoFlags, Core::VMAType::Flexible,
                          "BachataFexLibc") != 0) return nullptr;
    void* handle = MspaceCreate("BachataFexLibc", base, cap, 0);
    if (!handle) {
        (void)memory->UnmapMemory(reinterpret_cast<std::uintptr_t>(base), cap);
        return nullptr;
    }
    guest_arenas.push_back({base, cap, handle});
    return MspaceMemalign(handle, alignment, bytes);
}

void* PS4_SYSV_ABI GuestMalloc(std::size_t size) {
    std::lock_guard lock{guest_heap_mutex};
    return GuestAllocateLocked(size);
}

void PS4_SYSV_ABI GuestFree(void* pointer) {
    if (!pointer) return;
    std::lock_guard lock{guest_heap_mutex};
    if (auto* arena = FindOwnedArena(pointer)) {
        (void)MspaceFree(arena->handle, pointer);
    }
}

void* PS4_SYSV_ABI GuestCalloc(std::size_t count, std::size_t size) {
    if (count != 0 && size > std::numeric_limits<std::size_t>::max() / count) return nullptr;
    const auto bytes = count * size;
    std::lock_guard lock{guest_heap_mutex};
    void* p = GuestAllocateLocked(bytes);
    if (p && bytes) std::memset(p, 0, bytes);
    return p;
}

void* PS4_SYSV_ABI GuestRealloc(void* pointer, std::size_t size) {
    std::lock_guard lock{guest_heap_mutex};
    if (!pointer) return GuestAllocateLocked(size);
    auto* arena = FindOwnedArena(pointer);
    if (!arena) return nullptr;
    if (!size) {
        (void)MspaceFree(arena->handle, pointer);
        return nullptr;
    }
    const std::size_t old_size = MspaceMallocUsableSize(pointer);
    if (!old_size) return nullptr;
    if (void* p = MspaceRealloc(arena->handle, pointer, size)) return p;
    void* replacement = GuestAllocateLocked(size);
    if (replacement) {
        std::memcpy(replacement, pointer, std::min(old_size, size));
        (void)MspaceFree(arena->handle, pointer);
    }
    return replacement;
}

void* PS4_SYSV_ABI GuestMemalign(std::size_t alignment, std::size_t size) {
    std::lock_guard lock{guest_heap_mutex};
    return GuestAllocateLocked(size, alignment);
}

int PS4_SYSV_ABI GuestPosixMemalign(void** out, std::size_t alignment, std::size_t size) {
    if (!out || !IsGuestMapped(out, sizeof(*out), true)) return EFAULT;
    if (alignment < sizeof(void*) || !std::has_single_bit(alignment)) return EINVAL;
    void* result = GuestMemalign(alignment, size);
    if (!result) return ENOMEM;
    *out = result;
    return 0;
}

std::size_t PS4_SYSV_ABI GuestMallocUsableSize(void* pointer) {
    if (!pointer) return 0;
    std::lock_guard lock{guest_heap_mutex};
    return FindOwnedArena(pointer) ? MspaceMallocUsableSize(pointer) : 0;
}

int PS4_SYSV_ABI FexInitEnv(void*, void*) { return 0; }
int PS4_SYSV_ABI FexAtexit(void (*callback)()) { return callback ? 0 : -1; }
void PS4_SYSV_ABI FexIostreamInit(void*) {}
void* PS4_SYSV_ABI FexOperatorNew(std::size_t size) { return GuestMalloc(size); }
void PS4_SYSV_ABI FexOperatorDelete(void* pointer) { GuestFree(pointer); }
void* PS4_SYSV_ABI FexMemmove(void* destination, const void* source, std::size_t length) {
    return std::memmove(destination, source, length);
}

// The x86-64 PS4 va_list is a 24-byte SysV structure. Passing it directly to
// Bionic vsnprintf would interpret an ARM64 va_list instead. Reuse shadPS4's
// guest va_arg formatter, with a bounded output sink rather than the existing
// vsnprintf_ctx (which copies without respecting n).
struct FormatOutput {
    char* dst{};
    std::size_t capacity{};
};
void BoundedFormatOutput(char c, void* opaque, std::size_t index, std::size_t) {
    auto* buf = reinterpret_cast<FormatOutput*>(opaque);
    if (index < buf->capacity) buf->dst[index] = c;
    else if (c == '\0' && buf->capacity) buf->dst[buf->capacity - 1] = '\0';
}

int PS4_SYSV_ABI GuestVsnprintf(char* dest, std::size_t capacity,
                                const char* format, Common::VaList* args) {
    constexpr std::size_t MaxFormatLength = 4096;
    constexpr std::size_t MaxOutputSize = 1024 * 1024;
    if (!args || !IsGuestMapped(args, sizeof(*args), false) || !format) return -1;
    if (capacity > MaxOutputSize) return -1;  // Avoid excessive guest writes.
    if (capacity && !IsGuestMapped(dest, capacity, true)) return -1;
    // Read format through the guest mapping checker, including its terminator.
    std::string safe_format;
    bool terminated = false;
    for (std::size_t i = 0; i < MaxFormatLength; ++i) {
        if (!IsGuestMapped(format + i, 1, false)) return -1;
        if (format[i] == '\0') { terminated = true; break; }
        safe_format.push_back(format[i]);
    }
    if (!terminated) return -1;
    Common::VaList ap = *args;
    if (ap.gp_offset > 48 || ap.fp_offset > 176 ||
        !IsGuestMapped(ap.reg_save_area, 176, false)) return -1;
    if (ap.overflow_arg_area && !IsGuestMapped(ap.overflow_arg_area, sizeof(u64), false))
        return -1;
    FormatOutput out{dest, capacity};
    return _vsnprintf(BoundedFormatOutput, reinterpret_cast<char*>(&out),
                      safe_format.c_str(), &ap);
}
// PS4 libSceLibcInternal memset writes only validated guest VMM memory.
void* PS4_SYSV_ABI GuestInternalMemset(void* dst, int value, std::size_t length) {
    if (length != 0 && !IsGuestMapped(dst, length, true)) return nullptr;
    return std::memset(dst, value, length);
}

// Validate both sides of guest memory copies, never dereference raw host pointers.
void* PS4_SYSV_ABI GuestInternalMemcpy(void* dst, const void* source, std::size_t bytes) {
    if (bytes && (!IsGuestMapped(dst, bytes, true) ||
                  !IsGuestMapped(source, bytes, false))) return nullptr;
    return std::memcpy(dst, source, bytes);
}
int PS4_SYSV_ABI GuestInternalMemcmp(const void* a, const void* b, std::size_t bytes) {
    if (bytes && (!IsGuestMapped(a, bytes, false) ||
                  !IsGuestMapped(b, bytes, false))) return 0;
    return std::memcmp(a, b, bytes);
}
// GMpvxPFW924 is vprintf: its va_list is 24-byte x86-64 SysV, not AArch64.
int PS4_SYSV_ABI GuestInternalVprintf(const char* format, Common::VaList* ap) {
    constexpr std::size_t MaxPrint = 65536;
    char* const out = static_cast<char*>(GuestCalloc(1, MaxPrint));
    if (!out) return -1;
    const int count = GuestVsnprintf(out, MaxPrint, format, ap);
    if (count > 0) {
        const std::size_t n = std::min<std::size_t>(count, MaxPrint - 1);
        (void)std::fwrite(out, 1, n, stdout);
    }
    GuestFree(out);
    return count;
}
// BACHATA_SOTC_SHAREUTILITY_HLE_FROM_PORT: CUSA08809 imports
// sceShareUtilityInitializeEx2 via libSceShareUtility. The working
// SotC native port's handler accepts four 64-bit guest arguments and
// returns success; retaining ENOSYS causes the game to skip setup.
s32 PS4_SYSV_ABI GuestSotcShareUtilityInitializeEx2(u64 a, u64 b, u64 c, u64 d) {
    static_cast<void>(a);
    static_cast<void>(b);
    static_cast<void>(c);
    static_cast<void>(d);
    return 0;
}
} // namespace

void* FexLibcGuestAllocate(std::size_t bytes) { return GuestCalloc(1, bytes); }
void FexLibcGuestFree(void* pointer) { GuestFree(pointer); }
void RegisterFexLibcCompatAliases(Core::Loader::SymbolsResolver* sym);
void RegisterFexLibcGuestObjects(Core::Loader::SymbolsResolver* sym);

void RegisterFexLibcBootAliases(Core::Loader::SymbolsResolver* sym) {
    // Pure HLE registration: never map guest VMM pages from this call.
    RegisterFexLibcCompatAliases(sym);
    // From ShadowOfTheColossus-Android-Aot/src/runtime_sotc.c:
    // sceShareUtilityInitializeEx2 is a successful no-op for this title.
    // Real import identity from uploaded CUSA08809 log, not guessed NID.
    LIB_FUNCTION("j7DlalBzHh8", "libSceShareUtility", 1,
                 "libSceShareUtility", GuestSotcShareUtilityInitializeEx2);
    // BACHATA_RELEASE026_LIBCINTERNAL_REAL_NIDS: these imports arrive through
    // libSceLibcInternal, not through the previously registered libc aliases.
    LIB_FUNCTION("8zTFvBIAIN8", "libSceLibcInternal", 1,
                 "libSceLibcInternal", GuestInternalMemset);
    LIB_FUNCTION("GMpvxPFW924", "libSceLibcInternal", 1,
                 "libSceLibcInternal", GuestInternalVprintf);
    // BACHATA_FEX_LIBCINTERNAL_IMPORTS_READY: real CUSA08809 imports from
    // libSceLibcInternal, not the similarly named libc namespace.
#define INTERNAL_ALIAS(nid, fn) LIB_FUNCTION(nid, "libSceLibcInternal", 1, "libSceLibcInternal", fn)
    INTERNAL_ALIAS("gQX+4GDQjpM", GuestMalloc);
    INTERNAL_ALIAS("tIhsqj0qsFE", GuestFree);
    INTERNAL_ALIAS("Y7aJ1uydPMo", GuestRealloc);
    INTERNAL_ALIAS("2X5agFjKxMc", GuestCalloc);
    INTERNAL_ALIAS("Ujf3KzMvRmI", GuestMemalign);
    INTERNAL_ALIAS("cVSk9y8URbc", GuestPosixMemalign);
    INTERNAL_ALIAS("NDcSfcYZRC8", GuestMallocUsableSize);
    INTERNAL_ALIAS("Q2V+iqvjgC0", GuestVsnprintf);
    INTERNAL_ALIAS("Q3VBxCXhUHs", GuestInternalMemcpy);
    INTERNAL_ALIAS("DfivPArhucg", GuestInternalMemcmp);
    INTERNAL_ALIAS("+P6FRGH4LfA", FexMemmove);
    INTERNAL_ALIAS("fJnpuVVBbKk", FexOperatorNew);
    INTERNAL_ALIAS("hdm0YfMa7TQ", FexOperatorNew);
    INTERNAL_ALIAS("lYDzBVE5mZs", FexOperatorDelete);
    INTERNAL_ALIAS("FOt55ZNaVJk", FexOperatorDelete);
#undef INTERNAL_ALIAS
    LIB_FUNCTION("gQX+4GDQjpM", "libc", 1, "libc", GuestMalloc);
    LIB_FUNCTION("tIhsqj0qsFE", "libc", 1, "libc", GuestFree);
    LIB_FUNCTION("Y7aJ1uydPMo", "libc", 1, "libc", GuestRealloc);
    LIB_FUNCTION("2X5agFjKxMc", "libc", 1, "libc", GuestCalloc);
    LIB_FUNCTION("Ujf3KzMvRmI", "libc", 1, "libc", GuestMemalign);
    LIB_FUNCTION("cVSk9y8URbc", "libc", 1, "libc", GuestPosixMemalign);
    LIB_FUNCTION("NDcSfcYZRC8", "libc", 1, "libc", GuestMallocUsableSize);
    LIB_FUNCTION("Q2V+iqvjgC0", "libc", 1, "libc", GuestVsnprintf);
    LIB_FUNCTION("bzQExy189ZI", "libc", 1, "libc", FexInitEnv);
    LIB_FUNCTION("8G2LB+A3rzg", "libc", 1, "libc", FexAtexit);
    LIB_FUNCTION("sqWytnhYdEg", "libc", 1, "libc", FexIostreamInit);
    LIB_FUNCTION("-Bl9-SZ2noc", "libc", 1, "libc", FexIostreamInit);
    LIB_FUNCTION("+P6FRGH4LfA", "libc", 1, "libc", FexMemmove);
    LIB_FUNCTION("fJnpuVVBbKk", "libc", 1, "libc", FexOperatorNew);
    LIB_FUNCTION("hdm0YfMa7TQ", "libc", 1, "libc", FexOperatorNew);
    LIB_FUNCTION("ryUxD-60bKM", "libc", 1, "libc", FexOperatorNew);
    LIB_FUNCTION("Jh5qUcwiSEk", "libc", 1, "libc", FexOperatorNew);
    LIB_FUNCTION("lYDzBVE5mZs", "libc", 1, "libc", FexOperatorDelete);
    LIB_FUNCTION("FOt55ZNaVJk", "libc", 1, "libc", FexOperatorDelete);
    LIB_FUNCTION("z+P+xCnWLBk", "libc", 1, "libc", FexOperatorDelete);
    LIB_FUNCTION("MLWl90SFWNE", "libc", 1, "libc", FexOperatorDelete);
}
} // namespace Libraries::LibcInternal
#endif
