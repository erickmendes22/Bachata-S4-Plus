// SPDX-FileCopyrightText: Copyright 2026 Bachata S4+ contributors
// SPDX-License-Identifier: GPL-2.0-or-later
// Test actual Android SAF broker translation without Android or real content.
// Simulates BSF1 STAT/LIST/OPEN for an on-disk 64-byte fake Phyre resource.
#include "android_saf_bridge.h"
#include "android_saf_transport.h"
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fcntl.h>
#include <string>
#include <string_view>
#include <unistd.h>
#include <vector>

namespace {
std::string g_local_file;
std::string g_last_open;
void Be32(std::vector<std::uint8_t>& x, unsigned n) {
    for (int s=24;s>=0;s-=8) x.push_back((n>>s)&255u);
}
void Be64(std::vector<std::uint8_t>& x, std::uint64_t n) {
    for (int s=56;s>=0;s-=8) x.push_back((n>>s)&255u);
}
bool Directory(std::string_view path) {
    return path.empty()||path=="sce_sys"||path=="gra"||path=="gra/shader";
}
bool File(std::string_view path) {
    return path=="sce_sys/param.sfo" || path=="gra/shader/shader.GNM.phyre";
}
std::vector<std::uint8_t> BuildResponseList(std::string_view path) {
    std::string leaf;
    bool dir=false;
    if(path.empty()){leaf="gra";dir=true;}
    else if(path=="gra"){leaf="shader";dir=true;}
    else if(path=="gra/shader"){leaf="shader.GNM.phyre";dir=false;}
    else if(path=="sce_sys"){leaf="param.sfo";dir=false;}
    else return {0,0,0,0};
    std::vector<std::uint8_t> out;
    Be32(out,1);
    out.push_back(0);
    out.push_back(static_cast<std::uint8_t>(leaf.size()));
    for(char c:leaf)out.push_back(c);
    out.push_back(dir?1:0);
    Be64(out,dir?0:64);
    Be64(out,0);
    return out;
}
} // namespace

namespace BachataSaf::Protocol {
std::uint16_t Read16(const std::uint8_t* p) {
    return (std::uint16_t(p[0])<<8)|p[1];
}
std::uint32_t Read32(const std::uint8_t* p) {
    return (std::uint32_t(p[0])<<24)|(std::uint32_t(p[1])<<16)|
           (std::uint32_t(p[2])<<8)|p[3];
}
std::uint64_t Read64(const std::uint8_t* p) {
    return (std::uint64_t(Read32(p))<<32)|Read32(p+4);
}
Reply Request(const std::string&,const std::string&,int opcode,std::string_view path) {
    Reply ret;
    if(opcode==1 && (Directory(path)||File(path))){
        ret.status=0;
        ret.bytes.push_back(Directory(path)?1:0);
        Be64(ret.bytes,File(path)?64:0);
        Be64(ret.bytes,0);
    } else if(opcode==2){
        ret.status=0;ret.bytes=BuildResponseList(path);
    } else if(opcode==3 && File(path)){
        ret.fd=::open(g_local_file.c_str(),O_RDONLY|O_CLOEXEC);
        if(ret.fd>=0){ret.status=0;g_last_open=path;}
    }
    return ret;
}
} // namespace BachataSaf::Protocol

int main(int argc,char** argv) {
    assert(argc==3);
    g_local_file=argv[1];
    const std::filesystem::path scratch(argv[2]);
    assert(BachataSaf::Configure("test-socket","test-token",scratch,scratch));
    BachataSaf::RegisterGuestAlias("/app0","PhyreFIOS2");
    assert(BachataSaf::StatPath("PhyreFIOS2/gra/shader/shader.GNM.phyre"));
    // Real DocumentsProvider case often differs from game's import.
    assert(BachataSaf::StatPath("PhyreFIOS2/GRA/SHADER/SHADER.gnm.phyre"));
    auto fd=BachataSaf::OpenFd("PhyreFIOS2/gra/shader/shader.GNM.phyre");
    assert(fd && *fd>=0);
    assert(g_last_open=="gra/shader/shader.GNM.phyre");
    std::array<char,8> bytes{};
    assert(::pread(*fd,bytes.data(),bytes.size(),0)==8);
    assert(std::string_view(bytes.data(),4)=="TEST");
    ::close(*fd);
    auto fd2=BachataSaf::OpenFd("PhyreFIOS2/GRA/SHADER/shader.gnm.phyre");
    assert(fd2 && *fd2>=0);
    assert(g_last_open=="gra/shader/shader.GNM.phyre");
    ::close(*fd2);
    std::vector<BachataSaf::Entry> files;
    assert(BachataSaf::List("PhyreFIOS2/gra/shader",files));
    assert(files.size()==1&&files[0].name=="shader.GNM.phyre");
    auto host=BachataSaf::Resolve("PhyreFIOS2/gra/shader/shader.GNM.phyre");
    assert(host && std::filesystem::exists(*host));
    BachataSaf::Shutdown();
    std::puts("BACHATA_RELEASE026_FIOS_ALIAS_SAF_STAT_LIST_OPEN_PASS");
}
