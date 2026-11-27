#!/usr/bin/env python3
"""SotC PC 732cb37 depth-read/stencil-write descriptor contract."""
from pathlib import Path

def apply(root):
    src=Path(root)/'src'
    def edit(rel,old,new,n=1):
        p=src/rel
        s=p.read_text()
        if s.count(old)!=n:
            raise RuntimeError(f'{rel}: expected {n} anchors, found {s.count(old)}: {old[:120]}')
        p.write_text(s.replace(old,new))
    r='video_core/renderer_vulkan/vk_rasterizer.cpp'
    h='video_core/renderer_vulkan/vk_rasterizer.h'
    t='video_core/texture_cache/texture_cache.cpp'
    edit(t,'#include "video_core/texture_cache/texture_cache.h"','#include "video_core/texture_cache/texture_cache.h"\n#include "video_core/sotc_lod_stats.h"')
    edit(h,'    Pipeline::DescriptorWrites set_writes;', '''    std::array<VideoCore::ImageId, Shader::NUM_IMAGES + Shader::NUM_IMAGE_ARRAY_DESCRIPTORS> image_info_images{};
    void RefreshImageLayouts();
    Pipeline::DescriptorWrites set_writes;''')
    edit(r,'    image_infos.clear();','    image_infos.clear();\n    image_info_images.fill({});')
    edit(r,'    const auto state = BeginRenderingFast(pipeline);','    const auto state = BeginRenderingFast(pipeline);\n    RefreshImageLayouts();',2)
    edit(r,'void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {','''// Exact layout contract shared by sampling and stencil attachment writes.
static constexpr vk::PipelineStageFlags2 kDepthReadOnlyStencilStages =
    vk::PipelineStageFlagBits2::eAllCommands;
static constexpr vk::AccessFlags2 kDepthReadOnlyStencilAccess =
    vk::AccessFlagBits2::eDepthStencilAttachmentRead |
    vk::AccessFlagBits2::eDepthStencilAttachmentWrite |
    vk::AccessFlagBits2::eShaderRead;

void Rasterizer::RefreshImageLayouts() {
    if (!BachataSotcLod::Enabled()) return;
    for (size_t i=0; i<image_infos.size(); ++i) {
        if (const auto id=image_info_images[i]; id) {
            image_infos[i].imageLayout=texture_cache.GetImage(id).backing->state.layout;
        }
    }
}

void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {''')
    edit(r,'                image_infos.emplace_back(VK_NULL_HANDLE,*view,image.backing->state.layout);','''                image_infos.emplace_back(VK_NULL_HANDLE,*view,image.backing->state.layout);
                image_info_images[image_infos.size()-1]=image_id;''')
    edit(r,'''                    const auto new_layout = image.info.props.is_depth
                                                ? vk::ImageLayout::eDepthStencilReadOnlyOptimal
                                                : vk::ImageLayout::eShaderReadOnlyOptimal;
                    needs_barrier |= runtime.Transit(
                        &image, new_layout, vk::PipelineStageFlagBits2::eAllCommands,
                        vk::AccessFlagBits2::eShaderRead, desc.view_info.range);''','''                    const bool depth_sampled_as_attachment = BachataSotcLod::Enabled() &&
                        stage.sw_stage != Shader::SwStage::Compute && image.info.props.has_stencil &&
                        image_id == db_desc.first && liverpool->DrawRegs().depth_control.stencil_enable &&
                        !db_desc.second.view_info.is_storage &&
                        LiverpoolToVK::IsFormatDepthCompatible(desc.view_info.format) &&
                        !LiverpoolToVK::IsFormatStencilCompatible(desc.view_info.format);
                    if (depth_sampled_as_attachment) {
                        needs_barrier |= runtime.Transit(
                            &image, vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal,
                            kDepthReadOnlyStencilStages, kDepthReadOnlyStencilAccess,
                            desc.view_info.range);
                    } else {
                        const auto new_layout = image.info.props.is_depth
                                                    ? vk::ImageLayout::eDepthStencilReadOnlyOptimal
                                                    : vk::ImageLayout::eShaderReadOnlyOptimal;
                        needs_barrier |= runtime.Transit(
                            &image, new_layout, vk::PipelineStageFlagBits2::eAllCommands,
                            vk::AccessFlagBits2::eShaderRead, desc.view_info.range);
                    }''')
    edit(r,'''            image_infos.emplace_back(VK_NULL_HANDLE, *image_view.image_view,
                                     image.backing->state.layout);''','''            image_infos.emplace_back(VK_NULL_HANDLE, *image_view.image_view,
                                     image.backing->state.layout);
            image_info_images[image_infos.size()-1]=image_id;''')
    edit(r,'''        needs_barrier |= runtime.Transit(&image, new_layout,
                                         vk::PipelineStageFlagBits2::eEarlyFragmentTests |
                                             vk::PipelineStageFlagBits2::eLateFragmentTests,
                                         vk::AccessFlagBits2::eDepthStencilAttachmentWrite |
                                             vk::AccessFlagBits2::eDepthStencilAttachmentRead,
                                         desc.view_info.range);''','''        if (BachataSotcLod::Enabled() &&
            new_layout==vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal) {
            needs_barrier |= runtime.Transit(&image,new_layout,kDepthReadOnlyStencilStages,
                                             kDepthReadOnlyStencilAccess,desc.view_info.range);
        } else {
            needs_barrier |= runtime.Transit(&image, new_layout,
                                             vk::PipelineStageFlagBits2::eEarlyFragmentTests |
                                                 vk::PipelineStageFlagBits2::eLateFragmentTests,
                                             vk::AccessFlagBits2::eDepthStencilAttachmentWrite |
                                                 vk::AccessFlagBits2::eDepthStencilAttachmentRead,
                                             desc.view_info.range);
        }''')
    edit(t,'''    const auto access=depth ?
        vk::AccessFlagBits2::eDepthStencilAttachmentWrite|vk::AccessFlagBits2::eDepthStencilAttachmentRead :
        vk::AccessFlagBits2::eColorAttachmentWrite|vk::AccessFlagBits2::eColorAttachmentRead;
    const auto stage=depth ?
        vk::PipelineStageFlagBits2::eEarlyFragmentTests|vk::PipelineStageFlagBits2::eLateFragmentTests :
        vk::PipelineStageFlags2{vk::PipelineStageFlagBits2::eColorAttachmentOutput};''','''    const bool mixed=depth && BachataSotcLod::Enabled() &&
        layout==vk::ImageLayout::eDepthReadOnlyStencilAttachmentOptimal;
    const auto access=depth ?
        vk::AccessFlagBits2::eDepthStencilAttachmentWrite|vk::AccessFlagBits2::eDepthStencilAttachmentRead|
            (mixed ? vk::AccessFlags2{vk::AccessFlagBits2::eShaderRead} : vk::AccessFlags2{}) :
        vk::AccessFlagBits2::eColorAttachmentWrite|vk::AccessFlagBits2::eColorAttachmentRead;
    const auto stage=depth ?
        (mixed ? vk::PipelineStageFlags2{vk::PipelineStageFlagBits2::eAllCommands} :
        vk::PipelineStageFlagBits2::eEarlyFragmentTests|vk::PipelineStageFlagBits2::eLateFragmentTests) :
        vk::PipelineStageFlags2{vk::PipelineStageFlagBits2::eColorAttachmentOutput};''')
    return {'mixed_depth_stencil_layout':True,'descriptor_layout_refresh':True,'attachment_memo_contract':True}
