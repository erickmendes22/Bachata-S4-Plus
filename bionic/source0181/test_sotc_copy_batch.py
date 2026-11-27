"""Test the actual MemoryManager batch and staged-copy order, without a GPU."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
src=a.source/'src';s=(src/'core/memory.cpp').read_text()
methods=s[s.index('void MemoryManager::CopySparseMemory('):s.index('// Validate every physical span')]
header=(src/'core/memory.h').read_text()
assert 'void CopySparseMemoryBatch(std::span<const SparseCopy> ranges);' in header
body=(src/'video_core/buffer_cache/buffer_cache.cpp').read_text();body=body[body.index('bool BufferCache::SynchronizeMemory('):body.index('bool BufferCache::SynchronizeMemoryFromImage(')]
assert body.index('memory_tracker->ForEachUploadRange')<body.index('CopySparseMemoryBatch(ranges)')<body.index('staging.Flush()')<body.index('runtime.CopyBuffer(staging.buffer, arena, copies)')
fixture=r'''
#include "core/bachata_parallel_copy.h"
#include <cassert>
#include <bit>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <shared_mutex>
#include <span>
#include <random>
using u64=uint64_t;using VAddr=u64;using u8=uint8_t;
struct Part{u64 base,size;};
struct Vma{u64 base,size;bool physical;std::map<u64,Part> phys_areas;bool IsMapped()const{return false;}};
struct MemoryManager {
    std::shared_mutex mutex;
    std::map<u64,Vma> vma_map;
    struct Backing{std::vector<u8> data;u8* BackingBase(){return data.data();}}impl;
    struct SparseCopy{VAddr source;u8* dest;u64 size;};
    bool IsValidMapping(u64 addr){return addr>=vma_map.begin()->first&&addr<vma_map.rbegin()->second.base+vma_map.rbegin()->second.size;}
    auto FindVMA(u64 addr){return std::prev(vma_map.upper_bound(addr));}
    bool HasPhysicalBacking(const Vma& v){return v.physical;}
    void CopySparseMemory(VAddr,u8*,u64);
    void CopySparseMemoryUnlocked(VAddr,u8*,u64);
    void CopySparseMemoryBatch(std::span<const SparseCopy>);
};
'''+methods+r'''
int main(){
    constexpr u64 MB=1024*1024;
    MemoryManager m;
    m.impl.data.resize(10*MB);
    for(u64 i=0;i<m.impl.data.size();++i)m.impl.data[i]=(i*23+(i>>12)*19)%251;
    // Multiple VMAs and physical spans; include holes and backwards aliases.
    m.vma_map.emplace(MB,Vma{MB,4*MB,true,{{0,{6*MB,MB}},{MB+4096,{0,MB}},{3*MB,{4*MB,MB}}}});
    m.vma_map.emplace(5*MB,Vma{5*MB,2*MB,true,{{0,{2*MB,2*MB}}}});
    m.vma_map.emplace(7*MB,Vma{7*MB,MB,false,{}});
    m.vma_map.emplace(8*MB,Vma{8*MB,MB,true,{{0,{9*MB,MB}}}});
    std::mt19937_64 gen{112};
    auto check=[&](std::vector<std::pair<u64,u64>> specs){
        u64 total=0;for(auto [_,n]:specs)total+=n;
        std::vector<u8> serial(total+64,0xa5),parallel=serial;
        std::vector<MemoryManager::SparseCopy> ranges;
        u64 offset=32;
        for(auto [source,n]:specs){m.CopySparseMemory(source,serial.data()+offset,n);ranges.push_back({source,parallel.data()+offset,n});offset+=n;}
        m.CopySparseMemoryBatch(ranges);assert(serial==parallel);
    };
    check({{MB,6*MB}});check({{2*MB+73,3*MB},{MB+7,MB+91}});
    check({{6*MB,3*MB}}); // nonphysical VMA -> serial fallback
    check({{MB-4096,3*MB}}); // original invalid-start zero-fill, not split
    check({{8*MB,2*MB}}); // valid prefix, outside tail
    check({});check({{MB,0}});
    for(int i=0;i<50;++i){std::vector<std::pair<u64,u64>> v;for(int j=0;j<4;++j){u64 start=MB+gen()%(8*MB);v.emplace_back(start,gen()%(2*MB));}check(v);}
    // Several concurrent callers must not cross-publish job lifetimes.
    BachataCopyBatch::Pool pool{4};
    std::vector<std::jthread> producers;
    for(int j=0;j<4;++j)producers.emplace_back([&]{for(int k=0;k<40;++k){std::vector<unsigned> hits(257);pool.Run(hits.size(),[&](size_t i){++hits[i];});for(auto n:hits)assert(n==1);}});
    producers.clear();
    std::cout<<"BACHATA_SOTC_PHYSICAL_BATCH_PASS cases=57 concurrent=160\n";
}
'''
with tempfile.TemporaryDirectory() as td:
    f=Path(td)/'test.cpp';f.write_text(fixture);binary=Path(td)/'test'
    subprocess.run(['c++','-std=c++20','-O2','-pthread','-I',str(src),str(f),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True,timeout=30)
