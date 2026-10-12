// SPDX-License-Identifier: GPL-2.0-or-later
#include "port_camera_constants.h"
#include "port_runscaled_contract.h"
#include <cassert>
#include <cmath>
#include <cstring>
#include <array>
int main(){
    using namespace BachataCamera;
    std::array<float,216> f{};
    f[0]=3000.f;f[1]=1.f/3000.f;f[4]=640;f[5]=360;
    f[52]=1.42799f;f[57]=2.53865f;f[62]=1.00002f;f[63]=-0.0500679f;
    // Identity current view/inverse.
    for(int i=0;i<3;i++){f[8+i*4+i]=1;f[180+i*4+i]=1;}
    Scene now{};
    assert(Parse(f.data(),sizeof(f),now));
    Scene prev=now;
    prev.view[3]=2.5f;
    const Push p=MakePush(now,prev);
    assert(sizeof(p)==108);
    assert(std::abs(p.reproject[3]-2.5f)<1.e-5f);
    assert(p.size[0]==640 && p.size[1]==360);
    assert(p.proj[0]==1.42799f && p.mode==0);
    assert(!Parse(f.data(),32,now)); // no OOB read
    f[0]=2000;assert(!Parse(f.data(),sizeof(f),now));
    f[0]=3000;f[63]=0.1f;assert(!Parse(f.data(),sizeof(f),now));
    using namespace BachataPortScaled;
    const VkExtent2D scene{640,360},out{1280,720};
    const VkExtent2D alloc{1920,1080},badDepth{1280,720};
    assert(SceneAndOutput(VK_FORMAT_R8G8B8A8_UNORM,scene,out));
    assert(!SceneAndOutput(VK_FORMAT_B10G11R11_UFLOAT_PACK32,scene,out));
    assert(MatchingDepth(scene,scene,scene));
    assert(MatchingDepth(scene,alloc,alloc));
    assert(!MatchingDepth(scene,alloc,badDepth));
    return 0;
}
