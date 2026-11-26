"""Exercise the actual helper copied into generated native source."""
from pathlib import Path
import argparse,subprocess,tempfile
ap=argparse.ArgumentParser()
ap.add_argument("--source",type=Path,required=True)
args=ap.parse_args()
root=args.source/"src"
p=root/"core/memory.cpp"
s=p.read_text()
a=s.index("s32 MemoryManager::Free(")
b=s.index("s32 MemoryManager::PoolCommit(",a)
body=s[a:b]
assert body.count("BachataDmem::Intersect(")==2
assert "phys_handle->second.base < request_end" in body
assert "remaining_size -= size_in_dma" not in body
assert "std::min<u64>(phys_mapping.size - phys_offset, size)" not in body
assert s.count("BachataDmem::EntirelyUnmapped(vma_map,virtual_addr,size)")==2
assert s.count("rasterizer->HasMappedOverlap(virtual_addr,size)")==2
r=(root/"video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
assert "boost::icl::intersects(mapped_ranges,range)" in r
source=r'''
#include "core/bachata_dmem_ranges.h"
#include <cassert>
#include <map>
#include <vector>
using namespace BachataDmem;
struct Area { U64 base,size; bool mapped; bool IsMapped() const {return mapped;} };
int main(){
    auto r=Intersect(0x10000,0x30000,0x20000,0x30000);
    assert(r.begin==0x20000&&r.end==0x30000);
    assert(Intersect(0,0x10000,0x10000,0x10000).end==0);
    assert(Intersect(0,~U64{0},~U64{0}-3,8).end==0);
    for(U64 a=0;a<32;++a)for(U64 b=a;b<=32;++b)
    for(U64 c=0;c<32;++c)for(U64 n=0;n<=32;++n){
        auto x=Intersect(a,b,c,n);
        for(U64 pos=0;pos<64;++pos)
            assert((x.begin<=pos&&pos<x.end)==(a<=pos&&pos<b&&c<=pos&&pos<c+n));
    }
    std::map<U64,Area> m{{0,{0,16,false}},{16,{16,16,false}},{32,{32,16,true}},{64,{64,16,false}}};
    assert(EntirelyUnmapped(m,0,32));
    assert(EntirelyUnmapped(m,4,28));
    assert(!EntirelyUnmapped(m,4,29));
    assert(!EntirelyUnmapped(m,32,1));
    assert(!EntirelyUnmapped(m,48,16));
    assert(!EntirelyUnmapped(m,64,17));
    assert(!EntirelyUnmapped(m,0,0));
    assert(!EntirelyUnmapped(m,~U64{0}-1,8));
}
'''
with tempfile.TemporaryDirectory() as tmp:
    src=Path(tmp)/"test.cpp";out=Path(tmp)/"test"
    src.write_text(source)
    subprocess.run(["c++","-std=c++20","-O2","-I",str(root),str(src),"-o",str(out)],check=True)
    subprocess.run([str(out)],check=True)
app=(root/"core/libraries/app_content/app_content.cpp").read_text()
if "BACHATA_ISS_APPCONTENT_BOOT" in app:
    assert "*bootParam=OrbisAppContentBootParam{};" in app
    assert "BACHATA_ISS_APPCONTENT_ABSENT returning NOT_FOUND" in app
print("BACHATA_DMEM_EXACT_RANGE_PASS")
