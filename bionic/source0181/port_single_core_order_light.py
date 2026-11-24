#!/usr/bin/env python3
"""Bring the actual donor absent-lane and inactive-light contracts to 0.18.1,
and batch real GPU-written SRT page downloads on the common Bionic GPU path.
"""
from pathlib import Path
import re
def one(s,a,b,label):
    if s.count(a)!=1:
        raise RuntimeError(f"render/perf source drift {label}: {s.count(a)}")
    return s.replace(a,b,1)
def apply(root:Path):
    # Exact dedicated Order 16-light guard (de566ea0a46e).
    # The donor checks the 708-DWORD layout. Keep that contract, additionally
    # require actual contiguous fetched T# DWORDs rather than assuming a
    # partially immediate descriptor has the same slot identity.
    p=root/'src/shader_recompiler/resource.h'
    s=p.read_text()
    s=one(s,'struct ImageResource {','''template<class InfoT>
constexpr bool Order1886UnusedLightImage(const InfoT& info,u32 offset) {
    if (info.pgm_hash!=0x804aeeadULL) return false;
    const auto& flat=info.flattened_ud_buf;
    if (flat.size()!=708) return false;
    const u32 count=flat[657],mask=flat[655];
    if (count>16) return false;
    if (offset>=68 && offset<196 && (offset-68)%8==0)
        return (offset-68)/8>=count;
    if (offset>=196 && offset<324 && (offset-196)%8==0) {
        const u32 light=(offset-196)/8;
        return light>=count || ((mask>>light)&1)==0;
    }
    return false;
}

struct ImageResource {''','exact light table guard')
    s=one(s,'''    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {
        AmdGpu::Image image{};''',
        '''    constexpr AmdGpu::Image GetElementSharp(const auto& info,u32 element) const noexcept {
        // BACHATA_ORDER_LIGHT_GUARD: only inactive ordinary sampled images
        // in the verified 708-DWORD table; never blank active light images.
        if (!array_size && !is_depth && !is_atomic && !is_written && !is_r128 &&
            post_op==SharpFetchPostOp::None &&
            mip_fallback_mode==MipStorageFallbackMode::None &&
            sharp_fetch.load_mask==0xff &&
            Order1886UnusedLightImage(info,sharp_fetch.offsets[0])) {
            bool contiguous=true;
            for (u32 i=1;i<8;++i)
                contiguous &= sharp_fetch.offsets[i]==sharp_fetch.offsets[0]+i;
            if (contiguous) return AmdGpu::Image::Null(false);
        }
        AmdGpu::Image image{};''','apply prior to shader type selection and binding')
    p.write_text(s)

    return {"order":"exact 708-DWORD inactive light guard only"}
