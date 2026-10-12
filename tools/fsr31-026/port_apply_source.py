#!/usr/bin/env python3
"""Inject the port's REAL guest-rasterizer scene predicates in shadPS4 source.

Source integration only; does NOT overwrite the stripped existing ARM64 binary
or attempt pre-HUD framebuffer blits. This intentionally fails on source drift.
Requires a source-level build to become active in the emulator.
"""
from pathlib import Path
import shutil
import sys

project = Path(sys.argv[1]).resolve()
package = Path(__file__).resolve().parent
raster = project / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
header = project / "src/video_core/renderer_vulkan/vk_rasterizer.h"
assert raster.is_file() and header.is_file()
src = raster.read_text()
hdr = header.read_text()
for filename in ("port_camera_state.h", "port_rasterizer_scene.h"):
    shutil.copyfile(package / filename, raster.parent / filename)

def replace_once(value: str, before: str, after: str) -> str:
    count = value.count(before)
    if count != 1:
        raise RuntimeError(f"Source mismatch (expected 1, got {count}): {before[:90]!r}")
    return value.replace(before, after)

hdr = replace_once(hdr, '#include "common/recursive_lock.h"',
    '#include "common/recursive_lock.h"\n'
    '#include "video_core/renderer_vulkan/port_camera_state.h"\n'
    '#include "video_core/renderer_vulkan/port_rasterizer_scene.h"')
hdr = replace_once(hdr, "    bool attachment_feedback_loop{};",
    "    bool attachment_feedback_loop{};\n"
    "    Bachata::Fsr31::PortCameraState fsr31PortCamera{};\n"
    "    Bachata::Fsr31::RasterizerSceneStage fsr31PortStage{};")

src = replace_once(src,
    '#include "video_core/renderer_vulkan/vk_rasterizer.h"',
    '#include "video_core/renderer_vulkan/vk_rasterizer.h"\n'
    '#include <cstdlib>\n#include <cstdio>')

body = r'''
    // Bloodborne port: classify draws from guest GPU registers, guest shader
    // hashes and the *real* camera-depth target. Never guess from the Vulkan
    // render area or copy into the guest output framebuffer.
    static const bool port_enabled = [] {
        const char* mode = std::getenv("BACHATA_FSR31_MODE");
        return mode && mode[0]>='0' && mode[0]<='4' && mode[1]==0;
    }();
    if (port_enabled && cb_descs[0].first) {
        const auto& color = texture_cache.GetImage(cb_descs[0].first);
        const auto& cs = color.info.size;
        const auto& key = pipeline->GetGraphicsKey();
        const unsigned mrt = std::popcount(key.mrt_mask);
        const auto& depth_id = db_desc.first;
        Bachata::Fsr31::DrawState d{};
        d.colorId = cb_descs[0].first.index;
        d.depthId = depth_id ? depth_id.index : 0;
        d.colorWidth = cs.width;
        d.colorHeight = cs.height;
        d.vertexShaderHash = pipeline->GetStage(Shader::LogicalStage::Vertex).pgm_hash;
        d.mrtMask = key.mrt_mask;
        switch (color.info.pixel_format) {
        case vk::Format::eR16G16B16A16Sfloat:
            d.colorFormat = Bachata::Fsr31::Format::RGBA16F;
            break;
        case vk::Format::eR8G8B8A8Unorm:
            d.colorFormat = Bachata::Fsr31::Format::RGBA8UNorm;
            break;
        case vk::Format::eR8G8B8A8Srgb:
            d.colorFormat = Bachata::Fsr31::Format::RGBA8SRgb;
            break;
        default: break;
        }
        if (depth_id) {
            const auto& depth = texture_cache.GetImage(depth_id).info;
            d.depthWidth = depth.size.width;
            d.depthHeight = depth.size.height;
        }
        if (mrt >= 5 && d.depthId) {
            const auto& vp = regs.viewports[0];
            fsr31PortCamera.OnGBuffer(d.depthId,
                    vp.xscale < 0.f ? -1.f : 1.f,
                    vp.yscale < 0.f ? -1.f : 1.f);
        }
        d.cameraConstantsValid = (mrt >= 5 && d.depthId) ||
                                 fsr31PortCamera.HasCameraForDepth(d.depthId);
        const auto event = fsr31PortStage.Observe(d);
        // The port performs the temporal dispatch BEFORE this known
        // UI shader's draw and redirects it to a separately allocated UI
        // surface. That redirect still needs a verified Renderer integration;
        // do not inject a Vulkan blit here.
        if (event == Bachata::Fsr31::Event::BeginHUD)
            fsr31PortCamera.OnDisplayFrame();
    }
'''
src = replace_once(src,
    "    } else {\n        db_desc.first = {};\n    }\n}\n\nstatic std::pair<u32, u32> GetDrawOffsets(",
    "    } else {\n        db_desc.first = {};\n    }\n" + body +
    "}\n\nstatic std::pair<u32, u32> GetDrawOffsets(")

cam = r'''
            // Bloodborne port: inspect actual 864-byte guest camera buffer
            // on each GBuffer pass. Do not reuse stale matrices across frames.
            // MemoryManager already bounded the mapped guest range.
            if (!desc.is_written && size >= 216 * sizeof(float) &&
                (vsharp.base_address & 3) == 0) {
                fsr31PortCamera.OnConstants(
                    reinterpret_cast<const float*>(vsharp.base_address),216);
            }
'''
src = replace_once(src,
    "            const u64 size = memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize());\n"
    "            const auto buffer_id = buffer_cache.FindBuffer(vsharp.base_address, size);",
    "            const u64 size = memory->ClampRangeSize(vsharp.base_address, vsharp.GetSize());\n" +
    cam +
    "            const auto buffer_id = buffer_cache.FindBuffer(vsharp.base_address, size);")

header.write_text(hdr)
raster.write_text(src)
print("Port scene classifier + camera signatures connected to source Rasterizer;",
      "the existing core024 executable is unchanged.")
