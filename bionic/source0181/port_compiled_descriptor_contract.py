#!/usr/bin/env python3
"""Keep Vulkan shader resource contracts immutable after compilation.
Correct actual per-permutation metadata selection and the late SRT refresh.
Also mark the exact Vulkan phase of the reproducible 0x804aeead driver crash.
"""
from pathlib import Path
import re
def one(s,a,b,label):
    if s.count(a)!=1:
        raise RuntimeError(f"compiled resource contract drift {label}: {s.count(a)}")
    return s.replace(a,b,1)
def apply(root:Path):
    p=root/'src/shader_recompiler/resource.h'
    s=p.read_text()
    s=one(s,'    u16 array_stride_dw{};',
        '    u16 array_stride_dw{};\n    u32 compiled_binding_count{};', 'immutable image array size')
    s=one(s,'''    u32 NumBindings(const auto& info) const {
        if (array_size) return array_size+1u;''',
        '''    u32 NumBindings(const auto& info) const {
        return compiled_binding_count ? compiled_binding_count : LiveNumBindings(info);
    }
    u32 LiveNumBindings(const auto& info) const {
        if (array_size) return array_size+1u;''','separate live and compiled descriptor cardinality')
    p.write_text(s)
    p=root/'src/shader_recompiler/specialization.h'
    s=p.read_text()
    s=one(s,'                         spec.num_bindings = desc.NumBindings(*info);',
        '                         spec.num_bindings = desc.LiveNumBindings(*info);','compare live count')
    s=one(s,'        ForEachSharp(binding, fmasks, info->fmasks,',
        '''        // A null descriptor still consumes its compiled layout slots.
        for (size_t i=0;i<images.size();++i)
            images[i].num_bindings=info->images[i].LiveNumBindings(*info);
        ForEachSharp(binding, fmasks, info->fmasks,''','include null image array cardinality')
    s=one(s,'            if (other.bitset[binding++] && images[i] != other.images[i]) {',
        '''            if (images[i].num_bindings != other.images[i].num_bindings) return false;
            if (other.bitset[binding++] && images[i] != other.images[i]) {''','reject descriptor array mismatch even on nulls')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_cache.cpp'
    s=p.read_text()
    s=one(s,'    auto spv = Shader::Backend::SPIRV::EmitSPIRV(profile, runtime_info, ir_program, binding);',
        '''    // BACHATA_COMPILED_DESCRIPTOR_CONTRACT: freeze counts before SPIR-V
    // emission; the same Info feeds VkDescriptorSetLayout and BindTextures.
    for (auto& image:info.images) image.compiled_binding_count=image.LiveNumBindings(info);
    auto spv = Shader::Backend::SPIRV::EmitSPIRV(profile, runtime_info, ir_program, binding);''',
        'freeze counts on actual translated metadata')
    start=s.index('    auto& program = it_pgm.value();\n    auto& info = program->info;',s.index('PipelineCache::GetProgram('))
    end=s.index('\n}\n',start)
    s=s[:start]+'''    auto& program = it_pgm.value();
    auto& info = program->info;
    const auto start_binding = binding;
    // The first program's SRT layout is not the layout of every variant.
    // Refresh and specialize the actual candidate Info, not program->info.
    // The selected object remains stable for already-created pipelines.
    size_t perm_idx=program->modules.size();
    vk::ShaderModule module{};
    for (size_t i=0;i<program->modules.size();++i) {
        auto& candidate=program->modules[i];
        if (!candidate.module || !candidate.effective_info) continue;
        auto& effective=*candidate.effective_info;
        effective.pgm_base=params.Base();
        effective.user_data=params.user_data;
        effective.RefreshFlatBuf();
        if (srt_sync) srt_sync(effective);
        auto candidate_spec=Shader::StageSpecialization(effective,runtime_info,profile,start_binding);
        if (!(candidate.spec==candidate_spec)) continue;
        perm_idx=i;
        module=candidate.module;
        effective.AddBindings(binding);
        break;
    }
    if (!module) {
        auto new_info=std::make_unique<Shader::Info>(hw_stage,sw_stage,params);
        binding=start_binding;
        module=CompileModule(*new_info,runtime_info,params.code,perm_idx,binding);
        // Store the specialization of the shader that was actually emitted,
        // not a pre-translation snapshot of the first module.
        auto spec=Shader::StageSpecialization(*new_info,runtime_info,profile,start_binding);
        const u64 perm_hash=HashCombine(params.hash,perm_idx);
        RegisterShaderMeta(info,*new_info,spec.fetch_shader_data,spec,perm_hash,perm_idx);
        program->AddPermut(module,std::move(spec),std::move(new_info));
    }
    if (auto& fetch=program->modules[perm_idx].spec.fetch_shader_data; !fetch.Empty())
        fetch_shader=&fetch;
    return std::make_tuple(program->modules[perm_idx].effective_info.get(),module,
                           HashCombine(params.hash,perm_idx));'''+s[end:]
    # Preserve failing GCN and SPIR-V on disk even when general shader dumping is off.
    s=one(s,'    DumpShader(spv, info.pgm_hash, info.hw_stage, perm_idx, "spv");',
        '''    DumpShader(spv, info.pgm_hash, info.hw_stage, perm_idx, "spv");
    if (info.pgm_hash==0x804aeeadULL) {
        using namespace Common::FS;
        const auto dump_dir=GetUserPath(PathType::ShaderDir)/"dumps";
        std::filesystem::create_directories(dump_dir);
        const auto filename=GetShaderName(info.hw_stage,info.pgm_hash,perm_idx);
        IOFile{dump_dir/(filename+".bin"),FileAccessMode::Create}.WriteSpan(code);
        IOFile{dump_dir/(filename+".spv"),FileAccessMode::Create}.WriteSpan(std::span<const u32>{spv});
        LOG_INFO(Render_Vulkan,"BACHATA_ORDER_VARIANT_CONTRACT perm={} buffers={} images={} samplers={}",
                 perm_idx,info.buffers.size(),info.images.size(),info.samplers.size());
    }''','preserve exact shader if driver faults')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    s=p.read_text()
    s=one(s,'        ReadBackGpuWrittenSrtSources(*stage);\n        set_writes.resize(',
        '''        // SRT was synchronized before this exact permutation was selected.
        // Do not change its descriptors again after pipeline layout creation.
        set_writes.resize(''','remove post-specialization SRT mutation')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_compute_pipeline.cpp'
    s=p.read_text()
    s=one(s,'    auto [pipeline_result, pipe] =\n        instance.GetDevice().createComputePipelineUnique(pipeline_cache, compute_pipeline_ci);',
        '''    const bool trace_contract=info->pgm_hash==0x804aeeadULL;
    if (trace_contract) {
        LOG_INFO(Render_Vulkan,"BACHATA_ORDER_COMPUTE_CREATE_BEGIN descriptors={} slots={}",
                 bindings.size(),binding);
        for (const auto& b:bindings)
            LOG_INFO(Render_Vulkan,"BACHATA_ORDER_LAYOUT binding={} type={} count={}",
                     b.binding,static_cast<u32>(b.descriptorType),b.descriptorCount);
    }
    auto [pipeline_result, pipe] =
        instance.GetDevice().createComputePipelineUnique(pipeline_cache, compute_pipeline_ci);
    if (trace_contract)
        LOG_INFO(Render_Vulkan,"BACHATA_ORDER_COMPUTE_CREATE_END result={}",
                 vk::to_string(pipeline_result));''','locate crash inside or after actual Vulkan pipeline creation')
    p.write_text(s)
    p=root/'src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp'
    s=p.read_text()
    s=one(s,'ShaderMetaVersion = 16u;','ShaderMetaVersion = 17u;','layout ABI')
    s,n=re.subn(r'ShaderBinaryVersion = (\d+)u;',lambda m:f'ShaderBinaryVersion = {int(m.group(1))+1}u;',s)
    if n!=1: raise RuntimeError('shader binary version drift')
    p.write_text(s)
    return {"contract":"compiled descriptor counts, select via effective Info, no late SRT mutation",
            "capture":"only failing Order 0x804aeead exact SPIR-V/GCN and Vulkan pipeline creation boundaries"}
