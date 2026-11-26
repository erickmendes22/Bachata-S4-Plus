#!/usr/bin/env python3
"""Execute real presentation/producer/patch-probe methods with clock and Vulkan boundaries."""
from pathlib import Path
import argparse, re, subprocess, tempfile
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--positive-only',action='store_true');a=p.parse_args()
root=a.source.resolve()
PREFIX=r"""
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <queue>
#include <vector>
#include <cstring>
#include <memory>
#include <thread>
#include <string>
#include "common/order_frame_pacing.h"
using u32=uint32_t; using u64=uint64_t;
struct TestClock {
    using duration=std::chrono::nanoseconds; using rep=duration::rep;
    using period=duration::period; using time_point=std::chrono::time_point<TestClock>;
    static constexpr bool is_steady=true;
    static inline time_point value{};
    static time_point now(){return value;}
};
using Time=TestClock::time_point;
static bool stopped=false;
static Time ready_at=Time::max();
static std::chrono::nanoseconds production;
static std::vector<Time> presented;
static unsigned next_id=0;
static int requested_rate=0;
static unsigned notifications=0;
static int switch_mode=0;
void OnFlip(unsigned);
static bool ready_queued=false;
void AdvanceTo(Time);
struct StopToken {bool stop_requested() const{return stopped;}};
struct FakeCV {
    bool is_request=false; explicit FakeCV(bool request=false):is_request(request){} void notify_one(){if(is_request)++notifications;} void notify_all(){if(is_request)++notifications;}
    template<class Lock,class Predicate>
    bool wait_until(Lock& lock,Time deadline,Predicate pred){
        if(pred())return true;
        const auto previous=notifications;
        lock.unlock();
        AdvanceTo(std::min(deadline,ready_at));
        if(notifications==previous && TestClock::now()<deadline) AdvanceTo(deadline);
        lock.lock();
        return pred();
    }
};
#define LOG_INFO(...) NoOpLog(__VA_ARGS__)
#define LOG_TRACE(...) NoOpLog(__VA_ARGS__)
enum {Loader,Lib_VideoOut};
template<class... T>void NoOpLog(T&&...){}
#define ASSERT_MSG(value,...) assert(value)
#define PS4_SYSV_ABI
using s32=int32_t; using s64=int64_t;
constexpr int ORBIS_OK=0;
#define FRAME_END ((void)0)
namespace Common {
void SetCurrentThreadName(const char*){}
void SetCurrentThreadRealtime(std::chrono::nanoseconds){}
struct AccurateTimer {
    std::chrono::nanoseconds period; Time start{};
    explicit AccurateTimer(std::chrono::nanoseconds p):period(p){}
    void Start(){start=TestClock::now();}
    void End(){AdvanceTo(start+period);}
    std::chrono::nanoseconds GetTotalWait(){return std::chrono::nanoseconds(0);}
};
}
struct Settings {u32 GetVblankFrequency(){return 60;} u32 GetFrameLimit(){return 60;}} EmulatorSettings;
struct Debug {bool IsGuestThreadsPaused(){return false;}} DebugState;
namespace Ps4Settings {
bool MenuEnabled(){return false;}
struct Data {std::atomic<int> fps_limit{60};};
Data& Get(){static Data d;return d;}
}
namespace ImGui::Core {bool MustKeepDrawing(){return false;}}
namespace Libraries::Kernel {
struct OrbisKernelEvent {enum class Filter{VideoOut};};
struct Queue {template<class... Args>void TriggerEvent(Args...){};};
Queue* GetEqueue(int){return nullptr;}
u64 sceKernelGetProcessTime(){return TestClock::now().time_since_epoch().count();}
u64 sceKernelReadTsc(){return sceKernelGetProcessTime();}
}
namespace Vulkan {struct Frame{unsigned id;};}
static Vulkan::Frame frames[4096];
struct Presenter {
    Vulkan::Frame* PrepareBlankFrame(bool){frames[next_id].id=next_id+1;return &frames[next_id++];}
    Vulkan::Frame* PrepareFrame(const int&,std::uintptr_t){return PrepareBlankFrame(false);}
};
static auto presenter=std::make_unique<Presenter>();
namespace Libraries::VideoOut {
s32 sceVideoOutSetFlipRate(s32,s32);
enum class OrbisVideoOutInternalEventId {Vblank};
struct VideoOutDriver {
    struct Port;
    struct Request {Vulkan::Frame* frame{};Port* port{};s64 flip_arg{};s32 index{};bool eop{};
        operator bool()const{return frame!=nullptr;}};
    struct Port {
        struct Status {u64 count{},process_time{},tsc{};} vblank_status;
        std::atomic<int> flip_rate{0};bool is_open=true;
        struct Slot{int group_index{};std::uintptr_t address_left=1;};
        std::array<Slot,1> buffer_slots{};std::array<int,1> groups{};
        std::vector<int> vblank_events;std::mutex vo_mutex;FakeCV vblank_cv;
    } main_port;
    std::mutex mutex;std::queue<Request> requests;FakeCV request_cv{true};
    std::jthread present_thread;
    ~VideoOutDriver();
    Port* GetPort(int){return &main_port;}
    void SubmitFlipInternal(Port*,s32,s64,bool);
    void Flip(const Request& request){
        assert(request.frame->id==presented.size()+1);
        presented.push_back(TestClock::now());
        OnFlip(presented.size());
        if(switch_mode==3) AdvanceTo(TestClock::now()+production);
        if(presented.size()==360){stopped=true;ready_at=Time::max();return;}
        if(switch_mode==3)return; // backlog is already queued; Present has real cost
        ready_at=TestClock::now()+production;ready_queued=false;
    }
    void DrawLastFrame(){} void DrawBlankFrame(){}
    void PresentThread(StopToken token);
};
using VideoOutPort=VideoOutDriver::Port;
static VideoOutDriver* driver;
}
static Libraries::VideoOut::VideoOutDriver* active;
void AdvanceTo(Time deadline){
    if(deadline<TestClock::now())return;
    if(!ready_queued && ready_at<=deadline){
        TestClock::value=ready_at;
        active->SubmitFlipInternal(&active->main_port,0,next_id+1,false);
        ready_queued=true;ready_at=Time::max();
    }
    TestClock::value=deadline;
}

void OnFlip(unsigned count){
    if(count==90 && switch_mode==1) Libraries::VideoOut::sceVideoOutSetFlipRate(1,1);
    if(count==180 && switch_mode==1) Libraries::VideoOut::sceVideoOutSetFlipRate(1,0);
    if(count==90 && switch_mode==2) Common::OrderFramePacing::Configure("CUSA00785","01.02",{});
    if(count==180 && switch_mode==2) Common::OrderFramePacing::Configure("CUSA00785","01.02",Common::OrderFramePacing::PatchedInstruction);
}
"""
MAIN=r"""
int main(int argc,char** argv){
    assert(argc==5);
    production=std::chrono::microseconds(std::stoll(argv[1]));
    requested_rate=std::stoi(argv[2]);const int profile=std::stoi(argv[3]);switch_mode=std::stoi(argv[4]);
    auto bytes=Common::OrderFramePacing::PatchedInstruction;
    if(profile==1)bytes[6]=2;
    Common::OrderFramePacing::Configure(profile==0?"CUSA00000":"CUSA00785",profile==3?"01.00":"01.02",bytes);
    Libraries::VideoOut::VideoOutDriver instance;active=&instance;Libraries::VideoOut::driver=&instance;
    Libraries::VideoOut::sceVideoOutSetFlipRate(1,requested_rate);
    for(unsigned i=0;i<(switch_mode==3?360u:1u);++i)
        instance.SubmitFlipInternal(&instance.main_port,0,i+1,false);
    ready_queued=true;
    instance.PresentThread({});
    assert(presented.size()==360);
    const auto elapsed=(presented.back()-presented.front()).count();
    const double fps=359.0*1e9/double(elapsed);
    auto segment=[](unsigned a,unsigned b){return double(b-a)*1e9/double((presented[b]-presented[a]).count());};
    std::printf("RESULT fps=%.6f vblanks=%llu elapsed_ns=%lld segments=%.6f,%.6f,%.6f notifications=%u\n",
        fps,(unsigned long long)instance.main_port.vblank_status.count,(long long)elapsed,
        segment(5,80),segment(100,170),segment(200,300),notifications);
    const double vblank_hz=double(instance.main_port.vblank_status.count-1)*1e9/double(elapsed);
    if(switch_mode==3) assert(instance.main_port.vblank_status.count>=359);
    else assert(vblank_hz>59.7 && vblank_hz<60.2);
    assert(notifications==360);
}
"""
LOADER_PREFIX=r"""
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <span>
#include <string>
#include <vector>
#include "common/order_frame_pacing.h"
using u64=std::uint64_t;using uintptr_t=std::uintptr_t;
enum {Loader};template<class... T>void NoOpLog(T&&...){}
#define LOG_INFO(...) NoOpLog(__VA_ARGS__)
#define LOG_ERROR(...) NoOpLog(__VA_ARGS__)
namespace Core {
struct MemoryManager {
    bool mapped=true,readable=true;unsigned queries=0,reads=0;
    std::array<std::uint8_t,10> bytes=Common::OrderFramePacing::PatchedInstruction;
    std::uint64_t ClampRangeSize(uintptr_t,std::uint64_t n){return n;}
    std::uint64_t ClampGpuRangeSize(uintptr_t,std::uint64_t n){++queries;return mapped?n:0;}
    bool TryReadBacking(uintptr_t,void* out,std::uint64_t n){++reads;assert(n==bytes.size());if(readable)std::memcpy(out,bytes.data(),n);return readable;}
};
}
namespace Common {template<class T>struct Singleton {static T* Instance(){static T object;return &object;}};}
namespace MemoryPatcher {
uintptr_t g_eboot_address=0x800000000ULL;std::uint64_t g_eboot_image_size=0x1764000;
std::string g_game_serial="CUSA00785",version="01.02";
std::string CurrentAppVersion(){return version;}
bool patches_applied=false;
struct patchInfo {std::string gameSerial,modNameStr,offsetStr,valueStr,targetStr,sizeStr;bool isOffset{},littleEndian{};int patchMask{},maskOffset{};};
std::vector<patchInfo> pending_patches;
bool PatchMemory(const std::string&,const std::string&,const std::string&,const std::string&,const std::string&,bool,bool,int,int){Common::Singleton<Core::MemoryManager>::Instance()->bytes[6]=1;return true;}
"""
LOADER_MAIN=r"""
}
int main(){
    using namespace MemoryPatcher;using namespace Common::OrderFramePacing;
    auto& memory=*Common::Singleton<Core::MemoryManager>::Instance();
    auto reset=[&]{memory={};g_eboot_address=0x800000000ULL;g_eboot_image_size=0x1764000;g_game_serial="CUSA00785";version="01.02";Configure("","",{});};
#ifdef __ANDROID__
    reset();RefreshOrderFramePacing();assert(FrameLimit()==60 && memory.reads==1 && memory.queries==1);
    for(unsigned i=0;i<10;++i){reset();memory.bytes[i]^=1;RefreshOrderFramePacing();assert(FrameLimit()==0);}
    reset();memory.bytes[6]=2;RefreshOrderFramePacing();assert(FrameLimit()==0 && IsTarget());
    reset();version="01.00";RefreshOrderFramePacing();assert(FrameLimit()==0 && memory.queries==0);
    reset();g_game_serial="CUSA08809";RefreshOrderFramePacing();assert(FrameLimit()==0 && !IsTarget() && memory.queries==0);
    reset();memory.mapped=false;RefreshOrderFramePacing();assert(FrameLimit()==0 && memory.reads==0);
    reset();memory.readable=false;RefreshOrderFramePacing();assert(FrameLimit()==0 && memory.reads==1);
    reset();g_eboot_address=0;RefreshOrderFramePacing();assert(FrameLimit()==0 && memory.queries==0);
    reset();g_eboot_image_size=InstructionRva+9;RefreshOrderFramePacing();assert(FrameLimit()==0 && memory.queries==0);
    reset();g_eboot_address=UINTPTR_MAX-InstructionRva+1;RefreshOrderFramePacing();assert(FrameLimit()==0 && memory.queries==0);
    reset();RefreshOrderFramePacing();memory.readable=false;RefreshOrderFramePacing();assert(FrameLimit()==0);
    reset();memory.bytes[6]=2;pending_patches.push_back({.gameSerial="CUSA00785"});ApplyPendingPatches();assert(pending_patches.empty() && FrameLimit()==60);
    reset();pending_patches.clear();ApplyPendingPatches();assert(FrameLimit()==60); // managed and legacy both drain here
#else
    reset();RefreshOrderFramePacing();assert(FrameLimit()==0 && !IsTarget() && memory.queries==0 && memory.reads==0);
#endif
    std::puts("ORDER_FRAME_PACING_PATCH_PROBE_PASS title/version/all10bytes/VMA/bounds/overflow/failedread/post-patch/platform");
}
"""

LIFETIME_PREFIX = r'''
#include <atomic>
#include <cassert>
#include <condition_variable>
#include <latch>
#include <mutex>
#include <thread>
namespace Libraries::VideoOut {
struct VideoOutDriver {
    std::mutex mutex;
    std::condition_variable request_cv;
    std::latch waiting{1};
    std::atomic<bool> finished{false};
    std::jthread present_thread;
    struct QueueLifetime {
        VideoOutDriver* owner;
        ~QueueLifetime(){assert(!owner->present_thread.joinable() && owner->finished);}
    } requests{this};
    VideoOutDriver(){
        present_thread=std::jthread([this](std::stop_token token){
            std::unique_lock lock{mutex};
            waiting.count_down();
            request_cv.wait(lock,[&]{return token.stop_requested();});
            finished=true;
        });
        waiting.wait();
    }
    ~VideoOutDriver();
};
'''
LIFETIME_MAIN = r'''
}
int main(){for(unsigned i=0;i<100;++i){Libraries::VideoOut::VideoOutDriver instance;}}
'''

def method(text,signature):
    start=text.index(signature);end=text.index('\n}\n',start)+3
    return text[start:end]

driver=(root/'src/core/libraries/videoout/driver.cpp').read_text()
api=(root/'src/core/libraries/videoout/video_out.cpp').read_text()
patcher=(root/'src/common/memory_patcher.cpp').read_text()
header=(root/'src/common/order_frame_pacing.h').read_text()
present=method(driver,'void VideoOutDriver::PresentThread(').replace('std::chrono::steady_clock','TestClock').replace('std::this_thread::sleep_until','AdvanceTo').replace('std::stop_token','StopToken')
producer=method(driver,'void VideoOutDriver::SubmitFlipInternal(')
destructor=method(driver,'VideoOutDriver::~VideoOutDriver() {')
set_rate=method(api,'s32 PS4_SYSV_ABI sceVideoOutSetFlipRate(')
refresh=method(patcher,'void RefreshOrderFramePacing() {')
pending=method(patcher,'void ApplyPendingPatches() {')
on_load=method(patcher,'void OnGameLoaded() {')
assert on_load.count('ApplyPendingPatches();')==2
assert 'RefreshOrderFramePacing();' in method(patcher,'void AddPatchToQueue(')
assert 'std::atomic<int> flip_rate{0};' in (root/'src/core/libraries/videoout/driver.h').read_text()

with tempfile.TemporaryDirectory(prefix='order-frame-pacing-') as temporary:
    tmp=Path(temporary);(tmp/'common').mkdir()
    (tmp/'common/order_frame_pacing.h').write_text(header)
    def build(name,code,android=True):
        cpp=tmp/(name+'.cpp');cpp.write_text(code);binary=tmp/name
        command=['c++','-std=c++23','-O1','-g','-Wall','-Wextra','-Werror','-Wno-missing-field-initializers','-fsanitize=undefined','-fno-sanitize-recover=all','-pthread','-DSHADPS4_ENABLE_FEX_GUEST_CPU','-I',str(tmp)]
        if android:command+=['-D__ANDROID__']
        subprocess.run([*command,str(cpp),'-o',str(binary)],check=True)
        return binary
    def program(body=present,submit=producer):
        return PREFIX+'\nnamespace Libraries::VideoOut {\n'+submit+'\n'+destructor+'\n'+set_rate+'\n'+body+'\n}\n'+MAIN
    def run(binary,us,rate=0,profile=2,mode=0):
        data=subprocess.run([str(binary),str(us),str(rate),str(profile),str(mode)],text=True,capture_output=True,timeout=5)
        assert data.returncode==0,(binary.name,data.stdout,data.stderr)
        m=re.search(r'RESULT fps=([0-9.]+).*segments=([0-9.]+),([0-9.]+),([0-9.]+)',data.stdout);assert m,data.stdout
        return [float(x) for x in m.groups()]
    def check(binary):
        cases=0
        for us,expected in [(4000,60),(16000,60),(17000,1e6/17000),(20000,50),(25000,40),(40000,25)]:
            fps,*_=run(binary,us);assert abs(fps-expected)<.01,(us,fps,expected);cases+=1
        for profile in (0,1,3):
            fps,*_=run(binary,17000,profile=profile);assert abs(fps-30)<.01,(profile,fps);cases+=1
        fps,*_=run(binary,4000,rate=1);assert abs(fps-30)<.01;cases+=1
        for mode in (1,2):
            fps,first,middle,last=run(binary,17000,mode=mode)
            assert abs(first-1e6/17000)<.01 and abs(middle-30)<.01 and abs(last-1e6/17000)<.01,(mode,first,middle,last)
            cases+=1
        for us in (20000,40000):
            fps,*_=run(binary,us,mode=3)
            assert abs(fps-1e6/us)<.01,(us,fps)
            cases+=1
        return cases
    binary=build('pacing',program());cases=check(binary)
    print(f'ORDER_FRAME_PACING_REAL_METHODS_PASS cases={cases} 17ms:30->58.823529 20ms:30->50 25ms:30->40 FIFO/vblank/60cap/guest30/patch-toggle/expensive-Present-backlog')
    for android in (True,False):
        binary=build('probe'+str(android),LOADER_PREFIX+refresh+'\n'+pending+LOADER_MAIN,android)
        subprocess.run([str(binary)],check=True)
    lifetime=build('lifetime',LIFETIME_PREFIX+destructor+LIFETIME_MAIN)
    subprocess.run([str(lifetime)],check=True,timeout=5)
    print('ORDER_FRAME_PACING_LIFETIME_PASS stopped/woken/joined-before-queue-destruction cases=100')
    if not a.positive_only:
        variants={
            'vblank_only':(present.replace('if (!frame_limit || main_port.flip_rate.load(std::memory_order_relaxed) != 0)', 'if (true || !frame_limit || main_port.flip_rate.load(std::memory_order_relaxed) != 0)'),producer),
            'missing_notify':(present,producer.replace('request_cv.notify_one();','')),
            'missing_cap':(present.replace('1000000000 / frame_limit','1').replace('1000000000 / limit','1'),producer),
            'ignore_guest_rate':(present.replace('(main_port.flip_rate.load(std::memory_order_relaxed) + 1)','1').replace('main_port.flip_rate.load(std::memory_order_relaxed) != 0','false').replace('main_port.flip_rate.load(std::memory_order_relaxed) == 0','true'),producer),
            'wrong_vblank_clock':(present.replace('EmulatorSettings.GetVblankFrequency()', '(2 * EmulatorSettings.GetVblankFrequency())'),producer),
            'starve_vblank_on_backlog':(present.replace('            if (now >= tick_deadline) break;',''),producer),
        }
        for name,(body,submit) in variants.items():
            assert body!=present or submit!=producer,name
            mutant=build(name,program(body,submit))
            try:check(mutant)
            except AssertionError:print('ORDER_FRAME_PACING_NEGATIVE_PASS',name)
            else:raise AssertionError('Negative control escaped: '+name)
        for name,body in {
            'loose_guest_mapping':refresh.replace('ClampGpuRangeSize','ClampRangeSize'),
            'probe_before_patch':None,
        }.items():
            changed=pending
            if name=='probe_before_patch':
                body=refresh
                changed=pending.replace('    RefreshOrderFramePacing();','').replace('    patches_applied = true;','    RefreshOrderFramePacing();\n    patches_applied = true;')
            mutant=build(name,LOADER_PREFIX+body+'\n'+changed+LOADER_MAIN)
            result=subprocess.run([str(mutant)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
            assert result.returncode!=0,name
            print('ORDER_FRAME_PACING_NEGATIVE_PASS',name)
        for name,body in {
            'destroy_queue_before_join':destructor.replace('    if (present_thread.joinable()) present_thread.join();',''),
            'stop_without_wakeup':destructor.replace('    request_cv.notify_all();',''),
        }.items():
            mutant=build(name,LIFETIME_PREFIX+body+LIFETIME_MAIN)
            try:
                result=subprocess.run([str(mutant)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3)
                assert result.returncode!=0,name
            except subprocess.TimeoutExpired:
                assert name=='stop_without_wakeup'
            print('ORDER_FRAME_PACING_NEGATIVE_PASS',name)
