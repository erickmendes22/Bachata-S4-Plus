#!/usr/bin/env python3
"""Execute effective donor passes on IR graphs: LDS, divergence and missing lanes."""
import argparse
from pathlib import Path
import re
from test_donor_alu_semantics import run_cpp


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    args=parser.parse_args()
    passes=args.source/"src/shader_recompiler/ir/passes"
    files=[(passes/name).read_text() for name in
           ("donor_wave64_policy.h","donor_sotc_wave64.inc","donor_sotc_lds.inc","donor_order_lds.inc")]
    code="\n".join(re.sub(r"^\s*#(?:include|pragma)[^\n]*\n","",s,flags=re.M) for s in files)
    ops=set(re.findall(r"IR::Opcode::(\w+)",code))|{
        "Void","Phi","GetAttributeU32","IEqual","Barrier","SubgroupBarrier","IAdd32","ISub32",
        "ShiftRightLogical32","ShiftLeftLogical32","BitwiseAnd32","LoadSharedU32","LoadSharedU64",
        "WriteSharedU32","ReadLane","Ballot","UnpackUint2x32","CompositeExtractU32x2","BitCount"}
    cpp=r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <initializer_list>
#include <iostream>
#include <list>
#include <optional>
#include <queue>
#include <string>
#include <unordered_set>
#include <vector>
using u32=uint32_t;using u64=uint64_t;
#define ASSERT(x) assert(x)
#define LOG_INFO(...) ((void)0)
#define LOG_WARNING(...) ((void)0)
namespace Common {
template<class T,class U>auto AlignUp(T a,U b){return (a+b-1)/b*b;}
struct ElfInfo{std::string serial="CUSA08809";static ElfInfo& Instance(){static ElfInfo e;return e;}
std::string GameSerial()const{return serial;}};
}
namespace Shader {
enum class HwStage {Compute,Vertex,Fragment};
struct RuntimeInfo {struct HW {struct CS {std::array<u32,3> workgroup_size{64,1,1};u32 shared_memory_size=128;}cs;}hw;};
struct Profile{u32 subgroup_size=32;bool needs_lds_barriers=true;};
namespace IR {
enum class Opcode {'''+",".join(sorted(ops))+r'''};
enum class Attribute {LocalInvocationId,LocalInvocationIndex};
struct Inst;struct Block;
struct Value{
    uint64_t imm{};IR::Inst* inst{};
    Value()=default;Value(uint64_t n):imm(n){};Value(u32 n):imm(n){};Value(IR::Inst* p):inst(p){}
    bool IsImmediate()const{return !inst;}
    IR::Inst* Inst()const{assert(inst);return inst;}IR::Inst* TryInst()const{return inst;}
    u32 U32()const{assert(!inst);return imm;}bool U1()const{assert(!inst);return bool(imm);}
    IR::Attribute Attribute()const{return IR::Attribute(imm);}
};
using U1=Value;using U32=Value;using U64=Value;
struct Use{IR::Inst* user;};
struct Inst{
    Opcode op{};std::vector<Value> args;IR::Block* parent{};
    std::optional<Value> replacement;std::vector<Use> uses;
    Opcode GetOpcode()const{return op;}
    template<class T>T Flags()const{return T{};}
    Value Arg(size_t i)const{return args.at(i);}size_t NumArgs()const{return args.size();}
    void SetArg(size_t i,Value v){args.at(i)=v;}
    IR::Block* GetParent()const{return parent;}
    const std::vector<Use>& Uses()const{return uses;}
    void ReplaceUsesWithAndRemove(Value v){replacement=v;}
};
struct InstructionList:std::list<Inst>{static iterator s_iterator_to(Inst& inst);};
struct Block{
    using InstructionList=IR::InstructionList;InstructionList list;
    auto& Instructions(){return list;}const auto& Instructions()const{return list;}
    auto begin(){return list.begin();}auto end(){return list.end();}
    Inst* Add(Opcode op,std::initializer_list<Value> args={}){
        list.push_back({op,std::vector<Value>(args),this,{},{}});return &list.back();
    }
};
InstructionList::iterator InstructionList::s_iterator_to(Inst& inst){
    auto& list=inst.parent->list;return std::find_if(list.begin(),list.end(),[&](const Inst& p){return &p==&inst;});
}
bool IsPhi(const Inst& inst){return inst.GetOpcode()==Opcode::Phi;}
struct AbstractSyntaxNode{
    enum class Type {Block,If,EndIf,Loop,Repeat,Break,Return,Unreachable};
    struct Data{
        IR::Block* block{};
        struct If {IR::U1 cond;IR::Block* body{};IR::Block* merge{};}if_node;
        struct EndIf {IR::Block* merge{};}end_if;
        struct Loop {IR::Block* merge{};}loop;
        struct Repeat {IR::U1 cond;IR::Block* merge{};}repeat;
        struct Break {IR::U1 cond;IR::Block* merge{};}break_node;
    }data;
    Type type;
};
using AbstractSyntaxList=std::vector<AbstractSyntaxNode>;
struct Program{
    struct Info{HwStage hw_stage=HwStage::Compute;u32 shared_memory_scratch_size=0;u64 pgm_hash=0;}info;
    AbstractSyntaxList syntax_list;std::vector<Block*> blocks;
};
template<class Pred>auto BreadthFirstSearch(const Inst* start,Pred&& pred){
    std::queue<const Inst*> q;std::unordered_set<const Inst*> visited;
    q.push(start);visited.insert(start);
    while(!q.empty()){
        const auto* n=q.front();q.pop();if(auto r=pred(n))return r;
        for(const auto& a:n->args)if(a.inst&&visited.insert(a.inst).second)q.push(a.inst);
    }
    return std::optional<bool>{};
}
template<class Pred>auto BreadthFirstSearch(const Value& start,Pred&& pred){
    if(start.IsImmediate())return std::optional<bool>{};
    // The original donor callback takes a mutable pointer but only inspects it.
    return BreadthFirstSearch(start.inst,[&](const Inst* i){return pred(const_cast<Inst*>(i));});
}
struct IREmitter{
    Block& block;InstructionList::iterator where;
    IREmitter(Block& b,InstructionList::iterator it):block(b),where(it){}
    Value Emit(Opcode op,std::initializer_list<Value> args={}){
        auto it=block.list.insert(where,{op,std::vector<Value>(args),&block,{},{}});return Value{&*it};
    }
    Value Imm32(u32 v){return Value{v};}Value Imm64(u64 v){return Value{v};}
    void Barrier(){Emit(Opcode::Barrier);}void SubgroupBarrier(){Emit(Opcode::SubgroupBarrier);}
    Value GetAttributeU32(Attribute a){return Emit(Opcode::GetAttributeU32,{Value{u32(a)}});}
    Value ShiftRightLogical(Value a,Value b){return Emit(Opcode::ShiftRightLogical32,{a,b});}
    Value ShiftLeftLogical(Value a,Value b){return Emit(Opcode::ShiftLeftLogical32,{a,b});}
    Value BitwiseAnd(Value a,Value b){return Emit(Opcode::BitwiseAnd32,{a,b});}
    Value IAdd(Value a,Value b){return Emit(Opcode::IAdd32,{a,b});}
    Value ISub(Value a,Value b){return Emit(Opcode::ISub32,{a,b});}
    Value BitCount(Value a){return Emit(Opcode::BitCount,{a});}
    Value ReadLane(Value a,Value b){return Emit(Opcode::ReadLane,{a,b});}
    Value Ballot(Value a){return Emit(Opcode::Ballot,{a});}
    Value UnpackUint2x32(Value a){return Emit(Opcode::UnpackUint2x32,{a});}
    Value CompositeExtract(Value a,u32 b){return Emit(Opcode::CompositeExtractU32x2,{a,Value{b}});}
    void WriteShared(u32,Value a,Value b){Emit(Opcode::WriteSharedU32,{a,b});}
    Value LoadShared(u32 width,bool,Value a){return Emit(width==64?Opcode::LoadSharedU64:Opcode::LoadSharedU32,{a});}
};
}
}
'''+code+r'''
using namespace Shader;
namespace D=Shader::Optimization::DonorSotcWave64;
namespace O=Shader::Optimization::DonorOrderLds;
using Op=IR::Opcode;
IR::AbstractSyntaxNode BlockNode(IR::Block* b){IR::AbstractSyntaxNode n{};n.type=IR::AbstractSyntaxNode::Type::Block;n.data.block=b;return n;}
unsigned Count(const IR::Block& b,Op op){return std::count_if(b.list.begin(),b.list.end(),[&](const auto& i){return i.op==op;});}
int main(){
    unsigned cases=0;
    // Actual pass selects workgroup barriers for partial/full waves and
    // subgroup memory barriers for multi-wave reductions; zero LDS is untouched.
    for(u32 size:{16u,32u,64u,128u,256u})for(bool enabled:{false,true})for(bool memory:{false,true}){
        IR::Block b; b.Add(Op::WriteSharedU32);b.Add(Op::LoadSharedU32);b.Add(Op::Void);
        IR::Program p;p.blocks={&b};p.syntax_list={BlockNode(&b)};
        RuntimeInfo r;r.hw.cs.workgroup_size={size,1,1};r.hw.cs.shared_memory_size=memory?128:0;
        Profile profile;profile.needs_lds_barriers=enabled;
        D::SharedMemoryBarrierPass(p,r,profile);
        const unsigned expected=enabled&&memory?2:0;
        assert(Count(b,Op::Barrier)==(size<=64?expected:0));
        assert(Count(b,Op::SubgroupBarrier)==(size>64?expected:0));++cases;
    }
    // Donor Order handles non-64 threadgroups using subgroup memory ordering,
    // including its !needs_lds_barriers path. No zero-LDS insertion.
    for(u32 size:{16u,64u,128u})for(bool enabled:{false,true}){
        IR::Block b;b.Add(Op::WriteSharedU32);b.Add(Op::LoadSharedU32);b.Add(Op::Void);
        IR::Program p;p.blocks={&b};p.syntax_list={BlockNode(&b)};
        RuntimeInfo r;r.hw.cs.workgroup_size={size,1,1};Profile profile;profile.needs_lds_barriers=enabled;
        O::SharedMemoryBarrierPass(p,r,profile);
        const bool subgroup=size!=64||!enabled;
        assert(Count(b,Op::Barrier)==(subgroup?0:2));assert(Count(b,Op::SubgroupBarrier)==(subgroup?2:0));++cases;
    }
    // Reduction identities for an absent lane; never duplicate a sum/product.
    const std::pair<Op,u32> identities[]={{Op::FPMin32,0x7f800000u},{Op::FPMax32,0xff800000u},
        {Op::FPMul32,0x3f800000u},{Op::UMin32,0xffffffffu},{Op::BitwiseAnd32,0xffffffffu},
        {Op::SMin32,0x7fffffffu},{Op::SMax32,0x80000000u},{Op::IMul32,1u},
        {Op::FPAdd32,0u},{Op::IAdd32,0u},{Op::UMax32,0u},{Op::BitwiseOr32,0u},{Op::BitwiseXor32,0u}};
    for(auto [op,identity]:identities)for(u32 subgroup:{32u,64u}){
        IR::Block b;auto* value=b.Add(Op::GetAttributeU32,{IR::Value{u32(IR::Attribute::LocalInvocationId)}});
        auto* shuffle=b.Add(Op::ShuffleXor,{IR::Value{value},IR::Value{1u}});
        auto* step=b.Add(op,{IR::Value{value},IR::Value{shuffle}});
        auto* lane=b.Add(Op::ReadLane,{IR::Value{step},IR::Value{32u}});
        auto* plain=b.Add(Op::ReadLane,{IR::Value{value},IR::Value{33u}});
        auto* existing=b.Add(Op::ReadLane,{IR::Value{value},IR::Value{7u}});
        auto* dynamic=b.Add(Op::ReadLane,{IR::Value{value},IR::Value{value}});
        IR::Program p;p.blocks={&b};p.syntax_list={BlockNode(&b)};
        RuntimeInfo r;r.hw.cs.workgroup_size={16,1,1};Profile profile;profile.subgroup_size=subgroup;
        D::LowerWave64BallotPass(p,r,profile);
        assert(lane->replacement&&lane->replacement->U32()==identity);
        assert(!plain->replacement&&plain->Arg(1).U32()==(subgroup==64?1u:1u));
        assert(!existing->replacement&&existing->Arg(1).U32()==7);
        assert(!dynamic->replacement&&dynamic->Arg(1).TryInst()==value);++cases;
    }
    // Fixed-point uniformity: a constant ReadLane of a varying input is
    // uniform after wave64 lowering, so a branch on it can lower its own read.
    for(bool uniform_condition:{false,true}){
        IR::Block entry,body,merge;
        auto* laneid=entry.Add(Op::GetAttributeU32,{IR::Value{u32(IR::Attribute::LocalInvocationId)}});
        auto* first=entry.Add(Op::ReadLane,{IR::Value{laneid},IR::Value{0u}});
        auto* cond=entry.Add(Op::IEqual,{IR::Value{uniform_condition?first:laneid},IR::Value{0u}});
        auto* second=body.Add(Op::ReadLane,{IR::Value{laneid},IR::Value{32u}});
        entry.Add(Op::Void);body.Add(Op::Void);merge.Add(Op::Void);
        IR::AbstractSyntaxNode branch{},end{};
        branch.type=IR::AbstractSyntaxNode::Type::If;branch.data.if_node={IR::Value{cond},&body,&merge};
        end.type=IR::AbstractSyntaxNode::Type::EndIf;end.data.end_if.merge=&merge;
        IR::Program p;p.blocks={&entry,&body,&merge};p.syntax_list={BlockNode(&entry),branch,BlockNode(&body),end,BlockNode(&merge)};
        RuntimeInfo r;Profile profile;profile.subgroup_size=32;
        D::LowerWave64BallotPass(p,r,profile);
        assert(first->replacement.has_value());assert(second->replacement.has_value()==uniform_condition);
        assert(p.info.shared_memory_scratch_size==8);++cases;
    }
    // Divergent branches defer synchronization to their merge; a uniform
    // ReadLane condition can synchronize inside a one-wave body instead.
    for(bool uniform_condition:{false,true})for(u32 threads:{64u,128u}){
        IR::Block entry,body,merge;
        auto* laneid=entry.Add(Op::GetAttributeU32,{IR::Value{u32(IR::Attribute::LocalInvocationId)}});
        auto* lane=entry.Add(Op::ReadLane,{IR::Value{laneid},IR::Value{0u}});
        auto* cond=entry.Add(Op::IEqual,{IR::Value{uniform_condition?lane:laneid},IR::Value{0u}});
        body.Add(Op::WriteSharedU32);body.Add(Op::LoadSharedU32);body.Add(Op::Void);merge.Add(Op::Void);
        IR::AbstractSyntaxNode branch{},end{};
        branch.type=IR::AbstractSyntaxNode::Type::If;branch.data.if_node={IR::Value{cond},&body,&merge};
        end.type=IR::AbstractSyntaxNode::Type::EndIf;end.data.end_if.merge=&merge;
        IR::Program p;p.blocks={&entry,&body,&merge};p.syntax_list={BlockNode(&entry),branch,BlockNode(&body),end,BlockNode(&merge)};
        RuntimeInfo r;r.hw.cs.workgroup_size={threads,1,1};Profile profile;
        D::SharedMemoryBarrierPass(p,r,profile);
        const auto barrier=threads==64?Op::Barrier:Op::SubgroupBarrier;
        const bool uniform=uniform_condition&&threads==64;
        assert(Count(body,barrier)==(uniform?2:0));assert(Count(merge,barrier)==(uniform?0:1));++cases;
    }
    Common::ElfInfo::Instance().serial="OTHER";
    assert(!Optimization::BachataDonorIsSotc()&&!Optimization::BachataDonorIsOrder());
    Common::ElfInfo::Instance().serial="CUSA08034";assert(Optimization::BachataDonorIsSotc());
    Common::ElfInfo::Instance().serial="CUSA00785";assert(Optimization::BachataDonorIsOrder());
    std::cout<<"DONOR_WAVE64_LDS_GRAPH_EXECUTION_PASS cases="<<cases<<"\n";
}
'''
    run_cpp(cpp,"wave64_lds")


if __name__=="__main__":
    main()
