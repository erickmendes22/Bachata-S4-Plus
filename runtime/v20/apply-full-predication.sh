#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=388cff5177f82e75a667d529212d34f3c255b7fc
PRED_COMMIT=3559530df5aec4067a95912af13ef14896b65ada
UPSTREAM_URL=https://github.com/shadps4-emu/shadPS4.git

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20C requires source commit $SOURCE_COMMIT; refusing an unreviewed merge." >&2
  exit 20
fi

# Fetch only the predication commit, never recurse into the Android fork's submodules.
git remote remove shadps4-upstream >/dev/null 2>&1 || true
git remote add shadps4-upstream "$UPSTREAM_URL"
git -c fetch.recurseSubmodules=false fetch --no-tags --no-recurse-submodules \
  shadps4-upstream "$PRED_COMMIT"

# Important: use Git's merge machinery, but prefer the incoming predication side
# ONLY for overlapping hunks. This is different from checking out whole files from
# upstream: non-conflicting ARM64/newer renderer changes remain intact.
git -c submodule.recurse=false cherry-pick --no-commit -X theirs "$PRED_COMMIT"

if git diff --name-only --diff-filter=U | grep -q .; then
  echo "V20C still has unresolved conflicts:" >&2
  git diff --name-only --diff-filter=U >&2
  exit 21
fi

git diff --cached --check

# Hard verification for real predication.
test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -q 'EnableFromZpass' src/video_core/amdgpu/liverpool.cpp
grep -q 'RestorePredicatedIndexBase' src/video_core/amdgpu/liverpool.cpp
grep -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'copyQueryPoolResults' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'QueryType::eOcclusion' src/video_core/renderer_vulkan/vk_predication.cpp

# Ensure the newer ARM64 runtime path and the presenter fix are still present.
for method in IsGpuThread InGfxTask EnqueueCommand; do
  grep -q "$method" src/video_core/amdgpu/liverpool.h
done
grep -q 'Pm4GuestPointerUsable' src/video_core/amdgpu/liverpool.cpp
grep -q 'PrepareBlankFrame(true)' src/core/libraries/videoout/driver.cpp

# Legacy SET_PREDICATION stub must be gone.
if grep -q 'LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");' \
    src/video_core/amdgpu/liverpool.cpp; then
  echo "Legacy IT_SET_PREDICATION stub still present" >&2
  exit 22
fi

echo 'V20C predication integrated with conflict-hunk preference only; newer ARM64 presenter/runtime retained.'
git status --short
git diff --cached --stat
