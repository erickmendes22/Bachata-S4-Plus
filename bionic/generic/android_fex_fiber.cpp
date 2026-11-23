// SPDX-FileCopyrightText: Copyright 2026 Bachata S4+ contributors
// SPDX-License-Identifier: GPL-2.0-or-later
//
// SHARED PS4 FIBERS ON FEX/ANDROID ARM64.
//
// The desktop implementation is guarded by ARCH_X86_64 and uses native x86
// stack-switch assembly. Registering those functions on ARM64 is invalid.
// Here the syscall bridge snapshots/replaces *guest x86-64* GPR, XMM and RSP.
// The FEX HLE veneer ends with RET, which resumes the stored guest continuation.
// This file must only be compiled with SHADPS4_ENABLE_FEX_GUEST_CPU.
#include "common/types.h"
#include "common/logging/log.h"
#include "core/guest_cpu/hle_call_adapter.h"
#include "core/libraries/fiber/fiber.h"
#include "core/libraries/fiber/fiber_error.h"
#include "core/libraries/libs.h"
#include "core/loader/symbols_resolver.h"
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <memory>
#include <mutex>
#include <optional>
#include <string_view>
#include <unordered_map>

#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
namespace Libraries::Fiber {
namespace {
using Frame = Core::GuestCpu::HleCallFrame;
using Result = Core::GuestCpu::HleCallResult;
constexpr u32 Signature0 = 0xdef1649c, Signature1 = 0xb37592a0,
              OptSignature = 0xbb40e64d, MinimumContext = 512;
constexpr u64 StackSignature = 0x7149f2ca7149f2caULL;
constexpr u64 StackSizeCheck = 0xdeadbeefdeadbeefULL;
constexpr std::array<std::size_t, 6> ArgRegs{7, 6, 2, 1, 8, 9};
constexpr std::size_t RAX=0, RSP=4, RBP=5, RSI=6, RDI=7;

bool GuestMemory(Frame& f, u64 addr, std::size_t size, bool writable) {
    return addr >= 4096 && f.validate_range &&
           f.validate_range(f.validate_context, addr, size, writable);
}
std::optional<u64> Arg(Frame& f, std::size_t index) {
    if (index < ArgRegs.size()) return f.gpr[ArgRegs[index]];
    const u64 offset = sizeof(u64) * (index - ArgRegs.size() + 1);
    if (f.rsp > UINT64_MAX - offset ||
        !GuestMemory(f, f.rsp + offset, sizeof(u64), false)) return std::nullopt;
    u64 value{};
    std::memcpy(&value, reinterpret_cast<const void*>(f.rsp + offset), sizeof(value));
    return value;
}
bool GuestName(Frame& f, u64 address, char (&out)[ORBIS_FIBER_MAX_NAME_LENGTH + 1]) {
    std::memset(out, 0, sizeof(out));
    if (!address) return false;
    for (u32 i=0; i<ORBIS_FIBER_MAX_NAME_LENGTH; ++i) {
        if (address > UINT64_MAX-i || !GuestMemory(f, address+i, 1, false))
            return false;
        const char c=*reinterpret_cast<const char*>(address+i);
        out[i]=c;
        if (!c) return true;
    }
    return true;
}
void Ret(Frame& f, s32 status) {f.gpr[RAX]=static_cast<u64>(static_cast<s64>(status));}
bool Valid(Frame& f, u64 addr) {
    if (!GuestMemory(f, addr, sizeof(OrbisFiber), false)) return false;
    const auto* fiber=reinterpret_cast<const OrbisFiber*>(addr);
    return fiber->magic_start==Signature0 && fiber->magic_end==Signature1;
}
struct Registers {
    std::array<u64,16> gpr{};
    std::array<std::array<u64,2>,16> xmm{};
    u64 rsp{}, resumed_output{};
};
Registers Snapshot(const Frame& f, u64 resumed_output=0) {
    return {f.gpr,f.xmm,f.rsp,resumed_output};
}
std::mutex saved_mutex;
std::unordered_map<u64,Registers> suspended;
std::atomic<u32> context_size_check{0};
struct Active { bool running{}; u64 current{}, main_output{}; Registers main{}; };
thread_local Active active;

bool Resume(Frame& f, const Registers& r, u64 incoming) {
    if (r.resumed_output) {
        if (!GuestMemory(f,r.resumed_output,sizeof(u64),true)) return false;
        std::memcpy(reinterpret_cast<void*>(r.resumed_output),&incoming,8);
    }
    f.gpr=r.gpr; f.xmm=r.xmm;
    f.rsp=r.rsp; f.gpr[RSP]=r.rsp;
    Ret(f,0);
    return true;
}
// HLE stub executes syscall; RET. A new fiber's first RET must target
// the actual x86 guest entrypoint; after it, stack alignment is SysV (8 mod 16).
bool Start(Frame& f, OrbisFiber* fiber, u64 incoming) {
    const u64 entry=reinterpret_cast<u64>(fiber->entry);
    if (entry<4096) return false;
    u64 top{};
    if (fiber->addr_context && fiber->size_context>=MinimumContext) {
        const u64 base=reinterpret_cast<u64>(fiber->addr_context);
        if (base>UINT64_MAX-fiber->size_context) return false;
        top=(base+fiber->size_context)&~u64{15};
    } else {
        if (f.rsp<4096+272) return false;
        top=(f.rsp-256)&~u64{15}; // preserve caller's 128-byte redzone
    }
    if (top<16 || !GuestMemory(f,top-16,16,true)) return false;
    const u64 stack_words[2]{entry,0}; // zero is deliberate trap if entry returns
    std::memcpy(reinterpret_cast<void*>(top-16),stack_words,sizeof(stack_words));
    f.rsp=top-16;f.gpr[RSP]=top-16;
    f.gpr[RDI]=fiber->arg_on_initialize; f.gpr[RSI]=incoming;
    Ret(f,0);return true;
}
bool Attach(Frame& f, OrbisFiber* fiber, u64 context, u64 size) {
    if (!context && !size) return true;
    if (!context || !size || (context&15) || (size&15) ||
        size<MinimumContext || context>UINT64_MAX-size ||
        !GuestMemory(f,context,size,true) || fiber->addr_context) return false;
    fiber->addr_context=reinterpret_cast<void*>(context);
    fiber->size_context=size;
    fiber->context_start=reinterpret_cast<void*>(context);
    fiber->context_end=reinterpret_cast<void*>(context+size);
    std::memcpy(reinterpret_cast<void*>(context),&StackSignature,8);
    if (fiber->flags & FiberFlags::ContextSizeCheck)
        for(u64 p=context+8;p+8<=context+size;p+=8)
            std::memcpy(reinterpret_cast<void*>(p),&StackSizeCheck,8);
    return true;
}
enum class Op {
    Initialize, InitializeInternal, OptInitialize, Finalize, Run, RunAttach,
    Switch, SwitchAttach, GetSelf, ReturnToThread, GetInfo, Rename,
    StartSizeCheck, StopSizeCheck, GetFramePointer
};
class FiberBridge final:public Core::GuestCpu::HleCallAdapter {
public:
    explicit FiberBridge(Op operation):op(operation){}
    Result Invoke(Frame& f) const override {
        auto arg=[&](std::size_t index){return Arg(f,index);};
        const auto a=arg(0);
        if (!a && op!=Op::StopSizeCheck) return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
        switch(op) {
        case Op::OptInitialize:{
            if(!*a){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if((*a&7) || !GuestMemory(f,*a,sizeof(OrbisFiberOptParam),true)){
                Ret(f,ORBIS_FIBER_ERROR_ALIGNMENT);return true;}
            reinterpret_cast<OrbisFiberOptParam*>(*a)->magic=OptSignature;
            Ret(f,0);return true;
        }
        case Op::Initialize:
        case Op::InitializeInternal:{
            const auto name=arg(1),entry=arg(2),init=arg(3),context=arg(4),
                       size=arg(5),optarg=arg(6),last=arg(7),build=arg(8);
            if(!name||!entry||!init||!context||!size||!optarg||!last||
               (op==Op::InitializeInternal&&!build))
                return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
            if(!*a||!*name||!*entry){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if((*a&7)||(*context&15)||(*optarg&7)){
                Ret(f,ORBIS_FIBER_ERROR_ALIGNMENT);return true;}
            if((*size&&*size<MinimumContext)||(*size&15)){
                Ret(f,ORBIS_FIBER_ERROR_RANGE);return true;}
            if(bool(*context)!=bool(*size)||*context>UINT64_MAX-*size||
               !GuestMemory(f,*a,sizeof(OrbisFiber),true)||
               (*context&&!GuestMemory(f,*context,*size,true))||
               (*optarg&&(!GuestMemory(f,*optarg,sizeof(OrbisFiberOptParam),false)||
                 reinterpret_cast<const OrbisFiberOptParam*>(*optarg)->magic!=OptSignature))){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            char guest_name[ORBIS_FIBER_MAX_NAME_LENGTH+1]{};
            if(!GuestName(f,*name,guest_name)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            auto* fiber=reinterpret_cast<OrbisFiber*>(*a);
            // Construct the atomic FiberState correctly in the guest backing.
            std::construct_at(fiber);
            std::memcpy(fiber->name,guest_name,sizeof(guest_name));
            fiber->entry=reinterpret_cast<OrbisFiberEntry>(*entry);
            fiber->arg_on_initialize=*init;
            fiber->addr_context=reinterpret_cast<void*>(*context);
            fiber->size_context=*size;
            fiber->flags=op==Op::InitializeInternal?static_cast<u32>(*last):0;
            const u32 firmware=op==Op::InitializeInternal?static_cast<u32>(*build):
                              static_cast<u32>(*last);
            if(firmware>=0x3500000u) fiber->flags|=FiberFlags::SetFpuRegs;
            if(context_size_check.load()) fiber->flags|=FiberFlags::ContextSizeCheck;
            fiber->context_start=reinterpret_cast<void*>(*context);
            fiber->context_end=reinterpret_cast<void*>(*context+*size);
            fiber->magic_start=Signature0;fiber->magic_end=Signature1;
            fiber->state.store(FiberState::Idle);
            if(*context){
                std::memcpy(reinterpret_cast<void*>(*context),&StackSignature,8);
                if(fiber->flags&FiberFlags::ContextSizeCheck)
                    for(u64 p=*context+8;p+8<=*context+*size;p+=8)
                        std::memcpy(reinterpret_cast<void*>(p),&StackSizeCheck,8);
            }
            {std::lock_guard lock{saved_mutex};suspended.erase(*a);}
            Ret(f,0);return true;
        }
        case Op::Finalize:{
            if(!*a){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if(*a&7){Ret(f,ORBIS_FIBER_ERROR_ALIGNMENT);return true;}
            if(!Valid(f,*a)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            auto* fiber=reinterpret_cast<OrbisFiber*>(*a);
            FiberState expected=FiberState::Idle;
            if(!fiber->state.compare_exchange_strong(expected,FiberState::Terminated)){
                Ret(f,ORBIS_FIBER_ERROR_STATE);return true;}
            {std::lock_guard lock{saved_mutex};suspended.erase(*a);}
            Ret(f,0);return true;
        }
        case Op::GetInfo:{
            const auto dst=arg(1);
            if(!dst)return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
            if(!*a||!*dst){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if((*a&7)||(*dst&7)){Ret(f,ORBIS_FIBER_ERROR_ALIGNMENT);return true;}
            if(!Valid(f,*a)||!GuestMemory(f,*dst,sizeof(OrbisFiberInfo),true)){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            auto* dstinfo=reinterpret_cast<OrbisFiberInfo*>(*dst);
            if(dstinfo->size!=sizeof(OrbisFiberInfo)){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            const auto* fiber=reinterpret_cast<const OrbisFiber*>(*a);
            dstinfo->entry=fiber->entry;dstinfo->arg_on_initialize=fiber->arg_on_initialize;
            dstinfo->addr_context=fiber->addr_context;dstinfo->size_context=fiber->size_context;
            std::memcpy(dstinfo->name,fiber->name,sizeof(dstinfo->name));
            dstinfo->size_context_margin=UINT64_MAX;
            Ret(f,0);return true;
        }
        case Op::Rename:{
            const auto name=arg(1);
            if(!name)return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
            if(!*a||!*name){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if((*a&7)||!Valid(f,*a)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            char str[ORBIS_FIBER_MAX_NAME_LENGTH+1]{};
            if(!GuestName(f,*name,str)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            std::memcpy(reinterpret_cast<OrbisFiber*>(*a)->name,str,sizeof(str));
            Ret(f,0);return true;
        }
        case Op::StartSizeCheck:{
            if(*a){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            u32 expected=0;
            Ret(f,context_size_check.compare_exchange_strong(expected,1)?
                  0:ORBIS_FIBER_ERROR_STATE);return true;
        }
        case Op::StopSizeCheck:{
            u32 expected=1;
            Ret(f,context_size_check.compare_exchange_strong(expected,0)?
                  0:ORBIS_FIBER_ERROR_STATE);return true;
        }
        case Op::GetSelf:
        case Op::GetFramePointer:{
            if(!*a){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if(!active.running){Ret(f,ORBIS_FIBER_ERROR_PERMISSION);return true;}
            if(!GuestMemory(f,*a,sizeof(u64),true)){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            const u64 value=op==Op::GetSelf?active.current:f.gpr[RBP];
            std::memcpy(reinterpret_cast<void*>(*a),&value,8);
            Ret(f,0);return true;
        }
        case Op::Run:
        case Op::RunAttach:{
            const bool attach=op==Op::RunAttach;
            const auto ctx=attach?arg(1):std::optional<u64>{0};
            const auto size=attach?arg(2):std::optional<u64>{0};
            const auto incoming=arg(attach?3:1),out=arg(attach?4:2);
            if(!ctx||!size||!incoming||!out)
                return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
            if(!*a){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if(*a&7){Ret(f,ORBIS_FIBER_ERROR_ALIGNMENT);return true;}
            if(!Valid(f,*a)||(*out&&!GuestMemory(f,*out,8,true))){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            if(active.running){Ret(f,ORBIS_FIBER_ERROR_PERMISSION);return true;}
            auto* fiber=reinterpret_cast<OrbisFiber*>(*a);
            if(!Attach(f,fiber,*ctx,*size)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            FiberState expected=FiberState::Idle;
            if(!fiber->state.compare_exchange_strong(expected,FiberState::Run)){
                Ret(f,ORBIS_FIBER_ERROR_STATE);return true;}
            const Registers main=Snapshot(f);
            std::optional<Registers> continuation;
            {std::lock_guard lock{saved_mutex};
             const auto it=suspended.find(*a);
             if(it!=suspended.end()){continuation=it->second;suspended.erase(it);}}
            const bool ok=continuation?Resume(f,*continuation,*incoming):
                                       Start(f,fiber,*incoming);
            if(!ok){fiber->state.store(FiberState::Idle);
                    Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            active={true,*a,*out,main};
            return true;
        }
        case Op::Switch:
        case Op::SwitchAttach:{
            const bool attach=op==Op::SwitchAttach;
            const auto ctx=attach?arg(1):std::optional<u64>{0};
            const auto size=attach?arg(2):std::optional<u64>{0};
            const auto incoming=arg(attach?3:1),out=arg(attach?4:2);
            if(!ctx||!size||!incoming||!out)
                return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
            if(!*a){Ret(f,ORBIS_FIBER_ERROR_NULL);return true;}
            if(!active.running){Ret(f,ORBIS_FIBER_ERROR_PERMISSION);return true;}
            if(*a==active.current){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            if(!Valid(f,*a)||(*out&&!GuestMemory(f,*out,8,true))){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            auto* next=reinterpret_cast<OrbisFiber*>(*a);
            if(!Attach(f,next,*ctx,*size)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            FiberState expected=FiberState::Idle;
            if(!next->state.compare_exchange_strong(expected,FiberState::Run)){
                Ret(f,ORBIS_FIBER_ERROR_STATE);return true;}
            const Registers current=Snapshot(f,*out);
            std::optional<Registers> continuation;
            {std::lock_guard lock{saved_mutex};
             const auto it=suspended.find(*a);
             if(it!=suspended.end()){continuation=it->second;suspended.erase(it);}}
            const bool ok=continuation?Resume(f,*continuation,*incoming):
                                       Start(f,next,*incoming);
            if(!ok){next->state.store(FiberState::Idle);
                    Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            {std::lock_guard lock{saved_mutex};suspended.insert_or_assign(active.current,current);}
            reinterpret_cast<OrbisFiber*>(active.current)->state.store(FiberState::Idle);
            active.current=*a;
            return true;
        }
        case Op::ReturnToThread:{
            const auto out=arg(1);
            if(!out)return Core::GuestCpu::HleCallFailure{EFAULT,Name()};
            if(!active.running){Ret(f,ORBIS_FIBER_ERROR_PERMISSION);return true;}
            if(*out&&!GuestMemory(f,*out,8,true)){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            if(!Valid(f,active.current)){Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            auto* fiber=reinterpret_cast<OrbisFiber*>(active.current);
            if(active.main_output && !GuestMemory(f,active.main_output,8,true)){
                Ret(f,ORBIS_FIBER_ERROR_INVALID);return true;}
            if(fiber->addr_context){
                const Registers current=Snapshot(f,*out);
                std::lock_guard lock{saved_mutex};
                suspended.insert_or_assign(active.current,current);
            }
            fiber->state.store(FiberState::Idle);
            if(active.main_output)
                std::memcpy(reinterpret_cast<void*>(active.main_output),&*a,8);
            const Registers parent=active.main;
            active={};
            if(!Resume(f,parent,0)) Ret(f,ORBIS_FIBER_ERROR_INVALID);
            return true;
        }
        }
        return Core::GuestCpu::HleCallFailure{ENOSYS,Name()};
    }
private: Op op;
};
} // namespace

// All 15 official libSceFiber NIDs, no unsupported ARM64 'success' stubs.
// Crucially this executes on the FEX guest x86 frame, not in host ucontext.
void RegisterFexFiberBridge(Core::Loader::SymbolsResolver* sym) {
    static constexpr struct {const char* nid;Op operation;} exports[]{
        {"hVYD7Ou2pCQ",Op::Initialize},
        {"7+OJIpko9RY",Op::InitializeInternal},
        {"asjUJJ+aa8s",Op::OptInitialize},
        {"JeNX5F-NzQU",Op::Finalize},
        {"a0LLrZWac0M",Op::Run},
        {"avfGJ94g36Q",Op::RunAttach},
        {"PFT2S-tJ7Uk",Op::Switch},
        {"ZqhZFuzKT6U",Op::SwitchAttach},
        {"p+zLIOg27zU",Op::GetSelf},
        {"B0ZX2hx9DMw",Op::ReturnToThread},
        {"uq2Y5BFz0PE",Op::GetInfo},
        {"JzyT91ucGDc",Op::Rename},
        {"Lcqty+QNWFc",Op::StartSizeCheck},
        {"Kj4nXMpnM8Y",Op::StopSizeCheck},
        {"0dy4JtMUcMQ",Op::GetFramePointer},
    };
    for(const auto& e:exports){
        Core::Loader::SymbolResolver sr{};
        sr.name=e.nid;sr.library="libSceFiber";sr.library_version=1;
        sr.module="libSceFiber";sr.type=Core::Loader::SymbolType::Function;
        sym->AddFunction(sr,std::make_shared<FiberBridge>(e.operation));
    }
    LOG_INFO(Lib_Fiber,"BACHATA_FEX_FIBER_REAL_CONTEXT registered {} ops",std::size(exports));
}
} // namespace Libraries::Fiber
#endif
