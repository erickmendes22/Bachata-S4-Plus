"""Active Order Android texture-set memo adapted to FEX/0.18.1.

Donor: gow3_android_daedalus_fork, fix/order1886-adreno830-pervertex-interpolation,
overlay vk_rasterizer.cpp::BindTexturesFromSet. Keep exact T# words, shader
metadata, native VMA generation, all real image barriers, storage/feedback
fallbacks, alias ownership and existing view UID retirement checks.
"""
from pathlib import Path

API=r'''    // BACHATA_ORDER_TEXTURE_SET: no cached raw Vulkan handle is trusted
    // without checking the live image, backing and view under one lock.
    struct OrderSampledSetEntry {
        ImageId id{};
        VAddr guest_address{};
        ImageViewInfo view_info{};
        vk::ImageView handle{};
        ViewMemo memo{};
    };
    bool CheckOrderSampledSet(std::span<OrderSampledSetEntry> entries,
                              u64 generation, bool remember);
'''
METHOD=r'''bool TextureCache::CheckOrderSampledSet(std::span<OrderSampledSetEntry> entries,
                                         u64 generation, bool remember) {
    if(entries.empty() || generation!=RegistryGeneration()) return false;
    std::scoped_lock lock{mutex};
    if(generation!=RegistryGeneration()) return false;
    for(auto& entry:entries) {
        if(!entry.id || !entry.handle || !slot_images.IsAllocated(entry.id)) return false;
        auto& image=slot_images[entry.id];
        constexpr auto rejected=ImageFlagBits::Dirty|ImageFlagBits::Aliased;
        if(False(image.flags&ImageFlagBits::Registered) || True(image.flags&rejected) ||
           image.binding.needs_rebind || image.binding.is_target || image.binding.force_general ||
           (!remember && image.binding.is_bound) || image.depth_id || image.info.props.is_depth ||
           image.info.guest_address!=entry.guest_address || !image.backing ||
           image.track_addr!=image.info.guest_address ||
           image.track_addr_end!=image.info.guest_address+image.info.guest_size ||
           (image.backing->num_samples>1)!=(image.info.num_samples>1)) return false;
        const auto& range=entry.view_info.range;
        if(!range.extent.levels || !range.extent.layers ||
           range.base.level>=image.info.resources.levels ||
           range.base.layer>=image.info.resources.layers ||
           range.extent.levels>image.info.resources.levels-range.base.level ||
           range.extent.layers>image.info.resources.layers-range.base.layer) return false;
        if(remember) {
            ImageViewId selected{};
            for(auto id:image.backing->image_view_ids) {
                if(!slot_image_views.IsAllocated(id)) continue;
                const auto& view=slot_image_views[id];
                if(view.info==entry.view_info && *view.image_view==entry.handle) {
                    selected=id;break;
                }
            }
            if(!selected) return false;
            entry.memo={entry.id,image.image_uid,image.backing,image.backing->backing_uid,
                        selected,slot_image_views[selected].view_uid,entry.view_info};
        } else {
            const auto& v=entry.memo;
            if(v.image_id!=entry.id || v.image_uid!=image.image_uid || v.backing!=image.backing ||
               v.backing_uid!=image.backing->backing_uid || v.view_info!=entry.view_info ||
               !v.view_id || !slot_image_views.IsAllocated(v.view_id)) return false;
            const auto& view=slot_image_views[v.view_id];
            if(view.view_uid!=v.view_uid || view.info!=entry.view_info ||
               *view.image_view!=entry.handle) return false;
        }
    }
    // No partial binding effects if any later texture failed validation.
    if(!remember) for(const auto& entry:entries) {
        auto& image=slot_images[entry.id];
        image.tick_accessed_last=scheduler.CurrentTick();
        TouchImage(image);
        image.binding.is_bound=1u;
        image.usage.texture=1u;
    }
    return true;
}

'''
MEMBERS=r'''    struct OrderTextureSetKey {
        static constexpr u32 MaxImages=16;
        const Shader::Info* stage{};
        u64 program{};
        u64 mapping_generation{};
        u32 count{};
        std::array<std::array<u64,4>,MaxImages> sharps{};
        std::array<u32,MaxImages> flags{};
        std::array<VAddr,MaxImages> addresses{};
        bool operator==(const OrderTextureSetKey&) const=default;
    };
    struct OrderTextureSetMemo {
        OrderTextureSetKey key{};
        u64 generation{};
        bool valid{};
        std::array<VideoCore::TextureCache::OrderSampledSetEntry,OrderTextureSetKey::MaxImages> entries{};
    };
    using OrderTextureSetTable=std::array<OrderTextureSetMemo,128>;
    std::unique_ptr<OrderTextureSetTable> order_texture_sets;
    OrderTextureSetMemo* OrderTextureSetSlot(const Shader::Info& stage, OrderTextureSetKey& key);
'''
METHODS=r'''Rasterizer::OrderTextureSetMemo* Rasterizer::OrderTextureSetSlot(
    const Shader::Info& stage, OrderTextureSetKey& key) {
    static const bool enabled=[] {
        const char* v=std::getenv("ORDER1886_TEXTURE_SET_MEMO");
        return !v||v[0]!='0';
    }();
    // The donor explicitly excludes its scalar-mode-dependent a7b66f58
    // image guard. A matching T# is not proof that this shader is active.
    if(!enabled || !texture_cache.BindingMemoEnabled() ||
       stage.pgm_hash==0xa7b66f58 || stage.images.empty() ||
       stage.images.size()>OrderTextureSetKey::MaxImages) return nullptr;
    key.stage=&stage;
    key.program=stage.pgm_hash;
    key.mapping_generation=memory->MappingGeneration();
    key.count=static_cast<u32>(stage.images.size());
    u64 hash=key.program^reinterpret_cast<u64>(&stage);
    for(u32 i=0;i<key.count;++i) {
        const auto& res=stage.images[i];
        if(res.is_written || res.is_atomic || res.is_depth ||
           res.mip_fallback_mode!=Shader::MipStorageFallbackMode::None) return nullptr;
        const auto sharp=res.GetSharp(stage);
        if(!sharp.Valid() || !sharp.Address()) return nullptr;
        static_assert(sizeof(sharp)==sizeof(key.sharps[i]));
        std::memcpy(key.sharps[i].data(),&sharp,sizeof(sharp));
        key.flags[i]=u32(res.is_array)|(u32(res.is_r128)<<1)|(u32(res.post_op)<<2);
        key.addresses[i]=sharp.Address();
        for(u64 word:key.sharps[i]) {
            hash=(hash^word)*0x9e3779b97f4a7c15ull;
            hash^=hash>>32;
        }
        hash^=key.flags[i];
    }
    if(!order_texture_sets) order_texture_sets=std::make_unique<OrderTextureSetTable>();
    return &(*order_texture_sets)[hash%order_texture_sets->size()];
}

'''
BEGIN=r'''    OrderTextureSetKey order_set_key{};
    auto* order_set=OrderTextureSetSlot(stage,order_set_key);
    bool order_set_hit=false;
    if(order_set && order_set->valid && order_set->key==order_set_key &&
       order_set->generation==texture_cache.RegistryGeneration() &&
       order_set_key.mapping_generation==memory->MappingGeneration()) {
        // Own the complete memo across any recorder/cache callbacks.
        auto entries=order_set->entries;
        auto samples=std::span{entries}.first(order_set_key.count);
        if(texture_cache.CheckOrderSampledSet(samples,order_set->generation,false)) {
            order_set_hit=true;
            for(const auto& entry:samples) {
                auto& image=texture_cache.GetImage(entry.id);
                bound_images.emplace_back(entry.id);
                // Do NOT bypass layout/hazard transitions on a set hit.
                needs_barrier|=runtime.Transit(&image,vk::ImageLayout::eShaderReadOnlyOptimal,
                    vk::PipelineStageFlagBits2::eAllCommands,
                    vk::AccessFlagBits2::eShaderRead,entry.view_info.range);
                image_infos.emplace_back(VK_NULL_HANDLE,entry.handle,image.backing->state.layout);
                auto& write=set_writes[set_write_index++];
                write.dstSet=VK_NULL_HANDLE;
                write.dstBinding=binding.unified++;
                write.dstArrayElement=0;
                write.descriptorCount=1;
                write.descriptorType=vk::DescriptorType::eSampledImage;
                write.pImageInfo=&image_infos.back();
            }
        }
    }
    if(!order_set_hit) {
        if(order_set) order_set->valid=false;
'''
END=r'''        // The full native path above remains authoritative for all misses.
        // Capture only one-to-one, live, clean sampled bindings. A null,
        // associated-depth, storage, alias or transient mapping is not cached.
        if(order_set && image_bindings.size()==order_set_key.count &&
           image_infos.size()-first_image_idx==order_set_key.count &&
           order_set_key.mapping_generation==memory->MappingGeneration()) {
            OrderTextureSetMemo next{};
            next.key=order_set_key;
            next.generation=texture_cache.RegistryGeneration();
            bool valid=true;
            for(u32 i=0;i<order_set_key.count;++i) {
                const auto& [id,desc]=image_bindings[i];
                if(!id || desc.type!=VideoCore::TextureCache::BindingType::Texture) {
                    valid=false;break;
                }
                auto& entry=next.entries[i];
                entry.id=id;
                entry.guest_address=order_set_key.addresses[i];
                entry.view_info=desc.view_info;
                entry.handle=image_infos[first_image_idx+i].imageView;
            }
            if(valid && texture_cache.CheckOrderSampledSet(
                std::span{next.entries}.first(order_set_key.count),next.generation,true)) {
                next.valid=true;
                *order_set=std::move(next);
            }
        }
    }
    // Bounded evidence on real hits/misses; no per-draw log or clock.
    if(order_set) {
        static thread_local u64 hits{},misses{};
        hits+=order_set_hit;misses+=!order_set_hit;
        if(((hits+misses)&0x3ffff)==0)
            LOG_INFO(Render_Vulkan,"BACHATA_ORDER_TEXTURE_SET hits={} misses={}",hits,misses);
    }

'''
def one(s,a,b,label):
    if s.count(a)!=1: raise RuntimeError("Order texture set anchor "+label+": "+str(s.count(a)))
    return s.replace(a,b,1)

def apply(root:Path):
    root=Path(root)/"src/video_core"
    tc=root/"texture_cache/texture_cache.cpp"
    th=root/"texture_cache/texture_cache.h"
    rc=root/"renderer_vulkan/vk_rasterizer.cpp"
    rh=root/"renderer_vulkan/vk_rasterizer.h"
    t=th.read_text()
    anchor="    [[nodiscard]] ImageView& FindTexture(ImageId image_id, const ImageDesc& desc,"
    th.write_text(one(t,anchor,API+"\n"+anchor,"cache set API"))
    tc.write_text(one(tc.read_text(),"ImageView* TextureCache::TryViewMemo(",METHOD+"ImageView* TextureCache::TryViewMemo(","cache set validation"))
    r=rh.read_text()
    anchor="    using DescriptorViewMemos ="
    rh.write_text(one(r,anchor,MEMBERS+"\n"+anchor,"raster set storage"))
    s=rc.read_text()
    marker="void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {"
    a=s.index(marker)
    o=s.index("{",a);d=1;b=o+1
    while d:
        d+=(s[b]=="{")-(s[b]=="}");b+=1
    body=s[a:b]
    body=one(body,"    const u32 first_image_idx = image_infos.size();",
             "    const u32 first_image_idx = image_infos.size();\n"+BEGIN,"full binding fallback")
    body=one(body,"    for (const auto& sampler : stage.samplers) {",END+"    for (const auto& sampler : stage.samplers) {","samplers always bound")
    rc.write_text(s[:a]+METHODS+body+s[b:])
    return {"donor":"Android effective BindTexturesFromSet","key":"exact T# words, metadata, program, FEX mapping generation",
            "hit":"single locked validation of complete set; real transitions and sampler binding retained",
            "fallback":"null/dirty/untracked/alias/storage/depth/feedback/rebind and recycled view/backing"}
