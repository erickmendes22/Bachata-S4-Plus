// SPDX-FileCopyrightText: Copyright 2026 shadPS4 Emulator Project
// SPDX-License-Identifier: GPL-2.0-or-later
//
// Adapted for the Bachata S4+ reverse-source reconstruction.
// Architectural reference: shadPS4 commit 7db6e4ba56b98841624ab776aaa56763f10bdc89.

#include "bachata/per_vertex_aux_gs.h"

#include <sirit/sirit.h>
#include "shader_recompiler/info.h"
#include "shader_recompiler/profile.h"
#include "shader_recompiler/runtime_info.h"

namespace Bachata::PerVertexFallback {

using Sirit::Id;

namespace {
constexpr std::uint32_t Spirv15 = 0x00010500;

class AuxEmitter final : public Sirit::Module {
public:
    AuxEmitter(const Shader::Profile& profile_, const Shader::Info& info_,
               const Shader::RuntimeInfo& runtime_)
        : Sirit::Module{Spirv15}, profile{profile_}, info{info_}, runtime{runtime_},
          fs{runtime_.fs_info}, locations{ComputeLocations(profile_, info_, runtime_)} {
        void_id = TypeVoid();
        float_id = TypeFloat(32);
        uint_id = TypeUInt(32);
        int_id = TypeInt(32, true);
        vec2_id = TypeVector(float_id, 2);
        vec4_id = TypeVector(float_id, 4);

        const Id float_arr = TypeArray(float_id, Constant(uint_id, 1));
        gl_per_vertex_type = TypeStruct(vec4_id, float_id, float_arr, float_arr);
        Decorate(gl_per_vertex_type, spv::Decoration::Block);
        MemberDecorate(gl_per_vertex_type, 0, spv::Decoration::BuiltIn,
                       static_cast<std::uint32_t>(spv::BuiltIn::Position));
        MemberDecorate(gl_per_vertex_type, 1, spv::Decoration::BuiltIn,
                       static_cast<std::uint32_t>(spv::BuiltIn::PointSize));
        MemberDecorate(gl_per_vertex_type, 2, spv::Decoration::BuiltIn,
                       static_cast<std::uint32_t>(spv::BuiltIn::ClipDistance));
        MemberDecorate(gl_per_vertex_type, 3, spv::Decoration::BuiltIn,
                       static_cast<std::uint32_t>(spv::BuiltIn::CullDistance));

        has_clip = fs.clip_distance_emulation;
        num_inputs = fs.num_inputs - (has_clip ? 1u : 0u);
        for (std::uint32_t i = 0; i < num_inputs; ++i) {
            if (!fs.inputs[i].IsDefault()) {
                input_slots.push_back(i);
                per_vertex[i] =
                    info.fs_interpolation[i].primary == Shader::Qualifier::PerVertex;
            }
        }
        has_bary_coord = fs.addr_flags.persp_center_ena != 0;
    }

    void Emit() {
        AddCapability(spv::Capability::Shader);
        AddCapability(spv::Capability::Geometry);
        const Id fn_type = TypeFunction(void_id);
        main = OpFunction(void_id, spv::FunctionControlMask::MaskNone, fn_type);
        AddExecutionMode(main, spv::ExecutionMode::Triangles);
        AddExecutionMode(main, spv::ExecutionMode::OutputTriangleStrip);
        AddExecutionMode(main, spv::ExecutionMode::OutputVertices, 3);
        AddExecutionMode(main, spv::ExecutionMode::Invocations, 1);

        DefineInputs();
        DefineOutputs();
        AddEntryPoint(spv::ExecutionModel::Geometry, main, "main", interfaces);
        AddLabel(OpLabel());
        EmitMain();
    }

private:
    Id Int(std::int32_t v) { return Constant(int_id, v); }

    Id AddInput(Id type) {
        const Id id = AddGlobalVariable(TypePointer(spv::StorageClass::Input, type),
                                        spv::StorageClass::Input);
        interfaces.push_back(id);
        return id;
    }

    Id AddOutput(Id type) {
        const Id id = AddGlobalVariable(TypePointer(spv::StorageClass::Output, type),
                                        spv::StorageClass::Output);
        interfaces.push_back(id);
        return id;
    }

    void DefineInputs() {
        gl_in = AddInput(TypeArray(gl_per_vertex_type, Constant(uint_id, 3)));
        const Id input_arr = TypeArray(vec4_id, Constant(uint_id, 3));
        for (std::uint32_t slot : input_slots) {
            const Id id = AddInput(input_arr);
            Decorate(id, spv::Decoration::Location,
                     fs.inputs[slot].param_index + (has_clip ? 1u : 0u));
            input_ids.push_back(id);
        }
    }

    void DefineOutputs() {
        gl_out = AddOutput(gl_per_vertex_type);
        output_ids.resize(input_slots.size());
        pv_output_ids.resize(input_slots.size());

        for (std::size_t k = 0; k < input_slots.size(); ++k) {
            const std::uint32_t slot = input_slots[k];
            const std::uint32_t loc = locations.slot_loc[slot];
            if (per_vertex[slot]) {
                for (std::uint32_t v = 0; v < 3; ++v) {
                    const Id id = AddOutput(vec4_id);
                    Decorate(id, spv::Decoration::Location, loc + v);
                    Decorate(id, spv::Decoration::Flat);
                    pv_output_ids[k][v] = id;
                }
            } else {
                const Id id = AddOutput(vec4_id);
                Decorate(id, spv::Decoration::Location, loc);
                output_ids[k] = id;
            }
        }

        if (has_bary_coord) {
            bary_coord = AddOutput(vec2_id);
            Decorate(bary_coord, spv::Decoration::Location, locations.bary_coord_loc);
        }
    }

    void EmitMain() {
        const Id input_vec4 = TypePointer(spv::StorageClass::Input, vec4_id);
        const Id output_vec4 = TypePointer(spv::StorageClass::Output, vec4_id);

        std::array<Id, 3> positions;
        for (int v = 0; v < 3; ++v) {
            positions[v] =
                OpLoad(vec4_id, OpAccessChain(input_vec4, gl_in, Int(v), Int(0)));
        }

        std::vector<std::array<Id, 3>> attrs(input_slots.size());
        for (std::size_t k = 0; k < input_slots.size(); ++k) {
            for (int v = 0; v < 3; ++v) {
                attrs[k][v] =
                    OpLoad(vec4_id, OpAccessChain(input_vec4, input_ids[k], Int(v)));
            }
        }

        std::array<Id, 3> bary{};
        if (has_bary_coord) {
            bary[0] = ConstantComposite(vec2_id, Constant(float_id, 0.0f),
                                       Constant(float_id, 0.0f));
            bary[1] = ConstantComposite(vec2_id, Constant(float_id, 1.0f),
                                       Constant(float_id, 0.0f));
            bary[2] = ConstantComposite(vec2_id, Constant(float_id, 0.0f),
                                       Constant(float_id, 1.0f));
        }

        for (int v = 0; v < 3; ++v) {
            OpStore(OpAccessChain(output_vec4, gl_out, Int(0)), positions[v]);
            for (std::size_t k = 0; k < input_slots.size(); ++k) {
                const auto slot = input_slots[k];
                if (per_vertex[slot]) {
                    for (int p = 0; p < 3; ++p) {
                        OpStore(pv_output_ids[k][p], attrs[k][p]);
                    }
                } else {
                    OpStore(output_ids[k], attrs[k][v]);
                }
            }
            if (has_bary_coord) {
                OpStore(bary_coord, bary[v]);
            }
            OpEmitVertex();
        }

        OpEndPrimitive();
        OpReturn();
        OpFunctionEnd();
    }

    const Shader::Profile& profile;
    const Shader::Info& info;
    const Shader::RuntimeInfo& runtime;
    const Shader::FragmentRuntimeInfo& fs;
    Locations locations{};

    bool has_clip{};
    std::uint32_t num_inputs{};
    bool has_bary_coord{};
    std::vector<std::uint32_t> input_slots;
    std::array<bool, 32> per_vertex{};
    std::vector<Id> input_ids;
    std::vector<Id> output_ids;
    std::vector<std::array<Id, 3>> pv_output_ids;
    std::vector<Id> interfaces;

    Id main{};
    Id void_id{};
    Id float_id{};
    Id uint_id{};
    Id int_id{};
    Id vec2_id{};
    Id vec4_id{};
    Id gl_per_vertex_type{};
    Id gl_in{};
    Id gl_out{};
    Id bary_coord{};
};
} // namespace

std::uint32_t UnsupportedBarycentricMask(const Shader::RuntimeInfo& runtime_info) {
    const auto& af = runtime_info.fs_info.addr_flags;
    std::uint32_t mask = 0;
    if (af.persp_sample_ena) mask |= 1u << 0;
    if (af.persp_centroid_ena) mask |= 1u << 1;
    if (af.persp_pull_model_ena) mask |= 1u << 2;
    if (af.linear_sample_ena) mask |= 1u << 3;
    if (af.linear_center_ena) mask |= 1u << 4;
    if (af.linear_centroid_ena) mask |= 1u << 5;
    return mask;
}

bool CanExpand(const Shader::Profile& profile, const Shader::RuntimeInfo& runtime_info) {
    const auto& fs = runtime_info.fs_info;
    return fs.is_vs_direct &&
           fs.prim_type == AmdGpu::PrimitiveType::TriangleList &&
           !profile.supports_amd_shader_explicit_vertex_parameter &&
           !profile.supports_fragment_shader_barycentric &&
           UnsupportedBarycentricMask(runtime_info) == 0 &&
           !fs.clip_distance_emulation;
}

bool NeedsAuxGS(const Shader::Profile& profile, const Shader::Info& info,
                const Shader::RuntimeInfo& runtime_info) {
    if (!CanExpand(profile, runtime_info)) return false;
    const auto& fs = runtime_info.fs_info;
    if (fs.addr_flags.persp_center_ena) return true;
    for (std::uint32_t i = 0; i < fs.num_inputs; ++i) {
        if (info.fs_interpolation[i].primary == Shader::Qualifier::PerVertex) return true;
    }
    return false;
}

Locations ComputeLocations(const Shader::Profile& profile, const Shader::Info& info,
                           const Shader::RuntimeInfo& runtime_info) {
    Locations out{};
    const auto& fs = runtime_info.fs_info;
    const bool expand = CanExpand(profile, runtime_info);
    const bool has_clip = fs.clip_distance_emulation;
    const std::uint32_t count = fs.num_inputs - (has_clip ? 1u : 0u);
    std::uint32_t loc = has_clip ? 1u : 0u;

    for (std::uint32_t i = 0; i < count; ++i) {
        if (fs.inputs[i].IsDefault()) continue;
        out.slot_loc[i] = loc;
        const bool pv = info.fs_interpolation[i].primary == Shader::Qualifier::PerVertex;
        loc += pv && expand ? 3u : 1u;
    }
    out.bary_coord_loc = loc;
    return out;
}

std::vector<std::uint32_t> EmitAuxGS(const Shader::Profile& profile, const Shader::Info& info,
                                     const Shader::RuntimeInfo& runtime_info) {
    AuxEmitter emitter{profile, info, runtime_info};
    emitter.Emit();
    return emitter.Assemble();
}

} // namespace Bachata::PerVertexFallback
