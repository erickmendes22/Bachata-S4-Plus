#include "../rendering_snapshot.h"
#include <cassert>
#include <initializer_list>
#include <cstdint>
int main() {
    VkRenderingAttachmentInfo color{};color.sType=VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO;
    color.imageView=(VkImageView)(uintptr_t)1;
    color.imageLayout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
    color.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
    color.loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;
    VkRenderingAttachmentInfo depth=color,stencil=color;
    depth.imageLayout=VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_OPTIMAL;
    stencil.imageLayout=VK_IMAGE_LAYOUT_STENCIL_ATTACHMENT_OPTIMAL;
    stencil.loadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE;
    VkRenderingInfo info{};info.sType=VK_STRUCTURE_TYPE_RENDERING_INFO;
    info.layerCount=1;info.renderArea.extent={1920,1080};
    info.colorAttachmentCount=1;info.pColorAttachments=&color;
    info.pDepthAttachment=&depth;info.pStencilAttachment=&stencil;
    Bs4RenderingSnapshot snapshot{};assert(snapshot.assign(&info));
    auto copy=snapshot;auto load=copy.load();
    assert(load.pColorAttachments==&copy.color&&load.pDepthAttachment==&copy.depth&&load.pStencilAttachment==&copy.stencil);
    assert(load.pColorAttachments->loadOp==VK_ATTACHMENT_LOAD_OP_LOAD);
    assert(load.pDepthAttachment->loadOp==VK_ATTACHMENT_LOAD_OP_LOAD&&load.pStencilAttachment->loadOp==VK_ATTACHMENT_LOAD_OP_LOAD);
    assert(load.pDepthAttachment->imageLayout!=load.pStencilAttachment->imageLayout);
    assert(color.loadOp==VK_ATTACHMENT_LOAD_OP_CLEAR&&stencil.loadOp==VK_ATTACHMENT_LOAD_OP_DONT_CARE);
    for(auto* attachment:{&color,&depth,&stencil}) {
        auto original=*attachment;
        attachment->storeOp=VK_ATTACHMENT_STORE_OP_DONT_CARE;assert(!snapshot.assign(&info));*attachment=original;
        attachment->resolveMode=VK_RESOLVE_MODE_SAMPLE_ZERO_BIT;assert(!snapshot.assign(&info));*attachment=original;
        attachment->pNext=&info;assert(!snapshot.assign(&info));*attachment=original;
    }
    info.flags=VK_RENDERING_CONTENTS_SECONDARY_COMMAND_BUFFERS_BIT;assert(!snapshot.assign(&info));info.flags=0;
    info.viewMask=1;assert(!snapshot.assign(&info));info.viewMask=0;
    info.renderArea.offset.x=1;assert(!snapshot.assign(&info));info.renderArea.offset.x=0;
    info.pNext=&color;assert(!snapshot.assign(&info));info.pNext=nullptr;
    info.pDepthAttachment=info.pStencilAttachment=nullptr;assert(snapshot.assign(&info,true));
    assert(snapshot.khr);load=snapshot.load();assert(!load.pDepthAttachment&&!load.pStencilAttachment);
}
