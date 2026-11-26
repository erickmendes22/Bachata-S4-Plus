// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include <chrono>
#include <type_traits>
#include <utility>

namespace Common::BachataProgress {

// Used only for shader/pipeline misses. A missing end identifies the call that
// has not returned; exceptions intentionally do not manufacture a success end.
template <class Report, class Function>
decltype(auto) Phase(const char* phase, Report&& report, Function&& function) {
    const auto start = std::chrono::steady_clock::now();
    report(phase, "begin", std::chrono::microseconds::rep{0});
    const auto finish = [&] {
        const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - start).count();
        report(phase, "end", elapsed);
    };
    if constexpr (std::is_void_v<decltype(std::forward<Function>(function)())>) {
        std::forward<Function>(function)();
        finish();
    } else {
        decltype(auto) value = std::forward<Function>(function)();
        finish();
        if constexpr (std::is_reference_v<decltype(value)>) {
            return static_cast<decltype(value)>(value);
        } else {
            return value;
        }
    }
}

// Fast ready waits never consult the clock. Report exactly once after a long
// wait, with the caller's lock held, then retain the original predicate wait.
template <class Condition, class Lock, class Predicate, class Report,
          class Duration = std::chrono::seconds>
void WaitOnce(Condition& condition, Lock& lock, Predicate&& ready, Report&& report,
              Duration timeout = std::chrono::seconds{2}) {
    if (ready() || condition.wait_for(lock, timeout, ready)) {
        return;
    }
    report();
    condition.wait(lock, ready);
}

} // namespace Common::BachataProgress
