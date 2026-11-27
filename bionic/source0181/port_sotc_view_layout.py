"""Repair exact backing/subresource layout publication and FEX attachment replay.
Keep the PC #308 renderer, two-stage binding, all draws and original FEX memory.
A descriptor must name the layout of its actual VkImageView, not the last
transition issued against some other mip or another sample-count backing.
"""
from pathlib import Path

HEADER=r'''#pragma once
#include <cstdint>
#include <optional>
namespace BachataViewLayout {
template<class Layout,class States>
std::optional<Layout> Uniform(Layout global,const States& states,
    std::uint32_t levels,std::uint32_t layers,std::uint32_t mip,
    std::uint32_t layer,std::uint32_t nmips,std::uint32_t nlayers) {
    if(!nmips||!nlayers||mip>=levels||layer>=layers||
       nmips>levels-mip||nlayers>layers-layer) return {};
    if(states.empty()) return global;
    if(states.size()!=std::uint64_t(levels)*layers) return {};
    const auto first=states[std::uint64_t(mip)*layers+layer].layout;
    for(std::uint32_t m=mip;m<mip+nmips;++m)
        for(std::uint32_t l=layer;l<layer+nlayers;++l)
            if(states[std::uint64_t(m)*layers+l].layout!=first) return {};
    return first;
}
}
'''
METHOD=r'''void Rasterizer::RefreshImageLayouts(RenderState* state,u64* token) {
    if (!BachataSotcLod::Enabled()) return;
    using BoundView=VideoCore::TextureCache::BoundView;
    using Layout=vk::ImageLayout;
    std::array<BoundView,Shader::NUM_IMAGES+Shader::NUM_IMAGE_ARRAY_DESCRIPTORS> resolved{};
    const auto exact=[](const BoundView& b) {
        const auto& r=b.view->info.range;
        const auto& res=b.image->info.resources;
        return BachataViewLayout::Uniform(b.backing->state.layout,b.backing->subresource_states,
            res.levels,res.layers,r.base.level,r.base.layer,r.extent.levels,r.extent.layers);
    };
    const auto compatible=[](const BoundView& b,Layout layout) {
        if(layout==Layout::eGeneral) return true;
        if(b.view->info.is_storage) return false;
        switch(layout) {
        case Layout::eShaderReadOnlyOptimal:
        case Layout::eDepthStencilReadOnlyOptimal:
        case Layout::eAttachmentFeedbackLoopOptimalEXT:
        case Layout::eReadOnlyOptimal:
            return true;
        case Layout::eDepthReadOnlyOptimal:
        case Layout::eDepthReadOnlyStencilAttachmentOptimal:
            return LiverpoolToVK::IsFormatDepthCompatible(b.view->info.format);
        case Layout::eStencilReadOnlyOptimal:
        case Layout::eDepthAttachmentStencilReadOnlyOptimal:
            return LiverpoolToVK::IsFormatStencilCompatible(b.view->info.format);
        default: return false;
        }
    };
    for(size_t i=0;i<image_infos.size();++i) {
        if(const auto id=image_info_images[i];id) {
            resolved[i]=texture_cache.FindBoundView(id,image_infos[i].imageView);
            ASSERT_MSG(resolved[i].backing,"SotC descriptor lost its live view/backing");
        }
    }
    for(size_t i=0;i<image_infos.size();++i) {
        auto& b=resolved[i];
        if(!b.backing) continue;
        const auto layout=exact(b);
        if(layout && compatible(b,*layout)) continue;
        // A view covering divergent mip/layer layouts cannot be described by
        // the last-transition state. Normalize this actual backing, and all
        // attached views of it, without changing the authoritative backing.
        bool storage=false,color=false;
        for(size_t j=0;j<image_infos.size();++j)
            if(resolved[j].backing==b.backing) storage|=resolved[j].view->info.is_storage;
        std::array<RenderAttachment*,9> attachments{};
        size_t n=0;
        if(state) {
            const auto add=[&](VideoCore::ImageId id,RenderAttachment& a,bool is_color) {
                if(!id||!a.image_view) return;
                const auto v=texture_cache.FindBoundView(id,a.image_view);
                ASSERT_MSG(v.backing,"SotC attachment lost its live view/backing");
                if(v.backing==b.backing) {
                    attachments[n++]=&a;color|=is_color;
                }
            };
            for(u32 cb=0;cb<state->num_color_attachments;++cb)
                add(cb_descs[cb].first,state->color_attachments[cb],true);
            add(db_desc.first,state->depth_stencil_attachment,false);
        }
        const auto common=color&&!storage&&instance.IsAttachmentFeedbackLoopLayoutSupported()
            ?Layout::eAttachmentFeedbackLoopOptimalEXT:Layout::eGeneral;
        auto* previous=b.image->backing;
        b.image->backing=b.backing;
        needs_barrier|=runtime.Transit(b.image,common,vk::PipelineStageFlagBits2::eAllCommands,
            vk::AccessFlagBits2::eMemoryRead|vk::AccessFlagBits2::eMemoryWrite);
        b.image->backing=previous;
        for(size_t a=0;a<n;++a) attachments[a]->image_layout=common;
        if(n) {
            attachment_feedback_loop|=color;
            if(token) *token=0;
            if(active_target_memo) active_target_memo->valid=false;
        }
    }
    // All transitions are now decided. Publish each view's own final layout.
    for(size_t i=0;i<image_infos.size();++i) {
        if(!resolved[i].backing) continue;
        const auto layout=exact(resolved[i]);
        ASSERT_MSG(layout&&compatible(resolved[i],*layout),"SotC descriptor layout not uniform");
        image_infos[i].imageLayout=*layout;
    }
}'''

def apply(root):
    src=Path(root)/'src/video_core'
    def edit(rel,a,b,n=1):
        p=src/rel;s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f'{rel}: expected {n} anchors, found {s.count(a)}: {a[:100]}')
        p.write_text(s.replace(a,b))
    (src/'renderer_vulkan/bachata_view_layout.h').write_text(HEADER)
    h='texture_cache/texture_cache.h';c='texture_cache/texture_cache.cpp'
    edit(h,'    struct AttachmentReplay {','''    struct BoundView {
        Image* image{};
        Image::BackingImage* backing{};
        const ImageView* view{};
    };
    BoundView FindBoundView(ImageId id,vk::ImageView handle);
    struct AttachmentReplay {''')
    edit(c,'bool TextureCache::CheckAttachment(AttachmentReplay& entry,bool record) {','''TextureCache::BoundView TextureCache::FindBoundView(ImageId id,vk::ImageView handle) {
    // The draw owns these views through submission; DeleteImage defers slot
    // reclamation until the scheduler tick retires, even after unregistering.
    std::scoped_lock lock{mutex};
    if(!id||!handle||!slot_images.IsAllocated(id)) return {};
    auto& image=slot_images[id];
    const auto find=[&](Image::BackingImage& backing)->BoundView {
        const auto check=[&](size_t n)->BoundView {
            const auto view_id=backing.image_view_ids[n];
            if(!slot_image_views.IsAllocated(view_id)) return {};
            const auto& view=slot_image_views[view_id];
            if(*view.image_view==handle) return {&image,&backing,&view};
            return {};
        };
        if(backing.last_view<backing.image_view_ids.size()) {
            auto hit=check(backing.last_view);if(hit.backing)return hit;
        }
        for(size_t n=0;n<backing.image_view_ids.size();++n) {
            auto hit=check(n);if(hit.backing)return hit;
        }
        return {};
    };
    if(image.backing) {
        auto hit=find(*image.backing);if(hit.backing)return hit;
    }
    for(auto& backing:image.backing_images) if(&backing!=image.backing) {
        auto hit=find(backing);if(hit.backing)return hit;
    }
    return {};
}

bool TextureCache::CheckAttachment(AttachmentReplay& entry,bool record) {''')
    h='renderer_vulkan/vk_rasterizer.h';c='renderer_vulkan/vk_rasterizer.cpp'
    edit(h,'    void RefreshImageLayouts();','    void RefreshImageLayouts(RenderState* state=nullptr,u64* token=nullptr);')
    edit(c,'#include "video_core/renderer_vulkan/vk_rasterizer.h"',
         '#include "video_core/renderer_vulkan/vk_rasterizer.h"\n#include "video_core/renderer_vulkan/bachata_view_layout.h"')
    p=src/c;s=p.read_text();a=s.index('void Rasterizer::RefreshImageLayouts() {')
    b=s.index('{',a)+1;depth=1
    while depth:
        depth+=(s[b]=='{')-(s[b]=='}');b+=1
    p.write_text(s[:a]+METHOD+s[b:])
    edit(c,'    const auto& state=BeginRenderingFast(pipeline,storage,render_token);\n    RefreshImageLayouts();',
         '    RenderState state=BeginRenderingFast(pipeline,storage,render_token);\n    RefreshImageLayouts(&state,&render_token);',2)
    edit(c,'''    if (needs_barrier) {
        runtime.FlushBarriers();
    }

    scheduler.EndRendering();
    pipeline->BindResources(set_writes, push_data);''','''    RefreshImageLayouts();
    if (needs_barrier) {
        runtime.FlushBarriers();
    }

    scheduler.EndRendering();
    pipeline->BindResources(set_writes, push_data);''',2)
    # Registry epochs track cache lifetime, not a concurrent FEX VMA mutation.
    edit(h,'u64 render_serial{},color_serial{},registry{},state_registry{},meta{},gpu{},token{};',
         'u64 render_serial{},color_serial{},registry{},state_registry{},meta{},gpu{},token{},mapping{};')
    edit(h,'        std::array<VideoCore::TextureCache::AttachmentReplay,9> attachments{};',
         '        std::array<VideoCore::TextureCache::ImageDesc,9> recorded_descs{};\n        std::array<VideoCore::TextureCache::AttachmentReplay,9> attachments{};')
    edit(c,'''        const auto color=key.mrt_mask?liverpool->DrawRelSerial(L::RelColor):0;
        if(memo.prepared && memo.render_serial==render && memo.color_serial==color &&''','''        const auto color=key.mrt_mask?liverpool->DrawRelSerial(L::RelColor):0;
        const auto mapping=memory->MappingGeneration();
        if(memo.prepared && !(mapping&1) && memo.mapping==mapping &&
           memo.render_serial==render && memo.color_serial==color &&''')
    edit(c,'        memo.render_serial=render;memo.color_serial=color;',
         '        memo.render_serial=render;memo.color_serial=color;memo.mapping=mapping;')
    edit(c,'        memo.prepared=true;','        memo.prepared=!(memo.mapping&1) && memo.mapping==memory->MappingGeneration();')
    edit(c,'    if(m.reused && m.valid && same_ids && texture_cache.ReuseAttachmentSet(',
         '    if(m.reused && m.valid && same_ids && !(m.mapping&1) &&\n       m.mapping==memory->MappingGeneration() && texture_cache.ReuseAttachmentSet(')
    edit(c,'    m.valid=m.prepared && !attachment_feedback_loop &&',
         '    m.valid=m.prepared && !(m.mapping&1) && m.mapping==memory->MappingGeneration() && !attachment_feedback_loop &&')
    edit(c,'            m.attachments[i]={.id=cb_descs[i].first,.desc=&cb_descs[i].second,',
         '            m.recorded_descs[i]=cb_descs[i].second;\n            m.attachments[i]={.id=cb_descs[i].first,.desc=&m.recorded_descs[i],')
    edit(c,'        m.attachments[8]={.id=db_desc.first,.desc=&db_desc.second,.view=a.image_view,',
         '        m.recorded_descs[8]=db_desc.second;\n        m.attachments[8]={.id=db_desc.first,.desc=&m.recorded_descs[8],.view=a.image_view,')
