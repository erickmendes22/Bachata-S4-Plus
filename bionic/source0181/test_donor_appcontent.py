"""Compile the actual AppContent and Sysmodule lifecycle methods, using real filesystem space."""
from pathlib import Path
import argparse
import subprocess
import tempfile

parser=argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
root=parser.parse_args().source.resolve()/'src'
app=(root/'core/libraries/app_content/app_content.cpp').read_text()
sys=(root/'core/libraries/sysmodule/sysmodule_internal.cpp').read_text()
app=app[app.index('namespace Libraries::AppContent {'):app.index('void RegisterLib(Core::Loader::SymbolsResolver* sym)')]+ '\n}\n'
load=sys[sys.index('s32 loadModule(s32 id,'):sys.index('s32 preloadModulesForLibkernel()')]
fixture=r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <string_view>
#include <vector>
#include "core/libraries/app_content/app_content.h"
#include "core/libraries/app_content/app_content_error.h"
#include "core/libraries/playgo/bachata_installed_package.h"
#include "core/libraries/sysmodule/sysmodule_table.h"
#include "core/libraries/sysmodule/sysmodule_error.h"
#define LOG_ERROR(...) ((void)0)
#define LOG_INFO(...) ((void)0)
#define LOG_WARNING(...) ((void)0)
#define UNREACHABLE_MSG(...) std::abort()
namespace fs=std::filesystem;
static fs::path test_root;
namespace Common {
struct ElfInfo {static constexpr int FW_150=0x150;std::string serial;
    static ElfInfo& Instance(){static ElfInfo a;return a;}
    std::string_view GameSerial()const{return serial;}};
template<class T>struct Singleton{static T* Instance(){static T a;return &a;}};
namespace FS {enum class FileAccessMode {Read};enum class PathType {LicensesDir};
const fs::path& GetUserPath(PathType){static const auto dir=test_root/"licenses";return dir;}}
}
namespace fmt {std::string format(const char*,const char* mount){return std::string(mount)+"/sce_sys/param.sfo";}}
namespace Core::FileSys {
struct IFile {fs::path path;};
struct IBackend {fs::path root;
    std::shared_ptr<IFile> Open(std::string_view path,Common::FS::FileAccessMode){auto p=root/path;return fs::exists(p)?std::make_shared<IFile>(IFile{p}):nullptr;}};
struct MntPoints {
    std::map<std::string,fs::path> mounts;
    std::filesystem::path GetHostPath(std::string_view name){auto i=mounts.find(std::string(name));return i==mounts.end()?fs::path{}:i->second;}
    void Mount(fs::path path,std::string name,bool){mounts[name]=path;}
    void Unmount(std::string name){mounts.erase(name);}
    std::shared_ptr<IFile> Open(std::string_view name,bool){
        for(auto& [guest,host]:mounts)if(name.starts_with(guest+"/")){
            auto path=host/std::string(name.substr(guest.size()+1));
            if(fs::exists(path))return std::make_shared<IFile>(IFile{path});}
        return nullptr;
    }
    std::shared_ptr<IBackend> CreateBackend(fs::path path,bool){return std::make_shared<IBackend>(IBackend{path});}
};}
struct {fs::path GetAddonInstallDir()const{return test_root/"addons";}bool IsDevKit()const{return false;}} EmulatorSettings;
struct PSF {
    std::map<std::string,std::string> values;
    std::optional<std::string_view> GetString(std::string key){auto i=values.find(key);if(i==values.end())return {};return i->second;}
    std::optional<s32> GetInteger(std::string key){auto i=values.find(key);if(i==values.end())return {};return std::stoi(i->second);}
    bool Open(const std::shared_ptr<Core::FileSys::IFile>& f){std::ifstream in(f->path);std::string line;while(std::getline(in,line)){auto p=line.find('=');if(p!=std::string::npos)values.emplace(line.substr(0,p),line.substr(p+1));}return bool(in)||in.eof();}
};
struct RIF {std::vector<std::string> entitlements;
    bool Open(const fs::path&,const fs::path& f){std::ifstream in(f);std::string line;while(std::getline(in,line))entitlements.push_back(line);return in.eof();}
    const auto& GetLicenseOnlyEntitlements()const{return entitlements;}};
namespace Libraries::SystemService {enum class OrbisSystemServiceEventType {EntitlementUpdate};
struct OrbisSystemServiceEvent{OrbisSystemServiceEventType event_type{};struct {int userId{},np_service_label{};}service_entitlement_update;};
int events=0;void PushSystemServiceEvent(const OrbisSystemServiceEvent&){++events;}}
@APP@
namespace Libraries::SysModule {
s32 loadModuleInternal(s32 index,s32,const void*,s32* result){++g_modules_array[index].is_loaded;if(result)*result=0;return ORBIS_OK;}
@SYSMODULE@
}
using namespace Libraries::AppContent;
using namespace Libraries::SysModule;
static bool All(const void* ptr,size_t n,unsigned char value){auto bytes=static_cast<const unsigned char*>(ptr);return std::all_of(bytes,bytes+n,[&](auto b){return b==value;});}
int main(int argc,char** argv){
    assert(argc==2);test_root=argv[1];fs::create_directories(test_root/"download");fs::create_directories(test_root/"licenses");
    auto* mnt=Common::Singleton<Core::FileSys::MntPoints>::Instance();mnt->Mount(test_root/"download","/download0",false);mnt->Mount(test_root/"download","/temp0",false);
    auto& serial=Common::ElfInfo::Instance().serial;auto* sfo=Common::Singleton<PSF>::Instance();
    auto& module=*std::find_if(g_modules_array.begin(),g_modules_array.end(),[](auto& x){return x.id==0xb4;});
    unsigned cases=0;
    for(const char* title:{"CUSA00004","CUSA00223","CUSA00552","CUSA00557"}){
        serial=title;sfo->values={{"TITLE_ID",title},{"CONTENT_ID","UP0000-CUSA00000_00-BASE"},{"USER_DEFINED_PARAM_1","7"}};
        sdk_ver=0;OrbisAppContentInitParam init{};OrbisAppContentBootParam boot;std::memset(&boot,0xa5,sizeof(boot));
        OrbisAppContentMountPoint point{};std::strcpy(point.data,"/download0");
        u32 hits=999;u64 kb=999;s32 param=999;
        OrbisAppContentAddcontInfo list[2];std::memset(list,0xa5,sizeof(list));OrbisNpUnifiedEntitlementLabel absent{};std::strcpy(absent.data,"UNKNOWN");
        assert(sceAppContentInitialize(&init,&boot)==ORBIS_APP_CONTENT_ERROR_PARAMETER&&All(&boot,sizeof(boot),0xa5));++cases;
        assert(loadModule(0xb4,0,nullptr,nullptr)==0&&loadModule(0xb4,0,nullptr,nullptr)==0&&module.is_loaded==2);++cases;
        init.reserved[31]=1;assert(sceAppContentInitialize(&init,&boot)==ORBIS_APP_CONTENT_ERROR_PARAMETER&&All(&boot,sizeof(boot),0xa5));init.reserved[31]=0;++cases;
        assert(sceAppContentInitialize(nullptr,&boot)==ORBIS_APP_CONTENT_ERROR_PARAMETER&&All(&boot,sizeof(boot),0xa5));++cases;
        assert(sceAppContentInitialize(&init,&boot)==0&&All(&boot,sizeof(boot),0));++cases;
        assert(sceAppContentInitialize(&init,&boot)==ORBIS_APP_CONTENT_ERROR_BUSY);++cases;
        assert(sceAppContentAppParamGetInt(0,&param)==0&&param==3);assert(sceAppContentAppParamGetInt(1,&param)==0&&param==7);++cases;
        assert(sceAppContentGetAddcontInfoList(12,list,2,&hits)==0&&hits==0&&All(list,sizeof(list),0xa5));++cases;
        assert(sceAppContentGetAddcontInfo(12,&absent,list)==ORBIS_APP_CONTENT_ERROR_NOT_FOUND&&All(list,sizeof(list),0xa5));++cases;
        assert(sceAppContentAddcontEnqueueDownload(12,&absent)==ORBIS_APP_CONTENT_ERROR_NOT_FOUND);assert(sceAppContentAddcontEnqueueDownload(12,nullptr)==ORBIS_APP_CONTENT_ERROR_PARAMETER);++cases;
        OrbisAppContentMountPoint out;std::memset(&out,0xa5,sizeof(out));assert(sceAppContentAddcontMount(12,&absent,&out)==ORBIS_APP_CONTENT_ERROR_NOT_FOUND&&All(&out,sizeof(out),0xa5));++cases;
        assert(sceAppContentDownloadDataGetAvailableSpaceKb(&point,&kb)==0&&kb>0&&kb<=fs::space(test_root/"download").capacity/1024);++cases;
        std::memset(&point,0xff,sizeof(point));kb=77;assert(sceAppContentDownloadDataGetAvailableSpaceKb(&point,&kb)==ORBIS_APP_CONTENT_ERROR_PARAMETER&&kb==77);++cases;
        assert(sceAppContentTemporaryDataMount2(0,&out)==0&&!std::strcmp(out.data,"/temp0")&&All(out.data+6,10,0));++cases;
        assert(unloadModule(0xb4,0,nullptr,nullptr,false)==0&&module.is_loaded==1&&is_initialized);++cases;
        assert(unloadModule(0xb4,0,nullptr,nullptr,false)==0&&module.is_loaded==0&&!is_initialized&&!donor_module_loaded);++cases;
        assert(unloadModule(0xb4,0,nullptr,nullptr,false)==ORBIS_SYSMODULE_NOT_LOADED);++cases;
        hits=99;assert(sceAppContentGetAddcontInfoList(0,list,2,&hits)==ORBIS_APP_CONTENT_ERROR_PARAMETER&&hits==99);++cases;
    }
    // The real initialization path discovers both installed and license-only content.
    serial="CUSA00552";sfo->values["TITLE_ID"]=serial;
    auto addon=test_root/"addons"/serial/"dlc"/"sce_sys";fs::create_directories(addon);
    std::ofstream(addon/"param.sfo")<<"CATEGORY=ac\nCONTENT_ID=UP0000-CUSA00000_00-EXTRA\n";
    std::ofstream(test_root/"licenses"/"UP0000-CUSA00000_00.idx")<<"stub";
    std::ofstream(test_root/"licenses"/"UP0000-CUSA00000_00.rif")<<"EXTRA\nLICENSE\n";
    OrbisAppContentInitParam init{};OrbisAppContentBootParam boot{};u32 hits=0;
    assert(loadModule(0xb4,0,nullptr,nullptr)==0);assert(sceAppContentInitialize(&init,&boot)==0&&addcont_count==2);++cases;
    OrbisAppContentAddcontInfo list[2]{};assert(sceAppContentGetAddcontInfoList(5,list,2,&hits)==0&&hits==2);++cases;
    assert(!strcmp(list[0].entitlement_label.data,"EXTRA")&&list[0].status==OrbisAppContentAddcontDownloadStatus::Installed);++cases;
    OrbisNpUnifiedEntitlementLabel installed{},license{};std::strcpy(installed.data,"EXTRA");std::strcpy(license.data,"LICENSE");
    assert(sceAppContentAddcontEnqueueDownload(0,&installed)==0);++cases;
    OrbisAppContentMountPoint out{};assert(sceAppContentAddcontMount(0,&installed,&out)==0&&!strcmp(out.data,"/addcont0"));++cases;
    std::memset(&out,0xa5,sizeof(out));assert(sceAppContentAddcontMount(0,&license,&out)==ORBIS_APP_CONTENT_ERROR_NOT_FOUND&&All(&out,sizeof(out),0xa5));++cases;
    assert(unloadModule(0xb4,0,nullptr,nullptr,false)==0&&addcont_count==0);++cases;
    assert(loadModule(0xb4,0,nullptr,nullptr)==0&&sceAppContentInitialize(&init,&boot)==0&&addcont_count==2);++cases;
    assert(unloadModule(0xb4,0,nullptr,nullptr,false)==0);++cases;
    serial="CUSA00785";OrbisAppContentMountPoint unrelated{};std::strcpy(unrelated.data,"/download0");u64 kb=0;assert(sceAppContentDownloadDataGetAvailableSpaceKb(&unrelated,&kb)==0&&kb==1048576);++cases;
    std::cout<<"BACHATA_DONOR_APPCONTENT_LIFECYCLE_PASS cases="<<cases<<"\n";
}
'''
with tempfile.TemporaryDirectory() as d:
    folder=Path(d)
    source=folder/'test.cpp'; exe=folder/'test'
    source.write_text(fixture.replace('@APP@',app).replace('@SYSMODULE@',load))
    subprocess.run(['c++','-std=c++23','-O2','-I',str(root),str(source),'-o',str(exe)],check=True)
    subprocess.run([str(exe),str(folder/'data')],check=True)
