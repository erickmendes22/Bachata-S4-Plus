\
#!/usr/bin/env bash
set -euo pipefail

PATCH_COMMIT=3559530df5aec4067a95912af13ef14896b65ada
UPSTREAM_URL=https://github.com/shadps4-emu/shadPS4.git

git remote remove shadps4-upstream >/dev/null 2>&1 || true
git remote add shadps4-upstream "$UPSTREAM_URL"

git -c fetch.recurseSubmodules=false \
    fetch --no-tags --no-recurse-submodules \
    shadps4-upstream "$PATCH_COMMIT"

if ! git -c submodule.recurse=false cherry-pick --no-commit "$PATCH_COMMIT"; then
  echo "V20: upstream predication commit did not apply cleanly." >&2
  git status --short >&2 || true
  git diff --name-only --diff-filter=U >&2 || true
  exit 20
fi

test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
find src -type f -name 'occlusion_predicate.comp' -print -quit | grep -q .
grep -R -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan
grep -R -q 'copyQueryPoolResults' src/video_core/renderer_vulkan
grep -R -q 'QueryType::eOcclusion' src/video_core/renderer_vulkan

if grep -R -q 'Unimplemented IT_SET_PREDICATION' src/video_core; then
  echo "V20 verification failed: legacy unimplemented SET_PREDICATION path remains" >&2
  exit 22
fi

printf 'V20 full predication source verified at %s\n' "$PATCH_COMMIT"
