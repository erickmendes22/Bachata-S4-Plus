"""Check exact subresource layout selection using the production helper."""
from pathlib import Path
import tempfile,subprocess,argparse
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
src=a.source/'src/video_core';h=src/'renderer_vulkan'
code=r'''
#include "bachata_view_layout.h"
#include <cassert>
#include <vector>
enum L {Undefined,Sampled,Storage,Depth};
struct S {L layout;};
int main(){
    using BachataViewLayout::Uniform;
    std::vector<S> states{{Sampled},{Sampled},{Storage},{Storage}};
    // The global state is the *last transition*, not necessarily this view.
    assert(Uniform(Storage,states,2,2,0,0,1,2)==Sampled);
    assert(Uniform(Sampled,states,2,2,1,0,1,2)==Storage);
    assert(!Uniform(Storage,states,2,2,0,0,2,2));
    assert(!Uniform(Storage,states,2,2,0,0,0,1));
    assert(!Uniform(Storage,states,2,2,1,0,2,1));
    assert(!Uniform(Storage,states,2,2,0,2,1,1));
    states[1].layout=Depth;
    assert(!Uniform(Storage,states,2,2,0,0,1,2));
    assert(Uniform(Storage,states,2,2,0,1,1,1)==Depth);
    states.pop_back();
    assert(!Uniform(Storage,states,2,2,0,0,1,1));
    states.clear();
    assert(Uniform(Sampled,states,2,2,1,1,1,1)==Sampled);
}
'''
with tempfile.TemporaryDirectory() as d:
    d=Path(d);(d/'test.cpp').write_text(code)
    subprocess.run(['c++','-std=c++20','-Wall','-Wextra','-Werror','-I',str(h),str(d/'test.cpp'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test')],check=True)
r=(h/'vk_rasterizer.cpp').read_text()
assert r.count('RefreshImageLayouts(&state,&render_token);')==2
assert r.count('RefreshImageLayouts();')==2
assert 'm.mapping==memory->MappingGeneration()' in r
assert '.desc=&m.recorded_descs[i]' in r
print('SOTC_VIEW_LAYOUT_CONTRACT_OK; graphics/compute integration checked')
