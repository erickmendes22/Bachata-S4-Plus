#!/usr/bin/env python3
"""Cheap host-side ABI/guest-state test before expensive Android NDK builds.

Tests the actual bionic/generic/android_fex_fiber.cpp against minimal source-API
mocks (so it does not link Vulkan, FEXCore or Android). Includes guest x86 frame
RSP/RET transitions for Run -> Switch -> ReturnToThread. The host compiler
test is NOT Android gameplay proof; Android FEX must still be tested on-device.
"""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

OVERLAY = Path(__file__).resolve().parent.parent / "generic/android_fex_fiber.cpp"
H = {
"common/types.h": """
#pragma once
#include <cstdint>
using u64=uint64_t;using u32=uint32_t;using s32=int32_t;using s64=int64_t;
#define PS4_SYSV_ABI
""",
"common/logging/log.h": """
#pragma once
#define LOG_INFO(...) do {} while(0)
#define Lib_Fiber 0
""",
"core/guest_cpu/hle_call_adapter.h": """
#pragma once
#include "common/types.h"
#include <array>
#include <memory>
#include <string_view>
#include <variant>
namespace Core::GuestCpu {
struct HleCallFrame {u64 operation{};std::array<u64,16> gpr{};
std::array<std::array<u64,2>,16> xmm{};uintptr_t rsp{};
bool(*validate_range)(void*,uintptr_t,size_t,bool){};void*validate_context{};};
struct HleCallFailure{int error{};std::string_view name;};
using HleCallResult=std::variant<bool,HleCallFailure>;
class HleCallAdapter {public:virtual ~HleCallAdapter()=default;
virtual HleCallResult Invoke(HleCallFrame&)const=0;
std::string_view Name()const{return "fex-fiber-test";}};
}
""",
"core/libraries/fiber/fiber.h": """
#pragma once
#include "common/types.h"
#include <atomic>
namespace Core::Loader {class SymbolsResolver;}
namespace Libraries::Fiber {
#define ORBIS_FIBER_MAX_NAME_LENGTH (31)
#define ORBIS_FIBER_CONTEXT_MINIMUM_SIZE (512)
typedef void PS4_SYSV_ABI(*OrbisFiberEntry)(u64,u64);
enum FiberState:u32{Run=1u,Idle=2u,Terminated=3u};
enum FiberFlags:u32{None=0,NoUlobjmgr=1,ContextSizeCheck=0x10,SetFpuRegs=0x100};
struct OrbisFiber;
struct OrbisFiberContext {struct{u64 rax,rcx,rdx,rbx,rsp,rbp,r8,r9,r10,r11,r12,r13,r14,r15;
uint16_t fpucw;uint32_t mxcsr;};OrbisFiber*current_fiber;OrbisFiber*prev_fiber;
u64 arg_on_run_to,arg_on_return,return_val;};
struct OrbisFiber {u32 magic_start;std::atomic<FiberState> state;OrbisFiberEntry entry;
u64 arg_on_initialize;void*addr_context;u64 size_context;
char name[ORBIS_FIBER_MAX_NAME_LENGTH+1];OrbisFiberContext*context;
u32 flags;void*context_start;void*context_end;u32 magic_end;};
struct OrbisFiberInfo {u64 size;OrbisFiberEntry entry;u64 arg_on_initialize;
void*addr_context;u64 size_context;char name[ORBIS_FIBER_MAX_NAME_LENGTH+1];
u64 size_context_margin;uint8_t pad[48];};
struct OrbisFiberOptParam{u32 magic;};
static_assert(sizeof(OrbisFiberInfo)==128);
}
""",
"core/libraries/fiber/fiber_error.h": """
#pragma once
constexpr int ORBIS_FIBER_ERROR_NULL=0x80590001,
ORBIS_FIBER_ERROR_ALIGNMENT=0x80590002,
ORBIS_FIBER_ERROR_RANGE=0x80590003,
ORBIS_FIBER_ERROR_INVALID=0x80590004,
ORBIS_FIBER_ERROR_PERMISSION=0x80590005,
ORBIS_FIBER_ERROR_STATE=0x80590006;
""",
"core/libraries/libs.h": "#pragma once\n",
"core/loader/symbols_resolver.h": """
#pragma once
#include "common/types.h"
#include "core/guest_cpu/hle_call_adapter.h"
#include <memory>
#include <string>
#include <unordered_map>
namespace Core::Loader {
enum class SymbolType {Function};
struct SymbolResolver{std::string name,library,module;int library_version{};
SymbolType type{};};
class SymbolsResolver {public:
std::unordered_map<std::string,std::shared_ptr<Core::GuestCpu::HleCallAdapter>> ops;
void AddFunction(const SymbolResolver&s,std::shared_ptr<Core::GuestCpu::HleCallAdapter> fn)
{ops[s.name]=std::move(fn);}
};
}
""",
}
MAIN = r"""
#include "core/loader/symbols_resolver.h"
#include "core/libraries/fiber/fiber.h"
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <variant>
using Core::GuestCpu::HleCallFrame;
using Core::Loader::SymbolsResolver;
using namespace Libraries::Fiber;
namespace Libraries::Fiber{void RegisterFexFiberBridge(Core::Loader::SymbolsResolver*);}
constexpr std::size_t args[6]{7,6,2,1,8,9};
bool GuestAccess(void*,uintptr_t addr,size_t size,bool)
{return addr>0x10000&&size<1'000'000&&addr+size>addr;}
struct Guest{
std::array<uint64_t,1024> stack{};
HleCallFrame frame{};
Guest(){frame.validate_range=GuestAccess;frame.rsp=(uintptr_t)&stack[400];
frame.gpr[4]=frame.rsp;stack[400]=0xfeedface;}
void Args(std::initializer_list<uint64_t> x){
size_t i=0;for(auto v:x){if(i<6)frame.gpr[args[i]]=v;else stack[401+i-6]=v;++i;}}
};
void Call(SymbolsResolver& db,const char*nid,Guest& g,std::initializer_list<uint64_t> x){
g.Args(x);const auto it=db.ops.find(nid);assert(it!=db.ops.end());
const auto result=it->second->Invoke(g.frame);
if(std::holds_alternative<Core::GuestCpu::HleCallFailure>(result)){
std::cerr<<"FAIL HLE "<<nid<<"\n";std::abort();}
assert(std::get<bool>(result));
}
void Entry(uint64_t,uint64_t){}
int main(){
SymbolsResolver db;RegisterFexFiberBridge(&db);assert(db.ops.size()==15);
Guest g;alignas(8) OrbisFiberOptParam opt{};
auto f1=std::make_unique<OrbisFiber>();
auto f2=std::make_unique<OrbisFiber>();
auto stack1=std::make_unique<std::array<uint64_t,1024>>();
auto stack2=std::make_unique<std::array<uint64_t,1024>>();
Call(db,"asjUJJ+aa8s",g,{(uint64_t)&opt});
assert(g.frame.gpr[0]==0&&opt.magic==0xbb40e64d);
Call(db,"hVYD7Ou2pCQ",g,{(uint64_t)f1.get(),(uint64_t)"one",
(uint64_t)&Entry,0x11,(uint64_t)stack1.get(),sizeof(*stack1),
(uint64_t)&opt,0x3500000});
assert(g.frame.gpr[0]==0&&f1->state.load()==FiberState::Idle);
Call(db,"hVYD7Ou2pCQ",g,{(uint64_t)f2.get(),(uint64_t)"two",
(uint64_t)&Entry,0x22,(uint64_t)stack2.get(),sizeof(*stack2),
(uint64_t)&opt,0x3500000});
assert(g.frame.gpr[0]==0&&f2->state.load()==FiberState::Idle);
const uint64_t mainrsp=g.frame.rsp;
uint64_t completed=0;
g.frame.gpr[3]=0x998877;
Call(db,"a0LLrZWac0M",g,{(uint64_t)f1.get(),0x999,(uint64_t)&completed});
assert(g.frame.rsp!=mainrsp&&*(uint64_t*)g.frame.rsp==(uint64_t)&Entry);
assert(g.frame.gpr[7]==0x11&&g.frame.gpr[6]==0x999);
g.frame.rsp+=8;g.frame.gpr[4]=g.frame.rsp;
uint64_t self{};
Call(db,"p+zLIOg27zU",g,{(uint64_t)&self});assert(self==(uint64_t)f1.get());
const auto suspended_rsp=g.frame.rsp;
uint64_t incoming{};
Call(db,"PFT2S-tJ7Uk",g,{(uint64_t)f2.get(),0x123,(uint64_t)&incoming});
assert(g.frame.gpr[7]==0x22&&g.frame.gpr[6]==0x123);
assert(f1->state.load()==FiberState::Idle&&f2->state.load()==FiberState::Run);
g.frame.rsp+=8;g.frame.gpr[4]=g.frame.rsp;
Call(db,"PFT2S-tJ7Uk",g,{(uint64_t)f1.get(),0xabcd,0});
assert(incoming==0xabcd&&g.frame.rsp==suspended_rsp);
Call(db,"B0ZX2hx9DMw",g,{0xbeef,0});
assert(g.frame.rsp==mainrsp&&g.frame.gpr[3]==0x998877&&completed==0xbeef);
Call(db,"JeNX5F-NzQU",g,{(uint64_t)f1.get()});
assert(g.frame.gpr[0]==0&&f1->state.load()==FiberState::Terminated);
std::cout<<"BACHATA_FEX_FIBER_CONTEXT_ABI_SELFTEST_PASS ops="<<db.ops.size()<<"\n";
}
"""

def main() -> None:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler or not OVERLAY.exists():
        raise SystemExit("FEX guest fiber host ABI compiler or source not found")
    with tempfile.TemporaryDirectory(prefix="bachata-fiber-") as tmp:
        folder = Path(tmp)
        for name, data in H.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data)
        test = folder / "test.cpp"
        test.write_text(MAIN)
        executable = folder / "test"
        subprocess.run([compiler, "-std=c++20", "-Wall", "-Wextra",
                        "-Werror", "-O1", "-DSHADPS4_ENABLE_FEX_GUEST_CPU",
                        "-I", str(folder), str(OVERLAY), str(test), "-o",
                        str(executable)], check=True)
        subprocess.run([str(executable)], check=True)

if __name__ == "__main__":
    main()
