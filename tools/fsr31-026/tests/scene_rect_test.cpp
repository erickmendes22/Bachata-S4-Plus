// SPDX-License-Identifier: GPL-2.0-or-later
#include "../scene_rect.h"
#include <cassert>
#include <limits>
#include <cstdio>
int main(){
    Bs4SceneWriter w{};w.vertices=3;w.instances=1;
    w.viewport={0,360,640,-360,0,1};
    bool window=true;assert(bs4_scene_rect(w,{640,360},{},&window)&&!window);
    w.viewport={0,0,16384,16384,0,1};
    assert(!bs4_scene_rect(w,{640,360},{16384,16384}));
    w.rawViewportValid=true;w.rawViewport[0]=w.rawViewport[2]=320;
    w.rawViewport[1]=180;w.rawViewport[3]=-180;
    assert(bs4_scene_rect(w,{640,360},{32768,32768},&window)&&window);
    assert(!bs4_scene_rect(w,{640,360},{}));
    w.viewport.width=8192;assert(!bs4_scene_rect(w,{640,360},{16384,16384}));
    w.viewport.height=8192;assert(bs4_scene_rect(w,{640,360},{8192,8192}));
    w.viewport.x=1;assert(!bs4_scene_rect(w,{640,360},{8192,8192}));w.viewport.x=0;
    w.rawViewport[0]=321;assert(!bs4_scene_rect(w,{640,360},{8192,8192}));w.rawViewport[0]=320;
    w.rawViewport[2]=960;assert(!bs4_scene_rect(w,{640,360},{8192,8192}));w.rawViewport[2]=320;
    w.rawViewport[1]=std::numeric_limits<float>::infinity();assert(!bs4_scene_rect(w,{640,360},{8192,8192}));w.rawViewport[1]=180;
    w.instances=2;assert(!bs4_scene_rect(w,{640,360},{8192,8192}));w.instances=1;
    w.vertices=7;assert(!bs4_scene_rect(w,{640,360},{8192,8192}));
    std::puts("PASS native scene rectangle: ordinary and exact hardware window, invalid/unrelated rectangles refused");
}
