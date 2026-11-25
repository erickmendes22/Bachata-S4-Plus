"""Coherent inherited buffer hazard and image-copy footprint contract.

DXVK barrier tree and exact footprint arithmetic from Order c53cd01. The tree
is common to SotC 732cb37 as well. Preserve the existing FEX scheduler proxy,
including command-buffer ownership, and original Android presenter / FPS.
"""
from pathlib import Path
import shutil

def apply(root:Path):
    v=root/"src/video_core/renderer_vulkan"
    def edit(name,a,b,n=1):
        p=v/name;s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"donor runtime contract {name}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    for name in ("vk_barrier_tracker.h","vk_barrier_tracker.cpp","vk_copy_footprint.h"):
        shutil.copyfile(Path(__file__).parent/"inherited_runtime"/name,v/name)
    edit("vk_runtime.h",'#include "common/interval_set.h"','#include "common/interval_set.h"\n#include "video_core/renderer_vulkan/vk_barrier_tracker.h"')
    edit("vk_runtime.h","    BufferBarriers* resource{};",
         """    BarrierTracker donor_barriers;
    struct AccessMemo {
        u64 resource{},start{},end{};
        u32 epoch{},access{};
    };
    std::array<AccessMemo,512> donor_access_memo{};
    u32 donor_access_epoch=1;
    bool donor_range_tracking{};
    BufferBarriers* resource{};""")
    p=v/"vk_runtime.cpp";s=p.read_text()
    for inc in ('#include "common/elf_info.h"','#include "video_core/renderer_vulkan/vk_copy_footprint.h"'):
        if inc not in s:s=inc+"\n"+s
    p.write_text(s)
    edit("vk_runtime.cpp","    blit_helper = std::make_unique<VideoCore::BlitHelper>(instance, scheduler);",
         """    const auto serial=Common::ElfInfo::Instance().GameSerial();
    donor_range_tracking=serial=="CUSA00785"||serial=="CUSA08809"||serial=="CUSA08034";
    blit_helper = std::make_unique<VideoCore::BlitHelper>(instance, scheduler);""")
    edit("vk_runtime.cpp","""    MakeCurrent(handle);
    bool has_access = resource->write_ranges.Overlaps(offset, offset + size);""",
         """    if (!size) return false;
    if (donor_range_tracking) {
        const AddressRange range{reinterpret_cast<u64>(handle),offset,offset+size-1};
        return donor_barriers.FindRange(range,Access::Write) ||
            (check_read_access && donor_barriers.FindRange(range,Access::Read));
    }
    MakeCurrent(handle);
    bool has_access = resource->write_ranges.Overlaps(offset, offset + size);""")
    edit("vk_runtime.cpp","""    MakeCurrent(handle);

    const Interval range = {""",
         """    if (!size) return;
    if (!donor_range_tracking) MakeCurrent(handle);

    const Interval range = {""")
    edit("vk_runtime.cpp","""    if (src_access & WRITE_MASK) {
        resource->write_ranges.Add(range);
    }
    if (src_access & READ_MASK) {
        resource->read_ranges.Add(range);
    }""",
         """    if (donor_range_tracking) {
        AddressRange tracked{reinterpret_cast<u64>(handle),offset,offset+size-1};
        // As in both donors, coarse reads are conservative and writes exact.
        if (!(src_access & WRITE_MASK)) {
            tracked.range_start &= ~u64{4095};
            tracked.range_end |= u64{4095};
        }
        const auto insert=[&](Access access) {
            u64 hash=tracked.resource ^ tracked.range_start*0x9E3779B97F4A7C15ull ^
                     tracked.range_end<<13 ^ u64(access)<<61;
            hash=(hash^hash>>31)*0xFF51AFD7ED558CCDull;
            auto& memo=donor_access_memo[(hash^hash>>29)%donor_access_memo.size()];
            if(memo.epoch==donor_access_epoch && memo.resource==tracked.resource &&
               memo.start==tracked.range_start && memo.end==tracked.range_end &&
               memo.access==u32(access)) return;
            donor_barriers.InsertRange(tracked,access);
            memo={tracked.resource,tracked.range_start,tracked.range_end,
                  donor_access_epoch,u32(access)};
        };
        if(src_access & WRITE_MASK) insert(Access::Write);
        if(src_access & READ_MASK) insert(Access::Read);
    } else {
        if (src_access & WRITE_MASK) resource->write_ranges.Add(range);
        if (src_access & READ_MASK) resource->read_ranges.Add(range);
    }""")
    edit("vk_runtime.cpp","    image_barriers.clear();\n    for (auto& resource : resources) {",
         """    image_barriers.clear();
    donor_barriers.Clear();
    if(++donor_access_epoch==0) {
        donor_access_memo={};
        donor_access_epoch=1;
    }
    for (auto& resource : resources) {""")
    # Bounded hazard hulls preserve every actual copy region. Only reduce the
    # number of conservative lookup/insert calls; retain the existing recorder.
    edit("vk_runtime.cpp","""    bool needs_flush{};
    for (const auto& copy : copies) {
        needs_flush |= IsBufferAccessed(src, copy.srcOffset, copy.size);
        needs_flush |= IsBufferAccessed(dst, copy.dstOffset, copy.size, true);
    }""",
         """    const bool bounded=donor_range_tracking && copies.size()>4;
    u64 src_min=~u64{0},src_max=0,dst_min=~u64{0},dst_max=0;
    bool needs_flush{};
    for(const auto& copy:copies) {
        if(bounded) {
            src_min=std::min<u64>(src_min,copy.srcOffset);
            src_max=std::max<u64>(src_max,copy.srcOffset+copy.size);
            dst_min=std::min<u64>(dst_min,copy.dstOffset);
            dst_max=std::max<u64>(dst_max,copy.dstOffset+copy.size);
        } else {
            needs_flush |= IsBufferAccessed(src,copy.srcOffset,copy.size);
            needs_flush |= IsBufferAccessed(dst,copy.dstOffset,copy.size,true);
        }
    }
    if(bounded)
        needs_flush=IsBufferAccessed(src,src_min,src_max-src_min) ||
                    IsBufferAccessed(dst,dst_min,dst_max-dst_min,true);""")
    edit("vk_runtime.cpp","""    for (const auto& copy : copies) {
        AccessBuffer(src, copy.srcOffset, copy.size, vk::PipelineStageFlagBits2::eCopy,
                     vk::AccessFlagBits2::eTransferRead);""",
         """    if(bounded) {
        AccessBuffer(src,src_min,src_max-src_min,vk::PipelineStageFlagBits2::eCopy,
                     vk::AccessFlagBits2::eTransferRead);
        AccessBuffer(dst,dst_min,dst_max-dst_min,vk::PipelineStageFlagBits2::eCopy,
                     vk::AccessFlagBits2::eTransferWrite);
        return;
    }
    for (const auto& copy : copies) {
        AccessBuffer(src, copy.srcOffset, copy.size, vk::PipelineStageFlagBits2::eCopy,
                     vk::AccessFlagBits2::eTransferRead);""")
    p=v/"vk_runtime.cpp";s=p.read_text()
    a=s.index("static u32 BufferImageCopySize(")
    b=s.index("\nRuntime::Runtime",a)
    s=s[:a]+r'''static u64 BufferImageCopySize(const vk::BufferImageCopy& copy,vk::Format format) {
    const auto bytes=BufferImageCopyByteSize(copy,format);
    ASSERT_MSG(bytes.has_value(),
        "Invalid image-copy footprint format={} extent={}x{}x{} layers={} offset={}",
        vk::to_string(format),copy.imageExtent.width,copy.imageExtent.height,
        copy.imageExtent.depth,copy.imageSubresource.layerCount,copy.bufferOffset);
    return *bytes;
}
'''+s[b:]
    p.write_text(s)
    # Check the actual byte span against the backing allocation before Vulkan
    # recording, with no silent truncation or discarded copies.
    edit("vk_runtime.cpp","""                          std::span<const vk::BufferImageCopy> upload_copies) {
    SetBackingSamples""",
         """                          std::span<const vk::BufferImageCopy> upload_copies) {
    if(donor_range_tracking) for(const auto& copy:upload_copies) {
        const auto bytes=BufferImageCopySize(copy,dst->info.pixel_format);
        ASSERT_MSG(BufferImageCopyFits(copy,bytes,src->SizeBytes()),
                   "Image upload exceeds backing: address={:#x} offset={} bytes={} capacity={}",
                   dst->info.guest_address,copy.bufferOffset,bytes,src->SizeBytes());
    }
    SetBackingSamples""")
    # Build the exact tree as a part of the existing translation unit.
    with p.open("a") as f:f.write('\n#include "video_core/renderer_vulkan/vk_barrier_tracker.cpp"\n')
    return {"hazard_tracker":"actual donor tree + epoch access memo + bounded copy hulls",
            "image_copy":"exact donor 64-bit compressed and aspect-aware footprint",
            "scheduler":"existing FEX recorder unchanged","fps":"unchanged"}
