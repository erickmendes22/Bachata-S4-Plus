"""SM8650 boot ABI fix isolated from renderer changes.

Do not treat a pthread start argument as a dereferenceable pointer.
Keep the native pthread implementation and Orbis errno translation.
Reuse only byte-identical SRT programs inside a single lookup, and only
when the whole register prefix is present and no dynamic T# table exists.
Never reuse a previous draw's mutable guest resource table.
"""
from pathlib import Path

def edit(root, rel, old, new):
    p=root/rel
    s=p.read_text()
    if s.count(old)!=1:
        raise RuntimeError(f"Gen3/SRT source drift {rel}: {old[:120]}")
    p.write_text(s.replace(old,new,1))

def apply(root: Path):
    pt="src/core/libraries/kernel/threads/pthread.cpp"
    anchor="int PS4_SYSV_ABI posix_pthread_getthreadid_np() {"
    edit(root,pt,anchor,r'''// BACHATA_PTHREAD_OPAQUE_ARGUMENT: POSIX start_routine's argument is
// an opaque machine word, not an address that pthread_create dereferences.
// Passing a small integer through (void*) is valid; the FEX typed pointer
// decoder otherwise rejects 1..4095 with EFAULT before native creation.
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
int PS4_SYSV_ABI fex_pthread_create_name_np(PthreadT* thread, const PthreadAttrT* attr,
                                          PthreadEntryFunc entry, u64 arg, const char* name) {
    return posix_pthread_create_name_np(thread, attr, entry,
        reinterpret_cast<void*>(static_cast<uintptr_t>(arg)), name);
}
int PS4_SYSV_ABI fex_pthread_create(PthreadT* thread, const PthreadAttrT* attr,
                                  PthreadEntryFunc entry, u64 arg) {
    return fex_pthread_create_name_np(thread, attr, entry, arg, nullptr);
}
#endif

'''+anchor)
    for nid,lib,name in (
        ("OxhIB8LB-PQ","libScePosix","posix_pthread_create"),
        ("Jmi+9w9u0E4","libScePosix","posix_pthread_create_name_np"),
        ("OxhIB8LB-PQ","libkernel","posix_pthread_create"),
        ("Jmi+9w9u0E4","libkernel","posix_pthread_create_name_np"),
        ("6UgtwV+0zb4","libkernel","ORBIS(posix_pthread_create_name_np)"),
    ):
        old=f'    LIB_FUNCTION("{nid}", "{lib}", 1, "libkernel", {name});'
        if name.startswith("ORBIS"):
            new="ORBIS(fex_pthread_create_name_np)"
        elif name.endswith("_name_np"):
            new="fex_pthread_create_name_np"
        else:
            new="fex_pthread_create"
        edit(root,pt,old,
             '#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n'+old.replace(", "+name+");",", "+new+");")+
             '\n#else\n'+old+'\n#endif')
    # Decode failures are rare; record argument positions only on a failure.
    # Never turn other malformed pointers into success, or enable per-call tracing.
    ad="src/core/guest_cpu/hle_call_adapter.h"
    edit(root,ad,"#include <cstring>","#include <cstring>\n#include <cstdio>")
    edit(root,ad,'''            if (!AllDecoded(decoded, std::index_sequence_for<Args...>{})) {
                return HleCallFailure{EFAULT, Name()};
            }''',r'''            if (!AllDecoded(decoded, std::index_sequence_for<Args...>{})) {
                size_t index=0;
                const auto report=[&](const auto& arg) {
                    if (!arg.has_value())
                        std::fprintf(stderr,"BACHATA_HLE_ARG_REJECT name=%.*s index=%zu\n",
                                     int(Name().size()),Name().data(),index);
                    ++index;
                };
                std::apply([&](const auto&... arg) { (report(arg), ...); },decoded);
                return HleCallFailure{EFAULT, Name()};
            }''')

    return {"pthread":"opaque start argument and failure-only ABI evidence"}
