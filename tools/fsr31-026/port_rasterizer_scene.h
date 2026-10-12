// SPDX-License-Identifier: GPL-2.0-or-later
// Bloodborne 01.09 guest-render-state classifier.
// Adapted from the selection predicates in ducvd89/Bloodborne-Android
// (vk_rasterizer.cpp / ui_composition.h, android-0.5.2).
// This module NEVER intercepts vkCmdBeginRendering or writes guest images.
#pragma once
#include <array>
#include <bit>
#include <cstdint>
namespace Bachata::Fsr31 {
enum class Format : std::uint8_t { Other, RGBA16F, RGBA8UNorm, RGBA8SRgb };
enum class Event : std::uint8_t { None, GBuffer, HDRScene, LDRScene, BeginHUD };
struct DrawState {
    std::uint64_t colorId{}, depthId{}, vertexShaderHash{};
    std::uint32_t mrtMask{}, colorWidth{}, colorHeight{}, depthWidth{}, depthHeight{};
    Format colorFormat{Format::Other};
    bool cameraConstantsValid{}, displayBuffer{};
};
struct Scene {
    std::uint64_t colorId{}, depthId{};
    std::uint32_t width{}, height{};
    Format format{Format::Other};
    bool ready{};
};
constexpr bool IsBloodborneUiShader(std::uint64_t hash) {
    constexpr std::array<std::uint64_t,10> hashes{
        0x34e8a281ull,0x81d336ceull,0x09957251ull,0x24042a9bull,
        0xa400228bull,0xbb4d5f8cull,0xe94b5b06ull,0x9951d199ull,
        0x44072322ull,0xa334a845ull};
    for (auto h : hashes) if (h==hash) return true;
    return false;
}
class RasterizerSceneStage {
public:
    void OnDisplayFrame() { scene_={}; mainDepth_=0; hudStarted_=false; }
    const Scene& CurrentScene() const { return scene_; }
    bool HUDStarted() const { return hudStarted_; }
    Event Observe(const DrawState& draw) {
        if (draw.displayBuffer) { OnDisplayFrame(); return Event::None; }
        if (hudStarted_ || !draw.colorId) return Event::None;
        const unsigned mrt=std::popcount(draw.mrtMask);
        if (mrt>=5 && draw.depthId && draw.cameraConstantsValid) {
            mainDepth_=draw.depthId; scene_={};
            return Event::GBuffer;
        }
        const bool sceneDepth=draw.cameraConstantsValid && mainDepth_ &&
                              draw.depthId==mainDepth_;
        const bool sizesMatch=draw.colorWidth && draw.colorHeight &&
                              draw.colorWidth==draw.depthWidth &&
                              draw.colorHeight==draw.depthHeight;
        // The game-tested Scaleform shader, *different* guest UI target, and
        // its decoupled 1920x1080 logical size are required together.
        // A small Vulkan pass followed by a larger one is NOT enough.
        if (scene_.ready && IsBloodborneUiShader(draw.vertexShaderHash) &&
            draw.colorId!=scene_.colorId &&
            draw.colorWidth==1920 && draw.colorHeight==1080 &&
            (draw.colorFormat==Format::RGBA8UNorm ||
             draw.colorFormat==Format::RGBA8SRgb)) {
            hudStarted_=true;
            return Event::BeginHUD;
        }
        if (sceneDepth && sizesMatch && mrt<=2 &&
            draw.colorFormat==Format::RGBA16F) {
            scene_={draw.colorId,draw.depthId,draw.colorWidth,
                    draw.colorHeight,draw.colorFormat,true};
            return Event::HDRScene;
        }
        if (sceneDepth && sizesMatch && mrt<=2 &&
            (draw.colorFormat==Format::RGBA8UNorm ||
             draw.colorFormat==Format::RGBA8SRgb)) {
            scene_={draw.colorId,draw.depthId,draw.colorWidth,
                    draw.colorHeight,draw.colorFormat,true};
            return Event::LDRScene;
        }
        return Event::None;
    }
private:
    std::uint64_t mainDepth_{};
    Scene scene_{};
    bool hudStarted_{};
};
} // namespace Bachata::Fsr31
