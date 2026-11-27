"""Port the shared ISS/TLOU kernel semaphore contract (runtime_sema.c).
Keep the original pthread POSIX semaphores and non-donor priority/ID policy.
Shared registry ownership prevents destruction while a guest wait is active.
"""
from pathlib import Path

BODY = r'''class OrbisSem {
public:
    OrbisSem(s32 initial, s32 maximum, std::string_view name, bool fifo)
        : name{name}, token_count{initial}, max_count{maximum}, init_count{initial},
          is_fifo{fifo} {}

    s32 Wait(bool can_block, s32 need, u32* timeout) {
        std::unique_lock lock{mutex};
        if (deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        if (need <= 0 || need > max_count) return ORBIS_KERNEL_ERROR_EINVAL;
        if (token_count >= need) {
            token_count -= need;
            return ORBIS_OK;
        }
        if (!can_block) return ORBIS_KERNEL_ERROR_EBUSY;
        if (timeout && !*timeout) return ORBIS_KERNEL_ERROR_ETIMEDOUT;

        WaitingThread waiter{need, is_fifo ? 0u : static_cast<u32>(g_curthread->attr.prio)};
        auto it = wait_list.begin();
        if (is_fifo) it = wait_list.end();
        else while (it != wait_list.end() && (*it)->priority <= waiter.priority) ++it;
        it = wait_list.insert(it, &waiter);
        if (timeout) {
            const auto deadline = std::chrono::steady_clock::now() +
                                  std::chrono::microseconds(*timeout);
            if (!waiter.event.wait_until(lock, deadline, [&] { return waiter.done; })) {
                wait_list.erase(it);
                *timeout = 0;
                return ORBIS_KERNEL_ERROR_ETIMEDOUT;
            }
            const auto remaining = std::chrono::duration_cast<std::chrono::microseconds>(
                deadline - std::chrono::steady_clock::now()).count();
            *timeout = waiter.result == ORBIS_OK && remaining > 0 ? static_cast<u32>(remaining) : 0;
        } else {
            waiter.event.wait(lock, [&] { return waiter.done; });
        }
        return waiter.result;
    }

    s32 Signal(s32 count) {
        std::scoped_lock lock{mutex};
        if (deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        if (count <= 0 || count > max_count - token_count) return ORBIS_KERNEL_ERROR_EINVAL;
        token_count += count;
        for (auto it = wait_list.begin(); it != wait_list.end();) {
            auto* waiter = *it;
            // Match donor: service waiters in order, skipping those that cannot be satisfied.
            if (waiter->need_count > token_count) { ++it; continue; }
            it = wait_list.erase(it);
            token_count -= waiter->need_count;
            Complete(*waiter, ORBIS_OK);
        }
        return ORBIS_OK;
    }

    s32 Cancel(s32 count, s32* num_waiters) {
        std::scoped_lock lock{mutex};
        if (deleted) return ORBIS_KERNEL_ERROR_ESRCH;
        if (count > max_count) return ORBIS_KERNEL_ERROR_EINVAL;
        if (num_waiters) *num_waiters = static_cast<s32>(wait_list.size());
        WakeAll(ORBIS_KERNEL_ERROR_ECANCELED);
        token_count = count < 0 ? init_count : count;
        return ORBIS_OK;
    }

    void Delete() {
        std::scoped_lock lock{mutex};
        deleted = true;
        WakeAll(ORBIS_KERNEL_ERROR_EACCES);
    }

private:
    struct WaitingThread {
        s32 need_count;
        u32 priority;
        std::condition_variable event{};
        s32 result{};
        bool done{};
    };
    static void Complete(WaitingThread& waiter, s32 result) {
        waiter.result = result;
        waiter.done = true;
        waiter.event.notify_one();
    }
    void WakeAll(s32 result) {
        for (auto* waiter : wait_list) Complete(*waiter, result);
        wait_list.clear();
    }
    std::list<WaitingThread*> wait_list;
    std::string name;
    s32 token_count;
    std::mutex mutex;
    const s32 max_count;
    const s32 init_count;
    const bool is_fifo;
    bool deleted{};
};

using OrbisKernelSema = u32;

static std::mutex orbis_sems_mutex;
static Common::SlotVector<std::shared_ptr<OrbisSem>> orbis_sems;
static std::unordered_map<OrbisKernelSema, std::shared_ptr<OrbisSem>> donor_sems;
static u32 donor_next_sema = 1;

static bool DonorSemaphore() {
    return BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial());
}

static std::shared_ptr<OrbisSem> FindSemaLocked(OrbisKernelSema sem) {
    if (DonorSemaphore()) {
        auto it = donor_sems.find(sem);
        return it == donor_sems.end() ? nullptr : it->second;
    }
    return orbis_sems.IsAllocated(sem) ? orbis_sems[sem] : nullptr;
}

static std::shared_ptr<OrbisSem> FindSema(OrbisKernelSema sem) {
    std::scoped_lock lock{orbis_sems_mutex};
    return FindSemaLocked(sem);
}

s32 PS4_SYSV_ABI sceKernelCreateSema(OrbisKernelSema* sem, const char* pName, u32 attr,
                                     s32 initCount, s32 maxCount, const void* pOptParam) {
    if (!sem || !pName || attr > 2 || initCount < 0 || maxCount <= 0 || initCount > maxCount) {
        LOG_ERROR(Lib_Kernel, "Semaphore creation parameters are invalid!");
        return ORBIS_KERNEL_ERROR_EINVAL;
    }
    const bool donor = DonorSemaphore();
    if (donor && pOptParam) return ORBIS_KERNEL_ERROR_EINVAL;
    auto object = std::make_shared<OrbisSem>(initCount, maxCount, pName, donor || attr == 1);
    std::scoped_lock lock{orbis_sems_mutex};
    if (donor) {
        if (donor_next_sema == UINT32_MAX) return ORBIS_KERNEL_ERROR_ENOSPC;
        const auto id = donor_next_sema++;
        donor_sems.emplace(id, std::move(object));
        *sem = id;
    } else {
        *sem = orbis_sems.Insert(std::move(object)).index;
    }
    return ORBIS_OK;
}

s32 PS4_SYSV_ABI sceKernelWaitSema(OrbisKernelSema sem, s32 needCount, u32* pTimeout) {
    auto object = FindSema(sem);
    return object ? object->Wait(true, needCount, pTimeout) : ORBIS_KERNEL_ERROR_ESRCH;
}

s32 PS4_SYSV_ABI sceKernelSignalSema(OrbisKernelSema sem, s32 signalCount) {
    auto object = FindSema(sem);
    return object ? object->Signal(signalCount) : ORBIS_KERNEL_ERROR_ESRCH;
}

s32 PS4_SYSV_ABI sceKernelPollSema(OrbisKernelSema sem, s32 needCount) {
    auto object = FindSema(sem);
    return object ? object->Wait(false, needCount, nullptr) : ORBIS_KERNEL_ERROR_ESRCH;
}

s32 PS4_SYSV_ABI sceKernelCancelSema(OrbisKernelSema sem, s32 setCount, s32* pNumWaitThreads) {
    auto object = FindSema(sem);
    return object ? object->Cancel(setCount, pNumWaitThreads) : ORBIS_KERNEL_ERROR_ESRCH;
}

s32 PS4_SYSV_ABI sceKernelDeleteSema(OrbisKernelSema sem) {
    std::scoped_lock lock{orbis_sems_mutex};
    auto object = FindSemaLocked(sem);
    if (!object) return ORBIS_KERNEL_ERROR_ESRCH;
    object->Delete();
    if (DonorSemaphore()) donor_sems.erase(sem);
    else orbis_sems.Erase(sem);
    return ORBIS_OK;
}

'''

def apply(root: Path):
    path = Path(root) / 'src/core/libraries/kernel/threads/semaphore.cpp'
    s = path.read_text()
    anchor = '#include <condition_variable>'
    assert s.count(anchor) == 1
    s = s.replace(anchor, '''#include <condition_variable>
#include <chrono>
#include <memory>
#include <unordered_map>
#include "common/elf_info.h"
#include "core/libraries/playgo/bachata_installed_package.h"''', 1)
    a = s.index('class OrbisSem {')
    b = s.index('s32 PS4_SYSV_ABI posix_sem_init', a)
    assert 'static Common::SlotVector<std::unique_ptr<OrbisSem>> orbis_sems;' in s[a:b]
    path.write_text(s[:a] + BODY + s[b:])
