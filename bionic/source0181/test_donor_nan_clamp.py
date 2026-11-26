#!/usr/bin/env python3
"""Execute effective F32/F64 min/max/clamp/saturate bodies and title policy.

F operations deliberately use a legal NaN-propagating boundary implementation;
N operations implement the specified one-NaN numeric operand rule. Testing
both routing and values avoids relying on a driver's accidental NaN behavior.
"""
import argparse
from pathlib import Path
import re

from test_donor_alu_semantics import function, run_cpp


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True)
    args=parser.parse_args();root=args.source
    if (root/"src").exists():root=root/"src"
    shader=root/"shader_recompiler"
    source=(shader/"backend/spirv/emit_spirv_floating_point.cpp").read_text()
    policy=re.sub(r"^\s*#(?:include|pragma)[^\n]*\n","",(shader/"donor_nan_clamp.h").read_text(),flags=re.M)
    bodies="\n".join(function(source,f"Id EmitFP{name}{width}(")
                       for name in ("Min","Max","Clamp","Saturate") for width in (32,64))
    cpp=r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string>
using Id=double;using f32=float;using f64=double;
namespace Common {struct ElfInfo {
    std::string serial="CUSA08809";static ElfInfo& Instance(){static ElfInfo x;return x;}
    std::string GameSerial()const{return serial;}
};}
'''+policy+r'''
namespace DonorNanClamp=Shader::DonorNanClamp;
double Round(Id type,double v){return type==32?double(float(v)):v;}
double FMin(double a,double b){return std::isnan(a)||std::isnan(b)?std::numeric_limits<double>::quiet_NaN():std::min(a,b);}
double FMax(double a,double b){return std::isnan(a)||std::isnan(b)?std::numeric_limits<double>::quiet_NaN():std::max(a,b);}
struct EmitContext {
    Id F32[2]{0,32},F64[2]{0,64};unsigned n=0,f=0;
    Id ConstF32(float x){return x;}Id Constant(Id type,double x){return Round(type,x);}
    Id OpNMin(Id type,Id a,Id b){++n;return std::fmin(Round(type,a),Round(type,b));}
    Id OpNMax(Id type,Id a,Id b){++n;return std::fmax(Round(type,a),Round(type,b));}
    Id OpFMin(Id type,Id a,Id b){++f;return FMin(Round(type,a),Round(type,b));}
    Id OpFMax(Id type,Id a,Id b){++f;return FMax(Round(type,a),Round(type,b));}
    Id OpFClamp(Id type,Id v,Id lo,Id hi){++f;return FMin(FMax(Round(type,v),Round(type,lo)),Round(type,hi));}
};
'''+bodies+r'''
bool Same(double actual,double expected){return std::isnan(expected)?std::isnan(actual):actual==expected;}
int main(){
    constexpr bool forced_ieee=false;
    if(forced_ieee)setenv("SHADPS4_IEEE_MINMAX","0",1); // donor checks presence, not numeric value
    else unsetenv("SHADPS4_IEEE_MINMAX");
    const double nan=std::numeric_limits<double>::quiet_NaN(),inf=std::numeric_limits<double>::infinity();
    const double values[]{nan,inf,-inf,0.,-0.,1.,-1.,7.,-7.,0.5,std::numeric_limits<float>::denorm_min(),
                          std::numeric_limits<double>::denorm_min()};
    unsigned binary=0,clamps=0,saturations=0;
    for(const char* serial:{"CUSA08809","CUSA08034","CUSA00785","CUSA12345"}){
        Common::ElfInfo::Instance().serial=serial;
        const bool sotc=std::string(serial)=="CUSA08809"||std::string(serial)=="CUSA08034";
        const bool aware=sotc&&!forced_ieee;
        const bool saturation=aware||std::string(serial)=="CUSA00785";
        for(unsigned width:{32u,64u})for(double raw_a:values){
            const double a=Round(width,raw_a);EmitContext sat;
            const auto result=width==32?EmitFPSaturate32(sat,a):EmitFPSaturate64(sat,a);
            const auto expected=saturation?std::fmin(std::fmax(a,0.),1.):FMin(FMax(a,0.),1.);
            assert(Same(result,expected));assert(sat.n==(saturation?2u:0u)&&sat.f==(saturation?0u:1u));
            if(saturation&&std::isnan(a))assert(result==0);
            ++saturations;
            for(double raw_b:values){const double b=Round(width,raw_b);
                for(bool maximum:{false,true}){EmitContext ctx;
                    const auto actual=maximum?(width==32?EmitFPMax32(ctx,a,b):EmitFPMax64(ctx,a,b)):
                                              (width==32?EmitFPMin32(ctx,a,b):EmitFPMin64(ctx,a,b));
                    const auto expected_value=maximum?(aware?std::fmax(a,b):FMax(a,b)):
                                                       (aware?std::fmin(a,b):FMin(a,b));
                    assert(Same(actual,expected_value));assert(ctx.n==(aware?1u:0u)&&ctx.f==(aware?0u:1u));++binary;
                }
                for(double raw_c:values){const double c=Round(width,raw_c);EmitContext ctx;
                    const auto actual=width==32?EmitFPClamp32(ctx,a,b,c):EmitFPClamp64(ctx,a,b,c);
                    const auto expected_value=aware?std::fmin(std::fmax(a,b),c):FMin(FMax(a,b),c);
                    assert(Same(actual,expected_value));assert(ctx.n==(aware?2u:0u)&&ctx.f==(aware?0u:1u));++clamps;
                }
            }
        }
    }
    // Signed zero participates in every position. A permitted zero sign is not
    // overconstrained: the relevant contract here is numeric selection and NaN.
    std::cout<<"DONOR_NAN_CLAMP_POLICY_PASS ieee="<<forced_ieee<<" binary="<<binary
             <<" clamp="<<clamps<<" saturate="<<saturations<<"\n";
}
'''
    run_cpp(cpp,"donor_nan_clamp")
    run_cpp(cpp.replace("constexpr bool forced_ieee=false;","constexpr bool forced_ieee=true;"),
            "donor_nan_clamp_ieee_override")


if __name__=="__main__":main()
