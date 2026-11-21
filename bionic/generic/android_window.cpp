// SPDX-License-Identifier: GPL-2.0-or-later
// Headless SDL event integration for an Android service-owned ANativeWindow.
// This replaces src/sdl_window.cpp ONLY in the native Bionic core build.
#include <android/native_window.h>
#include <chrono>
#include <span>
#include <stdexcept>
#include <thread>
#include <vector>

#include "android_surface.h"
#include "sdl_window.h"

namespace Frontend {

WindowSDL::WindowSDL(s32 requested_width, s32 requested_height,
                     Input::GameControllers* source, std::string_view)
    : width{requested_width}, height{requested_height}, controllers{*source} {
    ANativeWindow* native = BachataAndroid::surface.load(std::memory_order_acquire);
    if (!native) {
        throw std::runtime_error("Bachata Bionic: Android Surface was not supplied");
    }
    window_info.type = WindowSystemType::Android;
    window_info.render_surface = native;  // The JNI run call retains this reference.
    window_info.render_surface_scale = 1.0f;
    const int w = ANativeWindow_getWidth(native);
    const int h = ANativeWindow_getHeight(native);
    if (w > 0 && h > 0) {
        width = w;
        height = h;
    }
}

WindowSDL::~WindowSDL() = default;

void WindowSDL::WaitEvent() {
    if (BachataAndroid::stop_requested.load(std::memory_order_acquire)) {
        is_open = false;
        return;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(8));
}

void WindowSDL::InitTimers() {
    // No SDLActivity exists in Bachata's EmulationService. Never start SDL timers
    // bound to a non-existent SDL_Window. Controller injection is a separate path.
}

// The modern 0.21.1 frontend takes decoded icon bytes; Android uses the
// Java application icon and has no SDL window to decorate.
void WindowSDL::SetIcon(std::span<const u8>) {}
void WindowSDL::RequestKeyboard() { ++keyboard_grab; }
void WindowSDL::ReleaseKeyboard() {
    if (keyboard_grab > 0) --keyboard_grab;
}

void SetWindowIcon(SDL_Window*, const std::vector<u8>&) {}
void SetDefaultWindowIcon(SDL_Window*) {}

}  // namespace Frontend
