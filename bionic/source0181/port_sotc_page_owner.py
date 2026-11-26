"""SotC PC T38/Android 0.72 page-owner protocol, adapted to native FEX.

Reference: AjncSystem/ShadowOfTheColossus-PC@732cb37d3470 src/runtime_memory.c
and src/probe.c; Android runtime_memory.c + probe.c. Guest VirtualQuery at
the verified pool-release call site must not report committed old aliases
whose physical pages now belong to a different live virtual mapping.
"""
from pathlib import Path

HEADER = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <algorithm>
#include <cstdint>
#include <vector>
#include <limits>

namespace BachataSotcOwner {
using U64 = std::uint64_t;
constexpr U64 Page=65536;
struct Span { U64 end{}; bool stale{}; };
class Owners {
public:
    // Called only with the native MemoryManager writer lock held, after
    // the real guest VA mapping succeeds. Partial pages erase uncertain
    // ownership rather than inventing a complete 64 KiB page association.
    void Note(U64 physical,U64 address,U64 size,U64 capacity) {
        if (!size || physical>=capacity || size>capacity-physical ||
            size>std::numeric_limits<U64>::max()-address) return;
        if (pages.size()!=capacity/Page) pages.resize(capacity/Page);
        const U64 end=physical+size;
        for (U64 p=physical/Page; p<pages.size() && p<=(end-1)/Page; ++p) {
            const U64 base=p*Page;
            if (base>=physical && Page<=end-base) {
                const U64 mapped=address+base-physical;
                pages[p]=mapped%Page==0?mapped:0;
            } else {
                pages[p]=0;
            }
        }
    }
    U64 Last(U64 physical) const {
        const U64 index=physical/Page;
        return index<pages.size()?pages[index]:0;
    }
    bool Empty() const {return pages.empty();}
    // Stop at a change of ownership. A live prefix followed by stale
    // pages must not be reported as one committed span either.
    template<class IsLive>
    Span Run(U64 physical,U64 address,U64 bytes,IsLive&& is_live) const {
        if (!bytes || bytes>std::numeric_limits<U64>::max()-address ||
            bytes>std::numeric_limits<U64>::max()-physical ||
            physical%Page || address%Page || bytes%Page) return {};
        const auto stale=[&](U64 offset) {
            const U64 owner=Last(physical+offset);
            return owner && owner!=address+offset && is_live(owner,physical+offset);
        };
        const bool first=stale(0);
        U64 offset=Page;
        while (offset<bytes && stale(offset)==first) offset+=Page;
        return {address+offset,first};
    }
private:
    std::vector<U64> pages;
};
} // namespace BachataSotcOwner
'''

def one(s,old,new,label):
    if s.count(old)!=1: raise RuntimeError("SotC owner anchor drift "+label+": "+str(s.count(old)))
    return s.replace(old,new,1)

def edit(p,old,new,label):
    p.write_text(one(p.read_text(),old,new,label))

def apply(root:Path):
    root=Path(root)/"src"
    (root/"core/bachata_sotc_page_owner.h").write_text(HEADER)
    h=root/"core/memory.h"
    p=root/"core/memory.cpp"
    k=root/"core/libraries/kernel/memory.cpp"
    a=root/"core/guest_cpu/hle_call_adapter.h"
    b=root/"core/guest_cpu/fex_hle_bridge.cpp"
    edit(h,'#include "core/memory_map_generation.h"',
           '#include "core/memory_map_generation.h"\n#include "core/bachata_sotc_page_owner.h"', "owner table header")
    edit(h,"    VMAMap vma_map;","    VMAMap vma_map;\n    BachataSotcOwner::Owners sotc_page_owners;","per-memory-manager lifetime")
    edit(h,"s32 VirtualQuery(VAddr addr, s32 flags, ::Libraries::Kernel::OrbisVirtualQueryInfo* info);",
           "s32 VirtualQuery(VAddr addr, s32 flags, ::Libraries::Kernel::OrbisVirtualQueryInfo* info,\n                     bool sotc_release=false);","query caller contract")
    edit(a,"[[nodiscard]] bool RevokeHostRange(const void* pointer);",
           "[[nodiscard]] bool RevokeHostRange(const void* pointer);\n"
           "[[nodiscard]] bool ReadActiveGuestHleMemory(std::uintptr_t address, void* out, std::size_t bytes);\n"
           "[[nodiscard]] std::uintptr_t ActiveGuestHleReturnAddress();","guest return address API")
    edit(b,"namespace Core::GuestCpu {\n",r'''namespace Core::GuestCpu {

bool ReadActiveGuestHleMemory(std::uintptr_t address, void* out, std::size_t bytes) {
    const auto* frame=ActiveHleCallFrame;
    if(!frame || !out || !address || !bytes || address>UINTPTR_MAX-bytes ||
       !frame->validate_range ||
       !frame->validate_range(frame->validate_context,address,bytes,false)) return false;
    std::memcpy(out,reinterpret_cast<const void*>(address),bytes);
    return true;
}
std::uintptr_t ActiveGuestHleReturnAddress() {
    std::uintptr_t rip{};
    if(ActiveHleCallFrame)
        (void)ReadActiveGuestHleMemory(ActiveHleCallFrame->rsp,&rip,sizeof(rip));
    return rip;
}
''',"validated guest stack, not host LR")
    s=b.read_text()
    if '#include <cstring>' not in s: b.write_text('#include <cstring>\n'+s)
    s=p.read_text()
    if '#include <atomic>' not in s: s='#include <atomic>\n'+s
    if '#include "common/elf_info.h"' not in s: s='#include "common/elf_info.h"\n'+s
    # Exact map mutation boundary: VMA/physical backing already installed;
    # record ownership before releasing the native MemoryManager writer lock.
    begin=s.index("s32 MemoryManager::MapMemory(")
    end=s.index("\ns32 MemoryManager::MapFile(",begin)
    body=s[begin:end]
    body=one(body,"        mapping_mutation.Finish();",r'''        if (type==VMAType::Direct) {
            const auto serial=Common::ElfInfo::Instance().GameSerial();
            if(serial=="CUSA08809"||serial=="CUSA08034")
                sotc_page_owners.Note(phys_addr,mapped_addr,size,total_direct_size);
        }
        mapping_mutation.Finish();''',"successful direct map")
    s=s[:begin]+body+s[end:]
    s=one(s,"s32 MemoryManager::VirtualQuery(VAddr addr, s32 flags,\n                                ::Libraries::Kernel::OrbisVirtualQueryInfo* info) {",
           "s32 MemoryManager::VirtualQuery(VAddr addr, s32 flags,\n                                ::Libraries::Kernel::OrbisVirtualQueryInfo* info, bool sotc_release) {","native query signature")
    start=s.index("s32 MemoryManager::VirtualQuery(")
    end=s.index("\ns32 MemoryManager::DirectMemoryQuery(",start)
    body=s[start:end]
    body=one(body,"    if (vma.type == VMAType::Reserved || vma.type == VMAType::PoolReserved) {",r'''    // BACHATA_SOTC_POOL_OWNER: only the exact guest pool-release query
    // receives a split/obsolete commitment result. The FEX VMA map itself
    // and all ordinary VirtualQuery callers retain their original contract.
    if (sotc_release && vma.type==VMAType::Direct && addr>=vma.base &&
        addr-vma.base<vma.size && !sotc_page_owners.Empty()) {
        const auto offset=addr-vma.base;
        auto part=vma.phys_areas.upper_bound(offset);
        if(part!=vma.phys_areas.begin()) {
            --part;
            if(offset>=part->first && offset-part->first<part->second.size) {
                const u64 in_area=offset-part->first;
                const PAddr physical=part->second.base+in_area;
                const u64 bytes=std::min<u64>(vma.size-offset,part->second.size-in_area);
                // A recycled table entry is not sufficient: the newer VA
                // must still map the same whole physical page under this lock.
                const auto live=[&](VAddr owner,PAddr phys) {
                    if(!IsValidMapping(owner)) return false;
                    const auto& other=FindVMA(owner)->second;
                    if(other.type!=VMAType::Direct || owner<other.base ||
                       owner-other.base>=other.size ||
                       BachataSotcOwner::Page>other.size-(owner-other.base)) return false;
                    const u64 off=owner-other.base;
                    auto found=other.phys_areas.upper_bound(off);
                    if(found==other.phys_areas.begin()) return false;
                    --found;
                    if(off<found->first || off-found->first>=found->second.size) return false;
                    const u64 delta=off-found->first;
                    return BachataSotcOwner::Page<=found->second.size-delta &&
                           found->second.base+delta==phys;
                };
                const auto run=sotc_page_owners.Run(physical,addr,bytes,live);
                if(run.end && (run.stale || run.end<info->end || addr!=info->start)) {
                    info->start=addr;
                    info->end=run.end;
                    info->offset=physical;
                    info->memory_type=part->second.memory_type;
                    if(run.stale) {
                        info->is_committed=0;
                        static std::atomic<u64> skips{},pages{};
                        const u64 count=skips.fetch_add(1,std::memory_order_relaxed)+1;
                        const u64 n=(run.end-addr)/BachataSotcOwner::Page;
                        const u64 total=pages.fetch_add(n,std::memory_order_relaxed)+n;
                        if(count<=20 || !(count&(count-1)))
                            LOG_INFO(Kernel_Vmm,"BACHATA_SOTC_POOL_OWNER skipped={} total={} addr={:#x} phys={:#x}",n,total,addr,physical);
                    }
                }
            }
        }
    }
    if (vma.type == VMAType::Reserved || vma.type == VMAType::PoolReserved) {''',"pool release query result")
    p.write_text(s[:start]+body+s[end:])
    s=k.read_text()
    inc='#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n#include "core/guest_cpu/hle_call_adapter.h"\n#include "core/module.h"\n#include <atomic>\n#endif\n'
    s=one(s,'#include "core/linker.h"','#include "core/linker.h"\n'+inc,"FEX call-site validation headers")
    s=one(s,"    return memory->VirtualQuery(std::bit_cast<VAddr>(addr), flags, info);",r'''    bool sotc_release=false;
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if((serial=="CUSA08809"||serial=="CUSA08034") && info &&
       infoSize==sizeof(OrbisVirtualQueryInfo)) {
        const auto rip=Core::GuestCpu::ActiveGuestHleReturnAddress();
        const auto* main=Common::Singleton<Core::Linker>::Instance()->GetModule(0);
        constexpr VAddr release_rva=0x1ac82;
        if(main && rip>=main->GetBaseAddress() &&
           rip-main->GetBaseAddress()==release_rva) {
            u8 opcode{};
            sotc_release=Core::GuestCpu::ReadActiveGuestHleMemory(rip-5,&opcode,sizeof(opcode)) &&
                         opcode==0xe8;
            static std::atomic_bool logged{};
            if(sotc_release && !logged.exchange(true,std::memory_order_relaxed))
                LOG_INFO(Kernel_Vmm,"BACHATA_SOTC_POOL_OWNER_SITE verified=true rva={:#x}",release_rva);
        }
    }
#endif
    return memory->VirtualQuery(std::bit_cast<VAddr>(addr), flags, info,sotc_release);''',"donor's exact x86 call site")
    k.write_text(s)
    return {"donor":"PC T38 732cb37 + Android runtime 0.72","guard":"guest RIP at verified release site; no host LR",
            "ownership":"last complete 64 KiB physical mapping, validated live against native FEX VMA",
            "query":"split live/stale runs; stale not committed; normal calls unchanged"}
