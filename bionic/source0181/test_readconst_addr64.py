#!/usr/bin/env python3
"""Run production ADDR64 dispatch, SRT predicates, bounds and GPU lowering.

Only the IR storage/API boundary is modeled. Function bodies are extracted
from --source, including the existing carry-address simplification. These
tests establish compiler behavior; they do not claim a GPU/gameplay result.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

from port_readconst_addr64 import function_span


def function(source, signature):
    start, end = function_span(source, signature)
    return source[start:end]


def run_cpp(code, name):
    with tempfile.TemporaryDirectory(prefix="bachata-readconst-") as directory:
        directory = Path(directory)
        source = directory / (name + ".cpp")
        binary = directory / name
        source.write_text(code)
        subprocess.run(["c++", "-std=c++23", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(source), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


def test_graph(shader):
    flatten = (shader / "ir/passes/flatten_extended_userdata_pass.cpp").read_text()
    functions = [function(flatten, signature) for signature in (
        "static inline u16 GetFlatbufOffset(", "static inline void SetFlatbufOffset(",
        "static bool IsAllowedOffsetInstruction(", "static bool IsUniformSrtSource(",
        "static bool IsCpuSrtOffset(", "static bool IsReadConstSource(",
        "static bool CanFlattenReadConst(", "void SimplifyReadConstAddressAdd(",
        "static u64 ReadConstIndexUpperBound(", "static std::optional<u32> ReadConstByteSpan(",
        "static bool ReadConstUniformBase(", "void LowerDynamicReadConstPass(")]
    header = (shader / "ir/ir_emitter.h").read_text()
    tag = re.search(r"constexpr u64 ReadConstAddr64Flag = [^;]+;", header)[0]
    predicate = function(header, "[[nodiscard]] inline bool IsReadConstAddr64(")
    emitter = (shader / "ir/ir_emitter.cpp").read_text()
    emitters = [function(emitter, signature) for signature in (
        "U32 IREmitter::ReadConst(", "U32 IREmitter::ReadConstAddr64(")]
    gvn = (shader / "ir/srt_gvn_table.h").read_text()
    start = gvn.index("    InstVector MakeInstVector(")
    end = gvn.index("\n    }", start) + len("\n    }")
    gvn_body = gvn[start:end]
    policy = function((shader / "readconst_policy.h").read_text(),
                      "inline bool BachataReadConstOrder(")
    constants = re.search(r"constexpr u32 OrderMaxReadConstBytes = [^;]+;", flatten)[0]
    opcodes = set(re.findall(r"(?:IR::)?Opcode::(\w+)", "\n".join(functions + emitters)))
    opcodes.update(["GetAttributeU32", "SelectU32", "ReadConstArray"])
    cpp = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <list>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>
using u16=std::uint16_t;using u32=std::uint32_t;using u64=std::uint64_t;
#define ASSERT(x) do { if (!(x)) throw std::runtime_error("assertion"); } while(false)
#define ASSERT_MSG(x,...) ASSERT(x)
#define UNREACHABLE_MSG(...) throw std::runtime_error("unreachable")
template<class... A> void Log(A&&...) {}
#define LOG_INFO(category,...) Log(__VA_ARGS__)
#define LOG_ERROR(category,...) Log(__VA_ARGS__)
#define LOG_WARNING(category,...) Log(__VA_ARGS__)
namespace Common {
struct ElfInfo {std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo e;return e;}
    const std::string& GameSerial()const{return serial;}};
}
struct Settings {bool dma=false;bool IsDirectMemoryAccessEnabled()const{return dma;}} EmulatorSettings;
namespace AmdGpu {struct Buffer {};}
namespace Shader {
using SharpLocation=u16;
constexpr u32 NUM_BUFFERS=8;
template<class> struct SharpFetch {
    std::array<u32,4> immediates{};std::array<SharpLocation,4> offsets{};u32 load_mask{};
    bool operator==(const SharpFetch&)const=default;
};
enum class BufferType {Guest,ReadConst};
namespace IR {
enum class Opcode {'''+",".join(sorted(opcodes))+r'''};
enum class Type {U32};
using ScalarReg=u32;
struct Inst;struct Block;
struct Value {
    u32 immediate{};IR::Inst* instruction{};
    Value()=default;Value(u32 n):immediate(n){};Value(IR::Inst* p):instruction(p){}
    bool IsImmediate()const{return instruction==nullptr;}
    IR::Inst* Inst()const{ASSERT(instruction);return instruction;}
    IR::Inst* TryInst()const{return instruction;}
    u32 U32()const{ASSERT(IsImmediate());return immediate;}
    IR::ScalarReg ScalarReg()const{return U32();}
    bool operator==(const Value&)const=default;
};
using U32=Value;
struct Field16 {u16 value{};void Assign(u16 x){value=x;}operator u16()const{return value;}};
struct BufferInstInfo {Field16 flatbuf_off_dw{};};
struct Use {IR::Inst* user{};u32 operand{};};
struct Inst {
    Opcode opcode;std::vector<Value> args;IR::Block* parent{};
    u64 flags{};std::vector<Use> uses;std::optional<Value> replacement;
    Opcode GetOpcode()const{return opcode;}
    size_t NumArgs()const{return args.size();}Value Arg(size_t i)const{return args.at(i);}
    IR::Block* GetParent()const{return parent;}
    const auto& Uses()const{return uses;}
    template<class T>T Flags()const{T x;std::memcpy(reinterpret_cast<char*>(&x),&flags,sizeof(T));return x;}
    template<class T>void SetFlags(T x){std::memcpy(&flags,&x,sizeof(T));}
    void SetArg(size_t i,Value value){args.at(i)=value;}
    void ReplaceUsesWith(Value value){replacement=value;}
};
struct InstructionList:std::list<Inst>{static iterator s_iterator_to(Inst& inst);};
struct Block {
    using InstructionList=IR::InstructionList;InstructionList instructions;
    auto begin(){return instructions.begin();}auto end(){return instructions.end();}
    Inst* Add(Opcode op,std::initializer_list<Value> args={}){
        instructions.push_back({op,std::vector<Value>(args),this,{},{},{}});
        auto* node=&instructions.back();
        for(u32 i=0;i<node->args.size();++i)
            if(auto* source=node->args[i].TryInst())source->uses.push_back({node,i});
        return node;
    }
};
InstructionList::iterator InstructionList::s_iterator_to(Inst& inst){
    auto& list=inst.parent->instructions;
    return std::find_if(list.begin(),list.end(),[&](const Inst& x){return &x==&inst;});
}
struct IREmitter {
    Block& block;InstructionList::iterator where;
    IREmitter(Block& b,InstructionList::iterator it):block(b),where(it){}
    Value Emit(Opcode op,std::initializer_list<Value> args){
        auto node=block.instructions.insert(where,{op,std::vector<Value>(args),&block,{},{},{}});
        for(u32 i=0;i<node->args.size();++i)
            if(auto* source=node->args[i].TryInst())source->uses.push_back({&*node,i});
        return Value{&*node};
    }
    template<class T>T Inst(Opcode op,Value a,Value b){return Emit(op,{a,b});}
    Value Imm32(u32 n){return Value{n};}
    Value IAdd(Value a,Value b){return Emit(Opcode::IAdd32,{a,b});}
    Value ShiftRightLogical(Value a,Value b){return Emit(Opcode::ShiftRightLogical32,{a,b});}
    U32 ReadConst(const Value&,const U32&);U32 ReadConstAddr64(const Value&,const U32&);
    Value ReadConstBuffer(Value binding,Value index,BufferInstInfo){
        return Emit(Opcode::ReadConstBuffer,{binding,index});
    }
};
'''+tag+"\n"+predicate+"\n"+"\n".join(emitters)+r'''
}
struct BufferResource {
    SharpFetch<AmdGpu::Buffer> sharp_fetch{};IR::Type used_types{};
    BufferType buffer_type{};u32 readconst_size_bytes{};
};
namespace IR {
struct Program {
    struct Info {std::vector<BufferResource> buffers;u64 pgm_hash=0x1234;} info;
    std::vector<Block*> post_order_blocks;
};
}
'''+policy+r'''
namespace Optimization {
'''+constants+"\n"+"\n\n".join(functions)+r'''
struct GvnKey {
    using InstVector=std::vector<u32>;
    u32 GetValueNumber(IR::Value value) {
        return value.IsImmediate()?value.U32():u32(reinterpret_cast<std::uintptr_t>(value.TryInst()));
    }
'''+gvn_body+r'''
};
}
}
using namespace Shader;
using namespace Shader::Optimization;
using Op=IR::Opcode;
IR::Value I(u32 x){return IR::Value{x};}

void FlagsAndGvn() {
    IR::Block block;
    auto* lo=block.Add(Op::GetUserData,{I(2)});
    auto* hi=block.Add(Op::GetUserData,{I(3)});
    auto* base=block.Add(Op::CompositeConstructU32x2,{lo,hi});
    IR::IREmitter emitter{block,block.end()};
    const auto regular=emitter.ReadConst(base,I(0));
    const auto tagged=emitter.ReadConstAddr64(base,I(0));
    assert(!IR::IsReadConstAddr64(regular.Inst()) && IR::IsReadConstAddr64(tagged.Inst()));
    GvnKey gvn;
    assert(gvn.MakeInstVector(regular.Inst())!=gvn.MakeInstVector(tagged.Inst()));
    for(u16 offset:{u16{0},u16{1},u16{65535},u16{0}}) {
        SetFlatbufOffset(tagged.Inst(),offset);
        assert(GetFlatbufOffset(tagged.Inst())==offset);
        assert(IR::IsReadConstAddr64(tagged.Inst()));
    }
    auto* buffer=block.Add(Op::ReadConstBuffer,{I(0),I(0)});
    buffer->SetFlags(IR::ReadConstAddr64Flag);
    assert(!IR::IsReadConstAddr64(buffer));
    SetFlatbufOffset(buffer,47);
    assert(GetFlatbufOffset(buffer)==47);
}

void BoundsAndUniformity() {
    IR::Block b;
    auto* varying=b.Add(Op::GetAttributeU32);
    auto* uniform=b.Add(Op::GetUserData,{I(2)});
    auto* lane=b.Add(Op::ReadLane,{varying,I(0)});
    auto* shift=b.Add(Op::ShiftRightLogical32,{lane,I(2)});
    assert(ReadConstIndexUpperBound(lane)==UINT32_MAX);
    assert(ReadConstIndexUpperBound(shift)==UINT32_MAX/4);
    assert(!ReadConstByteSpan(shift));
    assert(ReadConstByteSpan(shift).value_or(OrderMaxReadConstBytes)==4*1024*1024);
    assert(ReadConstByteSpan(I(3'000'000))==12'000'004u); // exact known extent above fallback
    assert(!ReadConstByteSpan(I(UINT32_MAX)));
    assert(ReadConstByteSpan(I(0))==4);
    auto* masked=b.Add(Op::BitwiseAnd32,{varying,I(2047)});
    assert(ReadConstByteSpan(masked)==8192);
    auto* bigshift=b.Add(Op::ShiftLeftLogical32,{I(1),I(20)});
    assert(ReadConstByteSpan(bigshift)==4*1024*1024+4);
    auto* invalidshift=b.Add(Op::ShiftLeftLogical32,{I(1),I(32)});
    assert(!ReadConstByteSpan(invalidshift));
    auto* overflowing=b.Add(Op::IMul32,{I(UINT32_MAX),I(UINT32_MAX)});
    assert(!ReadConstByteSpan(overflowing));
    auto* summed=b.Add(Op::IAdd32,{I(UINT32_MAX-1),I(4)});
    assert(!ReadConstByteSpan(summed));
    auto* minimum=b.Add(Op::UMin32,{varying,I(15)});
    auto* maximum=b.Add(Op::UMax32,{minimum,I(31)});
    assert(ReadConstByteSpan(maximum)==128);
    assert(!IsCpuSrtOffset(lane) && !IsCpuSrtOffset(shift));
    auto* uniform_lane=b.Add(Op::ReadLane,{uniform,varying});
    assert(IsCpuSrtOffset(uniform_lane)); // uniform data is independent of selected lane
    auto* same_phi=b.Add(Op::Phi,{uniform,uniform});
    auto* varying_phi=b.Add(Op::Phi,{uniform,I(4)});
    assert(IsCpuSrtOffset(same_phi) && !IsCpuSrtOffset(varying_phi));
    auto* cycle=b.Add(Op::Phi,{I(0)});
    cycle->SetArg(0,cycle);
    assert(!IsCpuSrtOffset(cycle) && !ReadConstByteSpan(cycle));

    auto* base=b.Add(Op::CompositeConstructU32x2,{uniform,uniform});
    auto* read=b.Add(Op::ReadConst,{base,I(1)});
    assert(CanFlattenReadConst(read));
    read->SetFlags(IR::ReadConstAddr64Flag);
    assert(CanFlattenReadConst(read));
    read->SetArg(1,uniform);
    assert(!CanFlattenReadConst(read)); // tagged dynamic indexes stay GPU work
    read->SetFlags(u64{0});
    assert(CanFlattenReadConst(read)); // existing scalar SRT behavior preserved
    read->SetArg(1,lane);
    assert(!CanFlattenReadConst(read));
    base->SetArg(0,varying);
    read->SetArg(1,I(1));
    assert(!CanFlattenReadConst(read));
}

void Lowering() {
    IR::Block b;
    auto* lo=b.Add(Op::GetUserData,{I(2)});
    auto* hi=b.Add(Op::GetUserData,{I(3)});
    auto* base=b.Add(Op::CompositeConstructU32x2,{lo,hi});
    auto* lane=b.Add(Op::GetAttributeU32);
    auto* offset=b.Add(Op::ShiftRightLogical32,{lane,I(2)});
    auto* first=b.Add(Op::ReadConst,{base,I(2047)});
    auto* second=b.Add(Op::ReadConst,{base,offset});
    second->SetFlags(IR::ReadConstAddr64Flag);
    IR::Program p;p.post_order_blocks={&b};
    LowerDynamicReadConstPass(p);
    assert(p.info.buffers.size()==1);
    const auto& desc=p.info.buffers[0];
    assert(desc.readconst_size_bytes==4*1024*1024 && desc.sharp_fetch.load_mask==3);
    assert(desc.sharp_fetch.offsets[0]==2 && desc.sharp_fetch.offsets[1]==3);
    assert(first->replacement && second->replacement);
    assert(second->replacement->Inst()->GetOpcode()==Op::ReadConstBuffer);
    assert(second->replacement->Inst()->Arg(1)==IR::Value{offset});
    assert(first->replacement->Inst()->Arg(0).U32()==0);

    // A load with an existing flat slot stays a flat load and retains its tag.
    IR::Block flat;
    auto* already=flat.Add(Op::ReadConst,{base,I(1)});
    already->SetFlags(IR::ReadConstAddr64Flag);SetFlatbufOffset(already,25);
    IR::Program q;q.post_order_blocks={&flat};LowerDynamicReadConstPass(q);
    assert(q.info.buffers.empty() && !already->replacement && IR::IsReadConstAddr64(already));

    // Only unresolved ADDR64 has the donor's explicit null result without DMA.
    IR::Block missing;
    auto* vector_base=missing.Add(Op::CompositeConstructU32x2,{lane,lane});
    auto* addr64=missing.Add(Op::ReadConst,{vector_base,I(0)});
    addr64->SetFlags(IR::ReadConstAddr64Flag);
    IR::Program r;r.post_order_blocks={&missing};LowerDynamicReadConstPass(r);
    assert(addr64->replacement && addr64->replacement->IsImmediate() && addr64->replacement->U32()==0);
    auto* regular=missing.Add(Op::ReadConst,{vector_base,I(0)});
    bool rejected=false;
    try {LowerDynamicReadConstPass(r);}catch(const std::runtime_error&){rejected=true;}
    assert(rejected && !regular->replacement);
    EmulatorSettings.dma=true;LowerDynamicReadConstPass(r);
    assert(!regular->replacement);EmulatorSettings.dma=false;
    Common::ElfInfo::Instance().serial="CUSA00000";LowerDynamicReadConstPass(r);
    assert(!regular->replacement);Common::ElfInfo::Instance().serial="CUSA00785";

    SharpFetch<AmdGpu::Buffer> fetch{};
    IR::Block sources;
    auto* indirect=sources.Add(Op::ReadConst,{base,I(3)});
    auto* pair=sources.Add(Op::CompositeConstructU32x2,{indirect,I(0)});
    assert(!ReadConstUniformBase(pair,fetch));
    SetFlatbufOffset(indirect,35);
    assert(ReadConstUniformBase(pair,fetch));
    assert(fetch.offsets[0]==35 && fetch.immediates[1]==0 && fetch.load_mask==1);
}

void CarryAddress() {
    IR::Block b;
    auto* base_lo=b.Add(Op::GetUserData,{I(4)});
    auto* base_hi=b.Add(Op::GetUserData,{I(5)});
    auto* lane=b.Add(Op::GetAttributeU32);
    auto* lo=b.Add(Op::IAdd32,{base_lo,lane});
    auto* carry=b.Add(Op::SelectU32,{I(1),I(1),I(0)});
    auto* hi=b.Add(Op::IAdd32,{base_hi,carry});
    auto* address=b.Add(Op::CompositeConstructU32x2,{lo,hi});
    auto* read=b.Add(Op::ReadConst,{address,I(2)});
    auto* sibling=b.Add(Op::ReadConst,{address,I(3)});
    read->SetFlags(IR::ReadConstAddr64Flag);sibling->SetFlags(IR::ReadConstAddr64Flag);
    SimplifyReadConstAddressAdd(*read);
    assert(address->Arg(0)==IR::Value{base_lo} && address->Arg(1)==IR::Value{base_hi});
    assert(!read->Arg(1).IsImmediate() && !sibling->Arg(1).IsImmediate());
    assert(!CanFlattenReadConst(read) && !CanFlattenReadConst(sibling));
    assert(IR::IsReadConstAddr64(read) && IR::IsReadConstAddr64(sibling));
    IR::Program p;p.post_order_blocks={&b};LowerDynamicReadConstPass(p);
    assert(p.info.buffers.size()==1 && p.info.buffers[0].readconst_size_bytes==4*1024*1024);
    assert(read->replacement->Inst()->Arg(1)==read->Arg(1));
    assert(sibling->replacement->Inst()->Arg(1)==sibling->Arg(1));
}

int main() {
    FlagsAndGvn();BoundsAndUniformity();Lowering();CarryAddress();
    std::cout<<"BACHATA_READCONST_GRAPH_BOUNDS_PASS\n";
}
'''
    run_cpp(cpp, "readconst_graph")


def test_dispatch(shader):
    body = function((shader / "frontend/translate/vector_memory.cpp").read_text(),
                    "void Translator::BUFFER_LOAD(")
    policy = function((shader / "readconst_policy.h").read_text(),
                      "inline bool BachataReadConstOrder(")
    cpp = r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
using u32=std::uint32_t;using u64=std::uint64_t;
#define UNREACHABLE() assert(false)
namespace Common {struct ElfInfo {std::string serial="CUSA00785";
    static ElfInfo& Instance(){static ElfInfo e;return e;}
    const std::string& GameSerial()const{return serial;}};}
namespace AmdGpu {enum class DataFormat{FormatInvalid};enum class NumberFormat{Zero};}
namespace Shader {
'''+policy+r'''
namespace IR {
using VectorReg=u32;using ScalarReg=u32;
struct Value {std::array<u32,4> words{};u32 count=1;Value()=default;Value(u32 n):words{n}{}
    explicit Value(std::array<u32,4> a,u32 c):words(a),count(c){};u32 U32()const{return words[0];}};
using U32=Value;using U8=Value;using U16=Value;using F32=Value;
struct Field {u32 value{};template<class T>void Assign(T v){value=static_cast<u32>(v);}
    explicit operator bool()const{return value!=0;}};
struct BufferInstInfo {Field index_enable,voffset_enable,inst_offset,globally_coherent,
    system_coherent,typed,inst_data_fmt,inst_num_fmt,pc;};
struct Emitter {
    std::array<u32,256> vgpr{},sgpr{};
    struct Read {u64 base;u32 index;};std::vector<Read> reads;u32 fallback_loads=0;
    Value GetVectorReg(u32 r){return Value{vgpr.at(r)};}Value GetScalarReg(u32 r){return Value{sgpr.at(r)};}
    Value Imm32(u32 n){return Value{n};}
    Value IAdd(Value a,Value b){return Value{u32(a.U32()+b.U32())};}
    Value ShiftRightLogical(Value a,Value b){return Value{a.U32()>>b.U32()};}
    template<class... T>Value CompositeConstruct(T... v){return Value{{v.U32()...},sizeof...(v)};}
    Value CompositeExtract(Value a,u32 i){return Value{a.words.at(i)};}
    void SetVectorReg(u32 r,Value v){vgpr.at(r)=v.U32();}
    Value ReadConstAddr64(Value base,Value offset){
        reads.push_back({u64(base.words[0])|(u64(base.words[1])<<32),offset.U32()});
        return Value{0xabc00000u|u32(reads.size())};
    }
    Value LoadBufferFormat(Value,Value,BufferInstInfo){++fallback_loads;return Value{{1,2,3,4},4};}
    Value LoadBufferU8(Value,Value,BufferInstInfo){++fallback_loads;return Value{0x80};}
    Value LoadBufferU16(Value,Value,BufferInstInfo){++fallback_loads;return Value{0x8000};}
    Value LoadBufferU32(u32 count,Value,Value,BufferInstInfo){++fallback_loads;return Value{{1,2,3,4},count};}
    Value SConvert(u32,Value a){return a;}Value UConvert(u32,Value a){return a;}
};
}
namespace Gcn {
struct Operand {u32 code{};u32 value{};};
struct GcnInst {struct Control {struct MUBUF {bool idxen{},offen{},addr64{},glc{},slc{};u32 offset{};}mubuf;
    struct MTBUF {u32 dfmt{},nfmt{};}mtbuf;}control;std::array<Operand,4> src;};
struct Translator {IR::Emitter ir;u32 pc=0;
    IR::U32 GetSrc(Operand x){return IR::Value{x.value};}
    void BUFFER_LOAD(u32,bool,bool,const GcnInst&,u32=32,bool=false);
};
'''+body+r'''
}
}
using namespace Shader::Gcn;
int main() {
    unsigned cases=0;
    for(u32 count=1;count<=4;++count)for(bool index:{false,true})for(bool offset:{false,true})
    for(u32 imm:{0u,12u,4092u})for(u32 scalar:{0u,64u,UINT32_MAX-7}){
        Translator t;GcnInst g{};g.src[0].code=10;g.src[1].code=30;g.src[2].code=4;
        g.src[3].value=scalar;g.control.mubuf={index,offset,true,false,false,imm};
        t.ir.vgpr[10]=0x12345000;t.ir.vgpr[11]=8;
        t.BUFFER_LOAD(count,false,false,g);
        assert(t.ir.reads.size()==count && t.ir.fallback_loads==0);
        for(u32 i=0;i<count;++i){
            assert(t.ir.reads[i].base==0x812345000ull);
            assert(t.ir.reads[i].index==(u32(imm+scalar)>>2)+i);
            assert(t.ir.vgpr[30+i]==(0xabc00000u|(i+1)));
        }
        ++cases;
    }
    for(const char* title:{"CUSA00000","CUSA08809","CUSA08034","CUSA00785"})
    for(bool inst_typed:{false,true})for(bool buffer_typed:{false,true})
    for(u32 width:{8u,16u,32u})for(bool addr64:{false,true}){
        Common::ElfInfo::Instance().serial=title;
        Translator t;GcnInst g{};g.src[0].code=10;g.src[1].code=30;g.src[2].code=4;
        g.control.mubuf.addr64=addr64;t.BUFFER_LOAD(1,inst_typed,buffer_typed,g,width,false);
        const bool adapted=std::string(title)=="CUSA00785"&&addr64&&!inst_typed&&!buffer_typed&&width==32;
        assert(t.ir.reads.size()==unsigned(adapted));
        assert(t.ir.fallback_loads==unsigned(!adapted));
        ++cases;
    }
    std::cout<<"BACHATA_ADDR64_BUFFER_LOAD_PASS cases="<<cases<<'\n';
}
'''
    run_cpp(cpp, "readconst_dispatch")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    shader = args.source.resolve() / "src/shader_recompiler"
    test_graph(shader)
    test_dispatch(shader)
    print("BACHATA_ADDR64_READCONST_PROTOCOL_PASS")


if __name__ == "__main__":
    main()
