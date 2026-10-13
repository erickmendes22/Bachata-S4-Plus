// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <vulkan/vulkan.h>
#include <algorithm>
#include <cstdint>
#include <vector>

namespace BachataRendering {
// VkRenderingInfo VUID-pNext-06079 / 06080: every bound attachment
// must contain offset + extent. Never enlarge a legal render area.
inline bool BoundArea(VkRect2D requested, const std::vector<VkExtent2D>& attachments,
                      VkRect2D& output) {
    output=requested;
    if(attachments.empty() || requested.offset.x<0 || requested.offset.y<0 ||
       !requested.extent.width || !requested.extent.height)return false;
    for(const auto& attachment:attachments) {
        const auto x=uint32_t(requested.offset.x),y=uint32_t(requested.offset.y);
        if(x>=attachment.width || y>=attachment.height)return false;
        output.extent.width=std::min(output.extent.width,attachment.width-x);
        output.extent.height=std::min(output.extent.height,attachment.height-y);
    }
    return output.extent.width!=requested.extent.width ||
           output.extent.height!=requested.extent.height;
}
}
