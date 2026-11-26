#!/usr/bin/env python3
"""Run real EndRendering and compact reason accounting with a clock boundary."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from test_order_readconst_pool import block
from port_order_pass_end_reasons import CALLS, function_span
from port_order_present_end_reasons import CALLS as PRESENT_CALLS


PROGRAM = r'''
#include <array>
#include <atomic>
#include <barrier>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <mutex>
#include <numeric>
#include <string_view>
#include <thread>
#include <vector>
#include "common/types.h"
#include "video_core/renderer_vulkan/order_render_pass_reasons.h"
struct ReasonClock {
 using time_point=std::chrono::steady_clock::time_point;
 inline static thread_local s64 us=0;
 inline static thread_local u64 calls=0;
 static time_point now(){++calls;return time_point{std::chrono::microseconds{us}};}
};
std::mutex log_mutex;std::vector<std::vector<u64>>logs;
template<class...T>void Capture(int,std::string_view text,T...args) {
 assert(text.starts_with("BACHATA_ORDER_PASS_END_REASON "));
 std::scoped_lock lock{log_mutex};logs.push_back({static_cast<u64>(args)...});
}
#define LOG_INFO Capture
constexpr int Render_Vulkan=0;
namespace Vulkan {
inline thread_local bool enabled=true;
bool UsesOrderRenderPassCoalescing(){return enabled;}
enum class OrderRenderPassEvent{End};
inline thread_local u64 old_ends=0;
void CountOrderRenderPass(OrderRenderPassEvent){++old_ends;}
@COUNTER@
struct Scheduler {
 bool is_rendering=false;u64 ends=0,drains=0;std::function<void()>on_drain;
 void DrainDrawPipe(){++drains;if(on_drain)on_drain();}
 struct Commands{Scheduler&s;void endRendering(){++s.ends;}};
 Commands CommandBuffer(){return {*this};}
 void EndRendering(OrderPassEndReason reason=OrderPassEndReason::Unspecified);
};
@END@
}
using namespace Vulkan;
void Closed(Scheduler&s,OrderPassEndReason reason,u32 n) {
 for(u32 i=0;i<n;++i){s.is_rendering=true;s.EndRendering(reason);}
}
void NoOpAndDrain() {
 Scheduler s;for(int i=0;i<4096;++i)s.EndRendering(OrderPassEndReason::Dispatch);
 assert(s.ends==0&&old_ends==0&&ReasonClock::calls==0&&logs.empty());
 s.on_drain=[&]{s.is_rendering=true;s.on_drain={};};
 s.EndRendering(OrderPassEndReason::ImageDownload);
 assert(s.ends==1&&old_ends==1&&ReasonClock::calls==1);
}
void Owners() {
 Scheduler a,b;
 Closed(a,OrderPassEndReason::IndirectClamp,512);Closed(b,OrderPassEndReason::Barrier,512);
 assert(ReasonClock::calls==2&&logs.empty());
 ReasonClock::us=6'000'000;
 Closed(a,OrderPassEndReason::IndirectClamp,512);Closed(b,OrderPassEndReason::Barrier,512);
 assert(ReasonClock::calls==4&&logs.size()==2&&old_ends==2048);
 for(size_t i=0;i<logs.size();++i){
  const auto&record=logs[i];assert(record.size()==27);assert(record[4]==1024);
  assert(record[0]==reinterpret_cast<std::uintptr_t>(i?&b:&a));
  const auto reason=i?OrderPassEndReason::Barrier:OrderPassEndReason::IndirectClamp;
  assert(record[5+unsigned(reason)]==1024);
  assert(std::accumulate(record.begin()+5,record.end(),u64{})==record[4]);
 }
}
void Threads() {
 Scheduler owner;std::vector<std::jthread>workers;std::barrier ready{2};
 // Direct counter calls isolate the same scheduler identity on independent
 // producer threads; real EndRendering itself is serialized by the draw owner.
 for(int n=0;n<2;++n)workers.emplace_back([&]{
  ready.arrive_and_wait();
  CountOrderPassEndReason(&owner,OrderPassEndReason::Present);ReasonClock::us=6'000'000;
  for(int i=1;i<1024;++i)CountOrderPassEndReason(&owner,OrderPassEndReason::Present);
  assert(ReasonClock::calls==2);
 });
 workers.clear();assert(logs.size()==2);
 assert(logs[0][0]==logs[1][0]&&logs[0][1]!=logs[1][1]);
 assert(logs[0][4]==1024&&logs[1][4]==1024);
}
void Disabled() {
 enabled=false;Scheduler s;Closed(s,OrderPassEndReason::ImageAlias,2048);
 assert(s.ends==2048&&old_ends==0&&ReasonClock::calls==0&&logs.empty());
}
void Unknown() {
 Scheduler s;s.is_rendering=true;s.EndRendering();ReasonClock::us=6'000'000;
 for(int i=1;i<1024;++i){s.is_rendering=true;s.EndRendering();}
 assert(logs.size()==1&&logs[0][5]==1024&&logs[0][4]==1024);
}
int main(){
 for(auto test:{NoOpAndDrain,Owners,Threads,Disabled,Unknown}){
  logs.clear();std::jthread worker{test};worker.join();
 }
 std::cout<<"ORDER_PASS_END_REASONS_PASS real_open_closures_owner_thread_sampling\n";
}
'''


def source_contracts(src: Path) -> None:
    calls = dict(CALLS)
    presenter = src / "video_core/renderer_vulkan/vk_presenter.cpp"
    if "EndRendering(Vulkan::OrderPassEndReason::Present)" in presenter.read_text():
        calls.update(PRESENT_CALLS)
    annotated = 0
    for name, functions in calls.items():
        text = (src / name).read_text()
        for signature, reason in functions.items():
            first, last = function_span(text, signature)
            body = text[first:last]
            assert body.count("EndRendering(Vulkan::OrderPassEndReason::" + reason + ");") == 1
            assert "EndRendering();" not in body
            annotated += 1
    scheduler = (src / "video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
    ending = block(scheduler, "void Scheduler::EndRendering(")
    assert ending.index("DrainDrawPipe();") < ending.index("if (!is_rendering)")
    assert ending.index("if (!is_rendering)") < ending.index("CountOrderPassEndReason(this, reason)")
    assert ending.count("CountOrderRenderPass(OrderRenderPassEvent::End)") == 1
    print("ORDER_PASS_END_PRODUCER_CONTRACT_PASS callers=" + str(annotated), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    src = args.source.resolve() / "src"
    source_contracts(src)
    text = (src / "video_core/renderer_vulkan/vk_scheduler.cpp").read_text()
    counter = block(text, "static void CountOrderPassEndReason(")
    # Clock is an explicit I/O boundary, not a replacement policy/algorithm.
    counter = counter.replace("std::chrono::steady_clock", "ReasonClock")
    ending = block(text, "void Scheduler::EndRendering(")
    program = PROGRAM.replace("@COUNTER@", counter).replace("@END@", ending)
    compiler = shlex.split(os.environ.get("CXX", "c++")) + [
        "-std=c++23", "-O1", "-g", "-Wall", "-Wextra", "-Werror", "-pthread",
        "-fsanitize=undefined", "-fno-sanitize-recover=all", "-I", str(src)]
    with tempfile.TemporaryDirectory(prefix="order-pass-end-") as tmp:
        folder = Path(tmp)
        def run(name: str, code: str, negative: bool = False) -> None:
            cpp, binary = folder / (name + ".cpp"), folder / name
            cpp.write_text(code)
            subprocess.run(compiler + [str(cpp), "-o", str(binary)], check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=15)
            if negative:
                assert result.returncode != 0, "Negative control accepted: " + name
                print("ORDER_PASS_END_NEGATIVE_PASS", name, flush=True)
            else:
                assert result.returncode == 0, result.stdout + result.stderr
                print(result.stdout, end="", flush=True)
        run("positive", program)
        controls = {
            "count_noop": ("    if (!is_rendering) {", "    CountOrderPassEndReason(this, reason);\n    if (!is_rendering) {"),
            "no_real_closure_counter": ("    if (UsesOrderRenderPassCoalescing()) CountOrderPassEndReason(this, reason);", "    (void)reason;"),
            "merge_owners": ("candidate.owner == owner", "candidate.owner != nullptr"),
            "clock_every_closure": ("if (++window->unchecked < 1024) return;", "++window->unchecked;"),
            "no_drain": ("    DrainDrawPipe();", ""),
        }
        for name, (old, new) in controls.items():
            assert old in program
            run(name, program.replace(old, new, 1), True)


if __name__ == "__main__":
    main()
