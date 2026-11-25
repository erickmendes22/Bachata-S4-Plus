#!/usr/bin/env python3
"""Compile effective atomic/trinary/LDS emitters with real Sirit and spirv-val.

Usage: --source EFFECTIVE --sirit PINNED_SIRIT --out OUTPUT
SPIRV-Headers defaults to Sirit/externals/SPIRV-Headers/include. --emit-only
allows a local environment without spirv-val to produce binaries; CI must use
the default validation mode. Exercises nested atomic selections and outer Phi.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import subprocess
from test_donor_alu_semantics import function


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--sirit",type=Path,required=True)
    parser.add_argument("--headers",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--spirv-val",default=shutil.which("spirv-val"))
    parser.add_argument("--emit-only",action="store_true")
    args=parser.parse_args()
    if not args.emit_only and not args.spirv_val:
        parser.error("spirv-val required; install spirv-tools for this CI gate")
    args.out.mkdir(parents=True,exist_ok=True)
    args.sirit=args.sirit.resolve()
    headers=(args.headers or args.sirit/"externals/SPIRV-Headers/include").resolve()
    src=args.source/"src/shader_recompiler/backend/spirv"
    atomics=(src/"emit_spirv_atomic.cpp").read_text()
    fp=(src/"emit_spirv_floating_point.cpp").read_text()
    barriers=(src/"emit_spirv_barriers.cpp").read_text()
    bodies="template <typename NegFn, typename NonNegFn>\n"+function(atomics,"Id AtomicF32MinMaxFallback(")
    bodies+="\n"+"\n".join(function(atomics,f"Id Emit{kind}AtomicF{op}32(")
                                for kind in ("Buffer","Image") for op in ("Min","Max"))
    bodies+="\n"+"\n".join(function(fp,f"Id {name}(") for name in
                                ("EmitFPMinTri32","EmitFPMaxTri32","EmitFPMedTri32"))
    bodies+="\n"+function(barriers,"void EmitSubgroupBarrier(")
    cpp=r'''
#include <array>
#include <cstdint>
#include <fstream>
#include <string>
#include <sirit/sirit.h>
using Id=Sirit::Id;using u32=uint32_t;
namespace IR{struct Inst{};}
struct EmitContext:Sirit::Module {
    struct Profile {bool supports_buffer_fp32_atomic_min_max=false;
                    bool supports_image_fp32_atomic_min_max=false;}profile;
    std::array<Id,3> F32{},U32{},U1{};
    Id u32_zero_value{},buffer{},image{},buffer_u32{},image_u32{},last_label{};
    explicit EmitContext(u32 version):Module(version){
        AddCapability(spv::Capability::Shader);
        SetMemoryModel(spv::AddressingModel::Logical,spv::MemoryModel::GLSL450);
        U1[1]=TypeBool();U32[1]=TypeInt(32,false);F32[1]=TypeFloat(32);
        U32[2]=TypeVector(U32[1],2);u32_zero_value=ConstU32(0);
        const Id array=TypeRuntimeArray(U32[1]);Decorate(array,spv::Decoration::ArrayStride,4);
        const Id block=TypeStruct(array);Decorate(block,spv::Decoration::Block);
        MemberDecorate(block,0,spv::Decoration::Offset,0);
        const Id ptr=TypePointer(spv::StorageClass::StorageBuffer,block);
        buffer=AddGlobalVariable(ptr,spv::StorageClass::StorageBuffer);
        Decorate(buffer,spv::Decoration::DescriptorSet,0);Decorate(buffer,spv::Decoration::Binding,0);
        buffer_u32=TypePointer(spv::StorageClass::StorageBuffer,U32[1]);
        const Id it=TypeImage(U32[1],spv::Dim::Dim2D,0,false,false,2,spv::ImageFormat::R32ui);
        image=AddGlobalVariable(TypePointer(spv::StorageClass::UniformConstant,it),spv::StorageClass::UniformConstant);
        Decorate(image,spv::Decoration::DescriptorSet,0);Decorate(image,spv::Decoration::Binding,1);
        image_u32=TypePointer(spv::StorageClass::Image,U32[1]);
    }
    Id ConstU32(u32 n){return Constant(U32[1],n);}
    Id AddLabel(Id id){last_label=Module::AddLabel(id);return last_label;}
    Id AddLabel(){last_label=Module::AddLabel();return last_label;}
    Id BufferPtr(Id offset){return OpAccessChain(buffer_u32,buffer,u32_zero_value,offset);}
    Id ImagePtr(Id coords){return OpImageTexelPointer(image_u32,image,coords,u32_zero_value);}
};
Id EmitBitCastF32U32(EmitContext& ctx,Id value){return ctx.OpBitcast(ctx.F32[1],value);}
template<bool Float=false>Id BufferAtomicU32(EmitContext& ctx,IR::Inst*,u32,Id address,Id value,
                                              Id(Sirit::Module::*fn)(Id,Id,Id,Id,Id)){
    return (ctx.*fn)(Float?ctx.F32[1]:ctx.U32[1],ctx.BufferPtr(address),
                     ctx.ConstU32(u32(spv::Scope::Device)),ctx.ConstU32(0),value);
}
Id ImageAtomicF32(EmitContext& ctx,IR::Inst*,u32,Id coords,Id value,
                  Id(Sirit::Module::*fn)(Id,Id,Id,Id,Id)){
    return (ctx.*fn)(ctx.F32[1],ctx.ImagePtr(coords),ctx.ConstU32(u32(spv::Scope::Device)),ctx.ConstU32(0),value);
}
'''
    for kind in ("Buffer","Image"):
        for op in ("UMin","UMax","SMin","SMax"):
            ptr="ctx.BufferPtr(address)" if kind=="Buffer" else "ctx.ImagePtr(address)"
            cpp+=f"""Id Emit{kind}Atomic{op}32(EmitContext& ctx,IR::Inst*,u32,Id address,Id value){{
    return ctx.OpAtomic{op}(ctx.U32[1],{ptr},ctx.ConstU32(u32(spv::Scope::Device)),ctx.ConstU32(0),value);
}}
"""
    cpp+=bodies+r'''
void Generate(u32 version,const std::string& path){
    EmitContext ctx(version);
    const Id void_type=ctx.TypeVoid();
    const Id main=ctx.OpFunction(void_type,spv::FunctionControlMask::MaskNone,ctx.TypeFunction(void_type));
    ctx.AddLabel();
    const Id value=ctx.OpBitcast(ctx.F32[1],ctx.OpLoad(ctx.U32[1],ctx.BufferPtr(ctx.ConstU32(4))));
    const Id coords=ctx.OpCompositeConstruct(ctx.U32[2],ctx.ConstU32(0),ctx.ConstU32(0));
    const Id left=ctx.OpLabel(),right=ctx.OpLabel(),merge=ctx.OpLabel();
    const Id cond=ctx.OpFOrdLessThan(ctx.U1[1],value,ctx.Constant(ctx.F32[1],0.0f));
    ctx.OpSelectionMerge(merge,spv::SelectionControlMask::MaskNone);
    ctx.OpBranchConditional(cond,left,right);
    ctx.AddLabel(left);
    const Id a=EmitBufferAtomicFMin32(ctx,nullptr,0,ctx.ConstU32(0),value);
    const Id left_last=ctx.last_label;
    ctx.OpBranch(merge);
    ctx.AddLabel(right);
    const Id b=EmitImageAtomicFMax32(ctx,nullptr,0,coords,value);
    const Id right_last=ctx.last_label;
    ctx.OpBranch(merge);
    ctx.AddLabel(merge);
    const Id previous=ctx.OpPhi(ctx.F32[1],a,left_last,b,right_last);
    const Id c=EmitBufferAtomicFMax32(ctx,nullptr,0,ctx.ConstU32(1),previous);
    const Id d=EmitImageAtomicFMin32(ctx,nullptr,0,coords,c);
    const Id mn=EmitFPMinTri32(ctx,previous,c,d);
    const Id mx=EmitFPMaxTri32(ctx,previous,c,d);
    const Id median=EmitFPMedTri32(ctx,mn,mx,value);
    EmitSubgroupBarrier(ctx);
    ctx.OpStore(ctx.BufferPtr(ctx.ConstU32(2)),ctx.OpBitcast(ctx.U32[1],median));
    ctx.OpReturn();ctx.OpFunctionEnd();
    if(version>=0x00010400u)ctx.AddEntryPoint(spv::ExecutionModel::GLCompute,main,"main",ctx.buffer,ctx.image);
    else ctx.AddEntryPoint(spv::ExecutionModel::GLCompute,main,"main");
    ctx.AddExecutionMode(main,spv::ExecutionMode::LocalSize,64u,1u,1u);
    const auto words=ctx.Assemble();
    std::ofstream out(path,std::ios::binary);out.write(reinterpret_cast<const char*>(words.data()),words.size()*4);
}
int main(int argc,char** argv){
    if(argc!=2)return 2;
    Generate(0x00010300u,std::string(argv[1])+"/donor-alu-lds-v13.spv");
    Generate(0x00010400u,std::string(argv[1])+"/donor-alu-lds-v14.spv");
}
'''
    generated=args.out/"donor_spirv.cpp"
    generated.write_text(cpp)
    objects=args.out/"sirit-objects"
    objects.mkdir(exist_ok=True)
    includes=["-I"+str(args.sirit/"include"),"-I"+str(args.sirit/"src"),"-I"+str(headers)]
    sources=sorted((args.sirit/"src").rglob("*.cpp"))
    if len(sources)<10:raise RuntimeError("Incomplete pinned Sirit source")
    def compile_file(source):
        obj=objects/(str(source.relative_to(args.sirit/"src")).replace("/","_")+".o")
        result=subprocess.run(["c++","-std=c++20","-O0",*includes,"-c",str(source),"-o",str(obj)],
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if result.returncode:
            print(result.stderr)
            result.check_returncode()
        return obj
    with ThreadPoolExecutor(max_workers=4) as executor:
        compiled=list(executor.map(compile_file,sources))
    exe=args.out/"donor_spirv"
    subprocess.run(["c++","-std=c++20","-O0",*includes,str(generated),
                    *map(str,compiled),"-o",str(exe)],check=True)
    subprocess.run([str(exe),str(args.out)],check=True)
    if args.emit_only:
        print("DONOR_REAL_SIRIT_SPIRV_EMITTED_NOT_VALIDATED",args.out)
        return
    for suffix,target in (("v13","vulkan1.1"),("v14","vulkan1.2")):
        subprocess.run([args.spirv_val,"--target-env",target,str(args.out/f"donor-alu-lds-{suffix}.spv")],check=True)
    print("DONOR_REAL_SIRIT_NESTED_ATOMIC_TRINARY_LDS_SPIRV_VALIDATED")


if __name__=="__main__":
    main()
