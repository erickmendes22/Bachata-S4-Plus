"""Avoid a provably irrelevant subset of vertex shader permutations.

0.18.1's Translator::EmitPrologue only reads step_rate_0 if
num_input_vgprs > 0, and step_rate_1 if num_input_vgprs > 1.
StageSpecialization separately compares fetch attribute divisors.
Ignore rates only in the live draw lookup, not in disk-cache equality,
and never bypass compiled descriptor metadata checks.
"""
from pathlib import Path

def apply(root:Path):
    def edit(rel,old,new):
        p=root/rel
        s=p.read_text()
        if s.count(old)!=1: raise RuntimeError("unused VS rates drift "+rel+": "+old[:100])
        p.write_text(s.replace(old,new,1))
    sp="src/shader_recompiler/specialization.h"
    edit(sp,"    bool operator==(const StageSpecialization& other) const {",
r'''    static bool RuntimeMatchesForDraw(const RuntimeInfo& a,const RuntimeInfo& b) {
        if(a==b)return true;
        if(a.sw_stage!=SwStage::Vertex||b.sw_stage!=SwStage::Vertex||
           a.props.num_input_vgprs!=b.props.num_input_vgprs)return false;
        // Only remove values the shader translator does not read.
        // Fetch attributes are compared independently below (divisor).
        auto x=a,y=b;
        if(a.props.num_input_vgprs==0)x.sw.vs.step_rate_0=y.sw.vs.step_rate_0=0;
        if(a.props.num_input_vgprs<=1)x.sw.vs.step_rate_1=y.sw.vs.step_rate_1=0;
        return x==y;
    }

    bool operator==(const StageSpecialization& other) const {
        return Matches(other,false);
    }

    bool Matches(const StageSpecialization& other,bool live_draw) const {''')
    edit(sp,'''        if (runtime_info != other.runtime_info) {
            return false;
        }''',
'''        if (live_draw ? !RuntimeMatchesForDraw(runtime_info,other.runtime_info)
                      : runtime_info != other.runtime_info) {
            return false;
        }''')
    pc="src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    edit(pc,'''            if (effective.sw_stage!=SwStage::TessellationControl &&
                effective.sw_stage!=SwStage::TessellationEval &&
                stored.runtime_info!=runtime_info) continue;''',
'''            if (effective.sw_stage!=SwStage::TessellationControl &&
                effective.sw_stage!=SwStage::TessellationEval &&
                !Shader::StageSpecialization::RuntimeMatchesForDraw(stored.runtime_info,runtime_info)) continue;''')
    edit(pc,"        if (!(candidate.spec==candidate_spec)) continue;",
'''        if (!candidate.spec.Matches(candidate_spec,!BachataCompat::Sotc608())) continue;''')
    return {"specialization":"ignore only unused VS step rates; fetch divisor and descriptor checks unchanged",
            "scope":"live draw only; disk equality and SotC unchanged"}
