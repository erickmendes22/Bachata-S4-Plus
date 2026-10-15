// SPDX-License-Identifier: GPL-2.0-or-later
// R13 restart: read-only guest-buffer observation, no descriptor replacement,
// no render-pass suspension, no global image redirection.
#include "native_scene_observer.h"
extern VkImageView bs4_native_ui_sampled_view(VkCommandBuffer,VkImageView) __attribute__((weak));
extern "C" void bs4_fsr31_before_native_draw(VkCommandBuffer) __attribute__((weak));
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
extern "C" bool bs4_fsr31_temporal_resources_ready(VkExtent2D);
namespace {
std::unordered_map<VkCommandBuffer,Bs4NativeUiBoundary> native_ui_boundaries;
struct Memory { VkDeviceSize size{},offset{},length{}; const unsigned char* data{}; };
struct Buffer { VkDeviceMemory memory{}; VkDeviceSize offset{}; };
using Sampled=std::map<std::pair<uint32_t,uint32_t>,VkImageView>;
using Buffers=std::map<std::pair<uint32_t,uint32_t>,VkDescriptorBufferInfo>;
struct DrawState {
    VkImageView depth{};
    std::array<VkImageView,8> colors{};
    VkExtent2D area{};
    uint64_t renderEpoch{};
    uint32_t mrt{};
    std::array<float,4> raw{};
    std::array<unsigned char,120> pushRaw{};
    VkShaderStageFlags pushStages{};
    bool rawValid{},inside{},haveCamera{},cameraLatched{};
    VkViewport viewport{};
    bool viewportValid{},viewportWithCount{};
    VkPipelineLayout graphicsLayout{},boundGraphicsLayout{};bool pipelineObserved{},pendingGraphicsResources{};
    VkRect2D scissor{};
    bool scissorValid{},scissorWithCount{};
    std::map<uint32_t,Buffers> pushes;
    std::map<uint32_t,Sampled> sampledPushes;
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
std::unordered_map<VkDescriptorSet,Sampled> sampledDescriptors;
std::unordered_map<VkCommandBuffer,DrawState> commands;
uint64_t frame=1;
std::unordered_map<VkPipelineLayout,uint64_t> layoutHashes, fragmentHashes;
std::unordered_map<VkPipeline,VkPipelineLayout> graphicsPipelines;
std::unordered_map<VkImageView,Bs4SceneWriter> sceneWriters;
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
PFN_vkCmdSetScissor setScissor;
PFN_vkCmdSetScissorWithCount setScissorCount;
PFN_vkCmdSetViewport setViewport;
PFN_vkCmdSetViewportWithCount setViewportCount;
PFN_vkSetDebugUtilsObjectNameEXT objectName;
PFN_vkDestroyPipelineLayout destroyLayout;
PFN_vkCreateGraphicsPipelines createGraphics;
PFN_vkDestroyPipeline destroyPipeline;
PFN_vkCmdBindPipeline bindPipeline;
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
            d.haveCamera=true;d.cameraLatched=true;d.cameraDepth=d.depth;
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
void sampled_writes(Sampled& dest,const VkWriteDescriptorSet& w) {
    for(uint32_t n=0;n<w.descriptorCount;++n){
        const auto key=std::make_pair(w.dstBinding,w.dstArrayElement+n);dest.erase(key);
        if(w.pImageInfo&&(w.descriptorType==VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE||
            w.descriptorType==VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER||
            w.descriptorType==VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT))dest[key]=w.pImageInfo[n].imageView;
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
        commands[cb].sets.erase(set);
        for(uint32_t n=0;n<count;n++){writes(commands[cb].pushes[set],w[n]);sampled_writes(commands[cb].sampledPushes[set],w[n]);}}
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS&&w&&bs4_native_ui_sampled_view) {
        std::vector<VkWriteDescriptorSet> changed(w,w+count);
        std::vector<std::vector<VkDescriptorImageInfo>> images(count);
        for(uint32_t i=0;i<count;i++)if(w[i].pImageInfo&&
            (w[i].descriptorType==VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER||w[i].descriptorType==VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE)) {
            images[i].assign(w[i].pImageInfo,w[i].pImageInfo+w[i].descriptorCount);
            for(auto& image:images[i])image.imageView=bs4_native_ui_sampled_view(cb,image.imageView);
            changed[i].pImageInfo=images[i].data();
        }
        pushDescriptors(cb,point,layout,set,count,changed.data());return;
    }
    pushDescriptors(cb,point,layout,set,count,w);
}
void VKAPI_CALL update_hook(VkDevice d,uint32_t count,const VkWriteDescriptorSet* w,
                           uint32_t copies,const VkCopyDescriptorSet* c) {
    {std::lock_guard lock{guard};if(w)for(uint32_t n=0;n<count;n++){writes(descriptors[w[n].dstSet],w[n]);sampled_writes(sampledDescriptors[w[n].dstSet],w[n]);}
     // Unsupported descriptor-copy updates invalidate destination knowledge.
     if(c)for(uint32_t n=0;n<copies;n++){descriptors.erase(c[n].dstSet);sampledDescriptors.erase(c[n].dstSet);}}
    updateDescriptors(d,count,w,copies,c);
}
void VKAPI_CALL sets_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
                         uint32_t first,uint32_t count,const VkDescriptorSet* s,
                         uint32_t dynCount,const uint32_t* dyn) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS&&s){std::lock_guard lock{guard};
        auto& active=commands[cb].sets;for(uint32_t n=0;n<count;n++){
            if(dynCount)active.erase(first+n);else {active[first+n]=s[n];commands[cb].sampledPushes.erase(first+n);}
        }}
    bindSets(cb,point,layout,first,count,s,dynCount,dyn);
}
void VKAPI_CALL constants_hook(VkCommandBuffer cb,VkPipelineLayout l,VkShaderStageFlags stage,
                              uint32_t offset,uint32_t size,const void* values) {
    if((stage&VK_SHADER_STAGE_VERTEX_BIT)&&offset==0&&size==120&&values) {
        std::lock_guard lock{guard};auto& d=commands[cb];
        std::memcpy(d.raw.data(),values,16);d.rawValid=true;d.graphicsLayout=l;
        std::memcpy(d.pushRaw.data(),values,120);d.pushStages=stage;
        d.pendingGraphicsResources=true;
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
void VKAPI_CALL scissor_hook(VkCommandBuffer cb,uint32_t first,uint32_t count,const VkRect2D* value) {
    if(first==0){std::lock_guard lock{guard};auto& d=commands[cb];
        d.scissorValid=count==1&&value;d.scissorWithCount=false;if(d.scissorValid)d.scissor=*value;}
    setScissor(cb,first,count,value);
}
void VKAPI_CALL scissor_count_hook(VkCommandBuffer cb,uint32_t count,const VkRect2D* value) {
    {std::lock_guard lock{guard};auto& d=commands[cb];d.scissorValid=count==1&&value;
        d.scissorWithCount=true;if(d.scissorValid)d.scissor=*value;}
    setScissorCount(cb,count,value);
}
VkPipelineLayout shader_layout(const DrawState& d){
    // Push constants can legally remain valid across compatible pipeline switches.
    // They are not proof of the shader currently executing this draw.
    return d.pipelineObserved?d.boundGraphicsLayout:d.graphicsLayout;
}
VkPipelineLayout boundary_layout(const DrawState& d){
#ifdef BS4_FSR31_TEST_HARNESS
    if(std::getenv("BS4_TEST_USE_PREVIOUS_BOUND_BOUNDARY"))return shader_layout(d);
#endif
    // Core025 records BindResources/PushData before BeginRendering, then binds
    // the draw's graphics pipeline AFTER BeginRendering. At this boundary the
    // previously bound pipeline belongs to the preceding draw. Only a fresh,
    // complete native PushData packet may identify the upcoming draw. A real
    // graphics bind or completed draw consumes it; stale constants never win.
    return d.pendingGraphicsResources&&d.rawValid?d.graphicsLayout:shader_layout(d);
}
VkResult VKAPI_CALL graphics_create_hook(VkDevice dev,VkPipelineCache cache,uint32_t count,
    const VkGraphicsPipelineCreateInfo* info,const VkAllocationCallbacks* alloc,VkPipeline* out){
    if(out)std::fill(out,out+count,VK_NULL_HANDLE);
    const auto result=createGraphics(dev,cache,count,info,alloc,out);
    // Pipeline creation may partially succeed; only non-null returned handles have state.
    if(info&&out){std::lock_guard lock{guard};for(uint32_t n=0;n<count;++n)
        if(out[n])graphicsPipelines[out[n]]=info[n].layout;}
    return result;
}
void VKAPI_CALL pipeline_destroy_hook(VkDevice dev,VkPipeline pipeline,const VkAllocationCallbacks* alloc){
    {std::lock_guard lock{guard};graphicsPipelines.erase(pipeline);}
    destroyPipeline(dev,pipeline,alloc);
}
void VKAPI_CALL pipeline_bind_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipeline pipeline){
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS){std::lock_guard lock{guard};auto& d=commands[cb];
        d.pipelineObserved=true;d.pendingGraphicsResources=false;const auto it=graphicsPipelines.find(pipeline);
        d.boundGraphicsLayout=it==graphicsPipelines.end()?VK_NULL_HANDLE:it->second;
    }
    bindPipeline(cb,point,pipeline);
}
VkResult VKAPI_CALL name_hook(VkDevice dev,const VkDebugUtilsObjectNameInfoEXT* info) {
    if(info&&info->objectType==VK_OBJECT_TYPE_PIPELINE_LAYOUT) {
        std::lock_guard lock{guard};auto layout=(VkPipelineLayout)(uintptr_t)info->objectHandle;
        layoutHashes.erase(layout);fragmentHashes.erase(layout);
        const char* name=info->pObjectName;
        if(name&&std::strncmp(name,"Graphics PipelineLayout ",24)==0) {
            const char* fragment=std::strstr(name,"fs_0x");
            if(!fragment)fragment=std::strstr(name,"ps_0x");
            if(fragment){char* end{};const auto h=std::strtoull(fragment+5,&end,16);
                if(end!=fragment+5&&(*end=='\0'||*end=='_'||*end==','))fragmentHashes[layout]=h;}
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
    {std::lock_guard lock{guard};layoutHashes.erase(layout);fragmentHashes.erase(layout);}destroyLayout(dev,layout,ac);
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
        if(!bs4_fsr31_temporal_resources_ready(d.cameraSize))return out;
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
void note_writer(VkCommandBuffer cb,uint32_t vertices,uint32_t instances) {
    std::lock_guard lock{guard};const auto it=commands.find(cb);
    if(it==commands.end())return;
    it->second.pendingGraphicsResources=false;
    if(!vertices||!instances||!it->second.inside)return;
    const auto& d=it->second;
    Bs4SceneWriter writer{};writer.command=cb;writer.frame=frame;writer.area=d.area;
    std::copy(d.raw.begin(),d.raw.end(),writer.rawViewport);writer.rawViewportValid=d.rawValid;
    writer.viewport=d.viewport;writer.scissor=d.scissor;writer.scissorValid=d.scissorValid;writer.renderEpoch=d.renderEpoch;writer.vertices=vertices;writer.instances=instances;writer.colorCount=d.mrt;
    const auto vs=layoutHashes.find(shader_layout(d)),ps=fragmentHashes.find(shader_layout(d));
    if(vs!=layoutHashes.end())writer.vertexHash=vs->second;
    if(ps!=fragmentHashes.end())writer.fragmentHash=ps->second;
    auto add=[&](const Sampled& bindings){for(const auto& pair:bindings)if(pair.second){
        bool found=false;for(uint32_t n=0;n<writer.sampledCount;++n)found|=writer.sampled[n]==pair.second;
        if(found)continue;
        if(writer.sampledCount<8)writer.sampled[writer.sampledCount++]=pair.second;else writer.sampledOverflow=true;
    }};
    for(const auto& p:d.sampledPushes)add(p.second);
    for(const auto& p:d.sets){const auto it=sampledDescriptors.find(p.second);if(it!=sampledDescriptors.end())add(it->second);}
    for(const auto color:d.colors)if(color)sceneWriters[color]=writer;
}
void VKAPI_CALL draw_hook(VkCommandBuffer cb,uint32_t n,uint32_t i,uint32_t first,uint32_t base) {
    if(n&&i&&bs4_fsr31_before_native_draw)bs4_fsr31_before_native_draw(cb);
    observe_draw(cb);const auto shift=shift_geometry(cb,n,i);
    draw(cb,n,i,first,base);restore(cb,shift);note_writer(cb,n,i);
}
void VKAPI_CALL indexed_hook(VkCommandBuffer cb,uint32_t n,uint32_t i,uint32_t first,int32_t vertex,uint32_t base) {
    if(n&&i&&bs4_fsr31_before_native_draw)bs4_fsr31_before_native_draw(cb);
    observe_draw(cb);const auto shift=shift_geometry(cb,n,i);
    drawIndexed(cb,n,i,first,vertex,base);restore(cb,shift);note_writer(cb,n,i);
}
void VKAPI_CALL indirect_hook(VkCommandBuffer cb,VkBuffer b,VkDeviceSize off,uint32_t n,uint32_t stride) {
    if(n&&bs4_fsr31_before_native_draw)bs4_fsr31_before_native_draw(cb);
    observe_draw(cb);
    // GPU indirect arguments may not be host-visible. A proven G-buffer
    // geometry pass supplies the contract; do not infer a vertex count from
    // unreadable GPU memory or jitter a fullscreen post-processing pass.
    bool geometry=false;{std::lock_guard lock{guard};auto it=commands.find(cb);
        geometry=it!=commands.end()&&it->second.mrt>=5;}
    const auto shift=geometry&&n?shift_geometry(cb,UINT32_MAX,1):ViewportShift{};
    drawIndirect(cb,b,off,n,stride);restore(cb,shift);note_writer(cb,UINT32_MAX,n);
}
void VKAPI_CALL indexed_indirect_hook(VkCommandBuffer cb,VkBuffer b,VkDeviceSize off,uint32_t n,uint32_t stride) {
    if(n&&bs4_fsr31_before_native_draw)bs4_fsr31_before_native_draw(cb);
    observe_draw(cb);
    bool geometry=false;{std::lock_guard lock{guard};auto it=commands.find(cb);
        geometry=it!=commands.end()&&it->second.mrt>=5;}
    const auto shift=geometry&&n?shift_geometry(cb,UINT32_MAX,1):ViewportShift{};
    drawIndexedIndirect(cb,b,off,n,stride);restore(cb,shift);note_writer(cb,UINT32_MAX,n);
}
}
void bs4_native_scene_begin(VkCommandBuffer cb,const VkRenderingInfo* info) {
    {
        std::lock_guard lock{guard};auto& d=commands[cb];d.inside=info;++d.renderEpoch;d.colors={};
        if(info&&info->pColorAttachments)for(uint32_t n=0;n<std::min<uint32_t>(8,info->colorAttachmentCount);++n)
            d.colors[n]=info->pColorAttachments[n].imageView;
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
    std::lock_guard lock{guard};commands.erase(cb);native_ui_boundaries.erase(cb);
}
void bs4_native_scene_present() {
    std::lock_guard lock{guard};commands.clear();native_ui_boundaries.clear();++frame;
}
bool bs4_native_scene_camera(VkCommandBuffer cb,VkImageView* depth,VkExtent2D* size) {
    if(!depth||!size)return false;
    std::lock_guard lock{guard};const auto it=commands.find(cb);
    // The camera is captured during the multi-target G-buffer pass.
    // The following LDR 640x360 scene pass often uses no depth attachment,
    // so haveCamera is invalidated for *current* geometry; keep its last
    // proven camera for this command buffer until reset/present.
    if(it==commands.end()||!it->second.cameraLatched)return false;
    *depth=it->second.cameraDepth;*size=it->second.cameraSize;return true;
}
extern "C" PFN_vkVoidFunction bs4_native_scene_wrap(const char* name,PFN_vkVoidFunction proc) {
    if(!name||!proc)return proc;
    const char* input=std::getenv("BACHATA_FSR31_INPUT");
    if(!input||std::strcmp(input,"port"))return proc;
#define WRAP(member,symbol,fn) if(!std::strcmp(name,symbol)) {if(proc!=reinterpret_cast<PFN_vkVoidFunction>(fn))member=reinterpret_cast<decltype(member)>(proc);return reinterpret_cast<PFN_vkVoidFunction>(fn);}
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
    WRAP(setScissor,"vkCmdSetScissor",scissor_hook)
    WRAP(setScissorCount,"vkCmdSetScissorWithCount",scissor_count_hook)
    WRAP(setScissorCount,"vkCmdSetScissorWithCountEXT",scissor_count_hook)
    WRAP(objectName,"vkSetDebugUtilsObjectNameEXT",name_hook)
    WRAP(destroyLayout,"vkDestroyPipelineLayout",layout_destroy_hook)
    WRAP(createGraphics,"vkCreateGraphicsPipelines",graphics_create_hook)
    WRAP(destroyPipeline,"vkDestroyPipeline",pipeline_destroy_hook)
    WRAP(bindPipeline,"vkCmdBindPipeline",pipeline_bind_hook)
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
    const auto hash=layoutHashes.find(boundary_layout(it->second));
    const bool movie=hash!=layoutHashes.end()&&Vulkan::UiComposition::MovieShader(hash->second);
    const auto old=layoutHashes.find(it->second.graphicsLayout);
    if(!it->second.pendingGraphicsResources&&it->second.pipelineObserved&&!movie&&old!=layoutHashes.end()&&Vulkan::UiComposition::MovieShader(old->second)){
        static unsigned logs=0;if(logs++<16)std::fprintf(stderr,
            "[BS4_FSR31] UI_SHADER_IDENTITY_REJECTED_STALE_PUSH cb=%p pushed_vs=0x%llx bound_vs=0x%llx bound_known=%d\n",
            reinterpret_cast<void*>(cb),(unsigned long long)old->second,
            (unsigned long long)(hash==layoutHashes.end()?0:hash->second),int(bool(it->second.boundGraphicsLayout)));
    }
    if(it->second.pendingGraphicsResources&&it->second.pipelineObserved&&
       boundary_layout(it->second)!=shader_layout(it->second)){
        static unsigned logs=0;if(logs++<16)std::fprintf(stderr,
            "[BS4_FSR31] UI_BOUNDARY_PENDING_RESOURCES cb=%p next_vs=0x%llx movie=%d previous_pipeline=%p\n",
            reinterpret_cast<void*>(cb),(unsigned long long)(hash==layoutHashes.end()?0:hash->second),
            int(movie),reinterpret_cast<void*>(it->second.boundGraphicsLayout));
    }
    return movie;
}

void bs4_native_scene_draw_state(VkCommandBuffer cb,const Bs4NativeRenderState& state) {
    if(!cb||state.colorCount>1||!state.width||!state.height)return;
    std::lock_guard lock{guard};const auto it=commands.find(cb);
    if(it==commands.end()||!it->second.rawValid)return;
    const auto& d=it->second;
    const auto hash=layoutHashes.find(boundary_layout(d));
    if(hash==layoutHashes.end()||!Vulkan::UiComposition::MovieShader(hash->second))return;
    // The native scheduler can reuse an existing rendering instance. This
    // callback is ordered after BindResources on its worker, so shader/raw
    // viewport identity is current even without a Vulkan BeginRendering.
    if(!state.colorCount&&!state.depthEnabled&&!state.stencilEnabled)return;
    Bs4NativeUiBoundary boundary{};boundary.frame=frame;
    boundary.color=state.colorCount?reinterpret_cast<VkImageView>(state.colors[0].view):VK_NULL_HANDLE;
    boundary.depth=(state.depthEnabled||state.stencilEnabled)?
        reinterpret_cast<VkImageView>(state.depth):VK_NULL_HANDLE;
    boundary.guestExtent={state.width,state.height};
    std::copy(d.raw.begin(),d.raw.end(),boundary.rawViewport);
    // A command buffer may contain multiple UI draws in a single frame.
    // Preserve the newest native attachment/viewport instead of retaining
    // the first entry and misrouting later shared-target HUD draws.
    native_ui_boundaries.insert_or_assign(cb,boundary);
    static bool loggedColor=false;
    if(boundary.color&&!loggedColor) {
        loggedColor=true;
        std::fprintf(stderr,
            "[BS4_FSR31] FIRST_NATIVE_COLOR_UI_BOUNDARY hash=0x%llx "
            "color=%p extent=%ux%u command=%p\\n",
            static_cast<unsigned long long>(hash->second),
            reinterpret_cast<void*>(boundary.color),boundary.guestExtent.width,
            boundary.guestExtent.height,reinterpret_cast<void*>(cb));
    }
    static bool logged=false;
    if(!logged) {
        logged=true;
        std::fprintf(stderr,
           "[BS4_FSR31] FIRST_NATIVE_UI_BOUNDARY vertex_hash=0x%llx "
           "hud_view=%p extent=%ux%u command=%p\\n",
           static_cast<unsigned long long>(hash->second),
           reinterpret_cast<void*>(boundary.color),boundary.guestExtent.width,
           boundary.guestExtent.height,reinterpret_cast<void*>(cb));
    }
}

bool bs4_native_scene_ui_state(VkCommandBuffer cb,Bs4NativeUiBoundary& out) {
    std::lock_guard lock{guard};const auto it=native_ui_boundaries.find(cb);
    if(it==native_ui_boundaries.end()||it->second.frame!=frame)return false;
    out=it->second;return true;
}

void bs4_native_scene_register_pipeline(VkPipelineLayout layout,uint64_t hash) {
    if(!layout)return;
    std::lock_guard lock{guard};layoutHashes[layout]=hash;
}

bool bs4_native_scene_dynamic_ready(VkCommandBuffer cb) {
    std::lock_guard lock{guard};const auto it=commands.find(cb);
    if(it==commands.end())return false;
    const auto& d=it->second;
    return d.rawValid&&d.viewportValid&&d.scissorValid&&pushConstants&&
        (d.viewportWithCount?bool(setViewportCount):bool(setViewport))&&
        (d.scissorWithCount?bool(setScissorCount):bool(setScissor));
}

static bool scale_ui(VkCommandBuffer cb,VkExtent2D guest,VkExtent2D output,
                     bool scaled,VkExtent2D hardware,bool record) {
    struct Snapshot {
        std::array<float,4> raw{};std::array<unsigned char,120> pushRaw{};
        VkPipelineLayout graphicsLayout{};VkShaderStageFlags pushStages{};
        VkViewport viewport{};VkRect2D scissor{};
        bool rawValid{},viewportValid{},scissorValid{},viewportWithCount{},scissorWithCount{};
    } d;
    {std::lock_guard lock{guard};const auto it=commands.find(cb);
        if(it==commands.end())return false;
        const auto& original=it->second;
        d={original.raw,original.pushRaw,original.graphicsLayout,original.pushStages,
           original.viewport,original.scissor,original.rawValid,original.viewportValid,
           original.scissorValid,original.viewportWithCount,original.scissorWithCount};}
    if(!d.rawValid||!d.viewportValid||!d.scissorValid||!pushConstants||
       !guest.width||!guest.height||!output.width||!output.height)return false;
    const auto scale=scaled?Vulkan::UiComposition::Scale(guest.width,guest.height,
        output.width,output.height,Vulkan::UiComposition::NativeViewport(2*d.raw[2],2*d.raw[3])):
        std::array<float,2>{1.f,1.f};
    float raw[4];std::memcpy(raw,d.pushRaw.data(),16);
    raw[0]*=scale[0];raw[2]*=scale[0];raw[1]*=scale[1];raw[3]*=scale[1];
    std::memcpy(d.pushRaw.data(),raw,16);
    // Port keeps the hardware-window viewport when clipping is disabled.
    // Only its raw shader viewport and scissor scale in that case.
    const bool clipDisabled=d.viewport.x==0&&d.viewport.y==0&&
        d.viewport.width==float(hardware.width)&&d.viewport.height==float(hardware.height);
    if(!clipDisabled){d.viewport.x*=scale[0];d.viewport.width*=scale[0];
        d.viewport.y*=scale[1];d.viewport.height*=scale[1];}
    if(!std::isfinite(d.viewport.width)||!std::isfinite(d.viewport.height)||
       std::abs(d.viewport.width)>hardware.width||std::abs(d.viewport.height)>hardware.height)return false;
    const auto x0=std::lround(double(d.scissor.offset.x)*scale[0]);
    const auto y0=std::lround(double(d.scissor.offset.y)*scale[1]);
    const auto x1=std::lround((double(d.scissor.offset.x)+d.scissor.extent.width)*scale[0]);
    const auto y1=std::lround((double(d.scissor.offset.y)+d.scissor.extent.height)*scale[1]);
    if(x0<0||y0<0||x1>INT32_MAX||y1>INT32_MAX)return false;
    d.scissor={{int32_t(x0),int32_t(y0)},{uint32_t(std::max(0L,x1-x0)),uint32_t(std::max(0L,y1-y0))}};
    if((d.viewportWithCount?!setViewportCount:!setViewport)||
       (d.scissorWithCount?!setScissorCount:!setScissor))return false;
    // Original entry points preserve the native cache of unscaled values.
    // The draw boundary also calls this with scaled=false for other targets,
    // restoring state even when the native cache suppresses repeated commands.
    if(!record)return true;
    pushConstants(cb,d.graphicsLayout,d.pushStages,0,120,d.pushRaw.data());
    native_viewport(cb,d.viewport,d.viewportWithCount);
    if(d.scissorWithCount)setScissorCount(cb,1,&d.scissor);else setScissor(cb,0,1,&d.scissor);
    return true;
}

bool bs4_native_scene_apply_ui_scale(VkCommandBuffer cb,VkExtent2D guest,VkExtent2D output,
                                    bool scaled,VkExtent2D hardware) {
    return scale_ui(cb,guest,output,scaled,hardware,true);
}
bool bs4_native_scene_can_ui_scale(VkCommandBuffer cb,VkExtent2D guest,VkExtent2D output,
                                  VkExtent2D hardware) {
    return scale_ui(cb,guest,output,true,hardware,false);
}

bool bs4_native_scene_writer(VkImageView view,Bs4SceneWriter& out) {
    std::lock_guard lock{guard};const auto it=sceneWriters.find(view);
    if(it==sceneWriters.end())return false;out=it->second;return true;
}
void bs4_native_scene_forget_view(VkImageView view) {
    std::lock_guard lock{guard};sceneWriters.erase(view);
}


bool bs4_native_scene_active_writer(VkCommandBuffer cb,VkImageView view,Bs4SceneWriter& out){
    std::lock_guard lock{guard};const auto state=commands.find(cb);const auto writer=sceneWriters.find(view);
    if(state==commands.end()||writer==sceneWriters.end()||!state->second.inside||
       writer->second.command!=cb||writer->second.frame!=frame||writer->second.renderEpoch!=state->second.renderEpoch)return false;
    out=writer->second;return true;
}
