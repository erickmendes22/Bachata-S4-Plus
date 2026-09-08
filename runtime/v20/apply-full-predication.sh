#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=be6bc2e9c60799e071dd2fafa6216e8d80ec619c
PARENT_RENDERER=388cff5177f82e75a667d529212d34f3c255b7fc
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
PATCH_PATH="$SCRIPT_DIR/full-predication-arm64.patch"
VARIANT="${V20_VARIANT:-blankfix}"

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20E requires hardened buildable source $SOURCE_COMMIT" >&2
  exit 20
fi

echo "V20E variant=$VARIANT source=$SOURCE_COMMIT"

case "$VARIANT" in
  blankfix)
    ;;
  parent-presenter-texture)
    git checkout "$PARENT_RENDERER" -- \
      src/video_core/renderer_vulkan/vk_presenter.cpp \
      src/video_core/renderer_vulkan/vk_presenter.h \
      src/video_core/texture_cache/texture_cache.cpp \
      src/video_core/texture_cache/texture_cache.h
    ;;
  *)
    echo "Unknown V20_VARIANT=$VARIANT" >&2
    exit 21
    ;;
esac

python3 - <<'PY'
from pathlib import Path
p = Path('src/core/libraries/videoout/driver.cpp')
s = p.read_text()
old = '''void VideoOutDriver::DrawBlankFrame() {\n    const auto empty_frame = presenter->PrepareBlankFrame(false);\n    if (empty_frame) {\n        presenter->Present(empty_frame);\n    }\n}'''
new = '''void VideoOutDriver::DrawBlankFrame() {\n    const auto empty_frame = presenter->PrepareBlankFrame(true);\n    if (empty_frame) {\n        presenter->Present(empty_frame);\n    }\n}'''
if old not in s:
    raise SystemExit('DrawBlankFrame hardened block not found')
p.write_text(s.replace(old, new, 1))
PY

git apply --check "$PATCH_PATH"
git apply --index "$PATCH_PATH"
git add src/core/libraries/videoout/driver.cpp
if [[ "$VARIANT" == "parent-presenter-texture" ]]; then
  git add \
    src/video_core/renderer_vulkan/vk_presenter.cpp \
    src/video_core/renderer_vulkan/vk_presenter.h \
    src/video_core/texture_cache/texture_cache.cpp \
    src/video_core/texture_cache/texture_cache.h
fi

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
grep -q 'PrepareBlankFrame(true)' src/core/libraries/videoout/driver.cpp

if grep -q 'LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");' \
    src/video_core/amdgpu/liverpool.cpp; then
  echo "Legacy IT_SET_PREDICATION stub still present" >&2
  exit 22
fi

echo "V20E $VARIANT ready for AArch64/FEX compilation"
git diff --cached --stat
