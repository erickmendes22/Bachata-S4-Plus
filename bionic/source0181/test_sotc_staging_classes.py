#!/usr/bin/env python3
import argparse,pathlib,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
root=pathlib.Path(a.source)/"src"
s=(root/"video_core/renderer_vulkan/vk_staging_buffer_pool.cpp").read_text()
assert "BachataStaging::SizeClass(size,LARGE_MIN_GRANULARITY)" in s
assert "BachataStaging::MaxReuse(alloc_size,deferred)" in s
assert "entry.held || entry_size < size || entry_size > max_size" in s
assert "(!scheduler.IsFree(entry.tick) && !unsynchronized)" in s
assert "entry.held || frame-entry.last_used_frame<LARGE_IDLE_FRAMES" in s
assert "bytes<=keep" in s
code=r'''
#include "video_core/renderer_vulkan/bachata_staging_classes.h"
#include <cassert>
using namespace Vulkan::BachataStaging;
int main(){
    constexpr auto K=1024ULL,M=K*K;
    for(std::uint64_t i=1;i<64*M;i+=1273){
        const auto cl=SizeClass(i,64*K);
        assert(cl>=i && cl>=64*K && (cl&(cl-1))==0);
        assert(MaxReuse(cl,true)==cl && MaxReuse(cl,false)==2*cl);
    }
    assert(KeepBytes(8ULL<<30)==128*M);
    assert(KeepBytes(10ULL<<30)==256*M);
    assert(SizeClass(UINT64_MAX,64*K)==UINT64_MAX);
    assert(MaxReuse(UINT64_MAX,false)==UINT64_MAX);
}
'''
with tempfile.TemporaryDirectory() as d:
    f=pathlib.Path(d)/"test.cpp";exe=pathlib.Path(d)/"test";f.write_text(code)
    subprocess.run(["c++","-std=c++20","-O2","-fsanitize=undefined","-I",str(root),str(f),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print("BACHATA_SOTC_STAGING_CLASSES_PASS")
