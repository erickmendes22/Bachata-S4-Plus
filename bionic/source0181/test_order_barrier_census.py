#!/usr/bin/env python3
"""Verify actual hazard results, provenance, alias criteria and bounded census.

The existing hazard tracker and Runtime methods execute unchanged decisions;
only pending diagnostic causes are observed. Vulkan and clocks are boundaries.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from test_order_readconst_pool import block
import test_order_render_state_memo as memo
import test_order_image_alias as alias


RUNTIME = r'''
struct Interval {u64 start,end;};
struct Ranges {
    std::vector<Interval>ranges;
    void Add(Interval range){ranges.push_back(range);}
    bool Overlaps(u64 begin,u64 end)const {
        return std::ranges::any_of(ranges,[&](auto r){return begin<r.end&&r.start<end;});
    }
    void Clear(){ranges.clear();}
};
struct Runtime {
    Scheduler&scheduler;
    explicit Runtime(Scheduler&s):scheduler{s}{}
    bool donor_range_tracking=true,order_resource_census=true;
    OrderBarrierPending order_barrier_pending{};
    BarrierTracker donor_barriers;
    struct Memo {u64 resource{},start{},end{};u32 epoch{},access{};};
    std::array<Memo,512>donor_access_memo{};u32 donor_access_epoch=1;
    struct BufferBarriers {
        const VideoCore::Buffer*handle;Ranges read_ranges,write_ranges;
        explicit BufferBarriers(const VideoCore::Buffer*h):handle{h}{}
    };
    std::vector<BufferBarriers>resources;BufferBarriers*resource{};
    vk::MemoryBarrier2 memory_barrier{};std::vector<vk::ImageMemoryBarrier2>image_barriers;
    bool IsBufferAccessed(const VideoCore::Buffer*,u64,u64,bool=false);
    void AccessBuffer(const VideoCore::Buffer*,u64,u64,vk::PipelineStageFlags2,vk::AccessFlags2);
    void MakeCurrent(const VideoCore::Buffer*);
    void SetBackingSamples(VideoCore::Image*i,u32 n){i->backing->num_samples=n;}
    bool Transit(VideoCore::Image*,vk::ImageLayout,vk::PipelineStageFlags2,vk::AccessFlags2,std::optional<VideoCore::SubresourceRange> = {});
    void FlushBarriers();
};
'''


RUNTIME_TESTS = r'''
using namespace Vulkan;
bool enabled=true,inline_enabled=false;
u64 Kind(OrderBarrierKind k){return u64{1}<<static_cast<u32>(k);}
u64 Origin(OrderBarrierOrigin k){return u64{1}<<static_cast<u32>(k);}
void Hazards(bool deferred) {
    Scheduler scheduler{deferred};Runtime r{scheduler};VideoCore::Buffer b,other;
    r.AccessBuffer(&b,10,20,vk::PipelineStageFlagBits2::eAllCommands,vk::AccessFlagBits2::eShaderRead);
    assert(!r.IsBufferAccessed(&b,10,20,false)&&r.order_barrier_pending.kinds==0);
    {
        const OrderBarrierScope scope{&r,OrderBarrierOrigin::Gds};
        assert(r.IsBufferAccessed(&b,10,20,true));
        assert(r.order_barrier_pending.kinds==Kind(OrderBarrierKind::BufferWar));
        assert(r.order_barrier_pending.origins==Origin(OrderBarrierOrigin::Gds));
    }
    r.FlushBarriers();assert(r.order_barrier_pending.kinds==0&&r.order_barrier_pending.origins==0);
    assert(!r.IsBufferAccessed(&b,10,20,true));
    r.AccessBuffer(&b,10,20,vk::PipelineStageFlagBits2::eAllCommands,vk::AccessFlagBits2::eShaderWrite);
    {const OrderBarrierScope scope{&r,OrderBarrierOrigin::ReadConst};assert(r.IsBufferAccessed(&b,10,20));}
    assert(r.order_barrier_pending.kinds==Kind(OrderBarrierKind::BufferRaw));
    {const OrderBarrierScope scope{&r,OrderBarrierOrigin::Buffer};assert(r.IsBufferAccessed(&b,10,20,true));}
    assert(r.order_barrier_pending.kinds==(Kind(OrderBarrierKind::BufferRaw)|Kind(OrderBarrierKind::BufferWaw)));
    assert(!r.IsBufferAccessed(&other,10,20,true));
    assert(!r.IsBufferAccessed(&b,30,1,true));
    assert(!r.IsBufferAccessed(&b,10,0,true));
    // The real pending state crosses an owner-thread handoff without relying
    // on that thread's lexical Scope object still being alive.
    std::thread next([&]{r.FlushBarriers();});next.join();
    assert(!r.order_barrier_pending.kinds&&!r.order_barrier_pending.origins);
    scheduler.Sync();
}
void Images(bool deferred) {
    Rasterizer raster{deferred};auto&r=raster.runtime;
    auto&image=raster.texture_cache.GetImage(1);
    {const OrderBarrierScope scope{&r,OrderBarrierOrigin::Texture};
     assert(r.Transit(&image,vk::ImageLayout::eColorAttachmentOptimal,vk::PipelineStageFlagBits2::eColorAttachmentOutput,
                     vk::AccessFlagBits2::eColorAttachmentRead|vk::AccessFlagBits2::eColorAttachmentWrite));}
    assert(r.order_barrier_pending.kinds==Kind(OrderBarrierKind::ImageLayout));
    r.FlushBarriers();
    assert(!r.Transit(&image,vk::ImageLayout::eColorAttachmentOptimal,vk::PipelineStageFlagBits2::eColorAttachmentOutput,
                     vk::AccessFlagBits2::eColorAttachmentRead|vk::AccessFlagBits2::eColorAttachmentWrite));
    assert(!r.order_barrier_pending.kinds);
    image.object.state.access_mask=vk::AccessFlagBits2::eShaderWrite;
    {const OrderBarrierScope scope{&r,OrderBarrierOrigin::Attachment};
     assert(r.Transit(&image,vk::ImageLayout::eColorAttachmentOptimal,vk::PipelineStageFlagBits2::eColorAttachmentOutput,
                     vk::AccessFlagBits2::eColorAttachmentRead|vk::AccessFlagBits2::eColorAttachmentWrite));}
    assert(r.order_barrier_pending.kinds==Kind(OrderBarrierKind::ImageWrite));
    assert(r.order_barrier_pending.origins==Origin(OrderBarrierOrigin::Attachment));
    r.FlushBarriers();raster.scheduler.Sync();
}
int main(){for(bool deferred:{false,true}){Hazards(deferred);Images(deferred);}
    std::cout<<"ORDER_BARRIER_RUNTIME_PROVENANCE_PASS\n";}
'''


COUNTERS = r'''
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
#include "common/types.h"
struct FakeClock {
    using duration=std::chrono::microseconds;using time_point=std::chrono::time_point<FakeClock,duration>;
    inline static u64 micros{},calls{};
    static time_point now(){++calls;return time_point{duration{micros}};}
};
struct Row {std::string format;std::vector<u64>values;};
std::vector<Row>rows;
constexpr int Render_Vulkan=0;
template<class... T>void Log(int,const char*format,T... values){rows.push_back({format,{static_cast<u64>(values)...}});}
#define LOG_INFO Log
@HEADER@
using namespace Vulkan;
int main() {
    const void*owner=reinterpret_cast<void*>(1),*other=reinterpret_cast<void*>(2);
    OrderBarrierPending pending{};
    {
        OrderBarrierScope a{owner,OrderBarrierOrigin::Buffer};
        assert(OrderBarrierScope::Origin(owner)==OrderBarrierOrigin::Buffer);
        assert(OrderBarrierScope::Origin(other)==OrderBarrierOrigin::Other);
        {OrderBarrierScope b{owner,OrderBarrierOrigin::Gds};NoteOrderBarrier(pending,owner,OrderBarrierKind::BufferWar);}
        assert(OrderBarrierScope::Origin(owner)==OrderBarrierOrigin::Buffer);
        NoteOrderBarrier(pending,owner,OrderBarrierKind::ImageLayout);
    }
    assert(OrderBarrierScope::Origin(owner)==OrderBarrierOrigin::Other);
    for(u32 i=0;i<4096;++i)CountOrderBarrierFlush(owner,pending,false,true,true);
    assert(rows.empty()&&FakeClock::calls==0);
    for(u32 i=0;i<1023;++i)CountOrderBarrierFlush(owner,pending,true,true,true);
    assert(FakeClock::calls==1&&rows.empty());
    FakeClock::micros=6'000'000;CountOrderBarrierFlush(owner,pending,true,true,true);
    assert(rows.size()==1&&FakeClock::calls==2);
    const auto&v=rows.back().values;
    assert(v[0]==1&&v[3]==1024&&v[4]==0&&v[5]==0&&v[6]==1024&&v[7]==0);
    assert(v[10]==1024&&v[11]==1024&&v[15]==1024&&v[17]==1024);
    const auto before=rows.size();
    for(u32 i=0;i<1024;++i)CountOrderBarrierFlush(owner,{},true,true,false);
    assert(rows.size()==before&&FakeClock::calls==3);
    // Independent owner gets an independent window; no mixing of counters.
    for(u32 i=0;i<1023;++i)CountOrderBarrierFlush(other,{},true,false,true);
    FakeClock::micros=12'000'000;CountOrderBarrierFlush(other,{},true,false,true);
    assert(rows.size()==before+1&&rows.back().values[0]==2&&rows.back().values[5]==1024);
    rows.clear();FakeClock::calls=0;FakeClock::micros=20'000'000;
    OrderAliasProbe probe{2,1,1,0,0};
    CountOrderAliasProbe(owner,OrderAliasEvent::Registration,true,probe);
    for(u32 i=0;i<1022;++i)CountOrderAliasProbe(owner,OrderAliasEvent::Write,false);
    assert(rows.empty()&&FakeClock::calls==1);
    FakeClock::micros=26'000'000;CountOrderAliasProbe(owner,OrderAliasEvent::Synchronize,true);
    assert(rows.size()==1&&FakeClock::calls==2);
    const auto&a=rows[0].values;
    assert(a[3]==1&&a[4]==1&&a[5]==2&&a[6]==1&&a[7]==1);
    assert(a[10]==1022&&a[11]==0&&a[12]==1&&a[13]==1);
    std::cout<<"ORDER_RESOURCE_CENSUS_CLOCK_OWNER_PASS\n";
}
'''


ALIAS_TESTS = r'''
int main() {
    Images f;auto a=f.Add(736),b=f.Add(720);
    auto&first=f.cache.slot_images[a];auto&second=f.cache.slot_images[b];
    auto probe=f.cache.ProbeOrderAliasRegistration(second);
    assert(probe.same_base==1&&probe.eligible==1&&!probe.layout&&!probe.shape_format&&!probe.one_way);
    first.info.resources.layers=2;
    probe=f.cache.ProbeOrderAliasRegistration(second);
    assert(probe.same_base==1&&!probe.eligible&&probe.one_way==1);
    first.info.resources.layers=1;first.info.num_samples=2;
    probe=f.cache.ProbeOrderAliasRegistration(second);assert(probe.layout==1);
    first.info.num_samples=1;first.info.resources.levels=2;
    probe=f.cache.ProbeOrderAliasRegistration(second);assert(probe.shape_format==1);
    second.info.guest_address+=0x100000;
    probe=f.cache.ProbeOrderAliasRegistration(second);assert(!probe.same_base);
    std::cout<<"ORDER_ALIAS_REGISTRATION_CRITERIA_PASS\n";
}
'''


def runtime_program(source: Path) -> str:
    code=memo.program(source).split("using namespace Vulkan;\nbool enabled=true,inline_enabled=false;")[0]
    code=code.replace("#include <atomic>", '#include <atomic>\n#include "video_core/renderer_vulkan/vk_barrier_tracker.h"',1)
    code=code.replace("namespace VideoCore {", "namespace VideoCore {\nstruct Buffer {};",1)
    code=code.replace("eDepthStencilAttachmentRead=64", "eDepthStencilAttachmentRead=64,eShaderRead=128,eIndexRead=256,eVertexAttributeRead=512,eUniformRead=1024,eTransferRead=2048,eMemoryRead=4096,eIndirectCommandRead=8192,eTransformFeedbackWriteEXT=16384",1)
    code=code.replace(block(code,"struct Runtime {")+";",RUNTIME,1)
    runtime=(source/"src/video_core/renderer_vulkan/vk_runtime.cpp").read_text()
    extra="\n".join(block(runtime,s) for s in ("bool Runtime::IsBufferAccessed(","void Runtime::AccessBuffer(","void Runtime::MakeCurrent("))
    code=code.replace("bool Runtime::Transit(",extra+"\nbool Runtime::Transit(",1)
    return code+RUNTIME_TESTS


def source_guards(source: Path) -> None:
    root=source/"src";raster=(root/"video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    functions={"void Rasterizer::BindBuffers(":"Buffer","void Rasterizer::BindTextures(":"Texture",
        "RenderState Rasterizer::BeginRenderingFull(":"Attachment","void Rasterizer::BindVertexBuffers(":"Vertex",
        "void Rasterizer::BindIndexBuffer(":"Index","void Rasterizer::DrawIndirect(":"Indirect",
        "void Rasterizer::DispatchDirect(":"Dispatch","void Rasterizer::DispatchIndirect(":"Indirect"}
    def verify(text: str):
        for fn,origin in functions.items():
            body=block(text,fn)
            assert f"const OrderBarrierScope order_barrier_scope{{&runtime,OrderBarrierOrigin::{origin}}};" in body
            assert body.index("const OrderBarrierScope")<body.index(";\n")+1
        bind=block(text,"void Rasterizer::BindBuffers(")
        assert bind.index("const OrderBarrierScope gds_scope")<bind.index("runtime.IsBufferAccessed(gds_buf")
        assert bind.index("desc.used_as_readconst ? OrderBarrierOrigin::ReadConst")<bind.index("const auto vsharp")
    verify(raster)
    for fn,origin in functions.items():
        marker=f"const OrderBarrierScope order_barrier_scope{{&runtime,OrderBarrierOrigin::{origin}}};"
        start=raster.index(fn);end=start+len(block(raster,fn));changed=raster[:start]+raster[start:end].replace(marker,"")+raster[end:]
        try:verify(changed)
        except AssertionError:pass
        else:raise AssertionError("missing provenance source accepted: "+fn)
    runtime=(root/"video_core/renderer_vulkan/vk_runtime.cpp").read_text()
    assert '#ifdef __ANDROID__\n    order_resource_census=serial=="CUSA00785";\n#endif' in runtime
    flush=block(runtime,"void Runtime::FlushBarriers()")
    assert flush.index("if (!dep_info.memoryBarrierCount")<flush.index("CountOrderBarrierFlush")<flush.index("scheduler.EndRendering")
    print("ORDER_BARRIER_PRODUCER_GUARDS_PASS negatives=8",flush=True)


def run(folder: Path, source: Path, code: str, name: str, *, tracker=False, negative=False):
    path=folder/(name+".cpp");exe=folder/name;path.write_text(code)
    args=shlex.split(os.environ.get("CXX","c++"))+["-std=c++23","-D__ANDROID__","-O1","-pthread",
        "-Wall","-Wextra","-Werror","-Wno-unused-parameter","-Wno-unused-variable","-Wno-missing-field-initializers",
        "-fsanitize=undefined","-fno-sanitize-recover=all","-I",str(source/"src"),str(path)]
    if tracker:args.append(str(source/"src/video_core/renderer_vulkan/vk_barrier_tracker.cpp"))
    result=subprocess.run(args+["-o",str(exe)],capture_output=True,text=True)
    if result.returncode:
        (folder/(name+".build.log")).write_text(result.stdout+result.stderr)
        raise RuntimeError(name+" compile:\n"+"\n".join(result.stderr.splitlines()[:65]))
    env=dict(os.environ,ORDER1886_COALESCE_CLEAR_PASS="1",ORDER1886_INLINE_ATTACHMENT_CLEAR="0")
    result=subprocess.run([str(exe)],capture_output=True,text=True,env=env,timeout=20)
    (folder/(name+".run.log")).write_text(result.stdout+result.stderr)
    if negative:
        assert result.returncode!=0,"negative survived: "+name
        print("ORDER_RESOURCE_CENSUS_NEGATIVE_PASS",name,flush=True)
    else:
        if result.returncode:raise RuntimeError(name+" run:\n"+result.stdout+result.stderr)
        print(result.stdout,end="",flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--keep",type=Path);parser.add_argument("--positive-only",action="store_true")
    args=parser.parse_args();source=args.source.resolve();source_guards(source)
    with tempfile.TemporaryDirectory(prefix="order-resource-census-") as temporary:
        folder=args.keep.resolve() if args.keep else Path(temporary);folder.mkdir(exist_ok=True,parents=True)
        code=runtime_program(source);run(folder,source,code,"runtime",tracker=True)
        header=(source/"src/video_core/renderer_vulkan/order_resource_census.h").read_text()
        counters=COUNTERS.replace("@HEADER@",header.replace("#pragma once","").replace("std::chrono::steady_clock","FakeClock"))
        run(folder,source,counters,"counters")
        aliases=alias.make_program(source/"src");aliases=aliases[:aliases.index("int main(")]+ALIAS_TESTS
        run(folder,source,aliases,"alias_criteria")
        if args.positive_only:return
        mutations=(
            ("buffer_note",code,"if (order_resource_census && (prior_write || prior_read))","if (false)",True),
            ("pending_clear",code,"        order_barrier_pending={};","",True),
            ("image_note",code,"if (order_resource_census) for (size_t i=prev_num_barriers;","if (false) for (size_t i=prev_num_barriers;",True),
            ("closed_scope",counters,"    if (!open) return;","    (void)open;",False),
            ("clock_per_event",counters,"    if (++w.unchecked < 1024) return;","    ++w.unchecked;",False),
            ("wrong_scope_owner",counters,"current.owner == owner ? current.origin : OrderBarrierOrigin::Other","(void(owner),current.origin)",False),
            ("one_way_alias",aliases,"if (forward!=reverse) {++probe.one_way;continue;}","if (forward!=reverse) {++probe.eligible;continue;}",False),
        )
        for name,text,old,new,tracker in mutations:
            assert text.count(old)==1,(name,text.count(old));run(folder,source,text.replace(old,new),name,tracker=tracker,negative=True)
        print("ORDER_RESOURCE_CENSUS_GATE_PASS negatives=7 producer_guards=8",flush=True)


if __name__=="__main__":main()
