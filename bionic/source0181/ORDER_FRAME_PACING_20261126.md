# The Order 01.02: verified 60-FPS patch and presentation pacing

## Evidence and scope

The user tested package `64450bf5187edc68532c9b577f8be1b7069b6d00` on a
nubia NX809J, Android 16, Adreno 840. Diagnostic `D375882C` identifies native
Order revision `dbc91188b0058e67bcc5c9750dc202251e33e431`, CUSA00785 01.02.
The native log reports applying `60 FPS Unlock` at `0x8004507c4`, value `01`.
The application trace initially reports approximately 59–60 FPS, then long
intervals around 30 and later lower values. This establishes that the patch
was applied; it does not prove the engine's requested interval never changes
later or that the GPU can sustain 60 FPS in every scene.

The exact donor 60-FPS recipe changes the immediate in the instruction at
RVA `0x4507be` from `c7 05 8c 05 17 01 02 00 00 00` to
`c7 05 8c 05 17 01 01 00 00 00`. Its target is the sync-interval global at
RVA `0x15c0d54`. Other engine writes to this global exist; they are not all
part of the donor's 60-FPS recipe. This change does not turn the 60-FPS patch
into a different unlocked-rate recipe or override explicit guest flip rates.

The active donor's `VideoOutDriver::PresentThread` uses an independent
60-FPS presentation deadline and a condition variable notified by incoming
requests. The previous Bachata implementation consumes only on a 60-Hz
vblank tick. In the extracted real-method reproduction, this quantizes
17–33 ms frame production to 30 FPS.

Donor provenance: PC `c53cd01d032995fe622033623ab64b4cf6b02233`, Android
`756a4f0cc603b02971d45b36354143249a4fe492`. This is a source adaptation to
the retained ARM64 Bionic + FEX core, not a donor binary/runtime transplant.

## Runtime changes

`order_frame_pacing.h` enables the separate presentation deadline only for
Android, CUSA00785, version 01.02, and an exact match of all ten patched
instruction bytes. `RefreshOrderFramePacing` runs after pending patches in
both managed and legacy launch paths and after an immediately applied patch.
The probe validates image bounds, addition overflow, the mapped guest span,
and reads the existing physical backing alias. It does not dereference a
protected guest virtual address. A failed probe leaves the old cadence active.

The incoming FIFO request now wakes presentation between vblanks. The guest
vblank frequency and event publication remain in their original path. The
new path remains capped at 60 FPS; a nonzero `sceVideoOutSetFlipRate` request
retains the guest's cadence. Patch/profile/rate transitions are checked at
the boundary and after an intervening sleep. No additional game bytes are
changed and `Flip`, including its actual-present frame counter, is retained.

The presentation loop stops consuming at the current tick deadline, even
when a queued request makes `wait_until` return immediately. This avoids
starving vblank updates if `Flip` itself is expensive and the queue has a
backlog. Thread shutdown requests stop, notifies the wait and joins before
the queue, ports and condition variable are destroyed. `flip_rate` is atomic
because the guest setter and presentation thread access it concurrently.

Two bounded diagnostics separate the questions in the user's report:

- `BACHATA_ORDER_FRAME_PACING`: whether the real instruction was readable and
  matched, the game version and the selected presentation limit.
- `BACHATA_ORDER_FLIP_RATE`: the first guest request and changes to its rate,
  along with patch verification, vblank frequency and presentation limit.

These records can distinguish a failed patch/probe, an explicit 30-FPS guest
request, and frame production that remains below the enabled 60-FPS limit.
They do not measure GPU utilization or continuously inspect the engine global.

## Verification

`test_order_frame_pacing.py --source <effective-tree>` compiles the actual
`PresentThread`, request producer, guest rate setter, patch refresh, pending
patch drain and destructor with C++23 and UBSan. Clock/driver/GPU boundaries
are controlled by the fixture; it is not an Android gameplay benchmark.

The real-method cases cover 4, 16, 17, 20, 25 and 40 ms producers; FIFO order;
the 60-Hz guest clock; the 60-FPS limit; explicit 30-FPS requests; another
title; a wrong game version; unapplied patch bytes; profile/rate transitions;
and expensive presentation with an already queued backlog. At 17, 20 and
25 ms, the controlled reproduction changes from 30 FPS to approximately
58.82, 50 and 40 FPS respectively. These are model results, not claimed device
FPS improvements.

The patch probe checks all ten bytes independently, title/version/platform,
VMA validation, image/overflow limits, failed reads and post-patch ordering.
One hundred actual-thread shutdowns verify stop/wake/join before destruction.
Negative controls reject the old vblank-only path, missing notification,
missing cap, ignored guest cadence, a changed vblank clock, backlog starvation,
unsafe guest-span probing, probing before patches, premature queue destruction
and shutdown without notification.

Compilation and these checks establish the implementation contracts. A fresh
capture with this native revision is still required to measure the device's
scene-specific performance and determine whether an engine-requested interval
or remaining CPU/GPU work limits gameplay below 60 FPS.
