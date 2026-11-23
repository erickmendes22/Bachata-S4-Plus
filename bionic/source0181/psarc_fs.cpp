// SPDX-FileCopyrightText: Copyright 2026 Bachata S4+ contributors
// SPDX-License-Identifier: GPL-2.0-or-later
#include "core/file_sys/backends/psarc_fs.h"
#include <algorithm>
#include <array>
#include <cstring>
#include <limits>
#include <mutex>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
#include <zlib.h>
#include "common/logging/log.h"

namespace Core::FileSys {
namespace {
constexpr u64 MaxTocBytes=64u*1024u*1024u;
constexpr u64 MaxManifestBytes=64u*1024u*1024u;
constexpr u32 MaxBlockSize=4u*1024u*1024u;
constexpr u32 MaxFileCount=1'000'000;
u32 Be32(const u8* p) {
    return u32(p[0])<<24|u32(p[1])<<16|u32(p[2])<<8|u32(p[3]);
}
u64 Be40(const u8* p) {
    return u64(p[0])<<32|u64(p[1])<<24|u64(p[2])<<16|u64(p[3])<<8|p[4];
}
std::string Normalize(std::string_view src) {
    std::string ret;
    ret.reserve(src.size());
    for (char c:src) ret.push_back(c=='\\' ? '/' :
        c>='A'&&c<='Z' ? char(c-'A'+'a') : c);
    while (!ret.empty() && (ret.front()=='/' || ret.front()=='.' &&
           ret.size()>1 && ret[1]=='/')) {
        if (ret[0]=='/') ret.erase(0,1);
        else ret.erase(0,2);
    }
    while (!ret.empty() && ret.back()=='/') ret.pop_back();
    if (ret.size()>4096 || ret.find("..")!=std::string::npos ||
        ret.find(':')!=std::string::npos || ret.find('\0')!=std::string::npos)
        return {};
    return ret;
}
} // namespace

struct PsarcStorage {
    struct Entry {
        u32 first_block{};
        u64 size{};
        u64 offset{};
        std::string path;
        u32 blocks{};
    };
    std::unique_ptr<IFile> source;
    mutable std::mutex io_mutex;
    std::vector<Entry> entries;
    std::vector<u32> compressed_sizes;
    std::vector<u64> block_prefix;
    std::unordered_map<std::string,u32> paths;
    std::unordered_set<std::string> directories;
    u32 block_size{};
    u64 physical_size{};
    bool valid{};

    explicit PsarcStorage(std::unique_ptr<IFile> file):source(std::move(file)) {
        if(!source || !source->IsOpen()) return;
        physical_size=source->Size();
        if(physical_size<32) return;
        std::array<u8,32> header{};
        if(!Raw(0,header.data(),header.size())) return;
        if(std::memcmp(header.data(),"PSAR",4)!=0) {
            LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_HEADER_INVALID not a PSAR archive");
            return;
        }
        if (std::memcmp(header.data()+8,"zlib",4)!=0) {
            LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_UNSUPPORTED_CODEC fourcc={:02x}{:02x}{:02x}{:02x}",
                      header[8],header[9],header[10],header[11]);
            return; // never claim we mounted a non-zlib archive
        }
        const u64 toc_len=Be32(header.data()+12);
        const u32 record_len=Be32(header.data()+16);
        const u32 nfiles=Be32(header.data()+20);
        block_size=Be32(header.data()+24);
        if(toc_len>physical_size || toc_len>MaxTocBytes ||
           nfiles<1 || nfiles>MaxFileCount || record_len<30 || record_len>256 ||
           block_size==0 || block_size>MaxBlockSize ||
           32u+u64(nfiles)*record_len>toc_len) {
            LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_TOC_INVALID toc={} files={} entry={} block={}",
                      toc_len,nfiles,record_len,block_size);
            return;
        }
        u32 width=1;
        for(u32 v=block_size-1;v>255;v>>=8) ++width;
        const u64 table_start=32u+u64(record_len)*nfiles;
        const u64 table_count=(toc_len-table_start)/width;
        if(table_count>16'000'000u) return;
        std::vector<u8> toc(toc_len-32);
        if(!Raw(32,toc.data(),toc.size())) return;
        entries.reserve(nfiles);
        for(u32 i=0;i<nfiles;++i){
            const u8* e=toc.data()+u64(i)*record_len;
            Entry entry;
            entry.first_block=Be32(e+16);
            entry.size=Be40(e+20);
            entry.offset=Be40(e+25);
            const u64 nb=entry.size/block_size + ((entry.size%block_size)!=0);
            if(nb>table_count || entry.first_block>table_count-nb ||
               entry.offset>physical_size || entry.size> (1ull<<40)) {
                LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_ENTRY_INVALID index={}",i);
                return;
            }
            entry.blocks=static_cast<u32>(nb);
            entries.push_back(entry);
        }
        compressed_sizes.reserve(table_count);
        block_prefix.reserve(table_count+1);
        block_prefix.push_back(0);
        for(u64 i=0;i<table_count;++i){
            const u8* p=toc.data()+u64(nfiles)*record_len+i*width;
            u32 stored=0;
            for(u32 b=0;b<width;++b) stored=(stored<<8)|p[b];
            if(stored>MaxBlockSize+65536) return;
            compressed_sizes.push_back(stored);
            const u32 bytes=stored==0?block_size:stored;
            block_prefix.push_back(block_prefix.back()+bytes);
        }
        // The first PSARC entry is the newline-delimited file manifest.
        if(entries[0].size==0 || entries[0].size>MaxManifestBytes) return;
        std::vector<u8> list(static_cast<size_t>(entries[0].size));
        if(!ReadEntry(0,0,list.data(),list.size())) return;
        directories.insert("");
        std::string name;
        u32 entry_index=1;
        const auto add_name=[&](){
            if(entry_index>=entries.size()) return;
            const std::string relative=Normalize(name);
            name.clear();
            if(relative.empty()) {++entry_index; return;}
            entries[entry_index].path=relative;
            paths.try_emplace(relative,entry_index);
            std::size_t slash=relative.find('/');
            while(slash!=std::string::npos){
                directories.insert(relative.substr(0,slash));
                slash=relative.find('/',slash+1);
            }
            ++entry_index;
        };
        for(u8 c:list){
            if(c=='\n' || c==0) add_name();
            else if(c!='\r' && name.size()<4096) name.push_back(char(c));
        }
        if(!name.empty()) add_name();
        if(paths.empty()) {
            LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_NO_FILENAMES archive has no usable file table");
            return;
        }
        valid=true;
        LOG_INFO(Lib_SysModule,"BIONIC_PSARC_INDEX_READY files={} paths={} block_size={} toc={}",
                 nfiles,paths.size(),block_size,toc_len);
    }

    bool Raw(u64 where,void* data,u64 size) {
        if(!source || where>physical_size || size>physical_size-where ||
           where>static_cast<u64>(std::numeric_limits<s64>::max()) ||
           size>static_cast<u64>(std::numeric_limits<s64>::max()))return false;
        std::scoped_lock lock{io_mutex};
        if(!source->Seek(static_cast<s64>(where),Common::FS::SeekOrigin::SetOrigin))
            return false;
        auto* dst=static_cast<u8*>(data);
        for(u64 got=0;got<size;){
            s64 n=source->Read(dst+got,size-got);
            if(n<=0)return false;
            got+=u64(n);
        }
        return true;
    }

    bool ReadBlock(u32 entry_index,u32 block,std::vector<u8>& output) {
        if(entry_index>=entries.size())return false;
        const auto& entry=entries[entry_index];
        if(block>=entry.blocks)return false;
        const u32 block_index=entry.first_block+block;
        if(block_index>=compressed_sizes.size())return false;
        const u64 expected=std::min<u64>(block_size,entry.size-u64(block)*block_size);
        const u32 compressed=compressed_sizes[block_index];
        const u64 stored=compressed==0?expected:compressed;
        const u64 file_at=entry.offset+
            block_prefix[block_index]-block_prefix[entry.first_block];
        if(file_at<entry.offset || file_at>physical_size ||
           stored>physical_size-file_at) return false;
        std::vector<u8> packed(stored);
        if(!Raw(file_at,packed.data(),stored))return false;
        output.resize(expected);
        if(compressed==0 || stored==expected) {
            if(stored!=expected)return false;
            std::memcpy(output.data(),packed.data(),expected);
            return true;
        }
        uLongf out_size=static_cast<uLongf>(expected);
        if(uncompress(output.data(),&out_size,packed.data(),packed.size())!=Z_OK ||
           out_size!=expected) {
            LOG_ERROR(Lib_SysModule,"BIONIC_PSARC_DEFLATE_FAILURE entry={} block={}",
                      entry_index,block);
            return false;
        }
        return true;
    }

    bool ReadEntry(u32 index,u64 offset,void* dst,u64 size) {
        if(index>=entries.size() || offset>entries[index].size ||
           size>entries[index].size-offset) return false;
        auto* output=static_cast<u8*>(dst);
        u64 copied=0;
        std::vector<u8> decoded;
        while(copied<size) {
            const u64 current=offset+copied;
            const u32 chunk=static_cast<u32>(current/block_size);
            const u32 within=static_cast<u32>(current%block_size);
            if(!ReadBlock(index,chunk,decoded) || within>=decoded.size())return false;
            const u64 len=std::min<u64>(size-copied,decoded.size()-within);
            std::memcpy(output+copied,decoded.data()+within,len);
            copied+=len;
        }
        return true;
    }
};

class PsarcFile final : public IFile {
public:
    PsarcFile(std::shared_ptr<PsarcStorage> owner,u32 entry)
        :store{std::move(owner)},index{entry} {}
    s64 Read(void* dst,u64 size) override {
        std::scoped_lock lock{pos_mutex};
        const u64 total=store->entries[index].size;
        const u64 n=std::min<u64>(size,total-pos);
        if(n==0)return 0;
        if(!store->ReadEntry(index,pos,dst,n))return -1;
        pos+=n;return static_cast<s64>(n);
    }
    s64 Write(const void*,u64) override {return -1;}
    bool Seek(s64 offset,Common::FS::SeekOrigin origin) override {
        std::scoped_lock lock{pos_mutex};
        const u64 base=origin==Common::FS::SeekOrigin::SetOrigin?0:
            origin==Common::FS::SeekOrigin::CurrentPosition?pos:Size();
        if(base>static_cast<u64>(std::numeric_limits<s64>::max()))return false;
        const s64 current=static_cast<s64>(base);
        if((offset>0&&current>std::numeric_limits<s64>::max()-offset) ||
           (offset<0&&current<std::numeric_limits<s64>::min()-offset))return false;
        const s64 new_pos=current+offset;
        if(new_pos<0 || static_cast<u64>(new_pos)>Size())return false;
        pos=static_cast<u64>(new_pos);return true;
    }
    u64 Tell() const override {std::scoped_lock lock{pos_mutex};return pos;}
    u64 Size() const override {return store->entries[index].size;}
    bool Flush() override {return true;}
    bool IsOpen() const override {return store && store->valid;}
    MmapPolicy GetMmapPolicy() const override {return MmapPolicy::Copy;}
    bool Map(u8* addr,u64 bytes,u64 offset,u32 protection,const FileMapContext& ctx) override {
        if(offset>Size() || bytes>Size()-offset)return false;
        ctx.map_anonymous(addr,bytes);
        if(!store->ReadEntry(index,offset,addr,bytes))return false;
        ctx.protect(addr,bytes,protection);
        return true;
    }
    void Stat(FileStat& stat) override {stat.size=Size();stat.is_directory=false;}
private:
    std::shared_ptr<PsarcStorage> store;
    u32 index;
    mutable std::mutex pos_mutex;
    u64 pos{};
};

class PsarcDirectory final : public IDirectory {
public:
    PsarcDirectory(std::shared_ptr<PsarcStorage> store,std::string relative) {
        const std::string prefix=relative.empty()?"":relative+"/";
        std::unordered_set<std::string> already;
        for(const auto& [path,id]:store->paths) {
            if(!path.starts_with(prefix))continue;
            const std::string rest=path.substr(prefix.size());
            const auto end=rest.find('/');
            const auto name=rest.substr(0,end);
            if(!already.insert(name).second)continue;
            const bool directory=end!=std::string::npos;
            listing.push_back({name,directory,directory?0:store->entries[id].size});
        }
        std::sort(listing.begin(),listing.end(),
                  [](const DirEntry& a,const DirEntry& b){return a.name<b.name;});
    }
    bool Next(DirEntry& out) override {
        if(pos>=listing.size())return false;
        out=listing[pos++];return true;
    }
    void Rewind() override {pos=0;}
private:
    std::vector<DirEntry> listing;
    std::size_t pos{};
};

PsarcBackend::PsarcBackend(std::unique_ptr<IFile> input)
    :m_shared{std::make_shared<PsarcStorage>(std::move(input))} {}
PsarcBackend::~PsarcBackend()=default;
bool PsarcBackend::IsOpen() const {return m_shared&&m_shared->valid;}
bool PsarcBackend::Exists(std::string_view rel) {
    const auto path=Normalize(rel);
    return IsOpen() && (m_shared->paths.contains(path)||m_shared->directories.contains(path));
}
bool PsarcBackend::IsDirectory(std::string_view rel) {
    return IsOpen()&&m_shared->directories.contains(Normalize(rel));
}
std::unique_ptr<IFile> PsarcBackend::Open(std::string_view rel,Common::FS::FileAccessMode mode) {
    if(!IsOpen()||mode!=Common::FS::FileAccessMode::Read)return {};
    auto it=m_shared->paths.find(Normalize(rel));
    if(it==m_shared->paths.end())return {};
    return std::make_unique<PsarcFile>(m_shared,it->second);
}
std::unique_ptr<IDirectory> PsarcBackend::OpenDir(std::string_view rel) {
    const auto path=Normalize(rel);
    if(!IsDirectory(path))return {};
    return std::make_unique<PsarcDirectory>(m_shared,path);
}
std::optional<std::vector<u8>> PsarcBackend::ReadFile(std::string_view rel) const {
    if(!IsOpen())return std::nullopt;
    const auto it=m_shared->paths.find(Normalize(rel));
    if(it==m_shared->paths.end())return std::nullopt;
    const auto& entry=m_shared->entries[it->second];
    if(entry.size>MaxManifestBytes) return std::nullopt;
    std::vector<u8> out(entry.size);
    if(!m_shared->ReadEntry(it->second,0,out.data(),out.size()))return std::nullopt;
    return out;
}
} // namespace Core::FileSys
