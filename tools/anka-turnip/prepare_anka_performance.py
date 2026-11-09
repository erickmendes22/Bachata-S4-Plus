#!/usr/bin/env python3
"""Inject verified extra performance backports into Anka v1.0.0 official build.

Pinned Anka commit: ec336240478e6be391cb5f319b0d3ef09f97c0a0
Pinned Droid-Deck source: c437d891164c5e31a65219a5451005875fab74ac
Original seven Anka patches are applied unchanged; this runs after them.
"""
import argparse
from pathlib import Path

HOOK = '# 3. The cross file and the build (the options of the released build). The build folder is inside\n'
EXTRA = r"""
# 2b. Additional A830 performance patches, preserving all seven original Anka patches.
# DD_SRC must point at the separately pinned Droid-Deck patch source checkout.
: "${DD_SRC:?Set DD_SRC to pinned Droid-Deck/Drivers source}"
(
  cd "$SRC"
  export PYTHONPATH="$DD_SRC/patches/scripts"
  # Kernel PWR_MAX on KGSL submission, refreshed every 1000 submits.
  python3 "$DD_SRC/patches/scripts/perf_pwr_max.py"
  # GMEM bandwidth factor 11 -> 10, as in DD-Turnip.
  python3 "$DD_SRC/patches/scripts/autotune_bandwidth.py"
  # Vulkan optional required subgroup=32 on A8xx (potential compute throughput).
  if [ "${ANKA_HALF_WAVE:-1}" = 1 ]; then
      p="$DD_SRC/patches/linux/0002-ir3-half-wave-subgroups.patch"
      if git apply --check "$p"; then
          git apply "$p"
          echo "Applied A830 half-wave subgroup patch"
      elif git apply --reverse --check "$p"; then
          echo "A830 half-wave subgroup patch already in Mesa"
      else
          echo "A830 half-wave patch incompatible with pinned Mesa; stop rather than ship unmodified binary" >&2
          exit 2
      fi
  fi
  grep -Fq 'KGSL_CMDBATCH_PWR_CONSTRAINT' src/freedreno/vulkan/tu_knl_kgsl.cc
  # Mesa upstream 2026-10-08 e984ef294e: KGSL zero-timeout fix.
  # Pinned 2026-11-07 Anka Mesa already carries it; do NOT patch twice.
  grep -Fq 'kgsl_poll_timestamp' src/freedreno/vulkan/tu_knl_kgsl.cc || {
    echo "Missing KGSL Zero Timeout patch e984ef29 in pinned Mesa" >&2
    exit 3
  }
  grep -Fq 'return kgsl_poll_timestamp(device, context_id, timestamp);' src/freedreno/vulkan/tu_knl_kgsl.cc || {
    echo "KGSL zero-timeout must use non-blocking READTIMESTAMP; refused" >&2
    exit 3
  }
  grep -Fq 'gmem_bandwidth * 10 + total_draw_call_bandwidth' src/freedreno/vulkan/tu_autotune.cc
  if [ "${ANKA_HALF_WAVE:-1}" = 1 ]; then
      grep -Fq 'ir3_nir_lower_half_subgroups' src/freedreno/ir3/ir3_lower_subgroups.c
  fi
  echo "Anka extra patches validated against Mesa source"
)
"""
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build_sh", type=Path)
    args = ap.parse_args()
    path=args.build_sh
    s=path.read_text()
    if s.count(HOOK)!=1: raise SystemExit("Anka v1.0.0 build.sh marker drift; refusing to patch")
    if "Anka extra patches validated against Mesa source" in s: raise SystemExit("Anka builder already customized")
    path.write_text(s.replace(HOOK, EXTRA+"\n"+HOOK))
    print(f"Injected A830 performance patch stage into {path}")
if __name__ == "__main__":
    main()
