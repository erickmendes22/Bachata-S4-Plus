#!/usr/bin/env python3
"""Compile the real PS4 SAF IFile and test independent broker descriptors.

The test compiles bionic/source0181/saf_fs_backend.cpp, not a rewritten
implementation. It simulates Android's broker with two independent open(2)
descriptors over a temporary file, exercises pread/seek/stat/map and confirms
one game's file handle cannot alter another one's cursor.
"""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SRC=HERE/"saf_fs_backend.cpp"
HEADER=HERE/"saf_fs_backend.h"
MOCKS={
"core/file_sys/ifile.h":r"""
#pragma once
#include <cstdint>
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <string_view>
#include <vector>
using u8=uint8_t;using u32=uint32_t;using u64=uint64_t;using s64=int64_t;
namespace Common::FS {
enum class FileAccessMode {Read};
enum class SeekOrigin {SetOrigin,CurrentPosition,End};
}
namespace Core::FileSys {
enum class MmapPolicy{Native,Copy,Unsupported};
struct FileStat {
u64 size{};
s64 mtime_sec{},mtime_nsec{},atime_sec{},atime_nsec{},ctime_sec{},ctime_nsec{};
bool is_directory{};
};
struct FileMapContext {
std::function<void(u8*,u64)> map_anonymous;
std::function<void(u8*,u64,u32)> protect;
};
class IFile {
public:virtual ~IFile()=default;
virtual s64 Read(void*,u64)=0;virtual s64 Write(const void*,u64)=0;
virtual bool Seek(s64,Common::FS::SeekOrigin)=0;
virtual u64 Tell()const=0;virtual u64 Size()const=0;
virtual bool Flush()=0;virtual bool IsOpen()const=0;
virtual MmapPolicy GetMmapPolicy()const{return MmapPolicy::Unsupported;}
virtual bool Map(u8*,u64,u64,u32,const FileMapContext&){return false;}
virtual void Stat(FileStat& stat){stat.size=Size();}
virtual bool IsReadOnly()const{return true;}
virtual bool IsWriteOnly()const{return false;}
};
}
""",
"android_saf_bridge.h":r"""
#pragma once
#include <optional>
#include <string_view>
namespace BachataSaf {std::optional<int> OpenFd(std::string_view);}
""",
"common/logging/log.h":r"""
#pragma once
inline void IgnoreLog(auto&&...){}
#define Kernel_Fs 0
#define LOG_TRACE(...) IgnoreLog(__VA_ARGS__)
#define LOG_WARNING(...) IgnoreLog(__VA_ARGS__)
""",
}
MAIN=r"""
#include "core/file_sys/backends/saf_fs_backend.h"
#include "android_saf_bridge.h"
#include <cassert>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <fcntl.h>
#include <unistd.h>
using namespace Core::FileSys;
static std::string filename;
std::optional<int> BachataSaf::OpenFd(std::string_view name) {
if(name!="app0/test.bin"&&name!="/app0/test.bin")return {};
int fd=::open(filename.c_str(),O_RDONLY|O_CLOEXEC);
if(fd<0)return {};
return fd;
}
int main(int argc,char**argv){
assert(argc==2);filename=argv[1];
auto a=OpenSafGuestFile("/app0/test.bin");
auto b=OpenSafGuestFile("/app0/test.bin");
assert(a&&b&&a->Size()==8192&&b->Size()==8192);
assert(a->GetMmapPolicy()==MmapPolicy::Copy);
char read_a[20]{},read_b[20]{};
assert(a->Read(read_a,10)==10);
assert(b->Read(read_b,10)==10);
assert(std::memcmp(read_a,read_b,10)==0);
assert(a->Tell()==10&&b->Tell()==10);
assert(a->Seek(300,Common::FS::SeekOrigin::SetOrigin));
assert(a->Read(read_a,19)==19);
assert(b->Read(read_b,19)==19);
assert(a->Tell()==319&&b->Tell()==29);
FileStat stat{};a->Stat(stat);assert(stat.size==8192);
uint32_t protected_with{};
std::vector<uint8_t> page(4096);
FileMapContext ctx{};
ctx.map_anonymous=[](u8*,u64){};
ctx.protect=[&](u8*,u64,u32 flags){protected_with=flags;};
assert(a->Map(page.data(),page.size(),4096,123,ctx));
assert(protected_with==123);
assert(page[0]=='A'+4096%26&&page[4095]=='A'+8191%26);
assert(!a->Map(page.data(),2,8191,0,ctx));
assert(!a->Write(page.data(),100));
assert(!OpenSafGuestFile("/app0/absent.bin"));
std::cout<<"BACHATA_SAF_DIRECT_FD_INDEPENDENT_READ_PASS\n";
}
"""
def run():
    cxx=shutil.which("clang++") or shutil.which("g++")
    if not cxx or not SRC.is_file() or not HEADER.is_file():
        raise RuntimeError("Missing SAF backend C++ source or host compiler")
    with tempfile.TemporaryDirectory(prefix="bachata-saf-") as tmp:
        directory=Path(tmp)
        for name,src in MOCKS.items():
            p=directory/name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(src)
        hdr=directory/"core/file_sys/backends/saf_fs_backend.h"
        hdr.parent.mkdir(parents=True,exist_ok=True)
        hdr.write_text(HEADER.read_text())
        (directory/"test.cpp").write_text(MAIN)
        (directory/"test.bin").write_bytes(bytes(ord("A")+i%26 for i in range(8192)))
        subprocess.run([cxx,"-std=c++20","-Wall","-Wextra","-Werror","-O1",
                        "-I",str(directory),str(SRC),str(directory/"test.cpp"),
                        "-o",str(directory/"test")],check=True)
        subprocess.run([str(directory/"test"),str(directory/"test.bin")],check=True)
if __name__=="__main__":
    run()
