"""Test the exact production copy/reset and resource-free matching bodies."""
import argparse,pathlib,tempfile,subprocess,re
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
root=pathlib.Path(a.source)/"src"
g=(root/"video_core/renderer_vulkan/vk_graphics_pipeline.h").read_text()
s=(root/"shader_recompiler/specialization.h").read_text()
start=g.index("    GraphicsPipelineKey() {")
end=g.index("    void Serialize(",start)
key=g[start:end]
start=s.index("        if (buffers.empty() && images.empty()")
end=s.index("\n        }",start)+len("\n        }")
match=s[start:end]
cpp=r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <vector>
#include <array>
#include <iostream>
struct GraphicsPipelineKey {
    uint8_t a;
    uint64_t b;
    uint8_t c;
'''+key+r'''
};
struct Info {struct {unsigned mask;} ud_mask;};
struct Spec {
    std::vector<int> buffers,images,fmasks,samplers;
    struct {unsigned user_data;} start;
    const Info* info;
    bool Matches(const Spec& other) const {
'''+match+r'''
    return false;
    }
};
int main(){
    GraphicsPipelineKey a;
    std::memset(static_cast<void*>(&a),0xA5,sizeof(a));a.a=1;a.b=2;a.c=3;
    GraphicsPipelineKey b=a,c;
    c=a;
    assert(a==b&&a==c);
    c=GraphicsPipelineKey{};
    const auto* p=reinterpret_cast<const unsigned char*>(&c);
    for(size_t i=0;i<sizeof(c);++i) assert(p[i]==0);
    Info used{{1}},unused{{0}};
    Spec x{{},{},{},{},{2},&used},y{{},{},{},{},{3},&used};
    assert(!x.Matches(y)&&!y.Matches(x));
    y.start.user_data=2;
    assert(x.Matches(y));
    x.info=y.info=&unused;y.start.user_data=7;
    assert(x.Matches(y));
    x.info=&used;assert(!x.Matches(y));
    std::cout<<"BACHATA_DONOR_PIPELINE_KEY_AND_SGPR_CONTRACT_PASS\n";
}
'''
with tempfile.TemporaryDirectory() as d:
    p=pathlib.Path(d)/"test.cpp";p.write_text(cpp)
    exe=pathlib.Path(d)/"test"
    subprocess.run(["c++","-std=c++23","-O2","-Wall","-Wextra","-Werror",str(p),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
