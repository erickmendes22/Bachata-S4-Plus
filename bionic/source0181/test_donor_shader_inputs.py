#!/usr/bin/env python3
"""Execute effective WQM, vertex prologue, fetch parsing/emission/cache contracts.

The changed source is compiled as C++23. IR and archive boundary models provide
values/storage; dispatches, arithmetic, parser and serializer are production
bodies, exercised against GCN expectations including the donors' title policies.
"""
import argparse
from pathlib import Path
import re

from test_donor_alu_semantics import function, run_cpp


COMMON = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <span>
#include <string>
#include <utility>
#include <vector>
using u8=uint8_t;using s8=int8_t;using u16=uint16_t;using u32=uint32_t;using u64=uint64_t;
#define ASSERT(x) assert(x)
#define ASSERT_MSG(x,...) assert(x)
#define UNREACHABLE() assert(false)
#define UNREACHABLE_MSG(...) assert(false)
#define LOG_WARNING(...) ((void)0)
namespace Common {
struct ElfInfo {std::string serial="CUSA08809";static ElfInfo& Instance(){static ElfInfo e;return e;}
std::string GameSerial()const{return serial;}};
}
'''


def policy(root):
    contents=(root/"frontend/donor_shader_input_policy.h").read_text()
    return re.sub(r"^\s*#(?:include|pragma)[^\n]*\n","",contents,flags=re.M)


def test_wqm(root):
    source=(root/"frontend/translate/scalar_alu.cpp").read_text()
    begin=source.index("        case Opcode::S_WQM_B64:")
    end=source.index("        case Opcode::S_BREV_B32:",begin)
    dispatch=source[begin:end]
    cpp=COMMON+policy(root)+r'''
namespace Shader {
namespace IR {using U1=std::array<bool,64>;using U32=std::array<u32,64>;using U64=u64;}
struct Emitter {
    IR::U1 scc{};
    IR::U1 InverseBallot(u64 mask){IR::U1 out{};for(u32 i=0;i<64;++i)out[i]=(mask>>i)&1;return out;}
    IR::U32 Imm32(u32 n){IR::U32 out{};out.fill(n);return out;}
    IR::U32 Select(const IR::U1& c,const IR::U32& a,const IR::U32& b){IR::U32 out{};for(u32 i=0;i<64;++i)out[i]=c[i]?a[i]:b[i];return out;}
    IR::U32 QuadBroadcast(const IR::U32& a,const IR::U32& index){IR::U32 out{};for(u32 i=0;i<64;++i)out[i]=a[(i&~3u)+index[i]];return out;}
    IR::U32 BitwiseOr(const IR::U32& a,const IR::U32& b){IR::U32 out{};for(u32 i=0;i<64;++i)out[i]=a[i]|b[i];return out;}
    IR::U1 INotEqual(const IR::U32& a,const IR::U32& b){IR::U1 out{};for(u32 i=0;i<64;++i)out[i]=a[i]!=b[i];return out;}
    u64 Ballot(const IR::U1& c){u64 out{};for(u32 i=0;i<64;++i)if(c[i])out|=u64{1}<<i;return out;}
    void SetScc(const IR::U1& c){scc=c;}
};
enum class Opcode {S_WQM_B64};
enum class OperandField {ExecLo,VccLo,Scalar};
struct Operand {OperandField field;u64 value;};
struct GcnInst {Opcode opcode=Opcode::S_WQM_B64;std::array<Operand,1> src{},dst{};};
struct Translator {
    Emitter ir;u64 out=0x9876543210abcdefULL;bool written=false;
    u64 GetSrc64(Operand op){return op.value;}
    void SetDst64(Operand,u64 value){out=value;written=true;}
    void Emit(const GcnInst& inst){switch(inst.opcode){
'''+dispatch+r'''
    }}
};
}
int main(){
    unsetenv("SOTC_WQM_COPY");
    unsigned checked=0;
    for(const auto* serial:{"CUSA08809","CUSA08034","CUSA00785","CUSA12345"}) {
        Common::ElfInfo::Instance().serial=serial;
        const bool sotc=std::string(serial)=="CUSA08809"||std::string(serial)=="CUSA08034";
        // Every possible quad mask, at every one of the 16 quad positions.
        // Separate full-wave fixtures exercise simultaneous disjoint quads.
        std::vector<u64> inputs{0,~u64{0},0x1111111111111111ULL,0x8080808080808080ULL,
                                0x0123456789abcdefULL,0xf00000000000000fULL};
        for(u32 q=0;q<16;++q)for(u64 pattern=0;pattern<16;++pattern)inputs.push_back(pattern<<(q*4));
        for(u64 mask:inputs)for(auto dst:{Shader::OperandField::ExecLo,Shader::OperandField::VccLo,Shader::OperandField::Scalar})
          for(auto src:{Shader::OperandField::ExecLo,Shader::OperandField::VccLo}) {
            Shader::Translator t;
            Shader::GcnInst inst;inst.src[0]={src,mask};inst.dst[0]={dst,0};t.Emit(inst);
            const bool noop=!sotc||(src==Shader::OperandField::ExecLo&&dst==Shader::OperandField::ExecLo);
            if(noop){assert(!t.written);assert(t.out==0x9876543210abcdefULL);}
            else {
                u64 expected{};for(u32 q=0;q<16;++q)if((mask>>(q*4))&15)expected|=u64{15}<<(q*4);
                assert(t.written&&t.out==expected);
                for(u32 i=0;i<64;++i)assert(t.ir.scc[i]==bool((expected>>i)&1));
            }
            ++checked;
        }
    }
    std::cout<<"DONOR_WQM_QUAD_MASK_PASS cases="<<checked<<"\n";
}
'''
    run_cpp(cpp,"wqm")
    # Separate executable initialization verifies the donor's opt-out because
    # the production preference is intentionally cached once per process.
    disabled=cpp[0:cpp.index("int main(){")]+r'''
int main(){setenv("SOTC_WQM_COPY","0",1);Shader::Translator t;Shader::GcnInst i;
i.src[0]={Shader::OperandField::ExecLo,1};i.dst[0]={Shader::OperandField::VccLo,0};t.Emit(i);
assert(!t.written);std::cout<<"DONOR_WQM_DISABLED_PASS\n";}
'''
    run_cpp(disabled,"wqm_disabled")


def test_instances(root):
    source=(root/"frontend/translate/translate.cpp").read_text()
    begin=source.index("    case SwStage::Vertex: {")
    end=source.index("    case SwStage::Fragment:",begin)
    body=source[begin:end]
    cpp=COMMON+policy(root)+r'''
namespace Shader {
enum class HwStage {Vertex,Local};enum class SwStage {Vertex};
namespace IR {using U32=u32;using ScalarReg=u32;enum VectorReg:u32 {V0};
VectorReg operator++(VectorReg& x,int){const auto old=x;x=VectorReg(u32(x)+1);return old;}
VectorReg& operator++(VectorReg& x){x=VectorReg(u32(x)+1);return x;}
enum class Attribute {BaseVertex,BaseInstance,VertexId,InstanceId};}
struct RuntimeInfo {
    struct {u32 num_input_vgprs=3;} props;
    struct {struct {u16 vertex_sgpr_offset{},instance_sgpr_offset{};u32 step_rate_0=1,step_rate_1=1;}vs;}sw;
};
struct FetchData {bool empty=true;s8 vertex_offset_sgpr=-1,instance_offset_sgpr=-1;bool Empty()const{return empty;}};
struct Emitter {
    std::array<u32,16> scalars{},vectors{};std::array<bool,16> scalar_written{},vector_written{};
    u32 first{},invocation=0,base_vertex=41;
    u32 GetAttributeU32(IR::Attribute attr){switch(attr){
      case IR::Attribute::BaseVertex:return base_vertex;case IR::Attribute::BaseInstance:return first;
      case IR::Attribute::VertexId:return base_vertex+7;case IR::Attribute::InstanceId:return first+invocation;
    }std::abort();}
    u32 ISub(u32 a,u32 b){return a-b;}u32 IDiv(u32 a,u32 b){assert(b);return a/b;}u32 Imm32(u32 n){return n;}
    void SetScalarReg(u32 i,u32 n){scalars[i]=n;scalar_written[i]=true;}
    void SetVectorReg(IR::VectorReg i,u32 n){vectors[u32(i)]=n;vector_written[u32(i)]=true;}
};
// The packet-to-SGPR decoder is unchanged; reserve 0 for no indirect SGPR.
s8 UdRegFromShOffset(u16 offset,HwStage){return offset?s8(offset-1):-1;}
struct Translator {
    Emitter ir;RuntimeInfo runtime_info;FetchData fetch_data;struct{HwStage hw_stage=HwStage::Vertex;}info;
    void Prologue(){IR::VectorReg dst_vreg=IR::VectorReg::V0;switch(SwStage::Vertex){
'''+body+r'''
    }}
};
}
int main(){
    unsetenv("SHADPS4_ABSOLUTE_INSTANCE_ID");
    unsigned checked=0;
    for(const auto* serial:{"CUSA08809","CUSA08034","CUSA00785","CUSA12345"})
      for(u32 first:{0u,18u,3409u})for(u32 invocation:{0u,1u,33u})
      for(u32 step0:{0u,1u,2u,17u})for(u32 step1:{0u,1u,3u})
      for(u32 nvgprs=0;nvgprs<=3;++nvgprs)for(bool local:{false,true})
      for(bool indirect:{false,true})for(bool fetch:{false,true})for(bool offset:{false,true}){
        Common::ElfInfo::Instance().serial=serial;
        const bool sotc=std::string(serial)=="CUSA08809"||std::string(serial)=="CUSA08034";
        const bool order=std::string(serial)=="CUSA00785";
        Shader::Translator t;t.ir.first=first;t.ir.invocation=invocation;
        t.runtime_info.props.num_input_vgprs=nvgprs;
        t.runtime_info.sw.vs.step_rate_0=step0;t.runtime_info.sw.vs.step_rate_1=step1;
        t.runtime_info.sw.vs.instance_sgpr_offset=indirect?6:0;
        t.runtime_info.sw.vs.vertex_sgpr_offset=indirect?5:0;
        t.info.hw_stage=local?Shader::HwStage::Local:Shader::HwStage::Vertex;
        t.fetch_data.empty=!fetch;
        t.fetch_data.instance_offset_sgpr=offset?5:-1;
        t.fetch_data.vertex_offset_sgpr=offset?4:-1;
        t.Prologue();
        const u32 absolute=first+invocation;
        // Match GCN-relative instance counters and each pinned donor's
        // indirect fetch path. Unrelated games retain the old prologue.
        u32 step_id=absolute;
        if(order&&!indirect)step_id=invocation;
        if(sotc&&!(indirect&&!fetch&&offset))step_id=invocation;
        u32 plain=absolute;
        if(indirect){
            const bool add_in_fetch=order?(fetch&&offset):(!fetch&&offset);
            if(!add_in_fetch)plain=invocation;
        }else if(order||sotc)plain=invocation;
        const bool vertex_add_in_fetch=order?(fetch&&offset):(!fetch&&offset);
        assert(t.ir.vectors[0]==(indirect&&!vertex_add_in_fetch?7u:48u));
        if(nvgprs>0){assert(t.ir.vector_written[1]);assert(t.ir.vectors[1]==(local||!step0?0:step_id/step0));}
        else assert(!t.ir.vector_written[1]);
        if(nvgprs>1&&!local){assert(t.ir.vector_written[2]);assert(t.ir.vectors[2]==(!step1?0:step_id/step1));}
        else assert(!t.ir.vector_written[2]);
        if(nvgprs>2){assert(t.ir.vector_written[3]);assert(t.ir.vectors[3]==plain);}
        else assert(!t.ir.vector_written[3]);
        assert(t.ir.scalar_written[5]==indirect);
        if(indirect)assert(t.ir.scalars[5]==first);
        ++checked;
    }
    std::cout<<"DONOR_INSTANCE_ID_STEP_RATE_PASS cases="<<checked<<"\n";
}
'''
    run_cpp(cpp,"instances")
    disabled=cpp[0:cpp.index("int main(){")]+r'''
int main(){setenv("SHADPS4_ABSOLUTE_INSTANCE_ID","0",1);Shader::Translator t;
t.ir.first=3409;t.ir.invocation=2;t.Prologue();
assert(t.ir.vectors[1]==3411&&t.ir.vectors[2]==3411&&t.ir.vectors[3]==3411);
std::cout<<"DONOR_ABSOLUTE_INSTANCE_SWITCH_PASS\n";}
'''
    run_cpp(disabled,"absolute_instances")


def enum(source,name):
    begin=source.index("enum class "+name+" :")
    end=source.index("\n};",begin)+3
    return source[begin:end]


def test_fetch(root):
    source=(root/"frontend/fetch_shader.cpp").read_text()
    header=(root/"frontend/fetch_shader.h").read_text()
    definitions=header[header.index("struct VertexAttribute {"):header.index("const u32* GetFetchShaderCode(")]
    opcodes=(root/"frontend/opcodes.h").read_text()
    enums="\n".join(enum(opcodes,name) for name in
        ("InstEncoding","EncodingMask","OpcodeSOP1","OpcodeSOPP","OpcodeSMRD","OpcodeVOP2",
         "OpcodeVOP1","OpcodeMUBUF","OpcodeMTBUF"))
    decode=function((root/"frontend/decode.cpp").read_text(),"InstEncoding GetInstructionEncoding(")
    parser=function(source,"bool ParseFetchShader(")
    getcode=function(source,"const u32* GetFetchShaderCode(")
    serialization=(root.parent/"video_core/renderer_vulkan/vk_pipeline_serialization.cpp").read_text()
    serialize=function(serialization,"void Gcn::FetchShaderData::Serialize(")
    deserialize=function(serialization,"bool Gcn::FetchShaderData::Deserialize(")
    translator=function((root/"frontend/translate/translate.cpp").read_text(),"void Translator::EmitFetch(")
    tail=translator[translator.index("    for (u32 semantic"):]
    cpp=COMMON+policy(root)+r'''
template<class T,size_t>using SmallVector=std::vector<T>;
namespace AmdGpu {
struct Buffer {u64 base_address{};u32 data_format{},num_format{};
constexpr u32 GetNumberConversion()const{return 0;}constexpr u32 DstSelect()const{return 0;}};
}
namespace Serialization {
struct Archive {std::vector<u8> bytes;size_t offset{};void Grow(size_t n){bytes.reserve(bytes.size()+n);}};
struct Writer {
    Archive& ar;template<class T>void Write(const T& v){const auto* p=reinterpret_cast<const u8*>(&v);ar.bytes.insert(ar.bytes.end(),p,p+sizeof(T));}
    template<class T>void Write(const std::vector<T>& v){Write(u32(v.size()));for(const auto& item:v)Write(item);}
};
struct Reader {
    Archive& ar;template<class T>void Read(T& v){assert(ar.offset+sizeof(T)<=ar.bytes.size());std::memcpy(&v,ar.bytes.data()+ar.offset,sizeof(T));ar.offset+=sizeof(T);}
    template<class T>void Read(std::vector<T>& v){u32 count{};Read(count);v.resize(count);for(auto& item:v)Read(item);}
};
}
namespace Shader {
struct Info {bool has_fetch_shader=true;u32 fetch_shader_sgpr_base{};std::span<const u32> user_data;
template<class T>constexpr T ReadUdReg(u32,u32)const{return T{};}};
namespace Gcn {
'''+enums+"\n"+definitions+"\n"+decode+"\n"+getcode+"\n"+parser+r'''
}
'''+serialize+"\n"+deserialize+r'''
namespace IR {
using VectorReg=u32;using F32=float;
enum Attribute:u32{Param0};Attribute operator+(Attribute x,u32 n){return Attribute(u32(x)+n);}
template<class E>auto ApplyReadNumberConversionVec4(E&,const std::array<float,4>& v,u32){return v;}
}
struct Emitter {
    std::array<float,256> regs;Emitter(){regs.fill(-1234);}
    float GetAttribute(IR::Attribute a,u32 i){return 10.f+u32(a)*4+i;}
    std::array<float,4> CompositeConstruct(float a,float b,float c,float d){return {a,b,c,d};}
    float CompositeExtract(const std::array<float,4>& v,u32 i){return v[i];}
    float Imm32(float x){return x;}void SetVectorReg(u32 i,float x){regs[i]=x;}
};
auto ApplySwizzle(Emitter&,const std::array<float,4>& v,u32){return v;}
struct Translator {
    Emitter ir;Info info;Gcn::FetchShaderData fetch_data;
    void EmitFetch(){
'''+tail+r'''
};
}
using namespace Shader::Gcn;
std::vector<u32> FetchCode(bool constants,u32 components){
    std::vector<u32> code;
    code.push_back(u32(InstEncoding::SMRD)|(u32(OpcodeSMRD::S_LOAD_DWORDX4)<<22)|(8u<<15)|(1u<<9)|4u);
    code.push_back(u32(InstEncoding::MUBUF)|((u32(OpcodeMUBUF::BUFFER_LOAD_FORMAT_X)+components-1)<<18));
    code.push_back((2u<<16)|(20u<<8));
    if(constants){
        code.push_back(u32(InstEncoding::VOP1)|(u32(OpcodeVOP1::V_MOV_B32)<<9)|(23u<<17)|242u);
        code.push_back(u32(InstEncoding::VOP1)|(u32(OpcodeVOP1::V_MOV_B32)<<9)|(91u<<17)|242u);
    }
    code.push_back(u32(InstEncoding::SOP1)|(u32(OpcodeSOP1::S_SETPC_B64)<<8));
    return code;
}
int main(){
    unsigned checked=0;
    for(const auto* serial:{"CUSA08809","CUSA08034","CUSA00785","CUSA12345"})for(u32 components=1;components<=3;++components){
        Common::ElfInfo::Instance().serial=serial;
        const bool sotc=std::string(serial)=="CUSA08809"||std::string(serial)=="CUSA08034";
        auto code=FetchCode(true,components);const u32* ptr=code.data();
        std::array<u32,16> ud{};std::memcpy(ud.data(),&ptr,sizeof(ptr));
        Shader::Info info;info.user_data=ud;
        FetchShaderData parsed;assert(ParseFetchShader(info,parsed));
        assert(parsed.attributes.size()==1&&parsed.size==code.size()*4);
        assert(parsed.attributes[0].dest_vgpr==20&&parsed.attributes[0].num_elements==components);
        assert(parsed.attributes[0].sgpr_base==2&&parsed.attributes[0].dword_offset==4);
        const std::vector<u8> expected=sotc?std::vector<u8>{23,91}:std::vector<u8>{};
        assert(parsed.one_vgprs==expected);
        Shader::Translator t;t.fetch_data=parsed;t.EmitFetch();
        for(u32 i=0;i<components;++i)assert(t.ir.regs[20+i]==10.f+i);
        for(u32 i=components;i<3;++i)assert(t.ir.regs[20+i]==-1234);
        assert(t.ir.regs[23]==(sotc?1.f:-1234));assert(t.ir.regs[91]==(sotc?1.f:-1234));
        Serialization::Archive archive;parsed.Serialize(archive);
        FetchShaderData warm;warm.one_vgprs={99,100,101};assert(warm.Deserialize(archive));
        assert(warm==parsed&&archive.offset==archive.bytes.size());
        t.fetch_data=warm;t.ir=Shader::Emitter{};t.EmitFetch();
        assert(t.ir.regs[23]==(sotc?1.f:-1234));
        auto differing=warm;differing.one_vgprs.push_back(88);assert(!(differing==warm));
        // A reused parse result must discard the previous shader's constants.
        auto no_const=FetchCode(false,components);ptr=no_const.data();std::memcpy(ud.data(),&ptr,sizeof(ptr));
        assert(ParseFetchShader(info,parsed));assert(parsed.one_vgprs.empty());
        ++checked;
    }
    std::cout<<"DONOR_FETCH_PARSE_EMIT_CACHE_PASS cases="<<checked<<"\n";
}
'''
    run_cpp(cpp,"fetch")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    args=parser.parse_args()
    root=args.source/"src/shader_recompiler"
    test_wqm(root)
    test_instances(root)
    test_fetch(root)


if __name__=="__main__":
    main()
