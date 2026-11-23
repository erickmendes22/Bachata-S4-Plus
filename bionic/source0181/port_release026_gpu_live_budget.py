#!/usr/bin/env python3
"""Restore live GPU memory-budget telemetry and pressure-aware GC from Release.

The pinned 0.18.1 TextureCache freezes its thresholds using startup memory
budget. Release 0.2.6 has GetLiveGpuMemoryBudget / GetGpuMemoryTelemetry
and adapts to memory pressure. This patch computes live Vulkan
VK_EXT_memory_budget plus the VMA allocator's own allocation size.
It is never based on an invented fixed device RAM amount.
"""
from pathlib import Path

def repl(text: str, old: str, new: str, name: str) -> str:
    n=text.count(old)
    if n!=1:raise RuntimeError(f"GPU budget source drift {name}: {n}")
    return text.replace(old,new,1)

def apply(root: Path) -> dict:
    header=root/"src/video_core/renderer_vulkan/vk_instance.h"
    cpp=root/"src/video_core/renderer_vulkan/vk_instance.cpp"
    cache=root/"src/video_core/texture_cache/texture_cache.cpp"
    h=header.read_text();c=cpp.read_text();t=cache.read_text()
    h=repl(h,"namespace Vulkan {\n\nclass Instance {",
r"""namespace Vulkan {

// The live memory snapshot reflects both other Android processes and
// this VMA allocator. Physical heapBudget is NOT equal to emulator headroom.
struct GpuMemoryTelemetry {
    u64 live_budget{};
    u64 device_usage{};
    u64 vma_usage{};
    u64 device_available{};
    bool measured{};
};

class Instance {""","telemetry type")
    h=repl(h,
        "    [[nodiscard]] u64 GetDeviceMemoryUsage() const;\n",
        "    [[nodiscard]] u64 GetDeviceMemoryUsage() const;\n"
        "    [[nodiscard]] u64 GetLiveGpuMemoryBudget() const;\n"
        "    [[nodiscard]] GpuMemoryTelemetry GetGpuMemoryTelemetry() const;\n",
        "live instance API")
    c=repl(c,"u64 Instance::GetDeviceMemoryUsage() const {\n",
r"""// BACHATA_RELEASE026_GPU_LIVE_BUDGET
GpuMemoryTelemetry Instance::GetGpuMemoryTelemetry() const {
    GpuMemoryTelemetry out{};
    out.live_budget = total_memory_budget;
    if (!allocator || !supports_memory_budget) return out;
    vk::PhysicalDeviceMemoryBudgetPropertiesEXT ext{};
    vk::PhysicalDeviceMemoryProperties2 props{.pNext=&ext};
    physical_device.getMemoryProperties2(&props);
    VmaBudget alloc_budgets[VK_MAX_MEMORY_HEAPS]{};
    vmaGetHeapBudgets(allocator, alloc_budgets);
    u64 emulator_headroom = 0;
    for (const size_t heap : valid_heaps) {
        if (heap >= props.memoryProperties.memoryHeapCount) continue;
        const u64 budget = ext.heapBudget[heap];
        const u64 used = ext.heapUsage[heap];
        const u64 free = budget > used ? budget - used : 0;
        const u64 ours = alloc_budgets[heap].usage;
        out.device_usage += used;
        out.vma_usage += ours;
        out.device_available += free;
        // Headroom includes our OWN allocator's usage, otherwise GC
        // thresholds would shrink every time the emulator allocates.
        const u64 available = free > UINT64_MAX - ours ? UINT64_MAX : free + ours;
        emulator_headroom = available > UINT64_MAX - emulator_headroom
                               ? UINT64_MAX : emulator_headroom + available;
    }
    out.measured = true;
    out.live_budget = std::min(out.live_budget, emulator_headroom);
    return out;
}

u64 Instance::GetLiveGpuMemoryBudget() const {
    return GetGpuMemoryTelemetry().live_budget;
}

u64 Instance::GetDeviceMemoryUsage() const {
""","live budget implementation")
    t=repl(t,
        """    if (instance.CanReportMemoryUsage()) {
        total_used_memory = instance.GetDeviceMemoryUsage();
    }
    if (total_used_memory < trigger_gc_memory) {""",
        """    if (instance.CanReportMemoryUsage()) {
        // Release 0.2.6's missing live budget means memory pressure
        // MUST be sampled at GC time, not only at Vulkan device creation.
        const auto telemetry = instance.GetGpuMemoryTelemetry();
        total_used_memory = telemetry.device_usage;
        if (telemetry.measured && telemetry.live_budget != 0) {
            const u64 live = telemetry.live_budget;
            trigger_gc_memory = std::min(trigger_gc_memory, live / 2);
            pressure_gc_memory = std::min(pressure_gc_memory, live - live / 4);
            critical_gc_memory = std::min(critical_gc_memory, live - live / 8);
        }
    }
    if (total_used_memory < trigger_gc_memory) {""","live GPU GC thresholds")
    header.write_text(h);cpp.write_text(c);cache.write_text(t)
    return {
        "ported": ["Vulkan::Instance::GetLiveGpuMemoryBudget",
                   "Vulkan::Instance::GetGpuMemoryTelemetry",
                   "TextureCache::GarbageCollectImages live budget pressure"],
        "uses": ["VK_EXT_memory_budget", "vmaGetHeapBudgets"],
        "doesNotUseHardcodedRam": True,
    }
