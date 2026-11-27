"""Exercise real Program and GetProgram methods with a controlled SRT/mapping fixture."""
from pathlib import Path
import argparse, subprocess, tempfile
p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path)
root=p.parse_args().source.resolve()/'src'
h=(root/'video_core/renderer_vulkan/vk_pipeline_cache.h').read_text()
c=(root/'video_core/renderer_vulkan/vk_pipeline_cache.cpp').read_text()
program=h[h.index('struct Program {'):h.index('struct DrawIndirectParams {')]
method=c[c.index('PipelineCache::Result PipelineCache::GetProgram('):c.index('std::optional<vk::ShaderModule> PipelineCache::ReplaceShader(')]
assert 'm.stage_spec_memo.valid = false;' in c
source=r'''
#include <cassert>
#include <algorithm>
#include <array>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <span>
#include <string>
#include <tuple>
#include <vector>
#include <cstdlib>
#include "common/types.h"
#include "video_core/renderer_vulkan/sotc_stage_spec_memo.h"
namespace vk{using ShaderModule=u64;}
namespace boost::container{template<class T,size_t N>using small_vector=std::vector<T>;}
namespace Common{struct ElfInfo{std::string serial="CUSA08809";static auto& Instance(){static ElfInfo info;return info;}std::string_view GameSerial(){return serial;}};}
struct {bool collect=false;bool IsShaderCollect(){return collect;}} EmulatorSettings;
namespace Core{struct Memory{u64 generation=2;static Memory* Instance(){static Memory mem;return &mem;}u64 MappingGeneration(){return generation;}};}
namespace Shader{
    enum class HwStage{Fragment,Compute,Vertex};enum class SwStage{Fragment,Compute,Vertex};
    namespace Backend{struct Bindings{u32 unified{},buffer{};bool operator==(const Bindings&)const=default;};}
    struct RuntimeInfo{u32 property{};struct{struct{u32 shared_memory_size{};}cs;}hw;bool operator==(const RuntimeInfo& b)const{return property==b.property;}};
    struct ShaderParams{std::span<const u32> user_data,code;u64 hash{},base{};u64 Base()const{return base;}};
    struct Info{HwStage hw_stage{};SwStage sw_stage{};u64 pgm_base{};std::span<const u32> user_data;std::vector<u32> flattened_ud_buf;u32 layout{};
        Info()=default;Info(HwStage h,SwStage s,ShaderParams p):hw_stage(h),sw_stage(s),pgm_base(p.base),user_data(p.user_data){}
        void RefreshFlatBuf(){flattened_ud_buf={user_data[layout],user_data[2]};}
        void AddBindings(Backend::Bindings& b){b.unified+=layout+1;}};
    namespace Gcn{struct FetchShaderData{bool Empty(){return true;}};}
    inline unsigned constructed=0;
    struct StageSpecialization{const Info* info{};u32 value{};RuntimeInfo runtime{};Backend::Bindings start{};Gcn::FetchShaderData fetch_shader_data{};
       StageSpecialization()=default;StageSpecialization(const Info& i,RuntimeInfo rt,int,Backend::Bindings b):info(&i),value(i.flattened_ud_buf[0]),runtime(rt),start(b){++constructed;}
       bool operator==(const StageSpecialization& b)const{return value==b.value&&runtime==b.runtime&&start==b.start;}};
}
namespace Vulkan{
using Shader::HwStage;using Shader::SwStage;
@PROGRAM@
u64 HashCombine(u64 h,size_t p){return h*32+p;}
void RegisterShaderMeta(auto&&...){ }
struct PipelineCache{
    struct ProgramMap{std::map<u64,std::unique_ptr<Program>> data;
        struct Iterator{std::unique_ptr<Program>* p;auto& value(){return *p;}};
        auto try_emplace(u64 hash){auto [it,ok]=data.try_emplace(hash);return std::pair{Iterator{&it->second},ok};}}program_cache;
    Shader::RuntimeInfo rt{};int profile=0;Shader::Gcn::FetchShaderData* fetch_shader{};
    std::function<void(Shader::Info&)> srt_sync;
    using Result=std::tuple<const Shader::Info*,vk::ShaderModule,u64>;
    auto BuildRuntimeInfo(HwStage,SwStage){return rt;}
    vk::ShaderModule CompileModule(Shader::Info& info,Shader::RuntimeInfo&,std::span<const u32>,size_t perm,Shader::Backend::Bindings& b){info.RefreshFlatBuf();info.AddBindings(b);return 100+perm;}
    Result GetProgram(HwStage,SwStage,const Shader::ShaderParams&,Shader::Backend::Bindings&);
};
@METHOD@
}
int main(){using namespace Vulkan;using namespace Shader;
    PipelineCache cache;std::array<u32,3> ud{10,20,0},code{0};ShaderParams params{ud,code,17,0x10000};
    auto& program=cache.program_cache.data[17]=std::make_unique<Program>(HwStage::Compute,SwStage::Compute,params);
    auto add=[&](u32 layout,u32 specialization,u64 module){auto info=std::make_unique<Info>(HwStage::Compute,SwStage::Compute,params);info->layout=layout;info->RefreshFlatBuf();StageSpecialization spec(*info,cache.rt,0,{});spec.value=specialization;program->AddPermut(module,std::move(spec),std::move(info));};
    add(0,11,200);add(1,20,201);
    unsigned syncs=0;bool gpu_dirty=false;
    cache.srt_sync=[&](Info& info){++syncs;if(gpu_dirty&&info.layout==0)info.flattened_ud_buf[0]=11;};
    const auto query=[&](u64 expected,u32 compiled,u32 synced,Backend::Bindings b={}){constructed=syncs=0;auto [info,module,hash]=cache.GetProgram(HwStage::Compute,SwStage::Compute,params,b);assert(module==expected&&hash==HashCombine(17,expected==200?0:1));assert(info&&constructed==compiled&&syncs==synced);assert(b.unified==info->layout+1);};
    query(201,2,2);query(201,0,2); // both negative and positive memo hits
    ud[2]=9;query(201,2,2);query(201,0,2); // flat/user mutation, still matches 2nd variant
    gpu_dirty=true;query(200,1,1);query(200,0,1); // live SRT changes, earlier candidate now wins
    gpu_dirty=false;query(201,1,2);query(201,0,2);
    Core::Memory::Instance()->generation=4;query(201,2,2);query(201,0,2);
    Core::Memory::Instance()->generation=5;query(201,2,2);query(201,2,2); // odd generation not reusable
    Core::Memory::Instance()->generation=6;query(201,2,2);query(201,0,2);
    params.base+=256;query(201,2,2);query(201,0,2);
    cache.rt.hw.cs.shared_memory_size=128;query(201,2,2);query(201,0,2);
    auto replacement=std::make_unique<Info>(*program->modules[1].effective_info);auto spec=program->modules[1].spec;
    program->InsertPermut(201,std::move(spec),1,std::move(replacement));query(201,1,2);query(201,0,2);
    EmulatorSettings.collect=true;query(201,2,2);query(201,2,2);EmulatorSettings.collect=false;
    Common::ElfInfo::Instance().serial="CUSA00785";query(201,2,2);query(201,2,2);
    std::cout<<"BACHATA_SOTC_STAGE_SPEC_REAL_METHOD_PASS cases=24\n";
}
'''
with tempfile.TemporaryDirectory() as d:
    f=Path(d)/'test.cpp';exe=Path(d)/'test';f.write_text(source.replace('@PROGRAM@',program).replace('@METHOD@',method))
    subprocess.run(['c++','-std=c++23','-O2','-I',str(root),str(f),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
