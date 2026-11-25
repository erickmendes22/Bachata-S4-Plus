"""Align PS4 kernel TSC APIs with the retained FEX RDTSC/RDTSCP clock.

FEX f2b679f6 Core.cpp scales low-frequency ARM counters by default while
the previous HLE exposed unscaled CNTVCT and its frequency. Mixed HLE/RDTSC
timers therefore ran up to 64 times too fast. Keep FEX's policy and derive
the actual scale from its CPUID contract after context initialization.
"""
from pathlib import Path
import shutil


def apply(root):
    root = Path(root)

    def edit(name, old, new):
        p = root / name
        text = p.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"FEX clock source drift {name}: {old[:100]!r}")
        p.write_text(text.replace(old, new, 1))

    shutil.copyfile(Path(__file__).with_name("guest_tsc_clock.h"),
                    root / "src/core/fex/guest_tsc_clock.h")
    engine = "src/core/fex/fex_guest_engine.cpp"
    edit(engine, '#include "fex_guest_engine.h"',
         '#include "fex_guest_engine.h"\n#include "guest_tsc_clock.h"')
    edit(engine, '''  if (!impl->Context->InitCore()) {
    return fail(Failure(EngineStage::Context, EIO));
  }
''', '''  if (!impl->Context->InitCore()) {
    return fail(Failure(EngineStage::Context, EIO));
  }
#if defined(__aarch64__)
  const auto tsc = impl->Context->RunCPUIDFunction(0x15, 0);
  if (!guest_tsc_clock.Configure(tsc.eax, tsc.ebx, tsc.ecx)) {
    return fail(Failure(EngineStage::Context, EPROTO));
  }
  std::fprintf(stderr,
      "BACHATA_FEX_TSC_ALIGNED crystal_hz=%u numerator=%u denominator=%u guest_hz=%llu\\n",
      tsc.ecx, tsc.ebx, tsc.eax,
      static_cast<unsigned long long>(guest_tsc_clock.Frequency(0)));
#endif
''')

    time = "src/core/libraries/kernel/time.cpp"
    edit(time, '#include "common/native_clock.h"', '''#include "common/native_clock.h"
#if defined(SHADPS4_ENABLE_FEX_GUEST_CPU) && defined(__aarch64__)
#include "core/fex/guest_tsc_clock.h"
#endif''')
    edit(time, '''static std::unique_ptr<Common::NativeClock> clock;
''', '''static std::unique_ptr<Common::NativeClock> clock;

static u64 GuestTscFrequency(u64 fallback) {
#if defined(SHADPS4_ENABLE_FEX_GUEST_CPU) && defined(__aarch64__)
    return Core::Fex::guest_tsc_clock.Frequency(fallback);
#else
    return fallback;
#endif
}

static u64 GuestTscTicks(u64 ticks) {
#if defined(SHADPS4_ENABLE_FEX_GUEST_CPU) && defined(__aarch64__)
    return Core::Fex::guest_tsc_clock.Ticks(ticks);
#else
    return ticks;
#endif
}
''')
    edit(time, '    return clock ? clock->GetTscFrequency() : 0;',
         '    return clock ? GuestTscFrequency(clock->GetTscFrequency()) : 0;')
    edit(time, '    return clock ? clock->GetUptime() - initial_ptc : 0;',
         '    return clock ? GuestTscTicks(clock->GetUptime() - initial_ptc) : 0;')
    edit(time, '    return clock ? clock->GetTscFrequency() : 1;',
         '    return clock ? GuestTscFrequency(clock->GetTscFrequency()) : 1;')
    edit(time, '    return clock ? clock->GetUptime() : 0;',
         '    return clock ? GuestTscTicks(clock->GetUptime()) : 0;')
    # Kernel microsecond/nanosecond clocks retain wall-clock units. On ARM
    # there is no reason to estimate and round a discoverable exact frequency.
    edit("src/common/rdtsc.cpp", 'u64 EstimateRDTSCFrequency() {', '''u64 EstimateRDTSCFrequency() {
#if defined(ARCH_ARM64) && !defined(_MSC_VER)
    u64 architectural_frequency;
    asm volatile("mrs %0, cntfrq_el0" : "=r"(architectural_frequency));
    if (architectural_frequency) return architectural_frequency;
#endif''')
    return {"fexRevision": "f2b679f6028ce1c38875233aecfcf5d3f8ebecec",
            "tsc": "FEX CPUID 0x15 ratio shared by kernel raw counter APIs",
            "wallClock": "unchanged units; exact ARM CNTFRQ calibration",
            "cpuBackend": "FEX"}
