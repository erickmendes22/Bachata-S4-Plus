"""Annotate presentation closures after the shared present queue overlay."""
from pathlib import Path
from port_order_pass_end_reasons import annotate


CALLS = {"video_core/renderer_vulkan/vk_presenter.cpp": {
    "Frame* Presenter::PrepareLastFrame()": "Present",
    "Frame* Presenter::PrepareFrame(": "Present",
    "Frame* Presenter::PrepareBlankFrame(": "Present",
}}


def apply(root):
    root = Path(root)
    if not (root / "src/video_core/renderer_vulkan/order_render_pass_reasons.h").exists():
        raise RuntimeError("Presentation reasons require the pass-end reason family")
    annotate(root, CALLS)
    return {"presentation_control_flow": "unchanged", "actual_closures": "Present"}
