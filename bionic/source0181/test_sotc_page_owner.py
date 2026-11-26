"""Execute the actual copied page-owner helper and check FEX integration."""
import argparse,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
root=p.parse_args().source/"src"
s=(root/"core/memory.cpp").read_text()
m=(root/"core/libraries/kernel/memory.cpp").read_text()
b=(root/"core/guest_cpu/fex_hle_bridge.cpp").read_text()
assert "sotc_page_owners.Note(phys_addr,mapped_addr,size,total_direct_size)" in s
assert "sotc_page_owners.Run(physical,addr,bytes,live)" in s
assert "if(run.stale)" in s and "info->is_committed=0" in s
assert "rip-main->GetBaseAddress()==release_rva" in m and "opcode==0xe8" in m
assert "ReadActiveGuestHleMemory(ActiveHleCallFrame->rsp" in b
cpp=r'''
#include "core/bachata_sotc_page_owner.h"
#include <cassert>
using namespace BachataSotcOwner;
int main(){
    Owners o;
    constexpr U64 A=0x20000000,B=0x30000000;
    o.Note(0,A,4*Page,8*Page);
    o.Note(Page,B,2*Page,8*Page);
    const auto live=[&](U64 a,U64 p){return a==B+p-Page && p>=Page && p<3*Page;};
    auto r=o.Run(0,A,4*Page,live);
    assert(!r.stale && r.end==A+Page);
    r=o.Run(Page,A+Page,3*Page,live);
    assert(r.stale && r.end==A+3*Page);
    r=o.Run(3*Page,A+3*Page,Page,live);
    assert(!r.stale && r.end==A+4*Page);
    r=o.Run(Page,B,2*Page,live);
    assert(!r.stale && r.end==B+2*Page);
    r=o.Run(Page,A+Page,2*Page,[](U64,U64){return false;});
    assert(!r.stale && r.end==A+3*Page);
    o.Note(Page+4096,B+4096,4096,8*Page);
    assert(o.Last(Page)==0);
    r=o.Run(Page,A+Page,2*Page,live);
    assert(!r.stale && r.end==A+2*Page);
    assert(o.Run(Page+1,A+Page,Page,live).end==0);
    assert(o.Run(Page,A+Page,Page-1,live).end==0);
}
'''
with tempfile.TemporaryDirectory() as d:
    source=Path(d)/"owner.cpp";exe=Path(d)/"owner"
    source.write_text(cpp)
    subprocess.run(["c++","-std=c++20","-Wall","-Wextra","-Werror","-I",str(root),str(source),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print("BACHATA_SOTC_PAGE_OWNER_PASS")
