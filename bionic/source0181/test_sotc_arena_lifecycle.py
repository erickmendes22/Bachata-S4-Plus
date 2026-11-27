#!/usr/bin/env python3
"""Compile and execute the effective arena lifecycle against a deterministic GPU.

The allocator, residency, eviction, unmap and pinning methods, Backing and
IntervalList definitions, plus the staging pool's held-allocation lifecycle are
production C++. Vulkan allocation, GPU completion, memory and tracking are the
boundaries mocked here. No source-token check stands in for the contract tests.
"""
import argparse
from pathlib import Path
import re

from test_donor_alu_semantics import function, run_cpp


def strip_includes(text):
    return re.sub(r"^\s*#(?:include|pragma)[^\n]*\n", "", text, flags=re.M)


COMMON = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <chrono>
#include <concepts>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <functional>
#include <iostream>
#include <iterator>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <ranges>
#include <span>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using u8=uint8_t;using u16=uint16_t;using u32=uint32_t;using u64=uint64_t;
using s64=int64_t;using VAddr=u64;using VkDeviceMemory=u64;
constexpr u64 operator""_KB(unsigned long long n){return n<<10;}
constexpr u64 operator""_MB(unsigned long long n){return n<<20;}
constexpr u64 operator""_GB(unsigned long long n){return n<<30;}
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define LOG_INFO(...) ((void)0)
#define LOG_WARNING(...) ((void)0)
#define LOG_CRITICAL(...) ((void)0)
namespace boost::container {template<class T,size_t N>using small_vector=std::vector<T>;}
template<class T,size_t N>using SmallVector=std::vector<T>;
namespace Common {
template<class T>constexpr T AlignUp(T n,T a){return (n+a-1)/a*a;}
struct ElfInfo {std::string serial="CUSA08809";static ElfInfo& Instance(){static ElfInfo e;return e;}
std::string GameSerial()const{return serial;}};
}
namespace vk {
using DeviceMemory=u64;using DeviceAddress=u64;
enum class Result{eSuccess,eErrorOutOfDeviceMemory};
const char* to_string(Result r){return r==Result::eSuccess?"success":"out of memory";}
struct MemoryAllocateInfo {u64 allocationSize;u32 memoryTypeIndex;};
struct SparseMemoryBind {u64 resourceOffset{},size{};DeviceMemory memory{};u64 memoryOffset{};};
struct BufferCopy {u64 srcOffset{},dstOffset{},size{};};
}
namespace Vulkan {
struct DeviceState {
    u64 next=1;std::vector<vk::MemoryAllocateInfo> attempts;std::vector<u64> freed;
    std::function<bool(vk::MemoryAllocateInfo)> reject;
};
struct Device {
    std::shared_ptr<DeviceState> state;
    std::pair<vk::Result,vk::DeviceMemory> allocateMemory(vk::MemoryAllocateInfo a)const{
        state->attempts.push_back(a);
        if(state->reject&&state->reject(a))return {vk::Result::eErrorOutOfDeviceMemory,0};
        return {vk::Result::eSuccess,state->next++};
    }
    void freeMemory(vk::DeviceMemory m)const{assert(m);state->freed.push_back(m);}
};
struct Instance {
    std::shared_ptr<DeviceState> state=std::make_shared<DeviceState>();
    Device GetDevice()const{return {state};}
    u64 UniformMinAlignment()const{return 256;}
    u64 GetDeviceMemoryUsage()const{return 0;}u64 GetTotalMemoryBudget()const{return 1_GB;}
};
vk::DeviceMemory Check(std::pair<vk::Result,vk::DeviceMemory> p){assert(p.first==vk::Result::eSuccess);return p.second;}
struct Scheduler {
    struct Operation {u64 tick;std::function<void()> fn;};
    u64 tick=1,completed=0;unsigned finishes=0,flushes=0;
    std::deque<Operation> gpu,deferred;
    std::function<void()> on_flush,on_finish;
    u64 CurrentTick()const{return tick;}bool IsFree(u64 t)const{return t<=completed;}
    void Record(std::function<void()> f){gpu.push_back({tick,std::move(f)});}
    void DeferOperation(std::function<void()> f){deferred.push_back({tick,std::move(f)});}
    void Flush(){++flushes;if(on_flush)on_flush();++tick;}
    void Complete(u64 until){
        assert(until<tick);while(!gpu.empty()&&gpu.front().tick<=until){gpu.front().fn();gpu.pop_front();}
        completed=std::max(completed,until);
    }
    void PopPendingOperations(){while(!deferred.empty()&&IsFree(deferred.front().tick)){
        auto fn=std::move(deferred.front().fn);deferred.pop_front();fn();}}
    void Finish(){++finishes;Flush();Complete(tick-1);PopPendingOperations();
        if(auto fn=std::exchange(on_finish,{}))fn();}
};
}
namespace VideoCore {
enum class MemoryType {HostCached,HostUncached,DeviceLocal,Sparse};
struct Bytes {
    std::unordered_map<u64,u8> changed;
    u8 Get(u64 address)const{auto i=changed.find(address);return i==changed.end()?u8((address^(address>>10)^0x5a)&255):i->second;}
};
struct Buffer {
    VAddr cpu_addr{};u64 size_bytes{};bool arena=false,pagetable=false;Bytes bytes;
    std::vector<u8> mapped_data;unsigned invalidates=0;
    Buffer()=default;
    Buffer(const Vulkan::Instance&,u64 address,u64 size,MemoryType type,const char* =nullptr)
      :cpu_addr(address),size_bytes(size),arena(type==MemoryType::Sparse),mapped_data(arena?0:size){}
    u64 SizeBytes()const{return mapped_data.size();}
    u64 Offset(VAddr a)const{assert(a>=cpu_addr);return a-cpu_addr;}
    vk::DeviceAddress BufferDeviceAddress()const{return 0x10000000000ULL+cpu_addr;}
    void Flush(u64 offset,u64 size)const{assert(offset+size<=mapped_data.size());}
    void Invalidate(u64 offset,u64 size){assert(offset+size<=mapped_data.size());++invalidates;}
    std::pair<u8*,u64> Map(u64 size,u64){mapped_data.resize(size);return {mapped_data.data(),0};}
    void Commit(){}
};
struct TextureCache {unsigned collections=0;void EmergencyCollect(){++collections;}};
struct Memory {
    Bytes bytes;unsigned reads=0;
    void CopySparseMemory(VAddr addr,u8* target,u64 n){++reads;for(u64 i=0;i<n;++i)target[i]=bytes.Get(addr+i);}
};
}
'''


def arena_test(root):
    source=(root/"video_core/buffer_cache/buffer_cache.cpp").read_text()
    header=(root/"video_core/buffer_cache/buffer_cache.h").read_text()
    pool=(root/"video_core/renderer_vulkan/vk_staging_buffer_pool.cpp").read_text()
    pool_h=(root/"video_core/renderer_vulkan/vk_staging_buffer_pool.h").read_text()
    staging_classes=strip_includes((root/"video_core/renderer_vulkan/bachata_staging_classes.h").read_text())
    staging_policy=function(pool,"bool SotcStagingLargePow2(")
    interval=strip_includes((root/"common/interval_set.h").read_text())
    spans=strip_includes((root/"video_core/buffer_cache/bachata_readback_span.h").read_text())
    members=header[header.index("    static constexpr u64 ARENA_CHUNK_SIZE"):
                   header.index("    u32 arena_memory_type_index{};")]
    backing=header[header.index("    struct Backing :"):
                   header.index("    IntervalList<Backing> resident_ranges;")]
    hot=header[header.index("    struct HotReadback {"):
               header.index("    std::vector<HotReadback> hot_readbacks;")]
    binds=header[header.index("    struct ArenaBinds {"):
                 header.index("    const Buffer* GetArena(")]
    helper=source[source.index("namespace {\nbool IsSotcArena()"):
                  source.index("const Buffer* BufferCache::EnsureResident(")]
    staging_ref=pool_h[pool_h.index("struct StagingBufferRef {"):pool_h.index("class StagingBufferPool {")]
    # The unchanged upstream IntervalList compares iterator differences to sizes.
    # Keep that header verbatim while retaining -Werror for the adapted methods.
    cpp=COMMON+'\n#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wsign-compare"\n'+interval+'\n#pragma GCC diagnostic pop\n'+spans+'\n'+staging_classes+r'''
namespace Vulkan {
using VideoCore::MemoryType;
'''+staging_ref+r'''
constexpr u64 LARGE_MIN_GRANULARITY=64_KB;
'''+function(pool,"u64 RoundAllocationSize(")+'\n'+staging_policy+r'''
struct StagingBufferPool {
    struct LargeBuffer {std::unique_ptr<VideoCore::Buffer> buffer;u64 tick,last_used_frame;bool held;};
    const Instance& instance;Scheduler& scheduler;u64 frame=0;
    std::array<std::vector<LargeBuffer>,3> large_caches;
    StagingBufferPool(const Instance& i,Scheduler& s):instance(i),scheduler(s){}
    StagingBufferRef Request(u64 n,MemoryType t,u64=0,bool held=false){return RequestLarge(n,t,held,false);}
    StagingBufferRef RequestLarge(u64,MemoryType,bool,bool);
    void FreeDeferred(const StagingBufferRef&);
    bool Held(const StagingBufferRef& r)const{for(const auto& e:large_caches[u32(r.type)])if(e.buffer.get()==r.buffer)return e.held;std::abort();}
};
'''+function(pool,"StagingBufferRef StagingBufferPool::RequestLarge(")+function(pool,"void StagingBufferPool::FreeDeferred(")+r'''
struct Runtime {
    Scheduler& scheduler;
    struct Fill {u64 offset,size;u32 value;};std::vector<Fill> fills;
    explicit Runtime(Scheduler& s):scheduler(s){}
    template<class Copies>void CopyBuffer(const VideoCore::Buffer* src,VideoCore::Buffer* dst,const Copies& copies){
        for(auto c:copies){scheduler.Record([src,dst,c]{
            if(dst->pagetable)return;
            assert(c.dstOffset+c.size<=dst->mapped_data.size());
            if(src->arena){for(u64 i=0;i<c.size;++i)dst->mapped_data[c.dstOffset+i]=src->bytes.Get(src->cpu_addr+c.srcOffset+i);}
            else{assert(c.srcOffset+c.size<=src->mapped_data.size());std::memcpy(dst->mapped_data.data()+c.dstOffset,src->mapped_data.data()+c.srcOffset,c.size);}
        });}
    }
    void FillBuffer(VideoCore::Buffer*,u64 offset,u64 size,u32 value){fills.push_back({offset,size,value});}
};
}
namespace VideoCore {
struct Ranges {
    IntervalList<> ranges;
    bool Intersects(VAddr a,u64 n)const{return ranges.Overlaps(a,a+n);}
    void Add(VAddr a,u64 n){ranges.Add({a,a+n});}
    void Clear(){ranges.Clear();}
    void Subtract(VAddr a,u64 n){IntervalList<> out;for(auto r:ranges){if(r.end<=a||r.start>=a+n)out.Add(r);
        else{if(r.start<a)out.Add({r.start,a});if(r.end>a+n)out.Add({a+n,r.end});}}ranges=std::move(out);}
};
struct MemoryTracker {
    Ranges gpu,cpu;std::vector<Interval> marked;
    bool IsRegionGpuModified(VAddr a,u64 n)const{return gpu.Intersects(a,n);}
    bool IsRegionCpuModified(VAddr a,u64 n)const{return cpu.Intersects(a,n);}
    void MarkRegionAsCpuModified(VAddr a,u64 n){cpu.Add(a,n);marked.push_back({a,a+n});}
    void UnmarkRegionAsGpuModified(VAddr a,u64 n,bool){gpu.Subtract(a,n);}
};
struct BufferCache {
    static constexpr u64 ARENA_PAGE_BITS=32,NUM_ARENA_PAGES=256,ARENA_PAGE_SIZE=4_GB,STREAM_THRESHOLD=16_KB;
    u32 block_shift=16,block_size=1u<<16,blocks_per_arena_page_shift=16;
    Vulkan::Instance instance;Vulkan::Scheduler scheduler;Vulkan::StagingBufferPool staging_pool;
    Vulkan::Runtime runtime;TextureCache texture_cache;
    std::unique_ptr<Memory> memory=std::make_unique<Memory>();
    std::unique_ptr<MemoryTracker> memory_tracker=std::make_unique<MemoryTracker>();
    std::unique_ptr<Buffer> bda_pagetable_buffer=std::make_unique<Buffer>();
    Buffer arena0,arena1,stream_buffer;std::array<const Buffer*,NUM_ARENA_PAGES> address_space{};
    std::deque<Buffer> arenas;const Buffer* synchronized_arena{};
'''+binds+backing+hot+r'''
    IntervalList<Backing> resident_ranges;u64 resident_version{};
    std::unordered_map<VkDeviceMemory,u64> backing_blocks;std::vector<vk::DeviceMemory> fresh_backings;
    bool coherent_arena_upload=true;std::vector<ArenaBinds> pending_binds;
    std::vector<std::vector<vk::SparseMemoryBind>> submitted_binds;
    std::vector<HotReadback> hot_readbacks;
    Ranges gpu_modified_ranges,srt_source_pages;std::vector<Interval> dirty_readbacks;
'''+members+r'''
    u32 arena_memory_type_index=2;
    BufferCache():staging_pool(instance,scheduler),runtime(scheduler){
        block_last_use=static_cast<u16*>(std::calloc(1u<<24,sizeof(u16)));assert(block_last_use);
        arena0.arena=true;arena1.arena=true;arena1.cpu_addr=1_GB*4;
        arena0.size_bytes=arena1.size_bytes=4_GB;
        address_space[0]=&arena0;address_space[1]=&arena1;bda_pagetable_buffer->pagetable=true;
        scheduler.on_flush=[this]{for(const auto& b:pending_binds)submitted_binds.push_back(b.binds);pending_binds.clear();};
    }
    ~BufferCache(){std::free(block_last_use);}
    const Buffer* EnsureResident(const Buffer*,u64,u64);void EnsureResidentLegacy(const Buffer*,u64,u64);
    const Buffer* GetArena(u64,u64);
    std::pair<const Buffer*,u64> ObtainBuffer(VAddr,u32,bool,bool=false);
    bool IsRegionGpuModified(VAddr a,u64 n){return memory_tracker->IsRegionGpuModified(a,n);}
    bool SynchronizeMemory(const Buffer* arena,VAddr,u64,bool,bool){synchronized_arena=arena;return false;}
    void SynchronizeMemoryFromImage(const Buffer* arena,VAddr,u64){synchronized_arena=arena;}
    bool MaybeEvictCold(std::chrono::steady_clock::time_point);void NoteFaultRebind(VAddr,u64);
    void ReleaseUnmappedArena(VAddr,u64);
    void MarkReadbacksDirty(VAddr a,u64 n){dirty_readbacks.push_back({a,a+n});}
};
'''+helper
    for signature in ["const Buffer* BufferCache::EnsureResident(","void BufferCache::EnsureResidentLegacy(",
                      "const Buffer* BufferCache::GetArena(",
                      "std::pair<const Buffer*, u64> BufferCache::ObtainBuffer(",
                      "std::pair<vk::DeviceMemory, u64> BufferCache::AllocateArenaBlocks(",
                      "u64 BufferCache::ArenaUsedBytes(","void BufferCache::FreeArenaBlocks(",
                      "void BufferCache::UnbindResident(","bool BufferCache::MaybeEvictCold(",
                      "bool BufferCache::FinishEviction(","void BufferCache::NoteFaultRebind(",
                      "void BufferCache::ReleaseUnmappedArena("]:
        cpp+=function(source,signature)
    cpp+=r'''
}
using VideoCore::BufferCache;using VideoCore::Buffer;using VideoCore::MemoryType;
using Time=std::chrono::steady_clock::time_point;
Time At(u64 seconds){return Time{}+std::chrono::seconds(seconds);}
constexpr u64 B=1u<<16;
void Sotc(){Common::ElfInfo::Instance().serial="CUSA08809";}
void Seed(BufferCache& c){
    Sotc();for(u64 first:{0u,16u,32u})c.EnsureResident(&c.arena0,first,first+7);
    c.scheduler.Finish();c.submitted_binds.clear();
    assert(c.ArenaUsedBytes()==24*B);assert(c.resident_ranges.Size()==3);
}
void CompleteCopies(BufferCache& c){c.scheduler.Flush();c.scheduler.Complete(c.scheduler.CurrentTick()-1);}
void TestAllocate(){
    BufferCache c;Sotc();auto a=c.AllocateArenaBlocks(3),b=c.AllocateArenaBlocks(3),d=c.AllocateArenaBlocks(3),e=c.AllocateArenaBlocks(3);
    assert(a.first==b.first&&b.first==d.first&&d.first==e.first);
    assert(a.second==0&&b.second==3&&d.second==6&&e.second==9);
    assert(c.instance.state->attempts.size()==1&&c.fresh_backings.size()==1);
    c.FreeArenaBlocks(b.first,b.second,3);c.FreeArenaBlocks(d.first,d.second,3);
    auto middle=c.AllocateArenaBlocks(6);assert(middle.first==a.first&&middle.second==3);
    assert(c.instance.state->attempts.size()==1&&c.fresh_backings.size()==1);
    c.FreeArenaBlocks(a.first,a.second,3);c.FreeArenaBlocks(e.first,e.second,3);c.FreeArenaBlocks(middle.first,middle.second,6);
    assert(c.arena_chunks.empty()&&c.chunk_by_memory.empty()&&c.ArenaUsedBytes()==0);
    assert(c.instance.state->freed.empty());c.scheduler.Finish();assert(c.instance.state->freed==std::vector<u64>{a.first});
    // All permutations of four holes coalesce to one reusable run, independent of free order.
    std::array<unsigned,4> order{0,1,2,3};unsigned permutations=0;
    do{BufferCache p;std::array<std::pair<u64,u64>,5> taken;
        for(auto& t:taken)t=p.AllocateArenaBlocks(2);
        for(auto i:order)p.FreeArenaBlocks(taken[i].first,taken[i].second,2);
        auto run=p.AllocateArenaBlocks(8);assert(run.first==taken[0].first&&run.second==0);
        assert(p.instance.state->attempts.size()==1);++permutations;
    }while(std::next_permutation(order.begin(),order.end()));assert(permutations==24);
    {BufferCache p;p.arena_fallback_memory_type_index=9;
     p.instance.state->reject=[](auto a){return a.memoryTypeIndex==2;};
     auto x=p.AllocateArenaBlocks(4),y=p.AllocateArenaBlocks(4);
     assert(x.first==y.first&&y.second==4);assert(p.arena_chunks[0]->memory_type==9);
     assert(p.fresh_backings.empty()&&p.texture_cache.collections==0);}
    {BufferCache p;p.instance.state->reject=[](auto a){return a.allocationSize>=64_MB;};
     auto x=p.AllocateArenaBlocks(3);assert(x.second==0&&p.texture_cache.collections==1&&p.scheduler.finishes==1);
     assert(p.instance.state->attempts.size()==3&&p.instance.state->attempts.back().allocationSize==3*B);}
    {BufferCache p;p.arena_fallback_memory_type_index=9;
     p.instance.state->reject=[](auto a){return a.memoryTypeIndex==2||a.allocationSize>=64_MB;};
     p.AllocateArenaBlocks(3);assert(p.arena_chunks[0]->memory_type==9&&p.texture_cache.collections==1);}
    std::cout<<"SOTC_ARENA_ALLOCATOR_PASS permutations="<<permutations<<"\n";
}
void TestHeldAndBatches(){
    BufferCache c;Seed(c);c.hot_readbacks.push_back({{32*B,40*B},At(0)});
    assert(!c.MaybeEvictCold(At(100))&&c.pending_eviction);
    const auto download=c.pending_eviction->download;
    assert(c.staging_pool.Held(download));assert(download.buffer->invalidates==0);
    auto other=c.staging_pool.Request(download.size,MemoryType::HostCached,0,true);
    assert(other.buffer!=download.buffer);c.staging_pool.FreeDeferred(other);
    assert(!c.FinishEviction(At(101),30,false));assert(download.buffer->invalidates==0);
    CompleteCopies(c);
    // A later submitted command buffer also protects sparse bindings, even when the download is done.
    c.scheduler.Record([]{});c.scheduler.Flush();
    assert(!c.FinishEviction(At(101),30,false));assert(c.staging_pool.Held(download));
    c.scheduler.Complete(c.scheduler.CurrentTick()-1);
    c.BindsForArena(&c.arena0)->binds.push_back({32*B,8*B,77,0});
    assert(!c.MaybeEvictCold(At(102))&&c.pending_eviction&&c.staging_pool.Held(download));
    c.scheduler.Complete(c.scheduler.CurrentTick()-1);
    assert(c.MaybeEvictCold(At(103))&&!c.pending_eviction);
    assert(!c.staging_pool.Held(download)&&download.buffer->invalidates==1);
    assert(c.ArenaUsedBytes()==8*B&&c.resident_ranges.Size()==1&&c.hot_readbacks.empty());
    assert(c.memory_tracker->marked.size()==2&&c.dirty_readbacks.size()==2&&c.runtime.fills.size()==2);
    assert(c.submitted_binds.size()==2&&c.submitted_binds[0].size()==1&&c.submitted_binds[0][0].memory==77);
    assert(c.submitted_binds[1].size()==2);
    for(auto bind:c.submitted_binds[1])assert(bind.memory==0);
    for(auto f:c.runtime.fills)assert(f.value==0&&f.size==8*sizeof(vk::DeviceAddress));
    // FreeDeferred releases the hold but not the current GPU-tick reuse protection.
    auto not_yet=c.staging_pool.Request(download.size,MemoryType::HostCached,0,true);
    assert(not_yet.buffer!=download.buffer);c.staging_pool.FreeDeferred(not_yet);
    c.scheduler.Finish();auto reused=c.staging_pool.Request(download.size,MemoryType::HostCached,0,true);
    assert(reused.buffer==download.buffer);c.staging_pool.FreeDeferred(reused);
    // A fault pins only the evicted intersection; a normal rebind clears eviction, not its pin.
    c.NoteFaultRebind(32*B+16,B);assert(c.pinned_ranges.Contains(32,34));
    assert(!c.pinned_ranges.Contains(31));c.EnsureResident(&c.arena0,32,33);
    assert(!c.evicted_ranges.Overlaps(32,34)&&c.pinned_ranges.Contains(32,34));
    std::cout<<"SOTC_ARENA_STAGING_SPARSE_ORDER_PASS\n";
}
void TestProtection(){
    for(unsigned kind=0;kind<4;++kind){
        BufferCache c;Seed(c);assert(!c.MaybeEvictCold(At(100))&&c.pending_eviction);
        for(const auto& pick:c.pending_eviction->chosen)for(const auto& r:pick.ranges){
            if(kind==0)for(u64 b=r.start;b<r.end;++b)c.block_last_use[b]=101;
            if(kind==1)c.memory_tracker->gpu.Add(r.start*B,(r.end-r.start)*B);
            if(kind==2)c.gpu_modified_ranges.Add(r.start*B,(r.end-r.start)*B);
            if(kind==3)c.pinned_ranges.Add({r.start,r.end});
        }
        CompleteCopies(c);assert(c.MaybeEvictCold(At(101)));
        assert(c.resident_ranges.Size()==3&&c.ArenaUsedBytes()==24*B);
        assert(c.evicted_ranges.Empty()&&c.memory_tracker->marked.empty()&&c.runtime.fills.empty());
    }
    for(unsigned kind=0;kind<4;++kind){
        BufferCache c;Seed(c);
        for(const auto& r:c.resident_ranges){
            if(kind==0)for(u64 b=r.start;b<r.end;++b)c.block_last_use[b]=100;
            if(kind==1)c.memory_tracker->gpu.Add(r.start*B,(r.end-r.start)*B);
            if(kind==2)c.gpu_modified_ranges.Add(r.start*B,(r.end-r.start)*B);
            if(kind==3)c.pinned_ranges.Add({r.start,r.end});
        }
        assert(!c.MaybeEvictCold(At(100))&&!c.pending_eviction);
    }
    {BufferCache c;Seed(c);assert(!c.MaybeEvictCold(At(100))&&c.pending_eviction);
     const auto before=c.scheduler.finishes;assert(c.FinishEviction(At(106),30,false));
     assert(c.scheduler.finishes==before+1&&c.resident_ranges.Size()==1);}
    std::cout<<"SOTC_ARENA_LIVE_DIRTY_PINNED_DEADLINE_PASS cases=9\n";
}
void TestMismatch(){
    BufferCache c;Seed(c);
    for(const auto& r:c.resident_ranges){const auto a=r.start*B;c.arena0.bytes.changed[a]=u8(c.memory->bytes.Get(a)^255);}
    assert(!c.MaybeEvictCold(At(100)));CompleteCopies(c);assert(c.MaybeEvictCold(At(101)));
    assert(c.evict_retry.size()==2&&c.resident_ranges.Size()==3&&c.evicted_ranges.Empty());
    for(auto [key,deadline]:c.evict_retry){(void)key;assert(deadline==At(161));}
    assert(!c.MaybeEvictCold(At(103)));assert(c.pending_eviction&&c.pending_eviction->chosen.size()==1);
    for(const auto& p:c.pending_eviction->chosen)assert(!c.evict_retry.contains(p.key));
    CompleteCopies(c);assert(c.MaybeEvictCold(At(104)));assert(c.evict_retry.size()==3);
    assert(!c.MaybeEvictCold(At(106))&&!c.pending_eviction);
    assert(!c.MaybeEvictCold(At(162))&&c.pending_eviction); // expired mismatches are reconsidered
    // CPU-dirty data need not match the GPU: the next bind uploads it by contract.
    c.memory_tracker->cpu.Add(0,48*B);CompleteCopies(c);assert(c.MaybeEvictCold(At(163)));
    assert(c.resident_ranges.Size()==1&&c.ArenaUsedBytes()==8*B);
    std::cout<<"SOTC_ARENA_MISMATCH_RETRY_CPU_DIRTY_PASS\n";
}
void TestIdentity(){
    for(unsigned change=0;change<4;++change){BufferCache c;Seed(c);
        assert(!c.MaybeEvictCold(At(100))&&c.pending_eviction);
        const auto old=c.pending_eviction->chosen[0].ranges[0];
        auto replacement=old;
        if(change==0)replacement.offset+=31;
        if(change==1)replacement.memory+=80;
        if(change==2){replacement.start++;replacement.offset++;}
        c.scheduler.on_finish=[&]{
            VideoCore::SubtractArenaIntervals(c.resident_ranges,old.start,old.end);
            if(change!=3)c.resident_ranges.Add(replacement);
            c.BindsForArena(&c.arena0)->binds.push_back({old.start*B,8*B,88,0});
        };
        assert(c.FinishEviction(At(100),30,true));
        assert(!c.evicted_ranges.Overlaps(old.start,old.end));
        assert(!c.memory_tracker->cpu.Intersects(old.start*B,8*B));
        for(const auto& batch:c.submitted_binds){bool nonzero=false,zero=false;
            for(const auto& bind:batch){nonzero|=bind.memory!=0;zero|=bind.memory==0;}assert(!(nonzero&&zero));}
    }
    // Crossing an arena page boundary emits a null sparse bind for each owning arena.
    {BufferCache c;auto [memory,offset]=c.AllocateArenaBlocks(2);
     BufferCache::Backing range{{65535,65537},memory,offset};
     c.UnbindResident(std::span{&range,1});assert(c.pending_binds.size()==2);
     assert(c.pending_binds[0].binds[0].resourceOffset==4_GB-B);
     assert(c.pending_binds[1].binds[0].resourceOffset==0);
     assert(c.instance.state->freed.empty());c.scheduler.Finish();assert(c.instance.state->freed.size()==1);}
    std::cout<<"SOTC_ARENA_BACKING_IDENTITY_REVALIDATION_PASS cases=5\n";
}
void TestLegacyAndUnmap(){
    for(const char* serial:{"CUSA00785","CUSA12345"}){BufferCache c;Common::ElfInfo::Instance().serial=serial;
        c.EnsureResident(&c.arena0,10,19);assert(c.arena_chunks.empty()&&c.backing_blocks.size()==1);
        assert(c.instance.state->attempts[0].allocationSize==10*B);
        const auto memory=c.resident_ranges.begin()->memory;
        c.EnsureResident(&c.arena0,10,19);assert(c.instance.state->attempts.size()==1);
        assert(!c.MaybeEvictCold(At(100))&&!c.pending_eviction);
        c.ReleaseUnmappedArena(12*B,4*B);assert(c.resident_ranges.Size()==2&&c.backing_blocks.at(memory)==6);
        auto it=c.resident_ranges.begin();assert(it->start==10&&it->end==12&&it->offset==0);
        ++it;assert(it->start==16&&it->end==20&&it->offset==6);
        assert(c.instance.state->freed.empty());c.ReleaseUnmappedArena(0,32*B);
        assert(c.resident_ranges.Empty()&&c.backing_blocks.empty());c.scheduler.Finish();
        assert(c.instance.state->freed==std::vector<u64>{memory});
    }
    {BufferCache c;Sotc();c.EnsureResident(&c.arena0,10,19);c.EnsureResident(&c.arena0,10,19);
     const auto version=c.resident_version;c.ReleaseUnmappedArena(12*B,4*B);
     assert(c.resident_version!=version&&c.ArenaUsedBytes()==6*B);
     c.EnsureResident(&c.arena0,10,19);assert(c.resident_ranges.Contains(10,20)&&c.ArenaUsedBytes()==10*B);
     assert(c.instance.state->attempts.size()==1); // the returned chunk hole was reused
     c.evicted_ranges.Add({10,20});c.pinned_ranges.Add({10,20});c.ReleaseUnmappedArena(12*B,4*B);
     assert(!c.evicted_ranges.Overlaps(12,16)&&!c.pinned_ranges.Overlaps(12,16));
     assert(c.pinned_ranges.Contains(10,12)&&c.pinned_ranges.Contains(16,20));}
    {BufferCache c;Common::ElfInfo::Instance().serial="CUSA12345";
     c.EnsureResident(&c.arena0,0,1024);assert(c.arena_chunks.empty()&&c.backing_blocks.size()==2);
     assert(c.instance.state->attempts[0].allocationSize==64_MB&&c.instance.state->attempts[1].allocationSize==B);}
    Sotc();std::cout<<"SOTC_ARENA_LEGACY_UNMAP_CACHE_PASS cases=4\n";
}
void TestAllocationRecoveryRebind(){
    for(bool migrate:{false,true})for(bool partial:{false,true}){BufferCache c;Sotc();unsigned attempts=0;
        const u64 first=migrate?65546:10;const Buffer* current=migrate?&c.arena1:&c.arena0;
        c.instance.state->reject=[&](auto){return ++attempts==1;};
        c.scheduler.on_finish=[&]{
            if(migrate)current=c.GetArena(65535,65536);
            current=c.EnsureResident(current,first+(partial?2:0),first+3);
        };
        const auto [result,offset]=c.ObtainBuffer(first*B,4*B,false);
        assert(c.resident_ranges.Contains(first,first+4)&&c.ArenaUsedBytes()==4*B);
        assert(result==current&&result==c.synchronized_arena&&offset==current->Offset(first*B));
        if(migrate){assert(result!=&c.arena1&&result->cpu_addr==0&&offset==first*B);}
        // No overlapping binds to the same guest blocks may share a sparse batch.
        for(const auto& batch:c.pending_binds){assert(batch.arena==current);for(size_t i=0;i<batch.binds.size();++i)
          for(size_t j=i+1;j<batch.binds.size();++j){const auto& a=batch.binds[i];const auto& b=batch.binds[j];
            assert(a.resourceOffset+a.size<=b.resourceOffset||b.resourceOffset+b.size<=a.resourceOffset);}}
        assert(c.arena_chunks.size()==1&&c.instance.state->attempts.size()==2);
    }
    // The first gap may already own an unpublished run when the second gap hits OOM.
    // A nested callback can bind the first gap from a different run in the new chunk.
    {BufferCache c;Sotc();c.EnsureResident(&c.arena0,12,13);
     const auto held=c.AllocateArenaBlocks(1020);(void)held;unsigned attempts=0;
     c.instance.state->reject=[&](auto){return ++attempts==1;};
     BufferCache::Backing nested{};
     c.scheduler.on_finish=[&]{c.EnsureResident(&c.arena0,10,11);nested=*c.resident_ranges.Find(10);};
     c.EnsureResident(&c.arena0,10,15);
     assert(c.resident_ranges.Contains(10,16)&&c.ArenaUsedBytes()==1026*B);
     const auto preserved=*c.resident_ranges.Find(10);
     assert(preserved.memory==nested.memory&&preserved.offset==nested.offset);
     assert(c.chunk_by_memory.at(nested.memory)->used_blocks>=2);}
    std::cout<<"SOTC_ARENA_OOM_NESTED_REBIND_RESERVATION_PASS cases=5\n";
}
void TestEvictionFlushRebind(){
    for(unsigned kind=0;kind<4;++kind){BufferCache c;Seed(c);
        assert(!c.MaybeEvictCold(At(100))&&c.pending_eviction);
        const auto download=c.pending_eviction->download;CompleteCopies(c);
        c.BindsForArena(&c.arena0)->binds.push_back({100*B,B,77,0});
        bool injected=false;auto ordinary_flush=c.scheduler.on_flush;
        c.scheduler.on_flush=[&]{ordinary_flush();if(std::exchange(injected,true))return;
            for(const auto& pick:c.pending_eviction->chosen)for(const auto& r:pick.ranges){
                if(kind==0)for(u64 b=r.start;b<r.end;++b)c.block_last_use[b]=102;
                if(kind==1)c.memory_tracker->gpu.Add(r.start*B,(r.end-r.start)*B);
                if(kind==2)c.gpu_modified_ranges.Add(r.start*B,(r.end-r.start)*B);
                if(kind==3)c.pinned_ranges.Add({r.start,r.end});
            }
        };
        assert(!c.MaybeEvictCold(At(101))&&c.pending_eviction);
        assert(c.staging_pool.Held(download)&&download.buffer->invalidates==0);
        c.scheduler.Complete(c.scheduler.CurrentTick()-1);
        assert(c.MaybeEvictCold(At(102))&&!c.pending_eviction);
        assert(c.resident_ranges.Size()==3&&c.ArenaUsedBytes()==24*B&&c.evicted_ranges.Empty());
        assert(!c.staging_pool.Held(download)&&c.runtime.fills.empty());
    }
    std::cout<<"SOTC_ARENA_FLUSH_REBIND_RETIREMENT_PASS cases=4\n";
}
void TestUnmapNestedRebind(){
    for(const char* serial:{"CUSA08809","CUSA00785"})for(bool neighbours:{false,true}){
        BufferCache c;Common::ElfInfo::Instance().serial=serial;
        c.EnsureResident(&c.arena0,neighbours?8:10,11);
        if(neighbours)c.EnsureResident(&c.arena0,16,17);
        bool armed=false,injected=false;u64 last_bind_tick=0;unsigned unbinds=0;
        const auto ordinary_flush=c.scheduler.on_flush;
        c.scheduler.on_finish=[&]{c.EnsureResident(&c.arena0,12,13);armed=true;};
        c.scheduler.on_flush=[&]{
            for(const auto& batch:c.pending_binds)for(const auto& bind:batch.binds){
                if(bind.memory)last_bind_tick=c.scheduler.CurrentTick();
                else {++unbinds;assert(c.scheduler.IsFree(last_bind_tick));}
            }
            ordinary_flush();
            // The second completion publishes a range absent from the first
            // post-Finish snapshot. It must be submitted, retired and recollected.
            if(armed&&!std::exchange(injected,true))c.EnsureResident(&c.arena0,14,15);
        };
        c.ReleaseUnmappedArena(10*B,6*B);
        assert(injected&&unbinds&&c.scheduler.finishes==3);
        assert(!c.resident_ranges.Overlaps(10,16));
        u64 used=c.ArenaUsedBytes();
        for(const auto& [memory,blocks]:c.backing_blocks){(void)memory;used+=blocks*B;}
        assert(used==(neighbours?4:0)*B);
        assert(c.resident_ranges.Size()==(neighbours?2:0));
        if(neighbours){assert(c.resident_ranges.Contains(8,10));assert(c.resident_ranges.Contains(16,18));}
        // A sparse submission must never bind and unbind an overlapping range.
        for(const auto& batch:c.submitted_binds)for(size_t i=0;i<batch.size();++i)
            for(size_t j=i+1;j<batch.size();++j){const auto& a=batch[i];const auto& b=batch[j];
                if(bool(a.memory)!=bool(b.memory))
                    assert(a.resourceOffset+a.size<=b.resourceOffset||b.resourceOffset+b.size<=a.resourceOffset);}
        c.scheduler.Finish();
    }
    Sotc();std::cout<<"SOTC_ARENA_UNMAP_NESTED_REBIND_PASS cases=4\n";
}
int main(){
    setenv("SOTC_ARENA_EVICT_MB","1",1);setenv("SOTC_ARENA_EVICT_STEP_MB","1",1);
    setenv("SOTC_ARENA_EVICT_IDLE_S","30",1);setenv("SOTC_EVICT_ASYNC","1",1);
    setenv("SOTC_ARENA_GROUP","1",1);
    TestAllocate();TestHeldAndBatches();TestProtection();TestMismatch();TestIdentity();TestLegacyAndUnmap();TestAllocationRecoveryRebind();TestEvictionFlushRebind();TestUnmapNestedRebind();
}
'''
    run_cpp(cpp,"sotc_arena_lifecycle")


def emergency_test(root):
    source=(root/"video_core/texture_cache/texture_cache.cpp").read_text()
    refresh=function(source,"void TextureCache::RefreshImage(")
    guard=refresh[refresh.index("{\n")+2:refresh.index("    if (False(image.flags")]
    cpp=COMMON+r'''
template<class F>struct ScopeExit{F fn;~ScopeExit(){fn();}};
struct ScopeTag{};template<class F>auto operator+(ScopeTag,F fn){return ScopeExit<F>{fn};}
#define SCOPE_EXIT const auto scope_exit=ScopeTag{}+[&]()
struct CheckedMutex {
    bool owned=false,contended=false;unsigned attempts=0;
    bool try_lock(){assert(!owned);++attempts;if(contended)return false;owned=true;return true;}
    void unlock(){assert(owned);owned=false;}
};
using ImageId=unsigned;
struct FakeImage {bool download=false;struct{bool tiled=false;bool IsTiled()const{return tiled;}}info;
    bool SafeToDownload()const{return download;}};
struct TextureCache {
    inline static thread_local u32 arena_refresh_depth{};
    std::atomic_bool arena_emergency_pending{};CheckedMutex mutex;
    u64 gc_tick=10;std::vector<FakeImage> slot_images=std::vector<FakeImage>(600);
    std::vector<ImageId> downloaded,freed;unsigned image_gcs=0,sampler_gcs=0;
    struct Lru {void ForEachItemBelow(u64,auto fn){for(unsigned i=0;i<600;++i)if(fn(i))break;}}lru_cache;
    void DownloadImageMemory(ImageId id){downloaded.push_back(id);}void FreeImage(ImageId id){freed.push_back(id);}
    void GarbageCollectImages(){++image_gcs;}void GarbageCollectSamplers(){++sampler_gcs;}
    void EmergencyCollect();void RunGarbageCollector();
    void RefreshProbe(){
'''+guard+r'''
        assert(arena_refresh_depth==1);EmergencyCollect();
    }
};
'''+function(source,"void TextureCache::EmergencyCollect(")+function(source,"void TextureCache::RunGarbageCollector(")+r'''
int main(){TextureCache c;c.mutex.owned=true;c.RefreshProbe();
    assert(c.arena_refresh_depth==0&&c.mutex.attempts==0&&c.arena_emergency_pending.load());
    assert(c.freed.empty());c.mutex.owned=false;c.mutex.contended=true;c.RunGarbageCollector();
    assert(c.mutex.attempts==1&&c.arena_emergency_pending.load()&&c.freed.empty());
    c.mutex.contended=false;c.slot_images[0].download=true;c.slot_images[0].info.tiled=true;
    c.slot_images[1].download=true;c.RunGarbageCollector();
    assert(!c.arena_emergency_pending.load()&&c.freed.size()==512&&c.downloaded==std::vector<ImageId>{1});
    assert(std::ranges::find(c.freed,0)==c.freed.end());assert(!c.mutex.owned);
    assert(c.image_gcs==2&&c.sampler_gcs==2&&c.gc_tick==12);
    std::cout<<"SOTC_ARENA_TEXTURE_GC_REENTRANCY_PASS\n";
}
'''
    run_cpp(cpp,"sotc_arena_emergency_collect")


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True)
    args=parser.parse_args();root=args.source
    if (root/"src").exists():root=root/"src"
    arena_test(root);emergency_test(root)


if __name__=="__main__":main()
