#!/usr/bin/env python3
"""Keep GPU preparation and vblank progressing across presentation backpressure.

The Android Order donor supplies the nonblocking producer/frame acquisition and
separate presentation worker. This adapts the complete ownership protocol to
FEX's CP + Draw producers, preserves FIFO across retries and owns callback life.
Apply after frame pacing, WSI and DrawPipe overlays in either effective core.
"""
from pathlib import Path
import re


POLICY = '''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "common/elf_info.h"
namespace Common::PresentQueueProgress {
inline bool Enabled() {
#if defined(__ANDROID__) && defined(SHADPS4_ENABLE_FEX_GUEST_CPU)
    const auto serial = Common::ElfInfo::Instance().GameSerial();
    return serial == "CUSA00785" || serial == "CUSA08809" || serial == "CUSA08034";
#else
    return false;
#endif
}
}
'''

GET_FRAME = '''Frame* Presenter::GetRenderFrame(u32 width, u32 height, bool allow_wait) {
    // BACHATA_PRESENT_QUEUE_PROGRESS: neither FEX GPU producer may wait for
    // presentation. The missing fence can depend on work it has yet to submit.
    // Idle blank work also polls: it must never occupy the only swap worker
    // waiting for frames whose presentation is queued behind that idle work.
    const bool progress = Common::PresentQueueProgress::Enabled();
    const bool gpu_owner = liverpool &&
        (liverpool->OnDrawThread() ||
         std::this_thread::get_id() == liverpool->GetGpuCommandProcessorThread());
    const bool poll = progress && (gpu_owner || !allow_wait);
    Frame* frame;
    {
        std::unique_lock lock{free_mutex};
        if (poll) {
            if (free_queue.empty()) {
                frame_pool_empty.fetch_add(1, std::memory_order_relaxed);
                return nullptr;
            }
        } else {
            free_cv.wait(lock, [this] { return !free_queue.empty(); });
        }
        frame = free_queue.front();
        free_queue.pop();
    }
    const vk::Device device = instance.GetDevice();
    for (;;) {
        const auto result = device.waitForFences(
            frame->present_done, false, poll ? 0ULL : std::numeric_limits<u64>::max());
        if (result == vk::Result::eSuccess) break;
        if (result == vk::Result::eTimeout && poll) {
            frame_fence_pending.fetch_add(1, std::memory_order_relaxed);
            std::scoped_lock lock{free_mutex};
            free_queue.push(frame);
            free_cv.notify_one();
            return nullptr;
        }
        if (result == vk::Result::eTimeout) continue;
        UNREACHABLE_MSG("GetRenderFrame fence wait failed: {}", vk::to_string(result));
    }
    if (!width || !height) {
        width = expected_frame_width;
        height = expected_frame_height;
    }
    if (frame->width != width || frame->height != height ||
        frame->is_hdr != swapchain.GetHDR()) {
        RecreateFrame(frame, width, height);
    }
    return frame;
}'''

DISCARD_FRAME = '''void Presenter::DiscardFrame(Frame* frame) {
    if (!frame) return;
    // A prepared but cancelled flip has no presentation fence submission.
    // Its producing work still owns the image: retire that real timeline
    // before returning it to the pool. This runs only on the swap worker.
    if (frame->ready_semaphore == draw_scheduler.GetWorkSemaphore()->Handle()) {
        draw_scheduler.WaitSubmitted(frame->ready_tick, false);
    }
    const vk::SemaphoreWaitInfo wait{
        .semaphoreCount = 1, .pSemaphores = &frame->ready_semaphore,
        .pValues = &frame->ready_tick};
    const auto result = instance.GetDevice().waitSemaphores(wait, ~u64{0});
    ASSERT_MSG(result == vk::Result::eSuccess,
               "Cancelled frame ready wait failed: {}", vk::to_string(result));
    std::scoped_lock lock{free_mutex};
    free_queue.push(frame);
    free_cv.notify_one();
}'''

DESTRUCTOR = '''VideoOutDriver::~VideoOutDriver() {
    // Stop publication and its wait predicate use the same mutex. Queued CP
    // callbacks own only callback_lifetime; clearing owner also waits for an
    // already executing callback, before any member of this driver is freed.
    {
        std::scoped_lock lock{mutex};
        stopping.store(true, std::memory_order_release);
        present_thread.request_stop();
    }
    request_cv.notify_all();
    if (present_progress_enabled) Close(1);
    {
        std::scoped_lock lock{callback_lifetime->mutex};
        callback_lifetime->owner = nullptr;
    }
    if (present_thread.joinable()) present_thread.join();
    {
        std::scoped_lock lock{swap_mutex};
        swap_thread.request_stop();
    }
    swap_cv.notify_all();
    if (swap_thread.joinable()) swap_thread.join();
}'''

METHODS = '''bool VideoOutDriver::RunPresenter(std::function<void()> work, bool if_idle) {
    if (!present_progress_enabled) {
        work();
        return true;
    }
    if (if_idle) {
        std::scoped_lock lock{mutex};
        if (!requests.empty() || preparing_frame || prepare_queued) return false;
    }
    {
        std::scoped_lock lock{swap_mutex};
        if (stopping.load(std::memory_order_acquire) ||
            (if_idle && (swap_busy || !swap_queue.empty()))) return false;
        swap_queue.push_back(std::move(work));
    }
    swap_cv.notify_one();
    return true;
}

void VideoOutDriver::QueueFrameRetirement(Vulkan::Frame* frame) {
    if (!frame) return;
    // Cleanup is accepted even after stop. The vblank producer is joined
    // before the swap worker is stopped, and that worker drains its queue.
    {
        std::scoped_lock lock{swap_mutex};
        swap_queue.push_back([frame] { presenter->DiscardFrame(frame); });
    }
    swap_cv.notify_one();
}

void VideoOutDriver::SwapThread(std::stop_token token) {
    Common::SetCurrentThreadName("shadPS4:SwapPresent");
    for (;;) {
        std::function<void()> work;
        {
            std::unique_lock lock{swap_mutex};
            swap_busy = false;
            if (!swap_cv.wait(lock, token, [this] { return !swap_queue.empty(); })) return;
            // Stop abandons no prepared frame. Stale flips below become
            // fenced retirement, and cleanup drains before member teardown.
            work = std::move(swap_queue.front());
            swap_queue.pop_front();
            swap_busy = true;
        }
        work();
    }
}

void VideoOutDriver::QueueFramePreparation() {
    {
        std::scoped_lock lock{mutex};
        if (stopping.load(std::memory_order_acquire) || requests.empty() ||
            !requests.front().activated || requests.front().frame ||
            preparing_frame || prepare_queued) return;
        prepare_queued = true;
    }
    // No retry is posted by this callback. A failed poll remains at the FIFO
    // head until the next presentation slot; ProcessCommands cannot spin it.
    liverpool->SendCommand([lifetime = callback_lifetime] {
        std::scoped_lock lock{lifetime->mutex};
        if (lifetime->owner) lifetime->owner->PrepareFrontRequest(true);
    });
}

void VideoOutDriver::PrepareFrontRequest(bool queued) {
    Request request{};
    {
        std::scoped_lock lock{mutex};
        if (queued) prepare_queued = false;
        if (stopping.load(std::memory_order_acquire) || requests.empty() ||
            !requests.front().activated || requests.front().frame ||
            preparing_frame || (!queued && prepare_queued)) return;
        preparing_frame = true;
        request = requests.front();
    }
    // Attribute and address belong to this request, not a later registration.
    // CP callbacks already drain DrawPipe; an EOP producer is itself GpuDraw.
    auto* frame = request.index == -1
        ? presenter->PrepareBlankFrame(false)
        : presenter->PrepareFrame(request.attribute, request.address);
    {
        std::scoped_lock lock{mutex};
        ASSERT_MSG(!requests.empty() && requests.front().sequence == request.sequence,
                   "Presentation FIFO head changed while preparing a frame");
        requests.front().frame = frame;
        preparing_frame = false;
        if (frame) frames_prepared.fetch_add(1, std::memory_order_relaxed);
    }
    if (frame) request_cv.notify_one();
}

VideoOutDriver::Request VideoOutDriver::ReceiveRequest() {
    Request request{};
    {
        std::scoped_lock lock{mutex};
        if (!requests.empty() && requests.front().frame) {
            request = requests.front();
            requests.pop_front();
        }
    }
    if (present_progress_enabled) QueueFramePreparation();
    return request;
}

void VideoOutDriver::NotePresentProgress() {
    if (!present_progress_enabled || (++progress_polls & 63u) != 0) return;
    const u64 accepted = frames_accepted.load(std::memory_order_relaxed);
    if (!accepted) return;
    const auto now = std::chrono::steady_clock::now();
    const u64 shown = frames_presented.load(std::memory_order_relaxed);
    if (shown != progress_last_presented) {
        progress_last_presented = shown;
        progress_since = now;
        progress_reported = now;
        return;
    }
    if (now - progress_reported < std::chrono::seconds(2)) return;
    progress_reported = now;
    u64 pending = 0, head = 0;
    bool queued = false, preparing = false, busy = false;
    u64 swapping = 0;
    {
        std::scoped_lock lock{mutex};
        pending = requests.size();
        if (pending) head = requests.front().sequence;
        queued = prepare_queued;
        preparing = preparing_frame;
    }
    {
        std::scoped_lock lock{swap_mutex};
        busy = swap_busy;
        swapping = swap_queue.size();
    }
    const auto pool = presenter->GetFrameAcquireProgress();
    LOG_WARNING(Lib_VideoOut,
        "BACHATA_GPU_WAIT phase=present_progress accepted={} prepared={} presented={} "
        "pending={} head={} retry={} preparing={} pool_empty={} fence_pending={} "
        "swap_busy={} swap_queue={} idle_ms={}",
        accepted, frames_prepared.load(std::memory_order_relaxed), shown,
        pending, head, queued, preparing, pool.empty, pool.fence_pending, busy, swapping,
        std::chrono::duration_cast<std::chrono::milliseconds>(now - progress_since).count());
}
'''

INTERNAL = '''void VideoOutDriver::SubmitFlipInternal(u64 sequence) {
    bool first = false;
    {
        std::scoped_lock lock{mutex};
        if (stopping.load(std::memory_order_acquire)) return;
        const auto found = std::find_if(requests.begin(), requests.end(),
            [sequence](const Request& request) { return request.sequence == sequence; });
        // Close has already retired this port generation, including callbacks
        // which had not yet reached the GPU owner. Nothing can be republished.
        if (found == requests.end()) return;
        found->activated = true;
        first = found == requests.begin();
    }
    // A later activation does not retry or overtake a deferred FIFO head.
    if (first) PrepareFrontRequest(false);
}'''

SUBMIT = '''bool VideoOutDriver::SubmitFlip(VideoOutPort* port, s32 index,
                                    s64 flip_arg, bool is_eop) {
    std::scoped_lock producer_lock{callback_lifetime->mutex};
    if (callback_lifetime->owner != this || stopping.load(std::memory_order_acquire)) return false;
    if (!present_progress_enabled) return SubmitFlipLegacyProducer(port, index, flip_arg, is_eop);
    u64 sequence = 0;
    {
        std::scoped_lock lock{mutex, port->port_mutex};
        if (!port->is_open) return false;
        if (index != -1 && port->flip_status.flip_pending_num > 16) {
            LOG_ERROR(Lib_VideoOut, "Flip queue is full");
            return false;
        }
        Request request{
            .frame = nullptr, .port = port, .flip_arg = flip_arg, .index = index, .eop = is_eop,
        };
        request.hdr = port->is_hdr;
        request.port_generation = port->generation;
        if (index != -1) {
            const auto& buffer = port->buffer_slots[index];
            ASSERT_MSG(buffer.group_index >= 0, "Trying to flip an unregistered buffer!");
            request.attribute = port->groups[buffer.group_index];
            request.address = buffer.address_left;
        }
        request.sequence = sequence = ++next_request_sequence;
        requests.push_back(request);
        if (is_eop) ++port->flip_status.gc_queue_num;
        ++port->flip_status.flip_pending_num;
        port->flip_status.submit_tsc = Libraries::Kernel::sceKernelReadTsc();
        frames_accepted.fetch_add(1, std::memory_order_relaxed);
    }
    if (is_eop) {
        SubmitFlipInternal(sequence);
    } else {
        // Acceptance fixes FIFO position and owns the port generation and
        // descriptor. GPU activation still occurs in the ordered CP callback.
        liverpool->SendCommand([lifetime = callback_lifetime, sequence] {
            std::scoped_lock lock{lifetime->mutex};
            if (lifetime->owner) lifetime->owner->SubmitFlipInternal(sequence);
        });
    }
    return true;
}'''

FLIP = '''void VideoOutDriver::Flip(const Request& req) {
    if (!present_progress_enabled) {
        FlipPrepared(req);
        return;
    }
    ASSERT_MSG(req.frame, "A deferred flip must not complete or publish labels");
    // HDR, Present and completion share the single swap owner with blank/last.
    // Capture the entire request by value; retries never execute this body.
    if (!RunPresenter([this, req] { FlipPrepared(req); })) {
        QueueFrameRetirement(req.frame);
    }
}'''

BLANK = '''void VideoOutDriver::DrawBlankFrame() {
    RunPresenter([this] {
        if (stopping.load(std::memory_order_acquire)) return;
        const auto empty_frame = presenter->PrepareBlankFrame(true);
        if (empty_frame) presenter->Present(empty_frame, false, false);
    }, true);
}'''

LAST = '''void VideoOutDriver::DrawLastFrame() {
    RunPresenter([this] {
        if (stopping.load(std::memory_order_acquire)) return;
        const auto frame = presenter->PrepareLastFrame();
        if (frame) presenter->Present(frame, true);
    }, true);
}'''

MEMBERS = '''    // The CP may retain a callback after this driver stops. It retains this
    // token, never an unprotected this pointer. Its mutex spans active access.
    struct CallbackLifetime {
        std::recursive_mutex mutex;
        VideoOutDriver* owner{};
    };
    std::shared_ptr<CallbackLifetime> callback_lifetime = std::make_shared<CallbackLifetime>();
    bool present_progress_enabled{};
    std::atomic<bool> stopping{false};
    bool prepare_queued{};
    bool preparing_frame{};
    u64 next_request_sequence{};
    std::atomic<u64> frames_accepted{}, frames_prepared{}, frames_presented{};
    u32 progress_polls{};
    u64 progress_last_presented{};
    std::chrono::steady_clock::time_point progress_since = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point progress_reported = progress_since;
    std::mutex swap_mutex;
    std::condition_variable_any swap_cv;
    std::deque<std::function<void()>> swap_queue;
    bool swap_busy{};
    std::jthread swap_thread;
'''


def block(text, anchor):
    start = text.index(anchor)
    brace = text.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def one(text, old, new, label):
    if text.count(old) != 1:
        raise RuntimeError(f'presentation progress anchor drift {label}: {text.count(old)}')
    return text.replace(old, new, 1)


def apply(root: Path):
    root = Path(root)
    dc_path = root / 'src/core/libraries/videoout/driver.cpp'
    dh_path = dc_path.with_suffix('.h')
    pc_path = root / 'src/video_core/renderer_vulkan/vk_presenter.cpp'
    ph_path = pc_path.with_suffix('.h')
    dc, dh, pc, ph = [path.read_text() for path in (dc_path, dh_path, pc_path, ph_path)]
    if 'BACHATA_PRESENT_QUEUE_PROGRESS' in pc:
        if 'void VideoOutDriver::PrepareFrontRequest(' not in dc:
            raise RuntimeError('incomplete presentation progress overlay')
        return {'alreadyApplied': True}
    for include in ('atomic', 'chrono', 'deque', 'functional', 'memory'):
        if f'#include <{include}>' not in dh:
            dh = one(dh, '#include <condition_variable>',
                     f'#include <{include}>\n#include <condition_variable>', include)
    if '#include <atomic>' not in ph:
        ph = one(ph, '#pragma once', '#pragma once\n#include <atomic>', 'presenter atomics')
    pc = one(pc, '#include "common/debug.h"',
             '#include "common/debug.h"\n#include "common/present_queue_progress.h"', 'presenter policy')
    pc = one(pc, '#include "video_core/buffer_cache/buffer.h"',
             '#include "video_core/amdgpu/liverpool.h"\n#include "video_core/buffer_cache/buffer.h"',
             'complete Liverpool type for producer accessors')
    dc = one(dc, '#include "common/assert.h"',
             '#include "common/assert.h"\n#include "common/present_queue_progress.h"', 'driver policy')
    ph = one(ph, '    void Present(Frame* frame,', '    bool Present(Frame* frame,', 'present result')
    ph, n = re.subn(r'Frame\* GetRenderFrame\(u32 width\s*=\s*0,\s*u32 height\s*=\s*0\);',
                   'Frame* GetRenderFrame(u32 width = 0, u32 height = 0, bool allow_wait = true);', ph)
    if n != 1: raise RuntimeError('presentation frame declaration drift')
    ph = one(ph, '    Frame* PrepareLastFrame();', '''    Frame* PrepareLastFrame();
    void DiscardFrame(Frame* frame);
    struct FrameAcquireProgress { u64 empty, fence_pending; };
    FrameAcquireProgress GetFrameAcquireProgress() const noexcept {
        return {frame_pool_empty.load(std::memory_order_relaxed),
                frame_fence_pending.load(std::memory_order_relaxed)};
    }''', 'acquire observation')
    ph = one(ph, '    std::mutex free_mutex;',
             '    std::atomic<u64> frame_pool_empty{}, frame_fence_pending{};\n    std::mutex free_mutex;',
             'acquire counters')
    pc = one(pc, block(pc, 'Frame* Presenter::GetRenderFrame('), GET_FRAME + '\n\n' + DISCARD_FRAME, 'frame acquisition')
    prepare = block(pc, 'Frame* Presenter::PrepareFrame(')
    # Acquiring a frame is a pure poll before touching image cache/command state.
    m = re.search(r'    Frame\* frame\s*=\s*GetRenderFrame\([^;]+;', prepare)
    if not m: raise RuntimeError('game frame acquisition drift')
    acquire = m.group(0)
    prepare = prepare[:m.start()] + prepare[m.end():]
    # SotC derives native output dimensions locally; retain this policy ahead of
    # the poll. Order already computes width/height from nativeFrame policy.
    body_start = prepare.index('{') + 1
    prefix_end = prepare.index('    const auto frame_subresources')
    prefix = prepare[body_start:prefix_end]
    desc_start = prefix.index('    auto desc =')
    desc_end = prefix.index('    texture_cache.UpdateImage(image_id);') + len('    texture_cache.UpdateImage(image_id);')
    desc = prefix[desc_start:desc_end]
    desc_line, cache_lines = desc.split('\n', 1)
    policy = prefix[:desc_start] + prefix[desc_end:]
    resolved_extent = ''
    if 'texture_cache.GetImage(image_id).info.size' in policy:
        resolved_extent = '''#ifdef __ANDROID__
    // The nonblocking acquisition used the request's pure description. Keep
    // the existing final extent if FindImage selected a larger alias backing.
    // The acquired frame's presentation fence is already retired here.
    if (!BachataCompat::Sotc608() && !fsr_settings.enable) {
        const auto& resolved = texture_cache.GetImage(image_id).info.size;
        if (frame->width != resolved.width || frame->height != resolved.height) {
            RecreateFrame(frame, resolved.width, resolved.height);
        }
    }
#endif
'''
    # The video-out description is owned input. It supplies the intended output
    # extent without touching FindImage/UpdateImage during an unsuccessful poll.
    policy = policy.replace('texture_cache.GetImage(image_id).info.size', 'desc.info.size')
    new_prefix = '\n' + desc_line + '\n' + policy.strip('\n') + '\n' + acquire + '\n    if (!frame) return nullptr;\n' + cache_lines + '\n' + resolved_extent + '\n'
    prepare = prepare[:body_start] + new_prefix + prepare[prefix_end:]
    pc = one(pc, block(pc, 'Frame* Presenter::PrepareFrame('), prepare, 'pure game poll')
    blank = block(pc, 'Frame* Presenter::PrepareBlankFrame(')
    blank = one(blank, '    Frame* frame = GetRenderFrame();',
                '    Frame* frame = GetRenderFrame(0, 0, !present_thread);\n    if (!frame) return nullptr;',
                'blank null')
    pc = one(pc, block(pc, 'Frame* Presenter::PrepareBlankFrame('), blank, 'blank preparation')
    present = block(pc, 'void Presenter::Present(')
    present = present.replace('void Presenter::Present(', 'bool Presenter::Present(', 1)
    # This function has exactly one early return (failed acquisition); all
    # actual QueuePresent outcomes already converge in bool presented.
    present = one(present, '            free_frame(false);\n            return;',
                  '            free_frame(false);\n            return false;', 'failed acquisition result')
    present = present[:-1] + '    return presented;\n}'
    pc = one(pc, block(pc, 'void Presenter::Present('), present, 'actual presented result')
    dh = one(dh, '        bool eop;', '''        bool eop;
        BufferAttributeGroup attribute{};
        VAddr address{};
        bool hdr{};
        u64 sequence{};
        u64 port_generation{};
        bool activated{};''', 'owned request')
    dh = one(dh, '    bool is_hdr = false;', '    bool is_hdr = false;\n    u64 generation{};', 'port generation')
    dh = one(dh, '    std::queue<Request> requests;', '    std::deque<Request> requests;', 'iterable FIFO')
    dh = one(dh, '    void SubmitFlipInternal(VideoOutPort* port, s32 index, s64 flip_arg, bool is_eop = false);',
             '    void SubmitFlipInternal(u64 sequence);', 'GPU activation signature')
    dh = one(dh, '    void Flip(const Request& req);', '''    void Flip(const Request& req);
    void FlipPrepared(const Request& req);
    void SubmitFlipLegacy(VideoOutPort* port, s32 index, s64 flip_arg, bool is_eop);
    bool SubmitFlipLegacyProducer(VideoOutPort* port, s32 index, s64 flip_arg, bool is_eop);
    void PrepareFrontRequest(bool queued);
    void QueueFramePreparation();
    Request ReceiveRequest();
    bool RunPresenter(std::function<void()> work, bool if_idle = false);
    void QueueFrameRetirement(Vulkan::Frame* frame);
    void SwapThread(std::stop_token token);
    void NotePresentProgress();''', 'driver methods')
    if 'std::condition_variable request_cv;' not in dh:
        dh = one(dh, '    std::mutex mutex;\n    VideoOutPort',
                 '    std::mutex mutex;\n    std::condition_variable request_cv;\n    VideoOutPort',
                 'request wake')
    dh = one(dh, '    std::mutex mutex;\n    std::condition_variable request_cv;',
             MEMBERS + '\n    std::mutex mutex;\n    std::condition_variable request_cv;', 'driver state')
    ctor = block(dc, 'VideoOutDriver::VideoOutDriver(')
    ctor = one(ctor, '    present_thread = ', '''    callback_lifetime->owner = this;
    present_progress_enabled = Common::PresentQueueProgress::Enabled();
    if (present_progress_enabled) {
        swap_thread = std::jthread([this](std::stop_token token) { SwapThread(token); });
        LOG_INFO(Lib_VideoOut, "BACHATA_PRESENT_QUEUE_PROGRESS enabled FIFO CP+Draw swap_worker");
    }
    present_thread = ''', 'worker start')
    dc = one(dc, block(dc, 'VideoOutDriver::VideoOutDriver('), ctor, 'constructor')
    if 'VideoOutDriver::~VideoOutDriver() = default;' in dc:
        dc = one(dc, 'VideoOutDriver::~VideoOutDriver() = default;', DESTRUCTOR, 'default destructor')
    else:
        dc = one(dc, block(dc, 'VideoOutDriver::~VideoOutDriver()'), DESTRUCTOR, 'stoppable destructor')
    opened = block(dc, 'int VideoOutDriver::Open(')
    opened = one(opened, '    if (main_port.is_open)',
                 '    std::scoped_lock lifetime_lock{callback_lifetime->mutex};\n'
                 '    std::scoped_lock port_lock{main_port.port_mutex};\n'
                 '    if (main_port.is_open)', 'open publication')
    opened = one(opened, '    main_port.is_open = true;',
                 '    ++main_port.generation;\n    main_port.is_open = true;', 'new port generation')
    dc = one(dc, block(dc, 'int VideoOutDriver::Open('), opened, 'open lifetime')
    closed = block(dc, 'void VideoOutDriver::Close(')
    closed = one(closed, '    std::scoped_lock lock{mutex};', '''    std::scoped_lock lifetime_lock{callback_lifetime->mutex};
    std::scoped_lock lock{mutex, main_port.port_mutex, main_port.vo_mutex};
    ++main_port.generation;
    if (present_progress_enabled) {
        // No preparation can run while this lifetime token is held. Frames
        // already handed to the swap queue validate their captured generation.
        for (const auto& request : requests) QueueFrameRetirement(request.frame);
        requests.clear();
    }''', 'close pending ownership')
    closed = closed[:-1] + '    main_port.vo_cv.notify_all();\n}'
    dc = one(dc, block(dc, 'void VideoOutDriver::Close('), closed, 'close generation')
    old_internal = block(dc, 'void VideoOutDriver::SubmitFlipInternal(')
    legacy = old_internal.replace('void VideoOutDriver::SubmitFlipInternal(',
                                  'void VideoOutDriver::SubmitFlipLegacy(', 1)
    legacy = legacy.replace('requests.push({', 'requests.push_back({')
    dc = one(dc, old_internal, legacy + '\n\n' + INTERNAL + '\n\n' + METHODS, 'request ownership')
    submit = block(dc, 'bool VideoOutDriver::SubmitFlip(')
    submit = one(submit,
        '        liverpool->SendCommand([=, this]() { SubmitFlipInternal(port, index, flip_arg, is_eop); });',
        '''        liverpool->SendCommand([lifetime = callback_lifetime, port, index, flip_arg, is_eop] {
            std::scoped_lock lock{lifetime->mutex};
            if (lifetime->owner) {
                lifetime->owner->SubmitFlipLegacy(port, index, flip_arg, is_eop);
            }
        });''', 'callback lifetime')
    submit = one(submit, '        SubmitFlipInternal(port, index, flip_arg, is_eop);',
                 '        SubmitFlipLegacy(port, index, flip_arg, is_eop);', 'legacy EOP')
    submit = submit.replace('bool VideoOutDriver::SubmitFlip(', 'bool VideoOutDriver::SubmitFlipLegacyProducer(', 1)
    dc = one(dc, block(dc, 'bool VideoOutDriver::SubmitFlip('), SUBMIT + '\n\n' + submit, 'safe producer')
    old_flip = block(dc, 'void VideoOutDriver::Flip(')
    prepared = old_flip.replace('void VideoOutDriver::Flip(', 'void VideoOutDriver::FlipPrepared(', 1)
    prepared = one(prepared, '    // Update HDR status before presenting.', '''    if (present_progress_enabled) {
        bool current;
        {
            std::scoped_lock lock{req.port->port_mutex};
            current = !stopping.load(std::memory_order_acquire) && req.port->is_open &&
                      req.port_generation == req.port->generation;
        }
        if (!current) {
            presenter->DiscardFrame(req.frame);
            return;
        }
    }
    // Update HDR status before presenting.''', 'pre-present generation')
    prepared = one(prepared, '    presenter->SetHDR(req.port->is_hdr);',
                   '    presenter->SetHDR(present_progress_enabled ? req.hdr : req.port->is_hdr);', 'owned HDR')
    prepared = one(prepared, '    presenter->Present(req.frame);',
                   '    const bool presented = presenter->Present(req.frame);', 'actual present result')
    report_start = prepared.index('#ifdef ENABLE_BACHATA_RUNTIME')
    report_end = prepared.index('#endif', report_start) + len('#endif')
    prepared = prepared[:report_start] + prepared[report_end:]
    prepared = one(prepared, '''    // Update flip status.
    auto* port = req.port;
    {
        std::unique_lock lock{port->port_mutex};''', '''    auto* port = req.port;
    // Close/reopen can occur during a real Present. The old frame remains
    // owned by Presenter, but it cannot publish into the new port generation.
    std::unique_lock completion_lock{port->port_mutex};
    if (present_progress_enabled &&
        (!port->is_open || req.port_generation != port->generation)) return;
    if (presented) frames_presented.fetch_add(1, std::memory_order_relaxed);
#ifdef ENABLE_BACHATA_RUNTIME
    if (presented) Platform::Bachata::ReportPresentedFrame();
#endif

    // Update flip status.
    {''', 'completion generation and actual report')
    dc = one(dc, old_flip, FLIP + '\n\n' + prepared, 'swap completion')
    dc = one(dc, block(dc, 'void VideoOutDriver::DrawBlankFrame()'), BLANK, 'serialized blank')
    dc = one(dc, block(dc, 'void VideoOutDriver::DrawLastFrame()'), LAST, 'serialized last')
    pt = block(dc, 'void VideoOutDriver::PresentThread(')
    receive = block(pt, '    const auto receive_request = [this] -> Request') + ';'
    pt = one(pt, receive, '    const auto receive_request = [this]() -> Request { return ReceiveRequest(); };',
             'FIFO receive')
    # A deferred front must not make Order's immediate loop wake/spin. A ready
    # callback notifies it; unsuccessful retries wait for the next vblank.
    pt = pt.replace('token.stop_requested() || !requests.empty()',
                    'token.stop_requested() || (!requests.empty() && requests.front().frame)')
    pt = one(pt, '        timer.Start();',
             '        timer.Start();\n        NotePresentProgress();', 'vblank observer')
    dc = one(dc, block(dc, 'void VideoOutDriver::PresentThread('), pt, 'vblank loop')
    for path, value in ((dc_path, dc), (dh_path, dh), (pc_path, pc), (ph_path, ph)):
        path.write_text(value)
    (root / 'src/common/present_queue_progress.h').write_text(POLICY)
    return {'applied': True, 'family': 'producer frame poll + FIFO retry + independent vblank + safe callbacks'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    print(apply(parser.parse_args().source))
