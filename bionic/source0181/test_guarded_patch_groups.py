#!/usr/bin/env python3
"""Compile the real XML parser and both patch application paths with pinned pugixml."""
from pathlib import Path
import argparse
import os
import re
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--pugixml', type=Path)
a = p.parse_args()
source = a.source.resolve()
pugi = (a.pugixml or source / 'externals/pugixml').resolve() / 'src'
assert (pugi / 'pugixml.cpp').is_file(), 'pinned pugixml submodule is required'
text = (source / 'src/common/memory_patcher.cpp').read_text()
header = (source / 'src/common/memory_patcher.h').read_text()
assert 'RequireAllExpected' in text and 'ApplyGuardedGroup' in text


def function(name):
    match = re.search(r'^\S[^\n]*\b' + re.escape(name) + r'\(', text, re.M)
    assert match, name
    start = match.start()
    first = text.index('{', match.end())
    depth, i, state = 1, first + 1, ''
    while depth:
        c = text[i]
        if state == 'line':
            if c == '\n': state = ''
        elif state == 'block':
            if text[i:i+2] == '*/': state = ''; i += 1
        elif state in ('"', "'"):
            if c == '\\': i += 1
            elif c == state: state = ''
        elif text[i:i+2] == '//': state = 'line'; i += 1
        elif text[i:i+2] == '/*': state = 'block'; i += 1
        elif c in ('"', "'"): state = c
        elif c == '{': depth += 1
        elif c == '}': depth -= 1
        i += 1
    return text[start:i]


names_before = [
    'ParseStrictHexAddress', 'ParseStrictHexBytes', 'IsWithinEbootBounds', 'toHex',
    'convertValueToHex', 'AppliedXmlFiles', 'XmlAppliedKey', 'PatchLineTypeFromString',
    'BuildPatchLine', 'IsMaskType', 'ToPatchMask',
]
names_after = [
    'ApplyLine', 'CanonicalSelectorKey', 'PatchDefinitionIdentity',
    'EnumeratePatchDefinitions', 'ApplyManagedPatches', 'ApplyLegacyPatchesFromXML',
    'IsXmlAlreadyApplied', 'MarkXmlApplied', 'ResetAppliedXmlFiles',
    'PatchMemory', 'PatternToByte', 'PatternScan',
]
group = text[text.index('struct GuardedPatchChoices {'):text.index('bool ApplyLine(')]
prefix = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <codecvt>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <optional>
#include <sstream>
#include <span>
#include <string>
#include <unordered_set>
#include <vector>
#include <pugixml.hpp>
#include "common/memory_patcher.h"
#include "common/guarded_patch_group.h"
using u8=std::uint8_t; using u16=std::uint16_t; using u32=std::uint32_t;
using u64=std::uint64_t; using s32=std::int32_t;
#define LOG_ERROR(...) ((void)0)
#define LOG_WARNING(...) ((void)0)
#define LOG_INFO(...) ((void)0)
namespace Core {
struct MemoryManager {
    std::uintptr_t hole_begin{},hole_end{};
    // The production legacy method skips mapping validation below 1 GiB.
    // Keep that behavior in the mock so accidentally calling it is detected.
    std::uint64_t ClampRangeSize(std::uintptr_t,std::uint64_t size) const { return size; }
    std::uint64_t ClampGpuRangeSize(std::uintptr_t address,std::uint64_t size) const {
        return hole_begin && address<hole_end && hole_begin<address+size ? 0 : size;
    }
};
}
namespace Common {
template<class T> struct Singleton { static T* Instance(){static T value;return &value;} };
}
namespace MemoryPatcher {
uintptr_t g_eboot_address{};
uint64_t g_eboot_image_size{};
std::string g_game_serial;
std::string version="01.02";
std::string CurrentAppVersion(){return version;}
'''

tests = r'''
} // namespace MemoryPatcher
using namespace MemoryPatcher;
static const std::string aspect="16:9 Aspect Ratio (Full Screen)";
static std::array<std::uint8_t,128> original() {
    std::array<std::uint8_t,128> b;b.fill(0xa5);
    for(unsigned i=0;i<4;++i){b[16+i]=1+i;b[32+i]=0x11+i;b[48+i]=0x21+i;}
    return b;
}
static std::string line(std::string address,std::string expected,std::string value,
                        std::string extra="",std::string type="bytes") {
    return "<Line Type=\""+type+"\" Address=\""+address+"\" Expected=\""+expected+
           "\" Value=\""+value+"\" "+extra+"/>";
}
static std::string lines() {
    return line("400010","01020304","11223344")+
           line("400020","11121314","aabbccdd")+
           line("400030","21222324","31323334","IfEnabled=\""+aspect+"\"")+
           line("400030","21222324","41424344","IfDisabled=\""+aspect+"\"");
}
static void replace(std::string& text,const std::string& from,const std::string& to) {
    auto p=text.find(from);assert(p!=std::string::npos);text.replace(p,from.size(),to);
}
static std::string metadata(const std::string& name,const std::string& content,bool enabled,
                            bool guarded=true,std::string app="01.02") {
    return "<Metadata Title=\"Order\" Name=\""+name+"\" Author=\"donor\" AppVer=\""+
           app+"\" AppElf=\"eboot.bin\" RequireAllExpected=\""+(guarded?"true":"false")+
           "\" isEnabled=\""+(enabled?"true":"false")+"\"><PatchList>"+content+
           "</PatchList></Metadata>";
}
int main(int argc,char** argv) {
    assert(argc==2);const auto xml=std::filesystem::path(argv[1]);unsigned cases=0;
    const auto run=[&](std::string content,bool managed,bool enabled,bool widescreen,
                       bool guarded,std::string app,std::array<std::uint8_t,128>& bytes,
                       bool duplicate=false,bool hole=false) {
        ResetAppliedXmlFiles();version="01.02";
        g_eboot_address=reinterpret_cast<std::uintptr_t>(bytes.data());
        g_eboot_image_size=bytes.size();
        auto* memory=Common::Singleton<Core::MemoryManager>::Instance();
        memory->hole_begin=hole?g_eboot_address+32:0;memory->hole_end=hole?g_eboot_address+36:0;
        // Managed selection deliberately disagrees with the XML flags.
        std::ofstream f(xml);
        f<<"<Patch>"<<metadata("Resolution",content,managed?!enabled:enabled,guarded,app)
         <<metadata(aspect,"",managed?!widescreen:widescreen,false);
        if(duplicate)f<<metadata(aspect,"",false,false);
        f<<"</Patch>";f.close();
        const auto defs=EnumeratePatchDefinitions(xml);assert(defs.size()==(duplicate?3:2));
        assert(defs[0].require_all_expected==guarded);
        assert(defs[0].lines[0].expected=="01020304" || content.find("01020304")==std::string::npos);
        if(managed){
            std::unordered_set<std::string> ids;
            if(enabled)ids.insert(defs[0].id);if(widescreen)ids.insert(defs[1].id);
            const auto result=ApplyManagedPatches(xml,ids);
            assert(!result.records.empty());
        } else ApplyLegacyPatchesFromXML(xml);
        ++cases;
    };
    for(bool managed:{false,true})for(bool enabled:{false,true})for(bool wide:{false,true}) {
        auto bytes=original();auto expected=bytes;
        if(enabled){
            const std::array<unsigned char,4> a{0x11,0x22,0x33,0x44},b{0xaa,0xbb,0xcc,0xdd};
            std::copy(a.begin(),a.end(),expected.begin()+16);std::copy(b.begin(),b.end(),expected.begin()+32);
            for(unsigned i=0;i<4;++i)expected[48+i]=(wide?0x31:0x41)+i;
        }
        run(lines(),managed,enabled,wide,true,"01.02",bytes);assert(bytes==expected);
        // Re-applying the same selected group remains valid without requiring originals.
        run(lines(),managed,enabled,wide,true,"01.02",bytes);assert(bytes==expected);
    }
    for(bool managed:{false,true})for(unsigned fault=0;fault<14;++fault) {
        auto bytes=original();auto content=lines();std::string app="01.02";
        switch(fault){
        case 0:bytes[48]^=1;break;
        case 1:replace(content,"400030","40007f");break;
        case 2:replace(content,"Expected=\"11121314\"","Expected=\"\"");break;
        case 3:replace(content,"aabbccdd","abc");break;
        case 4:replace(content,"400020","400012");break;
        case 5:replace(content,"IfEnabled=\""+aspect+"\"","IfEnabled=\"missing\"");break;
        case 6:replace(content,"IfEnabled=\""+aspect+"\"","IfEnabled=\""+aspect+"\" IfDisabled=\""+aspect+"\"");break;
        case 7:app="01.00";break;
        case 8:replace(content,"Type=\"bytes\"","Type=\"mask\"");break;
        case 9:replace(content,"400020","ffffffffffffffff");break;
        case 10:replace(content,"400020","3fffff");break;
        case 11:replace(content,"11121314","1112");break;
        case 12:break; // unmapped page, despite being inside image bounds
        case 13:break; // duplicate conditional name
        }
        const auto before=bytes;
        run(content,managed,true,true,true,app,bytes,fault==13,fault==12);
        assert(bytes==before);
    }
    for(bool managed:{false,true}) {
        // No opt-in: legacy Expected continues to be ignored, as in prior builds.
        auto bytes=original();auto expected=bytes;
        const auto content=line("400010","ffffffff","11223344");
        const std::array<unsigned char,4> value{0x11,0x22,0x33,0x44};
        std::copy(value.begin(),value.end(),expected.begin()+16);
        run(content,managed,true,false,false,"01.02",bytes);assert(bytes==expected);
        // The historical version-independent mask path is preserved.
        bytes=original();expected=bytes;expected[16]=0x11;expected[17]=0x22;
        run(line("01 02 03 04","","1122","","mask"),managed,true,false,false,"01.00",bytes);
        assert(bytes==expected);
    }
    // A malformed final line cannot leave the earlier line applied.
    for(bool managed:{false,true}) {
        auto bytes=original();const auto before=bytes;
        run(line("400010","01020304","11223344")+line("400020","11121314","zz"),
            managed,true,false,true,"01.02",bytes);assert(bytes==before);
    }
    std::cout<<"BACHATA_GUARDED_PATCH_GROUP_PASS cases="<<cases
             <<" real-XML/managed/legacy/preimages/conditions/idempotence/bounds/holes/no-partial-write\n";
}
'''

with tempfile.TemporaryDirectory(prefix='bachata-patch-groups-') as tmp:
    root = Path(tmp)
    common = root / 'common'
    common.mkdir()
    (common / 'memory_patcher.h').write_text(header)
    (common / 'patch_session.h').write_text(
        '#pragma once\nnamespace PatchSession { struct Config; enum class RejectReason { None }; }\n')
    (common / 'guarded_patch_group.h').write_bytes((source / 'src/common/guarded_patch_group.h').read_bytes())
    cpp = root / 'test.cpp'
    program = (prefix + '\n'.join(function(n) for n in names_before) + '\n' + group + '\n' +
               '\n'.join(function(n) for n in names_after) + '\n' + tests)
    cpp.write_text(program)
    exe = root / 'test'
    command = [os.environ.get('CXX', 'c++'), '-std=c++23', '-O1', '-g0',
               '-fsanitize=undefined', '-fno-sanitize-recover=all',
               '-I', str(root), '-I', str(pugi), str(cpp), str(pugi / 'pugixml.cpp'),
               '-o', str(exe)]
    subprocess.run(command, check=True)
    subprocess.run([str(exe), str(root / 'patch.xml')], check=True)
    assert program.count('memory->ClampGpuRangeSize(') == 1
    cpp.write_text(program.replace('memory->ClampGpuRangeSize(', 'memory->ClampRangeSize('))
    subprocess.run(command, check=True)
    negative = subprocess.run([str(exe), str(root / 'negative.xml')], capture_output=True, text=True)
    assert negative.returncode != 0 and 'bytes==before' in negative.stderr, negative.stderr
    print('BACHATA_GUARDED_PATCH_MAPPING_NEGATIVE_PASS legacy-small-range-fast-path-rejected')
