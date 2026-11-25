#!/usr/bin/env python3
"""Exercise production clock conversion with the pinned FEX CPUID contract."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument("--source", required=True, type=Path)
a = p.parse_args()
source = a.source.resolve() / "src"
code = r'''
#include "core/fex/guest_tsc_clock.h"
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>

int main() {
    Core::Fex::GuestTscClock clock;
    assert(clock.Frequency(123)==123 && clock.Ticks(77)==77);
    unsigned cases=0;
    // Real ARM crystal rates, an unscaled high-frequency host, and both
    // SMALLTSCSCALE settings. Formula matches pinned FEX Core/CPUID/IR.
    for (std::uint32_t crystal : {19200000u, 24000000u, 24576000u,
                                  100000000u, 1000000000u, 2400000000u}) {
        for (bool scale : {false, true}) {
            unsigned shift=0;
            while (scale && (std::uint64_t{crystal} << shift) < 1000000000u) ++shift;
            assert(clock.Configure(1, 1u << shift, crystal));
            const auto guest_hz=std::uint64_t{crystal} << shift;
            assert(clock.Frequency(0)==guest_hz);
            for (std::uint64_t raw : {std::uint64_t{0}, std::uint64_t{1},
                                      std::uint64_t{crystal}*1234567,
                                      std::numeric_limits<std::uint64_t>::max()-7}) {
                assert(clock.Ticks(raw)==(raw << shift));
                // Mixing HLE sceKernelReadTsc with guest RDTSC must give
                // the same delta and elapsed seconds as two guest reads.
                const auto before=clock.Ticks(raw);
                const auto after=(raw+crystal*3ull) << shift;
                assert(after-before==guest_hz*3);
                assert((after-before)/clock.Frequency(0)==3);
                ++cases;
            }
            const auto prior=clock.Frequency(0);
            assert(!clock.Configure(0,1,crystal));
            assert(!clock.Configure(1,0,crystal));
            assert(!clock.Configure(1,3,crystal));
            assert(!clock.Configure(1,1,0));
            assert(clock.Frequency(0)==prior);
        }
    }
    std::cout << "BACHATA_FEX_KERNEL_RDTSC_CLOCK_PASS cases=" << cases << '\n';
}
'''
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "clock.cpp").write_text(code)
    subprocess.run(["c++", "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-I", str(source), str(d / "clock.cpp"), "-o", str(d / "clock")], check=True)
    subprocess.run([str(d / "clock")], check=True)
