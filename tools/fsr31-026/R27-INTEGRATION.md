# Existing R27 core025 integration — work in progress, no APK release

Base APK SHA256: 400b160cd689e5d8872b12746266c4e1bda8196036c28d752bb51319ced72978.
Native025 input SHA256: 373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59.
No native emulator is compiled. hook_fsr_existing025.py patches one verified
Presenter BL into the existing binary. Every R27 compatibility/RB byte outside
the hook/cave is retained. The SDK is compiled separately; test harnesses have
SDK-specific names and cannot be confused with native emulator executables.

Fixed: runtime-name validation accepts n027/n028 identities, device-proc hooks
check the executable owner (024/020 remain unwrapped), recursive wrapper entry
points are not saved as their own originals, and the SDK attaches to a queue
actually requested by the core with synchronization2 explicitly enabled.
The GPU test now requires automatic interception/attachment, not a fake native
FsrPass pointer. ARM64 native callback ABI tests pass with absent/declined/active
SDK at zero and Android-like PIE bases, preserving original arguments and SIMD
arguments on fallback. These do not establish GPU/device gameplay correctness.

Unresolved: Port OnDraw selects UI on ldr_target == color and redirects every
UI color/depth attachment and later sampled display image. The imported SDK
expects a different larger UI attachment. The supplied A03FA2DB log reports
camera and LDR candidates but no temporal dispatch. Existing separate-image
GPU tests do not cover the Port shared-target case. A correct native boundary
handoff and positive shared-target composition test are required before release.
Do not revive speculative render-pass interruption or global image substitution.

R27 Elden024 routing, core023 removal, patches and native controls are mandatory
packaging invariants. No APK is generated at this checkpoint.
