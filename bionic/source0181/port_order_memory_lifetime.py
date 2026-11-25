"""Adapt the actual Order 0.1.37 GPU memory-pressure and cache-lifetime rules.

Source: c53cd01d032995fe622033623ab64b4cf6b02233 with 756a4f0
Android overlays. This is an adaptation to 0.18.1, not an imported runtime.
"""
from pathlib import Path

def apply(root: Path):
    def edit(rel, old, new):
        p=root/rel
        s=p.read_text()
        if s.count(old)!=1:
            raise RuntimeError("Order cache parity source drift: "+rel+": "+old[:100])
        p.write_text(s.replace(old,new,1))
    tc="src/video_core/texture_cache/texture_cache.cpp"
    vi="src/video_core/renderer_vulkan/vk_instance.cpp"
    vh="src/video_core/renderer_vulkan/vk_instance.h"
    edit(vh,"    [[nodiscard]] u64 GetLiveGpuMemoryBudget() const;",
         "    [[nodiscard]] u64 GetLiveGpuMemoryBudget() const;\n    [[nodiscard]] u64 GetDeviceMemoryBudgetNow() const;")
    edit(vi,"u64 Instance::GetLiveGpuMemoryBudget() const {",
         """u64 Instance::GetDeviceMemoryBudgetNow() const {
    if (!supports_memory_budget) return 0;
    vk::PhysicalDeviceMemoryBudgetPropertiesEXT ext{};
    vk::PhysicalDeviceMemoryProperties2 props{.pNext=&ext};
    physical_device.getMemoryProperties2(&props);
    u64 budget = 0;
    for (const size_t heap : valid_heaps) {
        if (heap < props.memoryProperties.memoryHeapCount) budget += ext.heapBudget[heap];
    }
    return budget;
}

u64 Instance::GetLiveGpuMemoryBudget() const {""")
    edit(tc,'#include "common/assert.h"', '#include "common/assert.h"\n#include "video_core/amdgpu/regs_color.h"')
    edit(tc, """        if (telemetry.measured && telemetry.live_budget != 0) {
            const u64 live = telemetry.live_budget;
            trigger_gc_memory = std::min(trigger_gc_memory, live / 2);
            pressure_gc_memory = std::min(pressure_gc_memory, live - live / 4);
            critical_gc_memory = std::min(critical_gc_memory, live - live / 8);
        }""",
    """        if (AmdGpu::BachataOrderNoMsaa()) {
            // Donor compares heapUsage to the same driver's current heapBudget.
            // Recompute, not min(previous, budget): temporary pressure must recover.
            const u64 budget = instance.GetDeviceMemoryBudgetNow();
            if (budget) {
                trigger_gc_memory = budget / 10 * 7;
                pressure_gc_memory = budget / 100 * 85;
                critical_gc_memory = budget / 100 * 95;
            }
        } else if (telemetry.measured && telemetry.live_budget != 0) {
            const u64 live = telemetry.live_budget;
            trigger_gc_memory = std::min(trigger_gc_memory, live / 2);
            pressure_gc_memory = std::min(pressure_gc_memory, live - live / 4);
            critical_gc_memory = std::min(critical_gc_memory, live - live / 8);
        }""")
    edit(tc,"            DownloadImageMemory(image_id);\n        }\n        FreeImage(image_id);",
            """            // The Order donor completes writeback while pages still belong
            // to the image. Deferred callbacks must not overwrite a reused heap.
            DownloadImageMemory(image_id, AmdGpu::BachataOrderNoMsaa());
        }
        FreeImage(image_id);""")
    return {"budget":"The Order current heapBudget vs heapUsage, thresholds 70/85/95; can recover",
            "imageLifetime":"synchronous GPU writeback before releasing tracked pages",
            "scope":"The Order only; other games preserve their existing behavior",
            "reference":"exact effective donor texture_cache.cpp and vk_instance.cpp",
            "remaining":"deferred readback ownership queue, worker pipelines and draw snapshots"}
