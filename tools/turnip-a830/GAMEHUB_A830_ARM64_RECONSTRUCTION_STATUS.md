# GameHub A830: reverse-engineered original ARM64 ABI (2026-11-02)

Original user GameHub `libvulkan_freedreno.so` is 14,257,760 bytes, SHA256 `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`.

The analysis extracted 118 named GPUProps from the original `strcmp -> branch -> property-load` sequence, and 22 driconf fields from `string -> parse -> strb` code. Independently extracted 116 named GPUProps from the pinned V38 compiled ARM64. Exactly 100 properties match by name, and **only `prim_alloc_threshold` differs** between the two analyzed A830 profile tables: GameHub 15 / V38 baseline 7. The parent branch already integrates 15.

See `tools/turnip-a830/gamehub_driconf_22_verified.hpp` for the corrected `tu_sync_renderpass_cache` byte at **0x4C** (NOT 0x4B). This accessor alone does not implement a GPU cache barrier.

See `tools/turnip-a830/gamehub_indexed_draw_init_verified.hpp` for original AArch64 branch 0x99bdbc..0x99be14. It selects 0x600 or 0x1800 only when the A830 index-quirk and other runtime bytes meet the conditions. The other runtime byte at +0x326 has **not** been proved equivalent to `tu_split_indexed_draws` at driconf +0x4E. Do not wire them together.

**Already equivalent** between original and V38: R8G8 fast-clear workaround (the V38 name is `QCTDD12766770_r8g8_fc_alignment`), UBWC coherence, LRZ feedback, Z24S8 capability, and 100 named GPU properties except the documented primitive threshold. Do not add duplicate or contradictory patches.

No new driver binary is claimed to solve ghosts, flicker or texture omissions without an on-device Vulkan capture. The original SotC log also explicitly says async pipeline draws may be skipped and shows a texture `InvalidFileFourCC`; those guest-side problems cannot be repaired solely by a host Vulkan .so.

The complete original proprietary C++ cannot be recovered exactly from an optimized, stripped ELF. The project produces verified functional reconstructions for the code paths identified, not the original source tree. The separate C++ test bundle contains 9 tests, 20 opcode checks, the extracted 118/22 maps and a reproducible ELF-to-map tool.
