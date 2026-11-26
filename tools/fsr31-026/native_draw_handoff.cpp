// SPDX-License-Identifier: GPL-2.0-or-later
#include "native_draw_handoff.h"
#include <cstring>

namespace {
template<class T> T read(const void* p,size_t offset) {
    T out;std::memcpy(&out,static_cast<const unsigned char*>(p)+offset,sizeof(out));return out;
}
template<class T> void write(void* p,size_t offset,T value) {
    std::memcpy(static_cast<unsigned char*>(p)+offset,&value,sizeof(value));
}
struct Operation {
    uint64_t bytes;
    Bs4NativeWorker callback;
    Bs4NativeRenderState state;
};
static_assert(sizeof(Operation)==0x140);
}

bool bs4_native_enqueue_draw(void* scheduler,const Bs4NativeRenderState& state,
    Bs4NativeAllocate allocate,Bs4NativeFlush flush,Bs4NativeWorker worker) {
    if(!scheduler||!worker||state.colorCount>8||!state.width||!state.height||
       state.width>16384||state.height>16384||state.layers!=1)return false;
    auto* queue=read<void*>(scheduler,0x11f0);
    const auto threaded=read<uint8_t>(scheduler,0x11e8);
    if(threaded!=1) {
        // Native mode changes can leave a queue awaiting a drain. Do not
        // record on the frontend while those Vulkan commands are pending.
        if(queue)return false;
        const auto command=read<uint64_t>(scheduler,0xf08);
        if(!command)return false;
        worker(&state,command);return true;
    }
    if(!queue||!allocate||!flush)return false;
    auto* block=allocate(queue,sizeof(Operation));
    if(!block)return false;
    const Operation operation{sizeof(Operation),worker,state};
    std::memcpy(block,&operation,sizeof(operation));
    // Same cursor/flush protocol as native Scheduler::BeginRendering. The
    // allocator may switch chunks, so read the cursor only after allocating.
    const auto cursor=read<uintptr_t>(queue,0x10)+sizeof(Operation);
    write(queue,0x10,cursor);
    const auto origin=read<uintptr_t>(queue,0x40);
    if(cursor-origin>0x10000)flush(queue);
    return true;
}
