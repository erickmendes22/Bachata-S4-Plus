#!/usr/bin/env python3
"""Prevent a 720p UI pass from destroying a completed 360p camera scene.
This tests the R27 condition in vulkan_capture.cpp, not gameplay or AMD dispatch.
"""
from pathlib import Path
src = Path(__file__).resolve().parents[1].joinpath("vulkan_capture.cpp").read_text()
assert "(camera_ready&&camera_size.width==w&&camera_size.height==h)" in src

def classify(w,h,port,camera_ready,camera_size,ui_known):
    small = w>=600 and h>=320 and (
        (w<1280 and h<720) or (port and w==1280 and h==720 and not ui_known)
    )
    return small and (not port or (camera_ready and camera_size==(w,h)))

assert classify(640,360,True,True,(640,360),False)
assert not classify(1280,720,True,True,(640,360),False)
assert not classify(1280,720,True,False,(0,0),False)
assert classify(1280,720,True,True,(1280,720),False)
assert not classify(1280,720,True,True,(1280,720),True)
print("PASS: completed 360p scene survives 720p UI candidate")
