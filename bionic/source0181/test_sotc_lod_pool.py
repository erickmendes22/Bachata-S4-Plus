#!/usr/bin/env python3
"""Exercise the actual FEX VMA query, physical reads and SotC LOD policy.

Memory storage/mapping events are fixtures; physical-span traversal, VMA types,
mapping generation, shared mutex and the pressure policy are effective code.
The guest addresses remain PROT_NONE so direct guest dereferences fail.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def block(text, marker):
    begin = text.index(marker)
    opening = text.index("{", begin)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[begin:end + 1]
    raise AssertionError(marker)


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <cstring>
#include <functional>
#include <iostream>
#include <map>
#include <mutex>
#include <shared_mutex>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
#include <sys/mman.h>
#include "common/types.h"
#include "common/shared_first_mutex.h"
#include "core/memory_map_generation.h"
#define DECLARE_ENUM_FLAG_OPERATORS(...)
unsigned log_count{};
#define LOG_INFO(...) (++log_count)
namespace Common {
struct ElfInfo {
    inline static std::string_view serial="CUSA08809";
    static ElfInfo& Instance(){static ElfInfo value;return value;}
    std::string_view GameSerial()const{return serial;}
};
}
struct ObservedMutex {
    Common::SharedFirstMutex real;
    std::function<void(unsigned)> after_read;
    unsigned reads{};
    void lock(){real.lock();}
    void unlock(){real.unlock();}
    void lock_shared(){real.lock_shared();}
    void unlock_shared(){
        real.unlock_shared();
        const auto callback=after_read;
        ++reads;
        if(callback)callback(reads);
    }
};
namespace Core {
@TYPES@
struct AddressSpace {
    static constexpr u64 capacity=6_GB;
    u8* bytes=static_cast<u8*>(mmap(nullptr,capacity,PROT_READ|PROT_WRITE,
                                   MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE,-1,0));
    AddressSpace(){assert(bytes!=MAP_FAILED);}
    ~AddressSpace(){assert(!munmap(bytes,capacity));}
    u8* BackingBase(){return bytes;}
};
class MemoryManager {
    using PhysMap=std::map<PAddr,PhysicalMemoryArea>;
    using PhysHandle=PhysMap::iterator;
    using VMAMap=std::map<VAddr,VirtualMemoryArea>;
    using VMAHandle=VMAMap::iterator;
public:
    AddressSpace impl;
    PhysMap dmem_map;
    VMAMap vma_map;
    ObservedMutex mutex;
    MemoryMapGeneration mapping_generation;
    u64 total_direct_size{};
    VAddr metadata_va{};
    PAddr metadata_pa{};
    static constexpr u64 metadata_size=0x220000;
    static constexpr u64 bitmap_offset=0x4000;
    @QUERY_DECL@
    bool TryReadBacking(VAddr,void*,u64);
    @VALID@
    @FIND_VMA@
    @FIND_DMEM@
    @BACKED@
    @GENERATION@
    @TOTAL@
    void Build(VAddr base,u64 total=0x128000000ULL) {
        mutex.after_read={};
        std::scoped_lock lock{mutex};
        const auto mutation=mapping_generation.BeginMutation();
        metadata_va=base;total_direct_size=total;metadata_pa=total-metadata_size;
        dmem_map.clear();vma_map.clear();
        dmem_map.emplace(0,PhysicalMemoryArea{0,0x100000,0,PhysicalMemoryType::Mapped});
        dmem_map.emplace(0x100000,PhysicalMemoryArea{0x100000,0x40000000,0,PhysicalMemoryType::Mapped});
        dmem_map.emplace(0x40100000,PhysicalMemoryArea{0x40100000,metadata_pa-0x40100000,3,PhysicalMemoryType::Mapped});
        dmem_map.emplace(metadata_pa,PhysicalMemoryArea{metadata_pa,metadata_size,0,PhysicalMemoryType::Mapped});
        std::memset(impl.bytes+metadata_pa,0,metadata_size);
        SetMaps({Make(base,metadata_size,metadata_pa),Make(base+0x300000,0x40000000,0x100000)});
        SetPool(0);
    }
    static VirtualMemoryArea Make(VAddr a,u64 n,PAddr p,VMAType type=VMAType::Direct) {
        VirtualMemoryArea result{};result.base=a;result.size=n;result.type=type;
        result.prot=MemoryProt::CpuReadWrite;
        if(type==VMAType::Direct||type==VMAType::Flexible)
            result.phys_areas.emplace(0,PhysicalMemoryArea{p,n,0,PhysicalMemoryType::Mapped});
        return result;
    }
    void SetMaps(std::vector<VirtualMemoryArea> values) {
        std::sort(values.begin(),values.end(),[](const auto& a,const auto& b){return a.base<b.base;});
        vma_map.clear();VAddr cursor=0x10000;
        for(auto& value:values){
            assert(value.base>=cursor);
            if(value.base>cursor)vma_map.emplace(cursor,Make(cursor,value.base-cursor,0,VMAType::Free));
            cursor=value.base+value.size;vma_map.emplace(value.base,std::move(value));
        }
        vma_map.emplace(cursor,Make(cursor,(u64{1}<<40)-cursor,0,VMAType::Free));
    }
    std::array<u64,3> Meta()const {
        std::array<u64,3> value{};std::memcpy(value.data(),impl.bytes+metadata_pa+0x190,sizeof(value));return value;
    }
    void SetMeta(std::array<u64,3> meta) {
        std::memcpy(impl.bytes+metadata_pa+0x190,meta.data(),sizeof(meta));
    }
    void SetPool(unsigned percent) {
        const u64 pages=(metadata_pa-0x100000)>>16;
        const u64 words=(pages+63)/64;
        SetMeta({metadata_va+bitmap_offset,words,pages});
        auto* bits=reinterpret_cast<u64*>(impl.bytes+metadata_pa+bitmap_offset);
        std::fill_n(bits,words,0);
        const u64 free=(pages*percent+99)/100;
        for(u64 i=0;i<free;++i)bits[i/64]|=u64{1}<<(i%64);
    }
    void Changed(auto&& operation) {
        std::scoped_lock lock{mutex};
        const auto mutation=mapping_generation.BeginMutation();operation();
    }
};
namespace {
template<class F>
@VISIT@
}
@QUERY@
@READ@
}
@LOD@
'''

MAIN = r'''
int main(){
    constexpr VAddr observed=0x200a30000ULL,donor=0x1000000000ULL;
    std::vector<void*> protected_guest;
    for(const VAddr base:{observed,donor}){
        void* p=mmap(reinterpret_cast<void*>(base),Core::MemoryManager::metadata_size,
                     PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
        assert(p==reinterpret_cast<void*>(base));protected_guest.push_back(p);
    }
    Core::MemoryManager memory;
    unsigned cases{};
    const auto unknown=[&]{
        assert(BachataSotcLod::PoolFreePercent(&memory)==-1);++cases;
    };
    const auto check=[&](int expected){
        BachataSotcLod::PoolSample sample{};
        assert(BachataSotcLod::PoolFreePercent(&memory,&sample)==expected);
        assert(sample.pool==memory.metadata_va+0x140);
        assert(sample.physical==memory.metadata_pa);
        assert(sample.pages==memory.Meta()[2]);++cases;
    };
    for(const auto title:{"CUSA08809","CUSA08034"}){
        Common::ElfInfo::serial=title;assert(BachataSotcLod::Enabled());
        for(const VAddr base:{observed,donor,VAddr{0x5a9000000ULL}}){
            memory.Build(base,base==donor?0x13c000000ULL:0x128000000ULL);
            for(unsigned percent:{0u,2u,3u,7u,8u,10u,16u,17u,51u,100u}){
                memory.SetPool(percent);check(percent);
            }
        }
    }
    Common::ElfInfo::serial="CUSA00785";assert(!BachataSotcLod::Enabled());
    Common::ElfInfo::serial="OTHER";assert(!BachataSotcLod::Enabled());
    Common::ElfInfo::serial="CUSA08809";

    // The donor accepts rounded bitmap capacity. More words than minimally
    // needed do not invalidate the pool; padding bits are capped by pages.
    memory.Build(observed);memory.SetPool(10);
    auto rounded=memory.Meta();rounded[1]*=2;memory.SetMeta(rounded);check(10);
    std::memset(memory.impl.bytes+memory.metadata_pa+memory.bitmap_offset,0xff,rounded[1]*8);check(100);

    // Metadata mapping split across VMAs and physical span entries remains a
    // single physically contiguous, fully mapped candidate.
    memory.Build(observed);
    memory.Changed([&]{
        memory.SetMaps({memory.Make(observed,0x10000,memory.metadata_pa),
                        memory.Make(observed+0x10000,memory.metadata_size-0x10000,memory.metadata_pa+0x10000)});
        auto& first=memory.vma_map.at(observed);
        first.phys_areas.at(0).size=0x4000;
        first.phys_areas.emplace(0x4000,Core::PhysicalMemoryArea{memory.metadata_pa+0x4000,0xc000,0,Core::PhysicalMemoryType::Mapped});
    });check(0);

    // A hole or remap within the candidate invalidates it even when its first
    // bytes still contain convincing allocator metadata.
    memory.Build(observed);
    memory.Changed([&]{
        memory.SetMaps({memory.Make(observed,0x10000,memory.metadata_pa),
                        memory.Make(observed+0x20000,memory.metadata_size-0x20000,memory.metadata_pa+0x20000)});
    });unknown();
    memory.Build(observed);
    memory.Changed([&]{memory.vma_map.at(observed).phys_areas.at(0).size=0x10000;});unknown();
    memory.Build(observed);
    memory.Changed([&]{
        auto& v=memory.vma_map.at(observed);v.phys_areas.at(0).size=0x10000;
        v.phys_areas.emplace(0x10000,Core::PhysicalMemoryArea{0x100000,memory.metadata_size-0x10000,0,Core::PhysicalMemoryType::Mapped});
    });unknown();
    memory.Build(observed);
    memory.Changed([&]{memory.SetMaps({memory.Make(observed,memory.metadata_size,memory.metadata_pa,Core::VMAType::Flexible)});});unknown();
    memory.Build(observed);
    memory.Changed([&]{memory.dmem_map.at(memory.metadata_pa).memory_type=3;});unknown();
    memory.Build(observed);
    memory.Changed([&]{memory.dmem_map.at(memory.metadata_pa).dma_type=Core::PhysicalMemoryType::Free;});unknown();

    // dmem_map coalesces same-type neighbors, so it cannot prove allocation
    // identity. A false enlarged tail must fail its layout, not read at a
    // guessed virtual offset or turn "unknown" into a full pool.
    memory.Build(observed);
    memory.Changed([&]{
        memory.dmem_map.at(0x40100000).memory_type=0;
        memory.SetMaps({memory.Make(observed,0x40000000,0x100000),
                        memory.Make(observed+0x40000000,memory.total_direct_size-0x40100000,0x40100000)});
    });unknown();
    memory.Build(observed);
    memory.Changed([&]{memory.SetMaps({});});unknown();
    const VAddr relocated=0x520a30000ULL;
    memory.Changed([&]{
        memory.metadata_va=relocated;
        memory.SetMaps({memory.Make(relocated,memory.metadata_size,memory.metadata_pa)});
        memory.SetPool(17);
    });check(17);
    memory.Build(observed);
    // A second alias of metadata is legal: the bitmap pointer may name the
    // original alias. Safe backing reads, not guessed pointer rebasing, apply.
    memory.Changed([&]{
        memory.SetMaps({memory.Make(observed,memory.metadata_size,memory.metadata_pa),
                        memory.Make(observed-0x400000,memory.metadata_size,memory.metadata_pa)});
        memory.metadata_va=observed-0x400000;
    });check(0);

    for(const auto invalid:std::vector<std::array<u64,3>>{
        {observed+0x4000,0,1},{observed+0x4000,1,0},{observed+0x4000,1,65},
        {observed+0x4000,0x10001,64},{observed+0x4000,2000,100000},
        {observed+0x4001,1,64},{0,1,64},{(u64{1}<<40)-8,2,64},
        {u64{1}<<40,1,64},{observed+memory.metadata_size+0x10000,1,64}}){
        memory.Build(observed);memory.SetMeta(invalid);unknown();
    }
    memory.Build(observed);
    memory.SetMeta({observed+memory.metadata_size-8,2,64});unknown();

    // Valid bitmap reads on either side of a remap cannot make one sample.
    memory.Build(observed);
    const unsigned query_unlock=memory.mutex.reads+1;
    memory.mutex.after_read=[&](unsigned read){if(read!=query_unlock)return;
        memory.mutex.after_read={};
        memory.Changed([&]{
            std::memcpy(memory.impl.bytes+0x100000,memory.impl.bytes+memory.metadata_pa,memory.metadata_size);
            memory.vma_map.at(observed).phys_areas.at(0).base=0x100000;
        });
    };unknown();

    // Stable mappings do not excuse allocator metadata changing between the
    // initial header and final chunk. The second header read catches this.
    memory.Build(observed);
    const unsigned bitmap_unlock=memory.mutex.reads+3;
    memory.mutex.after_read=[&](unsigned read){if(read!=bitmap_unlock)return;
        memory.mutex.after_read={};auto meta=memory.Meta();--meta[2];memory.SetMeta(meta);
    };unknown();

    // The existing default policy is unchanged: unknown!=0%, 30-report
    // cadence, low pool->mip4, recovery->mip3 then2, unused bank->15.
    memory.Build(observed);memory.SetMeta({0,0,0});
    std::array<u64,256> entries{};
    BachataSotcLod::Mark(258);BachataSotcLod::Collect(&memory,entries);
    assert(entries[2]>>56==2 && entries[1]>>56==15);
    assert(((entries[2]>>32)&0xffffff)==256);
    assert(log_count==1);
    memory.SetPool(0);
    unsigned queries=memory.mutex.reads;
    for(unsigned i=1;i<30;++i){
        BachataSotcLod::Mark(2);BachataSotcLod::Collect(&memory,entries);
        assert(entries[2]>>56==2);
    }
    assert(memory.mutex.reads==queries && log_count==1);
    BachataSotcLod::Mark(2);BachataSotcLod::Collect(&memory,entries);
    assert(entries[2]>>56==4 && log_count==2);
    for(const auto& [free,mip]:std::array<std::pair<unsigned,unsigned>,5>{{{0,4},{10,3},{16,3},{17,2},{7,3}}}){
        memory.SetPool(free);const auto previous=entries[2]>>56;
        for(unsigned i=1;i<30;++i){BachataSotcLod::Mark(2);BachataSotcLod::Collect(&memory,entries);assert(entries[2]>>56==previous);}
        BachataSotcLod::Mark(2);BachataSotcLod::Collect(&memory,entries);assert(entries[2]>>56==mip);++cases;
    }
    assert(log_count==5);
    for(void* p:protected_guest)assert(!munmap(p,Core::MemoryManager::metadata_size));
    std::cout<<"BACHATA_SOTC_LOD_POOL_PASS cases="<<cases<<" protected_guest=2 cadence=30\n";
}
'''


def harness(src):
    header = (src / "core/memory.h").read_text()
    memory = (src / "core/memory.cpp").read_text()
    lod = (src / "video_core/sotc_lod_stats.h").read_text()
    declarations = header[header.index("    struct DirectTailMapping {"):
                          header.index("    bool TryReadBacking(")]
    replacements = {
        "TYPES": header[header.index("enum class MemoryProt"):
                        header.index("class MemoryManager {")],
        "QUERY_DECL": declarations,
        "QUERY": block(memory, "bool MemoryManager::QueryDirectTailMapping("),
        "READ": block(memory, "bool MemoryManager::TryReadBacking("),
        "VISIT": block(memory, "bool VisitPhysicalSpans("),
        "VALID": block(header, "    bool IsValidMapping("),
        "FIND_VMA": block(header, "    VMAHandle FindVMA("),
        "FIND_DMEM": block(header, "    PhysHandle FindDmemArea("),
        "BACKED": block(header, "    bool HasPhysicalBacking("),
        "GENERATION": block(header, "    [[nodiscard]] u64 MappingGeneration()"),
        "TOTAL": block(header, "    u64 GetTotalDirectSize()"),
        "LOD": re.sub(r"^\s*#(?:include|pragma)[^\n]*\n", "", lod, flags=re.M),
    }
    code = PREAMBLE
    for name, value in replacements.items():
        code = code.replace("@" + name + "@", value)
    assert not re.search(r"@\w+@", code)
    return code + MAIN


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--baseline", type=Path,
                        help="Also reproduce the previous fixed-VA policy from this source")
    args = parser.parse_args()
    src = (args.source / "src").resolve()
    code = harness(src)
    mutations = {
        "restore_aot_va": ("const VAddr metadata = mapping.address + MetadataOffset;",
                           "const VAddr metadata = 0x1000000140ULL + 0x50;"),
        "ignore_mapping_generation": ("memory->MappingGeneration() != mapping.generation", "false"),
        "ignore_metadata_reset": ("again != meta ||", "false ||"),
        "ignore_physical_span": ("valid = valid && next == expected;", "(void)next;"),
        "ignore_bitmap_hole": ("count * sizeof(u64))) return -1;", "count * sizeof(u64))) {}"),
        "zero_means_unknown": ("free = std::min(free, pages);", "if(!free) { return -1; }\n    free = std::min(free, pages);"),
        "skip_low_pool_pressure": ("if(free<3)want=2;", "if(free<3)want=0;"),
    }
    with tempfile.TemporaryDirectory(prefix="bachata-sotc-lod-") as directory:
        temp = Path(directory)

        def run(text, name, success=True):
            cpp = temp / (name + ".cpp")
            exe = temp / name
            cpp.write_text(text)
            subprocess.run(["c++", "-std=c++23", "-O1", "-g", "-pthread", "-Wall", "-Wextra",
                            "-Werror", "-fsanitize=undefined", "-fno-sanitize-recover=all",
                            "-I", str(src), str(cpp), "-o", str(exe)], check=True)
            result = subprocess.run([str(exe)], text=True, capture_output=True)
            if success:
                assert result.returncode == 0, (name, result.stdout, result.stderr)
                print(result.stdout, end="")
            else:
                assert result.returncode != 0, (name, "negative control unexpectedly passed")
                assert "Assertion" in result.stderr or "runtime error" in result.stderr, result.stderr
                print("NEGATIVE_REJECTED", name)

        if args.baseline:
            old = (args.baseline / "src/video_core/sotc_lod_stats.h").read_text()
            old = re.sub(r"^\s*#(?:include|pragma)[^\n]*\n", "", old, flags=re.M)
            old = old.replace("namespace BachataSotcLod", "namespace PreviousSotcLod")
            baseline_main = r'''
int main(){
    Core::MemoryManager memory;memory.Build(0x200a30000ULL);memory.SetPool(0);
    std::array<u64,3> actual{};
    assert(memory.TryReadBacking(0x200a30190ULL,actual.data(),sizeof(actual)));
    assert(actual[0]==0x200a34000ULL && actual[1]>0 && actual[2]>0);
    assert(PreviousSotcLod::PoolFreePercent(&memory)==-1);
    std::array<u64,256> old{},fixed{};
    PreviousSotcLod::Mark(2);PreviousSotcLod::Collect(&memory,old);
    BachataSotcLod::Mark(2);BachataSotcLod::Collect(&memory,fixed);
    assert(old[2]>>56==2 && fixed[2]>>56==4);
    std::cout<<"BACHATA_SOTC_LOD_POOL_REPRO old=-1/mip2 relocated=0/mip4\n";
}
'''
            run(code[:code.index("\nint main(){")] + old + baseline_main, "baseline_repro")
        run(code, "positive")
        for name, (before, after) in mutations.items():
            assert code.count(before) == 1, (name, code.count(before))
            run(code.replace(before, after), name, success=False)
    print("BACHATA_SOTC_LOD_POOL_SUITE_PASS negative_controls=" + str(len(mutations)))


if __name__ == "__main__":
    main()
