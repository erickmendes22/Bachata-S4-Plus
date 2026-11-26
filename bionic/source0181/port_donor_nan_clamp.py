#!/usr/bin/env python3
"""Close the remaining active donor NaN min/max/clamp/saturate contract.

SotC defaults to NMin/NMax, including NMin(NMax(x, lo), hi) for clamp.
Order uses that composition only for saturation. Preserve other titles' F
operations and the SotC donor's SHADPS4_IEEE_MINMAX presence-based opt-out.
"""
from pathlib import Path
import re


def apply(root):
    root=Path(root)
    shader=root/"src/shader_recompiler"
    policy=Path(__file__).with_name("donor_nan_clamp.h").read_text()
    (shader/"donor_nan_clamp.h").write_text(policy)
    path=shader/"backend/spirv/emit_spirv_floating_point.cpp"
    source=path.read_text()
    source='#include "shader_recompiler/donor_nan_clamp.h"\n'+source

    def replace_body(name,old,new):
        nonlocal source
        signature=f"Id {name}("
        if source.count(signature)!=1:
            raise RuntimeError("Donor NaN clamp definition drift: "+name)
        begin=source.index(signature);end=source.index("\n}",begin)+2
        body=source[begin:end]
        if body.count(old)!=1:
            raise RuntimeError("Donor NaN clamp operation drift: "+name)
        source=source[:begin]+body.replace(old,new,1)+source[end:]

    for width in (32,64):
        ty=f"ctx.F{width}[1]"
        for op in ("Min","Max"):
            replace_body(f"EmitFP{op}{width}",f"return ctx.OpF{op}({ty}, a, b);",
                         f"return DonorNanClamp::MinMax() ? ctx.OpN{op}({ty}, a, b)\n"
                         f"                                   : ctx.OpF{op}({ty}, a, b);")
        for name,lo,hi,predicate in (("Clamp","min_value","max_value","MinMax"),
                                      ("Saturate","zero","one","Saturate")):
            replace_body(f"EmitFP{name}{width}",f"return ctx.OpFClamp({ty}, value, {lo}, {hi});",
                         f"return DonorNanClamp::{predicate}()\n"
                         f"               ? ctx.OpNMin({ty}, ctx.OpNMax({ty}, value, {lo}), {hi})\n"
                         f"               : ctx.OpFClamp({ty}, value, {lo}, {hi});")
    path.write_text(source)

    renderer=root/"src/video_core/renderer_vulkan"
    cache=renderer/"vk_pipeline_serialization.cpp"
    text=cache.read_text()
    text,count=re.subn(r"(ShaderBinaryVersion = )(\d+)(u;)",
                      lambda m:m[1]+str(int(m[2])+1)+m[3],text)
    if count!=1:raise RuntimeError("Donor NaN clamp binary generation drift")
    cache.write_text(text)
    live=renderer/"order_live_pso_cache.h"
    if live.exists():
        versions="-".join(re.search(rf"{name} = (\d+)u;",text)[1]
                          for name in ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
        text,count=re.subn(r"live-pso-v1-\d+-\d+-\d+","live-pso-v1-"+versions,live.read_text())
        if count!=1:raise RuntimeError("Donor NaN clamp live PSO generation drift")
        live.write_text(text)
    return {"SotC":"NaN-aware F32/F64 min/max/clamp/saturate, default on",
            "Order":"NaN-to-zero F32/F64 saturate; other F operations preserved",
            "otherTitles":"unchanged", "cache":"SPIR-V and live PSO generation incremented"}
