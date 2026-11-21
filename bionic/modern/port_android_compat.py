#!/usr/bin/env python3
"""Bionic-only adaptations for the modern 0.21.1 PS4 kernel.

Do not import outdated 0.16.x HLE, guest libc, SAF or GPU implementations.
Refuse source drift rather than silently dropping guest-visible behavior.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    data = path.read_text()
    count = data.count(old)
    if count != 1:
        if path.name == "exception.cpp":
            for needle in ("sigisemptyset", "native_thr.GetHandle()", "sigismember"):
                at = data.find(needle)
                if at >= 0:
                    print(f"BIONIC_021_SIGNAL_SOURCE {needle}: {data[max(0,at-160):at+310]}")
        if path.name == "time.cpp":
            function_at = data.find("sceKernelConvertUtcToLocaltime")
            if function_at >= 0:
                print("BIONIC_021_TIME_ACTUAL_SOURCE_BEGIN")
                print(data[function_at:function_at + 2400])
                print("BIONIC_021_TIME_ACTUAL_SOURCE_END")
        raise RuntimeError(f"{path}: expected one exact 0.21.1 anchor, found {count}")
    path.write_text(data.replace(old, new, 1))


def integrate(source: Path) -> None:
    time = source / "src/core/libraries/kernel/time.cpp"
    zone = time.read_text()
    # The applied 0.21.1 ARM64 port already replaced std::chrono::current_zone
    # with localtime_r + tm_gmtoff. Replacing it again would regress behavior.
    if "std::chrono::current_zone()" in zone:
        raise RuntimeError("0.21.1 timezone still depends on unsupported NDK chrono tzdb")
    if "localtime_r(&t, &tm_val)" not in zone or "tm_val.tm_gmtoff" not in zone:
        raise RuntimeError("0.21.1 timezone implementation needs manual Bionic review")
    print("BIONIC_021_TIME_ALREADY_COMPATIBLE")

    exception = source / "src/core/libraries/kernel/threads/exception.cpp"
    replace_once(
        exception,
        """        if (!sigisemptyset(&native_oact.sa_mask)) {
            LOG_ERROR(Lib_Kernel, "Unhandled sa_mask");
        }""",
        """#if defined(__ANDROID__)
        // BIONIC_021_NATIVE_SIGNAL_MASK: sigisemptyset is a glibc extension.
        bool masked = false;
        for (int s = 1; s <= SIGRTMAX; ++s) {
            if (sigismember(&native_oact.sa_mask, s) == 1) {
                masked = true;
                break;
            }
        }
        if (masked) {
            LOG_ERROR(Lib_Kernel, "Unhandled sa_mask");
        }
#else
        if (!sigisemptyset(&native_oact.sa_mask)) {
            LOG_ERROR(Lib_Kernel, "Unhandled sa_mask");
        }
#endif""",
    )
    replace_once(
        exception,
        "    const auto pthr = reinterpret_cast<pthread_t>(thread->native_thr.GetHandle());\n",
        """#if defined(__ANDROID__)
    // BIONIC_021_NATIVE_PTHREAD_HANDLE: Android pthread_t is integer-valued.
    const auto pthr = static_cast<pthread_t>(thread->native_thr.GetHandle());
#else
    const auto pthr = reinterpret_cast<pthread_t>(thread->native_thr.GetHandle());
#endif
""",
    )
    print("BIONIC_021_KERNEL_POSIX_ADAPTATIONS_INTEGRATED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    integrate(ap.parse_args().source)
