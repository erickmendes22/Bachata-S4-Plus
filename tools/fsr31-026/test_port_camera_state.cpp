// SPDX-License-Identifier: GPL-2.0-or-later
#include "port_camera_state.h"
#include <cassert>
int main() {
    using namespace Bachata::Fsr31;
    PortCameraState c;
    std::array<float,216> data{};
    c.OnGBuffer(42);
    c.OnConstants(data.data(),data.size());
    assert(!c.HasCameraForDepth(42));
    data[0]=3000.f; data[1]=1.f/3000.f; data[4]=640.f; data[5]=360.f;
    data[52]=1.f; data[57]=-1.f; data[62]=.1f; data[63]=1.f;
    data[8]=data[180]=1.f;
    c.OnConstants(data.data(),data.size());
    assert(c.HasCameraForDepth(42));
    assert(!c.HasCameraForDepth(43));
    assert(c.Current().renderWidth==640 && c.Current().renderHeight==360);
    c.OnDisplayFrame();
    assert(!c.HasCameraForDepth(42));
    c.OnGBuffer(42);
    c.OnConstants(data.data(),data.size());
    assert(c.HasTemporalHistory());
}
