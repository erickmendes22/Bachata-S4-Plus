"""Complete pinned FEX call/return guard recovery and retain decisive fault evidence.

FEX f2b679f6 emits the same x25 STP in both BranchOps.cpp and its callback
dispatcher (Dispatcher.cpp:504). IsAddressInCodeBuffer deliberately excludes
the dispatcher, whose bounds are published through SignalDelegatorConfig.
Keep the existing exact instruction/address/SP predicate for both ranges.
Never recover an arbitrary native fault or change guest/HLE CPU semantics.
"""
from pathlib import Path


def apply(root: Path):
    def edit(path, old, new):
        text = path.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"FEX fault evidence contract {path.name}: {old[:100]}")
        path.write_text(text.replace(old, new))

    fex = root / "src/core/fex/fex_guest_engine.cpp"
    header = fex.with_suffix(".h")
    signals = root / "src/core/signals.cpp"
    edit(
        header,
        "bool HandleGuestSignal(int signal, siginfo_t* info, void* rawContext) noexcept;",
        "bool HandleGuestSignal(int signal, siginfo_t* info, void* rawContext) noexcept;\n"
        "// Fatal-path evidence only; never changes or resumes the faulting context.\n"
        "void ReportGuestFaultEvidence(int signal, siginfo_t* info, void* rawContext) noexcept;",
    )
    edit(
        fex,
        "bool HandleGuestSignal(int signal, siginfo_t* info, void* rawContext) noexcept {",
        r'''namespace {
#if defined(__aarch64__)
thread_local std::uint64_t FexCallRetRecoveries{};

// This runs in an existing signal handler. Avoid formatting libraries,
// allocation, locks, and reads from code outside the known FEX mappings.
void WriteFexFaultEvidence(const char* event, int signal, siginfo_t* info,
                          void* rawContext) noexcept {
  if (!info || !rawContext || !ActiveFexExecution.Context ||
      !ActiveFexExecution.Thread || !ActiveFexExecution.SignalDelegator) return;
  const auto* context = reinterpret_cast<const ucontext_t*>(rawContext);
  const auto* thread = ActiveFexExecution.Thread;
  const auto pc = static_cast<std::uintptr_t>(context->uc_mcontext.pc);
  const auto fault = reinterpret_cast<std::uintptr_t>(info->si_addr);
  const auto base = reinterpret_cast<std::uintptr_t>(thread->CallRetStackBase);
  constexpr std::uint64_t size = FEXCore::Core::InternalThreadState::CALLRET_STACK_SIZE;
  const auto sp = static_cast<std::uint64_t>(context->uc_mcontext.regs[25]);
  const bool in_jit = ActiveFexExecution.Context->IsAddressInCodeBuffer(
      ActiveFexExecution.Thread, pc);
  const auto& config = ActiveFexExecution.SignalDelegator->GetConfig();
  const bool in_dispatcher = pc >= config.DispatcherBegin && pc < config.DispatcherEnd;
  const bool opcode_valid = (in_jit || in_dispatcher) && !(pc & 3);
  const std::uint32_t opcode = opcode_valid ?
      *reinterpret_cast<const volatile std::uint32_t*>(pc) : 0;
  const bool guard_match = opcode_valid && BachataFex::IsCallRetGuardAccess(
      base, size, kRequiredPageSize, fault, sp, opcode);
  char buffer[768];
  std::size_t used = 0;
  const auto append = [&](const char* text) {
    while (*text && used < sizeof(buffer) - 1) buffer[used++] = *text++;
  };
  const auto field = [&](const char* name, std::uint64_t value) {
    append(name);
    append("0x");
    bool significant = false;
    for (int shift = 60; shift >= 0; shift -= 4) {
      const auto digit = static_cast<unsigned>((value >> shift) & 15);
      if (digit || significant || !shift) {
        significant = true;
        if (used < sizeof(buffer) - 1) buffer[used++] = "0123456789abcdef"[digit];
      }
    }
  };
  append(event);
  field(" recoveries=", FexCallRetRecoveries);
  field(" signal=", static_cast<unsigned>(signal));
  field(" si_code=", static_cast<std::uint32_t>(info->si_code));
  field(" pc=", pc);
  field(" opcode=", opcode);
  field(" opcode_valid=", opcode_valid);
  field(" jit=", in_jit);
  field(" dispatcher=", in_dispatcher);
  field(" fault=", fault);
  field(" x25=", sp);
  field(" callret_base=", base);
  field(" callret_size=", size);
  field(" lower_guard=", base >= kRequiredPageSize ? base - kRequiredPageSize : 0);
  field(" upper_guard=", base + size);
  field(" reset=", base + size / 4);
  field(" guard_match=", guard_match);
  if (thread->CurrentFrame) {
    field(" callret_saved=", thread->CurrentFrame->State.callret_sp);
    // State.rip can be the last HLE syscall boundary, not the instruction
    // corresponding to the current JIT host PC. Preserve that distinction.
    field(" saved_guest_rip=", thread->CurrentFrame->State.rip);
    field(" saved_guest_rsp=", thread->CurrentFrame->State.gregs[FEXCore::X86State::REG_RSP]);
  }
  buffer[used++] = '\n';
  const int saved_errno = errno;
  const auto written = ::write(STDERR_FILENO, buffer, used);
  (void)written; // Best effort in a signal handler; consume fortified libc's result.
  errno = saved_errno;
}
#endif
} // namespace

void ReportGuestFaultEvidence(int signal, siginfo_t* info, void* rawContext) noexcept {
#if defined(__aarch64__)
  WriteFexFaultEvidence("BACHATA_FEX_UNHANDLED_FAULT_EVIDENCE", signal, info, rawContext);
#else
  static_cast<void>(signal);
  static_cast<void>(info);
  static_cast<void>(rawContext);
#endif
}

bool HandleGuestSignal(int signal, siginfo_t* info, void* rawContext) noexcept {''',
    )
    edit(
        fex,
        """  if (!ActiveFexExecution.Context->IsAddressInCodeBuffer(ActiveFexExecution.Thread, pc)) {
    return false;
  }

  auto* registers = reinterpret_cast<std::uint64_t*>(context->uc_mcontext.regs);""",
        """  const bool in_jit = ActiveFexExecution.Context->IsAddressInCodeBuffer(
      ActiveFexExecution.Thread, pc);
  const auto& config = ActiveFexExecution.SignalDelegator->GetConfig();
  const bool in_dispatcher = pc >= config.DispatcherBegin && pc < config.DispatcherEnd;
  // FEX's callback dispatcher also pushes [x25,#-16]!, but is intentionally
  // outside IsAddressInCodeBuffer. Only the strict SIGSEGV guard path may
  // handle it; BUS_ADRALN recovery keeps its original JIT-only restriction.
  if (!in_jit && !(signal == SIGSEGV && in_dispatcher)) return false;

  auto* registers = reinterpret_cast<std::uint64_t*>(context->uc_mcontext.regs);""",
    )
    edit(
        fex,
        """    const auto reset=base+size/4;
    // The branch target cache is optional.""",
        """    ++FexCallRetRecoveries;
    // First recovery and powers of two retain frequency evidence without
    // logging every fault. Record the original x25 before repairing it.
    if ((FexCallRetRecoveries & (FexCallRetRecoveries - 1)) == 0)
      WriteFexFaultEvidence("BACHATA_FEX_CALLRET_GUARD_RECOVERED", signal, info, rawContext);
    const auto reset=base+size/4;
    // The branch target cache is optional.""",
    )
    edit(
        fex,
        """    static thread_local bool logged=false;
    if(!logged) {
      logged=true;
      constexpr char message[]=\"BACHATA_FEX_CALLRET_GUARD_RECOVERED\\n\";
      (void)::write(STDERR_FILENO,message,sizeof(message)-1);
    }
""",
        "",
    )
    edit(
        signals,
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
            uint64_t guest_rip = 0;""",
        """#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
            ::Core::Fex::ReportGuestFaultEvidence(sig, info, raw_context);
            uint64_t guest_rip = 0;""",
    )
    return {
        "fex_guard": "pinned JIT and callback dispatcher, strict x25 opcode/address/SP predicate",
        "fault_evidence": "fatal faults and logarithmic guard recovery counts; no arbitrary recovery",
        "guest_rip": "explicitly labelled saved HLE-boundary state",
    }
