#!/usr/bin/env bash
set -euo pipefail

SOURCE_COMMIT=be6bc2e9c60799e071dd2fafa6216e8d80ec619c
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
PATCH_PATH="$SCRIPT_DIR/../v20/full-predication-arm64.patch"
VARIANT="${V20H_VARIANT:-zpass-failopen}"

if [[ "$(git rev-parse HEAD)" != "$SOURCE_COMMIT" ]]; then
  echo "V20H requires hardened buildable source $SOURCE_COMMIT" >&2
  exit 20
fi

test -f "$PATCH_PATH"

echo "V20H variant=$VARIANT source=$SOURCE_COMMIT"

case "$VARIANT" in
  zpass-failopen|legacy-pixelstats) ;;
  *) echo "Unknown V20H_VARIANT=$VARIANT" >&2; exit 21 ;;
esac

# Start from the already reviewed/compiled real predication port.
git apply --check "$PATCH_PATH"
git apply --index "$PATCH_PATH"

if [[ "$VARIANT" == "zpass-failopen" ]]; then
python3 - <<'PY'
from pathlib import Path
p = Path('src/video_core/amdgpu/liverpool.cpp')
s = p.read_text()
old = '''                case PredicationOp::Zpass:\n                    predication->EnableFromZpass(set_pred->Address(), num_counter_pairs,\n                                                 draw_visible, combine);\n                    break;'''
new = '''                case PredicationOp::Zpass:\n                    // V20H diagnostic: keep the real predication implementation for BOOL32/64,\n                    // but fail-open ZPASS so an unresolved GPU occlusion query cannot deadlock\n                    // guest-visible synchronization.\n                    LOG_WARNING(Render, "V20H ZPASS fail-open addr={:#x}", set_pred->Address());\n                    predication->Disable();\n                    break;'''
if old not in s:
    raise SystemExit('V20H: ZPASS predication block not found')
p.write_text(s.replace(old, new, 1))
PY
  git add src/video_core/amdgpu/liverpool.cpp
fi

if [[ "$VARIANT" == "legacy-pixelstats" ]]; then
python3 - <<'PY'
from pathlib import Path

# Restore the synthetic monotonically-changing pixel counter retained by the
# hardened pre-predication core. Keep all new predication state alongside it.
h = Path('src/video_core/amdgpu/liverpool.h')
s = h.read_text()
old = '''    bool packet_predicated{};\n    std::optional<std::pair<u32, u32>> saved_index_base{};'''
new = '''    // V20H: immediate guest-visible pixel-pipe writeback counter.\n    u64 pixel_counter{};\n    bool packet_predicated{};\n    std::optional<std::pair<u32, u32>> saved_index_base{};'''
if old not in s:
    raise SystemExit('V20H: Liverpool predication state block not found')
h.write_text(s.replace(old, new, 1))

p = Path('src/video_core/amdgpu/liverpool.cpp')
s = p.read_text()
old = '''                    const VAddr address = event->Address<VAddr>();\n                    if (predication) {\n                        predication->DumpZpassCounters(address, num_counter_pairs);\n                    } else {\n                        static constexpr u64 OcclusionCounterValidMask = 0x8000000000000000ULL;\n                        const u64 counter = OcclusionCounterValidMask;\n                        auto* memory = Core::Memory::Instance();\n                        const u64 result_size = u64(num_counter_pairs) * sizeof(u64) * 2;\n                        if (!memory->IsValidMapping(address, result_size)) {\n                            LOG_WARNING(Render,\n                                        "Pixel-pipe stats writeback address is invalid: {:#x}",\n                                        address);\n                            break;\n                        }\n                        for (u32 i = 0; i < num_counter_pairs; ++i) {\n                            auto* dst = reinterpret_cast<void*>(address + i * sizeof(u64) * 2);\n                            if (!memory->TryWriteBacking(dst, &counter, sizeof(counter))) {\n                                std::memcpy(dst, &counter, sizeof(counter));\n                            }\n                        }\n                    }'''
new = '''                    const VAddr address = event->Address<VAddr>();\n                    // V20H diagnostic: restore the old immediate synthetic ZPASS result.\n                    // GoW3 waits on guest memory with IT_WAIT_REG_MEM; asynchronous query\n                    // completion here can leave that memory equal to REF indefinitely.\n                    static constexpr u64 OcclusionCounterValidMask = 0x8000000000000000ULL;\n                    static constexpr u64 OcclusionCounterStep = 0x2FFFFFFULL;\n                    const u64 counter = pixel_counter | OcclusionCounterValidMask;\n                    auto* memory = Core::Memory::Instance();\n                    const u64 result_size = u64(num_counter_pairs) * sizeof(u64) * 2;\n                    if (!memory->IsValidMapping(address, result_size)) {\n                        LOG_WARNING(Render,\n                                    "V20H legacy pixel-stats address invalid: {:#x}", address);\n                        break;\n                    }\n                    for (u32 i = 0; i < num_counter_pairs; ++i) {\n                        auto* dst = reinterpret_cast<void*>(address + i * sizeof(u64) * 2);\n                        if (!memory->TryWriteBacking(dst, &counter, sizeof(counter))) {\n                            std::memcpy(dst, &counter, sizeof(counter));\n                        }\n                    }\n                    pixel_counter += OcclusionCounterStep;'''
if old not in s:
    raise SystemExit('V20H: patched PixelPipeStatDump block not found')
p.write_text(s.replace(old, new, 1))
PY
  git add src/video_core/amdgpu/liverpool.cpp src/video_core/amdgpu/liverpool.h
fi

git diff --cached --check

# Hard verification common to both variants.
test -f src/video_core/renderer_vulkan/vk_predication.cpp
test -f src/video_core/renderer_vulkan/vk_predication.h
test -f src/video_core/host_shaders/occlusion_predicate.comp
grep -q 'beginConditionalRenderingEXT' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'copyQueryPoolResults' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'QueryType::eOcclusion' src/video_core/renderer_vulkan/vk_predication.cpp
grep -q 'EnableFromZpass' src/video_core/renderer_vulkan/vk_predication.cpp
for method in IsGpuThread InGfxTask EnqueueCommand; do
  grep -q "$method" src/video_core/amdgpu/liverpool.h
done
test -f runtime/scripts/build-shadps4-arm64.sh
test -f runtime/scripts/install-debian-runtime-deps.sh

if [[ "$VARIANT" == "zpass-failopen" ]]; then
  grep -q 'V20H ZPASS fail-open' src/video_core/amdgpu/liverpool.cpp
  if grep -A4 'case PredicationOp::Zpass' src/video_core/amdgpu/liverpool.cpp | grep -q 'EnableFromZpass'; then
    echo "V20H: ZPASS still enables GPU-side predicate" >&2
    exit 23
  fi
else
  grep -q 'u64 pixel_counter{}' src/video_core/amdgpu/liverpool.h
  grep -q 'V20H diagnostic: restore the old immediate synthetic ZPASS result' src/video_core/amdgpu/liverpool.cpp
  grep -q 'pixel_counter += OcclusionCounterStep' src/video_core/amdgpu/liverpool.cpp
fi

echo "V20H $VARIANT ready for AArch64/FEX compilation"
git diff --cached --stat
