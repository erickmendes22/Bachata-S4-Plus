// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>

// Own the pointed-to attachments: the caller's BeginRendering data is temporary.
// Splitting is legal only when ending the instance preserves every attachment.
struct Bs4RenderingSnapshot {
    VkRenderingInfo info{};
    VkRenderingAttachmentInfo color{},depth{},stencil{};
    bool hasDepth{},hasStencil{},valid{},khr{};
    bool assign(const VkRenderingInfo* source,bool extension=false) {
        *this={};
        if(!source||source->pNext||source->flags||source->viewMask||source->layerCount!=1||
           source->renderArea.offset.x||source->renderArea.offset.y||
           source->colorAttachmentCount!=1||!source->pColorAttachments||
           !source->pColorAttachments[0].imageView)return false;
        const auto stored=[](const VkRenderingAttachmentInfo& a) {
            return !a.pNext&&!a.resolveMode&&!a.resolveImageView&&
                (!a.imageView||a.storeOp==VK_ATTACHMENT_STORE_OP_STORE);
        };
        if(!stored(source->pColorAttachments[0])||
           (source->pDepthAttachment&&!stored(*source->pDepthAttachment))||
           (source->pStencilAttachment&&!stored(*source->pStencilAttachment)))return false;
        info=*source;color=source->pColorAttachments[0];
        hasDepth=source->pDepthAttachment;hasStencil=source->pStencilAttachment;
        if(hasDepth)depth=*source->pDepthAttachment;
        if(hasStencil)stencil=*source->pStencilAttachment;
        // Never retain caller-owned pointers, including after a value copy.
        info.pColorAttachments=nullptr;info.pDepthAttachment=nullptr;info.pStencilAttachment=nullptr;
        valid=true;khr=extension;return true;
    }
    VkRenderingInfo load() {
        auto resumed=info;
        color.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        if(depth.imageView)depth.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        if(stencil.imageView)stencil.loadOp=VK_ATTACHMENT_LOAD_OP_LOAD;
        resumed.pColorAttachments=&color;
        resumed.pDepthAttachment=hasDepth?&depth:nullptr;
        resumed.pStencilAttachment=hasStencil?&stencil:nullptr;
        return resumed;
    }
};
