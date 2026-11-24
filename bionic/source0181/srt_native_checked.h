// SPDX-License-Identifier: GPL-2.0-or-later
// Based on GoW3 srt_arm64.h (239b7df8145e); guest memory is accessed only by checked callbacks.
#pragma once
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <memory>
#include <span>
#include <vector>
#if defined(__aarch64__) && defined(__linux__)
#include <sys/mman.h>
#include <unistd.h>
#endif
namespace Shader::CheckedArm64Srt {
using U32=std::uint32_t;
using U64=std::uint64_t;
enum Op:U32 { End,Imm,LoadFlat,Add,Sub,Mul,Shl,Shr,And,Or,Xor,Not,UMin,UMax,Bfe,
              PushPtrImm,PushPtrExpr,CopyImm,CopyExpr,PopPtr };
constexpr U32 Magic=0x31545253, Zero=0x80000000u, Stack=64;
using Push=U64(*)(void*,U64,U32,U32,U32);
using Copy=void(*)(void*,U64,U32,U32,U32,U32,U32);
struct Code { std::vector<U32> insns; U32 flat_count{}, parent_words{}; };
inline Code Compile(std::span<const U32> program, U64 push, U64 copy) {
    if (program.size()<4 || program.size()>65536 || program[0]!=Magic ||
        (program.size()-1)%3!=0 || !push || !copy) return {};
    // x19=context, x20=current, x21=flat; saved regs, 64 pointer slots, 64 value slots.
    Code result{{0xd503245f,0xd10c83ff,0xa90053f3,0xa9017bf5,
                 0xaa0003f3,0xaa0103f4,0xaa0103f5},16,0};
    auto emit=[&](U32 x){result.insns.push_back(x);};
    auto imm=[&](U32 reg,U32 val){
        emit(0x52800000u|((val&65535u)<<5)|reg);
        if (val>>16) emit(0x72a00000u|((val>>16)<<5)|reg);
    };
    auto call=[&](U64 addr){
        for (U32 i=0;i<4;++i)
            emit((i?0xf2800000u:0xd2800000u)|(i<<21)|
                 (U32((addr>>(16*i))&65535u)<<5)|16u);
        emit(0xd63f0200);
    };
    auto load=[&](U32 reg,U32 slot){emit(0xb94003e0u|((136u+slot)<<10)|reg);};
    auto store=[&](U32 reg,U32 slot){emit(0xb90003e0u|((136u+slot)<<10)|reg);};
    auto flat=[&](U32 slot) {
        if(slot>=262144) return false;
        result.flat_count=std::max(result.flat_count,slot+1); return true;
    };
    U32 n=0,depth=0;
    for (size_t i=1;i<program.size();i+=3) {
        const U32 word=program[i],op=word&~Zero,a=program[i+1],b=program[i+2];
        const U32 z=bool(word&Zero);
        if (op==End) {
            if(n||depth||i+3!=program.size())return {};
            emit(0xa9417bf5);emit(0xa94053f3);emit(0x910c83ff);emit(0xd65f03c0);
            return result;
        }
        if (op==Imm || op==LoadFlat) {
            if(n==Stack)return {};
            if(op==Imm)imm(3,a);
            else { if(!flat(a))return {};imm(4,a);emit(0xb8645aa3); }
            store(3,n++);continue;
        }
        if (op==PushPtrImm || op==PushPtrExpr || op==CopyImm || op==CopyExpr) {
            const bool is_push=op==PushPtrImm||op==PushPtrExpr;
            const bool dynamic=op==PushPtrExpr||op==CopyExpr;
            const U32 index=static_cast<U32>((i-1)/3);
            if(dynamic) {if(!n)return {};load(2,--n);} else imm(2,a);
            emit(0xaa1303e0);emit(0xaa1403e1);
            if(is_push) {
                if(depth==Stack)return {};
                emit(0xf90003f4u|((4u+depth++)<<10));
                imm(3,z);imm(4,index);call(push);emit(0xaa0003f4);
                result.parent_words+=2;continue;
            }
            U32 count=1;
            if(op==CopyImm&&!z&&a<0x3fffffe0u&&b<262144-32) {
                while(count<32&&i+3*count+2<program.size()&&
                      program[i+3*count]==CopyImm&&program[i+3*count+1]==a+count&&
                      program[i+3*count+2]==b+count)++count;
            }
            if(b>=262144 || !flat(b+count-1))return {};
            imm(3,b);imm(4,count);imm(5,z);imm(6,index);call(copy);
            i+=3*(count-1);continue;
        }
        if(op==PopPtr) {
            if(!depth)return {};
            emit(0xf94003f4u|((4u+--depth)<<10));continue;
        }
        if(op==Not) {
            if(!n)return {};
            load(3,n-1);emit(0x2a2303e3);store(3,n-1);continue;
        }
        if(op==Bfe) {
            if(n<3)return {};
            load(5,--n);load(4,--n);load(3,n-1);
            for(U32 x:{0x1ac42463u,0x52800024u,0x1ac52084u,0x51000484u,
                       0x12800006u,0x710080bfu,0x1a8420c4u,0x0a040063u})emit(x);
            store(3,n-1);continue;
        }
        if(n<2)return {};
        load(4,--n);load(3,n-1);
        switch(op) {
        case Add:emit(0x0b040063);break;
        case Sub:emit(0x4b040063);break;
        case Mul:emit(0x1b047c63);break;
        case Shl:emit(0x1ac42063);break;
        case Shr:emit(0x1ac42463);break;
        case And:emit(0x0a040063);break;
        case Or:emit(0x2a040063);break;
        case Xor:emit(0x4a040063);break;
        case UMin:emit(0x6b04007f);emit(0x1a843063);break;
        case UMax:emit(0x6b04007f);emit(0x1a848063);break;
        default:return {};
        }
        store(3,n-1);
    }
    return {};
}
struct Native {
    using Fn=void(*)(void*,U32*);
    Fn run{};
    U32 flat_count{},parent_words{};
    void* mapping{};
    size_t bytes{};
    Native()=default;
    Native(const Native&)=delete;
    ~Native(){
#if defined(__aarch64__) && defined(__linux__)
        if(mapping)munmap(mapping,bytes);
#endif
    }
    static std::unique_ptr<Native> Create(std::span<const U32> program,Push push,Copy copy) {
#if defined(__aarch64__) && defined(__linux__)
        auto code=Compile(program,reinterpret_cast<U64>(push),reinterpret_cast<U64>(copy));
        if(code.insns.empty())return {};
        auto out=std::make_unique<Native>();
        const long page=sysconf(_SC_PAGESIZE);
        if(page<=0)return {};
        const size_t len=code.insns.size()*sizeof(U32);
        out->bytes=(len+size_t(page)-1)/size_t(page)*size_t(page);
        auto* mem=mmap(nullptr,out->bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        if(mem==MAP_FAILED)return {};
        out->mapping=mem;
        std::memcpy(mem,code.insns.data(),len);
        __builtin___clear_cache(static_cast<char*>(mem),static_cast<char*>(mem)+len);
        if(mprotect(mem,out->bytes,PROT_READ|PROT_EXEC)!=0)return {};
        out->run=reinterpret_cast<Fn>(mem);
        out->flat_count=code.flat_count;out->parent_words=code.parent_words;
        return out;
#else
        (void)program;(void)push;(void)copy;return {};
#endif
    }
};
}
