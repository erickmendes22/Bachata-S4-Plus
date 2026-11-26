#!/usr/bin/env python3
"""Run the effective FIFO/packet methods with deterministic GPU-side blocking.

The test compiles Liverpool's actual queue/draw/drain implementation, the
generated snapshot template and Pipeline's actual scoped stage selection.
Only rendering and PM4 structures are small substitutes; the concurrency,
publication, snapshot and producer-handoff code is the code built in the core.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
args = parser.parse_args()
subprocess.run([sys.executable, str(Path(__file__).with_name("test_donor_pm4_indirect.py")),
                "--source", args.source], check=True)
src = Path(args.source).resolve() / "src"
lp = (src / "video_core/amdgpu/liverpool.cpp").read_text()
lh = (src / "video_core/amdgpu/liverpool.h").read_text()
ph = (src / "video_core/renderer_vulkan/vk_pipeline_common.h").read_text()
methods = lp[lp.index("void Liverpool::MarkDrawWords("):lp.index("// BACHATA_RELEASE026_CE_QUEUE_PARITY")]
members = lh[lh.index("    static constexpr u32 DrawChunkWords"):lh.index("    std::jthread process_thread{};")]
pipeline = ph[ph.index("    using DrawStageArray="):ph.index("    bool IsCompute() const")]

# Guard the edges not invoked by the fake Vulkan renderer below.
assert "const auto value=*reinterpret_cast<const PM4CmdEventWriteEop*>(header);" in lp
assert "const auto value=*reinterpret_cast<const PM4CmdEventWriteEos*>(header);" in lp
assert "const auto value=*reinterpret_cast<const PM4DmaData*>(header);" in lp
assert "std::vector<u32> owned(data->data,data->data+words);" in lp
assert "QueueIndirectDraw(" in lp and "QueueDispatchIndirect(" in lp
assert "task.resume();\n            DrainDrawQueue();" in lp
pc = (src / "video_core/renderer_vulkan/vk_pipeline_cache.cpp").read_text()
replace = pc[pc.index("PipelineCache::ReplaceShader("):]
assert "liverpool->InvalidateDrawSnapshots();" in replace[:700]
assert "if(rasterizer)rasterizer->DetachDrawPipeline();" in lp
sc = (src / "video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
submit = sc[sc.index("void Scheduler::SubmitExecution("):]
assert submit.index("DrainDrawPipe();") < submit.index("work_semaphore.NextTick()")
compute=lp[lp.index("Liverpool::Task Liverpool::ProcessCompute("):]
assert "ASC side effects are synchronous barriers" in compute
assert "if(draw_pending_writes)DrainDrawQueue();" in compute
rp = (src / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
assert "liverpool->DrawVertexBuffers()" in rp
assert "selected?prepared:pipeline_cache.GetGraphicsPipeline" in rp

HARNESS = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bitset>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <thread>
#include <utility>
#include <vector>
#include "common/bachata_progress.h"
#include "video_core/amdgpu/bachata_draw_snapshot.h"
using u8=std::uint8_t;using u16=std::uint16_t;using u32=std::uint32_t;
using u64=std::uint64_t;using VAddr=u64;
#define ASSERT(...) assert((__VA_ARGS__))
constexpr int Render_Vulkan=0;
std::atomic<u32> policy_logs{0};
template<class...Args>void TestLog(const Args&...){++policy_logs;}
#define LOG_INFO(...) TestLog(__VA_ARGS__)
#define LOG_WARNING(...) TestLog(__VA_ARGS__)
namespace fmt {template<class T>int make_format_args(const T&){return 0;}}
namespace Common {
template<class R>using UniqueFunction=std::function<R()>;
inline void SetCurrentThreadName(const char*){}
struct ElfInfo {
    std::string serial="CUSA08809";
    static ElfInfo& Instance(){static ElfInfo value;return value;}
    const std::string& GameSerial()const{return serial;}
};
}
struct Settings {bool uffd{};bool IsUserfaultfdTracking()const{return uffd;}} EmulatorSettings;
namespace Shader {
enum class SwStage{Vertex=0,Compute=1,Fragment=2};constexpr u32 MaxStageTypes=2;
struct Info {
    SwStage sw_stage{SwStage::Vertex};
    std::optional<int> params{42};
    std::span<const u32> user_data;
    std::vector<u32> flattened_ud_buf;
    std::vector<VAddr> srt_guest_sources;
    std::vector<u32> sharp_tables;
    VAddr pgm_base{};
    u64 pgm_hash{};
    u32 metadata{};
    bool uses_dma{},has_storage_images{};
    struct Resource {bool is_written{};};
    std::vector<Resource> buffers,images;
};
}
namespace AmdGpu {
struct Buffer {u32 value{};};
struct CbDbExtent {u32 value{};};constexpr u32 NUM_COLOR_BUFFERS=2;
struct ComputeProgram {u32 value{};};
struct Regs {static constexpr u32 NumRegs=64;std::array<u32,NumRegs> reg_array{};};
class Liverpool;
}
namespace Vulkan {
constexpr u32 MaxVertexBufferCount=32;
struct DrawIndirectParams {u16 vertex_sgpr_offset{};u32 instance_sgpr_offset{};bool indirect{};};
class Pipeline {
public:
    bool is_compute{};
    std::array<const Shader::Info*,Shader::MaxStageTypes> stages{};
@PIPELINE@
};
struct Attribute {
    AmdGpu::Buffer* guest{};
    AmdGpu::Buffer GetSharp(const Shader::Info&)const{return *guest;}
};
struct FetchShader {std::vector<Attribute> attributes;};
class GraphicsPipeline:public Pipeline {
public:
    FetchShader fetch;
    const FetchShader& GetFetchShader()const{return fetch;}
};
class ComputePipeline:public Pipeline {};
struct Scheduler {
    std::thread::id producer;
    bool recorder{true};
    bool HasRecordThread()const{return recorder;}
    void ClaimRecorder(){producer=std::this_thread::get_id();}
    u64 CurrentTick()const{return 7;}
    u64 RecordedSubmitTick()const{return 6;}
    u64 KnownGpuTick()const{return 5;}
    Scheduler* GetWorkSemaphore(){return this;}
};
class Rasterizer {
public:
    AmdGpu::Liverpool* cp{};
    Scheduler scheduler;
    GraphicsPipeline graphics;
    ComputePipeline compute;
    Shader::Info vs,cs;
    std::array<u32,1> live_words{7};
    AmdGpu::Buffer vertex{17};
    bool markers{};
    std::atomic<bool> hold{false},entered{false};
    struct Observation {
        u32 reg,word,flat,sharp,vertex,metadata,dispatch;VAddr address;
        u32 indirect_offset{},indirect_stride{},indirect_count{};
        VAddr count_address{};u16 vertex_sgpr{},instance_sgpr{};
    };
    std::vector<Observation> observations;
    std::vector<int> ordered;
    int guest_value{};
    u32 serial_calls{},prepared_calls{},prepared_after_write{};
    Rasterizer(){
        vs.user_data=live_words;vs.flattened_ud_buf={27};vs.sharp_tables={37};vs.metadata=47;
        vs.srt_guest_sources={0x1234};vs.pgm_base=0x4567;
        cs=vs;cs.sw_stage=Shader::SwStage::Compute;
        graphics.stages[0]=&vs;compute.stages[1]=&cs;compute.is_compute=true;
        graphics.fetch.attributes.push_back({&vertex});
    }
    bool CanPipelineDraw()const{return !markers;}
    Scheduler& GetScheduler(){return scheduler;}
    template<class F>void ScopeMarker(const char*,int,F&& fn){fn();}
    const Pipeline* PrepareDrawPipeline(bool c,const DrawIndirectParams&){
        ++prepared_calls;
        prepared_after_write=guest_value;
        return c?static_cast<Pipeline*>(&compute):static_cast<Pipeline*>(&graphics);
    }
    void Draw(bool,u32,const GraphicsPipeline* pipeline=nullptr,bool selected=false);
    void DrawIndirect(bool indexed,VAddr address,u32 offset,u32 stride,u32 max_count,
                      VAddr count_address,u16 vertex_sgpr,u16 instance_sgpr,
                      const GraphicsPipeline* pipeline=nullptr,bool selected=false){
        Draw(indexed,offset,pipeline,selected);
        if(selected){
            auto& value=observations.back();value.address=address;
            value.indirect_offset=offset;value.indirect_stride=stride;value.indirect_count=max_count;
            value.count_address=count_address;value.vertex_sgpr=vertex_sgpr;value.instance_sgpr=instance_sgpr;
        }
    }
    void DispatchDirect(const ComputePipeline* pipeline=nullptr,bool selected=false);
    void DispatchIndirect(VAddr address,u32,u32,const ComputePipeline* pipeline=nullptr,bool selected=false){
        DispatchDirect(pipeline,selected);
        if(selected)observations.back().address=address;
    }
};
}
namespace AmdGpu {
class Liverpool {
public:
    Regs regs{};
    std::array<CbDbExtent,NUM_COLOR_BUFFERS> last_cb_extent{};
    CbDbExtent last_db_extent{};
    ComputeProgram cs_live{};
    Vulkan::Rasterizer* rasterizer{};
    explicit Liverpool(Vulkan::Rasterizer& renderer):rasterizer{&renderer}{renderer.cp=this;}
    ~Liverpool(){
        DrainDrawQueue();
        if(draw_worker.joinable()){
            draw_worker.request_stop();draw_cv.notify_all();draw_worker.join();
        }
    }
    bool OnDrawThread()const{return draw_owner==this;}
    Regs& DrawRegs(){return OnDrawThread()?back_regs:regs;}
    ComputeProgram& GetCsRegs(){return OnDrawThread()?back_cs:cs_live;}
    std::span<const AmdGpu::Buffer> DrawVertexBuffers()const{
        return OnDrawThread()?back_vertices:std::span<const AmdGpu::Buffer>{};
    }
    void DrainDrawQueue();void InvalidateDrawSnapshots();
@MEMBERS@
};
@METHODS@
}
namespace Vulkan {
void Rasterizer::Draw(bool,u32,const GraphicsPipeline* pipeline,bool selected){
    if(!selected){++serial_calls;return;}
    assert(cp->OnDrawThread());
    assert(scheduler.producer==std::this_thread::get_id());
    entered.store(true,std::memory_order_release);
    while(hold.load(std::memory_order_acquire))std::this_thread::yield();
    const auto& info=pipeline->GetStage(Shader::SwStage::Vertex);
    assert(!info.params);
    // A lookup on another pipeline must not inherit the active packet's stages.
    assert(&compute.GetStage(Shader::SwStage::Compute)==&cs);
    observations.push_back({cp->DrawRegs().reg_array[0],info.user_data[0],
        info.flattened_ud_buf[0],info.sharp_tables[0],cp->DrawVertexBuffers()[0].value,
        info.metadata,0,0});
    ordered.push_back(static_cast<int>(cp->DrawRegs().reg_array[0]));
}
void Rasterizer::DispatchDirect(const ComputePipeline* pipeline,bool selected){
    if(!selected){++serial_calls;return;}
    assert(cp->OnDrawThread());
    assert(scheduler.producer==std::this_thread::get_id());
    const auto& info=pipeline->GetStage(Shader::SwStage::Compute);
    assert(!info.params);
    observations.push_back({cp->DrawRegs().reg_array[0],info.user_data[0],
        info.flattened_ud_buf[0],info.sharp_tables[0],0,info.metadata,cp->GetCsRegs().value,0});
}
}
int main(){
    using AmdGpu::Liverpool;
    {
        Vulkan::Rasterizer renderer;Liverpool cp{renderer};
        renderer.hold.store(true);
        cp.regs.reg_array[0]=1;
        cp.QueueDirectDraw("draw:{}",nullptr,false,0);
        while(!renderer.entered.load(std::memory_order_acquire))std::this_thread::yield();
        // The consumer has the first packet, while the producer mutates all
        // original mutable state and the pointed V# table for a later packet.
        cp.regs.reg_array[0]=2;cp.MarkDrawWords(0,1);
        renderer.live_words[0]=8;renderer.vs.flattened_ud_buf[0]=28;
        renderer.vs.sharp_tables[0]=38;renderer.vertex.value=18;
        cp.QueueDirectDraw("draw:{}",nullptr,false,0);
        renderer.live_words[0]=99;renderer.vs.flattened_ud_buf[0]=99;
        renderer.vs.sharp_tables[0]=99;renderer.vertex.value=99;
        renderer.hold.store(false,std::memory_order_release);
        cp.DrainDrawQueue();
        assert(renderer.observations.size()==2);
        const auto first=renderer.observations[0],second=renderer.observations[1];
        assert(first.reg==1 && first.word==7 && first.flat==27 && first.sharp==37 && first.vertex==17);
        assert(second.reg==2 && second.word==8 && second.flat==28 && second.sharp==38 && second.vertex==18);
        assert(renderer.scheduler.producer==std::this_thread::get_id());
        assert(!Vulkan::Pipeline::draw_owner && !Vulkan::Pipeline::draw_stages);

        std::vector<int> payload{5,6};
        cp.QueueGpuTask([&renderer,payload=std::move(payload)]{
            renderer.ordered.push_back(payload[0]+payload[1]);renderer.guest_value=81;
        });
        assert(payload.empty());
        cp.regs.reg_array[0]=3;cp.MarkDrawWords(0,1);
        cp.QueueIndirectDraw(false,0x123456,4,64,23,0x12345678abcdef00ull,3,5);
        cp.DrainDrawQueue();
        assert((renderer.ordered==std::vector<int>{1,2,11,3}));
        assert(renderer.prepared_after_write==81 && renderer.observations.back().address==0x123456);
        const auto indirect=renderer.observations.back();
        assert(indirect.indirect_offset==4 && indirect.indirect_stride==64 && indirect.indirect_count==23);
        assert(indirect.count_address==0x12345678abcdef00ull && indirect.vertex_sgpr==3 && indirect.instance_sgpr==5);

        cp.cs_live.value=92;
        cp.QueueDispatchDirect();
        cp.cs_live.value=93;
        cp.QueueDispatchIndirect(0x987654,0,12);
        cp.DrainDrawQueue();
        assert(renderer.observations[3].dispatch==92);
        assert(renderer.observations[4].dispatch==93 && renderer.observations[4].address==0x987654);

        cp.InvalidateDrawSnapshots();
        renderer.vs.metadata=76; // simulate reused Info storage after PSO eviction
        cp.QueueDirectDraw("draw:{}",nullptr,false,0);cp.DrainDrawQueue();
        assert(renderer.observations.back().metadata==76);

        renderer.observations.clear();renderer.ordered.clear();
        for(u32 i=0;i<4096;++i){
            cp.regs.reg_array[0]=i;cp.MarkDrawWords(0,1);
            renderer.live_words[0]=i;renderer.vs.flattened_ud_buf[0]=i+1;
            renderer.vertex.value=i+2;
            cp.QueueDirectDraw("draw:{}",nullptr,false,0);
        }
        cp.DrainDrawQueue();
        assert(renderer.observations.size()==4096);
        for(u32 i=0;i<4096;++i){
            const auto& observation=renderer.observations[i];
            assert(observation.reg==i && observation.word==i && observation.flat==i+1 && observation.vertex==i+2);
        }
        assert(policy_logs.load()==1);
    }
    {
        Vulkan::Rasterizer renderer;Liverpool cp{renderer};
        EmulatorSettings.uffd=true;
        cp.QueueDirectDraw("draw:{}",nullptr,false,0);
        assert(renderer.serial_calls==1 && !cp.draw_worker.joinable());
        EmulatorSettings.uffd=false;
        Common::ElfInfo::Instance().serial="UNRELATED";
        cp.QueueDirectDraw("draw:{}",nullptr,false,0);
        assert(renderer.serial_calls==2 && !cp.draw_worker.joinable());
    }
    {
        Common::ElfInfo::Instance().serial="CUSA08809";
        Vulkan::Rasterizer renderer;renderer.scheduler.recorder=false;
        Liverpool cp{renderer};
        cp.QueueDirectDraw("draw:{}",nullptr,false,0);cp.DrainDrawQueue();
        assert(cp.draw_worker.joinable() && renderer.observations.size()==1);
    }
    std::cout<<"BACHATA_DONOR_DRAW_PIPE_PASS owned-state/pointed-V#/FIFO/side-effects/lookup-barrier/compute/eviction/4096-wraps\n";
}
'''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    source = folder / "draw.cpp"
    executable = folder / "draw"
    source.write_text(HARNESS.replace("@PIPELINE@", pipeline).replace("@MEMBERS@", members)
                      .replace("@METHODS@", methods))
    subprocess.run(["c++", "-std=c++23", "-O2", "-pthread", "-Wall", "-Wextra", "-Werror",
                    "-I", str(src), str(source), "-o", str(executable)], check=True)
    subprocess.run([str(executable)], check=True, timeout=30,
                   env={**os.environ, "SOTC_CP_THREADS": "1"})
