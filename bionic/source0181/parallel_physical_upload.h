// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <condition_variable>
#include <cstring>
#include <mutex>
#include <span>
#include <thread>
#include <vector>
#include <atomic>
#include <algorithm>
#include <cstdint>
namespace BachataUpload {
struct Copy { const std::uint8_t* src; std::uint8_t* dst; size_t size; };
// Two execution lanes (one existing GPU thread, one persistent copy worker).
// Caller must keep both mappings alive until CopyBatch returns.
class Pool {
public:
    Pool():worker([this]{Run();}){}
    Pool(const Pool&)=delete;
    ~Pool() {
        {std::lock_guard l(mutex); stop=true;}
        wake.notify_one();
        worker.join();
    }
    void CopyBatch(std::span<const Copy> copies) {
        std::scoped_lock batch_lock(batch_mutex);
        {
            std::lock_guard l(mutex);
            active=copies; next.store(0,std::memory_order_relaxed);
            done=false; pending=true;
        }
        wake.notify_one();
        Consume(copies);
        std::unique_lock l(mutex);
        finished.wait(l,[&]{return done;});
        active={};
    }
private:
    void Consume(std::span<const Copy> copies) {
        for(;;) {
            auto i=next.fetch_add(1,std::memory_order_relaxed);
            if(i>=copies.size())return;
            const auto& c=copies[i];
            std::memcpy(c.dst,c.src,c.size);
        }
    }
    void Run() {
        for(;;) {
            std::unique_lock l(mutex);
            wake.wait(l,[&]{return stop||pending;});
            if(stop)return;
            auto work=active; pending=false;
            l.unlock();
            Consume(work);
            l.lock(); done=true; l.unlock(); finished.notify_one();
        }
    }
    std::mutex batch_mutex,mutex;
    std::condition_variable wake,finished;
    std::span<const Copy> active;
    std::atomic<size_t> next{};
    bool pending{},done{},stop{};
    std::thread worker;
};
}
