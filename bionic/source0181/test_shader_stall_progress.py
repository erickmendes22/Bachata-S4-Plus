#!/usr/bin/env python3
"""Exercise the effective phase/wait code with deterministic compiler/GPU boundaries."""
import argparse
from pathlib import Path
import re

from test_donor_alu_semantics import function, run_cpp
from assert_native_api import has_translation_srt_callback


def without_includes(source):
    return re.sub(r"^\s*#(?:include|pragma)[^\n]*\n", "", source, flags=re.M)


def phase_test(root):
    helper = without_includes((root / "common/bachata_progress.h").read_text())
    cache = (root / "video_core/renderer_vulkan/vk_pipeline_cache.cpp").read_text()
    compile_module = function(cache, "vk::ShaderModule PipelineCache::CompileModule(")
    assert has_translation_srt_callback(cache)
    # Keep the structural ABI check tied to the actual callback position.
    # A live sync elsewhere, or one appearing only in diagnostic text, cannot
    # replace the guest-read barrier inside TranslateProgram.
    no_sync = compile_module.replace("srt_sync(info);", "(void)info;")
    assert not has_translation_srt_callback(no_sync)
    no_guard = compile_module.replace("if (srt_sync)", "if (false)")
    assert not has_translation_srt_callback(no_guard)
    too_early = no_sync.replace("const auto ir_program =",
        "if (srt_sync) srt_sync(info);\n    const auto ir_program =", 1)
    assert not has_translation_srt_callback(too_early)
    log_only = compile_module.replace("srt_sync(info);", '(void)"srt_sync(info);";')
    assert not has_translation_srt_callback(log_only)
    print("SHADER_PROGRESS_SRT_CALLBACK_POSITION_PASS negative_controls=4", flush=True)
    cpp = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>
using u32=uint32_t;using u64=uint64_t;
'''+helper+r'''
struct Event {std::string phase,event;u64 hash;};
std::vector<Event> events;std::vector<std::string> calls;
template<class...Args>void Log(const char* format,Args&&... args){
    if constexpr(sizeof...(Args)==9){
        if(std::string_view(format).starts_with("BACHATA_GPU_PROGRESS")){
            const auto values=std::forward_as_tuple(args...);
            events.push_back({std::get<0>(values),std::get<1>(values),std::get<2>(values)});
            assert(std::get<5>(values)==17&&std::get<6>(values)==16&&std::get<7>(values)==15);
            assert(std::get<8>(values)>=0);
        }
    }
}
#define LOG_INFO(channel,...) Log(__VA_ARGS__)
namespace vk {using ShaderModule=u32;}
std::string fail_phase;bool patched=false;unsigned registered=0;
void Boundary(const char* phase){calls.emplace_back(phase);if(fail_phase==phase)throw std::runtime_error(phase);}
namespace Shader {
enum class HwStage {Vertex};enum class SwStage {Vertex,Compute};
struct Info {
    HwStage hw_stage{};SwStage sw_stage{};u64 pgm_hash=0x5dab0dab;
    struct Image {u32 compiled_binding_count{};u32 LiveNumBindings(const Info&)const{return 3;}};
    std::vector<Image> images=std::vector<Image>(1);std::vector<int> buffers,samplers;
    std::vector<u32> flattened_ud_buf;
};
struct RuntimeInfo{};
namespace Backend {struct Bindings{};namespace SPIRV {
std::vector<u32> EmitSPIRV(int,RuntimeInfo&,int,Bindings&){Boundary("emit_spirv");return {1,2,3};}
}}
template<class Sync>int TranslateProgram(std::span<const u32>,int&,Info&,RuntimeInfo&,int,Sync sync){
    Boundary("translate");sync();return 42;
}
}
namespace Common::FS {
enum class PathType{ShaderDir};enum class FileAccessMode{Create};
std::filesystem::path GetUserPath(PathType){return "/tmp";}
struct IOFile {IOFile(const std::filesystem::path&,FileAccessMode){};template<class T>void WriteSpan(T){};};
}
struct Settings {bool IsPatchShaders()const{return patched;}bool IsShaderCollect()const{return false;}}EmulatorSettings;
struct Debug {template<class...Args>void CollectShader(Args&&...){};}DebugState;
namespace AmdGpu {bool BachataOrderNoMsaa(){return false;}}
namespace Vulkan {
using Shader::SwStage;
struct Scheduler {
    u64 CurrentTick()const{return 17;}u64 RecordedSubmitTick()const{return 16;}
    Scheduler* GetWorkSemaphore(){return this;}u64 KnownGpuTick()const{return 15;}
};
struct Instance{u32 GetDevice()const{return 1;}};
template<class...Args>void SetObjectName(Args&&...){}
vk::ShaderModule CompileSPV(std::span<const u32>,u32){Boundary("create_shader_module");return 7;}
class PipelineCache {
public:
    Scheduler scheduler;Instance instance;int pools{},profile{};
    std::function<void(Shader::Info&)> srt_sync=[](auto&){Boundary("srt_sync");};
    template<class...Args>void DumpShader(Args&&...){}
    std::string GetShaderName(Shader::HwStage,u64,size_t){return "test";}
    std::optional<std::vector<u32>> GetShaderPatch(u64,Shader::HwStage,size_t,const char*){
        return patched?std::optional<std::vector<u32>>{{9,8,7}}:std::nullopt;
    }
    template<class...Args>vk::ShaderModule QueueCapturedShader(Args&&...){throw std::logic_error("disabled worker path");}
    void RegisterShaderBinary(std::vector<u32>&&,u64,size_t){++registered;}
    vk::ShaderModule CompileModule(Shader::Info&,Shader::RuntimeInfo&,
                                  const std::span<const u32>&,size_t,Shader::Backend::Bindings&);
};
'''+compile_module+r'''
}
void TestCompilePhases(){
    for(bool patch:{false,true})for(const std::string failure:{"","translate","srt_sync","emit_spirv","create_shader_module"}){
        patched=patch;fail_phase=failure;events.clear();calls.clear();registered=0;
        Vulkan::PipelineCache cache;Shader::Info info;Shader::RuntimeInfo runtime;
        Shader::Backend::Bindings bindings;const u32 words[]{1,2};
        bool threw=false;
        try{assert(cache.CompileModule(info,runtime,std::span<const u32>{words},4,bindings)==7);}
        catch(const std::runtime_error&){threw=true;}
        assert(threw==!failure.empty());
        std::vector<std::string> active;
        for(const auto& e:events){
            assert(e.hash==info.pgm_hash);
            if(e.event=="begin")active.push_back(e.phase);
            else{assert(!active.empty()&&active.back()==e.phase);active.pop_back();}
        }
        if(failure.empty()){
            assert(active.empty()&&registered==1&&events.size()==8);
            assert((calls==std::vector<std::string>{"translate","srt_sync","emit_spirv","create_shader_module"}));
            assert(info.images[0].compiled_binding_count==3);
        }else{
            assert(registered==0&&!active.empty()&&active.back()==failure);
            assert(events.back().event=="begin"&&events.back().phase==failure);
        }
    }
    auto quiet=[](const char*,const char*,auto){};
    auto owned=Common::BachataProgress::Phase("move",quiet,[]{return std::make_unique<int>(42);});
    assert(*owned==42);int value=7;
    int& alias=Common::BachataProgress::Phase("ref",quiet,[&]() -> int& {return value;});
    assert(&alias==&value);
    std::cout<<"SHADER_PROGRESS_COMPILE_PHASES_PASS cases=10\n";
}
void TestWaitOnce(){
    std::mutex mutex;std::condition_variable cv;
    std::unique_lock lock{mutex};unsigned reports=0;bool ready=true;
    Common::BachataProgress::WaitOnce(cv,lock,[&]{return ready;},[&]{++reports;},std::chrono::milliseconds{0});
    assert(reports==0&&lock.owns_lock());ready=false;
    std::atomic_bool sampled=false;
    std::thread worker([&]{
        sampled.wait(false);
        {std::scoped_lock guard{mutex};ready=true;}
        cv.notify_all();
    });
    Common::BachataProgress::WaitOnce(cv,lock,[&]{return ready;},[&]{
        assert(lock.owns_lock()&&!ready);++reports;
        sampled.store(true);sampled.notify_all();
    },std::chrono::milliseconds{0});
    assert(lock.owns_lock()&&ready&&reports==1);lock.unlock();worker.join();
    std::cout<<"SHADER_PROGRESS_WAIT_ONCE_PASS\n";
}
int main(){TestCompilePhases();TestWaitOnce();}
'''
    run_cpp(cpp, "shader_stall_progress")


def timeline_test(root):
    source = (root / "video_core/renderer_vulkan/vk_semaphore.cpp").read_text()
    wait = function(source, "void Semaphore::Wait(")
    cpp = r'''
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
using u32=uint32_t;using u64=uint64_t;
unsigned warnings=0;
#define LOG_WARNING(...) (++warnings)
#define ASSERT_MSG(condition,...) do{if(!(condition))throw std::runtime_error("GPU wait failure");}while(0)
namespace vk {
enum class Result{eSuccess,eTimeout,eErrorDeviceLost};
struct SemaphoreWaitInfo{u32 semaphoreCount;const u64* pSemaphores;const u64* pValues;};
}
namespace Vulkan {
constexpr u64 WAIT_TIMEOUT=std::numeric_limits<u64>::max();
struct Device{
    mutable std::vector<u64> timeouts;std::vector<vk::Result> results;
    vk::Result waitSemaphores(const vk::SemaphoreWaitInfo* info,u64 timeout)const{
        assert(info->semaphoreCount==1&&*info->pValues==5&&*info->pSemaphores==9);
        assert(timeouts.size()<results.size());const auto result=results[timeouts.size()];
        timeouts.push_back(timeout);return result;
    }
};
struct Instance{Device device;const Device& GetDevice()const{return device;}};
struct Semaphore {
    Instance instance;u64 known=0,refresh_value=0;unsigned refreshes=0;
    struct Handle{u64 value=9;const u64& get()const{return value;}}semaphore;
    bool IsFree(u64 tick)const{return known>=tick;}
    u64 KnownGpuTick()const{return known;}u64 CurrentTick()const{return 6;}
    void Refresh(){++refreshes;known=refresh_value;}
    void Wait(u64 tick);
};
'''+wait+r'''
}
int main(){
    using vk::Result;
    {Vulkan::Semaphore s;s.known=5;s.Wait(5);assert(s.refreshes==0&&s.instance.device.timeouts.empty());}
    {Vulkan::Semaphore s;s.refresh_value=5;s.Wait(5);assert(s.refreshes==1&&s.instance.device.timeouts.empty());}
    for(unsigned count=0;count<3;++count){
        Vulkan::Semaphore s;warnings=0;s.instance.device.results.assign(count,Result::eTimeout);
        s.instance.device.results.push_back(Result::eSuccess);s.Wait(5);
        assert(warnings==(count?1u:0u)&&s.refreshes==2);
        assert(s.instance.device.timeouts.size()==count+1);
        assert(s.instance.device.timeouts[0]==2'000'000'000ULL);
        for(unsigned i=1;i<=count;++i)assert(s.instance.device.timeouts[i]==Vulkan::WAIT_TIMEOUT);
    }
    {Vulkan::Semaphore s;s.instance.device.results={Result::eErrorDeviceLost};bool failed=false;
     try{s.Wait(5);}catch(const std::runtime_error&){failed=true;}
     assert(failed&&s.instance.device.timeouts.size()==1);}
    std::cout<<"SHADER_PROGRESS_TIMELINE_WAIT_PASS cases=6\n";
}
'''
    run_cpp(cpp, "shader_stall_timeline")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    root = args.source / "src" if (args.source / "src").exists() else args.source
    phase_test(root)
    timeline_test(root)


if __name__ == "__main__":
    main()
