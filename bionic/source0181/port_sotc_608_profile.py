"""Title-specific compatibility profile for the last known SotC gameplay build."""
from pathlib import Path

HEADER = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "common/elf_info.h"
namespace BachataCompat {
inline bool Sotc608() {
#ifdef __ANDROID__
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    return serial=="CUSA08809" || serial=="CUSA08034";
#else
    return false;
#endif
}
inline bool Order1886() {
#ifdef __ANDROID__
    return Common::ElfInfo::Instance().GameSerial()=="CUSA00785";
#else
    return false;
#endif
}
}
'''
def install(root: Path):
    (root/"src/common/bachata_compat_profile.h").write_text(HEADER)
    for rel in (
        "src/core/memory.cpp",
        "src/video_core/buffer_cache/buffer_cache.cpp",
        "src/video_core/renderer_vulkan/vk_rasterizer.cpp",
        "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp",
        "src/video_core/renderer_vulkan/vk_presenter.cpp",
        "src/video_core/renderer_vulkan/vk_scheduler.cpp",
        "src/shader_recompiler/ir/passes/flatten_extended_userdata_pass.cpp",
        "src/shader_recompiler/ir/passes/lower_wave64_pass.cpp",
        "src/core/guest_cpu/hle_call_adapter.cpp",
    ):
        p=root/rel
        # Prefix independent of the upstream include order. Never add to a public ABI header.
        p.write_text('#include "common/bachata_compat_profile.h"\n'+p.read_text())
