#!/usr/bin/env python3
"""Exercise the integrated FEX signal handler against real guard mappings.

Only the FEX engine/context API and ARM ucontext layout are mocked. The guard
predicate, complete signal-handler function and evidence writer come from the
effective production source. No ARM guest execution or gameplay is simulated.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
args = parser.parse_args()
src = args.source.resolve() / "src"
engine = (src / "core/fex/fex_guest_engine.cpp").read_text()
start = engine.index(
    "namespace {\n#if defined(__aarch64__)\nthread_local std::uint64_t FexCallRetRecoveries{};"
)
end = engine.index("\nclass GuestEngine::Thread", start)

prefix = r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <cerrno>
#include <csignal>
#include <cstdio>
#include <optional>
#include <sys/mman.h>
#include <unistd.h>
#include "core/fex/fex_callret_guard.h"

struct TestUContext {
    struct { uint64_t pc{}; uint64_t regs[31]{}; } uc_mcontext;
};
// Define after libc includes so the test keeps its native Linux ABI.
#define ucontext_t TestUContext
#if !defined(__aarch64__)
#define __aarch64__ 1
#endif
namespace FEXCore {
namespace X86State { constexpr size_t REG_RSP = 4; }
namespace Core {
struct CpuFrame {
    struct { uint64_t callret_sp{}, rip{}; uint64_t gregs[16]{}; } State;
};
struct InternalThreadState {
    static constexpr size_t CALLRET_STACK_SIZE = 0x400000;
    void* CallRetStackBase{};
    CpuFrame* CurrentFrame{};
};
}
struct Config { uintptr_t DispatcherBegin{}, DispatcherEnd{}; };
struct SignalDelegator {
    Config config;
    const Config& GetConfig() const { return config; }
};
struct Context {
    bool jit{};
    bool IsAddressInCodeBuffer(Core::InternalThreadState*, uintptr_t) { return jit; }
};
namespace ArchHelpers::Arm64 {
enum class UnalignedHandlerType { HalfBarrier };
std::optional<uint64_t> HandleUnalignedAccess(Core::InternalThreadState*,
        UnalignedHandlerType, uintptr_t, uint64_t*) { return std::nullopt; }
}
}
namespace Core::Fex {
constexpr uint64_t kRequiredPageSize = 4096;
struct Active {
    FEXCore::Context* Context;
    FEXCore::Core::InternalThreadState* Thread;
    FEXCore::SignalDelegator* SignalDelegator;
} ActiveFexExecution;
'''
suffix = r'''
}
int main() {
    using namespace Core::Fex;
    FEXCore::Context ctx;
    FEXCore::SignalDelegator delegator;
    FEXCore::Core::CpuFrame frame;
    FEXCore::Core::InternalThreadState thread;
    constexpr auto size = FEXCore::Core::InternalThreadState::CALLRET_STACK_SIZE;
    auto allocation = mmap(nullptr, size + 8192, PROT_NONE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(allocation != MAP_FAILED);
    const auto base = reinterpret_cast<uintptr_t>(allocation) + 4096;
    assert(mprotect(reinterpret_cast<void*>(base), size, PROT_READ | PROT_WRITE) == 0);
    thread.CallRetStackBase = reinterpret_cast<void*>(base);
    thread.CurrentFrame = &frame;
    ActiveFexExecution = {&ctx, &thread, &delegator};

    // Actual pinned callback dispatcher encoding: STP xzr,xzr,[x25,#-16]!.
    alignas(4) uint32_t opcode = 0xa9bf7f3f;
    ucontext_t uc;
    uc.uc_mcontext.pc = reinterpret_cast<uintptr_t>(&opcode);
    uc.uc_mcontext.regs[25] = base;
    siginfo_t si{};
    si.si_code = SEGV_ACCERR;
    si.si_addr = reinterpret_cast<void*>(base - 16);
    delegator.config = {uc.uc_mcontext.pc, uc.uc_mcontext.pc + 4};
    const auto reset = base + size / 4;
    auto* entry = reinterpret_cast<uint64_t*>(reset);
    entry[0] = 123;
    entry[1] = 456;
    // Regression: IsAddressInCodeBuffer is false for the dispatcher.
    assert(!ctx.jit && HandleGuestSignal(SIGSEGV, &si, &uc));
    assert(uc.uc_mcontext.regs[25] == reset && frame.State.callret_sp == reset);
    assert(!entry[0] && !entry[1]);

    uc.uc_mcontext.regs[25] = base;
    delegator.config = {};
    assert(!HandleGuestSignal(SIGSEGV, &si, &uc)); // Unknown native code.
    assert(uc.uc_mcontext.regs[25] == base);
    ctx.jit = true;
    assert(HandleGuestSignal(SIGSEGV, &si, &uc));

    uc.uc_mcontext.regs[25] = base;
    opcode = 0xf9000320;
    assert(!HandleGuestSignal(SIGSEGV, &si, &uc)); // Not the pinned pair store.
    opcode = 0xa9bf7f3f;
    si.si_code = SEGV_MAPERR;
    assert(!HandleGuestSignal(SIGSEGV, &si, &uc));
    si.si_code = SEGV_ACCERR;
    si.si_addr = reinterpret_cast<void*>(base + 16);
    assert(!HandleGuestSignal(SIGSEGV, &si, &uc)); // Mapped data, not a guard.

    si.si_addr = reinterpret_cast<void*>(base + size);
    uc.uc_mcontext.regs[25] = base + size;
    opcode = 0xa8c10720; // LDP x0,x1,[x25],#16.
    assert(HandleGuestSignal(SIGSEGV, &si, &uc));
    ctx.jit = false;
    delegator.config = {uc.uc_mcontext.pc, uc.uc_mcontext.pc + 4};
    si.si_code = BUS_ADRALN;
    assert(!HandleGuestSignal(SIGBUS, &si, &uc)); // Do not broaden BUS recovery.

    const auto before = uc.uc_mcontext.regs[25];
    errno = ERANGE;
    ReportGuestFaultEvidence(SIGSEGV, &si, &uc);
    assert(uc.uc_mcontext.regs[25] == before && errno == ERANGE);
    assert(munmap(allocation, size + 8192) == 0);
    puts("FEX_DISPATCHER_GUARD_AND_FATAL_EVIDENCE_PASS");
}
'''

with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    cpp = folder / "test.cpp"
    exe = folder / "test"
    cpp.write_text(prefix + engine[start:end] + suffix)
    subprocess.run(
        ["c++", "-std=c++23", "-O2", "-Wall", "-Wextra", "-Werror",
         "-I", str(src), str(cpp), "-o", str(exe)], check=True,
    )
    result = subprocess.run([str(exe)], check=True, capture_output=True, text=True, timeout=10)
    assert "opcode=0xa9bf7f3f opcode_valid=0x1 jit=0x0 dispatcher=0x1" in result.stderr
    assert "recoveries=0x1" in result.stderr and "recoveries=0x2" in result.stderr
    assert "BACHATA_FEX_UNHANDLED_FAULT_EVIDENCE recoveries=0x3" in result.stderr
    assert "guard_match=0x1" in result.stderr and "saved_guest_rip=" in result.stderr
    print(result.stdout, end="")
