#!/usr/bin/env python3
"""Exercise the applied image alias family, with GPU execution at the boundary.

FindImage, ResolveOverlap, ImageInfo, registration, refresh, invalidation,
authority, deferred copy recording and retirement are extracted from production.
The GPU image storage, page protection, Vulkan submission and hash implementation
are fixtures; this is a coherence/ownership test, not a gameplay measurement.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from test_order_readconst_pool import block


PROGRAM = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cassert>
#include <chrono>
#include <compare>
#include <condition_variable>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <ranges>
#include <queue>
#include <semaphore>
#include <set>
#include <span>
#include <string>
#include <thread>
#include <tuple>
#include <utility>
#include <vector>
#include "common/types.h"
#define ASSERT_MSG(x,...) assert(x)
#define ASSERT(x) assert(x)
template<class... A>void IgnoreLog(A&&...){}
constexpr int Render_Vulkan=0,Render=1;
#define LOG_ERROR IgnoreLog
#define LOG_WARNING IgnoreLog
#define LOG_INFO IgnoreLog
#define UNREACHABLE_MSG(...) std::abort()
#define RENDERER_TRACE ((void)0)
#define TRACE_HINT(...) ((void)0)
namespace boost::container {template<class T,size_t N>using small_vector=std::vector<T>;}
namespace Common {
template<class R>using UniqueFunction=std::function<R()>;
template<class T,class U> auto AlignUp(T a,U b){return (a+b-1)/b*b;}
template<class T,class U> auto DivCeil(T a,U b){return (a+b-1)/b;}
struct ElfInfo {
 std::string serial="CUSA00785";
 static ElfInfo& Instance(){static ElfInfo i;return i;}
 std::string_view GameSerial()const{return serial;}
};
@SLOTID@;
}
struct GpuImage {u32 width{},height{},layers{};std::vector<u64> pixels;};
namespace vk {
enum class Format{eUndefined,eR16G16B16A16Sfloat,eR16G16B16A16Uint,eR8Unorm};
inline std::string to_string(Format f){return std::to_string(int(f));}
using Image=GpuImage*;
enum class ImageLayout{eTransferSrcOptimal,eTransferDstOptimal};
enum class PipelineStageFlagBits2{eCopy};
enum class AccessFlagBits2{eTransferRead,eTransferWrite};
struct ImageAspectFlagBits {static constexpr u32 eColor=1,eDepth=2,eStencil=4;};
struct Extent3D{u32 width{},height{},depth{};};
struct Offset3D{int x{},y{},z{};};
struct Subresource{u32 aspectMask{},mipLevel{},baseArrayLayer{},layerCount{};};
struct ImageCopy{Subresource srcSubresource;Offset3D srcOffset;Subresource dstSubresource;Offset3D dstOffset;Extent3D extent;};
struct BufferImageCopy{u64 bufferOffset{};u32 bufferRowLength{},bufferImageHeight{};Subresource imageSubresource;Offset3D imageOffset;Extent3D imageExtent;};
struct CommandBuffer {
 void copyImage(Image src,ImageLayout,Image dst,ImageLayout,const ImageCopy& copy) {
   assert(src&&dst&&src!=dst);
   for(u32 l=0;l<copy.srcSubresource.layerCount;++l)
    for(u32 y=0;y<copy.extent.height;++y)for(u32 x=0;x<copy.extent.width;++x)
     dst->pixels[(l*dst->height+y)*dst->width+x]=src->pixels[(l*src->height+y)*src->width+x];
 }
};
}
namespace AmdGpu {
struct ColorBuffer;struct DepthBuffer;struct Image;struct CbDbExtent{};
enum class ImageType:u64{Color2D,Color3D};
enum class TileMode{DisplayLinearAligned,Tiled};enum class ArrayMode{ArrayLinearAligned,Tiled};
struct Liverpool {
 inline static thread_local bool draw_thread=false;
 std::thread::id gpu_id=std::this_thread::get_id();
 std::mutex submit_mutex;std::condition_variable submit_cv;
 std::queue<std::function<void()>>command_queue;std::atomic<u64>num_commands{};
 bool draw_snapshot_valid=true;u64 drains{};std::function<void()>drain_check;
 bool OnDrawThread()const{return draw_thread;}
 void DrainDrawQueue(){++drains;if(drain_check)drain_check();}
 template<bool wait_done=false>
 @SEND_COMMAND@
 void ProcessCommands();
};
@PROCESS_COMMANDS@
}
namespace Libraries::VideoOut {struct BufferAttributeGroup;}
namespace Shader {struct ImageResource;}
u64 XXH3_64bits(const void* data,size_t size) {
 u64 hash=14695981039346656037ULL;
 for(size_t i=0;i<size;++i)hash=(hash^static_cast<const u8*>(data)[i])*1099511628211ULL;
 return hash;
}
struct Scheduler {
 u64 tick=1,copies{},ends{},barriers{};
 std::thread::id required_owner{};
 std::vector<std::function<void()>> commands,retire;
 u64 CurrentTick()const{return tick;}
 template<class... A>void EndRendering(A&&...){++ends;}
 template<class F>void RecordDeferred(F&& f){assert(required_owner==std::thread::id{}||required_owner==std::this_thread::get_id());++copies;commands.emplace_back([f=std::forward<F>(f)]{f(vk::CommandBuffer{});});}
 template<class F>void DeferOperation(F&& f){retire.emplace_back(std::forward<F>(f));}
 void Execute(){auto work=std::move(commands);commands.clear();for(auto&f:work)f();}
 void Complete(){Execute();auto work=std::move(retire);retire.clear();for(auto&f:work)f();++tick;}
};
namespace VideoCore {
@TYPES@
@INFO@
s32 ImageInfo::MipOf(const ImageInfo&)const{return -1;}
s32 ImageInfo::SliceOf(const ImageInfo&,s32)const{return -1;}
bool ImageInfo::IsCompatible(const ImageInfo&)const{return false;}
void ImageInfo::UpdateSize(){std::abort();}
using ImageIds=std::vector<ImageId>;
@FLAGS@;
inline bool False(u32 x){return !x;}inline bool True(u32 x){return x!=0;}
struct ImageView{};struct ImageViewInfo{SubresourceRange range;};
struct Image {
 ImageInfo info;u64 image_uid{},tick_accessed_last{},lru_id{},alias_generation{},track_addr{},track_addr_end{},hash{};
 std::array<u64,16>mip_hashes{};u32 flags=ImageFlagBits::Dirty;u32 aspect_mask=vk::ImageAspectFlagBits::eColor;
 struct {bool is_target{},is_bound{},needs_rebind{};}binding;
 struct{u32 render_target{},depth_target{};}usage;
 struct Backing{std::vector<ImageViewId>image_view_ids;};std::vector<Backing>backing_images;
 std::unique_ptr<GpuImage> gpu;ImageView view;
 explicit Image(const ImageInfo&i):info(i),gpu(std::make_unique<GpuImage>()) {
   gpu->width=i.size.width;gpu->height=i.size.height;gpu->layers=i.resources.layers;
   gpu->pixels.resize(size_t(i.size.width)*i.size.height*i.resources.layers,0);
 }
 @OVERLAPS@
 @TRACKED@
 @DOWNLOADABLE@
 vk::Image GetImage()const{return gpu.get();}
 ImageView&FindView(const ImageViewInfo&,bool=true){return view;}
};
struct Slots {
 std::map<ImageId,Image>items;u64 uid=0;
 ImageId Insert(int,const auto&,const auto&,const ImageInfo&i){u32 n=0;while(items.contains(ImageId{n}))++n;ImageId id{n};items.emplace(id,Image{i});items.at(id).image_uid=++uid;return id;}
 Image&operator[](ImageId i){return items.at(i);}const Image&operator[](ImageId i)const{return items.at(i);}
 bool IsAllocated(ImageId i)const{return items.contains(i);}void Erase(ImageId i){assert(items.erase(i)==1);}
};
struct ViewSlots{void Erase(ImageViewId){}};
struct PageTable {
 std::map<u64,std::vector<ImageId>>values;auto&operator[](u64 i){return values[i];}
 auto*find(u64 i){auto it=values.find(i);return it==values.end()?nullptr:&it->second;}
};
struct Lru {
 std::set<u64>live;u64 next=0,touches=0;
 u64 Insert(ImageId,u64){live.insert(++next);return next;}
 void Touch(u64 id,u64){assert(live.contains(id));++touches;}
 void Free(u64 id){assert(live.erase(id)==1);}
};
enum class PageOp{Track,Untrack};
struct PageManager {
 static VAddr GetPageAddr(VAddr a){return a&~u64{4095};}
 static VAddr GetNextPageAddr(VAddr a){return (a+4096)&~u64{4095};}
 void UpdatePageWatchers(VAddr,u64,PageOp){}
};
struct Buffer{std::vector<u8>bytes;};
struct BufferCache {
 Buffer buffer;u64 guest_reads{};
 std::pair<const Buffer*,u64>ObtainBufferForImage(VAddr a,u64 n){++guest_reads;buffer.bytes.resize(n);std::memcpy(buffer.bytes.data(),std::bit_cast<void*>(a),n);return {&buffer,0};}
};
struct TileManager {std::pair<const Buffer*,u64>DetileImage(const Buffer*b,u64 o,const ImageInfo&){return {b,o};}};
struct Runtime {
 Scheduler&scheduler;u64 uploads{};std::vector<std::tuple<Image*,vk::ImageLayout,vk::AccessFlagBits2>>transitions;
 explicit Runtime(Scheduler&s):scheduler(s){}
 void SetBackingSamples(Image*i,u32 n){assert(i->info.num_samples==n);}
 bool Transit(Image*i,vk::ImageLayout l,vk::PipelineStageFlagBits2,vk::AccessFlagBits2 a){transitions.emplace_back(i,l,a);return true;}
 void FlushBarriers(){++scheduler.barriers;}
 void CopyAliasImage(Image*,Image*,const vk::Extent3D&);
 void CopyMip(Image*,Image*,int,int){std::abort();}
 void UploadImage(Image*i,const Buffer*b,const auto&regions) {
   ++uploads;auto data=b->bytes;auto*dst=i->gpu.get();
   scheduler.commands.emplace_back([dst,data=std::move(data),regions]{
    for(auto&r:regions)for(u32 l=0;l<r.imageSubresource.layerCount;++l)
     for(u32 y=0;y<r.imageExtent.height;++y)for(u32 x=0;x<r.imageExtent.width;++x) {
      u64 value;std::memcpy(&value,data.data()+r.bufferOffset+((l*r.bufferImageHeight+y)*r.bufferRowLength+x)*8,8);
      dst->pixels[(l*dst->height+y)*dst->width+x]=value;
     }
   });
   i->flags&=~ImageFlagBits::Dirty;
 }
};
struct Metadata {std::function<void()>interleave;void Write(VAddr,u64){}void Unmap(VAddr,u64){if(interleave){auto f=std::move(interleave);interleave={};f();}}};
struct TextureCache {
 enum class BindingType{Texture,Storage,RenderTarget,DepthTarget};
 struct ImageDesc{ImageInfo info;ImageViewInfo view_info;BindingType type=BindingType::Texture;};
 struct ViewMemo{};
 enum class MetaType{CMask,FMask,HTile};
 struct MetaDataInfo{MetaType type;ImageId owner_id;u64 owner_uid;u32 num_samples;};
 struct Traits{static constexpr u32 PAGE_BITS=12;};
 int instance{};Scheduler scheduler;Runtime runtime{scheduler};BufferCache buffer_cache;TileManager tile_manager;ViewSlots slot_image_views;
 Slots slot_images;PageTable page_table;Lru lru_cache;PageManager tracker;std::mutex mutex,download_images_mutex;
 AmdGpu::Liverpool processor;AmdGpu::Liverpool*liverpool=&processor;
 std::atomic<u64>registry_generation{};u64 total_used_memory{},gc_tick{};
 Metadata surface_metadata;bool readback_linear_images=false;std::set<ImageId>download_images;
 @ALIAS_MEMBERS@
 bool ImageAliasesEnabled()const;void PublishAliasWrite(ImageId);
 void UnmapMemory(VAddr,size_t);
 ImageId FindImage(ImageDesc&,bool=false);void RegisterImage(ImageId);void UnregisterImage(ImageId);void DeleteImage(ImageId);
 std::tuple<ImageId,int,int>ResolveOverlap(const ImageInfo&,BindingType,ImageId,ImageId);
 ImageId ResolveDepthOverlap(const ImageInfo&,BindingType,ImageId){return {};}
 ImageId ExpandImage(const ImageInfo&,ImageId){std::abort();}
 @FREE@
 Image&GetImage(ImageId id){TouchImage(slot_images[id]);return slot_images[id];}
 void TrackImage(ImageId);void UntrackImage(ImageId);void TouchImage(const Image&);
 void TrackImageHead(ImageId);void TrackImageTail(ImageId);void UntrackImageHead(ImageId);void UntrackImageTail(ImageId);
 void MarkAsMaybeDirty(ImageId,Image&);void RefreshImage(Image&);void InvalidateMemory(VAddr,size_t);void InvalidateMemoryFromGPU(VAddr,size_t);
 @UPDATE@
 ImageView&FindRenderTarget(ImageId,const ImageDesc&);ImageView&FindTexture(ImageId,const ImageDesc&,ViewMemo* = nullptr);
 bool OrderDescriptorViewMemoEnabled()const{return false;}
 ImageView*TryViewMemo(ImageId,const ImageViewInfo&,ViewMemo&){std::abort();}
 void RememberViewMemo(ImageId,const ImageViewInfo&,ImageView&,ViewMemo&){}
 void RegisterMeta(VAddr,MetaDataInfo){}void UnregisterMeta(VAddr,u64){}
 void CancelImageReadbacks(VAddr,u64){}bool ResolveImageReadbacks(VAddr,u64,bool){return false;}
 template<class F>void ForEachPage(VAddr a,u64 n,F f){for(u64 p=a>>12;p<=((a+n-1)>>12);++p)f(p);}
 template<class F>void ForEachImageInRegion(VAddr a,u64 n,F f){for(auto&[id,image]:slot_images.items)if((image.flags&Registered)&&image.Overlaps(a,n))f(id,image);}
};
bool IsVulkanFormatCompatible(vk::Format a,vk::Format b){return a==b||(a!=vk::Format::eUndefined&&b!=vk::Format::eUndefined&&a!=vk::Format::eR8Unorm&&b!=vk::Format::eR8Unorm);}
@HELPERS@
@METHODS@
@RUNTIME@
}
using namespace VideoCore;
struct Images {
 std::vector<u64> guest;TextureCache cache;ImageInfo base;
 explicit Images(u32 width=1280,u32 height=736):guest(size_t(width)*height,0) {
  base.guest_address=std::bit_cast<VAddr>(guest.data());base.guest_size=u32(guest.size()*8);
  base.size={width,height,1};base.pitch=width;base.num_bits=64;base.type=AmdGpu::ImageType::Color2D;
  base.pixel_format=vk::Format::eR16G16B16A16Sfloat;base.mips_layout[0]={base.guest_size,width,height,0};
 }
 ImageId Add(u32 height){auto info=base;info.size.height=height;info.guest_size=info.size.width*height*8;info.mips_layout[0]={info.guest_size,info.pitch,height,0};TextureCache::ImageDesc desc{info};return cache.FindImage(desc);}
 void Write(ImageId id,u64 value,bool storage=false) {
  auto&im=cache.slot_images[id];TextureCache::ImageDesc desc{im.info};
  if(storage){desc.type=TextureCache::BindingType::Storage;cache.FindTexture(id,desc);}
  else {desc.type=TextureCache::BindingType::RenderTarget;cache.FindRenderTarget(id,desc);}
  auto*gpu=im.gpu.get();cache.scheduler.commands.emplace_back([gpu,value]{std::fill(gpu->pixels.begin(),gpu->pixels.end(),value);});
 }
 u64 Pixel(ImageId id,u32 y=0){cache.scheduler.Execute();return cache.slot_images[id].gpu->pixels[y*base.size.width];}
};
void AuthorityTest() {
 Images f;auto a=f.Add(736),b=f.Add(720);assert(a!=b);
 f.Write(a,17);assert(f.Pixel(b)==0);f.cache.UpdateImage(b);assert(f.Pixel(b)==17);
 const auto copied=f.cache.scheduler.copies;f.cache.UpdateImage(b);assert(f.cache.scheduler.copies==copied);
 f.Write(b,23,true);f.cache.UpdateImage(a);assert(f.Pixel(a)==23&&f.Pixel(a,730)==17);
 f.cache.UpdateImage(b);assert(f.Pixel(b)==23);
 assert(f.cache.scheduler.barriers==f.cache.scheduler.copies);
 assert(f.cache.runtime.transitions.size()==2*f.cache.scheduler.copies);
 for(size_t i=0;i<f.cache.runtime.transitions.size();i+=2) {
  assert(std::get<1>(f.cache.runtime.transitions[i])==vk::ImageLayout::eTransferSrcOptimal);
  assert(std::get<2>(f.cache.runtime.transitions[i])==vk::AccessFlagBits2::eTransferRead);
  assert(std::get<1>(f.cache.runtime.transitions[i+1])==vk::ImageLayout::eTransferDstOptimal);
  assert(std::get<2>(f.cache.runtime.transitions[i+1])==vk::AccessFlagBits2::eTransferWrite);
 }
}
void ThirdSizeTest() {
 Images f;auto a=f.Add(736),b=f.Add(700);f.Write(a,17);f.cache.UpdateImage(b);f.Write(b,23);
 auto c=f.Add(720);f.cache.UpdateImage(c);assert(f.Pixel(c)==23&&f.Pixel(c,710)==17);
 f.cache.UpdateImage(a);assert(f.Pixel(a)==23&&f.Pixel(a,730)==17);
}
void CpuAuthorityTest() {
 Images f;std::fill(f.guest.begin(),f.guest.end(),31);
 auto a=f.Add(736),b=f.Add(700);f.Write(b,23);auto c=f.Add(720);f.cache.UpdateImage(c);
 assert(f.Pixel(c)==23&&f.Pixel(c,710)==31);
 f.cache.SynchronizeAliasDownload(a);assert(f.Pixel(a)==23&&f.Pixel(a,730)==31);
}
void InvalidateTest(bool gpu) {
 Images f;auto a=f.Add(736),b=f.Add(720);f.Write(a,17);f.cache.UpdateImage(b);f.cache.scheduler.Execute();
 if(gpu)f.cache.InvalidateMemoryFromGPU(f.base.guest_address,8);else f.cache.InvalidateMemory(f.base.guest_address,8);
 f.guest[0]=31;f.cache.UpdateImage(b);assert(f.Pixel(b)==31);
 assert(f.cache.slot_images[a].alias_generation==0&&f.cache.slot_images[b].alias_generation==0);
 f.cache.UpdateImage(a);assert(f.Pixel(a)==31);
}
void MaybeDirtyTest() {
 Images f(4,8);auto a=f.Add(8),b=f.Add(4);f.Write(a,17);f.cache.UpdateImage(b);f.cache.scheduler.Execute();
 auto&im=f.cache.slot_images[b];f.cache.MarkAsMaybeDirty(b,im);f.guest[0]=39;
 f.cache.UpdateImage(b);assert(f.Pixel(b)==39);
 assert(im.alias_generation==0);
}
void IdentityTest() {
 Images f;auto a=f.Add(736),b=f.Add(720);f.Write(a,17);f.cache.UpdateImage(b);f.cache.scheduler.Execute();
 auto&state=f.cache.alias_states.at(f.base.guest_address);const auto old_uid=state.backing_uid;
 ++f.cache.slot_images[a].image_uid;f.cache.slot_images[a].gpu->pixels[0]=91;
 f.cache.slot_images[b].alias_generation=0;f.cache.UpdateImage(b);
 assert(f.Pixel(b)==17&&state.backing_uid!=old_uid); // stale UID is never a source
}
void RetireTest() {
 Images f;auto a=f.Add(736),b=f.Add(720);f.Write(a,17);f.cache.UpdateImage(b);
 const auto uid=f.cache.slot_images[a].image_uid;
 f.cache.FreeImage(a);assert(f.cache.slot_images.IsAllocated(a));
 const auto touches=f.cache.lru_cache.touches;f.cache.GetImage(a);assert(f.cache.lru_cache.touches==touches);
 assert(!f.cache.alias_states.contains(f.base.guest_address));
 // Copy is recorded before destruction. Execute and complete after local
 // Runtime::CopyAliasImage arguments and region have gone out of scope.
 assert(f.Pixel(b)==17);f.cache.scheduler.Complete();assert(!f.cache.slot_images.IsAllocated(a));
 auto c=f.Add(736);assert(c==a&&f.cache.slot_images[c].image_uid!=uid);
 f.Write(c,47);f.cache.UpdateImage(b);assert(f.Pixel(b)==47);
}
void PartialUnmapTest(int owner,bool total=false) {
 Images f;auto a=f.Add(736),b=f.Add(720);auto c=f.Add(728);f.Write(a,17);f.cache.scheduler.Execute();
 const auto reads=f.cache.buffer_cache.guest_reads,copies=f.cache.scheduler.copies;
 std::jthread worker;std::binary_semaphore ready{0};
 if(owner==2) {
  worker=std::jthread([&](std::stop_token stop){
   f.cache.processor.gpu_id=std::this_thread::get_id();ready.release();
   for(;;){
    {std::unique_lock lock{f.cache.processor.submit_mutex};
     f.cache.processor.submit_cv.wait(lock,[&]{return stop.stop_requested()||f.cache.processor.num_commands!=0;});}
    if(stop.stop_requested())break;
    f.cache.processor.ProcessCommands();
   }
  });ready.acquire();
 }
 if(owner==1)AmdGpu::Liverpool::draw_thread=true;
 f.cache.scheduler.required_owner=owner==2?f.cache.processor.gpu_id:std::this_thread::get_id();
 f.cache.processor.drain_check=[&]{assert(f.cache.mutex.try_lock());f.cache.mutex.unlock();};
 const VAddr address=f.base.guest_address+(total?0:u64{720}*1280*8);
 f.cache.UnmapMemory(address,total?f.base.guest_size:u64{16}*1280*8);
 AmdGpu::Liverpool::draw_thread=false;
 if(owner==2){worker.request_stop();f.cache.processor.submit_cv.notify_one();worker.join();}
 assert(f.cache.buffer_cache.guest_reads==reads);
 assert(!(f.cache.slot_images[a].flags&Registered));assert(!(f.cache.slot_images[c].flags&Registered));
 if(total)assert(f.cache.scheduler.copies==copies&&!(f.cache.slot_images[b].flags&Registered));
 else {
  assert(f.cache.scheduler.copies==copies+1);assert(f.cache.slot_images[b].flags&Registered);
  f.cache.scheduler.required_owner={};f.cache.UpdateImage(b);assert(f.Pixel(b)==17);
 }
 f.cache.scheduler.Complete();
 assert(!f.cache.slot_images.IsAllocated(a)&&!f.cache.slot_images.IsAllocated(c));
}
void WritebackRetireTest() {
 Images f;auto a=f.Add(736),b=f.Add(720);f.cache.UpdateImage(b);f.Write(a,17);f.cache.scheduler.Execute();
 // GPU download is the I/O boundary. The production notification runs only
 // after successful publication and before GC unregisters the authority.
 f.guest=f.cache.slot_images[a].gpu->pixels;
 f.cache.NoteAliasWriteback(f.cache.slot_images[a]);f.cache.FreeImage(a);
 f.cache.UpdateImage(b);assert(f.Pixel(b)==17);f.cache.scheduler.Complete();
}
void LateRegistrationTest() {
 Images f;auto a=f.Add(736);f.Write(a,17);f.cache.scheduler.Execute();ImageId b;
 // Deterministic boundary between the former unlocked probe and the final
 // lifetime lock. A real RegisterImage makes a previously non-alias range aliased.
 f.cache.surface_metadata.interleave=[&]{b=f.Add(720);};
 f.cache.UnmapMemory(f.base.guest_address+u64{720}*1280*8,u64{16}*1280*8);
 assert(b&&f.cache.slot_images[b].flags&Registered);
 f.cache.UpdateImage(b);assert(f.Pixel(b)==17);f.cache.scheduler.Complete();
}
void PartialWritebackTest() {
 Images f;auto a=f.Add(736),b=f.Add(720);f.Write(a,17);f.Write(b,23);
 f.cache.SynchronizeAliasDownload(b);f.cache.scheduler.Execute();
 std::copy(f.cache.slot_images[b].gpu->pixels.begin(),f.cache.slot_images[b].gpu->pixels.end(),f.guest.begin());
 f.cache.NoteAliasWriteback(f.cache.slot_images[b]);f.cache.FreeImage(b);
 f.cache.UpdateImage(a);assert(f.Pixel(a)==23&&f.Pixel(a,730)==17);f.cache.scheduler.Complete();
}
void EligibilityTest() {
 Images f;const auto a=f.base;auto b=a;b.size.height=720;
 assert(GetOrderAliasCopyExtent(a,b)->height==720);
 b=a;b.size.height=752;assert(GetOrderAliasCopyExtent(a,b)->height==736);
 for(int c=0;c<13;++c) {
  b=a;switch(c){case 0:b.guest_address+=8;break;case 1:b.num_bits=32;break;
   case 2:b.num_samples=2;break;case 3:b.props.is_depth=1;break;case 4:b.props.is_block=1;break;
   case 5:b.props.is_pow2=1;break;case 6:b.type=AmdGpu::ImageType::Color3D;break;
   case 7:b.pitch++;break;case 8:b.tile_mode=AmdGpu::TileMode::Tiled;break;
   case 9:b.array_mode=AmdGpu::ArrayMode::Tiled;break;case 10:b.bank_swizzle++;break;
   case 11:b.alt_tile=true;break;case 12:b.resources.levels=2;break;}
  assert(!GetOrderAliasCopyExtent(a,b));
 }
 b=a;b.pixel_format=vk::Format::eR16G16B16A16Uint;assert(GetOrderAliasCopyExtent(a,b));
 b.pixel_format=vk::Format::eR8Unorm;assert(!GetOrderAliasCopyExtent(a,b));
 b=a;b.resources.layers=2;assert(!GetOrderAliasCopyExtent(a,b));
 Image small{a},layers{b};assert(!CanAlias(small,layers)&&!CanAlias(layers,small));
 b=a;b.size.width/=2;Image narrow{b};assert(!CanAlias(small,narrow));
 b=a;b.size.depth=2;Image volume{b};assert(!CanAlias(small,volume));
 // Register a valid two-layer backing and a one-layer writer through the real
 // registration path: no unsupported one-way authority group may be created.
 TextureCache cache;auto large_id=cache.slot_images.Insert(0,cache.runtime,cache.slot_image_views,layers.info);
 cache.RegisterImage(large_id);auto small_id=cache.slot_images.Insert(0,cache.runtime,cache.slot_image_views,small.info);
 cache.RegisterImage(small_id);cache.PublishAliasWrite(small_id);
 assert(cache.alias_states.empty());
}
void PolicyTest() {
 Common::ElfInfo::Instance().serial="CUSA08809";Images f;auto a=f.Add(736),b=f.Add(720);
 f.Write(a,17);f.cache.UpdateImage(b);assert(f.Pixel(b)==0&&f.cache.alias_states.empty());
 Common::ElfInfo::Instance().serial="CUSA00785";
}
int main(int argc,char**argv) {
#ifndef __ANDROID__
 Images f;assert(!f.cache.ImageAliasesEnabled());std::cout<<"ORDER_IMAGE_ALIAS_DESKTOP_PASS\n";return 0;
#endif
 const std::string only=argc>1?argv[1]:"";
 if(only.empty()||only=="authority")AuthorityTest();
 if(only.empty()||only=="third")ThirdSizeTest();
 if(only.empty()||only=="cpu_authority")CpuAuthorityTest();
 if(only.empty()||only=="cpu")InvalidateTest(false);
 if(only.empty()||only=="gpu")InvalidateTest(true);
 if(only.empty()||only=="maybe")MaybeDirtyTest();
 if(only.empty()||only=="identity")IdentityTest();
 if(only.empty()||only=="retire")RetireTest();
 if(only.empty()||only=="unmap")for(int owner=0;owner<3;++owner){PartialUnmapTest(owner);PartialUnmapTest(owner,true);}
 if(only.empty()||only=="writeback")WritebackRetireTest();
 if(only.empty()||only=="late_registration")LateRegistrationTest();
 if(only.empty()||only=="partial_writeback")PartialWritebackTest();
 if(only.empty()||only=="eligibility")EligibilityTest();
 if(only.empty()||only=="policy")PolicyTest();
 std::cout<<"ORDER_IMAGE_ALIAS_PASS actual_find_refresh_authority_copy_invalidation_retire\n";
}
'''


TEXEL_PROGRAM = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstring>
#include <iostream>
#include <string_view>
#include <utility>
#include <vector>
#include "common/types.h"
#define LOG_INFO(...) ((void)0)
namespace boost::container {template<class T,size_t N>using small_vector=std::vector<T>;}
namespace Common {
template<class T,class U>auto AlignUp(T a,U b){return (a+b-1)/b*b;}
template<class T,class U>auto AlignDown(T a,U b){return a/b*b;}
struct ElfInfo{std::string_view serial="CUSA00785";static ElfInfo&Instance(){static ElfInfo i;return i;}auto GameSerial()const{return serial;}};
}
namespace BachataCompat {@POLICY@}
namespace vk {struct BufferCopy{u64 srcOffset,dstOffset,size;};}
namespace VideoCore {struct Buffer{u64 cpu_addr=0x100000;std::vector<u8>bytes=std::vector<u8>(128_KB);u64 Offset(VAddr a)const{return a-cpu_addr;}};enum class MemoryType{HostUncached};}
namespace Vulkan {struct StagingBufferRef{const VideoCore::Buffer*buffer{};u64 offset{};u8*mapped{};void Flush(){}};}
namespace VideoCore {
struct Memory{void CopySparseMemory(VAddr,u8*dst,u64 n){std::fill(dst,dst+n,3);}};
struct Tracker{template<class Range,class Commit>void ForEachUploadRange(VAddr,u64,bool,Range&&,Commit&&commit){commit();}};
struct Pool{Buffer b;Vulkan::StagingBufferRef Request(u64,MemoryType){return {&b,0,b.bytes.data()};}};
struct Runtime{void CopyBuffer(const Buffer*,const Buffer*,const auto&) {}};
struct Texture {u64 resolves{},writes{};bool ResolveImageReadbacks(VAddr,u64,bool){++resolves;return false;}void NoteMetaShaderWrite(VAddr,u64){++writes;}};
struct Stream:Buffer{std::pair<u8*,u64>Map(u64,u64){return {bytes.data(),0};}void Commit(){}};
struct Instance{u64 UniformMinAlignment(){return 16;}};
struct Ranges{void Add(VAddr,u64){}};
struct BufferCache {
 static constexpr u64 STREAM_THRESHOLD=16_KB;static constexpr u64 block_shift=16;
 Texture texture_cache;Stream stream_buffer;Instance instance;Buffer arena;Pool staging_pool;Runtime runtime;
 Memory memory_value;Memory*memory=&memory_value;Tracker tracker_value;Tracker*memory_tracker=&tracker_value;
 std::vector<int>fresh_backings;std::atomic<u64>cpu_upload_bytes{};bool coherent_arena_upload=false;
 Ranges gpu_modified_ranges;bool gpu=true;u64 image_syncs{};
 bool IsRegionGpuModified(VAddr,u64){return gpu;}
 const Buffer*GetArena(u64,u64){return &arena;}void EnsureResident(const Buffer*,u64,u64){}
 bool UploadFreshBacking(VAddr,u64){std::abort();}
 bool SynchronizeMemoryFromImage(const Buffer*,VAddr,u32){++image_syncs;return true;}
 bool SynchronizeMemory(const Buffer*,VAddr,u32,bool,bool);
 std::pair<const Buffer*,u64>ObtainBuffer(VAddr,u32,bool,bool);
};
@METHODS@
}
int main(){
 using namespace VideoCore;
 for(auto serial:{"CUSA00785","CUSA08809","OTHER"}) {
  Common::ElfInfo::Instance().serial=serial;BufferCache cache;
  cache.ObtainBuffer(0x100000,64_KB,false,true);
  const u64 expected=BachataCompat::Order1886()?1:2;
  assert(cache.image_syncs==expected);
  cache.ObtainBuffer(0x100000,64_KB,true,true);assert(cache.image_syncs==expected&&cache.texture_cache.writes==1);
  cache.ObtainBuffer(0x100000,64_KB,false,false);assert(cache.image_syncs==expected);
  cache.ObtainBuffer(0x100000,4096,false,true);assert(cache.image_syncs==2*expected);
  cache.gpu=false;cache.ObtainBuffer(0x100000,4096,false,true);assert(cache.image_syncs==2*expected);
 }
 std::cout<<"ORDER_TEXEL_SYNC_PASS actual_ObtainBuffer_and_SynchronizeMemory\n";
}
'''


def make_program(src: Path) -> str:
    read = lambda path: (src / path).read_text()
    cache = read("video_core/texture_cache/texture_cache.cpp")
    header = read("video_core/texture_cache/texture_cache.h")
    image = read("video_core/texture_cache/image.h")
    members = header[header.index("    struct AliasState {"):header.index("\n    std::mutex mutex;")]
    members = members.replace("tsl::robin_map<VAddr, AliasState>", "std::map<VAddr, AliasState>")
    method_signatures = (
        "bool TextureCache::ImageAliasesEnabled()", "void TextureCache::ForEachAlias(",
        "void TextureCache::SynchronizeAlias(", "bool TextureCache::CommitAliasWriter(",
        "void TextureCache::SynchronizeAliasDownload(",
        "void TextureCache::CopyAlias(", "void TextureCache::PublishAliasWrite(",
        "void TextureCache::InvalidateAlias(", "ImageId TextureCache::FindImage(",
        "void TextureCache::NoteAliasWriteback(", "void TextureCache::UnmapMemory(",
        "void TextureCache::UnmapImages(",
        "void TextureCache::RegisterAlias(", "void TextureCache::UnregisterAlias(",
        "void TextureCache::RegisterImage(", "void TextureCache::UnregisterImage(",
        "std::tuple<ImageId, int, int> TextureCache::ResolveOverlap(",
        "void TextureCache::DeleteImage(", "void TextureCache::TouchImage(",
        "void TextureCache::TrackImage(", "void TextureCache::UntrackImage(",
        "void TextureCache::TrackImageHead(", "void TextureCache::TrackImageTail(",
        "void TextureCache::UntrackImageHead(", "void TextureCache::UntrackImageTail(",
        "void TextureCache::MarkAsMaybeDirty(", "void TextureCache::RefreshImage(",
        "void TextureCache::InvalidateMemory(", "void TextureCache::InvalidateMemoryFromGPU(",
        "ImageView& TextureCache::FindRenderTarget(", "ImageView& TextureCache::FindTexture(",
    )
    census = (src / "video_core/renderer_vulkan/order_resource_census.h").exists()
    if census:
        method_signatures += ("Vulkan::OrderAliasProbe TextureCache::ProbeOrderAliasRegistration(",)
    methods = "\n".join(("template<class Func>\n" if "ForEachAlias" in sig else "") +
                        block(cache, sig) for sig in method_signatures)
    # Only the map iterator API is adapted to the standard-library fixture.
    methods = methods.replace(".first.value()", ".first->second")
    for name in ("state_it", "it", "alias_it"):
        methods = methods.replace(name + ".value()", name + "->second")
    values = {
        "SEND_COMMAND": block(read("video_core/amdgpu/liverpool.h"), "    void SendCommand("),
        "PROCESS_COMMANDS": block(read("video_core/amdgpu/liverpool.cpp"), "void Liverpool::ProcessCommands()"),
        "SLOTID": block(read("common/slot_vector.h"), "struct SlotId {"),
        "TYPES": read("video_core/texture_cache/types.h").split("namespace VideoCore {", 1)[1].rsplit("} // namespace VideoCore", 1)[0],
        "INFO": read("video_core/texture_cache/image_info.h").split("namespace VideoCore {", 1)[1].rsplit("} // namespace VideoCore", 1)[0],
        "FLAGS": block(image, "enum ImageFlagBits : u32 {"),
        "OVERLAPS": block(image, "bool Overlaps("),
        "TRACKED": block(image, "bool IsTracked()"),
        "DOWNLOADABLE": block(image, "bool SafeToDownload()"),
        "ALIAS_MEMBERS": members,
        "FREE": block(header, "    void FreeImage("),
        "UPDATE": block(header, "    void UpdateImage("),
        "HELPERS": "\n".join(block(cache, sig) for sig in (
            "std::optional<Extent3D> GetOrderAliasCopyExtent(", "static bool Covers(",
            "static bool CanAlias(", "static void CountOrderAliasCopy(")),
        "METHODS": methods,
        "RUNTIME": block(read("video_core/renderer_vulkan/vk_runtime.cpp"), "void Runtime::CopyAliasImage("),
    }
    program = PROGRAM
    if census:
        program = program.replace("#define LOG_INFO IgnoreLog",
            '#define LOG_INFO IgnoreLog\n#include "video_core/renderer_vulkan/order_resource_census.h"', 1)
        program = program.replace("auto*find(u64 i){auto it=values.find(i);return it==values.end()?nullptr:&it->second;}",
            "auto*find(u64 i){auto it=values.find(i);return it==values.end()?nullptr:&it->second;}\n const auto*find(u64 i)const{auto it=values.find(i);return it==values.end()?nullptr:&it->second;}", 1)
    if (src / "video_core/renderer_vulkan/order_render_pass_reasons.h").exists():
        program = '#include "video_core/renderer_vulkan/order_render_pass_reasons.h"\n' + program
    for key, value in values.items():
        program = program.replace("@" + key + "@", value)
    assert "@" not in program
    return program


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--positive-only", action="store_true")
    args = parser.parse_args()
    src = args.source.resolve() / "src"
    program = make_program(src)
    compiler = shlex.split(os.environ.get("CXX", "c++")) + [
        "-std=c++23", "-O1", "-g", "-fsanitize=undefined", "-fno-sanitize-recover=all",
        "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter", "-Wno-missing-field-initializers",
        "-pthread", "-I", str(src)]
    with tempfile.TemporaryDirectory(prefix="order-image-alias-") as tmp:
        temp = Path(tmp)
        def run(label: str, text: str, *, only: str = "", negative: bool = False,
                android: bool = True) -> None:
            path = temp / (label + ".cpp")
            path.write_text(text)
            subprocess.run(compiler + (["-D__ANDROID__"] if android else []) +
                           [str(path), "-o", str(temp / label)], check=True)
            result = subprocess.run([str(temp / label)] + ([only] if only else []),
                                    capture_output=True, text=True, timeout=30)
            if negative:
                assert result.returncode != 0, "Negative control accepted: " + label
                print("ORDER_IMAGE_ALIAS_NEGATIVE_PASS", label, flush=True)
            else:
                assert result.returncode == 0, label + "\n" + result.stdout + result.stderr
                print(result.stdout, end="", flush=True)
        run("positive", program)
        run("desktop", program, android=False)
        cache = (src / "video_core/buffer_cache/buffer_cache.cpp").read_text()
        texel = TEXEL_PROGRAM.replace("@POLICY@", block(
            (src / "common/bachata_compat_profile.h").read_text(), "inline bool Order1886()"))
        texel = texel.replace("@METHODS@", "\n".join(block(cache, sig) for sig in (
            "std::pair<const Buffer*, u64> BufferCache::ObtainBuffer(",
            "bool BufferCache::SynchronizeMemory(")))
        run("texel", texel)
        run("texel_desktop", texel, android=False)
        if args.positive_only:
            return
        controls = {
            "no_sync": ("        SynchronizeAlias(image_id);", "        // dropped alias sync", "authority"),
            "no_writer": ("    image.alias_generation = ++alias_generation;", "    return;", "authority"),
            "promote_partial_writer": ("(inserted && slot_images[state->backing].alias_generation <\n                                 candidate.alias_generation)",
                                       "(slot_images[state->backing].alias_generation < candidate.alias_generation)", "third"),
            "uninitialized_cpu_tail": ("            RefreshImage(backing);", "            // omitted backing initialization", "cpu_authority"),
            "no_cpu_invalidation": ("            InvalidateAlias(image);\n            image.flags |= ImageFlagBits::CpuDirty;",
                                    "            image.flags |= ImageFlagBits::CpuDirty;", "cpu"),
            "no_gpu_invalidation": ("        InvalidateAlias(image);\n        image.flags |= ImageFlagBits::GpuDirty;",
                                    "        image.flags |= ImageFlagBits::GpuDirty;", "gpu"),
            "no_maybe_invalidation": ("        InvalidateAlias(image);\n    }\n\n    const u32 num_layers",
                                      "    }\n\n    const u32 num_layers", "maybe"),
            "stale_uid": ("slot_images[image_id].image_uid == image_uid &&", "true &&", "identity"),
            "retired_lru": ("    if (False(image.flags & ImageFlagBits::Registered)) return;", "", "retire"),
            "unmap_no_preserve": ("for (const ImageId id : survivors) SynchronizeAlias(id);", "for (const ImageId id : survivors) (void)id;", "unmap"),
            "unmap_no_owner": ("liverpool->SendCommand<true>([this, cpu_addr, size] {\n            UnmapImages(cpu_addr, size, true);\n        });", "UnmapImages(cpu_addr, size, true);", "unmap"),
            "unmap_overlapping_survivor": ("if (!image.Overlaps(cpu_addr, size) &&", "if (true &&", "unmap"),
            "writeback_no_invalidation": ("            candidate.flags |= ImageFlagBits::CpuDirty;", "            (void)candidate;", "writeback"),
            "writeback_partial_not_committed": ("if (!CommitAliasWriter(it->second)) it->second.ResetAuthority();", "if (false) it->second.ResetAuthority();", "partial_writeback"),
            "one_way_alias": ("GetOrderAliasCopyExtent(lhs.info, rhs.info) && GetOrderAliasCopyExtent(rhs.info, lhs.info)", "GetOrderAliasCopyExtent(lhs.info, rhs.info) || GetOrderAliasCopyExtent(rhs.info, lhs.info)", "eligibility"),
            "pitch_alias": ("src.type == dst.type && src.pitch == dst.pitch && src.tile_mode == dst.tile_mode", "src.type == dst.type && src.tile_mode == dst.tile_mode", "eligibility"),
        }
        for label, (old, new, only) in controls.items():
            assert old in program, label
            run(label, program.replace(old, new, 1), only=only, negative=True)
        from port_order_image_alias import UNMAP_DISPATCH
        assert program.count(UNMAP_DISPATCH) == 1
        old_probe = r'''void TextureCache::UnmapMemory(VAddr cpu_addr, size_t size) {
    bool has_aliases = false;
    if (ImageAliasesEnabled()) {
        std::scoped_lock lock{mutex};
        ForEachImageInRegion(cpu_addr, size, [&](ImageId, const Image& image) {
            has_aliases |= True(image.flags & ImageFlagBits::Aliased);
        });
    }
    if (has_aliases) {
        liverpool->SendCommand<true>([this, cpu_addr, size] {UnmapImages(cpu_addr, size, true);});
        return;
    }
    UnmapImages(cpu_addr, size, false);
}'''
        probe_race = program.replace(block(program, "void TextureCache::UnmapMemory("), old_probe, 1)
        probe_race = probe_race.replace(UNMAP_DISPATCH, "", 1)
        run("unmap_probe_race", probe_race, only="late_registration", negative=True)
        old = "is_texel_buffer && !is_written && !BachataCompat::Order1886()"
        assert old in texel
        run("duplicate_texel_sync", texel.replace(old, "is_texel_buffer && !is_written", 1), negative=True)


if __name__ == "__main__":
    main()
