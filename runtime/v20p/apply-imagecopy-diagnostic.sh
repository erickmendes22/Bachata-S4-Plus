#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=be6bc2e9c60799e071dd2fafa6216e8d80ec619c
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
[[ "$(git rev-parse HEAD)" == "$SOURCE_COMMIT" ]] || { echo "V20P wrong source" >&2; exit 30; }

# Reuse the compiled/validated real-predication port but keep ZPASS fail-open.
V20H_VARIANT=zpass-failopen bash "$SCRIPT_DIR/../v20h/apply-sync-isolation.sh"

python3 - <<'PY'
from pathlib import Path
p=Path('src/video_core/texture_cache/image.cpp')
s=p.read_text()
a=s.index('void Image::CopyImage(Image& src_image) {')
b=s.index('void Image::CopyImageWithBuffer(Image& src_image',a)
f=s[a:b]

# O-A/O-B changed synchronization here. V20P goes back to the V20I-style path:
# no forced EndRendering/Finish in CopyImage; diagnostics only.
old='    scheduler->EndRendering();\n\n'
if f.count(old)!=1: raise SystemExit('V20P: CopyImage EndRendering anchor mismatch')
f=f.replace(old,'',1)

anchor='    const auto& src_info = src_image.info;\n\n'
diag=r'''    const auto& src_info = src_image.info;

    // V20P: one-run classifier for all leading ImageCopy hypotheses.
    static u64 p20_id_gen{};
    static u64 p20_lines{};
    const u64 p20_id = ++p20_id_gen;
    if (p20_id == 1) {
        LOG_WARNING(Render_Vulkan, "P20 ACTIVE revision=2 CopyImage diagnostics reached");
    }
    const auto p20_sl = src_image.backing->state.layout;
    const auto p20_dl = backing->state.layout;
    const auto p20_sa = src_image.aspect_mask & ~vk::ImageAspectFlagBits::eStencil;
    const auto p20_da = aspect_mask & ~vk::ImageAspectFlagBits::eStencil;
    const bool p20_fmt = src_info.pixel_format != info.pixel_format;
    const bool p20_aspect = p20_sa != p20_da;
    const bool p20_layers = src_info.resources.layers != info.resources.layers;
    const bool p20_mips = src_info.resources.levels != info.resources.levels;
    const bool p20_samples = src_info.num_samples != info.num_samples;
    const bool p20_cd = src_info.props.is_depth != info.props.is_depth;
    const bool p20_stencil = src_info.props.has_stencil || info.props.has_stencil;
    const bool p20_23 = !src_info.props.is_volume && info.props.is_volume;
    const bool p20_32 = src_info.props.is_volume && !info.props.is_volume;
    const bool p20_extent = src_info.size.width != info.size.width ||
                            src_info.size.height != info.size.height ||
                            src_info.size.depth != info.size.depth;
    const bool p20_alias = src_image.Overlaps(info.guest_address, info.guest_size);
    const bool p20_same_tile = src_info.guest_address == info.guest_address &&
                               src_info.tile_mode != info.tile_mode;
    const bool p20_oob = src_info.size.width > info.size.width ||
                         src_info.size.height > info.size.height ||
                         (src_info.props.is_volume && info.props.is_volume &&
                          src_info.size.depth > info.size.depth);
    const bool p20_anom = p20_fmt || p20_aspect || p20_layers || p20_mips || p20_samples ||
                          p20_cd || p20_stencil || p20_23 || p20_32 || p20_extent ||
                          p20_alias || p20_same_tile || p20_oob;
    const bool p20_emit = p20_id <= 128 || !(p20_id % 512) || (p20_anom && p20_lines < 4096);
    if (p20_emit) {
        ++p20_lines;
        LOG_WARNING(Render_Vulkan,
          "P20 COPY id={} src_uid={} dst_uid={} src=0x{:x}+0x{:x} dst=0x{:x}+0x{:x} "
          "fmt={}->{} depth={}->{} stencil={}->{} aspect=0x{:x}->0x{:x} "
          "size={}x{}x{}->{}x{}x{} pitch={}->{} tile={}->{} mips={}->{} layers={}->{} "
          "samples={}->{} layout={}->{} iflags=0x{:x}->0x{:x} usage=0x{:x}->0x{:x} "
          "bind={}/{}/{}/{}->{}/{}/{}/{} FORMAT_MISMATCH={} ASPECT_MISMATCH={} "
          "LAYER_MISMATCH={} MIP_MISMATCH={} SAMPLE_MISMATCH={} COLOR_DEPTH_COPY={} "
          "STENCIL_STRIPPED={} 2D_TO_3D={} 3D_TO_2D={} EXTENT_MISMATCH={} "
          "ALIAS_BACKING={} SAME_ADDRESS_DIFFERENT_TILING={} RANGE_OOB={}",
          p20_id,src_image.image_uid,image_uid,src_info.guest_address,src_info.guest_size,
          info.guest_address,info.guest_size,vk::to_string(src_info.pixel_format),
          vk::to_string(info.pixel_format),static_cast<bool>(src_static_cast<bool>(info.props.is_depth)),static_cast<bool>(info.props.is_depth),
          static_cast<bool>(src_static_cast<bool>(info.props.has_stencil)),static_cast<bool>(info.props.has_stencil),
          static_cast<VkImageAspectFlags>(p20_sa),static_cast<VkImageAspectFlags>(p20_da),
          src_info.size.width,src_info.size.height,src_info.size.depth,
          info.size.width,info.size.height,info.size.depth,src_info.pitch,info.pitch,
          static_cast<u32>(src_info.tile_mode),static_cast<u32>(info.tile_mode),
          src_info.resources.levels,info.resources.levels,src_info.resources.layers,
          info.resources.layers,src_info.num_samples,info.num_samples,
          vk::to_string(p20_sl),vk::to_string(p20_dl),static_cast<u32>(src_image.flags),
          static_cast<u32>(flags),static_cast<VkImageUsageFlags>(src_image.usage_flags),
          static_cast<VkImageUsageFlags>(usage_flags),static_cast<u32>(src_image.binding.is_bound),
          static_cast<u32>(src_image.binding.is_target),static_cast<u32>(src_image.binding.needs_rebind),static_cast<u32>(src_image.binding.force_general),
          static_cast<u32>(binding.is_bound),static_cast<u32>(binding.is_target),static_cast<u32>(binding.needs_rebind),static_cast<u32>(binding.force_general),
          p20_fmt,p20_aspect,p20_layers,p20_mips,p20_samples,p20_cd,p20_stencil,p20_23,p20_32,
          p20_extent,p20_alias,p20_same_tile,p20_oob);
    }

'''
if anchor not in f: raise SystemExit('V20P: src_info anchor missing')
f=f.replace(anchor,diag,1)

region_anchor = '        regions.push_back(region);'
region_trace = r'''        if (p20_emit) {
            LOG_WARNING(Render_Vulkan,
                "P20 REGION id={} mip={} src_layer={}+{} dst_layer={}+{} "
                "src_offset={},{},{} dst_offset={},{},{} extent={}x{}x{}",
                p20_id, mip,
                region.srcSubresource.baseArrayLayer, region.srcSubresource.layerCount,
                region.dstSubresource.baseArrayLayer, region.dstSubresource.layerCount,
                region.srcOffset.x, region.srcOffset.y, region.srcOffset.z,
                region.dstOffset.x, region.dstOffset.y, region.dstOffset.z,
                region.extent.width, region.extent.height, region.extent.depth);
        }
        regions.push_back(region);'''
if f.count(region_anchor) != 1: raise SystemExit('V20P region anchor mismatch')
f=f.replace(region_anchor,region_trace,1)

s=s[:a]+f+s[b:]
p.write_text(s)
PY

git add src/video_core/texture_cache/image.cpp
git diff --cached --check
grep -q 'V20H ZPASS fail-open' src/video_core/amdgpu/liverpool.cpp
grep -q 'P20 COPY id=' src/video_core/texture_cache/image.cpp
python3 - <<'PY'
from pathlib import Path
s=Path('src/video_core/texture_cache/image.cpp').read_text()
f=s[s.index('void Image::CopyImage(Image& src_image) {'):s.index('void Image::CopyImageWithBuffer(Image& src_image')]
assert 'scheduler->EndRendering();' not in f
assert 'Finish(' not in f
print('V20P verified: fail-open + multipath diagnostics; no forced CopyImage EndRendering/Finish')
PY

echo 'V20P ready'
git diff --cached --stat
