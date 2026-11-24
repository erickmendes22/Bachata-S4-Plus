// SPDX-License-Identifier: GPL-2.0-or-later
#include "ahb_release_slots.h"
#include <cassert>
#include <fcntl.h>
#include <cstdio>
using namespace std::chrono_literals;
int main(){
    BachataAhb::ReleaseSlots pool;
    auto a=pool.Take(1ms),b=pool.Take(1ms),c=pool.Take(1ms);
    assert(a&&b&&c&&a->index!=b->index&&b->index!=c->index);
    assert(!pool.Take(1ms));
    int f[2];assert(pipe(f)==0);
    pool.Returned(b->index,f[0]);
    auto reused=pool.Take(1ms);assert(reused&&reused->index==b->index&&reused->fence==f[0]);
    close(reused->fence);close(f[1]);
    assert(!pool.Take(1ms));
    pool.Retire();
    int p[2];assert(pipe(p)==0);
    pool.Returned(a->index,p[0]);
    assert(fcntl(p[0],F_GETFD)==-1);
    close(p[1]);
    assert(!pool.Take(1ms));
    std::puts("AHB_RELEASE_OWNERSHIP_PASS");
}
