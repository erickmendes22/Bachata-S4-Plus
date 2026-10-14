// SPDX-License-Identifier: GPL-2.0-or-later
#include "../native_scene_observer.h"
#include "../port_scene_frame.h"
#include <array>
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
template<class T>T handle(uintptr_t n){return reinterpret_cast<T>(n);}
template<class T>T wrap(const char* name,T original){return reinterpret_cast<T>(bs4_native_scene_wrap(name,reinterpret_cast<PFN_vkVoidFunction>(original)));}
std::array<unsigned char,2048> memory{};
int forwarded=0,viewportCalls=0,viewportCountCalls=0;
VkViewport actualViewport{};
bool resourcesReady=true;
extern "C" bool bs4_fsr31_temporal_resources_ready(VkExtent2D){return resourcesReady;}
VkResult VKAPI_CALL allocate(VkDevice,const VkMemoryAllocateInfo*,const VkAllocationCallbacks*,VkDeviceMemory* out){*out=handle<VkDeviceMemory>(1);return VK_SUCCESS;}
VkResult VKAPI_CALL map(VkDevice,VkDeviceMemory,VkDeviceSize offset,VkDeviceSize,VkMemoryMapFlags,void** out){*out=memory.data()+offset;return VK_SUCCESS;}
void VKAPI_CALL unmap(VkDevice,VkDeviceMemory){}
VkResult VKAPI_CALL bind(VkDevice,VkBuffer,VkDeviceMemory,VkDeviceSize){return VK_SUCCESS;}
void VKAPI_CALL push(VkCommandBuffer,VkPipelineBindPoint,VkPipelineLayout,uint32_t,uint32_t count,const VkWriteDescriptorSet* w){assert(count==1&&w&&w->pBufferInfo);}
void VKAPI_CALL constants(VkCommandBuffer,VkPipelineLayout,VkShaderStageFlags,uint32_t offset,uint32_t size,const void*){assert(offset==0&&size==120);}
void VKAPI_CALL viewport(VkCommandBuffer,uint32_t first,uint32_t count,const VkViewport* value){assert(first==0&&count==1);actualViewport=*value;viewportCalls++;}
void VKAPI_CALL viewport_count(VkCommandBuffer,uint32_t count,const VkViewport* value){assert(count==1);actualViewport=*value;viewportCountCalls++;}
VkResult VKAPI_CALL name(VkDevice,const VkDebugUtilsObjectNameInfoEXT*){return VK_SUCCESS;}
void VKAPI_CALL destroy_layout(VkDevice,VkPipelineLayout,const VkAllocationCallbacks*){}
void VKAPI_CALL draw(VkCommandBuffer,uint32_t n,uint32_t i,uint32_t first,uint32_t base){assert(n==30&&i==1&&first==0&&base==0);forwarded++;}
void VKAPI_CALL indirect(VkCommandBuffer,VkBuffer,VkDeviceSize off,uint32_t count,uint32_t stride){
 assert(off==32&&count==2&&stride==20);assert(actualViewport.x!=0);forwarded++;
}
int main(){
 setenv("BACHATA_FSR31_INPUT","port",1);
 auto a=wrap("vkAllocateMemory",&allocate);auto m=wrap("vkMapMemory",&map);
 auto b=wrap("vkBindBufferMemory",&bind);auto p=wrap("vkCmdPushDescriptorSetKHR",&push);
 auto c=wrap("vkCmdPushConstants",&constants);auto v=wrap("vkCmdSetViewport",&viewport);
 auto indirectDraw=wrap("vkCmdDrawIndirect",&indirect);auto indirectIndexed=wrap("vkCmdDrawIndexedIndirect",&indirect);
 auto d=wrap("vkCmdDraw",&draw);auto u=wrap("vkUnmapMemory",&unmap);
 auto vc=wrap("vkCmdSetViewportWithCountEXT",&viewport_count);
 auto named=wrap("vkSetDebugUtilsObjectNameEXT",&name);auto destroyed=wrap("vkDestroyPipelineLayout",&destroy_layout);
 VkDeviceMemory mem{};VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ai.allocationSize=memory.size();assert(a({},&ai,nullptr,&mem)==VK_SUCCESS);
 void* ptr{};assert(m({},mem,32,VK_WHOLE_SIZE,0,&ptr)==VK_SUCCESS);
 auto buffer=handle<VkBuffer>(2);assert(b({},buffer,mem,64)==VK_SUCCESS);
 auto cb=handle<VkCommandBuffer>(3);auto depth=handle<VkImageView>(4);
 std::array<float,216> camera{};camera[0]=3000;camera[1]=1.f/3000;camera[4]=640;camera[5]=360;
 for(int i=0;i<3;i++)camera[8+i*5]=camera[180+i*5]=1;
 camera[52]=2;camera[57]=3;camera[62]=1.0001f;camera[63]=-.1f;
 std::memcpy(memory.data()+80,camera.data(),sizeof(camera));
 VkDescriptorBufferInfo bufferInfo{buffer,16,864};
 VkWriteDescriptorSet write{VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};write.dstBinding=0;write.descriptorCount=1;write.descriptorType=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;write.pBufferInfo=&bufferInfo;
 VkRenderingAttachmentInfo dep{VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};dep.imageView=depth;
 VkRenderingInfo info{VK_STRUCTURE_TYPE_RENDERING_INFO};info.renderArea.extent={640,360};info.colorAttachmentCount=5;info.pDepthAttachment=&dep;
 std::array<float,30> raw{};raw[0]=320;raw[1]=180;raw[2]=320;raw[3]=-180;
 VkViewport vp{0,360,640,-360,0,1};
 auto setup=[&](){bs4_native_scene_reset(cb);p(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,{},0,1,&write);c(cb,{},VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());v(cb,0,1,&vp);bs4_native_scene_begin(cb,&info);};
 VkImageView found{};VkExtent2D size{};Bs4PortCameraDispatch out{};
 setup();d(cb,30,1,0,0);assert(bs4_native_scene_camera(cb,&found,&size));assert(found==depth&&size.width==640&&size.height==360);
 assert(!bs4_fsr31_port_camera(cb,depth,size,out));
 // The native 3D camera belongs to the whole command buffer/frame.
 // A later single-color LDR pass can omit the G-buffer depth attachment.
 bs4_native_scene_end(cb);
 VkRenderingInfo ldr=info;ldr.colorAttachmentCount=1;ldr.pDepthAttachment=nullptr;
 bs4_native_scene_begin(cb,&ldr);
 assert(bs4_native_scene_camera(cb,&found,&size)&&found==depth&&size.width==640);
 bs4_native_scene_end(cb);bs4_native_scene_present();bs4_fsr31_port_end_frame();
 assert(!bs4_native_scene_camera(cb,&found,&size));
 setup();d(cb,30,1,0,0);assert(bs4_fsr31_port_camera(cb,depth,{640,360},out));
 assert(!out.reset&&out.motion.proj[1]==-3&&out.motion.jitter[0]==-.25f);
 assert(std::abs(out.motion.jitter[1]-1.f/6.f)<1e-6f);
 assert(actualViewport.x==vp.x&&actualViewport.y==vp.y&&viewportCalls==4);
 bs4_native_scene_present();bs4_fsr31_port_end_frame();
 setup();vc(cb,1,&vp);const auto oldCalls=viewportCalls;d(cb,30,1,0,0);
 assert(bs4_fsr31_port_camera(cb,depth,{640,360},out)&&out.motion.jitter[0]==.25f);
 assert(viewportCountCalls==3&&viewportCalls==oldCalls&&actualViewport.x==vp.x&&actualViewport.y==vp.y);
 // Indirect G-buffer draws receive exactly the same phase, and the original
 // viewport is restored after each call (including WithCount state).
 indirectDraw(cb,buffer,32,2,20);assert(actualViewport.x==vp.x&&actualViewport.y==vp.y);
 indirectIndexed(cb,buffer,32,2,20);assert(actualViewport.x==vp.x&&actualViewport.y==vp.y);
 resourcesReady=false;setup();const auto noJitterCalls=viewportCalls;d(cb,30,1,0,0);
 assert(viewportCalls==noJitterCalls&&actualViewport.x==vp.x&&actualViewport.y==vp.y);
 resourcesReady=true;
 std::array<unsigned char,2048> original=memory;
 // Native viewport field interpretation is validated against the actual
 // recorded viewport, rather than accepting a sign guessed from its size.
 bs4_native_scene_present();bs4_fsr31_port_end_frame();raw[3]=180;setup();d(cb,30,1,0,0);assert(!bs4_native_scene_camera(cb,&found,&size));raw[3]=-180;
 // Uniform range arithmetic must reject overflow and partial mapped ranges.
 bufferInfo.offset=std::numeric_limits<VkDeviceSize>::max();setup();d(cb,30,1,0,0);assert(!bs4_native_scene_camera(cb,&found,&size));bufferInfo.offset=16;
 bufferInfo.range=863;setup();d(cb,30,1,0,0);assert(!bs4_native_scene_camera(cb,&found,&size));bufferInfo.range=864;
 info.colorAttachmentCount=4;setup();d(cb,30,1,0,0);assert(!bs4_native_scene_camera(cb,&found,&size));info.colorAttachmentCount=5;
 u({},mem);setup();d(cb,30,1,0,0);assert(!bs4_native_scene_camera(cb,&found,&size));
 assert(memory==original&&forwarded==11); // no guest memory writes; every draw forwarded
 auto layout=handle<VkPipelineLayout>(9);
 Bs4NativeRenderState native{};native.width=640;native.height=360;native.layers=1;
 native.colorCount=1;native.colors[0].view=11;
 Bs4NativeUiBoundary boundary{};
 bs4_native_scene_draw_state(cb,native);assert(!bs4_native_scene_ui_state(cb,boundary));
 VkDebugUtilsObjectNameInfoEXT ni{VK_STRUCTURE_TYPE_DEBUG_UTILS_OBJECT_NAME_INFO_EXT};ni.objectType=VK_OBJECT_TYPE_PIPELINE_LAYOUT;ni.objectHandle=9;
 ni.pObjectName="Graphics PipelineLayout fs_0x0000000012345678,vs_0x0000000034e8a281";assert(named({},&ni)==VK_SUCCESS);
 c(cb,layout,VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());assert(bs4_native_scene_ui_boundary(cb));
 ni.pObjectName="Graphics PipelineLayout fs_0x0000000034e8a281,vs_0x00000000abcdabcd";assert(named({},&ni)==VK_SUCCESS);assert(!bs4_native_scene_ui_boundary(cb));
 ni.pObjectName="Graphics PipelineLayout vs_0x0000000034e8a281";assert(named({},&ni)==VK_SUCCESS);assert(bs4_native_scene_ui_boundary(cb));
 bs4_native_scene_draw_state(cb,native);assert(bs4_native_scene_ui_state(cb,boundary));
 assert(boundary.color==handle<VkImageView>(11)&&boundary.guestExtent.width==640&&boundary.rawViewport[3]==-180);
 native.colors[0].view=12;bs4_native_scene_draw_state(cb,native);
 assert(bs4_native_scene_ui_state(cb,boundary)&&boundary.color==handle<VkImageView>(12)); // most recent UI draw must own its target
 bs4_native_scene_reset(cb);assert(!bs4_native_scene_ui_state(cb,boundary));
 c(cb,layout,VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());
 native.colorCount=0;native.stencilEnabled=1;native.depth=13;
 bs4_native_scene_draw_state(cb,native);assert(bs4_native_scene_ui_state(cb,boundary));
 assert(!boundary.color&&boundary.depth==handle<VkImageView>(13)); // first Scaleform mask pass
 destroyed({},layout,nullptr);assert(!bs4_native_scene_ui_boundary(cb));
 bs4_native_scene_present();assert(!bs4_native_scene_ui_state(cb,boundary));
 unsetenv("BACHATA_FSR31_INPUT");assert(wrap("vkCmdDraw",&draw)==&draw);
 std::cout<<"PASS native observer: forwarded draws, 864-byte camera, 120-byte raw viewport, depth pairing, finite bounds, unmap, no guest writes\n";
}
