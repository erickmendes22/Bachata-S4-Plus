"""SotC donor deferred compute builds using the FEX pipeline worker pool and recorder."""
from pathlib import Path
def apply(root):
    d=root/"src/video_core/renderer_vulkan"
    def edit(p,a,b,n=1):
        s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f"compute worker anchor {p.name}: {a[:80]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    h=d/"vk_compute_pipeline.h"; c=d/"vk_compute_pipeline.cpp"
    edit(h,"#pragma once","#pragma once\n#include <atomic>\n#include <string>")
    edit(h,"SerializationSupport& sdata, bool preloading);","SerializationSupport& sdata, bool preloading, bool deferred=false);")
    edit(h,"    ~ComputePipeline();","""    ~ComputePipeline();
    void Build(vk::PipelineCache cache);
    void WaitBuilt() const;
    void BindWhenReady() const;""")
    edit(h,"    ComputePipelineKey compute_key;","""    ComputePipelineKey compute_key;
    vk::ShaderModule compute_module;
    std::string debug_name;
    std::atomic<bool> ready{false};""")
    edit(c,"SerializationSupport& sdata, bool preloading /*=false*/)","SerializationSupport& sdata, bool preloading /*=false*/, bool deferred)")
    edit(c,"      compute_key{compute_key_} {","      compute_key{compute_key_}, compute_module{module} {")
    p=c.read_text()
    start=p.index("    const vk::PipelineShaderStageRequiredSubgroupSizeCreateInfo subgroup_size_ci")
    end=p.index("    u32 binding{};",start)
    shader=p[start:end].replace(".module = module,", ".module = compute_module,")
    p=p[:start]+p[end:]
    start=p.index("    const vk::ComputePipelineCreateInfo compute_pipeline_ci")
    end=p.index("ComputePipeline::~ComputePipeline() = default;",start)
    p=p[:start]+"""    debug_name=debug_str;
    if(!deferred) Build(pipeline_cache);
}

void ComputePipeline::Build(vk::PipelineCache cache) {
"""+shader+"""    const vk::ComputePipelineCreateInfo compute_pipeline_ci = {
        .stage=shader_ci,
        .layout=*pipeline_layout,
    };
    const auto device=instance.GetDevice();
    auto [result,pipe]=device.createComputePipelineUnique(cache,compute_pipeline_ci);
    ASSERT_MSG(result==vk::Result::eSuccess,"Failed to create compute pipeline: {}",vk::to_string(result));
    pipeline=std::move(pipe);
    SetObjectName(device,*pipeline,"Compute Pipeline {}",debug_name);
    ready.store(true,std::memory_order_release);
    ready.notify_all();
}
void ComputePipeline::WaitBuilt() const {
    ready.wait(false,std::memory_order_acquire);
}
void ComputePipeline::BindWhenReady() const {
    if(ready.load(std::memory_order_acquire)) {
        scheduler.CommandBuffer().bindPipeline(vk::PipelineBindPoint::eCompute,Handle());
        return;
    }
    scheduler.RecordDeferred([this](vk::CommandBuffer cmd){
        WaitBuilt();
        cmd.bindPipeline(vk::PipelineBindPoint::eCompute,Handle());
    });
}

"""+p[end:]
    c.write_text(p)
    edit(h,"    std::atomic<bool> ready{false};","    std::atomic<bool> ready{false};")
    h=d/"vk_pipeline_cache.h";c=d/"vk_pipeline_cache.cpp"
    edit(h,"        void Merge();","        void SubmitCompute(ComputePipeline* pipeline);\n        void WaitCompute();\n        void Merge();")
    edit(h,"using Job=std::packaged_task<std::shared_ptr<GraphicsBuild>(vk::PipelineCache)>;","using Job=std::packaged_task<void(vk::PipelineCache)>;")
    edit(h,"        std::deque<Job> queue;","        std::deque<Job> queue;\n        std::deque<Job> compute_queue;\n        std::vector<std::future<void>> compute_futures;")
    edit(c,"cv.wait(lk,[this]{return stop||!queue.empty();});\n                    if(queue.empty())return;\n                    job=std::move(queue.front());queue.pop_front();","""cv.wait(lk,[this]{return stop||!queue.empty()||!compute_queue.empty();});
                    if(queue.empty()&&compute_queue.empty())return;
                    auto& next=compute_queue.empty()?queue:compute_queue;
                    job=std::move(next.front());next.pop_front();""")
    edit(c,"    Job task{[this,job](vk::PipelineCache cache) {","""    auto promise=std::make_shared<std::promise<std::shared_ptr<GraphicsBuild>>>();
    auto result=promise->get_future();
    Job task{[this,job,promise](vk::PipelineCache cache) {
        try {""")
    edit(c,"        return job;\n    }};\n    auto result=task.get_future();","""        promise->set_value(job);
        } catch(...) {
            promise->set_exception(std::current_exception());
        }
    }};""")
    edit(c,"void PipelineCache::GraphicsWorkers::Merge() {","""void PipelineCache::GraphicsWorkers::SubmitCompute(ComputePipeline* pipeline) {
    std::erase_if(compute_futures,[](auto& f){
        if(f.wait_for(std::chrono::seconds(0))!=std::future_status::ready)return false;
        f.get();return true;
    });
    // Bound queue memory without dropping any dispatch.
    if(compute_futures.size()>=32) {
        compute_futures.front().get();
        compute_futures.erase(compute_futures.begin());
    }
    Job task{[pipeline](vk::PipelineCache cache){pipeline->Build(cache);}};
    compute_futures.push_back(task.get_future());
    {std::scoped_lock lk{mutex};compute_queue.emplace_back(std::move(task));}
    cv.notify_one();
}
void PipelineCache::GraphicsWorkers::WaitCompute() {
    for(auto& f:compute_futures)f.get();
    compute_futures.clear();
}
void PipelineCache::GraphicsWorkers::Merge() {
    WaitCompute();""")
    edit(c,"        it.value() = std::make_unique<ComputePipeline>(instance, scheduler, desc_heap, profile,\n                                                       *pipeline_cache, compute_key, *infos[0],\n                                                       modules[0], sdata, false);","""        const auto serial=Common::ElfInfo::Instance().GameSerial();
        const bool deferred=(serial=="CUSA08809"||serial=="CUSA08034") &&
            scheduler.HasRecordThread()&&!EmulatorSettings.IsShaderCollect();
        it.value() = std::make_unique<ComputePipeline>(instance, scheduler, desc_heap, profile,
                                                       *pipeline_cache, compute_key, *infos[0],
                                                       modules[0], sdata, false, deferred);
        if(deferred) {
            if(!graphics_workers)graphics_workers=std::make_unique<GraphicsWorkers>(*this);
            graphics_workers->SubmitCompute(it.value().get());
        }""")
    edit(d/"vk_rasterizer.cpp","    cmdbuf.bindPipeline(vk::PipelineBindPoint::eCompute, pipeline->Handle());","    pipeline->BindWhenReady();",2)
    return {"compute":"deferred Vulkan-only compilation on independent cache; compute-priority bounded queue; recorder binds in original dispatch order"}
