// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>

namespace BachataUi {
// Scaleform vertex shaders from the pinned Android port's UiComposition.
// Host Vulkan viewports cannot implement its raw PS4 NativeViewport check:
// fullscreen post-processing uses the same dimensions. Missing metadata
// must preserve the guest pass, rather than guessing a composition boundary.
constexpr bool MovieShader(uint64_t hash) {
    return hash == 0x34e8a281 || hash == 0x81d336ce || hash == 0x09957251 ||
           hash == 0x24042a9b || hash == 0xa400228b || hash == 0xbb4d5f8c ||
           hash == 0xe94b5b06 || hash == 0x9951d199 || hash == 0x44072322 ||
           hash == 0xa334a845;
}
}
