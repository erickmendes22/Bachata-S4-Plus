"""Order donor shader translation contracts, adapted to retained ARM64 SRT.
Source: c53cd01d032995fe622033623ab64b4cf6b02233, shader recompiler.
No changes to FEX, guest memory ABI, pipeline scheduling, Android FPS or presentation.
Preserve SotC dynamic T# arrays, full-width fetch bounds and compiled descriptor counts.
"""
from pathlib import Path
import re, shutil

def apply(root: Path, order: bool):
    sh=root/"src/shader_recompiler"
    def edit(p,a,b,n=1):
        s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"shader translation contract {p.name}: {a[:120]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    def prefix(p,inc):
        if inc not in p.read_text(): p.write_text(inc+"\n"+p.read_text())
    resource=sh/"resource.h"
    prefix(resource,"#include <optional>")
    prefix(resource,"#include <limits>")
    edit(resource,"    bool operator==(const SharpFetch&) const = default;",
        r'''    bool operator==(const SharpFetch&) const = default;

    template <u32 num_dwords=N>
    constexpr std::optional<u32> UnresolvedDword(size_t flatbuf_dwords) const {
        static_assert(num_dwords<=N);
        if (summary==Summary::Invalid) return 0u;
        for(u32 i=0;i<num_dwords;++i) {
            if ((load_mask&(1u<<i)) &&
                (offsets[i]==UNKNOWN_LOCATION || offsets[i]>=flatbuf_dwords))
                return i;
        }
        return std::nullopt;
    }''')
    edit(resource,"struct ImageResource {\n    SharpFetch<AmdGpu::Image> sharp_fetch{};",
        r'''// Inactivity is a proven necessary wave-uniform condition on all uses.
struct UniformResourceGuard {
    SharpFetch<u32> count{};
    u32 threshold{};
    u16 proven_uses{};
    bool enabled{};
    bool operator==(const UniformResourceGuard&) const = default;
    constexpr std::optional<u32> InactiveCount(const auto& info) const {
        if (!enabled || proven_uses==0) return std::nullopt;
        const auto& flat=info.flattened_ud_buf;
        if(count.UnresolvedDword(flat.size())) return std::nullopt;
        u32 value{};
        if(!count.Fetch(flat.data(),&value) || value>threshold) return std::nullopt;
        return value;
    }
};

struct ImageResource {
    SharpFetch<AmdGpu::Image> sharp_fetch{};
    UniformResourceGuard uniform_guard{};''')
    edit(resource,"    constexpr AmdGpu::Image GetSharp(const auto& info) const noexcept {\n        if (!array_size)",
        r'''    constexpr bool IsUniformlyInactive(const auto& info) const {
        if(array_size || is_depth || is_atomic || is_written || is_r128 ||
            post_op!=SharpFetchPostOp::None ||
            mip_fallback_mode!=MipStorageFallbackMode::None) return false;
        return uniform_guard.InactiveCount(info).has_value();
    }
    constexpr AmdGpu::Image GetSharp(const auto& info) const noexcept {
        if (!array_size)''')
    edit(resource,"        AmdGpu::Image image{};\n        if (!Fetch(info.flattened_ud_buf.data(), &image, element*array_stride_dw)) {",
        """        if (IsUniformlyInactive(info)) return AmdGpu::Image::Null(false);
        AmdGpu::Image image{};
        if (!Fetch(info.flattened_ud_buf.data(), &image, element*array_stride_dw)) {""")
    # FMask translation always depends on the full descriptor, not a single
    # ReadConst slot: classify, remap and re-specialize when the type changes.
    edit(resource,"""struct FMaskResource {
    SharpLocation sharp_idx;

    constexpr AmdGpu::Image GetSharp(const auto& info) const noexcept {
        return info.template ReadUdSharp<AmdGpu::Image>(sharp_idx);
    }
};
using FMaskResourceList = boost::container::static_vector<FMaskResource, NUM_FMASKS>;""",
         """struct FMaskResource {
    ImageResource source;
    constexpr AmdGpu::Image GetSharp(const auto& info) const noexcept {
        return source.GetSharp(info);
    }
};
using FMaskResourceList = boost::container::static_vector<FMaskResource, NUM_FMASKS>;""")
    # The donor retains a source for every FMask translation, including reads
    # eliminated as constants. A shader may consume up to NUM_IMAGES resources.
    edit(resource,"static constexpr u32 NUM_FMASKS = 8;","static constexpr u32 NUM_FMASKS = NUM_IMAGES;")
    passes=sh/"ir/passes"
    for n in ("sampled_image_uniform_guard_pass.cpp","sampled_image_uniform_guard_pass.h","fmask_identity.h"):
        shutil.copyfile(Path(__file__).parent/"inherited_shader"/n,passes/n)
    rp=passes/"resource_pass.h"
    prefix(rp,'#include "shader_recompiler/resource.h"')
    edit(rp,"    std::array<SharpReference, 2> sharps;\n};",
         "    std::array<SharpReference, 2> sharps;\n    UniformResourceGuard uniform_guard{};\n};")
    guard=passes/"sampled_image_uniform_guard_pass.cpp"
    # Our portable SRT keeps every discovered source (including dynamic
    # T# array references). The exact donor's ImageRecipe only accepts
    # resolved scalar locations, so dynamic table aliases cannot prove guards.
    prefix(guard,'#include "shader_recompiler/ir/microinstruction.h"')
    # Build as part of existing recompiler translation unit. Keep CMake and
    # target-specific compiler/linker boundaries unchanged.
    rec=sh/"recompiler.cpp"
    prefix(rec,'#include "shader_recompiler/ir/passes/sampled_image_uniform_guard_pass.h"')
    prefix(rec,'#include "common/elf_info.h"')
    edit(rec,"    Shader::Optimization::ResourcePatchingPass(program.info, resources, profile);",
         """    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if (serial=="CUSA00785") {
        Shader::Optimization::AnalyzeSampledImageUniformGuards(program.blocks, resources);
    }
    Shader::Optimization::ResourcePatchingPass(program.info, resources, profile);""")
    # The donor source has a convenience wrapper for its own pass API.
    # No declaration or use in our pipeline, so retain the analysis only.
    g=guard.read_text()
    g=re.sub(r"\nvoid SampledImageUniformGuardPass\(IR::Program& program, ResourceDiscoveryList& resources\) \{\n    AnalyzeSampledImageUniformGuards\(program.blocks, resources\);\n\}\n","\n",g)
    guard.write_text(g)
    with rec.open("a") as f: f.write('\n#include "shader_recompiler/ir/passes/sampled_image_uniform_guard_pass.cpp"\n')
    patch=passes/"resource_patching_pass.cpp"
    prefix(patch,'#include "shader_recompiler/ir/passes/fmask_identity.h"')
    # SotC's older resource matcher also omitted the r128/depth discriminator.
    # Preserve existing descriptor-array constraints and add those missing keys.
    anchor="            return desc.sharp_fetch == existing.sharp_fetch && desc.is_array == existing.is_array &&\n"
    old=patch.read_text()
    if old.count(anchor)!=1: raise RuntimeError("image descriptor key anchor")
    insert="                   desc.uniform_guard == existing.uniform_guard &&\n"
    if "                   desc.is_r128 == existing.is_r128 && desc.is_depth == existing.is_depth &&\n" not in old:
        insert+="                   desc.is_r128 == existing.is_r128 && desc.is_depth == existing.is_depth &&\n"
    edit(patch,anchor,anchor+insert)
    edit(patch,"            return desc.sharp_idx == existing.sharp_idx;",
         """            return desc.source.sharp_fetch == existing.source.sharp_fetch &&
                   desc.source.uniform_guard == existing.source.uniform_guard &&
                   desc.source.is_r128 == existing.source.is_r128 &&
                   desc.source.is_depth == existing.source.is_depth &&
                   desc.source.is_array == existing.source.is_array &&
                   desc.source.post_op == existing.source.post_op &&
                   desc.source.mip_fallback_mode == existing.source.mip_fallback_mode &&
                   desc.source.constant_mip_index == existing.source.constant_mip_index &&
                   desc.source.array_size == existing.source.array_size &&
                   desc.source.array_stride_dw == existing.source.array_stride_dw;""")
    edit(patch,"        .sharp_fetch = table_fetch ? *table_fetch : ConstructSharpFetch<AmdGpu::Image>(resource.sharps[0]),",
         """        .sharp_fetch = table_fetch ? *table_fetch : ConstructSharpFetch<AmdGpu::Image>(resource.sharps[0]),
        .uniform_guard = resource.uniform_guard,""")
    edit(patch,'        ASSERT_MSG(!is_written, "FMask storage instructions are not supported");',
         '''        ASSERT_MSG(!is_written, "FMask storage instructions are not supported");
        descriptors.Add(FMaskResource{.source=image_res});''')
    edit(patch,"""            IR::F32 fmaskx = ir.BitCast<IR::F32>(ir.Imm32(0x76543210));
            IR::F32 fmasky = ir.BitCast<IR::F32>(ir.Imm32(0xfedcba98));
            inst.ReplaceUsesWith(ir.CompositeConstruct(fmaskx, fmasky));""",
         """            const auto mapping=image.DstSelect();
            const auto payload=FmaskIdentityTexel(mapping);
            ASSERT_MSG(payload.has_value(),"Unsupported FMask selectors R={} G={} B={} A={}",
                       u32(mapping.r),u32(mapping.g),u32(mapping.b),u32(mapping.a));
            const auto component=[&](u32 bits){return ir.BitCast<IR::F32>(ir.Imm32(bits));};
            inst.ReplaceUsesWith(ir.CompositeConstruct(component((*payload)[0]),
                component((*payload)[1]),component((*payload)[2]),component((*payload)[3])));""")
    edit(patch,"""            // Track FMask resource to do specialization.
            descriptors.Add(FMaskResource{
                .sharp_idx = SharpLocationFromSource(resource.sharps[0].dwords[0].Inst()),
            });
""","")
    spec=sh/"specialization.h"
    edit(spec,"    bool is_fmask = false;\n    AmdGpu::CompMapping dst_select{};",
         "    bool is_fmask = false;\n    bool is_inactive = false;\n    AmdGpu::CompMapping dst_select{};")
    edit(spec,"struct FMaskSpecialization {\n    u32 width;\n    u32 height;",
         "struct FMaskSpecialization {\n    u32 width;\n    u32 height;\n    ImageSpecialization translation;\n    AmdGpu::CompMapping mapping{};")
    # Include descriptor classification even when the address is zero.
    edit(spec,"""        // A null descriptor still consumes its compiled layout slots.
        for (size_t i=0;i<images.size();++i)
            images[i].num_bindings=info->images[i].LiveNumBindings(*info);
        ForEachSharp(binding, fmasks, info->fmasks,
                     [](auto& spec, const auto& desc, AmdGpu::Image sharp) {
                         spec.width = sharp.width;
                         spec.height = sharp.height;
                     });""",
         """        // Donor: inactive, null, FMask and regular images are distinct
        // translation contracts, even if a descriptor address is zero.
        for (size_t i=0;i<images.size();++i) {
            const auto& desc=info->images[i];
            auto& spec=images[i];
            const auto sharp=desc.GetSharp(*info);
            spec.num_bindings=desc.LiveNumBindings(*info);
            spec.is_inactive=desc.IsUniformlyInactive(*info);
            spec.is_fmask=AmdGpu::IsFmask(sharp.GetDataFmt());
            if(spec.is_fmask) spec.dst_select=sharp.DstSelect();
        }
        for (const auto& desc:info->fmasks) {
            const auto sharp=desc.GetSharp(*info);
            auto& spec=fmasks.emplace_back();
            spec.width=sharp.width;
            spec.height=sharp.height;
            spec.mapping=sharp.DstSelect();
            auto& trans=spec.translation;
            trans.type=sharp.GetViewType(desc.source.is_array);
            trans.is_integer=AmdGpu::IsInteger(sharp.GetNumberFmt());
            trans.is_storage=desc.source.is_written;
            trans.is_cube=sharp.GetType()==AmdGpu::ImageType::Cube;
            trans.is_srgb=sharp.GetNumberFmt()==AmdGpu::NumberFormat::Srgb;
            trans.is_fmask=AmdGpu::IsFmask(sharp.GetDataFmt());
            trans.is_inactive=desc.source.IsUniformlyInactive(*info);
            trans.dst_select=sharp.DstSelect();
            trans.num_conversion=sharp.GetNumberConversion();
            trans.num_bindings=desc.source.LiveNumBindings(*info);
            ++binding;
        }""")
    edit(spec,"            if (images[i].num_bindings != other.images[i].num_bindings) return false;",
         """            if (images[i].num_bindings != other.images[i].num_bindings ||
                images[i].is_inactive != other.images[i].is_inactive ||
                images[i].is_fmask != other.images[i].is_fmask ||
                (images[i].is_fmask && images[i].dst_select != other.images[i].dst_select)) return false;""")
    # Bump the raw serialized InfoPersistent and specialization ABI together.
    # Old FMask layouts must never be interpreted as these structures.
    ser=root/"src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    s=ser.read_text()
    for name in ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"):
        match=re.search(rf"{name} = (\d+)u;",s)
        if not match: raise RuntimeError("missing cache ABI "+name)
        s=s.replace(match[0],f"{name} = {int(match[1])+200}u;",1)
    ser.write_text(s)
    live=ser.parent/"order_live_pso_cache.h"
    if live.exists():
        v=live.read_text()
        versions="-".join(re.search(rf"{n} = (\d+)u;",s)[1] for n in ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
        v,n=re.subn(r"live-pso-v1-\d+-\d+-\d+", "live-pso-v1-"+versions, v)
        if n!=1: raise RuntimeError("live PSO ABI namespace drift")
        live.write_text(v)
    return {"uniform_guard":"exact donor CFG edge dominance and all-use guard analysis for Order",
            "fmask":"full source descriptor, classification and swizzle; 4-component payload",
            "specialization":"inactive/FMask state explicit before live matching; preserve compiled array counts",
            "cache":"invalidate old raw metadata and shader ABI",
            "cpu":"FEX retained","fps":"original VideoOut/Android presenter retained"}
