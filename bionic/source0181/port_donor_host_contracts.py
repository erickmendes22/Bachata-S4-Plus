#!/usr/bin/env python3
"""ISS/TLOU donor runtime service contracts used by the linked libc."""
from pathlib import Path

RUSAGE=r'''#if defined(SHADPS4_ENABLE_FEX_GUEST_CPU) && defined(__linux__)
// ISS/TLOU runtime_kernel.c: FreeBSD guest rusage uses 64-bit timevals
// and fourteen 64-bit resource counters. No host struct leaks into guest ABI.
struct DonorRusage {
    OrbisKernelTimeval utime{}, stime{};
    s64 rest[14]{};
};
static_assert(sizeof(DonorRusage)==144);
static s32 PS4_SYSV_ABI donor_getrusage(s32 who, DonorRusage* out) {
    if (!out || (who!=0 && who!=1)) {
        SetPosixErrno(EINVAL);
        return -1;
    }
    struct rusage host{};
    if (::getrusage(who==0 ? RUSAGE_SELF : RUSAGE_THREAD,&host)!=0) {
        SetPosixErrno(errno);
        return -1;
    }
    *out={};
    out->utime={static_cast<s64>(host.ru_utime.tv_sec),static_cast<s64>(host.ru_utime.tv_usec)};
    out->stime={static_cast<s64>(host.ru_stime.tv_sec),static_cast<s64>(host.ru_stime.tv_usec)};
    return 0;
}
#endif

'''

def apply(root: Path):
    root=Path(root)/'src'
    def edit(rel,a,b):
        p=root/rel;s=p.read_text();assert s.count(a)==1,(rel,a[:100],s.count(a));p.write_text(s.replace(a,b,1))
    edit('core/libraries/kernel/time.cpp','void RegisterTime(Core::Loader::SymbolsResolver* sym) {',RUSAGE+'''void RegisterTime(Core::Loader::SymbolsResolver* sym) {
#if defined(SHADPS4_ENABLE_FEX_GUEST_CPU) && defined(__linux__)
    LIB_FUNCTION("hHlZQUnlxSM", "libkernel", 1, "libkernel", donor_getrusage);
    LIB_FUNCTION("hHlZQUnlxSM", "libScePosix", 1, "libkernel", donor_getrusage);
#endif''')
    edit('core/libraries/libc_internal/libc_internal_cxa.h','int PS4_SYSV_ABI fex_libc_cxa_atexit(', 'int PS4_SYSV_ABI fex_libc_atexit(void (*callback)());\nint PS4_SYSV_ABI fex_libc_cxa_atexit(')
    edit('core/libraries/libc_internal/libc_internal_cxa.cpp','    void* dso_handle;\n};','    void* dso_handle;\n    void (*plain)(){};\n};')
    edit('core/libraries/libc_internal/libc_internal_cxa.cpp','// BACHATA_SHARED_IO_CXA_FINALIZE:', '''// The donor stores atexit and __cxa_atexit in the same LIFO table.
int PS4_SYSV_ABI fex_libc_atexit(void (*callback)()) {
    if (!callback) return -1;
    std::lock_guard lock{AtexitMutex};
    AtexitEntries.push_back({nullptr,nullptr,nullptr,callback});
    return 0;
}

// BACHATA_SHARED_IO_CXA_FINALIZE:''')
    edit('core/libraries/libc_internal/libc_internal_cxa.cpp','        if (!found) return;\n#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU','''        if (!found) return;
        if (entry.plain) {
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
            static_cast<void>(Core::GuestCpu::RunGuestFunctionOrAbort(
                reinterpret_cast<const void*>(entry.plain), "atexit"));
#else
            entry.plain();
#endif
            continue;
        }
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU''')
