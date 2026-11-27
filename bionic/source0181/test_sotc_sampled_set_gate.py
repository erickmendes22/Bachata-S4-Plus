#!/usr/bin/env python3
"""Compile the real stage-set validation method; verify atomic failure and lifetime."""
import argparse
from pathlib import Path
import subprocess
import tempfile

FIXTURE=r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <map>
#include <mutex>
#include <ranges>
#include <span>
#include <vector>
#include <iostream>
#ifndef __cpp_lib_ranges_contains
namespace std::ranges {
template<input_range R,class T>bool contains(R&& r,const T& v){return find(r,v)!=end(r);}
}
#endif
using u32=uint32_t;using u64=uint64_t;using VAddr=u64;
using ImageId=u32;using ImageViewId=u32;
namespace vk {using Image=u64;using ImageView=u64;}
struct ImageViewInfo {
    struct {struct {u32 level=0,layer=0;}base;struct{u32 levels=1,layers=1;}extent;}range;
    u32 format=1;
    bool operator==(const ImageViewInfo& x) const {return range.base.level==x.range.base.level && range.base.layer==x.range.base.layer && range.extent.levels==x.range.extent.levels && range.extent.layers==x.range.extent.layers && format==x.format;}
};
struct ImageView {ImageViewInfo info{};vk::ImageView handle=100;vk::ImageView* image_view=&handle;};
namespace ImageFlagBits {constexpr u32 Registered=1,Dirty=2;}
bool True(u32 v){return v!=0;}bool False(u32 v){return v==0;}
struct Image {
    u32 flags=ImageFlagBits::Registered;
    struct {bool needs_rebind{},is_target{},force_general{},is_bound{};}binding;
    struct {bool texture{};}usage;
    ImageId depth_id{};
    struct Info {struct {bool is_depth{};}props;u32 sotc_first_mip{},num_samples=1;VAddr guest_address=0x10000;u64 guest_size=4096;struct {u32 levels=2,layers=2;}resources;}info;
    VAddr track_addr=0x10000,track_addr_end=0x11000;
    struct Backing {u32 num_samples=1;std::vector<ImageViewId> image_view_ids{1};vk::Image handle=500;}storage;
    Backing* backing=&storage;
    u64 image_uid=12,tick_accessed_last=0;
    vk::Image GetImage()const{return backing->handle;}
};
template<class T>struct Slots {std::map<u32,T> values;bool IsAllocated(u32 id)const{return values.contains(id);}T& operator[](u32 id){return values.at(id);}};
std::atomic<u64> sotc_mip_tail_gpu_epoch{1};
struct TextureCache {
    @ENTRY@
    std::mutex mutex;Slots<Image> slot_images;Slots<ImageView> slot_image_views;
    u64 registry=3;unsigned touches=0;struct {u64 CurrentTick(){return 17;}}scheduler;
    u64 TargetRegistryEpoch()const{return registry;}
    void TouchImage(const Image&){++touches;}
    bool CheckSotcSampledSet(std::span<SotcSampledSetEntry>,u64,u64,bool);
};
@METHOD@
int main(){
    for(unsigned fault=0;fault<15;++fault){
        TextureCache c;
        auto& a=c.slot_images.values.try_emplace(1).first->second;
        auto& b=c.slot_images.values.try_emplace(2).first->second;
        auto& av=c.slot_image_views.values.try_emplace(1).first->second;
        auto& bv=c.slot_image_views.values.try_emplace(2).first->second;
        b.info.guest_address=0x20000;b.track_addr=0x20000;b.track_addr_end=0x21000;
        b.storage.image_view_ids={2};b.storage.handle=600;b.image_uid=13;bv.handle=200;
        std::array<TextureCache::SotcSampledSetEntry,2> entries{};
        entries[0].id=1;entries[0].guest_address=a.info.guest_address;entries[0].handle=av.handle;
        entries[1].id=2;entries[1].guest_address=b.info.guest_address;entries[1].handle=bv.handle;
        sotc_mip_tail_gpu_epoch=1;
        assert(c.CheckSotcSampledSet(entries,3,1,true));assert(c.touches==0);
        switch(fault){
        case 1:++c.registry;break;case 2:++sotc_mip_tail_gpu_epoch;break;
        case 3:b.flags|=ImageFlagBits::Dirty;break;case 4:b.binding.needs_rebind=true;break;
        case 5:b.binding.is_target=true;break;case 6:b.binding.force_general=true;break;
        case 7:b.binding.is_bound=true;break;case 8:b.depth_id=1;break;
        case 9:b.info.sotc_first_mip=1;break;case 10:b.track_addr_end--;break;
        case 11:b.image_uid++;break;case 12:b.storage.handle++;break;
        case 13:b.storage.image_view_ids.clear();break;case 14:bv.handle++;break;
        }
        assert(c.CheckSotcSampledSet(entries,3,1,false)==(fault==0));
        assert(c.touches==(fault?0u:2u));assert(a.binding.is_bound==(fault==0));
        assert(a.usage.texture==(fault==0));
        if(!fault)assert(a.tick_accessed_last==17 && b.tick_accessed_last==17);
    }
    std::cout<<"BACHATA_SOTC_STAGE_SET_PASS cases=15\n";
}
'''

def block(s, marker):
    a=s.index(marker);b=s.index('{',a);d=1;i=b+1
    while d:
        d+=(s[i]=='{')-(s[i]=='}');i+=1
    return s[a:i]

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);root=p.parse_args().source/'src/video_core/texture_cache'
    h=(root/'texture_cache.h').read_text();cpp=(root/'texture_cache.cpp').read_text()
    source=FIXTURE.replace('@ENTRY@',block(h,'    struct SotcSampledSetEntry {')+';').replace('@METHOD@',block(cpp,'bool TextureCache::CheckSotcSampledSet('))
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/'test.cpp';exe=Path(d)/'test';f.write_text(source)
        subprocess.run(['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(f),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
if __name__=='__main__':main()
