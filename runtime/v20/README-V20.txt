GOW3 V20 FULL PREDICATION
=========================

Target:
  Bachata S4+ ARM64/FEX shadPS4 core

Upstream implementation:
  shadps4-emu/shadPS4 commit 3559530df5aec4067a95912af13ef14896b65ada
  "video_core: Implement IT_SET_PREDICATION using VK_EXT_conditional_rendering"

This V20 intentionally requires the real source implementation. The workflow aborts if:
  - vk_predication.cpp/.h are missing
  - occlusion_predicate.comp is missing
  - beginConditionalRenderingEXT is missing
  - copyQueryPoolResults is missing
  - an occlusion VkQueryPool is missing
  - Liverpool still contains the old generic Unimplemented IT_SET_PREDICATION warning

Expected CI artifact:
  shadps4-arm64-fex

That binary is then inserted into the known-installable V14A3 APK runtime and signed with P36.

