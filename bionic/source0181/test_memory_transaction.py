#!/usr/bin/env python3
"""Compile the effective MemoryTracker/RegionManager against a watcher-only mock.
Tests protection order, page boundary behavior, concurrent dirty word publication.
Does not claim Android/FEX runtime equivalence.
"""
import argparse, pathlib, subprocess, tempfile
p=argparse.ArgumentParser()
p.add_argument("--source",required=True)
args=p.parse_args()
src=(pathlib.Path(args.source)/"src").resolve()
with tempfile.TemporaryDirectory() as d:
    tmp=pathlib.Path(d)
    def write(path,content):
        target=tmp/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content)
    write("core/emulator_settings.h",r'''
#pragma once
enum GpuReadbacksMode : int {Disabled, Relaxed, Precise};
inline struct { unsigned GetReadbacksMode() const {return Precise;} } EmulatorSettings;
''')
    write("video_core/page_manager.h",r'''
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
        std::lock_guard l{mutex};
        return counts[a/4096];
    }
    void UpdatePageWatchersForRegion(VAddr base,const Bounds& bounds,
        const RegionBits& writes,const RegionBits& reads,PageOp w,PageOp r) {
        std::lock_guard l{mutex};
        for(u64 i=bounds.start_word*PAGES_PER_WORD+bounds.start_page;
            i<=bounds.end_word*PAGES_PER_WORD+bounds.end_page;++i) {
            auto& n=counts[base/4096+i];
            if(w!=PageOp::None&&writes.GetPage(i)) n.first+=int(w);
            if(r!=PageOp::None&&reads.GetPage(i)) n.second+=int(r);
            assert(n.first>=0&&n.first<=1&&n.second>=0&&n.second<=1);
        }
    }
private:
    std::mutex mutex;
    std::map<u64,std::pair<int,int>> counts;
};
}
''')
    write("test.cpp",r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <functional>
#include <iostream>
#include <memory>
#include <thread>
#include <type_traits>
#include <utility>
#include "video_core/buffer_cache/memory_tracker.h"
using namespace VideoCore;
int main() {
    PageManager pm;
    auto t=std::make_unique<MemoryTracker>(pm);
    constexpr VAddr a=HIGHER_PAGE_SIZE-4096;
    constexpr VAddr b=a+4096;
    constexpr u64 n=8192;
    auto check=[&](int write,int read) {
        assert((pm.At(a)==std::pair{write,read}));
        assert((pm.At(b)==std::pair{write,read}));
    };
    u64 bytes=0;
    int uploads=0;
    auto gather=[&](VAddr addr,u64 size) {
        assert(addr>=a&&addr+size<=a+n);
        bytes+=size;
    };
    t->ForEachUploadRange(a,n,true,gather,[&]{
        assert(bytes==n);
        check(1,0);
        assert(!t->IsRegionGpuModified(a,n));
        ++uploads;
    });
    check(1,1);
    assert(t->IsRegionGpuModified(a,n)&&!t->IsRegionCpuModified(a,n));
    bytes=0;
    t->ForEachUploadRange(a,n,false,gather,[&] {
        assert(bytes==0);check(1,1);++uploads;
    });
    t->UnmarkRegionAsGpuModified(a,n,false);
    check(1,0);
    t->MarkRegionAsCpuModified(a,n);
    check(0,0);
    t->ForEachUploadRange(a,n,false,gather,[&]{
        assert(bytes==n);check(1,0);++uploads;
    });
    check(1,0);
    assert(!t->IsRegionGpuModified(a,n));
    assert(uploads==3);
    bool invalid_called=false;
    auto invalid=[&]{invalid_called=true;};
    t->ForEachUploadRange(a,0,true,gather,invalid);
    t->ForEachUploadRange((1ULL<<40)-4096,8192,true,gather,invalid);
    assert(!invalid_called);
    assert(!t->IsRegionCpuModified(1ULL<<40,4096));
    // Drain initial whole-region notifications, then prove exact dirty-word
    // publication, coalescing and one-time consumption across the boundary.
    t->ForEachSweepSpan([](VAddr,u64){});
    t->MarkRegionAsCpuModified(a,n);
    std::vector<std::pair<VAddr,u64>> spans;
    auto collect=[&](VAddr addr,u64 size){spans.emplace_back(addr,size);};
    t->ForEachSweepSpan(collect);
    std::ranges::sort(spans);
    assert(spans.size()==2);
    assert((spans[0]==std::pair<VAddr,u64>{HIGHER_PAGE_SIZE-BYTES_PER_WORD,BYTES_PER_WORD}));
    assert((spans[1]==std::pair<VAddr,u64>{HIGHER_PAGE_SIZE,BYTES_PER_WORD}));
    spans.clear();
    t->ForEachSweepSpan(collect);
    assert(spans.empty());
    bytes=0;
    t->ForEachUploadRange(a,n,false,gather,[&]{assert(bytes==n);});
    std::atomic<bool> stop{false};
    std::thread reader([&]{
        while(!stop.load(std::memory_order_acquire))
            (void)t->IsRegionCpuModified(a,n);
    });
    for(int i=0;i<4096;++i){
        t->MarkRegionAsCpuModified(a,n);
        bytes=0;
        t->ForEachUploadRange(a,n,false,gather,[&]{
            assert(bytes==n);
            check(1,0);
        });
    }
    stop.store(true,std::memory_order_release);
    reader.join();
    std::cout<<"BACHATA_EFFECTIVE_DONOR_UPLOAD_TRANSACTION_PASS cross_region=2 cycles=4096\n";
}
''')
    binary=tmp/"test"
    subprocess.run(["c++","-std=c++23","-O2","-pthread","-I",str(tmp),"-I",str(src),str(tmp/"test.cpp"),"-o",str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
