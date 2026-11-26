#!/usr/bin/env python3
"""Exercise tracked ReadConst reuse with the effective MemoryTracker/RegionManager.

Vulkan memory/command execution and page protection are boundary fixtures. The
upload, invalidation, readback, sparse-alias copy and snapshot selection methods
come from the final source; no address-only cache replaces the real tracker.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from test_order_readconst_pool import block


PAGE_MANAGER = r'''
#pragma once
#include <cassert>
#include <map>
#include <mutex>
#include "common/types.h"
#include "video_core/buffer_cache/region_definitions.h"
namespace VideoCore {
enum class PageOp : s8 {None=0,Track=1,Untrack=-1};
class PageManager {
public:
    std::pair<int,int> At(VAddr a) {
        std::lock_guard l{mutex};return counts[a/4096];
    }
    void UpdatePageWatchersForRegion(VAddr base,const Bounds& bounds,
        const RegionBits& writes,const RegionBits& reads,PageOp w,PageOp r) {
        std::lock_guard l{mutex};
        for(u64 page=bounds.start_word*PAGES_PER_WORD+bounds.start_page;
            page<=bounds.end_word*PAGES_PER_WORD+bounds.end_page;++page) {
            auto& state=counts[base/4096+page];
            if(w!=PageOp::None&&writes.GetPage(page))state.first+=int(w);
            if(r!=PageOp::None&&reads.GetPage(page))state.second+=int(r);
            assert(state.first>=0&&state.first<=1&&state.second>=0&&state.second<=1);
        }
    }
private:
    std::mutex mutex;
    std::map<u64,std::pair<int,int>> counts;
};
}
'''


PROGRAM = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <numeric>
#include <optional>
#include <shared_mutex>
#include <span>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>
#include <sys/mman.h>
#include "common/types.h"
#include "video_core/buffer_cache/memory_tracker.h"
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define LOG_WARNING(...) ((void)0)
std::vector<std::vector<u64>> stats_logs;
constexpr int Render_Vulkan=0,Render=1;
template<class... T>void CaptureInfo(int,std::string_view format,T... values) {
    if(format.find("BACHATA_ORDER_READCONST_REUSE")!=std::string_view::npos)
        stats_logs.push_back({static_cast<u64>(values)...});
}
#define LOG_INFO CaptureInfo
namespace boost::container {template<class T,size_t N>using small_vector=std::vector<T>;}
namespace Common {
template<class A,class B>constexpr A AlignUp(A n,B a){return (n+A(a)-1)/A(a)*A(a);}
template<class A,class B>constexpr A AlignDown(A n,B a){return n/A(a)*A(a);}
struct ElfInfo {
    std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo i;return i;}
    std::string_view GameSerial()const{return serial;}
};
}
namespace BachataCompat {
@POLICY@
inline bool Sotc608(){return false;}
}
namespace Core {
enum class VMAType{Direct,Flexible,Pooled,Reserved};
enum class MemoryProt:u32{CpuRead=1,CpuWrite=2};
struct PhysicalArea{u64 base,size;};
struct VirtualMemoryArea {
    VAddr base;u64 size;VMAType type=VMAType::Direct;
    std::map<u64,PhysicalArea> phys_areas;
    bool IsMapped()const{return type!=VMAType::Reserved;}
};
class MemoryManager {
public:
    static constexpr VAddr Base=0x4'0000'0000ULL;
    static constexpr u64 Span=32_MB;
    std::shared_mutex mutex;
    u64 alias_copy_bytes{};
    std::map<VAddr,VirtualMemoryArea>vma_map;
    struct AddressSpace {
        std::vector<u8> backing=std::vector<u8>(64_MB);
        u8* BackingBase(){return backing.data();}
    }impl;
    MemoryManager(){
        void* guest=mmap(reinterpret_cast<void*>(Base),Span,PROT_NONE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
        assert(guest==reinterpret_cast<void*>(Base));
        vma_map.emplace(Base,VirtualMemoryArea{Base,Span,VMAType::Direct,{{0,{0,Span}}}});
    }
    ~MemoryManager(){munmap(reinterpret_cast<void*>(Base),Span);}
    auto FindVMA(VAddr address){return std::prev(vma_map.upper_bound(address));}
    bool IsValidMapping(VAddr address){
        auto it=vma_map.upper_bound(address);if(it==vma_map.begin())return false;--it;
        return address>=it->second.base&&address-it->second.base<it->second.size;
    }
    @PHYSICAL@
    void CopySparseMemory(VAddr,u8*,u64);
    void WriteSparseBacking(VAddr,const void*,u64);
    u64 ClampGpuRangeSize(VAddr,u64);
    u64 ClampRangeSize(VAddr,u64);
    int QueryProtection(VAddr address,void** start,void** end,u32* prot){
        if(!IsValidMapping(address))return -1;
        const auto&v=FindVMA(address)->second;if(!v.IsMapped())return -1;
        *start=reinterpret_cast<void*>(v.base);*end=reinterpret_cast<void*>(v.base+v.size);
        *prot=u32(MemoryProt::CpuRead);return 0;
    }
    u8 Byte(VAddr address){u8 value{};CopySparseMemory(address,&value,1);return value;}
};
@MEMORY@
}
namespace vk {
struct BufferCopy {u64 srcOffset,dstOffset,size;};
enum class PipelineStageFlagBits2{eCopy};
enum class AccessFlagBits2{eTransferRead,eTransferWrite};
}
namespace VideoCore {struct Buffer;}
namespace Vulkan {
struct Instance {
    u64 NonCoherentAtomSize()const{return 64;}
    u64 StorageMinAlignment()const{return 256;}
    u64 UniformMinAlignment()const{return 256;}
    u64 StorageMaxRange()const{return 128_MB;}
};
struct SubmitInfo{};
struct Scheduler {
    u64 current=1,submitted{},completed{},waits{};
    std::vector<std::function<void()>>commands,pending;
    std::function<void(VideoCore::Buffer*,VideoCore::Buffer*,std::span<const vk::BufferCopy>)>validate_copy;
    struct Semaphore {
        Scheduler&s;
        u64 CurrentTick()const{return s.current;}
        void Wait(u64 tick){assert(tick<=s.submitted);s.completed=std::max(s.completed,tick);++s.waits;}
    }work_semaphore{*this};
    u64 CurrentTick()const{return current;}
    bool IsFree(u64 tick)const{return tick<=completed;}
    void DrainDrawPipe(){}
    template<class... A>void EndRendering(A&&...){}
    void Flush(SubmitInfo&){for(auto&op:commands)op();commands.clear();submitted=current++;}
    void WaitSubmitted(u64 tick){assert(tick<=submitted);}
    void Wait(u64 tick);
    void Finish(){const auto tick=current;SubmitInfo info;Flush(info);work_semaphore.Wait(tick);}
    template<class F>void DeferOperation(F&&f){pending.emplace_back(std::forward<F>(f));}
    struct Commands {
        Scheduler&s;
        void copyBuffer(VideoCore::Buffer*,VideoCore::Buffer*,std::span<const vk::BufferCopy>)const;
    };
    Commands CommandBuffer(){return {*this};}
};
@WAIT@
}
namespace VideoCore {
enum class MemoryType:u8{DeviceLocal,HostUncached,HostCached,Stream,Sparse};
struct Buffer {
    VAddr cpu_addr;u64 size_bytes;MemoryType mem_type;
    bool is_coherent=false;
    std::vector<u8>storage;
    std::span<u8>mapped_data;
    Buffer(const Vulkan::Instance&,VAddr address,u64 size,MemoryType type,std::string_view={})
        :cpu_addr(address),size_bytes(size),mem_type(type),storage(size,0xa5),mapped_data(storage){}
    u64 SizeBytes()const{return size_bytes;}
    u64 Offset(VAddr address)const{assert(address>=cpu_addr);return address-cpu_addr;}
    Buffer* Handle()const{return const_cast<Buffer*>(this);}
    void Flush(u64 offset,u64 bytes){assert(offset+bytes<=size_bytes);}
    void Invalidate(u64 offset,u64 bytes){assert(offset+bytes<=size_bytes);}
};
constexpr u64 WATCHES_RESERVE_CHUNK=256;
struct StreamBuffer:Buffer {
    Vulkan::Scheduler&scheduler;u64 non_coherent_atom_size=64,offset{},mapped_size{},last_tick{};
    struct Watch{u64 upper_bound{},tick{};};
    std::vector<Watch>current_watches=std::vector<Watch>(256),previous_watches=std::vector<Watch>(256);
    u64 current_watch_cursor{},wait_cursor{},wait_bound{};std::optional<u64>invalidation_mark;
    StreamBuffer(const Vulkan::Instance&i,Vulkan::Scheduler&s,MemoryType t,u64 size)
        :Buffer(i,0,size,t),scheduler(s){}
    bool PrepareMap(u64,u64,bool);
    std::pair<u8*,u64>Map(u64,u64,bool allow_wait=true);
    void Commit();std::optional<u64>Reserve(u64,u64,bool);
    void AdvanceAndWatch();void ReserveWatches(std::vector<Watch>&,std::size_t);
    bool WaitPendingOperations(u64,bool);
};
@STREAM@
}
namespace Vulkan {
void Scheduler::Commands::copyBuffer(VideoCore::Buffer*src,VideoCore::Buffer*dst,
                                    std::span<const vk::BufferCopy>copies)const{
    if(s.validate_copy)s.validate_copy(src,dst,copies);
    const std::vector<vk::BufferCopy>owned(copies.begin(),copies.end());
    s.commands.emplace_back([src,dst,owned]{
        for(const auto&c:owned){assert(c.srcOffset+c.size<=src->SizeBytes());
            assert(c.dstOffset+c.size<=dst->SizeBytes());
            std::memcpy(dst->storage.data()+c.dstOffset,src->storage.data()+c.srcOffset,c.size);}
    });
}
using VideoCore::MemoryType;
constexpr u64 LARGE_MIN_GRANULARITY=64_KB,BLOCK_SIZE=16_MB;
struct StagingBufferRef {
    VideoCore::Buffer*buffer{};u64 offset{},size{};u8*mapped{};MemoryType type{};
    void Flush()const noexcept{buffer->Flush(offset,size);}
};
class StagingBufferPool {
    struct Block{std::unique_ptr<VideoCore::StreamBuffer>buffer;u64 last_used_frame;};
    struct Ring{std::vector<Block>blocks;size_t current=0;};
    struct LargeBuffer{std::unique_ptr<VideoCore::Buffer>buffer;u64 tick,last_used_frame;bool held;};
    const Instance&instance;Scheduler&scheduler;
    std::array<Ring,3>rings;std::array<std::vector<LargeBuffer>,3>large_caches;u64 frame{};
    StagingBufferRef RequestFromRing(Ring&,u64,u64,MemoryType,bool);
    StagingBufferRef RequestLarge(u64,MemoryType,bool,bool);
public:
    StagingBufferPool(const Instance&i,Scheduler&s):instance(i),scheduler(s){}
    StagingBufferRef Request(u64,MemoryType,u64 alignment=0,bool deferred=false,bool unsynchronized=false);
    void FreeDeferred(const StagingBufferRef&);
};
@POOL@
@ARENA@
@SCOPE@
@COST@
@OLD@
@SNAPSHOT@
struct Runtime {
    Scheduler&scheduler;StagingBufferPool pool;
    bool donor_range_tracking=false;u64 barriers{};
    struct Access{const VideoCore::Buffer*buffer;u64 start,end;bool write;};
    std::vector<Access>accesses;
    Runtime(const Instance&i,Scheduler&s):scheduler(s),pool(i,s){
        s.validate_copy=[this](auto*src,auto*dst,std::span<const vk::BufferCopy>copies){
            for(const auto&c:copies){
                assert(!IsBufferAccessed(src,c.srcOffset,c.size));
                assert(!IsBufferAccessed(dst,c.dstOffset,c.size,true));
            }
        };
    }
    StagingBufferPool&GetStagingPool(){return pool;}
    bool IsBufferAccessed(const VideoCore::Buffer*b,u64 off,u64 size,bool reads=false){
        return std::ranges::any_of(accesses,[&](const Access&a){return a.buffer==b&&
            off<a.end&&a.start<off+size&&(a.write||reads);});
    }
    void FlushBarriers(){++barriers;accesses.clear();}
    void AccessBuffer(const VideoCore::Buffer*b,u64 off,u64 size,
                      vk::PipelineStageFlagBits2,vk::AccessFlagBits2 kind){
        accesses.push_back({b,off,off+size,kind==vk::AccessFlagBits2::eTransferWrite});
    }
    void CopyBuffer(const VideoCore::Buffer*,const VideoCore::Buffer*,std::span<const vk::BufferCopy>);
    void Draw(const VideoCore::Buffer*b,u64 off,std::vector<u8>&out){
        if(IsBufferAccessed(b,off,1))FlushBarriers();
        accesses.push_back({b,off,off+1,false});
        scheduler.commands.emplace_back([b,off,&out]{out.push_back(b->storage[off]);});
    }
};
@COPY@
}
namespace VideoCore {
struct RangeSet {
    std::vector<std::pair<VAddr,VAddr>>ranges;
    void Add(VAddr a,u64 n){ranges.emplace_back(a,a+n);}
    bool Intersects(VAddr a,u64 n)const{
        return std::ranges::any_of(ranges,[&](auto r){return a<r.second&&r.first<a+n;});
    }
    template<class F>void ForEachInRange(VAddr a,u64 n,F&&f)const{
        for(auto r:ranges){const auto lo=std::max(a,r.first),hi=std::min(a+n,r.second);if(lo<hi)f(lo,hi);}
    }
    void Subtract(VAddr a,u64 n){
        std::vector<std::pair<VAddr,VAddr>>next;
        for(auto r:ranges){if(r.second<=a||r.first>=a+n)next.push_back(r);else{
            if(r.first<a)next.emplace_back(r.first,a);
            if(r.second>a+n)next.emplace_back(a+n,r.second);}}
        ranges=std::move(next);
    }
};
struct TextureBoundary {
    u64 resolutions{},image_syncs{};
    bool ResolveImageReadbacks(VAddr,u64,bool){++resolutions;return false;}
    void NoteMetaShaderWrite(VAddr,u64){}
};
struct LiverpoolBoundary {
    u64 sends{};
    template<bool wait,class F>void SendCommand(F&&f){++sends;f();}
};
class BufferCache {
    @LIMIT_DECL@
    @UPLOAD_MEMBER@
public:
    const Vulkan::Instance&instance;Vulkan::Scheduler&scheduler;Vulkan::Runtime&runtime;
    Vulkan::StagingBufferPool&staging_pool;Core::MemoryManager*memory;
    PageManager pages;std::unique_ptr<MemoryTracker>memory_tracker;
    TextureBoundary texture_cache;LiverpoolBoundary processor;LiverpoolBoundary*liverpool=&processor;
    StreamBuffer stream_buffer;Buffer arena;
    RangeSet gpu_modified_ranges,srt_source_pages;
    u32 block_shift=12;bool coherent_arena_upload=false;
    std::vector<u64>fresh_backings;
    BufferCache(const Vulkan::Instance&i,Vulkan::Scheduler&s,Vulkan::Runtime&r,Core::MemoryManager&m)
        :instance(i),scheduler(s),runtime(r),staging_pool(r.pool),memory(&m),
         memory_tracker(std::make_unique<MemoryTracker>(pages)),
         stream_buffer(i,s,MemoryType::HostUncached,16_MB),
         arena(i,Core::MemoryManager::Base,Core::MemoryManager::Span,MemoryType::Sparse){}
    const Buffer*GetArena(u64 first,u64 last){
        assert(first<<block_shift>=arena.cpu_addr);
        assert(((last+1)<<block_shift)<=arena.cpu_addr+arena.SizeBytes());return &arena;
    }
    void EnsureResident(const Buffer*,u64,u64){}
    bool UploadFreshBacking(VAddr,u64){return false;}
    bool SynchronizeMemoryFromImage(const Buffer*,VAddr,u32){++texture_cache.image_syncs;return false;}
    StreamBuffer&GetStreamBuffer(){return stream_buffer;}
    @LIMIT_ACCESSOR@
    @COUNTER@
    void InvalidateMemory(VAddr,u64,bool assume_locks=false);
    void ReadMemory(VAddr,u64,bool is_write,bool assume_locks);
    void DownloadMemory(const Buffer*,VAddr,u64);
    void MarkGuestWriteWindow(VAddr,u64);
    bool IsRegionGpuModified(VAddr,size_t);
    bool IsRegionCpuModified(VAddr,size_t);
    bool SynchronizeMemory(const Buffer*,VAddr,u32,bool,bool);
    std::pair<const Buffer*,u64>ObtainBuffer(VAddr,u32,bool,bool is_texel=false);
};
@CACHE@
}
namespace Vulkan {
@METRICS@
namespace Shader {enum class BufferType {Guest,ReadConst};}
struct Sharp {VAddr base_address;u64 requested;u64 GetSize()const{return requested;}};
struct Desc {bool used_as_readconst=true,is_written=false,is_formatted=false;
             Shader::BufferType buffer_type=Shader::BufferType::Guest;};
u64 Bound(const Instance&instance,Core::MemoryManager*memory,Desc desc,Sharp vsharp){
    const u64 alignment=instance.StorageMinAlignment();
@BOUND@
}
struct Binding {const VideoCore::Buffer*buffer{};u64 offset{},size{};bool snapshot{};};
struct Binder {
    const Instance&instance;Scheduler&scheduler;Runtime&runtime;Core::MemoryManager*memory;
    VideoCore::BufferCache&buffer_cache;std::unique_ptr<OrderReadConstArena>order_readconst_arena;
    Binder(const Instance&i,Scheduler&s,Runtime&r,Core::MemoryManager&m,VideoCore::BufferCache&c)
        :instance(i),scheduler(s),runtime(r),memory(&m),buffer_cache(c){}
    Binding Bind(VAddr address,u64 requested,Desc desc={}){
        OrderReadConstRecordScope recording(order_readconst_arena,runtime.GetStagingPool());
        const Sharp vsharp{address,requested};
        const u64 size=Bound(instance,memory,desc,vsharp);
        if(!size)return {};
        const bool readconst=desc.buffer_type==Shader::BufferType::ReadConst;
        const u64 alignment=instance.StorageMinAlignment();
@SELECTION@
        return {buffer,offset,size,pooled.buffer!=nullptr};
    }
};
}
using namespace Vulkan;
using Core::MemoryManager;
struct Fixture {
    Instance i;Scheduler s;Runtime r{i,s};MemoryManager m;VideoCore::BufferCache cache{i,s,r,m};
    Binder binder{i,s,r,m,cache};
    static constexpr VAddr address=MemoryManager::Base+16_MB-8_KB;
    void GuestWrite(VAddr a,u64 n,u8 value){
        cache.InvalidateMemory(a,n,false);
        std::vector<u8>data(n,value);m.WriteSparseBacking(a,data.data(),n);
    }
    void BindDraw(VAddr a,u64 n,std::vector<u8>&out){const auto b=binder.Bind(a,n);assert(b.buffer);r.Draw(b.buffer,b.offset,out);}
};
void ReuseAndDirtyTest(){
    Fixture f;constexpr u64 n=4_MB,calls=5000;const auto a=Fixture::address;
    f.GuestWrite(a,n,23);std::vector<u8>out;out.reserve(calls+4);
    for(u64 k=0;k<calls;++k){f.BindDraw(a,n,out);f.s.Finish();}
    assert(f.cache.ReadConstUploadBytes()==n&&out.size()==calls);
    assert(f.m.alias_copy_bytes==n);
    assert(std::ranges::all_of(out,[](u8 x){return x==23;}));
    assert(!f.cache.memory_tracker->IsRegionCpuModified(a,n));
    assert((f.cache.pages.At(a)==std::pair{1,0}));
    assert((f.cache.pages.At(a+n-1)==std::pair{1,0}));
    const auto first=f.binder.Bind(a,n);f.r.Draw(first.buffer,first.offset,out);
    const auto previous_barriers=f.r.barriers;
    f.GuestWrite(a,1,61); // Same VA changes before the next binding in the same tick.
    const auto second=f.binder.Bind(a,n);assert(second.buffer==first.buffer);
    f.r.Draw(second.buffer,second.offset,out);f.s.Finish();
    assert(out[out.size()-2]==23&&out.back()==61&&f.r.barriers>previous_barriers);
    assert(f.cache.ReadConstUploadBytes()==n+4_KB);
    std::cout<<"ORDER_READCONST_TRACKED_REUSE calls="<<calls<<" requested="<<calls*n
             <<" uploaded="<<n<<" same-VA-write-upload="<<4_KB<<" cross-region=2 PASS\n";
}
void PreviousCopyCostTest(){
    Fixture f;constexpr u64 bytes=4_MB,calls=5000;f.GuestWrite(Fixture::address,bytes,17);
    std::unique_ptr<OrderReadConstArena>arena;
    for(u64 k=0;k<calls;++k){
        {
            OrderReadConstRecordScope recording(arena,f.r.pool);
            const auto copied=MakePooledReadConstSnapshot(f.i,&f.m,*arena,Fixture::address,bytes);
            assert(copied.size==bytes&&copied.mapped[0]==17);
        }
        f.s.Finish();
    }
    assert(f.m.alias_copy_bytes==calls*bytes);
    std::cout<<"ORDER_READCONST_PRIOR_COPY_COST calls="<<calls<<" copied="<<f.m.alias_copy_bytes
             <<" unchanged_bytes=true PASS\n";
}
void GpuReadbackTest(){
    Fixture f;const auto a=Fixture::address;std::vector<u8>out;
    f.GuestWrite(a,64_KB,19);f.BindDraw(a,64_KB,out);f.s.Finish();
    const auto [buffer,offset]=f.cache.ObtainBuffer(a,4096,true);
    f.s.commands.emplace_back([buffer,offset]{std::fill_n(buffer->Handle()->storage.data()+offset,4096,u8{77});});
    assert(f.cache.IsRegionGpuModified(a,4096));
    const auto read=f.binder.Bind(a,4096);assert(!read.snapshot&&read.buffer==buffer);
    f.r.Draw(read.buffer,read.offset,out);f.s.Finish();
    assert(out.back()==77&&f.m.Byte(a)==19);
    f.cache.ReadMemory(a,4,false,false);
    assert(f.m.Byte(a)==77&&!f.cache.IsRegionGpuModified(a,4096));
    const auto uploads=f.cache.ReadConstUploadBytes();
    f.BindDraw(a,64_KB,out);f.s.Finish();
    assert(out.back()==77&&f.cache.ReadConstUploadBytes()==uploads);
    // A CPU write to a GPU-owned page publishes all old GPU bytes first.
    const auto [again,off]=f.cache.ObtainBuffer(a,4096,true);
    f.s.commands.emplace_back([again,off]{std::fill_n(again->Handle()->storage.data()+off,4096,u8{91});});
    f.GuestWrite(a+7,1,42);
    assert(f.m.Byte(a)==91&&f.m.Byte(a+7)==42&&f.m.Byte(a+8)==91);
    f.BindDraw(a,64_KB,out);f.s.Finish();assert(out.back()==91);
    std::cout<<"ORDER_READCONST_GPU_COHERENCE GPU-write/readback/CPU-after-GPU=PASS\n";
}
void MappingAndWindowTest(){
    Fixture f;const auto a=MemoryManager::Base+8_MB;std::vector<u8>out;
    f.GuestWrite(a,1_MB,3);f.BindDraw(a,1_MB,out);f.s.Finish();
    auto bytes=f.cache.ReadConstUploadBytes();
    f.cache.MarkGuestWriteWindow(a,256_KB);
    const u8 value=9;f.m.WriteSparseBacking(a,&value,1);
    f.BindDraw(a,1_MB,out);f.s.Finish();
    assert(out.back()==9&&f.cache.ReadConstUploadBytes()==bytes+256_KB);
    // Unmap invalidates before the physical backing is replaced at the same VA.
    f.cache.InvalidateMemory(MemoryManager::Base,MemoryManager::Span,false);
    auto&v=f.m.vma_map.begin()->second;v.type=Core::VMAType::Reserved;
    assert(!f.binder.Bind(a,1_MB).buffer);
    v.phys_areas={{0,{32_MB,MemoryManager::Span}}};v.type=Core::VMAType::Direct;
    f.m.WriteSparseBacking(a,&value,1);f.BindDraw(a,1_MB,out);f.s.Finish();assert(out.back()==9);
    assert(f.cache.memory_tracker->IsRegionCpuModified(a+2_MB,4096));
    // Strict clamp for Guest resources used by ReadConst, including sub-1GiB requests.
    const auto end=MemoryManager::Base+MemoryManager::Span;
    assert(Bound(f.i,&f.m,{},Sharp{end-16_KB,1_MB})==16_KB);
    assert(!f.binder.Bind(end+4096,64_KB).buffer);
    assert(!f.binder.Bind(UINT64_MAX-15,64_KB).buffer);
    std::cout<<"ORDER_READCONST_INVALIDATION write-window/unmap-remap/VMA-bound=PASS\n";
}
void ScopeAndLifetimeTest(){
    Fixture f;const auto a=Fixture::address;std::vector<u8>out;
    f.GuestWrite(a,4_MB,13);
    const auto cached=f.binder.Bind(a,4_MB);assert(!cached.snapshot);
    // Copy to the persistent arena is already recorded. A later binding may
    // finish its tick and recycle upload staging before the draw is recorded.
    f.s.Finish();
    for(int k=0;k<6;++k){const auto pressure=f.r.pool.Request(8_MB,VideoCore::MemoryType::HostUncached);
        std::memset(pressure.mapped,99,pressure.size);f.s.Finish();}
    f.r.Draw(cached.buffer,cached.offset,out);f.s.Finish();assert(out.back()==13);
    const auto small=f.binder.Bind(a,16_KB);assert(small.snapshot);
    f.GuestWrite(a,1,25);
    const auto changed=f.binder.Bind(a,16_KB);assert(changed.snapshot);
    f.r.Draw(small.buffer,small.offset,out);f.r.Draw(changed.buffer,changed.offset,out);f.s.Finish();
    assert(out[out.size()-2]==13&&out.back()==25);
    const auto odd=f.binder.Bind(a+2,64_KB);assert(odd.snapshot&&odd.offset%256==0);
    for(const std::string serial:{"CUSA08809","CUSA08034","OTHER"}){
        Common::ElfInfo::Instance().serial=serial;
        const auto before=f.s.pending.size();
        const auto legacy=f.binder.Bind(a,64_KB);assert(!legacy.snapshot&&f.s.pending.size()==before+1);
    }
    Common::ElfInfo::Instance().serial="CUSA00785";
    std::cout<<"ORDER_READCONST_LIFETIME persistent/flush/recycled-upload/small-immutable/other-titles=PASS\n";
}
void MetricsTest(){
    OrderReadConstReuseWindow window;stats_logs.clear();
    window.Add(10'000'000,100,4_MB,false,4_MB);
    window.Add(11'000'000,20,4_MB,false,0);assert(stats_logs.size()==1);
    window.Add(12'000'000,30,512,true,0);
    assert(stats_logs.size()==2&&stats_logs[1][2]==2&&stats_logs[1][3]==4_MB+512);
    assert(stats_logs[1][4]==1&&stats_logs[1][5]==512&&stats_logs[1][6]==1&&stats_logs[1][7]==0);
    std::cout<<"ORDER_READCONST_REUSE_METRICS actual-upload/2s=PASS\n";
}
int main(int argc,char**argv){
#ifndef __ANDROID__
    Fixture f;const auto before=f.s.pending.size();
    const auto legacy=f.binder.Bind(Fixture::address,64_KB);
    assert(legacy.buffer&&!legacy.snapshot&&f.s.pending.size()==before+1);
    assert(f.cache.ReadConstUploadBytes()==0);
    std::cout<<"ORDER_READCONST_NON_ANDROID_LEGACY=PASS\n";return 0;
#endif
    const std::string_view only=argc>1?argv[1]:"";
    if(only.empty()||only=="reuse")ReuseAndDirtyTest();
    if(only.empty())PreviousCopyCostTest();
    if(only.empty()||only=="gpu")GpuReadbackTest();
    if(only.empty()||only=="mapping")MappingAndWindowTest();
    if(only.empty()||only=="lifetime")ScopeAndLifetimeTest();
    if(only.empty())MetricsTest();
}
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    src = args.source.resolve() / "src"
    read = lambda name: (src / name).read_text()
    raster = read("video_core/renderer_vulkan/vk_rasterizer.cpp")
    cache = read("video_core/buffer_cache/buffer_cache.cpp")
    cache_h = read("video_core/buffer_cache/buffer_cache.h")
    memory = read("core/memory.cpp")
    memory_h = read("core/memory.h")
    stream = read("video_core/buffer_cache/buffer.cpp")
    pool = read("video_core/renderer_vulkan/vk_staging_buffer_pool.cpp")
    bind = block(raster, "void Rasterizer::BindBuffers(")
    selection = bind[bind.index("                std::shared_ptr<VideoCore::Buffer> isolated;"):
                     bind.index("                const u64 offset_aligned")]
    bound = bind[bind.index("            const bool readconst ="):
                 bind.index("                if (size != vsharp.GetSize())")]
    bound = bound.replace("                buffer_infos.emplace_back(VK_NULL_HANDLE, 0, VK_WHOLE_SIZE);",
                          "                return 0;")
    bound += "                return size;\n            }\n"
    assert "readconst || shadow || order_readconst" in bound
    assert "if (size <= VideoCore::BufferCache::ReadConstStreamThreshold() ||" in selection
    assert "!buffer_cache.IsRegionGpuModified" in selection
    assert "cpu_upload_bytes.fetch_add(total_size_bytes, std::memory_order_relaxed);" in block(
        cache, "bool BufferCache::SynchronizeMemory(")
    assert "readconst_reuse.snapshot = pooled.buffer != nullptr;" in bind
    public_start = cache_h.index("\npublic:\n", cache_h.index("class BufferCache {"))
    private_start = cache_h.index("\nprivate:\n", public_start)
    threshold_declaration = "static constexpr u64 STREAM_THRESHOLD = 16_KB;"
    upload_member = "std::atomic<u64> cpu_upload_bytes{};"
    threshold_assert = "static_assert(VideoCore::BufferCache::ReadConstStreamThreshold() == 16_KB);"
    assert cache_h.index(threshold_declaration) < public_start
    assert public_start < cache_h.index("ReadConstStreamThreshold()") < private_start
    assert public_start < cache_h.index("ReadConstUploadBytes()") < private_start
    assert cache_h.index(upload_member) > private_start
    assert "#include <atomic>" in cache_h and threshold_assert in raster
    assert "cpu_upload_bytes.load(std::memory_order_relaxed)" in cache_h
    values = {
        "POLICY": block(read("common/bachata_compat_profile.h"), "inline bool Order1886()"),
        "PHYSICAL": block(memory_h, "bool HasPhysicalBacking("),
        "MEMORY": "\n".join(block(memory, marker) for marker in (
            "void MemoryManager::CopySparseMemory(", "void MemoryManager::WriteSparseBacking(",
            "u64 MemoryManager::ClampGpuRangeSize(", "u64 MemoryManager::ClampRangeSize(")),
        "WAIT": block(read("video_core/renderer_vulkan/vk_scheduler.cpp"), "void Scheduler::Wait(u64 tick)"),
        "STREAM": "\n".join(block(stream, marker) for marker in (
            "bool StreamBuffer::PrepareMap(", "std::pair<u8*, u64> StreamBuffer::Map(",
            "void StreamBuffer::Commit(", "std::optional<u64> StreamBuffer::Reserve(",
            "void StreamBuffer::AdvanceAndWatch(", "void StreamBuffer::ReserveWatches(",
            "bool StreamBuffer::WaitPendingOperations(")),
        "POOL": "\n".join(block(pool, marker) for marker in (
            "u64 RoundAllocationSize(", "StagingBufferRef StagingBufferPool::Request(",
            "StagingBufferRef StagingBufferPool::RequestFromRing(",
            "StagingBufferRef StagingBufferPool::RequestLarge(", "void StagingBufferPool::FreeDeferred(")),
        "ARENA": block(raster, "class OrderReadConstArena") + ";",
        "SCOPE": block(raster, "struct OrderReadConstRecordScope") + ";",
        "COST": block(raster, "struct OrderReadConstCostWindow") + ";\n" +
                block(raster, "struct OrderReadConstCostSample") + ";",
        "OLD": block(raster, "std::shared_ptr<VideoCore::Buffer> MakeReadConstSnapshot("),
        "SNAPSHOT": block(raster, "StagingBufferRef MakePooledReadConstSnapshot("),
        "COPY": block(read("video_core/renderer_vulkan/vk_runtime.cpp"), "void Runtime::CopyBuffer("),
        "LIMIT_DECL": threshold_declaration,
        "UPLOAD_MEMBER": upload_member,
        "LIMIT_ACCESSOR": block(cache_h, "[[nodiscard]] static constexpr u64 ReadConstStreamThreshold()"),
        "COUNTER": block(cache_h, "[[nodiscard]] u64 ReadConstUploadBytes()"),
        "CACHE": "\n".join(block(cache, marker) for marker in (
            "void BufferCache::InvalidateMemory(", "void BufferCache::ReadMemory(",
            "void BufferCache::DownloadMemory(", "void BufferCache::MarkGuestWriteWindow(",
            "bool BufferCache::IsRegionCpuModified(", "bool BufferCache::IsRegionGpuModified(",
            "bool BufferCache::SynchronizeMemory(", "std::pair<const Buffer*, u64> BufferCache::ObtainBuffer(")),
        "METRICS": threshold_assert + "\n" + block(raster, "struct OrderReadConstReuseWindow") + ";\n" +
                   block(raster, "struct OrderReadConstReuseSample") + ";",
        "BOUND": bound, "SELECTION": selection,
    }
    program = PROGRAM
    if (src / "video_core/renderer_vulkan/order_render_pass_reasons.h").exists():
        program = '#include "video_core/renderer_vulkan/order_render_pass_reasons.h"\n' + program
    for name, value in values.items():
        program = program.replace("@" + name + "@", value)
    # Counting at the copy boundary leaves the real sparse-alias implementation intact.
    program = program.replace(
        "void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {",
        "void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {\n"
        "    alias_copy_bytes += size;", 1)
    with tempfile.TemporaryDirectory(prefix="order-readconst-reuse-") as temp:
        temp = Path(temp)
        def write(name: str, content: str) -> None:
            path = temp / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        write("core/emulator_settings.h", "#pragma once\n"
              "enum GpuReadbacksMode:int{Disabled,Relaxed,Precise};\n"
              "inline struct {unsigned GetReadbacksMode()const{return Precise;}} EmulatorSettings;\n")
        write("video_core/page_manager.h", PAGE_MANAGER)
        compiler = shlex.split(os.environ.get("CXX", "c++")) + [
            "-std=c++23", "-O2", "-pthread", "-Wall", "-Wextra", "-Werror",
            "-Wno-unused-parameter", "-Wno-sign-compare", "-I", str(temp), "-I", str(src)]

        def run(label: str, text: str, *, android: bool = True,
                negative: bool = False, only: str = "") -> None:
            write(label + ".cpp", text)
            command = compiler + (["-D__ANDROID__"] if android else []) + [
                str(temp / (label + ".cpp")), "-o", str(temp / label)]
            subprocess.run(command, check=True)
            result = subprocess.run([str(temp / label)] + ([only] if only else []),
                                    capture_output=True, text=True)
            if negative:
                assert result.returncode != 0, "Negative control accepted: " + label
                print("ORDER_READCONST_REUSE_NEGATIVE_PASS", label, flush=True)
            else:
                if result.returncode:
                    raise AssertionError(label + "\n" + result.stdout + result.stderr)
                print(result.stdout, end="", flush=True)

        run("positive", program)
        run("non_android", program, android=False)
        private_name = program.replace("BufferCache::ReadConstStreamThreshold()", "BufferCache::STREAM_THRESHOLD")
        assert private_name != program
        write("private_threshold.cpp", private_name)
        result = subprocess.run(compiler + ["-D__ANDROID__", str(temp / "private_threshold.cpp"),
                                            "-o", str(temp / "private_threshold")],
                                capture_output=True, text=True)
        assert result.returncode != 0 and "private" in result.stderr
        print("ORDER_READCONST_REUSE_NEGATIVE_PASS private_threshold_access", flush=True)
        controls = {
            "copy_every_binding": ("if (size <= VideoCore::BufferCache::ReadConstStreamThreshold() ||\n"
                                   "                            (vsharp.base_address & 3) != 0)",
                                   "if (true)", "reuse"),
            "skip_cpu_invalidation": ("    memory_tracker->InvalidateRegion(device_addr, size,",
                                      "    if (false) memory_tracker->InvalidateRegion(device_addr, size,", "reuse"),
            "skip_dirty_upload": ("        copies.emplace_back(total_size_bytes, addr, size);",
                                  "        if (false) copies.emplace_back(total_size_bytes, addr, size);", "reuse"),
            "unbounded_guest_constant": ("readconst || shadow || order_readconst",
                                         "readconst || shadow || (order_readconst && false)", "mapping"),
            "gpu_stale_snapshot": (
                "if (desc.used_as_readconst && !desc.is_written && size!=0 &&\n"
                "                    !buffer_cache.IsRegionGpuModified(vsharp.base_address,size))",
                "if (desc.used_as_readconst && !desc.is_written && size!=0 && true)", "gpu"),
            "lost_readback_publication": ("        memory->WriteSparseBacking(reinterpret_cast<VAddr>(dst_addr),",
                                          "        if (false) memory->WriteSparseBacking(reinterpret_cast<VAddr>(dst_addr),", "gpu"),
            "lost_read_write_barrier": ("IsBufferAccessed(dst,copy.dstOffset,copy.size,true)",
                                        "IsBufferAccessed(dst,copy.dstOffset,copy.size,false)", "reuse"),
            "read_protected_guest_instead_of_alias": (
                "impl.BackingBase()+part->second.base+lo-part->first,hi-lo);\n                cursor=hi;",
                "reinterpret_cast<const u8*>(address)+lo-begin,hi-lo);\n                cursor=hi;", "reuse"),
        }
        for label, (before, after, only) in controls.items():
            assert program.count(before) == 1, (label, program.count(before))
            run(label, program.replace(before, after, 1), negative=True, only=only)


if __name__ == "__main__":
    main()
