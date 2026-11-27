#!/usr/bin/env python3
"""SotC donor staging size classes and bounded reuse.
Port eba9ee46c35 as adapted in Android stage_sotc_pc_streaming_051.py.
Keep the existing FEX upload transaction, held leases and GPU timeline checks.
"""
from pathlib import Path

HEADER=r'''#pragma once
#include <algorithm>
#include <bit>
#include <cstdint>
namespace Vulkan::BachataStaging {
constexpr std::uint64_t SizeClass(std::uint64_t bytes,std::uint64_t minimum) {
    const auto value=std::max(bytes,minimum);
    return value <= (std::uint64_t{1}<<63) ? std::bit_ceil(value):value;
}
constexpr std::uint64_t MaxReuse(std::uint64_t size_class,bool held) {
    return held || size_class>(UINT64_MAX/2) ? size_class:size_class*2;
}
constexpr std::uint64_t KeepBytes(std::uint64_t ram) {
    return (ram >= (std::uint64_t{10}<<30) ? 256ULL:128ULL)<<20;
}
}
'''

def apply(root):
    directory=Path(root)/"src/video_core/renderer_vulkan"
    (directory/"bachata_staging_classes.h").write_text(HEADER)
    p=directory/"vk_staging_buffer_pool.cpp"
    s=p.read_text()
    def edit(old,new):
        nonlocal s
        if s.count(old)!=1: raise RuntimeError("SotC staging drift: "+old[:120])
        s=s.replace(old,new,1)
    edit("#include <bit>","#include <bit>\n#include <cstdlib>\n#if defined(__ANDROID__)\n#include <unistd.h>\n#endif\n#include \"common/elf_info.h\"\n#include \"video_core/renderer_vulkan/bachata_staging_classes.h\"")
    edit("} // Anonymous namespace\n\nStagingBufferPool::StagingBufferPool",r'''bool SotcStagingLargePow2() {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    static const bool enabled=[] {
        const char* v=std::getenv("SOTC_STAGING_LARGE_POW2");
        return !v || v[0]!='0';
    }();
    return enabled && (serial=="CUSA08809" || serial=="CUSA08034");
}
u64 SotcStagingKeepBytes() {
    if(!SotcStagingLargePow2())return 0;
    static const u64 bytes=[] {
        u64 ram=0;
#if defined(__ANDROID__)
        const long pages=sysconf(_SC_PHYS_PAGES);
        const long page_size=sysconf(_SC_PAGESIZE);
        if(pages>0 && page_size>0)ram=u64(pages)*u64(page_size);
#endif
        const char* v=std::getenv("SOTC_STAGING_LARGE_KEEP_MB");
        return v && v[0]!='a' ? std::min<u64>(std::strtoull(v,nullptr,10),256)*1_MB
                              : BachataStaging::KeepBytes(ram);
    }();
    return bytes;
}

} // Anonymous namespace

StagingBufferPool::StagingBufferPool''')
    edit("    const u64 max_size = std::max(size + size / 4, RoundAllocationSize(size));",
         r'''    // Deferred readbacks use exact size classes, nondeferred uploads
    // reuse up to twice the class. Outside SotC keep upstream allocation.
    const bool pow2=SotcStagingLargePow2();
    const u64 alloc_size=pow2?BachataStaging::SizeClass(size,LARGE_MIN_GRANULARITY)
                             :RoundAllocationSize(size);
    const u64 max_size=pow2?BachataStaging::MaxReuse(alloc_size,deferred)
                           :std::max(size+size/4,RoundAllocationSize(size));''')
    edit("std::make_unique<VideoCore::Buffer>(instance, 0, RoundAllocationSize(size),",
         "std::make_unique<VideoCore::Buffer>(instance, 0, alloc_size,")
    edit(r'''    std::erase_if(cache, [this](const LargeBuffer& entry) {
        return !entry.held && frame - entry.last_used_frame >= LARGE_IDLE_FRAMES &&
               scheduler.IsFree(entry.tick);
    });''',r'''    // Retain only already-allocated, completed idle storage, bounded per
    // memory type. Never reclaim a held readback or an in-flight GPU buffer.
    u64 keep=SotcStagingKeepBytes();
    if(keep)std::ranges::sort(cache,[](const LargeBuffer& a,const LargeBuffer& b){
        return a.last_used_frame>b.last_used_frame;
    });
    std::erase_if(cache,[this,&keep](const LargeBuffer& entry) {
        if(entry.held || frame-entry.last_used_frame<LARGE_IDLE_FRAMES ||
           !scheduler.IsFree(entry.tick))return false;
        const u64 bytes=entry.buffer->SizeBytes();
        if(bytes<=keep) {keep-=bytes;return false;}
        return true;
    });''')
    p.write_text(s)
    return {"donor":"eba9ee46c35 / Android 051","sizeClasses":"power-of-two readback and upload allocation",
            "idleKeep":"128MiB/256MiB at 10GiB RAM, only existing allocations",
            "preserved":"held and timeline checks; unchanged FEX upload transaction; other titles upstream"}
