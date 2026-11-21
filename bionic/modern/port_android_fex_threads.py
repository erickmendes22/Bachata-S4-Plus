#!/usr/bin/env python3
"""Restore ARM64/FEX execution of PS4 guest pthread entrypoints and callbacks.

The pinned 0.21.1 transplant replaced the entire kernel pthread.cpp and
silently removed the existing Nyces FEX guest-dispatch branches. On Android
the remaining _runOnAnotherStack invokes an x86-64 guest RIP as a native
AArch64 function, so shader/graphics fixes cannot make gameplay boot.
Preserve the modern 0.21.1 thread state, cancellation, and signal handling.
"""
from pathlib import Path
import argparse


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one 0.21.1 anchor, found {count}")
    return source.replace(old, new, 1)


def integrate(root: Path) -> None:
    p = root / "src/core/libraries/kernel/threads/pthread.cpp"
    s = p.read_text()
    if "BIONIC_021_FEX_PTHREAD_GUEST_ENTRY" in s:
        raise RuntimeError("FEX pthread port already applied; refusing duplicate")

    s = replace_once(
        s,
        '#include "core/fex/fex_guest_engine.h"\n',
        '#include "core/fex/fex_guest_engine.h"\n'
        '#include "core/guest_cpu/guest_callback.h"\n',
        "guest callback include",
    )
    s = replace_once(
        s,
        "        old->routine(old->routine_arg);\n",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
        if (Core::GuestCpu::IsGuestFunctionAddress(
                reinterpret_cast<const void*>(old->routine))) {
            Core::GuestCpu::RunGuestFunctionOrAbort(
                reinterpret_cast<const void*>(old->routine), "pthread cleanup",
                old->routine_arg);
        } else {
            old->routine(old->routine_arg);
        }
#else
        old->routine(old->routine_arg);
#endif
""",
        "guest pthread cleanup",
    )
    s = replace_once(
        s,
        "    if (ThreadDtors) {\n        (ThreadDtors)();\n    }\n",
        """    if (ThreadDtors) {
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
        if (Core::GuestCpu::IsGuestFunctionAddress(reinterpret_cast<const void*>(ThreadDtors))) {
            Core::GuestCpu::RunGuestFunctionOrAbort(reinterpret_cast<const void*>(ThreadDtors),
                                                    "pthread thread dtors");
        } else {
            (ThreadDtors)();
        }
#else
        (ThreadDtors)();
#endif
    }
""",
        "guest pthread destructors",
    )
    s = replace_once(
        s,
        "    void* ret = _runOnAnotherStack(curthread->arg, (void*)curthread->start_routine, stack);\n",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BIONIC_021_FEX_PTHREAD_GUEST_ENTRY: guest x86-64 functions MUST execute in FEX,
    // never via native AArch64 _runOnAnotherStack or direct function calls.
    void* ret{};
    if (Core::GuestCpu::IsGuestFunctionAddress(
            reinterpret_cast<const void*>(curthread->start_routine))) {
        const std::array<u64, 1> args{reinterpret_cast<u64>(curthread->arg)};
        LOG_INFO(Kernel_Pthread, "BIONIC_021_FEX_PTHREAD_GUEST_ENTRY name={} rip={:#x}",
                 curthread->name, reinterpret_cast<u64>(curthread->start_routine));
        const auto guest_result = Core::GuestCpu::RunGuestFunctionOrAbort(
            reinterpret_cast<const void*>(curthread->start_routine), args,
            "pthread start", reinterpret_cast<VAddr>(stack));
        ret = reinterpret_cast<void*>(guest_result);
        LOG_INFO(Kernel_Pthread, "BIONIC_021_FEX_PTHREAD_GUEST_EXIT name={} result={:#x}",
                 curthread->name, guest_result);
    } else {
        LOG_INFO(Kernel_Pthread, "BIONIC_021_FEX_PTHREAD_HOST_ENTRY name={}", curthread->name);
        ret = curthread->start_routine(curthread->arg);
    }
#else
    void* ret = _runOnAnotherStack(curthread->arg, (void*)curthread->start_routine, stack);
#endif
""",
        "guest pthread start",
    )
    s = replace_once(
        s,
        "    g_curthread->cleanup.push_front(&cup);\n    init_routine();\n    g_curthread->cleanup.pop_front();",
        """    g_curthread->cleanup.push_front(&cup);
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BIONIC_021_FEX_PTHREAD_ONCE: guest C++/libc constructors run in FEX.
    if (Core::GuestCpu::IsGuestFunctionAddress(reinterpret_cast<const void*>(init_routine))) {
        Core::GuestCpu::RunGuestFunctionOrAbort(reinterpret_cast<const void*>(init_routine),
                                                "pthread once");
    } else {
        init_routine();
    }
#else
    init_routine();
#endif
    g_curthread->cleanup.pop_front();""",
        "guest pthread once",
    )
    p.write_text(s)
    print("BIONIC_021_FEX_PTHREAD_CALLBACKS_AND_ENTRY_RESTORED")

    # The 0.21.1 dynamic sysmodule preloader tracks early guest-libc demand,
    # but the FEX ENOSYS branch returns before the new flag code ever runs.
    linker = root / "src/core/linker.cpp"
    t = linker.read_text()
    t = replace_once(
        t,
        "    const auto aeronid = AeroLib::FindByNid(sr.name.c_str());\n",
        """    const auto aeronid = AeroLib::FindByNid(sr.name.c_str());
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BIONIC_021_FEX_PTHREAD_LLE_PRELOAD: the FEX unresolved-function early
    // return must not bypass new 0.21.1 guest libc/Fios2 preload bookkeeping.
    if (aeronid != nullptr && library->name == "libc" &&
        std::string_view{aeronid->name} == "Need_sceLibc") {
        Libraries::SysModule::g_need_scelibc = true;
        LOG_INFO(Core_Linker, "BIONIC_021_FEX_LIBC_PRELOAD_REQUESTED");
    }
    if (aeronid != nullptr && library->name == "libSceFios2" &&
        std::string_view{aeronid->name} == "sceFiosInitialize") {
        Libraries::SysModule::g_need_scelibc = true;
        LOG_INFO(Core_Linker, "BIONIC_021_FEX_FIOS2_LIBC_PRELOAD_REQUESTED");
    }
#endif
""",
        "FEX 0.21.1 libc preload",
    )
    linker.write_text(t)
    print("BIONIC_021_FEX_LIBC_PRELOAD_PATH_RESTORED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    integrate(parser.parse_args().source)
