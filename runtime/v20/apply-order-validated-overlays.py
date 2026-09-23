#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source")
SRC = ROOT / "runtime/sources/shadps4/src"

def replace(path, old, new, count=1):
    p = SRC / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"overlay anchor missing: {path}: {old[:120]!r}")
    text2 = text.replace(old, new, count)
    p.write_text(text2, encoding="utf-8")
    print(f"patched {path}")

# V5 + V6: keep the fixes at source level and gate them to The Order.
p = SRC / "video_core/renderer_vulkan/vk_rasterizer.cpp"
text = p.read_text(encoding="utf-8")
if '#include "common/elf_info.h"' not in text:
    anchor = '#include "common/assert.h"\n'
    if anchor not in text:
        raise SystemExit("vk_rasterizer include anchor missing")
    text = text.replace(anchor, anchor + '#include "common/elf_info.h"\n', 1)

old = '''        stage->PushUd(binding, push_data);
        BindBuffers(*stage, binding, push_data);
'''
new = '''        stage->PushUd(binding, push_data);

        // ORDER1886 V6 (RE_CONFIRMED): shader-specific user-data correction.
        if (Common::ElfInfo::Instance().GameSerial() == "CUSA00785" &&
            stage->pgm_hash == 0x9846aaffULL) {
            push_data.ud_regs[1] = 0x7F80000FU;
        }

        BindBuffers(*stage, binding, push_data);
'''
if old not in text:
    raise SystemExit("V6 anchor missing")
text = text.replace(old, new, 1)

old = '''    for (const auto& image_desc : stage.images) {
        const auto tsharp = image_desc.GetSharp(stage);
        if (texture_cache.IsMeta(tsharp.Address())) {
'''
new = '''    for (const auto& image_desc : stage.images) {
        auto tsharp = image_desc.GetSharp(stage);

        // ORDER1886 V5 (RE_CONFIRMED): only the two known fragment shader
        // families route the affected texture through the existing null-image path.
        if (Common::ElfInfo::Instance().GameSerial() == "CUSA00785" &&
            (stage.pgm_hash == 0xa7b66f58ULL || stage.pgm_hash == 0xefaaab2bULL)) {
            tsharp.data_format = u64(AmdGpu::DataFormat::FormatInvalid);
        }

        if (texture_cache.IsMeta(tsharp.Address())) {
'''
if old not in text:
    raise SystemExit("V5 anchor missing")
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("patched video_core/renderer_vulkan/vk_rasterizer.cpp (V5+V6)")

# V11: preserve ALL ReadConst users at the same source offset instead of
# overwriting the previous entry in a flat_map. This is the source-level,
# lifetime-safe equivalent of the historical duplicate chain.
p = SRC / "shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp"
text = p.read_text(encoding="utf-8")
old = "using PtrUserList = boost::container::flat_map<u32, Shader::IR::Inst*>;"
if old not in text:
    raise SystemExit("V11 PtrUserList anchor missing")
text = text.replace(old,
    "using PtrUserList = boost::container::flat_multimap<u32, Shader::IR::Inst*>;", 1)

old = "                user_list[inst.Arg(1).U32()] = &inst;"
if old not in text:
    raise SystemExit("V11 insert anchor missing")
text = text.replace(old,
    "                user_list.emplace(inst.Arg(1).U32(), &inst);", 1)
p.write_text(text, encoding="utf-8")
print("patched shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp (V11)")

# Confirmed post-V11 depth-overlap correction (historical V14):
# same-sample color<->depth recreation can use maintenance8 CopyImage.
p = SRC / "video_core/texture_cache/texture_cache.cpp"
text = p.read_text(encoding="utf-8")
if '#include "common/elf_info.h"' not in text:
    # Place alongside other common includes without assuming exact ordering.
    marker = '#include "common/'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("texture_cache common include anchor missing")
    line_end = text.find("\n", idx)
    text = text[:line_end+1] + '#include "common/elf_info.h"\n' + text[line_end+1:]

old = '''        if (cache_image.info.num_samples == 1 && new_info.num_samples == 1) {
            // Perform depth<->color copy using the intermediate copy buffer.
            if (instance.IsMaintenance8Supported()) {
                new_image.CopyImage(cache_image);
            } else {
                const auto& copy_buffer = buffer_cache.GetUtilityBuffer(MemoryUsage::DeviceLocal);
                new_image.CopyImageWithBuffer(cache_image, copy_buffer.Handle(), 0);
            }
        } else if (cache_image.info.num_samples == 1 && new_info.props.is_depth &&
'''
new = '''        if (cache_image.info.num_samples == 1 && new_info.num_samples == 1) {
            // Perform depth<->color copy using the intermediate copy buffer.
            if (instance.IsMaintenance8Supported()) {
                new_image.CopyImage(cache_image);
            } else {
                const auto& copy_buffer = buffer_cache.GetUtilityBuffer(MemoryUsage::DeviceLocal);
                new_image.CopyImageWithBuffer(cache_image, copy_buffer.Handle(), 0);
            }
        } else if (Common::ElfInfo::Instance().GameSerial() == "CUSA00785" &&
                   cache_image.info.num_samples == new_info.num_samples &&
                   instance.IsMaintenance8Supported()) {
            // ORDER1886 V14 (confirmed): maintenance8 permits the same-sample
            // color<->depth overlap copy, including the observed R32_SFLOAT
            // 2x MSAA -> D32_SFLOAT 2x MSAA case.
            new_image.CopyImage(cache_image);
        } else if (cache_image.info.num_samples == 1 && new_info.props.is_depth &&
'''
if old not in text:
    raise SystemExit("depth overlap anchor missing")
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("patched video_core/texture_cache/texture_cache.cpp (confirmed V14 carry-forward)")

print("Order overlays applied successfully")
