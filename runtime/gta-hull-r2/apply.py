#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
path = root / "src/shader_recompiler/ir/passes/hull_shader_transform.cpp"
text = path.read_text()

old = """                IR::Value voffset;
                bool success =
                    M_COMPOSITECONSTRUCTU32X3(MatchU32(0), MatchImm(voffset), MatchIgnore())
                        .Match(inst.Arg(IR::StoreBufferArgs::Address));
                ASSERT_MSG(success, "unhandled pattern in tess factor store");
"""

new = """                IR::Value index;
                IR::Value voffset;
                bool success =
                    M_COMPOSITECONSTRUCTU32X3(MatchU32(0), MatchImm(voffset), MatchIgnore())
                        .Match(inst.Arg(IR::StoreBufferArgs::Address));

                // The tess-factor SRD uses a zero element stride. When idxen is present,
                // the vector index therefore contributes 0 bytes to the effective address.
                // Some GTA V hull shaders keep that index dynamic instead of folding it to 0.
                // Accept that form while still requiring voffset to be immediate, so the
                // fixed SPIR-V tessellation builtin can be selected exactly as before.
                if (!success) {
                    success =
                        M_COMPOSITECONSTRUCTU32X3(MatchValue(index), MatchImm(voffset), MatchIgnore())
                            .Match(inst.Arg(IR::StoreBufferArgs::Address));
                }

                if (!success) {
                    IR::Value dynamic_voffset;
                    const bool dynamic_address =
                        M_COMPOSITECONSTRUCTU32X3(MatchValue(index), MatchValue(dynamic_voffset),
                                                  MatchIgnore())
                            .Match(inst.Arg(IR::StoreBufferArgs::Address));
                    ASSERT_MSG(!dynamic_address,
                               "GTA-HULL-R2: dynamic voffset in tess factor store");
                }
                ASSERT_MSG(success, "unhandled pattern in tess factor store");
"""

if old not in text:
    raise SystemExit("target matcher block not found; refusing fuzzy patch")

text = text.replace(old, new, 1)
path.write_text(text)
print(f"patched {path}")
