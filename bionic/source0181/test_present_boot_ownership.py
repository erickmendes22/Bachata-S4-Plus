"""Regression test extracted from production presentation ownership code."""
import argparse,pathlib,tempfile,subprocess
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
v=pathlib.Path(a.source)/"src/video_core/renderer_vulkan"
h=(v/"vk_presenter.h").read_text();s=(v/"vk_presenter.cpp").read_text()
assert "Frame* last_submit_frame{};" in h
assert "swapchain.GetImageCount()+1" in s
assert "free_frame(false)" in s and "free_frame(true)" in s
assert "if (last_submit_frame == nullptr)" in s
start=s.index("    const auto free_frame = [&](bool submitted)")
end=s.index("\n    };",start)+len("\n    };")
body=s[start:end]
cpp=r'''
#include <queue>
#include <mutex>
#include <condition_variable>
#include <cassert>
#include <iostream>
struct Frame {int id;};
struct Pool {
    std::queue<Frame*> free_queue;
    Frame* last_submit_frame{};
    std::mutex free_mutex;
    std::condition_variable free_cv;
    void Finish(Frame* frame,bool is_reusing_frame,bool submitted) {
'''+body+r'''
        free_frame(submitted);
    }
};
int main(){
    Pool p; Frame a{1},b{2},c{3};
    assert(!p.last_submit_frame);
    p.Finish(&a,false,true);
    assert(p.last_submit_frame==&a && p.free_queue.empty());
    p.Finish(&a,true,true);
    assert(p.free_queue.empty());
    p.Finish(&b,false,false);
    assert(p.last_submit_frame==&a && p.free_queue.front()==&b);
    p.free_queue.pop();
    p.Finish(&c,false,true);
    assert(p.last_submit_frame==&c && p.free_queue.front()==&a);
    p.free_queue.pop();
    for(int i=0;i<10000;++i){
        Frame* next=p.last_submit_frame==&a?&c:&a;
        Frame* old=p.last_submit_frame;
        p.Finish(next,false,true);
        assert(p.free_queue.size()==1 && p.free_queue.front()==old && p.last_submit_frame==next);
        p.free_queue.pop();
    }
    std::cout<<"BACHATA_FIRST_FLIP_AND_FRAME_OWNERSHIP_PASS cycles=10000\n";
}
'''
with tempfile.TemporaryDirectory() as d:
    f=pathlib.Path(d)/"test.cpp";f.write_text(cpp);exe=pathlib.Path(d)/"test"
    subprocess.run(["c++","-std=c++23","-O2","-pthread",str(f),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
