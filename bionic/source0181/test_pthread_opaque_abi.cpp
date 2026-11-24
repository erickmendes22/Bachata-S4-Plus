// SPDX-License-Identifier: GPL-2.0-or-later
#include "core/guest_cpu/hle_call_adapter.h"
#include <cassert>

using namespace Core::GuestCpu;
using Entry=void* (*)(void*);
static u64 observed{};
static int old_call(u64*,const u64*,Entry,void*,const char*) {
    return 0;
}
static int new_call(u64* result,const u64*,Entry,u64 token,const char*) {
    observed=token;
    *result=0x87654321;
    return 0;
}
int main() {
    HleCallFrame frame{};
    u64 result=0;
    frame.gpr[7]=reinterpret_cast<u64>(&result);
    frame.gpr[6]=0;
    frame.gpr[2]=0x800000000ULL;
    frame.gpr[1]=3; // valid opaque start routine argument, not a pointer to memory
    frame.gpr[8]=0;
    frame.validate_range=[](void*,std::uintptr_t address,std::size_t,bool) {
        return address>=4096;
    };
    auto old=MakeHleCallAdapter(&old_call);
    auto fixed=MakeHleCallAdapter(&new_call);
    auto failed=old->Invoke(frame);
    assert(std::get<HleCallFailure>(failed).error==EFAULT);
    for (u64 token: {0ULL,1ULL,3ULL,4095ULL,0x234567890ULL,~0ULL}) {
        frame.gpr[1]=token;
        assert(std::get<bool>(fixed->Invoke(frame)));
        assert(observed==token && result==0x87654321);
    }
    frame.gpr[7]=3; // genuinely invalid pointer still rejected
    auto bad=fixed->Invoke(frame);
    assert(std::get<HleCallFailure>(bad).error==EFAULT);
}
