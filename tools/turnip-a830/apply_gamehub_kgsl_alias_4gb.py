#!/usr/bin/env python3
"""Restore the GameHub A830 KGSL IB-alias 4-GiB boundary retry.

Grounding: ORIGINAL GameHub ARM64 ELF SHA256
1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404:
  0xa3c95c..0xa3c974: alias GPU VA + length - 1 crosses a 4-GiB boundary?
  0xa3ca40..0xa3c8a4: free crossed alias, retry with flag bit 32
  0xa3cb34..0xa3cb54: reject retry that still crosses; clean up
The flag bit is KGSL_MEMFLAGS_FORCE_32BIT in pinned msm_kgsl.h.
The WinNative patch 0005 creates/binds a VBO but omits this retry.
Runs AFTER WinNative patch 0005 and BEFORE compilation.
"""
from pathlib import Path
import sys

BEGIN = "static VkResult\nkgsl_bo_create_alias("
END = "static void\nkgsl_bo_destroy_alias("

REPLACEMENT = r'''static bool
kgsl_gamehub_a830_alias_crosses_4gb(uint64_t base, uint64_t length)
{
   // No allocation of zero bytes or wrapped VA may be considered valid.
   if (!length || base > UINT64_MAX - (length - 1))
      return true;
   // Same check as AArch64 0xa3c964..0xa3c974 and 0xa3cb3c..0xa3cb4c.
   return (base >> 32) != ((base + length - 1) >> 32);
}

static VkResult
kgsl_bo_create_alias(struct tu_device *dev, struct tu_bo *bo, uint64_t align)
{
   const int fd = dev->physical_device->local_fd;
   const uint64_t chip_id = dev->physical_device->dev_id.chip_id;
   const bool gamehub_a830_alias_guard =
      chip_id == 0xffff44050000ull ||
      chip_id == 0xffff44050001ull ||
      chip_id == 0x44050001ull;

   // The working GameHub first attempts ordinary VBO allocation. If that
   // GPU VA crosses a 4-GiB boundary, the rejected alias is freed and the
   // second and final allocation uses KGSL_MEMFLAGS_FORCE_32BIT.
   // On other GPUs retain the pre-existing WinNative behavior.
   const unsigned attempts = gamehub_a830_alias_guard ? 2 : 1;
   for (unsigned attempt = 0; attempt < attempts; ++attempt) {
      struct kgsl_gpuobj_alloc alloc = {
         .size = bo->size,
         .flags = KGSL_MEMFLAGS_VBO | KGSL_MEMFLAGS_VBO_NO_MAP_ZERO |
                  kgsl_align_flag(align) |
                  (attempt ? KGSL_MEMFLAGS_FORCE_32BIT : 0ull),
      };
      if (safe_ioctl(fd, IOCTL_KGSL_GPUOBJ_ALLOC, &alloc))
         return vk_errorf(dev, VK_ERROR_OUT_OF_DEVICE_MEMORY,
                          "GPUOBJ_ALLOC for IB alias failed (%s)",
                          strerror(errno));

      struct kgsl_gpumem_get_info info = {
         .id = alloc.id,
      };
      if (safe_ioctl(fd, IOCTL_KGSL_GPUMEM_GET_INFO, &info)) {
         const int saved_errno = errno;
         struct kgsl_gpumem_free_id free_req = { .id = alloc.id };
         safe_ioctl(fd, IOCTL_KGSL_GPUMEM_FREE_ID, &free_req);
         return vk_errorf(dev, VK_ERROR_OUT_OF_DEVICE_MEMORY,
                          "querying IB alias failed (%s)",
                          strerror(saved_errno));
      }

      if (gamehub_a830_alias_guard &&
          kgsl_gamehub_a830_alias_crosses_4gb(info.gpuaddr, bo->size)) {
         struct kgsl_gpumem_free_id free_req = { .id = alloc.id };
         safe_ioctl(fd, IOCTL_KGSL_GPUMEM_FREE_ID, &free_req);
         if (attempt == 0)
            continue;
         return vk_errorf(dev, VK_ERROR_OUT_OF_DEVICE_MEMORY,
                          "IB alias crosses a 4GB boundary");
      }

      struct kgsl_gpumem_bind_range range = {
         .length = bo->size,
         .child_id = bo->gem_handle,
         .op = KGSL_GPUMEM_RANGE_OP_BIND,
      };
      struct kgsl_gpumem_bind_ranges bind = {
         .ranges = (uint64_t)(uintptr_t)&range,
         .ranges_nents = 1,
         .ranges_size = sizeof(range),
         .id = alloc.id,
      };
      if (safe_ioctl(fd, IOCTL_KGSL_GPUMEM_BIND_RANGES, &bind)) {
         const int saved_errno = errno;
         struct kgsl_gpumem_free_id free_req = { .id = alloc.id };
         safe_ioctl(fd, IOCTL_KGSL_GPUMEM_FREE_ID, &free_req);
         return vk_errorf(dev, VK_ERROR_OUT_OF_DEVICE_MEMORY,
                          "binding IB alias failed (%s)",
                          strerror(saved_errno));
      }

      bo->alias_handle = alloc.id;
      bo->iova = info.gpuaddr;
      return VK_SUCCESS;
   }

   return vk_errorf(dev, VK_ERROR_OUT_OF_DEVICE_MEMORY,
                    "no suitable A830 IB alias");
}

'''

def apply(path: Path) -> None:
    s = path.read_text()
    if s.count(BEGIN) != 1 or s.count(END) != 1:
        raise RuntimeError("Pinned WinNative KGSL alias anchors absent")
    start, end = s.index(BEGIN), s.index(END)
    original = s[start:end]
    for needle in ("KGSL_MEMFLAGS_VBO_NO_MAP_ZERO",
                   "IOCTL_KGSL_GPUOBJ_ALLOC",
                   "IOCTL_KGSL_GPUMEM_GET_INFO",
                   "IOCTL_KGSL_GPUMEM_BIND_RANGES",
                   "KGSL_GPUMEM_RANGE_OP_BIND",
                   "bo->alias_handle = alloc.id",
                   "bo->iova = info.gpuaddr"):
        if needle not in original:
            raise RuntimeError("WinNative alias source drift: " + needle)
    if "kgsl_gamehub_a830_alias_crosses_4gb" in s:
        raise RuntimeError("Already applied")
    s = s[:start] + REPLACEMENT + s[end:]
    if "kgsl_bo_destroy_alias" not in s or "kgsl_bo_needs_alias" not in s:
        raise RuntimeError("Alias life cycle missing")
    path.write_text(s)
    print("PASS A830 KGSL: original 4GB boundary guard + FORCE_32BIT retry + alias cleanup")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv) > 1 else
          Path("src/freedreno/vulkan/tu_knl_kgsl.cc"))
