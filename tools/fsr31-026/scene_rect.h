// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "native_scene_observer.h"
#include <algorithm>
#include <cmath>

// core025 clip-disabled shaders convert the guest viewport to a full hardware
// window in their epilogue. Only that exact window may use saved push data.
inline bool bs4_scene_rect(const Bs4SceneWriter& writer,VkExtent2D render,
                           VkExtent2D maxViewport,bool* window=nullptr) {
    if(window)*window=false;
    const auto& vp=writer.viewport;
    const auto close=[](float a,float b){return std::isfinite(a)&&std::isfinite(b)&&std::abs(a-b)<.01f;};
    if(close(std::abs(vp.width),float(render.width))&&
       close(std::abs(vp.height),float(render.height))&&
       close(std::min(vp.x,vp.x+vp.width),0)&&
       close(std::min(vp.y,vp.y+vp.height),0))return true;
    if(!writer.rawViewportValid||writer.instances!=1||!writer.vertices||writer.vertices>6||
       !maxViewport.width||!maxViewport.height||!close(vp.x,0)||!close(vp.y,0)||
       !close(vp.width,float(std::min(maxViewport.width,16384u)))||
       !close(vp.height,float(std::min(maxViewport.height,16384u))))return false;
    const auto* raw=writer.rawViewport;
    for(unsigned i=0;i<4;++i)if(!std::isfinite(raw[i]))return false;
    if(!close(2*std::abs(raw[2]),float(render.width))||
       !close(2*std::abs(raw[3]),float(render.height))||
       !close(raw[0]-std::abs(raw[2]),0)||!close(raw[1]-std::abs(raw[3]),0))return false;
    if(window)*window=true;
    return true;
}
