// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "port_camera_state.h"
#include <array>
#include <cstdint>
#include <cstddef>
#include <cmath>
namespace Bachata::Fsr31 {
struct MotionPush {
    std::array<float,12> reproject{};
    std::array<float,4> proj{},prevProj{};
    std::array<float,2> size{},jitter{},previousJitter{};
    std::uint32_t mode{};
};
static_assert(sizeof(MotionPush)==108);
static_assert(offsetof(MotionPush,mode)==104);
inline std::array<float,12> MultiplyAffine(
    const std::array<float,12>& a,const std::array<float,12>& b) {
    std::array<float,12> out{};
    for(int r=0;r<3;++r)for(int c=0;c<4;++c) {
        float v=c==3?a[r*4+3]:0.f;
        for(int k=0;k<3;++k)v+=a[r*4+k]*b[k*4+c];
        out[r*4+c]=v;
    }
    return out;
}
inline bool BuildMotionPush(MotionPush& out,
    const GuestCamera& curr,const GuestCamera& prev,
    std::uint32_t w,std::uint32_t h,
    std::array<float,2> jitter={0,0},
    std::array<float,2> previousJitter={0,0}) {
    if(!curr.valid||!prev.valid||!w||!h||
       curr.projection[0]==0.f||curr.projection[1]==0.f)return false;
    out.reproject=MultiplyAffine(prev.view,curr.inverseView);
    out.proj=curr.projection;out.prevProj=prev.projection;
    out.size={float(w),float(h)};
    out.jitter=jitter;out.previousJitter=previousJitter;out.mode=0;
    return true;
}
inline float CameraNear(const GuestCamera& curr) {
    return curr.projection[2]?-curr.projection[3]/curr.projection[2]:0.f;
}
inline float CameraVerticalFov(const GuestCamera& curr) {
    return curr.projection[1]?2.f*std::atan(1.f/std::abs(curr.projection[1])):0.f;
}
}
