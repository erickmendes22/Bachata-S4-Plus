#!/usr/bin/env python3
"""Port The Order 1886's pre-resource-patching SRT synchronization to shadPS4 0.18.1.

Source reference:
 erickmendes22/gow3_android_daedalus_fork
 fix/order1886-adreno830-pervertex-interpolation@524e74a3b3a67135e02a1b7e68d2b83359da9e96
 the-order-1886-android/overlay/gpu/shadps4/video_core/renderer_vulkan/
   vk_pipeline_cache.cpp (TranslateProgram guest_reads_done)
   vk_rasterizer.cpp (pipeline_cache.SetSrtSync)

The prior Bionic port only read back SRT pages at BindResources, after
specialization and translation had already consumed potentially stale guest
descriptors. This patch also refreshes the same pages at the exact IR barrier
between FlattenExtendedUserdataPass and ResourcePatchingPass, and before a
cached shader chooses its specialization. Uses the existing verified VMM-aware
SRT walker/readback rather than copying the port's older x86 Xbyak engine.
"""
from pathlib import Path

def only(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"The Order SRT source drift at {label}: {count} anchors")
    return text.replace(old, new, 1)

def apply(root: Path) -> dict:
    re_h = root / "src/shader_recompiler/recompiler.h"
    re_c = root / "src/shader_recompiler/recompiler.cpp"
    pc_h = root / "src/video_core/renderer_vulkan/vk_pipeline_cache.h"
    pc_c = root / "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    raster = root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    data = {p: p.read_text() for p in (re_h, re_c, pc_h, pc_c, raster)}
    if "BACHATA_RELEASE026_SRT_GPU_PAGE_READBACK" not in data[raster]:
        raise RuntimeError("Must port Release SRT GPU page readback before pre-compile sync")
    data[re_h] = only(data[re_h], '#include "common/object_pool.h"',
        '#include <functional>\n#include "common/object_pool.h"', "IR callback include")
    data[re_h] = only(data[re_h],
        'const Profile& profile);',
        'const Profile& profile,\n'
        '                                            const std::function<void()>& guest_reads_done = {});',
        "IR guest read callback declaration")
    # The 0.18.1 graft and FEX core may format the signature differently.
    # Match the unique function declaration, never an unrelated Profile use.
    import re
    expr = r'(IR::Program\\s+TranslateProgram\\s*\\([^{};]*?)\\)\\s*\\{'
    matches = list(re.finditer(expr, data[re_c]))
    if len(matches) != 1:
        raise RuntimeError(
            f"The Order SRT drift: expected unique TranslateProgram definition, found {len(matches)}")
    found = matches[0]
    if 'const Profile& profile' not in found.group(1):
        raise RuntimeError("Unexpected TranslateProgram ABI: missing Profile")
    data[re_c] = (data[re_c][:found.start()] + found.group(1) +
                  ', const std::function<void()>& guest_reads_done) {' +
                  data[re_c][found.end():])
    data[re_c] = only(data[re_c],
        '    Shader::Optimization::FlattenExtendedUserdataPass(program, resources, profile);\n'
        '    Shader::IR::DumpProgram(program, info, "pre-res-patch.");',
        '    Shader::Optimization::FlattenExtendedUserdataPass(program, resources, profile);\n'
        '    // BACHATA_ORDER1886_PRE_RESOURCE_SRT_SYNC: the flattened SRT guest\n'
        '    // sources exist here, but ResourcePatchingPass has not yet captured\n'
        '    // any descriptor. Publish GPU writes before consuming them.\n'
        '    if (guest_reads_done) guest_reads_done();\n'
        '    Shader::IR::DumpProgram(program, info, "pre-res-patch.");',
        "IR pre-resource patch SRT barrier")
    data[pc_h] = only(data[pc_h], '#include <variant>',
        '#include <functional>\n#include <variant>', "pipeline callback include")
    data[pc_h] = only(data[pc_h],
        '    void Sync();\n',
        '    void Sync();\n'
        '    // The Order source: synchronize mutable guest SRT pages on the GPU\n'
        '    // thread before shader specialization and resource lowering.\n'
        '    void SetSrtSync(std::function<void(Shader::Info&)> callback) {\n'
        '        srt_sync = std::move(callback);\n'
        '    }\n',
        "pipeline SRT callback setter")
    data[pc_h] = only(data[pc_h],
        '    Shader::Profile profile{};\n',
        '    Shader::Profile profile{};\n'
        '    std::function<void(Shader::Info&)> srt_sync;\n',
        "pipeline SRT callback state")
    data[pc_c] = only(data[pc_c],
        '    const auto ir_program = Shader::TranslateProgram(code, pools, info, runtime_info, profile);',
        '    const auto ir_program = Shader::TranslateProgram(\n'
        '        code, pools, info, runtime_info, profile,\n'
        '        [this, &info] { if (srt_sync) srt_sync(info); });',
        "call after flatten IR before resource lowering")
    data[pc_c] = only(data[pc_c],
        '    info.RefreshFlatBuf();\n    auto spec = Shader::StageSpecialization(info, runtime_info, profile, binding);',
        '    info.RefreshFlatBuf();\n'
        '    if (srt_sync) srt_sync(info); // Refresh GPU-written sources before cache permutation.\n'
        '    auto spec = Shader::StageSpecialization(info, runtime_info, profile, binding);',
        "already-compiled shader specialization barrier")
    data[raster] = only(data[raster],
        '       guest_markers_enabled{EmulatorSettings.IsVkGuestMarkersEnabled()} {\n',
        '       guest_markers_enabled{EmulatorSettings.IsVkGuestMarkersEnabled()} {\n'
        '    pipeline_cache.SetSrtSync([this](Shader::Info& info) {\n'
        '        ReadBackGpuWrittenSrtSources(info);\n'
        '    });\n',
        "registered callback before GPU thread starts")
    for p, content in data.items():
        p.write_text(content)
    return {
        "reference": "The Order Android 524e74a3b3 vk_pipeline_cache.cpp",
        "implemented": "SRT GPU page readback during TranslateProgram and cached specialization",
        "preserved": "shadPS4 0.18.1 portable ARM64 walker and shader metadata ABI",
        "notClaimed": "nonuniform ReadLane/Phi SRT indices or full Release ARM64 emitter fixed",
    }
