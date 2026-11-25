"""Separate SotC PM4 register decoding from direct-draw preparation.

Ordered SPSC queue with dirty register chunks, captured CB/DB and CS state.
Drain before non-register commands, CE, compute, callbacks, flips and yields.
Only enable on the existing signal-based page tracker; UFFD is left serial.
"""
from pathlib import Path
import re
def apply(root):
    def edit(rel,a,b,n=1):
        p=root/"src"/rel;s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f"SotC draw pipe {rel}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    lp="video_core/amdgpu/liverpool.cpp"
    lh="video_core/amdgpu/liverpool.h"
    rp="video_core/renderer_vulkan/vk_rasterizer.cpp"
    rh="video_core/renderer_vulkan/vk_rasterizer.h"
    edit(lh,"#include <condition_variable>","#include <condition_variable>\n#include <bitset>")
    edit(lh,"    template <bool wait_done = false>\n    void SendCommand(auto&& func) {",
         """    bool OnDrawThread() const { return draw_owner==this; }
    Regs& DrawRegs() { return OnDrawThread()?back_regs:regs; }
    const auto& DrawCbExtent() const { return OnDrawThread()?back_cb_extent:last_cb_extent; }
    const auto& DrawDbExtent() const { return OnDrawThread()?back_db_extent:last_db_extent; }
    bool PrepareGpuSideFault() {
        if (OnDrawThread()) return true;
        if (std::this_thread::get_id()==gpu_id) {
            DrainDrawQueue();
            return true;
        }
        return false;
    }

    template <bool wait_done = false>
    void SendCommand(auto&& func) {
        if constexpr (wait_done) {
            if (OnDrawThread()) { func(); return; }
            if (std::this_thread::get_id()==gpu_id) {
                DrainDrawQueue();
                func();
                return;
            }
        }""")
    edit(lh,"        return mapped_queues[curr_qid].cs_state;",
         "        return OnDrawThread()?back_cs:mapped_queues[curr_qid].cs_state;")
    edit(lh,"    std::jthread process_thread{};",
         """    // One producer (CP), one consumer (draw preparation). The Vulkan
    // recorder still has exactly one owner at a time; drains hand it back.
    static constexpr u32 DrawChunkWords=32, DrawQueueCapacity=32;
    static constexpr u32 DrawChunkCount=Regs::NumRegs/DrawChunkWords;
    static_assert(Regs::NumRegs%DrawChunkWords==0);
    struct DrawChunk {
        u32 index{};
        std::array<u32,DrawChunkWords> words{};
    };
    struct DrawPacket {
        std::vector<DrawChunk> chunks;
        std::array<CbDbExtent,NUM_COLOR_BUFFERS> cb;
        CbDbExtent db;
        ComputeProgram cs;
        const void* address{};
        const char* marker{};
        bool indexed{};
        u32 offset{};
    };
    inline static thread_local Liverpool* draw_owner{};
    Regs back_regs{};
    std::array<CbDbExtent,NUM_COLOR_BUFFERS> back_cb_extent{};
    CbDbExtent back_db_extent{};
    ComputeProgram back_cs{};
    std::bitset<DrawChunkCount> draw_dirty{};
    std::vector<u32> draw_dirty_indices;
    bool draw_snapshot_valid{}, draw_back_owns_recorder{};
    std::array<DrawPacket,DrawQueueCapacity> draw_ring{};
    u64 draw_head{},draw_tail{};
    std::mutex draw_mutex;
    std::condition_variable draw_cv;
    std::jthread draw_worker;
    void MarkDrawWords(u32 first,u32 count);
    void MarkDrawBytes(const void* p,size_t bytes);
    void CopyDrawRegs(u32 first,const void* p,size_t bytes);
    void QueueDirectDraw(const char* marker,const void* address,bool indexed,u32 offset=0);
    void DrainDrawQueue();
    void DrawLoop(std::stop_token stop);

    std::jthread process_thread{};""")
    edit(lp,"    process_thread.join();\n    while (!ce_submits.empty())",
         """    process_thread.join();
    if(draw_worker.joinable()) {
        draw_worker.request_stop();
        draw_cv.notify_all();
        draw_worker.join();
    }
    while (!ce_submits.empty())""")
    edit(lp,"// BACHATA_RELEASE026_CE_QUEUE_PARITY: CE executes independently from DE.",
         """void Liverpool::MarkDrawWords(u32 first,u32 count) {
    if (!draw_snapshot_valid || !count) return;
    ASSERT(first<Regs::NumRegs && count<=Regs::NumRegs-first);
    const u32 end=(first+count-1)/DrawChunkWords;
    for(u32 i=first/DrawChunkWords;i<=end;++i) {
        if(!draw_dirty.test(i)) {
            draw_dirty.set(i);
            draw_dirty_indices.push_back(i);
        }
    }
}
void Liverpool::MarkDrawBytes(const void* p,size_t bytes) {
    const auto offset=reinterpret_cast<const u8*>(p)-reinterpret_cast<const u8*>(&regs);
    ASSERT(offset>=0 && offset%sizeof(u32)==0 && bytes%sizeof(u32)==0);
    MarkDrawWords(offset/sizeof(u32),bytes/sizeof(u32));
}
void Liverpool::CopyDrawRegs(u32 first,const void* p,size_t bytes) {
    // Repeated SET_* packets often carry values already in the register file.
    // Only mark changed chunks, so the consumer receives the actual deltas.
    auto* dst=&regs.reg_array[first];
    if (std::memcmp(dst,p,bytes)!=0) {
        MarkDrawWords(first,bytes/sizeof(u32));
        std::memcpy(dst,p,bytes);
    }
}
void Liverpool::DrawLoop(std::stop_token stop) {
    draw_owner=this;
    Common::SetCurrentThreadName("shadPS4:GpuDraw");
    for(;;) {
        std::unique_lock lk{draw_mutex};
        draw_cv.wait(lk,[&]{return draw_head!=draw_tail||stop.stop_requested();});
        if(draw_head==draw_tail) break;
        auto& op=draw_ring[draw_tail%DrawQueueCapacity];
        lk.unlock();
        for(const auto& chunk:op.chunks) {
            std::memcpy(&back_regs.reg_array[chunk.index*DrawChunkWords],
                        chunk.words.data(),sizeof(chunk.words));
        }
        back_cb_extent=op.cb;back_db_extent=op.db;back_cs=op.cs;
        rasterizer->GetScheduler().ClaimRecorder();
        rasterizer->ScopeMarker(op.marker,fmt::make_format_args(op.address),
                               [&]{rasterizer->Draw(op.indexed,op.offset);});
        lk.lock();
        ++draw_tail;
        lk.unlock();
        draw_cv.notify_all();
    }
    draw_owner=nullptr;
}
void Liverpool::DrainDrawQueue() {
    if (!draw_worker.joinable() || OnDrawThread()) return;
    if (!draw_back_owns_recorder) return;
    {
        std::unique_lock lk{draw_mutex};
        draw_cv.wait(lk,[&]{return draw_head==draw_tail;});
    }
    rasterizer->GetScheduler().ClaimRecorder();
    draw_back_owns_recorder=false;
}
void Liverpool::QueueDirectDraw(const char* marker,const void* address,bool indexed,u32 offset) {
    // Regression recovery: PM4 and draw preparation must share a single
    // producer until side-effect boundaries no longer force per-draw handoffs.
    // The Vulkan recording thread remains active; no draws are skipped.
    constexpr bool ordered_draw_worker_verified=false;
    if (!ordered_draw_worker_verified || !BachataSotcLod::Enabled() ||
        EmulatorSettings.IsUserfaultfdTracking()) {
        rasterizer->ScopeMarker(marker,fmt::make_format_args(address),
                                [&]{rasterizer->Draw(indexed,offset);});
        return;
    }
    if(!draw_worker.joinable()) {
        draw_worker=std::jthread([this](std::stop_token stop){DrawLoop(stop);});
        LOG_INFO(Render_Vulkan,"BACHATA_SOTC_DRAW_PIPE: direct draws, dirty register chunks, ordered drains");
    }
    std::unique_lock lk{draw_mutex};
    draw_cv.wait(lk,[&]{return draw_head-draw_tail<DrawQueueCapacity;});
    auto& op=draw_ring[draw_head%DrawQueueCapacity];
    op.chunks.clear();
    if (!draw_snapshot_valid) {
        // A full snapshot is only taken at a synchronization boundary.
        // Subsequent draws copy changed register chunks.
        op.chunks.reserve(DrawChunkCount);
        for(u32 i=0;i<DrawChunkCount;++i) {
            auto& chunk=op.chunks.emplace_back();
            chunk.index=i;
            std::memcpy(chunk.words.data(),&regs.reg_array[i*DrawChunkWords],sizeof(chunk.words));
        }
        draw_snapshot_valid=true;
    } else {
        for(const auto i:draw_dirty_indices) {
            auto& chunk=op.chunks.emplace_back();
            chunk.index=i;
            std::memcpy(chunk.words.data(),&regs.reg_array[i*DrawChunkWords],sizeof(chunk.words));
        }
    }
    draw_dirty.reset();draw_dirty_indices.clear();
    op.cb=last_cb_extent;op.db=last_db_extent;
    op.cs=mapped_queues[GfxQueueId].cs_state;
    op.address=address;op.marker=marker;op.indexed=indexed;op.offset=offset;
    ++draw_head;
    draw_back_owns_recorder=true;
    lk.unlock();
    draw_cv.notify_one();
}

// BACHATA_RELEASE026_CE_QUEUE_PARITY: CE executes independently from DE.""")
    # No queued draw may overlap a CE update, a guest callback or a queue switch.
    edit(lp,"    task.resume();\n    if (task.done()) {",
         "    DrainDrawQueue();\n    task.resume();\n    if (task.done()) {")
    edit(lp,"    while (num_commands) {\n        Common::UniqueFunction",
         "    while (num_commands) {\n        DrainDrawQueue();\n        draw_snapshot_valid=false;\n        Common::UniqueFunction")
    edit(lp,"            task.resume();\n\n            if (task.done())",
         "            task.resume();\n            DrainDrawQueue();\n\n            if (task.done())")
    edit(lp,"        if (submit_done) {\n            VideoCore::EndCapture();",
         "        DrainDrawQueue();\n        if (submit_done) {\n            VideoCore::EndCapture();")
    edit(lp,"    FIBER_ENTER(acb_task_name[vqid]);",
         "    DrainDrawQueue();\n    draw_snapshot_valid=false;\n    FIBER_ENTER(acb_task_name[vqid]);")
    edit(lp,"    // BACHATA_RELEASE026_OWNED_DCB_CCB: keep both PM4 vectors alive across",
         "    DrainDrawQueue();\n    // BACHATA_RELEASE026_OWNED_DCB_CCB: keep both PM4 vectors alive across")
    # PM4 register-only packets and direct draws can proceed while the consumer
    # works. Everything else conservatively drains first. NOP extent hints
    # have no side effect; real flip and marker NOPs drain in their case.
    edit(lp,"            const PM4ItOpcode opcode = header->type3.opcode;\n            switch (opcode) {\n            case PM4ItOpcode::Nop:",
         """            const PM4ItOpcode opcode = header->type3.opcode;
            switch(opcode) {
            case PM4ItOpcode::Nop:
            case PM4ItOpcode::ContextControl:
            case PM4ItOpcode::ClearState:
            case PM4ItOpcode::SetConfigReg:
            case PM4ItOpcode::SetContextReg:
            case PM4ItOpcode::SetShReg:
            case PM4ItOpcode::SetUconfigReg:
            case PM4ItOpcode::IndexType:
            case PM4ItOpcode::DrawIndex2:
            case PM4ItOpcode::DrawIndexOffset2:
            case PM4ItOpcode::DrawIndexAuto:
            case PM4ItOpcode::NumInstances:
            case PM4ItOpcode::IndexBase:
            case PM4ItOpcode::IndexBufferSize:
            case PM4ItOpcode::SetBase:
                break;
            default:
                DrainDrawQueue();
                if (opcode==PM4ItOpcode::EventWrite) draw_snapshot_valid=false;
                break;
            }
            switch (opcode) {
            case PM4ItOpcode::Nop:""")
    for kind in ("PatchedFlip","DebugMarkerPush","DebugColorMarkerPush","DebugMarkerPop"):
        edit(lp,f"                case PM4CmdNop::PayloadType::{kind}: {{",
             f"                case PM4CmdNop::PayloadType::{kind}: {{\n                    DrainDrawQueue();")
    edit(lp,"                regs.SetDefaults();",
         "                regs.SetDefaults();\n                draw_snapshot_valid=false;")
    edit(lp,"std::memcpy(&regs.reg_array[reg_addr], payload, (count - 1) * sizeof(u32));",
         "CopyDrawRegs(reg_addr,payload,(count-1)*sizeof(u32));",2)
    edit(lp,"std::memcpy(&regs.reg_array[Regs::ShRegWordOffset + set_data->reg_offset],\n                                header + 2, set_size);",
         "CopyDrawRegs(Regs::ShRegWordOffset+set_data->reg_offset,header+2,set_size);")
    edit(lp,"std::memcpy(&regs.reg_array[Regs::UconfigRegWordOffset + set_data->reg_offset],\n                            header + 2, (count - 1) * sizeof(u32));",
         "CopyDrawRegs(Regs::UconfigRegWordOffset+set_data->reg_offset,header+2,(count-1)*sizeof(u32));")
    edit(lp,"                regs.index_buffer_type.raw = index_type->raw;",
         "                regs.index_buffer_type.raw = index_type->raw;\n                MarkDrawBytes(&regs.index_buffer_type,sizeof(regs.index_buffer_type));")
    edit(lp,"                regs.num_instances.num_instances = num_instances->num_instances;",
         "                regs.num_instances.num_instances = num_instances->num_instances;\n                MarkDrawBytes(&regs.num_instances,sizeof(regs.num_instances));")
    edit(lp,"                regs.index_base_address.base_addr_hi = index_base->addr_hi;",
         "                regs.index_base_address.base_addr_hi = index_base->addr_hi;\n                MarkDrawBytes(&regs.index_base_address,sizeof(regs.index_base_address));")
    edit(lp,"                regs.num_indices = index_size->num_indices;",
         "                regs.num_indices = index_size->num_indices;\n                MarkDrawBytes(&regs.num_indices,sizeof(regs.num_indices));")
    edit(lp,"                rasterizer->ScopeMarker(\"gfx:{}:DrawIndex2\", fmt::make_format_args(cmd_address),\n                                        [&] { rasterizer->Draw(true); });",
         """                MarkDrawBytes(&regs.max_index_size,sizeof(regs.max_index_size));
                MarkDrawBytes(&regs.index_base_address,sizeof(regs.index_base_address));
                MarkDrawBytes(&regs.num_indices,sizeof(regs.num_indices));
                MarkDrawBytes(&regs.draw_initiator,sizeof(regs.draw_initiator));
                QueueDirectDraw("gfx:{}:DrawIndex2",cmd_address,true);""")
    edit(lp,"                rasterizer->ScopeMarker(\n                    \"gfx:{}:DrawIndexOffset2\", fmt::make_format_args(cmd_address),\n                    [&] { rasterizer->Draw(true, draw_index_off->index_offset); });",
         """                MarkDrawBytes(&regs.max_index_size,sizeof(regs.max_index_size));
                MarkDrawBytes(&regs.num_indices,sizeof(regs.num_indices));
                MarkDrawBytes(&regs.draw_initiator,sizeof(regs.draw_initiator));
                QueueDirectDraw("gfx:{}:DrawIndexOffset2",cmd_address,true,draw_index_off->index_offset);""")
    edit(lp,"                rasterizer->ScopeMarker(\"gfx:{}:DrawIndexAuto\", fmt::make_format_args(cmd_address),\n                                        [&] { rasterizer->Draw(false); });",
         """                MarkDrawBytes(&regs.num_indices,sizeof(regs.num_indices));
                MarkDrawBytes(&regs.draw_initiator,sizeof(regs.draw_initiator));
                QueueDirectDraw("gfx:{}:DrawIndexAuto",cmd_address,false);""")
    # GPU-side fault handlers must not queue callbacks to the CP while the CP
    # waits for the draw worker, and the front must drain before touching GPU state.
    edit(rh,"    std::thread::id GetGpuCommandProcessorThread();",
         "    bool PrepareGpuSideFault();\n    std::thread::id GetGpuCommandProcessorThread();")
    edit(rp,"std::thread::id Rasterizer::GetGpuCommandProcessorThread() {",
         """bool Rasterizer::PrepareGpuSideFault() { return liverpool->PrepareGpuSideFault(); }
std::thread::id Rasterizer::GetGpuCommandProcessorThread() {""")
    edit("video_core/page_manager.cpp","const auto is_gpu_thread =\n            std::this_thread::get_id() == rasterizer->GetGpuCommandProcessorThread();",
         "const auto is_gpu_thread = rasterizer->PrepareGpuSideFault();")
    for rel in (rp,"video_core/renderer_vulkan/vk_pipeline_cache.cpp"):
        p=root/"src"/rel;s=p.read_text()
        s=s.replace("liverpool->regs","liverpool->DrawRegs()")
        s=s.replace("liverpool->last_cb_extent","liverpool->DrawCbExtent()")
        s=s.replace("liverpool->last_db_extent","liverpool->DrawDbExtent()")
        p.write_text(s)
    # The guest's temporary 1080p video-out surface is not the Android
    # presentation allocation. Preserve the initial AHB output extent and
    # existing scaling; actual window resize still takes the standard path.
    edit("video_core/renderer_vulkan/vk_presenter.cpp",
         "    if(is_game_frame)swapchain.SetGameExtent(frame->width,frame->height);",
         "    // SotC: preserve the configured Android AHB output extent.")
    return {"ordered_draw_queue":"single PM4 producer for regression recovery; Vulkan recorder retained",
            "synchronization":"drain at side effects, callbacks, CE/compute, flips; signal tracker aware",
            "fallback":"serial on other games and UFFD"}
