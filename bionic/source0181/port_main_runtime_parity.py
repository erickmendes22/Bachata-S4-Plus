"""Match known donor FEX/DMEM runtime settings without touching guest patches.

Order 01.02 donor manifest specifies 5056 MiB and its Android log explicitly
reports dynamic_l1=0. The retained pinned FEX defaults DynamicL1Cache=true.
ISS donor also exposes the retail 5056 MiB DMEM size; use only when backing
already covers it and no user override or Pro/devkit mode is selected.
"""
from pathlib import Path

def apply(root:Path):
    p=Path(root)/"src/core/memory.cpp"
    s=p.read_text()
    old="    total_direct_size = total_size - flexible_size;"
    if s.count(old)!=1: raise RuntimeError("Main DMEM parity anchor drift")
    s=s.replace(old,'''    total_direct_size = total_size - flexible_size;
    const auto bachata_serial=Common::ElfInfo::Instance().GameSerial();
    const bool target=bachata_serial=="CUSA00785"||bachata_serial=="CUSA00004"||
                      bachata_serial=="CUSA00223";
    constexpr u64 donor_dmem=5056ull*1024*1024;
    constexpr u64 baseline_dmem=4608ull*1024*1024;
    if(target&&!is_neo&&!EmulatorSettings.IsDevKit()&&extra_dmem==0&&
       total_direct_size==baseline_dmem&&old_direct_size>=donor_dmem) {
        LOG_INFO(Kernel_Vmm,"BACHATA_MAIN_DMEM_PARITY old={} new={}",total_direct_size,donor_dmem);
        total_direct_size=donor_dmem;
    }''',1)
    p.write_text(s)
    p=Path(root)/"src/core/fex/fex_guest_engine.cpp"
    s=p.read_text()
    if '#include "common/elf_info.h"' not in s:
        s='#include "common/elf_info.h"\n'+s
    old='      FEXCore::Config::Set(FEXCore::Config::CONFIG_DISABLETELEMETRY, "1");'
    if s.count(old)!=1: raise RuntimeError("FEX config anchor drift")
    s=s.replace(old,old+'''
      // Order donor disables the resize heuristic, not the disk cache or TSO.
      // Preserve an explicit developer environment override.
      if(Common::ElfInfo::Instance().GameSerial()=="CUSA00785" &&
         std::getenv("FEX_DYNAMICL1CACHE")==nullptr) {
        FEXCore::Config::Set(FEXCore::Config::CONFIG_DYNAMICL1CACHE, "0");
        std::fprintf(stderr,"BACHATA_ORDER_FEX_CACHE dynamic_l1=0 disk_cache=unchanged tso=unchanged\\n");
      }''',1)
    p.write_text(s)
    print("BACHATA_MAIN_DMEM_PARITY / ORDER_FEX_CACHE applied")
    return {"dmem":"4608 -> 5056 MiB only on known title/default/reserved backing",
            "order_fex":"fixed JIT L1 as in donor; explicit environment override preserved",
            "preserved":"TSO, disk cache, original FEX engine, driver, visual effects"}
