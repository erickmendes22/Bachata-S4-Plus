#!/usr/bin/env python3
"""Keep SotC PM4 diagnostic age local to the suspended coroutine/loop.

Apply after port_sotc_stall_progress. This changes the observation lifetime,
not the packet predicate, CP progress, callback order or polling backoff.
"""
from pathlib import Path
import re


NOTE = r'''void Liverpool::NoteCommandWait(const char* reason, VAddr address, u64 reference,
                               u64 mask, u64 observed, u32 function, bool& first_poll, u32 qid,
                               CommandWaitEpisode& episode) {
    if (!SotcCommandWaitEnabled()) return;
    if (first_poll) {
        cp_progress = true;
        first_poll = false;
    }
    cp_wait = {reason, address, reference, mask, observed, function, qid, true};
    // BACHATA_SOTC_WAIT_EPISODE: callbacks may advance CP housekeeping without
    // satisfying this predicate. The suspended coroutine owns its diagnostic
    // age; other queues and ResetCommandWaitProgress cannot erase it.
    const auto& old = episode.state;
    const bool same = old.active && std::string_view(old.reason) == reason &&
                      old.qid == qid && old.address == address &&
                      old.reference == reference && old.mask == mask && old.function == function;
    if (!same) {
        episode = {cp_wait, SotcCommandWaitNowNs(), 0, false};
        return;
    }
    // A changing observation which still fails the comparison is not progress.
    episode.state.observed = observed;
    if (episode.reported || (++episode.polls & 31u) != 0) return;
    const u64 elapsed_ns = SotcCommandWaitNowNs() - episode.since_ns;
    if (elapsed_ns < 2'000'000'000ULL) return;
    episode.reported = true;
    cp_wait_reported = true;
    u64 tick = 0, submitted = 0, gpu = 0;
    if (rasterizer) {
        auto& scheduler = rasterizer->GetScheduler();
        tick = scheduler.CurrentTick();
        submitted = scheduler.RecordedSubmitTick();
        gpu = scheduler.GetWorkSemaphore()->KnownGpuTick();
    }
    const auto& wait = episode.state;
    // Only false predicate reentries sample time, once on entry and every 32
    // polls until the single report. Passing predicates and ordinary packets
    // do not call this observer or consult the clock.
    LOG_WARNING(Render_Vulkan,
        "BACHATA_GPU_WAIT phase=cp_predicate reason={} qid={} address={:#x} reference={:#x} "
        "mask={:#x} observed={:#x} function={} commands={} submits={} tick={} submitted={} gpu={} elapsed_ms={}",
        wait.reason, wait.qid, wait.address, wait.reference, wait.mask,
        wait.observed, wait.function, num_commands.load(std::memory_order_relaxed),
        num_submits.load(std::memory_order_relaxed), tick, submitted, gpu,
        elapsed_ns / 1'000'000);
}'''


def block(text, anchor):
    start = text.index(anchor)
    brace = text.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def one(text, old, new, label):
    if text.count(old) != 1:
        raise RuntimeError(f"SotC wait episode anchor drift {label}: {text.count(old)}")
    return text.replace(old, new, 1)


def apply(root: Path):
    root = Path(root)
    directory = root / "src/video_core/amdgpu"
    cpp_path, header_path = directory / "liverpool.cpp", directory / "liverpool.h"
    cpp, header = cpp_path.read_text(), header_path.read_text()
    if "BACHATA_SOTC_WAIT_EPISODE" in cpp:
        if (cpp.count("CommandWaitEpisode wait_episode{};") != 8 or
                "struct CommandWaitEpisode {" not in header):
            raise RuntimeError("Incomplete SotC local wait episode overlay")
        return {"alreadyApplied": True}
    cpp = one(cpp, block(cpp, "void Liverpool::NoteCommandWait("), NOTE, "observer")
    # Backoff continues to use the original CP-wide no-progress timer. Only its
    # diagnostic emission moves to the coroutine-owned predicate episode.
    old_report = block(cpp, "    if (!cp_wait_reported && cp_wait.active && elapsed_ns >=")
    cpp = one(cpp, old_report + "\n", "", "remove CP-wide diagnostic")
    if "#include <string_view>" not in cpp:
        cpp = one(cpp, '#include "common/assert.h"',
                  '#include <string_view>\n\n#include "common/assert.h"', "string_view include")
    cpp, count = re.subn(r"(?m)^([ \t]*)bool first_poll = true;$",
                        r"\1CommandWaitEpisode wait_episode{};\n\1bool first_poll = true;", cpp)
    if count != 8:
        raise RuntimeError(f"Expected 8 coroutine-owned wait loops, found {count}")
    cpp, count = re.subn(r"first_poll, (GfxQueueId|curr_qid)\);",
                        r"first_poll, \1, wait_episode);", cpp)
    if count != 8:
        raise RuntimeError(f"Expected 8 episode observer calls, found {count}")
    header = one(header,
                 "    void NoteCommandWait(const char* reason, VAddr address, u64 reference,\n"
                 "                         u64 mask, u64 observed, u32 function, bool& first_poll, u32 qid);",
                 "    struct CommandWaitEpisode;\n"
                 "    void NoteCommandWait(const char* reason, VAddr address, u64 reference,\n"
                 "                         u64 mask, u64 observed, u32 function, bool& first_poll, u32 qid,\n"
                 "                         CommandWaitEpisode& episode);", "declaration")
    header = one(header, "    } cp_wait;\n    bool cp_progress{};",
                 "    } cp_wait;\n"
                 "    struct CommandWaitEpisode {\n"
                 "        CpWaitState state{};\n"
                 "        u64 since_ns{};\n"
                 "        u32 polls{};\n"
                 "        bool reported{};\n"
                 "    };\n"
                 "    bool cp_progress{};", "owned episode state")
    cpp_path.write_text(cpp)
    header_path.write_text(header)
    return {
        "diagnostic": "one sample per unchanged PM4 predicate episode after 2s and a 32-poll sample",
        "lifetime": "local coroutine scope; completion/new wait cannot reuse a stale episode",
        "preserved": "predicate reads, CP progress, callback FIFO, queue publication and backoff",
        "scope": "SotC diagnostic observation only; no shader/cache/frontend/exporter changes",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    print(apply(parser.parse_args().source))
