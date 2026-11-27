#!/usr/bin/env python3
"""Port PC #308 as a single CP -> draw -> cache -> scheduler protocol.
Reference: SotC PC 732cb37, Android PC074 effective tree. Adapt to FEX ownership,
existing draw-packet lifetime, image UID and subresource barriers. Keep slow path.
"""
from pathlib import Path


def apply(root):
    root=Path(root)/'src/video_core'
    def edit(rel,a,b,count=1):
        p=root/rel;s=p.read_text()
        assert s.count(a)==count,(rel,a[:100],s.count(a),count)
        p.write_text(s.replace(a,b))
    def method(rel,signature,transform):
        p=root/rel;s=p.read_text();a=s.index(signature);i=s.index('{',a);j=i+1;depth=1
        while depth:
            depth+=(s[j]=='{')-(s[j]=='}');j+=1
        p.write_text(s[:a]+transform(s[a:j])+s[j:])
    h='amdgpu/liverpool.h';c='amdgpu/liverpool.cpp'
    edit(h,'''        u32 index{};
        std::array<u32,DrawChunkWords> words{};''','''        u32 index{}, mask{}, offset{};''')
    edit(h,'        std::vector<DrawChunk> chunks;','''        std::vector<DrawChunk> chunks;
        std::vector<u32> changed_words;
        bool full_snapshot{};''')
    edit(h,'    std::bitset<DrawChunkCount> draw_dirty{};','''    // PC #308: dirty chunks are candidates, not the transported payload.
    // Producer owns the published values; consumer owns relevance and serials.
    std::array<u32,Regs::NumRegs> published_draw_regs{};
    std::array<std::array<u32,Regs::NumRegs>,3> draw_rel_masks{};
    std::array<u64,3> draw_rel_serial{1,1,1};
public:
    enum DrawRelevance : u32 { RelRender, RelColor, RelDynamic };
    void AddDrawRelevance(DrawRelevance group,const void* field,size_t bytes,u32 mask=~u32{0}) {
        ASSERT(OnDrawThread());
        const auto first=reinterpret_cast<const u8*>(field)-reinterpret_cast<const u8*>(&back_regs);
        ASSERT(first>=0 && first%4==0 && bytes && bytes%4==0 && size_t(first)+bytes<=sizeof(back_regs.reg_array));
        for(size_t d=first/4;d<(first+bytes)/4;++d) draw_rel_masks[group][d]|=mask;
    }
    u64 DrawRelSerial(DrawRelevance group) const { ASSERT(OnDrawThread());return draw_rel_serial[group]; }
private:
    std::bitset<DrawChunkCount> draw_dirty{};''')
    edit(c,'''            for(const auto& chunk:op.chunks)
                std::memcpy(&back_regs.reg_array[chunk.index*DrawChunkWords],
                            chunk.words.data(),sizeof(chunk.words));
            back_cb_extent=op.cb;back_db_extent=op.db;back_cs=op.cs;''','''            std::array<bool,3> changed{};
            for(const auto& chunk:op.chunks) {
                auto mask=chunk.mask;
                auto offset=chunk.offset;
                while(mask) {
                    const auto bit=static_cast<u32>(__builtin_ctz(mask));
                    const auto index=chunk.index*DrawChunkWords+bit;
                    const u32 value=op.changed_words[offset++];
                    const u32 delta=back_regs.reg_array[index]^value;
                    back_regs.reg_array[index]=value;
                    for(u32 group=0;group<changed.size();++group)
                        changed[group]|=(delta&draw_rel_masks[group][index])!=0;
                    mask&=mask-1;
                }
            }
            changed[RelColor]|=std::memcmp(&back_cb_extent,&op.cb,sizeof(op.cb))!=0;
            changed[RelRender]|=std::memcmp(&back_db_extent,&op.db,sizeof(op.db))!=0;
            for(u32 group=0;group<changed.size();++group)
                if(changed[group]||op.full_snapshot) ++draw_rel_serial[group];
            back_cb_extent=op.cb;back_db_extent=op.db;back_cs=op.cs;''')
    edit(c,'''    op.chunks.clear();
    if(!draw_snapshot_valid) {
        op.chunks.reserve(DrawChunkCount);
        for(u32 i=0;i<DrawChunkCount;++i) {
            auto& chunk=op.chunks.emplace_back();chunk.index=i;
            std::memcpy(chunk.words.data(),&regs.reg_array[i*DrawChunkWords],sizeof(chunk.words));
        }
        draw_snapshot_valid=true;
    } else {
        for(const auto i:draw_dirty_indices) {
            auto& chunk=op.chunks.emplace_back();chunk.index=i;
            std::memcpy(chunk.words.data(),&regs.reg_array[i*DrawChunkWords],sizeof(chunk.words));
        }
    }''','''    op.chunks.clear();op.changed_words.clear();
    op.full_snapshot=!draw_snapshot_valid;
    const auto publish=[&](u32 chunk) {
        const auto start=static_cast<u32>(op.changed_words.size());
        u32 mask=0;
        for(u32 bit=0;bit<DrawChunkWords;++bit) {
            const auto index=chunk*DrawChunkWords+bit;
            const auto value=regs.reg_array[index];
            if(op.full_snapshot || value!=published_draw_regs[index]) {
                mask|=u32{1}<<bit;
                op.changed_words.push_back(value);
                published_draw_regs[index]=value;
            }
        }
        if(mask) op.chunks.push_back({chunk,mask,start});
    };
    if(op.full_snapshot) {
        op.chunks.reserve(DrawChunkCount);
        op.changed_words.reserve(Regs::NumRegs);
        for(u32 i=0;i<DrawChunkCount;++i) publish(i);
        draw_snapshot_valid=true;
    } else {
        for(const auto i:draw_dirty_indices) publish(i);
    }''')
    # Image registry, GPU ownership, metadata, backing/view identity, then all-or-nothing replay.
    h='texture_cache/image.h';c='texture_cache/texture_cache.h'
    edit(h,'inline std::atomic<u64> sotc_mip_tail_gpu_epoch{1};','''inline std::atomic<u64> sotc_mip_tail_gpu_epoch{1};
inline std::atomic<u64> sotc_target_gpu_epoch{1};''')
    edit(h,'''    if (False(image.flags & ImageFlagBits::GpuModified) && SotcMipTailMode()) {''','''    if (False(image.flags & ImageFlagBits::GpuModified))
        sotc_target_gpu_epoch.fetch_add(1,std::memory_order_relaxed);
    if (False(image.flags & ImageFlagBits::GpuModified) && SotcMipTailMode()) {''')
    edit(c,'''    bool ReuseAttachment(ImageId id, const ImageDesc& desc, vk::Image backing,
                         vk::ImageLayout layout, bool depth, u32 samples);''','''    struct AttachmentReplay {
        ImageId id{};
        const ImageDesc* desc{};
        vk::Image backing{};
        vk::ImageView view{};
        u64 uid{};
        vk::ImageLayout layout{};
        bool depth{};
        u32 samples{};
    };
    bool ReuseAttachmentSet(std::span<AttachmentReplay> set,u64 registry,u64 gpu,u64 meta,bool record);
private:
    bool CheckAttachment(AttachmentReplay& entry,bool record);
public:''')
    c='texture_cache/texture_cache.cpp'
    edit(c,'''bool TextureCache::ReuseAttachment(ImageId id,const ImageDesc& desc,vk::Image backing,
                                   vk::ImageLayout layout,bool depth,u32 samples) {
    std::scoped_lock lk{mutex};
    if (!id || !slot_images.IsAllocated(id)) return false;
    auto& img=slot_images[id];
    if (!img.backing || img.GetImage()!=backing || img.backing->num_samples!=samples ||''','''bool TextureCache::CheckAttachment(AttachmentReplay& entry,bool record) {
    const auto id=entry.id;
    if (!id) return !entry.view;
    if (!entry.desc || !entry.view || !slot_images.IsAllocated(id)) return false;
    const auto& desc=*entry.desc;
    const auto layout=entry.layout;
    const bool depth=entry.depth;
    auto& img=slot_images[id];
    if (!img.backing) return false;
    if (record) {
        entry.uid=img.image_uid;entry.backing=img.GetImage();
        if(depth) entry.samples=img.info.num_samples;
    }
    if (img.image_uid!=entry.uid || img.GetImage()!=entry.backing || img.backing->num_samples!=entry.samples ||''')
    edit(c,'''    const auto meta_matches=[&](VAddr address) {''','''    // RenderState references the exact live VkImageView, not just its image.
    const auto& infos=img.backing->image_view_infos;
    const auto it_view=std::ranges::find(infos,desc.view_info);
    if(it_view==infos.end()) return false;
    const auto index=static_cast<size_t>(it_view-infos.begin());
    if(index>=img.backing->image_view_ids.size()) return false;
    const auto view_id=img.backing->image_view_ids[index];
    if(!slot_image_views.IsAllocated(view_id) || *slot_image_views[view_id].image_view!=entry.view) return false;
    const auto meta_matches=[&](VAddr address) {''')
    edit(c,'''        TouchImage(stencil);
    }
    TouchImage(img);
    return true;
}

ImageView& TextureCache::FindRenderTarget''','''    }
    return true;
}

bool TextureCache::ReuseAttachmentSet(std::span<AttachmentReplay> set,u64 registry,u64 gpu,u64 meta,bool record) {
    std::scoped_lock lock{mutex};
    if(registry!=TargetRegistryEpoch() || gpu!=sotc_target_gpu_epoch.load(std::memory_order_relaxed) ||
       meta!=TargetMetaEpoch()) return false;
    for(auto& entry:set) if(!CheckAttachment(entry,record)) return false;
    if(record) return true;
    // PC #308 Apply: validate every color/depth attachment before touching any.
    for(const auto& entry:set) {
        if(!entry.id) continue;
        auto& img=slot_images[entry.id];
        if(entry.depth) {
            img.usage.depth_target=1u;
            if(entry.desc->info.stencil_addr) TouchImage(slot_images[img.sotc_stencil_id]);
        } else img.usage.render_target=1u;
        TouchImage(img);
    }
    return true;
}

ImageView& TextureCache::FindRenderTarget''')
    # Two memo slots for depth-only and G-buffer; serials drive both target preparation and state.
    h='renderer_vulkan/vk_rasterizer.h';c='renderer_vulkan/vk_rasterizer.cpp'
    edit(h,'    RenderState BeginRenderingFast(const GraphicsPipeline* pipeline);','    const RenderState& BeginRenderingFast(const GraphicsPipeline* pipeline,RenderState& storage,u64& token);\n    void EnsureDrawRelevance();')
    edit(h,'''        std::vector<u8> key, scratch, state_key;
        u64 registry{}, state_registry{}, meta{};
        bool prepared{}, reused{}, valid{};
        RenderState state{};
        std::array<vk::Image,9> backings{};
        std::array<VideoCore::ImageId,9> ids{};
    } target_memo;''','''        u64 render_serial{},color_serial{},registry{},state_registry{},meta{},gpu{},token{};
        u32 mrt_mask{};
        std::array<u8,AmdGpu::NUM_COLOR_BUFFERS> samples{};
        bool prepared{},reused{},valid{};
        RenderState state{};
        std::array<VideoCore::TextureCache::AttachmentReplay,9> attachments{};
        std::array<VideoCore::ImageId,9> ids{};
        std::array<RenderTargetInfo,AmdGpu::NUM_COLOR_BUFFERS> cb{};
        RenderTargetInfo db{};
    };
    std::array<TargetMemo,2> target_memos{};
    TargetMemo* active_target_memo{};
    u64 next_render_token{};
    bool draw_relevance_ready{};''')
    edit(h,'''    mutable std::vector<u8> dynamic_inputs;
    mutable bool dynamic_inputs_valid{};''','''    mutable u64 dynamic_serial{};
    mutable std::array<vk::ColorComponentFlags,AmdGpu::NUM_COLOR_BUFFERS> dynamic_write_masks{};
    mutable bool dynamic_inputs_valid{},dynamic_feedback{},dynamic_indexed{};''')
    edit(c,'void Rasterizer::PrepareRenderState(const GraphicsPipeline* pipeline) {','''void Rasterizer::EnsureDrawRelevance() {
    if(draw_relevance_ready||!liverpool->OnDrawThread()) return;
    using L=AmdGpu::Liverpool;
    const auto& r=liverpool->DrawRegs();
    const auto add=[&](L::DrawRelevance group,const auto& field) {
        liverpool->AddDrawRelevance(group,&field,sizeof(field));
    };
    // Donor depth/render, color, and dynamic relevance; exact inputs of our
    // FEX renderer, including complete depth_control (conservative superset).
    add(L::RelRender,r.color_control);add(L::RelRender,r.depth_control);
    add(L::RelRender,r.depth_buffer);add(L::RelRender,r.depth_view);
    add(L::RelRender,r.depth_render_control);add(L::RelRender,r.depth_htile_data_base);
    add(L::RelRender,r.depth_clear);add(L::RelRender,r.stencil_clear);
    add(L::RelColor,r.color_buffers);add(L::RelColor,r.color_target_mask);
    add(L::RelDynamic,r.screen_scissor);add(L::RelDynamic,r.window_scissor);
    add(L::RelDynamic,r.generic_scissor);add(L::RelDynamic,r.window_offset);
    add(L::RelDynamic,r.polygon_control);add(L::RelDynamic,r.viewport_control);
    add(L::RelDynamic,r.viewports);add(L::RelDynamic,r.viewport_depths);
    add(L::RelDynamic,r.viewport_scissors);add(L::RelDynamic,r.clipper_control);
    add(L::RelDynamic,r.mode_control);add(L::RelDynamic,r.primitive_type);
    add(L::RelDynamic,r.depth_control);add(L::RelDynamic,r.depth_buffer);
    add(L::RelDynamic,r.depth_render_control);add(L::RelDynamic,r.depth_bounds_min);
    add(L::RelDynamic,r.depth_bounds_max);add(L::RelDynamic,r.poly_offset);
    add(L::RelDynamic,r.stencil_control);add(L::RelDynamic,r.stencil_ref_front);
    add(L::RelDynamic,r.stencil_ref_back);add(L::RelDynamic,r.enable_primitive_restart);
    add(L::RelDynamic,r.primitive_restart_index);add(L::RelDynamic,r.line_control);
    add(L::RelDynamic,r.blend_constants);
    draw_relevance_ready=true;
}

void Rasterizer::PrepareRenderState(const GraphicsPipeline* pipeline) {''')
    edit(c,'''    auto& memo=target_memo;
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
        add(liverpool->DrawCbExtent());add(liverpool->DrawDbExtent());
        if (memo.prepared && k==memo.key &&
            texture_cache.ReusePreparedTargets(memo.ids,memo.registry)) {
            for (const auto id:memo.ids) if (id) bound_images.emplace_back(id);
            memo.reused=true;
            return;
        }
        memo.key.swap(k);
        memo.prepared=false;
        memo.valid=false;
    }''','''    static const bool depth_enabled=[] {const char* v=std::getenv("SOTC_DEPTH_FAST");return !v||*v!='0';}();
    static const bool gbuffer_enabled=[] {const char* v=std::getenv("SOTC_GBUFFER_FAST");return !v||*v!='0';}();
    const bool enabled=BachataSotcLod::Enabled() && liverpool->OnDrawThread() &&
        (key.mrt_mask?gbuffer_enabled:depth_enabled);
    auto& memo=target_memos[key.mrt_mask!=0];
    const auto previous=active_target_memo;
    active_target_memo=enabled?&memo:nullptr;
    memo.reused=false;
    if(enabled) {
        EnsureDrawRelevance();
        using L=AmdGpu::Liverpool;
        const auto render=liverpool->DrawRelSerial(L::RelRender);
        const auto color=key.mrt_mask?liverpool->DrawRelSerial(L::RelColor):0;
        if(memo.prepared && memo.render_serial==render && memo.color_serial==color &&
           memo.mrt_mask==key.mrt_mask && memo.samples==key.color_samples &&
           texture_cache.ReusePreparedTargets(memo.ids,memo.registry)) {
            if(previous!=&memo) {cb_descs=memo.cb;db_desc=memo.db;}
            for(const auto id:memo.ids) if(id) bound_images.emplace_back(id);
            memo.reused=true;
            return;
        }
        memo.render_serial=render;memo.color_serial=color;
        memo.mrt_mask=key.mrt_mask;memo.samples=key.color_samples;
    }
    memo.prepared=false;memo.valid=false;''')
    edit(c,'''    if (BachataSotcLod::Enabled()) {
        memo.ids.fill({});''','''    if(enabled) {
        memo.cb=cb_descs;memo.db=db_desc;
        memo.ids.fill({});''')
    def rendering(old):
        return '''const RenderState& Rasterizer::BeginRenderingFast(const GraphicsPipeline* pipeline,
                                                  RenderState& storage,u64& token) {
    token=0;
    if(!active_target_memo) {storage=BeginRendering(pipeline);return storage;}
    auto& m=*active_target_memo;
    bool same_ids=db_desc.first==m.ids[8];
    for(u32 i=0;i<m.state.num_color_attachments;++i) same_ids&=cb_descs[i].first==m.ids[i];
    if(m.reused && m.valid && same_ids && texture_cache.ReuseAttachmentSet(m.attachments,m.state_registry,m.gpu,m.meta,false)) {
        attachment_feedback_loop=false;token=m.token;return m.state;
    }
    storage=BeginRendering(pipeline);
    const auto& key=pipeline->GetGraphicsKey();
    m.valid=m.prepared && !attachment_feedback_loop &&
        !storage.depth_stencil_attachment.depth_clear && !storage.depth_stencil_attachment.stencil_clear &&
        std::ranges::none_of(storage.color_attachments,[](const auto& a){return a.is_clear!=0;});
    for(u32 i=0;i<storage.num_color_attachments;++i)
        if(cb_descs[i].first!=m.ids[i]) m.prepared=m.valid=false;
    if(db_desc.first!=m.ids[8]) m.prepared=m.valid=false;
    if(m.valid) {
        m.attachments.fill({});
        for(u32 i=0;i<storage.num_color_attachments;++i) {
            const auto& a=storage.color_attachments[i];
            m.attachments[i]={.id=cb_descs[i].first,.desc=&cb_descs[i].second,
                              .view=a.image_view,.layout=a.image_layout,.samples=key.color_samples[i]};
        }
        const auto& a=storage.depth_stencil_attachment;
        m.attachments[8]={.id=db_desc.first,.desc=&db_desc.second,.view=a.image_view,
                          .layout=a.image_layout,.depth=true};
        m.state_registry=texture_cache.TargetRegistryEpoch();m.meta=texture_cache.TargetMetaEpoch();
        m.gpu=VideoCore::sotc_target_gpu_epoch.load(std::memory_order_relaxed);
        m.valid=texture_cache.ReuseAttachmentSet(m.attachments,m.state_registry,m.gpu,m.meta,true);
        if(m.valid) {
            m.state=storage;m.token=++next_render_token;token=m.token;
            return m.state;
        }
    }
    return storage;
}'''
    method(c,'RenderState Rasterizer::BeginRenderingFast(',rendering)
    edit(c,'    const auto state = BeginRenderingFast(pipeline);','''    RenderState storage;
    u64 render_token=0;
    const auto& state=BeginRenderingFast(pipeline,storage,render_token);''',2)
    edit(c,'    scheduler.BeginRendering(state);','    scheduler.BeginRendering(state,render_token);',2)
    def dynamic(old):
        a=old.index('    const auto serial=');b=old.index('    if(!same) {')
        return old[:a]+'''    const bool enabled=BachataSotcLod::Enabled() && liverpool->OnDrawThread() && draw_relevance_ready;
    bool same=false;
    if(enabled) {
        const auto serial=liverpool->DrawRelSerial(AmdGpu::Liverpool::RelDynamic);
        const auto& masks=pipeline->GetGraphicsKey().write_masks;
        same=dynamic_inputs_valid && dynamic_serial==serial && dynamic_write_masks==masks &&
            dynamic_feedback==attachment_feedback_loop && dynamic_indexed==is_indexed;
        dynamic_serial=serial;dynamic_write_masks=masks;
        dynamic_feedback=attachment_feedback_loop;dynamic_indexed=is_indexed;
        dynamic_inputs_valid=true;
    } else dynamic_inputs_valid=false;
'''+old[b:]
    method(c,'void Rasterizer::UpdateDynamicState(',dynamic)
    h='renderer_vulkan/vk_scheduler.h';c='renderer_vulkan/vk_scheduler.cpp'
    edit(h,'    void BeginRendering(const RenderState& new_state);','    void BeginRendering(const RenderState& new_state,u64 token=0);')
    edit(h,'    RenderState render_state;','    RenderState render_state;\n    u64 render_state_token{};')
    edit(c,'''void Scheduler::BeginRendering(const RenderState& new_state) {
    DrainDrawPipe();
    if (is_rendering && render_state == new_state) {
        return;
    }
    EndRendering();
    is_rendering = true;
    render_state = new_state;''','''void Scheduler::BeginRendering(const RenderState& new_state,u64 token) {
    DrainDrawPipe();
    if(is_rendering && token && token==render_state_token) return;
    if (is_rendering && render_state == new_state) {
        render_state_token=token;
        return;
    }
    EndRendering();
    is_rendering = true;
    render_state = new_state;
    render_state_token=token;''')
    edit(c,'''void Scheduler::EndRendering() {
    DrainDrawPipe();''','''void Scheduler::EndRendering() {
    DrainDrawPipe();
    render_state_token=0;''')
    return {'pc308':'packed dword transport; relevance serials; atomic depth/GBuffer replay; dynamic derivation and scheduler token'}
