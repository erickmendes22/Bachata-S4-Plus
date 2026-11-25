#!/usr/bin/env python3
import argparse,pathlib,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument("--source",required=True);a=p.parse_args()
root=pathlib.Path(a.source)/"src";base=root/"video_core/buffer_cache"
s=(base/"buffer_cache.cpp").read_text()
b=s[s.index("void BufferCache::BeginAsyncReadback"):s.index("bool BufferCache::FinishAsyncReadback")]
f=s[s.index("bool BufferCache::FinishAsyncReadback"):s.index("void BufferCache::ReadMemory")]
assert "gpu_modified_ranges.Subtract" not in b
assert b.index("inflight_readbacks.push_back")<b.index("scheduler.Flush()")
assert f.index("memory->WriteSparseBacking")<f.index("gpu_modified_ranges.Subtract")<f.index("memory_tracker->UnmarkRegionAsGpuModified")
assert "staging_pool.Request(bytes,MemoryType::HostCached,0,true)" in b
assert "if(rb.validity.dirty)" in f and "staging_pool.FreeDeferred" in f
assert "scheduler.WaitSubmitted(rb.tick,false)" in s
assert s.count("MarkReadbacksDirty(")>=5
code=r'''
#include "video_core/buffer_cache/bachata_readback_span.h"
#include <cassert>
#include <iostream>
using namespace VideoCore::BachataReadback;
int main(){
  constexpr Span arena{0,0x1000000};
  auto span=Window(0x23456,1,arena,65536,0);
  assert(span.begin==0x20000 && span.end==0x30000);
  auto stream=Window(0x23456,1,arena,65536,4194304);
  assert(stream.begin==0x20000 && stream.end==0x420000);
  auto edge=Window(0xffff00,256,arena,65536,4194304);
  assert(edge.end==arena.end);
  assert(Window(0xffff00,257,arena,65536,0).end==0);
  Pending p{span};
  p.Mark({0x30000,0x40000});assert(!p.dirty);
  p.Mark({0x2ffff,0x30001});assert(p.dirty);
  Pending q{span};q.Mark({0x10000,0x20000});assert(!q.dirty);
  q.Mark({0x20000,0x20001});assert(q.dirty);
  for(unsigned i=0;i<4096;i++) {
    auto a=0x20000u+i*64u;
    Pending t{span};t.Mark({a,a+4});
    assert(t.dirty==(a<span.end));
  }
  std::cout<<"BACHATA_SOTC_ASYNC_READBACK_CONTRACT_PASS\n";
}
'''
with tempfile.TemporaryDirectory() as d:
    f=pathlib.Path(d)/"test.cpp";exe=pathlib.Path(d)/"test";f.write_text(code)
    subprocess.run(["c++","-std=c++20","-O2","-I",str(root),str(f),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
