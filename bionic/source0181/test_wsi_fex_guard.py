"""Test actual integrated call-ret guard predicate and presentation contracts."""
import argparse,pathlib,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
s=(pathlib.Path(a.source)/"src").resolve()
v=s/"video_core/renderer_vulkan"
swap=(v/"vk_swapchain.cpp").read_text()
present=(v/"vk_presenter.cpp").read_text()
driver=(s/"core/libraries/videoout/driver.cpp").read_text()
assert "BACHATA_WSI_SUBOPTIMAL_ACQUIRE accepted" in swap
assert "BACHATA_WSI_SUBOPTIMAL_PRESENT accepted" in swap
assert "acquire_retire_ticks.assign(image_count,0)" in swap
assert "scheduler.CurrentTick()" in present and "swapchain.SetAcquireRetire" in present
assert present.count("Platform::Bachata::ReportPresentedFrame()")==0
assert driver.count("Platform::Bachata::ReportPresentedFrame()")==1
assert driver.index("presenter->Present(req.frame);")<driver.index("Platform::Bachata::ReportPresentedFrame();")<driver.index("// Update flip status.")
cpp=r'''
#include <cassert>
#include <iostream>
#include "core/fex/fex_callret_guard.h"
int main(){
 using BachataFex::IsCallRetGuardAccess;
 constexpr uint64_t b=0x10000000,n=0x400000,p=4096;
 constexpr uint32_t stp=0xa9bf0720,ldp=0xa8c10720;
 assert(IsCallRetGuardAccess(b,n,p,b-16,b,stp));
 assert(IsCallRetGuardAccess(b,n,p,b-8,b,stp));
 assert(IsCallRetGuardAccess(b,n,p,b+n,b+n,ldp));
 assert(!IsCallRetGuardAccess(b,n,p,b+16,b+32,stp));
 assert(!IsCallRetGuardAccess(b,n,p,b-16,b,0xf9000320));
 assert(!IsCallRetGuardAccess(b,n,p,b-16,b,stp^0x20));
 assert(!IsCallRetGuardAccess(b,n,p,b-16,b+16,stp));
 assert(!IsCallRetGuardAccess(b,n,p,b-p-1,b-p+15,stp));
 assert(!IsCallRetGuardAccess(0,n,p,b-16,b,stp));
 for(unsigned r=0;r<32;++r)for(unsigned t=0;t<32;++t){
     assert(IsCallRetGuardAccess(b,n,p,b-16,b,0xa9bf0320|(t<<10)|r));
     assert(IsCallRetGuardAccess(b,n,p,b+n,b+n,0xa8c10320|(t<<10)|r));
 }
 std::cout<<"BACHATA_WSI_FLIP_FPS_AND_FEX_CALLRET_GUARD_PASS encodings=2048\n";
}
'''
with tempfile.TemporaryDirectory() as d:
 f=pathlib.Path(d)/"test.cpp";f.write_text(cpp);e=pathlib.Path(d)/"test"
 subprocess.run(["c++","-std=c++23","-O2","-Wall","-Wextra","-Werror","-I",str(s),str(f),"-o",str(e)],check=True)
 subprocess.run([str(e)],check=True)
