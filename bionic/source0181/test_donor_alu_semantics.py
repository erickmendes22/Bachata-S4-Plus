#!/usr/bin/env python3
"""Execute actual patched translator/emitter bodies against arithmetic/CFG models.

The models supply the IR/SPIR-V API boundary only. Instruction dispatch, legacy
arithmetic, NaN comparisons, trinary logic and atomic branch/Phi construction
come from the effective source passed to --source. No GPU success is implied.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

from port_donor_alu_semantics import function_span


def function(source, signature):
    a, b = function_span(source, signature)
    return source[a:b]


def run_cpp(code, name):
    with tempfile.TemporaryDirectory(prefix="bachata-alu-") as directory:
        source = Path(directory) / (name + ".cpp")
        exe = Path(directory) / name
        source.write_text(code)
        subprocess.run(["c++", "-std=c++23", "-O2", "-ffp-contract=off", "-Wall", "-Wextra",
                        "-Werror", str(source), "-o", str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


def test_translator(root):
    source = (root / "frontend/translate/vector_alu.cpp").read_text()
    dispatch = function(source, "void Translator::EmitVectorAlu(")
    selected = {}
    for match in re.finditer(r"    case Opcode::(\w+):", dispatch):
        opcode = match[1]
        if opcode == "V_CMP_CLASS_F32":
            continue
        if not (re.fullmatch(r"V_CMPX?_\w+_F(?:32|64)", opcode) or opcode in {
                "V_MAC_LEGACY_F32", "V_MUL_LEGACY_F32", "V_MAD_LEGACY_F32",
                "V_LOG_CLAMP_F32", "V_RCP_CLAMP_F32", "V_RSQ_CLAMP_F32", "V_RSQ_LEGACY_F32"}):
            continue
        rest = dispatch[match.start():]
        end = rest.find("\n    case Opcode::", 1)
        if end < 0:
            raise AssertionError("Missing next dispatch case: " + opcode)
        # Trim section comments only; preserve the whole legacy-RSQ block.
        text = rest[:end].split("\n        //")[0]
        selected[opcode] = text
    assert len(selected) == 47, selected.keys()
    declarations = """
    IR::F32 FPMulLegacy(const IR::F32&,const IR::F32&);
    IR::F32 ClampInfToMax(const IR::F32&);
    void EmitVectorAlu(const GcnInst&);
    void V_MUL_LEGACY_F32(const GcnInst&);
    void V_MAC_LEGACY_F32(const GcnInst&);
    void V_MAD_LEGACY_F32(const GcnInst&);
    void V_CMP_F32(ConditionOp,bool,bool,const GcnInst&);
    void V_CMP_F64(ConditionOp,bool,bool,const GcnInst&);
"""
    definitions = [function(source, signature) for signature in (
        "IR::F32 Translator::FPMulLegacy(", "IR::F32 Translator::ClampInfToMax(",
        "void Translator::V_MUL_LEGACY_F32(", "void Translator::V_MAC_LEGACY_F32(",
        "void Translator::V_MAD_LEGACY_F32(", "void Translator::V_CMP_F32(",
        "void Translator::V_CMP_F64(")]
    expected = {"F": "false", "TRU": "true", "EQ": "!nan && x==y", "LG": "!nan && x!=y",
                "GT": "x>y", "LT": "x<y", "LE": "x<=y", "GE": "x>=y", "U": "nan",
                "NGE": "!(x>=y)", "NGT": "!(x>y)", "NLE": "!(x<=y)",
                "NEQ": "nan || x!=y", "NLT": "!(x<y)", "NLG": "nan || x==y"}
    cases = []
    for opcode in selected:
        match = re.fullmatch(r"V_CMP(X?)_(\w+)_F(32|64)", opcode)
        if match:
            cases.append("{Opcode::" + opcode + "," + ("true" if match[1] else "false") +
                         "," + match[3] + ", [](double x,double y){ const bool nan="
                         "std::isnan(x)||std::isnan(y);(void)nan;(void)x;(void)y;return " +
                         expected[match[2]] + ";}}")
    cpp = r'''
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
using u64=uint64_t;
#define UNREACHABLE() throw std::runtime_error("unreachable comparison")
namespace IR {using F32=float;using F64=double;using U1=bool;using U64=u64;}
struct Emitter {
    bool exec=true;
    float Imm32(float x){return x;}
    bool Imm1(bool x){return x;}
    bool LogicalOr(bool a,bool b){return a||b;}
    bool LogicalAnd(bool a,bool b){return a&&b;}
    template<class T>T Select(bool a,T b,T c){return a?b:c;}
    template<class T>T FPMul(T a,T b){return a*b;}
    template<class T>T FPAdd(T a,T b){return a+b;}
    template<class T>bool FPIsNan(T a){return std::isnan(a);}
    template<class T>bool FPIsInf(T a){return std::isinf(a);}
    template<class T>bool FPEqual(T a,T b,bool ordered=true){return std::isnan(a)||std::isnan(b)?!ordered:a==b;}
    template<class T>bool FPNotEqual(T a,T b,bool ordered=true){return std::isnan(a)||std::isnan(b)?!ordered:a!=b;}
    template<class T>bool FPGreaterThan(T a,T b,bool ordered=true){return std::isnan(a)||std::isnan(b)?!ordered:a>b;}
    template<class T>bool FPLessThan(T a,T b,bool ordered=true){return std::isnan(a)||std::isnan(b)?!ordered:a<b;}
    template<class T>bool FPGreaterThanEqual(T a,T b,bool ordered=true){return std::isnan(a)||std::isnan(b)?!ordered:a>=b;}
    template<class T>bool FPLessThanEqual(T a,T b,bool ordered=true){return std::isnan(a)||std::isnan(b)?!ordered:a<=b;}
    float FPLog2(float a){return std::log2(a);}
    float FPRecip(float a){return 1.f/a;}
    float FPRecipSqrt(float a){return 1.f/std::sqrt(a);}
    bool GetExec(){return exec;} void SetExec(bool a){exec=a;}
    u64 Ballot(bool a){return a?1:0;}
};
enum class ConditionOp {F,TRU,EQ,LG,GT,LT,LE,GE,U};
enum class Opcode {'''+",".join(selected)+r'''};
struct Operand {double value;};
struct GcnInst {Opcode opcode;std::array<Operand,3> src;std::array<Operand,2> dst;};
struct Translator {
    Emitter ir;float result=0;u64 mask=0;
    template<class T>T GetSrc(Operand a){return static_cast<T>(a.value);}
    template<class T>T GetSrc64(Operand a){return static_cast<T>(a.value);}
    void SetDst(Operand,float a){result=a;}void SetDst64(Operand,u64 a){mask=a;}
'''+declarations+"\n};\n"+"\n\n".join(definitions)+r'''
void Translator::EmitVectorAlu(const GcnInst& inst){switch(inst.opcode){
'''+"\n".join(selected.values())+r'''
}}
bool Same(float actual,float expected){return std::isnan(expected)?std::isnan(actual):actual==expected;}
int main(){
    const double nan=std::numeric_limits<double>::quiet_NaN();
    const double inf=std::numeric_limits<double>::infinity();
    std::array<double,9> values{nan,inf,-inf,0.0,-0.0,1.0,-1.0,7.0,-7.0};
    struct Compare {Opcode op;bool set_exec;int width;bool(*expected)(double,double);};
    const Compare cases[]={'''+",\n".join(cases)+r'''};
    unsigned checked=0;
    for(const auto& c:cases)for(double x:values)for(double y:values)for(bool active:{false,true}){
        if(c.width==32){x=static_cast<float>(x);y=static_cast<float>(y);}
        Translator t;t.ir.exec=active;
        GcnInst inst{c.op,{{{x},{y},{0}}},{{{0},{0}}}};
        t.EmitVectorAlu(inst);
        const bool expected=c.expected(x,y)&&(active||!c.set_exec);
        assert(t.mask==unsigned(expected));
        assert(t.ir.exec==(c.set_exec?expected:active));
        ++checked;
    }
    for(double x:values)for(double y:values){
        float a=x,b=y;const float p=(a==0||b==0)?0.0f:a*b;
        for(auto op:{Opcode::V_MUL_LEGACY_F32,Opcode::V_MAC_LEGACY_F32,Opcode::V_MAD_LEGACY_F32}){
            Translator t;GcnInst inst{op,{{{x},{y},{11}}},{{{7},{0}}}};
            t.EmitVectorAlu(inst);
            const float expected=op==Opcode::V_MAC_LEGACY_F32?p+7:op==Opcode::V_MAD_LEGACY_F32?p+11:p;
            assert(Same(t.result,expected));
            if(op==Opcode::V_MUL_LEGACY_F32&&(a==0||b==0))assert(!std::signbit(t.result));
            ++checked;
        }
    }
    for(double x:values)for(auto op:{Opcode::V_LOG_CLAMP_F32,Opcode::V_RCP_CLAMP_F32,
                                   Opcode::V_RSQ_CLAMP_F32,Opcode::V_RSQ_LEGACY_F32}){
        Translator t;GcnInst inst{op,{{{x},{0},{0}}},{{{0},{0}}}};t.EmitVectorAlu(inst);
        float input=x;
        float expected=op==Opcode::V_LOG_CLAMP_F32?std::log2(input):op==Opcode::V_RCP_CLAMP_F32?
                       1.f/input:1.f/std::sqrt(input);
        if(op==Opcode::V_RSQ_LEGACY_F32&&input==0)expected=0;
        if(std::isinf(expected))expected=std::copysign(std::numeric_limits<float>::max(),expected);
        assert(Same(t.result,expected));++checked;
    }
    std::cout<<"DONOR_ALU_DISPATCH_LEGACY_NAN_EXEC_PASS cases="<<checked<<"\n";
}
'''
    run_cpp(cpp, "translator")


def test_trinary(root):
    source = (root / "backend/spirv/emit_spirv_floating_point.cpp").read_text()
    bodies = "\n".join(function(source, f"Id {name}(") for name in
                       ("EmitFPMinTri32", "EmitFPMaxTri32", "EmitFPMedTri32"))
    cpp = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
using Id=float;
struct EmitContext {
    Id F32[2]{},U1[2]{};
    Id OpNMin(Id,Id a,Id b){return std::fmin(a,b);}
    Id OpNMax(Id,Id a,Id b){return std::fmax(a,b);}
    Id OpFMin(Id,Id a,Id b){return std::min(a,b);}
    Id OpFMax(Id,Id a,Id b){return std::max(a,b);}
    Id OpLogicalOr(Id,Id a,Id b){return bool(a)||bool(b);}
    Id OpIsNan(Id,Id a){return std::isnan(a);}
    Id OpSelect(Id,Id cond,Id a,Id b){return cond?a:b;}
};
'''+bodies+r'''
int main(){
    const float nan=std::numeric_limits<float>::quiet_NaN();
    const float inf=std::numeric_limits<float>::infinity();
    const float values[]={nan,inf,-inf,0.f,-0.f,1.f,-1.f,7.f,-7.f};
    unsigned checked=0;
    for(float a:values)for(float b:values)for(float c:values){
        EmitContext ctx;
        const auto min=std::fmin(a,std::fmin(b,c));
        const auto max=std::fmax(a,std::fmax(b,c));
        std::array<float,3> sorted{a,b,c};
        const bool any_nan=std::isnan(a)||std::isnan(b)||std::isnan(c);
        float median=min;
        if(!any_nan){std::sort(sorted.begin(),sorted.end());median=sorted[1];}
        const auto same=[](float x,float y){return std::isnan(y)?std::isnan(x):x==y;};
        assert(same(EmitFPMinTri32(ctx,a,b,c),min));
        assert(same(EmitFPMaxTri32(ctx,a,b,c),max));
        assert(same(EmitFPMedTri32(ctx,a,b,c),median));++checked;
    }
    std::cout<<"DONOR_TRINARY_NAN_PASS cases="<<checked<<"\n";
}
'''
    run_cpp(cpp, "trinary")


def test_atomics(root):
    source = (root / "backend/spirv/emit_spirv_atomic.cpp").read_text()
    helper = "template <typename NegFn, typename NonNegFn>\n" + function(source, "Id AtomicF32MinMaxFallback(")
    bodies = "\n".join(function(source, f"Id Emit{kind}AtomicF{op}32(")
                       for kind in ("Buffer", "Image") for op in ("Min", "Max"))
    # Interpret the control flow emitted by the actual production helper.
    # Atomic operations mutate only when their instruction block executes.
    cpp = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <tuple>
#include <vector>
using u32=uint32_t;using Id=int;
namespace IR{struct Inst{};}
namespace spv{enum class SelectionControlMask{MaskNone};}
namespace Sirit{struct Module{
    Id OpAtomicFMin(Id,Id,Id,Id,Id){return 0;}
    Id OpAtomicFMax(Id,Id,Id,Id,Id){return 0;}
};}
enum Kind {UMin,UMax,SMin,SMax,FMin,FMax};
struct EmitContext{
    struct Profile {bool supports_buffer_fp32_atomic_min_max=false;
                    bool supports_image_fp32_atomic_min_max=false;}profile;
    Id F32[2]{},U32[2]{},U1[2]{};
    std::vector<std::function<u32()>> expr{[]{return u32(0);}};
    struct Ins{int op;Id a,b,c,d,e;};
    std::vector<Ins> code;
    std::map<Id,u32> resolved;
    Id u32_zero_value=ConstU32(0);
    Id Add(std::function<u32()> e){expr.push_back(e);return expr.size()-1;}
    u32 Get(Id x){return expr.at(x)();}
    Id ConstU32(u32 x){return Add([=]{return x;});}
    Id OpBitcast(Id,Id x){return x;}
    Id OpBitFieldUExtract(Id,Id x,Id start,Id len){return Add([=,this]{return (Get(x)>>Get(start))&((u32(1)<<Get(len))-1);});}
    Id OpINotEqual(Id,Id a,Id b){return Add([=,this]{return u32(Get(a)!=Get(b));});}
    Id OpLabel(){return Add([]{throw std::runtime_error("read label");return u32(0);});}
    void OpSelectionMerge(Id,spv::SelectionControlMask){}
    void OpBranchConditional(Id cond,Id yes,Id no){code.push_back({1,cond,yes,no,0,0});}
    void AddLabel(Id label){code.push_back({2,label,0,0,0,0});}
    void OpBranch(Id label){code.push_back({3,label,0,0,0,0});}
    Id Atomic(Kind kind,Id value){
        const Id result=expr.size();
        Add([=,this]{return resolved.at(result);});
        code.push_back({4,result,Id(kind),value,0,0});return result;
    }
    Id OpPhi(Id,Id a,Id alabel,Id b,Id blabel){
        const Id result=expr.size();Add([=,this]{return resolved.at(result);});
        code.push_back({5,result,a,alabel,b,blabel});return result;
    }
    std::tuple<u32,u32,unsigned> Run(Id result,u32 memory){
        std::map<Id,size_t> labels;
        for(size_t i=0;i<code.size();++i)if(code[i].op==2)labels[code[i].a]=i;
        unsigned mutations=0,steps=0;Id current=0,previous=0;
        for(size_t pc=0;pc<code.size();++pc){
            assert(++steps<30);auto ins=code[pc];
            if(ins.op==1){previous=current;pc=labels.at(Get(ins.a)?ins.b:ins.c)-1;}
            else if(ins.op==2)current=ins.a;
            else if(ins.op==3){previous=current;pc=labels.at(ins.a)-1;}
            else if(ins.op==4){
                const u32 value=Get(ins.c);resolved[ins.a]=memory;++mutations;
                switch(Kind(ins.b)){
                case UMin:memory=std::min(memory,value);break;
                case UMax:memory=std::max(memory,value);break;
                case SMin:memory=std::bit_cast<u32>(std::min(std::bit_cast<int32_t>(memory),std::bit_cast<int32_t>(value)));break;
                case SMax:memory=std::bit_cast<u32>(std::max(std::bit_cast<int32_t>(memory),std::bit_cast<int32_t>(value)));break;
                case FMin:memory=std::bit_cast<u32>(std::fmin(std::bit_cast<float>(memory),std::bit_cast<float>(value)));break;
                case FMax:memory=std::bit_cast<u32>(std::fmax(std::bit_cast<float>(memory),std::bit_cast<float>(value)));break;
                }
            }else if(ins.op==5){assert(previous==ins.c||previous==ins.e);resolved[ins.a]=Get(previous==ins.c?ins.b:ins.d);}
        }
        return {memory,Get(result),mutations};
    }
};
Id EmitBitCastF32U32(EmitContext&,Id value){return value;}
template<bool =false>Id BufferAtomicU32(EmitContext& ctx,IR::Inst*,u32,Id,Id value,
                                       Id(Sirit::Module::*fn)(Id,Id,Id,Id,Id)){
    return ctx.Atomic(fn==&Sirit::Module::OpAtomicFMin?FMin:FMax,value);
}
Id ImageAtomicF32(EmitContext& ctx,IR::Inst* inst,u32 handle,Id address,Id value,
                  Id(Sirit::Module::*fn)(Id,Id,Id,Id,Id)){
    return BufferAtomicU32(ctx,inst,handle,address,value,fn);
}
'''
    for kind in ("Buffer", "Image"):
        for op in ("UMin", "UMax", "SMin", "SMax"):
            cpp += f"Id Emit{kind}Atomic{op}32(EmitContext& ctx,IR::Inst*,u32,Id,Id value){{return ctx.Atomic({op},value);}}\n"
    cpp += helper + "\n" + bodies + r'''
int main(){
    const float inf=std::numeric_limits<float>::infinity();
    const float nan=std::numeric_limits<float>::quiet_NaN();
    const float values[]={-inf,-9.f,-1.f,-0.f,0.f,1.f,9.f,inf,nan};
    using EmitFn=Id(*)(EmitContext&,IR::Inst*,u32,Id,Id);
    const std::array<std::pair<EmitFn,bool>,4> fns{{{EmitBufferAtomicFMin32,true},
        {EmitBufferAtomicFMax32,false},{EmitImageAtomicFMin32,true},{EmitImageAtomicFMax32,false}}};
    unsigned checked=0;
    for(auto [fn,is_min]:fns)for(float initial:values)for(float value:values)for(bool native:{false,true}){
        EmitContext ctx;ctx.profile={native,native};
        const Id input=ctx.ConstU32(std::bit_cast<u32>(value));
        const Id result=fn(ctx,nullptr,0,0,input);
        auto [next,old,count]=ctx.Run(result,std::bit_cast<u32>(initial));
        assert(count==1);assert(old==std::bit_cast<u32>(initial));
        if(!std::isnan(initial)&&!std::isnan(value)){
            const float expected=is_min?std::fmin(initial,value):std::fmax(initial,value);
            assert(std::bit_cast<float>(next)==expected);
        }
        ++checked;
    }
    std::cout<<"DONOR_ATOMIC_EXCLUSIVE_CFG_PREVIOUS_VALUE_PASS cases="<<checked<<"\n";
}
'''
    run_cpp(cpp, "atomics")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    root = args.source / "src/shader_recompiler"
    test_translator(root)
    test_trinary(root)
    test_atomics(root)


if __name__ == "__main__":
    main()
