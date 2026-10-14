// SPDX-License-Identifier: GPL-2.0-or-later
#include "../native_compute_state.h"
#include <cassert>
#include <cstring>
#include <cstdio>
#include <vector>
template<class T>T h(uintptr_t x){return reinterpret_cast<T>(x);}
template<class T>T wrap(const char* name,T original){return reinterpret_cast<T>(bs4_native_compute_wrap(name,reinterpret_cast<PFN_vkVoidFunction>(original)));}
VkPipeline actual{};VkDescriptorSet set{};VkImageView image{};VkBuffer buffer{};uint32_t dynamic{},values[8]{};
void VKAPI_CALL pipeline(VkCommandBuffer,VkPipelineBindPoint,VkPipeline p){actual=p;}
void VKAPI_CALL sets(VkCommandBuffer,VkPipelineBindPoint,VkPipelineLayout,uint32_t,uint32_t count,const VkDescriptorSet* s,uint32_t n,const uint32_t* offsets){assert(count==1);set=*s;if(n)dynamic=*offsets;}
void VKAPI_CALL push(VkCommandBuffer,VkPipelineBindPoint,VkPipelineLayout,uint32_t,uint32_t count,const VkWriteDescriptorSet* w){
 for(uint32_t i=0;i<count;i++){if(w[i].pImageInfo)image=w[i].pImageInfo[0].imageView;if(w[i].pBufferInfo)buffer=w[i].pBufferInfo[0].buffer;}}
void VKAPI_CALL constants(VkCommandBuffer,VkPipelineLayout,VkShaderStageFlags,uint32_t offset,uint32_t size,const void* data){std::memcpy(reinterpret_cast<unsigned char*>(values)+offset,data,size);}
int main(){
 auto p=wrap("vkCmdBindPipeline",&pipeline);auto s=wrap("vkCmdBindDescriptorSets",&sets);auto d=wrap("vkCmdPushDescriptorSetKHR",&push);auto c=wrap("vkCmdPushConstants",&constants);
 const auto cb=h<VkCommandBuffer>(1);const auto layout=h<VkPipelineLayout>(2);auto native=h<VkPipeline>(3);auto nativeSet=h<VkDescriptorSet>(4);uint32_t offset=16;
 p(cb,VK_PIPELINE_BIND_POINT_COMPUTE,native);s(cb,VK_PIPELINE_BIND_POINT_COMPUTE,layout,0,1,&nativeSet,1,&offset);
 VkDescriptorImageInfo ii{};ii.imageView=h<VkImageView>(5);VkDescriptorBufferInfo bi{h<VkBuffer>(6),24,64};
 VkWriteDescriptorSet w[2]{};for(auto& v:w){v.sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;v.descriptorCount=1;}
 w[0].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;w[0].pImageInfo=&ii;w[1].dstBinding=1;w[1].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;w[1].pBufferInfo=&bi;
 d(cb,VK_PIPELINE_BIND_POINT_COMPUTE,layout,1,2,w);uint32_t words[8]{1,2,3,4,5,6,7,8};c(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,32,words);uint32_t partial=55;c(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,12,4,&partial);
 // Mutate the caller's temporary descriptors and pushes, then simulate SDK
 // direct Vulkan calls bypassing native wrappers and cached rebinds.
 ii.imageView={};bi.buffer={};std::memset(words,0,sizeof(words));actual={};set={};image={};buffer={};dynamic=0;std::memset(values,0,sizeof(values));
 assert(bs4_native_compute_can_restore(cb));
 bs4_native_compute_enter_sdk();p(cb,VK_PIPELINE_BIND_POINT_COMPUTE,h<VkPipeline>(99));
 uint32_t sdkWords[8]{};c(cb,layout,VK_SHADER_STAGE_COMPUTE_BIT,0,32,sdkWords);
 bs4_native_compute_restore(cb);bs4_native_compute_leave_sdk();
 assert(actual==native&&set==nativeSet&&image==h<VkImageView>(5)&&buffer==h<VkBuffer>(6)&&dynamic==16);
 for(unsigned i=0;i<8;i++)assert(values[i]==(i==3?55:i+1));
 bs4_native_compute_reset(cb);actual={};bs4_native_compute_restore(cb);assert(!actual);
 w[0].pNext=&w[1];d(cb,VK_PIPELINE_BIND_POINT_COMPUTE,layout,0,1,w);assert(!bs4_native_compute_can_restore(cb));
 bs4_native_compute_reset(cb);assert(bs4_native_compute_can_restore(cb));
 puts("PASS compute restoration: pipeline, descriptor sets/dynamic offsets, deep-copied push descriptors, partial push constants and reset isolation");
}
