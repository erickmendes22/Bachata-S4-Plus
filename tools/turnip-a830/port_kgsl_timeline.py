#!/usr/bin/env python3
"""Source-aware port of Mesa MR39751 (Zan Dobersek) to pinned Gen39 Mesa f28352d.

Runs AFTER the six original WinNative V39 A8xx patches. Do not fuzzy-apply
the historical profiling refactor: modern Mesa already changed the syncobj
submit and has important EPROTO/OOM cleanup fixes. Preserve that path and
integrate only the independent native timeline implementation.

Usage: port_kgsl_timeline.py <mesa-tree> <patch-dir>
"""
import re
import sys
from pathlib import Path

if len(sys.argv) != 3:
    sys.exit("usage: port_kgsl_timeline.py MESA_ROOT PATCH_DIR")
root = Path(sys.argv[1])
patchdir = Path(sys.argv[2])
p1 = (patchdir / "39751-1.patch").read_text()
p2 = (patchdir / "39751-2.patch").read_text()

def additions(patch, marker):
    start = patch.index(marker)
    start = patch.index("\n", start) + 1
    end = patch.find("\n@@ ", start)
    nextfile = patch.find("\ndiff --git", start)
    if end < 0 or (nextfile >= 0 and nextfile < end):
        end = nextfile
    if end < 0:
        end = len(patch)
    out = "".join(line[1:] for line in patch[start:end].splitlines(keepends=True)
                  if line.startswith("+") and not line.startswith("+++"))
    assert out.strip(), "No code for " + marker
    return out

def replace_one(text, old, new, name):
    assert text.count(old) == 1, f"{name}: source anchor mismatch (found {text.count(old)})"
    return text.replace(old, new, 1)

def apply(rel, transform):
    path = root / rel
    content = path.read_text()
    new = transform(content)
    assert new != content, f"{rel}: no modifications applied"
    path.write_text(new)

apply("src/freedreno/vulkan/tu_common.h", lambda s:
      replace_one(s, '#include "vk_sync_timeline.h"',
                  '#include "vk_sync_binary.h"\n#include "vk_sync_timeline.h"',
                  "binary sync include"))

def device_header(s):
    s = replace_one(s, "extern uint64_t os_page_size;",
                    """enum tu_kgsl_sync_impl_type {
   TU_KGSL_SYNC_IMPL_TYPE_SYNCOBJ,
   TU_KGSL_SYNC_IMPL_TYPE_TIMELINE,
};

extern uint64_t os_page_size;""", "native timeline selector")
    s = replace_one(s, "   struct vk_sync_type syncobj_type;",
                    """   enum tu_kgsl_sync_impl_type kgsl_sync_impl_type;
   struct vk_sync_type syncobj_type;
   struct vk_sync_binary_type binary_type;""", "physical device sync types")
    return s
apply("src/freedreno/vulkan/tu_device.h", device_header)

apply("src/freedreno/vulkan/tu_queue.h", lambda s:
      replace_one(s, "   int fence;           /* timestamp/fence of the last queue submission */",
                  """   int fence;           /* timestamp/fence of the last queue submission */

   uint32_t kgsl_queue_timeline_id;
   uint64_t kgsl_queue_timeline_seqno;""", "queue timeline state"))

def kernel(s):
    # Reuse the exact upstream ioctl helpers, including native KGSL GPU timeline commands.
    native_ioctl = additions(p2, "@@ -49,6 +49,92 @@ safe_ioctl")
    s = replace_one(s, "static int\nkgsl_submitqueue_new",
                    native_ioctl + "static int\nkgsl_submitqueue_new",
                    "native KGSL ioctl helpers")

    # Hook the queue timeline lifecycle to the existing KGSL context.
    start = s.index("static int\nkgsl_submitqueue_new(")
    end = s.index("static void kgsl_bo_finish(", start)
    function = s[start:end]
    function = replace_one(function, "   if (ret)\n      return ret;",
                           "   if (ret)\n      goto fail;", "queue init error path")
    function = replace_one(function, "   queue->msm_queue_id = req.drawctxt_id;",
                           """   queue->msm_queue_id = req.drawctxt_id;
   if (dev->physical_device->kgsl_sync_impl_type == TU_KGSL_SYNC_IMPL_TYPE_TIMELINE) {
      ret = kgsl_timeline_create_ioctl(dev->physical_device->local_fd,
                                       0, &queue->kgsl_queue_timeline_id);
      if (ret)
         goto fail;
   }""", "queue timeline allocation")
    function = replace_one(function, "   return 0;\n}",
                           """   return 0;
fail:
   kgsl_submitqueue_destroy(dev, queue);
   return ret;
}""", "queue cleanup")
    close = function.index("static void\nkgsl_submitqueue_close(")
    function = function[:close] + """static void
kgsl_submitqueue_close(struct tu_device *dev, struct tu_queue *queue)
{
   kgsl_submitqueue_destroy(dev, queue);
}

"""
    s = s[:start] + function + s[end:]

    # A nanosecond deadline is required by the native timeline wait ioctl.
    s = replace_one(s, "static VkResult\nwait_timestamp_safe(",
                    additions(p2, "@@ -712,6 +804,19 @@ get_relative_ms") +
                    "static VkResult\nwait_timestamp_safe(",
                    "native timeout")

    # Native Vulkan vk_sync_type with native GPU/CPU waits and signals.
    s = replace_one(s, "struct tu_kgsl_queue_submit {",
                    additions(p2, "@@ -1203,6 +1308,151 @@ const struct vk_sync_type vk_kgsl_sync_type") +
                    "struct tu_kgsl_queue_submit {", "native sync type")

    # Insert upstream profiling helpers solely for the new timeline path.
    # Preserve the modern pre-existing syncobj submit and its error handling.
    s = replace_one(s, "static VkResult\nkgsl_queue_submit(struct tu_queue *queue",
                    additions(p1, "@@ -1320,6 +1320,101 @@ kgsl_bind_finalize") +
                    "static VkResult\nkgsl_queue_submit_syncobj(struct tu_queue *queue",
                    "preserve syncobj submit")

    # The upstream native timeline submit directly attaches GPU timeline
    # signal aux commands and allows kernel-side wait-any, without CPU FD merges.
    s = replace_one(s, "static VkResult\nkgsl_device_init(struct tu_device *dev)",
                    additions(p2, "@@ -1647,6 +1897,283 @@ fail_submit") +
                    "static VkResult\nkgsl_device_init(struct tu_device *dev)",
                    "GPU-native timeline queue submit")

    # Native timeline support is probed at device creation; unsupported
    # kernels keep the original Gen39 syncobj behavior.
    old = """   device->timeline_type = vk_sync_timeline_get_type(&vk_kgsl_sync_type);

   device->sync_types[0] = &vk_kgsl_sync_type;
   device->sync_types[1] = &device->timeline_type.sync;
   device->sync_types[2] = NULL;"""
    new = """   uint32_t dummy_timeline_id = 0;
   if (kgsl_timeline_create_ioctl(fd, 0, &dummy_timeline_id) == 0) {
      kgsl_timeline_destroy_ioctl(fd, dummy_timeline_id);
      device->kgsl_sync_impl_type = TU_KGSL_SYNC_IMPL_TYPE_TIMELINE;
   } else {
      device->kgsl_sync_impl_type = TU_KGSL_SYNC_IMPL_TYPE_SYNCOBJ;
   }

   switch (device->kgsl_sync_impl_type) {
   case TU_KGSL_SYNC_IMPL_TYPE_SYNCOBJ:
      device->timeline_type = vk_sync_timeline_get_type(&vk_kgsl_sync_type);
      device->sync_types[0] = &vk_kgsl_sync_type;
      device->sync_types[1] = &device->timeline_type.sync;
      break;
   case TU_KGSL_SYNC_IMPL_TYPE_TIMELINE:
      device->binary_type = vk_sync_binary_get_type(&vk_kgsl_timeline_type);
      device->sync_types[0] = &vk_kgsl_timeline_type;
      device->sync_types[1] = &device->binary_type.sync;
      break;
   }
   device->sync_types[2] = NULL;"""
    s = replace_one(s, old, new, "runtime kernel timeline detection")
    assert s.count("kgsl_queue_submit_syncobj(") >= 2
    assert s.count("kgsl_queue_submit_timeline(") >= 2
    assert "KGSL_GPU_AUX_COMMAND_TIMELINE" in s
    assert "KGSL_TIMELINE_WAIT" in s
    return s

apply("src/freedreno/vulkan/tu_knl_kgsl.cc", kernel)
print("Mesa MR39751 native KGSL timeline port installed, preserving original V39 syncobj submit")
