#!/usr/bin/env python3
"""Close active donor indirect-argument hazards and Order GPU index bounds.

The Order donor clamps GPU-written indexed counts before native draws. Keep
that work on the GPU and use 0.18.1's timeline-tracked staging pool for output,
not the donor's unfenced wraparound ring. Shared indirect reads participate in
the barrier tracker, including their count buffer, as in the SotC donor.
"""
from pathlib import Path


def apply(root):
    src = Path(root) / "src"
    here = Path(__file__).parent

    def edit(rel, old, new):
        path = src / rel
        text = path.read_text()
        if text.count(old) != 1:
            raise RuntimeError(f"indirect submission {rel}: {old[:110]!r}: count={text.count(old)}")
        path.write_text(text.replace(old, new))

    rp = "video_core/renderer_vulkan/vk_rasterizer.cpp"
    rh = "video_core/renderer_vulkan/vk_rasterizer.h"
    (src / "video_core/renderer_vulkan/indirect_submission_limits.h").write_text(
        (here / "indirect_submission_limits.h").read_text())
    (src / "video_core/host_shaders/indirect_index_clamp.comp").write_text(
        (here / "indirect_index_clamp.comp").read_text())
    edit("video_core/host_shaders/CMakeLists.txt",
         "add_host_shader(fault_buffer_process.comp fault_buffer_process_comp)",
         "add_host_shader(fault_buffer_process.comp fault_buffer_process_comp)\n"
         "add_host_shader(indirect_index_clamp.comp indirect_index_clamp_comp)")
    edit("video_core/renderer_vulkan/vk_instance.h",
         "    u64 StorageMaxRange() const { return properties.limits.maxStorageBufferRange; }",
         """    u64 StorageMaxRange() const { return properties.limits.maxStorageBufferRange; }
    u32 MaxIndirectDrawCount() const { return properties.limits.maxDrawIndirectCount; }
    u32 MaxComputeDispatchX() const { return properties.limits.maxComputeWorkGroupCount[0]; }""")
    edit(rp, '#include "video_core/renderer_vulkan/vk_rasterizer.h"',
         '#include "video_core/renderer_vulkan/vk_rasterizer.h"\n'
         '#include "video_core/renderer_vulkan/indirect_submission_limits.h"\n'
         '#include "video_core/renderer_vulkan/vk_shader_util.h"\n'
         '#include "video_core/host_shaders/indirect_index_clamp_comp.h"\n#include <cstdlib>')
    edit(rh, "    void BindIndexBuffer(u32 index_offset = 0);", """    void BindIndexBuffer(u32 index_offset = 0, u32 indirect_bytes = 0,
                         u32 indirect_limit = ~u32{0});
    struct ClampedIndirectBatch {
        const VideoCore::Buffer* buffer;
        u64 offset; // GPU count word, followed by packed indexed arguments.
        u32 count;
    };
    std::vector<ClampedIndirectBatch> ClampIndexedIndirect(
        const VideoCore::Buffer* args, u64 offset, u32 count, u32 stride,
        const VideoCore::Buffer* count_buffer, u64 count_offset);
    u32 indirect_index_limit{~u32{0}};
    struct IndirectClampPipeline {
        vk::UniqueDescriptorSetLayout set_layout;
        vk::UniquePipelineLayout layout;
        vk::UniquePipeline pipeline;
    } indirect_clamp_pipeline;""")
    edit(rh, "    void ResetBindings(bool is_compute);", """    struct FixedFunctionRead {
        const VideoCore::Buffer* buffer;
        u64 offset, size;
        vk::AccessFlags2 access;
    };
    std::vector<FixedFunctionRead> fixed_function_reads;
    void ResetBindings(bool is_compute);""")

    text = (src / rp).read_text()
    first = text.index("void Rasterizer::DrawIndirect(")
    last = text.index("void Rasterizer::DispatchDirect(", first)
    draw = text[first:last]
    anchor = "    const DrawIndirectParams params = {"
    assert draw.count(anchor) == 1
    draw = draw.replace(anchor, INDIRECT_RECORD_BOUNDS + anchor)
    anchor = "        BindIndexBuffer();"
    assert draw.count(anchor) == 1
    draw = draw.replace(anchor,
        "        BindIndexBuffer(0, index_request.bytes, index_request.limit);")
    draw = draw.replace("ObtainBuffer(arg_address + offset, stride * max_count, false)",
                        "ObtainBuffer(arg_address + offset, argument_bytes, false)")
    draw = draw.replace("IsBufferAccessed(buffer, base, stride * max_count)",
                        "IsBufferAccessed(buffer, base, argument_bytes)")
    draw = draw.replace("    const VideoCore::Buffer* count_buffer;\n    u64 count_offset;",
                        "    const VideoCore::Buffer* count_buffer{};\n    u64 count_offset{};")
    anchor = "    pipeline->BindResources(set_writes, push_data);"
    if anchor not in draw:
        anchor = "    FastBindResolved(pipeline);"
    assert draw.count(anchor) == 1
    draw = draw.replace(anchor, """    std::vector<ClampedIndirectBatch> clamped;
    if (order_indexed && (indirect_index_limit != ~u32{0} ||
                          max_count > instance.MaxIndirectDrawCount())) {
        clamped = ClampIndexedIndirect(buffer, base, max_count, stride,
                                       count_buffer, count_offset);
        ASSERT_MSG(!clamped.empty(), "Nonempty indirect request produced no clamp batches");
    }

""" + anchor)
    old = """        ASSERT(sizeof(VkDrawIndexedIndirectCommand) == stride);

        if (count_address != 0) {"""
    assert draw.count(old) == 1
    draw = draw.replace(old, """        ASSERT((stride & 3) == 0 &&
               (max_count <= 1 || stride >= sizeof(VkDrawIndexedIndirectCommand)));

        if (!clamped.empty()) {
            for (const auto& batch : clamped) {
                if (count_address != 0) {
                    cmdbuf.drawIndexedIndirectCount(batch.buffer->Handle(), batch.offset + sizeof(u32),
                        batch.buffer->Handle(), batch.offset, batch.count,
                        sizeof(VkDrawIndexedIndirectCommand));
                } else {
                    cmdbuf.drawIndexedIndirect(batch.buffer->Handle(), batch.offset + sizeof(u32),
                        batch.count, sizeof(VkDrawIndexedIndirectCommand));
                }
                runtime.AccessBuffer(batch.buffer, batch.offset,
                    sizeof(u32) + u64(batch.count) * sizeof(VkDrawIndexedIndirectCommand),
                    vk::PipelineStageFlagBits2::eDrawIndirect,
                    vk::AccessFlagBits2::eIndirectCommandRead);
            }
        } else if (count_address != 0) {""")
    anchor = "    ResetBindings(false);\n}\n"
    assert draw.count(anchor) == 1
    draw = draw.replace(anchor, """    // Later WRITE_DATA/uploads must wait for these fixed-function reads.
    runtime.AccessBuffer(buffer, base, argument_bytes, vk::PipelineStageFlagBits2::eDrawIndirect,
                         vk::AccessFlagBits2::eIndirectCommandRead);
    if (count_address != 0) {
        runtime.AccessBuffer(count_buffer, count_offset, sizeof(u32),
                             vk::PipelineStageFlagBits2::eDrawIndirect,
                             vk::AccessFlagBits2::eIndirectCommandRead);
    }

""" + anchor)
    text = text[:first] + draw + text[last:]
    first = text.index("void Rasterizer::DispatchIndirect(")
    last = text.index("u64 Rasterizer::Flush(", first)
    dispatch = text[first:last]
    anchor = "    ResetBindings(true);"
    assert dispatch.count(anchor) == 1
    dispatch = dispatch.replace(anchor, """    runtime.AccessBuffer(buffer, base, size, vk::PipelineStageFlagBits2::eDrawIndirect,
                         vk::AccessFlagBits2::eIndirectCommandRead);

""" + anchor)
    text = text[:first] + dispatch + text[last:]
    (src / rp).write_text(text)
    edit(rp, "void Rasterizer::BindIndexBuffer(u32 index_offset) {", """void Rasterizer::BindIndexBuffer(u32 index_offset, u32 indirect_bytes, u32 indirect_limit) {""")
    edit(rp, "    const u32 index_buffer_size = regs.num_indices * index_size;", """    // Order indirect bounds were resolved before any resource transitions or
    // metadata clear consumption. Other draws retain the original size rule.
    const u32 index_buffer_size = indirect_bytes ? indirect_bytes : regs.num_indices * index_size;
    indirect_index_limit = indirect_limit;""")
    edit(rp, "void Rasterizer::ResetBindings(bool is_compute) {",
         CLAMP_IMPLEMENTATION + "\nvoid Rasterizer::ResetBindings(bool is_compute) {")
    edit(rp, "        needs_barrier |= runtime.IsBufferAccessed(range.buffer, range.offset, size);",
         """        needs_barrier |= runtime.IsBufferAccessed(range.buffer, range.offset, size);
        fixed_function_reads.push_back({range.buffer, range.offset, size,
                                        vk::AccessFlagBits2::eVertexAttributeRead});""")
    edit(rp, "    needs_barrier |= runtime.IsBufferAccessed(buffer, offset, index_buffer_size);",
         """    needs_barrier |= runtime.IsBufferAccessed(buffer, offset, index_buffer_size);
    fixed_function_reads.push_back({buffer, offset, index_buffer_size, vk::AccessFlagBits2::eIndexRead});""")
    edit(rp, "    bound_images.clear();\n    bound_buffers.clear();", """    for (const auto& read : fixed_function_reads) {
        runtime.AccessBuffer(read.buffer, read.offset, read.size,
                             vk::PipelineStageFlagBits2::eVertexInput, read.access);
    }
    fixed_function_reads.clear();
    bound_images.clear();
    bound_buffers.clear();""")
    edit("video_core/renderer_vulkan/vk_runtime.cpp",
         "        vk::AccessFlagBits2::eMemoryRead;",
         "        vk::AccessFlagBits2::eMemoryRead | vk::AccessFlagBits2::eIndirectCommandRead;")

    # The donor makes this hot warning opt-in. Preserve other titles' diagnostics.
    edit(rp, "namespace Vulkan {", "namespace Vulkan {\n" + META_WARNING_POLICY)
    edit(rp, "        if (texture_cache.IsMeta(tsharp.Address())) {",
         "        if (WarnMetadataTexture() && texture_cache.IsMeta(tsharp.Address())) {")
    return {"indirectHazards": "args/count reads participate in WAR barriers for draws and dispatches",
            "orderIndexBounds": "max_index_size and mapped bytes; clamp GPU-produced counts on GPU",
            "outputLifetime": "DeviceLocal staging pool, synchronized StreamBuffer watches",
            "batching": "descriptor range, dispatch X and native draw-count limits; GPU count per batch",
            "metadataWarning": "Order opt-in ORDER1886_WARN_META_TEXTURE, other titles preserved"}


INDIRECT_RECORD_BOUNDS = r'''    const bool order_indexed = is_indexed && BachataCompat::Order1886();
    BachataGpu::IndirectIndexRequest index_request{};
    u32 argument_bytes = stride * max_count;
    if (order_indexed) {
        const VAddr address = arg_address + offset;
        if (!max_count || address < arg_address || (address & 3)) return;
        const u64 requested = u64(max_count - 1) * stride + sizeof(VkDrawIndexedIndirectCommand);
        const auto records = BachataGpu::ResolveIndirectRecords(max_count, stride,
            sizeof(VkDrawIndexedIndirectCommand), memory->ClampGpuRangeSize(address, requested));
        if (!records.count) return;
        max_count = records.count;
        argument_bytes = records.bytes;
        if (count_address && ((count_address & 3) ||
            memory->ClampGpuRangeSize(count_address, sizeof(u32)) != sizeof(u32))) return;
        // Reject an empty index range before BindResources/BeginRendering:
        // those calls already publish image transitions and consume clear metadata.
        const auto& index_regs = liverpool->DrawRegs();
        const u32 index_size = index_regs.index_buffer_type.index_type == AmdGpu::IndexType::Index16
            ? sizeof(u16) : sizeof(u32);
        const VAddr index_address = index_regs.index_base_address.Address<VAddr>();
        const u32 wanted = index_regs.max_index_size ? index_regs.max_index_size : index_regs.num_indices;
        const u64 mapped = index_address
            ? memory->ClampGpuRangeSize(index_address, u64(wanted) * index_size) : 0;
        index_request = BachataGpu::ResolveIndirectIndices(
            index_regs.num_indices, index_regs.max_index_size, index_size, mapped);
        if (!index_request.bytes) return;
    }

'''

META_WARNING_POLICY = r'''static bool WarnMetadataTexture() {
    if (!BachataCompat::Order1886()) return true;
    static const bool enabled = [] {
        const char* value = std::getenv("ORDER1886_WARN_META_TEXTURE");
        return value && value[0] == '1';
    }();
    return enabled;
}
'''

CLAMP_IMPLEMENTATION = r'''std::vector<Rasterizer::ClampedIndirectBatch> Rasterizer::ClampIndexedIndirect(
    const VideoCore::Buffer* args, u64 offset, u32 count, u32 stride,
    const VideoCore::Buffer* count_buffer, u64 count_offset) {
    std::vector<ClampedIndirectBatch> result;
    if (!count) return result;
    const u64 alignment = instance.StorageMinAlignment();
    const u64 storage_range = instance.StorageMaxRange();
    auto& p = indirect_clamp_pipeline;
    if (!p.pipeline) {
        const auto device = instance.GetDevice();
        std::array<vk::DescriptorSetLayoutBinding, 3> bindings{};
        for (u32 i = 0; i < bindings.size(); ++i) {
            bindings[i] = {.binding = i, .descriptorType = vk::DescriptorType::eStorageBuffer,
                           .descriptorCount = 1, .stageFlags = vk::ShaderStageFlagBits::eCompute};
        }
        p.set_layout = Check(device.createDescriptorSetLayoutUnique({
            .flags = vk::DescriptorSetLayoutCreateFlagBits::ePushDescriptorKHR,
            .bindingCount = static_cast<u32>(bindings.size()), .pBindings = bindings.data(),
        }));
        const vk::PushConstantRange range{.stageFlags = vk::ShaderStageFlagBits::eCompute,
                                          .offset = 0, .size = 8 * sizeof(u32)};
        p.layout = Check(device.createPipelineLayoutUnique({
            .setLayoutCount = 1, .pSetLayouts = &*p.set_layout,
            .pushConstantRangeCount = 1, .pPushConstantRanges = &range,
        }));
        const auto module = CompileSPV(INDIRECT_INDEX_CLAMP_COMP, device);
        p.pipeline = Check(device.createComputePipelineUnique({}, vk::ComputePipelineCreateInfo{
            .stage = {.stage = vk::ShaderStageFlagBits::eCompute, .module = module, .pName = "main"},
            .layout = *p.layout,
        }));
        device.destroyShaderModule(module);
        LOG_INFO(Render_Vulkan, "BACHATA_ORDER_GPU_INDEX_CLAMP enabled=true gpu_arguments=true timeline_pool=true");
    }

    scheduler.EndRendering();
    const auto cmdbuf = scheduler.CommandBuffer();
    const u64 count_begin = count_buffer ? count_offset - count_offset % alignment : 0;
    const u64 count_bytes = count_buffer ? count_offset - count_begin + sizeof(u32) : 0;
    for (u32 first = 0; first < count;) {
        const u64 source_offset = offset + u64(first) * stride;
        const auto batch = BachataGpu::PlanIndirectClampBatch(count - first, stride, source_offset,
            alignment, storage_range, instance.MaxComputeDispatchX(), instance.MaxIndirectDrawCount());
        ASSERT_MSG(batch.count, "Device cannot represent indexed indirect clamp batch");
        // This pool reserves a new range when the old range's GPU tick is busy.
        // No CPU wait/read of the indirect records and no unfenced ring reuse.
        const auto output = runtime.GetStagingPool().Request(
            batch.output_bytes, VideoCore::MemoryType::DeviceLocal, alignment);
        const std::array<vk::DescriptorBufferInfo, 3> infos{{
            {args->Handle(), batch.source_begin, batch.source_bytes},
            {output.buffer->Handle(), output.offset, output.size},
            count_buffer ? vk::DescriptorBufferInfo{count_buffer->Handle(), count_begin, count_bytes}
                         : vk::DescriptorBufferInfo{args->Handle(), batch.source_begin, batch.source_bytes},
        }};
        std::array<vk::WriteDescriptorSet, 3> writes{};
        for (u32 i = 0; i < writes.size(); ++i) {
            writes[i] = {.dstBinding = i, .descriptorCount = 1,
                         .descriptorType = vk::DescriptorType::eStorageBuffer,
                         .pBufferInfo = &infos[i]};
        }
        const std::array<u32, 8> push{batch.count, batch.first_word, stride / u32{sizeof(u32)},
            indirect_index_limit, count_buffer ? 1u : 0u,
            count_buffer ? u32((count_offset - count_begin) / sizeof(u32)) : 0u,
            first, indirect_index_limit != ~u32{0} ? 1u : 0u};
        cmdbuf.bindPipeline(vk::PipelineBindPoint::eCompute, *p.pipeline);
        cmdbuf.pushDescriptorSetKHR(vk::PipelineBindPoint::eCompute, *p.layout, 0, writes);
        cmdbuf.pushConstants(*p.layout, vk::ShaderStageFlagBits::eCompute, 0, sizeof(push), push.data());
        cmdbuf.dispatch((batch.count + 63u) / 64u, 1, 1);
        result.push_back({output.buffer, output.offset, batch.count});
        runtime.AccessBuffer(args, source_offset,
            u64(batch.count - 1) * stride + sizeof(VkDrawIndexedIndirectCommand),
            vk::PipelineStageFlagBits2::eComputeShader, vk::AccessFlagBits2::eShaderRead);
        first += batch.count;
    }
    if (count_buffer) {
        runtime.AccessBuffer(count_buffer, count_offset, sizeof(u32),
            vk::PipelineStageFlagBits2::eComputeShader, vk::AccessFlagBits2::eShaderRead);
    }
    const vk::MemoryBarrier2 written{
        .srcStageMask = vk::PipelineStageFlagBits2::eComputeShader,
        .srcAccessMask = vk::AccessFlagBits2::eShaderWrite,
        .dstStageMask = vk::PipelineStageFlagBits2::eDrawIndirect,
        .dstAccessMask = vk::AccessFlagBits2::eIndirectCommandRead};
    cmdbuf.pipelineBarrier2(vk::DependencyInfo{.memoryBarrierCount = 1, .pMemoryBarriers = &written});
    return result;
}
'''
