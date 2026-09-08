#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=be6bc2e9c60799e071dd2fafa6216e8d80ec619c
PARENT_SOURCE=388cff5177f82e75a667d529212d34f3c255b7fc
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
PATCH_PATH="$SCRIPT_DIR/full-predication-arm64.patch"
VARIANT="${V20_VARIANT:-parent-texture}"

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20G requires hardened buildable source $SOURCE_COMMIT" >&2
  exit 20
fi

echo "V20G variant=$VARIANT source=$SOURCE_COMMIT parent=$PARENT_SOURCE"

case "$VARIANT" in
  parent-texture)
    git checkout "$PARENT_SOURCE" -- \
      src/video_core/texture_cache/texture_cache.cpp \
      src/video_core/texture_cache/texture_cache.h
    ;;
  parent-videoout)
    git checkout "$PARENT_SOURCE" -- \
      src/core/libraries/videoout/driver.cpp \
      src/core/libraries/videoout/driver.h
    ;;
  *)
    echo "Unknown V20_VARIANT=$VARIANT" >&2
    exit 21
    ;;
esac

# Apply the reviewed real predication port on top of the buildable ARM64/FEX tree.
git apply --check "$PATCH_PATH"
git apply --index "$PATCH_PATH"

case "$VARIANT" in
  parent-texture)
    git add src/video_core/texture_cache/texture_cache.cpp src/video_core/texture_cache/texture_cache.h
    ;;
  parent-videoout)
    git add src/core/libraries/videoout/driver.cpp src/core/libraries/videoout/driver.h
    ;;
esac

git diff --cached --check

test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -q 'EnableFromZpass' src/video_core/amdgpu/liverpool.cpp
grep -q 'RestorePredicatedIndexBase' src/video_core/amdgpu/liverpool.cpp
grep -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'copyQueryPoolResults' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'QueryType::eOcclusion' src/video_core/renderer_vulkan/vk_predication.cpp
for method in IsGpuThread InGfxTask EnqueueCommand; do
  grep -q "$method" src/video_core/amdgpu/liverpool.h
done
test -f runtime/scripts/build-shadps4-arm64.sh
test -f runtime/scripts/install-debian-runtime-deps.sh

# Keep the hardened Presenter intact in this round so these tests isolate either
# TextureCache or VideoOut rather than changing frame-format/blank-frame behavior again.
grep -q "embedded X11 server's DRI3 path" src/video_core/renderer_vulkan/vk_presenter.cpp
grep -q 'PrepareBlankFrame(false)' src/core/libraries/videoout/driver.cpp || \
  [[ "$VARIANT" == "parent-videoout" ]]

if grep -q 'LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");' \
    src/video_core/amdgpu/liverpool.cpp; then
  echo "Legacy IT_SET_PREDICATION stub still present" >&2
  exit 22
fi

echo "V20G $VARIANT ready for AArch64/FEX compilation"
git diff --cached --stat
