# Common FIOS completion ABI and inFAMOUS boot investigation

## Device evidence

`bachata-diagnostic-BS4-20261126-80C69C93.zip`, SHA-256
`6cb79be17d70ac96ee4c54b8c240d0040dd5df399becf36e9c761480412fc540`,
records **CUSA00004, inFAMOUS Second Son 01.00**, on nubia NX809J / SM8850,
Android 16. The actual native marker is
`ea720e1acac752be1e9bdfeaf1e097b1c509f174`; the report's inherited frontend
`runtimeRevision=50c8b90...` is not the revision of the executing ELF.

The session runs from 13:33:26.968446Z to 13:33:35.163291Z, approximately
8.195 seconds, and ends at the user's request with exit code 0. No first frame
is recorded. This is evidence of the reported boot failure, not a recorded crash
or proof that every thread was deadlocked for the entire interval.

The last main-thread operations register VideoOut buffers, create an ASC queue,
open `/app0/art/cache/all_shaders.xpps` successfully through the SAF direct-FD
backend (636,272 bytes), and invoke callback `0x8001c3260` with context
`0x2009b3410`, op 1, old `err=0`, old `result=0`. The subsequent FHOpen log proves
the callback returns. No later FIOS read or first frame appears in this capture.
The trophy thread also records a missing communication ID; the capture does not
establish that this is the main-thread blocker.

## Verified ABI defect

The previous HLE typedef and both invocation paths used:

`void callback(context, op, int error, int64 transfer_count)`.

Public interface declarations independently identify the ABI as:

`int callback(context, op, uint8 event, int error)`.

Sources, pinned to the revisions inspected:

- [GPCS4 PS4 FIOS types](https://github.com/Inori/GPCS4/blob/88480de36f983c66f7dd2c5951fead1a740d47a5/GPCS4/SceModules/SceFios2/sce_fios2_types.h): callback signature and 64-bit attribute layout.
- [VitaDB Downloader FIOS declarations](https://github.com/Rinnegatamante/VitaDB-Downloader/blob/5027e5dab3d737e26b69f9c4865f5ce2499d9de0/source/fios.h): independently used callback signature.
- [FIOS2 public header for NMS](https://github.com/sonny-tel/libSceFios2/blob/5d44f9e7a80ae00557af80fad335e4c74ef35d22/sceFios2.h): completion event 1, delete event 2, start event 3. This is a PC header for the same library, not a PS4 execution test.
- [AnyPS5 FIOS types](https://github.com/boykopovar/AnyPS5/blob/dca02060737acad8de4889f7aa857386b9400172/core/libs/prx/libSceFios2/include/Types.hpp): same signature and COMPLETE=1, an additional independent implementation reference.

The previous success call therefore sent **event 0**, and a successful read
sent its byte count as the callback's error. A consumer waiting for event 1
would ignore the successful open, exactly at the phase where this log stops.
This is a concrete emulator defect and a strong candidate for this boot failure;
the game's callback body and a corrected Android execution have not been observed.

## Changes and scope

`port_fios_callback_abi.py` corrects the typed native invocation and the existing
FEX bridge to send `(context, op, COMPLETE=1, error)`. Byte counts remain 64-bit
values returned by `OpGetActualCount`. Results are published before the callback,
and the callback executes outside the operation mutex. Callback/context pointers
are copied before entering guest code, so reentrant queries, nested submissions,
operation deletion and attribute release do not access a borrowed attribute later.

The shared helper now also completes the existing asynchronous positioned write,
archive size/mount/unmount, directory create/open, file delete and stat wrappers,
which previously omitted their callback. Archive size returns an operation handle;
its 64-bit byte result is queried through the operation. Synchronous unmount keeps
its status return, while asynchronous unmount returns a completed operation.
Negative positioned-write sizes/offsets are rejected before conversion to unsigned
kernel arguments, and the existing fallback's seek failure reaches the callback.

There is no title allowlist. The group applies to both cores and to all titles
using this HLE. It retains SAF, mount aliases, synchronous backend execution,
negative submission errors and execution of original PS4 callback code through
FEX. No replacement guest code, AOT runtime, forced success or event-flag bypass
is introduced. Other pre-existing FIOS limitations, such as directory enumeration
stubs, operation-delete event delivery and true asynchronous scheduling, are not
claimed to be implemented by this change.

`BACHATA_FIOS_COMPLETION` logs the actual event, operation, error and byte count.
The next capture can distinguish successful notification from the old event-0
call and show which subsequent boot operation is reached.

## Validation

`test_fios_callback_abi.py` compiles the actual generated HLE helpers and 21+
entrypoints, plus the real `guest_callback.h` argument encoder. Only file/backend
and Linker execution boundaries are replaced. The native run covers 28 scenarios;
the FEX-enabled run covers 56 scenarios, including 28 calls through the real
argument-packing bridge. It checks event/error slots, errors, actual read bytes,
counts above 32 bits, nested callbacks, result visibility, operation deletion,
attribute release and every newly completed wrapper. A callback also unmaps its
path while the logging boundary really consumes strings. FHOpen formats its
borrowed path before notification; the restored post-callback log faults in a
negative control, proving that this lifetime boundary is exercised.

Sixteen executable negative controls fail when reintroducing event 0, the old
native/FEX argument order, count truncation, lost errors, unpublished results,
callbacks under the operation mutex, or omitted completions. The lock control
times out as expected; controls must compile before a runtime failure counts.

The gate is registered in both native workflow source-validation stages and the
API audit requires the corrected callback markers on the fully generated source.
Android native compilation, package signing and final ELF verification remain
separate delivery gates. These host contracts do not establish successful game
boot, GPU correctness or gameplay performance on the user's device.
