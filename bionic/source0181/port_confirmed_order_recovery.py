"""Preserve f75b1f5 SRT/scheduler. Fix descriptor provenance and Android final present."""
from pathlib import Path
import re
def apply(root:Path):
    def edit(rel,old,new):
        p=root/rel
        s=p.read_text()
        if s.count(old)!=1: raise RuntimeError("Order confirmed base drift "+rel+": "+old[:100])
        p.write_text(s.replace(old,new,1))
    rp="src/shader_recompiler/ir/passes/resource_patching_pass.cpp"
    edit(rp,"return desc.sharp_fetch == existing.sharp_fetch && desc.is_array == existing.is_array &&",
         """return desc.sharp_fetch == existing.sharp_fetch && desc.is_array == existing.is_array &&
                   desc.is_r128 == existing.is_r128 && desc.is_depth == existing.is_depth &&""")
    # Immediate DWORDs must not be promoted to a memcpy of unrelated flat slots.
    edit(rp,"    if (sharp_fetch.summary != Summary::Invalid) {",
         """    if (sharp_fetch.summary != Summary::Invalid &&
        sharp.num_dwords != 0 &&
        sharp_fetch.load_mask == ((1u<<sharp.num_dwords)-1u)) {""")
    r="src/shader_recompiler/resource.h"
    edit(r,"        if (summary == Summary::SingleLoad) [[likely]] {",
         """        if (summary == Summary::SingleLoad &&
            (load_mask & ((1u<<num_dwords)-1u)) == ((1u<<num_dwords)-1u)) [[likely]] {""")
    edit(r,"    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {",
         """    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {
        const u32 words=is_r128?4u:8u;
        const u64 element_off=u64{element}*array_stride_dw;
        if (array_size && element>=array_size) return AmdGpu::Image::Null(is_depth);
        for (u32 i=0;i<words;++i) {
            if (!(sharp_fetch.load_mask&(1u<<i))) continue;
            if (sharp_fetch.offsets[i]==UNKNOWN_LOCATION ||
                u64{sharp_fetch.offsets[i]}+element_off>=info.flattened_ud_buf.size())
                return AmdGpu::Image::Null(is_depth);
        }""")
    ser="src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    edit(ser,"""            bool result{};
            if (is_compute) {""",
         """            infos.fill(nullptr);
            modules.fill(nullptr);
            runtime_infos.fill({});
            fetch_shader=nullptr;
            bool result{};
            if (is_compute) {""")
    # Retain every other f75b1f5 performance path. No broad SRT fallback.
    pc="src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    edit(pc,'    auto patch = GetShaderPatch(info.pgm_hash, info.hw_stage, perm_idx, "spv");',
         """    std::optional<std::vector<u32>> patch;
    if (EmulatorSettings.IsPatchShaders() || EmulatorSettings.IsShaderCollect())
        patch=GetShaderPatch(info.pgm_hash,info.hw_stage,perm_idx,"spv");""")
    # Same cache metadata structure, new binary generation due to changed
    # descriptor interpretation. Do not reuse a wrongly compiled module.
    p=root/ser
    s,n=re.subn(r'ShaderBinaryVersion = (\d+)u;',lambda m:f'ShaderBinaryVersion = {int(m.group(1))+109}u;',p.read_text())
    if n!=1: raise RuntimeError("Order shader cache version drift")
    p.write_text(s)
    # Direct final image delivery, but only when the final ImGui draw is
    # exactly the opaque full-screen game quad. No skipped overlays or UI.
    sw="src/video_core/renderer_vulkan/vk_swapchain.h"
    edit(sw,"    bool HasHDR() const {",
         """    bool OpaqueComposite() const {
        return composite_alpha==vk::CompositeAlphaFlagBitsKHR::eOpaque;
    }

    bool HasHDR() const {""")
    pp="src/video_core/renderer_vulkan/vk_presenter.cpp"
    edit(pp,"        ImGui::Core::Render(cmdbuf, swapchain_image_view, swapchain.GetExtent());",
r'''        bool direct_present=false;
#ifdef __ANDROID__
        if (!BachataCompat::Sotc608() && is_game_frame && !is_reusing_frame &&
            !swapchain.GetHDR() && swapchain.OpaqueComposite() &&
            !Libraries::SystemService::IsSplashVisible() && capture_with_overlays_count==0 &&
            !EmulatorSettings.IsNullGPU() && frame->opaque_sampled_view) {
            ImGui::Render();
            const auto* dd=ImGui::GetDrawData();
            const ImDrawList* last_list=nullptr;
            const ImDrawCmd* last_cmd=nullptr;
            bool callbacks=false;
            if (dd) for (int li=0;li<dd->CmdListsCount;++li) {
                const auto* list=dd->CmdLists[li];
                for (const auto& cmd:list->CmdBuffer) {
                    if (cmd.UserCallback) callbacks=true;
                    if (cmd.ElemCount) {last_list=list;last_cmd=&cmd;}
                }
            }
            // Earlier draws are fully occluded only if this final quad
            // covers all pixels with opaque white vertex color.
            if (dd && !callbacks && last_cmd && last_cmd->GetTexID()==frame->imgui_texture &&
                last_cmd->ElemCount==6 && dd->DisplayPos.x==0 && dd->DisplayPos.y==0 &&
                dd->FramebufferScale.x==1 && dd->FramebufferScale.y==1 &&
                dd->DisplaySize.x==float(extent.width) && dd->DisplaySize.y==float(extent.height) &&
                last_cmd->ClipRect.x<=0 && last_cmd->ClipRect.y<=0 &&
                last_cmd->ClipRect.z>=float(extent.width) && last_cmd->ClipRect.w>=float(extent.height)) {
                unsigned corners=0;
                unsigned corner_ids[6]{};
                bool exact=true;
                for (unsigned k=0;k<6;++k) {
                    const auto vi=last_cmd->VtxOffset+last_list->IdxBuffer[last_cmd->IdxOffset+k];
                    const auto& v=last_list->VtxBuffer[vi];
                    const bool x=v.pos.x==float(extent.width),y=v.pos.y==float(extent.height);
                    if ((!x&&v.pos.x!=0)||(!y&&v.pos.y!=0)||
                        v.uv.x!=float(x)||v.uv.y!=float(y)||v.col!=IM_COL32_WHITE) {exact=false;break;}
                    corner_ids[k]=unsigned(x)+2u*unsigned(y);
                    corners|=1u<<corner_ids[k];
                }
                const unsigned tri1=(1u<<corner_ids[0])|(1u<<corner_ids[1])|(1u<<corner_ids[2]);
                const unsigned tri2=(1u<<corner_ids[3])|(1u<<corner_ids[4])|(1u<<corner_ids[5]);
                const unsigned diagonal=tri1&tri2;
                const auto fmt=swapchain.GetSurfaceFormat().format;
                const auto features=instance.GetPhysicalDevice().getFormatProperties(fmt).optimalTilingFeatures;
                const auto needed=vk::FormatFeatureFlagBits::eBlitSrc|vk::FormatFeatureFlagBits::eBlitDst|
                                  vk::FormatFeatureFlagBits::eSampledImageFilterLinear;
                if (exact && corners==15 && (diagonal==6||diagonal==9) &&
                    (fmt==vk::Format::eR8G8B8A8Unorm||fmt==vk::Format::eB8G8R8A8Unorm) &&
                    (features&needed)==needed) {
                    const vk::ImageSubresourceRange range{vk::ImageAspectFlagBits::eColor,0,1,0,1};
                    const std::array barriers{
                        vk::ImageMemoryBarrier{.srcAccessMask=vk::AccessFlagBits::eMemoryWrite,
                            .dstAccessMask=vk::AccessFlagBits::eTransferRead,
                            .oldLayout=vk::ImageLayout::eShaderReadOnlyOptimal,.newLayout=vk::ImageLayout::eTransferSrcOptimal,
                            .srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,
                            .image=frame->image,.subresourceRange=range},
                        vk::ImageMemoryBarrier{.srcAccessMask=vk::AccessFlagBits::eNone,
                            .dstAccessMask=vk::AccessFlagBits::eTransferWrite,
                            .oldLayout=vk::ImageLayout::eColorAttachmentOptimal,.newLayout=vk::ImageLayout::eTransferDstOptimal,
                            .srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,
                            .image=swapchain_image,.subresourceRange=range}};
                    cmdbuf.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
                        vk::PipelineStageFlagBits::eTransfer,{}, {}, {},barriers);
                    const vk::ImageBlit blit{
                        .srcSubresource={vk::ImageAspectFlagBits::eColor,0,0,1},
                        .srcOffsets=std::array{vk::Offset3D{0,0,0},vk::Offset3D{s32(frame->width),s32(frame->height),1}},
                        .dstSubresource={vk::ImageAspectFlagBits::eColor,0,0,1},
                        .dstOffsets=std::array{vk::Offset3D{0,0,0},vk::Offset3D{s32(extent.width),s32(extent.height),1}}};
                    cmdbuf.blitImage(frame->image,vk::ImageLayout::eTransferSrcOptimal,
                        swapchain_image,vk::ImageLayout::eTransferDstOptimal,blit,vk::Filter::eLinear);
                    const vk::ImageMemoryBarrier restore{
                        .srcAccessMask=vk::AccessFlagBits::eTransferRead,.dstAccessMask=vk::AccessFlagBits::eShaderRead,
                        .oldLayout=vk::ImageLayout::eTransferSrcOptimal,.newLayout=vk::ImageLayout::eShaderReadOnlyOptimal,
                        .srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED,
                        .image=frame->image,.subresourceRange=range};
                    cmdbuf.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
                        vk::PipelineStageFlagBits::eFragmentShader,{}, {}, {},restore);
                    direct_present=true;
                    static bool reported=false;
                    if (!reported) {reported=true;LOG_INFO(Render_Vulkan,"BACHATA_ANDROID_DIRECT_FINAL_BLIT");}
                }
            }
        }
#endif
        if (!direct_present)
            ImGui::Core::Render(cmdbuf, swapchain_image_view, swapchain.GetExtent());''')
    edit(pp,"""            swapchain_copied_for_screenshot ? vk::AccessFlagBits::eTransferRead
                                            : vk::AccessFlagBits::eColorAttachmentWrite;""",
         """            direct_present ? vk::AccessFlagBits::eTransferWrite :
            swapchain_copied_for_screenshot ? vk::AccessFlagBits::eTransferRead
                                            : vk::AccessFlagBits::eColorAttachmentWrite;""")
    edit(pp,"""        const vk::ImageLayout post_old_layout = swapchain_copied_for_screenshot""",
         """        const vk::ImageLayout post_old_layout = direct_present ? vk::ImageLayout::eTransferDstOptimal :
                                                    swapchain_copied_for_screenshot""")
    # The swapchain acquire semaphore must guard transfer writes too.
    return {"descriptor":"complete load-mask, distinct R128/depth, bounds","present":"verified opaque fullscreen direct blit; otherwise original ImGui path","cache":"reset partial preload; no SRT or scheduler changes"}
