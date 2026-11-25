#!/usr/bin/env python3
"""Adapt the ports' active two-stage GPU path to the Bionic/FEX renderer.

Stage A owns PM4 and PipelineCache. Stage B owns buffer/texture binds and the
Vulkan recorder. Pipeline stages, pointed vertex descriptors and side-effect
payloads are owned by each FIFO packet. Signal faults and actual SRT downloads
drain/reclaim before touching GPU state. The older direct-draw queue supplies
its register-delta decoder, not its disabled whole-Draw implementation.
"""
from pathlib import Path
import importlib.util
import re


def apply(root):
    root = Path(root)
    src = root / "src"

    def edit(rel, old, new, count=1):
        path = src / rel
        text = path.read_text()
        if text.count(old) != count:
            raise RuntimeError(f"donor draw pipeline {rel}: expected {count} {old[:110]!r}, got {text.count(old)}")
        path.write_text(text.replace(old, new))

    lp = "video_core/amdgpu/liverpool.cpp"
    lh = "video_core/amdgpu/liverpool.h"
    rp = "video_core/renderer_vulkan/vk_rasterizer.cpp"
    rh = "video_core/renderer_vulkan/vk_rasterizer.h"
    pc = "video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    sc = "video_core/renderer_vulkan/vk_scheduler.cpp"
    sh = "video_core/renderer_vulkan/vk_scheduler.h"

    if "void Liverpool::QueueDirectDraw(" not in (src / lp).read_text():
        # The Order uses the same PM4 baseline. Reuse only the register-delta
        # and signal-fault foundation; preserve its presentation policy.
        presenter = src / "video_core/renderer_vulkan/vk_presenter.cpp"
        original_presenter = presenter.read_text()
        path = Path(__file__).with_name("port_sotc_draw_pipe.py")
        spec = importlib.util.spec_from_file_location("donor_draw_foundation", path)
        foundation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foundation)
        foundation.apply(root)
        presenter.write_text(original_presenter)

    (src / "video_core/amdgpu/bachata_draw_snapshot.h").write_text(SNAPSHOT_HEADER)
    edit(lh, '#include "video_core/amdgpu/regs.h"',
         '#include "video_core/amdgpu/regs.h"\n#include "shader_recompiler/info.h"\n#include "video_core/amdgpu/bachata_draw_snapshot.h"')
    edit(lh, "class Rasterizer;", "class Rasterizer;\nclass Pipeline;")
    edit(lh, "    bool OnDrawThread() const { return draw_owner==this; }",
         """    bool OnDrawThread() const { return draw_owner==this; }
    void DrainDrawQueue();
    void InvalidateDrawSnapshots();
    std::span<const AmdGpu::Buffer> DrawVertexBuffers() const {
        return OnDrawThread()?back_vertices:std::span<const AmdGpu::Buffer>{};
    }""")
    edit(lh, "    static constexpr u32 DrawChunkWords=32, DrawQueueCapacity=32;",
         "    static constexpr u32 DrawChunkWords=32, DrawQueueCapacity=128;")
    edit(lh, "    struct DrawPacket {\n        std::vector<DrawChunk> chunks;",
         """    struct DrawPacket {
        enum class Kind { Draw, Indirect, Dispatch, IndirectDispatch, Function };
        Kind kind{Kind::Draw};
        const Vulkan::Pipeline* pipeline{};
        BachataDrawPipe::Snapshots<Shader::Info,Shader::MaxStageTypes> stages;
        std::vector<AmdGpu::Buffer> vertices;
        Common::UniqueFunction<void> task;
        VAddr arg_address{},count_address{};
        u32 stride{},max_count{};
        u16 vertex_sgpr{},instance_sgpr{};
        std::vector<DrawChunk> chunks;""")
    edit(lh, "    ComputeProgram back_cs{};",
         "    ComputeProgram back_cs{};\n    std::span<const AmdGpu::Buffer> back_vertices{};")
    edit(lh, "    bool draw_snapshot_valid{}, draw_back_owns_recorder{};",
         "    bool draw_snapshot_valid{}, draw_back_owns_recorder{},draw_pending_writes{};\n    mutable bool draw_policy_logged{},draw_policy_enabled{};")
    edit(lh, "    void DrainDrawQueue();\n    void DrawLoop(std::stop_token stop);",
         """    bool DrawPipelineEnabled() const;
    void StartDrawWorker();
    void QueueDrawOperation(DrawPacket::Kind kind,const char* marker,const void* address,
                            bool indexed,u32 offset,VAddr args=0,u32 stride=0,u32 max_count=0,
                            VAddr count_address=0,u16 vertex_sgpr=0,u16 instance_sgpr=0);
    void QueueIndirectDraw(bool indexed,VAddr args,u32 offset,u32 stride,u32 max_count,
                            VAddr count_address,u16 vertex_sgpr,u16 instance_sgpr);
    void QueueDispatchDirect();
    void QueueDispatchIndirect(VAddr args,u32 offset,u32 size);
    void QueueGpuTask(Common::UniqueFunction<void>&& task);
    void DrawLoop(std::stop_token stop);""")
    edit(lp, '#include "common/assert.h"',
         '#include "common/assert.h"\n#include "common/elf_info.h"\n#include <cstdlib>')
    text = (src / lp).read_text()
    first = text.index("void Liverpool::DrawLoop(")
    last = text.index("// BACHATA_RELEASE026_CE_QUEUE_PARITY", first)
    text = text[:first] + QUEUE_IMPLEMENTATION + "\n" + text[last:]
    (src / lp).write_text(text)
    edit(lp, "        draw_worker.join();\n    }\n    while (!ce_submits.empty())",
         "        draw_worker.join();\n    }\n    if(rasterizer)rasterizer->DetachDrawPipeline();\n    while (!ce_submits.empty())")

    # Runtime graphics/compute entry points accept an already selected pipeline.
    edit(rh, "    void Draw(bool is_indexed, u32 index_offset = 0);",
         """    bool CanPipelineDraw() const { return !host_markers_enabled && !guest_markers_enabled; }
    void DetachDrawPipeline() {
        scheduler.SetDrawPipeDrain({});
        draw_pipeline_attached=false;
    }
    const Pipeline* PrepareDrawPipeline(bool compute,const DrawIndirectParams& params);
    void Draw(bool is_indexed,u32 index_offset=0,const GraphicsPipeline* prepared=nullptr,
              bool selected=false);""")
    edit(rh, "                      VAddr count_address, u16 vertex_sgpr_offset, u16 instance_sgpr_offset);",
         "                      VAddr count_address,u16 vertex_sgpr_offset,u16 instance_sgpr_offset,\n                      const GraphicsPipeline* prepared=nullptr,bool selected=false);")
    edit(rh, "    void DispatchDirect();\n    void DispatchIndirect(VAddr address, u32 offset, u32 size);",
         """    void DispatchDirect(const ComputePipeline* prepared=nullptr,bool selected=false);
    void DispatchIndirect(VAddr address,u32 offset,u32 size,
                          const ComputePipeline* prepared=nullptr,bool selected=false);""")
    edit(rh, "    const bool host_markers_enabled;",
         "    bool draw_pipeline_attached{true};\n    const bool host_markers_enabled;")
    edit(rp, "void Rasterizer::Draw(bool is_indexed, u32 index_offset) {",
         PREPARE_IMPLEMENTATION + "\nvoid Rasterizer::Draw(bool is_indexed,u32 index_offset,\n                       const GraphicsPipeline* prepared,bool selected) {")
    edit(rp, "                              u16 instance_sgpr_offset) {",
         "                              u16 instance_sgpr_offset,const GraphicsPipeline* prepared,\n                              bool selected) {")
    edit(rp, "void Rasterizer::DispatchDirect() {",
         "void Rasterizer::DispatchDirect(const ComputePipeline* prepared,bool selected) {")
    edit(rp, "void Rasterizer::DispatchIndirect(VAddr address, u32 offset, u32 size) {",
         "void Rasterizer::DispatchIndirect(VAddr address,u32 offset,u32 size,\n                                  const ComputePipeline* prepared,bool selected) {")
    edit(rp, "const GraphicsPipeline* pipeline = pipeline_cache.GetGraphicsPipeline();",
         "const GraphicsPipeline* pipeline = selected?prepared:pipeline_cache.GetGraphicsPipeline();")
    edit(rp, "const GraphicsPipeline* pipeline = pipeline_cache.GetGraphicsPipeline(params);",
         "const GraphicsPipeline* pipeline = selected?prepared:pipeline_cache.GetGraphicsPipeline(params);")
    edit(rp, "const ComputePipeline* pipeline = pipeline_cache.GetComputePipeline();",
         "const ComputePipeline* pipeline = selected?prepared:pipeline_cache.GetComputePipeline();", 2)
    edit(rp, "                              regs.vgt_instance_step_rate_0, regs.vgt_instance_step_rate_1);",
         "                              regs.vgt_instance_step_rate_0,regs.vgt_instance_step_rate_1,\n                              liverpool->DrawVertexBuffers());")

    # Pipeline reads use a packet's immutable Info, only on its owning Stage B.
    ph = "video_core/renderer_vulkan/vk_pipeline_common.h"
    edit(ph, "    auto GetStages() const {", PIPELINE_OVERRIDE + "\n    auto GetStages() const {\n        const auto& stages=DrawStages();")
    edit(ph, "        return *stages[u32(stage)];", "        return *DrawStages()[u32(stage)];")

    # Keep the scheduler's mutable state and recorder's single producer behind
    # the same FIFO handoff. Drain before locks that Stage B may itself need.
    edit(sh, "#include <condition_variable>", "#include <condition_variable>\n#include <functional>")
    edit(sh, "    void ClaimRecorder();", """    void SetDrawPipeDrain(std::function<void()> callback) { draw_pipe_drain=std::move(callback); }
    void DrainDrawPipe() const {
        static thread_local bool draining=false;
        if(draw_pipe_drain && !draining) {
            draining=true;
            draw_pipe_drain();
            draining=false;
        }
    }
    void ClaimRecorder();""")
    edit(sh, "    vk::CommandBuffer CommandBuffer() const {\n        return sessions.back().primary;",
         "    vk::CommandBuffer CommandBuffer() const {\n        DrainDrawPipe();\n        return sessions.back().primary;")
    edit(sh, "    void SubmitExecution(SubmitInfo& info);",
         "    std::function<void()> draw_pipe_drain;\n    void SubmitExecution(SubmitInfo& info);")
    for signature in ("void Scheduler::BeginRendering(const RenderState& new_state) {",
                      "void Scheduler::EndRendering() {", "vk::CommandBuffer Scheduler::UploadCommandBuffer() {",
                      "void Scheduler::Finish() {", "void Scheduler::Wait(u64 tick) {",
                      "void Scheduler::SubmitExecution(SubmitInfo& info) {"):
        edit(sc, signature, signature + "\n    DrainDrawPipe();")
    text=(src/sc).read_text()
    text,n=re.subn(r"(void Scheduler::PopPendingOperations\([^\)]*\) \{)",
                   r"\1\n    DrainDrawPipe();",text,count=1)
    if n!=1:raise RuntimeError("draw pipeline PopPendingOperations anchor")
    (src/sc).write_text(text)
    edit(rp, "    pipeline_cache.SetSrtSync([this](Shader::Info& info) {",
         "    scheduler.SetDrawPipeDrain([this]{liverpool->DrainDrawQueue();});\n    pipeline_cache.SetSrtSync([this](Shader::Info& info) {")
    edit(rp, "Rasterizer::~Rasterizer() = default;",
         """Rasterizer::~Rasterizer() {
    // Liverpool normally dies first (gnmdriver's global declaration order).
    if(draw_pipeline_attached)liverpool->DrainDrawQueue();
    scheduler.SetDrawPipeDrain({});
}""")

    # Only a real SRT download takes the recorder back. Locked range queries
    # stay on Stage A while read-only bindings run on Stage B.
    text = (src / rp).read_text()
    text = text.replace("            buffer_cache.TrackSrtSourcePage(page);",
                        "            liverpool->DrainDrawQueue();\n            buffer_cache.TrackSrtSourcePage(page);")
    (src / rp).write_text(text)
    tc = src / "video_core/texture_cache/texture_cache.cpp"
    text = tc.read_text()
    if "bool TextureCache::ResolveImageReadbacks(" in text:
        start = text.index("bool TextureCache::ResolveImageReadbacks(")
        end = text.index("void TextureCache::CancelImageReadbacks", start)
        block = text[start:end]
        anchor = "    const auto resolve=[&] {\n        std::scoped_lock lk{deferred_images_mutex};"
        if block.count(anchor) != 1:
            raise RuntimeError("draw pipeline image readback ownership anchor")
        block = block.replace(anchor, "    const auto resolve=[&] {\n        liverpool->DrainDrawQueue();\n        std::scoped_lock lk{deferred_images_mutex};")
        tc.write_text(text[:start] + block + text[end:])

    # Queued pipeline pointers live until every prior packet has consumed them.
    text = (src / pc).read_text()
    for anchor in ("void PipelineCache::ReclaimOrderGraphics() {",):
        if anchor in text:
            text = text.replace(anchor, anchor + "\n    liverpool->InvalidateDrawSnapshots();")
    text = re.sub(r"(std::optional<vk::ShaderModule> PipelineCache::ReplaceShader\([^\{]+\{)",
                  r"""\1
    if(!liverpool->OnDrawThread() &&
       std::this_thread::get_id()!=liverpool->GetGpuCommandProcessorThread()) {
        std::optional<vk::ShaderModule> result;
        liverpool->SendCommand<true>([&]{result=ReplaceShader(module,spv_code);});
        return result;
    }
    liverpool->InvalidateDrawSnapshots();""", text, count=1)
    (src / pc).write_text(text)
    edit("video_core/renderer_vulkan/vk_pipeline_serialization.cpp",
         '#include "video_core/renderer_vulkan/vk_pipeline_cache.h"',
         '#include "video_core/renderer_vulkan/vk_pipeline_cache.h"\n#include "video_core/renderer_vulkan/vk_scheduler.h"')
    edit("video_core/renderer_vulkan/vk_pipeline_serialization.cpp",
         "void PipelineCache::Sync() {", "void PipelineCache::Sync() {\n    scheduler.DrainDrawPipe();")
    edit("video_core/renderer_vulkan/vk_recorder.cpp",
         'LOG_INFO(Render_Vulkan, "cp_record_thread: thread {} takes over recording from {}",',
         'LOG_DEBUG(Render_Vulkan, "cp_record_thread: thread {} takes over recording from {}",')

    # Direct, indirect and compute packets all go through the same ownership.
    text = (src / lp).read_text()
    begin = text.index("Liverpool::Task Liverpool::ProcessGraphics(")
    tail = text[begin:]
    tail = tail.replace("rasterizer->DrawIndirect(", "QueueIndirectDraw(")
    tail = tail.replace("rasterizer->DispatchDirect()", "QueueDispatchDirect()")
    tail = tail.replace("rasterizer->DispatchIndirect(", "QueueDispatchIndirect(")
    text = text[:begin] + tail
    anchor = "            case PM4ItOpcode::SetBase:\n                break;"
    additions = ("DrawIndirect", "DrawIndirectMulti", "DrawIndirectCountMulti", "DrawIndexIndirect",
                 "DrawIndexIndirectMulti", "DrawIndexIndirectCountMulti", "DispatchDirect",
                 "DispatchIndirect", "EventWrite", "EventWriteEop", "EventWriteEos", "DmaData", "WriteData")
    if text.count(anchor) != 1:
        raise RuntimeError("draw pipeline PM4 allowlist anchor")
    text = text.replace(anchor, "            case PM4ItOpcode::SetBase:\n" +
                        "".join(f"            case PM4ItOpcode::{op}:\n" for op in additions) +
                        "                break;")
    text = text.replace("                if (opcode==PM4ItOpcode::EventWrite) draw_snapshot_valid=false;\n", "")
    # A queued write may target the following indirect PM4 stream itself.
    # Resolve writer packets before fetching any further guest command bytes.
    text = text.replace("    while (!dcb.empty()) {\n        ProcessCommands();",
                        "    while (!dcb.empty()) {\n        if(draw_pending_writes)DrainDrawQueue();\n        ProcessCommands();")
    compute_start=text.index("Liverpool::Task Liverpool::ProcessCompute(")
    compute=text[compute_start:]
    opcode_anchor="        switch (opcode) {"
    if compute.count(opcode_anchor)!=1:
        raise RuntimeError("draw pipeline compute opcode anchor")
    compute=compute.replace(opcode_anchor,"""        // ASC side effects are synchronous barriers. Only private register
        // updates and captured dispatches may run ahead of the GPU worker.
        switch(opcode) {
        case PM4ItOpcode::SetShReg:
        case PM4ItOpcode::DispatchDirect:
        case PM4ItOpcode::DispatchIndirect:
            break;
        default:
            DrainDrawQueue();
            break;
        }
        switch (opcode) {""")
    compute=compute.replace("    while (!acb.empty()) {", "    while (!acb.empty()) {\n        if(draw_pending_writes)DrainDrawQueue();")
    compute=compute.replace("std::memcpy(&regs.reg_array[Regs::ShRegWordOffset + set_data->reg_offset],\n                            header + 2, set_size);",
                            "CopyDrawRegs(Regs::ShRegWordOffset+set_data->reg_offset,header+2,set_size);")
    text=text[:compute_start]+compute
    (src / lp).write_text(text)
    _queue_side_effects(src / lp)

    return {"drawPipeline": "CP pipeline lookup and owned snapshots -> FIFO cache binding/recording",
            "defaults": "SotC on; The Order >=8 hardware threads; existing signal tracker",
            "ordering": "owned direct/indirect/compute and memory/fence tasks; drain before reads/CE/callbacks",
            "lifetime": "Info+V# snapshots, owned PM4 payloads, pipeline eviction/replacement drain",
            "recorder": "single producer, scheduler hook before state/lock access",
            "cpuBackend": "Bionic/FEX unchanged; UFFD remains serial"}


def _queue_side_effects(path):
    text = path.read_text()
    start = text.index("Liverpool::Task Liverpool::ProcessGraphics(")
    prefix, text = text[:start], text[start:]
    def case(op, replacement):
        nonlocal text
        first = text.index(f"            case PM4ItOpcode::{op}: {{")
        last = text.index("            case PM4ItOpcode::", first + 30)
        original = text[first:last]
        text = text[:first] + replacement(original) + text[last:]
    for op, typ, name in (("EventWriteEop", "PM4CmdEventWriteEop", "event_eop"),
                          ("EventWriteEos", "PM4CmdEventWriteEos", "event_eos")):
        def wrap(original, op=op, typ=typ, name=name):
            declaration = f"                const auto* {name} = reinterpret_cast<const {typ}*>(header);"
            if original.count(declaration) != 1:
                raise RuntimeError(f"draw pipeline {op} payload anchor")
            body = original.split(declaration, 1)[1]
            suffix = "                break;\n            }\n"
            if not body.endswith(suffix):
                raise RuntimeError(f"draw pipeline {op} body")
            body = body[:-len(suffix)]
            return (f"            case PM4ItOpcode::{op}: {{\n"
                    f"                const auto value=*reinterpret_cast<const {typ}*>(header);\n"
                    f"                QueueGpuTask([this,value] {{\n"
                    f"                    const auto* {name}=&value;" + body +
                    "                });\n                break;\n            }\n")
        case(op, wrap)
    def dma(original):
        anchor = "                ASSERT(dma_data->command.das == 0);"
        body = original[original.index(anchor):]
        suffix = "                break;\n            }\n"
        body = body[:-len(suffix)]
        return ("            case PM4ItOpcode::DmaData: {\n"
                "                const auto value=*reinterpret_cast<const PM4DmaData*>(header);\n"
                "                if(value.dst_addr_lo==0x3022C || !rasterizer)break;\n"
                "                QueueGpuTask([this,value] {\n"
                "                    const auto* dma_data=&value;\n" + body +
                "                });\n                break;\n            }\n")
    case("DmaData", dma)
    case("WriteData", lambda _: WRITE_DATA_CASE)
    case("EventWrite", lambda _: EVENT_WRITE_CASE)
    path.write_text(prefix + text)


SNAPSHOT_HEADER = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>
namespace BachataDrawPipe {
// Metadata belongs to a stable compiled permutation. Reuse its storage within
// the ring; copy every mutable field on each publication. Invalidate() is called
// after draining before an Info or pipeline can be replaced/reclaimed.
template<class Info,std::size_t Count> struct Snapshots {
    std::array<Info,Count> values{};
    std::array<const Info*,Count> origins{};
    std::array<const Info*,Count> pointers{};
    std::array<std::vector<std::uint32_t>,Count> words;
    void Invalidate() { origins.fill(nullptr); }
    void Capture(std::span<const Info* const> stages) {
        pointers.fill(nullptr);
        for(const Info* source:stages) {
            if(!source)continue;
            const auto slot=static_cast<std::size_t>(source->sw_stage);
            assert(slot<Count);
            auto& value=values[slot];
            if(origins[slot]!=source) { value=*source;origins[slot]=source; }
            value.params.reset();
            words[slot].assign(source->user_data.begin(),source->user_data.end());
            value.user_data=words[slot];
            value.pgm_base=source->pgm_base;
            value.flattened_ud_buf=source->flattened_ud_buf;
            value.srt_guest_sources=source->srt_guest_sources;
            value.sharp_tables=source->sharp_tables;
            pointers[slot]=&value;
        }
    }
};
} // namespace BachataDrawPipe
'''

PIPELINE_OVERRIDE = r'''    using DrawStageArray=std::array<const Shader::Info*,Shader::MaxStageTypes>;
    class ScopedDrawStages {
    public:
        ScopedDrawStages(const Pipeline* owner,const DrawStageArray& captured)
            : previous_owner{draw_owner},previous_stages{draw_stages} {
            draw_owner=owner;draw_stages=&captured;
        }
        ~ScopedDrawStages() { draw_owner=previous_owner;draw_stages=previous_stages; }
        ScopedDrawStages(const ScopedDrawStages&)=delete;
    private:
        const Pipeline* previous_owner;
        const DrawStageArray* previous_stages;
    };
    const DrawStageArray& DrawStages() const {
        return draw_owner==this && draw_stages?*draw_stages:stages;
    }
    inline static thread_local const Pipeline* draw_owner{};
    inline static thread_local const DrawStageArray* draw_stages{};
'''

PREPARE_IMPLEMENTATION = r'''const Pipeline* Rasterizer::PrepareDrawPipeline(bool compute,const DrawIndirectParams& params) {
    if(compute)return pipeline_cache.GetComputePipeline();
    const auto& regs=liverpool->DrawRegs();
    using Mode=AmdGpu::ColorControl::OperationMode;
    if(regs.color_control.mode==Mode::EliminateFastClear ||
       regs.color_control.mode==Mode::FmaskDecompress ||
       regs.color_control.mode==Mode::Resolve ||
       regs.primitive_type==AmdGpu::PrimitiveType::None)return nullptr;
    const bool depth_copy=regs.depth_render_override.force_z_dirty &&
        regs.depth_render_override.force_z_valid && regs.depth_buffer.DepthValid() &&
        regs.depth_buffer.DepthWriteValid() &&
        regs.depth_buffer.DepthAddress()!=regs.depth_buffer.DepthWriteAddress();
    const bool stencil_copy=regs.depth_render_override.force_stencil_dirty &&
        regs.depth_render_override.force_stencil_valid && regs.depth_buffer.StencilValid() &&
        regs.depth_buffer.StencilWriteValid() &&
        regs.depth_buffer.StencilAddress()!=regs.depth_buffer.StencilWriteAddress();
    if(regs.color_control.mode==Mode::Disable && (depth_copy||stencil_copy))return nullptr;
    return pipeline_cache.GetGraphicsPipeline(params);
}
'''

QUEUE_IMPLEMENTATION = r'''bool Liverpool::DrawPipelineEnabled() const {
    if(draw_policy_logged)return draw_policy_enabled;
    const auto cpus=std::thread::hardware_concurrency();
    const bool uffd=EmulatorSettings.IsUserfaultfdTracking();
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const char* reason="unrelated_title";
    bool enabled=false;
    if(!rasterizer)reason="renderer_unavailable";
    else if(!rasterizer->CanPipelineDraw())reason="debug_marker_ordering";
    else if(uffd)reason="uffd_owner_contract";
    else if(serial=="CUSA08809" || serial=="CUSA08034") {
        const char* option=std::getenv("SOTC_CP_THREADS");
        enabled=!option || option[0]!='0';
        reason=enabled?(option?"environment_enabled":"sotc_default"):"environment_disabled";
    } else if(serial=="CUSA00785") {
        const char* option=std::getenv("ORDER1886_DRAW_PIPE");
        enabled=option && option[0]?option[0]=='1':cpus>=8;
        reason=option && option[0]?(enabled?"environment_enabled":"environment_disabled"):
            (enabled?"order_cpu_default":"fewer_than_8_cpus");
    }
    // The Vulkan recorder is an independent stage and never disables this one.
    LOG_INFO(Render_Vulkan,
        "BACHATA_DRAW_PIPELINE enabled={} reason={} cpus={} backend=FEX tracking={} recorder={}",
        enabled,reason,cpus,uffd?"uffd":"signals",
        rasterizer && rasterizer->GetScheduler().HasRecordThread());
    draw_policy_enabled=enabled;draw_policy_logged=true;
    return enabled;
}
void Liverpool::StartDrawWorker() {
    if(draw_worker.joinable())return;
    draw_worker=std::jthread([this](std::stop_token stop){DrawLoop(stop);});
}
void Liverpool::DrawLoop(std::stop_token stop) {
    draw_owner=this;
    Common::SetCurrentThreadName("shadPS4:GpuDraw");
    for(;;) {
        std::unique_lock lk{draw_mutex};
        draw_cv.wait(lk,[&]{return draw_head!=draw_tail||stop.stop_requested();});
        if(draw_head==draw_tail)break;
        auto& op=draw_ring[draw_tail%DrawQueueCapacity];
        lk.unlock();
        rasterizer->GetScheduler().ClaimRecorder();
        if(op.kind==DrawPacket::Kind::Function) {
            op.task();
            op.task={};
        } else {
            for(const auto& chunk:op.chunks)
                std::memcpy(&back_regs.reg_array[chunk.index*DrawChunkWords],
                            chunk.words.data(),sizeof(chunk.words));
            back_cb_extent=op.cb;back_db_extent=op.db;back_cs=op.cs;
            back_vertices=op.vertices;
            Vulkan::Pipeline::ScopedDrawStages snapshot{op.pipeline,op.stages.pointers};
            using Kind=DrawPacket::Kind;
            if(op.kind==Kind::Draw) {
                rasterizer->Draw(op.indexed,op.offset,
                                 static_cast<const Vulkan::GraphicsPipeline*>(op.pipeline),true);
            } else if(op.kind==Kind::Indirect) {
                rasterizer->DrawIndirect(op.indexed,op.arg_address,op.offset,op.stride,
                    op.max_count,op.count_address,op.vertex_sgpr,op.instance_sgpr,
                    static_cast<const Vulkan::GraphicsPipeline*>(op.pipeline),true);
            } else if(op.kind==Kind::Dispatch) {
                rasterizer->DispatchDirect(static_cast<const Vulkan::ComputePipeline*>(op.pipeline),true);
            } else {
                rasterizer->DispatchIndirect(op.arg_address,op.offset,op.stride,
                    static_cast<const Vulkan::ComputePipeline*>(op.pipeline),true);
            }
            back_vertices={};
        }
        lk.lock();
        ++draw_tail;
        lk.unlock();
        draw_cv.notify_all();
    }
    draw_owner=nullptr;
}
void Liverpool::DrainDrawQueue() {
    if(!draw_worker.joinable() || OnDrawThread() || !draw_back_owns_recorder)return;
    {
        std::unique_lock lk{draw_mutex};
        draw_cv.wait(lk,[&]{return draw_head==draw_tail;});
    }
    rasterizer->GetScheduler().ClaimRecorder();
    draw_back_owns_recorder=false;
    draw_pending_writes=false;
}
void Liverpool::InvalidateDrawSnapshots() {
    DrainDrawQueue();
    for(auto& packet:draw_ring)packet.stages.Invalidate();
}
void Liverpool::QueueGpuTask(Common::UniqueFunction<void>&& task) {
    if(!DrawPipelineEnabled()) { DrainDrawQueue();task();return; }
    StartDrawWorker();
    std::unique_lock lk{draw_mutex};
    draw_cv.wait(lk,[&]{return draw_head-draw_tail<DrawQueueCapacity;});
    auto& op=draw_ring[draw_head%DrawQueueCapacity];
    op.kind=DrawPacket::Kind::Function;
    op.task=std::move(task);
    ++draw_head;
    draw_pending_writes=true;
    draw_back_owns_recorder=true;
    lk.unlock();draw_cv.notify_one();
}
void Liverpool::QueueDirectDraw(const char* marker,const void* address,bool indexed,u32 offset) {
    QueueDrawOperation(DrawPacket::Kind::Draw,marker,address,indexed,offset);
}
void Liverpool::QueueIndirectDraw(bool indexed,VAddr args,u32 offset,u32 stride,u32 max_count,
                                 VAddr count_address,u16 vertex_sgpr,u16 instance_sgpr) {
    QueueDrawOperation(DrawPacket::Kind::Indirect,"gfx:indirect",nullptr,indexed,offset,
                       args,stride,max_count,count_address,vertex_sgpr,instance_sgpr);
}
void Liverpool::QueueDispatchDirect() {
    QueueDrawOperation(DrawPacket::Kind::Dispatch,"gfx:dispatch",nullptr,false,0);
}
void Liverpool::QueueDispatchIndirect(VAddr args,u32 offset,u32 size) {
    QueueDrawOperation(DrawPacket::Kind::IndirectDispatch,"gfx:dispatch_indirect",nullptr,
                       false,offset,args,size);
}
void Liverpool::QueueDrawOperation(DrawPacket::Kind kind,const char* marker,const void* address,
    bool indexed,u32 offset,VAddr args,u32 stride,u32 max_count,VAddr count_address,
    u16 vertex_sgpr,u16 instance_sgpr) {
    using Kind=DrawPacket::Kind;
    if(!DrawPipelineEnabled()) {
        DrainDrawQueue();
        if(kind==Kind::Draw) {
            rasterizer->ScopeMarker(marker,fmt::make_format_args(address),
                                    [&]{rasterizer->Draw(indexed,offset);});
        } else if(kind==Kind::Indirect) {
            rasterizer->DrawIndirect(indexed,args,offset,stride,max_count,count_address,
                                     vertex_sgpr,instance_sgpr);
        } else if(kind==Kind::Dispatch)rasterizer->DispatchDirect();
        else rasterizer->DispatchIndirect(args,offset,stride);
        return;
    }
    // The next SRT walk can depend on storage/image/DMA writes queued so far.
    // Resolve those first, including work not yet marked in the page tracker.
    if(draw_pending_writes)DrainDrawQueue();
    const bool compute=kind==Kind::Dispatch || kind==Kind::IndirectDispatch;
    const Vulkan::DrawIndirectParams params{
        .vertex_sgpr_offset=vertex_sgpr,.instance_sgpr_offset=instance_sgpr,
        .indirect=kind==Kind::Indirect};
    const auto* pipeline=rasterizer->PrepareDrawPipeline(compute,params);
    // Pointed V# descriptors are also PM4-time state, not just their SGPR pointer.
    // Resolve them outside draw_mutex: a protected descriptor can fault and drain.
    std::array<AmdGpu::Buffer,Vulkan::MaxVertexBufferCount> vertex_sharps{};
    size_t vertex_count=0;
    if(pipeline && !compute) {
        const auto* graphics=static_cast<const Vulkan::GraphicsPipeline*>(pipeline);
        const auto& info=graphics->GetStage(Shader::SwStage::Vertex);
        for(const auto& attribute:graphics->GetFetchShader().attributes) {
            ASSERT(vertex_count<vertex_sharps.size());
            vertex_sharps[vertex_count++]=attribute.GetSharp(info);
        }
    }
    StartDrawWorker();
    std::unique_lock lk{draw_mutex};
    draw_cv.wait(lk,[&]{return draw_head-draw_tail<DrawQueueCapacity;});
    auto& op=draw_ring[draw_head%DrawQueueCapacity];
    op.kind=kind;op.pipeline=pipeline;op.task={};
    op.stages.pointers.fill(nullptr);
    if(pipeline)op.stages.Capture(pipeline->GetStages());
    op.vertices.assign(vertex_sharps.begin(),vertex_sharps.begin()+vertex_count);
    op.arg_address=args;op.count_address=count_address;
    op.stride=stride;op.max_count=max_count;
    op.vertex_sgpr=vertex_sgpr;op.instance_sgpr=instance_sgpr;
    op.chunks.clear();
    if(!draw_snapshot_valid) {
        op.chunks.reserve(DrawChunkCount);
        for(u32 i=0;i<DrawChunkCount;++i) {
            auto& chunk=op.chunks.emplace_back();chunk.index=i;
            std::memcpy(chunk.words.data(),&regs.reg_array[i*DrawChunkWords],sizeof(chunk.words));
        }
        draw_snapshot_valid=true;
    } else {
        for(const auto i:draw_dirty_indices) {
            auto& chunk=op.chunks.emplace_back();chunk.index=i;
            std::memcpy(chunk.words.data(),&regs.reg_array[i*DrawChunkWords],sizeof(chunk.words));
        }
    }
    draw_dirty.reset();draw_dirty_indices.clear();
    op.cb=last_cb_extent;op.db=last_db_extent;op.cs=GetCsRegs();
    op.address=address;op.marker=marker;op.indexed=indexed;op.offset=offset;
    if(pipeline)for(const auto* stage:pipeline->GetStages())if(stage) {
        draw_pending_writes|=stage->uses_dma || stage->has_storage_images;
        for(const auto& buffer:stage->buffers)draw_pending_writes|=buffer.is_written;
        for(const auto& image:stage->images)draw_pending_writes|=image.is_written;
    }
    draw_pending_writes|=compute || !pipeline;
    ++draw_head;draw_back_owns_recorder=true;
    lk.unlock();draw_cv.notify_one();
}
'''

WRITE_DATA_CASE = r'''            case PM4ItOpcode::WriteData: {
                const auto* data=reinterpret_cast<const PM4CmdWriteData*>(header);
                ASSERT(data->dst_sel.Value()==2 || data->dst_sel.Value()==5);
                ASSERT(!data->wr_one_addr.Value());
                const u32 words=header->type3.count.Value()-2;
                const VAddr address=data->Address<VAddr>();
                std::vector<u32> owned(data->data,data->data+words);
                QueueGpuTask([this,address,owned=std::move(owned)] {
                    if(rasterizer)rasterizer->OnFence();
                    std::memcpy(reinterpret_cast<void*>(address),owned.data(),owned.size()*sizeof(u32));
                });
                break;
            }
'''

EVENT_WRITE_CASE = r'''            case PM4ItOpcode::EventWrite: {
                const auto* event=reinterpret_cast<const PM4CmdEventWrite*>(header);
                if(event->event_type.Value()==EventType::SoVgtStreamoutFlush) {
                    regs.cp_strmout_cntl.offset_update_done=1;
                    MarkDrawBytes(&regs.cp_strmout_cntl,sizeof(regs.cp_strmout_cntl));
                } else if(event->event_index.Value()==EventIndex::ZpassDone &&
                          event->event_type.Value()==EventType::PixelPipeStatDump) {
                    const VAddr address=event->Address<VAddr>();
                    const auto value=pixel_counter|0x8000000000000000ULL;
                    const auto pairs=num_counter_pairs;
                    pixel_counter+=0x2FFFFFFULL;
                    QueueGpuTask([address,value,pairs] {
                        auto* result=reinterpret_cast<u64*>(address);
                        for(u32 i=0;i<pairs;++i,result+=2)*result=value;
                    });
                }
                break;
            }
'''
