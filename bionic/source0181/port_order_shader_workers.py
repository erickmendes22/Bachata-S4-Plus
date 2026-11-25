"""Adapt donor shader compile worker capture to shadPS4 0.18.1 FEX.

Guest-dependent IR translation/SRT synchronization remains on the command
thread. SPIR-V emission and VkShaderModule creation use immutable captures
on bounded reusable workers. Publish all stages before consuming the draw;
never execute a draw with a missing stage or suppress a compute dispatch.
"""
from pathlib import Path
import re

def apply(root: Path):
    def edit(rel, old, new):
        p=root/"src"/rel
        s=p.read_text()
        if s.count(old)!=1:
            raise RuntimeError("Shader worker parity source drift "+rel+": "+old[:100])
        p.write_text(s.replace(old,new,1))
    sp="shader_recompiler/backend/spirv/"
    v="video_core/renderer_vulkan/"
    edit(sp+"emit_spirv.h",'#include "shader_recompiler/ir/program.h"',
         '#include "shader_recompiler/ir/program.h"\n#include "shader_recompiler/frontend/fetch_shader.h"')
    edit(sp+"emit_spirv.h","[[nodiscard]] std::vector<u32> EmitSPIRV(",
         """// Immutable values captured before the guest can reuse the descriptor memory.
struct EmissionSnapshot {
    bool has_fetch{};
    Gcn::FetchShaderData fetch;
    std::vector<AmdGpu::Buffer> vertex, buffers;
    std::vector<AmdGpu::Image> images;
    explicit EmissionSnapshot(const Info& info);
};

[[nodiscard]] std::vector<u32> EmitSPIRV(""")
    edit(sp+"emit_spirv.h","const IR::Program& program, Bindings& binding);",
         "const IR::Program& program, Bindings& binding,\n                                         const EmissionSnapshot* snapshot = nullptr);")
    edit(sp+"spirv_emit_context.h","class EmitContext final",
         "struct EmissionSnapshot;\n\nclass EmitContext final")
    edit(sp+"spirv_emit_context.h","                         Bindings& binding);",
         "                         Bindings& binding, const EmissionSnapshot* snapshot = nullptr);")
    edit(sp+"spirv_emit_context.h","    Info& info;",
         "    Info& info;\n    const EmissionSnapshot* snapshot;")
    edit(sp+"spirv_emit_context.cpp",'#include "shader_recompiler/backend/spirv/spirv_emit_context.h"',
         '#include "shader_recompiler/backend/spirv/spirv_emit_context.h"\n#include "shader_recompiler/backend/spirv/emit_spirv.h"')
    edit(sp+"spirv_emit_context.cpp",
         """                         Bindings& binding_)
    : Sirit::Module(profile_.supported_spirv), info{info_}, runtime_info{runtime_info_},""",
         """                         Bindings& binding_, const EmissionSnapshot* snapshot_)
    : Sirit::Module(profile_.supported_spirv), info{info_}, snapshot{snapshot_}, runtime_info{runtime_info_},""")
    edit(sp+"spirv_emit_context.cpp",
         """        if (!Gcn::ParseFetchShader(info, fetch_shader)) {
            break;
        }""",
         """        if (snapshot) {
            if (!snapshot->has_fetch) break;
            fetch_shader = snapshot->fetch;
        } else if (!Gcn::ParseFetchShader(info, fetch_shader)) {
            break;
        }""")
    edit(sp+"spirv_emit_context.cpp","            const auto sharp = attrib.GetSharp(info);",
         "            const auto sharp = snapshot ? snapshot->vertex.at(semantic) : attrib.GetSharp(info);")
    edit(sp+"spirv_emit_context.cpp","        const auto buf_sharp = desc.GetSharp(info);",
         "        const auto buf_sharp = snapshot ? snapshot->buffers.at(buffers.size()) : desc.GetSharp(info);")
    edit(sp+"spirv_emit_context.cpp",
         """Id ImageType(EmitContext& ctx, const ImageResource& desc, Id sampled_type) {
    const auto image = desc.GetSharp(ctx.info);""",
         """Id ImageType(EmitContext& ctx, const ImageResource& desc, Id sampled_type,
             const AmdGpu::Image& image) {""")
    edit(sp+"spirv_emit_context.cpp","        const auto sharp = image_desc.GetSharp(info);",
         "        const auto sharp = snapshot ? snapshot->images.at(images.size()) : image_desc.GetSharp(info);")
    edit(sp+"spirv_emit_context.cpp","ImageType(*this, image_desc, sampled_type)",
         "ImageType(*this, image_desc, sampled_type, sharp)")
    edit(sp+"emit_spirv.cpp",
         """std::vector<u32> EmitSPIRV(const Profile& profile, const RuntimeInfo& runtime_info,
                           const IR::Program& program, Bindings& binding) {
    EmitContext ctx{profile, runtime_info, program.info, binding};""",
         """EmissionSnapshot::EmissionSnapshot(const Info& info) {
    if (info.sw_stage == SwStage::Vertex) {
        has_fetch = Gcn::ParseFetchShader(info, fetch);
        if (has_fetch)
            for (const auto& attr : fetch.attributes) vertex.push_back(attr.GetSharp(info));
    }
    for (const auto& desc : info.buffers) buffers.push_back(desc.GetSharp(info));
    for (const auto& desc : info.images) images.push_back(desc.GetSharp(info));
}

std::vector<u32> EmitSPIRV(const Profile& profile, const RuntimeInfo& runtime_info,
                           const IR::Program& program, Bindings& binding,
                           const EmissionSnapshot* snapshot) {
    EmitContext ctx{profile, runtime_info, program.info, binding, snapshot};""")
    # Descriptor presence bits must cover every possible resource, not just 128.
    # Do not import donor's older push-constant layout or remove the current
    # per-variant resource cardinality checks.
    edit("shader_recompiler/specialization.h",
         "    static constexpr size_t MaxStageResources = 128;",
         "    static constexpr size_t MaxStageResources = NUM_BUFFERS + NUM_IMAGES + NUM_FMASKS + NUM_SAMPLERS;")
    edit("shader_recompiler/specialization.h","            bitset[binding++] = true;",
         "            bitset.set(binding++);")
    edit("shader_recompiler/specialization.h","        if (!Valid()) {",
         "        if (!Valid() || !other.Valid() || fmasks.size() != other.fmasks.size()) {")
    edit("shader_recompiler/specialization.h",
         "if (buffers.empty() && images.empty() && samplers.empty())",
         "if (buffers.empty() && images.empty() && fmasks.empty() && samplers.empty() &&\n            other.buffers.empty() && other.images.empty() && other.fmasks.empty() && other.samplers.empty())")
    ps=root/"src"/v/"vk_pipeline_serialization.cpp"
    txt=ps.read_text()
    txt,n=re.subn(r"ShaderMetaVersion = (\d+)u;",lambda m:f"ShaderMetaVersion = {int(m[1])+1}u;",txt)
    assert n==1
    ps.write_text(txt)
    # Worker queue is bounded by shader-stage count. It lives with PipelineCache;
    # join before destroying the shader cache or Vulkan device.
    (root/"src"/v/"bachata_shader_workers.h").write_text("""// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <condition_variable>
#include <deque>
#include <functional>
#include <future>
#include <mutex>
#include <thread>
#include <vector>
#include <memory>
#include <stdexcept>

namespace Vulkan {
class BachataShaderWorkers {
public:
    explicit BachataShaderWorkers(unsigned count) {
        for (unsigned i=0;i<count;++i) threads.emplace_back([this] {
            for (;;) {
                std::function<void()> work;
                {
                    std::unique_lock lk{mutex};
                    cv.wait(lk,[this]{return stop || !tasks.empty();});
                    if (tasks.empty()) return;
                    work=std::move(tasks.front());
                    tasks.pop_front();
                }
                work();
            }
        });
    }
    ~BachataShaderWorkers() {
        {
            std::scoped_lock lk{mutex};
            stop=true;
        }
        cv.notify_all();
        for (auto& t:threads) t.join();
    }
    template<class F> auto Submit(F&& f) {
        using T=std::invoke_result_t<F>;
        auto job=std::make_shared<std::packaged_task<T()>>(std::forward<F>(f));
        auto future=job->get_future();
        {
            std::scoped_lock lk{mutex};
            if (stop) throw std::runtime_error("shader workers stopped");
            tasks.emplace_back([job]{(*job)();});
        }
        cv.notify_one();
        return future;
    }
private:
    std::mutex mutex;
    std::condition_variable cv;
    bool stop{};
    std::deque<std::function<void()>> tasks;
    std::vector<std::thread> threads;
};
}
""")
    h=v+"vk_pipeline_cache.h";cpp=v+"vk_pipeline_cache.cpp"
    edit(h,'#include <functional>','#include <functional>\n#include "video_core/renderer_vulkan/bachata_shader_workers.h"')
    edit(h,"    Shader::Pools pools;",
         """    Shader::Pools pools;
    struct PendingShader {
        u64 hash;
        size_t permutation;
        std::future<std::pair<vk::ShaderModule,std::vector<u32>>> future;
    };
    std::unique_ptr<BachataShaderWorkers> shader_workers;
    std::vector<PendingShader> pending_shaders;
    void PublishPendingShaders();
    vk::ShaderModule QueueCapturedShader(Shader::Info& info, Shader::RuntimeInfo& runtime,
                                         const std::span<const u32>& code, size_t permutation,
                                         Shader::Backend::Bindings& binding);""")
    edit(cpp,"PipelineCache::~PipelineCache() {",
         """PipelineCache::~PipelineCache() {
    PublishPendingShaders();
    shader_workers.reset();""")
    edit(cpp,"    if (!RefreshGraphicsKey()) {\n        return nullptr;\n    }",
         """    const bool key_valid=RefreshGraphicsKey();
    PublishPendingShaders(); // all stages must exist before any draw uses the key
    if (!key_valid) return nullptr;""")
    edit(cpp,"    const auto ir_program = Shader::TranslateProgram(",
         """    // Capture guest-facing inputs on the original GPU command thread.
    // Only SPIR-V emission and Vulkan module creation run on workers.
    if (AmdGpu::BachataOrderNoMsaa() && info.sw_stage != SwStage::Compute &&
        !EmulatorSettings.IsShaderCollect()) {
        return QueueCapturedShader(info,runtime_info,code,perm_idx,binding);
    }
    const auto ir_program = Shader::TranslateProgram(""")
    edit(cpp,"PipelineCache::Result PipelineCache::GetProgram(",
         """vk::ShaderModule PipelineCache::QueueCapturedShader(
    Shader::Info& info, Shader::RuntimeInfo& runtime, const std::span<const u32>& code,
    size_t permutation, Shader::Backend::Bindings& binding) {
    using namespace Shader::Backend::SPIRV;
    struct Build {
        Shader::Info info;
        Shader::RuntimeInfo runtime;
        Shader::Pools pools;
        std::optional<Shader::IR::Program> ir;
        std::optional<EmissionSnapshot> captured;
        std::optional<std::vector<u32>> patch;
        Shader::Backend::Bindings begin, end;
    };
    auto build=std::make_shared<Build>();
    build->info=info;
    build->runtime=runtime;
    build->begin=binding;
    build->ir.emplace(Shader::TranslateProgram(code,build->pools,build->info,
        build->runtime,profile,[this,build]{if(srt_sync)srt_sync(build->info);}));
    for(auto& image:build->info.images)
        image.compiled_binding_count=image.LiveNumBindings(build->info);
    build->captured.emplace(build->info);
    // Metadata and binding allocation are finalized before worker submission.
    // Subsequent stages can translate concurrently with this one's emission.
    info=build->info;
    runtime=build->runtime;
    info.AddBindings(binding);
    build->end=binding;
    if (EmulatorSettings.IsPatchShaders())
        build->patch=GetShaderPatch(info.pgm_hash,info.hw_stage,permutation,"spv");
    if (!shader_workers)
        shader_workers=std::make_unique<BachataShaderWorkers>(2);
    const auto hash=info.pgm_hash;
    // Drop borrowed guest-facing pointers: emission uses the immutable capture.
    build->info.user_data={};
    build->info.params.reset();
    auto result=shader_workers->Submit([this,build] {
        auto b=build->begin;
        auto spv=EmitSPIRV(profile,build->runtime,*build->ir,b,&*build->captured);
        ASSERT_MSG(b==build->end,"captured shader binding contract mismatch");
        auto module=CompileSPV(build->patch ? std::span<const u32>(*build->patch) :
                              std::span<const u32>(spv),instance.GetDevice());
        return std::make_pair(module,std::move(spv));
    });
    pending_shaders.push_back({hash,permutation,std::move(result)});
    return {}; // published before graphics pipeline selection
}

void PipelineCache::PublishPendingShaders() {
    for (auto& job:pending_shaders) {
        auto [module,spv]=job.future.get();
        auto it=program_cache.find(job.hash);
        ASSERT(it!=program_cache.end());
        auto& entry=it.value()->modules.at(job.permutation);
        ASSERT(!entry.module && entry.effective_info);
        entry.module=module;
        auto* effective=entry.effective_info.get();
        DumpShader(spv,job.hash,effective->hw_stage,job.permutation,"spv");
        RegisterShaderBinary(std::move(spv),job.hash,job.permutation);
        Vulkan::SetObjectName(instance.GetDevice(),module,
            GetShaderName(effective->hw_stage,job.hash,job.permutation));
        for (size_t i=0;i<infos.size();++i) {
            if (infos[i]==effective) modules[i]=module;
        }
    }
    pending_shaders.clear();
}

PipelineCache::Result PipelineCache::GetProgram(""")
    edit(cpp,"    auto runtime_info = BuildRuntimeInfo(hw_stage, sw_stage);",
         """    // A program hash may be requested again within the same draw.
    // Complete its pending entries rather than create duplicate permutations.
    if (std::ranges::any_of(pending_shaders,[&](const auto& p){return p.hash==params.hash;}))
        PublishPendingShaders();
    auto runtime_info = BuildRuntimeInfo(hw_stage, sw_stage);""")
    return {"worker":"two reusable SPIR-V/VkShaderModule workers with immutable fetch/buffer/image capture",
            "ordering":"join at graphics selection; no skipped draw, compute unchanged",
            "cache":"publish original per-variant Info and existing serial database on GPU thread",
            "remaining":"inter-draw preparation, parallel graphics pipeline creation, deferred GPU writes"}
