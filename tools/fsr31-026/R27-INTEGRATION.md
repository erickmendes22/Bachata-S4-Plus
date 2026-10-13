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

Verified checkpoint: run 38463663035 completed the native same-LDR boundary
handoff into explicitly prepared 720p UI targets: camera warmup used the copy
fallback, followed by seven real AMD FSR dispatches. Every readback preserved
916600 blue scene pixels and 5000 red HUD pixels with zero Vulkan validation
errors. This is a synthetic software-Vulkan test, not gameplay on Adreno.

The next checkpoint adds native Pipeline::BindResources shader identity (without
debug-utils names), copied Scheduler::BeginRendering handoffs, automatic 720p
color/depth allocation, and cached viewport/scissor/120-byte push-state restoration.
CPU tests cover 100 consecutive UI/non-UI restores. Native ARM64 emulation covers
four pipeline-entry ABI cases and six original shader-identity cases.

Automatic UI routing is scoped to the source image and command buffer. Later
rendering instances and sampled views follow the owned UI target; sampled aliases
preserve format and component mapping. Source transitions are mirrored to the UI
image, and resource lifetimes follow native source image/view destruction. The GPU
test additionally reopens the original attachment with LOAD and checks alias identity.
The first automatic-target CI stopped on an invalid field in the test, after both
SDK builds and the three motion/depth GPU cases passed. The field is corrected in
c65ec621172e02a955d4f14030d59a1599833118; automatic-target execution is still pending.

Remaining release requirements: successful automatic-target GPU test; complete
native stencil-only/depth-state parity; verify presentation samples the composed
image in real gameplay; integrate the Android controls/resolution patches and
Bionic loader into the exact R27 APK; validate final packaging and signing.
Camera motion is implemented; full object-motion/reactive-mask parity is not
established. Do not represent the synthetic tests as gameplay stability evidence.

R27 Elden024 routing, core023 removal, patches and native controls are mandatory
packaging invariants. No APK is generated at this checkpoint. No new emulator
core is built. Do not revive speculative render-pass interruption or global
image substitution.
