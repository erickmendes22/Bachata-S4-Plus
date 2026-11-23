#!/usr/bin/env python3
"""Compile the actual PSARC C++ reader and test zlib block boundaries in CI.

The fixture emulates /app0/build.psarc from the CUSA05170 diagnostic:
PhyreFIOS2/gra/shader/shader.GNM.phyre. It is original synthetic data,
not copyrighted game content.
"""
import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "psarc_fs.cpp"
HEADER = HERE / "psarc_fs.h"

MOCKS = {
"core/file_sys/ifile.h": r"""
#pragma once
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <vector>
using u8=uint8_t;using u32=uint32_t;using u64=uint64_t;using s64=int64_t;
namespace Common::FS {
enum class FileAccessMode { Read, Write, ReadWrite };
enum class SeekOrigin { SetOrigin, CurrentPosition, End };
}
namespace Core::FileSys {
enum class MmapPolicy { Native, Copy, Unsupported };
struct DirEntry {std::string name;bool is_directory{};u64 size{};};
struct FileStat {u64 size{};bool is_directory{};};
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
virtual void Stat(FileStat& out){out.size=Size();}
};
class IDirectory {public:virtual ~IDirectory()=default;
virtual bool Next(DirEntry&)=0;virtual void Rewind()=0;};
class IBackend {public:virtual ~IBackend()=default;
virtual bool Exists(std::string_view)=0;
virtual bool IsDirectory(std::string_view)=0;
virtual std::unique_ptr<IFile> Open(std::string_view,Common::FS::FileAccessMode)=0;
virtual std::unique_ptr<IDirectory> OpenDir(std::string_view)=0;
virtual bool IsReadOnly()const=0;
virtual std::filesystem::path RootPath()const=0;
virtual std::optional<std::vector<u8>> ReadFile(std::string_view)const=0;};
}
""",
"common/logging/log.h": r"""
#pragma once
inline void TestLogSink(auto&&...) {}
#define Lib_SysModule 0
#define LOG_INFO(...) TestLogSink(__VA_ARGS__)
#define LOG_ERROR(...) TestLogSink(__VA_ARGS__)
""",
}
MAIN = r"""
#include "core/file_sys/backends/psarc_fs.h"
#include <cassert>
#include <fstream>
#include <iostream>
#include <vector>
#include <algorithm>
using namespace Core::FileSys;
struct MemoryFile final: IFile {
std::vector<u8> bytes;u64 pos{};
explicit MemoryFile(std::vector<u8> b):bytes(std::move(b)){}
s64 Read(void* dst,u64 n)override {
n=std::min<u64>(n,bytes.size()-pos);
std::memcpy(dst,bytes.data()+pos,n);pos+=n;return n;
}
s64 Write(const void*,u64)override{return -1;}
bool Seek(s64 off,Common::FS::SeekOrigin origin)override{
s64 base=origin==Common::FS::SeekOrigin::SetOrigin?0:
origin==Common::FS::SeekOrigin::CurrentPosition?pos:bytes.size();
if(base+off<0||u64(base+off)>bytes.size())return false;
pos=base+off;return true;
}
u64 Tell()const override{return pos;}
u64 Size()const override{return bytes.size();}
bool Flush()override{return true;}
bool IsOpen()const override{return true;}
};
int main(int argc,char** argv) {
assert(argc==3);
std::ifstream in(argv[1],std::ios::binary);
std::vector<u8> psarc((std::istreambuf_iterator<char>(in)),{});
std::ifstream check(argv[2],std::ios::binary);
std::vector<u8> expected((std::istreambuf_iterator<char>(check)),{});
PsarcBackend valid(std::make_unique<MemoryFile>(std::move(psarc)));
assert(valid.IsOpen());
assert(valid.IsReadOnly());
assert(valid.IsDirectory(""));
assert(valid.IsDirectory("gra"));
assert(valid.IsDirectory("gra/shader"));
assert(valid.Exists("gra/shader/shader.GNM.phyre"));
assert(valid.Exists("/GRA/SHADER/SHADER.GNM.PHYRE"));
auto file=valid.Open("gra/shader/shader.GNM.phyre",
    Common::FS::FileAccessMode::Read);
assert(file && file->Size()==expected.size());
auto write=valid.Open("gra/shader/shader.GNM.phyre",
    Common::FS::FileAccessMode::Write);
assert(!write);
std::vector<u8> seen(expected.size());
assert(file->Read(seen.data(),13)==13);
assert(std::equal(seen.begin(),seen.begin()+13,expected.begin()));
assert(file->Seek(65526,Common::FS::SeekOrigin::SetOrigin));
assert(file->Read(seen.data()+65526,100)==100);
assert(std::equal(seen.begin()+65526,seen.begin()+65626,expected.begin()+65526));
file->Seek(0,Common::FS::SeekOrigin::SetOrigin);
assert(file->Read(seen.data(),seen.size())==s64(seen.size()));
assert(seen==expected);
auto dir=valid.OpenDir("gra/shader");
assert(dir);
DirEntry d{};
assert(dir->Next(d) && d.name=="shader.gnm.phyre" && !d.is_directory);
assert(!dir->Next(d));
auto content=valid.ReadFile("GRA/SHADER/SHADER.GNM.PHYRE");
assert(content&&*content==expected);
PsarcBackend invalid(std::make_unique<MemoryFile>(std::vector<u8>{0,1,2,3}));
assert(!invalid.IsOpen());
std::cout<<"BACHATA_REAL_PSARC_ZLIB_BLOCK_READ_PASS bytes="<<expected.size()<<"\n";
}
"""

def make_fixture() -> tuple[bytes, bytes]:
    name=b"gra/shader/shader.GNM.phyre\n"
    data=(b"SOTC/PH-Y-R-E" * 12000)[:130_000]
    bs=65536
    chunks=[name,data[:bs],data[bs:]]
    packed=[zlib.compress(x,9) for x in chunks]
    assert all(len(x)<65536 for x in packed)
    n=2
    toc_length=32+n*30+len(chunks)*2
    offsets=[toc_length,toc_length+len(packed[0])]
    def entry(start,size,offset):
        return b'\0'*16+struct.pack(">I",start)+size.to_bytes(5,'big')+offset.to_bytes(5,'big')
    head=struct.pack(">4sI4sIIIII",b"PSAR",0x10004,b"zlib",toc_length,30,n,bs,0)
    table=b''.join(struct.pack(">H",len(p)) for p in packed)
    archive=head+entry(0,len(name),offsets[0])+entry(1,len(data),offsets[1])+table+b''.join(packed)
    assert archive[:4]==b"PSAR"
    assert len(head)==32 and archive[12:16]==struct.pack(">I",toc_length)
    return archive,data

def run() -> None:
    cxx=shutil.which("clang++") or shutil.which("g++")
    if not cxx:
        raise RuntimeError("C++ host compiler unavailable; no silent test skip")
    if not SRC.is_file() or not HEADER.is_file():
        raise RuntimeError("PSARC source/headers absent")
    with tempfile.TemporaryDirectory(prefix="bachata-psarc-") as temp:
        out=Path(temp)
        for name,content in MOCKS.items():
            file=out/name
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text(content)
        header=out/"core/file_sys/backends/psarc_fs.h"
        header.parent.mkdir(parents=True,exist_ok=True)
        header.write_text(HEADER.read_text())
        (out/"test.cpp").write_text(MAIN)
        archive,expected=make_fixture()
        (out/"build.psarc").write_bytes(archive)
        (out/"shader.data").write_bytes(expected)
        subprocess.run([cxx,"-std=c++20","-Wall","-Wextra","-Werror","-O1",
                        "-I",str(out),str(SRC),str(out/"test.cpp"),
                        "-o",str(out/"run"),"-lz"],check=True)
        subprocess.run([str(out/"run"),str(out/"build.psarc"),
                        str(out/"shader.data")],check=True)

if __name__=="__main__":
    run()
