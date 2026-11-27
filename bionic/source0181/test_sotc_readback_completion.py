#!/usr/bin/env python3
"""Exercise the effective readback C++ with fake GPU bytes and real page tracking.

This compiles the actual Gather/Begin/Finish methods and MemoryTracker, not a
second implementation of their logic. Vulkan allocation/copy/submit are mocked
so late CPU writes, sparse holes and overlapping GPU rewrites are deterministic.
"""
import argparse
import ast
import os
from pathlib import Path
import subprocess
import tempfile


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
args = parser.parse_args()
src = (Path(args.source) / "src").resolve()
base = src / "video_core/buffer_cache"
source = (base / "buffer_cache.cpp").read_text()
header = (base / "buffer_cache.h").read_text()
begin = source.index("BachataReadback::Span BufferCache::ReadbackWindow(")
end = source.index("void BufferCache::ReadMemory(", begin)
methods = source[begin:end]
begin = header.index("    struct ReadbackItem {")
end = header.index("    bool SynchronizeMemory(", begin)
declarations = header[begin:end]

# Reuse only the watcher mock shared by the existing real MemoryTracker tests.
shared = ast.parse(Path(__file__).with_name("test_memory_transaction.py").read_text())
stubs = {}
for node in ast.walk(shared):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "write" and len(node.args) == 2
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in {"core/emulator_settings.h", "video_core/page_manager.h"}):
        stubs[node.args[0].value] = ast.literal_eval(node.args[1])
assert len(stubs) == 2

HARNESS = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <functional>
#include <iostream>
#include <memory>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>
#include "common/alignment.h"
#include "video_core/buffer_cache/memory_tracker.h"
#include "video_core/buffer_cache/bachata_readback_span.h"
namespace Common {
struct ElfInfo {
    static ElfInfo& Instance(){static ElfInfo i;return i;}
    std::string_view GameSerial()const{return "CUSA08809";}
};
}
namespace vk { struct BufferCopy {u64 srcOffset{},dstOffset{},size{};}; }
namespace VideoCore {
enum class MemoryType {HostCached};
struct Buffer {
    VAddr cpu_addr{};
    u64 size_bytes{};
    std::vector<u8> bytes;
    bool held{};
    explicit Buffer(u64 n):size_bytes(n),bytes(n){}
};
}
namespace Vulkan {
struct StagingBufferRef {
    VideoCore::Buffer* buffer{};
    u64 offset{},size{};
    u8* mapped{};
    void Invalidate()const {assert(buffer && buffer->held);}
};
struct StagingBufferPool {
    std::deque<VideoCore::Buffer> allocations;
    StagingBufferRef Request(u64 bytes,VideoCore::MemoryType,u64 alignment,bool held){
        assert(alignment==0 && held);
        auto& allocation=allocations.emplace_back(bytes);
        allocation.held=true;
        return {&allocation,0,bytes,allocation.bytes.data()};
    }
    void FreeDeferred(const StagingBufferRef& ref){
        assert(ref.buffer->held);ref.buffer->held=false;
    }
};
struct Scheduler {
    u64 tick=1;
    std::function<void()> on_flush;
    u64 CurrentTick()const{return tick;}
    void Flush(){++tick;if(on_flush){auto callback=std::move(on_flush);callback();}}
};
struct Runtime {
    void CopyBuffer(const VideoCore::Buffer* from,VideoCore::Buffer* to,
                    const std::vector<vk::BufferCopy>& copies){
        for(const auto& copy:copies){
            assert(copy.srcOffset+copy.size<=from->bytes.size());
            assert(copy.dstOffset+copy.size<=to->bytes.size());
            std::memcpy(to->bytes.data()+copy.dstOffset,
                        from->bytes.data()+copy.srcOffset,copy.size);
        }
    }
};
}
namespace VideoCore {
struct Intervals {
    struct Range {u64 begin,end;};
    std::vector<Range> entries;
    void Add(VAddr a,u64 n){entries.push_back({a,a+n});}
    bool Intersects(VAddr a,u64 n)const {
        return std::any_of(entries.begin(),entries.end(),[&](auto r){return a<r.end&&r.begin<a+n;});
    }
    template<class F> void ForEachInRange(VAddr a,u64 n,F&& fn)const {
        for(auto r:entries)if(a<r.end&&r.begin<a+n)
            fn(std::max(a,r.begin),std::min(a+n,r.end));
    }
    void Subtract(VAddr a,u64 n){
        std::vector<Range> keep;
        for(auto r:entries){
            if(r.end<=a||r.begin>=a+n)keep.push_back(r);
            else {if(r.begin<a)keep.push_back({r.begin,a});if(r.end>a+n)keep.push_back({a+n,r.end});}
        }
        entries=std::move(keep);
    }
};
struct Backing {u64 start,end;};
struct Residents {
    std::vector<Backing> entries;
    template<class F> void ForEachInRange(u64 start,u64 end,F&& fn)const {
        for(const auto& r:entries)if(start<r.end&&r.start<end)fn(r);
    }
};
struct Memory {
    std::vector<u8> bytes=std::vector<u8>(1_MB,0x11);
    void WriteSparseBacking(VAddr a,const void* p,u64 n){
        assert(a+n<=bytes.size());std::memcpy(bytes.data()+a,p,n);
    }
};
class BufferCache {
public:
    static constexpr u64 ARENA_PAGE_BITS=32;
    u32 block_shift=14;
    PageManager pages;
    std::unique_ptr<MemoryTracker> memory_tracker=std::make_unique<MemoryTracker>(pages);
    Buffer gpu{1_MB};
    Memory physical;
    Memory* memory=&physical;
    Intervals gpu_modified_ranges;
    Residents resident_ranges;
    Vulkan::StagingBufferPool staging_pool;
    Vulkan::Runtime runtime;
    Vulkan::Scheduler scheduler;
    std::array<const Buffer*,256> address_space{};
    BufferCache(){address_space[0]=&gpu;resident_ranges.entries.push_back({0,1_MB>>block_shift});}
    const Buffer* GetArena(u64 first,u64 last){
        assert(first<=last && (last<<block_shift)<gpu.size_bytes);return &gpu;
    }
    void GpuWrite(VAddr a,u64 n,u8 value){
        auto noop=[](VAddr,u64){};
        memory_tracker->ForEachUploadRange(a,n,true,noop,[]{});
        MarkReadbacksDirty(a,n);
        gpu_modified_ranges.Subtract(a,n);
        gpu_modified_ranges.Add(a,n);
        std::fill(gpu.bytes.begin()+a,gpu.bytes.begin()+a+n,value);
    }
    void Complete(VAddr a,u64 n=1,u64 stream=0){
        AsyncReadback rb{};BeginAsyncReadback(rb,a,n,stream);
        if(rb.tick)assert(FinishAsyncReadback(rb));
    }
@DECLARATIONS@
};
@METHODS@
}
using namespace VideoCore;
int main(){
    constexpr VAddr a=0x10000,b=0x30000;
    {
        BufferCache cache;
        cache.resident_ranges.entries={{a>>14,(a+16_KB)>>14},{(a+32_KB)>>14,(a+64_KB)>>14}};
        cache.GpuWrite(a,64_KB,0x22);
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        assert(rb.items.size()==1 && rb.items.front().copies.size()==2);
        assert(rb.staging.size==48_KB && rb.staging.buffer->held);
        assert(cache.memory_tracker->IsRegionGpuModified(a,64_KB));
        assert(cache.gpu_modified_ranges.Intersects(a,64_KB));
        assert(cache.FinishAsyncReadback(rb));
        assert(!rb.staging.buffer->held && cache.inflight_readbacks.empty());
        assert(cache.physical.bytes[a]==0x22 && cache.physical.bytes[a+20_KB]==0x11);
        assert(cache.physical.bytes[a+40_KB]==0x22);
        cache.GpuWrite(a+16_KB,16_KB,0x55); // GPU page bit with no resident bytes
        BufferCache::AsyncReadback empty{};cache.BeginAsyncReadback(empty,a+20_KB,1,0);
        assert(!empty.tick && !cache.memory_tracker->IsRegionGpuModified(a,64_KB));
        assert(!cache.gpu_modified_ranges.Intersects(a,64_KB));
    }
    {
        BufferCache cache;
        cache.GpuWrite(b,64_KB,0x33);cache.Complete(b);
        cache.GpuWrite(b,64_KB,0x44);cache.GpuWrite(a,64_KB,0x66);
        // A hot page already CPU-dirty at gather is omitted entirely. The
        // neighboring copies must not erase its remaining GPU provenance.
        cache.memory_tracker->MarkRegionAsCpuModified(b+4_KB,4_KB);
        std::fill(cache.physical.bytes.begin()+b+4_KB,cache.physical.bytes.begin()+b+8_KB,0xee);
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        assert(rb.items.size()==2 && rb.items[1].hot);
        assert(cache.FinishAsyncReadback(rb));
        assert(cache.physical.bytes[b]==0x44 && cache.physical.bytes[b+4_KB]==0xee);
        assert(cache.physical.bytes[b+8_KB]==0x44);
        assert(cache.gpu_modified_ranges.Intersects(b+4_KB,4_KB));
        assert(!cache.gpu_modified_ranges.Intersects(b,4_KB));
        assert(!cache.gpu_modified_ranges.Intersects(b+8_KB,56_KB));
        assert(cache.memory_tracker->IsRegionCpuModified(b+4_KB,4_KB));
    }
    {
        BufferCache cache;
        cache.GpuWrite(b,64_KB,0x33);cache.Complete(b);
        cache.GpuWrite(b,64_KB,0x44);cache.GpuWrite(a,64_KB,0x66);
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        assert(rb.items.size()==2 && rb.items[1].hot);
        // Simulate the donor's late CPU ownership case without a GPU rewrite.
        cache.memory_tracker->UnmarkRegionAsGpuModified(b+4_KB,4_KB,false);
        cache.memory_tracker->MarkRegionAsCpuModified(b+4_KB,4_KB);
        std::fill(cache.physical.bytes.begin()+b+4_KB,cache.physical.bytes.begin()+b+8_KB,0xee);
        assert(cache.FinishAsyncReadback(rb));
        assert(cache.physical.bytes[a]==0x66);
        assert(cache.physical.bytes[b]==0x44 && cache.physical.bytes[b+4_KB]==0xee);
        assert(cache.physical.bytes[b+8_KB]==0x44);
    }
    {
        BufferCache cache;
        cache.GpuWrite(b,64_KB,0x33);cache.Complete(b);
        cache.GpuWrite(b,64_KB,0x44);cache.GpuWrite(a,64_KB,0x66);
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        cache.GpuWrite(b,64_KB,0x77); // only the speculative item is dirty
        assert(cache.FinishAsyncReadback(rb));
        assert(cache.physical.bytes[a]==0x66 && cache.physical.bytes[b]==0x33);
        assert(cache.memory_tracker->IsRegionGpuModified(b,64_KB));
        assert(cache.gpu_modified_ranges.Intersects(b,64_KB));
        cache.Complete(b);assert(cache.physical.bytes[b]==0x77);
    }
    {
        BufferCache cache;
        cache.GpuWrite(b,64_KB,0x33);cache.Complete(b);
        cache.GpuWrite(b,64_KB,0x44);cache.GpuWrite(a,64_KB,0x66);
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        cache.GpuWrite(a,64_KB,0x88); // requested item needs a fresh snapshot
        assert(!cache.FinishAsyncReadback(rb));
        assert(cache.physical.bytes[a]==0x11 && cache.physical.bytes[b]==0x44);
        assert(cache.memory_tracker->IsRegionGpuModified(a,64_KB));
        cache.Complete(a);assert(cache.physical.bytes[a]==0x88);
    }
    {
        BufferCache cache;cache.GpuWrite(a,64_KB,0x33);
        cache.scheduler.on_flush=[&]{cache.MarkReadbacksDirty(a,4_KB);};
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        assert(rb.validity.dirty && !cache.FinishAsyncReadback(rb));
        assert(cache.physical.bytes[a]==0x11);
    }
    {
        BufferCache cache;
        cache.GpuWrite(b,128_KB,0x33);cache.Complete(b,1,128_KB);
        cache.GpuWrite(b,128_KB,0x44);cache.GpuWrite(a,64_KB,0x66);
        BufferCache::AsyncReadback rb{};cache.BeginAsyncReadback(rb,a,1,0);
        assert(rb.items.size()==1); // default mode 1 caps each hot item at 64 KiB
        assert(cache.FinishAsyncReadback(rb));
        for(auto& hot:cache.hot_readbacks)hot.last_request-=std::chrono::seconds(3);
        cache.GpuWrite(a,64_KB,0x99);cache.Complete(a);
        assert(cache.hot_readbacks.size()==1);
    }
    {
        // Two simultaneous guest faults inside the same window use one
        // allocation and one submission. Finish may run in either order.
        for(bool dependent_first:{false,true}) {
            BufferCache cache;
            cache.GpuWrite(a,64_KB,0x55);
            BufferCache::AsyncReadback leader{},join{};
            cache.BeginAsyncReadback(leader,a,1,0);
            cache.BeginAsyncReadback(join,a+4_KB,1,0);
            assert(join.dependent && join.tick==leader.tick);
            assert(cache.staging_pool.allocations.size()==1);
            assert(cache.inflight_readbacks.size()==1);
            if(dependent_first) {
                assert(cache.FinishAsyncReadback(join));
                assert(cache.FinishAsyncReadback(leader));
            } else {
                assert(cache.FinishAsyncReadback(leader));
                assert(cache.FinishAsyncReadback(join));
            }
            assert(cache.inflight_readbacks.empty());
            assert(!leader.staging.buffer->held);
            assert(cache.physical.bytes[a+4_KB]==0x55);
        }
    }
    {
        BufferCache cache;
        cache.GpuWrite(a,64_KB,0x55);
        BufferCache::AsyncReadback leader{},join{};
        cache.BeginAsyncReadback(leader,a,1,0);
        cache.BeginAsyncReadback(join,a,1,0);
        cache.GpuWrite(a,64_KB,0x66);
        assert(!cache.FinishAsyncReadback(join));
        assert(!cache.FinishAsyncReadback(leader));
        assert(cache.physical.bytes[a]==0x11);
        cache.Complete(a);assert(cache.physical.bytes[a]==0x66);
    }
    {
        BufferCache cache;
        cache.GpuWrite(a,64_KB,0x55);
        BufferCache::AsyncReadback leader{},join{};
        cache.BeginAsyncReadback(leader,a,1,0);
        cache.BeginAsyncReadback(join,a,1,0);
        assert(cache.FinishAsyncReadback(leader));
        cache.GpuWrite(a,64_KB,0x77);
        assert(!cache.FinishAsyncReadback(join));
        cache.Complete(a);assert(cache.physical.bytes[a]==0x77);
    }
    {
        PageManager pm;auto tracker=std::make_unique<MemoryTracker>(pm);
        const VAddr start=HIGHER_PAGE_SIZE-4_KB;
        auto noop=[](VAddr,u64){};
        tracker->ForEachUploadRange(start,12_KB,false,noop,[]{});
        tracker->MarkRegionAsCpuModified(start+4_KB,4_KB);
        u64 copied=0;
        const auto skipped=tracker->WriteUnlessCpuModified(start,12_KB,[&](VAddr addr,u64 n){
            assert(addr!=start+4_KB);copied+=n;
        });
        assert(skipped==4_KB && copied==8_KB);
        std::atomic<bool> entered{false},marked{false};
        std::atomic<int> value{0};std::thread guest;
        tracker->WriteUnlessCpuModified(start,4_KB,[&](VAddr,u64){
            guest=std::thread([&]{
                entered.store(true,std::memory_order_release);
                tracker->MarkRegionAsCpuModified(start,4_KB);
                marked.store(true,std::memory_order_release);value.store(9);
            });
            while(!entered.load(std::memory_order_acquire))std::this_thread::yield();
            assert(!marked.load(std::memory_order_acquire));value.store(7);
        });
        guest.join();assert(value.load()==9);
    }
    std::cout<<"BACHATA_SOTC_READBACK_COMPLETION_PASS resident-holes/hot-gather-provenance/hot-late-cpu/partial-retry/flush-race/locked-write/joined-faults\n";
}
'''

with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    for name, content in stubs.items():
        target = temporary / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    cpp = temporary / "readback.cpp"
    binary = temporary / "readback"
    cpp.write_text(HARNESS.replace("@DECLARATIONS@", declarations).replace("@METHODS@", methods))
    subprocess.run(["c++", "-std=c++23", "-O2", "-pthread", "-Wall", "-Wextra", "-Werror",
                    "-I", str(temporary), "-isystem", str(src), str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=20,
                   env={**os.environ, "SOTC_RB_HOT": "1", "SOTC_RB_NARROW": "64",
                        "SOTC_FAULT_GRACE": "0"})
