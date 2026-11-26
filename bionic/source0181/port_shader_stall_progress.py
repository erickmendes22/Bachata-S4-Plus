"""Identify the unfinished compiler/driver/queue phase without per-draw logs.

The current SotC diagnostic ends after a CompileModule entry. It contains no
phase exit, GPU wait target or queue snapshot, so that entry cannot distinguish
translation, SRT readback, shader-module creation and driver PSO compilation.
This overlay records miss phases and samples a prolonged wait only once.
"""
from pathlib import Path


def apply(root: Path):
    root = Path(root)

    def edit(rel, old, new, count=1):
        path = root / rel
        source = path.read_text()
        if source.count(old) != count:
            raise RuntimeError(f"Shader progress anchor drift: {rel}: {old[:100]}")
        path.write_text(source.replace(old, new))

    header = Path(__file__).with_name("inherited_shader") / "bachata_progress.h"
    (root / "src/common/bachata_progress.h").write_text(header.read_text())
    cache = "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    graphics = "src/video_core/renderer_vulkan/vk_graphics_pipeline.cpp"
    compute = "src/video_core/renderer_vulkan/vk_compute_pipeline.cpp"
    lp = "src/video_core/amdgpu/liverpool.cpp"
    lh = "src/video_core/amdgpu/liverpool.h"
    sh = "src/video_core/renderer_vulkan/vk_scheduler.h"
    semaphore = "src/video_core/renderer_vulkan/vk_semaphore.cpp"
    for rel in (cache, graphics, compute, lp):
        path = root / rel
        path.write_text('#include "common/bachata_progress.h"\n' + path.read_text())

    edit(sh, """    [[nodiscard]] u64 CurrentTick() const noexcept {
        return work_semaphore.CurrentTick();
    }""", """    [[nodiscard]] u64 CurrentTick() const noexcept {
        return work_semaphore.CurrentTick();
    }

    // Diagnostic snapshots may run on CP while Draw/recorder owns the session.
    // Read only published atomics, never the mutable command-buffer/session list.
    [[nodiscard]] u64 RecordedSubmitTick() const noexcept {
        return recorded_submit_tick.load(std::memory_order_acquire);
    }""")
    edit(cache, """    const auto ir_program = Shader::TranslateProgram(
        code, pools, info, runtime_info, profile,
        [this, &info] { if (srt_sync) srt_sync(info); });""", """    const auto report_progress = [&](const char* phase, const char* event, auto elapsed) {
        LOG_INFO(Render_Vulkan,
                 "BACHATA_GPU_PROGRESS phase={} event={} shader={:#x} stage={} variant={} tick={} submitted={} gpu={} elapsed_us={}",
                 phase, event, info.pgm_hash, info.hw_stage, perm_idx,
                 scheduler.CurrentTick(), scheduler.RecordedSubmitTick(),
                 scheduler.GetWorkSemaphore()->KnownGpuTick(), elapsed);
    };
    const auto ir_program = Common::BachataProgress::Phase("translate", report_progress, [&] {
        return Shader::TranslateProgram(code, pools, info, runtime_info, profile, [&] {
            if (srt_sync) {
                Common::BachataProgress::Phase("srt_sync", report_progress,
                                              [&] { srt_sync(info); });
            }
        });
    });""")
    edit(cache, """    auto spv = Shader::Backend::SPIRV::EmitSPIRV(profile, runtime_info, ir_program, binding);""",
         """    auto spv = Common::BachataProgress::Phase("emit_spirv", report_progress, [&] {
        return Shader::Backend::SPIRV::EmitSPIRV(profile, runtime_info, ir_program, binding);
    });""")
    edit(cache, """        module = CompileSPV(*patch, instance.GetDevice());""", """        module = Common::BachataProgress::Phase("create_shader_module", report_progress, [&] {
            return CompileSPV(*patch, instance.GetDevice());
        });""")
    edit(cache, """        module = CompileSPV(spv, instance.GetDevice());""", """        module = Common::BachataProgress::Phase("create_shader_module", report_progress, [&] {
            return CompileSPV(spv, instance.GetDevice());
        });""")

    graphics_old = """    auto [pipeline_result, pipe] =
        device.createGraphicsPipelineUnique(pipeline_cache, pipeline_info);"""
    graphics_call = "device.createGraphicsPipelineUnique(pipeline_cache, pipeline_info)"
    if "CreateOrderLiveGraphics(" in (root / graphics).read_text():
        graphics_old = """    auto [pipeline_result, pipe] = CreateOrderLiveGraphics(instance,pipeline_cache,
        pipeline_info,std::hash<GraphicsPipelineKey>{}(key),preloading);"""
        graphics_call = "CreateOrderLiveGraphics(instance,pipeline_cache,pipeline_info,std::hash<GraphicsPipelineKey>{}(key),preloading)"
    edit(graphics, graphics_old, """    const auto report_progress = [&](const char* phase, const char* event, auto elapsed) {
        LOG_INFO(Render_Vulkan,
                 "BACHATA_GPU_PROGRESS phase={} event={} shaders={} tick={} submitted={} gpu={} elapsed_us={}",
                 phase, event, debug_str, scheduler.CurrentTick(), scheduler.RecordedSubmitTick(),
                 scheduler.GetWorkSemaphore()->KnownGpuTick(), elapsed);
    };
    auto [pipeline_result, pipe] = Common::BachataProgress::Phase(
        "create_graphics_pso", report_progress,
        [&] { return """ + graphics_call + "; });")
    compute_old = "    auto [result,pipe]=device.createComputePipelineUnique(cache,compute_pipeline_ci);"
    compute_call = "device.createComputePipelineUnique(cache,compute_pipeline_ci)"
    compute_result = "result,pipe"
    compute_name = "debug_name"
    if compute_old not in (root / compute).read_text():
        compute_old = """    auto [pipeline_result, pipe] =
        instance.GetDevice().createComputePipelineUnique(pipeline_cache, compute_pipeline_ci);"""
        compute_call = "instance.GetDevice().createComputePipelineUnique(pipeline_cache, compute_pipeline_ci)"
        compute_result = "pipeline_result,pipe"
        compute_name = "debug_str"
    edit(compute, compute_old, """    const auto report_progress = [&](const char* phase, const char* event, auto elapsed) {
        LOG_INFO(Render_Vulkan,
                 "BACHATA_GPU_PROGRESS phase={} event={} shaders={} tick={} submitted={} gpu={} elapsed_us={}",
                 phase, event, """ + compute_name + """, scheduler.CurrentTick(), scheduler.RecordedSubmitTick(),
                 scheduler.GetWorkSemaphore()->KnownGpuTick(), elapsed);
    };
    auto [""" + compute_result + """] = Common::BachataProgress::Phase(
        "create_compute_pso", report_progress,
        [&] { return """ + compute_call + "; });")

    # Snapshot hashes with the packet. A timeout does not inspect Shader::Info,
    # descriptor vectors, recorder sessions or other data mutable by the consumer.
    edit(lh, """        VAddr arg_address{},count_address{};""", """        VAddr arg_address{},count_address{};
        u64 progress_shader_hash{},progress_vertex_hash{};""")
    edit(lh, """    void DrawLoop(std::stop_token stop);""", """    void DrawLoop(std::stop_token stop);
    void WaitDrawProgress(std::unique_lock<std::mutex>& lock, bool drain);""")
    edit(lp, """void Liverpool::DrainDrawQueue() {""", """void Liverpool::WaitDrawProgress(std::unique_lock<std::mutex>& lock, bool drain) {
    Common::BachataProgress::WaitOnce(draw_cv, lock,
        [&] { return drain ? draw_head==draw_tail : draw_head-draw_tail<DrawQueueCapacity; },
        [&] {
            const auto& front=draw_ring[draw_tail%DrawQueueCapacity];
            auto& scheduler=rasterizer->GetScheduler();
            LOG_WARNING(Render_Vulkan,
                "BACHATA_GPU_WAIT phase={} head={} tail={} kind={} shader={:#x} vertex={:#x} tick={} submitted={} gpu={}",
                drain?"cp_draw_drain":"cp_draw_capacity",draw_head,draw_tail,u32(front.kind),
                front.progress_shader_hash,front.progress_vertex_hash,
                scheduler.CurrentTick(),scheduler.RecordedSubmitTick(),
                scheduler.GetWorkSemaphore()->KnownGpuTick());
        });
}
void Liverpool::DrainDrawQueue() {""")
    edit(lp, """        draw_cv.wait(lk,[&]{return draw_head==draw_tail;});""",
         """        WaitDrawProgress(lk,true);""")
    edit(lp, """    draw_cv.wait(lk,[&]{return draw_head-draw_tail<DrawQueueCapacity;});""",
         """    WaitDrawProgress(lk,false);""", count=2)
    edit(lp, """    op.kind=DrawPacket::Kind::Function;
    op.task=std::move(task);""", """    op.kind=DrawPacket::Kind::Function;
    op.progress_shader_hash=op.progress_vertex_hash=0;
    op.task=std::move(task);""")
    edit(lp, """    op.kind=kind;op.pipeline=pipeline;op.task={};""", """    op.kind=kind;op.pipeline=pipeline;op.task={};
    op.progress_shader_hash=op.progress_vertex_hash=0;""")
    edit(lp, """    if(pipeline)for(const auto* stage:pipeline->GetStages())if(stage) {
        draw_pending_writes|=stage->uses_dma || stage->has_storage_images;""", """    if(pipeline)for(const auto* stage:pipeline->GetStages())if(stage) {
        if(stage->sw_stage==Shader::SwStage::Vertex)op.progress_vertex_hash=stage->pgm_hash;
        if(stage->sw_stage==Shader::SwStage::Fragment || stage->sw_stage==Shader::SwStage::Compute)
            op.progress_shader_hash=stage->pgm_hash;
        draw_pending_writes|=stage->uses_dma || stage->has_storage_images;""")

    edit(semaphore, """    while (instance.GetDevice().waitSemaphores(&wait_info, WAIT_TIMEOUT) != vk::Result::eSuccess) {
    }""", """    // One bounded observation, then the original blocking wait. A slow GPU
    // does not produce repeated logs or periodic polling during normal draws.
    auto result=instance.GetDevice().waitSemaphores(&wait_info,2'000'000'000ULL);
    if(result==vk::Result::eTimeout) {
        LOG_WARNING(Render_Vulkan,
            "BACHATA_GPU_WAIT phase=timeline target={} tick={} gpu={}",
            tick,CurrentTick(),KnownGpuTick());
    }
    while(result!=vk::Result::eSuccess) {
        ASSERT_MSG(result==vk::Result::eTimeout,"Failed to wait for GPU timeline: {}",vk::to_string(result));
        result=instance.GetDevice().waitSemaphores(&wait_info,WAIT_TIMEOUT);
    }""")
    return {
        "phases": "translation, SRT sync, SPIR-V, shader module and graphics/compute PSO misses",
        "waits": "one observation after 2 seconds for CP/Draw and GPU timeline",
        "snapshot": "packet-owned shader hashes, locked queue positions, published atomic ticks",
    }
