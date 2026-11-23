#!/usr/bin/env python3
"""Reject malformed AMD GPU image swizzles before creating Vulkan image views.

CUSA00785 in BS4-20261123-02682AF4 logs invalid SRT descriptors, then
aborts in liverpool_to_vk::ComponentSwizzle when the selector is 2 or 3.
These are reserved, unlike Zero=0, One=1, R/G/B/A=4..7.
The ordinary Vulkan null image descriptor path already exists; use that
path rather than substituting arbitrary color channels for garbage data.

This is crash containment, not a claim that the nonuniform SRT source
has been reconstructed. Keep the CPU/GPU SRT investigation separate.
"""
from pathlib import Path

def apply(root: Path) -> dict:
    file=root/"src/video_core/renderer_vulkan/vk_rasterizer.cpp"
    text=file.read_text()
    old="""        if (!memory->IsValidGpuMapping(tsharp.Address(), 0) ||
            !magic_enum::enum_contains(data_fmt) || !magic_enum::enum_contains(num_fmt)) {
            LOG_WARNING(Render_Vulkan,
                        "Rejecting invalid T# address={:#x}, pitch={}, width={}, "
                        "data_format={}, num_format={}",
                        tsharp.Address(), tsharp.pitch, tsharp.width, static_cast<u32>(data_fmt),
                        static_cast<u32>(num_fmt));"""
    new="""        // BACHATA_RELEASE026_IMAGE_SWIZZLE_GUARD: AMD image DST_SEL
        // encodings 2 and 3 are reserved, not Vulkan components.
        // Invalid SRT data must not reach ComponentSwizzle() / UNREACHABLE.
        // Preserve a null descriptor rather than forging valid RGB channels.
        const auto legal_select = [](u64 s) {
            return s == 0 || s == 1 || (s >= 4 && s <= 7);
        };
        const bool swizzle_selector_valid =
            legal_select(tsharp.dst_sel_x) && legal_select(tsharp.dst_sel_y) &&
            legal_select(tsharp.dst_sel_z) && legal_select(tsharp.dst_sel_w);
        if (!memory->IsValidGpuMapping(tsharp.Address(), 0) ||
            !magic_enum::enum_contains(data_fmt) || !magic_enum::enum_contains(num_fmt) ||
            !swizzle_selector_valid) {
            LOG_WARNING(Render_Vulkan,
                        "BACHATA_RELEASE026_BAD_T# address={:#x}, pitch={}, width={}, "
                        "data_format={}, num_format={} dst_sel={},{},{},{}",
                        tsharp.Address(), tsharp.pitch, tsharp.width, static_cast<u32>(data_fmt),
                        static_cast<u32>(num_fmt), u32(tsharp.dst_sel_x), u32(tsharp.dst_sel_y),
                        u32(tsharp.dst_sel_z), u32(tsharp.dst_sel_w));"""
    if text.count(old)!=1:
        raise RuntimeError(f"0.18.1 texture validation drift: found {text.count(old)}")
    text=text.replace(old,new,1)
    if "liverpool_to_vk.cpp" in text and "vk::ComponentSwizzle::eR" in text:
        raise RuntimeError("Unexpected swallowed renderer source")
    file.write_text(text)
    return {"scope":"all texture descriptors with reserved AMD channel selector 2/3",
            "effect":"GPU null binding instead of abort in ComponentSwizzle",
            "notClaimed":"nonuniform SRT offsets fixed or missing textures reconstructed"}
