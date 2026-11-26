// SPDX-License-Identifier: GPL-2.0-or-later
#include "../native_draw_handoff.h"
#include <array>
#include <cassert>
#include <cstring>
#include <iostream>
#include <vector>
std::array<unsigned char,0x1200> scheduler{};
std::array<unsigned char,0x80> queue{};
alignas(16) std::array<unsigned char,0x200> storage{};
std::vector<uint64_t> commands;
unsigned flushes=0,allocations=0;
Bs4NativeRenderState received{};
template<class T> void put(void* p,size_t offset,T v){std::memcpy(static_cast<unsigned char*>(p)+offset,&v,sizeof(v));}
void worker(const void* p,uint64_t command){std::memcpy(&received,p,sizeof(received));commands.push_back(command);}
void* allocate(void* q,size_t size){assert(q==queue.data()&&size==0x140);allocations++;return storage.data();}
void flush(void* q){assert(q==queue.data());flushes++;}
int main(){
 Bs4NativeRenderState state{};state.width=640;state.height=360;state.layers=1;
 state.colorCount=1;state.colors[0].view=0xabc;state.depth=0xdef;
 put(scheduler.data(),0xf08,uint64_t(0x123));
 assert(bs4_native_enqueue_draw(scheduler.data(),state,allocate,flush,worker));
 assert(commands==std::vector<uint64_t>{0x123}&&received.colors[0].view==0xabc);
 put(scheduler.data(),0x11f0,queue.data());
 assert(!bs4_native_enqueue_draw(scheduler.data(),state,allocate,flush,worker));
 assert(commands.size()==1&&allocations==0);
 put(scheduler.data(),0x11e8,uint8_t(1));
 put(queue.data(),0x10,uintptr_t(0x1000));put(queue.data(),0x40,uintptr_t(0x1000));
 assert(bs4_native_enqueue_draw(scheduler.data(),state,allocate,flush,worker));
 assert(commands.size()==1&&allocations==1&&flushes==0); // not recorded on frontend
 state.colors[0].view=0;state.width=1; // original caller's stack is reusable
 uint64_t bytes{};Bs4NativeWorker callback{};
 std::memcpy(&bytes,storage.data(),8);std::memcpy(&callback,storage.data()+8,8);
 assert(bytes==0x140&&callback==worker);callback(storage.data()+16,0x456);
 assert(commands.back()==0x456&&received.width==640&&received.colors[0].view==0xabc);
 state=received;put(queue.data(),0x10,uintptr_t(0x11000));
 assert(bs4_native_enqueue_draw(scheduler.data(),state,allocate,flush,worker));assert(flushes==1);
 state.colorCount=9;assert(!bs4_native_enqueue_draw(scheduler.data(),state,allocate,flush,worker));
 assert(allocations==2&&commands.size()==2);
 std::cout<<"PASS native draw handoff: copied payload, original queue ordering, direct mode, pending-queue rejection and chunk flush\n";
}
