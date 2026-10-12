// SPDX-License-Identifier: GPL-2.0-or-later
// Bloodborne Android 0.5.2 guest camera-constants signature.
// Native renderer must supply the real 864-byte guest constant buffer.
#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstddef>
namespace Bachata::Fsr31 {
struct GuestCamera {
    std::array<float,12> view{}, inverseView{};
    std::array<float,4> projection{};
    std::uint32_t renderWidth{}, renderHeight{};
    bool valid{};
};
class PortCameraState {
public:
    void OnGBuffer(std::uint64_t depth, float xSign=1.f,float ySign=1.f) {
        if(depth!=currentDepth_) {currentDepth_=depth;passHasCamera_=false;}
        viewportXSign_=xSign;viewportYSign_=ySign;
    }
    void OnConstants(const float* data,std::size_t floats) {
        // Port's exact far-plane, reciprocal, size, and matrix offsets.
        if(!currentDepth_||passHasCamera_||!data||floats<192||
           data[0]!=3000.f||data[4]<64.f||data[5]<64.f||
           std::abs(data[1]*data[0]-1.f)>0.001f)return;
        GuestCamera c{};
        std::copy_n(data+8,12,c.view.begin());
        std::copy_n(data+180,12,c.inverseView.begin());
        c.projection={data[52]*viewportXSign_,data[57]*viewportYSign_,
                      data[62],data[63]};
        c.renderWidth=static_cast<std::uint32_t>(data[4]);
        c.renderHeight=static_cast<std::uint32_t>(data[5]);
        c.valid=std::isfinite(c.projection[0])&&
                std::isfinite(c.projection[1])&&
                c.projection[0]!=0.f&&c.projection[1]!=0.f;
        if(!c.valid)return;
        current_=c;passHasCamera_=true;
    }
    bool WaitingForConstants() const {
        return currentDepth_ != 0 && !passHasCamera_;
    }
    bool HasCameraForDepth(std::uint64_t depth) const {
        return passHasCamera_&&current_.valid&&depth&&depth==currentDepth_;
    }
    bool HasTemporalHistory() const {
        return previous_.valid&&current_.valid&&passHasCamera_;
    }
    void OnDisplayFrame() {
        if(passHasCamera_)previous_=current_;
        passHasCamera_=false;currentDepth_=0;
    }
    const GuestCamera& Current() const{return current_;}
    const GuestCamera& Previous() const{return previous_;}
private:
    std::uint64_t currentDepth_{};
    float viewportXSign_{1},viewportYSign_{1};
    GuestCamera current_{},previous_{};
    bool passHasCamera_{};
};
} // namespace Bachata::Fsr31
