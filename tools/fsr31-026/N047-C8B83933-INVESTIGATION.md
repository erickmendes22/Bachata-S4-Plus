# C8B83933: selected image provenance and the missing post-HUD boundary

The n046 device report records five GPU_FRAME_PROBE events (dispatch 0,1,2,3,256). In all five, native R and G means are 1.000, while B is 0.408–0.516. Clone means match within rounding; reconstructed and pre-HUD composition means remain near those values. All five report cyan=0 and invalid=0. The screenshot is cyan/white. These are bounded sampled grids, not a synchronized dump of the displayed screenshot. The report does not establish the causal writer or the stage producing the visible cyan. It does establish that saturation is present in these sampled native input images before the AMD dispatch. Termination is CANCELLED_BY_USER; the generic BACKEND_CRASHED field is not proof of a crash.

## Selection mismatch with the Port

Pinned Port RunScaled is selected by OnDraw only when the current UI color ImageId equals ldr_target (plus camera readiness and non-display UI classification). OnColorTarget alone checks RGBA8 format and depth allocation size; that test alone is not sufficient scene identity. The shipped SDK first_pre_ui_color accepts a submitted reduced color target and composes it into a distinct full-size movie/HUD attachment. Successful submission plus matching dimensions is not equivalent to the Port's same-target rule. This is a confirmed structural difference, not a confirmed causal identification of C8B83933's cyan frame.

## Investigation changes

* Track the last executed graphics draw per color view, including frame/CB, VS and FS hashes, area, viewport, MRT count and bounded sampled image views. Collect outside injected work, clear on view destruction, and log at most 32 selected sources. Descriptor images are removed when a binding becomes a buffer, descriptor copies invalidate knowledge, and pushed descriptors supersede bound sets. Fragment names use the renderer's `fs_0x` convention (with `ps_0x` compatibility). This records provenance, not a proof that a shader is tone mapping.
* Record a seventh GPU sample after the actual full-size HUD rendering instance ends, retaining the original pre-HUD sample. It uses the already owned temporal slot and its real submission completion fence. No scheduler insertion, scene recoloring, per-frame device wait, core rebuild or new UI redirection is introduced.
* Bounded reporting now recognizes persistent R/G saturation as well as cyan/nonfinite values, throttling saturation reports to one in sixteen so initial events do not consume the entire report allowance.
* GPU CI requires the real cross-CB Vulkan hook path to show all seven stages and the known HUD's 64 red sampled pixels after rendering. That verifies the post-HUD hook rather than calling its function directly.
* CPU tests exercise actual draw forwarding, distinct vertex/fragment identity, sampled descriptor provenance, buffer replacement invalidation and view lifetime cleanup; existing jitter and UI-scale tests remain required.

## Interpretation limits

If native samples are saturated while the selected writer or dependency is an intermediate, repair producer selection/dataflow. If post-HUD becomes cyan while pre-HUD does not, investigate the original HUD/movie passes. If neither is cyan in the actual affected frame, trace the subsequent display copy/Presenter. Do not invert R/B, disable FP16, change gamma, clamp color or label an intermediate as final based on the screenshot alone. Camera-only motion, masks and full production owned-UI wiring remain separate integration gaps. These changes close evidence gaps; they do not claim the device cyan is repaired.
