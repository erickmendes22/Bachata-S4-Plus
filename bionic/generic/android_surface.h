// SPDX-License-Identifier: GPL-2.0-or-later
// Shared ownership is held by the synchronous JNI launch call.
#pragma once

#include <atomic>
struct ANativeWindow;

namespace BachataAndroid {
extern std::atomic<ANativeWindow*> surface;
extern std::atomic<bool> stop_requested;
}
