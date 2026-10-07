#!/usr/bin/env python3
from pathlib import Path

p = Path("src/shader_recompiler/ir/passes/hull_shader_transform.cpp")
s = p.read_text()

start = s.index("            case IR::Opcode::StoreBufferU32:")
end = s.index("            case IR::Opcode::WriteSharedU32:", start)

block = r'''            case IR::Opcode::StoreBufferU32:
            case IR::Opcode::StoreBufferU32x2:
            case IR::Opcode::StoreBufferU32x3:
            case IR::Opcode::StoreBufferU32x4: {
                IR::Value soffset = IR::GetBufferSOffsetArg(&inst);
                if (!M_GETATTRIBUTEU32(MatchAttribute(IR::Attribute::TessFactorsBufferBase),
                                       MatchIgnore())
                         .Match(soffset)) {
                    break;
                }

                const auto inst_info = inst.Flags<IR::BufferInstInfo>();
                IR::IREmitter ir{*block, IR::Block::InstructionList::s_iterator_to(inst)};

                IR::U32 voffset;
                bool success =
                    M_COMPOSITECONSTRUCTU32X3(MatchU32(0), MatchValue(voffset), MatchIgnore())
                        .Match(inst.Arg(IR::StoreBufferArgs::Address));
                ASSERT_MSG(success, "unhandled pattern in tess factor store");

                const u32 num_dwords = u32(opcode) - u32(IR::Opcode::StoreBufferU32) + 1;
                const IR::Value data = inst.Arg(IR::StoreBufferArgs::Data);

                const auto GetValue = [&](IR::Value value) -> IR::F32 {
                    if (auto* value_inst = value.TryInstRecursive();
                        value_inst && value_inst->GetOpcode() == IR::Opcode::BitCastU32F32) {
                        return IR::F32{value_inst->Arg(0)};
                    }
                    return ir.BitCast<IR::F32, IR::U32>(IR::U32{value});
                };

                const IR::U32 factor_offset{
                    ir.IAdd(voffset, ir.Imm32(static_cast<u32>(inst_info.inst_offset.Value())))};
                const IR::U32 factor_index(ir.ShiftRightLogical(factor_offset, ir.Imm32(2u)));

                inst.Invalidate();
                if (num_dwords == 1) {
                    ir.SetTessFactor(GetValue(data), factor_index);
                    break;
                }

                auto* data_inst = data.TryInstRecursive();
                ASSERT(data_inst &&
                       (data_inst->GetOpcode() == IR::Opcode::CompositeConstructU32x2 ||
                        data_inst->GetOpcode() == IR::Opcode::CompositeConstructU32x3 ||
                        data_inst->GetOpcode() == IR::Opcode::CompositeConstructU32x4));
                for (u32 i = 0; i < num_dwords; i++) {
                    IR::U32 component_idx{ir.IAdd(factor_index, ir.Imm32(i))};
                    ir.SetTessFactor(GetValue(data_inst->Arg(i)), component_idx);
                }
                break;
            }

'''

p.write_text(s[:start] + block + s[end:])

for reject in Path("src").rglob("*.rej"):
    reject.unlink()

s = p.read_text()
required = ["MatchValue(voffset)", "SetTessFactor", "struct PhiInfo", "seq_num"]
for token in required:
    if token not in s:
        raise SystemExit(f"missing required token: {token}")
if "std::set<IR::Inst*> phis" in s:
    raise SystemExit("later PR Phi simplification detected")

# trigger build
