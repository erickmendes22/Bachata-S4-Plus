#!/usr/bin/env python3
"""Execute effective event flags/entrypoints with controlled waiter scheduling."""
from pathlib import Path
import argparse
import os
import re
import subprocess
import tempfile


def block(text, marker):
    start=text.index(marker);opening=text.index('{',start);depth=1;end=opening+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]


PREFIX=r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <future>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>
#include "common/types.h"
#include "core/libraries/kernel/orbis_error.h"
using namespace std::chrono_literals;
#define LOG_TRACE(...) ((void)0)
#define LOG_DEBUG(...) ((void)0)
#define LOG_ERROR(...) ((void)0)
#define UNREACHABLE() std::abort()
#define LOG_WARNING(category,format,...) CaptureLog(__VA_ARGS__)
namespace Core::GuestCpu {
std::atomic<unsigned> published{},revoked{};
bool PublishHostRange(const void*,std::size_t,bool){++published;return true;}
bool RevokeHostRange(const void*){++revoked;return true;}
}
struct GateMutex {
    std::mutex value;
    inline static std::atomic<bool> hold_resume{};
    inline static std::atomic<unsigned> resuming{};
    inline static thread_local bool waiter{};
    inline static thread_local unsigned locks{};
    void lock(){
        if(waiter && ++locks>1 && hold_resume.load()){
            ++resuming;
            while(hold_resume.load())std::this_thread::yield();
        }
        value.lock();
    }
    bool try_lock(){return value.try_lock();}
    void unlock(){value.unlock();}
};
namespace Libraries::Kernel {
struct Pthread {std::mutex lock;struct {s32 prio{700};} attr;std::atomic<s32> tid{};std::string name;};
thread_local Pthread* g_curthread{};
void CaptureLog(const char*,VAddr,const char*,s32,u64,u64,u32,s32,u64,u32,u64,u64);
@@EVENT@@
struct Seen {VAddr object;std::string name,thread;u64 bits,observed,age;u32 mode,pending;};
std::vector<Seen> logs;
bool delete_during_log=false;
void CaptureLog(const char* name,VAddr object,const char* thread,s32 tid,u64 bits,u64 observed,
                u32 mode,s32 priority,u64 age,u32 pending,u64 sets,u64 delivered){
    auto& registry=EventFlags();
    assert(registry.mutex.try_lock());registry.mutex.unlock();
    auto handle=reinterpret_cast<EventFlagInternal*>(object);
    auto owner=FindEventFlag(handle);
    if(owner){assert(owner->m_mutex.try_lock());owner->m_mutex.unlock();}
    if(delete_during_log)assert(sceKernelDeleteEventFlag(handle)==ORBIS_OK);
    logs.push_back({object,name,thread,bits,observed,age,mode,pending});
    assert(tid>0 && priority>=0 && age>=5000 && pending>0 && sets==0 && delivered==0);
}
}
using namespace Libraries::Kernel;
using Flag=EventFlagInternal;
template<class P>void Until(P pred){
    const auto end=std::chrono::steady_clock::now()+2s;
    while(!pred()){assert(std::chrono::steady_clock::now()<end);std::this_thread::yield();}
}
struct Owner {
    OrbisKernelEventFlag handle{};
    explicit Owner(u32 attr=0x21,u64 bits=0,const char* name="PS4SyncEvent"){
        assert(sceKernelCreateEventFlag(&handle,name,attr,bits,nullptr)==ORBIS_OK);
    }
    ~Owner(){if(handle)assert(sceKernelDeleteEventFlag(handle)==ORBIS_OK);}
    std::shared_ptr<Flag> Ref()const{auto ref=FindEventFlag(handle);assert(ref);return ref;}
};
struct Result {int rc=123;u64 bits=0;u32 remaining=500000;std::atomic<bool> done{};};
std::jthread Wait(OrbisKernelEventFlag handle,Result& out,s32 tid,s32 priority=700,
                  u64 bits=1,u32 mode=0x11,bool infinite=false){
    return std::jthread([=,&out]{
        Pthread thread;thread.tid=tid;thread.attr.prio=priority;thread.name="GuestWait"+std::to_string(tid);
        g_curthread=&thread;GateMutex::waiter=true;GateMutex::locks=0;
        out.rc=sceKernelWaitEventFlag(handle,bits,mode,&out.bits,infinite?nullptr:&out.remaining);
        out.done.store(true);g_curthread=nullptr;
    });
}
u32 Pending(const Owner& owner){auto ref=owner.Ref();std::scoped_lock lock{ref->m_mutex};return ref->PendingCount();}
s32 Delivered(const Owner& owner){
    auto ref=owner.Ref();std::scoped_lock lock{ref->m_mutex};
    for(auto* w=ref->m_waiters;w;w=w->next)if(w->state==Flag::WaitState::Delivered)return w->thread.tid;
    return 0;
}
void Hold(){GateMutex::resuming=0;GateMutex::hold_resume=true;}
void Release(){GateMutex::hold_resume=false;}

void Immediate(){
    Owner flag(0x21,0b1110);u64 result{};
    assert(sceKernelPollEventFlag(flag.handle,0b1010,0x21,&result)==ORBIS_OK && result==0b1110);
    assert(sceKernelPollEventFlag(flag.handle,0b1110,0x02,&result)==ORBIS_OK && result==0b0100);
    assert(sceKernelPollEventFlag(flag.handle,0b0100,0x11,&result)==ORBIS_OK && result==0b0100);
    assert(sceKernelPollEventFlag(flag.handle,1,1,&result)==ORBIS_KERNEL_ERROR_EBUSY && result==0);
    assert(sceKernelWaitEventFlag(flag.handle,0,1,&result,nullptr)==ORBIS_KERNEL_ERROR_EINVAL);
    assert(sceKernelSetEventFlag(flag.handle,8)==ORBIS_OK);
    u32 micros=5000;
    assert(sceKernelWaitEventFlag(flag.handle,8,0x11,&result,&micros)==ORBIS_OK && result==8 && micros==5000);
    for(auto* invalid:{static_cast<Flag*>(nullptr),reinterpret_cast<Flag*>(0x12340)}){
        assert(sceKernelSetEventFlag(invalid,1)==ORBIS_KERNEL_ERROR_ESRCH);
        assert(sceKernelClearEventFlag(invalid,0)==ORBIS_KERNEL_ERROR_ESRCH);
        assert(sceKernelCancelEventFlag(invalid,0,nullptr)==ORBIS_KERNEL_ERROR_ESRCH);
        assert(sceKernelPollEventFlag(invalid,1,1,nullptr)==ORBIS_KERNEL_ERROR_ESRCH);
        assert(sceKernelWaitEventFlag(invalid,1,1,nullptr,nullptr)==ORBIS_KERNEL_ERROR_ESRCH);
        assert(sceKernelDeleteEventFlag(invalid)==ORBIS_KERNEL_ERROR_ESRCH);
    }
}
void PollNoThreadLock(){
    Owner flag;Pthread thread;thread.name="PollingGuest";
    std::unique_lock held{thread.lock};
    auto result=std::async(std::launch::async,[&]{
        g_curthread=&thread;const int rc=sceKernelPollEventFlag(flag.handle,1,1,nullptr);
        g_curthread=nullptr;return rc;
    });
    assert(result.wait_for(200ms)==std::future_status::ready);
    assert(result.get()==ORBIS_KERNEL_ERROR_EBUSY);
}
void SetClear(){
    Owner flag(0x11);Result result;Hold();auto thread=Wait(flag.handle,result,1);
    Until([&]{return Pending(flag)==1;});
    assert(sceKernelSetEventFlag(flag.handle,1)==ORBIS_OK);
    assert(sceKernelClearEventFlag(flag.handle,0)==ORBIS_OK);
    Release();thread.join();
    assert(result.rc==ORBIS_OK && result.bits==1 && result.remaining>0);
}
void RepeatedSet(){
    Owner flag;Result first,second;Hold();auto a=Wait(flag.handle,first,1);
    Until([&]{return Pending(flag)==1;});auto b=Wait(flag.handle,second,2);
    Until([&]{return Pending(flag)==2;});
    assert(sceKernelSetEventFlag(flag.handle,1)==ORBIS_OK);
    assert(sceKernelSetEventFlag(flag.handle,1)==ORBIS_OK);
    Release();a.join();b.join();
    assert(first.rc==0 && second.rc==0 && first.bits==1 && second.bits==1);
}
void QueueOrder(u32 attr,s32 second_priority,s32 expected){
    Owner flag(attr);Result first,second;Hold();auto a=Wait(flag.handle,first,1,700);
    Until([&]{return Pending(flag)==1;});auto b=Wait(flag.handle,second,2,second_priority);
    Until([&]{return Pending(flag)==2;});
    sceKernelSetEventFlag(flag.handle,1);assert(Delivered(flag)==expected && Pending(flag)==1);
    sceKernelSetEventFlag(flag.handle,1);Release();a.join();b.join();
    assert(first.rc==0 && second.rc==0);
}
void Ordering(){QueueOrder(0x21,200,1);QueueOrder(0x22,200,2);QueueOrder(0x22,700,1);}
void Broadcast(){
    Owner flag;std::array<Result,3> result;std::vector<std::jthread> threads;Hold();
    for(unsigned i=0;i<3;++i){threads.push_back(Wait(flag.handle,result[i],i+1,700,i+1,1));Until([&]{return Pending(flag)==i+1;});}
    sceKernelSetEventFlag(flag.handle,3);Release();for(auto& t:threads)t.join();
    for(const auto& r:result)assert(r.rc==0 && r.bits==3);
}
void Timeout(){
    Owner flag;Result result;result.remaining=10000;auto thread=Wait(flag.handle,result,1);
    thread.join();assert(result.rc==ORBIS_KERNEL_ERROR_ETIMEDOUT && result.bits==0 && !result.remaining && !Pending(flag));
    sceKernelSetEventFlag(flag.handle,1);u64 bits{};
    assert(sceKernelPollEventFlag(flag.handle,1,0x11,&bits)==0 && bits==1);
}
void CancelAndNewWait(){
    Owner flag(0x11);Result old,next;Hold();auto a=Wait(flag.handle,old,1);
    Until([&]{return Pending(flag)==1;});int count=-1;
    assert(sceKernelCancelEventFlag(flag.handle,8,&count)==0 && count==1);
    auto b=Wait(flag.handle,next,2,700,2,0x11);
    Until([&]{return Pending(flag)==1;});sceKernelSetEventFlag(flag.handle,2);sceKernelClearEventFlag(flag.handle,0);
    Release();a.join();b.join();
    assert(old.rc==ORBIS_KERNEL_ERROR_ECANCELED && old.bits==8);
    assert(next.rc==0 && next.bits==10);
}
void SetThenCancel(){
    Owner flag;Result sent,canceled;Hold();auto a=Wait(flag.handle,sent,1);
    Until([&]{return Pending(flag)==1;});sceKernelSetEventFlag(flag.handle,1);
    auto b=Wait(flag.handle,canceled,2,700,2,0x11);
    Until([&]{return Pending(flag)==1;});int count=-1;
    assert(sceKernelCancelEventFlag(flag.handle,8,&count)==0 && count==1);
    sceKernelSetEventFlag(flag.handle,16);Release();a.join();b.join();
    assert(sent.rc==0 && sent.bits==1 && canceled.rc==ORBIS_KERNEL_ERROR_ECANCELED && canceled.bits==8);
}
void DeleteWait(bool delivered){
    Owner flag;Result result;Hold();auto ref=flag.Ref();std::weak_ptr<Flag> weak=ref;
    auto thread=Wait(flag.handle,result,1);Until([&]{return Pending(flag)==1;});
    if(delivered)sceKernelSetEventFlag(flag.handle,1);
    ref.reset();const auto handle=flag.handle;flag.handle=nullptr;
    assert(sceKernelDeleteEventFlag(handle)==0 && !FindEventFlag(handle));
    assert(!weak.expired());
    assert(sceKernelSetEventFlag(handle,1)==ORBIS_KERNEL_ERROR_ESRCH);
    assert(sceKernelCancelEventFlag(handle,1,nullptr)==ORBIS_KERNEL_ERROR_ESRCH);
    assert(sceKernelDeleteEventFlag(handle)==ORBIS_KERNEL_ERROR_ESRCH);
    Release();thread.join();assert(weak.expired());
    assert(result.rc==(delivered?ORBIS_OK:ORBIS_KERNEL_ERROR_EACCES));
    assert(result.bits==(delivered?1u:0u));
}
void InFlightReference(){
    Owner flag;auto ref=flag.Ref();const auto handle=flag.handle;flag.handle=nullptr;
    assert(sceKernelDeleteEventFlag(handle)==0);
    assert(ref->Set(1)==ORBIS_KERNEL_ERROR_ESRCH && ref->Clear(0)==ORBIS_KERNEL_ERROR_ESRCH);
    assert(ref->Wait(1,Flag::WaitMode::And,Flag::ClearMode::All,nullptr,nullptr)==ORBIS_KERNEL_ERROR_EACCES);
}
void Census(){
    auto& registry=EventFlags();
    registry.wait_reports=0;registry.last_report={};logs.clear();
    constexpr unsigned N=40;
    std::vector<std::unique_ptr<Owner>> flags;
    std::array<Result,N> results;std::vector<std::jthread> threads;
    for(unsigned i=0;i<N;++i){
        flags.push_back(std::make_unique<Owner>());
        threads.push_back(Wait(flags.back()->handle,results[i],i+1,700,1,0x11,true));
        Until([&]{return Pending(*flags.back())==1;});
        auto ref=flags.back()->Ref();std::scoped_lock lock{ref->m_mutex};
        ref->m_waiters->since-=10s; // Change only diagnostic age, never a predicate/deadline.
    }
    {
        std::scoped_lock lock{registry.mutex};
        auto f=std::async(std::launch::async,[]{ReportEventFlagWaits();});
        assert(f.wait_for(200ms)==std::future_status::ready);f.get();assert(logs.empty());
    }
    for(unsigned i=0;i<8;++i){
        {std::scoped_lock lock{registry.mutex};registry.last_report-=3s;}
        ReportEventFlagWaits();assert(logs.size()==(i+1)*4);
        ReportEventFlagWaits();assert(logs.size()==(i+1)*4);
    }
    {std::scoped_lock lock{registry.mutex};registry.last_report-=3s;}
    ReportEventFlagWaits();assert(logs.size()==32);
    for(const auto& log:logs)assert(log.name=="PS4SyncEvent" && log.thread.starts_with("GuestWait") && log.bits==1 && log.observed==0 && log.mode==0x11);
    for(unsigned i=0;i<N;++i){assert(!results[i].done);flags[i].reset();}
    for(auto& t:threads)t.join();
    for(const auto& r:results)assert(r.rc==ORBIS_KERNEL_ERROR_EACCES);
    // The copied strings/results survive deleting the object during logging.
    registry.wait_reports=0;registry.last_report={};logs.clear();
    Owner flag;Result result;auto t=Wait(flag.handle,result,100,700,1,0x11,true);
    Until([&]{return Pending(flag)==1;});
    {auto ref=flag.Ref();std::scoped_lock lock{ref->m_mutex};ref->m_waiters->since-=10s;}
    delete_during_log=true;ReportEventFlagWaits();delete_during_log=false;
    flag.handle=nullptr;t.join();assert(logs.size()==1 && logs[0].name=="PS4SyncEvent");
}
struct CpState {
    std::atomic<u32> num_commands{},num_submits{};
    std::atomic<bool> submit_done{};
    @@CP@@
};
void CpSnapshot(){CpState cp;cp.num_commands=7;cp.num_submits=11;cp.submit_done=true;
    const auto state=cp.GetPendingCommandProgress();assert(state.commands==7 && state.submits==11 && state.submit_done);}
int main(int argc,char** argv){
    const std::string only=argc>1?argv[1]:"all";
    auto run=[&](const char* name,auto fn){if(only=="all"||only==name){fn();std::cout<<"PASS "<<name<<'\n';}};
    run("immediate",Immediate);run("poll_no_thread_lock",PollNoThreadLock);run("set_clear",SetClear);run("repeated_set",RepeatedSet);
    run("ordering",Ordering);run("broadcast",Broadcast);run("timeout",Timeout);
    run("cancel_new_wait",CancelAndNewWait);run("set_cancel",SetThenCancel);
    run("delete_pending",[]{DeleteWait(false);});run("delete_delivered",[]{DeleteWait(true);});
    run("inflight",InFlightReference);run("census",Census);run("cp_snapshot",CpSnapshot);
    assert(EventFlags().flags.empty());
    assert(Core::GuestCpu::published.load()==Core::GuestCpu::revoked.load());
}
'''


def source_contract(source):
    src=source/'src';event=(src/'core/libraries/kernel/threads/event_flag.cpp').read_text()
    assert '#include "core/libraries/kernel/threads/pthread.h"' in event.splitlines()
    assert '#include "core/libraries/kernel/threads/event_flag_delivery.h"' in event.splitlines()
    assert 'std::chrono::system_clock' not in event and 'sleep_for' not in event
    assert 'wait_for(' not in event and 'm_status' not in event
    assert 'delete ef;' not in event and 'RevokeHostRange(ef)' in event
    assert 'PublishHostRange(*ef, sizeof(EventFlagInternal), true)' in event
    for name in ('Clear','Cancel','Set','Poll','Wait'):
        body=block(event,'int PS4_SYSV_ABI sceKernel'+name+'EventFlag(')
        assert 'auto flag = FindEventFlag(ef);' in body and 'ef->' not in body
    delete=block(event,'int PS4_SYSV_ABI sceKernelDeleteEventFlag(')
    assert delete.index('RemoveEventFlag(ef)')<delete.index('flag->Delete()')<delete.index('RevokeHostRange(ef)')
    driver=(src/'core/libraries/videoout/driver.cpp').read_text()
    note=block(driver,'void VideoOutDriver::NotePresentProgress(')
    assert 'Kernel::ReportEventFlagWaits();' in note and 'cp.commands, cp.submits, cp.submit_done' in note
    assert '#include "core/libraries/kernel/threads/event_flag_delivery.h"' in driver.splitlines()
    assert 'void ReportEventFlagWaits();' in (src/'core/libraries/kernel/threads/event_flag_delivery.h').read_text()
    cp=(src/'video_core/amdgpu/liverpool.h').read_text()
    pending=block(cp,'    PendingCommandProgress GetPendingCommandProgress(')
    assert pending.count('.load(std::memory_order_relaxed)')==3
    return event,cp


def identity_dependency(source, event):
    """Compile the real guest Pthread declaration and identity reader.

    The concurrency fixture uses a controlled Pthread. This separate probe
    verifies the production member types and the explicit include dependency,
    for both Android/FEX and the host configuration. Only assertion logging is
    replaced; the thread, mutex, semaphore, TLS and priority declarations are real.
    """
    include = '#include "core/libraries/kernel/threads/pthread.h"'
    assert include in event.splitlines()
    declaration = block(event, 'struct EventFlagWaitIdentity {') + ';\n'
    capture = block(event, 'static EventFlagWaitIdentity CaptureEventFlagWaitIdentity()')
    prefix = ('#include <algorithm>\n#include <array>\n#include <cstring>\n#include <mutex>\n'
              '#include <string>\n#include "common/types.h"\n'
              'namespace Libraries::Kernel { struct Pthread; extern thread_local Pthread* g_curthread; }\n')
    probe = prefix + include + '\nnamespace Libraries::Kernel {\n' + declaration + capture + '\n}\n'
    with tempfile.TemporaryDirectory(prefix='event-flag-identity-dependency-') as tmp:
        work = Path(tmp)
        shim = work/'common/assert.h'
        shim.parent.mkdir(parents=True)
        shim.write_text('#pragma once\n#define ASSERT(...) ((void)0)\n#define ASSERT_MSG(...) ((void)0)\n')
        cpp = work/'identity.cpp'
        for name, body, android, success in (
            ('android_fex', probe, True, True),
            ('host', probe, False, True),
            ('missing_pthread_include', probe.replace(include, ''), True, False),
        ):
            cpp.write_text(body)
            command = ['g++', '-std=c++20', '-pthread', '-fsyntax-only', '-I', str(work), '-I', str(source/'src')]
            if android:
                command += ['-D__ANDROID__', '-DSHADPS4_ENABLE_FEX_GUEST_CPU']
            result = subprocess.run([*command, str(cpp)], capture_output=True, text=True)
            assert (result.returncode == 0) == success, (name, result.stderr)
            if not success:
                assert 'incomplete type' in result.stderr and 'Pthread' in result.stderr, result.stderr
    print('PASS: real Pthread header/identity helper, Android-FEX/host, missing-include negative')


def run(source,positive_only=False):
    event,cp=source_contract(source)
    identity_dependency(source,event)
    methods=event[event.index('constexpr int ORBIS_KERNEL_EVF_ATTR_TH_FIFO'):event.index('void RegisterKernelEventFlag(')]
    assert methods.count('std::mutex m_mutex;')==1
    methods=methods.replace('std::mutex m_mutex;','GateMutex m_mutex;').replace(
        'std::condition_variable cv;','std::condition_variable_any cv;').replace('private:','public:')
    pending=block(cp,'    struct PendingCommandProgress {')+';\n'+block(cp,'    PendingCommandProgress GetPendingCommandProgress(')
    text=PREFIX.replace('@@EVENT@@',methods).replace('@@CP@@',pending)
    assert '@@' not in text
    with tempfile.TemporaryDirectory(prefix='event-flag-delivery-') as tmp:
        path=Path(tmp)/'gate.cpp';binary=path.with_suffix('')
        def check(body,case='all',negative=False):
            path.write_text(body)
            subprocess.run(['g++','-std=c++20','-O1','-g','-pthread','-fsanitize=address,undefined',
                '-fno-sanitize-recover=all','-DSHADPS4_ENABLE_FEX_GUEST_CPU','-I',str(source/'src'),
                str(path),'-o',str(binary)],check=True)
            # The test process is traced in the local executor, where LSan
            # cannot inspect threads. Address/UAF and UB instrumentation remain
            # enabled; the registry and shared owners are checked explicitly.
            try:result=subprocess.run([str(binary),case],capture_output=True,text=True,timeout=8,
                env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
            except subprocess.TimeoutExpired:
                assert negative,'positive test hung';return
            if negative:assert result.returncode!=0,'negative unexpectedly passed'
            else:
                assert result.returncode==0,result.stdout+result.stderr
                print(result.stdout.strip())
        check(text)
        cancel=block(text,'    int Cancel(')
        delete=block(text,'    int Delete()')
        wait_wrapper=block(text,'int PS4_SYSV_ABI sceKernelWaitEventFlag(')
        negatives=[
            ('poll captures thread lock','poll_no_thread_lock',text.replace(
             'may_block ? CaptureEventFlagWaitIdentity() : EventFlagWaitIdentity{}','CaptureEventFlagWaitIdentity()',1)),
            ('recheck cleared bits','set_clear',text.replace('return waiter.state != WaitState::Pending;',
             'return waiter.state != WaitState::Pending && Satisfied(bits, wait_mode);',1)),
            ('retract delivered cancel','set_cancel',text.replace(cancel,cancel.replace('if (waiter->state != WaitState::Pending) continue;','if (false) continue;',1),1)),
            ('replace saved cancel result','cancel_new_wait',text.replace('if (result) *result = waiter.result;','if (result) *result = m_bits;',1)),
            ('clear bits wrong mask','immediate',text.replace('m_bits &= ~bits;','m_bits &= bits;',1)),
            ('ignore clear all','immediate',text.replace('if (mode == ClearMode::All) m_bits = 0;','if (mode == ClearMode::All) (void)m_bits;',1)),
            ('lose guest priority','ordering',text.replace('m_queue_mode == QueueMode::Fifo ||','true ||',1)),
            ('reverse equal priority','ordering',text.replace('(*next)->thread.priority <= waiter.thread.priority','(*next)->thread.priority < waiter.thread.priority',1)),
            ('delete pending not completed','delete_pending',text.replace('waiter->state = WaitState::Deleted;','(void)waiter->state;',1)),
            ('delete retracts delivered','delete_delivered',text.replace(delete,delete.replace('if (waiter->state != WaitState::Pending) continue;','if (false) continue;',1),1)),
            ('wait drops its owner','delete_pending',text.replace(wait_wrapper,wait_wrapper.replace('auto flag = FindEventFlag(ef);','auto flag = FindEventFlag(ef).get();',1),1)),
            ('census exceeds budget','census',text.replace('registry.wait_reports >= 32','registry.wait_reports >= 64',1).replace('registry.wait_reports == 32','registry.wait_reports == 64',1)),
            ('logs under registry lock','census',text.replace('const auto& wait = snapshots[i];','const auto& wait = snapshots[i];\n        std::scoped_lock bad_lock{registry.mutex};',1)),
            ('CP hides pending submits','cp_snapshot',text.replace('num_submits.load(std::memory_order_relaxed)','0u',1)),
        ]
        if not positive_only:
            for name,case,body in negatives:
                assert body!=text,name
                check(body,case,True);print('PASS negative:',name)
        print(f'BACHATA_EVENT_FLAG_DELIVERY_PASS real-methods/ABI/FIFO/guest-priority/timeout/cancel/delete/shared-lifetime/census {0 if positive_only else len(negatives)} negatives')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--positive-only',action='store_true')
    p.add_argument('--dependency-only',action='store_true')
    a=p.parse_args()
    if a.dependency_only:
        event,_=source_contract(a.source.resolve());identity_dependency(a.source.resolve(),event)
    else:
        run(a.source.resolve(),a.positive_only)
