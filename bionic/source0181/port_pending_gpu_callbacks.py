#!/usr/bin/env python3
"""Make GPU deferred completion safe when a fault rebind submits/waits again.

Arena OOM recovery reaches Finish from FaultManager's deferred callback. A
callback must leave the queue before invocation, otherwise nested completion
invokes that same callback again. Keep the recursive scheduler lock and permit
later completed releases to run before the allocation retry. Fault batches own
their range sets so such nested callbacks cannot invalidate an outer iterator.
"""
from pathlib import Path


def apply(root):
    root=Path(root)

    def edit(rel,old,new):
        path=root/rel;text=path.read_text()
        if text.count(old)!=1:
            raise RuntimeError(f"GPU pending callback anchor drift: {rel}: {old!r}")
        path.write_text(text.replace(old,new,1))

    edit("src/video_core/renderer_vulkan/vk_scheduler.cpp", """        pending_ops.front().callback();
        pending_ops.pop();""", """        // A fault rebind may run Finish() while recovering from an allocation
        // failure. Own the callable locally and remove it before invocation:
        // nested completion may reclaim later allocations, never this one again.
        auto operation = std::move(pending_ops.front());
        pending_ops.pop();
        operation.callback();""")
    edit("src/video_core/buffer_cache/fault_manager.cpp", """    scheduler.DeferOperation([this, mapped, area = current_area] {
        fault_ranges.Clear();""", """    scheduler.DeferOperation([this, mapped, area = current_area] {
        // A nested Finish may execute another completed fault batch. Its ranges
        // must not clear or mutate the range set currently being iterated here.
        RangeSet fault_ranges;""")
    edit("src/video_core/buffer_cache/fault_manager.h", "    RangeSet fault_ranges;\n", "")
    return {"cores":"Order and SotC", "scheduler":"pop before invocation; callable lives through return",
            "ordering":"FIFO invocation with nested completed frees permitted",
            "faults":"per-callback ranges; nested batches cannot invalidate an outer iterator"}
