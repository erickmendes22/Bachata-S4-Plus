// SPDX-License-Identifier: GPL-2.0-or-later
#include "../port_scene_frame.h"
#include <array>
#include <cassert>
#include <iostream>
#include <limits>
int main() {
    std::array<float,216> data{};
    data[0]=3000.f;data[1]=1.f/3000.f;data[4]=640;data[5]=360;
    for(int i=0;i<3;i++)data[8+i*5]=data[180+i*5]=1;
    data[52]=2;data[57]=3;data[62]=1.0001f;data[63]=-.1f;
    auto cb=reinterpret_cast<VkCommandBuffer>(uintptr_t(1));
    auto depth=reinterpret_cast<VkImageView>(uintptr_t(2));
    Bs4PortSceneFrame f{sizeof(f),1,1,7,cb,depth,5,{1920,1080},
                       data.data(),864,1,-1,.25f,-.125f};
    Bs4PortCameraDispatch out{};
    assert(bs4_fsr31_port_scene(&f));
    assert(!bs4_fsr31_port_camera(cb,depth,{640,360},out)); // history warmup
    bs4_fsr31_port_end_frame();
    assert(!bs4_fsr31_port_scene(&f)); // closed frame cannot be resurrected
    f.frameId=2;data[11]=-2.f;data[183]=2.f;
    assert(bs4_fsr31_port_scene(&f));
    data[11]=999; // copied constants; guest updates cannot mutate captured camera
    assert(bs4_fsr31_port_camera(cb,depth,{640,360},out));
    assert(!out.reset&&out.frameId==2);
    assert(out.motion.reproject[3]==2.f);
    assert(out.motion.proj[1]==-3.f&&out.motion.prev_proj[1]==-3.f);
    assert(out.motion.jitter[0]==.25f&&out.motion.jitter[1]==-.125f);
    assert(std::abs(out.verticalFov-2.f*std::atan(1.f/3.f))<1e-6f);
    assert(out.farPlane==3000.f&&out.nearPlane>0.f);
    assert(!bs4_fsr31_port_camera(reinterpret_cast<VkCommandBuffer>(uintptr_t(3)),depth,{640,360},out));
    assert(!bs4_fsr31_port_camera(cb,reinterpret_cast<VkImageView>(uintptr_t(4)),{640,360},out));
    assert(!bs4_fsr31_port_camera(cb,depth,{960,540},out));
    data[11]=-2.f;
    auto wrong=f;wrong.sceneId=9;assert(!bs4_fsr31_port_scene(&wrong));
    wrong=f;wrong.frameId=1;assert(!bs4_fsr31_port_scene(&wrong));
    bs4_fsr31_port_end_frame();
    assert(!bs4_fsr31_port_camera(cb,depth,{640,360},out)); // same CB reused
    f.frameId=4;assert(bs4_fsr31_port_scene(&f));
    assert(bs4_fsr31_port_camera(cb,depth,{640,360},out)&&out.reset);
    assert(out.motion.reproject[3]==0.f); // reset never reprojects stale history
    f.frameId=5;f.sceneId=8;assert(bs4_fsr31_port_scene(&f));
    assert(bs4_fsr31_port_camera(cb,depth,{640,360},out)&&out.reset);
    for(int i=0;i<7;i++) {
        wrong=f;wrong.frameId=6;
        if(i==0)wrong.abiVersion=0;
        if(i==1)wrong.constantsBytes=863;
        if(i==2)wrong.viewportYSign=0;
        if(i==3)wrong.jitterX=std::numeric_limits<float>::quiet_NaN();
        if(i==4)wrong.colorAttachmentCount=4;
        if(i==5)wrong.renderArea={320,180};
        if(i==6)wrong.depth={};
        assert(!bs4_fsr31_port_scene(&wrong));
    }
    data[0]=1000;wrong=f;wrong.frameId=6;assert(!bs4_fsr31_port_scene(&wrong));
    data[0]=3000;data[183]=100;assert(!bs4_fsr31_port_scene(&wrong));
    // Resolution and sceneId stay the same across a teleport. Motion history
    // must reset instead of reprojecting the previous scene into this one.
    data[11]=-50.f;data[183]=50.f;f.frameId=6;
    assert(bs4_fsr31_port_scene(&f));
    assert(bs4_fsr31_port_camera(cb,depth,{640,360},out)&&out.reset);
    bs4_fsr31_port_invalidate_after_gpu_drain();
    assert(!bs4_fsr31_port_camera(cb,depth,{640,360},out));
    std::cout<<"Port handoff: history, depth, camera cuts, viewport signs, jitter, copied constants and stale-CB rejection passed\n";
}
