// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstddef>
#include <cstdint>

// Binary ABI of R27's existing 025, verified by executing its worker.
// This is not the layout of an arbitrary upstream shadPS4 revision.
struct Bs4NativeColor {
    uint64_t view;
    uint32_t layout;
    unsigned char clear[16];
    uint32_t clearEnabled;
};
struct Bs4NativeRenderState {
    Bs4NativeColor colors[8];
    uint64_t depth;
    uint32_t depthLayout;
    float depthClear;
    uint32_t stencilClear;
    unsigned char reserved[8];
    uint8_t depthEnabled, depthClearEnabled, stencilEnabled, stencilClearEnabled;
    uint32_t width, height, layers, colorCount;
};
static_assert(sizeof(Bs4NativeColor)==32);
static_assert(sizeof(Bs4NativeRenderState)==304);
static_assert(offsetof(Bs4NativeRenderState,width)==0x120);

using Bs4NativeAllocate = void* (*)(void*,size_t);
using Bs4NativeFlush = void (*)(void*);
using Bs4NativeWorker = void (*)(const void*,uint64_t);

// Enqueue a copied draw boundary alongside the native Vulkan commands. Direct
// mode is supported only when there is no outstanding native worker queue.
bool bs4_native_enqueue_draw(void* scheduler,const Bs4NativeRenderState&,
    Bs4NativeAllocate,Bs4NativeFlush,Bs4NativeWorker);
