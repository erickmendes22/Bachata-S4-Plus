#include "../temporal_lifetime.h"
#include <cassert>
#include <unordered_map>
#include <cstdio>
static std::unordered_map<VkFence,bool> done;
static uintptr_t nextFence=100;
static unsigned waits=0,submissions=0;
extern "C" VkResult vkCreateFence(VkDevice,const VkFenceCreateInfo*,const VkAllocationCallbacks*,VkFence* out){*out=reinterpret_cast<VkFence>(nextFence++);done[*out]=false;return VK_SUCCESS;}
extern "C" void vkDestroyFence(VkDevice,VkFence f,const VkAllocationCallbacks*){done.erase(f);}
extern "C" VkResult vkWaitForFences(VkDevice,uint32_t n,const VkFence* f,VkBool32,uint64_t){assert(n==1);waits++;return done[*f]?VK_SUCCESS:VK_TIMEOUT;}
extern "C" VkResult vkResetFences(VkDevice,uint32_t n,const VkFence* f){assert(n==1);done[*f]=false;return VK_SUCCESS;}
static VkResult submit(VkQueue,uint32_t n,const VkSubmitInfo* info,VkFence f){assert(!n&&!info&&f);submissions++;return VK_SUCCESS;}
static VkResult submit2(VkQueue,uint32_t n,const VkSubmitInfo2* info,VkFence f){assert(!n&&!info&&f);submissions++;return VK_SUCCESS;}
int main(){auto device=reinterpret_cast<VkDevice>(1);auto queue=reinterpret_cast<VkQueue>(2);auto cb=reinterpret_cast<VkCommandBuffer>(3);auto other=reinterpret_cast<VkCommandBuffer>(4);
 for(size_t i=0;i<4;i++)assert(bs4_temporal_acquire(i,device,cb));
 assert(!bs4_temporal_acquire(0,device,other)&&waits==0);
 bs4_temporal_submitted(queue,other,submit,nullptr);assert(submissions==0);
 bs4_temporal_submitted(queue,cb,submit,nullptr);assert(submissions==4);
 bs4_temporal_submitted(queue,cb,submit,nullptr);assert(submissions==4);
 assert(!bs4_temporal_acquire(0,device,other)&&waits==1);
 for(auto& entry:done)entry.second=true;
 assert(bs4_temporal_acquire(0,device,other));
 bs4_temporal_submitted(queue,other,nullptr,submit2);assert(submissions==5);
 bs4_temporal_discard(cb);assert(!bs4_temporal_abandoned());
 assert(bs4_temporal_acquire(1,device,other));bs4_temporal_discard(other);assert(bs4_temporal_abandoned());
 bs4_temporal_reset_after_drain();assert(done.empty()&&!bs4_temporal_abandoned());
 std::puts("PASS recorded/pending/completed slot lifecycle; Submit1/Submit2; discarded CB recovery");}
