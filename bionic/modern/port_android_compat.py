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
        raise RuntimeError(f"{path}: expected one exact 0.21.1 anchor, found {count}")
    path.write_text(data.replace(old, new, 1))


def integrate(source: Path) -> None:
    time = source / "src/core/libraries/kernel/time.cpp"
    original_zone = """#else
#if defined(__APPLE__) || defined(__FreeBSD__)
    // std::chrono::current_zone() not available yet.
    const auto* time_zone = date::current_zone();
#else
    const auto* time_zone = std::chrono::current_zone();
#endif // __APPLE__
    auto info = time_zone->get_info(std::chrono::system_clock::now());

    *local_time = info.offset.count() + info.save.count() * 60 + time;

    if (st != nullptr) {
        st->t = time;
        st->west_sec = info.offset.count();
        st->dst_sec = info.save.count() * 60;
    }

    if (dst_sec != nullptr) {
        *dst_sec = info.save.count() * 60;
    }
#endif // _WIN32"""
    android_zone = """#elif defined(__ANDROID__)
    // BIONIC_021_HOST_TIME_ZONE: Android NDK libc++ does not implement
    // std::chrono::current_zone. Use Bionic localtime_r for the input time.
    struct tm local_tm{};
    if (local_time == nullptr || localtime_r(&time, &local_tm) == nullptr) {
        return ORBIS_KERNEL_ERROR_EINVAL;
    }
    const auto utc_offset = static_cast<s64>(local_tm.tm_gmtoff);
    const auto daylight_seconds = local_tm.tm_isdst > 0 ? 3600ULL : 0ULL;
    *local_time = static_cast<time_t>(static_cast<s64>(time) + utc_offset);
    if (st != nullptr) {
        st->t = time;
        st->west_sec = static_cast<u32>(utc_offset);
        st->dst_sec = daylight_seconds;
    }
    if (dst_sec != nullptr) {
        *dst_sec = daylight_seconds;
    }
#else
#if defined(__APPLE__) || defined(__FreeBSD__)
    // std::chrono::current_zone() not available yet.
    const auto* time_zone = date::current_zone();
#else
    const auto* time_zone = std::chrono::current_zone();
#endif // __APPLE__
    auto info = time_zone->get_info(std::chrono::system_clock::now());

    *local_time = info.offset.count() + info.save.count() * 60 + time;

    if (st != nullptr) {
        st->t = time;
        st->west_sec = info.offset.count();
        st->dst_sec = info.save.count() * 60;
    }

    if (dst_sec != nullptr) {
        *dst_sec = info.save.count() * 60;
    }
#endif // _WIN32"""
    replace_once(time, original_zone, android_zone)

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
