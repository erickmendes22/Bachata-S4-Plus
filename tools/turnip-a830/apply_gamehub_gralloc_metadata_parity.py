#!/usr/bin/env python3
"""Port the original GameHub ELF's gralloc -> modifier overlay to pinned V38.

Verified from ORIGINAL GameHub libvulkan_freedreno.so SHA256
1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404
ARM64:
 0xCA2C0C..0xCA2EB8: creates legacy gralloc, IMapper5, libui fallback
 0xCA2EC0..0xCA3178: get_buffer_basic_info:
    0xCA2F04  BL 0xCA1B7C     legacy gralloc basic-info callback
    0xCA2F18  LDR x8, [x8,#0x48] AIMapper5 getStandardMetadata
    0xCA2F1C  type=7        FourCC
    0xCA3034  type=8        modifier
    0xCA310C..0xCA3138 libui GraphicBufferMapper same two attributes
    0xCA3168..0xCA3170 only OVERWRITES FourCC and modifier
 0xCA1B7C..0xCA1BF0 copies the entire legacy-gralloc basic-info result.

The original does NOT replace native_handle FD/stride/offset by parsing
IMapper5 PLANE_LAYOUTS. V38 custom IMapper5 port did do that and collapsed
certain QTI metadata planes, a concrete divergence in UBWC import.

This patch restores GameHub's layout source while retaining V38's existing
IMapper parser as a fallback for devices whose legacy gralloc fails. Legacy
fourcc/modifier are overwritten only if both modern metadata values exist.
Also ports the original libui getInstance/getPixelFormatFourCC/
getPixelFormatModifier fallback without linking a private Android library.
"""
import sys
from pathlib import Path

SOURCE=Path("src/util/u_gralloc/u_gralloc_aimapper.c")

STRUCT_OLD="""struct aimapper_gralloc {
   struct u_gralloc base;
   void *mapper_lib;
   AIMapper *mapper;
};"""
STRUCT_NEW="""struct aimapper_gralloc {
   struct u_gralloc base;
   void *mapper_lib;
   AIMapper *mapper;
   // Original GameHub reads layout/strides/fds through legacy gralloc.
   struct u_gralloc *gamehub_legacy;
   void *gamehub_libui;
   void *gamehub_gbm;
   int32_t (*gamehub_fourcc)(void *, const native_handle_t *, uint32_t *);
   int32_t (*gamehub_modifier)(void *, const native_handle_t *, uint64_t *);
};"""

# before original V38 code interprets raw IMapper plane layouts
BEFORE_BASIC="""   uint32_t fourcc = 0;
   if (!md_scalar(gr, hnd->handle, SMT_PIXEL_FORMAT_FOURCC, &fourcc,"""
AFTER_BASIC="""   // GameHub's basic-info assembly first calls the LEGACY gralloc
   // to obtain the exact FDs/strides/plane offsets. IMapper5 or libui only
   // supplies FourCC+modifier; it does not redefine the plane layout.
   // This matters for QTI UBWC where PLANE_LAYOUTS reports a separate
   // metadata plane that must not be treated as a separate DMA-BUF.
   if (gr->gamehub_legacy) {
      struct u_gralloc_buffer_basic_info inherited = {0};
      int ret = gr->gamehub_legacy->ops.get_buffer_basic_info(
         gr->gamehub_legacy, hnd, &inherited);
      if (ret == 0) {
         uint32_t mapped_fourcc = 0;
         uint64_t mapped_modifier = DRM_FORMAT_MOD_INVALID;
         bool got_metadata = false;
         if (gr->mapper) {
            got_metadata =
               md_scalar(gr, hnd->handle, SMT_PIXEL_FORMAT_FOURCC,
                         &mapped_fourcc, sizeof(mapped_fourcc)) &&
               md_scalar(gr, hnd->handle, SMT_PIXEL_FORMAT_MODIFIER,
                         &mapped_modifier, sizeof(mapped_modifier));
         } else if (gr->gamehub_gbm && gr->gamehub_fourcc &&
                    gr->gamehub_modifier) {
            got_metadata =
               gr->gamehub_fourcc(gr->gamehub_gbm, hnd->handle,
                                  &mapped_fourcc) == 0 &&
               gr->gamehub_modifier(gr->gamehub_gbm, hnd->handle,
                                    &mapped_modifier) == 0;
         }
         if (got_metadata) {
            if (!mapped_fourcc) {
               const int hal_fourcc = get_fourcc_from_hal_format(hnd->hal_format);
               if (hal_fourcc != -1)
                  mapped_fourcc = (uint32_t)hal_fourcc;
            }
            if (mapped_fourcc) {
               *out = inherited;
               out->drm_fourcc = mapped_fourcc;
               out->modifier = mapped_modifier;
               return 0;
            }
         }
      }
   }

   // Keep V38 IMapper5 plane-layout decoding only if the original
   // GameHub layout path was unavailable for this particular allocation.
   // Never dereference a missing IMapper when libui is the only backend.
   if (!gr->mapper)
      return -EINVAL;

   uint32_t fourcc = 0;
   if (!md_scalar(gr, hnd->handle, SMT_PIXEL_FORMAT_FOURCC, &fourcc,"""

DESTROY_OLD="""   /* The mapper is owned by the vendor library; only the handle is ours.
    * Leave it loaded — unloading an SP-HAL under a live driver is not worth
    * the risk for a process-lifetime singleton.
    */
   FREE(gr);"""
DESTROY_NEW="""   if (gr->gamehub_legacy)
      gr->gamehub_legacy->ops.destroy(gr->gamehub_legacy);
   if (gr->gamehub_libui)
      dlclose(gr->gamehub_libui);

   /* Vendor SP-HAL is process-lifetime; do not unload the provider. */
   FREE(gr);"""

CREATE_OLD="""struct u_gralloc *
u_gralloc_aimapper_create(void)
{
   /* libvndksupport is the sanctioned route for a non-vendor process to load a
    * same-process vendor HAL; the Android Vulkan loader uses it for exactly
    * this. Without it we have no business touching /vendor libraries.
    */
   void *vndk = dlopen("libvndksupport.so", RTLD_NOW);
   if (!vndk)
      return NULL;

   sphal_load_fn sphal =
      (sphal_load_fn)dlsym(vndk, "android_load_sphal_library");
   if (!sphal)
      return NULL;

   load_imapper_fn load = NULL;
   void *lib = load_vendor_mapper(sphal, &load);
   if (!lib)
      return NULL;

   AIMapper *mapper = NULL;
   if (load(&mapper) != 0 || !mapper)
      return NULL;

   if (mapper->version < AIMAPPER_VERSION_5) {
      mesa_logw("aimapper: version %u is below 5, declining", mapper->version);
      return NULL;
   }

   if (!mapper->v5.getStandardMetadata)
      return NULL;

   struct aimapper_gralloc *gr = CALLOC_STRUCT(aimapper_gralloc);
   if (!gr)
      return NULL;

   gr->mapper_lib = lib;
   gr->mapper = mapper;

   gr->base.ops.get_buffer_basic_info = aimapper_get_buffer_basic_info;
   gr->base.ops.get_buffer_color_info = aimapper_get_buffer_color_info;
   gr->base.ops.destroy = destroy;

   mesa_logi("Using IMapper v5 stable-C API via SP-HAL");

   return &gr->base;
}"""
CREATE_NEW="""struct u_gralloc *
u_gralloc_aimapper_create(void)
{
   // GameHub loads the vendor SP-HAL through android_load_sphal_library
   // when available, but keeps libui as an independent fallback.
   void *vndk = dlopen("libvndksupport.so", RTLD_NOW);
   sphal_load_fn sphal = NULL;
   if (vndk)
      sphal = (sphal_load_fn)dlsym(vndk, "android_load_sphal_library");
   if (!sphal)
      sphal = (sphal_load_fn)dlsym(RTLD_DEFAULT,
                                  "android_load_sphal_library");

   load_imapper_fn load = NULL;
   void *lib = sphal ? load_vendor_mapper(sphal, &load) : NULL;
   AIMapper *mapper = NULL;
   if (lib && load && (load(&mapper) != 0 || !mapper ||
                       mapper->version < AIMAPPER_VERSION_5 ||
                       !mapper->v5.getStandardMetadata))
      mapper = NULL;

   struct aimapper_gralloc *gr = CALLOC_STRUCT(aimapper_gralloc);
   if (!gr)
      return NULL;

   gr->mapper_lib = lib;
   gr->mapper = mapper;

   // Same base first as the GameHub ELF @ 0xca2e0c, before modifier metadata.
   gr->gamehub_legacy = u_gralloc_fallback_create();

   // Original GameHub uses this exact dynamically resolved libui ABI when
   // the vendor IMapper5 metadata interface cannot be used.
   gr->gamehub_libui = dlopen("libui.so", RTLD_NOW | RTLD_LOCAL);
   void *ui = gr->gamehub_libui ? gr->gamehub_libui : RTLD_DEFAULT;
   typedef void *(*get_instance_fn)(void);
   get_instance_fn get_instance = (get_instance_fn)dlsym(
      ui, "_ZN7android9SingletonINS_19GraphicBufferMapperEE11getInstanceEv");
   gr->gamehub_fourcc = (int32_t (*)(void *, const native_handle_t *, uint32_t *))
      dlsym(ui, "_ZN7android19GraphicBufferMapper20getPixelFormatFourCCEPK13native_handlePj");
   gr->gamehub_modifier = (int32_t (*)(void *, const native_handle_t *, uint64_t *))
      dlsym(ui, "_ZN7android19GraphicBufferMapper22getPixelFormatModifierEPK13native_handlePm");
   if (get_instance && gr->gamehub_fourcc && gr->gamehub_modifier)
      gr->gamehub_gbm = get_instance();

   // Without IMapper5 or GraphicBufferMapper there is no metadata provider.
   if (!mapper && !gr->gamehub_gbm) {
      if (gr->gamehub_legacy)
         gr->gamehub_legacy->ops.destroy(gr->gamehub_legacy);
      if (gr->gamehub_libui)
         dlclose(gr->gamehub_libui);
      FREE(gr);
      return NULL;
   }

   gr->base.ops.get_buffer_basic_info = aimapper_get_buffer_basic_info;
   gr->base.ops.get_buffer_color_info = aimapper_get_buffer_color_info;
   gr->base.ops.destroy = destroy;

   mesa_logi("GameHub A830 gralloc: legacy FD/stride + IMapper5/libui format/modifier");
   return &gr->base;
}"""

COLOR_OLD="""   if (!hnd->handle)
      return -EINVAL;

   /* Defaults match u_gralloc.c's when a backend has no color op at all. */"""
COLOR_NEW="""   if (!hnd->handle)
      return -EINVAL;

   if (!gr->mapper) {
      // libui-only fallback: GameHub obtains basic image format information
      // from GraphicBufferMapper; default color data is sufficient for RGB.
      out->yuv_color_space = __DRI_YUV_COLOR_SPACE_ITU_REC601;
      out->sample_range = __DRI_YUV_NARROW_RANGE;
      out->horizontal_siting = __DRI_YUV_CHROMA_SITING_0_5;
      out->vertical_siting = __DRI_YUV_CHROMA_SITING_0_5;
      return 0;
   }

   /* Defaults match u_gralloc.c's when a backend has no color op at all. */"""

def apply(path:Path):
    s=path.read_text()
    for name,old,new in [
        ("struct",STRUCT_OLD,STRUCT_NEW),
        ("basic",BEFORE_BASIC,AFTER_BASIC),
        ("color",COLOR_OLD,COLOR_NEW),
        ("destroy",DESTROY_OLD,DESTROY_NEW),
        ("create",CREATE_OLD,CREATE_NEW),
    ]:
        if s.count(old)!=1:
            raise RuntimeError(f"Pinned GameHub A830 gralloc {name} anchor drift: {s.count(old)}")
        s=s.replace(old,new,1)
    for need in ("SMT_PIXEL_FORMAT_FOURCC", "SMT_PIXEL_FORMAT_MODIFIER",
                 "u_gralloc_fallback_create()", "gr->gamehub_legacy",
                 "gr->gamehub_gbm", "libui.so", "AIMapper_loadIMapper"):
        if need not in s:
            raise RuntimeError("Required GameHub fallback missing: "+need)
    path.write_text(s)
    print("PASS: original GameHub gralloc ABI path restored (legacy layout + metadata overlay + libui fallback)")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/util/u_gralloc/u_gralloc_aimapper.c"))
