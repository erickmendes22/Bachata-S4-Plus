// SPDX-License-Identifier: GPL-2.0-or-later
#include "../fsr31-026/port_camera_probe.cpp"
#include <cassert>
extern "C" int bs4_fsr31_selected_preset(){return 4;}
extern "C" VkImageView bs4_port_ui_redirect_sampled(VkCommandBuffer,VkImageView){return VK_NULL_HANDLE;}
extern "C" int bs4_port_ui_projection_signs(VkCommandBuffer,float* x,float* y){*x=1;*y=-1;return 1;}
extern "C" bool bs4_port_ui_try_activate(VkCommandBuffer){return false;}
extern "C" void bs4_port_ui_note_draw(VkCommandBuffer){}
extern "C" int bs4_port_ui_apply_camera_jitter(VkCommandBuffer,float,float){return 0;}
extern "C" int bs4_fsr31_attachment_ready(){return 1;}
extern "C" int bs4_fsr31_camera_resources_ready(VkExtent2D){return 0;}
unsigned forwarded=0;
void VKAPI_CALL push(VkCommandBuffer,VkPipelineBindPoint,VkPipelineLayout,uint32_t,uint32_t n,const VkWriteDescriptorSet* w){assert(n==1 && w->pBufferInfo->offset==32);++forwarded;}
int main(){
 std::array<float,216> f{};f[0]=3000;f[1]=1.f/3000;f[4]=640;f[5]=360;
 f[52]=1.4f;f[57]=2.5f;f[62]=1.00002f;f[63]=-.05f;
 for(int i=0;i<3;i++)f[8+i*4+i]=f[180+i*4+i]=1;
 std::array<uint8_t,896> storage{};std::memcpy(storage.data()+32,f.data(),864);
 auto mem=(VkDeviceMemory)1;auto buf=(VkBuffer)2;auto depth=(VkImageView)3;
 mapped[mem]={storage.data(),0,storage.size()};bound[buf]={mem,0};
 VkDescriptorBufferInfo info{buf,32,864};VkWriteDescriptorSet w{};
 w.descriptorType=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;w.descriptorCount=1;w.pBufferInfo=&info;
 for(const char* api:{"vkCmdPushDescriptorSet","vkCmdPushDescriptorSetKHR"}){
  auto cb=(VkCommandBuffer)(uintptr_t)(forwarded+10);bs4_port_note_render(cb,depth,{1920,1080},5);
  auto hook=(PFN_vkCmdPushDescriptorSetKHR)bs4_port_wrap_proc(api,(PFN_vkVoidFunction)push);
  assert(hook!=push);hook(cb,VK_PIPELINE_BIND_POINT_GRAPHICS,(VkPipelineLayout)4,0,1,&w);
  VkExtent2D extent{};assert(bs4_port_current_scene(cb,&extent)==depth);
  assert(extent.width==640 && extent.height==360);
 }
 assert(forwarded==2);std::puts("PASS: promoted/KHR push descriptors capture genuine camera and preserve guest call");
}
