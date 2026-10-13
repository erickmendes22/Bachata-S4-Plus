// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
// Bloodborne Android Port, vk_camera_motion.cpp / docs/upscaler.md:
// The scene constants are 216 float32s (864 bytes), the view and inverse view
// are 3x4 affine rows. Only a *matching* G-buffer may contribute a camera.
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
namespace BachataCamera {
struct Scene {
    std::array<float,12> view{},inverse{};
    std::array<float,4> projection{};
    uint32_t width=0,height=0;
    float nearPlane=0.f,farPlane=0.f;
};
struct Push {
    float reproject[12], proj[4], prev_proj[4],size[2],jitter[2],previous_jitter[2];
    uint32_t mode;
};
static_assert(sizeof(Push)==108,"Port shader push-constant ABI mismatch");
inline bool Parse(const void* src,size_t bytes,Scene& out) {
    if(!src || bytes<216*sizeof(float))return false;
    std::array<float,216> f{};
    std::memcpy(f.data(),src,sizeof(f)); // avoid alignment assumptions
    if(!std::isfinite(f[0]) || f[0]!=3000.f || !std::isfinite(f[1]) ||
       std::abs(f[1]*f[0]-1.0f)>1e-3f ||
       !std::isfinite(f[4]) || !std::isfinite(f[5]) ||
       f[4]<64 || f[5]<64 || f[4]>8192 || f[5]>8192 ||
       std::floor(f[4])!=f[4] || std::floor(f[5])!=f[5] ||
       !std::isfinite(f[52]) || !std::isfinite(f[57]) ||
       std::abs(f[52])<1e-4f || std::abs(f[57])<1e-4f ||
       !std::isfinite(f[62]) || !std::isfinite(f[63]) ||
       f[63]>=0.f) return false;
    for(unsigned i=0;i<12;++i)
        if(!std::isfinite(f[i+8]) || !std::isfinite(f[i+180]))
            return false;
    const float nearPlane=-f[63]/f[62];
    if(!std::isfinite(nearPlane)||nearPlane<=0.f||nearPlane>=f[0])return false;
    // Preserve the pinned Port signature (far=3000), plus finite/inverse
    // checks before accepting externally supplied constants.
    for(unsigned r=0;r<3;r++)for(unsigned c=0;c<4;c++){
        float value=c==3?f[8+r*4+3]:0.f;
        for(unsigned k=0;k<3;k++)value+=f[8+r*4+k]*f[180+k*4+c];
        const float expected=r==c?1.f:0.f;
        if(std::abs(value-expected)>0.01f)return false;
    }
    out.nearPlane=nearPlane;out.farPlane=f[0];
    out.width=uint32_t(f[4]);out.height=uint32_t(f[5]);
    std::memcpy(out.view.data(),f.data()+8,12*sizeof(float));
    std::memcpy(out.inverse.data(),f.data()+180,12*sizeof(float));
    out.projection={f[52],f[57],f[62],f[63]};
    return true;
}
// Exact Bloodborne Port signal: >=5 MRTs + depth target. The guest
// camera render area is a subregion of native-sized Vulkan attachments.
inline bool GBufferCanContainScene(unsigned mrt_count,bool has_depth,
                                   unsigned area_width,unsigned area_height,
                                   const Scene& camera) {
    return has_depth && mrt_count>=5 &&
           camera.width>=64 && camera.height>=64 &&
           camera.width<=area_width && camera.height<=area_height &&
           area_width<=4096 && area_height<=4096;
}
inline std::array<float,12> Multiply(const std::array<float,12>& a,
                                      const std::array<float,12>& b) {
    std::array<float,12> o{};
    for(int r=0;r<3;++r)for(int c=0;c<4;++c) {
        float v=c==3?a[r*4+3]:0;
        for(int k=0;k<3;++k)v+=a[r*4+k]*b[k*4+c];
        o[r*4+c]=v;
    }
    return o;
}
inline Push MakePush(const Scene& current,const Scene& previous,
                     float x_jitter=0,float y_jitter=0,
                     float prev_x_jitter=0,float prev_y_jitter=0) {
    Push p{};
    const auto m=Multiply(previous.view,current.inverse);
    std::memcpy(p.reproject,m.data(),sizeof(p.reproject));
    std::memcpy(p.proj,current.projection.data(),sizeof(p.proj));
    std::memcpy(p.prev_proj,previous.projection.data(),sizeof(p.prev_proj));
    p.size[0]=float(current.width);p.size[1]=float(current.height);
    p.jitter[0]=x_jitter;p.jitter[1]=y_jitter;
    p.previous_jitter[0]=prev_x_jitter;p.previous_jitter[1]=prev_y_jitter;
    p.mode=0; // object vectors absent; port camera shader still computes motion
    return p;
}
} // namespace BachataCamera
