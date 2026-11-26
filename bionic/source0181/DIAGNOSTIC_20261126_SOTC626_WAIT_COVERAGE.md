# SotC 626236DC: retention and predicate-wait coverage

## Evidence and limits

Diagnostic `BS4-20261126-626236DC` came from package
`a8f02cd6702f733ee065d990b942e1bd72f40a4b`. The native log identifies the SotC
core as `3938820401a1a5971b3f96aac7c0e01d6037568c`; the generic frontend runtime
revision is not used as the native identity.

The process ran for 31.709 seconds. Its first presentation was at 18.239 seconds;
the application reported 51.87 FPS in the next 2.014-second window. This proves
initial presentation progress, not sustained gameplay. The user then reported a
freeze and stopped the process. The native log has no per-line timestamps, so
its last activity cannot be assigned an exact wall-clock freeze time.

The retained native log has 11,591 lines. All 83 compute and 100 graphics PSO
begin records have matching ends; no runtime shader compilation or
`BACHATA_GPU_WAIT` remains unmatched/recorded. Last visible records are:

| Thread | Line | Record |
|---|---:|---|
| Present | 2476 | First game presentation, reported once by design |
| CP | 5369 | One-time SET_PREDICATION warning |
| Draw | 5593 | EnsureResident for blocks 612414..612415 |
| Game main | 6303 | System gesture stub call |
| Guest workers | 11581–11589 | Virtual reservation/direct-memory mapping |

These records are not stack samples. In particular, EnsureResident's last log
does not prove that allocation failed or that the Draw thread remained there.

## The truncation flag does not prove discarded content

The actual package's original `classes2.dex` has SHA-256
`f14d4a6d178d1e5f29a0c33d06f1169bd79674c50a812032ac6a79f345eca3df`.
Its `DiagnosticBundleBuilder.DEFAULT_MAX_LOG_BYTES` is 4,194,304. The real
`DiagnosticRedactor.redactStream` bytecode retains a 25% head and 75% tail.

The false-positive flag is visible in the real methods:

- `redactStream$appendHead` switches away from the head when its next complete
  redacted line would exceed the 1 MiB head budget.
- `redactStream`, instruction offset `0x0082`, immediately sets the returned
  `truncated` flag before sending that line to `redactStream$pushTail`.
- `pushTail` removes a line only while its deque exceeds the separate 3 MiB
  tail budget. Merely switching from head to tail need not remove anything.
- The head/tail separator is written whenever that flag is set and a tail
  exists, even when no tail eviction occurred.

The supplied file has a 1,048,456-byte head, the 49-byte separator, and a
715,702-byte tail, totaling 1,764,207 bytes. Replaying the observed bytecode
algorithm over the file with that separator removed produces the **identical
exported bytes**, `truncated=true`, and **zero removed lines**. This is a replay
of the retention algorithm, not execution of the Android DEX. The boundary also
continues one reservation: base `0x3edf00000` followed by its direct mapping at
`0x3ee1a0000`.

Thus the manifest flag alone cannot explain the missing wait marker. The
exported file does not supply the original source-file length, so this review
does not assert an absolute proof that no earlier producer discarded content.
The exporter was inspected, not modified. DEX extracts and the replay summary
are retained under `analysis/626236DC-retention` in the investigation workspace.

## Why housekeeping can hide the original CP marker

`ProcessCommands` marks `cp_progress` after every callback. `Process` then calls
`ResetCommandWaitProgress`, resetting the two-second no-progress timer. This is
correct for functional CP backoff, but does not prove that a particular PM4
predicate became true.

There are 380 `sceKernelMunmap` calls after the final visible Draw record.
In this core, `IsValidGpuMapping` accepts these sub-40-bit addresses. SotC unmap
calls `DropGpuModified`, which uses `SendCommand<true>` while the guest holds
the memory manager's `unmap_mutex`. Following operations on those same guest
workers demonstrate serviced CP callbacks after the last visible Draw log.
This rules out treating that last Draw record as the instant of a permanent
CP/Draw deadlock. Native timestamps are absent, so it does not establish that
callbacks continued until the final user stop.

The log does not identify the pending PM4 predicate. Housekeeping repeatedly
resetting its diagnostic age is a reproduced observability defect, not proof
that a particular WAIT_REG_MEM caused this freeze.

## Blocking-path coverage and donor comparison

Paths refer to the final generated source under `src/video_core`.

| Path | Existing observation | Progress producer / finding |
|---|---|---|
| `amdgpu/liverpool.cpp`: false PM4/CE predicate | `cp_predicate`, formerly after two seconds without any CP progress | Same comparisons and cooperative polling as before; unrelated callbacks could reset observation. Corrected below. |
| `DrainDrawQueue` / queue capacity | `cp_draw_drain` / `cp_draw_capacity` after two seconds | Draw worker advances tail outside execution of the queued operation. No such marker is present. Its absence alone does not prove the queue was empty. |
| `renderer_vulkan/vk_scheduler.cpp`: `WaitSubmitted` | No timed marker | Recorder publishes `recorded_submit_tick` only after queue submission returns. Donor uses the same atomic wait after a short spin; this wait precedes the instrumented Vulkan timeline wait. |
| `buffer_cache.cpp`: sparse binds | No marker for the submission wait or queue lock | Bachata waits for `CurrentTick()-2` before taking the queue mutex. This is the **previous** submission because SubmitExecution already advanced the tick. No self-wait or lock inversion was established; do not remove the ordering requirement. |
| `vk_recorder.cpp`: `AcquireChunk` | No timed marker | Producer kicks/yields at the in-flight limit; the independent consumer recycles chunks. Donor uses the same mechanism. The free-list lock is not held while executing a Vulkan command. |
| `vk_recorder.cpp`: `Sync` | No timed marker | Actual callers are Scheduler/Presenter destruction. It is not an active gameplay path in this generated tree. |
| `vk_semaphore.cpp`: `Semaphore::Wait` | `phase=timeline` after two seconds | Does not cover waiting for the recorder to submit, queue mutex acquisition, or a blocked driver call before reaching this method. |
| `vk_presenter.cpp`: free-frame CV and present fence | No timed marker | Present thread returns a frame and GPU signals its fence. Donor has the same free-frame/fence dependency. Waiting inside flip preparation blocks that CP callback before predicate backoff. |
| `vk_swapchain.cpp`: acquire retirement / image acquisition | No timed marker | Platform/GPU producer; native WSI was active in this capture. These waits precede returning a free frame. No observed surface error or proven WSI cycle identifies them as the cause. |

The VMAs' exclusive lock is acquired after early GPU unmap. Region tracking
does not retain its region mutex across the synchronous readback callback.
Those existing two-phase boundaries break the previously investigated simple
VMA/CP and region/CP inversions. No new blocking cycle was demonstrated here.

## Narrow correction: lifetime of the observed predicate

`port_sotc_wait_episode.py`, applied after `port_sotc_stall_progress`, gives each
of the eight CE/GFX/ASC wait loops its own coroutine-local
`CommandWaitEpisode`. Its identity is reason, queue, address, reference, mask
and function. Changes in the observed value which still fail the comparison
do not reset it. A changed identity starts a new episode. Passing the real
predicate exits the scope; another wait, even at the same address, gets fresh
state. There is no global pointer into a coroutine or shared episode between
queues.

The observer reads the clock at the first false predicate and every 32 false
reentries until its one report after two seconds. It does not read the clock
for ordinary packets or passing predicates. The functional `cp_progress`,
reset, callback FIFO, wait comparisons, scheduling and backoff remain unchanged.
The report still uses the actual observed value and published atomic ticks.

This capture correction is necessary to distinguish a prolonged PM4 predicate
from the synchronous paths above if the independent LOD/streaming correction
does not resolve the freeze. It is not presented as a gameplay fix by itself.
It does not instrument arbitrary draw calls, alter the exporter or change any
timeout into successful completion.

## Validation

`test_sotc_wait_episode.py --source <effective-tree>` extracts the real CP,
command dispatcher, predicate and coroutine methods. Clock, IRQ and GPU/VO
boundaries are mocks. Each SotC serial executes 73 callbacks across the same
key's long/short/long waits; the real dispatcher resets functional backoff on
every callback, but the two long predicate episodes each report once. The
short completed wait does not inherit the prior episode.

Additional checks cover all six identity fields, changing false observations,
independent queues, exact clock-read counts and other-title opt-out. Six
compiled negative controls are rejected: callback-reset age, ignored identity,
observed-value reset, static/reused episode lifetime, per-poll clock, and
duplicate reports. The existing CP graph fixture is adapted to the new
coroutine diagnostic lifetime while retaining its functional backoff tests.

No gameplay, new FPS gain, absence of every stall, or equivalence with the port
is inferred from this host test or from marker presence in an ELF.
