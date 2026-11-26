#!/usr/bin/env python3
"""Test effective CPU snapshot bytes, allocation calls and recorder/GPU lifetime.

The snapshot helpers, binding selection, held-block arena, pool allocation,
Scheduler::Wait and StreamBuffer watches are extracted from generated source. Vulkan allocation
and the FEX memory alias are boundary fixtures; no desktop driver time is
presented as Android performance.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


def block(text: str, marker: str) -> str:
    start = text.index(marker)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if depth == 0:
            return text[start:end + 1]
    raise AssertionError("Unclosed source block: " + marker)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--negative-control", choices=("cleanup_allocation",),
                        help="Run only the specified regression control")
    args = parser.parse_args()
    src = args.source.resolve() / "src"
    rasterizer = (src / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    buffer = (src / "video_core/buffer_cache/buffer.cpp").read_text()
    buffer_h = (src / "video_core/buffer_cache/buffer.h").read_text()
    pool = (src / "video_core/renderer_vulkan/vk_staging_buffer_pool.cpp").read_text()
    scheduler = (src / "video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
    rasterizer_h = (src / "video_core/renderer_vulkan/vk_rasterizer.h").read_text()
    profile = (src / "common/bachata_compat_profile.h").read_text()
    assert '#include "video_core/renderer_vulkan/vk_staging_buffer_pool.h"' in rasterizer
    assert '#include "common/bachata_compat_profile.h"' in rasterizer
    assert "eShaderDeviceAddress" in buffer_h.split("constexpr vk::BufferUsageFlags AllFlags")[0]
    assert "ReadFlags |" in buffer_h
    constructor = buffer[buffer.index("Buffer::Buffer("):buffer.index("void Buffer::Flush(")]
    assert ".usage = AllFlags" in constructor
    assert "VMA_ALLOCATION_CREATE_DEDICATED_MEMORY_BIT" in block(buffer, "void UniqueBuffer::Create(")

    old = block(rasterizer, "std::shared_ptr<VideoCore::Buffer> MakeReadConstSnapshot(")
    new = block(rasterizer, "StagingBufferRef MakePooledReadConstSnapshot(")
    assert "make_shared<VideoCore::Buffer>" in old
    assert "arena.Request(" in new and "make_shared" not in new and "DeferOperation" not in new
    assert "unsynchronized" not in new
    bind = block(rasterizer, "void Rasterizer::BindBuffers(")
    start = bind.index("                std::shared_ptr<VideoCore::Buffer> isolated;")
    end = bind.index("                const u64 offset_aligned", start)
    selection = bind[start:end]
    assert "BachataCompat::Order1886()" in selection
    assert "!buffer_cache.IsRegionGpuModified" in selection
    assert "buffer = pooled.buffer;" in selection and "offset = pooled.offset;" in selection
    assert "scheduler.DeferOperation" in selection
    cache_limit_interface = ""
    if "VideoCore::BufferCache::ReadConstStreamThreshold()" in selection:
        cache_h = (src / "video_core/buffer_cache/buffer_cache.h").read_text()
        public_start = cache_h.index("\npublic:\n", cache_h.index("class BufferCache {"))
        private_start = cache_h.index("\nprivate:\n", public_start)
        declaration = "static constexpr u64 STREAM_THRESHOLD = 16_KB;"
        assert cache_h.index(declaration) < public_start
        assert public_start < cache_h.index("ReadConstStreamThreshold()") < private_start
        accessor = block(cache_h, "[[nodiscard]] static constexpr u64 ReadConstStreamThreshold()")
        # Preserve the real access boundary; the binding must use the public
        # accessor instead of making the private constant visible in a fixture.
        cache_limit_interface = "class BufferCache {\n    " + declaration + "\npublic:\n    " + accessor + "\n};"
    assert "ClampGpuRangeSize" in bind and "const u64 bounded = std::min(mapped, limit);" in bind
    costs = block(rasterizer, "struct OrderReadConstCostWindow") + ";\n"
    costs += block(rasterizer, "struct OrderReadConstCostSample") + ";\n"
    arena = block(rasterizer, "class OrderReadConstArena") + ";\n"
    scope = block(rasterizer, "struct OrderReadConstRecordScope") + ";\n"
    cleanup = block(arena, "void RetireRecorded()")
    destructor = block(arena, "~OrderReadConstArena()")
    assert "push_back" not in cleanup and "pool.Request" not in cleanup
    assert "push_back" not in destructor and "pool.Request" not in destructor
    assert "std::unique_ptr<OrderReadConstArena> order_readconst_arena;" in rasterizer_h
    assert "class OrderReadConstArena;" in rasterizer_h
    assert rasterizer.index("class OrderReadConstArena") < rasterizer.index("Rasterizer::~Rasterizer()")
    presenter_h = (src / "video_core/renderer_vulkan/vk_presenter.h").read_text()
    assert presenter_h.index("Runtime runtime;") < presenter_h.index("std::unique_ptr<Rasterizer> rasterizer;")

    def validate_scopes(source: str) -> None:
        for name in ("Draw", "DrawIndirect", "DispatchDirect", "DispatchIndirect"):
            method = block(source, "void Rasterizer::" + name + "(")
            marker = "    OrderReadConstRecordScope readconst_recording{\n"
            assert method.count(marker) == 1, name
            pos = method.index(marker)
            prefix = method[method.index("{"):pos]
            assert prefix.count("{") - prefix.count("}") == 1, name
            assert pos < method.index("    if (!BindResources(pipeline))"), name
            assert "order_readconst_arena, runtime.GetStagingPool()};" in method
            assert "ResetBindings(" in method[pos:]

    validate_scopes(rasterizer)
    pool_methods = "\n".join(block(pool, marker) for marker in (
        "u64 RoundAllocationSize(",
        "StagingBufferRef StagingBufferPool::Request(",
        "StagingBufferRef StagingBufferPool::RequestFromRing(",
        "StagingBufferRef StagingBufferPool::RequestLarge(",
        "void StagingBufferPool::FreeDeferred(",
    ))
    stream_methods = "\n".join(block(buffer, marker) for marker in (
        "bool StreamBuffer::PrepareMap(", "std::pair<u8*, u64> StreamBuffer::Map(",
        "void StreamBuffer::Commit(", "std::optional<u64> StreamBuffer::Reserve(",
        "void StreamBuffer::AdvanceAndWatch(", "void StreamBuffer::ReserveWatches(",
        "bool StreamBuffer::WaitPendingOperations(",
    ))
    template = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <iostream>
#include <memory>
#include <new>
#include <numeric>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>
using u8=uint8_t; using u32=uint32_t; using u64=uint64_t; using VAddr=u64;
bool forbid_allocations{};
[[gnu::noinline]] void* operator new(std::size_t size) {
    if(forbid_allocations)throw std::bad_alloc{};
    if(void* allocation=std::malloc(size?size:1))return allocation;
    throw std::bad_alloc{};
}
[[gnu::noinline]] void operator delete(void* allocation)noexcept {std::free(allocation);}
[[gnu::noinline]] void operator delete(void* allocation,std::size_t)noexcept {std::free(allocation);}
constexpr u64 operator""_MB(unsigned long long n){return n*1024*1024;}
constexpr u64 operator""_KB(unsigned long long n){return n*1024;}
#define ASSERT_MSG(x,...) assert(x)
#define ASSERT(x) assert(x)
std::vector<std::vector<u64>> cost_logs;
constexpr int Render_Vulkan=0;
template<class... T> void CaptureCost(int,std::string_view,T... values) {
    cost_logs.push_back({static_cast<u64>(values)...});
}
#define LOG_INFO CaptureCost
namespace Common {
template<class A,class B> constexpr A AlignUp(A n,B a){return (n+A(a)-1)/A(a)*A(a);}
struct ElfInfo {
    std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo i;return i;}
    std::string_view GameSerial()const{return serial;}
};
}
namespace BachataCompat {
@POLICY@
}
namespace Vulkan {
struct Instance {
    u64 atom{64},alignment{256}; bool coherent{false};
    u64 NonCoherentAtomSize()const{return atom;}
    u64 StorageMinAlignment()const{return alignment;}
};
struct SubmitInfo {};
struct Scheduler {
    u64 current{1}, submitted{}, completed{}, waits{}, flushes{};
    std::vector<std::function<void()>> pending;
    struct SemaphoreFixture {
        Scheduler& scheduler;
        u64 CurrentTick()const{return scheduler.current;}
        void Wait(u64 tick) {
            assert(tick<=scheduler.submitted);
            scheduler.completed=std::max(scheduler.completed,tick);
            ++scheduler.waits;
        }
    } work_semaphore{*this};
    u64 CurrentTick()const{return current;}
    bool IsFree(u64 tick)const {assert(completed<=submitted);return completed>=tick;}
    void DrainDrawPipe(){}
    void Flush(SubmitInfo&){submitted=current++;++flushes;}
    void WaitSubmitted(u64 tick){assert(tick<=submitted);}
    void Wait(u64 tick);
    template<class F>void DeferOperation(F&& f){pending.emplace_back(std::forward<F>(f));}
};
@WAIT@
}
namespace Core {
enum class MemoryProt:u32{CpuRead=1,CpuWrite=2};
struct MemoryManager {
    std::vector<u8> guest=std::vector<u8>(9_MB+4096);
    bool readable{true}, unmapped{}, forbid_copy{};
    u64 copies{},copied_bytes{};
    VAddr Base()const{return reinterpret_cast<VAddr>(guest.data());}
    int QueryProtection(VAddr address,void** begin,void** end,u32* prot) {
        *begin=guest.data(); *end=guest.data()+guest.size();
        *prot=readable?u32(MemoryProt::CpuRead):0;
        return unmapped || address<Base() || address>=Base()+guest.size() ? -1:0;
    }
    void CopySparseMemory(VAddr address,u8* output,u64 size) {
        assert(!forbid_copy && address>=Base() && size<=Base()+guest.size()-address);
        ++copies;copied_bytes+=size;
        std::memcpy(output,reinterpret_cast<const void*>(address),size);
    }
};
}
namespace VideoCore {
@CACHE_LIMIT@
enum class MemoryType:u8{DeviceLocal,HostUncached,HostCached,Stream,Sparse};
struct Buffer {
    static inline u64 allocations{},destructions{},next_id{};
    static inline bool throw_next_allocation{};
    const u64 id=++next_id;
    u64 cpu_addr{},size_bytes{};
    MemoryType mem_type{};
    bool is_coherent{};
    std::vector<u8> storage;
    std::span<u8> mapped_data;
    std::vector<std::pair<u64,u64>> flushes;
    Buffer(const Vulkan::Instance& instance,VAddr address,u64 size,MemoryType type,
           std::string_view={})
        :cpu_addr(address),size_bytes(size),mem_type(type),is_coherent(instance.coherent),
         storage(size,0xa5),mapped_data(storage) {
        // Allocation is the fixture boundary. The caller is the unmodified
        // RequestLarge method and its real std::make_unique<Buffer> expression.
        if(std::exchange(throw_next_allocation,false))throw std::bad_alloc{};
        ++allocations;
    }
    ~Buffer(){++destructions;}
    u64 SizeBytes()const{return size_bytes;}
    void Flush(u64 offset,u64 size){assert(offset+size<=size_bytes);flushes.emplace_back(offset,size);}
    void Invalidate(u64,u64){}
};
constexpr u64 WATCHES_RESERVE_CHUNK=256;
struct StreamBuffer:Buffer {
    Vulkan::Scheduler& scheduler;
    u64 non_coherent_atom_size{},offset{},mapped_size{},last_tick{};
    struct Watch{u64 upper_bound{},tick{};};
    std::vector<Watch> current_watches=std::vector<Watch>(256),previous_watches=std::vector<Watch>(256);
    u64 current_watch_cursor{},wait_cursor{},wait_bound{};
    std::optional<u64> invalidation_mark;
    StreamBuffer(const Vulkan::Instance&i,Vulkan::Scheduler&s,MemoryType t,u64 bytes)
        :Buffer(i,0,bytes,t),scheduler(s),non_coherent_atom_size(i.NonCoherentAtomSize()){}
    bool PrepareMap(u64,u64,bool);
    std::pair<u8*,u64>Map(u64,u64,bool allow_wait=true);
    void Commit();
    std::optional<u64>Reserve(u64,u64,bool);
    void AdvanceAndWatch();
    void ReserveWatches(std::vector<Watch>&,std::size_t);
    bool WaitPendingOperations(u64,bool);
};
@STREAM@
}
namespace Vulkan {
using VideoCore::MemoryType;
constexpr u64 LARGE_MIN_GRANULARITY=64_KB, BLOCK_SIZE=16_MB;
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
@NEW@
struct Cache {
    bool gpu{};u64 obtains{};
    VideoCore::Buffer fallback;
    VideoCore::StreamBuffer stream;
    Cache(const Instance&i,Scheduler&s):fallback(i,0,4096,MemoryType::DeviceLocal),
        stream(i,s,MemoryType::HostUncached,16_MB){}
    bool IsRegionGpuModified(VAddr,u64){return gpu;}
    auto ObtainBuffer(VAddr,u64,bool,bool){++obtains;return std::pair{&fallback,u64{0}};}
    VideoCore::StreamBuffer&GetStreamBuffer(){return stream;}
};
struct Runtime {StagingBufferPool&pool;StagingBufferPool&GetStagingPool(){return pool;}};
struct Desc {bool used_as_readconst{true},is_written{},is_formatted{};};
struct Binding {const VideoCore::Buffer* buffer;u64 offset;};
Binding Select(const Instance&instance,Core::MemoryManager*memory,Runtime&runtime,
               Scheduler&scheduler,Cache&buffer_cache,Desc desc,VAddr address,u64 size,
               std::unique_ptr<OrderReadConstArena>& order_readconst_arena) {
    OrderReadConstRecordScope readconst_recording{order_readconst_arena, runtime.GetStagingPool()};
    const struct {VAddr base_address;} vsharp{address};
    const bool readconst=true;
    const u64 alignment=instance.StorageMinAlignment();
@SELECTION@
    return {buffer,offset};
}
}
using namespace Vulkan;
void Fill(Core::MemoryManager&memory,u8 seed) {
    for(u64 i=0;i<memory.guest.size();++i)memory.guest[i]=u8(seed+i*17u);
}
void CheckSnapshot(const StagingBufferRef&s,const Core::MemoryManager&memory,VAddr addr,u64 bytes,
                   const Instance&i) {
    assert(s.buffer&&s.mapped&&s.size>=bytes);
    assert(s.offset%i.StorageMinAlignment()==0&&s.offset%std::max<u64>(1,i.atom)==0);
    assert(std::memcmp(s.mapped,reinterpret_cast<const void*>(addr),bytes)==0);
    assert(std::all_of(s.mapped+bytes,s.mapped+s.size,[](u8 x){return x==0;}));
    assert(s.buffer->mem_type==VideoCore::MemoryType::HostUncached);
    assert(!s.buffer->flushes.empty());
    assert((s.buffer->flushes.back()==std::pair{s.offset,s.size}));
    assert(addr>=memory.Base());
}
void ByteAndAllocationTest() {
    Instance instance;Scheduler scheduler;StagingBufferPool pool(instance,scheduler);
    OrderReadConstArena arena(pool);arena.BeginRecording();
    Core::MemoryManager memory;Fill(memory,11);
    constexpr u64 count=5000,bytes=512;
    const u64 old_before=VideoCore::Buffer::allocations;
    std::vector<std::shared_ptr<VideoCore::Buffer>> held;
    for(u64 n=0;n<count;++n) {
        auto old=MakeReadConstSnapshot(instance,&memory,memory.Base(),bytes);
        assert(old&&std::memcmp(old->mapped_data.data(),memory.guest.data(),bytes)==0);
        held.push_back(std::move(old));
    }
    const u64 old_calls=VideoCore::Buffer::allocations-old_before;
    const u64 pool_before=VideoCore::Buffer::allocations;
    for(u64 n=0;n<count;++n) {
        auto out=MakePooledReadConstSnapshot(instance,&memory,arena,memory.Base(),bytes);
        CheckSnapshot(out,memory,memory.Base(),bytes,instance);
    }
    const u64 pool_calls=VideoCore::Buffer::allocations-pool_before;
    assert(old_calls==count&&pool_calls==1&&scheduler.waits==0);
    std::cout<<"ORDER_READCONST_ALLOCATION_CALLS old="<<old_calls<<" pooled="<<pool_calls
             <<" copies="<<count<<" bytes_per_copy="<<bytes<<" pending_tick="<<scheduler.current<<"\n";
    held.clear();
    arena.EndRecording();

    u64 cases=0;
    for(u64 atom:{1u,64u,256u})for(u64 alignment:{16u,256u,4096u})for(bool coherent:{false,true}) {
        Instance i{atom,alignment,coherent};Scheduler s;StagingBufferPool p(i,s);
        OrderReadConstArena a(p);a.BeginRecording();
        // An unrelated reservation ensures offsets do not accidentally start aligned.
        (void)a.Request(13,1);
        for(u64 n:{1u,3u,4u,63u,64u,255u,256u,257u,4095u,4096u,65535u,8388608u}) {
            auto previous=MakeReadConstSnapshot(i,&memory,memory.Base(),n);
            auto next=MakePooledReadConstSnapshot(i,&memory,a,memory.Base(),n);
            assert(previous);CheckSnapshot(next,memory,memory.Base(),n,i);
            assert(previous->SizeBytes()==next.size);
            assert(std::memcmp(previous->mapped_data.data(),next.mapped,next.size)==0);
            ++cases;
        }
        a.EndRecording();
    }
    std::cout<<"ORDER_READCONST_BYTE_EQUIVALENCE cases="<<cases<<" limits=8MiB alignment/padding/flush=PASS\n";
}
void LifetimeTest() {
    Instance i;Scheduler s;StagingBufferPool p(i,s);Core::MemoryManager memory;
    OrderReadConstArena arena(p);arena.BeginRecording();
    Fill(memory,23);
    const auto a=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    const auto b=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    assert(a.buffer==b.buffer&&a.offset!=b.offset);
    arena.EndRecording(); // The tick1 consumer has now been recorded.
    ++s.current; // Tick1 is queued in the recorder, not submitted or complete.
    arena.BeginRecording();
    Fill(memory,37);
    const auto c=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    assert(c.buffer!=a.buffer);
    assert(a.mapped[0]==23&&b.mapped[0]==23);
    s.submitted=1; // Driver submitted tick1, but the GPU still has not completed it.
    const auto d=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    assert(d.buffer==c.buffer&&d.offset!=c.offset);
    arena.EndRecording();arena.BeginRecording();
    Fill(memory,61);
    const auto e=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    assert(e.buffer!=a.buffer&&e.buffer!=c.buffer);
    assert(a.mapped[0]==23&&b.mapped[0]==23&&c.mapped[0]==37&&d.mapped[0]==37);
    arena.EndRecording();arena.BeginRecording();
    s.completed=1; // Only now may tick1 storage be reused, even while tick2 is busy.
    const u64 before=VideoCore::Buffer::allocations;
    (void)MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    const auto g=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),8_MB);
    assert(g.buffer==a.buffer&&VideoCore::Buffer::allocations==before);
    assert(c.mapped[0]==37&&d.mapped[0]==37&&s.waits==0);
    arena.EndRecording();
    std::cout<<"ORDER_READCONST_LIFETIME queued/submitted/busy/completed=PASS\n";
}
void PreconsumeLifetimeTest() {
    u64 cases=0;
    for(u64 atom:{64u,256u})for(u64 bytes:{512u,4096u,8u*1024u*1024u})
    for(bool internal_submit:{false,true}) {
        Instance i{atom,256,false};Scheduler s;StagingBufferPool p(i,s);
        OrderReadConstArena arena(p);arena.BeginRecording();
        Core::MemoryManager memory;Fill(memory,23);
        VideoCore::StreamBuffer other(i,s,MemoryType::HostUncached,64_KB);
        const auto [first,first_offset]=other.Map(64_KB,256);
        assert(first&&first_offset==0);other.Commit();
        const auto a=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),bytes);
        const auto padding=arena.Request(16_MB-a.size,256);
        assert(a.buffer==padding.buffer);
        if(internal_submit) {
            // Real StreamBuffer::Map -> WaitPendingOperations -> Scheduler::Wait.
            // The submit/completion boundary finishes N before the draw in N+1.
            const auto [next,next_offset]=other.Map(256,256);
            assert(next&&next_offset==0);other.Commit();
            assert(s.flushes==1&&s.current==2&&s.completed==1);
        }
        Fill(memory,61);
        const auto b=MakePooledReadConstSnapshot(i,&memory,arena,memory.Base(),bytes);
        assert(b.buffer!=a.buffer&&a.mapped[0]==23&&b.mapped[0]==61);
        if(internal_submit) {
            // A second internal wait after the rollover must not release the
            // full block while its consumer is still being prepared.
            const auto [next,next_offset]=other.Map(64_KB,256);
            assert(next&&next_offset==0);other.Commit();
            assert(s.flushes==2&&s.current==3&&s.completed==2);
        }
        // A different shared-pool caller must also honor the held block.
        const auto outsider=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(outsider.buffer!=a.buffer&&outsider.buffer!=b.buffer);
        p.FreeDeferred(outsider);
        const u64 consumer=s.current;
        arena.EndRecording(); // Consumer recorded only here, possibly in N+1.
        const auto busy=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(busy.buffer!=a.buffer&&a.mapped[0]==23);
        p.FreeDeferred(busy);
        s.submitted=consumer; // Submission alone must not free the consumer.
        const auto submitted=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(submitted.buffer!=a.buffer&&a.mapped[0]==23);
        p.FreeDeferred(submitted);
        s.completed=consumer;
        const auto retired=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(retired.buffer==a.buffer);
        p.FreeDeferred(retired);
        ++cases;
    }
    std::cout<<"ORDER_READCONST_PRECONSUME_LIFETIME cases="<<cases
             <<" internal-Flush/pending-consumer/final-tick=PASS\n";
}
void RecordingScopeTest() {
    Common::ElfInfo::Instance().serial="CUSA00785";
    if(!BachataCompat::Order1886())return;
    for(bool early:{false,true}) {
    Instance i;Scheduler s;StagingBufferPool p(i,s);Core::MemoryManager memory;
    std::unique_ptr<OrderReadConstArena> arena;
    StagingBufferRef first{},second{};
    auto record=[&](bool early) {
        OrderReadConstRecordScope outer(arena,p);
        first=MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),8_MB);
        (void)MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),8_MB);
        s.submitted=1;s.completed=1;s.current=2;
        {
            OrderReadConstRecordScope nested(arena,p);
            second=MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),8_MB);
            assert(second.buffer!=first.buffer);
        }
        s.Wait(s.current); // Inner scope exit is not the outer consumer.
        assert(s.current==3&&s.completed==2);
        const auto pressure=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(pressure.buffer!=first.buffer);p.FreeDeferred(pressure);
        if(early)return; // Same guard releases pending blocks on early exit.
    };
        record(early);
        // Final consumer tick3 was recorded but is still not complete.
        const auto busy=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(busy.buffer!=first.buffer);p.FreeDeferred(busy);
        s.submitted=3;s.completed=3;
        const auto free=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(free.buffer==first.buffer);p.FreeDeferred(free);
        arena.reset(); // Partial tail is retired to the pool, not destroyed.
        const auto first_again=p.Request(16_MB,MemoryType::HostUncached,256,true);
        const auto released_tail=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(first_again.buffer==first.buffer&&released_tail.buffer==second.buffer);
        p.FreeDeferred(first_again);p.FreeDeferred(released_tail);
    }
    std::cout<<"ORDER_READCONST_RECORD_SCOPE nested/early-return/destruction=PASS\n";
}
void AllocationExceptionTest() {
    Common::ElfInfo::Instance().serial="CUSA00785";
    if(!BachataCompat::Order1886())return;
    Instance i;Scheduler s;StagingBufferPool p(i,s);Core::MemoryManager memory;
    std::unique_ptr<OrderReadConstArena> arena;
    StagingBufferRef first{};
    bool caught=false;
    try {
        OrderReadConstRecordScope recording(arena,p);
        first=MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),8_MB);
        const auto second=MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),4_MB);
        assert(first.buffer==second.buffer); // A partial 12-MiB block will roll over.
        s.submitted=1;s.completed=1;s.current=2;
        VideoCore::Buffer::throw_next_allocation=true;
        (void)MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),8_MB);
    } catch(const std::bad_alloc&) {
        caught=true;
    }
    assert(caught&&!VideoCore::Buffer::throw_next_allocation);
    // Unwinding the actual guard must leave a usable, non-recording arena.
    {
        OrderReadConstRecordScope retry(arena,p);
        const auto next=MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),512);
        assert(next.buffer!=first.buffer);
    }
    arena.reset(); // A duplicated current/pending alias would free first twice.
    const auto busy=p.Request(16_MB,MemoryType::HostUncached,256,true);
    assert(busy.buffer!=first.buffer);p.FreeDeferred(busy);
    s.submitted=2;s.completed=2;
    const auto released=p.Request(16_MB,MemoryType::HostUncached,256,true);
    assert(released.buffer==first.buffer);p.FreeDeferred(released);
    std::cout<<"ORDER_READCONST_ALLOCATION_EXCEPTION unwind/retry/single-retirement=PASS\n";
}
void NoAllocationCleanupTest() {
    Common::ElfInfo::Instance().serial="CUSA00785";
    if(!BachataCompat::Order1886())return;
    for(u32 copies:{1u,2u,4u}) {
        Instance i;Scheduler s;StagingBufferPool p(i,s);Core::MemoryManager memory;
        std::unique_ptr<OrderReadConstArena> arena;
        StagingBufferRef first{};
        {
            OrderReadConstRecordScope recording(arena,p);
            for(u32 n=0;n<copies;++n) {
                const auto snapshot=MakePooledReadConstSnapshot(i,&memory,*arena,memory.Base(),8_MB);
                if(n==0)first=snapshot;
            }
            // Covers partial current, exactly full with no pending capacity,
            // and already pending blocks plus another exactly full current.
            forbid_allocations=true;
        } // Actual EndRecording/RetireRecorded must not invoke operator new.
        arena.reset(); // The partial tail destructor must not allocate either.
        forbid_allocations=false;
        s.submitted=1;s.completed=1;
        const auto released=p.Request(16_MB,MemoryType::HostUncached,256,true);
        assert(released.buffer==first.buffer);p.FreeDeferred(released);
    }
    std::cout<<"ORDER_READCONST_NO_ALLOC_CLEANUP partial/full/pending/destructor=PASS\n";
}
void GuardsAndSelectionTest() {
    Instance i;Scheduler s;StagingBufferPool p(i,s);Core::MemoryManager m;Fill(m,7);
    OrderReadConstArena arena(p);arena.BeginRecording();
    for(auto [address,size]:std::vector<std::pair<u64,u64>>{
            {m.Base(),0},{m.Base(),8_MB+1},{UINT64_MAX-8,64},{m.Base()-1,64},
            {m.Base()+m.guest.size()-4,8}}) {
        const u64 old=VideoCore::Buffer::allocations;
        assert(!MakePooledReadConstSnapshot(i,&m,arena,address,size).buffer);
        assert(VideoCore::Buffer::allocations==old);
    }
    for(bool unmapped:{false,true}) {
        m.unmapped=unmapped;m.readable=false;
        assert(!MakePooledReadConstSnapshot(i,&m,arena,m.Base(),512).buffer);
    }
    m.unmapped=false;m.readable=true;
    Runtime runtime{p};Cache cache(i,s);
    std::unique_ptr<OrderReadConstArena> order_readconst_arena;
    for(const std::string serial:{"CUSA00785","CUSA08809","CUSA08034","OTHER"}) {
        Common::ElfInfo::Instance().serial=serial;
        for(bool gpu:{false,true})for(bool written:{false,true})for(bool role:{false,true}) {
            cache.gpu=gpu;m.forbid_copy=gpu||written||!role;
            const u64 obtains=cache.obtains,pending=s.pending.size();
            auto bound=Select(i,&m,runtime,s,cache,Desc{role,written,false},m.Base(),512,
                              order_readconst_arena);
            if(m.forbid_copy) {
                assert(bound.buffer==&cache.fallback&&cache.obtains==obtains+1);
                assert(s.pending.size()==pending);
            } else if(BachataCompat::Order1886()) {
                assert(bound.buffer!=&cache.fallback&&cache.obtains==obtains);
                assert(s.pending.size()==pending);
                assert(bound.offset%256==0);
            } else {
                assert(bound.buffer!=&cache.fallback&&cache.obtains==obtains);
                assert(s.pending.size()==pending+1&&bound.offset==0);
            }
        }
    }
    arena.EndRecording();
    std::cout<<"ORDER_READCONST_GUARDS GPU-authority/VMA/readability/size/other-titles=PASS\n";
}
void CostWindowTest() {
    OrderReadConstCostWindow w;cost_logs.clear();
    w.Add(10'000'000,100,512);
    assert(cost_logs.size()==1&&cost_logs[0][2]==1&&cost_logs[0][4]==512);
    w.Add(11'000'000,150,0);
    assert(cost_logs.size()==1);
    w.Add(12'000'000,200,256);
    assert(cost_logs.size()==2&&cost_logs[1][1]==2'000'000&&cost_logs[1][2]==2);
    assert(cost_logs[1][3]==1&&cost_logs[1][4]==256&&cost_logs[1][5]==350&&cost_logs[1][6]==200);
    std::cout<<"ORDER_READCONST_COST_WINDOW first/2s/aggregates=PASS\n";
}
int main(int argc,char**) {
    if(argc>1){LifetimeTest();PreconsumeLifetimeTest();RecordingScopeTest();AllocationExceptionTest();NoAllocationCleanupTest();return 0;}
    ByteAndAllocationTest();LifetimeTest();PreconsumeLifetimeTest();RecordingScopeTest();
    AllocationExceptionTest();NoAllocationCleanupTest();GuardsAndSelectionTest();CostWindowTest();
}
'''
    values = {
        "POLICY": block(profile, "inline bool Order1886()"),
        "CACHE_LIMIT": cache_limit_interface,
        "STREAM": stream_methods, "POOL": pool_methods,
        "COST": costs, "OLD": old, "NEW": new, "SELECTION": selection,
        "ARENA": arena, "SCOPE": scope, "WAIT": block(scheduler, "void Scheduler::Wait(u64 tick)"),
    }
    source = template
    for name, value in values.items():
        source = source.replace("@" + name + "@", value)
    with tempfile.TemporaryDirectory(prefix="order-readconst-pool-") as temp:
        temp = Path(temp)
        compiler = shlex.split(os.environ.get("CXX", "c++"))

        def compile_and_run(label: str, text: str, *, android: bool = True,
                            negative: bool = False, lifetime_only: bool = False) -> None:
            path, exe = temp / (label + ".cpp"), temp / label
            path.write_text(text)
            command = compiler + ["-std=c++23", "-O2", "-Wall", "-Wextra", "-Werror",
                                  str(path), "-o", str(exe)]
            if android:
                command.append("-D__ANDROID__")
            subprocess.run(command, check=True)
            result = subprocess.run([str(exe)] + (["lifetime"] if lifetime_only else []),
                                    capture_output=True, text=True)
            if negative:
                if result.returncode == 0:
                    raise AssertionError("Negative control accepted: " + label)
                if label == "cleanup_allocation" and "bad_alloc" not in result.stderr:
                    raise AssertionError("Cleanup control did not reach the forbidden allocation: "
                                         + result.stdout + result.stderr)
                print("ORDER_READCONST_NEGATIVE_CONTROL_PASS", label)
            else:
                if result.returncode:
                    raise AssertionError(label + "\n" + result.stdout + result.stderr)
                print(result.stdout, end="")

        if not args.negative_control:
            compile_and_run("android", source)
            compile_and_run("non_android", source, android=False)
        mutations = {
            "unfenced_reuse": (
                "VideoCore::MemoryType::HostUncached, alignment, true, false);",
                "VideoCore::MemoryType::HostUncached, alignment, true, true);", True),
            "unheld_block": (
                "VideoCore::MemoryType::HostUncached, alignment, true, false);",
                "VideoCore::MemoryType::HostUncached, alignment, false, false);", True),
            "release_before_consumer": (
                "if (current.buffer) pending.push_back(current);",
                "if (current.buffer) pool.FreeDeferred(current);", True),
            "lost_final_tick": ("it->tick = scheduler.CurrentTick();", "it->tick = 0;", True),
            "nested_early_release": (
                "if (--recording_depth == 0) RetireRecorded();",
                "--recording_depth; RetireRecorded();", True),
            "held_tail_leak": (
                "if (current.buffer) pool.FreeDeferred(current);",
                "/* leaked held tail */", True),
            "rollover_duplicate_alias": (
                "            current = {};\n            offset = begin = 0;",
                "            /* stale current aliases pending after a failed allocation */\n"
                "            offset = begin = 0;", True),
            "cleanup_allocation": (
                cleanup,
                "void RetireRecorded() {\n"
                "        if (current.buffer && offset == current.size) {\n"
                "            pending.push_back(current);\n"
                "            current = {};\n"
                "            offset = 0;\n"
                "        }\n"
                "        for (const auto& block : pending) pool.FreeDeferred(block);\n"
                "        pending.clear();\n"
                "    }", True),
            "missing_flush": ("    snapshot.Flush();", "    /* missing flush */", False),
            "lost_alignment": (
                "const u64 alignment = std::max<u64>(atom, instance.StorageMinAlignment());",
                "const u64 alignment = 1;", False),
            "lost_padding": (
                "if (alloc_size > bytes) std::memset(snapshot.mapped + bytes, 0, alloc_size - bytes);",
                "/* missing padding */", False),
            "stale_gpu_snapshot": (
                "if (desc.used_as_readconst && !desc.is_written && size!=0 &&\n"
                "                    !buffer_cache.IsRegionGpuModified(vsharp.base_address,size))",
                "if (desc.used_as_readconst && !desc.is_written && size!=0 && true)", False),
            "lost_size_bound": (
                "bytes == 0 || bytes > 8_MB || address > UINT64_MAX - bytes",
                "bytes == 0 || bytes > 16_MB || address > UINT64_MAX - bytes", False),
        }
        for label, (before, after, lifetime_only) in mutations.items():
            if args.negative_control and label != args.negative_control:
                continue
            assert source.count(before) == 1, label
            compile_and_run(label, source.replace(before, after, 1),
                            negative=True, lifetime_only=lifetime_only)
        if args.negative_control:
            return
        for name in ("Draw", "DrawIndirect", "DispatchDirect", "DispatchIndirect"):
            method = block(rasterizer, "void Rasterizer::" + name + "(")
            stripped = method.replace(
                "    OrderReadConstRecordScope readconst_recording{\n"
                "        order_readconst_arena, runtime.GetStagingPool()};\n", "", 1)
            try:
                validate_scopes(rasterizer.replace(method, stripped, 1))
            except AssertionError:
                print("ORDER_READCONST_NEGATIVE_CONTROL_PASS missing_scope_" + name)
            else:
                raise AssertionError("Missing recording scope accepted: " + name)


if __name__ == "__main__":
    main()
