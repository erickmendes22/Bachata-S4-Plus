// SPDX-License-Identifier: GPL-2.0-or-later
// R13 restart: read-only guest-buffer observation, no descriptor replacement,
// no render-pass suspension, no global image redirection.
#include "native_scene_observer.h"
#include "port_scene_frame.h"
#include "port_ui_composition.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <map>
#include <mutex>
#include <unordered_map>
#include <vector>
namespace {
struct Memory { VkDeviceSize size{},offset{},length{}; const unsigned char* data{}; };
struct Buffer { VkDeviceMemory memory{}; VkDeviceSize offset{}; };
using Buffers=std::map<std::pair<uint32_t,uint32_t>,VkDescriptorBufferInfo>;
struct DrawState {
    VkImageView depth{};
    VkExtent2D area{};
    uint32_t mrt{};
    std::array<float,4> raw{};
    bool rawValid{},inside{},haveCamera{};
    VkViewport viewport{};
    bool viewportValid{},viewportWithCount{};
    VkPipelineLayout graphicsLayout{};
    std::map<uint32_t,Buffers> pushes;
    std::map<uint32_t,VkDescriptorSet> sets;
    std::array<float,216> constants{};
    VkImageView cameraDepth{};
    VkExtent2D cameraSize{},cameraArea{};
    float cameraXSign{},cameraYSign{};
};
std::mutex guard;
std::unordered_map<VkDeviceMemory,Memory> memories;
std::unordered_map<VkBuffer,Buffer> buffers;
std::unordered_map<VkDescriptorSet,Buffers> descriptors;
std::unordered_map<VkCommandBuffer,DrawState> commands;
uint64_t frame=1;
std::unordered_map<VkPipelineLayout,uint64_t> layoutHashes;
PFN_vkAllocateMemory allocate;
PFN_vkMapMemory mapMemory;
PFN_vkUnmapMemory unmapMemory;
PFN_vkFreeMemory freeMemory;
PFN_vkBindBufferMemory bindBuffer;
PFN_vkBindBufferMemory2 bindBuffer2;
PFN_vkDestroyBuffer destroyBuffer;
PFN_vkCmdPushDescriptorSetKHR pushDescriptors;
PFN_vkUpdateDescriptorSets updateDescriptors;
PFN_vkCmdBindDescriptorSets bindSets;
PFN_vkCmdPushConstants pushConstants;
PFN_vkCmdSetViewport setViewport;
PFN_vkCmdSetViewportWithCount setViewportCount;
PFN_vkSetDebugUtilsObjectNameEXT objectName;
PFN_vkDestroyPipelineLayout destroyLayout;
PFN_vkCmdDraw draw;
PFN_vkCmdDrawIndexed drawIndexed;
PFN_vkCmdDrawIndirect drawIndirect;
PFN_vkCmdDrawIndexedIndirect drawIndexedIndirect;
bool parse(const VkDescriptorBufferInfo& info,std::array<float,216>& out) {
    // A scene buffer must actually contain the 864-byte native constants.
    if(info.range!=VK_WHOLE_SIZE&&info.range<864)return false;
    auto b=buffers.find(info.buffer);if(b==buffers.end())return false;
    auto m=memories.find(b->second.memory);
    if(m==memories.end()||!m->second.data)return false;
    if(info.offset>UINT64_MAX-b->second.offset)return false;
    const auto offset=info.offset+b->second.offset;
    if(offset<m->second.offset)return false;
    const auto relative=offset-m->second.offset;
    if(relative>m->second.length||m->second.length-relative<sizeof(out))return false;
    std::memcpy(out.data(),m->second.data+relative,sizeof(out));
    BachataCamera::Scene camera{};
    return BachataCamera::Parse(out.data(),sizeof(out),camera);
}
bool raw_matches(const DrawState& d,const BachataCamera::Scene& c) {
    if(!d.rawValid||!d.viewportValid)return false;
    const auto& v=d.viewport;
    // This also validates the native PushData field interpretation at every
    // actual draw. Never infer signs from a clip-disabled 16K viewport.
    const float width=2.f*d.raw[2],height=2.f*d.raw[3];
    return std::abs(width-v.width)<.01f&&std::abs(height-v.height)<.01f&&
           std::abs((d.raw[0]-d.raw[2])-v.x)<.01f&&
           std::abs((d.raw[1]-d.raw[3])-v.y)<.01f&&
           std::abs(width)>=c.width&&std::abs(height)>=c.height&&
           std::abs(width)<=4096&&std::abs(height)<=4096;
}
void observe_draw(VkCommandBuffer cb) {
    std::lock_guard lock{guard};
    auto it=commands.find(cb);if(it==commands.end())return;
    auto& d=it->second;
    if(!d.inside||d.mrt<5||!d.depth||d.haveCamera)return;
    auto inspect=[&](const Buffers& candidates) {
        for(const auto& item:candidates) {
            std::array<float,216> constants{};
            BachataCamera::Scene camera{};
            if(!parse(item.second,constants)||
               !BachataCamera::Parse(constants.data(),sizeof(constants),camera)||
               !BachataCamera::GBufferCanContainScene(d.mrt,true,d.area.width,d.area.height,camera)||
               !raw_matches(d,camera))continue;
            // Jitter is zero in this observer until an actual raster shift
            // is wired; do not report unapplied synthetic jitter to FSR.
            Bs4PortSceneFrame f{sizeof(f),1,frame,
                (uint64_t(camera.width)<<32)|camera.height,cb,d.depth,d.mrt,d.area,
                constants.data(),sizeof(constants),
                std::copysign(1.f,d.raw[2]),std::copysign(1.f,d.raw[3]),0.f,0.f};
            if(!bs4_fsr31_port_scene(&f))continue;
            d.haveCamera=true;d.cameraDepth=d.depth;
            d.cameraSize={camera.width,camera.height};d.cameraArea=d.area;d.constants=constants;
            d.cameraXSign=f.viewportXSign;d.cameraYSign=f.viewportYSign;
            static bool first=true;
            if(first) {first=false;std::fprintf(stderr,
              "[BS4_R13_PORT] native scene observed %ux%u raw_viewport_signs=%g,%g depth_bound=1\n",
              camera.width,camera.height,f.viewportXSign,f.viewportYSign);}
            return true;
        }
        return false;
    };
    for(const auto& p:d.pushes)if(inspect(p.second))return;
    for(const auto& p:d.sets) {
        auto s=descriptors.find(p.second);
        if(s!=descriptors.end()&&inspect(s->second))return;
    }
}
void writes(Buffers& dest,const VkWriteDescriptorSet& w) {
    for(uint32_t j=0;j<w.descriptorCount;j++) {
        const auto key=std::make_pair(w.dstBinding,w.dstArrayElement+j);
        dest.erase(key);
        // Dynamic offsets, inline uniform blocks and texel views are not
        // silently interpreted as ordinary mapped uniform buffers.
        if(w.pBufferInfo&&(w.descriptorType==VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER||
                          w.descriptorType==VK_DESCRIPTOR_TYPE_STORAGE_BUFFER))
            dest[key]=w.pBufferInfo[j];
    }
}
VkResult VKAPI_CALL allocate_hook(VkDevice d,const VkMemoryAllocateInfo* i,
                     const VkAllocationCallbacks* a,VkDeviceMemory* out) {
    const auto r=allocate(d,i,a,out);
    if(r==VK_SUCCESS&&i&&out){std::lock_guard lock{guard};memories[*out].size=i->allocationSize;}
    return r;
}
VkResult VKAPI_CALL map_hook(VkDevice d,VkDeviceMemory m,VkDeviceSize off,
                           VkDeviceSize len,VkMemoryMapFlags flags,void** out) {
    const auto r=mapMemory(d,m,off,len,flags,out);
    if(r==VK_SUCCESS&&out&&*out){std::lock_guard lock{guard};auto& rec=memories[m];
        if(off<=rec.size) {
            const auto available=rec.size-off;
            if(len==VK_WHOLE_SIZE||len<=available)
                rec={rec.size,off,len==VK_WHOLE_SIZE?available:len,
                     static_cast<const unsigned char*>(*out)};
        }
    }return r;
}
void VKAPI_CALL unmap_hook(VkDevice d,VkDeviceMemory m) {
    {std::lock_guard lock{guard};auto it=memories.find(m);if(it!=memories.end())it->second.data=nullptr;}
    unmapMemory(d,m);
}
void VKAPI_CALL free_hook(VkDevice d,VkDeviceMemory m,const VkAllocationCallbacks* a) {
    {std::lock_guard lock{guard};memories.erase(m);
     for(auto i=buffers.begin();i!=buffers.end();)i=i->second.memory==m?buffers.erase(i):std::next(i);}
    freeMemory(d,m,a);
}
VkResult VKAPI_CALL bind_hook(VkDevice d,VkBuffer b,VkDeviceMemory m,VkDeviceSize off) {
    const auto r=bindBuffer(d,b,m,off);if(r==VK_SUCCESS){std::lock_guard lock{guard};buffers[b]={m,off};}return r;
}
VkResult VKAPI_CALL bind2_hook(VkDevice d,uint32_t count,const VkBindBufferMemoryInfo* i) {
    const auto r=bindBuffer2(d,count,i);if(r==VK_SUCCESS&&i){std::lock_guard lock{guard};
        for(uint32_t n=0;n<count;n++)buffers[i[n].buffer]={i[n].memory,i[n].memoryOffset};}return r;
}
void VKAPI_CALL destroy_hook(VkDevice d,VkBuffer b,const VkAllocationCallbacks* a) {
    {std::lock_guard lock{guard};buffers.erase(b);}destroyBuffer(d,b,a);
}
void VKAPI_CALL push_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
                        uint32_t set,uint32_t count,const VkWriteDescriptorSet* w) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS&&w){std::lock_guard lock{guard};
        for(uint32_t n=0;n<count;n++)writes(commands[cb].pushes[set],w[n]);}
    pushDescriptors(cb,point,layout,set,count,w);
}
void VKAPI_CALL update_hook(VkDevice d,uint32_t count,const VkWriteDescriptorSet* w,
                           uint32_t copies,const VkCopyDescriptorSet* c) {
    {std::lock_guard lock{guard};if(w)for(uint32_t n=0;n<count;n++)writes(descriptors[w[n].dstSet],w[n]);
     // Unsupported descriptor-copy updates invalidate destination knowledge.
     if(c)for(uint32_t n=0;n<copies;n++)descriptors.erase(c[n].dstSet);}
    updateDescriptors(d,count,w,copies,c);
}
void VKAPI_CALL sets_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
                         uint32_t first,uint32_t count,const VkDescriptorSet* s,
                         uint32_t dynCount,const uint32_t* dyn) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS&&s){std::lock_guard lock{guard};
        auto& active=commands[cb].sets;for(uint32_t n=0;n<count;n++){
            if(dynCount)active.erase(first+n);else active[first+n]=s[n];
        }}
    bindSets(cb,point,layout,first,count,s,dynCount,dyn);
}
void VKAPI_CALL constants_hook(VkCommandBuffer cb,VkPipelineLayout l,VkShaderStageFlags stage,
                              uint32_t offset,uint32_t size,const void* values) {
    if((stage&VK_SHADER_STAGE_VERTEX_BIT)&&offset==0&&size==120&&values) {
        std::lock_guard lock{guard};auto& d=commands[cb];
        std::memcpy(d.raw.data(),values,16);d.rawValid=true;d.graphicsLayout=l;
        for(float v:d.raw)if(!std::isfinite(v))d.rawValid=false;
    }
    pushConstants(cb,l,stage,offset,size,values);
}
void VKAPI_CALL viewport_hook(VkCommandBuffer cb,uint32_t first,uint32_t count,const VkViewport* v) {
    if(first==0){std::lock_guard lock{guard};auto& d=commands[cb];d.viewportValid=count==1&&v;d.viewportWithCount=false;
        if(d.viewportValid)d.viewport=*v;}
    setViewport(cb,first,count,v);
}
void VKAPI_CALL viewport_count_hook(VkCommandBuffer cb,uint32_t count,const VkViewport* v) {
    {std::lock_guard lock{guard};auto& d=commands[cb];d.viewportValid=count==1&&v;
     d.viewportWithCount=true;if(d.viewportValid)d.viewport=*v;}
    setViewportCount(cb,count,v);
}
VkResult VKAPI_CALL name_hook(VkDevice dev,const VkDebugUtilsObjectNameInfoEXT* info) {
    if(info&&info->objectType==VK_OBJECT_TYPE_PIPELINE_LAYOUT) {
        std::lock_guard lock{guard};auto layout=(VkPipelineLayout)(uintptr_t)info->objectHandle;
        layoutHashes.erase(layout);
        const char* name=info->pObjectName;
        if(name&&std::strncmp(name,"Graphics PipelineLayout ",24)==0) {
            const char* vertex=std::strstr(name,"vs_0x");
            if(vertex) {
                char* end{};const auto hash=std::strtoull(vertex+5,&end,16);
                if(end!=vertex+5&&(*end=='\0'||*end=='_'||*end==','))layoutHashes[layout]=hash;
            }
        }
    }
    return objectName(dev,info);
}
void VKAPI_CALL layout_destroy_hook(VkDevice dev,VkPipelineLayout layout,const VkAllocationCallbacks* ac) {
    {std::lock_guard lock{guard};layoutHashes.erase(layout);}destroyLayout(dev,layout,ac);
}
float halton(uint64_t n,unsigned base) {
    float f=1.f,r=0.f;while(n){f/=base;r+=f*float(n%base);n/=base;}return r;
}
struct ViewportShift {VkViewport original{},shifted{};bool applied{},withCount{};};
void native_viewport(VkCommandBuffer cb,const VkViewport& v,bool withCount) {
    if(withCount)setViewportCount(cb,1,&v);else setViewport(cb,0,1,&v);
}
ViewportShift shift_geometry(VkCommandBuffer cb,uint32_t vertices,uint32_t instances) {
    ViewportShift out{};
    {
        std::lock_guard lock{guard};auto it=commands.find(cb);
        if(it==commands.end()||frame<2||(vertices<=6&&instances<=1))return out;
        auto& d=it->second;
        if(!d.haveCamera||!d.inside||d.depth!=d.cameraDepth||!d.viewportValid||
           (d.viewportWithCount?!setViewportCount:!setViewport))return out;
        BachataCamera::Scene camera{};
        if(!BachataCamera::Parse(d.constants.data(),sizeof(d.constants),camera)||
           !raw_matches(d,camera)||
           std::abs(d.viewport.width)!=camera.width||
           std::abs(d.viewport.height)!=camera.height)return out;
        const auto phases=uint64_t(std::ceil(8.*std::pow(1280./camera.width,2)));
        const auto phase=(frame-1)%std::clamp<uint64_t>(phases,8,256)+1;
        const float x=halton(phase,2)-.5f,y=halton(phase,3)-.5f;
        Bs4PortSceneFrame f{sizeof(f),1,frame,
            (uint64_t(camera.width)<<32)|camera.height,cb,d.cameraDepth,5,d.cameraArea,
            d.constants.data(),sizeof(d.constants),d.cameraXSign,d.cameraYSign,x,y};
        if(!bs4_fsr31_port_scene(&f))return out;
        out.original=d.viewport;out.shifted=d.viewport;
        out.shifted.x+=x;out.shifted.y+=y;out.applied=true;out.withCount=d.viewportWithCount;
    }
    // Call the ORIGINAL entry point. Do not corrupt the observer's/native
    // cache of the unshifted viewport, or recursively intercept our own shift.
    native_viewport(cb,out.shifted,out.withCount);
    return out;
}
void restore(VkCommandBuffer cb,const ViewportShift& shift) {
    if(shift.applied)native_viewport(cb,shift.original,shift.withCount);
}
void VKAPI_CALL draw_hook(VkCommandBuffer cb,uint32_t n,uint32_t i,uint32_t first,uint32_t base) {
    observe_draw(cb);const auto shift=shift_geometry(cb,n,i);
    draw(cb,n,i,first,base);restore(cb,shift);
}
void VKAPI_CALL indexed_hook(VkCommandBuffer cb,uint32_t n,uint32_t i,uint32_t first,int32_t vertex,uint32_t base) {
    observe_draw(cb);const auto shift=shift_geometry(cb,n,i);
    drawIndexed(cb,n,i,first,vertex,base);restore(cb,shift);
}
void VKAPI_CALL indirect_hook(VkCommandBuffer cb,VkBuffer b,VkDeviceSize off,uint32_t n,uint32_t stride) {
    observe_draw(cb);drawIndirect(cb,b,off,n,stride);
}
void VKAPI_CALL indexed_indirect_hook(VkCommandBuffer cb,VkBuffer b,VkDeviceSize off,uint32_t n,uint32_t stride) {
    observe_draw(cb);drawIndexedIndirect(cb,b,off,n,stride);
}
}
void bs4_native_scene_begin(VkCommandBuffer cb,const VkRenderingInfo* info) {
    {
        std::lock_guard lock{guard};auto& d=commands[cb];d.inside=info;
        d.depth=info&&info->pDepthAttachment?info->pDepthAttachment->imageView:VK_NULL_HANDLE;
        if(d.depth&&d.depth!=d.cameraDepth)d.haveCamera=false;
        d.mrt=info?info->colorAttachmentCount:0;d.area=info?info->renderArea.extent:VkExtent2D{};
    }
    // The native BindResources/UpdateDynamicState commands precede
    // Scheduler::BeginRendering. Capture their constants here, before any
    // rendering instance starts; do not wait for a speculative HUD draw.
    observe_draw(cb);
}

void bs4_native_scene_end(VkCommandBuffer cb) {
    std::lock_guard lock{guard};commands[cb].inside=false;
}
void bs4_native_scene_reset(VkCommandBuffer cb) {
    std::lock_guard lock{guard};commands.erase(cb);
}
void bs4_native_scene_present() {
    std::lock_guard lock{guard};commands.clear();++frame;
}
bool bs4_native_scene_camera(VkCommandBuffer cb,VkImageView* depth,VkExtent2D* size) {
    if(!depth||!size)return false;
    std::lock_guard lock{guard};const auto it=commands.find(cb);
    if(it==commands.end()||!it->second.haveCamera)return false;
    *depth=it->second.cameraDepth;*size=it->second.cameraSize;return true;
}
extern "C" PFN_vkVoidFunction bs4_native_scene_wrap(const char* name,PFN_vkVoidFunction proc) {
    if(!name||!proc)return proc;
    const char* input=std::getenv("BACHATA_FSR31_INPUT");
    if(!input||std::strcmp(input,"port"))return proc;
#define WRAP(member,symbol,fn) if(!std::strcmp(name,symbol)) {member=reinterpret_cast<decltype(member)>(proc);return reinterpret_cast<PFN_vkVoidFunction>(fn);}
    WRAP(allocate,"vkAllocateMemory",allocate_hook)
    WRAP(mapMemory,"vkMapMemory",map_hook)
    WRAP(unmapMemory,"vkUnmapMemory",unmap_hook)
    WRAP(freeMemory,"vkFreeMemory",free_hook)
    WRAP(bindBuffer,"vkBindBufferMemory",bind_hook)
    WRAP(bindBuffer2,"vkBindBufferMemory2",bind2_hook)
    WRAP(bindBuffer2,"vkBindBufferMemory2KHR",bind2_hook)
    WRAP(destroyBuffer,"vkDestroyBuffer",destroy_hook)
    WRAP(pushDescriptors,"vkCmdPushDescriptorSetKHR",push_hook)
    WRAP(updateDescriptors,"vkUpdateDescriptorSets",update_hook)
    WRAP(bindSets,"vkCmdBindDescriptorSets",sets_hook)
    WRAP(pushConstants,"vkCmdPushConstants",constants_hook)
    WRAP(setViewport,"vkCmdSetViewport",viewport_hook)
    WRAP(setViewportCount,"vkCmdSetViewportWithCount",viewport_count_hook)
    WRAP(setViewportCount,"vkCmdSetViewportWithCountEXT",viewport_count_hook)
    WRAP(objectName,"vkSetDebugUtilsObjectNameEXT",name_hook)
    WRAP(destroyLayout,"vkDestroyPipelineLayout",layout_destroy_hook)
    WRAP(draw,"vkCmdDraw",draw_hook)
    WRAP(drawIndexed,"vkCmdDrawIndexed",indexed_hook)
    WRAP(drawIndirect,"vkCmdDrawIndirect",indirect_hook)
    WRAP(drawIndexedIndirect,"vkCmdDrawIndexedIndirect",indexed_indirect_hook)
#undef WRAP
    return proc;
}

bool bs4_native_scene_ui_boundary(VkCommandBuffer cb) {
    std::lock_guard lock{guard};auto it=commands.find(cb);
    if(it==commands.end())return false;
    const auto hash=layoutHashes.find(it->second.graphicsLayout);
    return hash!=layoutHashes.end()&&Vulkan::UiComposition::MovieShader(hash->second);
}
