"""Test the exact production copy/reset and resource-free matching bodies."""
import argparse,pathlib,tempfile,subprocess,re
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
root=pathlib.Path(a.source)/"src"
g=(root/"video_core/renderer_vulkan/vk_graphics_pipeline.h").read_text()
s=(root/"shader_recompiler/specialization.h").read_text()
start=g.index("    GraphicsPipelineKey() {")
end=g.index("    void Serialize(",start)
key=g[start:end]
# Check the actual 0.18.1 API and emitter rather than inventing donor fields.
info=(root/"shader_recompiler/info.h").read_text()
bindings=(root/"shader_recompiler/backend/bindings.h").read_text()
emit=(root/"shader_recompiler/backend/spirv/emit_spirv_context_get_set.cpp").read_text()
assert "bool has_flatbuf" in info and "u32 unified" in bindings and "u32 buffer" in bindings
assert "ctx.EmitFlatbufferLoad(ctx.ConstU32(static_cast<u32>(reg)))" in emit
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
struct Info {bool has_flatbuf;};
struct Spec {
    std::vector<int> buffers,images,fmasks,samplers;
    struct Bindings {unsigned unified,buffer; bool operator==(const Bindings&) const=default;} start;
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
    Info used{true},unused{false};
    Spec x{{},{},{},{},{2,1},&used},y{{},{},{},{},{3,1},&used};
    assert(!x.Matches(y)&&!y.Matches(x));
    y.start.unified=2;
    assert(x.Matches(y));
    x.info=y.info=&unused;y.start.unified=7;
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
