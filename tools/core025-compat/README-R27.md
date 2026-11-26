# R27: Elden Ring on retained core024, remove core023

The R26 Elden diagnostic 42976864 reports corruption and freezes on native025.
This release changes dispatch, not the native renderer. No claim is made that
an underlying core025 renderer fault is fixed or that device gameplay is validated.

CUSA18723, CUSA28527 and CUSA28863 select the byte-identical retained core024.
The dispatcher also checks a bounded, typed TITLE_ID in param.sfo under
--override-root for custom directory names. Invalid SFOs fall through to 025.
The native023 file and manifest entry are removed; its numeric and Black Ops
heuristic routing are removed. Former 023 games use 025. Driveclub's existing
020 route and loader preload are retained. Native025, its RB/compatibility
hooks, all patch catalogs, DEX and other runtime entries are byte-identical to
R26. Elden 720p/60 FPS options are preserved, including user selection semantics.

Runtime identity is bachata-s4-n027-0.2.6-r, with the original extraction suffix
and length, avoiding stale n026 reuse and collisions with other FSR branches.

88 ARM64 cases execute the entire dispatcher through execve at two PIE biases,
modeling Linux file syscalls and checking exact argv/environment preservation,
three Elden regional IDs, old 023 destinations, custom roots, malformed/wrong
SFO types, neighboring IDs, and Driveclub's original absolute-path SFO route.
No GPU operation is modeled as a successful device gameplay test.
Packaging checks all runtime manifest hashes, all preserved entry bytes and ZIP
CRC. The APK is signed and verified with P36 V2/V3 for SDK24-36.

Reproduce with package_r27.py BASE_R26.apk WORK, then the existing
SignAndVerify.java signer with locally held P36 credentials.
