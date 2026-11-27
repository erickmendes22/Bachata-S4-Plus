"""Installed-package PlayGo contract from TLOU and ISS reference ports."""
from pathlib import Path
HEADER=r'''#pragma once
#include <cstdint>
#include <string_view>
namespace BachataBoot {
constexpr std::uint64_t LanguageMask(std::uint64_t language) {
    return language<48 ? std::uint64_t{1}<<(63-language):0;
}
constexpr bool InstalledPackageTitle(std::string_view serial) {
    return serial=="CUSA00552"||serial=="CUSA00557"||
           serial=="CUSA00004"||serial=="CUSA00223";
}
constexpr std::uint64_t CompletedSize(std::uint64_t parsed) {
    return parsed?parsed:1;
}
}
'''
def once(s,old,new,why):
    if s.count(old)!=1: raise RuntimeError("boot contract drift "+why+": "+str(s.count(old)))
    return s.replace(old,new,1)
def apply(root):
    root=Path(root)/"src"
    h=root/"core/libraries/playgo/bachata_installed_package.h"
    h.write_text(HEADER)
    p=h.with_name("playgo.cpp")
    s=p.read_text()
    s=once(s,'#include "playgo.h"','#include "playgo.h"\n#include "bachata_installed_package.h"\n#include "common/elf_info.h"',"installed package dependencies")
    s=once(s,"    return (1 << (64 - systemLang - 1));","    return BachataBoot::LanguageMask(systemLang);","64-bit PS4 language mask")
    s=once(s,"    *outSpeed = playgo->speed;",r'''    // Reference ports report Full for an extracted, parsed package.
    // Do not make a missing/corrupt package appear installed.
    if(BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial()) &&
       playgo->GetPlaygoHeader().file_size && !playgo->chunks.empty()) {
        *outSpeed=OrbisPlayGoInstallSpeed::Full;
    } else {
        *outSpeed = playgo->speed;
    }''',"full install speed")
    s=once(s,"    outProgress->progressSize = total_size;\n    outProgress->totalSize = total_size;",r'''    if(BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial()))
        total_size=BachataBoot::CompletedSize(total_size);
    outProgress->progressSize = total_size;
    outProgress->totalSize = total_size;''',"complete progress nonzero")
    s=once(s,"    LOG_INFO(Lib_PlayGo, \"called, bufSize = {}\", param->bufSize);",
           "    if(!param) return ORBIS_PLAYGO_ERROR_BAD_POINTER;\n    LOG_INFO(Lib_PlayGo, \"called, bufSize = {}\", param->bufSize);","init parameter safety")
    s=once(s,"    playgo->langMask = scePlayGoConvertLanguage(system_lang);",
           "    playgo->langMask = scePlayGoConvertLanguage(system_lang);\n"
           "    LOG_INFO(Lib_PlayGo,\"BACHATA_PLAYGO_PACKAGE chunks={} language={} mask={:#x}\","
           "playgo->chunks.size(),system_lang,playgo->langMask);","actual parsed state evidence")
    p.write_text(s)
    return {"playgo":"real parsed local chunks, 64-bit language mask, Full and nonzero progress for target packages"}
