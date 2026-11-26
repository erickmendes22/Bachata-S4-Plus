#!/usr/bin/env python3
"""Execute real frame acquisition, CP callback and VideoOut ownership methods.

Vulkan/WSI are boundaries. Their fences become ready only when the simulated
command producer submits the dependency; vblank waits are satisfied only by
the real PresentThread advancing it. Negative builds restore the deadlocks,
reordering, duplicate completion and unsafe callback lifetime.
"""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile


def block(text, anchor):
    start = text.index(anchor)
    brace = text.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


PREFIX = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <deque>
#include <functional>
#include <future>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <queue>
#include <semaphore>
#include <span>
#include <string>
#include <thread>
#include <vector>
using u8=uint8_t;using u32=uint32_t;using u64=uint64_t;
using s32=int32_t;using s64=int64_t;using VAddr=uint64_t;
using namespace std::chrono_literals;
#define ASSERT_MSG(x,...) assert(x)
#define ASSERT(x) assert(x)
#define UNREACHABLE_MSG(...) std::abort()
#define LOG_INFO(...) ((void)0)
#define LOG_DEBUG(...) ((void)0)
#define LOG_ERROR(...) ((void)0)
std::atomic<unsigned> reports{0},diagnostics{0};
std::mutex swap_start_mutex;
std::condition_variable swap_start_cv;
bool pause_swap_start=false,swap_start_entered=false,release_swap_start=false;
#define LOG_WARNING(...) (++diagnostics)
#define FRAME_END ((void)0)
namespace Platform::Bachata {void ReportPresentedFrame(){++reports;}}
namespace Common {
struct ElfInfo {
    std::string serial="CUSA08809";
    static ElfInfo& Instance(){static ElfInfo e;return e;}
    const std::string& GameSerial()const{return serial;}
};
template<class R,class... A>using UniqueFunction=std::function<R(A...)>;
void SetCurrentThreadName(const char* name){
    if(std::string_view(name)!="shadPS4:SwapPresent")return;
    std::unique_lock l{swap_start_mutex};
    if(pause_swap_start){swap_start_entered=true;swap_start_cv.notify_all();
        swap_start_cv.wait(l,[]{return release_swap_start;});}
}
void SetCurrentThreadRealtime(std::chrono::nanoseconds){}
struct AccurateTimer {
    std::chrono::nanoseconds period;std::chrono::steady_clock::time_point start;
    explicit AccurateTimer(std::chrono::nanoseconds p):period(p){}
    void Start(){start=std::chrono::steady_clock::now();}
    void End(){std::this_thread::sleep_until(start+period);}
    std::chrono::nanoseconds GetTotalWait(){return 0ns;}
};
}
#include "common/present_queue_progress.h"
@@PACING@@
namespace ImGui::Core {bool MustKeepDrawing(){return false;}}
struct Settings {u32 GetVblankFrequency(){return 1000;}} EmulatorSettings;
struct Debug {bool IsGuestThreadsPaused(){return false;}} DebugState;
namespace Libraries::Kernel {
using OrbisKernelEqueue=int;
struct OrbisKernelEvent {enum class Filter{VideoOut};};
std::atomic<unsigned> flip_events{0};
struct Equeue {template<class...A>void TriggerEvent(A...){++flip_events;}template<class...A>void RemoveEvent(A...){}};
Equeue* GetEqueue(int id){static Equeue queue;return id==1?&queue:nullptr;}
u64 sceKernelGetProcessTime(){return 1;}
u64 sceKernelReadTsc(){return 1;}
void ReportEventFlagWaits(){} // The event-flag gate exercises the real bounded census.
}
namespace Libraries::VideoOut {
enum class OrbisVideoOutInternalEventId{Flip,Vblank};
struct SceVideoOutResolutionStatus{u32 full_width{},full_height{},pane_width{},pane_height{};};
struct SceVideoOutVblankStatus{u64 count{},process_time{},tsc{};};
struct FlipStatus{u64 count{},process_time{},tsc{},submit_tsc{};s64 flip_arg{};
    int current_buffer{},gc_queue_num{},flip_pending_num{};};
constexpr int ORBIS_VIDEO_OUT_ERROR_RESOURCE_BUSY=-1;
}
#include "core/libraries/videoout/buffer.h"
namespace Vulkan {struct Frame;}
#define private public
#include "core/libraries/videoout/driver.h"
#undef private
namespace AmdGpu {
enum class TileMode{Display2DThin,DisplayLinearAligned};
enum class ImageType{Color2D};
TileMode GetArrayMode(TileMode m){return m;}
struct Liverpool {
    static inline thread_local bool draw=false;
    static inline thread_local bool cp=false;
    std::thread::id gpu_id{};
    std::mutex submit_mutex;
    std::condition_variable submit_cv;
    std::atomic<unsigned> num_commands{0},num_submits{0};
    std::atomic<bool> submit_done{false};
    std::queue<std::function<void()>> command_queue;
    bool cp_progress=false,draw_snapshot_valid=false;
    bool OnDrawThread()const{return draw;}
    std::thread::id GetGpuCommandProcessorThread()const{return cp?std::this_thread::get_id():std::thread::id{};}
    void DrainDrawQueue(){}
    void SetVoPort(Libraries::VideoOut::VideoOutPort*){}
    @@PENDING_CP@@
    @@SEND@@
    void ProcessCommands();
    void Pump(){cp=true;gpu_id=std::this_thread::get_id();ProcessCommands();cp=false;gpu_id={};}
};
@@COMMANDS@@
}
std::unique_ptr<AmdGpu::Liverpool> liverpool;
namespace vk {
enum class Result {eSuccess,eTimeout,eErrorDeviceLost};
std::string to_string(Result){return "mock";}
struct Fence{std::atomic<bool> ready{true};};
struct Semaphore{std::atomic<u64> value{1};};
struct SemaphoreWaitInfo{u32 semaphoreCount;Semaphore** pSemaphores;u64* pValues;};
std::atomic<unsigned> gpu_blocking_waits{0};
std::atomic<unsigned> ready_waits{0};
std::atomic<unsigned> submission_waits{0};
struct Device {
    Result waitForFences(Fence* fence,bool,u64 timeout)const {
        if (fence->ready.load()) return Result::eSuccess;
        if (timeout==0) return Result::eTimeout;
        ++gpu_blocking_waits;
        // A blocking call on either producer would prevent the next command
        // from submitting the very dependency needed by this fence.
        assert(!AmdGpu::Liverpool::draw && !AmdGpu::Liverpool::cp);
        return Result::eTimeout;
    }
    Result waitSemaphores(const SemaphoreWaitInfo& wait,u64)const{
        assert(!AmdGpu::Liverpool::draw && !AmdGpu::Liverpool::cp);
        ++ready_waits;
        const auto deadline=std::chrono::steady_clock::now()+1500ms;
        while((*wait.pSemaphores)->value.load()<*wait.pValues){
            assert(std::chrono::steady_clock::now()<deadline);std::this_thread::yield();
        }
        return Result::eSuccess;
    }
};
}
struct GuardedCV:std::condition_variable {
    template<class L,class P>void wait(L& l,P p){
        assert(p() || (!AmdGpu::Liverpool::draw && !AmdGpu::Liverpool::cp));
        std::condition_variable::wait(l,p);
    }
};
std::mutex preparation_mutex;
std::condition_variable preparation_cv;
bool block_preparation=false,preparation_entered=false,release_preparation=false;
namespace VideoCore {
using Libraries::VideoOut::TilingMode;
using VideoOutFormat=Libraries::VideoOut::PixelFormat;
VideoOutFormat ConvertPixelFormat(VideoOutFormat f){return f;}
struct ImageInfo {
    struct Props{bool is_tiled{};}props;
    AmdGpu::TileMode tile_mode{},array_mode{};
    AmdGpu::ImageType type{};
    VideoOutFormat pixel_format{};
    struct Size{u32 width{},height{};}size;
    u32 pitch{},num_bits{};
    VAddr guest_address{};
    void UpdateSize(){}
    ImageInfo()=default;
    ImageInfo(const Libraries::VideoOut::BufferAttributeGroup&,VAddr)noexcept;
};
@@IMAGE_INFO@@
struct TextureCache {
    enum class BindingType{VideoOut};
    struct ImageDesc {
        ImageInfo info;
        BindingType type{};
        @@IMAGE_DESC@@
    };
    struct Image{ImageInfo info;}image;
    bool larger_alias=false;
    unsigned lookups=0;
    int FindImage(const ImageDesc& d){++lookups;image.info=d.info;if(larger_alias)image.info.size.height*=2;return 0;}
    const Image& GetImage(int)const{return image;}
    void UpdateImage(int){
        std::unique_lock l{preparation_mutex};
        if(block_preparation){preparation_entered=true;preparation_cv.notify_all();
            preparation_cv.wait(l,[]{return release_preparation;});}
    }
};
}
namespace BachataCompat {bool Sotc608(){return false;}}
namespace Vulkan {
struct Scheduler {
    struct Recorder{void Kick(){assert(false && "retirement must not publish from swap");}}recorder_object;
    Recorder* recorder=&recorder_object;
    struct ObservedTick{
        std::atomic<u64> value{1};
        u64 load(std::memory_order order=std::memory_order_seq_cst){return value.load(order);}
        void store(u64 v){value.store(v);}
        void wait(u64 v,std::memory_order order){++vk::submission_waits;value.wait(v,order);}
        void notify_all(){value.notify_all();}
    }recorded_submit_tick;
    struct WorkSemaphore{vk::Semaphore sem;vk::Semaphore* Handle(){return &sem;}} work_semaphore;
    WorkSemaphore* GetWorkSemaphore(){return &work_semaphore;}
    void WaitSubmitted(u64,bool);
};
@@WAIT_SUBMITTED@@
struct Frame {
    vk::Fence fence;
    vk::Fence* present_done=&fence;
    vk::Semaphore ready;
    vk::Semaphore* ready_semaphore=&ready;
    u64 ready_tick=1;
    u32 width=16,height=16;
    bool is_hdr=false;
    VAddr payload{};
    u32 attribute_tag{};
};
struct Presenter {
    struct Instance{vk::Device GetDevice(){return {};}} instance;
    struct Swapchain{bool GetHDR(){return false;}}swapchain;
    struct Settings{bool enable=false;}fsr_settings;
    VideoCore::TextureCache texture_cache;
    Scheduler draw_scheduler;
    AmdGpu::Liverpool* liverpool{};
    u32 expected_frame_width=16,expected_frame_height=16;
    std::queue<Frame*> free_queue;
    Frame* last_submit_frame{};
    std::mutex free_mutex;
    GuardedCV free_cv;
    std::atomic<u64> frame_pool_empty{},frame_fence_pending{};
    std::atomic<unsigned> recreated{0},present_calls{0},idle_calls{0};
    std::atomic<bool> present_result{true},wait_vblank{false};
    Libraries::VideoOut::VideoOutPort* wait_port=nullptr;
    std::atomic<u64> required_vblank{0};
    std::mutex records_mutex;
    std::vector<VAddr> shown;
    std::vector<u32> tags;
    std::vector<bool> hdrs;
    std::thread::id swap_owner{};
    std::atomic<unsigned> in_present{0};
    std::mutex wsi_mutex;
    std::condition_variable wsi_cv;
    bool hold_wsi=false,wsi_entered=false,release_wsi=false;
    struct FrameAcquireProgress{u64 empty,fence_pending;};
    FrameAcquireProgress GetFrameAcquireProgress()const{return {frame_pool_empty.load(),frame_fence_pending.load()};}
    void RecreateFrame(Frame* f,u32 w,u32 h){++recreated;f->width=w;f->height=h;}
    Frame* GetRenderFrame(u32 width=0,u32 height=0,bool allow_wait=true);
    Frame* PrepareFrame(const Libraries::VideoOut::BufferAttributeGroup&,VAddr);
    Frame* PrepareBlankFrame(bool);
    void DiscardFrame(Frame*);
    Frame* PrepareLastFrame(){++idle_calls;return nullptr;}
    void SetHDR(bool value){std::scoped_lock l{records_mutex};hdrs.push_back(value);}
    bool Present(Frame* f,bool reuse=false,bool game=true){
        assert(f);
        assert(in_present.fetch_add(1)==0);
        if(Common::PresentQueueProgress::Enabled()){
            if(swap_owner==std::thread::id{})swap_owner=std::this_thread::get_id();
            assert(swap_owner==std::this_thread::get_id());
        }
        ++present_calls;
        {
            std::unique_lock l{wsi_mutex};
            if(hold_wsi){wsi_entered=true;wsi_cv.notify_all();wsi_cv.wait(l,[&]{return release_wsi;});}
        }
        if(wait_vblank){
            assert(wait_port);
            std::unique_lock l{wait_port->vo_mutex};
            const bool advanced=wait_port->vblank_cv.wait_for(l,350ms,[&]{
                return wait_port->vblank_status.count>=required_vblank.load();
            });
            assert(advanced && "Present blocked the vblank that the guest needs");
        }
        {std::scoped_lock l{records_mutex};shown.push_back(f->payload);tags.push_back(f->attribute_tag);}
        auto* frame=f;const bool is_reusing_frame=reuse;
        @@FREE_FRAME@@
        free_frame(present_result.load());
        --in_present;
        return present_result.load();
    }
};
@@GET_FRAME@@
@@PREPARE_FRAME@@
@@PREPARE_BLANK@@
@@DISCARD_FRAME@@
}
std::unique_ptr<Vulkan::Presenter> presenter;
namespace Libraries::VideoOut {
@@METHODS@@
}
using Libraries::VideoOut::VideoOutDriver;
using Libraries::VideoOut::MaxDisplayBufferGroups;
template<class F>void Until(F predicate){
    const auto end=std::chrono::steady_clock::now()+1500ms;
    while(!predicate()){assert(std::chrono::steady_clock::now()<end);std::this_thread::yield();}
}
void StopVblank(VideoOutDriver& d){
    {std::scoped_lock l{d.mutex};d.present_thread.request_stop();}
    d.request_cv.notify_all();d.present_thread.join();
}
void ConfigurePort(VideoOutDriver& driver){
    auto* d=&driver;
    d->main_port.prev_index=0;
    for(unsigned i=0;i<MaxDisplayBufferGroups;++i){
        d->main_port.groups[i].is_occupied=true;
        auto& attrib=d->main_port.groups[i].attrib;
        attrib.pixel_format=Libraries::VideoOut::PixelFormat::A8R8G8B8Srgb;
        attrib.tiling_mode=Libraries::VideoOut::TilingMode::Tile;
        attrib.width=attrib.height=16;attrib.pitch_in_pixel=16;attrib.option=200+i;
    }
    for(unsigned i=0;i<16;++i){
        d->main_port.buffer_slots[i].group_index=i%MaxDisplayBufferGroups;
        d->main_port.buffer_slots[i].address_left=100+i;
        d->main_port.buffer_labels[i]=1;
    }
}
std::unique_ptr<VideoOutDriver> Create(bool manual=true){
    reports=0;diagnostics=0;vk::gpu_blocking_waits=0;vk::ready_waits=0;vk::submission_waits=0;
    Libraries::Kernel::flip_events=0;
    liverpool=std::make_unique<AmdGpu::Liverpool>();
    presenter=std::make_unique<Vulkan::Presenter>();presenter->liverpool=liverpool.get();
    auto d=std::make_unique<VideoOutDriver>(16,16);
    if(manual)StopVblank(*d);
    assert(d->Open(nullptr)==1);ConfigurePort(*d);
    return d;
}
void Eop(VideoOutDriver& d,int index){
    AmdGpu::Liverpool::draw=true;
    assert(d.SubmitFlip(&d.main_port,index,index,true));
    AmdGpu::Liverpool::draw=false;
}
void AddFrame(Vulkan::Frame& f,bool ready){
    f.fence.ready=ready;
    std::scoped_lock l{presenter->free_mutex};presenter->free_queue.push(&f);presenter->free_cv.notify_one();
}
void Finish(VideoOutDriver& d,VideoOutDriver::Request req,unsigned target){
    d.Flip(req);Until([&]{std::scoped_lock l{d.main_port.port_mutex};return d.main_port.flip_status.count==target;});
}
void FifoAndDependency(){
    auto d=Create();
    Eop(*d,1);Eop(*d,2);Eop(*d,3);
    assert(d->frames_accepted==3 && d->frames_prepared==0 && reports==0);
    assert(presenter->frame_pool_empty==1);
    for(int n=0;n<64;++n){assert(!d->ReceiveRequest());assert(d->requests.front().sequence==1);}
    assert(liverpool->num_commands==1);
    liverpool->Pump();
    assert(liverpool->num_commands==0 && d->requests.size()==3 && reports==0);
    Vulkan::Frame frame;AddFrame(frame,false);
    assert(!d->ReceiveRequest());
    // The dependency is genuinely submitted by the next CP command. A
    // blocking GetRenderFrame prevents Pump reaching it in the negative build.
    liverpool->SendCommand([&]{frame.fence.ready=true;});
    liverpool->Pump();
    assert(frame.fence.ready && presenter->frame_fence_pending==1 && presenter->recreated==0);
    assert(d->main_port.flip_status.flip_pending_num==3 && d->main_port.flip_status.count==0);
    assert(d->main_port.buffer_labels[0]==1);
    d->main_port.groups[1].attrib.option=999;d->main_port.buffer_slots[1].address_left=999;
    d->main_port.is_hdr=true;
    Vulkan::Frame spare;AddFrame(spare,true);
    for(unsigned n=1;n<=3;++n){
        auto req=d->ReceiveRequest();
        if(!req){liverpool->Pump();req=d->ReceiveRequest();}
        assert(req && req.sequence==n && req.index==int(n));
        Finish(*d,req,n);
        if(liverpool->num_commands)liverpool->Pump();
    }
    assert((presenter->shown==std::vector<VAddr>{101,102,103}));
    assert((presenter->tags==std::vector<u32>{201,202,203}));
    assert((presenter->hdrs==std::vector<bool>{false,false,false}));
    assert(reports==3 && d->frames_presented==3 && d->frames_prepared==3);
    assert(d->main_port.flip_status.flip_pending_num==0 && d->main_port.flip_status.gc_queue_num==0);
    assert(d->main_port.prev_index==3 && d->main_port.buffer_labels[0]==0 && d->main_port.buffer_labels[1]==0);
    assert(vk::gpu_blocking_waits==0 && !d->prepare_queued);
}
void CpuProducerAndBlank(){
    auto d=Create();
    assert(d->SubmitFlip(&d->main_port,-1,8,false));
    liverpool->Pump();assert(!d->ReceiveRequest());liverpool->Pump();
    Vulkan::Frame f,spare;AddFrame(f,false);
    (void)d->ReceiveRequest();liverpool->SendCommand([&]{f.fence.ready=true;});liverpool->Pump();
    assert(!d->ReceiveRequest());liverpool->Pump();
    auto r=d->ReceiveRequest();assert(r && r.index==-1);Finish(*d,r,1);
    assert(reports==1 && d->main_port.flip_status.gc_queue_num==0);
    AddFrame(spare,true);
    presenter->present_result=false;
    assert(d->SubmitFlip(&d->main_port,2,9,false));liverpool->Pump();
    auto skipped=d->ReceiveRequest();assert(skipped);Finish(*d,skipped,2);
    assert(reports==1 && d->frames_presented==1 && d->main_port.flip_status.flip_pending_num==0);
    // Idle work cannot steal a resource from a deferred guest head.
    {std::scoped_lock l{presenter->free_mutex};while(!presenter->free_queue.empty())presenter->free_queue.pop();}
    Eop(*d,3);d->DrawBlankFrame();d->DrawLastFrame();
    {std::scoped_lock l{d->swap_mutex};assert(d->swap_queue.empty());}
}
void VblankIndependent(){
    auto d=Create(false);Vulkan::Frame frame;AddFrame(frame,true);
    presenter->wait_port=&d->main_port;presenter->wait_vblank=true;
    {std::scoped_lock l{d->main_port.vo_mutex};presenter->required_vblank=d->main_port.vblank_status.count+15;}
    Eop(*d,1);
    Until([&]{return reports.load()==1;});
    {std::scoped_lock l{d->main_port.vo_mutex};assert(d->main_port.vblank_status.count>=presenter->required_vblank);}
    assert(presenter->present_calls==1 && vk::gpu_blocking_waits==0);
    StopVblank(*d);
}
void CallbackLifetime(){
    auto d=Create();auto state=d->callback_lifetime;
    assert(d->SubmitFlip(&d->main_port,1,1,false));
    assert(liverpool->num_commands==1);d.reset();
    assert(state->owner==nullptr);
    liverpool->Pump();assert(presenter->present_calls==0);
    d=Create();Vulkan::Frame frame;AddFrame(frame,true);state=d->callback_lifetime;
    {std::scoped_lock l{preparation_mutex};block_preparation=true;preparation_entered=false;release_preparation=false;}
    assert(d->SubmitFlip(&d->main_port,1,1,false));
    std::thread cp([]{liverpool->Pump();});
    {std::unique_lock l{preparation_mutex};assert(preparation_cv.wait_for(l,500ms,[]{return preparation_entered;}));}
    auto dying=std::async(std::launch::async,[&]{d.reset();});
    assert(dying.wait_for(20ms)==std::future_status::timeout);
    {std::scoped_lock l{preparation_mutex};release_preparation=true;preparation_cv.notify_all();}
    cp.join();dying.get();assert(state->owner==nullptr);
    {std::scoped_lock l{preparation_mutex};block_preparation=false;}
}
void IdlePollAndDiagnostics(){
    auto d=Create();
    // Empty idle blank is polled even on the separate worker (no producer).
    d->DrawBlankFrame();Until([&]{return presenter->frame_pool_empty.load()>0;});
    assert(presenter->present_calls==0);
    Eop(*d,1);
    d->progress_polls=63;
    d->progress_since=std::chrono::steady_clock::now()-3s;d->progress_reported=d->progress_since;
    d->NotePresentProgress();assert(diagnostics==1 && reports==0);
}
void QueuedIdleBeforeGuest(){
    {std::scoped_lock l{swap_start_mutex};pause_swap_start=true;swap_start_entered=false;release_swap_start=false;}
    auto d=Create();
    {std::unique_lock l{swap_start_mutex};assert(swap_start_cv.wait_for(l,500ms,[]{return swap_start_entered;}));}
    d->DrawBlankFrame();
    {std::scoped_lock l{d->swap_mutex};assert(d->swap_queue.size()==1);}
    Eop(*d,1);assert(!d->ReceiveRequest());
    assert(d->requests.size()==1 && liverpool->num_commands==1);
    // Idle was accepted first. It cannot now block the one swap worker on a
    // frame that the queued guest presentation will only return later.
    {std::scoped_lock l{swap_start_mutex};release_swap_start=true;swap_start_cv.notify_all();}
    Until([&]{return presenter->frame_pool_empty.load()>=2;});
    Until([&]{std::scoped_lock l{d->swap_mutex};return !d->swap_busy && d->swap_queue.empty();});
    assert(presenter->present_calls==0 && reports==0);
    Vulkan::Frame frame;AddFrame(frame,true);liverpool->Pump();
    auto req=d->ReceiveRequest();assert(req);Finish(*d,req,1);
    assert(reports==1 && presenter->shown==std::vector<VAddr>{101});
    {std::scoped_lock l{swap_start_mutex};pause_swap_start=false;}
}
void RealDescriptorExtent(){
    auto d=Create();
    auto group=d->main_port.groups[1];
    group.attrib.width=1920;group.attrib.height=1080;group.attrib.pitch_in_pixel=2048;
    VideoCore::TextureCache::ImageDesc desc{group,0x200a30000ULL};
    assert(desc.info.size.width==1920 && desc.info.size.height==1080);
    assert(desc.info.guest_address==0x200a30000ULL && desc.info.pitch==1920);
    AmdGpu::Liverpool::draw=true;
    auto* failed=presenter->PrepareFrame(group,100);
    assert(!failed && presenter->texture_cache.lookups==0);
    Vulkan::Frame frame;AddFrame(frame,true);
    presenter->expected_frame_width=1920;presenter->expected_frame_height=1080;
    presenter->texture_cache.larger_alias=true;
    auto* result=presenter->PrepareFrame(group,100);
    assert(result==&frame && frame.width==1920);
    assert(frame.height==@@RESOLVED_HEIGHT@@);
    AmdGpu::Liverpool::draw=false;
}
void LegacySelection(){
    const auto serial=Common::ElfInfo::Instance().serial;
    Common::ElfInfo::Instance().serial="CUSA00000";
    {
        auto d=Create();assert(!d->present_progress_enabled && !d->swap_thread.joinable());
        Vulkan::Frame frame;AddFrame(frame,true);
        assert(d->SubmitFlip(&d->main_port,1,5,false));liverpool->Pump();
        auto req=d->ReceiveRequest();assert(req);Finish(*d,req,1);
        assert(reports==1 && presenter->shown==std::vector<VAddr>{101});
    }
    Common::ElfInfo::Instance().serial=serial;
}
void CloseBeforeActivation(){
    auto d=Create();Vulkan::Frame frame;AddFrame(frame,true);
    const u64 original_generation=d->main_port.generation;
    assert(d->SubmitFlip(&d->main_port,1,1,false));
    assert(d->requests.size()==1 && !d->requests.front().activated);
    d->Close(1);assert(d->requests.empty() && !d->main_port.is_open);
    assert(d->main_port.generation!=original_generation);
    assert(d->Open(nullptr)==1);ConfigurePort(*d);d->main_port.flip_events.push_back(1);
    d->main_port.buffer_slots[2].address_left=202;d->main_port.groups[2].attrib.option=302;
    assert(d->SubmitFlip(&d->main_port,2,2,false));
    d->main_port.buffer_slots[2].address_left=999;d->main_port.groups[2].attrib.option=999;
    liverpool->Pump();auto req=d->ReceiveRequest();assert(req && req.sequence==2);
    Finish(*d,req,1);
    assert(presenter->shown==std::vector<VAddr>{202} && presenter->tags==std::vector<u32>{302});
    assert(reports==1 && d->frames_prepared==1 && Libraries::Kernel::flip_events==1);
    assert(d->main_port.flip_status.flip_pending_num==0);
}
void ClosePreparedRetirement(){
    auto d=Create();Vulkan::Frame frame;
    frame.ready_semaphore=presenter->draw_scheduler.GetWorkSemaphore()->Handle();
    frame.ready_tick=5;frame.ready_semaphore->value=0;
    presenter->draw_scheduler.recorded_submit_tick.store(0);
    AddFrame(frame,true);Eop(*d,1);
    assert(d->frames_prepared==1 && d->requests.front().frame==&frame);
    d->Close(1);
    Until([&]{return vk::submission_waits.load()>0 || vk::ready_waits.load()>0;});
    assert(vk::submission_waits>0);
    assert(vk::ready_waits==0);
    {std::scoped_lock l{presenter->free_mutex};assert(presenter->free_queue.empty());}
    // Recorder publication and GPU completion are distinct real dependencies.
    // Only queued CP commands satisfy them; neither Close nor retry fabricates a tick.
    liverpool->SendCommand([&]{presenter->draw_scheduler.recorded_submit_tick.store(5);
        presenter->draw_scheduler.recorded_submit_tick.notify_all();});
    liverpool->Pump();Until([&]{std::scoped_lock l{presenter->free_mutex};return vk::ready_waits.load()>0 || !presenter->free_queue.empty();});
    assert(vk::ready_waits>0);
    {std::scoped_lock l{presenter->free_mutex};assert(presenter->free_queue.empty());}
    liverpool->SendCommand([&]{frame.ready_semaphore->value=5;});liverpool->Pump();
    Until([&]{std::scoped_lock l{presenter->free_mutex};return presenter->free_queue.size()==1;});
    assert(reports==0 && d->main_port.flip_status.count==0 && d->requests.empty());
    assert(d->Open(nullptr)==1);ConfigurePort(*d);Eop(*d,2);
    auto req=d->ReceiveRequest();assert(req);Finish(*d,req,1);assert(reports==1);
}
void CloseInFlight(){
    auto d=Create();Vulkan::Frame old_frame,new_frame;AddFrame(old_frame,true);
    {std::scoped_lock l{presenter->wsi_mutex};presenter->hold_wsi=true;}
    Eop(*d,1);auto old=d->ReceiveRequest();assert(old);d->Flip(old);
    {std::unique_lock l{presenter->wsi_mutex};assert(presenter->wsi_cv.wait_for(l,500ms,[&]{return presenter->wsi_entered;}));}
    d->Close(1);assert(d->Open(nullptr)==1);ConfigurePort(*d);d->main_port.flip_events.push_back(1);
    AddFrame(new_frame,true);Eop(*d,2);auto next=d->ReceiveRequest();assert(next);d->Flip(next);
    assert(d->main_port.flip_status.flip_pending_num==1 && reports==0);
    {std::scoped_lock l{presenter->wsi_mutex};presenter->hold_wsi=false;presenter->release_wsi=true;presenter->wsi_cv.notify_all();}
    Until([&]{std::scoped_lock l{d->main_port.port_mutex};return d->main_port.flip_status.current_buffer==2;});
    {std::scoped_lock l{d->main_port.port_mutex};
        assert(d->main_port.flip_status.count==1 && d->main_port.flip_status.flip_pending_num==0);
        assert(d->main_port.flip_status.gc_queue_num==0 && d->main_port.prev_index==2);
    }
    assert(reports==1 && presenter->present_calls==2 && Libraries::Kernel::flip_events==1);
}
void RetryAcrossReopen(bool is_eop){
    auto d=Create();Eop(*d,1);assert(!d->ReceiveRequest());
    assert(d->prepare_queued && liverpool->num_commands==1);
    d->Close(1);assert(d->Open(nullptr)==1);ConfigurePort(*d);
    Vulkan::Frame frame;AddFrame(frame,true);
    if(is_eop)Eop(*d,2);
    else assert(d->SubmitFlip(&d->main_port,2,2,false));
    // The old retry has no borrowed descriptor. The serialized CP either
    // prepares the new activated head, or clears its token before activation.
    assert(d->frames_prepared==0);liverpool->Pump();
    auto req=d->ReceiveRequest();assert(req && req.sequence==2);Finish(*d,req,1);
    assert(!d->prepare_queued && liverpool->num_commands==0 && d->frames_prepared==1);
    assert(reports==1 && presenter->shown==std::vector<VAddr>{102});
}
void CloseQueuedAndDestroy(bool destroy){
    {std::scoped_lock l{swap_start_mutex};pause_swap_start=true;swap_start_entered=false;release_swap_start=false;}
    auto d=Create();Vulkan::Frame old_frame,new_frame;AddFrame(old_frame,true);
    {std::unique_lock l{swap_start_mutex};assert(swap_start_cv.wait_for(l,500ms,[]{return swap_start_entered;}));}
    Eop(*d,1);auto old=d->ReceiveRequest();assert(old);d->Flip(old);
    auto lifetime=d->callback_lifetime;
    std::future<void> dying;
    if(destroy){
        dying=std::async(std::launch::async,[&]{d.reset();});
        Until([&]{std::scoped_lock l{lifetime->mutex};return lifetime->owner==nullptr;});
        assert(dying.wait_for(0ms)==std::future_status::timeout);
    }else{
        d->Close(1);assert(d->Open(nullptr)==1);ConfigurePort(*d);d->main_port.flip_events.push_back(1);
        AddFrame(new_frame,true);Eop(*d,2);auto next=d->ReceiveRequest();assert(next);d->Flip(next);
    }
    {std::scoped_lock l{swap_start_mutex};release_swap_start=true;swap_start_cv.notify_all();}
    if(destroy){dying.get();assert(reports==0 && presenter->present_calls==0);}
    else{
        Until([&]{return reports.load()==1;});
        assert(presenter->shown==std::vector<VAddr>{102} && Libraries::Kernel::flip_events==1);
        assert(d->main_port.flip_status.count==1 && d->main_port.flip_status.flip_pending_num==0);
    }
    assert(vk::ready_waits==1);
    {std::scoped_lock l{swap_start_mutex};pause_swap_start=false;}
}
int main(int argc,char**argv){
    assert(argc==2);Common::ElfInfo::Instance().serial=argv[1];
    FifoAndDependency();CpuProducerAndBlank();VblankIndependent();CallbackLifetime();IdlePollAndDiagnostics();
    QueuedIdleBeforeGuest();RealDescriptorExtent();LegacySelection();
    CloseBeforeActivation();ClosePreparedRetirement();CloseInFlight();CloseQueuedAndDestroy(false);CloseQueuedAndDestroy(true);
    RetryAcrossReopen(false);RetryAcrossReopen(true);
    std::cout<<"PASS: real CP/Draw frame poll, FIFO, one retry, vblank, completion, idle and callback teardown\n";
}
'''


def fixture(source: Path):
    src = source / 'src'
    dc = (src/'core/libraries/videoout/driver.cpp').read_text()
    pc = (src/'video_core/renderer_vulkan/vk_presenter.cpp').read_text()
    cp_base = source
    if not (src/'video_core/amdgpu/liverpool.cpp').exists():
        cp_base = source.parents[1] / ('validation/boot-lod-pass-order' if 'order' in str(source) else 'validation/boot-lod-pass-sotc')
    cp = (cp_base/'src/video_core/amdgpu/liverpool.cpp').read_text()
    ch = (cp_base/'src/video_core/amdgpu/liverpool.h').read_text()
    anchors = ['VideoOutDriver::VideoOutDriver(', 'VideoOutDriver::~VideoOutDriver()',
        'int VideoOutDriver::Open(', 'void VideoOutDriver::Close(',
        'bool VideoOutDriver::SubmitFlip(', 'bool VideoOutDriver::SubmitFlipLegacyProducer(',
        'void VideoOutDriver::SubmitFlipLegacy(',
        'void VideoOutDriver::SubmitFlipInternal(', 'bool VideoOutDriver::RunPresenter(',
        'void VideoOutDriver::QueueFrameRetirement(',
        'void VideoOutDriver::SwapThread(', 'void VideoOutDriver::QueueFramePreparation(',
        'void VideoOutDriver::PrepareFrontRequest(', 'VideoOutDriver::Request VideoOutDriver::ReceiveRequest(',
        'void VideoOutDriver::NotePresentProgress(', 'void VideoOutDriver::Flip(',
        'void VideoOutDriver::FlipPrepared(', 'void VideoOutDriver::DrawBlankFrame()',
        'void VideoOutDriver::DrawLastFrame()', 'void VideoOutDriver::PresentThread(']
    methods = '\n\n'.join(block(dc,a) for a in anchors)
    prepare = block(pc,'Frame* Presenter::PrepareFrame(')
    prepare = prepare[:prepare.index('    const auto frame_subresources')]+\
        '    frame->payload=cpu_address;frame->attribute_tag=attribute.attrib.option;return frame;\n}'
    blank = block(pc,'Frame* Presenter::PrepareBlankFrame(')
    blank = blank[:blank.index('    auto& scheduler')]+'    frame->payload=0;return frame;\n}'
    pacing = 'namespace Common::OrderFramePacing {u32 FrameLimit(){return 0;}}'
    ii=(cp_base/'src/video_core/texture_cache/image_info.cpp').read_text()
    tc=(cp_base/'src/video_core/texture_cache/texture_cache.h').read_text()
    sc=(cp_base/'src/video_core/renderer_vulkan/vk_scheduler.cpp').read_text()
    desc=re.search(r'ImageDesc\(const Libraries::VideoOut::BufferAttributeGroup& group, VAddr cpu_address\)\s*:[^;]+?\{\}',tc)
    assert desc
    pending_cp = ''
    if '    struct PendingCommandProgress {' in ch:
        pending_cp = block(ch,'    struct PendingCommandProgress {')+';\n'+block(ch,'    PendingCommandProgress GetPendingCommandProgress(')
    values={'PACING':pacing,'SEND':block(ch,'    template <bool wait_done = false>'),
        'PENDING_CP':pending_cp,
        'COMMANDS':block(cp,'void Liverpool::ProcessCommands()'),
        'GET_FRAME':block(pc,'Frame* Presenter::GetRenderFrame('),
        'PREPARE_FRAME':prepare,'PREPARE_BLANK':blank,'METHODS':methods,
        'IMAGE_INFO':block(ii,'ImageInfo::ImageInfo(const Libraries::VideoOut::BufferAttributeGroup&'),
        'IMAGE_DESC':desc.group(0),'FREE_FRAME':block(pc,'    const auto free_frame =')+';',
        'WAIT_SUBMITTED':block(sc,'void Scheduler::WaitSubmitted('),
        'DISCARD_FRAME':block(pc,'void Presenter::DiscardFrame('),
        'RESOLVED_HEIGHT':'2160' if 'BACHATA_GUEST_SIZED_INTERMEDIATE' in prepare else '1080'}
    text=PREFIX
    for key,value in values.items():text=text.replace('@@'+key+'@@',value)
    assert '@@' not in text
    return text


def source_contract(source: Path):
    src=source/'src';dc=(src/'core/libraries/videoout/driver.cpp').read_text()
    pc=(src/'video_core/renderer_vulkan/vk_presenter.cpp').read_text()
    ph=(src/'video_core/renderer_vulkan/vk_presenter.h').read_text()
    assert '#include "video_core/amdgpu/liverpool.h"' in pc.splitlines()
    assert 'bool Present(Frame* frame,' in ph
    actual=block(pc,'bool Presenter::Present(')
    assert 'free_frame(false);\n            return false;' in actual
    assert actual.rstrip().endswith('return presented;\n}')
    assert actual.index('presented=swapchain.Present();')<actual.index('return presented;')
    prep=block(pc,'Frame* Presenter::PrepareFrame(')
    assert prep.index('if (!frame) return nullptr;')<prep.index('texture_cache.FindImage(desc)')
    assert 'texture_cache.GetImage(image_id)' not in prep[:prep.index('if (!frame) return nullptr;')]
    blank=block(pc,'Frame* Presenter::PrepareBlankFrame(')
    assert blank.index('if (!frame) return nullptr;')<blank.index('scheduler.EndRendering(')
    assert '[=, this]' not in block(dc,'bool VideoOutDriver::SubmitFlip(')
    assert 'token.stop_requested() || !requests.empty()' not in block(dc,'void VideoOutDriver::PresentThread(')
    for fn in ['void VideoOutDriver::DrawBlankFrame()','void VideoOutDriver::DrawLastFrame()']:
        assert 'RunPresenter(' in block(dc,fn)
    return 9


def producer_dependency(source: Path):
    """Compile the real Liverpool class and the presenter's producer expression.

    Only unrelated containers and assertion logging are shims. Liverpool's
    class, accessors, visibility and scalar/extent/function headers are real.
    The behavior fixture defines Liverpool itself, so it cannot catch a native
    TU accidentally depending on the texture cache's forward declaration.
    """
    src=source/'src'
    pc=(src/'video_core/renderer_vulkan/vk_presenter.cpp').read_text()
    include='#include "video_core/amdgpu/liverpool.h"'
    assert include in pc.splitlines()
    frame=block(pc,'Frame* Presenter::GetRenderFrame(')
    owner=re.search(r'    const bool gpu_owner\s*=[^;]+;',frame)
    assert owner, 'missing real producer expression'
    prefix='#include <array>\n#include <atomic>\n#include <thread>\nnamespace AmdGpu { struct Liverpool; }\n'
    probe=prefix+include+'\nbool Producer(AmdGpu::Liverpool* liverpool) {\n'+owner.group(0)+'\nreturn gpu_owner;\n}\n'
    with tempfile.TemporaryDirectory(prefix='present-liverpool-dependency-') as tmp:
        work=Path(tmp)
        shims={
            'common/assert.h':'#pragma once\n#define ASSERT_MSG(...) ((void)0)\n#define UNREACHABLE_MSG(...) ((void)0)\n',
            'common/slot_vector.h':'#pragma once\n#include <cstddef>\nnamespace Common { template<class T> struct SlotVector { explicit SlotVector(std::size_t) {} }; }\n',
            'video_core/amdgpu/regs.h':'#pragma once\n#include "common/types.h"\nnamespace AmdGpu { constexpr u32 NUM_COLOR_BUFFERS=8; struct Buffer {}; struct ComputeProgram {}; struct Regs { static constexpr u32 NumRegs=32; std::array<u32,NumRegs> reg_array{}; }; }\n',
            'shader_recompiler/info.h':'#pragma once\n#include <cstddef>\nnamespace Shader { struct Info {}; constexpr std::size_t MaxStageTypes=6; }\n',
            'video_core/amdgpu/bachata_draw_snapshot.h':'#pragma once\n#include <cstddef>\nnamespace BachataDrawPipe { template<class T,std::size_t N> struct Snapshots {}; }\n',
        }
        for rel,text in shims.items():
            path=work/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        cpp=work/'producer.cpp'
        for name,text,android,success in (
            ('android_complete_header',probe,True,True),
            ('host_complete_header',probe,False,True),
            ('missing_include',probe.replace(include,''),True,False),
        ):
            cpp.write_text(text)
            command=['g++','-std=c++20','-pthread','-fsyntax-only','-I',str(work),'-I',str(src)]
            if android: command+=['-D__ANDROID__','-DSHADPS4_ENABLE_FEX_GUEST_CPU']
            result=subprocess.run([*command,str(cpp)],capture_output=True,text=True)
            assert (result.returncode==0)==success,(name,result.stderr)
            if not success:
                assert 'incomplete type' in result.stderr and 'Liverpool' in result.stderr,result.stderr
                assert 'OnDrawThread' in result.stderr and 'GetGpuCommandProcessorThread' in result.stderr,result.stderr
        print('PASS: real Liverpool header and producer expression, Android/host, missing-include negative')


def run(source: Path, positive_only=False):
    n=source_contract(source);producer_dependency(source);text=fixture(source)
    with tempfile.TemporaryDirectory(prefix='present-progress-') as tmp:
        work=Path(tmp)
        headers={'common/debug.h':'#pragma once\n','common/polyfill_thread.h':'#pragma once\n#include <thread>\n',
            'core/libraries/videoout/video_out.h':'#pragma once\n','common/elf_info.h':'#pragma once\n',
            'common/types.h':'#pragma once\n','common/assert.h':'#pragma once\n'}
        for path,value in headers.items():(work/path).parent.mkdir(parents=True,exist_ok=True);(work/path).write_text(value)
        for rel in ['src/core/libraries/videoout/driver.h','src/common/present_queue_progress.h']:
            dest=work/rel.removeprefix('src/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text((source/rel).read_text())
        header_root=source
        if not(source/'src/core/libraries/videoout/buffer.h').exists():
            header_root=source.parents[1]/('validation/boot-lod-pass-order' if 'order' in str(source) else 'validation/boot-lod-pass-sotc')
        (work/'core/libraries/videoout/buffer.h').write_text((header_root/'src/core/libraries/videoout/buffer.h').read_text())
        cpp=work/'gate.cpp';binary=work/'gate'
        def check(body,negative=False):
            cpp.write_text(body)
            subprocess.run(['g++','-std=c++20','-O1','-g','-pthread','-fsanitize=undefined','-fno-sanitize-recover=all',
                '-D__ANDROID__','-DSHADPS4_ENABLE_FEX_GUEST_CPU','-DENABLE_BACHATA_RUNTIME','-I',str(work),str(cpp),'-o',str(binary)],check=True)
            result=subprocess.run([str(binary),'CUSA08809'],text=True,capture_output=True,timeout=12)
            if negative:
                assert result.returncode!=0,'negative unexpectedly passed'
            else:
                assert result.returncode==0,result.stdout+result.stderr
                print(result.stdout.strip())
                for title in ['CUSA08034','CUSA00785']:
                    subprocess.run([str(binary),title],check=True,timeout=12)
        check(text)
        negatives=[
            ('blocking producer fence', 'poll ? 0ULL : std::numeric_limits<u64>::max()', 'std::numeric_limits<u64>::max()'),
            ('missing Draw owner', '(liverpool->OnDrawThread() ||', '(false ||'),
            ('completion before presentation', '        frames_accepted.fetch_add(1, std::memory_order_relaxed);', '        frames_accepted.fetch_add(1, std::memory_order_relaxed);\n        ++port->flip_status.count;'),
            ('lost owned descriptor', 'presenter->PrepareFrame(request.attribute, request.address)', 'presenter->PrepareFrame(request.port->groups[request.index], request.port->buffer_slots[request.index].address_left)'),
            ('count failed presentation', 'if (presented) Platform::Bachata::ReportPresentedFrame();', 'Platform::Bachata::ReportPresentedFrame();'),
            ('vblank performs blocking presentation', 'if (!RunPresenter([this, req] { FlipPrepared(req); })) {\n        QueueFrameRetirement(req.frame);\n    }', 'FlipPrepared(req);'),
            ('unsafe queued callback lifetime', 'callback_lifetime->owner = nullptr;', '(void)callback_lifetime;'),
            ('no single callback gate', 'requests.front().frame ||\n            preparing_frame || prepare_queued) return;', 'requests.front().frame ||\n            preparing_frame) return;'),
            ('idle waits for later guest frame', 'GetRenderFrame(0, 0, !present_thread)', 'GetRenderFrame()'),
            ('deferred moved to tail', '        if (!requests.empty() && requests.front().frame) {',
             '        if (!requests.empty() && !requests.front().frame) { requests.push_back(requests.front()); requests.pop_front(); }\n        if (!requests.empty() && requests.front().frame) {'),
            ('stale queued frame presented', 'req.port_generation == req.port->generation;', 'true;'),
            ('stale in-flight completion', '(!port->is_open || req.port_generation != port->generation)', 'false'),
            ('no retirement of prepared frame', 'for (const auto& request : requests) QueueFrameRetirement(request.frame);', 'for (const auto& request : requests) (void)request;'),
            ('skip recorder publication before retirement', 'draw_scheduler.WaitSubmitted(frame->ready_tick, false);', '(void)frame;'),
            ('skip GPU completion before reuse', 'const auto result = instance.GetDevice().waitSemaphores(wait, ~u64{0});', 'const auto result = vk::Result::eSuccess;'),
            ('abandon queued frame at shutdown', '            work = std::move(swap_queue.front());', '            if (token.stop_requested()) return;\n            work = std::move(swap_queue.front());'),
            ('resurrect closed deferred request', '        requests.clear();', '        (void)requests;'),
        ]
        if not positive_only:
            for name,old,new in negatives:
                assert old in text,name
                check(text.replace(old,new,1),True)
                print('PASS negative:',name)
        print(f'PASS: {n} source contracts, {len(negatives) if not positive_only else 0} executable negatives')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--positive-only',action='store_true')
    p.add_argument('--dependency-only',action='store_true',help='Check only native source contracts and the Liverpool include regression')
    a=p.parse_args()
    if a.dependency_only:
        n=source_contract(a.source.resolve());producer_dependency(a.source.resolve())
        print(f'PASS: {n} source contracts; existing runtime negatives unchanged')
    else:
        run(a.source.resolve(),a.positive_only)
