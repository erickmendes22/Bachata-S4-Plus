#!/usr/bin/env python3
"""Deliver kernel event flags before rescheduling; retain in-flight owners."""
from pathlib import Path


def block(text, marker):
    start = text.index(marker)
    opening = text.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def one(text, old, new, why):
    if text.count(old) != 1:
        raise RuntimeError(f'event-flag delivery anchor drift: {why}: {text.count(old)}')
    return text.replace(old, new, 1)


DELIVERY = r'''// BACHATA_EVENT_FLAG_DELIVERY: Set commits a result to each selected waiter.
// Clearing bits or canceling a later wait cannot retract an already delivered result.
struct EventFlagWaitIdentity {
    s32 priority{700};
    s32 tid{};
    std::array<char, 64> name{};
};

static EventFlagWaitIdentity CaptureEventFlagWaitIdentity() {
    EventFlagWaitIdentity identity{};
    if (g_curthread) {
        // Capture the guest priority, never the host scheduler's priority.
        // Take this before the event lock; a Set never needs a Pthread lock.
        std::scoped_lock lock{g_curthread->lock};
        identity.priority = g_curthread->attr.prio;
        identity.tid = g_curthread->tid.load(std::memory_order_relaxed);
        const auto size = std::min(g_curthread->name.size(), identity.name.size() - 1);
        std::memcpy(identity.name.data(), g_curthread->name.data(), size);
    }
    return identity;
}

struct EventFlagWaitSnapshot {
    VAddr object{};
    std::array<char, 32> name{};
    EventFlagWaitIdentity thread{};
    u64 bits{}, observed{}, age_ms{}, sets{}, delivered{};
    u32 wait_mode{}, clear_mode{}, pending{};
};

class EventFlagInternal {
public:
    enum class ClearMode { None, All, Bits };
    enum class WaitMode { And, Or };
    enum class ThreadMode { Single, Multi };
    enum class QueueMode { Fifo, ThreadPrio };
    using Clock = std::chrono::steady_clock;

    EventFlagInternal(const std::string& name, ThreadMode thread_mode, QueueMode queue_mode,
                      uint64_t bits)
        : m_name(name), m_thread_mode(thread_mode), m_queue_mode(queue_mode), m_bits(bits) {}

    int Wait(u64 bits, WaitMode wait_mode, ClearMode clear_mode, u64* result, u32* ptr_micros) {
        const bool may_block = !ptr_micros || *ptr_micros != 0;
        const auto identity = may_block ? CaptureEventFlagWaitIdentity() : EventFlagWaitIdentity{};
        std::unique_lock lock{m_mutex};
        if (m_deleted) return ORBIS_KERNEL_ERROR_EACCES;
        if (m_thread_mode == ThreadMode::Single && PendingCount() != 0)
            return ORBIS_KERNEL_ERROR_EPERM;
        if (Satisfied(bits, wait_mode)) {
            if (result) *result = m_bits;
            Consume(bits, clear_mode);
            return ORBIS_OK;
        }
        const auto start = Clock::now();
        const u32 micros = ptr_micros ? *ptr_micros : 0;
        if (ptr_micros && !micros) {
            if (result) *result = m_bits;
            return ORBIS_KERNEL_ERROR_ETIMEDOUT;
        }

        Waiter waiter{};
        waiter.bits = bits;
        waiter.wait_mode = wait_mode;
        waiter.clear_mode = clear_mode;
        waiter.thread = identity;
        waiter.since = start;
        waiter.sets_at_entry = m_sets;
        Enqueue(waiter);
        // Unlink before the stack waiter dies, including exceptional host waits.
        struct Registration {
            EventFlagInternal& flag;
            Waiter& waiter;
            ~Registration() { flag.Unlink(waiter); }
        } registration{*this, waiter};
        const auto complete = [&] { return waiter.state != WaitState::Pending; };
        bool finished = true;
        if (ptr_micros) {
            finished = waiter.cv.wait_until(lock, start + std::chrono::microseconds(micros), complete);
            const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(Clock::now() - start).count();
            *ptr_micros = elapsed >= micros ? 0 : micros - static_cast<u32>(elapsed);
        } else {
            // Diagnostics inspect owned snapshots from the existing presenter.
            // Infinite guest waits have no periodic diagnostic wakeups.
            waiter.cv.wait(lock, complete);
        }
        if (!finished) {
            if (result) *result = m_bits;
            *ptr_micros = 0;
            return ORBIS_KERNEL_ERROR_ETIMEDOUT;
        }
        if (result) *result = waiter.result;
        if (waiter.state == WaitState::Canceled) return ORBIS_KERNEL_ERROR_ECANCELED;
        if (waiter.state == WaitState::Deleted) return ORBIS_KERNEL_ERROR_EACCES;
        return ORBIS_OK;
    }

    int Poll(u64 bits, WaitMode wait_mode, ClearMode clear_mode, u64* result) {
        u32 micros = 0;
        const int rc = Wait(bits, wait_mode, clear_mode, result, &micros);
        return rc == ORBIS_KERNEL_ERROR_ETIMEDOUT ? ORBIS_KERNEL_ERROR_EBUSY : rc;
    }

    int Set(u64 bits) {
        std::scoped_lock lock{m_mutex};
        if (m_deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        ++m_sets;
        m_bits |= bits;
        for (auto* waiter = m_waiters; waiter; waiter = waiter->next) {
            if (waiter->state != WaitState::Pending || !Satisfied(waiter->bits, waiter->wait_mode)) continue;
            waiter->result = m_bits;
            Consume(waiter->bits, waiter->clear_mode);
            waiter->state = WaitState::Delivered;
            ++m_delivered;
            waiter->cv.notify_one();
        }
        return ORBIS_OK;
    }

    int Clear(u64 bits) {
        std::scoped_lock lock{m_mutex};
        if (m_deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        m_bits &= bits;
        return ORBIS_OK;
    }

    int Cancel(u64 set_pattern, int* count) {
        std::scoped_lock lock{m_mutex};
        if (m_deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        int canceled = 0;
        m_bits = set_pattern;
        for (auto* waiter = m_waiters; waiter; waiter = waiter->next) {
            if (waiter->state != WaitState::Pending) continue;
            waiter->result = set_pattern;
            waiter->state = WaitState::Canceled;
            waiter->cv.notify_one();
            ++canceled;
        }
        if (count) *count = canceled;
        return ORBIS_OK;
    }

    int Delete() {
        std::scoped_lock lock{m_mutex};
        if (m_deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        m_deleted = true;
        for (auto* waiter = m_waiters; waiter; waiter = waiter->next) {
            if (waiter->state != WaitState::Pending) continue;
            waiter->result = m_bits;
            waiter->state = WaitState::Deleted;
            waiter->cv.notify_one();
        }
        return ORBIS_OK;
    }

    bool TrySnapshotWait(Clock::time_point now, EventFlagWaitSnapshot& out) {
        std::unique_lock lock{m_mutex, std::try_to_lock};
        if (!lock || m_deleted) return false;
        for (auto* waiter = m_waiters; waiter; waiter = waiter->next) {
            if (waiter->state != WaitState::Pending || waiter->reported ||
                now - waiter->since < std::chrono::seconds(5)) continue;
            out = {};
            out.object = reinterpret_cast<VAddr>(this);
            std::memcpy(out.name.data(), m_name.data(), std::min(m_name.size(), out.name.size() - 1));
            out.thread = waiter->thread;
            out.bits = waiter->bits;
            out.observed = m_bits;
            out.wait_mode = waiter->wait_mode == WaitMode::And ? 1 : 2;
            out.clear_mode = waiter->clear_mode == ClearMode::All ? 0x10 :
                             waiter->clear_mode == ClearMode::Bits ? 0x20 : 0;
            out.age_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now - waiter->since).count();
            out.pending = PendingCount();
            out.sets = m_sets - waiter->sets_at_entry;
            out.delivered = m_delivered;
            waiter->reported = true;
            return true;
        }
        return false;
    }

private:
    enum class WaitState { Pending, Delivered, Canceled, Deleted };
    struct Waiter {
        std::condition_variable cv;
        u64 bits{}, result{}, sets_at_entry{};
        WaitMode wait_mode{};
        ClearMode clear_mode{};
        WaitState state{WaitState::Pending};
        EventFlagWaitIdentity thread{};
        Clock::time_point since{};
        Waiter* next{};
        bool reported{};
    };

    bool Satisfied(u64 bits, WaitMode mode) const {
        return mode == WaitMode::And ? (m_bits & bits) == bits : (m_bits & bits) != 0;
    }
    void Consume(u64 bits, ClearMode mode) {
        if (mode == ClearMode::All) m_bits = 0;
        else if (mode == ClearMode::Bits) m_bits &= ~bits;
    }
    u32 PendingCount() const {
        u32 count = 0;
        for (auto* waiter = m_waiters; waiter; waiter = waiter->next)
            count += waiter->state == WaitState::Pending;
        return count;
    }
    void Enqueue(Waiter& waiter) {
        auto** next = &m_waiters;
        // Lower numeric guest priority is serviced first. Equal priorities
        // retain arrival order; FIFO ignores priority altogether.
        while (*next && (m_queue_mode == QueueMode::Fifo ||
                        (*next)->thread.priority <= waiter.thread.priority)) next = &(*next)->next;
        waiter.next = *next;
        *next = &waiter;
    }
    void Unlink(Waiter& waiter) {
        auto** next = &m_waiters;
        while (*next != &waiter) next = &(*next)->next;
        *next = waiter.next;
    }

    std::mutex m_mutex;
    bool m_deleted{};
    std::string m_name;
    ThreadMode m_thread_mode;
    QueueMode m_queue_mode;
    u64 m_bits{}, m_sets{}, m_delivered{};
    Waiter* m_waiters{};
};

// Handles retain the existing pointer ABI. A lookup pins the state before any
// blocking operation, and Delete removes lookup visibility before revocation.
// No registry lock is held during a wait or a logger call.
struct EventFlagRegistry {
    std::mutex mutex;
    std::unordered_map<EventFlagInternal*, std::shared_ptr<EventFlagInternal>> flags;
    u32 wait_reports{};
    EventFlagInternal::Clock::time_point last_report{};
};

static EventFlagRegistry& EventFlags() {
    // Registry lifetime covers guest thread teardown. Individual deleted
    // objects are reclaimed as soon as their last in-flight call returns.
    static auto* registry = new EventFlagRegistry;
    return *registry;
}

static std::shared_ptr<EventFlagInternal> FindEventFlag(EventFlagInternal* handle) {
    auto& registry = EventFlags();
    std::scoped_lock lock{registry.mutex};
    const auto it = registry.flags.find(handle);
    return it == registry.flags.end() ? nullptr : it->second;
}

static std::shared_ptr<EventFlagInternal> RemoveEventFlag(EventFlagInternal* handle) {
    auto& registry = EventFlags();
    std::scoped_lock lock{registry.mutex};
    const auto it = registry.flags.find(handle);
    if (it == registry.flags.end()) return nullptr;
    auto flag = std::move(it->second);
    registry.flags.erase(it);
    return flag;
}

void ReportEventFlagWaits() {
    auto& registry = EventFlags();
    std::array<EventFlagWaitSnapshot, 4> snapshots{};
    u32 count = 0;
    const auto now = EventFlagInternal::Clock::now();
    {
        std::unique_lock lock{registry.mutex, std::try_to_lock};
        if (!lock || registry.wait_reports >= 32 ||
            now - registry.last_report < std::chrono::seconds(2)) return;
        registry.last_report = now;
        for (const auto& [handle, flag] : registry.flags) {
            if (count == snapshots.size() || registry.wait_reports == 32) break;
            if (!flag->TrySnapshotWait(now, snapshots[count])) continue;
            ++count;
            ++registry.wait_reports;
        }
    }
    // Only owned values remain; neither event nor registry mutex is held.
    for (u32 i = 0; i < count; ++i) {
        const auto& wait = snapshots[i];
        LOG_WARNING(Kernel_Event,
            "BACHATA_GUEST_WAIT phase=event_flag name={} object={:#x} thread={} tid={} "
            "bits={:#x} observed={:#x} mode={:#x} priority={} age_ms={} pending={} sets={} delivered={}",
            wait.name.data(), wait.object, wait.thread.name.data(), wait.thread.tid,
            wait.bits, wait.observed, wait.wait_mode | wait.clear_mode, wait.thread.priority,
            wait.age_ms, wait.pending, wait.sets, wait.delivered);
    }
}
'''

PROGRESS = '''    struct PendingCommandProgress {
        u32 commands{}, submits{};
        bool submit_done{};
    };
    PendingCommandProgress GetPendingCommandProgress() const noexcept {
        return {num_commands.load(std::memory_order_relaxed),
                num_submits.load(std::memory_order_relaxed),
                submit_done.load(std::memory_order_relaxed)};
    }

'''


def apply(root: Path):
    root = Path(root)
    event_path = root/'src/core/libraries/kernel/threads/event_flag.cpp'
    event = event_path.read_text()
    if 'BACHATA_EVENT_FLAG_DELIVERY' in event:
        return {'alreadyApplied': True}
    event = one(event, '#include <condition_variable>',
        '#include <algorithm>\n#include <array>\n#include <chrono>\n#include <condition_variable>\n'
        '#include <cstring>\n#include <memory>\n#include <unordered_map>', 'standard includes')
    event = one(event, '#include "core/libraries/libs.h"',
        '#include "core/libraries/libs.h"\n#include "core/libraries/kernel/threads/pthread.h"\n'
        '#include "core/libraries/kernel/threads/event_flag_delivery.h"', 'complete guest priority and census declaration')
    event = one(event, block(event, 'class EventFlagInternal')+';', DELIVERY, 'latched state and owned registry')
    unsupported = '''    if (queue_mode == EventFlagInternal::QueueMode::ThreadPrio) {
        LOG_ERROR(Kernel_Event, "ThreadPriority attr is not supported!");
    }

'''
    event = one(event, unsupported, '', 'priority now follows guest order')
    event = one(event, '    *ef = new EventFlagInternal(std::string(pName), thread_mode, queue_mode, initPattern);',
'''    auto flag = std::make_shared<EventFlagInternal>(std::string(pName), thread_mode, queue_mode, initPattern);
    {
        auto& registry = EventFlags();
        std::scoped_lock lock{registry.mutex};
        registry.flags.emplace(flag.get(), flag);
    }
    *ef = flag.get();''', 'publish registered owner')
    delete = block(event, 'int PS4_SYSV_ABI sceKernelDeleteEventFlag(')
    event = one(event, delete, '''int PS4_SYSV_ABI sceKernelDeleteEventFlag(OrbisKernelEventFlag ef) {
    auto flag = RemoveEventFlag(ef);
    if (!flag) return ORBIS_KERNEL_ERROR_ESRCH;
    const int result = flag->Delete();
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    (void)Core::GuestCpu::RevokeHostRange(ef);
#endif
    return result;
}''', 'delete wakes pending and releases only its ownership')
    for name in ('sceKernelClearEventFlag', 'sceKernelCancelEventFlag', 'sceKernelSetEventFlag',
                 'sceKernelPollEventFlag', 'sceKernelWaitEventFlag'):
        original = block(event, f'int PS4_SYSV_ABI {name}(')
        owned = one(original, '    if (ef == nullptr) {',
            '    auto flag = FindEventFlag(ef);\n    if (!flag) {', name+' pin')
        owned = owned.replace('ef->', 'flag->')
        for call in ('Clear(bitPattern)', 'Cancel(setPattern, pNumWaitThreads)', 'Set(bitPattern)'):
            owned = owned.replace('    flag->'+call+';\n    return ORBIS_OK;', '    return flag->'+call+';')
        event = one(event, original, owned, name+' owned entrypoint')
    event_path.write_text(event)

    census = root/'src/core/libraries/kernel/threads/event_flag_delivery.h'
    census.write_text('''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
namespace Libraries::Kernel {
// Bounded, nonblocking snapshots. Called only by the existing idle observer.
void ReportEventFlagWaits();
}
''')
    cp_path = root/'src/video_core/amdgpu/liverpool.h'
    cp = cp_path.read_text()
    cp = one(cp, '    bool OnDrawThread() const { return draw_owner==this; }',
             PROGRESS+'    bool OnDrawThread() const { return draw_owner==this; }', 'atomic pending command snapshot')
    cp_path.write_text(cp)
    driver_path = root/'src/core/libraries/videoout/driver.cpp'
    driver = driver_path.read_text()
    driver = one(driver, '#include "common/assert.h"',
        '#include "common/assert.h"\n#include "core/libraries/kernel/threads/event_flag_delivery.h"', 'census include')
    driver = one(driver, '    const auto pool = presenter->GetFrameAcquireProgress();',
        '    const auto pool = presenter->GetFrameAcquireProgress();\n'
        '    const auto cp = liverpool->GetPendingCommandProgress();\n'
        '    Kernel::ReportEventFlagWaits();', 'idle producer state')
    driver = one(driver, '        "swap_busy={} swap_queue={} idle_ms={}",',
        '        "swap_busy={} swap_queue={} idle_ms={} cp_commands={} cp_submits={} cp_submit_done={}",', 'CP fields')
    driver = one(driver, '        std::chrono::duration_cast<std::chrono::milliseconds>(now - progress_since).count());',
        '        std::chrono::duration_cast<std::chrono::milliseconds>(now - progress_since).count(),\n'
        '        cp.commands, cp.submits, cp.submit_done);', 'CP atomic values')
    driver_path.write_text(driver)
    return {'applied': True, 'family': 'event delivery, pending cancellation and shared handle lifetime',
            'diagnostic': 'idle-only census: no guest wake, try-lock, 4/sample, 32/process'}


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('source',type=Path)
    print(apply(p.parse_args().source))
