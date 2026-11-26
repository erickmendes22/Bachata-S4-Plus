#!/usr/bin/env python3
"""Compile real FIOS registration, resolver, relocator and dynamic-load methods.

ELF storage, symbol tables, veneer allocation and loading bytes are controlled
boundaries. The decisions which select guest exports and seal/revisit imports
are the generated production methods, including the existing sysmodule arm.
"""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def block(text, marker):
    start = text.index(marker)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[start:end + 1]
    raise AssertionError(marker)


PREAMBLE = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <ranges>
#include <set>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <variant>
#include <vector>
using u16=uint16_t;using u32=uint32_t;using u64=uint64_t;using s32=int32_t;
using VAddr=u64;
#if FIOS_TEST_FEX
#define SHADPS4_ENABLE_FEX_GUEST_CPU 1
#endif
#ifndef __cpp_lib_ranges_contains
namespace std::ranges {
template<input_range R,class T,class P=std::identity>
bool contains(R&& range,const T& value,P project={}) {
    return std::ranges::find(range,value,project)!=std::ranges::end(range);
}
}
#endif
template<class... T>void Consume(const T&... values){((void)values,...);}
[[maybe_unused]] constexpr int Core_Linker=1,Lib_Kernel=2,Lib_SysModule=3;
#define LOG_INFO(...) Consume(__VA_ARGS__)
#define LOG_WARNING(...) Consume(__VA_ARGS__)
#define LOG_ERROR(...) Consume(__VA_ARGS__)
#define ASSERT_MSG(condition,...) assert(condition)
#define UNREACHABLE_MSG(...) assert(false)
namespace Common {
std::vector<std::string> SplitString(const std::string& value,char separator){
    std::vector<std::string> parts;size_t begin=0;
    for(size_t i=0;i<=value.size();++i)if(i==value.size()||value[i]==separator){
        parts.emplace_back(value.substr(begin,i-begin));begin=i+1;
    }
    return parts;
}
template<class T>struct Singleton{
    inline static T* pointer=nullptr;
    static T* Instance(){assert(pointer);return pointer;}
};
struct ElfInfo{
    std::string serial="CUSA00004";
    const std::string& GameSerial()const{return serial;}
};
}
struct Settings {
    std::filesystem::path root;
    const std::filesystem::path& GetSysModulesDir()const{return root;}
} EmulatorSettings;
namespace Core {
namespace AeroLib {
struct Nid {std::string name,nid;};
const Nid* FindByNid(const char*){return nullptr;}
u64 GetStub(const char*){return 0xdead0001;}
u64 GetStub(const std::string&){return 0xdead0002;}
}
namespace GuestCpu {
struct HleCallAdapter{u64 operation;};
struct HleVeneerFailure{std::string error;};
struct HleVeneerAllocator {
    std::map<u64,u64> allocated;
    std::variant<u64,HleVeneerFailure> Allocate(const HleCallAdapter& adapter){
        auto [it,added]=allocated.emplace(adapter.operation,0xf0000000ULL+adapter.operation*32);
        (void)added;return it->second;
    }
};
}
namespace Loader {
enum class SymbolType{Unknown,Function,Object,Tls,NoType};
struct SymbolResolver{
    std::string name,nidName,library;u16 library_version{};std::string module;
    SymbolType type{};
};
struct SymbolRecord{
    std::string name,nid_name;u64 virtual_address{};
    std::shared_ptr<GuestCpu::HleCallAdapter> hle_adapter;bool hle_fallback{};
};
struct SymbolsResolver {
    std::map<std::string,SymbolRecord> records;
    unsigned registrations{},unsupported_calls{};
    @POLICY_METHODS@
    @POLICY_FIELD@
    static std::string Key(const SymbolResolver& s){
        return s.name+":"+s.library+":"+std::to_string(s.library_version)+":"+
               s.module+":"+std::to_string(static_cast<int>(s.type));
    }
    void Add(const SymbolResolver& s,SymbolRecord record){records[Key(s)]=std::move(record);}
    const SymbolRecord* FindSymbol(const SymbolResolver& s)const{
        const auto it=records.find(Key(s));return it==records.end()?nullptr:&it->second;
    }
    size_t GetSize()const{return records.size();}
    const std::shared_ptr<GuestCpu::HleCallAdapter>& AddUnsupportedFunction(const SymbolResolver& s){
        ++unsupported_calls;
        auto& record=records[Key(s)];
        if(!record.hle_adapter){record.name=s.name;record.hle_fallback=true;
            record.hle_adapter=std::make_shared<GuestCpu::HleCallAdapter>(GuestCpu::HleCallAdapter{999});}
        return record.hle_adapter;
    }
};
}
namespace Devtools::Widget {
struct ModuleList{static void AddModule(const std::string&){}};
}
struct LibraryInfo{
    std::string name="libSceFios2";u16 version=1;
    bool operator==(const LibraryInfo&)const=default;
};
struct ModuleInfo{
    std::string name="libSceFios2";
    bool operator==(const ModuleInfo&)const=default;
};
enum {R_X86_64_RELATIVE=8,R_X86_64_DTPMOD64=16,R_X86_64_GLOB_DAT=6,
      R_X86_64_JUMP_SLOT=7,R_X86_64_64=1,STT_FUN=2,STT_OBJECT=1,STT_NOTYPE=0,
      STB_LOCAL=0,STB_GLOBAL=1,STB_WEAK=2};
struct elf_relocation{
    u64 rel_offset{};s32 rel_addend{};u32 type{},symbol{};
    u32 GetType()const{return type;}u32 GetSymbol()const{return symbol;}
};
struct ElfSymbol{
    u64 st_value{};u32 st_name{},bind=STB_GLOBAL,type=STT_FUN,visibility{};
    u32 GetBind()const{return bind;}u32 GetType()const{return type;}
    u32 GetVisibility()const{return visibility;}
};
struct OrbisProcParam{u64 size=0x18;};
struct Module {
    std::filesystem::path path;
    LibraryInfo library;ModuleInfo module;
    std::vector<LibraryInfo> export_libs;
    std::vector<ModuleInfo> export_modules,import_modules;
    Loader::SymbolsResolver export_sym;
    std::array<u64,4> slots{};
    std::array<ElfSymbol,4> symbols{};
    std::string names;
    std::vector<elf_relocation> relocations;
    std::set<u32> resolved;
    struct {u32 relocation_table_size{};ElfSymbol* symbol_table{};const char* str_table{};}dynamic_info;
    struct {u64 image_size{},modid{};}tls;
    std::function<s32()> start;
    const LibraryInfo* FindLibrary(const std::string& id)const{return id=="L"?&library:nullptr;}
    const ModuleInfo* FindModule(const std::string& id)const{return id=="M"?&module:nullptr;}
    const auto& GetExportLibs()const{return export_libs;}
    const auto& GetExportModules()const{return export_modules;}
    const auto& GetImportModules()const{return import_modules;}
    VAddr GetBaseAddress()const{return reinterpret_cast<VAddr>(slots.data());}
    bool TestRelaBit(u32 bit)const{return resolved.contains(bit);}
    void SetRelaBit(u32 bit){resolved.insert(bit);}
    template<class F>void ForEachRelocation(F&& visit){
        for(u32 i=0;i<relocations.size();++i)visit(&relocations[i],i,false);
    }
    template<class T>T GetProcParam(){return nullptr;}
    s32 Start(u64,const void*,OrbisProcParam*){return start?start():0;}
};
class Linker {
public:
    std::mutex mutex;
    std::vector<std::unique_ptr<Module>> m_modules;
    Loader::SymbolsResolver m_hle_symbols;
    std::unique_ptr<GuestCpu::HleVeneerAllocator> m_hle_veneers;
    std::unique_ptr<Module> next_module;
    std::vector<std::string> load_paths;
    unsigned generation_changes{};
    u32 FindByName(const std::filesystem::path& path){
        for(u32 i=0;i<m_modules.size();++i)if(m_modules[i]->path==path)return i;
        return u32(-1);
    }
    s32 LoadModule(const std::filesystem::path& path,bool){
        load_paths.push_back(path.generic_string());
        if(!next_module)return -1;
        next_module->path=path;m_modules.push_back(std::move(next_module));
        return static_cast<s32>(m_modules.size()-1);
    }
    Module* GetModule(u32 handle){return m_modules.at(handle).get();}
    Loader::SymbolsResolver& GetHLESymbols(){return m_hle_symbols;}
    void AdvanceGenerationCounter(){++generation_changes;}
    @RELOCATE_ANY@
    @RELOCATE_ALL@
    s32 LoadAndStartModule(const std::filesystem::path&,u64,const void*,int*);
    void Relocate(Module*);
    bool Resolve(const std::string&,Loader::SymbolType,Module*,Loader::SymbolRecord*);
};
// The unchanged loader compares its unsigned handle with the -1 sentinel.
// Keep that production body verbatim without suppressing other warnings.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
@LOAD_AND_START@
#pragma GCC diagnostic pop
@RESOLVE@
@RELOCATE@
}
Core::Loader::SymbolResolver Symbol(std::string name,Core::Loader::SymbolType type,
                                   std::string lib="libSceFios2",u16 version=1,
                                   std::string module="libSceFios2") {
    return {std::move(name),"",std::move(lib),version,std::move(module),type};
}
namespace Libraries::Fios2 {
void RegisterLib(Core::Loader::SymbolsResolver* sym){
    ++sym->registrations;
    sym->Add(Symbol("open",Core::Loader::SymbolType::Function),
             {"open","",0x100000,std::make_shared<Core::GuestCpu::HleCallAdapter>(Core::GuestCpu::HleCallAdapter{1}),false});
    sym->Add(Symbol("filter",Core::Loader::SymbolType::Object),{"filter","",0x200000,{},false});
}
}
void RegisterAtBoot(Core::Loader::SymbolsResolver* sym,const std::filesystem::path& game_specific_modules_path){
@REGISTRATION@
}
namespace Libraries::SysModule {
constexpr s32 ORBIS_OK=0;
struct OrbisSysmoduleModuleInternal{s32 handle{},is_loaded{};};
inline std::array<OrbisSysmoduleModuleInternal,4> g_modules_array{};
@LOAD_FIOS_ARM@
}
std::unique_ptr<Core::Module> MainModule(std::string library="libSceFios2"){
    auto m=std::make_unique<Core::Module>();
    m->path="/app0/eboot.bin";m->library.name=library;m->module.name=library;
    m->import_modules.push_back(m->module);
    m->names.push_back('\0');
    const auto add=[&](std::string name){const auto i=static_cast<u32>(m->names.size());m->names+=name;m->names.push_back('\0');return i;};
    m->symbols[1]={0,add("open#L#M"),Core::STB_GLOBAL,Core::STT_FUN,0};
    m->symbols[2]={0,add("filter#L#M"),Core::STB_GLOBAL,Core::STT_OBJECT,0};
    m->symbols[3]={24,0,Core::STB_LOCAL,Core::STT_FUN,0};
    m->relocations={{0,0,Core::R_X86_64_JUMP_SLOT,1},{8,0,Core::R_X86_64_64,2},
                    {16,16,Core::R_X86_64_RELATIVE,0},{24,0,Core::R_X86_64_64,3}};
    m->dynamic_info={static_cast<u32>(m->relocations.size()*sizeof(Core::elf_relocation)),m->symbols.data(),m->names.data()};
    return m;
}
std::unique_ptr<Core::Module> GuestModule(std::string library="libSceFios2",u16 version=1){
    auto m=std::make_unique<Core::Module>();m->library={library,version};m->module.name=library;
    m->export_libs.push_back(m->library);m->export_modules.push_back(m->module);
    m->export_sym.Add(Symbol("open",Core::Loader::SymbolType::Function,library,version,library),{"guest-open","",0x800123000ULL,{},false});
    m->export_sym.Add(Symbol("filter",Core::Loader::SymbolType::Object,library,version,library),{"guest-filter","",0x800456000ULL,{},false});
    return m;
}
void Select(Core::Linker& linker,Common::ElfInfo& game){
    Common::Singleton<Core::Linker>::pointer=&linker;
    Common::Singleton<Common::ElfInfo>::pointer=&game;
    Libraries::SysModule::g_modules_array={};
}
'''

MAIN = r'''
int main(int argc,char** argv){
    assert(argc==2);EmulatorSettings.root=argv[1];
    unsigned cases=0;
    for(const auto serial:{"CUSA00004","CUSA00223","CUSA08809","CUSA08034","CUSA05170","OTHER"}){
        Common::ElfInfo game;game.serial=serial;
        const auto dir=EmulatorSettings.root/serial;std::filesystem::create_directories(dir);
        Core::Linker linker;Select(linker,game);
        assert(linker.m_hle_symbols.Fios2PreferGuestExports());
        RegisterAtBoot(&linker.m_hle_symbols,dir);
        assert(linker.m_hle_symbols.registrations==1);
        auto* main=linker.m_modules.emplace_back(MainModule()).get();
        linker.Relocate(main);
        assert(main->slots[2]==main->GetBaseAddress()+16 && main->TestRelaBit(2));
        assert(main->slots[3]==main->GetBaseAddress()+24 && main->TestRelaBit(3));
#if FIOS_TEST_FEX
        assert(main->slots[0]==0xf0000020 && main->slots[1]==0x200000);
        assert(!main->TestRelaBit(0) && !main->TestRelaBit(1));
        linker.RelocateAllImports();
        assert(!main->TestRelaBit(0) && linker.m_hle_veneers->allocated.size()==1);
        auto guest=GuestModule();guest->tls.image_size=64;
        guest->start=[&]{assert(main->slots[0]==0x800123000ULL && main->slots[1]==0x800456000ULL);return 7;};
        linker.next_module=std::move(guest);int start=-1;
        assert(Libraries::SysModule::loadModuleInternal(3,0,nullptr,&start)==0);
        assert(start==7 && linker.generation_changes==1);
        assert(linker.load_paths==std::vector<std::string>{"/app0/sce_module/libSceFios2.prx"});
        assert(main->TestRelaBit(0) && main->TestRelaBit(1));
        assert(main->slots[0]==0x800123000ULL && main->slots[1]==0x800456000ULL);
        assert(Libraries::SysModule::g_modules_array[3].handle==1);
        linker.RelocateAllImports();assert(main->slots[0]==0x800123000ULL);
#else
        assert(main->slots[0]==0x100000 && main->slots[1]==0x200000);
        assert(main->TestRelaBit(0) && main->TestRelaBit(1));
        linker.m_modules.push_back(GuestModule());linker.RelocateAllImports();
        assert(main->slots[0]==0x100000);
#endif
        ++cases;
    }
#if FIOS_TEST_FEX
    Common::ElfInfo game;const auto dir=EmulatorSettings.root/game.serial;
    // The explicit override wins even if a guest module is already present.
    {std::ofstream(dir/"libSceFios2.use-hle")<<"";
     Core::Linker cp;Select(cp,game);RegisterAtBoot(&cp.m_hle_symbols,dir);
     assert(!cp.m_hle_symbols.Fios2PreferGuestExports());
     auto* main=cp.m_modules.emplace_back(MainModule()).get();cp.m_modules.push_back(GuestModule());
     cp.Relocate(main);assert(main->slots[0]==0xf0000020 && main->TestRelaBit(0));
     int result=-1;assert(Libraries::SysModule::loadModuleInternal(3,0,nullptr,&result)==0);
     assert(cp.load_paths.empty() && result==0);
     std::filesystem::remove(dir/"libSceFios2.use-hle");++cases;}
    // An available staged SPRX wins over the game's PRX; its exports are real.
    {std::ofstream(dir/"libSceFios2.sprx")<<"fixture";
     Core::Linker cp;Select(cp,game);RegisterAtBoot(&cp.m_hle_symbols,dir);
     auto* main=cp.m_modules.emplace_back(MainModule()).get();cp.Relocate(main);
     cp.next_module=GuestModule();int result=-1;
     assert(Libraries::SysModule::loadModuleInternal(3,0,nullptr,&result)==0);
     assert(cp.load_paths==std::vector<std::string>{(dir/"libSceFios2.sprx").generic_string()});
     assert(main->slots[0]==0x800123000ULL && result==0);
     std::filesystem::remove(dir/"libSceFios2.sprx");++cases;}
    // Absent/unloadable guest module keeps the established usable HLE fallback.
    {Core::Linker cp;Select(cp,game);RegisterAtBoot(&cp.m_hle_symbols,dir);
     auto* main=cp.m_modules.emplace_back(MainModule()).get();cp.Relocate(main);
     int result=-1;assert(Libraries::SysModule::loadModuleInternal(3,0,nullptr,&result)==0);
     assert(result==0 && Libraries::SysModule::g_modules_array[3].handle>=90);
     assert(main->slots[0]==0xf0000020 && !main->TestRelaBit(0));++cases;}
    // Export identity includes the imported library version and module.
    {Core::Linker cp;RegisterAtBoot(&cp.m_hle_symbols,dir);
     auto* main=cp.m_modules.emplace_back(MainModule()).get();cp.m_modules.push_back(GuestModule("libSceFios2",2));
     cp.Relocate(main);assert(main->slots[0]==0xf0000020 && main->slots[1]==0x200000 && !main->TestRelaBit(0));
     auto guest=GuestModule();guest->export_modules[0].name="OtherModule";
     cp.m_modules.push_back(std::move(guest));cp.RelocateAllImports();
     assert(main->slots[0]==0xf0000020 && main->slots[1]==0x200000 && !main->TestRelaBit(0));++cases;}
    // A partial guest export table cannot erase the pre-existing HLE record.
    {Core::Linker cp;RegisterAtBoot(&cp.m_hle_symbols,dir);
     auto* main=cp.m_modules.emplace_back(MainModule()).get();
     auto guest=GuestModule();guest->export_sym.records.erase(Core::Loader::SymbolsResolver::Key(Symbol("open",Core::Loader::SymbolType::Function)));
     cp.m_modules.push_back(std::move(guest));cp.Relocate(main);
     assert(main->slots[0]==0xf0000020 && main->slots[1]==0x800456000ULL);
     assert(!main->TestRelaBit(0) && main->TestRelaBit(1));++cases;}
    // Unknown imports remain ENOSYS/unfinished and retain their registered adapter.
    {Core::Linker cp;auto* main=cp.m_modules.emplace_back(MainModule()).get();cp.m_modules.push_back(GuestModule());
     Core::Loader::SymbolRecord first{},second{};
     assert(!cp.Resolve("absent#L#M",Core::Loader::SymbolType::Function,main,&first));
     assert(!cp.Resolve("absent#L#M",Core::Loader::SymbolType::Function,main,&second));
     assert(first.hle_adapter && first.hle_adapter==second.hle_adapter && second.virtual_address==0);++cases;}
    // Non-FIOS libraries keep their original HLE priority and finalized imports.
    {Core::Linker cp;auto* main=cp.m_modules.emplace_back(MainModule("OtherLib")).get();
     cp.m_hle_symbols.Add(Symbol("open",Core::Loader::SymbolType::Function,"OtherLib",1,"OtherLib"),
        {"other-hle","",0xabc,std::make_shared<Core::GuestCpu::HleCallAdapter>(Core::GuestCpu::HleCallAdapter{7}),false});
     cp.m_modules.push_back(GuestModule("OtherLib"));cp.Relocate(main);
     assert(main->slots[0]==0xf00000e0 && main->TestRelaBit(0));++cases;}
    // A valid guest export wins with no registered HLE at all.
    {Core::Linker cp;auto* main=cp.m_modules.emplace_back(MainModule()).get();cp.m_modules.push_back(GuestModule());
     cp.Relocate(main);assert(main->slots[0]==0x800123000ULL && main->TestRelaBit(0));++cases;}
#endif
    std::cout<<"BACHATA_SHARED_IO_FIOS_EXPORTS_PASS cases="<<cases<<" fex="<<FIOS_TEST_FEX<<"\n";
}
'''


def program(source):
    root = source / "src"
    cpp = (root / "core/linker.cpp").read_text()
    h = (root / "core/linker.h").read_text()
    symbols = (root / "core/loader/symbols_resolver.h").read_text()
    libs = (root / "core/libraries/libs.cpp").read_text()
    sysmodule = (root / "core/libraries/sysmodule/sysmodule_internal.cpp").read_text()
    a = libs.index("        // BACHATA_SHARED_IO_FIOS_POLICY:")
    b = libs.index('        LOG_INFO(Lib_Kernel, "BIONIC_BOOT_STAGE=LIBC_HLE_END");', a)
    load = block(sysmodule, "s32 loadModuleInternal(")
    load = load[:load.index("    // Most of the logic the actual module has here")] + "    return -999;\n}"
    replacements = {
        "POLICY_METHODS": block(symbols, "    void SetFios2PreferGuestExports(") + "\n" +
                          block(symbols, "    [[nodiscard]] bool Fios2PreferGuestExports()"),
        "POLICY_FIELD": "    std::atomic_bool m_fios2_prefer_guest_exports{true};",
        "REGISTRATION": libs[a:b],
        # Resolve has alternative #ifdef/#else opening braces; extract the
        # complete method through its next function rather than counting both.
        "RESOLVE": cpp[cpp.index("bool Linker::Resolve("):cpp.index("\nvoid* Linker::TlsGetAddr(")],
        "RELOCATE": block(cpp, "void Linker::Relocate("),
        "RELOCATE_ANY": block(h, "    void RelocateAnyImports("),
        "RELOCATE_ALL": block(h, "    void RelocateAllImports("),
        "LOAD_AND_START": block(cpp, "s32 Linker::LoadAndStartModule("),
        "LOAD_FIOS_ARM": load,
    }
    assert symbols.count(replacements["POLICY_FIELD"]) == 1
    text = PREAMBLE + MAIN
    for key, value in replacements.items():
        text = text.replace("@" + key + "@", value)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    text = program(args.source)
    mutations = {
        "hle_shadows_guest": (" && !prefer_guest_fios2) {", ") {"),
        "provisional_sealed": ("*return_info = *hle_record;\n        return false;", "*return_info = *hle_record;\n        return true;"),
        "drop_provisional_adapter": ("*return_info = *hle_record;\n        return false;", "*return_info = {};\n        return false;"),
        "ignore_use_hle": ("SetFios2PreferGuestExports(!fios_force_hle)", "SetFios2PreferGuestExports(true)"),
        "all_libraries_guest_first": ('sr.library == "libSceFios2" &&', 'true &&'),
        "skip_dynamic_relocation": ("    RelocateAnyImports(module);", "    (void)module;"),
        "erase_hle_on_guest_miss": ("if (prefer_guest_fios2 && hle_record != nullptr && !hle_record->hle_fallback)", "if (prefer_guest_fios2 && m_modules.size()==1 && hle_record != nullptr && !hle_record->hle_fallback)"),
    }
    compiler = os.environ.get("CXX", "c++")
    with tempfile.TemporaryDirectory(prefix="bachata-shared-fios-") as directory:
        temp = Path(directory)
        def run(name, code, *, fex=1, negative=False):
            path = temp / (name + ".cpp")
            exe = temp / name
            state = temp / (name + "-state")
            state.mkdir()
            path.write_text(code)
            build = subprocess.run([compiler, "-std=c++23", "-O1", "-g", "-pthread", "-Wall", "-Wextra",
                                    "-Werror", "-Wunused-const-variable", "-Wno-implicit-fallthrough",
                                    "-fsanitize=undefined", "-fno-sanitize-recover=all",
                                    "-DFIOS_TEST_FEX=" + str(fex), str(path), "-o", str(exe)],
                                   text=True, capture_output=True)
            assert build.returncode == 0, name + " must compile before runtime validation:\n" + build.stderr
            result = subprocess.run([str(exe), str(state)], text=True, capture_output=True, timeout=15)
            if negative:
                assert result.returncode != 0, name + " negative unexpectedly passed"
                assert "Assertion" in result.stderr or "runtime error" in result.stderr, result.stderr
                print("NEGATIVE_REJECTED", name)
            else:
                assert result.returncode == 0, (name, result.stdout, result.stderr)
                print(result.stdout, end="")
        run("fex", text)
        run("desktop", text, fex=0)
        for name, (old, new) in mutations.items():
            assert text.count(old) == 1, (name, text.count(old))
            run(name, text.replace(old, new, 1), negative=True)
    print("BACHATA_SHARED_IO_FIOS_EXPORTS_SUITE_PASS negatives=" + str(len(mutations)))


if __name__ == "__main__":
    main()
