#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=388cff5177f82e75a667d529212d34f3c255b7fc
PRED_COMMIT=3559530df5aec4067a95912af13ef14896b65ada
UPSTREAM_URL=https://github.com/shadps4-emu/shadPS4.git

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20D requires source commit $SOURCE_COMMIT; refusing an unreviewed merge." >&2
  exit 20
fi

git remote remove shadps4-upstream >/dev/null 2>&1 || true
git remote add shadps4-upstream "$UPSTREAM_URL"
git -c fetch.recurseSubmodules=false fetch --no-tags --no-recurse-submodules \
  shadps4-upstream "$PRED_COMMIT"

# Start a normal 3-way cherry-pick. If Git reports content conflicts, preserve the
# newer ARM64 file everywhere except the actual conflict blocks, where the incoming
# predication implementation wins. This avoids replacing whole renderer files.
set +e
git -c submodule.recurse=false cherry-pick --no-commit "$PRED_COMMIT"
rc=$?
set -e

if (( rc != 0 )); then
  mapfile -t conflicts < <(git diff --name-only --diff-filter=U)
  if (( ${#conflicts[@]} == 0 )); then
    echo "cherry-pick failed without merge conflicts" >&2
    git status --short >&2 || true
    exit 21
  fi

  printf 'V20D resolving conflict hunks in:\n'
  printf '  %s\n' "${conflicts[@]}"

  for f in "${conflicts[@]}"; do
    if git checkout --conflict=merge -- "$f" 2>/dev/null; then
      python3 - "$f" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
lines = p.read_text().splitlines(keepends=True)
out = []
i = 0
seen = 0
while i < len(lines):
    if lines[i].startswith('<<<<<<< '):
        seen += 1
        i += 1
        ours = []
        while i < len(lines) and not lines[i].startswith('======='):
            ours.append(lines[i]); i += 1
        if i >= len(lines):
            raise SystemExit(f'malformed conflict in {p}')
        i += 1
        theirs = []
        while i < len(lines) and not lines[i].startswith('>>>>>>> '):
            theirs.append(lines[i]); i += 1
        if i >= len(lines):
            raise SystemExit(f'malformed conflict in {p}')
        i += 1
        # Keep the newer ARM64 file outside conflicts; use predication only for
        # the overlapping hunk itself.
        out.extend(theirs)
    else:
        out.append(lines[i]); i += 1
if seen == 0:
    raise SystemExit(f'no conflict markers produced for {p}')
p.write_text(''.join(out))
print(f'{p}: resolved {seen} conflict hunk(s) with incoming predication side')
PY
      git add "$f"
    else
      # Fallback for non-content conflicts (unexpected add/add etc.).
      git checkout --theirs -- "$f"
      git add "$f"
    fi
  done
fi

if git diff --name-only --diff-filter=U | grep -q .; then
  echo "V20D still has unresolved conflicts:" >&2
  git diff --name-only --diff-filter=U >&2
  exit 22
fi

git diff --cached --check

# Real predication must be present.
test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -q 'EnableFromZpass' src/video_core/amdgpu/liverpool.cpp
grep -q 'RestorePredicatedIndexBase' src/video_core/amdgpu/liverpool.cpp
grep -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'copyQueryPoolResults' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'QueryType::eOcclusion' src/video_core/renderer_vulkan/vk_predication.cpp

# Keep the newer VideoOut/Presenter baseline which fixed the post-logo black screen.
grep -q 'PrepareBlankFrame(true)' src/core/libraries/videoout/driver.cpp
grep -q 'PrepareLastFrame' src/core/libraries/videoout/driver.cpp

if grep -q 'LOG_WARNING(Render, "Unimplemented IT_SET_PREDICATION");' \
    src/video_core/amdgpu/liverpool.cpp; then
  echo "Legacy IT_SET_PREDICATION stub still present" >&2
  exit 23
fi

echo 'V20D predication integrated while retaining newer ARM64 VideoOut/Presenter baseline.'
git status --short
git diff --cached --stat
