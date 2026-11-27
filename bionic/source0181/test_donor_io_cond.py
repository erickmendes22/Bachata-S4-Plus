"""Compile the real donor IO helper and inspect the real condvar publication sites."""
from pathlib import Path
import subprocess,sys,tempfile,argparse
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
src=a.source/'src';h=src/'core/libraries/kernel/bachata_donor_io.h'
code=r'''
#include "bachata_donor_io.h"
#include <cassert>
#include <array>
#include <cstring>
using namespace BachataDonorIO;
int main(){
    int err=0;
    auto error=[&](int e){err=e;};
    Count published=0;
    unsigned calls=0;
    auto copy=[&](Count off,Count n){assert(off==published); published+=n;};
    auto got=FullRead(Chunk*2+5,[&](Count n)->Result{
        assert(n<=Chunk); ++calls; return std::min<Count>(n,Chunk/2);
    },copy,error);
    assert(got==Chunk*2+5 && published==Chunk*2+5 && calls==5);
    published=0;calls=0;
    assert(FullRead(100,[&](Count)->Result{++calls;if(calls==1)return 10;
        errno=EIO;return -1;},copy,error)==10);
    assert(published==10);
    published=0;calls=0;
    assert(FullRead(5,[&](Count)->Result{++calls;errno=EINTR;return -1;},copy,error)==-1);
    assert(err==EINTR && calls==64 && published==0);
    assert(FullRead(3,[](Count)->Result{return 0;},copy,error)==0);
    assert(FullRead(3,[](Count)->Result{return 4;},copy,error)==-1 && err==EIO);
    struct V{void* iov_base;Count iov_len;};
    std::array<V,3> v{{{nullptr,4},{nullptr,8},{nullptr,9}}};
    calls=0;
    assert(ReadVector(v.data(),3,[&](void*,Count n)->Result{++calls;
        return calls==2?-1:n;},error)==4 && calls==2);
    calls=0;
    assert(ReadVector(v.data(),3,[&](void*,Count n)->Result{++calls;
        return calls==1?2:n;},error)==2 && calls==1);
    calls=0;
    assert(ReadVector(v.data(),3,[&](void*,Count)->Result{++calls;return -1;},error)==-1 && calls==1);
    v[0].iov_len=Max;calls=0;
    assert(ReadVector(v.data(),3,[&](void*,Count)->Result{++calls;return 0;},error)==-1 && calls==0);
}
'''
with tempfile.TemporaryDirectory() as d:
    d=Path(d);(d/'test.cpp').write_text(code)
    subprocess.run(['c++','-std=c++20','-Wall','-Wextra','-Werror','-I',str(h.parent),str(d/'test.cpp'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test')],check=True)
c=(src/'core/libraries/kernel/threads/condvar.cpp').read_text()
assert 'SleepqRemove(sq, td);\n        td->wake_sema.release();\n        SleepqUnlock(this);' in c
assert 'SleepqDrop(sq, [](Pthread* td, void*) { td->wake_sema.release(); }, nullptr);' in c
assert 'DonorCondWake() && error == POSIX_ETIMEDOUT' in c
print('DONOR_IO_CONTRACT_OK; condvar publication sites checked (not a gameplay test)')
