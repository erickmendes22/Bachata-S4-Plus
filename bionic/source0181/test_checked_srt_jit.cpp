// SPDX-License-Identifier: GPL-2.0-or-later
#include "srt_native_checked.h"
#include <array>
#include <cassert>
#include <cstdio>
#include <random>
using namespace Shader::CheckedArm64Srt;
struct Context { U32* flat; U32 calls{}; };
U64 PushTest(void*,U64 cur,U32 off,U32 zero,U32) {
    return zero||cur==0?0:0x10000ULL+U32(off<<2);
}
void CopyTest(void* opaque,U64 cur,U32 off,U32 b,U32 count,U32 zero,U32) {
    auto& ctx=*static_cast<Context*>(opaque);++ctx.calls;
    for(U32 j=0;j<count;++j)
        ctx.flat[b+j]=zero||cur==0?0:100+(U32(cur-0x10000)/4+off+j)%128;
}
static void AddOp(std::vector<U32>& p,U32 op,U32 a=0,U32 b=0) {
    p.insert(p.end(),{op,a,b});
}
U32 Eval(U32 op,U32 a,U32 b) {
    switch(op) {
    case Add:return a+b;case Sub:return a-b;case Mul:return a*b;
    case Shl:return a<<(b&31);case Shr:return a>>(b&31);
    case And:return a&b;case Or:return a|b;case Xor:return a^b;
    case UMin:return std::min(a,b);case UMax:return std::max(a,b);
    default:assert(false);return 0;
    }
}
int main() {
    std::vector<U32> p{Magic};
    AddOp(p,PushPtrImm,3);
    for(U32 i=0;i<8;++i)AddOp(p,CopyImm,i,16+i);
    AddOp(p,CopyImm|Zero,0,24);
    AddOp(p,PushPtrImm,7);AddOp(p,CopyImm,1,25);AddOp(p,PopPtr);
    AddOp(p,LoadFlat,0);AddOp(p,PushPtrExpr);AddOp(p,CopyImm,1,26);AddOp(p,PopPtr);
    AddOp(p,LoadFlat,1);AddOp(p,Not);AddOp(p,CopyExpr,0,27);
    AddOp(p,LoadFlat,2);AddOp(p,LoadFlat,3);AddOp(p,LoadFlat,4);
    AddOp(p,Bfe);AddOp(p,CopyExpr,0,28);
    for(U32 op:{Add,Sub,Mul,Shl,Shr,And,Or,Xor,UMin,UMax}) {
        AddOp(p,LoadFlat,5);AddOp(p,Imm,33);AddOp(p,op);AddOp(p,CopyExpr,0,29+op);
    }
    AddOp(p,PopPtr);AddOp(p,End);
    auto emitted=Compile(p,1,2);
    assert(!emitted.insns.empty()&&emitted.flat_count==43&&emitted.parent_words==6);
    assert(Compile(std::array<U32,4>{Magic,PopPtr,0,0},1,2).insns.empty());
#if defined(__aarch64__)
    std::array<U32,64> flat{};
    Context ctx{flat.data(),0};
    auto native=Native::Create(p,PushTest,CopyTest);assert(native&&native->run);
    std::mt19937 rng(123);
    for(unsigned trial=0;trial<500;++trial) {
        flat.fill(0xdeadbeef);ctx.calls=0;
        for(unsigned i=0;i<6;++i)flat[i]=rng();
        flat[4]=trial%70;
        native->run(&ctx,flat.data());
        for(U32 i=0;i<8;++i)assert(flat[16+i]==103+i);
        assert(flat[24]==0&&flat[25]==108&&flat[26]==100+((flat[0]+1u)%128));
        assert(flat[27]==100+((3u+~flat[1])%128));
        U32 mask=flat[4]>=32?~0u:(1u<<flat[4])-1;
        assert(flat[28]==100+((3+((flat[2]>>(flat[3]&31))&mask))%128));
        for(U32 op:{Add,Sub,Mul,Shl,Shr,And,Or,Xor,UMin,UMax})
            assert(flat[29+op]==100+((3+Eval(op,flat[5],33))%128));
        assert(ctx.calls==16);
    }
    std::puts("CHECKED_ARM64_SRT_EXECUTION_PASS");
#else
    std::puts("CHECKED_ARM64_SRT_ENCODING_PASS (host only)");
#endif
}
