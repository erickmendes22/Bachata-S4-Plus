"""Live-state PSO cache and Vulkan object lifetime for Order/FEX.
The exact donor uses VK_KHR_pipeline_binary. The reported Android driver
does not advertise that extension. Use isolated VkPipelineCache objects
instead; never deserialize a GraphicsPipeline or preload a saved draw state.
"""
from pathlib import Path
import re

def apply(root: Path):
    d=root/"src/video_core/renderer_vulkan"
    def edit(name,a,b,n=1):
        p=d/name;s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f"Order live PSO anchor {name}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    ser=(d/"vk_pipeline_serialization.cpp").read_text()
    version="-".join(re.search(rf"{v} = (\d+)u;",ser)[1] for v in
                     ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
    header=r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include "common/elf_info.h"
#include "common/path_util.h"
#include "core/emulator_settings.h"
#include "video_core/amdgpu/regs_color.h"
#include "video_core/renderer_vulkan/driver_cache_file.h"
#include "video_core/renderer_vulkan/vk_instance.h"

namespace Vulkan {
inline vk::ResultValue<vk::UniquePipeline> CreateOrderLiveGraphics(
    const Instance& instance, vk::PipelineCache shared,
    const vk::GraphicsPipelineCreateInfo& original, u64 hash, bool preloading) {
    const auto device=instance.GetDevice();
    if (!AmdGpu::BachataOrderNoMsaa() || preloading ||
        EmulatorSettings.IsShaderCollect() || EmulatorSettings.IsPatchShaders())
        return device.createGraphicsPipelineUnique(shared, original);
    // Use current descriptors, shader modules and dynamic rendering state.
    // No cached guest pointers, serialized graphics objects or warmup.
    constexpr size_t max_blob=8u<<20;
    std::vector<u8> bytes;
    std::filesystem::path path;
    DriverCacheFile::Identity id{instance.GetVendorID(),instance.GetDeviceID(),
                                 instance.GetDriverVersion(),{}};
    const auto uuid=instance.GetPipelineCacheUUID();
    std::copy(uuid.begin(),uuid.end(),id.uuid.begin());
    const char* setting=std::getenv("BACHATA_ORDER_LIVE_PSO_CACHE");
    const bool disk=EmulatorSettings.IsPipelineCacheEnabled() &&
                    (!setting || *setting!='0');
    if(disk) {
        try {
            const auto driver=fmt::format("{:x}-{:x}-{:x}-{:016x}",
                id.vendor,id.device,id.driver,DriverCacheFile::Checksum(id.uuid));
            path=Common::FS::GetUserPath(Common::FS::PathType::CacheDir) /
                Common::ElfInfo::Instance().GameSerial() / "live-pso-v1-@ABI@" /
                driver / fmt::format("{:016x}.bin",hash);
            std::error_code ec;
            const auto size=std::filesystem::file_size(path,ec);
            if(!ec && size<=max_blob+48) bytes=DriverCacheFile::Load(path,id);
        } catch (...) { path.clear(); bytes.clear(); }
    }
    // Bound the driver-side cache lifetime to this one pipeline creation.
    // Never merge into the growing shared compute cache.
    auto cache=device.createPipelineCacheUnique({
        .initialDataSize=bytes.size(),.pInitialData=bytes.empty()?nullptr:bytes.data()});
    if(cache.result!=vk::Result::eSuccess && !bytes.empty()) {
        bytes.clear();
        cache=device.createPipelineCacheUnique({});
    }
    if(cache.result!=vk::Result::eSuccess)
        return device.createGraphicsPipelineUnique(nullptr,original);
    vk::PipelineCreationFeedback feedback{};
    vk::PipelineCreationFeedbackCreateInfo feedback_info{
        .pNext=original.pNext,.pPipelineCreationFeedback=&feedback};
    auto info=original;
    info.pNext=&feedback_info;
    auto result=device.createGraphicsPipelineUnique(*cache.value,info);
    if(result.result!=vk::Result::eSuccess && !bytes.empty()) {
        // Never retry against a rejected cache. Reconstruct from live state.
        bytes.clear();
        cache=device.createPipelineCacheUnique({});
        feedback=vk::PipelineCreationFeedback{};
        if(cache.result!=vk::Result::eSuccess)
            return device.createGraphicsPipelineUnique(nullptr,original);
        result=device.createGraphicsPipelineUnique(*cache.value,info);
    }
    if(result.result!=vk::Result::eSuccess) return result;
    const bool valid=bool(feedback.flags&vk::PipelineCreationFeedbackFlagBits::eValid);
    const bool hit=valid&&bool(feedback.flags&
        vk::PipelineCreationFeedbackFlagBits::eApplicationPipelineCacheHit);
    static u64 hits{},misses{},unreported{};
    if(!valid) ++unreported; else if(hit) ++hits; else ++misses;
    const auto total=hits+misses+unreported;
    if(total<=8 || total%64==0)
        LOG_INFO(Render_Vulkan,
            "BACHATA_ORDER_LIVE_PSO hash={:#x} archive_bytes={} driver_hits={} driver_misses={} unreported={} driver_ns={}",
            hash,bytes.size(),hits,misses,unreported,feedback.duration);
    if(disk&&!path.empty()&&!hit) {
        try {
            const auto& api=VULKAN_HPP_DEFAULT_DISPATCHER;
            size_t size=0;
            if(api.vkGetPipelineCacheData(device,*cache.value,&size,nullptr)==VK_SUCCESS &&
               size>32 && size<=max_blob) {
                std::vector<u8> payload(size);
                if(api.vkGetPipelineCacheData(device,*cache.value,&size,payload.data())==VK_SUCCESS &&
                   size<=payload.size()) {
                    payload.resize(size);
                    DriverCacheFile::Save(path,payload,id);
                }
            }
        } catch (...) {
            LOG_WARNING(Render_Vulkan,"Order live PSO cache write skipped");
        }
    }
    return result;
}
}
'''
    (d/"order_live_pso_cache.h").write_text(header.replace("@ABI@",version))
    g="vk_graphics_pipeline.cpp"
    edit(g,'#include "video_core/renderer_vulkan/vk_graphics_pipeline.h"',
         '#include "video_core/renderer_vulkan/vk_graphics_pipeline.h"\n#include "video_core/renderer_vulkan/order_live_pso_cache.h"')
    # These 3 modules are private to this constructor, unlike Program::Module.
    # Vulkan permits their destruction immediately after pipeline creation.
    edit(g,"    const vk::Device device = instance.GetDevice();",
         """    const vk::Device device = instance.GetDevice();
    struct AuxLifetime {
        vk::Device device;
        std::array<vk::ShaderModule,3> modules{};
        size_t count{};
        ~AuxLifetime() {
            for(size_t i=0;i<count;++i) device.destroyShaderModule(modules[i]);
        }
    } aux{device};
    const auto compile_aux=[&](std::span<const u32> code) {
        ASSERT(aux.count<aux.modules.size());
        auto module=CompileSPV(code,device);
        aux.modules[aux.count++]=module;
        return module;
    };""")
    for n in ("tcs","tes","fragment"):
        edit(g,f"CompileSPV(sdata.{n}, instance.GetDevice())",f"compile_aux(sdata.{n})")
    edit("vk_graphics_pipeline.h","    ~GraphicsPipeline();",
         """    ~GraphicsPipeline();
    vk::Result CreationResult() const { return creation_result; }""")
    edit("vk_graphics_pipeline.h","    void BuildDescSetLayout(bool preloading);",
         """    vk::Result creation_result{vk::Result::eSuccess};
    void BuildDescSetLayout(bool preloading);""")
    edit(g,"""    auto [pipeline_result, pipe] =
        device.createGraphicsPipelineUnique(pipeline_cache, pipeline_info);
    ASSERT_MSG(pipeline_result == vk::Result::eSuccess, "Failed to create graphics pipeline: {}",""",
         """    auto [pipeline_result, pipe] = CreateOrderLiveGraphics(instance,pipeline_cache,
        pipeline_info,std::hash<GraphicsPipelineKey>{}(key),preloading);
    creation_result=pipeline_result;
    if(AmdGpu::BachataOrderNoMsaa()&&!preloading&&!EmulatorSettings.IsShaderCollect()&&
       (pipeline_result==vk::Result::eErrorOutOfHostMemory ||
        pipeline_result==vk::Result::eErrorOutOfDeviceMemory)) return;
    ASSERT_MSG(pipeline_result == vk::Result::eSuccess, "Failed to create graphics pipeline: {}",""")
    # On OOM reclaim the oldest live graphics objects only after all recorded
    # commands and submitted work are complete. No draw is silently discarded.
    h="vk_pipeline_cache.h";c="vk_pipeline_cache.cpp"
    edit(h,"    Shader::Pools pools;",
         """    Shader::Pools pools;
    std::unordered_map<const GraphicsPipeline*,u64> order_pso_use;
    u64 order_pso_clock{};
    void ReclaimOrderGraphics();""")
    edit(h,"#include <functional>","#include <functional>\n#include <unordered_map>")
    edit(c,"const GraphicsPipeline* PipelineCache::GetGraphicsPipeline(const DrawIndirectParams params) {",
         """void PipelineCache::ReclaimOrderGraphics() {
    scheduler.EndRendering();
    scheduler.Finish();
    scheduler.DrainRecorder();
    std::vector<std::pair<u64,GraphicsPipelineKey>> candidates;
    candidates.reserve(graphics_pipelines.size());
    for(auto it=graphics_pipelines.begin();it!=graphics_pipelines.end();++it) {
        const auto* p=it.value().get();
        if(!p) continue;
        auto stamp=order_pso_use.find(p);
        candidates.emplace_back(stamp==order_pso_use.end()?0:stamp->second,it.key());
    }
    std::ranges::sort(candidates,{},&std::pair<u64,GraphicsPipelineKey>::first);
    const auto count=std::min(candidates.size(),std::max<size_t>(64,candidates.size()/3));
    for(size_t i=0;i<count;++i) {
        auto it=graphics_pipelines.find(candidates[i].second);
        if(it==graphics_pipelines.end()) continue;
        order_pso_use.erase(it.value().get());
        graphics_pipelines.erase(it);
    }
    LOG_WARNING(Render_Vulkan,"BACHATA_ORDER_PSO_RECLAIM evicted={} remaining={}",
                count,graphics_pipelines.size());
}
const GraphicsPipeline* PipelineCache::GetGraphicsPipeline(const DrawIndirectParams params) {""")
    edit(c,"""    if(auto it=graphics_pipelines.find(graphics_key);it!=graphics_pipelines.end())
        return it->second.get();""",
         """    if(auto it=graphics_pipelines.find(graphics_key);it!=graphics_pipelines.end()) {
        if(AmdGpu::BachataOrderNoMsaa()&&!EmulatorSettings.IsShaderCollect())
            order_pso_use[it->second.get()]=++order_pso_clock;
        return it->second.get();
    }
    if(AmdGpu::BachataOrderNoMsaa()&&!EmulatorSettings.IsShaderCollect()) {
        const auto hash=std::hash<GraphicsPipelineKey>{}(graphics_key);
        GraphicsPipeline::SerializationSupport sdata{};
        const auto build=[&] {
            return std::make_unique<GraphicsPipeline>(instance,scheduler,desc_heap,profile,
                graphics_key,*pipeline_cache,infos,runtime_infos,fetch_shader,modules,sdata,false);
        };
        auto result=build();
        if(result->CreationResult()!=vk::Result::eSuccess) {
            const auto error=result->CreationResult();
            result.reset();
            LOG_WARNING(Render_Vulkan,"BACHATA_ORDER_PSO_OOM hash={:#x} result={}",hash,vk::to_string(error));
            ReclaimOrderGraphics();
            sdata={};
            result=build();
        }
        ASSERT_MSG(result->CreationResult()==vk::Result::eSuccess,
                   "Order graphics pipeline failed after synchronized reclamation: {}",
                   vk::to_string(result->CreationResult()));
        const auto* p=result.get();
        graphics_pipelines.try_emplace(graphics_key,std::move(result));
        order_pso_use[p]=++order_pso_clock;
        ++num_new_pipelines;
        return p;
    }""")
    # The old sampling hook follows the generic insertion, which Order now
    # bypasses. Place it on the actual Order live path before allocation.
    p=d/c;s=p.read_text()
    begin=s.index("#ifdef __ANDROID__\n        if (AmdGpu::BachataOrderNoMsaa() &&")
    end=s.index("#endif",begin)+len("#endif")
    sample=s[begin:end]
    s=s[:begin]+s[end:]
    anchor="        const auto hash=std::hash<GraphicsPipelineKey>{}(graphics_key);\n        GraphicsPipeline::SerializationSupport sdata{};"
    assert s.count(anchor)==1
    s=s.replace(anchor,"        const auto hash=std::hash<GraphicsPipelineKey>{}(graphics_key);\n"+sample+"\n        GraphicsPipeline::SerializationSupport sdata{};")
    p.write_text(s)
    # The Android donor interns identical SRT programs and refreshes the
    # base program once per shader selection. Retain our per-permutation
    # compiled descriptor metadata but share the actual synchronized data
    # for consecutive candidates whose complete walker bytes are identical.
    walker=root/"src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp"
    w=walker.read_text()
    old="""    auto copy = std::make_unique<u32[]>(words);
    std::memcpy(copy.get(), code, words * sizeof(u32));
    std::scoped_lock lock{g_walker_mutex};
    return g_walkers.emplace_back(std::move(copy)).get();"""
    assert w.count(old)==1
    # The portable walker no longer poisons failed loads (revalidates every
    # dispatch), so intern only when the live code has no atomic mutations.
    assert "fetch_or(" not in w and "fetch_and(" not in w
    w=w.replace(old,"""    std::scoped_lock lock{g_walker_mutex};
    if (AmdGpu::BachataOrderNoMsaa()) {
        static std::unordered_multimap<u64,std::pair<const u32*,size_t>> index;
        u64 hash=14695981039346656037ull;
        for(size_t i=0;i<words;++i) { hash^=code[i];hash*=1099511628211ull; }
        const auto [first,last]=index.equal_range(hash);
        for(auto it=first;it!=last;++it) {
            const auto& [stored,n]=it->second;
            if(n==words&&!std::memcmp(stored,code,words*sizeof(u32))) return stored;
        }
        auto copy=std::make_unique<u32[]>(words);
        std::memcpy(copy.get(),code,words*sizeof(u32));
        const auto* stored=g_walkers.emplace_back(std::move(copy)).get();
        index.emplace(hash,std::pair{stored,words});
        return stored;
    }
    auto copy = std::make_unique<u32[]>(words);
    std::memcpy(copy.get(), code, words * sizeof(u32));
    return g_walkers.emplace_back(std::move(copy)).get();""")
    if '#include "video_core/amdgpu/regs_color.h"' not in w:
        w=w.replace('#include "core/memory.h"','#include "core/memory.h"\n#include "video_core/amdgpu/regs_color.h"',1)
    walker.write_text(w)
    edit(c,"    for (size_t k=0;k<program->modules.size();++k) {",
         """    const Shader::Info* order_srt_snapshot=nullptr;
    for (size_t k=0;k<program->modules.size();++k) {""")
    edit(c,"""        effective.pgm_base=params.Base();
        effective.user_data=params.user_data;
        effective.RefreshFlatBuf();
        if (srt_sync) srt_sync(effective);""",
         """        effective.pgm_base=params.Base();
        effective.user_data=params.user_data;
        const bool share_srt=AmdGpu::BachataOrderNoMsaa() &&
            effective.sw_stage!=SwStage::TessellationControl &&
            effective.sw_stage!=SwStage::TessellationEval &&
            effective.srt_info.walker_func;
        if (share_srt && order_srt_snapshot &&
            effective.srt_info.walker_func==order_srt_snapshot->srt_info.walker_func &&
            effective.srt_info.walker_func_size==order_srt_snapshot->srt_info.walker_func_size &&
            effective.srt_info.flattened_bufsize_dw==order_srt_snapshot->srt_info.flattened_bufsize_dw) {
            // Same guest SGPR input and exact same immutable walker, in this
            // one shader selection only. Copy synchronized bytes and provenance.
            effective.flattened_ud_buf=order_srt_snapshot->flattened_ud_buf;
            effective.srt_guest_sources=order_srt_snapshot->srt_guest_sources;
        } else {
            effective.RefreshFlatBuf();
            if (srt_sync) srt_sync(effective);
            order_srt_snapshot=share_srt?&effective:nullptr;
        }""")
    return {"cache":"driver-validated per-PSO cache, exact live state, no eager graphics warmup",
            "lifetime":"free auxiliary Vulkan shader modules after pipeline creation",
            "oom":"GPU-complete least-recently-used eviction and one retry, no discarded draw",
            "feedback":"actual driver-reported application cache hits, misses and duration",
            "srt":"intern exact immutable walkers; reuse synchronized snapshot only within one shader selection"}
