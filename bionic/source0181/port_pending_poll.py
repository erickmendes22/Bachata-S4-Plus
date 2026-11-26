#!/usr/bin/env python3
"""Avoid redundant timeline queries on Order/SotC draw and dispatch paths.

The active Order donor uses an empty-queue fast exit and a 1/32 pending-poll
limit. The SotC donor also skips a front callback whose tick is not submitted.
Keep the FEX scheduler's forced completion path, recursive lock, and pop-before-
callback ownership. Only the four rasterizer hot callers use the new policy.

Apply after DrawPipe, pending_gpu_callbacks, and the Order runtime submit fix.
No shader/cache ABI, command ordering, draw-write hazard, or PM4 policy changes.
"""
import argparse
from pathlib import Path


TITLE_POLICY = r'''static bool UsesTargetPendingPoll() {
#ifdef __ANDROID__
    const auto serial = Common::ElfInfo::Instance().GameSerial();
    return serial == "CUSA00785" || serial == "CUSA08809" || serial == "CUSA08034";
#else
    return false;
#endif
}

'''

HOT_POLL = r'''void Scheduler::PopPendingOperationsHot() {
    // BACHATA_PENDING_POLL: only draw/dispatch polling is rate limited.
    // Recovery, submission and explicit waits keep PopPendingOperations' forced
    // path. Other games retain their existing per-draw behavior.
    if (!UsesTargetPendingPoll()) {
        PopPendingOperations();
        return;
    }
    DrainDrawPipe();
    std::unique_lock lk(pending_ops_mutex);
    if (pending_ops.empty()) {
        return;
    }
    const u64 front_tick = pending_ops.front().gpu_tick;
    if (!work_semaphore.IsFree(front_tick)) {
        // With the recorder, advancing CurrentTick only records a submission;
        // the driver cannot complete it until the recorder has published it.
        if (front_tick >= CurrentTick() ||
            (recorder && front_tick > RecordedSubmitTick())) {
            return;
        }
        if ((++pending_hot_polls & 31u) != 0) {
            return;
        }
        PopPendingOperations();
        return;
    }
    // A Wait/Submit/priority poll already observed this tick. Retire immediately
    // without a second Vulkan query. The recursive lock preserves FIFO even if
    // a callback reaches Finish and frees later allocations before retrying OOM.
    PopPendingOperations(false);
}

'''


def replace(text, old, new, label):
    if text.count(old) != 1:
        raise RuntimeError(f"pending poll anchor drift ({label}): {text.count(old)}")
    return text.replace(old, new, 1)


def apply(root):
    root = Path(root) / "src/video_core/renderer_vulkan"
    paths = {name: root / name for name in
             ("vk_scheduler.h", "vk_scheduler.cpp", "vk_rasterizer.cpp")}
    texts = {name: path.read_text() for name, path in paths.items()}
    header = texts["vk_scheduler.h"]
    source = texts["vk_scheduler.cpp"]

    if "    void PopPendingOperations();" in header:
        # SotC's force path originally had no known-tick overload. Its default
        # remains an immediate Refresh; all existing callers remain unchanged.
        header = replace(header, "    void PopPendingOperations();",
                         "    void PopPendingOperations(bool refresh = true);", "SotC declaration")
        source = replace(source, """void Scheduler::PopPendingOperations() {
    DrainDrawPipe();
    std::unique_lock lk(pending_ops_mutex);
    work_semaphore.Refresh();""", """void Scheduler::PopPendingOperations(bool refresh) {
    DrainDrawPipe();
    std::unique_lock lk(pending_ops_mutex);
    if (refresh) work_semaphore.Refresh();""", "SotC force path")

    header = replace(header, "    void PopPendingOperations(bool refresh = true);",
                     "    void PopPendingOperations(bool refresh = true);\n"
                     "    /// Poll completion from draw/dispatch without querying an idle timeline.\n"
                     "    void PopPendingOperationsHot();", "hot declaration")
    header = replace(header, "    std::recursive_mutex pending_ops_mutex;",
                     "    std::recursive_mutex pending_ops_mutex;\n"
                     "    u32 pending_hot_polls = 0; ///< Protected by pending_ops_mutex.",
                     "hot counter")
    if '#include "common/elf_info.h"' not in source:
        source = replace(source, '#include "common/assert.h"',
                         '#include "common/assert.h"\n#include "common/elf_info.h"',
                         "title policy")
    source = replace(source, "void Scheduler::PopPendingOperations(bool refresh) {",
                     TITLE_POLICY + HOT_POLL + "void Scheduler::PopPendingOperations(bool refresh) {",
                     "hot implementation")
    rasterizer = texts["vk_rasterizer.cpp"]
    # All four calls are at the start of Draw/DrawIndirect/DispatchDirect/Indirect.
    # Fail if a recovery path is ever added to this file rather than changing it.
    if rasterizer.count("    scheduler.PopPendingOperations();") != 4:
        raise RuntimeError("pending poll: expected exactly four rasterizer hot callers")
    for name in ("Draw", "DrawIndirect", "DispatchDirect", "DispatchIndirect"):
        start = rasterizer.index(f"void Rasterizer::{name}(")
        end = rasterizer.index("\n}", start) + 2
        body = rasterizer[start:end]
        updated = replace(body, "    scheduler.PopPendingOperations();",
                          "    scheduler.PopPendingOperationsHot();", name)
        rasterizer = rasterizer[:start] + updated + rasterizer[end:]
    texts.update({"vk_scheduler.h": header, "vk_scheduler.cpp": source,
                  "vk_rasterizer.cpp": rasterizer})
    # Validate all anchors before writing any of the three files.
    for name, path in paths.items():
        path.write_text(texts[name])
    return {"pendingPoll": "Order/SotC draw and dispatch only; empty/unsubmitted skip; 1/32 polling",
            "forcedCompletion": "unchanged FIFO; pop before callback; nested Finish/OOM remains immediate",
            "otherTitles": "original forced per-draw polling"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    print(apply(parser.parse_args().source))
