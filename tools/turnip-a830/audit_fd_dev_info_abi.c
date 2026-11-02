#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include "freedreno_dev_info.h"
#define PROP(x) printf("props.%-48s 0x%04zx\n", #x, offsetof(struct fd_dev_info,props.x))
int main(void) {
 printf("ABI_V38 sizeof=0x%zx magic=0x%zx props=0x%zx quirks=0x%zx\n",
   sizeof(struct fd_dev_info),
   offsetof(struct fd_dev_info,magic_raw),
   offsetof(struct fd_dev_info,props),
   offsetof(struct fd_dev_info,quirks));
 PROP(has_fs_tex_prefetch);
 PROP(has_coherent_ubwc_flag_caches);
 PROP(ubwc_coherency_quirk);
 PROP(broken_ds_ubwc_quirk);
 PROP(has_gmem_fast_clear);
 PROP(has_ubwc_linear_mipmap_fallback);
 PROP(supports_linear_mipmap_threshold_in_blocks);
 PROP(has_gmem_vpc_attr_buf);
 PROP(supports_uav_ubwc);
 PROP(ubwc_unorm_snorm_int_compatible);
 PROP(enable_tp_ubwc_flag_hint);
 PROP(ubwc_all_formats_compatible);
 PROP(has_image_processing);
 PROP(subpass_fence_cleans_resolve);
 PROP(has_lrz_feedback);
 PROP(concurrent_resolve);
 PROP(has_z24uint_s8uint);
 PROP(has_scalar_alu);
 PROP(supports_double_threadsize);
 PROP(has_early_preamble);
 PROP(gmem_ccu_color_cache_fraction);
 PROP(gmem_per_ccu_color_cache_size);
 PROP(gmem_ccu_depth_cache_fraction);
 PROP(gmem_per_ccu_depth_cache_size);
 PROP(sysmem_ccu_color_cache_fraction);
 PROP(sysmem_per_ccu_color_cache_size);
 PROP(sysmem_ccu_depth_cache_fraction);
 PROP(sysmem_per_ccu_depth_cache_size);
 PROP(gmem_vpc_attr_buf_size);
 PROP(gmem_vpc_pos_buf_size);
 PROP(gmem_vpc_bv_pos_buf_size);
 PROP(max_sets);
 PROP(line_width_min);
 PROP(max_draw_states);
 PROP(max_texel_buffer_range_elements);
 PROP(max_storage_buffer_range_bytes);
 return 0;
}
