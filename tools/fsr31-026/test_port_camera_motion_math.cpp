// SPDX-License-Identifier: GPL-2.0-or-later
#include "port_camera_motion_math.h"
#include <cassert>
#include <cmath>
using namespace Bachata::Fsr31;
int main() {
    GuestCamera current{},previous{};
    current.valid=previous.valid=true;
    current.view={1,0,0,0, 0,1,0,0, 0,0,1,0};
    current.inverseView=current.view;previous.view=current.view;
    current.projection={1,-1,1,-.1f};
    previous.projection=current.projection;
    MotionPush out{};
    assert(BuildMotionPush(out,current,previous,640,360));
    assert(out.reproject[0]==1 && out.reproject[5]==1 && out.reproject[10]==1);
    assert(out.size[0]==640 && out.size[1]==360);
    assert(std::abs(CameraNear(current)-.1f)<1e-6f);
    assert(std::abs(CameraVerticalFov(current)-1.57079632679f)<1e-5f);
    previous.view[3]=4;
    assert(BuildMotionPush(out,current,previous,640,360));
    assert(out.reproject[3]==4);
}
