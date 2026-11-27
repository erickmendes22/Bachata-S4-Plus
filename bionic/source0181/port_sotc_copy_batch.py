"""Port staged SotC's batched 512-KiB physical geometry uploads to FEX.

The donor's optional cross-submit async upload cannot outlive the FEX upload
transaction: mapping and dirty-page ownership may change. Keep the staged
renderer parallel copy and join before GPU ownership and command recording.
"""
from pathlib import Path

POOL = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <functional>
#include <mutex>
#include <thread>
#include <vector>

namespace BachataCopyBatch {
class Pool {
    struct Job {
        const std::function<void(std::size_t)>& run;
        std::size_t count;
        std::atomic_size_t next{0};
        void Work() {
            for (;;) {
                auto i=next.fetch_add(1,std::memory_order_relaxed);
                if(i>=count) return;
                run(i);
            }
        }
    };
    std::mutex serial, mutex;
    std::condition_variable_any work;
    std::condition_variable done;
    Job* job{};
    std::size_t epoch{}, remaining{};
    std::vector<std::jthread> workers;
public:
    explicit Pool(unsigned count) {
        workers.reserve(count);
        for(unsigned i=0;i<count;++i) workers.emplace_back([this](std::stop_token stop) {
            std::size_t seen=0;
            for (;;) {
                std::unique_lock lock{mutex};
                if(!work.wait(lock,stop,[&]{return epoch!=seen;})) return;
                seen=epoch;
                auto* active=job;
                lock.unlock();
                active->Work();
                lock.lock();
                if(--remaining==0) done.notify_one();
            }
        });
    }
    ~Pool() {
        for(auto& worker:workers) worker.request_stop();
        work.notify_all();
        workers.clear();
    }
    void Run(std::size_t count,const std::function<void(std::size_t)>& run) {
        if(count<2 || workers.empty()) {
            for(std::size_t i=0;i<count;++i) run(i);
            return;
        }
        std::scoped_lock one{serial};
        Job active{run,count};
        {
            std::scoped_lock lock{mutex};
            job=&active;
            remaining=workers.size();
            ++epoch;
        }
        work.notify_all();
        active.Work();
        std::unique_lock lock{mutex};
        done.wait(lock,[&]{return remaining==0;});
        job=nullptr;
    }
};
inline void ParallelFor(std::size_t count,const std::function<void(std::size_t)>& run) {
    static Pool pool{std::clamp(std::thread::hardware_concurrency()/4,1u,4u)};
    pool.Run(count,run);
}
} // namespace BachataCopyBatch
'''

METHOD = r'''void MemoryManager::CopySparseMemoryBatch(std::span<const SparseCopy> ranges) {
    // All physical backing pointers and VMA topology stay valid until the
    // last worker has joined. Workers never acquire VMM/region locks or
    // access a protected guest address. File mappings use the original path.
    std::shared_lock lk{mutex};
    constexpr u64 piece_size=512*1024;
    std::vector<SparseCopy> pieces;
    bool physical=true;
    for(const auto& range:ranges) {
        for(u64 offset=0;offset<range.size;) {
            const auto address=range.source+offset;
            if(address<range.source || !IsValidMapping(address)) {physical=false;break;}
            const auto& vma=FindVMA(address)->second;
            if(address<vma.base || address-vma.base>=vma.size || !HasPhysicalBacking(vma)) {
                physical=false;break;
            }
            const auto bytes=std::min({range.size-offset,vma.size-(address-vma.base),piece_size});
            pieces.push_back({address,range.dest+offset,bytes});
            offset+=bytes;
        }
        if(!physical) break;
    }
    if(!physical) {
        for(const auto& range:ranges) CopySparseMemoryUnlocked(range.source,range.dest,range.size);
        return;
    }
    BachataCopyBatch::ParallelFor(pieces.size(),[&](std::size_t i) {
        const auto& piece=pieces[i];
        CopySparseMemoryUnlocked(piece.source,piece.dest,piece.size);
    });
}
'''

def apply(root):
    src=Path(root)/'src'
    def edit(path, old, new):
        p=src/path;s=p.read_text()
        if s.count(old)!=1: raise RuntimeError(f'{path}: copy batch anchor drift ({s.count(old)}) {old[:100]}')
        p.write_text(s.replace(old,new,1))
    (src/'core/bachata_parallel_copy.h').write_text(POOL)
    edit('core/memory.h','#include <map>','#include <map>\n#include <span>')
    edit('core/memory.h','    void CopySparseMemory(VAddr source, u8* dest, u64 size);', '''    void CopySparseMemory(VAddr source, u8* dest, u64 size);
    struct SparseCopy { VAddr source; u8* dest; u64 size; };
    void CopySparseMemoryBatch(std::span<const SparseCopy> ranges);''')
    edit('core/memory.h','private:\n    VMAHandle FindVMA(VAddr target)', 'private:\n    void CopySparseMemoryUnlocked(VAddr address,u8* dest,u64 size);\n    VMAHandle FindVMA(VAddr target)')
    edit('core/memory.cpp','#include "core/memory.h"','#include "core/memory.h"\n#include "core/bachata_parallel_copy.h"')
    edit('core/memory.cpp','''void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {
    std::shared_lock lk{mutex};
    while (size) {''','''void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {
    std::shared_lock lk{mutex};
    CopySparseMemoryUnlocked(address,dest,size);
}

'''+METHOD+'''
void MemoryManager::CopySparseMemoryUnlocked(VAddr address, u8* dest, u64 size) {
    while (size) {''')
    edit('video_core/buffer_cache/buffer_cache.cpp','''        staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);
        for (auto& copy : copies) {
            memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);''','''        staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);
        static const bool copy_batch=[] {
            const char* v=std::getenv("SOTC_COPY_BATCH");
            return !v || v[0]!='0';
        }();
        const bool parallel=IsSotcArena() && copy_batch && total_size_bytes>=2_MB;
        if(parallel) {
            std::vector<Core::MemoryManager::SparseCopy> ranges;
            ranges.reserve(copies.size());
            for(const auto& copy:copies)
                ranges.push_back({copy.dstOffset,staging.mapped+copy.srcOffset,copy.size});
            memory->CopySparseMemoryBatch(ranges);
        }
        for (auto& copy : copies) {
            if(!parallel) memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);''')
