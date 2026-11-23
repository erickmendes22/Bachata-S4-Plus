#!/usr/bin/env python3
"""Port the Bachata 0.2.6 command-buffer ownership contract into shadPS4 0.18.1.

The actual 0.2.6 AArch64 ELF implements CopyCmdBuffers by allocating independent
DCB/CCB vectors on each submission. The upstream 0.18.1 uses two fixed-capacity
queue vectors instead, asserting at liverpool.cpp:1137 when a game exceeds their
2-MiB reservations. Merely growing those vectors can invalidate spans held by
suspended GPU coroutines.

This adapter makes each submitted graphics coroutine OWN its copies until the
task is destroyed. It changes the shared GPU executor, never a game's code.
It fails closed when the pinned source differs.
"""
from __future__ import annotations

from pathlib import Path

MARKER = "BACHATA_RELEASE026_OWNED_DCB_CCB"


def replace_one(text: str, old: str, new: str, what: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"0.2.6 command buffers: {what}: expected one source anchor, got {count}")
    return text.replace(old, new, 1)


def patch_header(text: str) -> str:
    text = replace_one(
        text,
        "#include <vector>\n",
        "#include <utility>\n#include <vector>\n",
        "explicit utility include")
    text = replace_one(
        text,
        "        mapped_queues[GfxQueueId].ccb_buffer_offset = 0;\n"
        "        mapped_queues[GfxQueueId].dcb_buffer_offset = 0;\n",
        "",
        "remove unsafe shared copy offsets")
    start = (
        "    void ReserveCopyBufferSpace() {\n"
        "        GpuQueue& gfx_queue = mapped_queues[GfxQueueId];\n"
        "        std::scoped_lock lk(gfx_queue.m_access);\n"
        "        constexpr size_t GfxReservedSize = 2_MB >> 2;\n"
        "        gfx_queue.ccb_buffer.reserve(GfxReservedSize);\n"
        "        gfx_queue.dcb_buffer.reserve(GfxReservedSize);\n"
        "    }")
    text = replace_one(
        text, start,
        "    // Compatibility API; copied PM4 streams now belong to each GPU coroutine.\n"
        "    void ReserveCopyBufferSpace() {}",
        "remove global fixed-capacity reservation")
    text = replace_one(
        text,
        "    using CmdBuffer = std::pair<std::span<const u32>, std::span<const u32>>;\n"
        "    CmdBuffer CopyCmdBuffers(std::span<const u32> dcb, std::span<const u32> ccb);\n"
        "    Task ProcessGraphics(std::span<const u32> dcb, std::span<const u32> ccb);",
        "    using CmdBuffer = std::pair<std::vector<u32>, std::vector<u32>>;\n"
        "    CmdBuffer CopyCmdBuffers(std::span<const u32> dcb, std::span<const u32> ccb);\n"
        "    // The by-value CmdBuffer is stored in the suspended coroutine frame.\n"
        "    Task ProcessGraphics(std::span<const u32> dcb, std::span<const u32> ccb,\n"
        "                         CmdBuffer owned_buffers = {});",
        "own copied command streams in coroutine frame")
    text = replace_one(
        text,
        "        std::atomic<u32> dcb_buffer_offset;\n"
        "        std::atomic<u32> ccb_buffer_offset;\n"
        "        std::vector<u32> dcb_buffer;\n"
        "        std::vector<u32> ccb_buffer;\n",
        "",
        "drop unused shared staging memory")
    return text


def patch_source(text: str) -> str:
    text = replace_one(
        text,
        "Liverpool::Task Liverpool::ProcessGraphics(std::span<const u32> dcb, std::span<const u32> ccb) {",
        "Liverpool::Task Liverpool::ProcessGraphics(std::span<const u32> dcb,\n"
        "                                           std::span<const u32> ccb,\n"
        "                                           CmdBuffer owned_buffers) {",
        "graphic coroutine definition")
    text = replace_one(
        text,
        "    FIBER_EXIT;\n}\n\ntemplate <bool is_indirect>\n",
        "    // BACHATA_RELEASE026_OWNED_DCB_CCB: keep both PM4 vectors alive across\n"
        "    // co_yield/RESUME_GFX, until the GPU task is actually destroyed.\n"
        "    static_cast<void>(owned_buffers);\n"
        "    FIBER_EXIT;\n}\n\ntemplate <bool is_indirect>\n",
        "coroutine lifetime anchor")
    begin = (
        "Liverpool::CmdBuffer Liverpool::CopyCmdBuffers(std::span<const u32> dcb, "
        "std::span<const u32> ccb) {")
    end = "\nvoid Liverpool::SubmitGfx(std::span<const u32> dcb, std::span<const u32> ccb) {"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise RuntimeError("0.2.6 command buffers: missing original copy/submit function boundaries")
    a = text.index(begin)
    b = text.index(end, a)
    orig = text[a:b]
    for required in (
        "dcb copy buffer out of reserved space",
        "ccb copy buffer out of reserved space",
        "queue.dcb_buffer_offset",
        "queue.ccb_buffer_offset",
        "return std::make_pair(dcb, ccb);",
    ):
        if required not in orig:
            raise RuntimeError(f"0.2.6 command buffers: unexpected upstream copy body: {required}")
    new = (
        "Liverpool::CmdBuffer Liverpool::CopyCmdBuffers(std::span<const u32> dcb,\n"
        "                                                   std::span<const u32> ccb) {\n"
        "    CmdBuffer owned{};\n"
        "    if (!dcb.empty()) {\n"
        "        owned.first.assign(dcb.begin(), dcb.end());\n"
        "    }\n"
        "    if (!ccb.empty()) {\n"
        "        owned.second.assign(ccb.begin(), ccb.end());\n"
        "    }\n"
        "    return owned;\n"
        "}\n"
    )
    text = text[:a] + new + text[b:]
    text = replace_one(
        text,
        "    if (EmulatorSettings.IsCopyGpuBuffers()) {\n"
        "        std::tie(dcb, ccb) = CopyCmdBuffers(dcb, ccb);\n"
        "    }\n\n"
        "    auto task = ProcessGraphics(dcb, ccb);",
        "    CmdBuffer owned_buffers{};\n"
        "    if (EmulatorSettings.IsCopyGpuBuffers()) {\n"
        "        owned_buffers = CopyCmdBuffers(dcb, ccb);\n"
        "        dcb = owned_buffers.first;\n"
        "        ccb = owned_buffers.second;\n"
        "    }\n\n"
        "    // Moving these vectors preserves spans into their allocations. The\n"
        "    // graphics coroutine owns both allocations across asynchronous PM4 work.\n"
        "    auto task = ProcessGraphics(dcb, ccb, std::move(owned_buffers));",
        "submission ownership transfer")
    return text


def audit(header: str, source: str) -> None:
    required = (
        ("header", header, "std::pair<std::vector<u32>, std::vector<u32>>"),
        ("header", header, "CmdBuffer owned_buffers = {}"),
        ("source", source, MARKER),
        ("source", source, "std::move(owned_buffers)"),
        ("source", source, "owned.first.assign(dcb.begin(), dcb.end());"),
        ("source", source, "owned.second.assign(ccb.begin(), ccb.end());"),
    )
    forbidden = (
        ("header", header, "dcb_buffer_offset"),
        ("header", header, "ccb_buffer_offset"),
        ("source", source, "dcb copy buffer out of reserved space"),
        ("source", source, "ccb copy buffer out of reserved space"),
    )
    errors = [f"{place} lacks {needle}" for place, txt, needle in required if needle not in txt]
    errors += [f"{place} still has {needle}" for place, txt, needle in forbidden if needle in txt]
    if errors:
        raise RuntimeError("GPU owned command buffer parity failure:\n" + "\n".join(errors))


def apply(root: Path) -> dict:
    header = root / "src/video_core/amdgpu/liverpool.h"
    source = root / "src/video_core/amdgpu/liverpool.cpp"
    h, c = header.read_text(), source.read_text()
    if MARKER in c:
        audit(h, c)
        return {"status": "already-applied", "release": "0.2.6",
                "ownership": "per-graphics-coroutine"}
    new_h = patch_header(h)
    new_c = patch_source(c)
    audit(new_h, new_c)
    header.write_text(new_h)
    source.write_text(new_c)
    return {"status": "ported", "release": "0.2.6",
            "ownership": "per-graphics-coroutine",
            "dcbCcbBufferMode": "independent-owned-vectors",
            "static2MiBAssertion": "removed-with-owned-lifetime"}


def selftest() -> None:
    # Reject absent/moved anchors before the full NDK compilation.
    try:
        patch_header("unexpected shadPS4 source")
    except RuntimeError as error:
        assert "anchor" in str(error)
    else:
        raise AssertionError("unrecognized source must fail closed")
    try:
        patch_source("unexpected shadPS4 source")
    except RuntimeError as error:
        assert "definition" in str(error)
    else:
        raise AssertionError("unrecognized GPU source must fail closed")
    print("BACHATA_RELEASE026_CMDBUFFER_FAIL_CLOSED_SELFTEST_PASS")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("selftest", "apply", "audit"))
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    if args.command == "selftest":
        selftest()
    elif args.source is None:
        parser.error("--source required for apply/audit")
    elif args.command == "apply":
        print(apply(args.source))
    else:
        audit((args.source / "src/video_core/amdgpu/liverpool.h").read_text(),
              (args.source / "src/video_core/amdgpu/liverpool.cpp").read_text())
        print("BACHATA_RELEASE026_GPU_COMMAND_BUFFER_OWNERSHIP_AUDIT_PASS")
