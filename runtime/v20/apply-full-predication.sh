#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=be6bc2e9c60799e071dd2fafa6216e8d80ec619c
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
PATCH_PATH="$SCRIPT_DIR/full-predication-arm64.patch"
VARIANT="${V20_VARIANT:-formatonly}"

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20F requires hardened buildable source $SOURCE_COMMIT" >&2
  exit 20
fi

echo "V20F variant=$VARIANT source=$SOURCE_COMMIT"

case "$VARIANT" in
  formatonly|format-blankfix)
    ;;
  *)
    echo "Unknown V20_VARIANT=$VARIANT" >&2
    exit 21
    ;;
esac

# Restore only the parent/desktop VideoOut sampled-image format mapping. Do not
# replace Presenter or TextureCache wholesale: the hardened tree has Android/FEX
# APIs and runtime dependencies that must remain intact.
python3 - <<'PY'
from pathlib import Path
p = Path('src/video_core/renderer_vulkan/vk_presenter.cpp')
s = p.read_text()
old = '''static vk::Format GetFrameViewFormat(const Libraries::VideoOut::PixelFormat format) {\n#ifdef ENABLE_BACHATA_RUNTIME\n    // The embedded X11 server's DRI3 path exposes the guest frame with the opposite R/B\n    // memory order from desktop WSI. Compensate in the sampled image view.\n    switch (format) {\n    case Libraries::VideoOut::PixelFormat::A8B8G8R8Srgb:\n        return vk::Format::eB8G8R8A8Srgb;\n    case Libraries::VideoOut::PixelFormat::A8R8G8B8Srgb:\n        return vk::Format::eR8G8B8A8Srgb;\n    default:\n        break;\n    }\n#endif\n    switch (format) {'''
new = '''static vk::Format GetFrameViewFormat(const Libraries::VideoOut::PixelFormat format) {\n    switch (format) {'''
if old not in s:
    raise SystemExit('hardened GetFrameViewFormat override not found')
p.write_text(s.replace(old, new, 1))
PY

if [[ "$VARIANT" == "format-blankfix" ]]; then
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
fi

git apply --check "$PATCH_PATH"
git apply --index "$PATCH_PATH"
git add src/video_core/renderer_vulkan/vk_presenter.cpp
if [[ "$VARIANT" == "format-blankfix" ]]; then
  git add src/core/libraries/videoout/driver.cpp
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

# Verify the Android R/B override is actually gone while the parent mapping remains.
if grep -q "embedded X11 server's DRI3 path" src/video_core/renderer_vulkan/vk_presenter.cpp; then
  echo "Android GetFrameViewFormat override still present" >&2
  exit 23
fi
grep -A5 'static vk::Format GetFrameViewFormat' src/video_core/renderer_vulkan/vk_presenter.cpp | \
  grep -q 'eR8G8B8A8Srgb'

if [[ "$VARIANT" == "format-blankfix" ]]; then
  grep -q 'PrepareBlankFrame(true)' src/core/libraries/videoout/driver.cpp
else
  grep -q 'PrepareBlankFrame(false)' src/core/libraries/videoout/driver.cpp
fi

if grep -q 'LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");' \
    src/video_core/amdgpu/liverpool.cpp; then
  echo "Legacy IT_SET_PREDICATION stub still present" >&2
  exit 22
fi

echo "V20F $VARIANT ready for AArch64/FEX compilation"
git diff --cached --stat
