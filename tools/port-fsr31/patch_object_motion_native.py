#!/usr/bin/env python3
"""Adapt exact Port VkObjectMotion GPU buffers to core025's native scheduler.

This builds original Port allocation/history/RT7 code; actual G-buffer
pipeline selection and shader parameter assignment are subsequent integration.
"""
from pathlib import Path
import re
import sys
root=Path(sys.argv[1]).resolve()
upstream=Path(__file__).resolve().parent/"gpu/shadps4/video_core/renderer_vulkan"
out=root/"src/video_core/renderer_vulkan"
for name in ["motion_history.h","vk_object_motion.h","vk_object_motion.cpp"]:
    (out/name).write_bytes((upstream/name).read_bytes())
p=out/"vk_object_motion.cpp"
s=p.read_text()
def one(before,after):
    global s
    n=s.count(before)
    if n!=1:raise RuntimeError(f"ObjectMotion source mismatch, found {n}: {before[:90]!r}")
    s=s.replace(before,after)
one('#include "bbport_settings.h"\n#include "bbport_toggles.h"\n','')
one('''    if (!BbSettings::Get().object_motion ||
        BbSettings::Get().upscaler == BbSettings::UpscalerOff) {''',
    '''    // Enabled only for an explicit temporal renderer session.
    const char* mode=std::getenv("BACHATA_FSR31_MODE");
    if (!mode || mode[0]<'0' || mode[0]>'4' || mode[1]!=0) {''')
one('if (!enabled || BbToggle::Disabled(1u << 29) || params_used >= ParamsPerFrame)',
    'if (!enabled || params_used >= ParamsPerFrame)')
s,n=re.subn(r'    if \(BbStats::enabled && \(frame % 600\) == 0 && history\.stats\.draws\) \{.*?        history\.stats = \{\};\n    \}\n','',s,count=1,flags=re.S)
if n!=1:raise RuntimeError("Cannot retire unsupported Port stats from OnFrameStart")
s,n=re.subn(r'    static u32 reports = 0;\n    if \(BbStats::enabled && reports < 16\) \{.*?\n    \}\n','',s,count=1,flags=re.S)
if n!=1:raise RuntimeError("Cannot retire unsupported Port stats from GPU target")
# The original core025 scheduler already records directly via CommandBuffer().
# Preserve barrier order, but do not assume the Port's recording-thread API.
one('''    scheduler.Record([](vk::CommandBuffer cmd) {''',
    '''    { const auto cmd=scheduler.CommandBuffer();''')
one('''    scheduler.Record([barrier](vk::CommandBuffer cmd) {''',
    '''    { const auto cmd=scheduler.CommandBuffer();''')
one('''    scheduler.Record([barrier](vk::CommandBuffer cmdbuf) {''',
    '''    { const auto cmdbuf=scheduler.CommandBuffer();''')
# All three lambda wrappers end with the same "});" after pipelineBarrier2;
# only replace these explicit sites, leaving other lambdas untouched.
s,n=re.subn(r'(?m)^    \}\);(?=\n)', '    }', s)
if n != 3:
    raise RuntimeError(f"Expected three scheduler closures, found {n}")
if "BbSettings" in s or "BbStats" in s or "BbToggle" in s or "scheduler.Record" in s:
    raise RuntimeError("Port dependency remains unadapted")
p.write_text(s)
cm=root/"CMakeLists.txt"
c=cm.read_text()
anchor="                src/video_core/renderer_vulkan/vk_rasterizer.h"
assert c.count(anchor)==1
c=c.replace(anchor,anchor+'''
                src/video_core/renderer_vulkan/motion_history.h
                src/video_core/renderer_vulkan/vk_object_motion.h
                src/video_core/renderer_vulkan/vk_object_motion.cpp''')
cm.write_text(c)
print("PASS: Port ObjectMotion GPU position-history buffers and RT7 compiled into native core025 sources")
, '    }', s)
if n!=3:raise RuntimeError(f"Expected exactly three scheduler closure ends, found {n}")
if "BbSettings" in s or "BbStats" in s or "BbToggle" in s or "scheduler.Record" in s:
    raise RuntimeError("Port dependency remains unadapted")
p.write_text(s)
cm=root/"CMakeLists.txt"
c=cm.read_text()
anchor="                src/video_core/renderer_vulkan/vk_rasterizer.h"
assert c.count(anchor)==1
c=c.replace(anchor,anchor+'''
                src/video_core/renderer_vulkan/motion_history.h
                src/video_core/renderer_vulkan/vk_object_motion.h
                src/video_core/renderer_vulkan/vk_object_motion.cpp''')
cm.write_text(c)
print("PASS: Port ObjectMotion GPU position-history buffers and RT7 compiled into native core025 sources")
