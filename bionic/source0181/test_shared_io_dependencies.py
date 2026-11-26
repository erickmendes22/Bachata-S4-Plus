#!/usr/bin/env python3
"""Exercise generated resolver/relocation, guest object and C++ ABI methods.

ELF bytes, VMA allocation, native HLE registration and FEX execution are controlled
boundaries. Selection, rebind, object publication, table mutation and callback
dispatch are extracted from the actual source, not reimplemented in this gate.
"""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

from test_shared_io_fios_exports import block, program as resolver_program


SUPPORT = r'''
using u8=uint8_t;using s16=int16_t;using s64=int64_t;
#define PS4_SYSV_ABI
[[maybe_unused]] constexpr int Lib_DiscMap=4,Lib_LibcInternal=5,Loader=6;
std::atomic<unsigned> bind_logs{},sdk_logs{},disc_logs{},cxa_logs{},bridge_calls{};
template<class... T>void Evidence(int category,const char* format,const T&... values){
    Consume(category,values...);const std::string_view f=format;
    if(f.starts_with("BACHATA_SHARED_IO_LIBC_BIND "))++bind_logs;
    if(f.starts_with("BACHATA_SHARED_IO_LIBC_SDK_OBJECT "))++sdk_logs;
    if(f.starts_with("BACHATA_SHARED_IO_DISC_MAP "))++disc_logs;
    if(f.starts_with("BACHATA_SHARED_IO_CXA_FINALIZE "))++cxa_logs;
}
#undef LOG_INFO
#define LOG_INFO(...) Evidence(__VA_ARGS__)
#define LOG_TRACE(...) Consume(__VA_ARGS__)
#define LOG_CRITICAL(...) Consume(__VA_ARGS__)
namespace fmt {template<class T>T ptr(T pointer){return pointer;}}
'''

BOUNDARIES = r'''
namespace Core::KernelFixture {using PthreadMutexT=void*;}
namespace Libraries::Kernel {using PthreadMutexT=Core::KernelFixture::PthreadMutexT;}
namespace Core {
enum class MemoryProt{CpuReadWrite};enum class MemoryMapFlags{NoFlags};enum class VMAType{Flexible};
struct MemoryFixture {
    std::vector<std::pair<void*,size_t>> mappings;
    int failure{};unsigned calls{};bool invalid_span{};
    ~MemoryFixture(){for(auto [p,n]:mappings)assert(munmap(p,n)==0);}
    int MapMemory(void** out,u64,size_t bytes,MemoryProt prot,MemoryMapFlags flags,VMAType type,std::string_view name){
        ++calls;assert(bytes==0x4000 && prot==MemoryProt::CpuReadWrite &&
                       flags==MemoryMapFlags::NoFlags && type==VMAType::Flexible && name=="BachataFexLibcObjects");
        if(failure){*out=nullptr;return failure==1?-12:0;}
        *out=mmap(nullptr,bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        assert(*out!=MAP_FAILED);mappings.emplace_back(*out,bytes);return 0;
    }
    u64 ClampGpuRangeSize(VAddr address,u64 size)const{
        if(invalid_span)return 0;
        for(auto [p,n]:mappings){const auto begin=reinterpret_cast<VAddr>(p);
            if(address>=begin && address-begin<n && size<=n-(address-begin))return size;}
        return 0;
    }
};
struct Memory {inline static MemoryFixture* instance{};static auto* Instance(){assert(instance);return instance;}};
}
// The table boundaries preserve typed symbol registration and strong HLE status.
// The generated LIB_OBJ macro below is used without modification.
@LIB_OBJ@
#define LIB_FUNCTION(nid,lib,version,mod,function) \
    sym->Add(Symbol(nid,Core::Loader::SymbolType::Function,lib,version,mod), \
             {nid,"",reinterpret_cast<u64>(&function), \
              std::make_shared<Core::GuestCpu::HleCallAdapter>(Core::GuestCpu::HleCallAdapter{77}),false})
namespace Libraries::LibcInternal {
@ORBIS_FILE@
@GUEST_OBJECTS@
}
void BootObjects(Core::Linker* linker,Core::MemoryFixture* memory){
    Core::Memory::instance=memory;
#if FIOS_TEST_FEX
@BOOT_OBJECTS@
#else
    Consume(linker,memory);
#endif
}
struct CallbackPayload{std::function<void()> action;};
void GuestDestructor(void* pointer){
#if FIOS_TEST_FEX
    Consume(pointer);assert(false && "guest address was called natively");
#else
    static_cast<CallbackPayload*>(pointer)->action();
#endif
}
namespace Core::GuestCpu {
// Execution remains a controlled FEX boundary; the actual production bridge
// argument encoder and RunGuestFunctionOrAbort body are compiled below.
@CALLBACK_ENCODER@
@CALLBACK_RUN@
@CALLBACK_TEMPLATE@
}
Core::Linker::GuestFunctionResult Core::Linker::RunGuestFunction(VAddr address,std::span<const u64> args,VAddr stack){
    assert(address==reinterpret_cast<VAddr>(&GuestDestructor));
    assert(args.size()==1 && stack==0);++bridge_calls;
    reinterpret_cast<CallbackPayload*>(args[0])->action();return u64(0);
}
namespace Libraries::LibcInternal {
@CXA_BODY@
}
namespace Libraries::DiscMap {
[[maybe_unused]] constexpr int ORBIS_OK=0;
@DISC_MAP_ERROR@
@DISC_MAP@
}
'''


TESTS = r'''
using Core::Loader::SymbolType;
constexpr const char* Internal="libSceLibcInternal";
constexpr std::array<const char*,4> Calendar{"1mecP7RgI2A","5bBacGLyLOs","efhK-YSUYYQ","n7AepwR0s34"};
std::unique_ptr<Core::Module> Import(std::string nid,std::string library=Internal,std::string module=Internal,SymbolType type=SymbolType::Function){
    auto m=MainModule(library);m->module.name=module;m->import_modules={m->module};
    m->path="/app0/sce_module/libSceFios2.prx";
    m->names="\0"s+nid+"#L#M"+"\0"s;
    m->symbols[1]={0,1,Core::STB_GLOBAL,type==SymbolType::Object?Core::STT_OBJECT:Core::STT_FUN,0};
    m->relocations.resize(1);m->dynamic_info.str_table=m->names.data();
    m->dynamic_info.relocation_table_size=sizeof(Core::elf_relocation);return m;
}
std::unique_ptr<Core::Module> Export(const char* nid,VAddr address=0x800123000ULL,
                                  std::string library="libc",u16 version=2,std::string module="libc",
                                  SymbolType type=SymbolType::Function){
    auto m=GuestModule(library,version);m->module.name=module;m->export_modules={m->module};
    m->export_sym.records.clear();m->export_sym.Add(Symbol(nid,type,library,version,module),{nid,"",address,{},false});return m;
}
bool Resolve(Core::Linker& cp,Core::Module* importer,const char* nid,Core::Loader::SymbolRecord& out,SymbolType type=SymbolType::Function){
    return cp.Resolve(std::string(nid)+"#L#M",type,importer,&out);
}
unsigned ResolverCases(){
    unsigned cases=0;
    for(auto nid:Calendar){
        Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(nid)).get();
        cp.m_modules.push_back(Export(nid,0x800123000ULL,"libc",4,"VendorLibc"));
        Core::Loader::SymbolRecord r{};const auto before=bind_logs.load();
#if FIOS_TEST_FEX
        assert(Resolve(cp,m,nid,r));assert(r.virtual_address==0x800123000ULL && !r.hle_adapter);
        assert(bind_logs==before+1);
        // A returned record is a value; registry retirement cannot mutate it.
        cp.m_modules.back()->export_sym.records.clear();assert(r.name==nid && r.virtual_address==0x800123000ULL);
#else
        assert(!Resolve(cp,m,nid,r));assert(r.virtual_address!=0x800123000ULL && bind_logs==before);
#endif
        ++cases;
    }
#if FIOS_TEST_FEX
    // Unknown imports and an absent/ambiguous libc stay on the pre-existing
    // provisional ENOSYS adapter; neither namespace nor symbol type is guessed.
    for(int condition=0;condition<9;++condition){
        Core::Linker cp;auto import=Import(Calendar[0]);
        if(condition==0)import->library.name="OtherLib";
        if(condition==1)import->module.name="OtherModule";
        auto* m=cp.m_modules.emplace_back(std::move(import)).get();
        auto target=Export(Calendar[0]);
        if(condition==2)target->export_libs[0].name="OtherLib";
        if(condition==3)target->export_sym.records.clear();
        if(condition==4)target=Export(Calendar[0],0);
        if(condition==5)target=Export(Calendar[0],0x800123000,"libc",2,"libc",SymbolType::Object);
        if(condition==6)target->export_sym.records.begin()->second.hle_adapter=std::make_shared<Core::GuestCpu::HleCallAdapter>();
        cp.m_modules.push_back(std::move(target));
        if(condition==7)cp.m_modules.push_back(Export(Calendar[0],0x800456000));
        if(condition==8)cp.m_modules.push_back(Export(Calendar[0],0x800123000,"libc",3));
        Core::Loader::SymbolRecord r{};const auto before=bind_logs.load();
        assert(!Resolve(cp,m,Calendar[0],r));assert(r.hle_adapter && r.virtual_address==0 && bind_logs==before);++cases;
    }
    {Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(Calendar[0])).get();auto target=Export(Calendar[0]);
     target->export_libs.push_back(target->export_libs[0]);target->export_modules.push_back(target->export_modules[0]);
     cp.m_modules.push_back(std::move(target));Core::Loader::SymbolRecord r{};
     assert(Resolve(cp,m,Calendar[0],r) && r.virtual_address==0x800123000);++cases;}
    {Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(Calendar[0])).get();
     cp.m_modules.push_back(Export(Calendar[0]));cp.m_modules.push_back(Export(Calendar[0],0x900321000,Internal,1,Internal));
     Core::Loader::SymbolRecord r{};const auto before=bind_logs.load();
     assert(Resolve(cp,m,Calendar[0],r) && r.virtual_address==0x900321000 && bind_logs==before);++cases;}
    // Allocator/stdio/cxa families remain excluded even if no strong HLE exists.
    for(const auto* nid:{"gQX+4GDQjpM","tIhsqj0qsFE","Y7aJ1uydPMo","2X5agFjKxMc",
                        "Ujf3KzMvRmI","cVSk9y8URbc","NDcSfcYZRC8","fJnpuVVBbKk",
                        "hdm0YfMa7TQ","lYDzBVE5mZs","FOt55ZNaVJk","-hn1tcVHq5Q",
                        "W6SiVSiCDtI","OJjm-QOIHlI","Vla-Z+eXlxo","LYo3GhIlB38",
                        "gigoVHZvVPE","iF1iQHzxBJU","fEoW6BJsPt4","jVDuvE3s5Bs",
                        "xeYO4u7uyJ0","uodLYyUip20","tsvEmnenz48","H2e8t5ScQGc","unknown"}){
        for(bool strong:{false,true}){
            Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(nid)).get();cp.m_modules.push_back(Export(nid));
            if(strong)cp.m_hle_symbols.Add(Symbol(nid,SymbolType::Function,Internal,1,Internal),
                {nid,"",0x111,std::make_shared<Core::GuestCpu::HleCallAdapter>(Core::GuestCpu::HleCallAdapter{17}),false});
            Core::Loader::SymbolRecord r{};const auto before=bind_logs.load();
            assert(Resolve(cp,m,nid,r)==strong && r.hle_adapter && bind_logs==before);
            assert(r.virtual_address==(strong?0x111:0));++cases;
        }
    }
    // A real strong implementation of an allowed NID still wins.
    {Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(Calendar[0])).get();cp.m_modules.push_back(Export(Calendar[0]));
     cp.m_hle_symbols.Add(Symbol(Calendar[0],SymbolType::Function,Internal,1,Internal),
         {"strong","",0x432,std::make_shared<Core::GuestCpu::HleCallAdapter>(),false});
     Core::Loader::SymbolRecord r{};assert(Resolve(cp,m,Calendar[0],r)&&r.virtual_address==0x432);++cases;}
    // Late libc publication must revisit Internal imports before module Start.
    {Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(Calendar[0])).get();cp.Relocate(m);
     assert(!m->TestRelaBit(0) && m->slots[0]!=0);
     auto late=Export(Calendar[0]);late->start=[&]{assert(m->TestRelaBit(0)&&m->slots[0]==0x800123000);return 17;};
     cp.next_module=std::move(late);int result=-1;
     assert(cp.LoadAndStartModule("/app0/sce_module/libc.prx",0,nullptr,&result)==1 && result==17);
     cp.RelocateAllImports();assert(m->slots[0]==0x800123000);++cases;}
    // The fallback accepts functions only, never an object of the same NID.
    {Core::Linker cp;auto* m=cp.m_modules.emplace_back(Import(Calendar[0],Internal,Internal,SymbolType::Object)).get();
     cp.m_modules.push_back(Export(Calendar[0],0x800123000,"libc",2,"libc",SymbolType::Object));
     Core::Loader::SymbolRecord r{};assert(!Resolve(cp,m,Calendar[0],r,SymbolType::Object)&&r.virtual_address==0);++cases;}
    // Explicit FIOS override remains independent of these libc dependencies.
    {Core::Linker cp;cp.m_hle_symbols.SetFios2PreferGuestExports(false);Libraries::Fios2::RegisterLib(&cp.m_hle_symbols);
     auto* m=cp.m_modules.emplace_back(MainModule()).get();cp.m_modules.push_back(GuestModule());
     cp.Relocate(m);assert(m->TestRelaBit(0)&&m->slots[0]==0xf0000020);++cases;}
#endif
    return cases;
}
unsigned ObjectCases(){
    unsigned cases=0;
    for(int failure=0;failure<4;++failure){
        Core::MemoryFixture memory;memory.failure=failure==3?1:failure;
        Core::Linker cp;
        u32 host_marker=1;
        if(failure==3)cp.m_hle_symbols.AddSymbol(Symbol("P330P3dFF68",SymbolType::Object,"libc",1,"libc"),reinterpret_cast<VAddr>(&host_marker));
        const auto before=sdk_logs.load();BootObjects(&cp,&memory);
        const auto* object=cp.m_hle_symbols.FindSymbol(Symbol("ZT4ODD2Ts9o",SymbolType::Object,Internal,1,Internal));
#if FIOS_TEST_FEX
        assert(memory.calls==1);
        if(failure==0){
            assert(object && !object->hle_adapter && memory.ClampGpuRangeSize(object->virtual_address,4)==4);
            const auto* original=cp.m_hle_symbols.FindSymbol(Symbol("P330P3dFF68",SymbolType::Object,"libc",1,"libc"));
            assert(original && original->virtual_address==object->virtual_address);
            const VAddr address=object->virtual_address;
            assert(*reinterpret_cast<u32*>(address)==1 && sdk_logs==before+1);
            auto* m=cp.m_modules.emplace_back(Import("ZT4ODD2Ts9o",Internal,Internal,SymbolType::Object)).get();
            cp.Relocate(m);assert(m->TestRelaBit(0)&&m->slots[0]==address);
            for(int i=0;i<1024;++i)cp.m_hle_symbols.AddSymbol(Symbol("growth"+std::to_string(i),SymbolType::Object),i+1);
            cp.m_hle_symbols.records.clear();assert(*reinterpret_cast<u32*>(address)==1);
        }else assert(!object && sdk_logs==before);
#else
        assert(memory.calls==0 && !object && sdk_logs==before);
#endif
        ++cases;
    }
    return cases;
}
unsigned FinalizeCases(){
    using namespace Libraries::LibcInternal;unsigned cases=0;
    Core::Linker bridge_context;Common::Singleton<Core::Linker>::pointer=&bridge_context;
    assert(AtexitEntries.empty());assert(fex_libc_cxa_atexit(nullptr,nullptr,nullptr)!=0);
    int da{},db{};std::vector<int> seen;std::array<unsigned,3> first_calls{};
    CallbackPayload a{[&]{assert(first_calls[0]++==0);seen.push_back(1);}},
                    b{[&]{assert(first_calls[1]++==0);seen.push_back(2);}},
                    c{[&]{assert(first_calls[2]++==0);seen.push_back(3);}};
    assert(fex_libc_cxa_atexit(GuestDestructor,&a,&da)==0);
    assert(fex_libc_cxa_atexit(GuestDestructor,&b,&db)==0);
    assert(fex_libc_cxa_atexit(GuestDestructor,&c,&da)==0);
    fex_libc_cxa_finalize(&da);assert((seen==std::vector<int>{3,1})&&AtexitEntries.size()==1);
    fex_libc_cxa_finalize(&da);assert(seen.size()==2);
    fex_libc_cxa_finalize(nullptr);assert((seen==std::vector<int>{3,1,2})&&AtexitEntries.empty());++cases;
    // A callback can grow/reallocate the vector, register on another thread,
    // and recursively finalize the same DSO without retaining an entry reference.
    seen.clear();std::array<CallbackPayload,128> added;
    for(size_t i=0;i<added.size();++i)added[i].action=[&,i]{seen.push_back(100+static_cast<int>(i));};
    CallbackPayload tail{[&]{seen.push_back(1);}};
    CallbackPayload recursive{[&]{seen.push_back(2);
        std::thread registration([&]{for(auto& item:added)assert(fex_libc_cxa_atexit(GuestDestructor,&item,&da)==0);});registration.join();
        fex_libc_cxa_finalize(&da);seen.push_back(9);}};
    fex_libc_cxa_atexit(GuestDestructor,&tail,&da);fex_libc_cxa_atexit(GuestDestructor,&recursive,&da);
    fex_libc_cxa_finalize(&da);
    assert(seen.size()==131&&seen.front()==2&&seen[1]==227&&seen[128]==100&&seen[129]==1&&seen.back()==9&&AtexitEntries.empty());++cases;
    // A second thread may make progress while the first callback is running.
    std::mutex m;std::condition_variable cv;bool entered=false,other_done=false;
    CallbackPayload older{[&]{std::lock_guard lock{m};other_done=true;cv.notify_all();}};
    CallbackPayload blocking{[&]{std::unique_lock lock{m};entered=true;cv.notify_all();
        assert(cv.wait_for(lock,std::chrono::seconds(2),[&]{return other_done;}));}};
    fex_libc_cxa_atexit(GuestDestructor,&older,&da);fex_libc_cxa_atexit(GuestDestructor,&blocking,&da);
    std::thread first([&]{fex_libc_cxa_finalize(&da);});
    {std::unique_lock lock{m};assert(cv.wait_for(lock,std::chrono::seconds(2),[&]{return entered;}));}
    fex_libc_cxa_finalize(&da);first.join();assert(AtexitEntries.empty());++cases;
    std::array<std::atomic<unsigned>,256> called{};std::array<CallbackPayload,256> concurrent;
    for(size_t i=0;i<concurrent.size();++i){concurrent[i].action=[&,i]{assert(called[i].fetch_add(1)==0);};
        assert(fex_libc_cxa_atexit(GuestDestructor,&concurrent[i],i%2?&da:&db)==0);}
    std::barrier begin(8);std::vector<std::thread> finishers;
    for(int i=0;i<8;++i)finishers.emplace_back([&]{begin.arrive_and_wait();fex_libc_cxa_finalize(nullptr);});
    for(auto& worker:finishers){worker.join();}
    for(auto& n:called){assert(n==1);}
    assert(AtexitEntries.empty());++cases;
    CallbackPayload null_dso{[&]{seen.push_back(17);}};const auto old=seen.size();
    fex_libc_cxa_atexit(GuestDestructor,&null_dso,nullptr);fex_libc_cxa_finalize(&da);assert(seen.size()==old);
    fex_libc_cxa_finalize(nullptr);assert(seen.size()==old+1);++cases;
    // Actual registration binds both runtime namespaces to the same owner.
    Core::Linker cp;RegisterFexLibcCxaAliases(&cp.m_hle_symbols);
    for(const auto* name:{Internal,"libc"}){
        auto* importer=cp.m_modules.emplace_back(Import("H2e8t5ScQGc",name,name)).get();
        cp.m_modules.push_back(Export("H2e8t5ScQGc"));Core::Loader::SymbolRecord r{};
        assert(Resolve(cp,importer,"H2e8t5ScQGc",r)&&r.hle_adapter&&r.virtual_address==reinterpret_cast<u64>(&fex_libc_cxa_finalize));++cases;
    }
#if FIOS_TEST_FEX
    assert(bridge_calls==3+130+2+256+1);
#else
    assert(bridge_calls==0);
#endif
    assert(cxa_logs==1);return cases;
}
unsigned DiscCases(){
    using namespace Libraries::DiscMap;int flags=7,a=8,b=9;
    Consume(ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO);
    const int result=Func_7C980FFB0AA27E7A(nullptr,0,1,&flags,&a,&b);
#if FIOS_TEST_FEX
    assert(result==static_cast<s32>(0x81100004)&&flags==7&&a==8&&b==9);
    assert(Func_7C980FFB0AA27E7A(nullptr,-1,-1,nullptr,nullptr,nullptr)==result);
    assert(disc_logs==1);return 2;
#else
    assert(result==0&&flags==0&&a==0&&b==0&&disc_logs==0);return 1;
#endif
}
int main(){const auto cases=ResolverCases()+ObjectCases()+FinalizeCases()+DiscCases();
    std::cout<<"BACHATA_SHARED_IO_DEPENDENCIES_PASS cases="<<cases<<" fex="<<FIOS_TEST_FEX<<" bridges="<<bridge_calls<<"\n";}
'''


def program(source, generic):
    base = resolver_program(source).split("\nint main(", 1)[0]
    base = base.replace("#include <algorithm>", "#include <algorithm>\n#include <barrier>\n#include <chrono>\n#include <condition_variable>\n#include <thread>\n#include <unordered_map>\n#include <sys/mman.h>")
    # Evidence macros must precede the generated resolver definitions.
    pos = base.index("namespace Common {")
    base = base[:pos] + SUPPORT + base[pos:]
    base = base.replace("using VAddr=u64;", "using VAddr=u64;\nusing namespace std::string_literals;")
    base = base.replace("    size_t GetSize()const", "    void AddSymbol(const SymbolResolver& s,u64 address){Add(s,{s.name,\"\",address,{},false});}\n    size_t GetSize()const", 1)
    base = base.replace("    std::mutex mutex;", "    struct GuestExecutionFailure {int Stage{};std::string Error;};\n    using GuestFunctionResult=std::variant<u64,GuestExecutionFailure>;\n    GuestFunctionResult RunGuestFunction(VAddr,std::span<const u64>,VAddr);\n    std::mutex mutex;", 1)
    src = source / "src"
    libs = (src / "core/libraries/libs.h").read_text()
    lib_obj = libs[libs.index("#define LIB_OBJ("):libs.index("\nnamespace Libraries {")]
    io_h = (src / "core/libraries/libc_internal/libc_internal_io.h").read_text()
    io_types = io_h[io_h.index("union Orbis__mbstate_t {"):io_h.index("\ns32 PS4_SYSV_ABI internal_snprintf")]
    guest_objects = block(generic.read_text(), "void RegisterFexLibcGuestObjects(")
    boot = (src / "emulator.cpp").read_text()
    init = boot.index("    Libraries::InitHLELibs(&linker->GetHLESymbols());")
    a = boot.index("    Libraries::LibcInternal::RegisterFexLibcGuestObjects(", init)
    b = boot.index('    LOG_INFO(Loader, "BIONIC_BOOT_STAGE=GUEST_LIBC_OBJECTS_END");', a)
    assert init < a < b < boot.index("if (linker->LoadModule(eboot_path)", b)
    cxa = (src / "core/libraries/libc_internal/libc_internal_cxa.cpp").read_text()
    cxa_body = cxa[cxa.index("namespace Libraries::LibcInternal {")+len("namespace Libraries::LibcInternal {"):cxa.rindex("} // namespace Libraries::LibcInternal")]
    cxa_header = (src / "core/libraries/libc_internal/libc_internal_cxa.h").read_text()
    assert "void PS4_SYSV_ABI fex_libc_cxa_finalize(void* dso_handle);" in cxa_header
    callback = (src / "core/guest_cpu/guest_callback.h").read_text()
    # The fixture's Linker preserves the real result type under a local alias.
    callback_run = block(callback, "inline u64 RunGuestFunctionOrAbort(").replace("std::get_if<GuestExecutionFailure>", "std::get_if<Linker::GuestExecutionFailure>")
    callback_encoder = callback[callback.index("template <typename T>"):callback.index("inline bool IsGuestFunctionAddress")]
    disc = (src / "core/libraries/disc_map/disc_map.cpp").read_text()
    codes = (src / "core/libraries/disc_map/disc_map_codes.h").read_text()
    error = next(line for line in codes.splitlines() if "ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO" in line)
    replacements = {
        "LIB_OBJ": lib_obj, "ORBIS_FILE": io_types, "GUEST_OBJECTS": guest_objects,
        "BOOT_OBJECTS": boot[a:b], "CXA_BODY": cxa_body,
        "CALLBACK_ENCODER": callback_encoder,
        "CALLBACK_RUN": callback_run,
        "CALLBACK_TEMPLATE": block(callback, "template <typename... Args>"),
        "DISC_MAP_ERROR": error,
        "DISC_MAP": block(disc, "int PS4_SYSV_ABI Func_7C980FFB0AA27E7A("),
    }
    text = base + BOUNDARIES + TESTS
    for key, value in replacements.items():
        text = text.replace("@" + key + "@", value)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--generic", type=Path, default=Path(__file__).resolve().parents[1] / "generic/android_libc_compat.cpp")
    args = parser.parse_args()
    text = program(args.source, args.generic)
    mutations = {
        "calendar_alias_absent": ('sr.type == Loader::SymbolType::Function && shared_io_libc_nid)', 'sr.type == Loader::SymbolType::Function && shared_io_libc_nid && false)'),
        "alias_ambiguity": ('if (libc_record && !ambiguous) {', 'if (libc_record && (!ambiguous || libc_record)) {'),
        "alias_namespace": ('sr.library == "libSceLibcInternal" && sr.module == "libSceLibcInternal" &&', 'true &&'),
        "alias_all_nids": ('sr.type == Loader::SymbolType::Function && shared_io_libc_nid)', 'sr.type == Loader::SymbolType::Function && (shared_io_libc_nid || !sr.name.empty()))'),
        "alias_object_type": ('sr.type == Loader::SymbolType::Function && shared_io_libc_nid)', '(sr.type == Loader::SymbolType::Function || sr.type == Loader::SymbolType::Object) && shared_io_libc_nid)'),
        "alias_overrides_strong_hle": ('!hle_record->hle_fallback && !prefer_guest_fios2)', '!hle_record->hle_fallback && !prefer_guest_fios2 && sr.library != "libSceLibcInternal")'),
        "no_late_rebind": ('|| (exports_libc &&', '|| (exports_libc && false &&'),
        "sdk_host_address": ('symbols.AddSymbol(marker, address);', 'static u32 host_data=1; symbols.AddSymbol(marker, reinterpret_cast<VAddr>(&host_data));'),
        "sdk_unmapped": ('if (memory->ClampGpuRangeSize(address, sizeof(u32)) == sizeof(u32)) {', 'if (memory->ClampGpuRangeSize(address, sizeof(u32)) <= sizeof(u32)) {'),
        "sdk_wrong_value": ('*need = 1;', '*need = 0;'),
        "cxa_dso_filter": ('if (dso_handle && AtexitEntries[i - 1].dso_handle != dso_handle) continue;', '(void)dso_handle;'),
        "cxa_forward_order": ('for (std::size_t i = AtexitEntries.size(); i != 0; --i)', 'for (std::size_t i = 1; i <= AtexitEntries.size(); ++i)'),
        "cxa_drop_others": ('AtexitEntries.erase(AtexitEntries.begin() + (i - 1));', 'AtexitEntries.clear();'),
        "cxa_duplicate_callback": ('AtexitEntries.erase(AtexitEntries.begin() + (i - 1));', '(void)AtexitEntries;'),
        "cxa_native_guest_call": ('static_cast<void>(Core::GuestCpu::RunGuestFunctionOrAbort(\n            reinterpret_cast<const void*>(entry.func), "__cxa_finalize", entry.arg));', 'entry.func(entry.arg);'),
        "disc_false_success": ('return ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO;\n#else', 'return ORBIS_OK;\n#else'),
        "disc_write_outputs": ('return ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO;\n#else', '*flags=0; *ret1=0; *ret2=0; return ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO;\n#else'),
    }
    compiler = os.environ.get("CXX", "c++")
    with tempfile.TemporaryDirectory(prefix="bachata-shared-dependencies-") as directory:
        temp = Path(directory)
        def run(name, code, *, fex=1, negative=False):
            path, binary = temp / (name + ".cpp"), temp / name
            path.write_text(code)
            build = subprocess.run([compiler, "-std=c++23", "-O1", "-g", "-pthread", "-Wall", "-Wextra", "-Werror",
                                    "-Wunused-const-variable", "-Wno-implicit-fallthrough", "-Wno-unused-parameter",
                                    "-fsanitize=undefined", "-fno-sanitize-recover=all", "-DFIOS_TEST_FEX=" + str(fex),
                                    str(path), "-o", str(binary)], text=True, capture_output=True)
            assert build.returncode == 0, name + " must compile before runtime validation:\n" + build.stderr
            result = subprocess.run([str(binary)], text=True, capture_output=True, timeout=12)
            if negative:
                assert result.returncode != 0, name + " negative unexpectedly passed"
                assert "Assertion" in result.stderr or "runtime error" in result.stderr, result.stderr
                print("NEGATIVE_REJECTED", name, flush=True)
            else:
                assert result.returncode == 0, (name, result.stdout, result.stderr)
                print(result.stdout, end="", flush=True)
        run("fex", text)
        run("desktop", text, fex=0)
        for name, (old, new) in mutations.items():
            assert text.count(old) == 1, (name, text.count(old))
            run(name, text.replace(old, new, 1), negative=True)
    print("BACHATA_SHARED_IO_DEPENDENCIES_SUITE_PASS negatives=" + str(len(mutations)))


if __name__ == "__main__":
    main()
