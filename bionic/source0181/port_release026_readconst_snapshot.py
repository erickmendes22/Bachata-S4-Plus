#!/usr/bin/env python3
"""Release ReadConst GPU resource snapshot port for actual shadPS4 0.18.1 ABI.

The verified Release 0.2.6 Rasterizer creates an isolated, host-visible
ReadConst snapshot when a shader consumes a buffer as constant data.
The modern core already owns a BufferCache GPU-modified tracker; a CPU
snapshot must NEVER supersede newer GPU writes, so we snapshot ONLY
CPU-visible sources and bind the original GPU buffer for GPU-written
sources. Persistent GPU readback remains a separate unported subsystem.
"""
from pathlib import Path

def one(text: str, old: str, new: str, name: str) -> str:
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f"ReadConst snapshot parity source drift {name}: {n} occurrences")
    return text.replace(old,new,1)

def apply(root: Path) -> dict:
    resource=root/"src/shader_recompiler/resource.h"
    patching=root/"src/shader_recompiler/ir/passes/resource_patching_pass.cpp"
    cpp=root/"src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    a=resource.read_text();b=patching.read_text();c=cpp.read_text()
    a=one(a,
          "    bool is_formatted{};\n    SharpFetchPostOp post_op{};",
          "    bool is_formatted{};\n    bool used_as_readconst{}; // Release 0.2.6: preserve constant-source role.\n"
          "    SharpFetchPostOp post_op{};",
          "BufferResource role")
    b=one(b,
          "        buffer.is_formatted |= desc.is_formatted;\n",
          "        buffer.is_formatted |= desc.is_formatted;\n"
          "        buffer.used_as_readconst |= desc.used_as_readconst;\n",
          "combine ReadConst roles")
    b=one(b,
          """        .is_formatted = inst.GetOpcode() == IR::Opcode::LoadBufferFormatF32 ||
                        inst.GetOpcode() == IR::Opcode::StoreBufferFormatF32,
        .post_op = resource.sharps[0].post_op,""",
          """        .is_formatted = inst.GetOpcode() == IR::Opcode::LoadBufferFormatF32 ||
                        inst.GetOpcode() == IR::Opcode::StoreBufferFormatF32,
        .used_as_readconst = inst.GetOpcode() == IR::Opcode::ReadConstBuffer,
        .post_op = resource.sharps[0].post_op,""",
          "mark actual IR ReadConstBuffer consumer")
    # Use the actual 0.18.1 Buffer constructor (4 args) and its Flush(),
    # not the obsolete 0.16 Buffer(instance,scheduler,...) API. The staging
    # allocation is pinned to the GPU tick by Scheduler::DeferOperation.
    c=one(c,
          "void Rasterizer::BindBuffers(const Shader::Info& stage, Shader::Backend::Bindings& binding,\n",
          r"""// BACHATA_RELEASE026_READCONST_SNAPSHOT
// This is the Release's independent CPU constant buffer snapshot, adjusted
// for the 0.18.1 native Buffer/MemoryManager/Scheduler ABIs.
// NEVER snapshot CPU bytes if the source is GPU-modified; that would hide
// the GPU's newer descriptor writes from the shader. In that case the
// original BufferCache GPU-side buffer is used (ReadBackGpuWrittenSrtSources
// is still tracked separately).
std::shared_ptr<VideoCore::Buffer> MakeReadConstSnapshot(
    const Instance& instance, Core::MemoryManager* memory,
    VAddr address, u64 bytes) {
    if (bytes==0 || bytes>8_MB || address > UINT64_MAX - bytes) return {};
    void* map_start{};void* map_end{};u32 prot{};
    if (memory->QueryProtection(address,&map_start,&map_end,&prot)!=0 ||
        (prot & static_cast<u32>(Core::MemoryProt::CpuRead))==0 ||
        address<reinterpret_cast<VAddr>(map_start) ||
        address+bytes>reinterpret_cast<VAddr>(map_end)) return {};
    const u64 atom=std::max<u64>(1,instance.NonCoherentAtomSize());
    const u64 alloc_size=Common::AlignUp(std::max<u64>(bytes,atom),atom);
    auto snapshot=std::make_shared<VideoCore::Buffer>(
        instance,address,alloc_size,VideoCore::MemoryType::HostUncached,
        "Bachata Release ReadConst snapshot");
    if(snapshot->mapped_data.size()<alloc_size)return {};
    std::memcpy(snapshot->mapped_data.data(),reinterpret_cast<const void*>(address),bytes);
    if(alloc_size>bytes)
        std::memset(snapshot->mapped_data.data()+bytes,0,alloc_size-bytes);
    snapshot->Flush(0,alloc_size);
    return snapshot;
}

void Rasterizer::BindBuffers(const Shader::Info& stage, Shader::Backend::Bindings& binding,
""",
          "ReadConst GPU snapshot bridge")
    # In the resource-binding loop, select snapshot only for real
    # ReadConstBuffer IR resources and only if memory is CPU-authoritative.
    orig=r"""                const auto [buffer, offset] = buffer_cache.ObtainBuffer(
                    vsharp.base_address, size, desc.is_written, desc.is_formatted);
                const u64 offset_aligned = Common::AlignDown(offset, alignment);"""
    replacement=r"""                // Prefer the Release's immutable constant-source snapshot
                // when the data is CPU-authored. Keep the GPU cache's real
                // buffer for GPU-authored sources; never show stale CPU RAM.
                std::shared_ptr<VideoCore::Buffer> isolated;
                if (desc.used_as_readconst && !desc.is_written && size!=0 &&
                    !buffer_cache.IsRegionGpuModified(vsharp.base_address,size)) {
                    isolated=MakeReadConstSnapshot(instance,memory,vsharp.base_address,size);
                }
                const VideoCore::Buffer* buffer{};
                u64 offset{};
                if (isolated) {
                    buffer=isolated.get();
                    offset=0;
                    // Scheduler holds the allocation until the currently
                    // recorded GPU submission finishes. This prevents the
                    // old temporary readconst staging from being freed
                    // while Vulkan descriptors still reference it.
                    scheduler.DeferOperation([keep_alive=std::move(isolated)]{});
                } else {
                    std::tie(buffer,offset)=buffer_cache.ObtainBuffer(
                        vsharp.base_address,size,desc.is_written,desc.is_formatted);
                }
                const u64 offset_aligned = Common::AlignDown(offset, alignment);"""
    c=one(c,orig,replacement,"BindBuffers CPU authoritative snapshot")
    for path,content in ((resource,a),(patching,b),(cpp,c)):
        path.write_text(content)
    return {
        "ported":"ReadConst buffer provenance from IR through Rasterizer::BindBuffers",
        "snapshot":"independent VMA-checked host-visible CPU constant copy",
        "lifetime":"deferred GPU tick held by scheduler",
        "gpuWritten":"preserved GPU BufferCache path, never stale CPU snapshot",
        "limitations":"full ReadBackGpuWrittenSrtSources is not implemented",
    }
