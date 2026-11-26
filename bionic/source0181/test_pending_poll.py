#!/usr/bin/env python3
"""Count real Semaphore::Refresh Vulkan queries and execute scheduler callbacks.

Scheduler Hot/forced Pop, DeferOperation, SubmitExecution, Wait, Finish, and
Semaphore Refresh/Wait are extracted from the effective tree. The four actual
rasterizer entry prefixes drive both the new and pre-change control. Vulkan
submission/completion are deterministic boundaries, not a substitute queue.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

def function(text, marker):
    if text.count(marker) != 1:
        raise AssertionError(f"pending poll method drift: {marker}: {text.count(marker)}")
    start = text.index(marker)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[start:end + 1]
    raise AssertionError(f"unclosed method: {marker}")


def strip_includes(text):
    return re.sub(r"^\s*#(?:include|pragma)[^\n]*\n", "", text, flags=re.M)


def make_program(root):
    src = root / "src" if (root / "src").is_dir() else root
    scheduler = (src / "video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
    header = (src / "video_core/renderer_vulkan/vk_scheduler.h").read_text()
    semaphore = (src / "video_core/renderer_vulkan/vk_semaphore.cpp").read_text()
    sem_header = (src / "video_core/renderer_vulkan/vk_semaphore.h").read_text()
    rasterizer = (src / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
    unique = strip_includes((src / "common/unique_function.h").read_text())
    compat = src / "common/bachata_compat_profile.h"
    policy = strip_includes(compat.read_text()) if compat.exists() else ""
    # A mutation can deliberately remove the helper's only consumer. Keep that
    # control executable so it fails a runtime contract, not an unused warning.
    policy += "\n[[maybe_unused]] " + function(scheduler, "static bool UsesTargetPendingPoll()")
    assert '#include "common/elf_info.h"' in scheduler.splitlines()
    hot = function(scheduler, "void Scheduler::PopPendingOperationsHot(")
    forced = function(scheduler, "void Scheduler::PopPendingOperations(")
    assert "(bool refresh)" in forced
    assert header.count("void PopPendingOperationsHot();") == 1
    assert header.count("u32 pending_hot_polls = 0;") == 1
    sem_inline = "\n".join(function(sem_header, marker) for marker in (
        "[[nodiscard]] u64 CurrentTick()", "[[nodiscard]] u64 KnownGpuTick()",
        "[[nodiscard]] bool IsFree(", "[[nodiscard]] u64 NextTick()",
        "[[nodiscard]] vk::Semaphore Handle()"))
    scheduler_inline = "\n".join(function(header, marker) for marker in (
        "void DrainDrawPipe()", "[[nodiscard]] u64 CurrentTick()",
        "[[nodiscard]] u64 RecordedSubmitTick()", "void DeferOperation("))
    scheduler_methods = "\n".join(function(scheduler, marker) for marker in (
        "void Scheduler::WaitSubmitted(", "void Scheduler::Flush(SubmitInfo&",
        "void Scheduler::Flush()", "void Scheduler::Wait(", "void Scheduler::Finish(",
        "void Scheduler::SubmitExecution("))
    prefixes = []
    declarations = []
    for name in ("Draw", "DrawIndirect", "DispatchDirect", "DispatchIndirect"):
        method = function(rasterizer, f"void Rasterizer::{name}(")
        assert method.count("scheduler.PopPendingOperationsHot();") == 1
        end = method.index("scheduler.PopPendingOperationsHot();") + len("scheduler.PopPendingOperationsHot();")
        prefix = method[:end] + "\n}\n"
        prefixes.append(prefix)
        declarations.append(prefix[:prefix.index("{")].replace("Rasterizer::", "") + ";")
    prefixes = "\n".join(prefixes)
    controls = prefixes.replace("Rasterizer::", "ControlRasterizer::").replace(
        "scheduler.PopPendingOperationsHot();", "scheduler.PopPendingOperations();")

    program = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <queue>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
using u16=uint16_t;using u32=uint32_t;using u64=uint64_t;using VAddr=u64;
#define __ANDROID__ 1
#define TRACY_GPU_ENABLED 0
#define ASSERT_MSG(value,...) assert(value)
#define LOG_WARNING(...) ((void)0)
#define RENDERER_TRACE ((void)0)
#define WAIT_TIMEOUT 1000000000ULL
namespace Common {
struct ElfInfo {
    inline static std::string_view serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo instance;return instance;}
    std::string_view GameSerial()const{return serial;}
};
}
@UNIQUE@
@POLICY@
namespace vk {
enum class Result {eSuccess,eTimeout};
using Semaphore=u64;using CommandBuffer=u64;
struct UniqueSemaphore {u64 value=1;const u64& get()const{return value;}u64 operator*()const{return value;}};
struct SemaphoreWaitInfo {u32 semaphoreCount;const Semaphore* pSemaphores;const u64* pValues;};
}
namespace Vulkan {
struct Device {
    u64 queries=0,waits=0,counter=0,submitted=0;
    bool complete_on_submit=false;
    auto getSemaphoreCounterValue(vk::Semaphore){++queries;return std::pair{vk::Result::eSuccess,counter};}
    vk::Result waitSemaphores(const vk::SemaphoreWaitInfo* info,u64){
        ++waits;assert(info->semaphoreCount==1&&*info->pValues<=submitted);
        counter=std::max(counter,*info->pValues);return vk::Result::eSuccess;
    }
};
struct Instance {mutable Device device;Device& GetDevice()const{return device;}};
class Semaphore {
public:
    const Instance& instance;vk::UniqueSemaphore semaphore;
    std::atomic<u64> gpu_tick{0},current_tick{1};
    explicit Semaphore(const Instance& value):instance(value){}
    void Refresh();void Wait(u64);
@SEM_INLINE@
};
@SEM_REFRESH@
@SEM_WAIT@
struct SubmitInfo {u64 signal=0;void AddSignal(vk::Semaphore,u64 tick){signal=tick;}};
void QueueSubmit(const Instance& instance,const SubmitInfo& info,const std::vector<vk::CommandBuffer>&){
    auto& d=instance.GetDevice();d.submitted=std::max(d.submitted,info.signal);
    if(d.complete_on_submit)d.counter=d.submitted;
}
struct Recorder {
    std::queue<Common::UniqueFunction<void>> work;bool eager=true;u32 kicks=0;
    void Run(Common::UniqueFunction<void>&& fn){work.push(std::move(fn));}
    void Kick(){++kicks;if(!eager)return;while(!work.empty()){auto fn=std::move(work.front());work.pop();fn();}}
    u64 Real(u64 fake){return fake;}void Retire(u32){}
};
class Scheduler {
public:
    Instance instance;Semaphore work_semaphore{instance};
    struct PendingOp {Common::UniqueFunction<void> callback;u64 gpu_tick;};
    std::queue<PendingOp> pending_ops;std::recursive_mutex pending_ops_mutex;
    u32 pending_hot_polls=0;std::atomic<u64> recorded_submit_tick{0};
    std::unique_ptr<Recorder> recorder;
    struct Session {vk::CommandBuffer upload=0,primary=1;};std::vector<Session> sessions{{}};
    std::function<void(SubmitInfo&)> on_submit;
    u32 drains=0,begin_sessions=0;
    std::function<void()> draw_pipe_drain=[this]{++drains;};
    void EndSession(){}void BeginSession(){++begin_sessions;sessions.push_back({});}
    void WaitSubmitted(u64,bool kick=true);void Wait(u64);void Finish();
    void SubmitExecution(SubmitInfo&);void Flush(SubmitInfo&);void Flush();
    void PopPendingOperations(bool refresh=true);void PopPendingOperationsHot();
@SCHEDULER_INLINE@
};
@FORCED@
@HOT@
@SCHEDULER_METHODS@
struct GraphicsPipeline{};struct ComputePipeline{};
struct Rasterizer {
    Scheduler& scheduler;struct {bool valid=true;}bind_memo;
    explicit Rasterizer(Scheduler& s):scheduler(s){}
@DECLARATIONS@
};
struct ControlRasterizer {
    Scheduler& scheduler;struct {bool valid=true;}bind_memo;
    explicit ControlRasterizer(Scheduler& s):scheduler(s){}
@DECLARATIONS@
};
@PREFIXES@
@CONTROLS@
template<class R>void HotCall(R& r,u32 kind){
    switch(kind%4){
    case 0:r.Draw(false,0,nullptr,false);break;
    case 1:r.DrawIndirect(true,0,0,20,1,0,0,0,nullptr,false);break;
    case 2:r.DispatchDirect(nullptr,false);break;
    case 3:r.DispatchIndirect(0,0,0,nullptr,false);break;
    }
}
void PublishRecorded(Scheduler& s,u64 tick,u64 gpu){
    s.work_semaphore.current_tick=tick+1;
    s.recorded_submit_tick=tick;
    s.instance.device.submitted=tick;s.instance.device.counter=gpu;
}
void TestEmptyAndUnsubmitted(){
    Scheduler s,old;Rasterizer r{s};ControlRasterizer control{old};
    for(u32 i=0;i<256;++i){HotCall(r,i);HotCall(control,i);}
    assert(s.instance.device.queries==0&&old.instance.device.queries==256);
    unsigned calls=0,old_calls=0;s.DeferOperation([&]{++calls;});old.DeferOperation([&]{++old_calls;});
    for(u32 i=0;i<256;++i){HotCall(r,i);HotCall(control,i);}
    assert(s.instance.device.queries==0&&old.instance.device.queries==512);
    assert(calls==0&&old_calls==0&&s.pending_ops.size()==1);
    assert(s.pending_hot_polls==0); // Unsubmitted work cannot consume the polling budget.
    std::cout<<"PENDING_POLL_QUERY_COUNT empty256=0/256 unsubmitted256=0/256 new/old\n";
}
void TestRecorderLag(){
    Scheduler s;Rasterizer r{s};s.recorder=std::make_unique<Recorder>();s.recorder->eager=false;
    unsigned calls=0;s.DeferOperation([&]{++calls;});s.Flush();
    assert(s.CurrentTick()==2&&s.RecordedSubmitTick()==0&&s.recorder->work.size()==1);
    const u64 before=s.instance.device.queries;
    for(u32 i=0;i<128;++i)HotCall(r,i);
    assert(s.instance.device.queries==before&&calls==0&&s.pending_hot_polls==0);
    s.recorder->eager=true;s.recorder->Kick();assert(s.RecordedSubmitTick()==1);
    s.instance.device.counter=1;
    for(u32 i=0;i<31;++i)HotCall(r,i);
    assert(calls==0&&s.instance.device.queries==before);
    HotCall(r,3);assert(calls==1&&s.instance.device.queries==before+1);
    std::cout<<"PENDING_POLL_RECORDER_PUBLICATION_PASS\n";
}
void TestPollLimitAndKnownTick(){
    Scheduler s,old;Rasterizer r{s};ControlRasterizer control{old};
    unsigned calls=0,old_calls=0;s.DeferOperation([&]{++calls;});old.DeferOperation([&]{++old_calls;});
    PublishRecorded(s,1,0);PublishRecorded(old,1,0);
    for(u32 i=0;i<64;++i){HotCall(r,i);HotCall(control,i);}
    assert(s.instance.device.queries==2&&old.instance.device.queries==64&&calls==0&&old_calls==0);
    s.instance.device.counter=1;
    for(u32 i=0;i<31;++i)HotCall(r,i);
    assert(calls==0);HotCall(r,3);assert(calls==1&&s.pending_ops.empty());
    for(u32 kind=0;kind<4;++kind){
        Scheduler known;Rasterizer entry{known};unsigned invoked=0;
        known.DeferOperation([&]{++invoked;});PublishRecorded(known,1,1);
        known.work_semaphore.gpu_tick=1;known.pending_hot_polls=1;
        HotCall(entry,kind);assert(invoked==1&&known.instance.device.queries==0);
    }
    // The counter wraps as an unsigned value; no special long-running-session failure.
    Scheduler wrap;Rasterizer entry{wrap};wrap.DeferOperation([]{});PublishRecorded(wrap,1,0);
    wrap.pending_hot_polls=std::numeric_limits<u32>::max();HotCall(entry,0);
    assert(wrap.pending_hot_polls==0&&wrap.instance.device.queries==1);
    std::cout<<"PENDING_POLL_QUERY_COUNT submitted_pending64=2/64 new/old; known-ready=0\n";
}
void TestForcedWaitSubmitAndRecovery(){
    for(bool recorder:{false,true}){
        Scheduler s;Rasterizer r{s};if(recorder)s.recorder=std::make_unique<Recorder>();
        unsigned calls=0;s.DeferOperation([&]{++calls;});s.Flush();
        assert(calls==0);s.pending_hot_polls=0;s.instance.device.counter=1;
        const u64 before=s.instance.device.queries;
        s.PopPendingOperations(); // explicit recovery ignores the hot budget
        assert(calls==1&&s.instance.device.queries==before+1);
        s.DeferOperation([&]{++calls;});s.instance.device.complete_on_submit=true;
        s.Flush();assert(calls==2); // submit force/known path is never rate limited
        s.instance.device.complete_on_submit=false;s.DeferOperation([&]{++calls;});s.Flush();
        const u64 tick=s.CurrentTick()-1;
        s.Wait(tick); // unchanged existing boundary: the caller drains after Wait
        const u64 after_wait=s.instance.device.queries;
        s.PopPendingOperations(false);
        assert(calls==3&&s.instance.device.queries==after_wait);
        // FaultManager uses the public default after Wait. It also stays forced.
        s.DeferOperation([&]{++calls;});s.Flush();s.Wait(s.CurrentTick()-1);
        s.PopPendingOperations();assert(calls==4);
        // At the next hot entry, already completed callbacks also retire immediately.
        s.DeferOperation([&]{++calls;});s.Flush();s.Wait(s.CurrentTick()-1);
        const u64 known=s.instance.device.queries;HotCall(r,0);
        assert(calls==5&&s.instance.device.queries==known);
    }
    std::cout<<"PENDING_POLL_FORCE_WAIT_SUBMIT_RECOVERY_PASS\n";
}
struct Owned {unsigned& destroyed;u64 magic=0x12345678;explicit Owned(unsigned& d):destroyed(d){}~Owned(){++destroyed;}};
void TestNestedFinishAndFifo(){
    for(bool recorder:{false,true}){
        Scheduler s;Rasterizer r{s};if(recorder)s.recorder=std::make_unique<Recorder>();
        std::vector<unsigned> entered;unsigned destroyed=0;bool freed=false;
        s.DeferOperation([&,owned=std::make_unique<Owned>(destroyed)]{
            entered.push_back(1);assert(entered.size()==1&&destroyed==0);
            s.instance.device.complete_on_submit=true;
            s.Finish(); // OOM retry must see later eligible frees before returning
            assert(freed&&destroyed==0&&owned->magic==0x12345678);
            entered.push_back(3);
            s.DeferOperation([&]{entered.push_back(4);}); // future tick, must remain queued
            s.PopPendingOperations(false);
            assert(entered.back()==3);
        });
        s.work_semaphore.current_tick=2;
        s.DeferOperation([&]{entered.push_back(2);freed=true;});
        PublishRecorded(s,1,1);s.work_semaphore.gpu_tick=1;
        HotCall(r,0);
        assert((entered==std::vector<unsigned>{1,2,3})&&destroyed==1&&s.pending_ops.size()==1);
        s.Finish();s.PopPendingOperations(false);
        assert((entered==std::vector<unsigned>{1,2,3,4})&&s.pending_ops.empty());
    }
    // Reentrant pop and same-tick append preserve invocation FIFO, including
    // callbacks that finish while the outer callback still owns its capture.
    Scheduler s;std::vector<unsigned> order;
    s.DeferOperation([&]{order.push_back(1);s.DeferOperation([&]{order.push_back(3);});s.PopPendingOperations(false);});
    s.DeferOperation([&]{order.push_back(2);});
    s.work_semaphore.gpu_tick=1;s.PopPendingOperations(false);
    assert((order==std::vector<unsigned>{1,2,3})&&s.pending_ops.empty());
    std::cout<<"PENDING_POLL_NESTED_FINISH_OOM_LIFETIME_FIFO_PASS\n";
}
void TestTitleScope(){
    Scheduler s;Rasterizer r{s};
    Common::ElfInfo::serial="UNRELATED";
    for(u32 i=0;i<64;++i)HotCall(r,i);
    assert(s.instance.device.queries==64);
    // No static cache of the first title in a reusable process.
    Common::ElfInfo::serial="CUSA00785";for(u32 i=0;i<64;++i)HotCall(r,i);
    assert(s.instance.device.queries==64);
    Common::ElfInfo::serial="CUSA08809";for(u32 i=0;i<64;++i)HotCall(r,i);
    assert(s.instance.device.queries==64);
    Common::ElfInfo::serial="UNRELATED";HotCall(r,0);assert(s.instance.device.queries==65);
    std::cout<<"PENDING_POLL_TITLE_REUSE_PASS\n";
}
}
int main(){
    for(auto serial:{"CUSA00785","CUSA08809","CUSA08034"}){
        Common::ElfInfo::serial=serial;
        Vulkan::TestEmptyAndUnsubmitted();Vulkan::TestRecorderLag();
        Vulkan::TestPollLimitAndKnownTick();Vulkan::TestForcedWaitSubmitAndRecovery();
        Vulkan::TestNestedFinishAndFifo();
    }
    Vulkan::TestTitleScope();std::cout<<"BACHATA_PENDING_POLL_PASS\n";
}
'''
    replacements = {"UNIQUE": unique, "POLICY": policy, "SEM_INLINE": sem_inline,
                    "SEM_REFRESH": function(semaphore, "void Semaphore::Refresh("),
                    "SEM_WAIT": function(semaphore, "void Semaphore::Wait("),
                    "SCHEDULER_INLINE": scheduler_inline, "FORCED": forced, "HOT": hot,
                    "SCHEDULER_METHODS": scheduler_methods,
                    "DECLARATIONS": "\n".join(declarations), "PREFIXES": prefixes,
                    "CONTROLS": controls}
    for name, value in replacements.items():
        program = program.replace("@" + name + "@", value)
    return program, hot, forced


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    program, hot, forced = make_program(args.source)
    # Regressions must fail executable contracts, not merely text checks.
    variants = [("actual", program, True)]
    mutations = {
        "old_per_draw_poll": hot[:hot.index("{") + 1] + "\n    PopPendingOperations();\n}",
        "query_unsubmitted": hot.replace("front_tick >= CurrentTick() ||", "false ||").replace(
            "(recorder && front_tick > RecordedSubmitTick())", "false"),
        "ignore_recorder_lag": hot.replace("(recorder && front_tick > RecordedSubmitTick())", "false"),
        "unlimited_hot_poll": hot.replace("& 31u", "& 0u"),
        "delay_known_callbacks": hot.replace("PopPendingOperations(false);", "return;"),
        "all_titles_hot": hot.replace("!UsesTargetPendingPoll()", "false"),
    }
    for name, changed in mutations.items():
        assert changed != hot, name
        variants.append((name, program.replace(hot, changed, 1), False))
    old_invocation = """        auto operation = std::move(pending_ops.front());
        pending_ops.pop();
        operation.callback();"""
    assert forced.count(old_invocation) == 1
    changed = forced.replace(old_invocation, """        pending_ops.front().callback();
        pending_ops.pop();""")
    variants.append(("callback_before_pop", program.replace(forced, changed, 1), False))
    changed = forced.replace("    DrainDrawPipe();", "    if ((++pending_hot_polls & 31u) != 0) return;\n    DrainDrawPipe();", 1)
    variants.append(("limit_forced_completion", program.replace(forced, changed, 1), False))
    with tempfile.TemporaryDirectory(prefix="bachata-pending-poll-") as directory:
        root = Path(directory)
        for name, content, success in variants:
            source = root / (name + ".cpp")
            binary = root / name
            source.write_text(content)
            compiled = subprocess.run(["c++", "-std=c++23", "-O1", "-pthread", "-Wall", "-Wextra", "-Werror",
                            "-Wno-unused-parameter", "-fsanitize=undefined", "-fno-sanitize-recover=all",
                            str(source), "-o", str(binary)], capture_output=True, text=True)
            assert compiled.returncode == 0, (name, compiled.stderr[:6000])
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=20)
            assert (result.returncode == 0) == success, (name, result.stdout, result.stderr)
            if success:
                print(result.stdout.strip())
            else:
                assert "Assertion" in result.stderr or "runtime error:" in result.stderr, (name, result.stderr)
                print("BACHATA_PENDING_POLL_NEGATIVE_PASS " + name)


if __name__ == "__main__":
    main()
