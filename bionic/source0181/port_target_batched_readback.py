"""Batch linear image downloads using the donor's synchronous batch path.

Keep the guest-memory ownership rules and publication order of the FEX core.
All staging allocations stay held until the single GPU fence completes; no
deferred write to guest memory is introduced by this adaptation.
"""
from pathlib import Path

def apply(root: Path):
    p=root/"src/video_core/texture_cache/texture_cache.cpp"
    s=p.read_text()
    old='''void TextureCache::ProcessDownloadImages() {
'''
    if s.count(old)!=1: raise RuntimeError("readback function drift")
    end=s.index("\n}\n",s.index(old))+3
    begin=s.index(old)
    original=s[begin:end]
    body='''void TextureCache::ProcessDownloadImages() {
    if (!readback_linear_images) return;
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const bool batch=serial=="CUSA00785"||serial=="CUSA08809"||serial=="CUSA08034";
    std::unique_lock lk{download_images_mutex};
    if(!batch) {
        for (const ImageId image_id : download_images) DownloadImageMemory(image_id,true);
        download_images.clear();
        return;
    }
    // Equivalent to the donor RecordImageDownload + single Finish path.
    // Retain allocations across Finish until their guest bytes are published.
    struct Copy {
        VAddr address;
        u32 size;
        Vulkan::StagingBufferRef staging;
    };
    std::vector<Copy> pending;
    pending.reserve(download_images.size());
    u64 pending_bytes=0;
    const auto flush=[&] {
        if(pending.empty()) return;
        scheduler.Finish();
        for(const auto& copy:pending) {
            copy.staging.Invalidate();
            Core::Memory::Instance()->TryWriteBacking(
                std::bit_cast<u8*>(copy.address), copy.staging.mapped, copy.size);
            runtime.GetStagingPool().FreeDeferred(copy.staging);
        }
        pending.clear();
        pending_bytes=0;
    };
    for(const ImageId image_id:download_images) {
        auto& image=slot_images[image_id];
        if(!image.SafeToDownload()) continue;
        const u64 bytes=u64{image.info.pitch}*image.info.size.height*image.info.size.depth*
            image.info.resources.layers*(image.info.num_bits/8);
        if(!bytes||bytes>image.info.guest_size||bytes>UINT32_MAX) continue;
        constexpr u64 batch_budget=32ull*1024*1024;
        if(pending_bytes+bytes>batch_budget) flush();
        const auto staging=runtime.GetStagingPool().Request(
            static_cast<u32>(bytes),MemoryType::HostCached,16,true);
        const vk::BufferImageCopy region={
            .bufferOffset=staging.offset,
            .bufferRowLength=image.info.pitch,
            .bufferImageHeight=image.info.size.height,
            .imageSubresource={
                .aspectMask=image.info.props.is_depth?vk::ImageAspectFlagBits::eDepth:vk::ImageAspectFlagBits::eColor,
                .mipLevel=0,.baseArrayLayer=0,.layerCount=image.info.resources.layers,
            },
            .imageOffset={0,0,0},
            .imageExtent={image.info.size.width,image.info.size.height,image.info.size.depth},
        };
        runtime.DownloadImage(&image,staging.buffer,std::span{&region,1});
        pending.push_back({image.info.guest_address,static_cast<u32>(bytes),staging});
        pending_bytes+=bytes;
    }
    download_images.clear();
    flush();
}'''
    s=s[:begin]+body+s[end:]
    if '#include "common/elf_info.h"' not in s:
        pos=s.index('#include "')
        s=s[:pos]+'#include "common/elf_info.h"\n'+s[pos:]
    p.write_text(s)
    return {"scope":"target serials","readback":"batched synchronous donor path","budget_bytes":33554432,
            "ownership":"held staging, publish after fence; skip CPU-dirty image"}
