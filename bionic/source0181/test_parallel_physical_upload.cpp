// SPDX-License-Identifier: GPL-2.0-or-later
#include "parallel_physical_upload.h"
#include <cassert>
#include <cstdio>
int main(){
    std::vector<std::uint8_t> a(4*1024*1024),b(a.size());
    BachataUpload::Pool pool;
    for(size_t k=0;k<24;++k){
        for(size_t i=0;i<a.size();++i)a[i]=static_cast<std::uint8_t>(i*7+k);
        std::fill(b.begin(),b.end(),0);
        std::vector<BachataUpload::Copy> work;
        for(size_t i=0;i<a.size();i+=65536)
            work.push_back({a.data()+i,b.data()+i,65536});
        pool.CopyBatch(work);
        assert(a==b);
    }
    std::puts("PHYSICAL_UPLOAD_POOL_PASS");
}
