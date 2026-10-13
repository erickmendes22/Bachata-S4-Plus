// Regression: depth and stencil may share an image but must never share
// mutable VkRenderingAttachmentInfo when the guest specifies different ops.
#include "../native_ui_targets.h"
#include <cassert>
int main() {
    const auto nativeView = reinterpret_cast<VkImageView>(uintptr_t(0x1234));
    const auto scaledView = reinterpret_cast<VkImageView>(uintptr_t(0x5678));
    VkRenderingAttachmentInfo d{}; d.sType=VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO;
    VkRenderingAttachmentInfo s{}; s.sType=VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO;
    d.imageView = nativeView;
    d.imageLayout = VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_OPTIMAL;
    d.loadOp = VK_ATTACHMENT_LOAD_OP_LOAD;
    d.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
    d.clearValue.depthStencil = {0.25f, 11};
    s.imageView = nativeView;
    s.imageLayout = VK_IMAGE_LAYOUT_STENCIL_ATTACHMENT_OPTIMAL;
    s.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
    s.storeOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
    s.clearValue.depthStencil = {0.75f, 27};
    VkRenderingInfo src{}; src.sType=VK_STRUCTURE_TYPE_RENDERING_INFO;
    src.pDepthAttachment = &d;
    src.pStencilAttachment = &s;
    VkRenderingInfo dst = src;
    VkRenderingAttachmentInfo scaledDepth{}, scaledStencil{};
    bs4_native_ui_rebind_depth_stencil(src,dst,scaledDepth,scaledStencil,scaledView);
    assert(dst.pDepthAttachment == &scaledDepth);
    assert(dst.pStencilAttachment == &scaledStencil);
    assert(dst.pDepthAttachment != dst.pStencilAttachment);
    assert(scaledDepth.imageView == scaledView && scaledStencil.imageView == scaledView);
    assert(scaledDepth.imageLayout == VK_IMAGE_LAYOUT_DEPTH_ATTACHMENT_OPTIMAL);
    assert(scaledStencil.imageLayout == VK_IMAGE_LAYOUT_STENCIL_ATTACHMENT_OPTIMAL);
    assert(scaledDepth.loadOp == VK_ATTACHMENT_LOAD_OP_LOAD);
    assert(scaledStencil.loadOp == VK_ATTACHMENT_LOAD_OP_CLEAR);
    assert(scaledDepth.storeOp == VK_ATTACHMENT_STORE_OP_STORE);
    assert(scaledStencil.storeOp == VK_ATTACHMENT_STORE_OP_DONT_CARE);
    assert(scaledDepth.clearValue.depthStencil.depth == 0.25f);
    assert(scaledStencil.clearValue.depthStencil.stencil == 27);
    assert(d.imageView == nativeView && s.imageView == nativeView);
    // Native depth-only and stencil-only rendering preserve their independent slots.
    for (int select=0;select<2;select++) {
        VkRenderingInfo only{}; only.sType=VK_STRUCTURE_TYPE_RENDERING_INFO;
        if (select==0) only.pDepthAttachment=&d;
        else only.pStencilAttachment=&s;
        VkRenderingInfo redirected=only;
        VkRenderingAttachmentInfo outDepth{},outStencil{};
        bs4_native_ui_rebind_depth_stencil(only,redirected,outDepth,outStencil,scaledView);
        assert(bool(redirected.pDepthAttachment)==(select==0));
        assert(bool(redirected.pStencilAttachment)==(select==1));
    }
    return 0;
}
