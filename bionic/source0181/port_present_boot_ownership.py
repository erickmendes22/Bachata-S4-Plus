"""Fix presentation before first flip and ownership of the last submitted frame.
Both 20261125 crashes occurred in Turnip on shadPS4:Present immediately after
VideoOut opened. The retained Presenter leaves last_submit_frame indeterminate,
and requeues that same frame while retaining its pointer for idle redraws.
Restore known WSI default; AHB is explicit opt-in until the full transport is
verified. Keep the existing frame accounting, FEX and all GPU corrections.
"""
from pathlib import Path

def apply(root:Path):
    v=root/"src/video_core/renderer_vulkan"
    def edit(name,a,b,n=1):
        p=v/name;s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"present boot {name}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    edit("vk_presenter.h","    Frame* last_submit_frame;",
         "    Frame* last_submit_frame{}; // no frame before the first completed submission")
    # Retain the last frame outside the free queue. Allocate one extra frame
    # so the number of frames available to the producer is unchanged.
    edit("vk_presenter.cpp","    const u32 num_images = swapchain.GetImageCount();",
         "    const u32 num_images = swapchain.GetImageCount()+1;")
    edit("vk_presenter.cpp","""    const auto free_frame = [&] {
        if (!is_reusing_frame) {
            last_submit_frame = frame;
            std::scoped_lock fl{free_mutex};
            free_queue.push(frame);
            free_cv.notify_one();
        }
    };""",
         """    const auto free_frame = [&](bool submitted) {
        if (is_reusing_frame) return;
        std::scoped_lock fl{free_mutex};
        if (submitted) {
            // Only the presentation thread reads/writes last_submit_frame.
            // The producer can reuse the old frame, never the retained one.
            if (last_submit_frame) free_queue.push(last_submit_frame);
            last_submit_frame=frame;
        } else {
            free_queue.push(frame);
        }
        free_cv.notify_one();
    };""")
    edit("vk_presenter.cpp","""            free_frame();
            return;""",
         """            if (!is_reusing_frame) {
                // No presentation fence was reset/submitted. Complete the
                // producing GPU work before returning this frame to the pool.
                if (frame->ready_semaphore==draw_scheduler.GetWorkSemaphore()->Handle())
                    draw_scheduler.WaitSubmitted(frame->ready_tick,false);
                const vk::SemaphoreWaitInfo wait{
                    .semaphoreCount=1,.pSemaphores=&frame->ready_semaphore,
                    .pValues=&frame->ready_tick};
                const auto result=instance.GetDevice().waitSemaphores(wait,~u64{0});
                ASSERT_MSG(result==vk::Result::eSuccess,"Skipped frame ready wait failed: {}",vk::to_string(result));
            }
            free_frame(false);
            return;""")
    edit("vk_presenter.cpp","    free_frame();\n#ifdef ENABLE_BACHATA_RUNTIME",
         "    free_frame(true);\n#ifdef ENABLE_BACHATA_RUNTIME")
    # The previous blank-frame guard exposed uninitialized last_submit_frame.
    # Keep the guard, and ensure repeated idle calls before first flip are safe.
    # AHB transport was not integrated as a full donor protocol: keep it opt-in.
    edit("vk_swapchain.cpp","return (!opt||opt[0]!='0')&&(serial==\"CUSA00785\"||serial==\"CUSA08809\"||serial==\"CUSA08034\");",
         "return (opt && opt[0]=='1' && opt[1]=='\\0')&&(serial==\"CUSA00785\"||serial==\"CUSA08809\"||serial==\"CUSA08034\");")
    edit("vk_swapchain.cpp","    SetupImages();\n    RefreshSemaphores();",
         """    SetupImages();
    RefreshSemaphores();
    LOG_INFO(Render_Vulkan,"BACHATA_PRESENT_WSI_READY {}x{} images={}",extent.width,extent.height,image_count);""")
    # Check actual signal handles/counts rather than passing invalid pointers
    # to the driver. No successful frame is skipped.
    edit("vk_scheduler.h","    void AddWait(vk::Semaphore semaphore, u64 tick = 1) {",
         """    void AddWait(vk::Semaphore semaphore, u64 tick = 1) {
        ASSERT_MSG(semaphore && num_wait_semas<wait_semas.size(),"Invalid queue wait");""")
    edit("vk_scheduler.h","    void AddSignal(vk::Semaphore semaphore, u64 tick = 1) {",
         """    void AddSignal(vk::Semaphore semaphore, u64 tick = 1) {
        ASSERT_MSG(semaphore && num_signal_semas<signal_semas.size(),"Invalid queue signal");""")
    p=v/"vk_scheduler.h";s=p.read_text()
    if '#include "common/assert.h"' not in s:
        p.write_text('#include "common/assert.h"\n'+s)
    return {"first_flip":"initialize pointer; retain one separate frame",
            "skipped_frame":"wait producer before recycling; do not publish as last",
            "presentation":"known WSI default; AHB explicit opt-in",
            "fps":"existing successful new-game-frame accounting unchanged",
            "submit":"validate semaphore handles and counts before writing arrays"}
