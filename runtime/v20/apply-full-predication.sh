#!/usr/bin/env bash
set -euo pipefail

# Reviewed port of upstream shadPS4 predication commit
# 3559530df5aec4067a95912af13ef14896b65ada onto the Android runtime below.
# Preserve the runtime queue, presenter, pointer guards, and Vulkan workarounds.
SOURCE_COMMIT=be6bc2e9c60799e071dd2fafa6216e8d80ec619c
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
PATCH_PATH="$SCRIPT_DIR/full-predication-arm64.patch"

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20 requires source commit $SOURCE_COMMIT; refusing an unreviewed merge." >&2
  exit 20
fi

git apply --check "$PATCH_PATH"
git apply --index "$PATCH_PATH"
git diff --cached --check

test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -q 'EnableFromZpass' src/video_core/amdgpu/liverpool.cpp
grep -q 'RestorePredicatedIndexBase' src/video_core/amdgpu/liverpool.cpp
grep -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan/vk_predication.cpp
for method in IsGpuThread InGfxTask EnqueueCommand; do
  grep -q "$method" src/video_core/amdgpu/liverpool.h
done
grep -q 'Pm4GuestPointerUsable' src/video_core/amdgpu/liverpool.cpp
echo 'V20 reviewed ARM64 predication patch applied; runtime methods retained.'
git diff --cached --stat
