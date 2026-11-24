"""SM8650 boot failures and verified redundant SRT work.

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

    pc="src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    edit(root,pc,"#include <ranges>","#include <ranges>\n#include <cstring>")
    edit(root,pc,"    const auto start_binding = binding;",
         """    const auto start_binding = binding;
    // BACHATA_SRT_LOOKUP_REUSE: candidate layouts can be different;
    // do not use the first program's resource metadata for every variant.
    // Only the just-refreshed flattened values of an identical SRT program
    // are reusable within this single GetProgram invocation.
    const Shader::Info* previous_srt=nullptr;
    const bool reuse_srt=!BachataCompat::Sotc608() && params.user_data.size()==16;""")
    edit(root,pc,'''        effective.RefreshFlatBuf();
        if (srt_sync) srt_sync(effective);''',
         '''        const auto& code=effective.srt_info;
        bool same=false;
        if (reuse_srt && previous_srt && effective.sharp_tables.empty() &&
            previous_srt->sharp_tables.empty()) {
            const auto& previous=previous_srt->srt_info;
            same=code.flattened_bufsize_dw==previous.flattened_bufsize_dw &&
                code.walker_func_size==previous.walker_func_size &&
                ((code.walker_func==previous.walker_func) ||
                 (code.walker_func && previous.walker_func && code.walker_func_size &&
                  std::memcmp(code.walker_func,previous.walker_func,code.walker_func_size)==0));
        }
        if (same) {
            effective.flattened_ud_buf=previous_srt->flattened_ud_buf;
            effective.srt_guest_sources=previous_srt->srt_guest_sources;
        } else {
            effective.RefreshFlatBuf();
            if (srt_sync) srt_sync(effective);
        }
        previous_srt=&effective;''')
    # CompileModule previously created/stat'ed a patch directory for
    # every permutation even with shader patching switched off.
    edit(root,pc,'    auto patch = GetShaderPatch(info.pgm_hash, info.hw_stage, perm_idx, "spv");',
         """    std::optional<std::vector<u32>> patch;
    if (BachataCompat::Sotc608() || EmulatorSettings.IsPatchShaders() ||
        EmulatorSettings.IsShaderCollect())
        patch=GetShaderPatch(info.pgm_hash,info.hw_stage,perm_idx,"spv");""")
    return {"pthread":"opaque 64-bit start argument, preserve native create and Orbis error",
            "srt":"single lookup reuse of byte-identical layouts, preserve candidate-specific descriptors",
            "fios":"CUSA05170 selects existing guest FIOS2 before archive HLE"}
