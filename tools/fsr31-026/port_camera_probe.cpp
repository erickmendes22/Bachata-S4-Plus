// SPDX-License-Identifier: GPL-2.0-or-later
// Vulkan interception of ACTUAL guest scene constant buffers. No guessing
// from frame timestamps or optical flow. The core024 shadPS4 rasterizer
// binds these uniform descriptors when it compiles/records Bloodborne draws.
#include "port_camera_constants.h"
#include <vulkan/vulkan.h>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <mutex>
#include <unordered_map>
#include <vector>
#include <cmath>
#include <algorithm>
#include <cstdlib>
#include <dlfcn.h>

extern "C" VkImageView bs4_port_ui_redirect_sampled(VkCommandBuffer,VkImageView);
extern "C" int bs4_port_ui_projection_signs(
    VkCommandBuffer,float*,float*);
namespace {
struct Binding {VkDeviceMemory memory=VK_NULL_HANDLE;VkDeviceSize base=0;};
struct Mapping {const uint8_t* addr=nullptr;VkDeviceSize offset=0,length=0;};
struct CameraRecord {
    BachataCamera::Scene camera{};
    VkImageView depth=VK_NULL_HANDLE;
    uint64_t frame=0;
    bool valid=false;
    bool jitterApplied=false;
    float jitterX=0.f,jitterY=0.f;
};
std::mutex guard;
std::unordered_map<VkBuffer,Binding> bound;
std::unordered_map<VkDeviceMemory,Mapping> mapped;
std::unordered_map<VkDescriptorSet,std::vector<VkDescriptorBufferInfo>> sets;
std::unordered_map<VkCommandBuffer,VkImageView> active_depth;
std::unordered_map<VkCommandBuffer,VkExtent2D> active_extent;
std::unordered_map<VkCommandBuffer,CameraRecord> recorded;
std::unordered_map<VkCommandBuffer,std::vector<VkDescriptorBufferInfo>> pending_push;
std::unordered_map<VkCommandBuffer,std::vector<VkDescriptorSet>> bound_sets;
CameraRecord previous_frame{},last_frame_camera{};
uint64_t frame_sequence=1;
std::atomic<int> seen{0};
PFN_vkMapMemory real_map{};
PFN_vkUnmapMemory real_unmap{};
PFN_vkBindBufferMemory real_bind{};
PFN_vkBindBufferMemory2 real_bind2{};
PFN_vkFreeMemory real_free_memory{};
PFN_vkDestroyBuffer real_destroy_buffer{};
PFN_vkCmdPushDescriptorSetKHR real_push_desc{};
PFN_vkCmdBindDescriptorSets real_bind_sets{};
PFN_vkUpdateDescriptorSets real_update_desc{};
PFN_vkCmdDraw real_draw{};
PFN_vkCmdDrawIndexed real_draw_indexed{};
PFN_vkCmdDrawIndirect real_draw_indirect{};
PFN_vkCmdDrawIndexedIndirect real_draw_indexed_indirect{};
using DlsymFn=void*(*)(void*,const char*);
inline bool from_descriptor(const VkDescriptorBufferInfo& info,
                            BachataCamera::Scene& camera) {
    auto buf=bound.find(info.buffer);
    if(buf==bound.end())return false;
    auto memory=mapped.find(buf->second.memory);
    if(memory==mapped.end() || !memory->second.addr)return false;
    const Mapping& m=memory->second;
    if(info.range!=VK_WHOLE_SIZE && info.range<864)return false;
    if(buf->second.base>UINT64_MAX-info.offset)return false;
    const VkDeviceSize position=buf->second.base+info.offset;
    if(position<m.offset || position-m.offset>m.length ||
       m.length-(position-m.offset)<864)return false;
    return BachataCamera::Parse(m.addr+(position-m.offset),864,camera);
}
void inspect_buffer(VkCommandBuffer cb,const VkDescriptorBufferInfo& info) {
    // Caller holds guard. The Vulkan mapped range remains owned by the game.
    BachataCamera::Scene c{};
    if(!from_descriptor(info,c))return;
    const auto d=active_depth.find(cb);
    const auto e=active_extent.find(cb);
    if(d==active_depth.end() || e==active_extent.end() ||
       !d->second || c.width!=e->second.width ||
       c.height!=e->second.height)return;
    float viewportX=0,viewportY=0;
    // The port's CameraMotion::OnGBufferPass applies these signs to
    // projection x/y before reconstructing motion from guest depth.
    if(!bs4_port_ui_projection_signs(cb,&viewportX,&viewportY))
        return;
    c.projection[0]*=viewportX;
    c.projection[1]*=viewportY;
    CameraRecord rec{};
    rec.camera=c;rec.depth=d->second;rec.frame=frame_sequence;rec.valid=true;
    recorded[cb]=rec;
    last_frame_camera=rec;
    if(seen.fetch_add(1)==0)
        std::fprintf(stderr,
            "[BS4_PORT] actual guest camera constants found in Vulkan "
            "uniform descriptor, scene=%ux%u depth_bound=1\n",c.width,c.height);
}
void inspect_writes(VkCommandBuffer cb,uint32_t count,
                    const VkWriteDescriptorSet* writes) {
    if(!writes)return;
    for(uint32_t i=0;i<count;i++){
        const auto& w=writes[i];
        if(w.descriptorType!=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER &&
           w.descriptorType!=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER &&
           w.descriptorType!=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC)
            continue;
        if(!w.pBufferInfo)continue;
        for(uint32_t j=0;j<w.descriptorCount;j++)
            inspect_buffer(cb,w.pBufferInfo[j]);
    }
}
} // namespace

extern "C" void bs4_port_note_render(VkCommandBuffer cb,
                    VkImageView depth,VkExtent2D size,
                    uint32_t attachment_count) {
    if(!cb || !size.width || !size.height)return;
    std::lock_guard lock{guard};
    if(depth && attachment_count>=2 && size.width<=1280 &&
       size.height<=720) {
        active_depth[cb]=depth;active_extent[cb]=size;
    }
}
extern "C" VkImageView bs4_port_camera_for_scene(VkCommandBuffer cb,
                      VkExtent2D size,void* out_push,uint32_t capacity) {
    if(!cb || !out_push || capacity!=sizeof(BachataCamera::Push))
        return VK_NULL_HANDLE;
    std::lock_guard lock{guard};
    const auto it=recorded.find(cb);
    // Scheduler flushes can split one displayed frame across command buffers.
    // The handoff is tied to the frame and verified depth, not the CB address.
    const CameraRecord* current=it==recorded.end()?&last_frame_camera:&it->second;
    if(!current->valid || current->frame!=frame_sequence ||
       !previous_frame.valid ||
       previous_frame.frame+1!=current->frame ||
       current->camera.width!=size.width ||
       current->camera.height!=size.height ||
       previous_frame.camera.width!=size.width ||
       previous_frame.camera.height!=size.height)
       return VK_NULL_HANDLE;
    const auto push=BachataCamera::MakePush(
        current->camera,previous_frame.camera,
        current->jitterApplied?current->jitterX:0.f,
        current->jitterApplied?current->jitterY:0.f,
        previous_frame.jitterApplied?previous_frame.jitterX:0.f,
        previous_frame.jitterApplied?previous_frame.jitterY:0.f);
    std::memcpy(out_push,&push,sizeof(push));
    return current->depth;
}
extern "C" VkImageView bs4_port_current_scene(VkCommandBuffer cb,VkExtent2D* size){
    if(!cb||!size)return VK_NULL_HANDLE;
    std::lock_guard lock{guard};
    const auto it=recorded.find(cb);
    const CameraRecord& c=it==recorded.end()?last_frame_camera:it->second;
    if(!c.valid||c.frame!=frame_sequence)return VK_NULL_HANDLE;
    *size={c.camera.width,c.camera.height};return c.depth;
}
extern "C" int bs4_port_camera_range(VkCommandBuffer cb,float* near,float* far){
    if(!cb||!near||!far)return 0;
    std::lock_guard lock{guard};const auto it=recorded.find(cb);
    const auto& c=it==recorded.end()?last_frame_camera:it->second;
    if(!c.valid||c.frame!=frame_sequence)return 0;
    *near=c.camera.nearPlane;*far=c.camera.farPlane;return 1;
}
extern "C" uint64_t bs4_port_frame_generation(){
    std::lock_guard lock{guard};return frame_sequence;
}
extern "C" void bs4_port_on_present() {
    std::lock_guard lock{guard};
    if(last_frame_camera.valid && last_frame_camera.frame==frame_sequence)
        previous_frame=last_frame_camera;
    ++frame_sequence;
    recorded.clear();pending_push.clear();bound_sets.clear();
    active_depth.clear();
    active_extent.clear();
}
extern "C" void bs4_port_reset_cb(VkCommandBuffer cb) {
    std::lock_guard lock{guard};
    recorded.erase(cb);active_depth.erase(cb);active_extent.erase(cb);
    pending_push.erase(cb);bound_sets.erase(cb);
}
static float Halton(unsigned n,unsigned base);
extern "C" int bs4_port_jitter_for_pass(VkExtent2D size,float* x,float* y) {
    if(!x || !y || !size.width || !size.height)return 0;
    const char* mode=std::getenv("BACHATA_FSR31_MODE");
    if(!mode || mode[0]<'0'||mode[0]>'4'||mode[1]!=0)return 0;
    std::lock_guard lock{guard};
    // A real guest camera from the previous displayed Bloodborne frame
    // identifies the renderer. Do not shift random Vulkan applications.
    if(!previous_frame.valid ||
       previous_frame.camera.width!=size.width ||
       previous_frame.camera.height!=size.height ||
       previous_frame.frame+1!=frame_sequence)return 0;
    const double ratio=1280.0/double(size.width);
    const unsigned phases=unsigned(std::clamp(
        std::ceil(8.0*ratio*ratio),8.0,256.0));
    const unsigned phase=unsigned((frame_sequence-1)%phases)+1;
    *x=Halton(phase,2)-0.5f;*y=Halton(phase,3)-0.5f;
    return 1;
}

extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_port_map(
    VkDevice d,VkDeviceMemory mem,VkDeviceSize off,VkDeviceSize len,
    VkMemoryMapFlags flags,void** ptr){
    if(!real_map)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult r=real_map(d,mem,off,len,flags,ptr);
    if(r==VK_SUCCESS && ptr && *ptr){
        std::lock_guard lock{guard};
        mapped[mem]={static_cast<const uint8_t*>(*ptr),off,len};
    }
    return r;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_unmap(
    VkDevice d,VkDeviceMemory mem){
    {std::lock_guard lock{guard};mapped.erase(mem);}
    if(real_unmap)real_unmap(d,mem);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_free_memory(
    VkDevice d,VkDeviceMemory mem,const VkAllocationCallbacks* ac){
    {std::lock_guard lock{guard};mapped.erase(mem);}
    if(real_free_memory)real_free_memory(d,mem,ac);
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_port_bind(
    VkDevice d,VkBuffer buffer,VkDeviceMemory mem,VkDeviceSize off){
    if(!real_bind)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult r=real_bind(d,buffer,mem,off);
    if(r==VK_SUCCESS){std::lock_guard lock{guard};bound[buffer]={mem,off};}
    return r;
}
extern "C" VKAPI_ATTR VkResult VKAPI_CALL bs4_port_bind2(
    VkDevice d,uint32_t count,const VkBindBufferMemoryInfo* infos) {
    if(!real_bind2)return VK_ERROR_INITIALIZATION_FAILED;
    const VkResult r=real_bind2(d,count,infos);
    if(r==VK_SUCCESS && infos){
        std::lock_guard lock{guard};
        for(uint32_t i=0;i<count;i++)
            bound[infos[i].buffer]={infos[i].memory,infos[i].memoryOffset};
    }
    return r;
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_destroy_buffer(
    VkDevice d,VkBuffer buf,const VkAllocationCallbacks* ac){
    {std::lock_guard lock{guard};bound.erase(buf);}
    if(real_destroy_buffer)real_destroy_buffer(d,buf,ac);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_push_desc(
    VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
    uint32_t set,uint32_t count,const VkWriteDescriptorSet* writes) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS) {
        std::lock_guard lock{guard};
        inspect_writes(cb,count,writes);
        auto& samples=pending_push[cb];
        samples.clear();
        for(uint32_t i=0;i<count;i++) {
            const auto& w=writes[i];
            if((w.descriptorType!=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER &&
                w.descriptorType!=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER) ||
               !w.pBufferInfo)continue;
            for(uint32_t j=0;j<w.descriptorCount;j++)
                samples.push_back(w.pBufferInfo[j]);
        }
    }
    if(real_push_desc) {
        std::vector<VkWriteDescriptorSet> patched;
        std::vector<std::vector<VkDescriptorImageInfo>> owned;
        bool changed=false;
        if(point==VK_PIPELINE_BIND_POINT_GRAPHICS && writes && count){
            patched.assign(writes,writes+count);
            owned.resize(count);
            for(uint32_t i=0;i<count;++i){
                auto& w=patched[i];
                if((w.descriptorType!=VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER &&
                    w.descriptorType!=VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE) ||
                   !w.pImageInfo || !w.descriptorCount)continue;
                owned[i].assign(w.pImageInfo,w.pImageInfo+w.descriptorCount);
                for(auto& info:owned[i]){
                    if(const VkImageView ui=bs4_port_ui_redirect_sampled(
                        cb,info.imageView);ui){
                        info.imageView=ui;
                        info.imageLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
                        changed=true;
                    }
                }
                w.pImageInfo=owned[i].data();
            }
        }
        real_push_desc(cb,point,layout,set,count,
                       changed?patched.data():writes);
    }
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_update_desc(
    VkDevice dev,uint32_t count,const VkWriteDescriptorSet* writes,
    uint32_t copies,const VkCopyDescriptorSet* copy) {
    if(writes){
        std::lock_guard lock{guard};
        for(uint32_t i=0;i<count;i++) {
            const auto& w=writes[i];
            if((w.descriptorType!=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER &&
                w.descriptorType!=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER) ||
               !w.pBufferInfo)continue;
            auto& dest=sets[w.dstSet];
            // Descriptor updates are often executed before a frame's data is
            // written; defer scene parsing to vkCmdBindDescriptorSets.
            if(dest.size()<w.dstBinding+w.descriptorCount)
                dest.resize(w.dstBinding+w.descriptorCount);
            for(uint32_t j=0;j<w.descriptorCount;j++)
                dest[w.dstBinding+j]=w.pBufferInfo[j];
        }
    }
    if(real_update_desc)real_update_desc(dev,count,writes,copies,copy);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_bind_sets(
    VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
    uint32_t first,uint32_t count,const VkDescriptorSet* descriptor_sets,
    uint32_t dynamic_count,const uint32_t* offsets) {
    if(point==VK_PIPELINE_BIND_POINT_GRAPHICS && descriptor_sets){
        std::lock_guard lock{guard};
        auto& active=bound_sets[cb];
        active.assign(descriptor_sets,descriptor_sets+count);
        for(uint32_t i=0;i<count;i++) {
            auto set=sets.find(descriptor_sets[i]);
            if(set==sets.end())continue;
            for(auto& info:set->second)if(info.buffer)inspect_buffer(cb,info);
        }
    }
    if(real_bind_sets)real_bind_sets(cb,point,layout,first,count,
                                   descriptor_sets,dynamic_count,offsets);
}
// Descriptor recording and scene beginning can have different order.
// Inspect again at the actual G-buffer draw, after both are known.
extern "C" bool bs4_port_ui_try_activate(VkCommandBuffer);
extern "C" void bs4_port_ui_note_draw(VkCommandBuffer);

extern "C" int bs4_port_ui_apply_camera_jitter(VkCommandBuffer,float,float);
static float Halton(unsigned n,unsigned base){
    float f=1.0f,r=0.0f;
    while(n){f/=float(base);r+=f*float(n%base);n/=base;}
    return r;
}
extern "C" int bs4_fsr31_attachment_ready();
extern "C" int bs4_fsr31_camera_resources_ready(VkExtent2D);
void bs4_port_scan_at_draw(VkCommandBuffer cb) {
    if(!bs4_fsr31_attachment_ready())return;
    bool valid=false,alreadyJittered=false;
    uint32_t width=0,height=0;
    uint64_t generation=0;
    {
        std::lock_guard lock{guard};
        auto existing=recorded.find(cb);
        if(existing==recorded.end() || existing->second.frame!=frame_sequence){
            auto p=pending_push.find(cb);
            if(p!=pending_push.end())
                for(const auto& b:p->second)inspect_buffer(cb,b);
            auto bound_it=bound_sets.find(cb);
            if(bound_it!=bound_sets.end())
                for(const auto& set_id:bound_it->second){
                    auto set=sets.find(set_id);
                    if(set==sets.end())continue;
                    for(const auto& b:set->second)
                        if(b.buffer)inspect_buffer(cb,b);
                }
            existing=recorded.find(cb);
        }
        if(existing!=recorded.end() && existing->second.valid &&
           existing->second.frame==frame_sequence){
            valid=true;
            width=existing->second.camera.width;
            height=existing->second.camera.height;
            alreadyJittered=existing->second.jitterApplied;
            generation=frame_sequence;
        }
    }
    if(!valid || alreadyJittered || !width ||
       !bs4_fsr31_camera_resources_ready({width,height}))return;
    const char* mode=std::getenv("BACHATA_FSR31_MODE");
    if(!mode || mode[0]<'0'||mode[0]>'4'||mode[1]!=0)return;
    const double ratio=1280.0/double(width);
    const unsigned phases=unsigned(std::clamp(
        std::ceil(8.0*ratio*ratio),8.0,256.0));
    const unsigned phase=unsigned((generation-1)%phases)+1;
    const float x=Halton(phase,2)-0.5f;
    const float y=Halton(phase,3)-0.5f;
    if(bs4_port_ui_apply_camera_jitter(cb,x,y)) {
        std::lock_guard lock{guard};
        auto it=recorded.find(cb);
        if(it!=recorded.end() && it->second.frame==generation){
            it->second.jitterApplied=true;
            it->second.jitterX=x;it->second.jitterY=y;
            if(last_frame_camera.valid && last_frame_camera.frame==generation) {
                last_frame_camera.jitterApplied=true;
                last_frame_camera.jitterX=x;last_frame_camera.jitterY=y;
            }
        }
    }
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_draw(
    VkCommandBuffer cb,uint32_t v,uint32_t n,uint32_t first,uint32_t instance) {
    bs4_port_scan_at_draw(cb);
    bs4_port_ui_note_draw(cb);
    bs4_port_ui_try_activate(cb);
    if(real_draw)real_draw(cb,v,n,first,instance);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_draw_indexed(
    VkCommandBuffer cb,uint32_t v,uint32_t n,uint32_t first,
    int32_t base,uint32_t instance) {
    bs4_port_scan_at_draw(cb);
    bs4_port_ui_note_draw(cb);
    bs4_port_ui_try_activate(cb);
    if(real_draw_indexed)real_draw_indexed(cb,v,n,first,base,instance);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_draw_indirect(
    VkCommandBuffer cb,VkBuffer buf,VkDeviceSize offset,uint32_t n,uint32_t stride) {
    bs4_port_scan_at_draw(cb);
    bs4_port_ui_note_draw(cb);
    bs4_port_ui_try_activate(cb);
    if(real_draw_indirect)real_draw_indirect(cb,buf,offset,n,stride);
}
extern "C" VKAPI_ATTR void VKAPI_CALL bs4_port_draw_indexed_indirect(
    VkCommandBuffer cb,VkBuffer buf,VkDeviceSize offset,uint32_t n,uint32_t stride) {
    bs4_port_scan_at_draw(cb);
    bs4_port_ui_note_draw(cb);
    bs4_port_ui_try_activate(cb);
    if(real_draw_indexed_indirect)real_draw_indexed_indirect(cb,buf,offset,n,stride);
}
extern "C" PFN_vkVoidFunction bs4_port_wrap_proc(
                  const char* name,PFN_vkVoidFunction proc) {
    if(!name || !proc)return proc;
#define PORT_WRAP(original,api,fn) \
    if(!std::strcmp(name,api)){original=reinterpret_cast<decltype(original)>(proc); \
       return reinterpret_cast<PFN_vkVoidFunction>(fn);}
    PORT_WRAP(real_map,"vkMapMemory",bs4_port_map)
    PORT_WRAP(real_unmap,"vkUnmapMemory",bs4_port_unmap)
    PORT_WRAP(real_bind,"vkBindBufferMemory",bs4_port_bind)
    PORT_WRAP(real_bind2,"vkBindBufferMemory2",bs4_port_bind2)
    PORT_WRAP(real_free_memory,"vkFreeMemory",bs4_port_free_memory)
    PORT_WRAP(real_destroy_buffer,"vkDestroyBuffer",bs4_port_destroy_buffer)
    PORT_WRAP(real_push_desc,"vkCmdPushDescriptorSetKHR",bs4_port_push_desc)
    PORT_WRAP(real_update_desc,"vkUpdateDescriptorSets",bs4_port_update_desc)
    PORT_WRAP(real_bind_sets,"vkCmdBindDescriptorSets",bs4_port_bind_sets)
    PORT_WRAP(real_draw,"vkCmdDraw",bs4_port_draw)
    PORT_WRAP(real_draw_indexed,"vkCmdDrawIndexed",bs4_port_draw_indexed)
    PORT_WRAP(real_draw_indirect,"vkCmdDrawIndirect",bs4_port_draw_indirect)
    PORT_WRAP(real_draw_indexed_indirect,"vkCmdDrawIndexedIndirect",bs4_port_draw_indexed_indirect)
#undef PORT_WRAP
    return proc;
}
