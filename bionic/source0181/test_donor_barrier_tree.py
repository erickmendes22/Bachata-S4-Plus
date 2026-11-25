"""Run actual integrated donor barrier tree against a bitset oracle."""
import argparse,pathlib,tempfile,subprocess
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
src=(pathlib.Path(a.source)/"src").resolve()
with tempfile.TemporaryDirectory() as d:
    root=pathlib.Path(d)
    (root/"common").mkdir()
    (root/"common/types.h").write_text("#pragma once\n#include <cstdint>\nusing u32=uint32_t;using u64=uint64_t;\n")
    cpp=root/"test.cpp"
    cpp.write_text(r'''
#include <algorithm>
#include <random>
#include <cassert>
#include <array>
#include <iostream>
#include "video_core/renderer_vulkan/vk_barrier_tracker.h"
int main(){
    std::mt19937_64 rng(0x27b10);
    using namespace Vulkan;
    BarrierTracker tree;
    for(int epoch=0;epoch<30;++epoch){
        std::array<std::array<std::array<bool,512>,2>,256> exact{};
        tree.Clear();
        assert(tree.Empty());
        for(int i=0;i<50000;++i){
            unsigned r=rng()%256,k=rng()%2,s=rng()%512,e=std::min(511u,s+unsigned(rng()%64));
            auto a=k?Access::Read:Access::Write;
            AddressRange range{r,s,e};
            bool expected=false;
            for(unsigned j=s;j<=e;++j)expected|=exact[r][k][j];
            assert(tree.FindRange(range,a)==expected);
            if(rng()%3!=0){
                tree.InsertRange(range,a);
                for(unsigned j=s;j<=e;++j)exact[r][k][j]=true;
            }
        }
    }
    std::cout<<"BACHATA_DONOR_BARRIER_TREE_PASS comparisons=1500000\n";
}''')
    exe=root/"test"
    subprocess.run(["c++","-std=c++23","-O2","-I",str(root),"-I",str(src),
                    str(cpp),str(src/"video_core/renderer_vulkan/vk_barrier_tracker.cpp"),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
