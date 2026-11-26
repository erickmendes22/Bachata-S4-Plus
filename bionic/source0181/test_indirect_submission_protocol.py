#!/usr/bin/env python3
"""Exercise effective indirect hazards, GPU clamp source and fenced allocations.

--validate-spirv additionally compiles the actual host shader and runs spirv-val;
use it in the native CI job after installing glslang-tools and spirv-tools.
"""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def block(text, marker):
    begin = text.index(marker)
    opening = text.index("{", begin)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[begin:end + 1]
    raise AssertionError(f"unclosed source block {marker}")


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
parser.add_argument("--validate-spirv", action="store_true")
args = parser.parse_args()
src = args.source.resolve() / "src"
runtime = (src / "video_core/renderer_vulkan/vk_runtime.cpp").read_text()
rasterizer = (src / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
buffer = (src / "video_core/buffer_cache/buffer.cpp").read_text()
pool = (src / "video_core/renderer_vulkan/vk_staging_buffer_pool.cpp").read_text()
shader_path = src / "video_core/host_shaders/indirect_index_clamp.comp"
shader = shader_path.read_text()
runtime_methods = "\n".join(block(runtime, name) for name in (
    "bool Runtime::IsBufferAccessed(", "void Runtime::AccessBuffer(",
    "void Runtime::FlushBarriers(", "void Runtime::MakeCurrent(",
    "void Runtime::CopyBuffer(", "void Runtime::FillBuffer(", "void Runtime::InlineData("))
stream_methods = "\n".join(block(buffer, name) for name in (
    "bool StreamBuffer::PrepareMap(", "std::optional<u64> StreamBuffer::Reserve(",
    "void StreamBuffer::AdvanceAndWatch(", "void StreamBuffer::ReserveWatches(",
    "bool StreamBuffer::WaitPendingOperations("))
draw = block(rasterizer, "void Rasterizer::DrawIndirect(")
prepare = draw[draw.index("{") + 1:draw.index("    const DrawIndirectParams params =")]
dispatch = block(rasterizer, "void Rasterizer::DispatchIndirect(")
draw_reads = draw[draw.index("    // Later WRITE_DATA/uploads"):draw.rindex("    ResetBindings(false);")]
dispatch_reads = dispatch[dispatch.index("    runtime.AccessBuffer(buffer, base, size,"):
                          dispatch.rindex("    ResetBindings(true);")]
reset = block(rasterizer, "void Rasterizer::ResetBindings(")
fixed_reads = reset[reset.index("    for (const auto& read : fixed_function_reads)"):
                    reset.index("    bound_images.clear();")]
clamp = block(rasterizer, "std::vector<Rasterizer::ClampedIndirectBatch> Rasterizer::ClampIndexedIndirect(")
index_bind = block(rasterizer, "void Rasterizer::BindIndexBuffer(")
assert "memory->ClampGpuRangeSize" in draw and "memory->ClampRangeSize" not in draw
assert "if (!index_request.bytes) return;" in prepare
assert "BindIndexBuffer(0, index_request.bytes, index_request.limit);" in draw
assert "indirect_bytes ? indirect_bytes : regs.num_indices * index_size" in index_bind
assert "if (clamped.empty())" not in draw
assert "batch.offset + sizeof(u32)" in draw and "batch.buffer->Handle(), batch.offset, batch.count" in draw
assert "PlanIndirectClampBatch" in clamp and "MemoryType::DeviceLocal, alignment" in clamp
assert "memory->" not in clamp and ".mapped" not in clamp
assert "clamped_args_head" not in clamp and "unsynchronized" not in clamp
assert "Reserve(size, alignment, false)" in pool and "!scheduler.IsFree(entry.tick)" in pool
assert "fixed_function_reads.push_back" in block(rasterizer, "void Rasterizer::BindVertexBuffers(")
assert "eVertexAttributeRead" in block(rasterizer, "void Rasterizer::BindVertexBuffers(")
assert "eIndexRead" in index_bind
assert "WarnMetadataTexture() && texture_cache.IsMeta(tsharp.Address())" in rasterizer
shader_main = block(shader, "void main()").replace("void main()", "void ShaderMain()", 1)
push_fields = re.search(r"uniform Push\s*\{([^}]+)\}\s*push", shader)[1]
warning_policy = block(rasterizer, "static bool WarnMetadataTexture()")

HARNESS = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <numeric>
#include <optional>
#include <random>
#include <span>
#include <tuple>
#include <vector>
#include "common/types.h"
#include "common/alignment.h"
#include "video_core/renderer_vulkan/indirect_submission_limits.h"
#include "video_core/renderer_vulkan/vk_barrier_tracker.h"
namespace vk {
using AccessFlags2=u64;using PipelineStageFlags2=u64;
struct AccessFlagBits2 {
    static constexpr u64 eNone=0,eIndexRead=1,eVertexAttributeRead=2,eUniformRead=4,eShaderRead=8,
        eColorAttachmentRead=16,eDepthStencilAttachmentRead=32,eTransferRead=64,eMemoryRead=128,
        eShaderWrite=256,eColorAttachmentWrite=512,eDepthStencilAttachmentWrite=1024,
        eTransferWrite=2048,eMemoryWrite=4096,eTransformFeedbackWriteEXT=8192,eIndirectCommandRead=16384;
};
struct PipelineStageFlagBits2 {
    static constexpr u64 eNone=0,eDrawIndirect=1,eCopy=2,eClear=4,eComputeShader=8,
        eVertexInput=16,eAllGraphics=32,eAllCommands=64;
};
struct MemoryBarrier2 {u64 srcStageMask{},srcAccessMask{},dstStageMask{},dstAccessMask{};};
struct ImageMemoryBarrier2 {};
struct DependencyInfo {
    const MemoryBarrier2* pMemoryBarriers{};u32 memoryBarrierCount{};
    const ImageMemoryBarrier2* pImageMemoryBarriers{};u32 imageMemoryBarrierCount{};
};
struct BufferCopy {u64 srcOffset,dstOffset,size;};
}
namespace VideoCore {
struct Buffer {u64 id{};u64 Handle()const{return id;}};
}
namespace Vulkan {
struct Scheduler {
    u64 current{1},completed{};u32 barriers{},copies{},fills{},updates{};
    u64 stages{};
    void EndRendering(){}
    void PopPendingOperations(){}
    struct Commands {
        Scheduler& s;
        void pipelineBarrier2(const vk::DependencyInfo& info) const {
            ++s.barriers;if(info.pMemoryBarriers)s.stages|=info.pMemoryBarriers->srcStageMask;
        }
        void copyBuffer(u64,u64,std::span<const vk::BufferCopy>) const {++s.copies;}
        void fillBuffer(u64,u64,u64,u32) const {++s.fills;}
        void updateBuffer(u64,u64,u64,const void*) const {++s.updates;}
    };
    Commands CommandBuffer(){return {*this};}
    u64 CurrentTick()const{return current;}
    bool IsFree(u64 tick){return completed>=tick;}
    void Wait(u64 tick){assert(IsFree(tick));}
};
struct Interval {u64 start,end;};
struct Ranges {
    std::vector<Interval> ranges;
    void Add(Interval value){ranges.push_back(value);}
    bool Overlaps(u64 start,u64 end)const{
        return std::ranges::any_of(ranges,[&](auto r){return start<r.end && r.start<end;});
    }
    void Clear(){ranges.clear();}
};
class Runtime {
public:
    Scheduler scheduler;
    bool donor_range_tracking{true};
    BarrierTracker donor_barriers;
    struct Memo {u64 resource{},start{},end{},epoch{};u32 access{};};
    std::array<Memo,256> donor_access_memo{};u64 donor_access_epoch{1};
    struct BufferBarriers {
        const VideoCore::Buffer* handle;Ranges read_ranges,write_ranges;
        explicit BufferBarriers(const VideoCore::Buffer*h):handle(h){}
    };
    std::vector<BufferBarriers> resources;BufferBarriers*resource{};
    vk::MemoryBarrier2 memory_barrier{};std::vector<vk::ImageMemoryBarrier2> image_barriers;
    bool IsBufferAccessed(const VideoCore::Buffer*,u64,u64,bool check_read_access=false);
    void AccessBuffer(const VideoCore::Buffer*,u64,u64,vk::PipelineStageFlags2,vk::AccessFlags2);
    void FlushBarriers();void MakeCurrent(const VideoCore::Buffer*);
    void CopyBuffer(const VideoCore::Buffer*,const VideoCore::Buffer*,std::span<const vk::BufferCopy>);
    void FillBuffer(const VideoCore::Buffer*,u64,u64,u32);
    void InlineData(VideoCore::Buffer*,u64,u32);
};
@RUNTIME@
void RecordDrawReads(Runtime& runtime,const VideoCore::Buffer*buffer,u64 base,u32 argument_bytes,
                     VAddr count_address,const VideoCore::Buffer*count_buffer,u64 count_offset){
@DRAW_READS@
}
void RecordDispatchReads(Runtime& runtime,const VideoCore::Buffer*buffer,u64 base,u32 size){
@DISPATCH_READS@
}
struct FixedRead {const VideoCore::Buffer*buffer;u64 offset,size;vk::AccessFlags2 access;};
void RecordFixedReads(Runtime& runtime,std::vector<FixedRead>&fixed_function_reads){
@FIXED_READS@
}
}
namespace VideoCore {
constexpr size_t WATCHES_RESERVE_CHUNK=256;
class StreamBuffer {
public:
    Vulkan::Scheduler scheduler;
    std::span<u8>mapped_data;bool is_coherent{true};u64 non_coherent_atom_size{1},size_bytes{64};
    u64 offset{},mapped_size{},last_tick{},wrap_generation{};
    struct Watch{u64 upper_bound{},tick{};};
    std::vector<Watch>current_watches=std::vector<Watch>(8),previous_watches;
    size_t current_watch_cursor{},wait_cursor{};std::optional<size_t>invalidation_mark;u64 wait_bound{};
    bool PrepareMap(u64,u64,bool);std::optional<u64>Reserve(u64,u64,bool);
    void AdvanceAndWatch();void ReserveWatches(std::vector<Watch>&,size_t);
    bool WaitPendingOperations(u64,bool);
};
@STREAM@
}
namespace BachataCompat {static bool order=true;bool Order1886(){return order;}}
@WARNING@
namespace AmdGpu {enum class IndexType {Index16,Index32};}
struct VkDrawIndexedIndirectCommand {u32 words[5];};
struct PreparationMemory {
    std::vector<std::pair<u64,u64>>ranges{{0x1000,0x100},{0x3000,0x80}};
    u64 ClampGpuRangeSize(VAddr address,u64 requested)const{
        for(const auto&[base,size]:ranges)
            if(address>=base && address-base<size)return std::min(requested,size-(address-base));
        return 0;
    }
};
struct PreparationLiverpool {
    struct Regs {
        struct {AmdGpu::IndexType index_type=AmdGpu::IndexType::Index32;}index_buffer_type;
        struct AddressReg{u64 value=0x3000;template<class T>T Address()const{return T(value);}}index_base_address;
        u32 max_index_size=32,num_indices=2;
    }regs;
    const Regs& DrawRegs()const{return regs;}
};
struct PreparationProbe {
    Vulkan::Scheduler scheduler;PreparationMemory backing;PreparationLiverpool registers;
    PreparationMemory*memory=&backing;PreparationLiverpool*liverpool=&registers;
    bool metadata_clear=true,image_state_changed=false;u32 prepared{},index_bytes{},index_limit{},argument_span{};
    bool FilterDraw()const{return true;}
    void Prepare(bool is_indexed,VAddr arg_address,u32 offset,u32 stride,u32 max_count,VAddr count_address){
#define RENDERER_TRACE
@PREPARE@
#undef RENDERER_TRACE
        // BindResources/BeginRendering publish layout state and consume metadata
        // clear before the Vulkan draw. Invalid records must return before here.
        ++prepared;image_state_changed=true;metadata_clear=false;
        index_bytes=index_request.bytes;index_limit=index_request.limit;argument_span=argument_bytes;
    }
};
using uint=u32;
struct ShaderPush {@PUSH_FIELDS@} push;
struct {u32 x;} gl_GlobalInvocationID;
std::vector<u32>src,dst,counts;
using std::min;
@SHADER@
int main(){
    using namespace BachataGpu;
    constexpr u32 Unlimited=std::numeric_limits<u32>::max();
    auto req=ResolveIndirectIndices(2,16,4,32);
    assert(req.bytes==32 && req.limit==8); // stale NUM_INDICES cannot truncate indirect indices
    req=ResolveIndirectIndices(2,16,2,19);assert(req.bytes==18 && req.limit==9);
    req=ResolveIndirectIndices(9,0,4,36);assert(req.bytes==36 && req.limit==Unlimited);
    req=ResolveIndirectIndices(9,0,4,0);assert(req.bytes==0 && req.limit==0);
    req=ResolveIndirectIndices(Unlimited,Unlimited,4,~u64{0});
    assert(req.bytes==0xfffffffcu && req.limit==0x3fffffffu);
    assert(!ResolveIndirectRecords(0,20,20,~u64{0}).count);
    assert(!ResolveIndirectRecords(2,16,20,100).count);
    assert(!ResolveIndirectRecords(2,21,20,100).count);
    assert(!ResolveIndirectRecords(1,20,20,19).count);
    assert(ResolveIndirectRecords(1,0,20,20).bytes==20);
    assert(ResolveIndirectRecords(3,32,20,83).count==2);
    assert(ResolveIndirectRecords(3,32,20,84).count==3);
    assert(ResolveIndirectRecords(Unlimited,20,20,~u64{0}).bytes==0xfffffff0u);
    assert(!PlanIndirectClampBatch(1,20,0,256,16,1,1).count);
    assert(!PlanIndirectClampBatch(1,20,0,256,4096,0,1).count);
    assert(!PlanIndirectClampBatch(2,16,0,256,4096,1,1).count);

    // Execute the actual DrawIndirect preparation prefix, including its returns.
    // A rejected index/argument range must not leave published image layouts or
    // consume metadata clear. A valid request carries its exact prevalidated bounds.
    for(u32 invalid=0;invalid<4;++invalid){
        PreparationProbe p;
        if(invalid==0)p.registers.regs.index_base_address.value=0x7000;
        if(invalid==1)p.registers.regs.max_index_size=p.registers.regs.num_indices=0;
        p.Prepare(true,0x1000,0,20,invalid==2?0:1,invalid==3?0x9000:0);
        assert(!p.prepared && p.metadata_clear && !p.image_state_changed);
    }
    {PreparationProbe p;p.Prepare(true,0x1000,0,20,1,0);
     assert(p.prepared==1 && p.index_bytes==128 && p.index_limit==32);}
    {PreparationProbe p;p.backing.ranges[1].second=50;p.Prepare(true,0x1000,0,20,1,0);
     assert(p.prepared==1 && p.index_bytes==48 && p.index_limit==12);}
    {PreparationProbe p;BachataCompat::order=false;p.registers.regs.index_base_address.value=0x7000;
     p.Prepare(true,0x1000,0,20,1,0);assert(p.prepared==1 && !p.index_bytes);
     BachataCompat::order=true;}

    // Real AccessBuffer -> real Copy/Fill/Inline paths. An indirect read must
    // participate in WAR dependencies even when no shader-resource read exists.
    for(bool tree:{false,true}){
        Vulkan::Runtime r;r.donor_range_tracking=tree;
        VideoCore::Buffer arguments{1},counter{2},upload{3};
        Vulkan::RecordDrawReads(r,&arguments,64,80,0x40000,&counter,16);
        assert(r.IsBufferAccessed(&arguments,64,80,true));
        assert(r.IsBufferAccessed(&counter,16,4,true));
        assert(!r.IsBufferAccessed(&arguments,64,80,false));
        const vk::BufferCopy copy{0,64,80};
        r.CopyBuffer(&upload,&arguments,std::span{&copy,1});
        assert(r.scheduler.barriers==1 && r.scheduler.copies==1);
        assert(r.scheduler.stages&vk::PipelineStageFlagBits2::eDrawIndirect);
        r.FlushBarriers();auto old=r.scheduler.barriers;
        Vulkan::RecordDrawReads(r,&arguments,64,80,0x40000,&counter,16);
        r.InlineData(&counter,16,7);assert(r.scheduler.barriers==old+1);
        r.FlushBarriers();old=r.scheduler.barriers;
        Vulkan::RecordDispatchReads(r,&arguments,128,12);
        r.FillBuffer(&arguments,128,12,0);assert(r.scheduler.barriers==old+1);
        r.FlushBarriers();old=r.scheduler.barriers;
        std::vector<Vulkan::FixedRead>reads{{&arguments,512,64,vk::AccessFlagBits2::eIndexRead},
                                           {&counter,128,64,vk::AccessFlagBits2::eVertexAttributeRead}};
        Vulkan::RecordFixedReads(r,reads);assert(reads.empty());
        assert(r.IsBufferAccessed(&arguments,512,64,true));
        assert(r.IsBufferAccessed(&counter,128,64,true));
        r.FillBuffer(&arguments,512,64,0);assert(r.scheduler.barriers==old+1);
        assert(r.scheduler.stages&vk::PipelineStageFlagBits2::eVertexInput);
    }

    // The effective StreamBuffer allocator refuses wraparound until the GPU
    // timeline completes. StagingBufferPool allocates another block on refusal.
    VideoCore::StreamBuffer ring;
    assert(ring.Reserve(32,4,false)==0);assert(ring.Reserve(32,4,false)==32);
    assert(!ring.Reserve(16,4,false));assert(!ring.Reserve(16,4,false));
    ring.scheduler.completed=1;ring.scheduler.current=2;
    assert(ring.Reserve(16,4,false)==0 && ring.last_tick==2);
    assert(ring.Reserve(48,4,false)==16);assert(!ring.Reserve(16,4,false));
    ring.scheduler.completed=2;ring.scheduler.current=3;
    assert(ring.Reserve(16,4,false)==0 && ring.last_tick==3);

    // Execute the actual GLSL main body with GPU inputs made visible after
    // recording. Every non-count argument is preserved bit-for-bit, including
    // signed vertex offsets, and native draw counts remain correct across batches.
    std::mt19937 rng(0x1886);
    u64 records=0,batches=0;
    for(u32 trial=0;trial<1200;++trial){
        const u32 n=1+rng()%300,stride=(5+rng()%5)*4;
        const u64 alignment=16ull<<(rng()%5),start=0x1000ull+(rng()%16)*4;
        const u64 storage=4096;
        const u32 max_draw=1+rng()%71,max_dispatch=1+rng()%3;
        const u32 total=rng()%(n+10),limit=rng()%257;
        const bool counted=trial&1,bounded=trial&2;
        std::vector<std::array<u32,5>>gpu_input(n);
        for(auto& v:gpu_input)v={u32(rng()%2?0xfffffffau:rng()%512),u32(1+rng()%4),
                                u32(rng()%300),0xfffffffdu,u32(rng())};
        u32 issued=0;
        for(u32 first=0;first<n;){
            const auto plan=PlanIndirectClampBatch(n-first,stride,start+u64(first)*stride,
                                                   alignment,storage,max_dispatch,max_draw);
            assert(plan.count && plan.count<=max_draw && plan.count<=max_dispatch*64);
            assert(plan.source_bytes<=storage && plan.output_bytes<=storage);
            assert(plan.source_begin%alignment==0);
            src.assign(plan.source_bytes/4+8,0);dst.assign(plan.output_bytes/4+8,0xcafef00du);
            counts.assign(3,0);
            push={plan.count,plan.first_word,stride/4,limit,counted?1u:0u,1,first,bounded?1u:0u};
            std::vector<std::function<void()>>queue;
            queue.push_back([&]{ // A preceding compute shader produces args and count.
                for(u32 j=0;j<plan.count;++j)
                    std::copy(gpu_input[first+j].begin(),gpu_input[first+j].end(),
                              src.begin()+plan.first_word+j*(stride/4));
                counts[1]=total;
            });
            queue.push_back([&]{
                for(u32 i=0;i<(plan.count+63)/64*64;++i){gl_GlobalInvocationID.x=i;ShaderMain();}
            });
            for(auto& op:queue)op();
            const u32 expected=counted?(total>first?std::min(plan.count,total-first):0):plan.count;
            assert(dst[0]==expected);issued+=dst[0];
            for(u32 j=0;j<plan.count;++j){
                const auto& original=gpu_input[first+j];
                const u32 available=limit>original[2]?limit-original[2]:0;
                assert(dst[1+j*5]==(bounded?std::min(original[0],available):original[0]));
                for(u32 word=1;word<5;++word)assert(dst[1+j*5+word]==original[word]);
                ++records;
            }
            for(size_t j=plan.output_bytes/4;j<dst.size();++j)assert(dst[j]==0xcafef00du);
            first+=plan.count;++batches;
        }
        assert(issued==(counted?std::min(n,total):n));
    }
    const char*flag=std::getenv("ORDER1886_WARN_META_TEXTURE");
    assert(WarnMetadataTexture()==bool(flag && flag[0]=='1'));
    BachataCompat::order=false;assert(WarnMetadataTexture());
    std::cout<<"BACHATA_INDIRECT_SUBMISSION_PROTOCOL_PASS records="<<records<<" batches="<<batches
             <<" real-WAR/args+count/vertex+index/mapped-bounds/GPU-produced/stride/count/fenced-reuse/early-reject-state\n";
}
'''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    cpp = folder / "indirect.cpp"
    exe = folder / "indirect"
    program = HARNESS
    for marker, value in (("RUNTIME", runtime_methods), ("STREAM", stream_methods),
                          ("DRAW_READS", draw_reads), ("DISPATCH_READS", dispatch_reads),
                          ("FIXED_READS", fixed_reads), ("WARNING", warning_policy),
                          ("PREPARE", prepare),
                          ("SHADER", shader_main), ("PUSH_FIELDS", push_fields)):
        program = program.replace(f"@{marker}@", value)
    cpp.write_text(program)
    subprocess.run(["c++", "-std=c++23", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-I", str(src), str(cpp),
                    str(src / "video_core/renderer_vulkan/vk_barrier_tracker.cpp"),
                    "-o", str(exe)], check=True)
    for value in ("0", "1"):
        subprocess.run([str(exe)], check=True, timeout=30,
                       env={**os.environ, "ORDER1886_WARN_META_TEXTURE": value})
    if args.validate_spirv:
        compiler, validator = shutil.which("glslangValidator"), shutil.which("spirv-val")
        if not compiler or not validator:
            raise RuntimeError("--validate-spirv requires glslangValidator and spirv-val")
        binary = folder / "indirect_index_clamp.spv"
        subprocess.run([compiler, "--target-env", "vulkan1.3", "-V", str(shader_path),
                        "-o", str(binary)], check=True)
        subprocess.run([validator, "--target-env", "vulkan1.3", str(binary)], check=True)
        print("BACHATA_INDIRECT_CLAMP_SPIRV_PASS actual-host-shader Vulkan1.3")
