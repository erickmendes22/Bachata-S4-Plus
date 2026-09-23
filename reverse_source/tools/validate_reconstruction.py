#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]

required = {
    "src/per_vertex_aux_gs.cpp": [
        "OutputVertices, 3",
        "spv::Decoration::Flat",
        "bary_coord",
        "UnsupportedBarycentricMask",
        "AmdGpu::PrimitiveType::TriangleList",
    ],
    "src/per_vertex_integration.cpp": [
        "supports_amd_shader_explicit_vertex_parameter",
        "supports_fragment_shader_barycentric",
        "CanExpand(profile, runtime_info)",
    ],
    "src/fragment_input_layout.cpp": [
        "location_count = slot.per_vertex && expand ? 3u : 1u",
        "bary_coord_location",
    ],
    "src/pipeline_aux_gs.cpp": [
        "has_real_geometry_shader",
        "NeedsAuxGS(profile, info, runtime_info)",
        "out.inject = true",
    ],
    "src/order1886_patches.cpp": [
        "ShaderNullA",
        "ShaderNullB",
        "ShadowUd1Value",
    ],
    "src/srt_duplicate_table.cpp": [
        "RecordReplacement",
        "PropagateFlags",
    ],
}

errors = []
for rel, needles in required.items():
    p = root / rel
    if not p.exists():
        errors.append(f"missing {rel}")
        continue
    text = p.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"{rel}: missing invariant: {needle}")

# Explicitly prevent two historical dead ends from silently returning.
all_cpp = "\n".join(p.read_text(encoding="utf-8") for p in root.glob("src/*.cpp"))
for forbidden in [
    "Flat -> Smooth",
    "readbacksMode=2",
    "directMemoryAccess=true",
]:
    if forbidden in all_cpp:
        errors.append(f"historical discarded experiment reintroduced: {forbidden}")

if errors:
    print("reverse-source audit FAILED")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("reverse-source audit OK")
print("validated invariants:", sum(len(v) for v in required.values()))
