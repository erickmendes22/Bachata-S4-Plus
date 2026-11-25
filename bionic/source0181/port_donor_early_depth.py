"""Preserve SotC's depth-before-storage-write semantics and pipeline specialization."""
from pathlib import Path
import re


def apply(root: Path):
    root = Path(root)
    def edit(rel, old, new):
        p = root / rel
        source = p.read_text()
        if source.count(old) != 1:
            raise RuntimeError(f"SotC early depth anchor drift: {rel}: {old[:90]}")
        p.write_text(source.replace(old, new, 1))

    include = 'shader_recompiler/donor_early_depth.h'
    (root / 'src' / include).write_text(Path(__file__).with_name('donor_early_depth.h').read_text())
    info = 'src/shader_recompiler/runtime_info.h'
    edit(info, '    bool clip_distance_emulation{false};',
         '    bool clip_distance_emulation{false};\n    bool early_fragment_tests{false};')
    edit(info, '               clip_distance_emulation == other.clip_distance_emulation &&',
         '               clip_distance_emulation == other.clip_distance_emulation &&\n'
         '               early_fragment_tests == other.early_fragment_tests &&')
    cache = 'src/video_core/renderer_vulkan/vk_pipeline_cache.cpp'
    emit = 'src/shader_recompiler/backend/spirv/emit_spirv.cpp'
    for file in (cache, emit):
        p = root / file
        p.write_text('#include "' + include + '"\n' + p.read_text())
    edit(cache, '        const auto& cb0_blend = regs.blend_control[0];', '''        // SotC deferred decals write storage images: failing early-depth fragments must
        // not execute those writes. Preserve the donor's title and export guards.
        static const bool donor_early_depth = [] {
            const char* value = std::getenv("SOTC_EARLY_Z");
            const auto serial = Common::ElfInfo::Instance().GameSerial();
            return value ? std::atoi(value) != 0 :
                (serial == "CUSA08809" || serial == "CUSA08034");
        }();
        info.hw.fs.early_fragment_tests = Shader::DonorEarlyDepth::RegisterPolicy(
            donor_early_depth, static_cast<u32>(regs.depth_shader_control.z_order),
            info.hw.fs.mrtz_mask);
        const auto& cb0_blend = regs.blend_control[0];''')
    edit(emit, '''        if (info.stores.GetAny(IR::Attribute::Depth)) {
            ctx.AddExecutionMode(main, spv::ExecutionMode::DepthReplacing);
        }
        break;''', '''        if (info.stores.GetAny(IR::Attribute::Depth)) {
            ctx.AddExecutionMode(main, spv::ExecutionMode::DepthReplacing);
        }
        if (DonorEarlyDepth::ShaderPolicy(ctx.runtime_info.hw.fs.early_fragment_tests,
                info.has_storage_images, info.has_discard,
                info.stores.GetAny(IR::Attribute::Depth),
                info.stores.Get(IR::Attribute::StencilRef),
                info.stores.Get(IR::Attribute::SampleMask))) {
            ctx.AddExecutionMode(main, spv::ExecutionMode::EarlyFragmentTests);
        }
        break;''')
    directory = root / 'src/video_core/renderer_vulkan'
    p = directory / 'vk_pipeline_serialization.cpp'
    source = p.read_text()
    for name in ('ShaderMetaVersion', 'ShaderBinaryVersion'):
        source, count = re.subn(rf'({name} = )(\d+)(u;)',
            lambda m: m[1] + str(int(m[2]) + 1) + m[3], source)
        if count != 1:
            raise RuntimeError('Early depth cache ABI drift: ' + name)
    p.write_text(source)
    live = directory / 'order_live_pso_cache.h'
    if live.exists():
        versions = '-'.join(re.search(rf'{name} = (\d+)u;', source)[1] for name in
                           ('ShaderMetaVersion', 'ShaderBinaryVersion', 'PipelineKeyVersion'))
        s, count = re.subn(r'live-pso-v1-\d+-\d+-\d+', 'live-pso-v1-' + versions, live.read_text())
        if count != 1:
            raise RuntimeError('Early depth live PSO cache ABI drift')
        live.write_text(s)
    return {'donor': 'SotC PC 732cb37d3470 effective renderer',
            'registerPolicy': 'SotC early Z, no depth/stencil/sample-mask export',
            'shaderPolicy': 'storage images, no discard or depth/stencil/sample-mask writes',
            'cache': 'runtime equality, serialized metadata and binary versions updated',
            'optionalLodFeedback': 'not enabled; donor default remains off'}
