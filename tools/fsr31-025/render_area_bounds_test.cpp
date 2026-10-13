// SPDX-License-Identifier: GPL-2.0-or-later
#include "../fsr31-026/render_area_bounds.h"
#include <cassert>
#include <cstdio>
int main() {
    using BachataRendering::BoundArea;
    VkRect2D fixed{};
    assert(BoundArea({{0,0},{1920,1080}},{{640,360}},fixed));
    assert(fixed.extent.width==640 && fixed.extent.height==360);
    assert(BoundArea({{0,0},{1920,1080}},{{1920,1080},{640,360}},fixed));
    assert(fixed.extent.width==640 && fixed.extent.height==360);
    assert(!BoundArea({{0,0},{640,360}},{{1920,1080}},fixed));
    assert(fixed.extent.width==640 && fixed.extent.height==360);
    assert(BoundArea({{16,8},{1920,1080}},{{640,360}},fixed));
    assert(fixed.offset.x==16 && fixed.offset.y==8);
    assert(fixed.extent.width==624 && fixed.extent.height==352);
    assert(!BoundArea({{640,0},{1920,1080}},{{640,360}},fixed));
    assert(!BoundArea({{-1,0},{1920,1080}},{{640,360}},fixed));
    assert(!BoundArea({{0,0},{1920,1080}},{},fixed));
    puts("PASS: oversized native render area is limited by all attachments; legal areas and offsets preserved; invalid/unknown geometry refused");
}
