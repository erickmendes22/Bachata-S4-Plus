"""Parallelize verified physical alias uploads without moving guest faults to workers."""
from pathlib import Path
import shutil

def apply(root:Path):
    def edit(rel,old,new):
        p=root/rel
        s=p.read_text()
        if s.count(old)!=1: raise RuntimeError("parallel physical upload drift "+rel+": "+old[:100])
        p.write_text(s.replace(old,new,1))
    shutil.copyfile(Path(__file__).with_name("parallel_physical_upload.h"),root/"src/common/parallel_physical_upload.h")
    h="src/core/memory.h"
    c="src/core/memory.cpp"
    bc="src/video_core/buffer_cache/buffer_cache.cpp"
    edit(h,'    bool TryReadBacking(VAddr address, void* data, u64 size);',
r'''    struct PhysicalUploadSpan { VAddr address; u8* destination; u64 size; };
    // Returns false without writing destination if any source is not physically backed.
    bool CopyPhysicalUploadBatch(std::span<const PhysicalUploadSpan> spans);
    bool TryReadBacking(VAddr address, void* data, u64 size);''')
    edit(h,'#pragma once','#pragma once\n#include <span>')
    edit(c,'#include "common/bachata_compat_profile.h"','#include "common/bachata_compat_profile.h"\n#include "common/parallel_physical_upload.h"')
    edit(c,'void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {',
r'''// BACHATA_PHYSICAL_UPLOAD_WORKER: keep the VMM read lock for the entire
// batch. Workers only see the unprotected memfd alias, never guest VA.
// All spans must validate before either lane touches staging memory.
bool MemoryManager::CopyPhysicalUploadBatch(std::span<const PhysicalUploadSpan> spans) {
    if (BachataCompat::Sotc608()) return false;
    std::shared_lock lock{mutex};
    std::vector<BachataUpload::Copy> work;
    u64 total=0;
    constexpr u64 chunk=1_MB;
    for (const auto& span:spans) {
        VAddr address=span.address;
        u64 size=span.size;
        u8* dst=span.destination;
        if(size>UINT64_MAX-address || size>UINT64_MAX-total) return false;
        total+=size;
        while(size) {
            if(!IsValidMapping(address)) return false;
            const auto& vma=FindVMA(address)->second;
            if(!HasPhysicalBacking(vma)) return false;
            const u64 bytes=std::min<u64>(size,vma.base+vma.size-address);
            if(!bytes) return false;
            if(!VisitPhysicalSpans(vma,address,bytes,[&](PAddr p,u64 n) {
                const auto* src=impl.BackingBase()+p;
                while(n) {
                    const u64 part=std::min(n,chunk);
                    work.push_back({src,dst,static_cast<size_t>(part)});
                    src+=part;dst+=part;n-=part;
                }
            })) return false;
            address+=bytes;size-=bytes;
        }
    }
    if(total<2_MB||work.size()<2)return false;
    // No Vulkan objects, guest readbacks or VMM lock acquisitions on worker.
    // Wait before flushing noncoherent memory or recording the transfer.
    static BachataUpload::Pool pool;
    pool.CopyBatch(work);
    return true;
}

void MemoryManager::CopySparseMemory(VAddr address, u8* dest, u64 size) {''')
    edit(bc,'#include "common/bachata_compat_profile.h"','#include "common/bachata_compat_profile.h"\n#include <vector>')
    edit(bc,'''        for (auto& copy : copies) {
            memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);
            copy.srcOffset += staging.offset;''',
r'''        bool parallel=false;
        if (!BachataCompat::Sotc608() && total_size_bytes>=2_MB) {
            std::vector<Core::MemoryManager::PhysicalUploadSpan> spans;
            spans.reserve(copies.size());
            for(const auto& copy:copies)
                spans.push_back({copy.dstOffset,staging.mapped+copy.srcOffset,copy.size});
            parallel=memory->CopyPhysicalUploadBatch(spans);
        }
        for (auto& copy : copies) {
            if(!parallel)
                memory->CopySparseMemory(copy.dstOffset, staging.mapped + copy.srcOffset, copy.size);
            copy.srcOffset += staging.offset;''')
    return {"parallel":"one persistent worker + caller; full physical span validation; no guest faults",
            "fence":"join before Vulkan flush and recording; SotC scalar path preserved"}
