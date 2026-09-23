// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>

namespace Shader {
struct Info;
struct PushData;
}

namespace Bachata::Order1886 {

constexpr std::uint64_t ShaderNullA = 0xa7b66f58ULL;
constexpr std::uint64_t ShaderNullB = 0xefaaab2bULL;
constexpr std::uint64_t ShadowShader = 0x9846aaffULL;
constexpr std::uint32_t ShadowUd1Value = 0x7F80000FU;

bool IsTargetTitle();
bool NeedsNullImagePath(const Shader::Info& info);
void ApplyShadowPushDataFix(const Shader::Info& info, Shader::PushData& push_data);

} // namespace Bachata::Order1886
