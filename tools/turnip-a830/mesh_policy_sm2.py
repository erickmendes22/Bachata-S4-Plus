#!/usr/bin/env python3
"""Spider-Man 2 DX12 capability-path experiment.

Gen39 WinNative 0001 unconditionally advertises compute-emulated mesh shaders
on Adreno 840. Rutabaga includes per-application gating of mesh support.
Default OFF in this dedicated driver variant; preserve an explicit override.
"""
from pathlib import Path
import sys

p = Path("src/freedreno/vulkan/tu_device.cc")
s = p.read_text()
old = """   return device->info->chip >= 7 &&
          device->info->cs_shared_mem_size >= 32 * 1024;"""
new = """   /* Experimental Spider-Man 2 compatibility path: do not advertise
    * compute-emulated mesh shaders without an explicit opt-in.
    * This only changes Vulkan device capabilities, not shader compilation.
    */
   if (!debug_get_bool_option("TU_SPIDERMAN2_COMPUTE_MESH", false))
      return false;

   return device->info->chip >= 7 &&
          device->info->cs_shared_mem_size >= 32 * 1024;"""
if s.count(old) != 1:
    sys.exit("ERR: Gen39 mesh shader predicate changed; refusing blind patch")
s = s.replace(old, new, 1)
assert s.count('TU_SPIDERMAN2_COMPUTE_MESH') == 1
p.write_text(s)
print("Spider-Man 2 mesh shader feature policy: opt-in, default OFF")
