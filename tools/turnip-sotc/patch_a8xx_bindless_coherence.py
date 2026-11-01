#!/usr/bin/env python3
"""Port GameHub/WinNative A8xx bindless descriptor invalidation to Mesa V38.

On A8xx, SP_UPDATE_CNTL(... gfx_bindless/cs_bindless=0xff) does not
replace writing the dedicated GFX and CS bindless invalidate registers.
Apply at device setup, 3D blits/clears and descriptor-base rebinding.
Keep a complete draw-state length: a single A8xx invalidate packet is
two dwords, so reserve two extra dwords in the descriptor-set draw state.
Fail closed on source drift; never touch A6xx/A7xx behavior.
"""
from pathlib import Path

def replace_exact(path, before, after, label):
    f=Path(path)
    s=f.read_text()
    n=s.count(before)
    assert n==1, f"{label}: expected 1 anchor, found {n}"
    f.write_text(s.replace(before,after,1))
    print("Applied",label)

CMD="src/freedreno/vulkan/tu_cmd_buffer.cc"
BLIT="src/freedreno/vulkan/tu_clear_blit.cc"

before='''         .gfx_bindless = CHIP == A6XX ? 0x1f : 0xff,));

   tu_cs_emit_wfi(cs);'''
after='''         .gfx_bindless = CHIP == A6XX ? 0x1f : 0xff,));
   // The A8xx descriptor caches have dedicated invalidate registers.
   // This must happen after SP_UPDATE_CNTL and before subsequent commands.
   if (CHIP >= A8XX) {
      tu_cs_emit_regs(cs, A6XX_SP_CS_BINDLESS_INVALIDATE(1));
      tu_cs_emit_regs(cs, A6XX_SP_GFX_BINDLESS_INVALIDATE(1));
   }

   tu_cs_emit_wfi(cs);'''
replace_exact(CMD,before,after,"A8xx bindless invalidate at hardware initialization")

before='''         .gfx_bindless = CHIP == A6XX ? 0x1f : 0xff,));

   with_crb (cs, 2 * 5 + 2 * 12) {'''
after='''         .gfx_bindless = CHIP == A6XX ? 0x1f : 0xff,));
   // Clear / resolve paths also use bindless global shader resources.
   if (CHIP >= A8XX) {
      tu_cs_emit_regs(cs, A6XX_SP_CS_BINDLESS_INVALIDATE(1));
      tu_cs_emit_regs(cs, A6XX_SP_GFX_BINDLESS_INVALIDATE(1));
   }

   with_crb (cs, 2 * 5 + 2 * 12) {'''
replace_exact(BLIT,before,after,"A8xx bindless invalidate in 3D clears/resolves")

before='''                             2 + bindless_pkt_size +
                             (descriptors_state->max_dynamic_offset_size ? 3 : 0));'''
after='''                             2 + bindless_pkt_size + (CHIP >= A8XX ? 2 : 0) +
                             (descriptors_state->max_dynamic_offset_size ? 3 : 0));'''
replace_exact(CMD,before,after,"reserve two extra A8xx descriptor draw-state dwords")

before='''   tu_cs_emit_regs(cs, SP_UPDATE_CNTL(CHIP,
      .cs_bindless = bind_point == VK_PIPELINE_BIND_POINT_COMPUTE ? CHIP == A6XX ? 0x1f : 0xff : 0,
      .gfx_bindless = bind_point == VK_PIPELINE_BIND_POINT_GRAPHICS ? CHIP == A6XX ? 0x1f : 0xff : 0,
   ));'''
after='''   if (CHIP >= A8XX) {
      // Rebinding a descriptor base must invalidate the corresponding A8xx
      // bindless cache, otherwise an earlier image/sampler can be reused.
      if (bind_point == VK_PIPELINE_BIND_POINT_COMPUTE)
         tu_cs_emit_regs(cs, A6XX_SP_CS_BINDLESS_INVALIDATE(1));
      else
         tu_cs_emit_regs(cs, A6XX_SP_GFX_BINDLESS_INVALIDATE(1));
   } else {
      tu_cs_emit_regs(cs, SP_UPDATE_CNTL(CHIP,
         .cs_bindless = bind_point == VK_PIPELINE_BIND_POINT_COMPUTE ? CHIP == A6XX ? 0x1f : 0xff : 0,
         .gfx_bindless = bind_point == VK_PIPELINE_BIND_POINT_GRAPHICS ? CHIP == A6XX ? 0x1f : 0xff : 0,
      ));
   }'''
replace_exact(CMD,before,after,"A8xx dedicated invalidation on descriptor rebinding")
print("A8XX_BINDLESS_COHERENCE_PATCH_COMPLETE")
