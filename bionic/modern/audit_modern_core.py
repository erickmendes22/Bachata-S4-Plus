#!/usr/bin/env python3
"""Read-only audit of a newer ARM64/FEX shadPS4 tree against Bachata Bionic.

No speculative modifications and no APK. Reports which old, exact-string
port anchors still exist, without treating an old overlay as an upgraded core.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

CHECKS = {
    "upstream_0211": ("CMakeLists.txt", 'set(EMULATOR_VERSION_MINOR "21")'),
    "upstream_patch_1": ("CMakeLists.txt", 'set(EMULATOR_VERSION_PATCH "1")'),
    "fex_guest_cpu": ("src/core/guest_cpu/fex_guest_cpu.cpp", "FexGuestCpuBackend"),
    "fex_guest_engine": ("src/core/fex/fex_guest_engine.cpp", "GuestEngine"),
    "guest_hle_bridge": ("src/core/guest_cpu/fex_hle_bridge.cpp", "HleGuestBridge"),
    "android_runtime_cli": ("src/main.cpp", "--bachata-socket"),
    "android_storage_root": ("src/main.cpp", "--bachata-storage-root"),
    "android_saf_socket": ("src/main.cpp", "--bachata-saf-socket"),
    "android_saf_token": ("src/main.cpp", "--bachata-saf-token"),
    "saf_mount": ("src/emulator.cpp", "MountSaf"),
    "fex_guest_signals": ("src/core/fex/fex_guest_engine.cpp", "DeliverGuestOrbisSignal"),
    "shader_recompiler": ("src/shader_recompiler", None),
    "vulkan_renderer": ("src/video_core/renderer_vulkan/vk_rasterizer.cpp", "Rasterizer"),
}

def string_expr(node):
    try:
        value = ast.literal_eval(node)
        return value if isinstance(value, str) else None
    except (ValueError, TypeError, SyntaxError, RecursionError):
        return None

def audit(source: Path, overlay: Path) -> dict:
    values = {}
    for name, (path, marker) in CHECKS.items():
        file = source / path
        values[name] = file.exists() and (
            marker is None or (file.is_file() and marker in file.read_text(errors="replace"))
        )
    old_code = overlay.read_text()
    tree = ast.parse(old_code)
    direct = 0
    compatible = []
    incompatible = []
    unavailable = []
    variables = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            if not isinstance(node.targets[0], ast.Name):
                continue
            var = node.targets[0].id
            expr = node.value
            if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
                if isinstance(expr.left, ast.Name) and expr.left.id == "upstream":
                    path = string_expr(expr.right)
                    if path:
                        variables[var] = path
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "replace" and len(node.args) >= 3):
            continue
        destination = node.args[0]
        path = variables.get(destination.id) if isinstance(destination, ast.Name) else None
        if path is None and isinstance(destination, ast.BinOp) and isinstance(destination.op, ast.Div):
            if isinstance(destination.left, ast.Name) and destination.left.id == "upstream":
                path = string_expr(destination.right)
        needle = string_expr(node.args[1])
        if path is None or needle is None:
            unavailable.append({"line": node.lineno, "path": path, "static": needle is not None})
            continue
        direct += 1
        dest = source / path
        if not dest.is_file():
            incompatible.append({"line": node.lineno, "file": path, "reason": "file missing"})
        else:
            count = dest.read_text(errors="replace").count(needle)
            if count == 1:
                compatible.append({"line": node.lineno, "file": path})
            else:
                incompatible.append({"line": node.lineno, "file": path,
                                    "reason": f"anchor occurrences={count}"})
    return {
        "target": "shadPS4 0.21.1 ARM64/FEX source",
        "checklist": values,
        "exact_legacy_anchors": {
            "count": direct,
            "matching": len(compatible),
            "different": len(incompatible),
            "dynamic_or_unchecked": len(unavailable),
            "not_yet_migrated": incompatible,
        },
        "invariant": "Source compatibility only; no Bionic core has been compiled yet."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--legacy-overlay", type=Path, required=True)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()
    result = audit(args.source, args.legacy_overlay)
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2))
    if args.markdown:
        summary = result["exact_legacy_anchors"]
        print("**Source:** shadPS4 0.21.1 ARM64/FEX (not the old 0.16.1).")
        print(f"**Static integration anchors:** {summary['matching']} intact, "
              f"{summary['different']} different, "
              f"{summary['dynamic_or_unchecked']} require manual review.")
        for key, okay in result["checklist"].items():
            print(f"- {'PASS' if okay else 'FAIL'}: {key}")
    else:
        print(json.dumps(result, indent=2))
    # Missing FEX/SAF or wrong target version blocks even a source-only port.
    required = ("upstream_0211", "upstream_patch_1", "fex_guest_cpu",
                "fex_guest_engine", "guest_hle_bridge",
                "android_runtime_cli", "android_saf_socket", "android_saf_token")
    if not all(result["checklist"][k] for k in required):
        raise SystemExit("The candidate 0.21.1 tree is missing required ARM64/FEX/Bachata elements")

if __name__ == "__main__":
    main()
