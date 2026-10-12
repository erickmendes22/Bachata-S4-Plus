// SPDX-License-Identifier: GPL-2.0-or-later
#include "port_rasterizer_scene.h"
#include <cassert>
using namespace Bachata::Fsr31;
int main() {
    RasterizerSceneStage scene;
    DrawState draw{};
    draw.colorId=1; draw.depthId=2; draw.colorWidth=640; draw.colorHeight=360;
    draw.depthWidth=640; draw.depthHeight=360;
    draw.mrtMask=1; draw.colorFormat=Format::RGBA8UNorm;
    draw.vertexShaderHash=0x34e8a281;
    // Exact failure mode from the rainbow build: an arbitrary small
    // attachment must not trigger FSR before the HUD.
    assert(scene.Observe(draw)==Event::None);
    assert(!scene.CurrentScene().ready);
    draw.mrtMask=0x1f;draw.cameraConstantsValid=true;
    assert(scene.Observe(draw)==Event::GBuffer);
    draw.mrtMask=1;draw.colorId=3;draw.colorFormat=Format::RGBA16F;
    assert(scene.Observe(draw)==Event::HDRScene);
    draw.colorId=4;draw.colorFormat=Format::RGBA8UNorm;
    draw.vertexShaderHash=0;
    assert(scene.Observe(draw)==Event::LDRScene);
    assert(scene.CurrentScene().colorId==4);
    // Actual Bloodborne port: the first Scaleform UI draw can target the
    // SAME 640x360 guest LDR image; only its viewport is logically 1080p.
    draw.colorId=4;draw.vertexShaderHash=0x34e8a281;
    assert(scene.Observe(draw)==Event::BeginHUD);
    assert(scene.HUDStarted());
    assert(scene.Observe(draw)==Event::None); // only once per frame
    scene.OnDisplayFrame();
    assert(!scene.HUDStarted() && !scene.CurrentScene().ready);
    assert(scene.Observe(draw)==Event::None);
    // Also accept the native-sized, separate HUD target after a new scene.
    draw.mrtMask=0x1f; draw.colorId=1;draw.depthId=2;
    draw.colorFormat=Format::RGBA16F;draw.vertexShaderHash=0;
    assert(scene.Observe(draw)==Event::GBuffer);
    draw.mrtMask=1;draw.colorId=4;draw.colorFormat=Format::RGBA8UNorm;
    assert(scene.Observe(draw)==Event::LDRScene);
    draw.colorId=6;draw.depthId=0;draw.colorWidth=1920;
    draw.colorHeight=1080;draw.depthWidth=1920;draw.depthHeight=1080;
    draw.vertexShaderHash=0x34e8a281;
    assert(scene.Observe(draw)==Event::BeginHUD);
}
