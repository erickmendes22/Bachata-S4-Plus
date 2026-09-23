// SPDX-License-Identifier: GPL-2.0-or-later
#include "bachata/order1886_patches.h"

// These includes intentionally name the public shadPS4-style interfaces the
// reconstructed runtime will expose. They are placeholders until the matching
// reconstructed headers are committed.
#include "shader_recompiler/info.h"
#include "shader_recompiler/resource.h"

namespace Bachata::Order1886 {

bool IsTargetTitle() {
    // EXPERIMENTAL SOURCE BOUNDARY:
    // Wire this to the reconstructed title-id service. The binary patches used
    // CUSA00785 gating. Do not use absolute global addresses.
    extern const char* BachataCurrentTitleId();
    const char* id = BachataCurrentTitleId();
    if (!id) {
        return false;
    }
    constexpr char kTitle[] = "CUSA00785";
    for (unsigned i = 0; i < sizeof(kTitle); ++i) {
        if (id[i] != kTitle[i]) {
            return false;
        }
        if (kTitle[i] == '\0') {
            return true;
        }
    }
    return true;
}

bool NeedsNullImagePath(const Shader::Info& info) {
    if (!IsTargetTitle()) {
        return false;
    }
    return info.pgm_hash == ShaderNullA || info.pgm_hash == ShaderNullB;
}

void ApplyShadowPushDataFix(const Shader::Info& info, Shader::PushData& push_data) {
    if (!IsTargetTitle() || info.pgm_hash != ShadowShader) {
        return;
    }
    push_data.ud_regs[1] = ShadowUd1Value;
}

} // namespace Bachata::Order1886
