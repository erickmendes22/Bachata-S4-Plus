#!/usr/bin/env python3
"""Coherent CE/PM4 port from release-era shadPS4 scheduling into pinned 0.18.1.

Apply AFTER port_release026_cmd_buffers.py: both CE and DE graphics tasks
must own a shared per-submit DCB/CCB allocation. Do not restore global 2 MiB
staging; do not let a CE task refer to data owned only by a DE task.
"""
from pathlib import Path

MARKER = "BACHATA_RELEASE026_CE_QUEUE_PARITY"

def one(src: str, old: str, new: str, label: str) -> str:
    count = src.count(old)
    if count != 1:
        raise RuntimeError(f"CE parity {label}: expected exactly one anchor, got {count}")
    return src.replace(old, new, 1)

def patch_header(h: str) -> str:
    h = one(h, "#include <mutex>\n", "#include <memory>\n#include <mutex>\n",
            "shared coroutine ownership header")
    h = one(h,
        "    Task ProcessGraphics(std::span<const u32> dcb, std::span<const u32> ccb,\n"
        "                         CmdBuffer owned_buffers = {});\n"
        "    Task ProcessCeUpdate(std::span<const u32> ccb);",
        "    Task ProcessGraphics(std::span<const u32> dcb,\n"
        "                         std::shared_ptr<CmdBuffer> owned_buffers = {});\n"
        "    Task ProcessCeUpdate(std::span<const u32> ccb,\n"
        "                         std::shared_ptr<CmdBuffer> owned_buffers = {});",
        "shared ownership API")
    h = one(h, "    void ProcessCommands();\n    void Process(std::stop_token stoken);",
        "    void ProcessCommands();\n    void ProcessCeQueue();\n    void Process(std::stop_token stoken);",
        "dedicated CE scheduler")
    h = one(h, "    std::array<GpuQueue, NumTotalQueues> mapped_queues{};\n",
        "    std::array<GpuQueue, NumTotalQueues> mapped_queues{};\n"
        "    std::queue<Task::Handle> ce_submits{};\n", "CE queue storage")
    return h

def patch_source(c: str) -> str:
    c = one(c,
        "Liverpool::~Liverpool() {\n"
        "    process_thread.request_stop();\n"
        "    process_thread.join();\n"
        "}\n",
        "Liverpool::~Liverpool() {\n"
        "    process_thread.request_stop();\n"
        "    process_thread.join();\n"
        "    while (!ce_submits.empty()) {\n"
        "        ce_submits.front().destroy();\n"
        "        ce_submits.pop();\n"
        "    }\n"
        "    for (auto& q : mapped_queues) {\n"
        "        while (!q.submits.empty()) {\n"
        "            q.submits.front().destroy();\n"
        "            q.submits.pop();\n"
        "        }\n"
        "    }\n"
        "}\n\n"
        "// BACHATA_RELEASE026_CE_QUEUE_PARITY: CE executes independently from DE.\n"
        "void Liverpool::ProcessCeQueue() {\n"
        "    auto& queue = mapped_queues[GfxQueueId];\n"
        "    Task::Handle task{};\n"
        "    {\n"
        "        std::scoped_lock lock{queue.m_access};\n"
        "        if (ce_submits.empty()) return;\n"
        "        task = ce_submits.front();\n"
        "    }\n"
        "    task.resume();\n"
        "    if (task.done()) {\n"
        "        task.destroy();\n"
        "        std::scoped_lock lock{queue.m_access};\n"
        "        ce_submits.pop();\n"
        "        --num_submits;\n"
        "        std::scoped_lock lock2{submit_mutex};\n"
        "        submit_cv.notify_all();\n"
        "    }\n"
        "}\n",
        "cleanup pending coroutine tasks and CE queue")
    c = one(c,
        "        while (num_submits || num_commands) {\n"
        "            ProcessCommands();\n",
        "        while ((num_submits || num_commands) && !stoken.stop_requested()) {\n"
        "            ProcessCommands();\n"
        "            ProcessCeQueue();\n",
        "schedule CE independently with stop guard")
    c = one(c,
        "Liverpool::Task Liverpool::ProcessCeUpdate(std::span<const u32> ccb) {",
        "Liverpool::Task Liverpool::ProcessCeUpdate(\n"
        "    std::span<const u32> ccb, std::shared_ptr<CmdBuffer> owned_buffers) {",
        "CE coroutine shared storage")
    c = one(c,
        "        const u32 type = header->type;\n"
        "        if (type != 3) {\n"
        "            // No other types of packets were spotted so far\n"
        "            UNREACHABLE_MSG(\"Invalid PM4 type {}\", type);\n"
        "        }\n\n"
        "        const PM4ItOpcode opcode = header->type3.opcode;\n"
        "        const auto* it_body = reinterpret_cast<const u32*>(header) + 1;",
        "        const u32 type = header->type;\n"
        "        if (type == 2) {\n"
        "            ccb = NextPacket(ccb, 1);\n"
        "            continue;\n"
        "        }\n"
        "        if (type != 3) {\n"
        "            UNREACHABLE_MSG(\"Invalid PM4 type {}\", type);\n"
        "        }\n\n"
        "        const PM4ItOpcode opcode = header->type3.opcode;\n"
        "        // Snapshot before a signal permits the guest to recycle the packet.\n"
        "        const u32 packet_words = header->type3.NumWords() + 1;\n"
        "        const auto* it_body = reinterpret_cast<const u32*>(header) + 1;",
        "CE packet-length snapshot and padding")
    c = one(c,
        "            while ((cblock.de_count - cblock.ce_count) >= diff) {\n"
        "                YIELD_CE();\n"
        "            }",
        "            while (cblock.ce_count >= cblock.de_count &&\n"
        "                   cblock.ce_count - cblock.de_count >= diff) {\n"
        "                YIELD_CE();\n"
        "            }",
        "counter unsigned underflow")
    c = one(c,
        "            while (!task.handle.done()) {\n"
        "                YIELD_CE();\n"
        "                RESUME_CE(task);\n"
        "            }\n"
        "            break;\n",
        "            while (!task.handle.done()) {\n"
        "                YIELD_CE();\n"
        "                RESUME_CE(task);\n"
        "            }\n"
        "            task.handle.destroy();\n"
        "            break;\n",
        "destroy nested CE coroutine")
    c = one(c,
        "        ccb = NextPacket(ccb, header->type3.NumWords() + 1);\n"
        "    }\n\n"
        "    FIBER_EXIT;\n"
        "}\n\n"
        "Liverpool::Task Liverpool::ProcessGraphics(",
        "        ccb = NextPacket(ccb, packet_words);\n"
        "    }\n\n"
        "    static_cast<void>(owned_buffers);\n"
        "    FIBER_EXIT;\n"
        "}\n\n"
        "Liverpool::Task Liverpool::ProcessGraphics(",
        "CE packet reuse safety")
    c = one(c,
        "Liverpool::Task Liverpool::ProcessGraphics(std::span<const u32> dcb,\n"
        "                                           std::span<const u32> ccb,\n"
        "                                           CmdBuffer owned_buffers) {",
        "Liverpool::Task Liverpool::ProcessGraphics(\n"
        "    std::span<const u32> dcb, std::shared_ptr<CmdBuffer> owned_buffers) {",
        "DE shared-owned coroutine")
    c = one(c,
        "    cblock.Reset();\n\n"
        "    // TODO: potentially, ASCs also can depend on CE and in this case the\n"
        "    // CE task should be moved into more global scope\n"
        "    Task ce_task{};\n\n"
        "    if (!ccb.empty()) {\n"
        "        // In case of CCB provided kick off CE asap to have the constant heap ready to use\n"
        "        ce_task = ProcessCeUpdate(ccb);\n"
        "        RESUME_GFX(ce_task);\n"
        "    }\n\n"
        "    const auto base_addr = reinterpret_cast<uintptr_t>(dcb.data());",
        "    // CE state persists across graphics submits; CE has its own FIFO.\n"
        "    auto base_addr = reinterpret_cast<uintptr_t>(dcb.data());",
        "remove intertwined CE execution/reset")
    c = one(c,
        "                const auto* indirect_buffer = reinterpret_cast<const PM4CmdIndirectBuffer*>(header);\n"
        "                auto task = ProcessGraphics(\n"
        "                    {indirect_buffer->Address<const u32>(), indirect_buffer->ib_size}, {});\n"
        "                RESUME_GFX(task);",
        "                const auto* indirect_buffer = reinterpret_cast<const PM4CmdIndirectBuffer*>(header);\n"
        "                if (indirect_buffer->chain) {\n"
        "                    dcb = {indirect_buffer->Address<const u32>(), indirect_buffer->ib_size};\n"
        "                    base_addr = reinterpret_cast<uintptr_t>(dcb.data());\n"
        "                    continue;\n"
        "                }\n"
        "                auto task = ProcessGraphics(\n"
        "                    {indirect_buffer->Address<const u32>(), indirect_buffer->ib_size});\n"
        "                RESUME_GFX(task);",
        "respect chained graphics indirect buffers")
    c = one(c,
        "                while (!task.handle.done()) {\n"
        "                    YIELD_GFX();\n"
        "                    RESUME_GFX(task);\n"
        "                }\n"
        "                break;\n",
        "                while (!task.handle.done()) {\n"
        "                    YIELD_GFX();\n"
        "                    RESUME_GFX(task);\n"
        "                }\n"
        "                task.handle.destroy();\n"
        "                break;\n",
        "destroy nested DE coroutine")
    c = one(c,
        "                while (cblock.ce_count <= cblock.de_count && !ce_task.handle.done()) {\n"
        "                    RESUME_GFX(ce_task);\n"
        "                }",
        "                while (cblock.ce_count <= cblock.de_count) {\n"
        "                    YIELD_GFX();\n"
        "                }",
        "yield DE until dedicated CE catches up")
    c = one(c,
        "            dcb = NextPacket(dcb, header->type3.NumWords() + 1);\n",
        "            dcb = NextPacket(dcb, count + 1);\n",
        "stable graphics PM4 size")
    c = one(c,
        "    if (ce_task.handle) {\n"
        "        while (!ce_task.handle.done()) {\n"
        "            RESUME_GFX(ce_task);\n"
        "        }\n"
        "        ce_task.handle.destroy();\n"
        "    }\n\n",
        "",
        "DE no longer owns CE coroutine")
    c = one(c,
        "    CmdBuffer owned_buffers{};\n"
        "    if (EmulatorSettings.IsCopyGpuBuffers()) {\n"
        "        owned_buffers = CopyCmdBuffers(dcb, ccb);\n"
        "        dcb = owned_buffers.first;\n"
        "        ccb = owned_buffers.second;\n"
        "    }\n\n"
        "    // Moving these vectors preserves spans into their allocations. The\n"
        "    // graphics coroutine owns both allocations across asynchronous PM4 work.\n"
        "    auto task = ProcessGraphics(dcb, ccb, std::move(owned_buffers));\n"
        "    {\n"
        "        std::scoped_lock lock{queue.m_access};\n"
        "        queue.submits.emplace(task.handle);\n"
        "    }\n\n"
        "    std::scoped_lock lk{submit_mutex};\n"
        "    ++num_submits;\n"
        "    submit_cv.notify_one();",
        "    std::shared_ptr<CmdBuffer> owned_buffers{};\n"
        "    if (EmulatorSettings.IsCopyGpuBuffers()) {\n"
        "        owned_buffers = std::make_shared<CmdBuffer>(CopyCmdBuffers(dcb, ccb));\n"
        "        dcb = owned_buffers->first;\n"
        "        ccb = owned_buffers->second;\n"
        "    }\n\n"
        "    // Both tasks must keep the same buffers alive while suspended.\n"
        "    auto task = ProcessGraphics(dcb, owned_buffers);\n"
        "    Task ce_task{};\n"
        "    if (!ccb.empty()) ce_task = ProcessCeUpdate(ccb, owned_buffers);\n"
        "    {\n"
        "        std::scoped_lock lock{submit_mutex, queue.m_access};\n"
        "        if (ce_task.handle) {\n"
        "            ce_submits.emplace(ce_task.handle);\n"
        "            ++num_submits;\n"
        "        }\n"
        "        queue.submits.emplace(task.handle);\n"
        "        ++num_submits;\n"
        "        submit_cv.notify_one();\n"
        "    }",
        "separate CE+DE submissions with shared PM4 ownership")
    return c

def audit(h: str, c: str) -> None:
    expected = [
        "std::shared_ptr<CmdBuffer>", "std::queue<Task::Handle> ce_submits",
        "void Liverpool::ProcessCeQueue()", MARKER,
        "const u32 packet_words = header->type3.NumWords() + 1",
        "if (indirect_buffer->chain)", "std::make_shared<CmdBuffer>",
        "ProcessCeUpdate(ccb, owned_buffers)", "ProcessCeQueue();"
    ]
    all_text = h + c
    missing = [item for item in expected if item not in all_text]
    obsolete = ["cblock.Reset();", "dcb copy buffer out of reserved space",
                "ccb copy buffer out of reserved space", "!ce_task.handle.done()"]
    old = [x for x in obsolete if x in c]
    if missing or old:
        raise RuntimeError(f"Release 0.2.6 CE parity missing={missing} obsolete={old}")

def apply(root: Path) -> dict:
    h_path = root / "src/video_core/amdgpu/liverpool.h"
    c_path = root / "src/video_core/amdgpu/liverpool.cpp"
    h, c = h_path.read_text(), c_path.read_text()
    if MARKER in c:
        audit(h, c)
        return {"status": "already-applied"}
    hh = patch_header(h)
    cc = patch_source(c)
    audit(hh, cc)
    h_path.write_text(hh)
    c_path.write_text(cc)
    return {"status": "applied", "release": "0.2.6",
            "copyOwnership": "shared between DE and CE coroutines",
            "ceQueue": "independent", "pm4Size": "snapshotted",
            "ibChains": "respected", "counterUnderflow": "guarded"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["apply", "audit"])
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    print(apply(args.source) if args.command == "apply" else
          audit((args.source / "src/video_core/amdgpu/liverpool.h").read_text(),
                (args.source / "src/video_core/amdgpu/liverpool.cpp").read_text()))
