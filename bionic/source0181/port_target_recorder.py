"""Integrate the actual donor's Vulkan recording queue, not its executable or CPU backend."""
from pathlib import Path
import shutil

def apply(root):
    d=root/"src/video_core/renderer_vulkan"
    def edit(p,a,b):
        s=p.read_text()
        if s.count(a)!=1: raise RuntimeError(f"recorder anchor {p.name}: {a[:90]} ({s.count(a)})")
        p.write_text(s.replace(a,b,1))
    for n in ("vk_recorder.h","vk_recorder.cpp","vk_recorder_cmds.inc"):
        shutil.copyfile(Path(__file__).parent/"recorder"/n,d/n)
    h=d/"vk_scheduler.h"; c=d/"vk_scheduler.cpp"
    edit(h,"class Instance;","class Instance;\nclass CommandRecorder;")
    edit(h,"explicit Scheduler(const Instance& instance);","explicit Scheduler(const Instance& instance, bool record_thread = false);")
    edit(h,"    void Wait(u64 tick);","""    void Wait(u64 tick);
    void WaitSubmitted(u64 tick, bool kick = true);
    void ClaimRecorder();
    void DrainRecorder();
    void RecordDeferred(Common::UniqueFunction<void, vk::CommandBuffer>&& func);
    bool HasRecordThread() const { return recorder != nullptr; }""")
    edit(h,"    void SubmitExecution(SubmitInfo& info);","    void SubmitExecution(SubmitInfo& info);\n    void BeginRecorded(vk::CommandBuffer fake);")
    edit(h,"    tracy::VkCtxScope* profiler_scope{};","""    tracy::VkCtxScope* profiler_scope{};
    std::atomic<u64> recorded_submit_tick{0};
    std::unique_ptr<CommandRecorder> recorder;""")
    edit(c,'#include "video_core/renderer_vulkan/vk_scheduler.h"','#include "video_core/renderer_vulkan/vk_scheduler.h"\n#include "video_core/renderer_vulkan/vk_recorder.h"\n#include <span>')
    edit(c,"Scheduler::Scheduler(const Instance& instance)","Scheduler::Scheduler(const Instance& instance, bool record_thread)")
    edit(c,"    BeginSession();\n    priority_pending_ops_thread =","""#if !TRACY_GPU_ENABLED
    if(record_thread) {
        recorder = std::make_unique<CommandRecorder>();
        LOG_INFO(Render_Vulkan,"BACHATA_GPU_RECORDER enabled");
    }
#endif
    BeginSession();
    priority_pending_ops_thread =""")
    edit(c,"Scheduler::~Scheduler() {","""Scheduler::~Scheduler() {
    if(recorder) {
        recorder->ClaimProducer();
        recorder->Sync();
        recorder.reset();
    }""")
    edit(c,"void Scheduler::BeginRendering(","""void Scheduler::ClaimRecorder() {
    if(recorder) recorder->ClaimProducer();
}
void Scheduler::DrainRecorder() {
    if(recorder) recorder->Sync();
}
void Scheduler::RecordDeferred(Common::UniqueFunction<void, vk::CommandBuffer>&& func) {
    const auto fake=CommandBuffer();
    if(!recorder) {func(vk::CommandBuffer{fake});return;}
    recorder->CountCommand();
    recorder->Run([this,fake,func=std::move(func)]{
        func(vk::CommandBuffer{recorder->Real(fake)});
    });
}
void Scheduler::BeginRecorded(vk::CommandBuffer fake) {
    const auto real=command_pool.Commit();
    Check(real.begin(vk::CommandBufferBeginInfo{.flags=vk::CommandBufferUsageFlagBits::eOneTimeSubmit}));
    recorder->Bind(fake,real);
}
void Scheduler::WaitSubmitted(u64 tick,bool kick) {
    if(!recorder || recorded_submit_tick.load(std::memory_order_acquire)>=tick)return;
    if(kick) recorder->Kick();
    auto done=recorded_submit_tick.load(std::memory_order_acquire);
    while(done<tick) {
        recorded_submit_tick.wait(done,std::memory_order_acquire);
        done=recorded_submit_tick.load(std::memory_order_acquire);
    }
}

void Scheduler::BeginRendering(""")
    edit(c,"    const vk::CommandBufferBeginInfo begin_info = {\n        .flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit,\n    };\n    upload_cmdbuf = command_pool.Commit();","""    if(recorder) {
        upload_cmdbuf=recorder->NewFakeHandle();
        recorder->Run([this,fake=upload_cmdbuf]{BeginRecorded(fake);});
        return upload_cmdbuf;
    }
    const vk::CommandBufferBeginInfo begin_info = {
        .flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit,
    };
    upload_cmdbuf = command_pool.Commit();""")
    edit(c,"    work_semaphore.Wait(tick);","    WaitSubmitted(tick);\n    work_semaphore.Wait(tick);")
    edit(c,"    const vk::CommandBufferBeginInfo begin_info = {\n        .flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit,\n    };\n    session.primary = command_pool.Commit();\n    Check(session.primary.begin(begin_info));","""    if(recorder) {
        session.primary=recorder->NewFakeHandle();
        recorder->Run([this,fake=session.primary]{BeginRecorded(fake);});
    } else {
        const vk::CommandBufferBeginInfo begin_info = {
            .flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit,
        };
        session.primary=command_pool.Commit();
        Check(session.primary.begin(begin_info));
    }""")
    edit(c,"void Scheduler::SubmitExecution(SubmitInfo& info) {\n    std::scoped_lock lk{submit_mutex};","void Scheduler::SubmitExecution(SubmitInfo& info) {")
    s=c.read_text()
    start=s.index("    // A ready image can be sampled")
    end=s.index("    ASSERT_MSG(submit_result != vk::Result::eErrorDeviceLost, \"Device lost during submit\");",start)+len("    ASSERT_MSG(submit_result != vk::Result::eErrorDeviceLost, \"Device lost during submit\");")
    body=s[start:end].replace("    ImGui::Core::TextureManager::Submit();","    std::scoped_lock lk{Scheduler::submit_mutex};\n    ImGui::Core::TextureManager::Submit();").replace("ASSERT_MSG(submit_result != vk::Result::eErrorDeviceLost, \"Device lost during submit\");","ASSERT_MSG(submit_result == vk::Result::eSuccess, \"Queue submit failed: {}\", vk::to_string(submit_result));")
    s=s[:start]+"""    if(recorder) {
        recorder->Run([this,info,fakes=std::move(cmd_buffers),signal_value]{
            std::vector<vk::CommandBuffer> real;
            real.reserve(fakes.size());
            for(const auto fake:fakes) real.emplace_back(recorder->Real(fake));
            QueueSubmit(instance,info,real);
            recorded_submit_tick.store(signal_value,std::memory_order_release);
            recorded_submit_tick.notify_all();
            recorder->Retire(static_cast<u32>(fakes.size()));
        });
        recorder->Kick();
    } else {
        QueueSubmit(instance,info,cmd_buffers);
    }"""+s[end:]
    s=s.replace("void Scheduler::SubmitExecution(SubmitInfo& info) {","static void QueueSubmit(const Instance& instance,const SubmitInfo& info,std::span<const vk::CommandBuffer> cmd_buffers) {\n"+body+"\n}\n\nvoid Scheduler::SubmitExecution(SubmitInfo& info) {",1)
    c.write_text(s)
    # The queue cannot accept sparse binds or a cross-scheduler timeline wait
    # ahead of the already recorded signal. Wait for submission, not GPU completion.
    edit(root/"src/video_core/buffer_cache/buffer_cache.cpp","    auto submit_result = instance.GetGraphicsQueue().bindSparse(sparse_info);","""    scheduler.WaitSubmitted(scheduler.CurrentTick()-2);
    std::scoped_lock queue_lock{Vulkan::Scheduler::submit_mutex};
    auto submit_result = instance.GetGraphicsQueue().bindSparse(sparse_info);""")
    p=d/"vk_presenter.cpp"
    edit(p,"      draw_scheduler{instance}, present_scheduler{instance}, flip_scheduler{instance},","""      draw_scheduler{instance, [] {
          const auto serial=Common::ElfInfo::Instance().GameSerial();
          const char* opt=std::getenv("BACHATA_GPU_RECORDER");
          return (!opt || opt[0]!='0') && (serial=="CUSA00785" || serial=="CUSA08809" || serial=="CUSA08034");
      }()}, present_scheduler{instance}, flip_scheduler{instance},""")
    edit(p,"    draw_scheduler.Finish();","    draw_scheduler.ClaimRecorder();\n    draw_scheduler.Finish();\n    draw_scheduler.DrainRecorder();")
    edit(p,"    info.AddWait(frame->ready_semaphore, frame->ready_tick);","""    if(frame->ready_semaphore==draw_scheduler.GetWorkSemaphore()->Handle())
        draw_scheduler.WaitSubmitted(frame->ready_tick,false);
    info.AddWait(frame->ready_semaphore, frame->ready_tick);""")
    # Add to the existing GPU target source list, not a new core or library.
    cm=root/"CMakeLists.txt"
    edit(cm,"src/video_core/renderer_vulkan/vk_scheduler.cpp","src/video_core/renderer_vulkan/vk_scheduler.cpp\n              src/video_core/renderer_vulkan/vk_recorder.cpp")
    return {"recorder":"actual donor command stream; deep-copy Vulkan inputs, ARM64 yield, single producer, ordered sparse binds and present waits"}
