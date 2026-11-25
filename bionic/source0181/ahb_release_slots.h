// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <optional>
#include <utility>
#include <unistd.h>
namespace BachataAhb {
class ReleaseSlots {
public:
    static constexpr unsigned Count=3;
    struct Acquired { unsigned index; int fence; };
    ~ReleaseSlots(){for(auto fd:fences)if(fd>=0)close(fd);}
    std::optional<Acquired> Take(std::chrono::milliseconds timeout) {
        std::unique_lock lock(mutex);
        if(!cv.wait_for(lock,timeout,[&]{
            if(retired)return true;
            for(bool x:free)if(x)return true;
            return false;
        })||retired)return {};
        for(unsigned i=0;i<Count;++i)if(free[i]){
            free[i]=false;
            return Acquired{i,std::exchange(fences[i],-1)};
        }
        return {};
    }
    void Returned(unsigned i,int fd) {
        std::lock_guard lock(mutex);
        if(retired||i>=Count||free[i]){
            if(fd>=0)close(fd);
            return;
        }
        fences[i]=fd;free[i]=true;cv.notify_one();
    }
    void Retire(){
        std::lock_guard lock(mutex);
        retired=true;cv.notify_all();
    }
private:
    std::mutex mutex;
    std::condition_variable cv;
    std::array<bool,Count> free{true,true,true};
    std::array<int,Count> fences{-1,-1,-1};
    bool retired{};
};
}
