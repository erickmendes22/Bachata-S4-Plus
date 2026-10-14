// SPDX-License-Identifier: GPL-2.0-or-later
#include "gpu_frame_probe.h"
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
namespace {
constexpr uint32_t side=8,tiles=9,pixels=side*side*tiles;
constexpr VkDeviceSize stride=pixels*8,total=stride*8;
unsigned reports=0,wsi_reports=0;
void transition(VkCommandBuffer cb,VkImage image,VkImageLayout from,VkImageLayout to,VkImageAspectFlags aspects){
    if(from==to)return;
    VkImageMemoryBarrier2 b{VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2};
    b.image=image;b.oldLayout=from;b.newLayout=to;
    b.srcStageMask=b.dstStageMask=VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT;
    b.srcAccessMask=b.dstAccessMask=VK_ACCESS_2_MEMORY_READ_BIT|VK_ACCESS_2_MEMORY_WRITE_BIT;
    b.srcQueueFamilyIndex=b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
    b.subresourceRange={aspects,0,1,0,1};
    VkDependencyInfo d{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};d.imageMemoryBarrierCount=1;d.pImageMemoryBarriers=&b;
    vkCmdPipelineBarrier2(cb,&d);
}
float half(uint16_t h){
    const unsigned exp=(h>>10)&31,mantissa=h&1023;
    if(exp==31)return mantissa?NAN:((h&0x8000)?-INFINITY:INFINITY);
    const float v=exp?std::ldexp(float(1024+mantissa),int(exp)-25):std::ldexp(float(mantissa),-24);
    return (h&0x8000)?-v:v;
}
struct Summary {unsigned cyan{},white{},red{},invalid{},topCyan{},bottomCyan{};double r{},g{},b{},a{};float min=1e30f,max=-1e30f,maxY{};};
Summary summarize(const unsigned char* data,bool fp16,bool bgra=false){
    Summary s{};
    for(unsigned i=0;i<pixels;i++){
        float c[4]{};
        for(unsigned k=0;k<4;k++){if(fp16){uint16_t h{};std::memcpy(&h,data+i*8+k*2,2);c[k]=half(h);}else c[k]=data[i*4+k]/255.f;}
        if(bgra)std::swap(c[0],c[2]);
        if(!std::isfinite(c[0])||!std::isfinite(c[1])||!std::isfinite(c[2])||!std::isfinite(c[3])){s.invalid++;continue;}
        const bool cyan=c[0]<.13f&&c[1]>.78f&&c[2]>.78f;
        s.red+=c[0]>.94f&&c[1]<.06f&&c[2]<.06f;
        s.cyan+=cyan;s.white+=c[0]>.94f&&c[1]>.94f&&c[2]>.94f;
        if(i<3*side*side)s.topCyan+=cyan;if(i>=6*side*side)s.bottomCyan+=cyan;
        s.r+=c[0];s.g+=c[1];s.b+=c[2];s.a+=c[3];
    }
    s.r/=pixels;s.g/=pixels;s.b/=pixels;s.a/=pixels;return s;
}
}
void bs4_probe_begin(Bs4GpuFrameProbe& p,VkDevice dev,VkPhysicalDevice physical,uint64_t frame,uint64_t camera){
    p.pending=false;p.stages=0;p.compositeImage={};
    // Capture the first 512 real dispatches and then one in sixteen. Reporting
    // is independently bounded, including when an input is persistently cyan.
    if(p.failed||(frame>=512&&frame%16))return;
    if(!p.buffer){
        VkBufferCreateInfo ci{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};ci.size=total;ci.usage=VK_BUFFER_USAGE_TRANSFER_DST_BIT;
        if(vkCreateBuffer(dev,&ci,nullptr,&p.buffer)!=VK_SUCCESS){p.failed=true;return;}
        VkMemoryRequirements req{};vkGetBufferMemoryRequirements(dev,p.buffer,&req);
        VkPhysicalDeviceMemoryProperties props{};vkGetPhysicalDeviceMemoryProperties(physical,&props);
        uint32_t index=UINT32_MAX;
        for(unsigned pass=0;pass<2&&index==UINT32_MAX;pass++)for(uint32_t i=0;i<props.memoryTypeCount;i++){
            const auto flags=props.memoryTypes[i].propertyFlags;
            if((req.memoryTypeBits&(1u<<i))&&(flags&VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT)&&
               (pass||(flags&VK_MEMORY_PROPERTY_HOST_COHERENT_BIT))){index=i;break;}
        }
        if(index==UINT32_MAX){bs4_probe_release(p,dev);p.failed=true;return;}
        p.coherent=props.memoryTypes[index].propertyFlags&VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
        VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=req.size;ai.memoryTypeIndex=index;
        if(vkAllocateMemory(dev,&ai,nullptr,&p.memory)!=VK_SUCCESS||vkBindBufferMemory(dev,p.buffer,p.memory,0)!=VK_SUCCESS||
           vkMapMemory(dev,p.memory,0,VK_WHOLE_SIZE,0,&p.mapped)!=VK_SUCCESS){bs4_probe_release(p,dev);p.failed=true;return;}
    }
    p.frame=frame;p.cameraFrame=camera;p.pending=true;
}
void bs4_probe_image(Bs4GpuFrameProbe& p,VkCommandBuffer cb,VkImage image,VkImageLayout layout,VkExtent2D size,VkFormat format,unsigned stage){
    if(!p.pending||stage>=8||!image||size.width<side||size.height<side)return;
    const bool fp16=format==VK_FORMAT_R16G16B16A16_SFLOAT;
    const bool motion=stage==4&&format==VK_FORMAT_R16G16_SFLOAT;
    const bool bgra=stage==7&&(format==VK_FORMAT_B8G8R8A8_UNORM||format==VK_FORMAT_B8G8R8A8_SRGB);
    const bool wsi_rgba=stage==7&&(format==VK_FORMAT_R8G8B8A8_UNORM||format==VK_FORMAT_R8G8B8A8_SRGB);
    const bool depth=stage==5&&(format==VK_FORMAT_D32_SFLOAT||format==VK_FORMAT_D32_SFLOAT_S8_UINT);
    if(!motion&&!depth&&stage==7&&!bgra&&!wsi_rgba)return;
    if(!motion&&!depth&&stage!=7&&((stage==1)!=fp16||(!fp16&&format!=VK_FORMAT_R8G8B8A8_UNORM)))return;
    const auto aspects=depth?(format==VK_FORMAT_D32_SFLOAT_S8_UINT?VK_IMAGE_ASPECT_DEPTH_BIT|VK_IMAGE_ASPECT_STENCIL_BIT:VK_IMAGE_ASPECT_DEPTH_BIT):VK_IMAGE_ASPECT_COLOR_BIT;
    transition(cb,image,layout,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,aspects);
    std::array<VkBufferImageCopy,tiles> regions{};
    for(unsigned y=0;y<3;y++)for(unsigned x=0;x<3;x++){
        const unsigned n=y*3+x;auto& r=regions[n];r.bufferOffset=stride*stage+n*side*side*(fp16?8:4);
        r.imageSubresource={depth?VK_IMAGE_ASPECT_DEPTH_BIT:VK_IMAGE_ASPECT_COLOR_BIT,0,0,1};
        r.imageOffset={int32_t((size.width-side)*x/2),int32_t((size.height-side)*y/2),0};r.imageExtent={side,side,1};
    }
    vkCmdCopyImageToBuffer(cb,image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,p.buffer,tiles,regions.data());
    transition(cb,image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,layout,aspects);
    VkMemoryBarrier2 b{VK_STRUCTURE_TYPE_MEMORY_BARRIER_2};b.srcStageMask=VK_PIPELINE_STAGE_2_TRANSFER_BIT;
    b.srcAccessMask=VK_ACCESS_2_TRANSFER_WRITE_BIT;b.dstStageMask=VK_PIPELINE_STAGE_2_HOST_BIT;b.dstAccessMask=VK_ACCESS_2_HOST_READ_BIT;
    VkDependencyInfo d{VK_STRUCTURE_TYPE_DEPENDENCY_INFO};d.memoryBarrierCount=1;d.pMemoryBarriers=&b;vkCmdPipelineBarrier2(cb,&d);
    p.stages|=1u<<stage;p.formats[stage]=format;
    if(stage==3)p.compositeImage=image;
}
void bs4_probe_resolve(Bs4GpuFrameProbe& p,VkDevice dev){
    if(!p.pending||!p.mapped||!p.stages)return;
    p.pending=false;
    if(!p.coherent){VkMappedMemoryRange r{VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE};r.memory=p.memory;r.size=VK_WHOLE_SIZE;
        if(vkInvalidateMappedMemoryRanges(dev,1,&r)!=VK_SUCCESS)return;}
    Summary s[8]{};bool unusual=false,saturated=false;
    for(unsigned i=0;i<8;i++)if(p.stages&(1u<<i)){
        const auto* data=static_cast<const unsigned char*>(p.mapped)+stride*i;
        if(i<4||i==6||i==7)s[i]=summarize(data,i==1,i==7&&(p.formats[7]==VK_FORMAT_B8G8R8A8_UNORM||p.formats[7]==VK_FORMAT_B8G8R8A8_SRGB));
        else for(unsigned n=0;n<pixels;n++){
            float x{},y{};
            if(i==4){uint16_t h[2]{};std::memcpy(h,data+n*4,4);x=half(h[0]);y=half(h[1]);}
            else std::memcpy(&x,data+n*4,4);
            if(!std::isfinite(x)||!std::isfinite(y)){s[i].invalid++;continue;}
            s[i].min=std::min(s[i].min,x);s[i].max=std::max(s[i].max,x);s[i].maxY=std::max(s[i].maxY,std::abs(y));
        }
        unusual|=s[i].cyan>pixels/10||s[i].invalid;
        saturated|=(i<4||i==6||i==7)&&s[i].r>.98&&s[i].g>.98&&s[i].b<.75;
    }
    const bool wsi=bool(p.stages&(1u<<7));
    if(wsi) {
        if(wsi_reports++>=160)return;
    } else {
        if(reports>=96||(!unusual&&p.frame>=4&&p.frame%256&&(!saturated||p.frame%16)))return;
        reports++;
    }
    std::fprintf(stderr,"[BS4_FSR31] GPU_FRAME_PROBE dispatch=%llu camera=%llu stages=0x%x samples=%u history_reset=%u",
        (unsigned long long)p.frame,(unsigned long long)p.cameraFrame,p.stages,pixels,unsigned(p.historyReset));
    const char* names[]={"native","clone","fsr","ui","motion","depth","post_hud","swapchain"};
    for(unsigned i=0;i<8;i++)if((i<4||i==6||i==7)&&(p.stages&(1u<<i)))std::fprintf(stderr,
        " %s={cyan:%u white:%u red:%u invalid:%u top:%u bottom:%u mean:%.3f,%.3f,%.3f,%.3f}",
        names[i],s[i].cyan,s[i].white,s[i].red,s[i].invalid,s[i].topCyan,s[i].bottomCyan,s[i].r,s[i].g,s[i].b,s[i].a);
    if(p.stages&16)std::fprintf(stderr," motion={invalid:%u range_x:%.3f,%.3f max_abs_y:%.3f}",s[4].invalid,s[4].min,s[4].max,s[4].maxY);
    if(p.stages&128)std::fprintf(stderr," swapchain_image=%p",reinterpret_cast<void*>(p.wsiImage));
    if(p.stages&32)std::fprintf(stderr," depth={invalid:%u range:%.6f,%.6f}",s[5].invalid,s[5].min,s[5].max);
    std::fprintf(stderr," formats=%d,%d,%d,%d,%d,%d,%d,%d gpu_completed=1\n",int(p.formats[0]),int(p.formats[1]),int(p.formats[2]),int(p.formats[3]),int(p.formats[4]),int(p.formats[5]),int(p.formats[6]),int(p.formats[7]));
}
void bs4_probe_release(Bs4GpuFrameProbe& p,VkDevice dev){
    if(p.mapped)vkUnmapMemory(dev,p.memory);if(p.buffer)vkDestroyBuffer(dev,p.buffer,nullptr);
    if(p.memory)vkFreeMemory(dev,p.memory,nullptr);p={};
}
