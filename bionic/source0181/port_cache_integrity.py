"""Prevent mixed-generation cached pipelines and make cache IO drain atomically.
No changes to renderer draw/submit order or guest memory.
"""
from pathlib import Path
import re

def one(s,a,b):
    if s.count(a)!=1: raise RuntimeError("cache integrity source drift: "+a[:100])
    return s.replace(a,b,1)

def apply(root:Path,namespace:str):
    p=root/"src/video_core/cache_storage.cpp"
    s=p.read_text()
    s=one(s,"std::mutex submit_mutex{};\nu32 num_requests{};\nstd::condition_variable_any request_cv{};\nstd::queue<std::packaged_task<void()>> req_queue{};\nstd::mutex m_request{};",
          "std::condition_variable_any request_cv{};\nstd::queue<std::packaged_task<void()>> req_queue{};\nstd::mutex m_request{};")
    i=s.index("void ProcessIO(")
    j=s.index("\nconstexpr std::string GetBlobFileExtension",i)
    s=s[:i]+"""void ProcessIO(const std::stop_token& stoken) {
    Common::SetCurrentThreadName("shadPS4:PipelineCacheIO");
    // One mutex owns the queue and predicate. Stop only after draining.
    for (;;) {
        std::packaged_task<void()> request;
        {
            std::unique_lock lock{m_request};
            Common::CondvarWait(request_cv,lock,stoken,[]{ return !req_queue.empty(); });
            if (req_queue.empty()) {
                if (stoken.stop_requested()) break;
                continue;
            }
            request=std::move(req_queue.front());
            req_queue.pop();
        }
        if(request.valid()) request();
    }
}
"""+s[j:]
    s=one(s,'    const auto& game_info = Common::ElfInfo::Instance();',
        '    const auto& game_info = Common::ElfInfo::Instance();\n'
        '    const auto cache_serial=std::string(game_info.GameSerial())+"-'+namespace+'";')
    s=one(s,'std::filesystem::path{game_info.GameSerial()}.replace_extension(".zip")',
        'std::filesystem::path{cache_serial+".zip"}')
    s=one(s,'cache_path = GetUserPath(PathType::CacheDir) / game_info.GameSerial();',
        'cache_path = GetUserPath(PathType::CacheDir) / cache_serial;')
    s=one(s,'    io_worker.request_stop();\n    io_worker.join();',
        '    io_worker.request_stop();\n    request_cv.notify_all();\n    io_worker.join();')
    s=one(s,'auto request = std::packaged_task<void()>{[=]() {\n            auto path{path_};',
        'auto request = std::packaged_task<void()>{[type,path_=std::move(path_),v=std::move(v)]() {\n            auto path{path_};')
    s=one(s,'''                const auto file = IOFile{path, FileAccessMode::Create};
                file.Write(v);''',
        '''                // Same-directory rename ensures a killed process cannot leave a
                // partially written file at the committed cache name.
                auto temp=path;
                temp+=".tmp";
                {
                    const auto file=IOFile{temp,FileAccessMode::Create};
                    if(!file.IsOpen()) return;
                    file.Write(v);
                }
                std::error_code ec;
                if(std::filesystem::file_size(temp,ec)!=v.size()*sizeof(T) || ec) {
                    std::filesystem::remove(temp,ec);
                    return;
                }
                std::filesystem::rename(temp,path,ec);
                if(ec) {
                    LOG_WARNING(Render,"BACHATA_CACHE_WRITE_RENAME_FAILED path={}",path.string());
                    std::filesystem::remove(temp,ec);
                }''')
    s=one(s,'    std::scoped_lock lk{submit_mutex};\n    ++num_requests;\n    request_cv.notify_one();',
        '    request_cv.notify_one();')
    p.write_text(s)
    p=root/"src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    s=p.read_text()
    s=one(s,'#include "common/serdes.h"','#include "common/serdes.h"\n#include <span>')
    s=one(s,'namespace Vulkan {\n\nvoid RegisterPipelineData',
        '''namespace Vulkan {
namespace {
u64 BachataSpvChecksum(std::span<const u32> words) {
    u64 hash=1469598103934665603ULL;
    for(u32 word:words) {
        for(unsigned shift=0;shift<32;shift+=8)
            hash=(hash^u8(word>>shift))*1099511628211ULL;
    }
    return hash;
}
struct PendingShaderBinary {
    u64 hash{};
    size_t index{};
    u64 checksum{};
    bool valid{};
};
thread_local PendingShaderBinary bachata_pending_binary;
}

void RegisterPipelineData''')
    s=one(s,'    meta.Write(perm_hash);\n    meta.Write(perm_idx);',
        '''    // Registration follows CompileModule on the same GPU command thread.
    // A metadata record without the actual binary identity is not reusable.
    if(!bachata_pending_binary.valid || bachata_pending_binary.hash!=info.pgm_hash ||
       bachata_pending_binary.index!=perm_idx) return;
    meta.Write(perm_hash);
    meta.Write(perm_idx);
    meta.Write(bachata_pending_binary.checksum);
    bachata_pending_binary.valid=false;''')
    s=one(s,'    Storage::DataBase::Instance().Save(Storage::BlobType::ShaderBinary,',
        '''    bachata_pending_binary={pgm_hash,perm_idx,BachataSpvChecksum(spv),true};
    Storage::DataBase::Instance().Save(Storage::BlobType::ShaderBinary,''')
    s=one(s,'Shader::StageSpecialization& spec, size_t& perm_idx) {',
        'Shader::StageSpecialization& spec, size_t& perm_idx, u64& binary_checksum) {')
    s=one(s,'    meta.Read(perm_idx);\n','    meta.Read(perm_idx);\n    meta.Read(binary_checksum);\n')
    s=one(s,'    size_t perm_idx{};\n    if (!LoadShaderMeta(ar, program->info, *effective_info, spec, perm_idx)) {',
        '    size_t perm_idx{};\n    u64 binary_checksum{};\n    if (!LoadShaderMeta(ar, program->info, *effective_info, spec, perm_idx,binary_checksum)) {')
    s=one(s,'    if (spv.empty()) {\n        return false;\n    }',
        '''    if (spv.empty() || BachataSpvChecksum(spv)!=binary_checksum) {
        LOG_WARNING(Render,"BACHATA_CACHE_BINARY_META_MISMATCH shader={:#x} perm={}",
                    program->info.pgm_hash,perm_idx);
        return false;
    }
    runtime_infos[stage]=spec.runtime_info;''')
    for name in ("Compute","Graphics"):
        s=one(s,f'bool PipelineCache::Load{name}Pipeline(Serialization::Archive& ar) {{',
             f'''bool PipelineCache::Load{name}Pipeline(Serialization::Archive& ar) {{
    // A partially failed preload must not leak prior stage pointers into
    // the next cached pipeline (especially absent optional stages).
    infos.fill(nullptr);
    modules.fill(nullptr);
    runtime_infos={{}};
    fetch_shader=nullptr;''')
    s=one(s,'    LOG_INFO(Render, "Preloaded {} pipelines", num_pipelines);',
        '''    infos.fill(nullptr);
    modules.fill(nullptr);
    runtime_infos={};
    fetch_shader=nullptr;
    LOG_INFO(Render, "Preloaded {} pipelines", num_pipelines);''')
    s=one(s,'ShaderMetaVersion = 17u;','ShaderMetaVersion = 18u;')
    s,n=re.subn(r'ShaderBinaryVersion = (\d+)u;',lambda m:f'ShaderBinaryVersion = {int(m.group(1))+1}u;',s)
    if n!=1: raise RuntimeError("cache binary version drift")
    p.write_text(s)
    return {"cache":"schema namespace, exact binary checksum, atomic blob write, drain IO, clear failed preload stages"}
