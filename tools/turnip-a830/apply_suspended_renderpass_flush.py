#!/usr/bin/env python3
"""Backport Droid-Deck's *selective* suspended-render-pass flush into pinned V38.

Source: Droid-Deck/Drivers
  patches/tu/0001-tu-flush-before-suspended-render-pass-chain.patch

This is NOT TU_DEBUG=flushall and does NOT add global per-draw cache flushes.
Fail closed on unexpected Mesa source rather than silently shipping without it.
"""
from pathlib import Path
import sys

SOURCE = Path("src/freedreno/vulkan/tu_cmd_buffer.cc")
MARKER = "A830 suspended-renderpass pre-chain cache flush (Droid-Deck)"
BEFORE = """   cmd->state.suspending = suspending;
   cmd->state.resuming = resuming;

   if (!resuming && cmd->device->dbg_renderpass_stomp_cs) {"""
AFTER = """   cmd->state.suspending = suspending;
   cmd->state.resuming = resuming;

   /* A830 suspended-renderpass pre-chain cache flush (Droid-Deck).
    *
    * A chain that remains suspended at EndCommandBuffer is rendered by
    * tu_insert_dynamic_cmdbufs() with a new, empty cache state. Emit any
    * previously pending barrier flushes in this original command buffer.
    * TU_DEBUG=flushall is neither needed nor enabled.
    */
   if (suspending && !resuming)
      tu_emit_cache_flush<CHIP>(cmd);

   if (!resuming && cmd->device->dbg_renderpass_stomp_cs) {"""

def apply(path: Path = SOURCE) -> None:
    text = path.read_text()
    start = text.find("tu_CmdBeginRendering(VkCommandBuffer commandBuffer,")
    stop = text.find("tu_renderpass_begin(cmd);", start)
    if start < 0 or stop < start:
        raise RuntimeError("Pinned V38 tu_CmdBeginRendering body not found")
    body = text[start:stop]
    if MARKER in body:
        assert body.count(MARKER) == 1, "Duplicated patch marker"
        assert body.count("if (suspending && !resuming)") == 1, "Duplicated flush"
        assert body.count("tu_emit_cache_flush<CHIP>(cmd);") == 1
        print("PASS: selective suspend-chain flush already integrated")
        return
    if body.count(BEFORE) != 1:
        raise RuntimeError("Pinned V38 suspend/resume anchor changed; refuse unsafe patch")
    if "if (suspending && !resuming)" in body:
        raise RuntimeError("Suspended chain already handles pre-chain flush; inspect before applying")
    if "tu_insert_dynamic_cmdbufs" not in text:
        raise RuntimeError("Expected deferred dynamic rendering implementation absent")
    rewritten = text[:start] + body.replace(BEFORE, AFTER, 1) + text[stop:]
    assert rewritten.count(MARKER) == 1
    assert rewritten[start:stop+len(AFTER)].count("if (suspending && !resuming)") == 1
    path.write_text(rewritten)
    print("PASS: selective suspended renderpass flush integrated; TU_DEBUG=flushall untouched")

if __name__ == "__main__":
    try:
        apply(Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE)
    except Exception as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
