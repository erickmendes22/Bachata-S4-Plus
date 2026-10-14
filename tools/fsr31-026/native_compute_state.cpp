// SPDX-License-Identifier: GPL-2.0-or-later
// Preserve the native compute bind point across injected AMD compute work.
// SDK calls use Vulkan's direct exports, not the native proc-address wrappers.
#include "native_compute_state.h"
#include <algorithm>
#include <array>
#include <cstring>
#include <map>
#include <mutex>
#include <vector>
namespace {
struct Descriptor {
    VkWriteDescriptorSet write{};
    std::vector<VkDescriptorImageInfo> images;
    std::vector<VkDescriptorBufferInfo> buffers;
    std::vector<VkBufferView> texels;
};
struct Set {
    VkPipelineLayout layout{};
    uint32_t first{};
    std::vector<VkDescriptorSet> sets;
    std::vector<uint32_t> offsets;
    std::vector<Descriptor> pushes;
    uint64_t order{};
};
struct Push {VkPipelineLayout layout{};VkShaderStageFlags stages{};uint32_t offset{},size{};std::array<unsigned char,256> bytes{};};
struct State {
    VkPipeline pipeline{};
    std::map<uint32_t,Set> sets;
    std::vector<Push> pushes;
    uint64_t order{};
    bool valid=true;
};
thread_local unsigned sdkDepth=0;
std::mutex mutex;
std::map<VkCommandBuffer,State> states;
PFN_vkCmdBindPipeline bindPipeline{};
PFN_vkCmdBindDescriptorSets bindSets{};
PFN_vkCmdPushDescriptorSetKHR pushSets{};
PFN_vkCmdPushConstants pushConstants{};
bool copy(Descriptor& d,const VkWriteDescriptorSet& w) {
    if(w.pNext||!w.descriptorCount||w.descriptorCount>256)return false;
    d.write=w;d.write.pNext=nullptr;d.write.pImageInfo=nullptr;d.write.pBufferInfo=nullptr;d.write.pTexelBufferView=nullptr;
    switch(w.descriptorType){
    case VK_DESCRIPTOR_TYPE_SAMPLER:case VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER:
    case VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:case VK_DESCRIPTOR_TYPE_STORAGE_IMAGE:case VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT:
        if(!w.pImageInfo)return false;
        d.images.assign(w.pImageInfo,w.pImageInfo+w.descriptorCount);break;
    case VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER:case VK_DESCRIPTOR_TYPE_STORAGE_BUFFER:
    case VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER_DYNAMIC:case VK_DESCRIPTOR_TYPE_STORAGE_BUFFER_DYNAMIC:
        if(!w.pBufferInfo)return false;
        d.buffers.assign(w.pBufferInfo,w.pBufferInfo+w.descriptorCount);break;
    case VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER:case VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER:
        if(!w.pTexelBufferView)return false;
        d.texels.assign(w.pTexelBufferView,w.pTexelBufferView+w.descriptorCount);break;
    default:return false;
    }
    return true;
}
void VKAPI_CALL pipeline_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipeline pipeline){
    if(!sdkDepth&&point==VK_PIPELINE_BIND_POINT_COMPUTE){std::lock_guard lock{mutex};states[cb].pipeline=pipeline;}
    bindPipeline(cb,point,pipeline);
}
void VKAPI_CALL sets_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
    uint32_t first,uint32_t count,const VkDescriptorSet* sets,uint32_t n,const uint32_t* offsets){
    if(!sdkDepth&&point==VK_PIPELINE_BIND_POINT_COMPUTE){std::lock_guard lock{mutex};auto& s=states[cb];
        if(!sets||!count||first>=32||count>32-first||n>256||(n&&!offsets))s.valid=false;
        else {Set v{};v.layout=layout;v.first=first;v.sets.assign(sets,sets+count);
            if(n)v.offsets.assign(offsets,offsets+n);
            v.order=++s.order;s.sets[first]=std::move(v);}}
    bindSets(cb,point,layout,first,count,sets,n,offsets);
}
void VKAPI_CALL descriptors_hook(VkCommandBuffer cb,VkPipelineBindPoint point,VkPipelineLayout layout,
    uint32_t set,uint32_t count,const VkWriteDescriptorSet* writes){
    if(!sdkDepth&&point==VK_PIPELINE_BIND_POINT_COMPUTE){std::lock_guard lock{mutex};auto& s=states[cb];
        if(!writes||!count||count>256||set>=32)s.valid=false;
        else {auto& target=s.sets[set];
            if(target.layout!=layout||!target.sets.empty())target={};
            target.layout=layout;target.first=set;target.order=++s.order;
            for(uint32_t i=0;i<count;i++){
                Descriptor d{};if(!copy(d,writes[i])){s.valid=false;break;}
                auto it=std::find_if(target.pushes.begin(),target.pushes.end(),[&](const Descriptor& old){
                    return old.write.dstBinding==writes[i].dstBinding&&old.write.dstArrayElement==writes[i].dstArrayElement;});
                if(it!=target.pushes.end())*it=std::move(d);else target.pushes.push_back(std::move(d));
            }
            if(target.pushes.size()>256)s.valid=false;
        }}
    pushSets(cb,point,layout,set,count,writes);
}
void VKAPI_CALL constants_hook(VkCommandBuffer cb,VkPipelineLayout layout,VkShaderStageFlags stage,
    uint32_t offset,uint32_t size,const void* data){
    if(!sdkDepth){std::lock_guard lock{mutex};auto& s=states[cb];
        if(!data||!size||offset>256||size>256-offset||(offset%4)||(size%4))s.valid=false;
        else {
            // Keep original stage masks: layouts using ALL stages cannot be
            // legally restored with COMPUTE alone. Replay remaining writes
            // in their original order, also preserving graphics values after
            // an earlier combined-stage native write.
            s.pushes.erase(std::remove_if(s.pushes.begin(),s.pushes.end(),[&](const Push& old){
                return !(old.stages&~stage)&&offset<=old.offset&&offset+size>=old.offset+old.size;
            }),s.pushes.end());
            if(s.pushes.size()>=128)s.valid=false;
            else {Push value{};value.layout=layout;value.stages=stage;value.offset=offset;value.size=size;
                std::memcpy(value.bytes.data(),data,size);s.pushes.push_back(value);}
        }}
    pushConstants(cb,layout,stage,offset,size,data);
}
}
PFN_vkVoidFunction bs4_native_compute_wrap(const char* name,PFN_vkVoidFunction original){
    if(!name||!original)return original;
#define WRAP(member,symbol,fn) if(!std::strcmp(name,symbol)){if(original!=reinterpret_cast<PFN_vkVoidFunction>(fn))member=reinterpret_cast<decltype(member)>(original);return reinterpret_cast<PFN_vkVoidFunction>(fn);}
    WRAP(bindPipeline,"vkCmdBindPipeline",pipeline_hook)
    WRAP(bindSets,"vkCmdBindDescriptorSets",sets_hook)
    WRAP(pushSets,"vkCmdPushDescriptorSetKHR",descriptors_hook)
    WRAP(pushConstants,"vkCmdPushConstants",constants_hook)
#undef WRAP
    return original;
}
bool bs4_native_compute_can_restore(VkCommandBuffer cb){
    std::lock_guard lock{mutex};const auto it=states.find(cb);
    return it==states.end()||it->second.valid;
}
void bs4_native_compute_restore(VkCommandBuffer cb){
    State snapshot{};{std::lock_guard lock{mutex};const auto it=states.find(cb);
        if(it==states.end()||!it->second.valid)return;
        snapshot=it->second;}
    if(snapshot.pipeline&&bindPipeline)bindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,snapshot.pipeline);
    std::vector<const Set*> ordered;for(auto& p:snapshot.sets)ordered.push_back(&p.second);
    std::sort(ordered.begin(),ordered.end(),[](auto a,auto b){return a->order<b->order;});
    for(const auto* set:ordered){
        if(!set->sets.empty()&&bindSets)bindSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,set->layout,set->first,
            set->sets.size(),set->sets.data(),set->offsets.size(),set->offsets.data());
        else if(!set->pushes.empty()&&pushSets){
            std::vector<VkWriteDescriptorSet> writes;
            for(const auto& d:set->pushes){auto w=d.write;
                w.pImageInfo=d.images.empty()?nullptr:d.images.data();
                w.pBufferInfo=d.buffers.empty()?nullptr:d.buffers.data();
                w.pTexelBufferView=d.texels.empty()?nullptr:d.texels.data();writes.push_back(w);}
            pushSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,set->layout,set->first,writes.size(),writes.data());
        }
    }
    if(pushConstants)for(const auto& value:snapshot.pushes)
        pushConstants(cb,value.layout,value.stages,value.offset,value.size,value.bytes.data());
}
void bs4_native_compute_reset(VkCommandBuffer cb){std::lock_guard lock{mutex};states.erase(cb);}

void bs4_native_compute_enter_sdk(){++sdkDepth;}
void bs4_native_compute_leave_sdk(){if(sdkDepth)--sdkDepth;}

bool bs4_native_compute_in_sdk(){return sdkDepth!=0;}
