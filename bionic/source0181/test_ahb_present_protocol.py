#!/usr/bin/env python3
"""Run the actual AHB adapter against controlled Android/Vulkan boundaries.

Callbacks, FDs, transaction ordering, shared-session retirement and geometry run
through production methods. The driver/compositor are fixtures, not performance
or on-device validation. No Android or Vulkan binaries are substituted.
"""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


def block(text, marker):
    start=text.index(marker)
    opening=text.index("{",start)
    depth=0
    for end in range(opening,len(text)):
        depth+=(text[end]=="{")-(text[end]=="}")
        if not depth:return text[start:end+1]
    raise AssertionError(marker)


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <future>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <new>
#include <optional>
#include <poll.h>
#include <set>
#include <sstream>
#include <string>
#include <string_view>
#include <sys/eventfd.h>
#include <thread>
#include <type_traits>
#include <unistd.h>
#include <utility>
#include <vector>
using u32=uint32_t;using u64=uint64_t;
using namespace std::chrono_literals;
thread_local bool on_binder=false;
struct BinderScope{BinderScope(){assert(!on_binder);on_binder=true;}~BinderScope(){on_binder=false;}};
void Owner(){assert(!on_binder);}
std::mutex fd_mutex;
std::set<int> owned_fds;
int NewFence(bool signal=true){
    const int fd=eventfd(signal?1:0,EFD_CLOEXEC|EFD_NONBLOCK);assert(fd>=0);
    std::scoped_lock lock{fd_mutex};assert(owned_fds.insert(fd).second);return fd;
}
int MockClose(int fd){
    std::scoped_lock lock{fd_mutex};assert(owned_fds.erase(fd)==1);return ::close(fd);
}
bool OwnsFd(int fd){std::scoped_lock lock{fd_mutex};return owned_fds.contains(fd);}
size_t FdCount(){std::scoped_lock lock{fd_mutex};return owned_fds.size();}
unsigned poll_calls{};bool poll_interrupt{};
int MockPoll(pollfd* fds,nfds_t n,int timeout){
    Owner();++poll_calls;
    if(poll_interrupt){errno=EINTR;return -1;}
    return ::poll(fds,n,timeout);
}
std::string fail_stage;unsigned fail_nth=1;
std::map<std::string,unsigned> calls;
bool FailAt(std::string_view stage){
    Owner();const auto count=++calls[std::string(stage)];return fail_stage==stage&&count==fail_nth;
}
std::vector<std::string> logs;
template<class... A>void Log(int,const char* format,const A&...args){
    std::ostringstream out;out<<format;((out<<" "<<args),...);logs.push_back(out.str());
}
[[maybe_unused]] constexpr int Render_Vulkan=0;
#define LOG_INFO Log
#define LOG_WARNING Log
struct ARect{int32_t left{},top{},right{},bottom{};bool operator==(const ARect&)const=default;};
struct ANativeWindow{};
struct AHardwareBuffer{u32 width{},height{};unsigned refs=1;};
struct AHardwareBuffer_Desc{u32 width,height,layers,format;u64 usage;u32 stride,rfu0;u64 rfu1;};
constexpr u32 AHARDWAREBUFFER_FORMAT_R8G8B8A8_UNORM=1;
constexpr u64 AHARDWAREBUFFER_USAGE_GPU_COLOR_OUTPUT=1,AHARDWAREBUFFER_USAGE_GPU_SAMPLED_IMAGE=2,AHARDWAREBUFFER_USAGE_COMPOSER_OVERLAY=4;
constexpr int ASURFACE_TRANSACTION_VISIBILITY_HIDE=0,ASURFACE_TRANSACTION_VISIBILITY_SHOW=1,ASURFACE_TRANSACTION_TRANSPARENCY_OPAQUE=1;
unsigned live_ahbs{},live_controls{},live_txns{},control_arrays{},applies{};
void AHardwareBuffer_release(AHardwareBuffer* b){assert(b&&b->refs);if(!--b->refs){--live_ahbs;delete b;}}
int AHardwareBuffer_allocate(const AHardwareBuffer_Desc* d,AHardwareBuffer** out){
    if(FailAt("hardware_buffer"))return -1;
    assert(d->format==1&&d->layers==1&&d->usage==7);
    *out=new AHardwareBuffer{d->width,d->height};++live_ahbs;return 0;
}
struct ASurfaceControl{AHardwareBuffer* current{};bool live=true;};
std::vector<std::unique_ptr<ASurfaceControl>> controls_storage;
struct ASurfaceTransactionStats{ASurfaceControl* control{};size_t count=1;bool signaled=true;int queried_fd=-1;};
using AndroidCallback=void(*)(void*,ASurfaceTransactionStats*);
struct ASurfaceTransaction {
    ASurfaceControl* control{};AHardwareBuffer* buffer{};int fd=-1;
    ARect source,dest;AndroidCallback complete{},commit{};void* complete_ctx{};void* commit_ctx{};
};
struct Pending {
    ASurfaceControl* control{};AHardwareBuffer* previous{};
    AndroidCallback complete{},commit{};void* complete_ctx{};void* commit_ctx{};
    ARect source,dest;bool buffer{};
};
std::deque<Pending> pending;
bool inline_commit{};
ASurfaceControl* ASurfaceControl_createFromWindow(ANativeWindow*,const char*){
    if(FailAt("surface_control"))return nullptr;
    auto c=std::make_unique<ASurfaceControl>();auto*p=c.get();controls_storage.push_back(std::move(c));++live_controls;return p;
}
void ASurfaceControl_release(ASurfaceControl*c){Owner();assert(c&&c->live);c->live=false;--live_controls;}
ASurfaceTransaction* ASurfaceTransaction_create(){
    if(FailAt("transaction_create"))return nullptr;++live_txns;return new ASurfaceTransaction;
}
void ASurfaceTransaction_delete(ASurfaceTransaction*t){
    Owner();if(t->fd>=0)MockClose(t->fd);if(t->buffer)AHardwareBuffer_release(t->buffer);--live_txns;delete t;
}
void ASurfaceTransaction_setBuffer(ASurfaceTransaction*t,ASurfaceControl*c,AHardwareBuffer*b,int fd){
    Owner();assert(!t->buffer&&t->fd<0);t->control=c;t->buffer=b;t->fd=fd;if(b)++b->refs;
}
void ASurfaceTransaction_setVisibility(ASurfaceTransaction*t,ASurfaceControl*c,int){Owner();t->control=c;}
void ASurfaceTransaction_setGeometry(ASurfaceTransaction*t,ASurfaceControl*,const ARect&s,const ARect&d,int transform){
    Owner();assert(transform==0);t->source=s;t->dest=d;
}
void ASurfaceTransaction_setBufferTransparency(ASurfaceTransaction*,ASurfaceControl*,int){Owner();}
void ASurfaceTransaction_setOnComplete(ASurfaceTransaction*t,void*c,AndroidCallback fn){Owner();assert(!t->complete);t->complete=fn;t->complete_ctx=c;}
void ASurfaceTransaction_setOnCommit(ASurfaceTransaction*t,void*c,AndroidCallback fn){Owner();assert(!t->commit);t->commit=fn;t->commit_ctx=c;}
void ASurfaceTransaction_apply(ASurfaceTransaction*t){
    Owner();++applies;assert(t->control&&t->control->live);
    auto*old=t->control->current;t->control->current=std::exchange(t->buffer,nullptr);
    if(t->fd>=0){MockClose(t->fd);t->fd=-1;} // compositor owns the submitted acquire FD
    if(t->complete||t->commit){
        pending.push_back({t->control,old,t->complete,t->commit,t->complete_ctx,t->commit_ctx,t->source,t->dest,t->control->current!=nullptr});
        auto&p=pending.back();
        if(inline_commit&&p.commit){auto fn=std::exchange(p.commit,nullptr);BinderScope binder;fn(std::exchange(p.commit_ctx,nullptr),nullptr);}
    }else if(old)AHardwareBuffer_release(old);
}
void ASurfaceTransactionStats_getASurfaceControls(ASurfaceTransactionStats*s,ASurfaceControl***out,size_t*n){
    assert(on_binder);*n=s->count;
    if(*n){*out=new ASurfaceControl*[*n];std::fill(*out,*out+*n,s->control);++control_arrays;}else *out=nullptr;
}
int ASurfaceTransactionStats_getPreviousReleaseFenceFd(ASurfaceTransactionStats*s,ASurfaceControl*c){
    assert(on_binder&&c==s->control);s->queried_fd=s->signaled?-1:NewFence(false);return s->queried_fd;
}
void ASurfaceTransactionStats_releaseASurfaceControls(ASurfaceControl**p){assert(on_binder);delete[]p;--control_arrays;}
void FireCommit(size_t i){
    auto&p=pending.at(i);assert(p.commit);auto fn=std::exchange(p.commit,nullptr);
    BinderScope binder;fn(std::exchange(p.commit_ctx,nullptr),nullptr);
}
int FireComplete(size_t i,bool released=true,size_t count=1){
    auto&p=pending.at(i);assert(p.complete);auto fn=std::exchange(p.complete,nullptr);
    ASurfaceTransactionStats stats{p.control,count,released};
    {BinderScope binder;fn(std::exchange(p.complete_ctx,nullptr),&stats);}
    if(p.previous){AHardwareBuffer_release(p.previous);p.previous=nullptr;}
    return stats.queried_fd;
}
void FinishCallbacks(){
    for(size_t i=0;i<pending.size();++i){if(pending[i].commit)FireCommit(i);if(pending[i].complete)FireComplete(i);}
    pending.clear();
}
namespace vk {
enum class Result{eSuccess,eErrorUnknown};
template<int K>struct Handle{int id{};explicit operator bool()const{return id!=0;}bool operator==(const Handle&)const=default;};
using Image=Handle<1>;using DeviceMemory=Handle<2>;using ImageView=Handle<3>;using Semaphore=Handle<4>;
enum class Format{eR8G8B8A8Unorm,eB8G8R8A8Unorm,eUndefined};
enum class ImageLayout{eUndefined,eGeneral};
enum class ImageType{e2D};enum class ImageViewType{e2D};enum class ImageTiling{eOptimal};enum class SharingMode{eExclusive};
enum class SampleCountFlagBits{e1};
struct FormatFeatureFlagBits{static constexpr u32 eColorAttachment=1,eTransferSrc=2,eTransferDst=4,eBlitDst=8;};
struct MemoryPropertyFlagBits{static constexpr u32 eDeviceLocal=1;};
struct ImageUsageFlagBits{static constexpr u32 eColorAttachment=1,eTransferSrc=2,eTransferDst=4;};
struct ImageAspectFlagBits{static constexpr u32 eColor=1;};
struct ExternalMemoryHandleTypeFlagBits{static constexpr u32 eAndroidHardwareBufferANDROID=1;};
struct ExternalSemaphoreHandleTypeFlagBits{static constexpr u32 eSyncFd=1;};
struct SemaphoreImportFlagBits{static constexpr u32 eTemporary=1;};
struct ExternalSemaphoreFeatureFlagBits{static constexpr u32 eExportable=1,eImportable=2;};
enum class ColorSpaceKHR{eSrgbNonlinear,Other};
enum class SurfaceTransformFlagBitsKHR{eIdentity,Other};
enum class PresentModeKHR{eFifo,eMailbox,eImmediate};
enum class CompositeAlphaFlagBitsKHR{eOpaque};
std::string to_string(PresentModeKHR p){return p==PresentModeKHR::eFifo?"fifo":"newest";}
struct Extent2D{u32 width,height;};struct Extent3D{u32 width,height,depth;};
struct SurfaceFormatKHR{Format format=Format::eR8G8B8A8Unorm;ColorSpaceKHR colorSpace=ColorSpaceKHR::eSrgbNonlinear;};
struct AndroidHardwareBufferPropertiesANDROID{u64 allocationSize=4096;u32 memoryTypeBits=3;};
struct AndroidHardwareBufferFormatPropertiesANDROID{Format format=Format::eR8G8B8A8Unorm;u32 formatFeatures=15;};
struct PropsChain{
 AndroidHardwareBufferPropertiesANDROID allocation;AndroidHardwareBufferFormatPropertiesANDROID format;
 template<class T>T&get(){if constexpr(std::is_same_v<T,AndroidHardwareBufferPropertiesANDROID>)return allocation;else return format;}
};
struct ExternalMemoryImageCreateInfo{u32 handleTypes;};
struct ImageCreateInfo{const void*pNext;ImageType imageType;Format format;Extent3D extent;u32 mipLevels,arrayLayers;SampleCountFlagBits samples;ImageTiling tiling;u32 usage;SharingMode sharingMode;ImageLayout initialLayout;};
struct MemoryDedicatedAllocateInfo{Image image;};
struct ImportAndroidHardwareBufferInfoANDROID{const void*pNext;AHardwareBuffer*buffer;};
struct MemoryAllocateInfo{const void*pNext;u64 allocationSize;u32 memoryTypeIndex;};
struct SubresourceRange{u32 aspectMask,baseMipLevel{},levelCount,baseArrayLayer{},layerCount;};
struct ImageViewCreateInfo{Image image;ImageViewType viewType;Format format;SubresourceRange subresourceRange;};
struct ExportSemaphoreCreateInfo{u32 handleTypes;};struct SemaphoreCreateInfo{const void*pNext{};};
struct ImportSemaphoreFdInfoKHR{Semaphore semaphore;u32 flags,handleType;int fd;};
struct SemaphoreGetFdInfoKHR{Semaphore semaphore;u32 handleType;};
struct MemoryProperties{u32 memoryTypeCount=2;struct MemoryType{u32 propertyFlags;}memoryTypes[2]={{0},{1}};};
}
int next_handle=1;std::set<int> live_images,live_memory,live_views,live_semaphores,exportable;
bool bad_format{},bad_features{},bad_memory_type{},import_fails{},export_fails{};
unsigned imported{},exported{};
struct Device {
 template<class A,class B>std::pair<vk::Result,vk::PropsChain>getAndroidHardwareBufferPropertiesANDROID(AHardwareBuffer&)const{
  vk::PropsChain chain;if(bad_format)chain.format.format=vk::Format::eUndefined;
  if(bad_features)chain.format.formatFeatures=0;if(bad_memory_type)chain.allocation.memoryTypeBits=0;
  return {FailAt("ahb_properties")?vk::Result::eErrorUnknown:vk::Result::eSuccess,chain};
 }
 std::pair<vk::Result,vk::Image>createImage(const vk::ImageCreateInfo&i)const{
  if(FailAt("image_create"))return {vk::Result::eErrorUnknown,{}};
  assert(i.format==vk::Format::eR8G8B8A8Unorm&&i.mipLevels==1&&i.arrayLayers==1&&i.usage==7);
  const auto*ext=static_cast<const vk::ExternalMemoryImageCreateInfo*>(i.pNext);assert(ext&&ext->handleTypes==1);
  const int id=next_handle++;live_images.insert(id);return {vk::Result::eSuccess,{id}};
 }
 std::pair<vk::Result,vk::DeviceMemory>allocateMemory(const vk::MemoryAllocateInfo&i)const{
  if(FailAt("memory_allocate"))return {vk::Result::eErrorUnknown,{}};
  const auto*imp=static_cast<const vk::ImportAndroidHardwareBufferInfoANDROID*>(i.pNext);assert(imp&&imp->buffer);
  const auto*dedicated=static_cast<const vk::MemoryDedicatedAllocateInfo*>(imp->pNext);assert(live_images.contains(dedicated->image.id));
  assert(i.memoryTypeIndex==1);int id=next_handle++;live_memory.insert(id);return {vk::Result::eSuccess,{id}};
 }
 vk::Result bindImageMemory(vk::Image i,vk::DeviceMemory m,u64 offset)const{
  assert(live_images.contains(i.id)&&live_memory.contains(m.id)&&offset==0);
  return FailAt("image_bind")?vk::Result::eErrorUnknown:vk::Result::eSuccess;
 }
 std::pair<vk::Result,vk::ImageView>createImageView(const vk::ImageViewCreateInfo&i)const{
  if(FailAt("view_create"))return {vk::Result::eErrorUnknown,{}};
  assert(live_images.contains(i.image.id));int id=next_handle++;live_views.insert(id);return {vk::Result::eSuccess,{id}};
 }
 std::pair<vk::Result,vk::Semaphore>createSemaphore(const vk::SemaphoreCreateInfo&i)const{
  if(FailAt(i.pNext?"ready_semaphore":"acquire_semaphore"))return {vk::Result::eErrorUnknown,{}};
  int id=next_handle++;live_semaphores.insert(id);if(i.pNext)exportable.insert(id);return {vk::Result::eSuccess,{id}};
 }
 void destroySemaphore(vk::Semaphore h)const{Owner();assert(live_semaphores.erase(h.id)==1);exportable.erase(h.id);}
 void destroyImageView(vk::ImageView h)const{Owner();assert(live_views.erase(h.id)==1);}
 void destroyImage(vk::Image h)const{Owner();assert(live_images.erase(h.id)==1);}
 void freeMemory(vk::DeviceMemory h)const{Owner();assert(live_memory.erase(h.id)==1);}
 vk::Result importSemaphoreFdKHR(const vk::ImportSemaphoreFdInfoKHR&i)const{
  Owner();++imported;assert(live_semaphores.contains(i.semaphore.id)&&i.flags==1&&i.handleType==1&&OwnsFd(i.fd));
  if(import_fails)return vk::Result::eErrorUnknown;MockClose(i.fd);return vk::Result::eSuccess;
 }
 std::pair<vk::Result,int>getSemaphoreFdKHR(const vk::SemaphoreGetFdInfoKHR&i)const{
  Owner();++exported;assert(exportable.contains(i.semaphore.id)&&i.handleType==1);
  if(export_fails)return {vk::Result::eErrorUnknown,-1};return {vk::Result::eSuccess,NewFence()};
 }
};
struct PhysicalDevice{vk::MemoryProperties getMemoryProperties()const{Owner();return {};}};
namespace Vulkan {
struct Instance{
 bool supported=true;Device GetDevice()const{return {};}PhysicalDevice GetPhysicalDevice()const{return {};}
 bool SupportsAndroidAhbPresent()const{return supported;}
};
}
namespace Common {struct ElfInfo{
 std::string serial="CUSA00785";static ElfInfo&Instance(){static ElfInfo i;return i;}
 std::string_view GameSerial()const{return serial;}
};}
#define close MockClose
#define poll MockPoll
@RELEASE_SLOTS@
@ADAPTER@
#undef close
#undef poll
@POLICY@
namespace Vulkan {
struct Swapchain {
 const Instance&instance;struct Window{struct Info{void*render_surface;};ANativeWindow native;
 Info GetWindowInfo(){return {&native};}}window;
 bool ahb_disabled{},needs_hdr{};u32 width=2688,height=1216,game_width=1280,game_height=720,image_count{},image_index{},frame_index{};
 vk::Extent2D extent{width,height};vk::SurfaceFormatKHR surface_format;
 vk::SurfaceTransformFlagBitsKHR transform=vk::SurfaceTransformFlagBitsKHR::eIdentity;
 vk::PresentModeKHR present_mode=vk::PresentModeKHR::eFifo;
 vk::CompositeAlphaFlagBitsKHR composite_alpha=vk::CompositeAlphaFlagBitsKHR::eOpaque;
 std::unique_ptr<AndroidAhbPresent>ahb;unsigned wsi_creates{},wsi_acquires{},wsi_presents{};
 explicit Swapchain(const Instance&i):instance(i){}
 void Create(){
 @SWAPCHAIN_CREATE@
 ++wsi_creates;
 }
 bool AcquireNextImage(){
 @SWAPCHAIN_ACQUIRE@
 ++wsi_acquires;return true;
 }
 bool Present(){
 @SWAPCHAIN_PRESENT@
 ++wsi_presents;return true;
 }
 void Recreate(){ahb.reset();extent={width,height};Create();}
};
}
bool ActualCapabilities(bool ahb_mem,bool ahb_foreign,bool ahb_sync,u32 features){
 struct {u32 externalSemaphoreFeatures;}sync_props{features};
 const auto sync_required=vk::ExternalSemaphoreFeatureFlagBits::eExportable|vk::ExternalSemaphoreFeatureFlagBits::eImportable;
 bool android_ahb_present{};
 @CAPABILITIES@
 return android_ahb_present;
}
void Reset(){
 FinishCallbacks();
 assert(live_images.empty()&&live_memory.empty()&&live_views.empty()&&live_semaphores.empty());
 assert(live_ahbs==0&&live_controls==0&&live_txns==0&&control_arrays==0&&FdCount()==0);
 for(const auto&c:controls_storage)assert(!c->live&&!c->current);
 controls_storage.clear();calls.clear();fail_stage.clear();fail_nth=1;
 bad_format=bad_features=bad_memory_type=import_fails=export_fails=poll_interrupt=inline_commit=false;
 poll_calls=imported=exported=applies=0;logs.clear();unsetenv("BACHATA_AHB_PRESENT");
 Common::ElfInfo::Instance().serial="CUSA00785";
}
std::unique_ptr<Vulkan::AndroidAhbPresent>Create(Vulkan::Instance&i,bool fifo=true,u32 w=1280,u32 h=720,u32 dw=2688,u32 dh=1216){
 static ANativeWindow window;auto p=std::make_unique<Vulkan::AndroidAhbPresent>(i);
 assert(p->Create(&window,w,h,dw,dh,fifo));return p;
}
u32 Frame(Vulkan::AndroidAhbPresent&p){u32 id=99;assert(p.Acquire(id,100ms));assert(p.Present(id));return id;}
'''

TESTS = r'''
void FifoTest(){
 Reset();Vulkan::Instance i;auto p=Create(i);assert(Frame(*p)==0);
 u32 next=99;auto f=std::async(std::launch::async,[&]{return p->Acquire(next,300ms);});
 assert(f.wait_for(10ms)==std::future_status::timeout);
 FireCommit(0);
 assert(f.wait_for(100ms)==std::future_status::ready&&f.get());assert(next==1);
 assert(pending[0].complete); // did not wait for OnComplete / present fence
 assert(p->Present(next));assert(pending.size()==2);
 FireCommit(1);assert(Frame(*p)==2);FireCommit(2);
 // A committed transaction does not release any buffer. All three remain busy.
 u32 reused=99;auto wait=std::async(std::launch::async,[&]{return p->Acquire(reused,300ms);});
 assert(wait.wait_for(10ms)==std::future_status::timeout);
 const int fd=FireComplete(1,false); // transaction1 replaced slot0
 assert(wait.wait_for(100ms)==std::future_status::ready&&wait.get());
 assert(reused==0&&p->Acquired(reused)&&!OwnsFd(fd)&&imported==1);
 p.reset();Reset();
}
void CompleteDoesNotGate(){
 Reset();Vulkan::Instance i;auto p=Create(i);Frame(*p);
 // Exercise independent dispatch deterministically; even an early completion
 // is not permission to bypass the registered commit token.
 FireComplete(0);u32 next=99;
 auto f=std::async(std::launch::async,[&]{return p->Acquire(next,300ms);});
 assert(f.wait_for(10ms)==std::future_status::timeout);FireCommit(0);
 assert(f.wait_for(100ms)==std::future_status::ready&&f.get());p.reset();Reset();
}
void NewestTest(){
 Reset();Vulkan::Instance i;auto p=Create(i,false);
 assert(Frame(*p)==0&&Frame(*p)==1&&Frame(*p)==2);
 for(const auto&t:pending)assert(!t.commit);
 FireComplete(1);u32 next=99;assert(p->Acquire(next,0ms)&&next==0&&!p->Acquired(next));
 assert(imported==0);p.reset();Reset();
}
void SessionTest(){
 Reset();Vulkan::Instance i;auto old=Create(i);Frame(*old);FireCommit(0);Frame(*old);old.reset();
 auto fresh=Create(i);Frame(*fresh);const size_t current=2;
 FireCommit(1); // old instance cannot open the new instance's commit gate
 u32 next=99;auto f=std::async(std::launch::async,[&]{return fresh->Acquire(next,300ms);});
 assert(f.wait_for(10ms)==std::future_status::timeout);
 const int fd=FireComplete(1,false);assert(fd>=0&&!OwnsFd(fd));
 FireCommit(current);assert(f.wait_for(100ms)==std::future_status::ready&&f.get());
 fresh.reset();Reset();
}
void StateTest(){
 Reset();using State=Vulkan::AndroidAhbPresent::State;
 auto state=std::make_shared<State>();assert(state->Begin(true)==1);state->Committed(1);
 assert(state->Begin(true)==2);state->Committed(1);
 assert(!state->WaitForCommit(Vulkan::AndroidAhbPresent::Clock::now()));
 auto wait=std::async(std::launch::async,[&]{return state->WaitForCommit(Vulkan::AndroidAhbPresent::Clock::now()+500ms);});
 assert(wait.wait_for(10ms)==std::future_status::timeout);state->Retire("test_retire");
 assert(wait.wait_for(100ms)==std::future_status::ready&&!wait.get());
 state->Committed(2);assert(!state->WaitForCommit(Vulkan::AndroidAhbPresent::Clock::now()));
 state.reset();Reset();
}
void InlineCommitTest(){
 Reset();inline_commit=true;Vulkan::Instance i;auto p=Create(i);Frame(*p);
 u32 next=99;assert(p->Acquire(next,0ms)&&next==1);p.reset();Reset();
}
@AHB_CONTENT_FIT@
void GeometryTest(){
 Reset();using A=Vulkan::AndroidAhbPresent;
 assert((A::FitDestination(1280,720,2688,1216)==ARect{263,0,2424,1216}));
 assert((A::FitDestination(1920,1080,1920,1080)==ARect{0,0,1920,1080}));
 assert((A::FitDestination(1280,720,1080,1920)==ARect{0,656,1080,1263}));
 // Reproduce both stages of the fit, including the reported ultrawide display.
 for(const auto& display:std::array<std::pair<float,float>,5>{
         {{2688,1216},{2048,926},{1920,1080},{1080,1920},{2560,1440}}}){
  const float sx=1280.0f/display.first,sy=720.0f/display.second;
  const auto size=BachataFitAhbContent(1280,720,display.first,display.second,sx,sy);
  assert(std::abs(size.first-display.first)<0.01f&&std::abs(size.second-display.second)<0.01f);
  const auto rect=A::FitDestination(1280,720,static_cast<u32>(display.first),static_cast<u32>(display.second));
  const float output_w=(size.first/display.first)*(rect.right-rect.left);
  const float output_h=(size.second/display.second)*(rect.bottom-rect.top);
  assert(std::abs(output_w-output_h*16.0f/9.0f)<=2.0f);
  const auto splash=BachataFitAhbContent(640,480,display.first,display.second,sx,sy);
  assert(std::abs(splash.first*sx-(splash.second*sy)*4.0f/3.0f)<0.01f);
  assert(std::abs(splash.second-display.second)<0.01f&&splash.first<display.first);
 }
 const auto partial=BachataFitAhbContent(1280,720,2000,800,1280.0f/2688,720.0f/1216);
 assert(partial.first<=2000&&partial.second<=800);
 assert(std::abs(partial.first*(1280.0f/2688)-partial.second*(720.0f/1216)*16.0f/9.0f)<0.01f);
 unsigned count=0;
 for(u32 w:{1u,720u,1280u,8192u,static_cast<u32>(INT32_MAX)})
 for(u32 h:{1u,480u,720u,8192u,static_cast<u32>(INT32_MAX)})
 for(u32 dw:{1u,1080u,2688u,static_cast<u32>(INT32_MAX)})
 for(u32 dh:{1u,1216u,1920u,static_cast<u32>(INT32_MAX)}){
  const auto r=A::FitDestination(w,h,dw,dh);
  assert(r.left>=0&&r.top>=0&&r.right>r.left&&r.bottom>r.top);
  assert(u32(r.right)<=dw&&u32(r.bottom)<=dh);
  assert(std::abs(int64_t{r.left}-(int64_t{dw}-r.right))<=1);
  assert(std::abs(int64_t{r.top}-(int64_t{dh}-r.bottom))<=1);++count;
 }
 Vulkan::Instance i;auto p=Create(i);Frame(*p);
 assert((pending.back().source==ARect{0,0,1280,720}));
 assert((pending.back().dest==ARect{263,0,2424,1216}));p.reset();Reset();
 std::cout<<"AHB_GEOMETRY_PASS cases="<<count<<"\n";
}
void ImportTest(){
 for(int mode=0;mode<4;++mode){
  Reset();Vulkan::Instance i;auto p=Create(i,false);Frame(*p);Frame(*p);Frame(*p);
  int fd=FireComplete(1,false);assert(OwnsFd(fd));import_fails=true;
  if(mode==0){u64 one=1;assert(write(fd,&one,sizeof(one))==sizeof(one));}
  if(mode==2)poll_interrupt=true;
  if(mode==3){MockClose(fd); // replace with invalid but owned descriptor to test POLLNVAL
    std::scoped_lock lock{fd_mutex};owned_fds.insert(fd);}
  u32 id=99;const bool ready=p->Acquire(id,0ms);
  assert(ready==(mode==0));assert(!OwnsFd(fd)&&imported==1&&poll_calls==1);
  if(ready)assert(!p->Acquired(id));else assert(std::string_view(p->FailureReason())=="release_fence_wait");
  p.reset();Reset();
 }
}
void FailureTest(){
 for(const auto stage:{"surface_control","hardware_buffer","ahb_properties","image_create","memory_allocate","image_bind","view_create","acquire_semaphore","ready_semaphore"})
 for(unsigned nth:{1u,2u,3u}){
  if(std::string_view(stage)=="surface_control"&&nth>1)continue;
  Reset();fail_stage=stage;fail_nth=nth;Vulkan::Instance i;ANativeWindow w;
  {Vulkan::AndroidAhbPresent p(i);assert(!p.Create(&w,1280,720,2688,1216,true));assert(std::string_view(p.FailureReason())==stage);}
  Reset();
 }
 for(int mode=0;mode<3;++mode){
  Reset();bad_format=mode==0;bad_features=mode==1;bad_memory_type=mode==2;
  Vulkan::Instance i;ANativeWindow w;{Vulkan::AndroidAhbPresent p(i);assert(!p.Create(&w,1280,720,2688,1216,true));}
  Reset();
 }
 for(int stage=0;stage<2;++stage){
  Reset();Vulkan::Instance i;auto p=Create(i);u32 idx;assert(p->Acquire(idx,0ms));
  if(stage==0)export_fails=true;else{fail_stage="transaction_create";fail_nth=calls[fail_stage]+1;}
  assert(!p->Present(idx));assert(FdCount()==0);p.reset();Reset();
 }
 for(bool fifo:{false,true}){
  Reset();Vulkan::Instance i;auto p=Create(i,fifo);Frame(*p);
  if(!fifo){Frame(*p);Frame(*p);}
  u32 idx=99;assert(!p->Acquire(idx,0ms));
  assert(std::string_view(p->FailureReason())==(fifo?"commit_timeout":"release_timeout"));
  p.reset();Reset();
 }
 Reset();Vulkan::Instance i;auto p=Create(i,false);Frame(*p);Frame(*p);FireComplete(1,true,2);
 u32 idx=99;assert(!p->Acquire(idx,0ms)&&std::string_view(p->FailureReason())=="release_identity");
 p.reset();Reset();
}
void PolicyTest(){
 Reset();
 for(const auto serial:{"CUSA00785","CUSA08809","CUSA08034","CUSA00004","OTHER"})
 for(const char*opt:{static_cast<const char*>(nullptr),"0","1","","true","10"}){
  Common::ElfInfo::Instance().serial=serial;if(opt)setenv("BACHATA_AHB_PRESENT",opt,1);else unsetenv("BACHATA_AHB_PRESENT");
  const bool title=std::string_view(serial)=="CUSA00785"||std::string_view(serial)=="CUSA08809"||std::string_view(serial)=="CUSA08034";
  assert(BachataAhbTarget()==(title&&(!opt||std::string_view(opt)=="1")));
 }
 for(unsigned ext=0;ext<8;++ext)for(unsigned flags=0;flags<4;++flags)
  assert(ActualCapabilities(ext&1,ext&2,ext&4,flags)==(ext==7&&flags==3));
 Reset();Vulkan::Instance i;
 for(int reason=0;reason<7;++reason){
  {Vulkan::Swapchain s(i);
   switch(reason){case 0:setenv("BACHATA_AHB_PRESENT","0",1);break;case 1:s.ahb_disabled=true;break;
    case 2:s.needs_hdr=true;break;case 3:s.surface_format.format=vk::Format::eB8G8R8A8Unorm;break;
    case 4:s.surface_format.colorSpace=vk::ColorSpaceKHR::Other;break;case 5:s.transform=vk::SurfaceTransformFlagBitsKHR::Other;break;
    case 6:i.supported=false;break;}
   s.Create();assert(!s.ahb&&s.wsi_creates==1&&calls["surface_control"]==0);
   assert(!logs.empty()&&logs.back().find("wsi")!=std::string::npos);
  }i.supported=true;Reset();
 }
 {Vulkan::Swapchain s(i);s.Create();assert(s.ahb&&s.image_count==3&&s.extent.width==1280&&s.extent.height==720);
  assert(s.AcquireNextImage()&&s.Present());FireCommit(0);assert(s.AcquireNextImage());
  export_fails=true;assert(!s.Present()&&s.ahb_disabled);s.Recreate();assert(!s.ahb&&s.wsi_creates==1&&s.AcquireNextImage());}
 Reset();
 {fail_stage="image_bind";Vulkan::Swapchain s(i);s.Create();assert(!s.ahb&&s.ahb_disabled&&s.wsi_creates==1);}
 Reset();
 {Vulkan::Swapchain s(i);s.present_mode=vk::PresentModeKHR::eMailbox;s.Create();assert(s.ahb);
  assert(s.AcquireNextImage()&&s.Present());assert(s.AcquireNextImage()&&s.Present());FireComplete(1,true,2);
  assert(!s.AcquireNextImage()&&s.ahb_disabled);s.Recreate();assert(!s.ahb&&s.wsi_creates==1);}
 Reset();
}
int main(int argc,char**argv){
 const std::string only=argc>1?argv[1]:"";
 if(only.empty()||only=="fifo"){FifoTest();CompleteDoesNotGate();InlineCommitTest();}
 if(only.empty()||only=="newest")NewestTest();
 if(only.empty()||only=="session"){SessionTest();StateTest();}
 if(only.empty()||only=="geometry")GeometryTest();
 if(only.empty()||only=="import")ImportTest();
 if(only.empty()||only=="failure")FailureTest();
 if(only.empty()||only=="policy")PolicyTest();
 std::cout<<"AHB_PRESENT_PROTOCOL_PASS actual_commit_release_fds_lifetime_create_geometry_fallback\n";
}
'''


def program(source):
    base=source/"src/video_core/renderer_vulkan"
    h=(base/"vk_ahb_present.h").read_text()
    slots=(base/"ahb_release_slots.h").read_text()
    swap=(base/"vk_swapchain.cpp").read_text()
    presenter=(base/"vk_presenter.cpp").read_text()
    assert "BACHATA_AHB_CONTENT_FIT" in presenter and "swapchain.PresentLayout() == vk::ImageLayout::eGeneral" in presenter
    instance=(base/"vk_instance.cpp").read_text()
    # Access visibility is the only adapter change: the state/fit unit cases use
    # the exact nested class methods without mirroring their implementation.
    adapter=h[h.index("namespace Vulkan {"):h.rindex("#endif")]
    adapter=adapter.replace("class AndroidAhbPresent {","struct AndroidAhbPresent {",1)
    adapter=adapter.replace("private:","public:")
    create=block(swap,"void Swapchain::Create(")
    create=create[create.index("#ifdef __ANDROID__")+len("#ifdef __ANDROID__"):create.index("#endif")]
    def arm(name):
        method=block(swap,name)
        return method[method.index("#ifdef __ANDROID__")+len("#ifdef __ANDROID__"):method.index("#endif")]
    start=instance.index("    android_ahb_present=ahb_mem&&ahb_foreign&&ahb_sync&&")
    caps=instance[start:instance.index(";",start)+1]
    values={"RELEASE_SLOTS":slots[slots.index("namespace BachataAhb {"):],"ADAPTER":adapter,
            "POLICY":block(swap,"static const char* BachataAhbPolicyBlockReason(){")+"\n"+block(swap,"static bool BachataAhbTarget(){"),
            "SWAPCHAIN_CREATE":create,"SWAPCHAIN_ACQUIRE":arm("bool Swapchain::AcquireNextImage()"),
            "SWAPCHAIN_PRESENT":arm("bool Swapchain::Present()"),"CAPABILITIES":caps,
            "AHB_CONTENT_FIT":block(presenter,"static std::pair<float,float> BachataFitAhbContent(")}
    text=PREAMBLE+TESTS
    for key,value in values.items():text=text.replace("@"+key+"@",value)
    assert "@" not in text
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--positive-only",action="store_true")
    args=parser.parse_args()
    code=program(args.source)
    compiler=shlex.split(os.environ.get("CXX","c++"))
    with tempfile.TemporaryDirectory(prefix="bachata-ahb-protocol-") as directory:
        temp=Path(directory)
        def run(name,text,only="",negative=False):
            src=temp/(name+".cpp");exe=temp/name;src.write_text(text)
            built=subprocess.run(compiler+["-std=c++23","-O1","-g","-pthread","-Wall","-Wextra","-Werror",
                "-Wno-misleading-indentation","-Wno-unused-parameter","-Wno-missing-field-initializers",
                "-Wunused-const-variable","-fsanitize=undefined","-fno-sanitize-recover=all",str(src),"-o",str(exe)],
                text=True,capture_output=True)
            assert built.returncode==0,name+" must compile before runtime validation:\n"+built.stderr
            result=subprocess.run([str(exe)]+([only] if only else []),text=True,capture_output=True,timeout=15)
            if negative:
                assert result.returncode!=0,name+" negative passed"
                assert "Assertion" in result.stderr or "runtime error" in result.stderr,(name,result.stdout,result.stderr)
                print("AHB_NEGATIVE_REJECTED",name,flush=True)
            else:
                assert result.returncode==0,(name,result.stdout,result.stderr)
                print(result.stdout,end="",flush=True)
        run("positive",code)
        if args.positive_only:return
        mutations={
            "skip_commit_wait":("if (!state->WaitForCommit(deadline))","if (false)","fifo"),
            "no_commit_progress":("ctx->state->Committed(ctx->sequence);","(void)ctx;","fifo"),
            "stale_commit":("!retired && pending == value","!retired && value != 0","session"),
            "no_retirement":("            releases.Retire();","            (void)releases;","session"),
            "double_content_fit":("const float fit = std::min(content_w*scale_x/game_w,content_h*scale_y/game_h);","scale_x=scale_y=1.0f; const float fit = std::min(content_w*scale_x/game_w,content_h*scale_y/game_h);","geometry"),
            "stretch_geometry":("const ARect dst=FitDestination(width,height,destination_width,destination_height);","const ARect dst{0,0,static_cast<int32_t>(destination_width),static_cast<int32_t>(destination_height)};","geometry"),
            "double_close_import":("slot.imported=true;return true; // Vulkan owns fd only after success.","close(next->fence);slot.imported=true;return true; // Vulkan owns fd only after success.","fifo"),
            "leak_failed_import":("        close(next->fence);\n        if(result>0", "        if(result>0", "import"),
            "reuse_unsignaled":("if(result>0&&(p.revents&POLLIN)&&!(p.revents&(POLLERR|POLLNVAL)))return true;","if(result>=-1)return true;","import"),
            "ignore_opt_out":('if(opt[0]==\'0\'&&opt[1]==\'\\0\')return "opt_out";','if(opt[0]==\'0\'&&opt[1]==\'\\0\')return nullptr;',"policy"),
            "partial_view_leak":("            if(s.view)dev.destroyImageView(s.view);","            (void)s.view;","failure"),
            "missing_foreign_capability":("android_ahb_present=ahb_mem&&ahb_foreign&&ahb_sync&&","android_ahb_present=ahb_mem&&(ahb_foreign||true)&&ahb_sync&&","policy"),
        }
        for name,(old,new,only) in mutations.items():
            assert code.count(old)==1,(name,code.count(old))
            run(name,code.replace(old,new,1),only,True)
        print("AHB_PRESENT_PROTOCOL_SUITE_PASS negatives="+str(len(mutations)),flush=True)


if __name__=="__main__":main()
