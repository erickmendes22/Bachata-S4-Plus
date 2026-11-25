"""Recover real Android presentation and the FEX call-ret guard protocol.
Reference logs 48FCDEC7,487A12C8; pinned FEX f2b679f6.
No CPU replacement, no changes to graphics patches or application frontend.
"""
from pathlib import Path
import shutil

def apply(root:Path):
    v=root/"src/video_core/renderer_vulkan"
    def edit(p,a,b,n=1):
        s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"Android WSI/FEX contract {p.name}: {a[:120]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    sw=v/"vk_swapchain.cpp";sh=v/"vk_swapchain.h";pr=v/"vk_presenter.cpp"
    edit(sh,"    bool AcquireNextImage();","    bool AcquireNextImage();\n    void SetAcquireRetire(vk::Semaphore timeline,u64 tick);")
    edit(sh,"    std::vector<vk::Semaphore> present_ready;",
         """    std::vector<vk::Semaphore> present_ready;
    std::vector<u64> acquire_retire_ticks;
    vk::Semaphore acquire_retire_timeline{};
    bool surface_lost{};""")
    edit(sw,"    Destroy();\n\n    SetSurfaceProperties();",
         """    Destroy();
    if(surface_lost) {
        instance.GetInstance().destroySurfaceKHR(surface);
        surface=CreateSurface(instance.GetInstance(),window);
        surface_lost=false;
        FindPresentFormat();
        FindPresentMode();
    }
    image_index=0;
    frame_index=0;

    SetSurfaceProperties();""")
    edit(sw,"    RefreshSemaphores();\n    LOG_INFO(Render_Vulkan,\"BACHATA_PRESENT_WSI_READY",
         "    RefreshSemaphores();\n    acquire_retire_ticks.assign(image_count,0);\n    acquire_retire_timeline=vk::Semaphore{};\n    LOG_INFO(Render_Vulkan,\"BACHATA_PRESENT_WSI_READY")
    edit(sw,"    Create(width_, height_);\n}",
         "    std::scoped_lock lock{Scheduler::submit_mutex};\n    Create(width_, height_);\n}")
    s=sw.read_text()
    if '#include "video_core/renderer_vulkan/vk_scheduler.h"' not in s:
        sw.write_text('#include "video_core/renderer_vulkan/vk_scheduler.h"\n'+s)
    edit(sw,"""    auto result = instance.GetDevice().waitIdle();
    if (result != vk::Result::eSuccess) {
        LOG_WARNING(ImGui, "Failed to wait for Vulkan device idle on mode change: {}",
                    vk::to_string(result));
    }

    needs_hdr = hdr;""","""    // Recreate owns the submission lock and waits for all outstanding work.
    needs_hdr = hdr;""")
    edit(sw,"bool Swapchain::AcquireNextImage() {",
         """void Swapchain::SetAcquireRetire(vk::Semaphore timeline,u64 tick) {
#ifdef __ANDROID__
    if(ahb) return;
#endif
    ASSERT(frame_index<acquire_retire_ticks.size());
    ASSERT(!acquire_retire_timeline || acquire_retire_timeline==timeline);
    acquire_retire_timeline=timeline;
    acquire_retire_ticks[frame_index]=tick;
}
bool Swapchain::AcquireNextImage() {""")
    edit(sw,"    vk::Device device = instance.GetDevice();\n    vk::Result result =\n        device.acquireNextImageKHR",
         """    vk::Device device = instance.GetDevice();
    // A binary acquire semaphore cannot be reused until its preceding
    // queue wait completes, even if the next image is already available.
    ASSERT(frame_index<acquire_retire_ticks.size());
    const auto tick=acquire_retire_ticks[frame_index];
    if(tick) {
        const auto [status,completed]=device.getSemaphoreCounterValue(acquire_retire_timeline);
        ASSERT_MSG(status==vk::Result::eSuccess,"Acquire retirement query failed: {}",vk::to_string(status));
        if(completed<tick) {
            const vk::SemaphoreWaitInfo wait{.semaphoreCount=1,.pSemaphores=&acquire_retire_timeline,.pValues=&tick};
            const auto result=device.waitSemaphores(wait,~u64{0});
            ASSERT_MSG(result==vk::Result::eSuccess,"Acquire retirement wait failed: {}",vk::to_string(result));
        }
        acquire_retire_ticks[frame_index]=0;
    }
    vk::Result result =
        device.acquireNextImageKHR""")
    edit(sw,"""    case vk::Result::eSuccess:
        break;
    case vk::Result::eSuboptimalKHR:
    case vk::Result::eErrorSurfaceLostKHR:
    case vk::Result::eErrorOutOfDateKHR:
    case vk::Result::eErrorUnknown:
        needs_recreation = true;
        break;""",
         """    case vk::Result::eSuccess:
        needs_recreation=false;
        break;
    case vk::Result::eSuboptimalKHR: {
        // Vulkan returns a VALID acquired image and signals the semaphore.
        // Android can remain suboptimal indefinitely at a fixed extent.
        // Consume the image normally; actual window changes and OUT_OF_DATE
        // still recreate. Never abandon a successful acquire.
        static bool reported=false;
        if(!reported) {
            reported=true;
            LOG_INFO(Render_Vulkan,"BACHATA_WSI_SUBOPTIMAL_ACQUIRE accepted");
        }
        needs_recreation=false;
        break;
    }
    case vk::Result::eErrorSurfaceLostKHR:
        surface_lost=true;
        [[fallthrough]];
    case vk::Result::eErrorOutOfDateKHR:
    case vk::Result::eErrorUnknown:
        needs_recreation=true;
        break;""")
    edit(sw,"""    if (result == vk::Result::eErrorOutOfDateKHR || result == vk::Result::eSuboptimalKHR) {
        needs_recreation = true;
    } else {
        ASSERT_MSG(result == vk::Result::eSuccess, "Swapchain presentation failed: {}",
                   vk::to_string(result));
    }""",
         """    if (result == vk::Result::eErrorOutOfDateKHR || result == vk::Result::eErrorSurfaceLostKHR) {
        surface_lost=result==vk::Result::eErrorSurfaceLostKHR;
        needs_recreation=true;
    } else {
        ASSERT_MSG(result==vk::Result::eSuccess || result==vk::Result::eSuboptimalKHR,
                   "Swapchain presentation failed: {}",vk::to_string(result));
        needs_recreation=false;
        if(result==vk::Result::eSuboptimalKHR) {
            static bool reported=false;
            if(!reported) {
                reported=true;
                LOG_INFO(Render_Vulkan,"BACHATA_WSI_SUBOPTIMAL_PRESENT accepted");
            }
        }
    }""")
    edit(pr,"""    info.AddSignal(frame->present_done);
    scheduler.Flush(info);

    // Report new guest frames only after a successful presentation.
    bool presented=false;
    {
        std::scoped_lock submit_lock{Scheduler::submit_mutex};
        presented=swapchain.Present();
        if (!presented) {
            swapchain.Recreate(window.GetWidth(), window.GetHeight());
        }
    }

    free_frame(true);
#ifdef ENABLE_BACHATA_RUNTIME
    if(presented&&!is_reusing_frame&&is_game_frame) Platform::Bachata::ReportPresentedFrame();
#endif""",
         """    info.AddSignal(frame->present_done);
    const auto present_tick=scheduler.CurrentTick();
    scheduler.Flush(info);
    swapchain.SetAcquireRetire(scheduler.GetWorkSemaphore()->Handle(),present_tick);

    bool presented=false;
    {
        std::scoped_lock submit_lock{Scheduler::submit_mutex};
        presented=swapchain.Present();
    }
    // Recreate owns the queue submission lock, never take it recursively.
    if(!presented) swapchain.Recreate(window.GetWidth(),window.GetHeight());
    if(presented && !is_reusing_frame && is_game_frame) {
        static bool first=false;
        if(!first) {first=true;LOG_INFO(Render_Vulkan,"BACHATA_FIRST_GAME_PRESENT_OK");}
    }
    free_frame(true);""")
    driver=root/"src/core/libraries/videoout/driver.cpp"
    edit(driver,"    presenter->Present(req.frame);\n\n    // Update flip status.",
         """    presenter->Present(req.frame);
#ifdef ENABLE_BACHATA_RUNTIME
    // Restore the original Bachata frontend frame protocol at the guest flip
    // completion boundary. Idle/menu redraws never increment it.
    Platform::Bachata::ReportPresentedFrame();
#endif

    // Update flip status.""")
    # Restore missing FEX frontend signal recovery, strictly for JIT code
    # performing the exact call-ret stack instruction on its own guard page.
    fex=root/"src/core/fex/fex_guest_engine.cpp"
    shutil.copyfile(Path(__file__).with_name("fex_callret_guard.h"),fex.with_name("fex_callret_guard.h"))
    edit(fex,'#include "fex_guest_engine.h"','#include "fex_guest_engine.h"\n#include "fex_callret_guard.h"')
    edit(fex,"""  if (signal != SIGBUS || info == nullptr || rawContext == nullptr ||
      ActiveFexExecution.Context == nullptr || ActiveFexExecution.Thread == nullptr ||
      ActiveFexExecution.SignalDelegator == nullptr) {
    return false;
  }""",
         """  if ((signal!=SIGBUS && signal!=SIGSEGV) || info==nullptr || rawContext==nullptr ||
      ActiveFexExecution.Context==nullptr || ActiveFexExecution.Thread==nullptr ||
      ActiveFexExecution.SignalDelegator==nullptr) {
    return false;
  }""")
    edit(fex,"""  auto* registers = reinterpret_cast<std::uint64_t*>(context->uc_mcontext.regs);
  if (info->si_code != BUS_ADRALN) return false;""",
         """  auto* registers = reinterpret_cast<std::uint64_t*>(context->uc_mcontext.regs);
  if(signal==SIGSEGV) {
    if(info->si_code!=SEGV_ACCERR || (pc&3)) return false;
    auto* thread=ActiveFexExecution.Thread;
    constexpr std::uint64_t size=FEXCore::Core::InternalThreadState::CALLRET_STACK_SIZE;
    const auto base=reinterpret_cast<std::uint64_t>(thread->CallRetStackBase);
    const auto fault=reinterpret_cast<std::uint64_t>(info->si_addr);
    constexpr unsigned callret_reg=25; // pinned FEX non-ARM64EC ABI
    const auto insn=*reinterpret_cast<const volatile std::uint32_t*>(pc);
    if(!BachataFex::IsCallRetGuardAccess(base,size,kRequiredPageSize,fault,
                                         registers[callret_reg],insn)) return false;
    const auto reset=base+size/4;
    // The branch target cache is optional. An empty entry forces a safe
    // normal guest RIP lookup on the next return, not a stale native jump.
    auto* entry=reinterpret_cast<volatile std::uint64_t*>(reset);
    entry[0]=0;entry[1]=0;
    registers[callret_reg]=reset;
    thread->CurrentFrame->State.callret_sp=reset;
    static thread_local bool logged=false;
    if(!logged) {
      logged=true;
      constexpr char message[]="BACHATA_FEX_CALLRET_GUARD_RECOVERED\\n";
      (void)::write(STDERR_FILENO,message,sizeof(message)-1);
    }
    return true; // retry the same host instruction, now with a valid cache SP
  }
  if (info->si_code != BUS_ADRALN) return false;""")
    sig=root/"src/core/signals.cpp"
    edit(sig,"if (sig == SIGBUS && ::Core::Fex::HandleGuestSignal(sig, info, raw_context))",
         "if (::Core::Fex::HandleGuestSignal(sig, info, raw_context))")
    return {"wsi":"SUBOPTIMAL valid; surface loss recreated; index and acquire semaphore retirement safe",
            "fps":"original VideoOut Flip completion protocol restored",
            "fex":"strict pinned call-ret stack guard recovery; other faults retain normal handling",
            "ahb":"unchanged opt-in; original UI/SAF/FEX preserved"}
