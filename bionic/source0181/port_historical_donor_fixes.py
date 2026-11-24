#!/usr/bin/env python3
"""Log-driven integration of historical Order and Shadow source corrections.

Order: fe677e391489 (effective Info per SPIR-V permutation), fdb3fc068748
(canonical SRT traversal), 7dd64648f1ec (depth alias layout), 73ea8eace0e8
(aligned CPU vertex buffers), bf47fc30c67d / 9b7ce6baab50 (sample contract/cache).
Shadow: 685a8a0bd793 / 42e1c1d6e717 (ordered sparse arena release),
84fa5e51573c (small VMA blocks and real budget).
Adapts these to pinned shadPS4 0.18.1, not the dedicated port's worker ABI.
"""
from pathlib import Path
import re

def one(s, a, b, label):
    n=s.count(a)
    if n != 1:
        raise RuntimeError(f"Historical donor source drift {label}: {n}")
    return s.replace(a,b,1)

def apply(root: Path):
    files = {k:root/p for k,p in {
        'info':'src/shader_recompiler/info.h',
        'spec':'src/shader_recompiler/specialization.h',
        'resource':'src/shader_recompiler/resource.h',
        'pch':'src/video_core/renderer_vulkan/vk_pipeline_cache.h',
        'pcc':'src/video_core/renderer_vulkan/vk_pipeline_cache.cpp',
        'serh':'src/video_core/renderer_vulkan/vk_pipeline_serialization.h',
        'ser':'src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp',
        'insth':'src/video_core/renderer_vulkan/vk_instance.h',
        'inst':'src/video_core/renderer_vulkan/vk_instance.cpp',
        'raster':'src/video_core/renderer_vulkan/vk_rasterizer.cpp',
        'bch':'src/video_core/buffer_cache/buffer_cache.h',
        'bcc':'src/video_core/buffer_cache/buffer_cache.cpp',
        'image':'src/video_core/amdgpu/resource.h',
        'color':'src/video_core/amdgpu/regs_color.h',
        'depth':'src/video_core/amdgpu/regs_depth.h',
        'blit':'src/video_core/texture_cache/blit_helper.cpp',
    }.items()}
    s={k:p.read_text() for k,p in files.items()}
    def patch(k,a,b,label): s[k]=one(s[k],a,b,label)

    # The upstream cache compiles a new Info then discards it. On a changing
    # T#/SRT permutation it binds the first module's resource count/types
    # against the new Vulkan pipeline. This is exactly the donor fe677e39 fix.
    patch('pch','        Shader::StageSpecialization spec;\n',
          '        Shader::StageSpecialization spec;\n'
          '        std::unique_ptr<Shader::Info> effective_info;\n','stable per-permutation metadata')
    patch('pch', '''    void AddPermut(vk::ShaderModule module, Shader::StageSpecialization&& spec) {
        modules.emplace_back(module, std::move(spec));
    }

    void InsertPermut(vk::ShaderModule module, Shader::StageSpecialization&& spec,
                      size_t perm_idx) {
        modules.resize(std::max(modules.size(), perm_idx + 1)); // <-- beware of realloc
        modules[perm_idx] = {module, std::move(spec)};
    }''', '''    void AddPermut(vk::ShaderModule module, Shader::StageSpecialization&& spec,
                   std::unique_ptr<Shader::Info> effective = {}) {
        if (!effective) effective = std::make_unique<Shader::Info>(info);
        spec.info = &info;
        modules.emplace_back(module, std::move(spec), std::move(effective));
    }

    void InsertPermut(vk::ShaderModule module, Shader::StageSpecialization&& spec,
                      size_t perm_idx, std::unique_ptr<Shader::Info> effective) {
        spec.info = &info;
        modules.resize(std::max(modules.size(), perm_idx + 1));
        modules[perm_idx] = {module, std::move(spec), std::move(effective)};
    }''','module ownership and archive insertion')
    patch('pcc','RegisterShaderMeta(program->info, spec.fetch_shader_data, spec, perm_hash, 0);',
          'RegisterShaderMeta(program->info, program->info, spec.fetch_shader_data, spec, perm_hash, 0);',
          'first shader metadata')
    if s['pcc'].count('return std::make_tuple(&program->info, module, perm_hash);') != 2:
        raise RuntimeError('Historical donor GetProgram return count changed')
    s['pcc']=s['pcc'].replace('return std::make_tuple(&program->info, module, perm_hash);',
        'return std::make_tuple(program->modules[0].effective_info.get(), module, perm_hash);',1)
    patch('pcc', '''        auto new_info = Shader::Info(hw_stage, sw_stage, params);
        module = CompileModule(new_info, runtime_info, params.code, perm_idx, binding);

        RegisterShaderMeta(info, spec.fetch_shader_data, spec, perm_hash, perm_idx);
        program->AddPermut(module, std::move(spec));
    } else {
        info.AddBindings(binding);
        module = it->module;''', '''        auto new_info = std::make_unique<Shader::Info>(hw_stage, sw_stage, params);
        module = CompileModule(*new_info, runtime_info, params.code, perm_idx, binding);

        RegisterShaderMeta(info, *new_info, spec.fetch_shader_data, spec, perm_hash, perm_idx);
        program->AddPermut(module, std::move(spec), std::move(new_info));
    } else {
        auto& effective = *it->effective_info;
        effective.pgm_base = params.Base();
        effective.user_data = params.user_data;
        effective.RefreshFlatBuf();
        if (srt_sync) srt_sync(effective);
        effective.AddBindings(binding);
        module = it->module;''','keep compiled Info and refresh selected permutation')
    patch('pcc','return std::make_tuple(&program->info, module, perm_hash);',
          'return std::make_tuple(program->modules[perm_idx].effective_info.get(), module, perm_hash);',
          'return exact selected pipeline layout')
    patch('info','        bnd.unified += buffers.size() + images.size() + samplers.size();',
          '        bnd.unified += buffers.size() + samplers.size();\n'
          '        for (const auto& image : images) bnd.unified += image.NumBindings(*this);',
          'cached shader binding cursor counts every image array slot')
    patch('spec','        if (start != other.start) {',
          '        if (buffers.size() != other.buffers.size() || images.size() != other.images.size() ||\n'
          '            samplers.size() != other.samplers.size() || bitset != other.bitset) {\n'
          '            return false;\n'
          '        }\n'
          '        if (start != other.start) {','do not reuse layout after active resource change')
    patch('resource','? (tsharp.last_level - tsharp.base_level + 1)',
          '? (tsharp.last_level >= tsharp.base_level ? tsharp.last_level - tsharp.base_level + 1 : 1)',
          'prevent invalid mip array cardinality')
    # Persist the exact effective Info as well as the base specialization template.
    for k in ('serh','ser'):
        patch(k,'void RegisterShaderMeta(const Shader::Info& info,',
              'void RegisterShaderMeta(const Shader::Info& info, const Shader::Info& effective_info,',
              'archive metadata API '+k)
    patch('ser','    spec.Serialize(ar);\n    info.Serialize(ar);',
          '    spec.Serialize(ar);\n    info.Serialize(ar);\n    effective_info.Serialize(ar);',
          'serialize both metadata records')
    patch('ser','bool LoadShaderMeta(Serialization::Archive& ar, Shader::Info& info,',
          'bool LoadShaderMeta(Serialization::Archive& ar, Shader::Info& info, Shader::Info& effective_info,',
          'load both metadata records')
    patch('ser','    return info.Deserialize(ar);',
          '    return info.Deserialize(ar) && effective_info.Deserialize(ar);',
          'propagate either incompatible walker')
    patch('ser','    Shader::StageSpecialization spec{};\n    spec.info = &program->info;',
          '    auto effective_info = std::make_unique<Shader::Info>();\n'
          '    Shader::StageSpecialization spec{};\n    spec.info = &program->info;',
          'allocate stable archived effective Info')
    patch('ser','LoadShaderMeta(ar, program->info, spec, perm_idx)',
          'LoadShaderMeta(ar, program->info, *effective_info, spec, perm_idx)',
          'read effective archive metadata')
    patch('ser', '''            module = it->module;
        } else {
            module = CompileSPV(spv, instance.GetDevice());
        }
    }
    it_pgm.value()->InsertPermut(module, std::move(spec), perm_idx);

    infos[stage] = &it_pgm.value()->info;''', '''            // Do not replace the Info object already referenced by a cached pipeline.
            infos[stage] = it->effective_info.get();
            modules[stage] = it->module;
            if (auto& fetch = it->spec.fetch_shader_data; !fetch.Empty()) fetch_shader = &fetch;
            return true;
        } else {
            if (perm_idx < it_pgm.value()->modules.size() &&
                it_pgm.value()->modules[perm_idx].module) return false;
            module = CompileSPV(spv, instance.GetDevice());
        }
    }
    it_pgm.value()->InsertPermut(module, std::move(spec), perm_idx, std::move(effective_info));

    infos[stage] = it_pgm.value()->modules[perm_idx].effective_info.get();''',
          'restore stable effective Info and avoid replacing a live cached module')
    patch('ser','ShaderMetaVersion = 14u;', 'ShaderMetaVersion = 15u;',
          'new archive metadata generation')
    m=re.search(r'ShaderBinaryVersion = (\d+)u;',s['ser'])
    if not m: raise RuntimeError("Missing shader binary version")
    s['ser']=s['ser'][:m.start()]+f'ShaderBinaryVersion = {int(m.group(1))+1}u;'+s['ser'][m.end():]

    # Turnip device without mixed attachment sample support. Preserve all
    # original PS4 samples outside the specific Order title/device condition.
    msaa_header=root/'src/video_core/amdgpu/bachata_order_msaa.h'
    msaa_header.write_text("""// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <atomic>
namespace AmdGpu {
inline std::atomic<bool> bachata_order_single_sample{false};
inline bool BachataOrderNoMsaa() {
    return bachata_order_single_sample.load(std::memory_order_relaxed);
}
}
""")
    for k in ('image','color','depth'):
        patch(k,'#pragma once\n','#pragma once\n#include "video_core/amdgpu/bachata_order_msaa.h"\n',
              'centralized sample mode '+k)
    patch('image', '''    u32 NumLevels() const {
        if (GetType() == ImageType::Color2DMsaa || GetType() == ImageType::Color2DMsaaArray) {''',
          '''    u32 NumLevels() const {
        const auto raw_type = static_cast<ImageType>(type);
        if (raw_type == ImageType::Color2DMsaa || raw_type == ImageType::Color2DMsaaArray) {''',
          'MSAA level bits are not mip levels in compatibility mode')
    patch('image','    ImageType GetType() const noexcept {\n        return static_cast<ImageType>(type);\n    }',
          '''    ImageType GetType() const noexcept {
        const auto original = static_cast<ImageType>(type);
        if (BachataOrderNoMsaa()) {
            if (original == ImageType::Color2DMsaa) return ImageType::Color2D;
            if (original == ImageType::Color2DMsaaArray) return ImageType::Color2DArray;
        }
        return original;
    }''','coherent shader image types and sample count')
    patch('color','        return 1 << attrib.num_fragments_log2;',
          '        return BachataOrderNoMsaa() ? 1u : (1u << attrib.num_fragments_log2);','color attachments')
    patch('depth','        return 1u << z_info.num_samples; // spec doesn\'t say it is a log2',
          '        return BachataOrderNoMsaa() ? 1u : (1u << z_info.num_samples);','depth attachments')
    patch('inst','#include "common/debug.h"',
          '#include "common/debug.h"\n#include "common/elf_info.h"\n'
          '#include "video_core/amdgpu/bachata_order_msaa.h"','device compatibility includes')
    patch('inst','    CreateDevice();\n    CollectPhysicalMemoryInfo();',
          '''    CreateDevice();
    // bf47fc30: query enabled extensions AFTER CreateDevice. The test's
    // Adreno 840 also lacks both AMD/NV mixed attachment sample extensions.
    const bool order = Common::ElfInfo::Instance().GameSerial() == "CUSA00785";
    const auto name = std::string_view{properties.deviceName.data()};
    const bool adreno8xx = properties.vendorID == 0x5143 &&
        (name.find("830") != std::string_view::npos || name.find("840") != std::string_view::npos);
    const bool single_sample = order && adreno8xx &&
        !nv_framebuffer_mixed_samples && !amd_mixed_attachment_samples;
    AmdGpu::bachata_order_single_sample.store(single_sample, std::memory_order_relaxed);
    LOG_INFO(Render_Vulkan, "BACHATA_ORDER_MSAA mode={} mixed_nv={} mixed_amd={}",
             single_sample ? "single" : "guest", nv_framebuffer_mixed_samples,
             amd_mixed_attachment_samples);
    CollectPhysicalMemoryInfo();''','select sample mode from actual device')
    patch('ser','#include "shader_recompiler/frontend/fetch_shader.h"',
          '#include "shader_recompiler/frontend/fetch_shader.h"\n'
          '#include "video_core/amdgpu/bachata_order_msaa.h"','sample-aware cache')
    patch('ser','meta.Write(Serialization::ShaderBinaryVersion);',
          'meta.Write(Serialization::ShaderBinaryVersion + (AmdGpu::BachataOrderNoMsaa() ? 64u : 0u));',
          'write shader binary sample-mode identity')
    patch('ser','binary_version != Serialization::ShaderBinaryVersion',
          'binary_version != Serialization::ShaderBinaryVersion + (AmdGpu::BachataOrderNoMsaa() ? 64u : 0u)',
          'reject incompatible sample-mode binary')
    patch('ser','''void RegisterPipelineData(const GraphicsPipelineKey& key, u64 hash,
                          GraphicsPipeline::SerializationSupport& sdata) {
    if (!Storage''',
          '''void RegisterPipelineData(const GraphicsPipelineKey& key, u64 hash,
                          GraphicsPipeline::SerializationSupport& sdata) {
    // 9b7ce6ba: do not replay graphics state without the live guest registers.
    if (AmdGpu::BachataOrderNoMsaa()) return;
    if (!Storage''','do not archive incomplete single-sample graphics state')
    patch('ser','''            } else {
                result = LoadGraphicsPipeline(ar);
            }''',
          '''            } else if (!AmdGpu::BachataOrderNoMsaa()) {
                result = LoadGraphicsPipeline(ar);
            }''','rebuild graphics from live registers in single-sample mode')
    # 8497bf4a is already in 0.18.1 (Vulkan image view is e2D).
    if 'vk::ImageViewType::e2DMS' in s['blit']:
        raise RuntimeError("Unexpected invalid Vulkan multisample view")
    patch('blit','state.depth_stencil_attachment.image_layout = vk::ImageLayout::eDepthAttachmentOptimal;',
          'state.depth_stencil_attachment.image_layout = vk::ImageLayout::eDepthStencilAttachmentOptimal;',
          '7dd64648: match Runtime::CopyColorAndDepth barrier layout')

    # Never submit a VkDescriptorBufferInfo outside the real Vulkan range.
    patch('insth','    /// Returns the minimum alignment required for accessing host-mapped device memory',
          '    u64 StorageMaxRange() const { return properties.limits.maxStorageBufferRange; }\n\n'
          '    /// Returns the minimum alignment required for accessing host-mapped device memory',
          'device storage descriptor limit')
    patch('raster','#include "core/debug_state.h"',
          '#include "common/elf_info.h"\n#include "core/debug_state.h"','title-specific donor scope')
    patch('raster', '''            const u64 mapped = vsharp.base_address
                ? (readconst ? memory->ClampGpuRangeSize(vsharp.base_address, vsharp.GetSize())
                             : memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize())) : 0;
            if (vsharp.base_address == 0 || vsharp.GetSize() == 0 ||
                (readconst && ((vsharp.base_address & 3) != 0 || mapped < 4))) {''',
          '''            const bool shadow = Common::ElfInfo::Instance().GameSerial() == "CUSA08809";
            const u64 mapped = vsharp.base_address
                ? ((readconst || shadow) ? memory->ClampGpuRangeSize(vsharp.base_address, vsharp.GetSize())
                                        : memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize())) : 0;
            const u64 worst_adjust = vsharp.base_address % alignment;
            const u64 limit = instance.StorageMaxRange() > worst_adjust
                ? instance.StorageMaxRange() - worst_adjust : 0;
            const u64 bounded = std::min(mapped, limit);
            if (vsharp.base_address == 0 || bounded == 0 ||
                (readconst && ((vsharp.base_address & 3) != 0 || bounded < 4))) {''',
          'reject zero-size ranges and respect actual hardware storage limit')
    patch('raster','''                const u64 size = readconst ? (mapped & ~u64{3}) :
                    memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize());''',
          '''                const u64 size = readconst ? (bounded & ~u64{3}) : bounded;''',
          'use validated size for allocation and binding')
    patch('raster', '''                } else {
                    std::tie(buffer,offset)=buffer_cache.ObtainBuffer(
                        vsharp.base_address,size,desc.is_written,desc.is_formatted);
                }
                const u64 offset_aligned''',
          '''                } else if (Common::ElfInfo::Instance().GameSerial() == "CUSA00785" &&
                           !readconst && !desc.is_written && (vsharp.base_address & 3) != 0 &&
                           size >= 4096 && size <= buffer_cache.GetStreamBuffer().SizeBytes()/2 &&
                           !buffer_cache.IsRegionGpuModified(vsharp.base_address,size)) {
                    // 73ea8eac: CPU-owned vertex records shifted by two bytes.
                    // Use an aligned stream slot rather than truncate the byte offset to DWORDs.
                    auto& stream=buffer_cache.GetStreamBuffer();
                    const auto [data, stream_offset]=stream.Map(size,alignment);
                    memory->CopySparseMemory(vsharp.base_address,data,size);
                    stream.Commit();
                    buffer=&stream;
                    offset=stream_offset;
                } else {
                    std::tie(buffer,offset)=buffer_cache.ObtainBuffer(
                        vsharp.base_address,size,desc.is_written,desc.is_formatted);
                }
                const u64 offset_aligned''','aligned CPU vertex source path')
    # Donor 84fa5e51: VMA must not retain large blocks that sparse arena
    # allocations cannot use. On integrated mobile devices keep 64MiB blocks.
    patch('inst','''        .flags = VMA_ALLOCATOR_CREATE_BUFFER_DEVICE_ADDRESS_BIT,
        .physicalDevice = physical_device,
        .device = *device,
        .pVulkanFunctions = &functions,''',
          '''        .flags = static_cast<VmaAllocatorCreateFlags>(
            VMA_ALLOCATOR_CREATE_BUFFER_DEVICE_ADDRESS_BIT |
            (supports_memory_budget ? VMA_ALLOCATOR_CREATE_EXT_MEMORY_BUDGET_BIT : 0)),
        .physicalDevice = physical_device,
        .device = *device,
        .preferredLargeHeapBlockSize = IsIntegrated() ? 64_MB : 0,
        .pVulkanFunctions = &functions,''','smaller integrated VMA blocks, live Vulkan budget')

    # Shadow donor releases whole sparse blocks only, waits prior work, and
    # queues unbind before reuse. Split backing allocations into releasable
    # 64 MiB spans instead of pinning a multi-GiB allocation until its last page.
    patch('bch','#include <deque>','#include <deque>\n#include <unordered_map>','sparse backing ownership')
    patch('bch','    void TickFrame();',
          '    void TickFrame();\n    void ReleaseUnmappedArena(VAddr address, u64 size);','release API')
    patch('bch','    IntervalList<Backing> resident_ranges;',
          '    IntervalList<Backing> resident_ranges;\n'
          '    std::unordered_map<VkDeviceMemory, u64> backing_blocks;','resident allocation reference counts')
    patch('bcc','''    const vk::MemoryAllocateInfo alloc_info = {
        .allocationSize = resident_blocks << block_shift,''',
          '''    // 685a8a0b / 42e1c1d6: sparse allocation lifetime must not tie
    // hundreds of independent guest mappings to one unreleasable VkDeviceMemory.
    const u64 max_blocks = std::max<u64>(1, (64ULL << 20) >> block_shift);
    if (resident_blocks > max_blocks) {
        for (const auto& gap : bind_ranges) {
            for (u64 begin=gap.start; begin<gap.end;) {
                const u64 end=std::min(gap.end,begin+max_blocks);
                EnsureResident(arena,begin,end-1);
                begin=end;
            }
        }
        return;
    }
    const vk::MemoryAllocateInfo alloc_info = {
        .allocationSize = u64{resident_blocks} << block_shift,''','bounded releasable backing allocations')
    patch('bcc','    const auto device_memory = Vulkan::Check(instance.GetDevice().allocateMemory(alloc_info));',
          '    const auto device_memory = Vulkan::Check(instance.GetDevice().allocateMemory(alloc_info));\n'
          '    backing_blocks.emplace(static_cast<VkDeviceMemory>(device_memory), resident_blocks);',
          'track backing blocks')
    patch('bcc','void BufferCache::SubmitPendingArenaBinds(Vulkan::SubmitInfo& info) {',
          '''// Adapted from Shadow donor ReleaseMemory: the existing memory manager calls
// Rasterizer::UnmapMemory before changing guest VMAs. InvalidateMemory already
// handles required old GPU readbacks; this runs in GPU command order.
void BufferCache::ReleaseUnmappedArena(VAddr address, u64 size) {
    if (!size || address >= (1ULL<<40) || size > (1ULL<<40)-address) return;
    const u64 first=Common::AlignUp(address,u64{block_size})>>block_shift;
    const u64 end=(address+size)>>block_shift;
    if (first>=end) return;
    boost::container::small_vector<Backing,16> released;
    resident_ranges.ForEachInRange(first,end,[&](const Backing& backing) {
        const u64 a=std::max(first,backing.start), b=std::min(end,backing.end);
        if (a<b) released.push_back(backing.SubRange(a,b));
    });
    if (released.empty()) return;
    scheduler.Finish();
    for (const auto& range : released) {
        for (u64 begin=range.start; begin<range.end;) {
            const u64 page=begin>>blocks_per_arena_page_shift;
            const u64 stop=std::min(range.end,(page+1)<<blocks_per_arena_page_shift);
            if (const Buffer* arena=address_space[page]) {
                BindsForArena(arena)->binds.push_back(vk::SparseMemoryBind{
                    .resourceOffset=(begin<<block_shift)-arena->cpu_addr,
                    .size=(stop-begin)<<block_shift,
                    .memory={},
                    .memoryOffset=0,
                });
            }
            begin=stop;
        }
        runtime.FillBuffer(bda_pagetable_buffer.get(),range.start*sizeof(vk::DeviceAddress),
                           (range.end-range.start)*sizeof(vk::DeviceAddress),0u);
        const auto handle=static_cast<VkDeviceMemory>(range.memory);
        auto it=backing_blocks.find(handle);
        if (it!=backing_blocks.end()) {
            it->second-=std::min(it->second,range.end-range.start);
            if (!it->second) {
                backing_blocks.erase(it);
                scheduler.DeferOperation([device=instance.GetDevice(),memory=range.memory] {
                    device.freeMemory(memory);
                });
            }
        }
    }
    // 0.18.1 IntervalList lacks Subtract; preserve partial neighbours with
    // their original allocation offsets rather than clearing the entire cache.
    IntervalList<Backing> retained;
    retained.Reserve(resident_ranges.Size());
    for (const auto& range : resident_ranges) {
        if (range.end<=first || range.start>=end) retained.Add(range);
        else {
            if (range.start<first) retained.Add(range.SubRange(range.start,first));
            if (range.end>end) retained.Add(range.SubRange(end,range.end));
        }
    }
    resident_ranges=std::move(retained);
    const u64 bytes=(end-first)<<block_shift;
    memory_tracker->UnmarkRegionAsGpuModified(first<<block_shift,bytes,true);
    gpu_modified_ranges.Subtract(first<<block_shift,bytes);
    srt_source_pages.Subtract(first<<block_shift,bytes);
    // Separate unbind and later rebind submissions as in donor 42e1c1d6.
    scheduler.Flush();
    LOG_INFO(Render,"BACHATA_SHADOW_ARENA_RELEASE address={:#x} span={:#x}",address,size);
}

void BufferCache::SubmitPendingArenaBinds(Vulkan::SubmitInfo& info) {''','ordered sparse unmap release')
    patch('raster','''void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    buffer_cache.InvalidateMemory(addr, size);
    texture_cache.UnmapMemory(addr, size);''',
          '''void Rasterizer::UnmapMemory(VAddr addr, u64 size) {
    buffer_cache.InvalidateMemory(addr, size);
    texture_cache.UnmapMemory(addr, size);
    if (Common::ElfInfo::Instance().GameSerial() == "CUSA08809") {
        liverpool->SendCommand<false>([this,addr,size] {
            buffer_cache.ReleaseUnmappedArena(addr,size);
        });
    }''','connect Shadow release to guest unmap')

    for k,p in files.items(): p.write_text(s[k])
    return {
        "order": ["canonical GVN traversal","per-permutation Info and cache","exact descriptor array cursor",
                  "sample-count contract","depth alias layout","aligned CPU vertex records"],
        "shadow": ["actual storage range limit","64 MiB sparse backing blocks","ordered unmap reclamation",
                   "real memory budget VMA"],
        "limits": "does not replace arbitrary large guest buffers with a guessed size; no device test claim",
    }
