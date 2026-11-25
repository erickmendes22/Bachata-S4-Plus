#!/usr/bin/env python3
"""Exhaust the hardware-order/export and SPIR-V side-effect guards used by the core."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument('--source', required=True)
args = p.parse_args()
src = Path(args.source).resolve() / 'src'
header = src / 'shader_recompiler/donor_early_depth.h'
assert header.exists()
runtime = (src / 'shader_recompiler/runtime_info.h').read_text()
assert 'early_fragment_tests == other.early_fragment_tests' in runtime
cache = (src / 'video_core/renderer_vulkan/vk_pipeline_cache.cpp').read_text()
assert 'Shader::DonorEarlyDepth::RegisterPolicy(' in cache
emit = (src / 'shader_recompiler/backend/spirv/emit_spirv.cpp').read_text()
assert 'DonorEarlyDepth::ShaderPolicy(' in emit
assert 'spv::ExecutionMode::EarlyFragmentTests' in emit

code = r'''
#include <cassert>
#include <iostream>
#include "shader_recompiler/donor_early_depth.h"
int main() {
    using namespace Shader::DonorEarlyDepth;
    unsigned cases = 0;
    // GCN Z_ORDER: 0 late; 1 early+late; 2 re-Z; 3 early+re-Z.
    constexpr bool before_pixel[4] = {false, true, false, true};
    for (unsigned enabled = 0; enabled < 2; ++enabled) {
        for (unsigned z = 0; z < 4; ++z) {
            for (unsigned outputs = 0; outputs < 16; ++outputs) {
                const bool no_export = (outputs == 0 || outputs == 8);
                const bool requested = enabled && before_pixel[z] && no_export;
                assert(RegisterPolicy(enabled, z, outputs) == requested);
                for (unsigned effects = 0; effects < 32; ++effects) {
                    const bool actual = ShaderPolicy(RegisterPolicy(enabled, z, outputs),
                        effects & 1, effects & 2, effects & 4, effects & 8, effects & 16);
                    // Only storage writes alone can force early tests without changing discard
                    // or shader-exported depth, stencil and coverage semantics.
                    assert(actual == (requested && effects == 1));
                    ++cases;
                }
            }
        }
    }
    std::cout << "BACHATA_DONOR_EARLY_DEPTH_PASS cases=" << cases << '\n';
}
'''
with tempfile.TemporaryDirectory() as d:
    cpp = Path(d) / 'depth.cpp'
    exe = Path(d) / 'depth'
    cpp.write_text(code)
    subprocess.run(['c++', '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-I', str(src), str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True, timeout=10)
