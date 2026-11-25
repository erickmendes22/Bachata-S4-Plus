#!/usr/bin/env python3
"""Execute actual scheduler completion/Finish and fault callbacks with nested OOM.

The production UniqueFunction is used so callable moves and captured-resource
lifetime are tested. GPU time and allocation are boundary models; callback
invocation, FIFO mutation and fault iteration are production source.
"""
import argparse
from pathlib import Path
import re

from test_donor_alu_semantics import function, run_cpp


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True)
    args=parser.parse_args();root=args.source
    if (root/"src").exists():root=root/"src"
    source=(root/"video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
    header=(root/"video_core/renderer_vulkan/vk_scheduler.h").read_text()
    pop=function(source,"void Scheduler::PopPendingOperations(")
    finish=function(source,"void Scheduler::Finish(")
    defer=header[header.index("    void DeferOperation("):header.index("    /// Defers an operation",header.index("    void DeferOperation(")+10)]
    unique=(root/"common/unique_function.h").read_text()
    unique=re.sub(r"^\s*#(?:include|pragma)[^\n]*\n","",unique,flags=re.M)
    faults=(root/"video_core/buffer_cache/fault_manager.cpp").read_text()
    callback=faults[faults.index("    scheduler.DeferOperation([this, mapped, area = current_area] {"):]
    callback=callback[:callback.index("\n    });")+len("\n    });")]
    declaration="void PopPendingOperations(bool refresh=true);" if "(bool refresh)" in pop else "void PopPendingOperations();"
    cpp=r'''
#include <algorithm>
#include <bit>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <queue>
#include <utility>
#include <vector>
using u8=uint8_t;using u32=uint32_t;using u64=uint64_t;using VAddr=u64;
#define ASSERT_MSG(x,...) assert(x)
#define LOG_INFO(...) ((void)0)
namespace BachataCompat {inline bool target=false;bool Sotc608(){return target;}}
'''+unique+r'''
struct SubmitInfo {};
struct Semaphore {
    u64 completed=0;unsigned refreshes=0;
    void Refresh(){++refreshes;}bool IsFree(u64 tick)const{return tick<=completed;}
};
struct Scheduler {
    struct PendingOp {Common::UniqueFunction<void> callback;u64 gpu_tick;};
    std::queue<PendingOp> pending_ops;std::recursive_mutex pending_ops_mutex;
    Semaphore work_semaphore;u64 tick=1;unsigned drains=0,finishes=0;
    u64 CurrentTick()const{return tick;}
    void DrainDrawPipe(){++drains;}
    void SubmitExecution(SubmitInfo&){++finishes;work_semaphore.completed=tick++;PopPendingOperations();}
    void Wait(u64 until){assert(work_semaphore.IsFree(until));}
    void Finish();
'''+declaration+defer+r'''
};
'''+pop+finish+r'''
struct RangeSet {
    std::vector<std::pair<u64,u64>> ranges;u64 generation=0;
    void Clear(){++generation;ranges.clear();}
    void Add(u64 a,u64 n){ranges.emplace_back(a,a+n);}
    void ForEach(auto fn){const u64 version=generation;for(size_t i=0;i<ranges.size();++i){
        const auto range=ranges[i];fn(range.first,range.second);assert(version==generation);}}
};
struct BufferCache {
    std::vector<u64> obtained,pinned;std::function<void(u64)> during_obtain;
    void NoteFaultRebind(u64 a,u64){pinned.push_back(a);}
    unsigned ObtainBuffer(u64 a,u64,bool){obtained.push_back(a);if(during_obtain)during_obtain(a);return 0;}
};
struct FaultManager {
    Scheduler& scheduler;BufferCache& buffer_cache;u32 current_area{};u64 sparse_pagesize=4096;
    std::array<u64,4> fault_areas{};
    // Kept in the fixture to detect old code that clears one shared range set.
    RangeSet fault_ranges;
    FaultManager(Scheduler& s,BufferCache& b):scheduler(s),buffer_cache(b){}
    void Queue(const u64* words,u32 area){current_area=area;const auto* mapped=std::bit_cast<const u8*>(words);
        fault_areas[area]=scheduler.CurrentTick();
'''+callback+r'''
    }
};
struct Owned {
    unsigned& destroyed;u64 value=0x12345678;
    explicit Owned(unsigned& d):destroyed(d){}~Owned(){++destroyed;}
};
void TestPopAndLifetime(){
    Scheduler s;std::vector<unsigned> entered;unsigned destroyed=0;bool freed=false;
    s.DeferOperation([&,owned=std::make_unique<Owned>(destroyed)]{
        entered.push_back(1);assert(entered.size()==1); // old code reentered the same callback
        assert(destroyed==0&&owned->value==0x12345678);
        s.Finish(); // nested completion must reclaim callback 2 before allocation retry
        assert(freed&&destroyed==0&&owned->value==0x12345678);
        entered.push_back(3);
    });
    s.DeferOperation([&]{entered.push_back(2);freed=true;});
    s.work_semaphore.completed=1;s.PopPendingOperations();
    assert((entered==std::vector<unsigned>{1,2,3}));assert(destroyed==1&&s.pending_ops.empty());
    assert(s.finishes==1);std::cout<<"GPU_PENDING_POP_LIFETIME_OOM_RELEASE_PASS\n";
}
void TestFifoAndTicks(){
    Scheduler s;std::vector<unsigned> entered;
    s.tick=3;s.DeferOperation([&]{entered.push_back(1);s.DeferOperation([&]{entered.push_back(3);});s.PopPendingOperations();});
    s.DeferOperation([&]{entered.push_back(2);});
    s.work_semaphore.completed=2;s.PopPendingOperations();assert(entered.empty()&&s.pending_ops.size()==2);
    s.work_semaphore.completed=3;s.PopPendingOperations();
    assert((entered==std::vector<unsigned>{1,2,3})&&s.pending_ops.empty());
    // Newly scheduled work at a future tick remains queued through recursive pops.
    s.tick=4;s.DeferOperation([&]{entered.push_back(4);s.tick=5;
        s.DeferOperation([&]{entered.push_back(5);});s.PopPendingOperations();});
    s.work_semaphore.completed=4;s.PopPendingOperations();assert(entered.back()==4&&s.pending_ops.size()==1);
    s.work_semaphore.completed=5;s.PopPendingOperations();assert(entered.back()==5&&s.pending_ops.empty());
    std::cout<<"GPU_PENDING_FIFO_TICK_PASS\n";
}
void TestNestedFaultBatches(){
    Scheduler s;BufferCache buffers;FaultManager faults{s,buffers};bool freed=false,first=true;
    const std::array<u64,3> batch_a{2,0x10000,0x30000},batch_b{2,0x20000,0x40000};
    faults.Queue(batch_a.data(),0);faults.Queue(batch_b.data(),1);
    s.DeferOperation([&]{freed=true;});
    buffers.during_obtain=[&](u64 address){if(address==0x10000&&std::exchange(first,false)){
        s.Finish();assert(freed&&faults.fault_areas[1]==0);
        assert(faults.fault_areas[0]!=0); // outer batch still owns its callable/ranges
    }};
    s.work_semaphore.completed=1;s.PopPendingOperations();
    assert((buffers.obtained==std::vector<u64>{0x10000,0x20000,0x40000,0x30000}));
    assert(faults.fault_areas[0]==0&&faults.fault_areas[1]==0&&s.pending_ops.empty());
    std::cout<<"GPU_PENDING_NESTED_FAULT_RANGE_OWNERSHIP_PASS\n";
}
int main(){for(bool target:{false,true}){BachataCompat::target=target;
    TestPopAndLifetime();TestFifoAndTicks();TestNestedFaultBatches();}}
'''
    cpp=cpp.replace("#include <algorithm>","#include <algorithm>\n#include <array>",1)
    run_cpp(cpp,"pending_gpu_callbacks")


if __name__=="__main__":main()
