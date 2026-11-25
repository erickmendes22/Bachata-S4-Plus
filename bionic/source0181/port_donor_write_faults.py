"""Port effective donor guest write fault windows and SotC repeat-fault grace.
Order c53cd01 aligned 256 KiB fault window; SotC 732cb37 + 0366868
15-page write-ahead, two-quantum hot-page retention and dirty DMA requeue.
Preserve precise GPU read protection, sparse aliases, and FEX ABI.
"""
from pathlib import Path
def apply(root:Path,order:bool):
    src=root/"src";v=src/"video_core";bc=v/"buffer_cache"
    def edit(p,a,b,n=1):
        s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"donor write faults {p.name}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    mt=bc/"memory_tracker.h"
    # Only clean, already tracked, non-GPU-owned pages can be unprotected.
    # A marked but not written page only costs a later upload.
    edit(mt,"    /// Removes all protection from a page and ensures GPU data has been flushed if requested",
         """    template<bool stop_at_dirty>
    void MarkWriteWindow(VAddr cpu_addr,u64 size) noexcept {
        if ((cpu_addr&(BYTES_PER_PAGE-1)) || (size&(BYTES_PER_PAGE-1))) return;
        IteratePages(cpu_addr,size,[](RegionManager* manager,u64 offset,u64 size) {
            const auto bounds=manager->GetBounds(offset,size);
            manager->Lock(bounds);
            u64 run_start=0,run_size=0;
            const auto flush=[&] {
                if(run_size) manager->template ChangeRegionState<StateOp::Set,StateOp::None,false>(
                    run_start,run_size);
                run_size=0;
            };
            bool stopped=false;
            for(u64 n=0;n<size;n+=BYTES_PER_PAGE) {
                const auto at=offset+n;
                const bool dirty=manager->template IsRegionModified<Type::GPU>(at,BYTES_PER_PAGE) ||
                    manager->template IsRegionModified<Type::CPU>(at,BYTES_PER_PAGE);
                if(dirty) {
                    flush();
                    if constexpr(stop_at_dirty) {stopped=true;break;}
                } else {
                    if(!run_size)run_start=at;
                    run_size+=BYTES_PER_PAGE;
                }
            }
            flush();
            manager->Unlock(bounds);
            return stopped;
        });
    }

    /// Removes all protection from a page and ensures GPU data has been flushed if requested""")
    header=v/"renderer_vulkan/vk_rasterizer.h";rast=v/"renderer_vulkan/vk_rasterizer.cpp"
    edit(header,"    bool InvalidateMemory(VAddr addr, u64 size, bool assume_locks = false);",
         "    bool InvalidateMemory(VAddr addr, u64 size, bool assume_locks = false, bool guest_fault = false);")
    edit(rast,"bool Rasterizer::InvalidateMemory(VAddr addr, u64 size, bool assume_locks) {",
         "bool Rasterizer::InvalidateMemory(VAddr addr, u64 size, bool assume_locks, bool guest_fault) {")
    # Only genuine guest faults feed the grace/window. Other invalidations
    # (unmap, HLE, GPU command thread) retain the exact old path.
    if order:
        policy=r'''    buffer_cache.InvalidateMemory(addr, size, assume_locks);
    texture_cache.InvalidateMemory(addr, size);
    if(guest_fault && !assume_locks && Common::ElfInfo::Instance().GameSerial()=="CUSA00785") {
        constexpr u64 span=256_KB;
        const VAddr begin=Common::AlignDown(addr,span);
        if(IsMapped(begin,span)) buffer_cache.MarkGuestWriteWindow(begin,span);
    }'''
    else:
        policy=r'''    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const bool target=serial=="CUSA08809"||serial=="CUSA08034";
    buffer_cache.InvalidateMemory(addr, size, assume_locks, guest_fault&&target);
    texture_cache.InvalidateMemory(addr, size);
    if(target && guest_fault && !assume_locks) {
        constexpr u64 span=15*4_KB;
        const VAddr begin=Common::AlignUp(addr+1,4_KB);
        if(IsMapped(begin,span)) buffer_cache.MarkGuestWriteWindow(begin,span);
    }'''
    edit(rast,"    buffer_cache.InvalidateMemory(addr, size, assume_locks);\n    texture_cache.InvalidateMemory(addr, size);",policy)
    page=v/"page_manager.cpp"
    edit(page,"return rasterizer->InvalidateMemory(addr, size, is_gpu_thread);",
         "return rasterizer->InvalidateMemory(addr, size, is_gpu_thread, !is_gpu_thread);")
    edit(page,"""            rasterizer->InvalidateMemory(addr, 1,
                                         ptid == rasterizer->GetGpuCommandProcessorThreadId());""",
         """            const bool gpu_thread=ptid==rasterizer->GetGpuCommandProcessorThreadId();
            rasterizer->InvalidateMemory(addr,1,gpu_thread,!gpu_thread);""")
    h=bc/"buffer_cache.h";c=bc/"buffer_cache.cpp"
    edit(h,"    void InvalidateMemory(VAddr device_addr, u64 size, bool assume_locks = false);",
         "    void InvalidateMemory(VAddr device_addr, u64 size, bool assume_locks = false"+("" if order else ", bool guest_fault = false")+");\n    void MarkGuestWriteWindow(VAddr addr,u64 size);")
    edit(c,"void BufferCache::InvalidateMemory(VAddr device_addr, u64 size, bool assume_locks) {",
         "void BufferCache::MarkGuestWriteWindow(VAddr addr,u64 size) {\n    memory_tracker->MarkWriteWindow<"+("false" if order else "true")+">(addr,size);\n}\n\nvoid BufferCache::InvalidateMemory(VAddr device_addr, u64 size, bool assume_locks"+("" if order else ", bool guest_fault")+") {")
    if not order:
        edit(c,"""        ReadMemory(device_addr, size, true, assume_locks);
    });
}""","""        ReadMemory(device_addr, size, true, assume_locks);
    },guest_fault);
}""")
        rm=bc/"region_manager.h"
        edit(rm,"#include <atomic>","#include <atomic>\n#include <algorithm>\n#include <chrono>\n#include <cstdlib>")
        edit(rm,"namespace VideoCore {\n","""namespace VideoCore {
struct FaultGrace {
    static u32 Pages() {
        static const u32 v=[] {
            const char* e=std::getenv("SOTC_FAULT_GRACE");
            if(e&&e[0]=='0')return 0u;
            const char* p=std::getenv("SOTC_FAULT_GRACE_PAGES");
            return p?static_cast<u32>(std::min<unsigned long>(std::strtoul(p,nullptr,10),1024)):32u;
        }();
        return v;
    }
    static u32 Now() {
        static const u64 us=[] {
            const char* e=std::getenv("SOTC_FAULT_GRACE_US");
            return std::clamp<u64>(e?std::strtoull(e,nullptr,10):1000ULL,100,100000);
        }();
        return static_cast<u32>(std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count()/us);
    }
    inline static std::atomic<u32> budget_epoch{0},budget_used{0};
    static bool TakeBudget(u32 now) {
        auto epoch=budget_epoch.load(std::memory_order_relaxed);
        if(epoch!=now&&budget_epoch.compare_exchange_strong(epoch,now,std::memory_order_relaxed))
            budget_used.store(0,std::memory_order_relaxed);
        return budget_used.fetch_add(1,std::memory_order_relaxed)<Pages();
    }
};
""")
        edit(rm,"        cpu.Fill(~0ULL);\n        gpu.Fill(0ULL);",
             "        cpu.Fill(~0ULL);\n        gpu.Fill(0ULL);\n        ResetGrace();\n        (void)FaultGrace::Pages();(void)FaultGrace::Now();")
        edit(rm,"        sweep_words.store(~u64{0},std::memory_order_relaxed);",
             "        sweep_words.store(~u64{0},std::memory_order_relaxed);\n        ResetGrace();")
        edit(rm,"    VAddr CpuAddress() const noexcept { return cpu_addr; }",
             """    VAddr CpuAddress() const noexcept { return cpu_addr; }
    void NoteGuestWriteFaultLocked(u64 offset) {
        if(!FaultGrace::Pages())return;
        const auto page=offset/BYTES_PER_PAGE;
        const auto index=page/PAGES_PER_WORD,bit=u64{1}<<(page%PAGES_PER_WORD);
        const auto now=FaultGrace::Now();
        RotateGraceLocked(now);
        if(!grace_any){grace_epoch=now;grace_any=true;}
        const bool repeat=((fault_cur[index]|fault_prev[index])&bit)!=0;
        fault_cur[index]|=bit;
        if(repeat&&!((hot_cur[index]|hot_prev[index])&bit)&&FaultGrace::TakeBudget(now))
            hot_cur[index]|=bit;
    }""")
        edit(rm,"template <Type type, StateOp cpu_op, StateOp gpu_op, bool locked = true>",
             "template <Type type, StateOp cpu_op, StateOp gpu_op, bool locked = true, bool allow_grace = false>")
        edit(rm,"""        IterateWords(bounds, [&](u64 index, u64 mask) {
            const u64 base_page = index * PAGES_PER_WORD;
            const u64 word = std::atomic_ref<u64>(state[index]).load(std::memory_order_acquire) & mask;
            UpdateStateAndProtection<cpu_op, gpu_op>(write_prot, read_prot, index, mask);""",
             """        // Crucial adaptation: our writable binding publishes GPU ownership
        // after the upload callback, so only the read-only call site passes
        // allow_grace=true. Written bindings always clear CPU ownership.
        constexpr bool grace_op=allow_grace&&type==Type::CPU&&
            cpu_op==StateOp::Clear&&gpu_op==StateOp::None;
        if constexpr(grace_op) RotateGraceLocked(FaultGrace::Now());
        IterateWords(bounds, [&](u64 index, u64 mask) {
            const u64 base_page = index * PAGES_PER_WORD;
            const u64 word = std::atomic_ref<u64>(state[index]).load(std::memory_order_acquire) & mask;
            u64 keep=0;
            if constexpr(grace_op) {
                if(grace_any) {
                    keep=(hot_cur[index]|hot_prev[index])&word&
                        ~std::atomic_ref<u64>(gpu[index]).load(std::memory_order_acquire);
                    if(keep)sweep_words.fetch_or(u64{1}<<index,std::memory_order_release);
                }
            }
            UpdateStateAndProtection<cpu_op, gpu_op>(write_prot, read_prot, index, mask&~keep);""")
        edit(rm,"    std::atomic<u64> sweep_words{~u64{0}};\n    LockType mutex;",
             """    std::atomic<u64> sweep_words{~u64{0}};
    RegionBits fault_cur{},fault_prev{},hot_cur{},hot_prev{};
    u32 grace_epoch{};
    bool grace_any{};
    void ResetGrace() {
        fault_cur.Fill(0);fault_prev.Fill(0);hot_cur.Fill(0);hot_prev.Fill(0);
        grace_epoch=0;grace_any=false;
    }
    void RotateGraceLocked(u32 now) {
        if(!grace_any||now==grace_epoch)return;
        const bool adjacent=now-grace_epoch==1;
        if(adjacent){fault_prev=fault_cur;hot_prev=hot_cur;}
        else {fault_prev.Fill(0);hot_prev.Fill(0);}
        fault_cur.Fill(0);hot_cur.Fill(0);
        grace_any=adjacent;grace_epoch=now;
    }
    LockType mutex;""")
        edit(mt,"void InvalidateRegion(VAddr cpu_addr, u64 size, auto&& on_flush) noexcept {",
             "void InvalidateRegion(VAddr cpu_addr, u64 size, auto&& on_flush,bool guest_fault=false) noexcept {")
        edit(mt,"IteratePages(cpu_addr, size, [&should_flush](RegionManager* manager, u64 offset, u64 size) {",
             "IteratePages(cpu_addr, size, [&should_flush,guest_fault](RegionManager* manager, u64 offset, u64 size) {")
        edit(mt,"            manager->Lock(bounds);\n            const bool modified =",
             "            manager->Lock(bounds);\n            if(guest_fault)manager->NoteGuestWriteFaultLocked(offset);\n            const bool modified =")
        edit(mt,"manager->template ForEachModifiedRange<Type::CPU,StateOp::Clear,StateOp::None>(\n                        offset,n,func);",
             "manager->template ForEachModifiedRange<Type::CPU,StateOp::Clear,StateOp::None,true,true>(\n                        offset,n,func);")
    return {"write_faults":"Order aligned 256KiB / SotC 15-page write ahead, only mapped clean pages",
            "sotc_grace":not order,"sotc_grace_gpu_writable_excluded":not order,
            "fex":"unchanged","fps":"original flip protocol"}
