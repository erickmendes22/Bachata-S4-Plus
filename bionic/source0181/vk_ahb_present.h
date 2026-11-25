// SPDX-License-Identifier: GPL-2.0-or-later
// Same-process adaptation of GoW3's AHB/SurfaceControl transport (239b7df8145e).
#pragma once
#ifdef __ANDROID__
#include <android/hardware_buffer.h>
#include <android/native_window.h>
#include <android/surface_control.h>
#include <chrono>
#include <memory>
#include <poll.h>
#include <cerrno>
#include <cstdlib>
#include "common/elf_info.h"
#include "video_core/renderer_vulkan/vk_instance.h"
#include "video_core/renderer_vulkan/ahb_release_slots.h"

namespace Vulkan {
class AndroidAhbPresent {
    using Slots=BachataAhb::ReleaseSlots;
    struct Slot {
        AHardwareBuffer* ahb{};
        vk::Image image{};
        vk::DeviceMemory memory{};
        vk::ImageView view{};
        vk::Semaphore acquired{},ready{};
        bool imported{};
        bool presented{};
    };
    struct Callback {
        std::shared_ptr<Slots> releases;
        int previous;
    };
public:
    static constexpr u32 Count=Slots::Count;
    explicit AndroidAhbPresent(const Instance& instance_):instance(instance_){}
    AndroidAhbPresent(const AndroidAhbPresent&)=delete;
    ~AndroidAhbPresent() {
        releases->Retire();
        if(control) {
            if(auto* t=ASurfaceTransaction_create()) {
                ASurfaceTransaction_setVisibility(t,control,ASURFACE_TRANSACTION_VISIBILITY_HIDE);
                ASurfaceTransaction_setBuffer(t,control,nullptr,-1);
                ASurfaceTransaction_apply(t);
                ASurfaceTransaction_delete(t);
            }
            ASurfaceControl_release(control);
        }
        // Swapchain::Destroy has waited for all Vulkan uses. SurfaceFlinger
        // retains its own AHB references until scanout has finished.
        auto dev=instance.GetDevice();
        for(auto& s:slots) {
            if(s.acquired)dev.destroySemaphore(s.acquired);
            if(s.ready)dev.destroySemaphore(s.ready);
            if(s.view)dev.destroyImageView(s.view);
            if(s.image)dev.destroyImage(s.image);
            if(s.memory)dev.freeMemory(s.memory);
            if(s.ahb)AHardwareBuffer_release(s.ahb);
        }
    }
    bool Create(ANativeWindow* window,u32 w,u32 h) {
        if(!window||!w||!h||!instance.SupportsAndroidAhbPresent())return false;
        width=w;height=h;
        control=ASurfaceControl_createFromWindow(window,"BachataGame");
        if(!control)return false;
        for(auto& s:slots)if(!CreateSlot(s))return false;
        return true;
    }
    bool Acquire(u32& index) {
        auto next=releases->Take(std::chrono::milliseconds(2000));
        if(!next)return false;
        index=next->index;
        auto& slot=slots[index];
        slot.imported=false;
        if(next->fence<0)return true;
        const vk::ImportSemaphoreFdInfoKHR import{
            .semaphore=slot.acquired,.flags=vk::SemaphoreImportFlagBits::eTemporary,
            .handleType=vk::ExternalSemaphoreHandleTypeFlagBits::eSyncFd,.fd=next->fence};
        if(instance.GetDevice().importSemaphoreFdKHR(import)==vk::Result::eSuccess){
            slot.imported=true;return true; // Vulkan owns fd
        }
        // Failed imports retain fd ownership. A bounded CPU wait is safe.
        pollfd p{next->fence,POLLIN,0};
        int result;
        do {result=poll(&p,1,2000);} while(result<0&&errno==EINTR);
        close(next->fence);
        return result>0&&(p.revents&POLLIN);
    }
    bool Present(u32 index) {
        auto [result,fd]=instance.GetDevice().getSemaphoreFdKHR({
            .semaphore=slots[index].ready,
            .handleType=vk::ExternalSemaphoreHandleTypeFlagBits::eSyncFd});
        if(result!=vk::Result::eSuccess)return false;
        auto* txn=ASurfaceTransaction_create();
        if(!txn){if(fd>=0)close(fd);return false;}
        auto ctx=std::make_unique<Callback>(Callback{releases,last});
        ASurfaceTransaction_setBuffer(txn,control,slots[index].ahb,fd); // owns fd
        const ARect rect{0,0,static_cast<int32_t>(width),static_cast<int32_t>(height)};
        // NDK's C++ API takes const ARect& (not pointers).
        ASurfaceTransaction_setGeometry(txn,control,rect,rect,0);
        ASurfaceTransaction_setBufferTransparency(txn,control,ASURFACE_TRANSACTION_TRANSPARENCY_OPAQUE);
        ASurfaceTransaction_setVisibility(txn,control,ASURFACE_TRANSACTION_VISIBILITY_SHOW);
        ASurfaceTransaction_setOnComplete(txn,ctx.release(),Complete);
        slots[index].presented=true;
        last=static_cast<int>(index);
        ASurfaceTransaction_apply(txn);
        ASurfaceTransaction_delete(txn);
        return true;
    }
    vk::ImageLayout AcquireLayout(u32 i)const{return slots[i].presented?vk::ImageLayout::eGeneral:vk::ImageLayout::eUndefined;}
    vk::Image Image(u32 i)const{return slots[i].image;}
    vk::ImageView View(u32 i)const{return slots[i].view;}
    vk::Semaphore Acquired(u32 i)const{return slots[i].imported?slots[i].acquired:vk::Semaphore{};}
    vk::Semaphore Ready(u32 i)const{return slots[i].ready;}
private:
    static void Complete(void* opaque,ASurfaceTransactionStats* stats) {
        std::unique_ptr<Callback> ctx(static_cast<Callback*>(opaque));
        if(ctx->previous<0)return;
        ASurfaceControl** controls=nullptr;
        size_t count=0;
        ASurfaceTransactionStats_getASurfaceControls(stats,&controls,&count);
        if(count==1) {
            const int fd=ASurfaceTransactionStats_getPreviousReleaseFenceFd(stats,controls[0]);
            ctx->releases->Returned(static_cast<unsigned>(ctx->previous),fd);
        } else {
            // Never reuse a buffer if its release identity is unknown.
            ctx->releases->Retire();
        }
        if(controls)ASurfaceTransactionStats_releaseASurfaceControls(controls);
    }
    bool CreateSlot(Slot& s) {
        const AHardwareBuffer_Desc desc{
            .width=width,.height=height,.layers=1,
            .format=AHARDWAREBUFFER_FORMAT_R8G8B8A8_UNORM,
            .usage=AHARDWAREBUFFER_USAGE_GPU_COLOR_OUTPUT |
                   AHARDWAREBUFFER_USAGE_GPU_SAMPLED_IMAGE |
                   AHARDWAREBUFFER_USAGE_COMPOSER_OVERLAY,
            .stride=0,.rfu0=0,.rfu1=0};
        if(AHardwareBuffer_allocate(&desc,&s.ahb)!=0||!s.ahb)return false;
        auto dev=instance.GetDevice();
        auto [pr,chain]=dev.getAndroidHardwareBufferPropertiesANDROID<
            vk::AndroidHardwareBufferPropertiesANDROID,vk::AndroidHardwareBufferFormatPropertiesANDROID>(*s.ahb);
        if(pr!=vk::Result::eSuccess)return false;
        auto& prop=chain.get<vk::AndroidHardwareBufferPropertiesANDROID>();
        auto& fmt=chain.get<vk::AndroidHardwareBufferFormatPropertiesANDROID>();
        const auto required=vk::FormatFeatureFlagBits::eColorAttachment|
            vk::FormatFeatureFlagBits::eTransferSrc|vk::FormatFeatureFlagBits::eTransferDst|
            vk::FormatFeatureFlagBits::eBlitDst;
        if(fmt.format!=vk::Format::eR8G8B8A8Unorm||(fmt.formatFeatures&required)!=required)return false;
        const vk::ExternalMemoryImageCreateInfo ext{
            .handleTypes=vk::ExternalMemoryHandleTypeFlagBits::eAndroidHardwareBufferANDROID};
        auto [ir,image]=dev.createImage({
            .pNext=&ext,.imageType=vk::ImageType::e2D,.format=fmt.format,
            .extent={width,height,1},.mipLevels=1,.arrayLayers=1,
            .samples=vk::SampleCountFlagBits::e1,.tiling=vk::ImageTiling::eOptimal,
            .usage=vk::ImageUsageFlagBits::eColorAttachment|vk::ImageUsageFlagBits::eTransferSrc|
                   vk::ImageUsageFlagBits::eTransferDst,
            .sharingMode=vk::SharingMode::eExclusive,.initialLayout=vk::ImageLayout::eUndefined});
        if(ir!=vk::Result::eSuccess)return false;
        s.image=image;
        auto mem=instance.GetPhysicalDevice().getMemoryProperties();
        u32 type=~0u;
        for(u32 i=0;i<mem.memoryTypeCount;++i)if(prop.memoryTypeBits&(1u<<i)){
            if(type==~0u)type=i;
            if(mem.memoryTypes[i].propertyFlags&vk::MemoryPropertyFlagBits::eDeviceLocal){type=i;break;}
        }
        if(type==~0u)return false;
        const vk::MemoryDedicatedAllocateInfo dedicated{.image=s.image};
        const vk::ImportAndroidHardwareBufferInfoANDROID imp{.pNext=&dedicated,.buffer=s.ahb};
        auto [mr,allocation]=dev.allocateMemory({
            .pNext=&imp,.allocationSize=prop.allocationSize,.memoryTypeIndex=type});
        if(mr!=vk::Result::eSuccess)return false;
        s.memory=allocation;
        if(dev.bindImageMemory(s.image,s.memory,0)!=vk::Result::eSuccess)return false;
        auto [vr,view]=dev.createImageView({
            .image=s.image,.viewType=vk::ImageViewType::e2D,.format=fmt.format,
            .subresourceRange={.aspectMask=vk::ImageAspectFlagBits::eColor,.levelCount=1,.layerCount=1}});
        if(vr!=vk::Result::eSuccess)return false;
        s.view=view;
        auto [ar,acquired]=dev.createSemaphore({});
        if(ar!=vk::Result::eSuccess)return false;
        s.acquired=acquired;
        const vk::ExportSemaphoreCreateInfo exp{.handleTypes=vk::ExternalSemaphoreHandleTypeFlagBits::eSyncFd};
        auto [rr,ready]=dev.createSemaphore({.pNext=&exp});
        if(rr!=vk::Result::eSuccess)return false;
        s.ready=ready;
        return true;
    }
    const Instance& instance;
    std::shared_ptr<Slots> releases=std::make_shared<Slots>();
    std::array<Slot,Count> slots{};
    ASurfaceControl* control{};
    u32 width{},height{};
    int last=-1;
};
}
#endif
