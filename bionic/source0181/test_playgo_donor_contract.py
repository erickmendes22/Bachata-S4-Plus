"""Verify actual helper, source wiring and exact 64-bit language masks."""
import argparse,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
r=p.parse_args().source/"src"
s=(r/"core/libraries/playgo/playgo.cpp").read_text()
assert "return BachataBoot::LanguageMask(systemLang)" in s
assert "*outSpeed=OrbisPlayGoInstallSpeed::Full" in s
assert "playgo->GetPlaygoHeader().file_size && !playgo->chunks.empty()" in s
assert "total_size=BachataBoot::CompletedSize(total_size)" in s
cpp=r'''
#include "core/libraries/playgo/bachata_installed_package.h"
#include <cassert>
using namespace BachataBoot;
int main(){
    static_assert(LanguageMask(1)==0x4000000000000000ULL);
    static_assert(LanguageMask(0)==0x8000000000000000ULL);
    for(unsigned i=0;i<48;++i) assert(LanguageMask(i)==(1ULL<<(63-i)));
    assert(!LanguageMask(48) && !LanguageMask(~0ULL));
    assert(CompletedSize(0)==1 && CompletedSize(100)==100);
    assert(InstalledPackageTitle("CUSA00552") && InstalledPackageTitle("CUSA00004"));
    assert(!InstalledPackageTitle("CUSA00785") && !InstalledPackageTitle("CUSA08809"));
}
'''
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/"test.cpp";p.write_text(cpp);exe=Path(d)/"test"
    subprocess.run(["c++","-std=c++20","-Wall","-Wextra","-Werror","-fsanitize=undefined","-I",str(r),str(p),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print("BACHATA_PLAYGO_DONOR_CONTRACT_PASS")
