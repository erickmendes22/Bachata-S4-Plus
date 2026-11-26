#!/usr/bin/env python3
"""Exercise the actual SotC CP/VO wait graph and bounded backoff.

Vulkan and IRQ are boundary mocks. Process, dispatch, PM4 predicate, wait and
flip methods are extracted from the supplied effective source. Deterministic
barriers arrange arrivals; negative builds prove the gate detects regressions.
"""
import argparse
import pathlib
import subprocess
import tempfile


def block(text, anchor):
    start = text.index(anchor)
    brace = text.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=pathlib.Path, required=True)
    args = ap.parse_args()
    root = args.source / "src"
    cp = (root / "video_core/amdgpu/liverpool.cpp").read_text()
    ch = (root / "video_core/amdgpu/liverpool.h").read_text()
    vc = (root / "core/libraries/videoout/driver.cpp").read_text()
    vh = (root / "core/libraries/videoout/driver.h").read_text()
    pm4 = (root / "video_core/amdgpu/pm4_cmds.h").read_text()
    packet = pm4[pm4.index("struct PM4CmdWaitRegMem {"):]
    actual_test = block(packet, "bool Test(").replace("bool Test(", "bool RealTest(", 1)
    wait_case = block(cp, "case PM4ItOpcode::WaitRegMem: {")
    assert "BACHATA_SOTC_COOPERATIVE_VO_WAIT" in wait_case
    assert "std::atomic<u32> num_mapped_queues{1u};" in ch
    src = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <coroutine>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <future>
#include <iostream>
#include <mutex>
#include <queue>
#include <semaphore>
#include <span>
#include <string>
#include <thread>
#include <vector>
#include <unistd.h>
using u64=uint64_t; using u32=uint32_t; using s64=int64_t; using s32=int32_t;
using VAddr=uint64_t;
std::atomic<unsigned> warning_count{0};
std::atomic<u32> warning_qid{~u32{0}};
void CaptureWarning(const char*,const char*,u32 qid,VAddr,u64,u64,u64,u32,u32,u32,u64,u64,u64,u64) {
    warning_qid=qid;
    ++warning_count;
}
#define LOG_WARNING(category,...) CaptureWarning(__VA_ARGS__)
#define ASSERT_MSG(x, ...) assert(x)
#define LOG_ERROR(...) ((void)0)
#define UNREACHABLE() std::abort()
#define UNREACHABLE_MSG(...) std::abort()
#define YIELD_GFX() co_yield {};
namespace Common {
struct ElfInfo {
    std::string serial;
    static ElfInfo& Instance(){static ElfInfo value;return value;}
    const std::string& GameSerial()const{return serial;}
};
template<class R,class... A> using UniqueFunction=std::function<R(A...)>;
void SetCurrentThreadName(const char*) {}
template<class CV,class P> void CondvarWait(CV& cv,
        std::unique_lock<std::mutex>& lk, std::stop_token stop, P pred) {
    std::stop_callback cb(stop,[&]{cv.notify_all();});
    cv.wait(lk,[&]{return stop.stop_requested() || pred();});
}
}
namespace VideoCore { void StartCapture(){} void EndCapture(){} }
namespace Platform {
enum class InterruptId { GpuIdle };
struct IrqC { static IrqC* Instance(){static IrqC v;return &v;} void Signal(InterruptId){} };
}
namespace Vulkan { struct Frame{}; }
namespace Libraries::Kernel {
u64 sceKernelGetProcessTime(){return 0;} u64 sceKernelReadTsc(){return 0;}
struct OrbisKernelEvent { enum class Filter{VideoOut}; };
struct Equeue { void TriggerEvent(u64,OrbisKernelEvent::Filter,void*){} };
Equeue* GetEqueue(int){return nullptr;}
}
namespace Libraries::VideoOut {
constexpr int MaxDisplayBuffers=16;
enum class OrbisVideoOutInternalEventId { Flip };
struct Group{};
struct VideoOutPort {
    struct Buffer { int group_index=0; u64 address_left=0; };
    std::array<Buffer,16> buffer_slots{};
    std::array<Group,16> groups{};
    std::array<u64,16> buffer_labels{};
    struct Status { int flip_pending_num=0,gc_queue_num=0,current_buffer=0;
      u64 submit_tsc=0,count=0,process_time=0,tsc=0; s64 flip_arg=0; } flip_status;
    std::mutex vo_mutex,port_mutex;
    std::condition_variable vo_cv;
    std::vector<int> flip_events;
    int prev_index=0;
    bool is_hdr=false;
    @@ISLABEL@@
    @@WAIT@@
    @@SIGNAL@@
};
}
using Libraries::VideoOut::VideoOutPort;
@@HELPERS@@
struct PM4CmdWaitRegMem {
    enum class MemSpace{Register,Memory};
    enum class Function{Always,LessThan,LessThanEqual,Equal,NotEqual,GreaterThanEqual,GreaterThan,Reserved};
    template<class T> struct Field { T v; T Value()const{return v;} };
    Field<MemSpace> mem_space{MemSpace::Memory}; Field<Function> function{Function::Equal};
    u32 mask=~u32{0},ref=0; u32* address{};
    std::promise<void>* reached{};
    std::binary_semaphore* first_release{};
    std::binary_semaphore* second_release{};
    mutable unsigned calls=0;
    template<class T=u32*> T Address()const{return reinterpret_cast<T>(address);}
    u32 Reg()const{return 0;}
    @@PREDICATE@@
    bool Test(std::span<const u32> regs,u32* observed=nullptr) const {
        ++calls;
        if(calls==1 && reached) {
            const bool result=RealTest(regs,observed);
            reached->set_value();
            first_release->acquire();
            return result;
        }
        if(calls==2 && second_release) second_release->acquire();
        return RealTest(regs,observed);
    }
};
enum class PM4ItOpcode { WaitRegMem };
struct CountingCV {
    std::condition_variable cv;
    std::atomic<unsigned> timed_waits{0};
    std::atomic<s64> last_us{0};
    std::function<void()> on_timed_wait;
    void notify_one(){cv.notify_one();} void notify_all(){cv.notify_all();}
    template<class L,class P> void wait(L& lock,P pred){cv.wait(lock,pred);}
    template<class L,class D,class P> bool wait_for(L& lock,D delay,P pred){
        if(on_timed_wait)on_timed_wait();
        last_us=std::chrono::duration_cast<std::chrono::microseconds>(delay).count();
        timed_waits.fetch_add(1,std::memory_order_release);
        return cv.wait_for(lock,delay,pred);
    }
};
struct ObservableMutex {
    std::mutex mutex;
    std::function<void()> before_unlock;
    void lock(){mutex.lock();}
    bool try_lock(){return mutex.try_lock();}
    void unlock(){if(before_unlock)before_unlock();mutex.unlock();}
};
struct Liverpool {
    @@TASK@@;
    struct Queue { ObservableMutex m_access; std::queue<Task::Handle> submits; };
    static constexpr unsigned NumTotalQueues=3;
    std::array<Queue,NumTotalQueues> mapped_queues;
    static constexpr unsigned GfxQueueId=0;
    std::atomic<unsigned> num_commands{0},num_submits{0};
    std::atomic<bool> submit_done{false};
    u32 curr_qid=0,gpu_tid=0;
    std::atomic<u32> num_mapped_queues{1u};
    std::thread::id gpu_id{};
    std::mutex submit_mutex;
    CountingCV submit_cv;
    std::queue<std::function<void()>> command_queue;
    bool draw_snapshot_valid=false;
    VideoOutPort* vo_port{};
    struct { std::array<u32,1> reg_array{}; } regs;
    struct Scheduler {
        struct Semaphore {u64 KnownGpuTick(){return 7;}} sem;
        u64 CurrentTick(){return 9;} u64 RecordedSubmitTick(){return 8;}
        Semaphore* GetWorkSemaphore(){return &sem;}
    } scheduler;
    struct Rasterizer {
        Scheduler scheduler;
        void OnSubmit(){} void Flush(){} Scheduler& GetScheduler(){return scheduler;}
    }* rasterizer=nullptr;
    @@WAIT_FIELDS@@
    void NoteCommandWait(const char*,VAddr,u64,u64,u64,u32,bool&,u32);
    void ResetCommandWaitProgress(); void BackoffCommandWait(std::stop_token);
    bool OnDrawThread() const {return false;}
    void DrainDrawQueue(){} void ProcessCeQueue(){}
    @@SEND@@
    void ProcessCommands(); void Process(std::stop_token);
    void SubmitAsc(u32,std::span<const u32>);
    std::array<u32,1> asc_configuration{};
    std::atomic<u32> asc_executed{0};
    u64* asc_release_label=nullptr;
    Task ProcessCompute(std::span<const u32> commands,u32 qid) {
        // The GPU operation is a boundary mock; publication uses real SubmitAsc.
        assert(qid==0 && asc_configuration[qid]==0x12345678);
        assert(commands.size()==1 && commands[0]==17);
        if(asc_release_label)*asc_release_label=0;
        asc_executed.fetch_add(1);
        co_return;
    }
    Task WaitTask(const PM4CmdWaitRegMem* header) {
        switch(PM4ItOpcode::WaitRegMem) {
            @@WAITCASE@@
        }
        co_return;
    }
};
@@WAIT_METHODS@@
@@COMMANDS@@
@@PROCESS@@
@@SUBMIT_ASC@@
namespace Libraries::VideoOut {
struct Presenter {
    Vulkan::Frame frame;
    void SetHDR(bool){} void Present(Vulkan::Frame*){}
    Vulkan::Frame* PrepareBlankFrame(bool){return &frame;}
    Vulkan::Frame* PrepareFrame(const Group&,u64){return &frame;}
};
struct VideoOutDriver {
    struct Request { Vulkan::Frame* frame; VideoOutPort* port; s64 flip_arg; s32 index; bool eop; };
    Liverpool* liverpool; Presenter* presenter;
    std::mutex mutex; std::queue<Request> requests;
    bool SubmitFlip(VideoOutPort*,s32,s64,bool=false);
    void SubmitFlipInternal(VideoOutPort*,s32,s64,bool);
    void Flip(const Request&);
};
@@SUBMIT@@
@@INTERNAL@@
@@FLIP@@
}
using namespace Libraries::VideoOut;
template<class P> void Until(P pred) {
    const auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(2);
    while(!pred()) {
        assert(std::chrono::steady_clock::now()<deadline);
        std::this_thread::yield();
    }
}
void Stop(Liverpool& cp,std::jthread& worker) {
    // Serialize the predicate check with stop publication in the fixture.
    {std::scoped_lock lock{cp.submit_mutex};worker.request_stop();}
    cp.submit_cv.notify_all();worker.join();
    for(auto& queue:cp.mapped_queues) {
        while(!queue.submits.empty()) {
            queue.submits.front().destroy();queue.submits.pop();
        }
    }
}
void FlipCase(bool late,bool cooperative) {
    Liverpool cp;
    VideoOutPort port;
    port.buffer_labels[0]=1;
    port.flip_status.flip_pending_num=0;
    cp.vo_port=&port;
    Presenter presenter;
    VideoOutDriver driver{&cp,&presenter};
    std::promise<void> reached;
    auto entered=reached.get_future();
    std::binary_semaphore release_first{0},release_second{0};
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    packet.reached=&reached;packet.first_release=&release_first;packet.second_release=&release_second;
    if(!late) assert(driver.SubmitFlip(&port,1,99,false));
    auto task=cp.WaitTask(&packet);
    cp.mapped_queues[0].submits.push(task.handle);
    cp.num_submits=1;
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    assert(entered.wait_for(std::chrono::seconds(2))==std::future_status::ready);
    if(late) assert(driver.SubmitFlip(&port,1,99,false));
    release_first.release();
    if(late && !cooperative) {
        // Acquiring vo_mutex after the first predicate guarantees the CP has
        // released it inside the real condition-variable wait.
        std::unique_lock lock{port.vo_mutex};
        assert(port.buffer_labels[0]==1);
        assert(cp.num_commands==1 && cp.num_submits==1);
        {std::scoped_lock qlock{driver.mutex};assert(driver.requests.empty());}
        // Rescue only the test so the real worker can be joined.
        port.buffer_labels[0]=0;
        lock.unlock();
        release_second.release();
        port.SignalVoLabel();
    }
    Until([&]{std::scoped_lock lock{driver.mutex};return !driver.requests.empty();});
    VideoOutDriver::Request request;
    {std::scoped_lock lock{driver.mutex};request=driver.requests.front();driver.requests.pop();}
    driver.Flip(request);
    if(!(late && !cooperative)) release_second.release();
    Until([&]{return cp.num_submits==0 && cp.num_commands==0;});
    assert(port.buffer_labels[0]==0 && port.prev_index==1);
    assert(port.flip_status.flip_pending_num==0 && port.flip_status.count==1);
    Stop(cp,worker);
}
void SyncCommandCase() {
    Liverpool cp;
    VideoOutPort port;
    cp.vo_port=&port;port.buffer_labels[0]=1;
    std::promise<void> reached;
    auto entered=reached.get_future();
    std::binary_semaphore first{0},second{0};
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    packet.reached=&reached;packet.first_release=&first;packet.second_release=&second;
    auto task=cp.WaitTask(&packet);
    cp.mapped_queues[0].submits.push(task.handle);cp.num_submits=1;
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    assert(entered.wait_for(std::chrono::seconds(2))==std::future_status::ready);
    std::promise<void> sent;
    auto completed=sent.get_future();
    std::jthread sender([&]{
        cp.SendCommand<true>([&]{port.buffer_labels[0]=0;});
        sent.set_value();
    });
    Until([&]{return cp.num_commands==1;});
    first.release();
    assert(completed.wait_for(std::chrono::seconds(2))==std::future_status::ready);
    sender.join();second.release();
    Until([&]{return cp.num_submits==0;});
    assert(port.buffer_labels[0]==0);
    Stop(cp,worker);
}
void BackoffCase(bool stop_while_false) {
    Liverpool cp;
    VideoOutPort port;
    cp.vo_port=&port;port.buffer_labels[0]=1;
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    std::atomic<u64> observed{~u64{0}};
    std::atomic<bool> queue_unlocked{false};
    cp.submit_cv.on_timed_wait=[&]{
        // This callback runs on CP, so diagnostic state has no cross-thread read.
        observed.store(cp.cp_wait.observed,std::memory_order_relaxed);
        const bool free=cp.mapped_queues[0].m_access.try_lock();
        if(free)cp.mapped_queues[0].m_access.unlock();
        queue_unlocked.store(free,std::memory_order_relaxed);
    };
    auto task=cp.WaitTask(&packet);
    cp.mapped_queues[0].submits.push(task.handle);cp.num_submits=1;
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    Until([&]{return cp.submit_cv.timed_waits.load(std::memory_order_acquire)>0;});
    assert(cp.submit_cv.last_us==100 && queue_unlocked.load());
    assert(observed.load()==1 && cp.num_submits==1);
    if(stop_while_false) {
        Stop(cp,worker);
        assert(port.buffer_labels[0]==1 && cp.num_submits==1);
    } else {
        // The value changes on CP only, avoiding a fixture predicate data race.
        cp.SendCommand<true>([&]{port.buffer_labels[0]=0;});
        Until([&]{return cp.num_submits==0;});
        assert(port.buffer_labels[0]==0);
        Stop(cp,worker);
    }
}
void PredicateAndBreadcrumb() {
    Liverpool cp;
    VideoOutPort port;
    cp.vo_port=&port;port.buffer_labels[0]=0;
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    auto task=cp.WaitTask(&packet);
    cp.mapped_queues[0].submits.push(task.handle);cp.num_submits=1;
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    Until([&]{return cp.num_submits==0;});
    assert(cp.submit_cv.timed_waits==0 && packet.calls==1);
    Stop(cp,worker);

    bool first=true;
    cp.cp_progress=false;
    cp.NoteCommandWait("wait_reg_mem_memory",0x1234,2,0xff,1,3,first,0);
    assert(cp.cp_progress && !first && cp.cp_wait.observed==1);
    cp.cp_progress=false;
    cp.NoteCommandWait("wait_reg_mem_memory",0x1234,2,0xff,9,3,first,0);
    assert(!cp.cp_progress && cp.cp_wait.observed==9);
    cp.cp_stalled=32;
    cp.cp_stall_since_ns=SotcCommandWaitNowNs()-2'001'000'000ULL;
    const auto old=warning_count.load();
    cp.BackoffCommandWait({});
    cp.BackoffCommandWait({});
    assert(warning_count==old+1 && cp.cp_wait_reported);
    cp.ResetCommandWaitProgress();
    assert(cp.cp_stalled==0 && cp.cp_stall_since_ns==0 && !cp.cp_wait_reported && !cp.cp_wait.active);
}
void MultiQueueBreadcrumbCase(u32 queues) {
    Liverpool cp;
    VideoOutPort port;
    cp.vo_port=&port;port.buffer_labels[0]=1;
    cp.num_mapped_queues=queues;
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    const auto old=warning_count.load();
    unsigned phase=0;
    cp.submit_cv.on_timed_wait=[&]{
        // Runs at the actual CV boundary on CP with submit_mutex held.
        if(phase==0) {
            assert(cp.curr_qid==0);
            // The next ProcessCommands runs before visiting the empty queue1.
            cp.command_queue.emplace([]{});++cp.num_commands;
            phase=1;
        } else if(phase==1) {
            assert(cp.curr_qid==1);
            // Avoid a two-second wall-clock test. The real helper still makes
            // the elapsed-time comparison, on its next no-progress pass.
            cp.cp_stall_since_ns=SotcCommandWaitNowNs()-2'001'000'000ULL;
            phase=2;
        } else if(phase==2) {
            assert(cp.curr_qid==1);
            assert(cp.cp_wait.active && cp.cp_wait.qid==0);
            assert(warning_count==old+1 && warning_qid==0);
            cp.command_queue.emplace([&]{port.buffer_labels[0]=0;});++cp.num_commands;
            phase=3;
        } else {
            assert(false && "completed breadcrumb episode did not progress");
        }
    };
    auto task=cp.WaitTask(&packet);
    cp.mapped_queues[0].submits.push(task.handle);cp.num_submits=1;
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    Until([&]{return cp.num_submits==0;});
    Stop(cp,worker);
    assert(phase==3 && port.buffer_labels[0]==0);
    std::cout<<"MULTI_QUEUE_BREADCRUMB_PASS queues="<<queues<<" wait_qid=0 poll_qid=1\n";
}
void AscPublicationCase(bool known) {
    Liverpool cp;
    cp.num_mapped_queues=known?2:1;
    cp.asc_configuration[0]=0x12345678;
    const std::array<u32,1> commands{17};
    // At the exact m_access unlock boundary the CP can observe the task.
    // The original split-lock method fails here deterministically: task is
    // visible but its submission has not yet been counted/published.
    cp.mapped_queues[1].m_access.before_unlock=[&]{
        if(!cp.mapped_queues[1].submits.empty()) {
            assert(cp.num_submits==1);
            assert(cp.num_mapped_queues.load(std::memory_order_acquire)==2);
        }
    };
    cp.SubmitAsc(1,commands);
    assert(cp.num_submits==1 && cp.num_mapped_queues==2);
    cp.mapped_queues[1].m_access.before_unlock={};
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    Until([&]{return cp.num_submits==0;});
    assert(cp.asc_executed==1);
    Stop(cp,worker);
}
void LateAscCase() {
    Liverpool cp;
    VideoOutPort port;
    cp.vo_port=&port;port.buffer_labels[0]=1;
    cp.asc_release_label=&port.buffer_labels[0];
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    auto task=cp.WaitTask(&packet);
    cp.mapped_queues[0].submits.push(task.handle);cp.num_submits=1;
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    Until([&]{return cp.submit_cv.timed_waits.load(std::memory_order_acquire)>0;});
    assert(cp.num_submits==1 && cp.num_mapped_queues==1);
    cp.asc_configuration[0]=0x12345678;
    const std::array<u32,1> commands{17};
    cp.SubmitAsc(1,commands);
    Until([&]{return cp.num_submits==0;});
    assert(cp.asc_executed==1 && port.buffer_labels[0]==0 && cp.num_mapped_queues==2);
    Stop(cp,worker);
}
int main(){
    Common::ElfInfo::Instance().serial="CUSA08809";
    AscPublicationCase(false);AscPublicationCase(true);LateAscCase();
    std::cout<<"ASC_PUBLICATION_PASS new/known queues, exact unlock and late wake\n";
    MultiQueueBreadcrumbCase(2);MultiQueueBreadcrumbCase(3);
    for(const char* serial:{"CUSA08809","CUSA08034","CUSA00785","OTHER","CUSA08809"}) {
        Common::ElfInfo::Instance().serial=serial;
        const bool cooperative=std::string(serial)=="CUSA08809" || std::string(serial)=="CUSA08034";
        assert(SotcCommandWaitEnabled()==cooperative);
        FlipCase(false,cooperative);FlipCase(true,cooperative);
        if(cooperative) {
            SyncCommandCase();BackoffCase(false);BackoffCase(true);PredicateAndBreadcrumb();
        }
        std::cout<<"CP_WAIT_GRAPH_PASS serial="<<serial<<" cooperative="<<cooperative<<'\n';
    }
}
'''
    replacements = {
        "ISLABEL": block(vh, "bool IsVoLabel("),
        "WAIT": block(vh, "void WaitVoLabel("),
        "SIGNAL": block(vh, "void SignalVoLabel("),
        "PREDICATE": actual_test,
        "HELPERS": "\n".join(block(cp, x) for x in (
            "static bool SotcCommandWaitEnabled()", "static u64 SotcCommandWaitNowNs()",
            "static void SotcCommandPause()")),
        "WAIT_METHODS": "\n".join(block(cp, x) for x in (
            "void Liverpool::NoteCommandWait(", "void Liverpool::ResetCommandWaitProgress()",
            "void Liverpool::BackoffCommandWait(")),
        "WAIT_FIELDS": ch[ch.index("struct CpWaitState {"):ch.index("    void ProcessCommands();")],
        "WAITCASE": wait_case,
        "TASK": block(ch, "struct Task {"),
        "SEND": block(ch, "template <bool wait_done = false>"),
        "COMMANDS": block(cp, "void Liverpool::ProcessCommands()"),
        "PROCESS": block(cp, "void Liverpool::Process(std::stop_token stoken)"),
        "SUBMIT_ASC": block(cp, "void Liverpool::SubmitAsc("),
        "SUBMIT": block(vc, "bool VideoOutDriver::SubmitFlip("),
        "INTERNAL": block(vc, "void VideoOutDriver::SubmitFlipInternal("),
        "FLIP": block(vc, "void VideoOutDriver::Flip("),
    }
    for key, value in replacements.items():
        src = src.replace("@@" + key + "@@", value)
    assert "@@" not in src
    controls = {
        "restore_vo_sleep": (
            "if (!SotcCommandWaitEnabled() && vo_port->IsVoLabel(wait_addr) &&",
            "if (vo_port->IsVoLabel(wait_addr) &&"),
        "bypass_predicate": (
            "while (!wait_reg_mem->Test(regs.reg_array, &observed))", "while (false)"),
        "drop_command_dispatch": (
            "callback();\n        cp_progress = true;", "cp_progress = true;"),
        "remove_backoff": (
            "if (!SotcCommandWaitEnabled()) return;\n    // The active donor backs off",
            "return;\n    // The active donor backs off"),
        "corrupt_observed": ("if (observed) *observed = value;", "if (observed) *observed = 0;"),
        "publish_task_before_count": (
            "std::scoped_lock lock{submit_mutex, queue.m_access};\n    queue.submits.emplace(task.handle);\n    ++num_submits;",
            "{std::scoped_lock queue_lock{queue.m_access};\n    queue.submits.emplace(task.handle);}\n"
            "    std::scoped_lock submit_lock{submit_mutex};\n    ++num_submits;"),
        "forget_wait_on_empty_queue": (
            "            cp_progress = false;\n            ProcessCommands();",
            "            cp_progress = false;\n            cp_wait.active = false;\n            ProcessCommands();"),
        "report_poll_queue_instead_of_wait_queue": (
            "cp_wait.reason, cp_wait.qid, cp_wait.address",
            "cp_wait.reason, curr_qid, cp_wait.address"),
    }
    with tempfile.TemporaryDirectory(prefix="sotc-cp-wait-") as temporary:
        output = pathlib.Path(temporary)
        def run(name, code, negative=False):
            path = output / (name + ".cpp")
            path.write_text(code)
            binary = path.with_suffix("")
            subprocess.run(["g++", "-std=c++20", "-O1", "-g", "-pthread", "-fsanitize=undefined",
                            "-fno-sanitize-recover=all", str(path), "-o", str(binary)], check=True)
            try:
                result = subprocess.run([str(binary)], text=True, capture_output=True, timeout=12)
                failed = result.returncode != 0
            except subprocess.TimeoutExpired:
                if not negative:
                    raise
                failed = True
            if negative:
                assert failed, f"negative control survived: {name}"
                print("NEGATIVE_REJECTED", name)
            else:
                assert not failed, result.stdout + result.stderr
                print(result.stdout, end="")
        run("effective", src)
        for name, (before, after) in controls.items():
            assert src.count(before) == 1, (name, src.count(before))
            run(name, src.replace(before, after, 1), negative=True)
    print("SOTC_CP_WAIT_GRAPH_PASS actual CP/VO methods, ASC publication, multi-queue breadcrumb, backoff, stop and 8 negatives")


if __name__ == "__main__":
    main()
