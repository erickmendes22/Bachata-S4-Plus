// SPDX-License-Identifier: GPL-2.0-or-later
#include "../native_scene_observer.h"
#include <array>
#include <cassert>
#include <cstring>
#include <cstdlib>
#include <iostream>
extern "C" bool bs4_fsr31_temporal_resources_ready(VkExtent2D){return false;}
template<class T>T wrap(const char* name,T value){return reinterpret_cast<T>(bs4_native_scene_wrap(name,reinterpret_cast<PFN_vkVoidFunction>(value)));}
VkViewport actualViewport{};VkRect2D actualScissor{};std::array<unsigned char,120> actualPush{};
unsigned calls=0;
void VKAPI_CALL push(VkCommandBuffer,VkPipelineLayout,VkShaderStageFlags,uint32_t offset,uint32_t size,const void* values){assert(offset==0&&size==120);std::memcpy(actualPush.data(),values,120);calls++;}
void VKAPI_CALL viewport(VkCommandBuffer,uint32_t first,uint32_t count,const VkViewport* v){assert(first==0&&count==1);actualViewport=*v;calls++;}
void VKAPI_CALL scissor(VkCommandBuffer,uint32_t first,uint32_t count,const VkRect2D* v){assert(first==0&&count==1);actualScissor=*v;calls++;}
void VKAPI_CALL viewport_count(VkCommandBuffer cb,uint32_t count,const VkViewport* v){viewport(cb,0,count,v);}
void VKAPI_CALL scissor_count(VkCommandBuffer cb,uint32_t count,const VkRect2D* v){scissor(cb,0,count,v);}
int main(){
 setenv("BACHATA_FSR31_INPUT","port",1);
 const auto c=wrap("vkCmdPushConstants",&push);const auto v=wrap("vkCmdSetViewport",&viewport);const auto s=wrap("vkCmdSetScissor",&scissor);
 const auto vc=wrap("vkCmdSetViewportWithCountEXT",&viewport_count);const auto sc=wrap("vkCmdSetScissorWithCountEXT",&scissor_count);
 const auto cb=reinterpret_cast<VkCommandBuffer>(uintptr_t(1));
 const auto layout=reinterpret_cast<VkPipelineLayout>(uintptr_t(2));
 std::array<unsigned char,120> raw{};float values[4]{320,180,320,-180};std::memcpy(raw.data(),values,16);
 for(size_t i=16;i<raw.size();++i)raw[i]=static_cast<unsigned char>(i);
 VkViewport vp{0,360,640,-360,0,1};VkRect2D rect{{13,7},{101,59}};
 c(cb,layout,VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());v(cb,0,1,&vp);s(cb,0,1,&rect);
 const auto before=calls;
 assert(bs4_native_scene_can_ui_scale(cb,{640,360},{1280,720},{16384,16384})&&calls==before);
 for(int frame=0;frame<100;frame++){
  assert(bs4_native_scene_apply_ui_scale(cb,{640,360},{1280,720},true,{16384,16384}));
  assert(actualViewport.width==1280&&actualViewport.height==-720&&actualViewport.y==720);
  assert(actualScissor.offset.x==26&&actualScissor.offset.y==14&&actualScissor.extent.width==202&&actualScissor.extent.height==118);
  float scaled[4];std::memcpy(scaled,actualPush.data(),16);assert(scaled[0]==640&&scaled[1]==360&&scaled[2]==640&&scaled[3]==-360);
  assert(!std::memcmp(actualPush.data()+16,raw.data()+16,104));
  // No native dynamic commands between these calls: emulate cache suppression.
  assert(bs4_native_scene_apply_ui_scale(cb,{640,360},{1280,720},false,{16384,16384}));
  assert(!std::memcmp(actualPush.data(),raw.data(),120));assert(actualViewport.width==640&&actualViewport.height==-360);
  assert(!std::memcmp(&actualScissor,&rect,sizeof(rect)));
 }
 values[0]=values[2]=960;values[1]=540;values[3]=-540;std::memcpy(raw.data(),values,16);
 c(cb,layout,VK_SHADER_STAGE_VERTEX_BIT,0,120,raw.data());
 vp={0,0,16384,16384,0,1};rect={{3,5},{1501,701}};vc(cb,1,&vp);sc(cb,1,&rect);
 assert(bs4_native_scene_apply_ui_scale(cb,{640,360},{1280,720},true,{16384,16384}));
 assert(actualViewport.width==16384&&actualViewport.height==16384); // clip-disabled hardware window stays fixed
 float native[4];std::memcpy(native,actualPush.data(),16);assert(native[2]==640&&native[3]==-360);
 assert(actualScissor.offset.x==2&&actualScissor.offset.y==3&&actualScissor.extent.width==1001&&actualScissor.extent.height==468);
 const auto validCalls=calls;rect={{INT32_MAX-1,0},{UINT32_MAX,10}};sc(cb,1,&rect);
 assert(!bs4_native_scene_can_ui_scale(cb,{640,360},{1280,720},{16384,16384})&&calls==validCalls+1);
 bs4_native_scene_register_pipeline(layout,0x34e8a281);assert(bs4_native_scene_ui_boundary(cb)); // no debug object name required
 bs4_native_scene_reset(cb);assert(!bs4_native_scene_dynamic_ready(cb));
 std::cout<<"PASS UI scale: reduced/native coordinates, clip-disabled viewport, rounded scissors, original push payload, 100 cached-state restores and overflow rejection\n";
}
