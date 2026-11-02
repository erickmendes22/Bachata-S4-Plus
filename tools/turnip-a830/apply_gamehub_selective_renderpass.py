#!/usr/bin/env python3
"""Recover GameHub A8xx renderpass decision paths into pinned Mesa V38 source.

Original GameHub / Rutabaga ELF:
SHA256 1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
AArch64 0x96539c..0x9658bc; per-GPU A830 flags at 0x8946e4+0x30a,b = 1,1.

This is functional reconstruction, NOT original uncompiled C++ source.
Preserves TU_DEBUG=gmEM/sysmem, existing resource hazards, tessellation,
autotuning and all safety paths. No unconditional A830 SYSMEM.
"""
from pathlib import Path
import sys

SOURCE=Path("src/freedreno/vulkan/tu_cmd_buffer.cc")
PREFIX = r'''
// Exact ELF policy translated to Mesa V38 types, not copied source:
// GameHub ARM64 0x96539c..0x9658bc, GPU A830 info 0x8946e4.
// A830, A830v1 and KGSL 0x44050001 have the two relevant quirks set to 1.
// Don't call these from the desktop/FEX launcher: driver renderpass only.
static bool
tu_gamehub_a8xx_msaa8_needs_sysmem(struct tu_cmd_buffer *cmd)
{
   if (cmd->device->physical_device->info->chip < A8XX)
      return false;
   const tu_render_pass *pass = cmd->state.pass;
   if (!pass || !pass->attachments)
      return false;
   for (uint32_t i = 0; i < pass->attachment_count; ++i) {
      const auto &att = pass->attachments[i];
      if (att.samples != VK_SAMPLE_COUNT_8_BIT)
         continue;
      const VkImageAspectFlags aspects = vk_format_aspects(att.format);
      if ((aspects & (VK_IMAGE_ASPECT_DEPTH_BIT | VK_IMAGE_ASPECT_STENCIL_BIT)) ||
          (aspects == VK_IMAGE_ASPECT_COLOR_BIT && !vk_format_is_int(att.format)))
         return true;
   }
   return false;
}

static bool
tu_gamehub_a8xx_multipass_msaa_needs_sysmem(struct tu_cmd_buffer *cmd)
{
   if (cmd->device->physical_device->info->chip < A8XX)
      return false;
   const tu_render_pass *pass = cmd->state.pass;
   if (!pass || pass->subpass_count < 2 || !pass->attachments)
      return false;
   bool any_msaa = false;
   for (uint32_t i = 0; i < pass->attachment_count; ++i)
      any_msaa |= pass->attachments[i].samples > VK_SAMPLE_COUNT_1_BIT;
   if (!any_msaa)
      return false;
   for (uint32_t i = 0; i < pass->subpass_count; ++i)
      if (pass->subpasses[i].input_count != 0)
         return false;
   return true;
}

static bool
tu_gamehub_a8xx_d32s8_msaa_input_prefers_gmem(struct tu_cmd_buffer *cmd)
{
   if (cmd->device->physical_device->info->chip < A8XX)
      return false;
   const tu_render_pass *pass = cmd->state.pass;
   if (!pass || !pass->attachments)
      return false;
   bool any_input = false;
   for (uint32_t i = 0; i < pass->subpass_count; ++i)
      any_input |= pass->subpasses[i].input_count != 0;
   if (!any_input)
      return false;
   for (uint32_t i = 0; i < pass->attachment_count; ++i) {
      const auto &att = pass->attachments[i];
      if (att.format == VK_FORMAT_D32_SFLOAT_S8_UINT &&
          att.samples > VK_SAMPLE_COUNT_1_BIT)
         return true;
   }
   return false;
}

'''
EARLY = r'''
   // A830-specific quirk fields are true in the original GameHub ELF.
   // First force SYSMEM for unsupported 8x attachments; then for
   // multisampled multi-subpass passes WITHOUT input attachments.
   // Do not force SYSMEM for the entire device.
   if (tu_gamehub_a8xx_msaa8_needs_sysmem(cmd)) {
      cmd->state.rp.force_render_mode_reason =
         "8x MSAA attachment format requires sysmem on A8xx";
      return true;
   }
   if (tu_gamehub_a8xx_multipass_msaa_needs_sysmem(cmd)) {
      cmd->state.rp.force_render_mode_reason =
         "multi-subpass MSAA without input attachments requires sysmem";
      return true;
   }
'''
LATE = r'''
   // The original GameHub 0x96577c..0x9658a4 makes this choice AFTER all
   // safety restrictions (tessellation, XFB, query, too many tiles) and
   // BEFORE the Mesa autotuner. Never override the earlier SYSMEM requirements.
   if (tu_gamehub_a8xx_d32s8_msaa_input_prefers_gmem(cmd))
      return false;

'''
def main():
    file=SOURCE if len(sys.argv)==1 else Path(sys.argv[1])
    s=file.read_text()
    if 'tu_gamehub_a8xx_msaa8_needs_sysmem' in s:
        raise RuntimeError('Patch already applied, refusing duplication')
    if s.count('#include "vk_util.h"')!=1:
        raise RuntimeError('Mesa source no longer matches V38 includes')
    s=s.replace('#include "vk_util.h"', '#include "vk_util.h"\n#include "vk_format.h"',1)
    begin=s.find('static bool\nuse_sysmem_rendering(')
    end=s.find('/* Optimization: there is no reason to load gmem',begin)
    if begin<0 or end<0 or begin>end:
        raise RuntimeError('Could not find pinned use_sysmem_rendering()')
    region=s[begin:end]
    if 'A830 GMEM page-write workaround' in region:
        raise RuntimeError('Do not stack unconditional SYSMEM build with GameHub selective policy')
    first='''   if (TU_DEBUG(SYSMEM)) {
      cmd->state.rp.force_render_mode_reason = "TU_DEBUG(SYSMEM)";
      return true;
   }
'''
    last='''   tu_autotune::render_mode optimal_mode =
      cmd->device->autotune->get_optimal_mode(cmd, rp_ctx, rp_key);
'''
    for label,needle in [('early',first),('late',last)]:
        if region.count(needle)!=1:
            raise RuntimeError(f'Pinned {label} decision location changed')
    for needle in ('cmd->state.rp.has_tess','cmd->state.rp.disable_gmem',
                   'cmd->state.rp.xfb_used','TU_DEBUG(GMEM)',
                   'cmd->device->autotune->get_optimal_mode'):
        if needle not in region:raise RuntimeError('Lost safety check: '+needle)
    region=region.replace(first,first+EARLY,1).replace(last,LATE+last,1)
    s=s[:begin]+PREFIX+region+s[end:]
    for name in ('tu_gamehub_a8xx_msaa8_needs_sysmem',
                 'tu_gamehub_a8xx_multipass_msaa_needs_sysmem',
                 'tu_gamehub_a8xx_d32s8_msaa_input_prefers_gmem'):
        if s.count(name)!=2:raise RuntimeError('Failed patch integrity '+name)
    file.write_text(s)
    print('PASS: selective GameHub A8xx renderpass policy integrated; no forced global sysmem')
if __name__=='__main__':main()
