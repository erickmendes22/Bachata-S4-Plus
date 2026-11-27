#!/usr/bin/env python3
"""SotC TexBindMemo/ReplayTexBindMemo semantics on live 0.18.1 FEX resources."""
from pathlib import Path

API = r'''    struct SotcSampledSetEntry {
        ImageId id{};
        VAddr guest_address{};
        ImageViewInfo view_info{};
        vk::ImageView handle{};
        u64 image_uid{};
        vk::Image backing{};
        ImageViewId view_id{};
    };
    bool SotcSampledSetEnabled() const;
    bool CheckSotcSampledSet(std::span<SotcSampledSetEntry> entries,
                             u64 registry, u64 gpu_epoch, bool remember);
'''
METHOD = r'''bool TextureCache::SotcSampledSetEnabled() const {
    static const bool enabled=[] {
        const char* v=std::getenv("SOTC_TEXBIND_MEMO");
        return !v || v[0]!='0';
    }();
    return enabled && FindMemoEnabled();
}

bool TextureCache::CheckSotcSampledSet(std::span<SotcSampledSetEntry> entries,
                                        u64 registry, u64 gpu_epoch, bool remember) {
    std::scoped_lock lock{mutex};
    if(entries.empty() || registry!=TargetRegistryEpoch() ||
       gpu_epoch!=sotc_mip_tail_gpu_epoch.load(std::memory_order_relaxed)) return false;
    for(auto& entry:entries) {
        if(!entry.id) {
            if(entry.handle || entry.guest_address) return false;
            continue;
        }
        if(!entry.handle || !slot_images.IsAllocated(entry.id)) return false;
        const auto& image=slot_images[entry.id];
        if(False(image.flags&ImageFlagBits::Registered) || True(image.flags&ImageFlagBits::Dirty) ||
           image.binding.needs_rebind || image.binding.is_target || image.binding.force_general ||
           (!remember && image.binding.is_bound) || image.depth_id || image.info.props.is_depth ||
           image.info.sotc_first_mip || image.info.guest_address!=entry.guest_address || !image.backing ||
           image.track_addr!=image.info.guest_address ||
           image.track_addr_end!=image.info.guest_address+image.info.guest_size ||
           image.info.num_samples!=1 || image.backing->num_samples!=1) return false;
        const auto& range=entry.view_info.range;
        if(!range.extent.levels || !range.extent.layers ||
           range.base.level>=image.info.resources.levels || range.base.layer>=image.info.resources.layers ||
           range.extent.levels>image.info.resources.levels-range.base.level ||
           range.extent.layers>image.info.resources.layers-range.base.layer) return false;
        if(remember) {
            ImageViewId selected{};
            for(auto id:image.backing->image_view_ids) {
                if(!slot_image_views.IsAllocated(id)) continue;
                const auto& view=slot_image_views[id];
                if(view.info==entry.view_info && *view.image_view==entry.handle) {selected=id;break;}
            }
            if(!selected) return false;
            entry.image_uid=image.image_uid;
            entry.backing=image.GetImage();
            entry.view_id=selected;
        } else {
            if(entry.image_uid!=image.image_uid || entry.backing!=image.GetImage() ||
               !entry.view_id || !slot_image_views.IsAllocated(entry.view_id) ||
               !std::ranges::contains(image.backing->image_view_ids,entry.view_id)) return false;
            const auto& view=slot_image_views[entry.view_id];
            if(view.info!=entry.view_info || *view.image_view!=entry.handle) return false;
        }
    }
    // Validate the complete stage before any touches or binding mutations.
    if(!remember) for(const auto& entry:entries) {
        if(!entry.id) continue;
        auto& image=slot_images[entry.id];
        image.tick_accessed_last=scheduler.CurrentTick();
        TouchImage(image);
        image.binding.is_bound=1u;
        image.usage.texture=1u;
    }
    return true;
}

'''
MEMBERS = r'''    struct SotcTextureSetKey {
        static constexpr u32 MaxImages=16;
        u64 program{},mapping_generation{};
        u32 shader_stage{},count{};
        std::array<std::array<u64,4>,MaxImages> sharps{};
        std::array<u32,MaxImages> flags{};
        std::array<VAddr,MaxImages> addresses{};
        std::array<u32,MaxImages> lod_banks{};
        bool operator==(const SotcTextureSetKey&) const=default;
    };
    struct SotcTextureSetMemo {
        SotcTextureSetKey key{};
        u64 registry{},gpu_epoch{};
        bool valid{};
        std::array<VideoCore::TextureCache::SotcSampledSetEntry,SotcTextureSetKey::MaxImages> entries{};
    };
    using SotcTextureSetTable=std::array<SotcTextureSetMemo,1024>;
    std::unique_ptr<SotcTextureSetTable> sotc_texture_sets;
    SotcTextureSetMemo* SotcTextureSetSlot(const Shader::Info& stage,SotcTextureSetKey& key);
'''
SLOT = r'''Rasterizer::SotcTextureSetMemo* Rasterizer::SotcTextureSetSlot(
    const Shader::Info& stage,SotcTextureSetKey& key) {
    if(!texture_cache.SotcSampledSetEnabled() || stage.images.empty() ||
       stage.images.size()>SotcTextureSetKey::MaxImages) return nullptr;
    key.program=stage.pgm_hash;
    key.shader_stage=u32(stage.sw_stage);
    key.mapping_generation=memory->MappingGeneration();
    key.count=static_cast<u32>(stage.images.size());
    u64 hash=key.program^(u64(key.shader_stage)<<32);
    for(u32 i=0;i<key.count;++i) {
        const auto& res=stage.images[i];
        if(res.is_written || res.is_atomic || res.is_depth || res.array_size ||
           res.mip_fallback_mode!=Shader::MipStorageFallbackMode::None || res.NumBindings(stage)!=1)
            return nullptr;
        const auto sharp=res.GetSharp(stage);
        if(!sharp.Valid() && sharp.Address()) return nullptr;
        // Full vs rebased tail selection depends on live writer/LOD state.
        // Retain the existing authoritative path for those dynamic resources.
        if(sharp.base_level && VideoCore::SotcMipTailMode()) return nullptr;
        static_assert(sizeof(sharp)==sizeof(key.sharps[i]));
        std::memcpy(key.sharps[i].data(),&sharp,sizeof(sharp));
        key.flags[i]=u32(res.is_array)|(u32(res.is_r128)<<1)|(u32(res.post_op)<<2);
        key.addresses[i]=sharp.Address();
        key.lod_banks[i]=(sharp && sharp.lod_hw_cnt_en)?u32(sharp.counter_bank_id):~0u;
        for(u64 word:key.sharps[i]) {hash=(hash^word)*0x9e3779b97f4a7c15ull;hash^=hash>>32;}
        hash^=key.flags[i];
    }
    if(!sotc_texture_sets) sotc_texture_sets=std::make_unique<SotcTextureSetTable>();
    return &(*sotc_texture_sets)[hash%sotc_texture_sets->size()];
}

'''
BEGIN = r'''    SotcTextureSetKey set_key{};
    auto* memo=SotcTextureSetSlot(stage,set_key);
    bool set_hit=false;
    if(memo && memo->valid && memo->key==set_key &&
       set_key.mapping_generation==memory->MappingGeneration()) {
        auto entries=memo->entries;
        auto samples=std::span{entries}.first(set_key.count);
        if(texture_cache.CheckSotcSampledSet(samples,memo->registry,memo->gpu_epoch,false)) {
            set_hit=true;
            for(u32 i=0;i<set_key.count;++i) {
                const auto& entry=samples[i];
                if(BachataSotcLod::Enabled() && set_key.lod_banks[i]!=~0u)
                    BachataSotcLod::Mark(set_key.lod_banks[i]);
                if(!entry.id) {
                    image_infos.emplace_back(VK_NULL_HANDLE,VK_NULL_HANDLE,vk::ImageLayout::eGeneral);
                } else {
                    auto& image=texture_cache.GetImage(entry.id);
                    bound_images.emplace_back(entry.id);
                    needs_barrier|=runtime.Transit(&image,vk::ImageLayout::eShaderReadOnlyOptimal,
                        vk::PipelineStageFlagBits2::eAllCommands,vk::AccessFlagBits2::eShaderRead,
                        entry.view_info.range);
                    image_infos.emplace_back(VK_NULL_HANDLE,entry.handle,image.backing->state.layout);
                    image_info_images[image_infos.size()-1]=entry.id;
                }
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
    if(!set_hit) {
        if(memo) memo->valid=false;
'''
END = r'''        if(memo && image_bindings.size()==set_key.count &&
           image_infos.size()-first_image_idx==set_key.count &&
           set_key.mapping_generation==memory->MappingGeneration()) {
            SotcTextureSetMemo next{};
            next.key=set_key;
            next.registry=texture_cache.TargetRegistryEpoch();
            next.gpu_epoch=VideoCore::sotc_mip_tail_gpu_epoch.load(std::memory_order_relaxed);
            bool valid=true;
            for(u32 i=0;i<set_key.count;++i) {
                const auto& [id,desc]=image_bindings[i];
                if(desc.type!=VideoCore::TextureCache::BindingType::Texture || desc.rebase_mip ||
                   (!id && (set_key.addresses[i]!=0 || image_infos[first_image_idx+i].imageView))) {
                    valid=false;break;
                }
                auto& entry=next.entries[i];
                entry.id=id;entry.guest_address=set_key.addresses[i];
                entry.view_info=desc.view_info;
                entry.handle=image_infos[first_image_idx+i].imageView;
            }
            if(valid && texture_cache.CheckSotcSampledSet(std::span{next.entries}.first(set_key.count),
                                                         next.registry,next.gpu_epoch,true)) {
                next.valid=true;*memo=std::move(next);
            }
        }
    }
    if(memo) {
        static thread_local u64 hits{},misses{};
        hits+=set_hit;misses+=!set_hit;
        if(((hits+misses)&0x3ffff)==0)
            LOG_INFO(Render_Vulkan,"BACHATA_SOTC_TEXTURE_SET hits={} misses={}",hits,misses);
    }

'''

def apply(root: Path) -> None:
    def edit(rel, a, b):
        p=root/'src/video_core'/rel
        s=p.read_text()
        if s.count(a)!=1: raise RuntimeError(f'{rel} sampled set anchor: {s.count(a)} {a[:100]}')
        p.write_text(s.replace(a,b,1))
    edit('texture_cache/texture_cache.h','    [[nodiscard]] std::optional<vk::ImageView> TryReuseSampledView(',API+'    [[nodiscard]] std::optional<vk::ImageView> TryReuseSampledView(')
    edit('texture_cache/texture_cache.cpp','std::optional<vk::ImageView> TextureCache::TryReuseSampledView(',METHOD+'std::optional<vk::ImageView> TextureCache::TryReuseSampledView(')
    edit('renderer_vulkan/vk_rasterizer.h','    void RefreshImageLayouts();',MEMBERS+'    void RefreshImageLayouts();')
    p=root/'src/video_core/renderer_vulkan/vk_rasterizer.cpp'
    s=p.read_text()
    marker='void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {'
    start=s.index(marker); opening=s.index('{',start); depth=1;end=opening+1
    while depth:
        depth+=(s[end]=='{')-(s[end]=='}');end+=1
    body=s[start:end]
    a='    const u32 first_image_idx = image_infos.size();'
    b='    for (const auto& sampler : stage.samplers) {'
    assert body.count(a)==body.count(b)==1
    body=body.replace(a,a+'\n'+BEGIN,1).replace(b,END+b,1)
    p.write_text(s[:start]+SLOT+body+s[end:])
