#!/usr/bin/env python3
"""Complete the same-process AHB commit/release protocol without replacing WSI.

Applies after the existing presentation ownership and target extent overlays.
Only the AHB adapter and its swapchain policy change; the presenter keeps its
existing worker, Vulkan submission and frame accounting.
"""
from pathlib import Path


STATE = r'''    // BACHATA_AHB_PRESENT_PROTOCOL: callbacks own only shared session state.
    // They never wait for a fence, submit work or apply another transaction.
    using Clock = std::chrono::steady_clock;
    struct State {
        Slots releases;
        std::mutex mutex;
        std::condition_variable cv;
        u64 sequence{}, pending{};
        bool retired{};
        const char* reason{};

        bool WaitForCommit(Clock::time_point deadline) {
            std::unique_lock lock{mutex};
            return cv.wait_until(lock, deadline, [&] { return retired || pending == 0; }) &&
                   !retired;
        }
        u64 Begin(bool fifo) {
            std::scoped_lock lock{mutex};
            if (retired || (fifo && pending)) return 0;
            const u64 value = ++sequence;
            if (fifo) pending = value;
            return value;
        }
        void Committed(u64 value) {
            std::scoped_lock lock{mutex};
            if (!retired && pending == value) {
                pending = 0;
                cv.notify_all();
            }
        }
        void Retire(const char* why) {
            {
                std::scoped_lock lock{mutex};
                if (!reason) reason = why;
                retired = true;
                cv.notify_all();
            }
            releases.Retire();
        }
        const char* FailureReason() {
            std::scoped_lock lock{mutex};
            return reason ? reason : "unspecified";
        }
    };
    struct Callback {
        std::shared_ptr<State> state;
        int previous;
    };
    struct CommitCallback {
        std::shared_ptr<State> state;
        u64 sequence;
    };'''

CREATE = r'''    bool Create(ANativeWindow* window,u32 w,u32 h,u32 output_w,u32 output_h,
                bool fifo_mode) {
        if (!window || !w || !h || !output_w || !output_h ||
            w > INT32_MAX || h > INT32_MAX || output_w > INT32_MAX || output_h > INT32_MAX)
            return Fail("extent_or_window");
        if (!instance.SupportsAndroidAhbPresent()) return Fail("capabilities");
        width=w;height=h;destination_width=output_w;destination_height=output_h;
        fifo=fifo_mode;
        control=ASurfaceControl_createFromWindow(window,"BachataGame");
        if(!control)return Fail("surface_control");
        for(auto& s:slots)if(!CreateSlot(s))return false;
        return true;
    }'''

ACQUIRE = r'''    bool Acquire(u32& index,std::chrono::milliseconds timeout=std::chrono::milliseconds(2000)) {
        // The existing presentation worker calls this before taking submit_mutex.
        // FIFO advances on commit, never on the later complete/present fence.
        const auto deadline = Clock::now() + timeout;
        if (!state->WaitForCommit(deadline)) return Fail("commit_timeout");
        auto next=state->releases.Take(std::chrono::milliseconds(RemainingMs(deadline)));
        if(!next)return Fail("release_timeout");
        index=next->index;
        auto& slot=slots[index];
        slot.imported=false;
        if(next->fence<0)return true; // NDK: the previous buffer is already released.
        const vk::ImportSemaphoreFdInfoKHR import{
            .semaphore=slot.acquired,.flags=vk::SemaphoreImportFlagBits::eTemporary,
            .handleType=vk::ExternalSemaphoreHandleTypeFlagBits::eSyncFd,.fd=next->fence};
        if(instance.GetDevice().importSemaphoreFdKHR(import)==vk::Result::eSuccess){
            slot.imported=true;return true; // Vulkan owns fd only after success.
        }
        // Import failure leaves the FD with us. CPU fallback shares the same
        // bounded deadline, including interruptions; callbacks never enter here.
        pollfd p{next->fence,POLLIN,0};
        int result;
        for (;;) {
            result=poll(&p,1,RemainingMs(deadline));
            if(result>=0||errno!=EINTR||Clock::now()>=deadline)break;
        }
        close(next->fence);
        if(result>0&&(p.revents&POLLIN)&&!(p.revents&(POLLERR|POLLNVAL)))return true;
        return Fail("release_fence_wait");
    }'''

PRESENT = r'''    bool Present(u32 index) {
        if(index>=Count)return Fail("buffer_index");
        auto [result,fd]=instance.GetDevice().getSemaphoreFdKHR({
            .semaphore=slots[index].ready,
            .handleType=vk::ExternalSemaphoreHandleTypeFlagBits::eSyncFd});
        if(result!=vk::Result::eSuccess)return Fail("export_sync_fd");
        auto* txn=ASurfaceTransaction_create();
        if(!txn){if(fd>=0)close(fd);return Fail("transaction_create");}
        auto complete=std::unique_ptr<Callback>(new(std::nothrow) Callback{state,last});
        auto commit=fifo ? std::unique_ptr<CommitCallback>(
                               new(std::nothrow) CommitCallback{state,0}) : nullptr;
        if(!complete||(fifo&&!commit)) {
            if(fd>=0)close(fd);
            ASurfaceTransaction_delete(txn);
            return Fail("callback_allocation");
        }
        const u64 sequence=state->Begin(fifo);
        if(!sequence) {
            if(fd>=0)close(fd);
            ASurfaceTransaction_delete(txn);
            return Fail("commit_not_ready");
        }
        if(commit)commit->sequence=sequence;
        ASurfaceTransaction_setBuffer(txn,control,slots[index].ahb,fd); // takes fd
        const ARect rect{0,0,static_cast<int32_t>(width),static_cast<int32_t>(height)};
        const ARect dst=FitDestination(width,height,destination_width,destination_height);
        ASurfaceTransaction_setGeometry(txn,control,rect,dst,0);
        ASurfaceTransaction_setBufferTransparency(txn,control,ASURFACE_TRANSACTION_TRANSPARENCY_OPAQUE);
        ASurfaceTransaction_setVisibility(txn,control,ASURFACE_TRANSACTION_VISIBILITY_SHOW);
        ASurfaceTransaction_setOnComplete(txn,complete.release(),Complete);
        if(commit)ASurfaceTransaction_setOnCommit(txn,commit.release(),Commit);
        slots[index].presented=true;
        last=static_cast<int>(index);
        // State is published before apply: the callback is allowed to run early.
        ASurfaceTransaction_apply(txn);
        ASurfaceTransaction_delete(txn);
        return true;
    }
    const char* FailureReason()const{return state->FailureReason();}'''

CALLBACKS = r'''    static int RemainingMs(Clock::time_point deadline) {
        const auto now=Clock::now();
        if(now>=deadline)return 0;
        const auto remaining=std::chrono::ceil<std::chrono::milliseconds>(deadline-now).count();
        return static_cast<int>(std::min<decltype(remaining)>(remaining,INT32_MAX));
    }
    bool Fail(const char* why) {
        state->Retire(why);
        return false;
    }
    static ARect FitDestination(u32 w,u32 h,u32 output_w,u32 output_h) {
        // Same fit-to-window geometry as the donor's geometry.h. Multiplication
        // uses 64 bits and Create has validated the signed ARect bounds.
        int64_t fitted_w=output_w;
        int64_t fitted_h=int64_t{output_w}*h/w;
        if(fitted_h>output_h) {
            fitted_h=output_h;
            fitted_w=int64_t{output_h}*w/h;
        }
        fitted_w=std::max<int64_t>(fitted_w,1);
        fitted_h=std::max<int64_t>(fitted_h,1);
        const int32_t left=static_cast<int32_t>((output_w-fitted_w)/2);
        const int32_t top=static_cast<int32_t>((output_h-fitted_h)/2);
        return {left,top,left+static_cast<int32_t>(fitted_w),top+static_cast<int32_t>(fitted_h)};
    }
    static void Commit(void* opaque,ASurfaceTransactionStats*) {
        std::unique_ptr<CommitCallback> ctx(static_cast<CommitCallback*>(opaque));
        ctx->state->Committed(ctx->sequence);
    }
    static void Complete(void* opaque,ASurfaceTransactionStats* stats) {
        std::unique_ptr<Callback> ctx(static_cast<Callback*>(opaque));
        if(ctx->previous<0)return;
        ASurfaceControl** controls=nullptr;
        size_t count=0;
        ASurfaceTransactionStats_getASurfaceControls(stats,&controls,&count);
        if(count==1) {
            const int fd=ASurfaceTransactionStats_getPreviousReleaseFenceFd(stats,controls[0]);
            ctx->state->releases.Returned(static_cast<unsigned>(ctx->previous),fd);
        } else {
            // Each transaction here changes exactly one control. Never reuse
            // a buffer when its release identity cannot be determined.
            ctx->state->Retire("release_identity");
        }
        if(controls)ASurfaceTransactionStats_releaseASurfaceControls(controls);
    }'''

POLICY = r'''static const char* BachataAhbPolicyBlockReason(){
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if(serial!="CUSA00785"&&serial!="CUSA08809"&&serial!="CUSA08034")return "title";
    const char* opt=std::getenv("BACHATA_AHB_PRESENT");
    if(!opt)return nullptr;
    if(opt[0]=='0'&&opt[1]=='\0')return "opt_out";
    if(opt[0]=='1'&&opt[1]=='\0')return nullptr;
    return "invalid_override";
}
static bool BachataAhbTarget(){return BachataAhbPolicyBlockReason()==nullptr;}'''

SELECT = r'''    // BACHATA_AHB_SELECTION: policy is distinct from driver capability and
    // per-session transport failures; every WSI fallback has an explicit cause.
    const char* ahb_reason=BachataAhbPolicyBlockReason();
    if(!ahb_reason&&ahb_disabled)ahb_reason="session_disabled";
    if(!ahb_reason&&needs_hdr)ahb_reason="hdr";
    if(!ahb_reason&&surface_format.format!=vk::Format::eR8G8B8A8Unorm)ahb_reason="format";
    if(!ahb_reason&&surface_format.colorSpace!=vk::ColorSpaceKHR::eSrgbNonlinear)ahb_reason="colorspace";
    if(!ahb_reason&&transform!=vk::SurfaceTransformFlagBitsKHR::eIdentity)ahb_reason="transform";
    if(!ahb_reason&&!instance.SupportsAndroidAhbPresent())ahb_reason="capabilities";
    LOG_INFO(Render_Vulkan,
        "BACHATA_AHB_SELECTION decision={} reason={} present_mode={} window={}x{}",
        ahb_reason?"wsi":"attempt",ahb_reason?ahb_reason:"eligible",
        vk::to_string(present_mode),extent.width,extent.height);
    if(!ahb_reason) {'''


def block(text, marker):
    start=text.index(marker)
    opening=text.index("{",start)
    depth=0
    for end in range(opening,len(text)):
        depth+=(text[end]=="{")-(text[end]=="}")
        if not depth:return text[start:end+1]
    raise RuntimeError("AHB protocol unmatched method: "+marker)


def apply(root):
    root=Path(root)/"src/video_core/renderer_vulkan"
    hp=root/"vk_ahb_present.h"
    sp=root/"vk_swapchain.cpp"
    h,s=hp.read_text(),sp.read_text()
    if "BACHATA_AHB_PRESENT_PROTOCOL" in h:
        if "BACHATA_AHB_SELECTION" not in s:raise RuntimeError("Partial AHB protocol overlay")
        return {"ahbPresentProtocol":"already applied"}
    def once(text,old,new,label):
        if text.count(old)!=1:raise RuntimeError(f"AHB protocol source drift {label}: {text.count(old)}")
        return text.replace(old,new,1)
    h=once(h,"#include <memory>","#include <memory>\n#include <algorithm>\n#include <condition_variable>\n#include <mutex>\n#include <new>","includes")
    h=once(h,block(h,"    struct Callback {")+";",STATE,"callback session state")
    h=once(h,"        releases->Retire();","        state->Retire(\"destroyed\");","retire shared session")
    for marker,replacement in (("    bool Create(",CREATE),("    bool Acquire(",ACQUIRE),
                               ("    bool Present(",PRESENT),("    static void Complete(",CALLBACKS)):
        h=once(h,block(h,marker),replacement,marker)
    h=once(h,"    std::shared_ptr<Slots> releases=std::make_shared<Slots>();",
           "    std::shared_ptr<State> state=std::make_shared<State>();\n    bool fifo{};","session member")
    failures={
        "if(AHardwareBuffer_allocate(&desc,&s.ahb)!=0||!s.ahb)return false;":"if(AHardwareBuffer_allocate(&desc,&s.ahb)!=0||!s.ahb)return Fail(\"hardware_buffer\");",
        "if(pr!=vk::Result::eSuccess)return false;":"if(pr!=vk::Result::eSuccess)return Fail(\"ahb_properties\");",
        "if(fmt.format!=vk::Format::eR8G8B8A8Unorm||(fmt.formatFeatures&required)!=required)return false;":"if(fmt.format!=vk::Format::eR8G8B8A8Unorm||(fmt.formatFeatures&required)!=required)return Fail(\"ahb_format_features\");",
        "if(ir!=vk::Result::eSuccess)return false;":"if(ir!=vk::Result::eSuccess)return Fail(\"image_create\");",
        "if(type==~0u)return false;":"if(type==~0u)return Fail(\"memory_type\");",
        "if(mr!=vk::Result::eSuccess)return false;":"if(mr!=vk::Result::eSuccess)return Fail(\"memory_allocate\");",
        "if(dev.bindImageMemory(s.image,s.memory,0)!=vk::Result::eSuccess)return false;":"if(dev.bindImageMemory(s.image,s.memory,0)!=vk::Result::eSuccess)return Fail(\"image_bind\");",
        "if(vr!=vk::Result::eSuccess)return false;":"if(vr!=vk::Result::eSuccess)return Fail(\"view_create\");",
        "if(ar!=vk::Result::eSuccess)return false;":"if(ar!=vk::Result::eSuccess)return Fail(\"acquire_semaphore\");",
        "if(rr!=vk::Result::eSuccess)return false;":"if(rr!=vk::Result::eSuccess)return Fail(\"ready_semaphore\");",
    }
    for old,new in failures.items():h=once(h,old,new,old)
    s=once(s,block(s,"static bool BachataAhbTarget(){"),POLICY,"target default and opt-out")
    old='''    // Use the same RGBA format and physical extent as WSI, keep HDR on WSI.
    if(!ahb_disabled&&BachataAhbTarget()&&!needs_hdr&&
       surface_format.format==vk::Format::eR8G8B8A8Unorm&&
       surface_format.colorSpace==vk::ColorSpaceKHR::eSrgbNonlinear&&
       transform==vk::SurfaceTransformFlagBitsKHR::eIdentity&&
       instance.SupportsAndroidAhbPresent()) {'''
    s=once(s,old,SELECT,"selection and reasons")
    s=once(s,"if(candidate->Create(native,bw,bh,extent.width,extent.height)){",
           "if(candidate->Create(native,bw,bh,extent.width,extent.height,\n"
           "                             present_mode==vk::PresentModeKHR::eFifo)){","FIFO preference")
    s=once(s,'LOG_WARNING(Render_Vulkan,"AHB initialization rejected; retaining Android WSI");',
           'LOG_WARNING(Render_Vulkan,"BACHATA_AHB_FALLBACK stage=create reason={} wsi=1",candidate->FailureReason());',"create fallback")
    s=once(s,'LOG_WARNING(Render_Vulkan,"AHB release timeout; recreate Android WSI");',
           'LOG_WARNING(Render_Vulkan,"BACHATA_AHB_FALLBACK stage=acquire reason={} wsi=1",ahb->FailureReason());',"acquire fallback")
    s=once(s,'LOG_WARNING(Render_Vulkan,"AHB present failed; recreate Android WSI");',
           'LOG_WARNING(Render_Vulkan,"BACHATA_AHB_FALLBACK stage=present reason={} wsi=1",ahb->FailureReason());',"present fallback")
    for path,text in ((hp,h),(sp,s)):path.write_text(text)
    return {"ahbPresentProtocol":"API31 OnCommit FIFO, independent release fences, centered fit",
            "scope":"CUSA00785/CUSA08809/CUSA08034; opt-out0; existing format/capability guards",
            "fallback":"bounded acquire, explicit reason, existing WSI recreate",
            "ownership":"presentation worker applies; callbacks only state+notify; shared lifetime"}


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    print(apply(parser.parse_args().source))
