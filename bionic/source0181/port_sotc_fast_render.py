"""SotC draw-state and resource fast paths with exact input validation.

Adapt the donor depth/GBuffer/fast bind principles, retain the 0.18.1 cache
and synchronization semantics; fall back for any dirty, aliased or cleared target.
"""
from pathlib import Path

def apply(root):
    def edit(rel,a,b,n=1):
        p=root/"src"/rel;s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f"SotC fast path {rel}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    t="video_core/texture_cache/"
    v="video_core/renderer_vulkan/"
    h=t+"texture_cache.h"
    c=t+"texture_cache.cpp"
    edit(h,"    /// Updates image contents if it was modified by CPU.",
         """    // Slot IDs can be recycled; registry changes invalidate all target memos.
    u64 TargetRegistryEpoch() const { return target_registry_epoch.load(std::memory_order_acquire); }
    u64 TargetMetaEpoch() const { return target_meta_epoch.load(std::memory_order_acquire); }
    bool ReusePreparedTargets(std::span<const ImageId> ids, u64 epoch);
    bool ReuseAttachment(ImageId id, const ImageDesc& desc, vk::Image backing,
                         vk::ImageLayout layout, bool depth, u32 samples);
    /// Updates image contents if it was modified by CPU.""")
    edit(h,"    std::mutex samplers_mutex;",
         """    std::atomic<u64> target_registry_epoch{1};
    std::atomic<u64> target_meta_epoch{1};
    std::mutex samplers_mutex;""")
    edit(h,"            it.value().clear_mask = -1;",
         """            if (it.value().clear_mask != -1) ++target_meta_epoch;
            it.value().clear_mask = -1;""")
    edit(h,"            if (is_clear) {\n                it.value().clear_mask",
         """            const auto previous=it.value().clear_mask;
            if (is_clear) {
                it.value().clear_mask""")
    edit(h,"                it.value().clear_mask &= ~(1u << slice);\n            }\n            return true;",
         """                it.value().clear_mask &= ~(1u << slice);
            }
            if (previous != it.value().clear_mask) ++target_meta_epoch;
            return true;""")
    edit(c,"void TextureCache::RegisterImage(ImageId image_id) {",
         """void TextureCache::RegisterImage(ImageId image_id) {
    target_registry_epoch.fetch_add(1,std::memory_order_release);""")
    edit(c,"void TextureCache::UnregisterImage(ImageId image_id) {",
         """void TextureCache::UnregisterImage(ImageId image_id) {
    target_registry_epoch.fetch_add(1,std::memory_order_release);""")
    edit(c,"        surface_metas.emplace(address, info);",
         "        ++target_meta_epoch;\n        surface_metas.emplace(address, info);")
    edit(c,"        entry = info;\n        return;",
         "        ++target_meta_epoch;\n        entry = info;\n        return;")
    edit(c,"        surface_metas.erase(address);",
         "        ++target_meta_epoch;\n        surface_metas.erase(address);")
    # Store the linked stencil identity, and revalidate it before reuse.
    edit(t+"image.h","    u64 depth_uid{};",
         """    u64 depth_uid{};
    ImageId sotc_stencil_id{};
    u64 sotc_stencil_uid{};""")
    edit(c,"        stencil_image.AssociateDepth(image_id, image.image_uid);",
         """        stencil_image.AssociateDepth(image_id, image.image_uid);
        image.sotc_stencil_id=stencil_id;
        image.sotc_stencil_uid=stencil_image.image_uid;""")
    edit(c,"ImageView& TextureCache::FindRenderTarget(ImageId image_id, const ImageDesc& desc) {",
         """bool TextureCache::ReusePreparedTargets(std::span<const ImageId> ids,u64 epoch) {
    std::scoped_lock lk{mutex};
    if (TargetRegistryEpoch()!=epoch) return false;
    for (const auto id:ids) {
        if (!id) continue;
        if (!slot_images.IsAllocated(id)) return false;
        const auto& img=slot_images[id];
        if (False(img.flags & ImageFlagBits::Registered) || img.binding.needs_rebind ||
            True(img.flags & ImageFlagBits::Dirty)) return false;
    }
    for (const auto id:ids) {
        if (!id) continue;
        auto& img=slot_images[id];
        img.binding.is_target=1;
        img.tick_accessed_last=scheduler.CurrentTick();
        TouchImage(img);
    }
    return true;
}

bool TextureCache::ReuseAttachment(ImageId id,const ImageDesc& desc,vk::Image backing,
                                   vk::ImageLayout layout,bool depth,u32 samples) {
    std::scoped_lock lk{mutex};
    if (!id || !slot_images.IsAllocated(id)) return false;
    auto& img=slot_images[id];
    if (!img.backing || img.GetImage()!=backing || img.backing->num_samples!=samples ||
        False(img.flags & ImageFlagBits::Registered) || !img.SafeToDownload() ||
        img.binding.needs_rebind || img.binding.is_bound || img.usage.vo_surface ||
        img.track_addr!=img.info.guest_address ||
        img.track_addr_end!=img.info.guest_address+img.info.guest_size)
        return false;
    if (!depth && readback_linear_images &&
        (!img.info.props.is_tiled || img.info.size.width<=8)) return false;

    const auto meta_matches=[&](VAddr address) {
        if (!address) return true;
        const auto it=surface_metas.find(address);
        return it!=surface_metas.end() && it.value().owner_uid==img.image_uid &&
               it.value().owner_id==id && it.value().num_samples==img.info.num_samples &&
               !IsMetaCleared(address,desc.view_info.range.base.layer);
    };
    if (depth) {
        if (img.info.meta_info.htile_addr!=desc.info.meta_info.htile_addr ||
            !meta_matches(desc.info.meta_info.htile_addr)) return false;
    } else if (img.info.meta_info.cmask_addr!=desc.info.meta_info.cmask_addr ||
               img.info.meta_info.fmask_addr!=desc.info.meta_info.fmask_addr ||
               !meta_matches(desc.info.meta_info.cmask_addr) ||
               !meta_matches(desc.info.meta_info.fmask_addr)) return false;

    const auto access=depth ?
        vk::AccessFlagBits2::eDepthStencilAttachmentWrite|vk::AccessFlagBits2::eDepthStencilAttachmentRead :
        vk::AccessFlagBits2::eColorAttachmentWrite|vk::AccessFlagBits2::eColorAttachmentRead;
    const auto stage=depth ?
        vk::PipelineStageFlagBits2::eEarlyFragmentTests|vk::PipelineStageFlagBits2::eLateFragmentTests :
        vk::PipelineStageFlags2{vk::PipelineStageFlagBits2::eColorAttachmentOutput};
    const auto same=[&](const Image::State& s) {
        return s.layout==layout && s.access_mask==access && s.pl_stage==stage;
    };
    const auto range=desc.view_info.range;
    const bool partial=range.base!=SubresourceBase{} || range.extent!=img.info.resources;
    if (!same(img.backing->state)) return false;
    const auto& states=img.backing->subresource_states;
    if (partial) {
        if (states.empty()) return false;
        for (u32 m=range.base.level;m<range.base.level+range.extent.levels;++m)
            for (u32 l=range.base.layer;l<range.base.layer+range.extent.layers;++l) {
                const auto idx=m*img.info.resources.layers+l;
                if (idx>=states.size() || !same(states[idx])) return false;
            }
    } else if (!states.empty()) return false;

    if (depth && desc.info.stencil_addr) {
        const auto sid=img.sotc_stencil_id;
        if (!sid || !slot_images.IsAllocated(sid)) return false;
        auto& stencil=slot_images[sid];
        if (stencil.image_uid!=img.sotc_stencil_uid ||
            stencil.info.guest_address!=desc.info.stencil_addr ||
            stencil.depth_id!=id || stencil.depth_uid!=img.image_uid)
            return false;
        TouchImage(stencil);
    }
    TouchImage(img);
    return true;
}

ImageView& TextureCache::FindRenderTarget(ImageId image_id, const ImageDesc& desc) {""")
    # Do not elide barriers, resource tracking or uploads in BindResources.
    # Only avoid redundant Vulkan descriptor and push-constant writes after
    # the complete descriptors have actually been resolved.
    r=v+"vk_rasterizer.h"
    edit(r,"    RenderState BeginRendering(const GraphicsPipeline* pipeline);",
         """    RenderState BeginRendering(const GraphicsPipeline* pipeline);
    RenderState BeginRenderingFast(const GraphicsPipeline* pipeline);
    void FastBindResolved(const GraphicsPipeline* pipeline);
    void RememberResolvedBind(const GraphicsPipeline* pipeline);""")
    edit(r,"    Pipeline::DescriptorWrites set_writes;",
         """    struct TargetMemo {
        std::vector<u8> key, scratch, state_key;
        u64 registry{}, state_registry{}, meta{};
        bool prepared{}, reused{}, valid{};
        RenderState state{};
        std::array<vk::Image,9> backings{};
        std::array<VideoCore::ImageId,9> ids{};
    } target_memo;
    struct BindMemo {
        const GraphicsPipeline* pipeline{};
        u64 tick{}, epoch{};
        bool valid{};
        std::vector<u8> current, previous;
    } bind_memo;
    Pipeline::DescriptorWrites set_writes;""")
    edit(v+"vk_scheduler.h","    void EndRendering();",
         """    void EndRendering();
    bool IsRendering() const { return is_rendering; }
    u64 RenderEpoch() const { return render_epoch; }""")
    edit(v+"vk_scheduler.h","    bool is_rendering = false;",
         "    bool is_rendering = false;\n    u64 render_epoch{};")
    edit(v+"vk_scheduler.cpp","    is_rendering = false;\n    CommandBuffer().endRendering();",
         "    is_rendering = false;\n    ++render_epoch;\n    CommandBuffer().endRendering();")
    r=v+"vk_rasterizer.cpp"
    edit(r,"    const auto& regs = liverpool->regs;\n    if (regs.color_control.degamma_enable)",
         """    const auto& regs = liverpool->regs;
    auto& memo=target_memo;
    memo.reused=false;
    if (BachataSotcLod::Enabled()) {
        auto& k=memo.scratch;
        k.clear();
        const auto add=[&](const auto& value) {
            const auto old=k.size();
            k.resize(old+sizeof(value));
            std::memcpy(k.data()+old,&value,sizeof(value));
        };
        add(key.mrt_mask);add(key.color_samples);add(regs.color_control);
        add(regs.color_target_mask);add(regs.color_buffers);
        add(regs.depth_control);add(regs.depth_buffer);add(regs.depth_view);
        add(regs.depth_render_control);add(regs.depth_htile_data_base);
        add(regs.depth_clear);add(regs.stencil_clear);
        add(liverpool->last_cb_extent);add(liverpool->last_db_extent);
        if (memo.prepared && k==memo.key &&
            texture_cache.ReusePreparedTargets(memo.ids,memo.registry)) {
            for (const auto id:memo.ids) if (id) bound_images.emplace_back(id);
            memo.reused=true;
            return;
        }
        memo.key.swap(k);
        memo.prepared=false;
        memo.valid=false;
    }
    if (regs.color_control.degamma_enable)""")
    edit(r,"        db_desc.first = {};\n    }\n}\n\nstatic std::pair<u32, u32> GetDrawOffsets",
         """        db_desc.first = {};
    }
    if (BachataSotcLod::Enabled()) {
        memo.ids.fill({});
        for (u32 i=0;i<std::bit_width(key.mrt_mask);++i) memo.ids[i]=cb_descs[i].first;
        memo.ids[8]=db_desc.first;
        memo.registry=texture_cache.TargetRegistryEpoch();
        memo.prepared=true;
    }
}

static std::pair<u32, u32> GetDrawOffsets""")
    edit(r,"const auto state = BeginRendering(pipeline);",
         "const auto state = BeginRenderingFast(pipeline);",2)
    edit(r,"    pipeline->BindResources(set_writes, push_data);\n    UpdateDynamicState",
         "    FastBindResolved(pipeline);\n    UpdateDynamicState",2)
    edit(r,"    scheduler.BeginRendering(state);\n",
         "    scheduler.BeginRendering(state);\n    RememberResolvedBind(pipeline);\n",2)
    # Bind memo is valid only within the same active dynamic-rendering scope.
    # Dispatch resets it before any compute/host work can reuse the layouts.
    edit(r,"void Rasterizer::DispatchDirect() {",
         "void Rasterizer::DispatchDirect() {\n    bind_memo.valid=false;")
    # The exact signature varies; insert into the body using a guarded match.
    p=root/"src"/r;s=p.read_text()
    import re
    s,n=re.subn(r"(void Rasterizer::DispatchIndirect\([^\{]+\) \{)",r"\1\n    bind_memo.valid=false;",s,count=1)
    assert n==1
    p.write_text(s)
    edit(r,"RenderState Rasterizer::BeginRendering(const GraphicsPipeline* pipeline) {",
         """void Rasterizer::FastBindResolved(const GraphicsPipeline* pipeline) {
    auto& m=bind_memo;
    if (!BachataSotcLod::Enabled()) {
        m.valid=false;
        pipeline->BindResources(set_writes,push_data);
        return;
    }
    m.current.clear();
    const auto append=[&](const void* p,size_t n) {
        if (!n) return;
        const auto pos=m.current.size();
        m.current.resize(pos+n);
        std::memcpy(m.current.data()+pos,p,n);
    };
    append(&push_data,sizeof(push_data));
    bool supported=true;
    for (const auto& w:set_writes) {
        append(&w.dstBinding,sizeof(w.dstBinding));
        append(&w.dstArrayElement,sizeof(w.dstArrayElement));
        append(&w.descriptorType,sizeof(w.descriptorType));
        append(&w.descriptorCount,sizeof(w.descriptorCount));
        if (w.pNext || w.pTexelBufferView) {supported=false;break;}
        if (w.pBufferInfo) append(w.pBufferInfo,sizeof(vk::DescriptorBufferInfo)*w.descriptorCount);
        else if (w.pImageInfo) append(w.pImageInfo,sizeof(vk::DescriptorImageInfo)*w.descriptorCount);
        else if (w.descriptorCount) {supported=false;break;}
    }
    if (supported && m.valid && scheduler.IsRendering() &&
        m.pipeline==pipeline && m.tick==scheduler.CurrentTick() &&
        m.epoch==scheduler.RenderEpoch() && m.current==m.previous) return;
    pipeline->BindResources(set_writes,push_data);
    if (!supported) m.current.clear();
}
void Rasterizer::RememberResolvedBind(const GraphicsPipeline* pipeline) {
    auto& m=bind_memo;
    if (!BachataSotcLod::Enabled() || m.current.empty()) {m.valid=false;return;}
    m.pipeline=pipeline;
    m.tick=scheduler.CurrentTick();
    m.epoch=scheduler.RenderEpoch();
    m.previous.swap(m.current);
    m.valid=true;
}

RenderState Rasterizer::BeginRenderingFast(const GraphicsPipeline* pipeline) {
    if (!BachataSotcLod::Enabled()) return BeginRendering(pipeline);
    auto& m=target_memo;
    const auto& key=pipeline->GetGraphicsKey();
    if (m.reused && m.valid && m.state_key==m.key &&
        m.state_registry==texture_cache.TargetRegistryEpoch() &&
        m.meta==texture_cache.TargetMetaEpoch()) {
        bool ok=true;
        for (u32 cb=0;cb<m.state.num_color_attachments;++cb) {
            const auto& [id,desc]=cb_descs[cb];
            if (id!=m.ids[cb]) {ok=false;break;}
            if (id && !texture_cache.ReuseAttachment(id,desc,m.backings[cb],
                    m.state.color_attachments[cb].image_layout,false,key.color_samples[cb])) {
                ok=false;break;
            }
        }
        if (ok && db_desc.first) {
            const auto& [id,desc]=db_desc;
            // The depth target never changes samples through SetBackingSamples.
            ok=id==m.ids[8] && texture_cache.ReuseAttachment(id,desc,m.backings[8],
                m.state.depth_stencil_attachment.image_layout,true,
                texture_cache.GetImage(id).info.num_samples);
        }
        if (ok) {
            attachment_feedback_loop=false;
            return m.state;
        }
    }
    auto state=BeginRendering(pipeline);
    m.valid=!attachment_feedback_loop &&
        !state.depth_stencil_attachment.depth_clear &&
        !state.depth_stencil_attachment.stencil_clear &&
        std::ranges::none_of(state.color_attachments,[](const auto& a){return a.is_clear!=0;});
    if (m.valid) {
        m.state=state;
        m.state_key=m.key;
        m.state_registry=texture_cache.TargetRegistryEpoch();
        m.meta=texture_cache.TargetMetaEpoch();
        m.backings.fill(vk::Image{});
        for (u32 i=0;i<state.num_color_attachments;++i) {
            if (const auto id=cb_descs[i].first;id) m.backings[i]=texture_cache.GetImage(id).GetImage();
        }
        if (const auto id=db_desc.first;id) m.backings[8]=texture_cache.GetImage(id).GetImage();
    }
    return state;
}

RenderState Rasterizer::BeginRendering(const GraphicsPipeline* pipeline) {""")
    return {"render_target_memo":"exact CB/DB registers, registry and meta epochs",
            "depth_gbuffer_fast_path":"full tracking, no clear, exact backing/barrier state, linked stencil validation",
            "resolved_fast_bind":"exact push data and descriptor payload, same command buffer/render epoch"}
