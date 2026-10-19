#!/usr/bin/env python3
"""SOTC IT_GET_LOD_STATS port for zenithblue-oss/shadps4-arm64.
Original behavior: tomasmosca/shadPS4-sotc (GPL-2.0-or-later).
Apply to the public source checkout, not the stripped R30 core025 ELF.
"""
from pathlib import Path
import argparse

def change(s, before, after, label):
    n=s.count(before)
    if n!=1:
        raise RuntimeError(f"{label}: expected 1 anchor, found {n}")
    return s.replace(before,after)

def patch(root):
    names=[
        "src/video_core/amdgpu/pm4_cmds.h",
        "src/video_core/amdgpu/liverpool.cpp",
        "src/video_core/renderer_vulkan/vk_rasterizer.h",
        "src/video_core/renderer_vulkan/vk_rasterizer.cpp",
    ]
    paths=[root/n for n in names]
    pm4,li,rh,rc=[p.read_text() for p in paths]
    pm4=change(pm4,"struct PM4CmdCondExec {", """// PM4 texture LOD feedback: CUSA08809.
struct PM4CmdGetLodStats {
    PM4Type3Header header;
    u32 bu_size;
    u32 base_lo;
    union { BitField<0, 2, u32> base_hi; u32 control; };
    u32 NumBytes() const { return bu_size + 32; }
    VAddr Address() const { return (VAddr{base_lo} << 6) |
                                   (VAddr{base_hi.Value()} << 38); }
};

struct PM4CmdCondExec {""", "PM4 GetLodStats")
    li=change(li, """            case PM4ItOpcode::GetLodStats: {
                LOG_WARNING(Render_Vulkan, "Unimplemented IT_GET_LOD_STATS");
                break;
            }""", """            case PM4ItOpcode::GetLodStats: {
                const auto* stats = reinterpret_cast<const PM4CmdGetLodStats*>(header);
                if (!rasterizer || !rasterizer->WriteLodStats(stats->Address(),
                                                              stats->NumBytes())) {
                    LOG_DEBUG(Render_Vulkan, "IT_GET_LOD_STATS skipped");
                }
                break;
            }""", "PM4 handler")
    rh=change(rh,"#include <memory>","#include <array>\n#include <memory>", "header include")
    rh=change(rh,"    void UnmapMemory(VAddr addr, u64 size);",
              "    void UnmapMemory(VAddr addr, u64 size);\n    bool WriteLodStats(VAddr addr, u32 bytes);", "Rasterizer API")
    rh=change(rh,"    bool attachment_feedback_loop{};",
              "    bool attachment_feedback_loop{};\n    std::array<u32, 256> sotc_lod_banks{};", "LOD bank storage")
    impl="""// Approximate GCN T# counter bank feedback for SOTC texture streaming.
// This intentionally does not change readback mode, DMA or other game behavior.
bool Rasterizer::WriteLodStats(VAddr addr, u32 bytes) {
    constexpr u32 HeaderBytes = 0x40;
    constexpr u32 MaxBytes = 16_MB;
    constexpr u64 NotSampled = u64{0xF} << 56;
    if (bytes <= HeaderBytes || bytes > MaxBytes ||
        ((bytes - HeaderBytes) % sizeof(u64)) != 0 ||
        !IsMapped(addr, bytes) || !memory->IsValidMapping(addr, bytes)) {
        return false;
    }
    const u32 count = (bytes - HeaderBytes) / sizeof(u64);
    std::vector<u64> entries(count);
    for (u32 i = 0; i < count; ++i) {
        const u32 uses = sotc_lod_banks[i % sotc_lod_banks.size()];
        // Mip 0/1 can overfill SOTC's streaming pool and corrupt guest heap.
        // AjncSystem's SOTC port uses a bounded priority and conservative mip 2.
        const u64 priority = std::min<u64>(u64{uses} * 256, 0xFFFFFF);
        entries[i] = uses != 0 ? (u64{2} << 56) | (priority << 32) : NotSampled;
    }
    if (!memory->TryWriteBacking(reinterpret_cast<void*>(addr + HeaderBytes),
                                  entries.data(), entries.size() * sizeof(u64))) {
        return false;
    }
    sotc_lod_banks.fill(0);
    return true;
}

"""
    rc=change(rc,"void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {",
              impl+"void Rasterizer::BindTextures(const Shader::Info& stage, Shader::Backend::Bindings& binding) {", "LOD writes")
    rc=change(rc,"        const Shader::MipStorageFallbackMode mip_fallback_mode = image_desc.mip_fallback_mode;",
"""        if (tsharp.lod_hw_cnt_en) {
            u32& count = sotc_lod_banks[tsharp.counter_bank_id];
            if (count < 0xFFFFFFu) { ++count; }
        }
        const Shader::MipStorageFallbackMode mip_fallback_mode = image_desc.mip_fallback_mode;""",
"LOD texture accounting")
    for p,s in zip(paths,[pm4,li,rh,rc]):p.write_text(s)
    print("PASS: PM4 decoder, LOD bank accounting, protected-backing writes")

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("source", type=Path)
    patch(a.parse_args().source)
