"""Compile actual patched semaphore methods and exercise count, lifetime and wait order."""
import argparse
import subprocess
import tempfile
from pathlib import Path

PREFIX = r'''
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <iostream>
#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>
using s32=int32_t; using u32=uint32_t;
#define PS4_SYSV_ABI
#define LOG_ERROR(...) ((void)0)
constexpr s32 ORBIS_OK=0, ORBIS_KERNEL_ERROR_ESRCH=-3, ORBIS_KERNEL_ERROR_EINVAL=-22,
    ORBIS_KERNEL_ERROR_EBUSY=-16, ORBIS_KERNEL_ERROR_ETIMEDOUT=-60,
    ORBIS_KERNEL_ERROR_ECANCELED=-85, ORBIS_KERNEL_ERROR_EACCES=-13,
    ORBIS_KERNEL_ERROR_ENOSPC=-28;
namespace Common {
struct ElfInfo { std::string_view serial="CUSA00552"; static ElfInfo& Instance(){static ElfInfo i;return i;} auto GameSerial(){return serial;} };
template<class T> struct SlotVector { std::map<u32,T> slots; struct Id{u32 index;};
    bool IsAllocated(u32 i){return slots.contains(i);} T& operator[](u32 i){return slots.at(i);}
    Id Insert(T x){u32 i=0;while(slots.contains(i))++i;slots.emplace(i,std::move(x));return {i};}
    void Erase(u32 i){slots.erase(i);}
};
}
#include "core/libraries/playgo/bachata_installed_package.h"
struct Thread {struct {int prio=1;} attr;}; thread_local Thread current; thread_local Thread* g_curthread=&current;
'''
MAIN = r'''
static void queued(u32 id, size_t n) {
    auto obj=FindSema(id); assert(obj);
    auto end=std::chrono::steady_clock::now()+std::chrono::seconds(2);
    while(std::chrono::steady_clock::now()<end) {
        { std::scoped_lock lock{obj->mutex}; if(obj->wait_list.size()==n) return; }
        std::this_thread::yield();
    }
    assert(false && "waiter not queued");
}
int main() {
    unsigned cases=0;
    for(auto title:{"CUSA00552","CUSA00557","CUSA00004","CUSA00223","CUSA00999"}) {
        Common::ElfInfo::Instance().serial=title;
        bool donor=DonorSemaphore();
        u32 id=0, next=0;
        assert(sceKernelCreateSema(nullptr,"x",1,0,1,nullptr)==ORBIS_KERNEL_ERROR_EINVAL); ++cases;
        assert(sceKernelCreateSema(&id,"x",2,1,3,nullptr)==0); ++cases;
        assert(sceKernelPollSema(id,0)==ORBIS_KERNEL_ERROR_EINVAL); ++cases;
        assert(sceKernelWaitSema(id,-1,nullptr)==ORBIS_KERNEL_ERROR_EINVAL); ++cases;
        assert(sceKernelWaitSema(id,4,nullptr)==ORBIS_KERNEL_ERROR_EINVAL); ++cases;
        assert(sceKernelSignalSema(id,INT32_MAX)==ORBIS_KERNEL_ERROR_EINVAL); ++cases;
        assert(sceKernelSignalSema(id,-1)==ORBIS_KERNEL_ERROR_EINVAL); ++cases;
        assert(sceKernelPollSema(id,1)==0); ++cases;
        u32 timeout=0; assert(sceKernelWaitSema(id,1,&timeout)==ORBIS_KERNEL_ERROR_ETIMEDOUT); ++cases;
        timeout=1000; assert(sceKernelWaitSema(id,1,&timeout)==ORBIS_KERNEL_ERROR_ETIMEDOUT && timeout==0); ++cases;
        std::atomic<int> a{999}, b{999};
        std::thread t1([&]{current.attr.prio=10;a=sceKernelWaitSema(id,1,nullptr);}); queued(id,1);
        std::thread t2([&]{current.attr.prio=1;b=sceKernelWaitSema(id,1,nullptr);}); queued(id,2);
        assert(sceKernelSignalSema(id,1)==0);
        {auto o=FindSema(id);std::scoped_lock lock{o->mutex};assert(o->wait_list.size()==1);assert(o->wait_list.front()->priority==(donor?0u:10u));}
        assert(sceKernelDeleteSema(id)==0);t1.join();t2.join();
        assert(a==(donor?0:ORBIS_KERNEL_ERROR_EACCES)&&b==(donor?ORBIS_KERNEL_ERROR_EACCES:0)); ++cases;
        assert(sceKernelWaitSema(id,1,nullptr)==ORBIS_KERNEL_ERROR_ESRCH); ++cases;
        assert(sceKernelCreateSema(&next,"x",1,0,3,nullptr)==0);
        assert(donor?next>id:next==id); ++cases;
        auto retained=FindSema(next); std::weak_ptr<OrbisSem> weak=retained;
        std::thread t3([&]{a=sceKernelWaitSema(next,2,nullptr);}); queued(next,1);
        std::thread t4([&]{b=sceKernelWaitSema(next,1,nullptr);}); queued(next,2);
        assert(sceKernelSignalSema(next,1)==0);t4.join();assert(b==0); ++cases;
        s32 waiting=-1;assert(sceKernelCancelSema(next,4,&waiting)==ORBIS_KERNEL_ERROR_EINVAL&&waiting==-1); ++cases;
        assert(sceKernelCancelSema(next,-1,&waiting)==0&&waiting==1);t3.join();assert(a==ORBIS_KERNEL_ERROR_ECANCELED); ++cases;
        timeout=2000000; std::thread t5([&]{a=sceKernelWaitSema(next,1,&timeout);});queued(next,1);
        assert(sceKernelSignalSema(next,1)==0);assert(sceKernelDeleteSema(next)==0);t5.join();assert(a==0&&timeout<=2000000); ++cases;
        assert(retained->Signal(1)==ORBIS_KERNEL_ERROR_ESRCH);retained.reset();assert(weak.expired()); ++cases;
        assert(sceKernelDeleteSema(next)==ORBIS_KERNEL_ERROR_ESRCH); ++cases;
    }
    std::cout<<"BACHATA_DONOR_SEMA_LIFETIME_PASS cases="<<cases<<"\n";
}
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
    s=(a.source/'src/core/libraries/kernel/threads/semaphore.cpp').read_text()
    body=s[s.index('class OrbisSem {'):s.index('s32 PS4_SYSV_ABI posix_sem_init')]
    # expose test-only fields to observe deterministic waiter registration
    body=body.replace('private:', 'public:')
    with tempfile.TemporaryDirectory() as d:
        src=Path(d)/'test.cpp'; exe=Path(d)/'test';src.write_text(PREFIX+body+MAIN)
        subprocess.run(['c++','-std=c++20','-O2','-pthread','-I',str(a.source/'src'),str(src),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True,timeout=30)
if __name__=='__main__':main()
