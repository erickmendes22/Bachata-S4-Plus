// PS4 /app0 lazy SAF mount backed by Android's existing game broker.
// Files are symlinks to held SCM_RIGHTS descriptors, NEVER byte copies.
// Local staging files (eboot/param.sfo) take precedence in GetHostPath().
#include "android_saf_bridge.h"
#include "android_saf_transport.h"
#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <mutex>
#include <sys/stat.h>
#include <unistd.h>
#include <unordered_map>

namespace BachataSaf {
namespace fs=std::filesystem;
namespace {
struct Session {
    std::mutex lock;
    std::string socket, token, prefix;
    fs::path shadow;
    std::unordered_map<std::string,int> handles;
    bool active=false;
};
Session& S() {static Session s;return s;}
bool Valid(std::string_view p,bool root=false) {
    if(p.empty())return root;
    if(p[0]=='/' || p.size()>4096 || p.find('\\')!=p.npos ||
       p.find('\0')!=p.npos)return false;
    std::size_t at=0;
    while(at<p.size()) {
        const auto end=p.find('/',at);
        const auto segment=p.substr(at,end==p.npos?end:end-at);
        if(segment.empty() || segment=="." || segment=="..")return false;
        if(end==p.npos)break;
        at=end+1;
    }
    return true;
}
std::optional<std::string> GuestPath(std::string_view path,bool allow_root=false) {
    if(path=="/app0"||path=="/hostapp")
        return allow_root?std::optional<std::string>{""}:std::nullopt;
    if(path.starts_with("/app0/"))path.remove_prefix(6);
    else if(path.starts_with("/hostapp/"))path.remove_prefix(9);
    else return std::nullopt;
    return Valid(path,allow_root)?std::optional<std::string>{path}:std::nullopt;
}
std::string Remote(const Session& s,std::string_view p) {
    return s.prefix.empty()?std::string(p):
        p.empty()?s.prefix:s.prefix+"/"+std::string(p);
}
struct Stat {bool directory{};std::uint64_t size{};};
std::optional<Stat> GetStat(const Session& s,std::string_view rel) {
    auto r=Protocol::Request(s.socket,s.token,1,Remote(s,rel));
    if(r.status!=0 || r.bytes.size()!=17)return std::nullopt;
    return Stat{r.bytes[0]!=0,Protocol::Read64(r.bytes.data()+1)};
}
bool GetList(const Session& s,std::string_view rel,std::vector<Entry>& out) {
    auto r=Protocol::Request(s.socket,s.token,2,Remote(s,rel));
    if(r.status!=0 || r.bytes.size()<4)return false;
    const auto count=Protocol::Read32(r.bytes.data());
    if(count>16384)return false;
    std::size_t cursor=4;
    for(std::uint32_t i=0;i<count;i++) {
        if(r.bytes.size()-cursor<2)return false;
        const auto len=Protocol::Read16(r.bytes.data()+cursor);cursor+=2;
        if(len==0 || len>255 || r.bytes.size()-cursor<std::size_t(len)+17)return false;
        std::string name(reinterpret_cast<const char*>(r.bytes.data()+cursor),len);
        cursor+=len;
        if(!Valid(name) || name.find('/')!=name.npos)return false;
        bool directory=r.bytes[cursor++]!=0;
        auto size=Protocol::Read64(r.bytes.data()+cursor);cursor+=8;
        auto modified=static_cast<long long>(Protocol::Read64(r.bytes.data()+cursor));
        cursor+=8;
        out.push_back(Entry{std::move(name),directory,size,modified});
    }
    return cursor==r.bytes.size();
}
void Warn(const char* event,std::string_view path,int error=0) {
    std::fprintf(stderr,"BIONIC_SAF_%s relative=%.*s code=%d\n",
       event,int(path.size()),path.data(),error);
}
} // namespace

bool Configure(const std::string& socket,const std::string& token,
               const fs::path& game_root,const fs::path& storage) {
    auto& s=S();
    std::scoped_lock lk(s.lock);
    for(auto& [key,fd]:s.handles)close(fd);
    s.handles.clear();s.active=false;s.prefix.clear();
    s.socket=socket;s.token=token;
    s.shadow=storage/(".bachata-saf-fex-"+std::to_string(getpid()));
    std::error_code ec;
    fs::remove_all(s.shadow,ec);
    ec.clear();fs::create_directories(s.shadow,ec);
    if(ec) {Warn("SHADOW_MKDIR_FAILED",s.shadow.string(),ec.value());return false;}
    // Selected SAF root can itself be CUSA00785, or its parent.
    auto root=GetStat(s,"");
    if(!root || !root->directory) {
        const auto folder=game_root.filename().string();
        if(Valid(folder)) {s.prefix=folder;root=GetStat(s,"");}
    }
    if(!root || !root->directory) {
        Warn("BROKER_ROOT_UNAVAILABLE",game_root.string());return false;
    }
    // Prefer a directory containing the selected game's param.sfo. This
    // prevents silently resolving a similarly named game in a parent tree.
    const auto param=GetStat(s,"sce_sys/param.sfo");
    if(!param && s.prefix.empty()) {
        const auto folder=game_root.filename().string();
        if(Valid(folder)) {
            s.prefix=folder;
            if(!GetStat(s,"sce_sys/param.sfo"))s.prefix.clear();
        }
    }
    // A valid socket is not sufficient: reject an unrelated SAF tree.
    if(!GetStat(s,"sce_sys/param.sfo") && !GetStat(s,"eboot.bin")) {
        Warn("GAME_ROOT_MISMATCH",game_root.string());
        return false;
    }
    s.active=true;
    const auto playgo=GetStat(s,"sce_sys/playgo-chunk.dat");
    const auto libc=GetStat(s,"sce_module/libc.prx");
    std::fprintf(stderr,
        "BIONIC_SAF_READY prefix=%s playgo=%d libc=%d shadow=%s\n",
        s.prefix.c_str(),int(playgo.has_value()),int(libc.has_value()),
        s.shadow.c_str());
    return true;
}
bool Enabled(){auto& s=S();std::scoped_lock lk(s.lock);return s.active;}
std::optional<fs::path> Resolve(std::string_view guest) {
    auto relative=GuestPath(guest);
    if(!relative)return std::nullopt;
    auto& s=S();
    std::scoped_lock lk(s.lock);
    if(!s.active)return std::nullopt;
    const auto found=s.handles.find(*relative);
    if(found!=s.handles.end())return s.shadow/(*relative);
    const auto meta=GetStat(s,*relative);
    if(!meta)return std::nullopt;
    const auto path=s.shadow/(*relative);
    std::error_code ec;
    if(meta->directory) {
        fs::create_directories(path,ec);
        if(ec)Warn("MKDIR_FAILED",*relative,ec.value());
        return ec?std::nullopt:std::optional<fs::path>{path};
    }
    // Do not pin every directory listing's files. Only OPEN files the
    // application actually touches; bound cache by the process fd limit.
    auto reply=Protocol::Request(s.socket,s.token,3,Remote(s,*relative));
    if(reply.status!=0 || reply.fd<0) {
        Warn("OPEN_FAILED",*relative,reply.status);
        return std::nullopt;
    }
    fs::create_directories(path.parent_path(),ec);
    if(!ec) {
        ec.clear();
        fs::remove(path,ec);
        ec.clear();
        fs::create_symlink("/proc/self/fd/"+std::to_string(reply.fd),path,ec);
    }
    if(ec) {
        Warn("SYMLINK_FAILED",*relative,ec.value());close(reply.fd);
        return std::nullopt;
    }
    // The alias handles only stat/path lookup. Real game reads request an
    // independent provider fd, so old aliases can be evicted safely.
    if(s.handles.size()>=512) {
        const auto previous=s.handles.begin();
        std::error_code ignore;
        fs::remove(s.shadow/previous->first,ignore);
        close(previous->second);
        s.handles.erase(previous);
    }
    s.handles.emplace(*relative,reply.fd);
    std::fprintf(stderr,"BIONIC_SAF_OPEN relative=%s size=%llu\n",
        relative->c_str(),static_cast<unsigned long long>(meta->size));
    return path;
}
bool List(std::string_view guest,std::vector<Entry>& out) {
    auto relative=GuestPath(guest,true);
    if(!relative)return false;
    auto& s=S();std::scoped_lock lk(s.lock);
    return s.active && GetList(s,*relative,out);
}
bool IsVirtualPath(const fs::path& path) {
    auto& s=S();std::scoped_lock lk(s.lock);
    if(!s.active)return false;
    auto relative=path.lexically_relative(s.shadow).generic_string();
    return Valid(relative);
}
std::optional<int> DuplicateFd(const fs::path& host) {
    auto& s=S();std::scoped_lock lk(s.lock);
    if(!s.active)return std::nullopt;
    auto relative=host.lexically_relative(s.shadow).generic_string();
    if(!Valid(relative))return std::nullopt;
    // Fresh provider handle: dup() would share file offset across game readers.
    auto reply=Protocol::Request(s.socket,s.token,3,Remote(s,relative));
    if(reply.status!=0 || reply.fd<0) {
        Warn("REOPEN_FAILED",relative,reply.status);
        return std::nullopt;
    }
    return reply.fd;
}
void Shutdown() {
    auto& s=S();std::scoped_lock lk(s.lock);
    s.active=false;
    for(auto& [key,fd]:s.handles)close(fd);
    s.handles.clear();
    std::error_code ec;
    if(!s.shadow.empty())fs::remove_all(s.shadow,ec);
}
} // namespace BachataSaf
