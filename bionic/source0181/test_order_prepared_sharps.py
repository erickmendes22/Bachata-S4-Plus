"""Compile production stage/lease helpers; exercise publication and live mapping."""
import argparse,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
src=a.source/'src'
code=r'''
#include "video_core/amdgpu/bachata_draw_snapshot.h"
#include <chrono>
#include <optional>
#include <cassert>
using U=std::uint32_t;
struct Sharp { std::array<std::uint64_t,4> w{}; static Sharp Null(bool=false){return {};} auto Address()const{return w[0];}};
struct Resource {
    bool is_written{},is_depth{},is_array{};
    unsigned array_size{};
    bool IsSpecial()const{return false;}
    Sharp GetSharp(const auto& i,bool=true)const{Sharp s;s.w[0]=i.flattened_ud_buf[0];return s;}
};
struct Info {
    unsigned sw_stage{};std::optional<int> params;
    std::span<const U> user_data;std::vector<U> flattened_ud_buf,sharp_tables;
    std::vector<std::uint64_t> srt_guest_sources;
    std::uint64_t pgm_base{};
    std::vector<Resource> buffers,images,samplers;
    BachataPreparedSharps::Stage<Sharp,Sharp,Sharp> order_sharps;
};
int main(){
    Info source;source.flattened_ud_buf={123};source.buffers.resize(1);source.images.resize(1);source.samplers.resize(1);
    BachataDrawPipe::Snapshots<Info,1> packet;
    const Info* p=&source;
    packet.Capture(std::span{&p,1},true);
    auto lease=packet.storage;
    const auto& old=*lease->pointers[0];
    source.flattened_ud_buf[0]=456;
    packet.Capture(std::span{&p,1},false);
    assert(packet.storage!=lease);
    // Even if the background work is not yet ready, the old snapshot is immutable.
    assert(old.order_sharps.GetBuffer(old,old.buffers[0]).Address()==123);
    assert(packet.pointers[0]->order_sharps.GetBuffer(*packet.pointers[0],packet.pointers[0]->buffers[0]).Address()==456);
    for(int n=0;n<200&&!old.order_sharps.ready.load(std::memory_order_acquire);++n)
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    if(!old.order_sharps.ready.load(std::memory_order_acquire)) {
        // Nonblocking submission is allowed to decline, so explicitly prepare the independent snapshot.
        auto isolated=old;isolated.order_sharps.Prepare(isolated);
        assert(isolated.order_sharps.GetImage(isolated,isolated.images[0],[](auto){return false;}).Address()==0);
    } else {
        auto s=old.order_sharps.GetImage(old,old.images[0],[](auto){return true;});
        assert(s.Address()==123);
        assert(old.order_sharps.GetImage(old,old.images[0],[](auto){return false;}).Address()==0);
        assert(old.order_sharps.Hash(old,old.images[0],s)==BachataPreparedSharps::ImageHash(s,old.images[0]));
        assert(!old.order_sharps.Hash(old,old.images[0],Sharp{}));
    }
    packet.Invalidate();
    assert(old.flattened_ud_buf[0]==123);
    Info copy=source;copy.order_sharps.Prepare(copy);
    Info replacement=copy;assert(!replacement.order_sharps.ready.load());
}
'''
with tempfile.TemporaryDirectory() as d:
    d=Path(d);(d/'test.cpp').write_text(code)
    subprocess.run(['c++','-std=c++20','-pthread','-Wall','-Wextra','-Werror','-I',str(src),str(d/'test.cpp'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test')],check=True)
print('ORDER_PREPARED_SHARPS_CONTRACT_OK')
