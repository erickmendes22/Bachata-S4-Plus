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
presenter = project / "src/video_core/renderer_vulkan/vk_presenter.cpp"
assert raster.is_file() and header.is_file() and presenter.is_file()
src = raster.read_text()
hdr = header.read_text()
pres = presenter.read_text()
for filename in ("port_camera_state.h", "port_rasterizer_scene.h", "port_ui_surface.h"):
    shutil.copyfile(package / filename, raster.parent / filename)

def replace_once(value: str, before: str, after: str) -> str:
    count = value.count(before)
    if count != 1:
        raise RuntimeError(f"Source mismatch (expected 1, got {count}): {before[:90]!r}")
    return value.replace(before, after)

hdr = replace_once(hdr, '#include "common/recursive_lock.h"',
    '#include "common/recursive_lock.h"\n'
    '#include "video_core/renderer_vulkan/port_camera_state.h"\n'
    '#include "video_core/renderer_vulkan/port_rasterizer_scene.h"\n'
    '#include "video_core/renderer_vulkan/port_ui_surface.h"')
hdr = replace_once(hdr,
    "    [[nodiscard]] Scheduler& GetScheduler() noexcept {",
    "    // Called only when a NEW guest VideoOut buffer is presented. This is\n"
    "    // the authoritative guest frame boundary; Beginning the HUD is NOT.\n"
    "    void Fsr31PortOnPresentedFrame();\n"
    "    Bachata::Fsr31::PortUiSurface::Display Fsr31PortTakeDisplay();\n\n"
    "    [[nodiscard]] Scheduler& GetScheduler() noexcept {")
hdr = replace_once(hdr, "    bool attachment_feedback_loop{};",
    "    bool attachment_feedback_loop{};\n"
    "    Bachata::Fsr31::PortCameraState fsr31PortCamera{};\n"
    "    Bachata::Fsr31::RasterizerSceneStage fsr31PortStage{};\n"
    "    std::unique_ptr<Bachata::Fsr31::PortUiSurface> fsr31PortUi;\n"
    "    VideoCore::ImageId fsr31PortLdr{};\n"
    "    std::array<float,2> fsr31PortUiRenderScale{1.f,1.f};")

src = replace_once(src,
    '#include "video_core/renderer_vulkan/vk_rasterizer.h"',
    '#include "video_core/renderer_vulkan/vk_rasterizer.h"\n'
    '#include <cstdlib>\n#include <cstdio>\n#include <cmath>')

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
        // Identify the real scene target BEFORE the first Scaleform draw.
        // Never use the final VideoOut image as temporal scene input.
        if (event == Bachata::Fsr31::Event::GBuffer) {
            fsr31PortLdr = {};
            fsr31PortUi->CancelFrame();
        } else if (event == Bachata::Fsr31::Event::LDRScene) {
            fsr31PortLdr = cb_descs[0].first;
        } else if (event == Bachata::Fsr31::Event::BeginHUD && fsr31PortLdr) {
            auto& scene = texture_cache.GetImage(fsr31PortLdr);
            const auto* depth = db_desc.first
                ? &texture_cache.GetImage(db_desc.first) : nullptr;
            // R13 policy: 640x360 scene -> 1280x720 composited frame.
            // Spatial blit is only a fallback until temporal dispatch is wired.
            const vk::Extent2D out{1280,720};
            if (scene.info.size.width < out.width &&
                scene.info.size.height < out.height) {
                fsr31PortUi->Begin(scene, fsr31PortLdr, cb_descs[0].first,
                                   depth, db_desc.first, out);
            }
        }
    }
'''
src = replace_once(src,
    '      pipeline_cache{instance, scheduler, liverpool} {',
    '      pipeline_cache{instance, scheduler, liverpool} {\n'
    '    fsr31PortUi = std::make_unique<Bachata::Fsr31::PortUiSurface>(instance, scheduler);')

src = replace_once(src,
    "    } else {\n        db_desc.first = {};\n    }\n}\n\nstatic std::pair<u32, u32> GetDrawOffsets(",
    "    } else {\n        db_desc.first = {};\n    }\n" + body +
    "}\n\nstatic std::pair<u32, u32> GetDrawOffsets(")

cam = r'''
            // Bloodborne port: inspect actual 864-byte guest camera buffer
            // on each GBuffer pass. Do not reuse stale matrices across frames.
            // MemoryManager already bounded the mapped guest range.
            if (!desc.is_written && vsharp.GetSize() == 864 &&
                fsr31PortCamera.WaitingForConstants() &&
                size >= 216 * sizeof(float) &&
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

frame_boundary = r'''
void Rasterizer::Fsr31PortOnPresentedFrame() {
    // The port advances the previous camera matrix at VideoOut, once per
    // completed guest frame, not on the first Scaleform UI draw. Doing so
    // earlier mixes motion history from different frames.
    fsr31PortCamera.OnDisplayFrame();
    fsr31PortStage.OnDisplayFrame();
    fsr31PortLdr = {};
}
Bachata::Fsr31::PortUiSurface::Display Rasterizer::Fsr31PortTakeDisplay() {
    return fsr31PortUi ? fsr31PortUi->TakeDisplay()
                       : Bachata::Fsr31::PortUiSurface::Display{};
}
'''
src = replace_once(src,
    "static std::pair<u32, u32> GetDrawOffsets(",
    frame_boundary + "\nstatic std::pair<u32, u32> GetDrawOffsets(")


# Native pre-UI composition: all HUD colors go to a separate host surface.
# This change does not install a user-facing APK; it is compile-validated first.
src = replace_once(src,
    "    if (state.num_layers == std::numeric_limits<u16>::max()) {",
    r'''    fsr31PortUiRenderScale = {1.f,1.f};
    if (fsr31PortUi && fsr31PortUi->Drawing() &&
        state.num_color_attachments == 1 &&
        fsr31PortUi->RedirectColor(cb_descs[0].first) &&
        (!db_desc.first || fsr31PortUi->RedirectDepth(db_desc.first))) {
        auto& color_attachment = state.color_attachments[0];
        color_attachment.image_view = fsr31PortUi->ColorView();
        color_attachment.image_layout = vk::ImageLayout::eGeneral;
        if (db_desc.first) {
            auto& depth_attachment = state.depth_stencil_attachment;
            depth_attachment.image_view = fsr31PortUi->DepthView();
            depth_attachment.image_layout = vk::ImageLayout::eGeneral;
        }
        const auto out = fsr31PortUi->Size();
        state.width = out.width;
        state.height = out.height;
        const auto& vp = regs.viewports[0];
        const bool native = std::abs(std::abs(vp.xscale * 2.f) - 1920.f) < 0.5f &&
                            std::abs(std::abs(vp.yscale * 2.f) - 1080.f) < 0.5f;
        fsr31PortUiRenderScale = fsr31PortUi->Scale(native);
    }
''' + "    if (state.num_layers == std::numeric_limits<u16>::max()) {")
src = replace_once(src,
    "        viewports.push_back(viewport);",
    r'''        viewport.x *= fsr31PortUiRenderScale[0];
        viewport.width *= fsr31PortUiRenderScale[0];
        viewport.y *= fsr31PortUiRenderScale[1];
        viewport.height *= fsr31PortUiRenderScale[1];
        viewports.push_back(viewport);''')
src = replace_once(src,
    "        scissors.push_back({\n"
    "            .offset = {vp_scsr.top_left_x, vp_scsr.top_left_y},\n"
    "            .extent = {vp_scsr.GetWidth(), vp_scsr.GetHeight()},\n"
    "        });",
    r'''        scissors.push_back({
            .offset = {s32(std::lround(float(vp_scsr.top_left_x)*fsr31PortUiRenderScale[0])),
                       s32(std::lround(float(vp_scsr.top_left_y)*fsr31PortUiRenderScale[1]))},
            .extent = {u32(std::lround(float(vp_scsr.GetWidth())*fsr31PortUiRenderScale[0])),
                       u32(std::lround(float(vp_scsr.GetHeight())*fsr31PortUiRenderScale[1]))},
        });''')

pres = replace_once(pres,
    "    texture_cache.UpdateImage(image_id);",
    "    texture_cache.UpdateImage(image_id);\n"
    "    const auto port_display = rasterizer->Fsr31PortTakeDisplay();\n"
    "    rasterizer->Fsr31PortOnPresentedFrame();")

# The upstream font helper uses reinterpret_cast inside constexpr data() accessors.
# Clang 18+ rejects these irrespective of the rasterizer change. The helpers
# operate on the live byte view at runtime; neither must be constexpr.
font_header = project / "src/core/libraries/font/fontft_internal.h"
font_src = font_header.read_text()
for old_signature, new_signature in (
    ("    constexpr u8* data() {", "    u8* data() {"),
    ("    constexpr const u8* data() const {", "    const u8* data() const {"),
):
    font_src = replace_once(font_src, old_signature, new_signature)


pres = replace_once(pres,
    "    const vk::Extent2D image_size = {image.info.size.width, image.info.size.height};",
    "    vk::Extent2D image_size = {image.info.size.width, image.info.size.height};")
pres = replace_once(pres,
    "    image_view = fsr_pass.Render(cmdbuf, image_view, image_size, {frame->width, frame->height},",
    "    // Preserve original guest screenshots; display the isolated HUD target.\n"
    "    if (port_display.view) {\n"
    "        image_view = port_display.view;\n"
    "        image_size = port_display.size;\n"
    "    }\n"
    "    image_view = fsr_pass.Render(cmdbuf, image_view, image_size, {frame->width, frame->height},")

header.write_text(hdr)
raster.write_text(src)
presenter.write_text(pres)
font_header.write_text(font_src)
print("Port scene classifier + camera signatures connected to source Rasterizer;",
      "native Clang constexpr blocker repaired; core024 executable unchanged.")
