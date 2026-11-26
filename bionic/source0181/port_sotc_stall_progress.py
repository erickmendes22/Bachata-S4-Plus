#!/usr/bin/env python3
"""Preserve SotC command-stream progress across supported PM4 boundaries."""
from pathlib import Path


WAIT_HELPERS = r'''static bool SotcCommandWaitEnabled() {
    const auto serial = Common::ElfInfo::Instance().GameSerial();
    return serial == "CUSA08809" || serial == "CUSA08034";
}

static u64 SotcCommandWaitNowNs() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}

static void SotcCommandPause() {
#if defined(__x86_64__) || defined(_M_X64)
    __builtin_ia32_pause();
#elif defined(__aarch64__)
    __asm__ __volatile__("yield" ::: "memory");
#endif
}

void Liverpool::NoteCommandWait(const char* reason, VAddr address, u64 reference,
                               u64 mask, u64 observed, u32 function, bool& first_poll, u32 qid) {
    if (!SotcCommandWaitEnabled()) return;
    if (first_poll) {
        cp_progress = true;
        first_poll = false;
    }
    cp_wait = {reason, address, reference, mask, observed, function, qid, true};
}

void Liverpool::ResetCommandWaitProgress() {
    cp_stalled = 0;
    cp_stall_since_ns = 0;
    cp_wait_reported = false;
    cp_wait.active = false;
}

void Liverpool::BackoffCommandWait(std::stop_token stoken) {
    if (!SotcCommandWaitEnabled()) return;
    // The active donor backs off only after a pass without progress. The
    // predicate is still polled; a timeout never makes a PM4 wait succeed.
    const u32 queues = std::max(num_mapped_queues.load(std::memory_order_acquire), 1u);
    if (++cp_stalled < queues || cp_stalled % queues != 0) return;
    static const bool yield_few_cores = [] {
        const char* option = std::getenv("SOTC_CP_YIELD");
        return (!option || option[0] != '0') && std::thread::hardware_concurrency() <= 6;
    }();
    if (cp_stalled / queues <= 32) {
        if (yield_few_cores) std::this_thread::yield();
        else for (u32 i = 0; i < 16; ++i) SotcCommandPause();
        return;
    }
    const u64 now_ns = SotcCommandWaitNowNs();
    if (!cp_stall_since_ns) cp_stall_since_ns = now_ns;
    const u64 elapsed_ns = now_ns - cp_stall_since_ns;
    if (elapsed_ns < 500'000) {
        std::this_thread::yield();
        return;
    }
    if (!cp_wait_reported && cp_wait.active && elapsed_ns >= 2'000'000'000ULL) {
        cp_wait_reported = true;
        u64 tick = 0, submitted = 0, gpu = 0;
        if (rasterizer) {
            auto& scheduler = rasterizer->GetScheduler();
            tick = scheduler.CurrentTick();
            submitted = scheduler.RecordedSubmitTick();
            gpu = scheduler.GetWorkSemaphore()->KnownGpuTick();
        }
        // Only CP-owned wait data and published atomic counters are sampled.
        // No clock read or diagnostic string construction occurs per DWORD.
        LOG_WARNING(Render_Vulkan,
            "BACHATA_GPU_WAIT phase=cp_predicate reason={} qid={} address={:#x} reference={:#x} "
            "mask={:#x} observed={:#x} function={} commands={} submits={} tick={} submitted={} gpu={} elapsed_ms={}",
            cp_wait.reason, cp_wait.qid, cp_wait.address, cp_wait.reference, cp_wait.mask,
            cp_wait.observed, cp_wait.function, num_commands.load(std::memory_order_relaxed),
            num_submits.load(std::memory_order_relaxed), tick, submitted, gpu,
            elapsed_ns / 1'000'000);
    }
    const u32 submits = num_submits.load(std::memory_order_relaxed);
    std::unique_lock lk{submit_mutex};
    submit_cv.wait_for(lk, std::chrono::microseconds(100), [&] {
        return stoken.stop_requested() || num_commands.load(std::memory_order_relaxed) ||
               num_submits.load(std::memory_order_relaxed) != submits;
    });
}

'''

WAIT_MEMBERS = r'''    void NoteCommandWait(const char* reason, VAddr address, u64 reference,
                         u64 mask, u64 observed, u32 function, bool& first_poll, u32 qid);
    void ResetCommandWaitProgress();
    void BackoffCommandWait(std::stop_token stoken);
    // All state below belongs to the CP thread, including its CE coroutine.
    struct CpWaitState {
        const char* reason{};
        VAddr address{};
        u64 reference{}, mask{}, observed{};
        u32 function{}, qid{};
        bool active{};
    } cp_wait;
    bool cp_progress{};
    u32 cp_stalled{};
    u64 cp_stall_since_ns{};
    bool cp_wait_reported{};

'''


def one(text, old, new, label):
    if text.count(old) != 1:
        raise RuntimeError(f"SotC wait progress anchor drift {label}: {text.count(old)}")
    return text.replace(old, new, 1)


def adapt_wait_case(source, name, yield_call, kind):
    start = source.index(f"case PM4ItOpcode::{name}: {{")
    end = source.index("\n            break;\n        }", start) + len("\n            break;\n        }") if kind == "asc" else source.index("\n                break;\n            }", start) + len("\n                break;\n            }")
    body = source[start:end]
    indent = "                " if kind == "gfx" else "            "
    if name == "WaitRegMem":
        old = f"{indent}while (!wait_reg_mem->Test(regs.reg_array)) {{\n{indent}    {yield_call}"
        new = f'''{indent}bool first_poll = true;
{indent}u32 observed = 0;
{indent}while (!wait_reg_mem->Test(regs.reg_array, &observed)) {{
{indent}    const bool memory_wait = wait_reg_mem->mem_space.Value() == PM4CmdWaitRegMem::MemSpace::Memory;
{indent}    NoteCommandWait(memory_wait ? "wait_reg_mem_memory" : "wait_reg_mem_register",
{indent}                    memory_wait ? wait_reg_mem->Address<VAddr>() : wait_reg_mem->Reg(),
{indent}                    wait_reg_mem->ref, wait_reg_mem->mask, observed,
{indent}                    u32(wait_reg_mem->function.Value()), first_poll, curr_qid);
{indent}    {yield_call}'''
    elif name == "MemSemaphore":
        indent += "    "
        old = f"{indent}while (!mem_semaphore->Signaled()) {{\n{indent}    {yield_call}"
        new = f'''{indent}bool first_poll = true;
{indent}u64 observed = 0;
{indent}while (!mem_semaphore->Signaled(&observed)) {{
{indent}    NoteCommandWait("mem_semaphore", mem_semaphore->Address<VAddr>(), 0,
{indent}                    ~u64{{0}}, observed, u32(PM4CmdWaitRegMem::Function::GreaterThan), first_poll, curr_qid);
{indent}    {yield_call}'''
    elif name == "Rewind":
        old = f"{indent}while (!rewind->Valid()) {{\n{indent}    {yield_call}"
        new = f'''{indent}bool first_poll = true;
{indent}u32 observed = 0;
{indent}while (!rewind->Valid(&observed)) {{
{indent}    NoteCommandWait("rewind_valid_bit", std::bit_cast<VAddr>(rewind) + sizeof(u32),
{indent}                    1, 1, observed, u32(PM4CmdWaitRegMem::Function::Equal), first_poll, curr_qid);
{indent}    {yield_call}'''
    else:
        raise AssertionError(name)
    body = one(body, old, new, f"{kind}/{name}")
    return source[:start] + body + source[end:]


def apply(root: Path) -> dict:
    directory = Path(root) / "src/video_core/amdgpu"
    path = directory / "liverpool.cpp"
    text = path.read_text()
    header = (directory / "liverpool.h").read_text()
    wire = (directory / "pm4_cmds.h").read_text()
    start = text.index("Liverpool::Task Liverpool::ProcessCompute(")
    before = text[:start]
    compute = text[start:]
    old = "        u32 next_dw_off = header->type3.NumWords() + 1;"
    if compute.count(old) != 1:
        raise RuntimeError("SotC ASC packet framing source drift")
    compute = compute.replace(old, """        // BACHATA_SOTC_ASC_PACKET_BOUNDARY: Type-2 is one DWORD. Its remaining
        // bits are not a Type-3 count, including at the final ring/submission word.
        // Classify it before the split check or the next packet loses its header.
        u32 next_dw_off = header->type == 2 ? 1 : header->type3.NumWords() + 1;""", 1)
    text = before + compute
    for include in ("#include <algorithm>", "#include <chrono>"):
        if include not in text.splitlines():
            text = include + "\n" + text
    text = one(text, "void Liverpool::ProcessCommands() {",
               WAIT_HELPERS + "void Liverpool::ProcessCommands() {", "wait helpers")
    header = one(header, "    void ProcessCommands();", WAIT_MEMBERS + "    void ProcessCommands();",
                 "CP state and declarations")
    header = one(header, "    u32 num_mapped_queues{1u}; // GFX is always available",
                 "    std::atomic<u32> num_mapped_queues{1u}; // GFX is always available",
                 "ASC queue-limit publication")
    text = one(text, "            curr_qid = (curr_qid + 1) % num_mapped_queues;",
               "            curr_qid = (curr_qid + 1) % num_mapped_queues.load(std::memory_order_acquire);",
               "CP acquire of published queues")
    text = one(text, """    const auto& task = ProcessCompute(acb, vqid);
    {
        std::scoped_lock lock{queue.m_access};
        queue.submits.emplace(task.handle);
    }

    std::scoped_lock lk{submit_mutex};
    num_mapped_queues = std::max(num_mapped_queues, gnm_vqid + 1);
    ++num_submits;
    submit_cv.notify_one();""", """    const auto& task = ProcessCompute(acb, vqid);
    // Publish the configured queue, its task and its submission count as one
    // transaction. A previously known ASC queue must not be consumed between
    // enqueue and ++num_submits; new queue readers acquire after preparation.
    std::scoped_lock lock{submit_mutex, queue.m_access};
    queue.submits.emplace(task.handle);
    ++num_submits;
    num_mapped_queues.store(
        std::max(num_mapped_queues.load(std::memory_order_relaxed), gnm_vqid + 1),
        std::memory_order_release);
    submit_cv.notify_one();""", "ASC enqueue and configuration publication")
    text = one(text, """        callback();
    }
}

void Liverpool::Process(std::stop_token stoken)""", """        callback();
        cp_progress = true;
    }
}

void Liverpool::Process(std::stop_token stoken)""", "command progress")
    text = one(text, """    task.resume();
    if (task.done()) {
        task.destroy();
        std::scoped_lock lock{queue.m_access};
        ce_submits.pop();""", """    task.resume();
    if (task.done()) {
        cp_progress = true;
        task.destroy();
        std::scoped_lock lock{queue.m_access};
        ce_submits.pop();""", "CE completion progress")
    text = one(text, """        curr_qid = -1;

        while ((num_submits || num_commands) && !stoken.stop_requested()) {
            ProcessCommands();""", """        curr_qid = -1;
        ResetCommandWaitProgress();

        while ((num_submits || num_commands) && !stoken.stop_requested()) {
            cp_progress = false;
            ProcessCommands();""", "iteration progress")
    text = one(text, """                if (queue.submits.empty()) {
                    continue;
                }
                task = queue.submits.front();
            }
            task.resume();
            DrainDrawQueue();

            if (task.done()) {""", """                if (!queue.submits.empty()) task = queue.submits.front();
            }
            // Do not sleep while holding a queue lock: another producer may be
            // the one that satisfies this wait. CE-only work is serviced above.
            if (!task) {
                if (cp_progress) ResetCommandWaitProgress();
                else BackoffCommandWait(stoken);
                continue;
            }
            task.resume();
            DrainDrawQueue();
            if (cp_progress || task.done()) ResetCommandWaitProgress();
            else BackoffCommandWait(stoken);

            if (task.done()) {""", "resume progress/backoff")
    # The old VO optimization slept inside the only CP thread. A non-EOP flip
    # arriving afterwards is a SendCommand, so its producer could never run.
    text = one(text, """                if (vo_port->IsVoLabel(wait_addr) &&
                    num_submits == mapped_queues[GfxQueueId].submits.size()) {""", """                // BACHATA_SOTC_COOPERATIVE_VO_WAIT: retain the actual predicate,
                // but let the CP service later flip/readback commands between polls.
                if (!SotcCommandWaitEnabled() && vo_port->IsVoLabel(wait_addr) &&
                    num_submits == mapped_queues[GfxQueueId].submits.size()) {""", "cooperative VO wait")
    gfx_start = text.index("Liverpool::Task Liverpool::ProcessGraphics(")
    asc_start = text.index("Liverpool::Task Liverpool::ProcessCompute(")
    prefix, gfx, asc = text[:gfx_start], text[gfx_start:asc_start], text[asc_start:]
    for name in ("WaitRegMem", "MemSemaphore", "Rewind"):
        gfx = adapt_wait_case(gfx, name, "YIELD_GFX();", "gfx")
        asc = adapt_wait_case(asc, name, "YIELD_ASC(vqid);", "asc")
    text = prefix + gfx + asc
    text = one(text, """            const auto diff = it_body[0];
            while (cblock.ce_count >= cblock.de_count &&
                   cblock.ce_count - cblock.de_count >= diff) {
                YIELD_CE();""", """            const auto diff = it_body[0];
            bool first_poll = true;
            while (cblock.ce_count >= cblock.de_count &&
                   cblock.ce_count - cblock.de_count >= diff) {
                NoteCommandWait("ce_de_counter_difference", 0, diff, ~u32{0},
                                cblock.ce_count - cblock.de_count,
                                u32(PM4CmdWaitRegMem::Function::LessThan), first_poll, GfxQueueId);
                YIELD_CE();""", "CE counter wait")
    text = one(text, """            case PM4ItOpcode::WaitOnCeCounter: {
                while (cblock.ce_count <= cblock.de_count) {
                    YIELD_GFX();""", """            case PM4ItOpcode::WaitOnCeCounter: {
                bool first_poll = true;
                while (cblock.ce_count <= cblock.de_count) {
                    NoteCommandWait("ce_counter", 0, cblock.de_count, ~u32{0}, cblock.ce_count,
                                    u32(PM4CmdWaitRegMem::Function::GreaterThan), first_poll, GfxQueueId);
                    YIELD_GFX();""", "DE counter wait")
    wire = one(wire, """    bool Test(std::span<const u32> regs) const {
        u32 value = mem_space.Value() == MemSpace::Memory ? *Address() : regs[Reg()];""", """    bool Test(std::span<const u32> regs, u32* observed = nullptr) const {
        u32 value = mem_space.Value() == MemSpace::Memory ? *Address() : regs[Reg()];
        if (observed) *observed = value;""", "capture actual wait observation")
    wire = one(wire, """    [[nodiscard]] bool Signaled() const {
        return *Address<u64*>() > 0;
    }""", """    [[nodiscard]] bool Signaled(u64* observed = nullptr) const {
        const u64 value = *Address<u64*>();
        if (observed) *observed = value;
        return value > 0;
    }""", "capture semaphore observation")
    wire = one(wire, """    bool Valid() const {
        return valid;
    }""", """    bool Valid(u32* observed = nullptr) const {
        const u32 value = valid.Value();
        if (observed) *observed = value;
        return value;
    }""", "capture rewind observation")
    # Check every anchor before publishing the generated files.
    path.write_text(text)
    (directory / "liverpool.h").write_text(header)
    (directory / "pm4_cmds.h").write_text(wire)
    return {
        "ascFraming": "Type-2 is one DWORD before split-packet assembly, as in active SotC donor",
        "cooperativeVoWait": "SotC keeps the predicate and services late CP commands between polls",
        "cpBackoff": "donor pause/yield/100us wait policy; commands and stop wake the wait",
        "ascPublication": "enqueue/count under both locks, queue limit published release/acquire",
        "diagnostic": "one compact sample after two seconds without progress; no per-DWORD clock",
        "preserved": "read-pointer publication, FIFO scheduling, Type-3 ownership and wait comparisons",
        "scope": "SotC core PM4 parser; no CPU/backend/frontend change",
    }
