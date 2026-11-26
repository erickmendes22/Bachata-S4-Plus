#!/usr/bin/env python3
"""Compile the effective PM4 wire types, HLE producers and CP dispatch cases.

This gate uses the real enum, BitField, header writer, NOP writer, packet
layouts and HLE functions. Only the renderer/debug sink is substituted.
Sentinel buffers and UBSan cover lengths, payload offsets and DWORD alignment;
the DrawPipe gate separately executes the real FIFO's scalar ownership.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def block(text, marker, semicolon=False):
    first = text.index(marker)
    opening = text.index("{", first)
    depth = 0
    for pos in range(opening, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if not depth:
                end = pos + 1
                if semicolon:
                    assert text[end] == ";"
                    end += 1
                return text[first:end]
    raise AssertionError(f"unclosed source block: {marker}")


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
args = parser.parse_args()
src = Path(args.source).resolve() / "src"
enum = (src / "video_core/amdgpu/pm4_opcodes.h").read_text()
cmds = (src / "video_core/amdgpu/pm4_cmds.h").read_text()
lp = (src / "video_core/amdgpu/liverpool.cpp").read_text()
gnm = (src / "core/libraries/gnmdriver/gnmdriver.cpp").read_text()
gnm_h = (src / "core/libraries/gnmdriver/gnmdriver.h").read_text()
names = set(re.findall(r"^\s*(\w+)\s*=", block(enum, "enum class PM4ItOpcode"), re.M))
for rel, text in (("liverpool.cpp", lp), ("pm4_cmds.h", cmds), ("gnmdriver.cpp", gnm)):
    missing = set(re.findall(r"\bPM4ItOpcode::(\w+)", text)) - names
    assert not missing, f"{rel}: unknown effective PM4 opcode references: {sorted(missing)}"

wire = cmds[cmds.index("enum class PM4ShaderType"):cmds.index("union ContextControlEnable")]
for name in ("PM4CmdNop", "DrawIndirectArgs", "PM4CmdDrawIndirectMulti",
             "PM4CmdDrawIndirectCountMulti"):
    wire += block(cmds, f"struct {name} {{", True) + "\n"
producers = block(gnm, "enum ShaderStages", True) + "\n"
producers += re.search(r"static constexpr std::array indirect_sgpr_offsets[^;]+;", gnm)[0] + "\n"
producers += block(gnm, "template <u32 data_block_size>\nstatic inline u32* WriteTrailingNop") + "\n"
for name in ("sceGnmDrawIndirectCountMulti", "sceGnmDrawIndirectMulti"):
    signature = re.search(rf"s32 PS4_SYSV_ABI {name}\([^;]+;", gnm_h)
    assert signature, f"real HLE declaration missing: {name}"
    producers += signature[0] + "\n"
    producers += block(gnm, f"s32 PS4_SYSV_ABI {name}(") + "\n"
cases = "\n".join(block(lp, f"case PM4ItOpcode::{name}: {{")
                  for name in ("DrawIndirectMulti", "DrawIndirectCountMulti"))
assert "QueueIndirectDraw(" in cases and "rasterizer->DrawIndirect(" not in cases

HARNESS = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <limits>
#include <vector>
#include "common/types.h"
#include "common/bit_field.h"
#include "video_core/amdgpu/pm4_opcodes.h"
namespace AmdGpu {
@WIRE@
}
using namespace AmdGpu;
constexpr s32 ORBIS_OK=0;
#define LOG_TRACE(...) ((void)0)
static bool neo_mode{};
bool sceKernelIsNeoMode(){return neo_mode;}
@PRODUCERS@
namespace fmt {template<class T>int make_format_args(const T&){return 0;}}
struct DebugSink {
    bool enabled{};u32 dumps{};
    bool DumpingCurrentReg()const{return enabled;}
    void PushRegsDump(VAddr,uintptr_t,int){++dumps;}
} DebugState;
struct Renderer {
    u32 markers{};
    template<class F>void ScopeMarker(const char*,int,F&& fn){++markers;fn();}
};
struct DispatchProbe {
    struct Call {
        bool indexed;VAddr args;u32 offset,stride,max_count;VAddr count_address;
        u16 vertex_sgpr,instance_sgpr;
    };
    std::vector<Call> calls;
    Renderer renderer;
    Renderer* rasterizer{&renderer};
    VAddr indirect_args_addr{0x123456780000ull},base_addr{0xabcdef00};int regs{};
    void QueueIndirectDraw(bool indexed,VAddr args,u32 offset,u32 stride,u32 max_count,
                           VAddr count_address,u16 vertex_sgpr,u16 instance_sgpr){
        calls.push_back({indexed,args,offset,stride,max_count,count_address,vertex_sgpr,instance_sgpr});
    }
    void Decode(const u32* words){
        const auto* header=reinterpret_cast<const PM4Header*>(words);
        switch(header->type3.opcode.Value()){
@CASES@
        default:assert(false);
        }
    }
};
static_assert(sizeof(PM4Type3Header)==sizeof(u32));
static_assert(sizeof(PM4CmdDrawIndirectMulti)==7*sizeof(u32));
static_assert(sizeof(PM4CmdDrawIndirectCountMulti)==10*sizeof(u32));
static_assert(offsetof(PM4CmdDrawIndirectCountMulti,count_addr)==6*sizeof(u32));
static_assert(offsetof(PM4CmdDrawIndirectCountMulti,stride)==8*sizeof(u32));
static_assert(static_cast<u32>(PM4ItOpcode::DrawIndirectCountMulti)==0x9c);
constexpr u32 Sentinel=0xa5ed7f11u;
template<class T>T Read(const u32* words){
    std::array<u32,sizeof(T)/sizeof(u32)> encoded;
    std::memcpy(encoded.data(),words,sizeof(T));return std::bit_cast<T>(encoded);
}
void Walk(const u32* words,u32 size,const std::vector<PM4ItOpcode>& ops,
          const std::vector<u32>& payloads){
    u32 pos=0;size_t packet=0;
    while(pos<size){
        const auto header=Read<PM4Type3Header>(words+pos);
        assert(header.type.Value()==3 && packet<ops.size());
        assert(header.opcode.Value()==ops[packet] && header.NumWords()==payloads[packet]);
        pos+=header.NumWords()+1;++packet;
    }
    assert(pos==size && packet==ops.size());
}
void Bounds(const std::array<u32,24>& words,u32 first,u32 size){
    for(u32 i=0;i<words.size();++i)
        if(i<first || i>=first+size)assert(words[i]==Sentinel);
}
void CheckCall(const DispatchProbe& probe,u32 offset,u32 stride,u32 max_count,VAddr count,
               u16 vertex,u16 instance){
    assert(probe.calls.size()==1);
    const auto& call=probe.calls[0];
    assert(!call.indexed && call.args==probe.indirect_args_addr && call.offset==offset);
    assert(call.stride==stride && call.max_count==max_count && call.count_address==count);
    assert(call.vertex_sgpr==vertex && call.instance_sgpr==instance);
}
int main(){
    u32 successful=0;
    for(bool neo:{false,true})for(u32 skew:{0u,1u})for(u32 stage=0;stage<ShaderStages::Max;++stage)
    for(u32 vertex:{0u,1u,15u})for(u32 instance:{0u,2u,15u})
    for(u32 flags:{0u,1u,0xe0000001u,0x9ffffffeu})for(u32 max_count:{0u,7u,0xffffffffu}){
        neo_mode=neo;
        const u32 expected_vertex=vertex?vertex+indirect_sgpr_offsets[stage]:0;
        const u32 expected_instance=instance?instance+indirect_sgpr_offsets[stage]:0;
        const u32 initiator=neo?((flags&0xe0000000u)|2u):2u;
        alignas(8) std::array<u32,24> words;
        const u32 first=2+skew;
        auto* cmdbuf=words.data()+first;
        words.fill(Sentinel);
        assert(sceGnmDrawIndirectMulti(cmdbuf,11,0x34,max_count,stage,vertex,instance,flags)==0);
        Bounds(words,first,11);
        Walk(cmdbuf,11,{PM4ItOpcode::DrawIndirectMulti,PM4ItOpcode::Nop},{6,3});
        const auto multi=Read<PM4CmdDrawIndirectMulti>(cmdbuf);
        assert(multi.header.shader_type.Value()==PM4ShaderType::ShaderGraphics);
        assert(static_cast<u32>(multi.header.predicate.Value())==(flags&1));
        assert(multi.data_offset==0x34 && multi.dw2==expected_vertex && multi.dw3==expected_instance);
        assert(multi.count==max_count && multi.stride==sizeof(DrawIndirectArgs));
        assert(multi.draw_initiator==initiator && cmdbuf[8]==0);
        assert(cmdbuf[9]==Sentinel && cmdbuf[10]==Sentinel);
        DispatchProbe multi_probe;multi_probe.Decode(cmdbuf);
        CheckCall(multi_probe,0x34,16,max_count,0,expected_vertex,expected_instance);
        ++successful;
        for(u64 count_address:{0ull,0x12345678abcdef00ull}){
            words.fill(Sentinel);
            assert(sceGnmDrawIndirectCountMulti(cmdbuf,16,0x74,max_count,count_address,
                                                stage,vertex,instance,flags)==0);
            Bounds(words,first,16);
            Walk(cmdbuf,16,{PM4ItOpcode::Nop,PM4ItOpcode::DrawIndirectCountMulti,PM4ItOpcode::Nop},
                          {2,9,2});
            assert(cmdbuf[1]==0 && cmdbuf[2]==Sentinel && cmdbuf[14]==0 && cmdbuf[15]==Sentinel);
            const auto count=Read<PM4CmdDrawIndirectCountMulti>(cmdbuf+3);
            assert(static_cast<u32>(count.header.predicate.Value())==(flags&1));
            assert(count.header.shader_type.Value()==PM4ShaderType::ShaderGraphics);
            assert(count.data_offset==0x74 && count.dw2==expected_vertex && count.dw3==expected_instance);
            assert(count.dw4==(count_address?1u<<30:0u));
            assert(count.count==max_count && count.count_addr==count_address && count.stride==16);
            assert(count.draw_initiator==initiator);
            DispatchProbe probe;probe.Decode(cmdbuf+3);
            words.fill(0); // The CP captures scalar values before PM4 storage is recycled.
            CheckCall(probe,0x74,16,max_count,count_address,expected_vertex,expected_instance);
            ++successful;
        }
    }
    // Rejected arguments leave the complete caller buffer unchanged.
    std::array<u32,24> words;words.fill(Sentinel);const auto untouched=words;
    auto count=[&](u32*ptr,u32 size,u32 stage,u32 v,u32 i){
        assert(sceGnmDrawIndirectCountMulti(ptr,size,4,8,0x123456780000ull,stage,v,i,1)==-1);
        assert(words==untouched);
    };
    auto multi=[&](u32*ptr,u32 size,u32 stage,u32 v,u32 i){
        assert(sceGnmDrawIndirectMulti(ptr,size,4,8,stage,v,i,1)==-1);assert(words==untouched);
    };
    count(nullptr,16,2,1,1);multi(nullptr,11,2,1,1);
    for(u32 size:{0u,1u,10u,11u,15u,17u,0xffffffffu})count(words.data(),size,2,1,1);
    for(u32 size:{0u,1u,10u,12u,15u,16u,0xffffffffu})multi(words.data(),size,2,1,1);
    for(u32 stage:{static_cast<u32>(ShaderStages::Max),0xffffffffu}){
        count(words.data(),16,stage,1,1);multi(words.data(),11,stage,1,1);
    }
    for(u32 invalid:{16u,17u,0xffffffffu}){
        count(words.data(),16,2,invalid,1);count(words.data(),16,2,1,invalid);
        multi(words.data(),11,2,invalid,1);multi(words.data(),11,2,1,invalid);
    }
    assert(sceGnmDrawIndirectCountMulti(words.data(),16,0x50,19,0x123456780000ull,2,1,2,0)==0);
    // Raw PM4 may select another stride or disable memory count despite a nonzero address.
    words[3+8]=64;words[3+4]=0;
    DebugState.enabled=true;
    DispatchProbe raw;raw.Decode(words.data()+3);
    CheckCall(raw,0x50,64,19,0,0x4d,0x4e);assert(DebugState.dumps==1);
    raw.rasterizer=nullptr;raw.Decode(words.data()+3);
    assert(raw.calls.size()==1 && raw.renderer.markers==1 && DebugState.dumps==2);
    assert(sceGnmDrawIndirectMulti(words.data(),11,0x28,23,2,1,2,0)==0);
    words[5]=48;DispatchProbe raw_multi;raw_multi.Decode(words.data());
    CheckCall(raw_multi,0x28,48,23,0,0x4d,0x4e);
    std::cout<<"BACHATA_PM4_INDIRECT_FAMILY_PASS cases="<<successful
             <<" enum/real-wire/HLE/CP/sentinels/count-address/stride/DWORD-alignment/invalid-ABI\n";
}
'''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    source = folder / "pm4.cpp"
    executable = folder / "pm4"
    source.write_text(HARNESS.replace("@WIRE@", wire).replace("@PRODUCERS@", producers)
                      .replace("@CASES@", cases))
    subprocess.run(["c++", "-std=c++23", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-fsanitize=undefined", "-fno-sanitize-recover=all",
                    "-I", str(src), str(source), "-o", str(executable)], check=True)
    subprocess.run([str(executable)], check=True, timeout=30)
