# Regression gate: device results BS4-20261125-33C0CE34 and 7F5AF3CA

Do not treat a successful APK build, source parity audit or first frame as a stable baseline. The emergency dual-core APK (packaging 70df3ee, main core a85d48e) was rejected by the user.

## SotC CUSA08809
- Log proves dispatch to libbachata_sotc_608a1ac.so and embedded revision 608a1ac652ce47e9081cf7b886cd0a382ef7fca4.
- User stopped after ~42s; no FIRST_FRAME_PRESENTED checkpoint. This core predates the frame-event fix, so absence of the frontend event alone does not establish that no Vulkan frame was presented. User reports regression. 100 shader compiles, 23 graphics and 60 compute pipeline compiles, 298 SRT page refresh lines; no fatal exception. Last GPU command log includes 0xfb974c0e and oversized buffer clamp. The previous 125.76s report is not equivalent to a validated stable baseline. Do not issue another APK on the premise that 608a1ac is confirmed good.
- Actual device SM8850 Adreno 840, Turnip profile turnip-8255659cc205110e, readbacksMode 2. Need original FA34AD51/819CF3DB raw logs, cache/config/driver and visual confirmation to compare. Official 0.2.6 is the user's functional reference, not a substitute for verified 0.18.1 source parity.

## Order CUSA00785
- Main core a85d48ec8b63932203d2bf92e213e79081930b36; first frame; backend crash at ~90s. Vulkan queue submission failed with ErrorDeviceLost, vk_scheduler.cpp:246. This is not the former memcpy host fault.
- 506 shader compiles, 412 graphics and 13 compute pipeline compiles, 17 ORDER1886_SRT_UNRESOLVED lines, zero SRT GPU refresh lines, 15 logged image footprint rejects. 29 preloaded pipelines. Do not conflate rate-limited rejection logs with total occurrences.
- Actual rejected T# raw words, in order:
  029d5f29 02300000 007fc1ff 96d90fac 02cea9f7 02300000 007fc1ff 96d90fac
  02d19297 1c600000 0003c00f a53003ac 02ceacac 02300000 007fc1ff 96d90fac
  02a08cb5 02800000 003fc0ff b6d803ac 02cafe62 02600000 00000000 a4d00204
- First descriptor lower four words represent 512x512 and type 9; upper words decode as depth 2552, pitch 5750, array end 4480. Second is 16x16 with pitch 5750. Upper words look like another image descriptor header; cannot decide whether R128 decode, IR resource discovery, SRT offsets, or source data is wrong without original MIMG/IR and source locations. Do not zero upper words, force R128, loosen bounds, or remove image guards on this evidence alone.
- Compare source/IR path against dedicated Order donor and authentic release before selecting a new correction. Prior 504db690 produced a first frame and better measured performance in available samples but still crashed; it is not a stable base.

## Eligibility
Single-core audit 45520100136 passed source parity, not game stability. Candidate bf75109 remains a source comparison reference only. No automatic APK from this branch until a causal correction is reviewed. Do not merge experimental native performance branch or ship a second game-specific binary as a permanent fix. Keep original P36 signature, incremental builds and source verification. Record exact tested core, driver, settings, log checkpoint and user gameplay result for each title before calling a revision stable.
