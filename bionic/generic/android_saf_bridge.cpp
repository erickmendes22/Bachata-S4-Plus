// PS4 /app0 lazy SAF mount backed by Android's existing game broker.
// Files are symlinks to held SCM_RIGHTS descriptors, NEVER byte copies.
// Local staging files (eboot/param.sfo) take precedence in GetHostPath().
#include "android_saf_bridge.h"
#include "android_saf_transport.h"
#include <cerrno>
#include <algorithm>
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
// Guest aliases are a separate mapping from the SAF broker session; do not
// take Session::lock recursively when Resolve/StatPath/OpenFd calls GuestPath.
std::mutex& AliasLock() {static std::mutex mutex;return mutex;}
std::unordered_map<std::string,std::string>& AliasMap() {
    static std::unordered_map<std::string,std::string> aliases;
    return aliases;
}
std::optional<std::string> SourceGuestPath(std::string_view guest) {
    std::scoped_lock lock{AliasLock()};
    std::size_t most_specific=0;
    std::optional<std::string> converted;
    for(const auto& [alias,source]:AliasMap()) {
        if((guest==alias || (guest.size()>alias.size() &&
           guest.starts_with(alias) && guest[alias.size()]=='/')) &&
           alias.size()>most_specific) {
            most_specific=alias.size();
            converted=source;
            converted->append(guest.substr(alias.size()));
        }
    }
    return converted;
}
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
    // FIOS2 names such as PhyreFIOS2/gra/shader must resolve to the same
    // /app0 SAF root the official Release maps with MntPoints::MountAlias.
    // The previously added MountAlias copied only local backend pointers,
    // which alone cannot make the separately handled Android SAF fallback
    // recognize the alias. Translate it before broker STAT/LIST/OPEN.
    const auto remapped=SourceGuestPath(path);
    if(remapped)path=*remapped;
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
// Match the working Release's case-insensitive PS4 guest file search in a
// case-sensitive Android DocumentsProvider. Do NOT synthesize missing files.
// LIST is used only after an exact STAT/OPEN failed, with bounded depth.
std::optional<std::string> FindActualCase(const Session& s, std::string_view wanted) {
    if (!Valid(wanted) || wanted.size()>4096) return std::nullopt;
    auto fold=[](unsigned char c) -> unsigned char {
        return c>='A' && c<='Z' ? static_cast<unsigned char>(c-'A'+'a') : c;
    };
    auto insensitive=[&](std::string_view a,std::string_view b) {
        if(a.size()!=b.size())return false;
        for(std::size_t i=0;i<a.size();++i)
            if(fold(static_cast<unsigned char>(a[i])) !=
               fold(static_cast<unsigned char>(b[i])))return false;
        return true;
    };
    std::string resolved;
    std::size_t from=0;
    for(unsigned depth=0;from<wanted.size() && depth<32;++depth) {
        const auto slash=wanted.find('/',from);
        const auto segment=wanted.substr(from,slash==wanted.npos?wanted.npos:slash-from);
        if(segment.empty())return std::nullopt;
        std::vector<Entry> found;
        if(!GetList(s,resolved,found))return std::nullopt;
        auto exact=std::find_if(found.begin(),found.end(),[&](const Entry& e){
            return e.name==segment;
        });
        if(exact==found.end())exact=std::find_if(found.begin(),found.end(),
            [&](const Entry& e){return insensitive(e.name,segment);});
        if(exact==found.end())return std::nullopt;
        if(slash!=wanted.npos&&!exact->directory)return std::nullopt;
        if(!resolved.empty())resolved+='/';
        resolved+=exact->name;
        if(slash==wanted.npos)return resolved;
        from=slash+1;
    }
    return std::nullopt;
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
    { std::scoped_lock alias_lock{AliasLock()};AliasMap().clear(); }
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
void RegisterGuestAlias(std::string_view source_guest,std::string_view alias_guest) {
    // Only the actual game-root virtual mounts may be forwarded into the
    // selected SAF game provider. Never alias another or absolute host path.
    if(source_guest!="/app0" && source_guest!="/hostapp")return;
    if(alias_guest.empty() || alias_guest.size()>1024 ||
       alias_guest.find("..")!=alias_guest.npos ||
       alias_guest.find('\\')!=alias_guest.npos ||
       alias_guest.find('\0')!=alias_guest.npos)return;
    std::scoped_lock lock{AliasLock()};
    AliasMap().insert_or_assign(std::string(alias_guest),std::string(source_guest));
    std::fprintf(stderr,"BACHATA_RELEASE026_SAF_ALIAS source=%.*s alias=%.*s\n",
                 int(source_guest.size()),source_guest.data(),
                 int(alias_guest.size()),alias_guest.data());
}
std::optional<fs::path> Resolve(std::string_view guest) {
    auto relative=GuestPath(guest);
    if(!relative)return std::nullopt;
    auto& s=S();
    std::scoped_lock lk(s.lock);
    if(!s.active)return std::nullopt;
    auto canonical=*relative;
    auto meta=GetStat(s,canonical);
    if(!meta) {
        if(const auto alternative=FindActualCase(s,canonical)) {
            canonical=*alternative;
            meta=GetStat(s,canonical);
        }
    }
    if(!meta)return std::nullopt;
    const auto found=s.handles.find(canonical);
    if(found!=s.handles.end())return s.shadow/canonical;
    const auto path=s.shadow/canonical;
    std::error_code ec;
    if(meta->directory) {
        fs::create_directories(path,ec);
        if(ec)Warn("MKDIR_FAILED",canonical,ec.value());
        return ec?std::nullopt:std::optional<fs::path>{path};
    }
    // Do not pin every directory listing's files. Only OPEN files the
    // application actually touches; bound cache by the process fd limit.
    auto reply=Protocol::Request(s.socket,s.token,3,Remote(s,canonical));
    if(reply.status!=0 || reply.fd<0) {
        Warn("OPEN_FAILED",canonical,reply.status);
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
        Warn("SYMLINK_FAILED",canonical,ec.value());close(reply.fd);
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
    s.handles.emplace(canonical,reply.fd);
    std::fprintf(stderr,"BIONIC_SAF_OPEN relative=%s size=%llu\n",
        canonical.c_str(),static_cast<unsigned long long>(meta->size));
    return path;
}
bool StatPath(std::string_view guest, bool* is_directory) {
    auto relative = GuestPath(guest, true);
    if (!relative) return false;
    auto& s = S();
    std::scoped_lock lk(s.lock);
    if (!s.active) return false;
    auto meta = GetStat(s, *relative);
    if(!meta) {
        if(const auto actual=FindActualCase(s,*relative))
            meta=GetStat(s,*actual);
    }
    if (!meta) return false;
    if (is_directory) *is_directory = meta->directory;
    return true;
}
bool List(std::string_view guest,std::vector<Entry>& out) {
    auto relative=GuestPath(guest,true);
    if(!relative)return false;
    auto& s=S();std::scoped_lock lk(s.lock);
    if(!s.active)return false;
    if(GetList(s,*relative,out))return true;
    const auto actual=FindActualCase(s,*relative);
    return actual && GetList(s,*actual,out);
}
bool IsVirtualPath(const fs::path& path) {
    auto& s=S();std::scoped_lock lk(s.lock);
    if(!s.active)return false;
    auto relative=path.lexically_relative(s.shadow).generic_string();
    return Valid(relative);
}
// BACHATA_RELEASE026_SAF_DIRECT_FD: issue an independent BSF1 OPEN per
// emulated file rather than first creating a symlink in app-private storage.
// FEX no longer depends on /proc/self/fd while reading game assets.
std::optional<int> OpenFd(std::string_view guest) {
    auto relative=GuestPath(guest);
    if(!relative)return std::nullopt;
    auto& s=S();
    std::scoped_lock lk(s.lock);
    if(!s.active)return std::nullopt;
    std::string canonical=*relative;
    auto reply=Protocol::Request(s.socket,s.token,3,Remote(s,canonical));
    if((reply.status!=0 || reply.fd<0)) {
        if(const auto actual=FindActualCase(s,canonical)) {
            canonical=*actual;
            reply=Protocol::Request(s.socket,s.token,3,Remote(s,canonical));
        }
    }
    if(reply.status!=0 || reply.fd<0) {
        Warn("DIRECT_FD_OPEN_FAILED",canonical,reply.status);
        return std::nullopt;
    }
    std::fprintf(stderr,"BACHATA_RELEASE026_SAF_DIRECT_FD_OPEN relative=%s\n",canonical.c_str());
    return reply.fd; // caller must close; independent of cached symlink handles
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
