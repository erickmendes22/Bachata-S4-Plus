"""Exercise actual bounded mailbox, checked cache reader and owner-side merge."""
import argparse, subprocess, tempfile
from pathlib import Path

def method(src,name):
    start=src.index(name); brace=src.index('{',start); depth=1; end=brace+1
    while depth:
        depth+=(src[end]=='{')-(src[end]=='}');end+=1
    return src[start:end]

def run(source):
    src=source/'src'; v=src/'video_core/renderer_vulkan'
    serial=(v/'vk_pipeline_serialization.cpp').read_text()
    cache=(v/'vk_pipeline_cache.cpp').read_text()
    assert 'StartOrderWarmup();' in serial and 'graphics=live' in serial
    assert 'order_warmup->live_hashes.insert(params.hash)' in cache
    assert cache.count('PumpOrderWarmup();')==2
    assert 'StopOrderWarmup();' in method(serial,'void PipelineCache::Sync(')
    assert 'StopOrderWarmup();' in method(cache,'PipelineCache::~PipelineCache(')
    assert 'StopOrderWarmup();' in method(cache,'std::optional<vk::ShaderModule> PipelineCache::ReplaceShader(')
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); (d/'common').mkdir()
        (d/'common/assert.h').write_text('#pragma once\n#include <cassert>\n#define ASSERT_MSG(x,...) assert(x)\n')
        (d/'common/types.h').write_text('#pragma once\n#include <cstdint>\nusing u8=uint8_t; using u32=uint32_t; using u64=uint64_t;\n')
        # Copy the actual reader header; quoted includes use the real tree otherwise.
        (d/'common/serdes.h').write_text((src/'common/serdes.h').read_text())
        (d/'test.cpp').write_text(r'''
#include <atomic>
#include <cassert>
#include <future>
#include <memory>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <concepts>
#include <utility>
#include <iostream>
#include "common/serdes.h"
#include "order_warmup_mailbox.h"
using namespace std::chrono_literals;
namespace Vulkan {
struct Info { u64 pgm_hash{}; unsigned hw_stage{},sw_stage{}; };
struct Spec { unsigned id{}; };
struct Program {
    struct Module { unsigned module{}; std::unique_ptr<Info> info; };
    Info info;
    std::vector<Module> modules;
    void InsertPermut(unsigned module,Spec&&,size_t perm,std::unique_ptr<Info> value) {
        if(modules.size()<=perm) modules.resize(perm+1);
        modules[perm]={module,std::move(value)};
    }
};
struct Map:std::unordered_map<u64,std::unique_ptr<Program>> {
    struct Iter { Map::iterator i; auto& value(){return i->second;} };
    std::pair<Iter,bool> try_emplace(u64 h){auto [i,ok]=std::unordered_map<u64,std::unique_ptr<Program>>::try_emplace(h);return {{i},ok};}
};
struct PipelineCache {
    struct OrderWarmStage {
        std::unique_ptr<Program> program; std::unique_ptr<Info> info;
        Spec spec; size_t permutation{}; unsigned module{};
    };
    struct Warm { std::unordered_set<u64> live_hashes; };
    std::unique_ptr<Warm> order_warmup=std::make_unique<Warm>(); Map program_cache;
    bool MergeOrderWarmStage(OrderWarmStage& stage);
};
''' + method(serial,'bool PipelineCache::MergeOrderWarmStage(').replace('stage.module=nullptr;','stage.module=0;') + r'''
}
int main(){
    using namespace Vulkan;
    OrderWarmupMailbox<int,2> box;
    assert(box.Push(1)); assert(box.Push(2));
    auto producer=std::async(std::launch::async,[&]{return box.Push(3);});
    assert(producer.wait_for(10ms)==std::future_status::timeout);
    assert(*box.Take()==1); assert(producer.get());
    assert(*box.Take()==2); assert(*box.Take()==3); assert(!box.Take());
    box.Finish(); assert(box.Drained());
    OrderWarmupMailbox<int,1> cancelled; assert(cancelled.Push(5));
    auto blocked=std::async(std::launch::async,[&]{return cancelled.Push(6);});
    assert(blocked.wait_for(10ms)==std::future_status::timeout);
    cancelled.Cancel(); assert(!blocked.get()); assert(*cancelled.Take()==5);
    Serialization::Archive ar; Serialization::Writer w{ar};
    std::vector<u32> expected{1,2,3}; std::string label="shader";
    w.Write(expected); w.Write(label); auto bytes=ar.TakeOff();
    for(size_t n=0;n<bytes.size();++n){
        auto copy=std::vector<u8>(bytes.begin(),bytes.begin()+n);
        Serialization::Archive bad{std::move(copy),true}; Serialization::Reader r{bad};
        std::vector<u32> v; std::string s; bool rejected=false;
        try{r.Read(v);r.Read(s);}catch(const std::runtime_error&){rejected=true;}
        assert(rejected);
    }
    Serialization::Archive valid{std::move(bytes),true};Serialization::Reader r{valid};
    std::vector<u32> got;std::string s;r.Read(got);r.Read(s);assert(got==expected&&s==label);
    auto stage=[](u64 hash,size_t perm,unsigned module,unsigned hw=1){
        PipelineCache::OrderWarmStage a; a.program=std::make_unique<Program>();
        a.info=std::make_unique<Info>();a.program->info={hash,hw,2};*a.info=a.program->info;
        a.permutation=perm;a.module=module;return a;
    };
    PipelineCache p;
    auto a=stage(10,2,5);assert(p.MergeOrderWarmStage(a)&&!a.module);
    auto* live=p.program_cache.at(10)->modules[2].info.get();
    auto duplicate=stage(10,2,6);assert(!p.MergeOrderWarmStage(duplicate)&&duplicate.module==6);
    auto b=stage(10,1,7);assert(p.MergeOrderWarmStage(b));
    assert(p.program_cache.at(10)->modules[2].info.get()==live);
    auto wrong_stage=stage(10,0,8,2);assert(!p.MergeOrderWarmStage(wrong_stage));
    p.order_warmup->live_hashes.insert(10);
    auto late=stage(10,0,9);assert(!p.MergeOrderWarmStage(late)&&late.module==9);
    p.order_warmup->live_hashes.insert(11);
    auto live_miss=stage(11,0,10);assert(!p.MergeOrderWarmStage(live_miss)&&!p.program_cache.contains(11));
    std::cout<<"ORDER_WARMUP_PASS bounded queue/cancel/checked reader/variant identity/live-writer exclusion\n";
}
''')
        subprocess.run(['c++','-std=c++20','-O2','-pthread','-I',str(d),'-I',str(v),str(d/'test.cpp'),'-o',str(d/'test')],check=True)
        subprocess.run([str(d/'test')],check=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);run(ap.parse_args().source)
