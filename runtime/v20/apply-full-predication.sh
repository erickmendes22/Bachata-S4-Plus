#!/usr/bin/env bash
set -euo pipefail

PATCH_COMMIT=3559530df5aec4067a95912af13ef14896b65ada
UPSTREAM_URL=https://github.com/shadps4-emu/shadPS4.git

if git rev-parse --verify "$PATCH_COMMIT^{commit}" >/dev/null 2>&1; then
  :
else
  git fetch --no-tags "$UPSTREAM_URL" "$PATCH_COMMIT"
fi

# Apply the upstream implementation as a real source change, preserving this ARM64 fork.
# --no-commit leaves the patched tree available for verification/build.
if ! git cherry-pick --no-commit "$PATCH_COMMIT"; then
  echo 'V20: upstream predication commit did not apply cleanly.' >&2
  git status --short >&2 || true
  git diff --name-only --diff-filter=U >&2 || true
  exit 20
fi

# Hard verification: do not build a fake/partial V20.
test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'copyQueryPoolResults' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'vk::QueryType::eOcclusion' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'PredicationManager' src/video_core/renderer_vulkan/vk_rasterizer.h
if grep -q 'Unimplemented IT_SET_PREDICATION"' src/video_core/amdgpu/liverpool.cpp; then
  echo 'V20 verification failed: legacy unimplemented SET_PREDICATION path is still present.' >&2
  exit 21
fi

printf 'V20 full predication source verified at %s\n' "$PATCH_COMMIT"

