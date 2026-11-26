// SPDX-License-Identifier: GPL-2.0-or-later
#include "port_scene_frame.h"
#include <mutex>
#include <algorithm>
namespace {
struct Record {
    BachataCamera::Scene camera{};
    uint64_t frame{},scene{};
    VkCommandBuffer command{};
    VkImageView depth{};
    float x{},y{};
    bool valid{};
};
std::mutex guard;
Record current{},previous{};
struct SubmittedPair {
    VkCommandBuffer scene{},ui{};
    VkImageView depth{};
    uint64_t frame{};
};
SubmittedPair authorized{};
bool frame_open=false;
bool committed=false;
bool finite_shift(float v) {return std::isfinite(v)&&std::abs(v)<=1.f;}
}
extern "C" __attribute__((visibility("default")))
int bs4_fsr31_port_scene(const Bs4PortSceneFrame* f) {
    if(!f||f->structSize!=sizeof(*f)||f->abiVersion!=1||!f->frameId||
       !f->sceneId||!f->command||!f->depth||
       f->constantsBytes!=864||
       (f->viewportXSign!=1.f&&f->viewportXSign!=-1.f)||
       (f->viewportYSign!=1.f&&f->viewportYSign!=-1.f)||
       !finite_shift(f->jitterX)||!finite_shift(f->jitterY))return 0;
    BachataCamera::Scene c{};
    if(!BachataCamera::Parse(f->constants,f->constantsBytes,c)||
       !BachataCamera::GBufferCanContainScene(f->colorAttachmentCount,true,
        f->renderArea.width,f->renderArea.height,c))return 0;
    c.projection[0]*=f->viewportXSign;
    c.projection[1]*=f->viewportYSign;
    std::lock_guard lock{guard};
    if(current.valid&&f->frameId<current.frame)return 0;
    if(current.valid&&f->frameId==current.frame) {
        if(!frame_open)return 0;
        if(committed)return current.scene==f->sceneId&&current.depth==f->depth&&
                            current.command==f->command&&current.x==f->jitterX&&
                            current.y==f->jitterY?1:0;
        // Like the Port, select the G-buffer whose depth the upcoming motion
        // pass uses. History advances once per displayed frame, not per pass.
        current={c,f->frameId,f->sceneId,f->command,f->depth,
                 f->jitterX,f->jitterY,true};
        return 1;
    }
    previous=current;authorized={};
    current={c,f->frameId,f->sceneId,f->command,f->depth,
             f->jitterX,f->jitterY,true};
    frame_open=true;committed=false;
    return 1;
}
void bs4_fsr31_port_authorize_submitted(VkCommandBuffer scene,VkCommandBuffer ui,
                                      VkImageView depth) {
    std::lock_guard lock{guard};
    if(!frame_open||!current.valid||!scene||!ui||scene==ui||
       current.command!=scene||current.depth!=depth)return;
    authorized={scene,ui,depth,current.frame};
}
bool bs4_fsr31_port_camera(VkCommandBuffer cb,VkImageView depth,
                           VkExtent2D size,Bs4PortCameraDispatch& out) {
    std::lock_guard lock{guard};
    const bool same=current.command==cb;
    const bool submitted=authorized.scene==current.command&&
       authorized.ui==cb&&authorized.depth==depth&&authorized.frame==current.frame;
    if(!frame_open||!current.valid||!previous.valid||(!same&&!submitted)||
       current.depth!=depth||current.camera.width!=size.width||
       current.camera.height!=size.height)
        return false;
    // The display size is not a scene identity. An abrupt camera cut at the
    // same resolution must invalidate temporal history, as in the Port.
    float travel2=0.f,orientationDelta=0.f;
    for(int r=0;r<3;++r) {
        const float t=current.camera.inverse[r*4+3]-previous.camera.inverse[r*4+3];
        travel2+=t*t;
        for(int c=0;c<3;++c) {
            const int k=r*4+c;
            orientationDelta=std::max(orientationDelta,
                std::abs(current.camera.inverse[k]-previous.camera.inverse[k]));
        }
    }
    const bool cameraCut=travel2>64.f||orientationDelta>.75f;
    const bool coherent=previous.valid&&!cameraCut&&previous.frame+1==current.frame&&
        previous.scene==current.scene&&
        previous.camera.width==current.camera.width&&
        previous.camera.height==current.camera.height;
    const auto& prior=coherent?previous:current;
    out.motion=BachataCamera::MakePush(current.camera,prior.camera,
                                      current.x,current.y,prior.x,prior.y);
    out.nearPlane=current.camera.nearPlane;
    out.farPlane=3000.f;
    out.verticalFov=2.f*std::atan(1.f/std::abs(current.camera.projection[1]));
    out.frameId=current.frame;
    out.reset=!coherent;
    committed=true;
    return true;
}
extern "C" __attribute__((visibility("default")))
void bs4_fsr31_port_invalidate_after_gpu_drain() {
    std::lock_guard lock{guard};current={};previous={};authorized={};frame_open=false;committed=false;
}

void bs4_fsr31_port_end_frame() {
    std::lock_guard lock{guard};authorized={};frame_open=false;committed=false;
}
