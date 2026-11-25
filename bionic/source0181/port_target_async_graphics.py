"""Port donor asynchronous graphics PSO creation to the existing FEX pipelines.

The worker receives the exact current 0.18.1 key, immutable per-permutation
Info, modules and vertex descriptors. Live pointers are published only on
the command thread. Separate VkPipelineCache handles avoid driver mutex
contention. Only geometry without storage side effects can use the donor's
cold-cache pop-in policy; fullscreen, indirect and write-side-effect draws wait.
"""
from pathlib import Path

def apply(root: Path):
    def edit(rel,a,b):
        p=root/"src"/rel
        s=p.read_text()
        if s.count(a)!=1: raise RuntimeError("async graphics drift "+rel+": "+a[:110])
        p.write_text(s.replace(a,b,1))
    v="video_core/renderer_vulkan/"
    h=v+"vk_pipeline_cache.h"
    c=v+"vk_pipeline_cache.cpp"
    gh=v+"vk_graphics_pipeline.h"
    gc=v+"vk_graphics_pipeline.cpp"
    edit(gh,"                     bool preloading);",
         "                     bool preloading, std::span<const AmdGpu::Buffer> captured_vertex = {});")
    edit(gh,"    const GraphicsPipelineKey& GetGraphicsKey() const {",
         "    void PublishStages(std::span<const Shader::Info*, MaxShaderStages> live) {\n        std::copy(live.begin(),live.end(),stages.begin());\n    }\n\n    const GraphicsPipelineKey& GetGraphicsKey() const {")
    edit(gh,"                         u32 step_rate_1) const;",
         "                         u32 step_rate_1, std::span<const AmdGpu::Buffer> captured = {}) const;")
    edit(gc,"    SerializationSupport& sdata, bool preloading)",
         "    SerializationSupport& sdata, bool preloading, std::span<const AmdGpu::Buffer> captured_vertex)")
    edit(gc,"                            guest_buffers, vs_info.step_rate_0, vs_info.step_rate_1);",
         "                            guest_buffers, vs_info.step_rate_0, vs_info.step_rate_1,captured_vertex);")
    edit(gc,"    VertexInputs<AmdGpu::Buffer>& guest_buffers, u32 step_rate_0, u32 step_rate_1) const {",
         "    VertexInputs<AmdGpu::Buffer>& guest_buffers, u32 step_rate_0, u32 step_rate_1,\n    std::span<const AmdGpu::Buffer> captured) const {")
    edit(gc,"        const auto buffer = attrib.GetSharp(vs_info);",
         "        const auto buffer = captured.empty()?attrib.GetSharp(vs_info):captured[semantic];")
    p=root/"src"/gc
    s=p.read_text()
    a="VertexInputs<AmdGpu::Buffer>& guest_buffers, u32 step_rate_0, u32 step_rate_1) const;"
    if s.count(a)!=2:raise RuntimeError("vertex input explicit instantiations")
    s=s.replace(a,"VertexInputs<AmdGpu::Buffer>& guest_buffers, u32 step_rate_0, u32 step_rate_1,\n    std::span<const AmdGpu::Buffer> captured) const;")
    # This value was never used: all buffers are storage buffers. Do not
    # access borrowed guest pointers on pipeline workers for no purpose.
    a="""            const auto sharp =
                preloading ? AmdGpu::Buffer{}
                           : buffer.GetSharp(*stage); // See for the comment in compute PL creation
"""
    if s.count(a)!=1:raise RuntimeError("buffer layout unused live read drift")
    s=s.replace(a,"")
    s=s.replace("void GraphicsPipeline::BuildDescSetLayout(bool preloading) {","void GraphicsPipeline::BuildDescSetLayout(bool /*preloading*/) {")
    p.write_text(s)
    edit(h,"#include <functional>","#include <functional>\n#include <future>\n#include <condition_variable>\n#include <deque>\n#include <mutex>\n#include <thread>")
    edit(h,"    u32 instance_sgpr_offset;\n};","    u32 instance_sgpr_offset;\n    bool indirect{};\n};")
    edit(h,"    DrawIndirectParams draw_indirect_params{};",
         """    struct GraphicsBuild {
        GraphicsPipelineKey key;
        std::array<Shader::Info,MaxShaderStages> snapshot;
        std::array<std::vector<u32>,MaxShaderStages> user_data;
        std::array<const Shader::Info*,MaxShaderStages> stages{};
        std::array<const Shader::Info*,MaxShaderStages> live{};
        std::array<Shader::RuntimeInfo,MaxShaderStages> runtime_infos{};
        std::array<vk::ShaderModule,MaxShaderStages> modules{};
        std::optional<Shader::Gcn::FetchShaderData> fetch;
        std::vector<AmdGpu::Buffer> vertex;
        GraphicsPipeline::SerializationSupport data;
        std::unique_ptr<GraphicsPipeline> pipeline;
    };
    struct PendingGraphics {
        std::future<std::shared_ptr<GraphicsBuild>> result;
    };
    tsl::robin_map<GraphicsPipelineKey,PendingGraphics> pending_graphics;
    class GraphicsWorkers {
    public:
        explicit GraphicsWorkers(PipelineCache& owner);
        ~GraphicsWorkers();
        std::future<std::shared_ptr<GraphicsBuild>> Submit(std::shared_ptr<GraphicsBuild> job);
        void Merge();
    private:
        using Job=std::packaged_task<std::shared_ptr<GraphicsBuild>(vk::PipelineCache)>;
        PipelineCache& owner;
        std::array<vk::UniquePipelineCache,2> caches;
        std::array<std::jthread,2> threads;
        std::mutex mutex;
        std::condition_variable cv;
        std::deque<Job> queue;
        bool stop{};
    };
    std::unique_ptr<GraphicsWorkers> graphics_workers;
    void PublishGraphics(bool wait=false);
    void FinishGraphicsWorkers();
    bool CanQueueGraphics(const DrawIndirectParams& params) const;
    void QueueGraphics();
    DrawIndirectParams draw_indirect_params{};""")
    p=root/"src"/c
    s=p.read_text()
    if '#include "common/elf_info.h"' not in s:
        s='#include "common/elf_info.h"\n'+s
    if "#include <chrono>" not in s:
        s='#include <chrono>\n'+s
    # SotC formerly restored pipelines through an uninitialized VkPipelineCache.
    if "PipelineCache::~PipelineCache() = default;" in s:
        a="""    WarmUp();

    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});"""
        if s.count(a)!=1:raise RuntimeError("SotC pipeline cache initialization drift")
        s=s.replace(a,"    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});")
        s=s.replace("    pipeline_cache = std::move(cache);\n}","    pipeline_cache = std::move(cache);\n    WarmUp();\n}",1)
        s=s.replace("PipelineCache::~PipelineCache() = default;",
                    "PipelineCache::~PipelineCache() { FinishGraphicsWorkers(); }")
    else:
        a="    shader_workers.reset();\n    SaveDriverCache();"
        if s.count(a)!=1:raise RuntimeError("Order workers destruction drift")
        s=s.replace(a,"    shader_workers.reset();\n    FinishGraphicsWorkers();\n    SaveDriverCache();")
    p.write_text(s)
    edit(c,"const GraphicsPipeline* PipelineCache::GetGraphicsPipeline(const DrawIndirectParams params) {",
         """PipelineCache::GraphicsWorkers::GraphicsWorkers(PipelineCache& owner_) : owner(owner_) {
    const auto device=owner.instance.GetDevice();
    for(auto& cache:caches) {
        auto [result,created]=device.createPipelineCacheUnique({});
        ASSERT_MSG(result==vk::Result::eSuccess,"Failed to create compiler pipeline cache");
        cache=std::move(created);
        ASSERT(device.mergePipelineCaches(*cache,*owner.pipeline_cache)==vk::Result::eSuccess);
    }
    for(size_t i=0;i<threads.size();++i) {
        threads[i]=std::jthread([this,i] {
            for(;;) {
                Job job;
                {
                    std::unique_lock lk{mutex};
                    cv.wait(lk,[this]{return stop||!queue.empty();});
                    if(queue.empty())return;
                    job=std::move(queue.front());queue.pop_front();
                }
                job(*caches[i]);
            }
        });
    }
}
PipelineCache::GraphicsWorkers::~GraphicsWorkers() {
    {std::scoped_lock lk{mutex};stop=true;}
    cv.notify_all();
    for(auto& thread:threads)if(thread.joinable())thread.join();
}
std::future<std::shared_ptr<PipelineCache::GraphicsBuild>>
PipelineCache::GraphicsWorkers::Submit(std::shared_ptr<GraphicsBuild> job) {
    Job task{[this,job](vk::PipelineCache cache) {
        job->pipeline=std::make_unique<GraphicsPipeline>(
            owner.instance,owner.scheduler,owner.desc_heap,owner.profile,job->key,
            cache,job->stages,job->runtime_infos,job->fetch?&*job->fetch:nullptr,
            job->modules,job->data,false,job->vertex);
        return job;
    }};
    auto result=task.get_future();
    {std::scoped_lock lk{mutex};queue.emplace_back(std::move(task));}
    cv.notify_one();
    return result;
}
void PipelineCache::GraphicsWorkers::Merge() {
    const std::array<vk::PipelineCache,2> sources{*caches[0],*caches[1]};
    const auto result=owner.instance.GetDevice().mergePipelineCaches(*owner.pipeline_cache,sources);
    if(result!=vk::Result::eSuccess)
        LOG_WARNING(Render_Vulkan,"Compiler cache merge: {}",vk::to_string(result));
}
bool PipelineCache::CanQueueGraphics(const DrawIndirectParams& params) const {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if(serial!="CUSA00785"&&serial!="CUSA08809"&&serial!="CUSA08034")return false;
    if(params.indirect||liverpool->regs.num_indices<=6||liverpool->regs.stage_enable.hs_en||
        EmulatorSettings.IsShaderCollect())return false;
    for(const auto* info:infos) {
        if(!info)continue;
        if(std::ranges::any_of(info->buffers,[](const auto& b){return b.is_written;})||
           std::ranges::any_of(info->images,[](const auto& i){return i.is_written;})||
           info->uses_dma)return false;
    }
    return true;
}
void PipelineCache::QueueGraphics() {
    auto job=std::make_shared<GraphicsBuild>();
    job->key=graphics_key;
    job->runtime_infos=runtime_infos;
    job->modules=modules;
    job->live=infos;
    for(u32 i=0;i<MaxShaderStages;++i) {
        if(!infos[i])continue;
        job->snapshot[i]=*infos[i];
        job->user_data[i].assign(infos[i]->user_data.begin(),infos[i]->user_data.end());
        job->snapshot[i].user_data=job->user_data[i];
        job->snapshot[i].params.reset();
        job->stages[i]=&job->snapshot[i];
    }
    if(fetch_shader) {
        job->fetch=*fetch_shader;
        const auto* vs=infos[u32(SwStage::Vertex)];
        if(vs)for(const auto& attribute:fetch_shader->attributes)
            job->vertex.push_back(attribute.GetSharp(*vs));
    }
    if(!graphics_workers)graphics_workers=std::make_unique<GraphicsWorkers>(*this);
    pending_graphics.try_emplace(job->key,PendingGraphics{graphics_workers->Submit(job)});
}
void PipelineCache::PublishGraphics(bool wait) {
    for(auto it=pending_graphics.begin();it!=pending_graphics.end();) {
        if(!wait&&it.value().result.wait_for(std::chrono::seconds(0))!=std::future_status::ready) {
            ++it;continue;
        }
        auto job=it.value().result.get();
        job->pipeline->PublishStages(job->live);
        RegisterPipelineData(job->key,std::hash<GraphicsPipelineKey>{}(job->key),job->data);
        graphics_pipelines.try_emplace(job->key,std::move(job->pipeline));
        ++num_new_pipelines;
        it=pending_graphics.erase(it);
    }
}
void PipelineCache::FinishGraphicsWorkers() {
    PublishGraphics(true);
    if(graphics_workers) {
        graphics_workers->Merge();
        graphics_workers.reset();
    }
}
const GraphicsPipeline* PipelineCache::GetGraphicsPipeline(const DrawIndirectParams params) {
    PublishGraphics();""")
    edit(c,"    const auto [it, is_new] = graphics_pipelines.try_emplace(graphics_key);",
         """    const bool can_queue=CanQueueGraphics(params);
    if(pending_graphics.contains(graphics_key)) {
        if(can_queue)return nullptr;
        // Required pass: never discard it, wait for the captured pipeline.
        PublishGraphics(true);
    }
    if(auto it=graphics_pipelines.find(graphics_key);it!=graphics_pipelines.end())
        return it->second.get();
    if(can_queue&&pending_graphics.size()<32) {
        QueueGraphics();
        return nullptr;
    }
    const auto [it, is_new] = graphics_pipelines.try_emplace(graphics_key);""")
    edit(c,"const ComputePipeline* PipelineCache::GetComputePipeline() {",
         "const ComputePipeline* PipelineCache::GetComputePipeline() {\n    PublishGraphics();")
    edit(c,"    std::optional<vk::ShaderModule> new_module{};",
         "    FinishGraphicsWorkers();\n    std::optional<vk::ShaderModule> new_module{};")
    edit(v+"vk_pipeline_serialization.cpp","void PipelineCache::Sync() {",
         "void PipelineCache::Sync() {\n    FinishGraphicsWorkers();")
    edit(v+"vk_rasterizer.cpp","        .instance_sgpr_offset = instance_sgpr_offset,\n    };",
         "        .instance_sgpr_offset = instance_sgpr_offset,\n        .indirect = true,\n    };")
    return {"graphics":"2 compiler workers, independent driver caches, immutable captured input, publish on GPU thread",
            "policy":"donor cold-cache geometry pop-in only, full-screen/indirect/storage-write passes block",
            "warmup":"driver VkPipelineCache initialized before warmup, worker caches merged before close"}
