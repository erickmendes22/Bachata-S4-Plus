#!/usr/bin/env python3
"""Port the donor's save/area-load texture collection and throttle memory telemetry."""
from pathlib import Path
HEADER = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <atomic>
#include <cstdlib>
#include <string_view>
namespace BachataSotcLoad {
inline std::atomic<bool> pending{false};
inline bool Notify(std::string_view serial, std::string_view line) {
    if (serial!="CUSA08809" && serial!="CUSA08034") return false;
    static const bool enabled=[] {const char* v=std::getenv("SOTC_LOAD_FLUSH");return !v || v[0]!='0';}();
    if (!enabled || line.find("st_gameflow() starting game")==std::string_view::npos) return false;
    pending.store(true,std::memory_order_release);
    return true;
}
template<class I> bool SafeToDrop(const I& image, bool gpu_modified, bool registered) {
    return registered && !gpu_modified && !image.binding.is_bound && !image.binding.is_target &&
        !image.binding.needs_rebind && !image.usage.storage && !image.usage.render_target &&
        !image.usage.depth_target && !image.usage.vo_surface;
}
}
'''
def apply(root: Path):
    root=Path(root)/'src'
    (root/'video_core/sotc_load_flush.h').write_text(HEADER)
    def edit(rel,a,b):
        p=root/rel;s=p.read_text();assert s.count(a)==1,(rel,a[:100],s.count(a));p.write_text(s.replace(a,b,1))
    log='core/file_sys/devices/logger.cpp'
    tex='video_core/texture_cache/texture_cache.cpp'
    edit(log,'#include "common/logging/log.h"','#include "common/logging/log.h"\n#include "common/elf_info.h"\n#include "video_core/sotc_load_flush.h"')
    edit(log,'    if (is_err) {','    if (BachataSotcLoad::Notify(Common::ElfInfo::Instance().GameSerial(), std::string_view{buffer})) {\n        LOG_INFO(Tty,"BACHATA_SOTC_LOAD_FLUSH_REQUEST");\n    }\n    if (is_err) {')
    edit(tex,'#include <cstdlib>','#include <cstdlib>\n#include <chrono>\n#include "video_core/sotc_load_flush.h"')
    edit(tex,'    if (instance.CanReportMemoryUsage()) {\n        // Release 0.2.6', '''    // Same 20 ms query cadence as the donor; keep the live-budget contract.
    static thread_local std::chrono::steady_clock::time_point last_sotc_query{};
    const auto now=std::chrono::steady_clock::now();
    const bool sample=!BachataSotcLod::Enabled() || now-last_sotc_query>=std::chrono::milliseconds{20};
    if (instance.CanReportMemoryUsage() && sample) {
        last_sotc_query=now;
        // Release 0.2.6''')
    edit(tex,'void TextureCache::RunGarbageCollector() {','''void TextureCache::RunGarbageCollector() {
    if (BachataSotcLod::Enabled() && BachataSotcLoad::pending.exchange(false,std::memory_order_acq_rel)) {
        // The donor drops unused images after a load. FEX cannot discard guest
        // data whose only authoritative copy is GPU-owned, including targets.
        std::unique_lock lock{mutex,std::defer_lock};
        if (arena_refresh_depth || gc_tick==0 || !lock.try_lock()) {
            BachataSotcLoad::pending.store(true,std::memory_order_release);
        } else {
            size_t freed=0;
            lru_cache.ForEachItemBelow(gc_tick-1,[&](ImageId id) {
                const auto& image=slot_images[id];
                if (!BachataSotcLoad::SafeToDrop(image,True(image.flags&ImageFlagBits::GpuModified),
                                                True(image.flags&ImageFlagBits::Registered))) return;
                FreeImage(id);++freed;
            });
            LOG_INFO(Render_Vulkan,"BACHATA_SOTC_LOAD_FLUSH images={}",freed);
        }
    }''')
