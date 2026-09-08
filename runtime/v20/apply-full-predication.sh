#!/usr/bin/env bash
set -euo pipefail

PATCH_COMMIT=3559530df5aec4067a95912af13ef14896b65ada
UPSTREAM_URL=https://github.com/shadps4-emu/shadPS4.git

git remote remove shadps4-upstream >/dev/null 2>&1 || true
git remote add shadps4-upstream "$UPSTREAM_URL"

git -c fetch.recurseSubmodules=false     fetch --no-tags --no-recurse-submodules     shadps4-upstream "$PATCH_COMMIT"

set +e
git -c submodule.recurse=false cherry-pick --no-commit "$PATCH_COMMIT"
rc=$?
set -e

if (( rc != 0 )); then
  echo "V20: cherry-pick conflicted; resolving known renderer conflicts with upstream predication side."

  conflicts="$(git diff --name-only --diff-filter=U || true)"
  printf '%s\n' "$conflicts"

  allowed_conflicts=(
    src/video_core/amdgpu/liverpool.cpp
    src/video_core/amdgpu/liverpool.h
    src/video_core/renderer_vulkan/vk_instance.cpp
    src/video_core/renderer_vulkan/vk_instance.h
    src/video_core/renderer_vulkan/vk_rasterizer.h
  )

  is_allowed() {
    local f="$1"
    local x
    for x in "${allowed_conflicts[@]}"; do
      [[ "$f" == "$x" ]] && return 0
    done
    return 1
  }

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if ! is_allowed "$f"; then
      echo "Unexpected conflict: $f" >&2
      exit 23
    fi

    # During cherry-pick: --theirs = predication commit version.
    git checkout --theirs -- "$f"
    git add "$f"
  done <<< "$conflicts"

  # Make sure all non-conflicting changes/new files from the commit remain staged.
  git add CMakeLists.txt           src/video_core/amdgpu/pm4_cmds.h           src/video_core/host_shaders/CMakeLists.txt           src/video_core/host_shaders/occlusion_predicate.comp           src/video_core/renderer_vulkan/vk_predication.cpp           src/video_core/renderer_vulkan/vk_predication.h           src/video_core/renderer_vulkan/vk_rasterizer.cpp || true
fi

if git diff --name-only --diff-filter=U | grep -q .; then
  echo "Unresolved V20 conflicts remain:" >&2
  git diff --name-only --diff-filter=U >&2
  exit 24
fi

# Hard verification.
test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -R -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan
grep -R -q 'copyQueryPoolResults' src/video_core/renderer_vulkan
grep -R -q 'QueryType::eOcclusion' src/video_core/renderer_vulkan
grep -q 'EnableFromZpass' src/video_core/amdgpu/liverpool.cpp
grep -q 'RestorePredicatedIndexBase' src/video_core/amdgpu/liverpool.cpp

if grep -q 'LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");'      src/video_core/amdgpu/liverpool.cpp; then
  echo "Legacy SET_PREDICATION implementation remains." >&2
  exit 25
fi

echo "V20 real predication port staged successfully."
git status --short
