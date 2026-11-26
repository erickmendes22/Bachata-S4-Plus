#!/usr/bin/env python3
"""Exercise the real DownloadImageMemory consumer of the image alias protocol.

The separate image alias gate executes the alias algorithm and actual copy
recording. Here the GPU copy, staging pool, writer publication and guest write
are controlled boundaries, so ordering and the preservation of asynchronous
downloads are tested using the production consumer rather than a mirrored one.
"""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


def block(text, marker):
    begin = text.index(marker)
    opening = text.index('{', begin)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if not depth:
            return text[begin:end + 1]
    raise AssertionError(marker)


FIXTURE = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <memory>
#include <span>
#include <utility>
#include <vector>
using u8=uint8_t;using u32=uint32_t;using u64=uint64_t;using VAddr=u64;
#define ASSERT(x) assert(x)
namespace vk {
enum class ImageAspectFlagBits {eDepth,eColor};
struct Offset3D {int x{},y{},z{};};
struct Extent3D {u32 width{},height{},depth{};};
struct Subresource {ImageAspectFlagBits aspectMask{};u32 mipLevel{},baseArrayLayer{},layerCount{};};
struct BufferImageCopy {
    u64 bufferOffset{};u32 bufferRowLength{},bufferImageHeight{};
    Subresource imageSubresource;Offset3D imageOffset;Extent3D imageExtent;
};
}
enum ImageFlagBits:u32 {GpuModified=1,Aliased=2};
bool True(u32 value){return value!=0;}bool False(u32 value){return value==0;}
enum class MemoryType {HostCached};
struct Download {
    std::shared_ptr<std::vector<u8>> storage;
    u8* mapped{};u64 offset{};int buffer{1};
    void Invalidate()const{assert(storage&&mapped==storage->data());}
};
struct Pool {
    int requests{},frees{};bool deferred{};Download latest;
    Download Request(u32 size,MemoryType,u32,bool async){
        ++requests;deferred=async;
        auto bytes=std::make_shared<std::vector<u8>>(size);
        latest={bytes,bytes->data(),0,1};return latest;
    }
    void FreeDeferred(const Download& d){assert(d.storage==latest.storage);++frees;}
};
namespace Core {
struct Memory {
    bool accept=true;int writes{};std::vector<u8> output;
    static Memory* Instance(){static Memory memory;return &memory;}
    bool TryWriteBacking(u8*,const u8* data,u32 size){
        ++writes;if(!accept)return false;
        output.assign(data,data+size);return true;
    }
};
}
namespace VideoCore {
using ImageId=u32;
struct Image {
    struct {
        VAddr guest_address=0x100000;u64 guest_size=256;
        u32 pitch=4,num_bits=64;
        vk::Extent3D size{4,8,1};
        struct {u32 layers=1;}resources;
        struct {bool is_depth=false;}props;
    }info;
    u32 flags{};
};
struct Runtime {
    Pool pool;int copies{};
    Pool& GetStagingPool(){return pool;}
    void DownloadImage(Image* image,int buffer,std::span<const vk::BufferImageCopy> regions){
        assert(buffer==1&&regions.size()==1);
        assert(regions[0].imageExtent.width==image->info.size.width);
        assert(regions[0].imageExtent.height==image->info.size.height);
        ++copies;std::fill(pool.latest.storage->begin(),pool.latest.storage->end(),u8{17});
    }
};
struct Scheduler {
    int finishes{};std::vector<std::function<void()>> pending;
    void Finish(){++finishes;}
    void DeferPriorityOperation(std::function<void()> work){pending.push_back(std::move(work));}
    void Complete(){auto work=std::move(pending);pending.clear();for(auto& fn:work)fn();}
};
struct TextureCache {
    std::array<Image,1> slot_images;Runtime runtime;Scheduler scheduler;
    bool aliases=true,pending_writer=false;int resolves{},syncs{},notes{};
    TextureCache(){*Core::Memory::Instance()=Core::Memory{};}
    bool ImageAliasesEnabled()const{return aliases;}
    void ResolveImageReadbacks(VAddr,u64,bool on_gpu){assert(on_gpu);++resolves;}
    void SynchronizeAliasDownload(ImageId id){
        ++syncs;
        // Boundary: the independently tested alias writer can make this
        // previously CPU-only backing GPU-modified before eligibility checks.
        if(aliases&&pending_writer&&(slot_images[id].flags&ImageFlagBits::Aliased))
            slot_images[id].flags|=ImageFlagBits::GpuModified;
    }
    void NoteAliasWriteback(const Image&){++notes;}
    void DownloadImageMemory(ImageId image_id,bool sync);
};
@METHOD@
}
using namespace VideoCore;
void PendingWriter(){
    TextureCache c;c.slot_images[0].flags=ImageFlagBits::Aliased;c.pending_writer=true;
    c.DownloadImageMemory(0,false);
    assert(c.resolves==1&&c.syncs==1&&c.runtime.copies==1);
    assert(c.scheduler.finishes==1&&!c.runtime.pool.deferred&&c.scheduler.pending.empty());
    assert(c.notes==1&&Core::Memory::Instance()->writes==1);
    assert(Core::Memory::Instance()->output==std::vector<u8>(256,17));
}
void Unmodified(){
    TextureCache c;c.slot_images[0].flags=ImageFlagBits::Aliased;
    c.DownloadImageMemory(0,false);
    assert(c.syncs==1&&c.runtime.pool.requests==0&&c.scheduler.finishes==0);
    assert(c.notes==0&&Core::Memory::Instance()->writes==0);
}
void AsyncPolicy(bool title,bool aliased){
    TextureCache c;c.aliases=title;
    c.slot_images[0].flags=ImageFlagBits::GpuModified|(aliased?ImageFlagBits::Aliased:0u);
    c.DownloadImageMemory(0,false);
    assert(c.runtime.pool.deferred&&c.scheduler.finishes==0&&c.scheduler.pending.size()==1);
    assert(Core::Memory::Instance()->writes==0&&c.notes==0);
    c.scheduler.Complete();
    assert(Core::Memory::Instance()->output==std::vector<u8>(256,17));
    assert(c.runtime.pool.frees==1&&c.notes==0);
}
void WriteFailure(){
    TextureCache c;Core::Memory::Instance()->accept=false;
    c.slot_images[0].flags=ImageFlagBits::Aliased|ImageFlagBits::GpuModified;
    c.DownloadImageMemory(0,false);
    assert(c.scheduler.finishes==1&&Core::Memory::Instance()->writes==1);
    assert(c.notes==0&&Core::Memory::Instance()->output.empty());
}
void ExplicitSync(){
    TextureCache c;c.aliases=false;c.slot_images[0].flags=ImageFlagBits::GpuModified;
    c.DownloadImageMemory(0,true);
    assert(c.scheduler.finishes==1&&!c.runtime.pool.deferred&&c.scheduler.pending.empty());
    assert(Core::Memory::Instance()->output==std::vector<u8>(256,17));
}
int main(){
    PendingWriter();Unmodified();AsyncPolicy(true,false);AsyncPolicy(false,true);
    AsyncPolicy(false,false);WriteFailure();ExplicitSync();
    std::cout<<"BACHATA_ORDER_ALIAS_DOWNLOAD_PASS cases=7\n";
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    text = (args.source / 'src/video_core/texture_cache/texture_cache.cpp').read_text()
    method = block(text, 'void TextureCache::DownloadImageMemory(')
    compiler = shlex.split(os.environ.get('CXX', 'c++')) + [
        '-std=c++23', '-O1', '-Wall', '-Wextra', '-Werror',
        '-fsanitize=undefined', '-fno-sanitize-recover=all']
    variants = {'positive': method}
    needle = '    SynchronizeAliasDownload(image_id);\n'
    assert method.count(needle) == 1
    variants['missing_writer_sync'] = method.replace(needle, '', 1)
    needle = 'sync |= ImageAliasesEnabled() && True(image.flags & ImageFlagBits::Aliased);'
    assert method.count(needle) == 1
    variants['global_synchronous_gc'] = method.replace(needle, 'sync |= ImageAliasesEnabled();', 1)
    needle = '            NoteAliasWriteback(image);'
    assert method.count(needle) == 1
    variants['missing_writeback_publication'] = method.replace(needle, '', 1)
    needle = 'download.mapped, download_size)) {'
    assert method.count(needle) == 1
    variants['failed_writeback_published'] = method.replace(
        needle, 'download.mapped, download_size) || true) {', 1)
    with tempfile.TemporaryDirectory(prefix='bachata-alias-download-') as directory:
        root = Path(directory)
        for name, body in variants.items():
            source = root / (name + '.cpp')
            binary = root / name
            source.write_text(FIXTURE.replace('@METHOD@', body))
            subprocess.run([*compiler, str(source), '-o', str(binary)], check=True)
            result = subprocess.run([str(binary)], text=True, capture_output=True, timeout=10)
            if name == 'positive':
                assert result.returncode == 0, result.stdout + result.stderr
                print(result.stdout.strip(), flush=True)
            else:
                assert result.returncode != 0, 'Accepted negative: ' + name
                print('NEGATIVE_REJECTED', name, flush=True)
    print('BACHATA_ORDER_ALIAS_DOWNLOAD_SUITE_PASS negatives=4', flush=True)


if __name__ == '__main__':
    main()
