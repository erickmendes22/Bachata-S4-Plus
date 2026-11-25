"""Inherited renderer infrastructure; retain FEX CPU and Bachata presentation/FPS.
References: exact Order c53cd01 and SotC 732cb37 effective GPU source trees.
The barrier tree is the common DXVK implementation, not the donor runtime.
"""
from pathlib import Path
import re, shutil

def apply(root: Path, sotc: bool):
    v=root/"src/video_core/renderer_vulkan"
    def edit(p,a,b,n=1):
        p=Path(p); s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"Inherited infrastructure anchor {p.name}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    def prefix(p,inc):
        if inc not in p.read_text(): p.write_text(inc+"\n"+p.read_text())
    for n in ("vk_barrier_tracker.h","vk_barrier_tracker.cpp"):
        shutil.copyfile(Path(__file__).parent/"inherited"/n,v/n)
    # Compile exact tree in this translation unit: no additional CMake ABI.
    # The original Zlib notice remains in both copied files.
    h=v/"vk_runtime.h"; c=v/"vk_runtime.cpp"
    edit(h,'#include "common/interval_set.h"','#include "common/interval_set.h"\n#include "video_core/renderer_vulkan/vk_barrier_tracker.h"')
    edit(h,"    BufferBarriers* resource{};","""    BarrierTracker donor_barriers;
    bool donor_range_tracking{};
    BufferBarriers* resource{};""")
    prefix(c,'#include "common/elf_info.h"')
    edit(c,"    blit_helper = std::make_unique<VideoCore::BlitHelper>(instance, scheduler);",
         """    const auto serial=Common::ElfInfo::Instance().GameSerial();
    donor_range_tracking=serial=="CUSA00785" || serial=="CUSA08809" || serial=="CUSA08034";
    blit_helper = std::make_unique<VideoCore::BlitHelper>(instance, scheduler);""")
    edit(c,"""    MakeCurrent(handle);
    bool has_access = resource->write_ranges.Overlaps(offset, offset + size);""",
         """    if (!size) return false;
    if (donor_range_tracking) {
        const AddressRange range{reinterpret_cast<u64>(handle),offset,offset+size-1};
        return donor_barriers.FindRange(range,Access::Write) ||
            (check_read_access && donor_barriers.FindRange(range,Access::Read));
    }
    MakeCurrent(handle);
    bool has_access = resource->write_ranges.Overlaps(offset, offset + size);""")
    edit(c,"""    MakeCurrent(handle);

    const Interval range = {""","""    if (!size) return;
    if (!donor_range_tracking) MakeCurrent(handle);

    const Interval range = {""")
    edit(c,"""    if (src_access & WRITE_MASK) {
        resource->write_ranges.Add(range);
    }
    if (src_access & READ_MASK) {
        resource->read_ranges.Add(range);
    }""",
         """    if (donor_range_tracking) {
        AddressRange tracked{reinterpret_cast<u64>(handle),offset,offset+size-1};
        if (src_access & WRITE_MASK) donor_barriers.InsertRange(tracked,Access::Write);
        if (src_access & READ_MASK) {
            // Donor's coarse reads: conservative overtracking is safe.
            tracked.range_start &= ~u64{4095};
            tracked.range_end |= u64{4095};
            donor_barriers.InsertRange(tracked,Access::Read);
        }
    } else {
        if (src_access & WRITE_MASK) resource->write_ranges.Add(range);
        if (src_access & READ_MASK) resource->read_ranges.Add(range);
    }""")
    edit(c,"    image_barriers.clear();\n    for (auto& resource : resources) {",
         "    image_barriers.clear();\n    donor_barriers.Clear();\n    for (auto& resource : resources) {")
    with c.open("a") as f: f.write('\n#include "video_core/renderer_vulkan/vk_barrier_tracker.cpp"\n')
    # Correct GPU-resource lifetime. These are temporary modules created only
    # by the constructor, not the shared Program::Module objects.
    g=v/"vk_graphics_pipeline.cpp"
    edit(g,"    const vk::Device device = instance.GetDevice();",
         """    const vk::Device device = instance.GetDevice();
    struct AuxLifetime {
        vk::Device device;
        std::array<vk::ShaderModule,3> modules{};
        size_t count{};
        ~AuxLifetime() { for(size_t i=0;i<count;++i) device.destroyShaderModule(modules[i]); }
    } aux{device};
    const auto compile_aux=[&](std::span<const u32> code) {
        ASSERT(aux.count<aux.modules.size());
        auto module=CompileSPV(code,device);
        aux.modules[aux.count++]=module;
        return module;
    };""")
    for n in ("tcs","tes","fragment"):
        edit(g,f"CompileSPV(sdata.{n}, instance.GetDevice())",f"compile_aux(sdata.{n})")
    # Move only the shader/pipeline cache to the already announced persistent
    # Android runtime-home. Do not change UserDir, saves, SAF, logs or FPS.
    pc=v/"vk_pipeline_cache.cpp"; ser=v/"vk_pipeline_serialization.cpp"
    prefix(pc,'#include "common/path_util.h"')
    prefix(pc,'#include "common/elf_info.h"')
    prefix(pc,"#include <filesystem>")
    prefix(pc,"#include <algorithm>")
    version="-".join(re.search(rf"{n} = (\d+)u;",ser.read_text())[1] for n in
                     ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
    init=r'''
#ifdef __ANDROID__
    if (EmulatorSettings.IsPipelineCacheEnabled()) {
        using namespace Common::FS;
        const auto serial=Common::ElfInfo::Instance().GameSerial();
        if (serial=="CUSA00785" || serial=="CUSA08809" || serial=="CUSA08034") {
            const auto old=GetUserPath(PathType::CacheDir);
            const auto user=GetUserPath(PathType::UserDir);
            const auto runtime=user.parent_path().parent_path();
            if (user.filename()=="user" && runtime.filename()=="runtime" &&
                runtime.parent_path().filename()=="files") {
                const auto uuid=instance.GetPipelineCacheUUID();
                std::string key;
                for(auto b:uuid) key+=fmt::format("{:02x}",unsigned(b));
                const auto stable=runtime.parent_path()/"runtime-home"/"cache-bionic-0181-@ABI@" /
                    fmt::format("{:x}-{:x}-{:x}-{}",instance.GetVendorID(),instance.GetDeviceID(),
                                instance.GetDriverVersion(),key);
                std::error_code ec;
                std::filesystem::create_directories(stable,ec);
                if (!ec && std::filesystem::is_directory(stable,ec)) {
                    SetUserPath(PathType::CacheDir,stable);
                    LOG_INFO(Render,"BACHATA_PERSISTENT_CACHE_ROOT {}",stable.string());
                } else {
                    LOG_WARNING(Render,"BACHATA_PERSISTENT_CACHE_ROOT_FAILED {}",ec.message());
                }
            }
        }
    }
#endif
'''.replace("@ABI@",version)
    if sotc:
        edit(pc,"    WarmUp();\n\n    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});",
             init+"\n    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});")
        edit(pc,"    pipeline_cache = std::move(cache);\n}","    pipeline_cache = std::move(cache);\n    WarmUp();\n}")
    else:
        edit(pc,"    // BACHATA_DRIVER_CACHE: initialize the driver cache BEFORE warming",
             init+"\n    // BACHATA_DRIVER_CACHE: initialize the driver cache BEFORE warming")
        # Use profile/driver isolated cache, never load legacy driver-v1.
        edit(pc,'/ "driver-v1" / key / "cache.bin";','/ "driver-v2" / key / "cache.bin";')
        # Restore modules independently of graphics PSO state. Never recreate
        # Order graphics PSOs from obsolete registers.
        marker="    u32 num_pipelines{};\n    u32 num_total_pipelines{};"
        edit(ser,marker,r'''    if (AmdGpu::BachataOrderNoMsaa()) {
        u32 restored{};
        Storage::DataBase::Instance().ForEachBlob(Storage::BlobType::ShaderMeta,
            [&](std::vector<u8>&& data) {
                Serialization::Archive ar{std::move(data)};
                infos.fill(nullptr);
                modules.fill(nullptr);
                fetch_shader=nullptr;
                if (LoadPipelineStage(ar,0)) ++restored;
            });
        infos.fill(nullptr);
        modules.fill(nullptr);
        fetch_shader=nullptr;
        LOG_INFO(Render,"BACHATA_ORDER_CACHE restored_modules={}",restored);
    }

'''+marker)
        # Checkpoint the driver cache on the GPU owner at a real compile
        # boundary; no worker can race vkGetPipelineCacheData.
        edit(pc,"        RegisterPipelineData(graphics_key, pipeline_hash, sdata);\n        ++num_new_pipelines;",
             """        RegisterPipelineData(graphics_key, pipeline_hash, sdata);
        ++num_new_pipelines;
        if (AmdGpu::BachataOrderNoMsaa() && num_new_pipelines%128==0) SaveDriverCache();""")
    # Stable per-permutation restoration (no directional alias at another index).
    edit(ser,"const auto& it = std::ranges::find(it_pgm.value()->modules, spec, &Program::Module::spec);",
         """auto& entries=it_pgm.value()->modules;
        auto it=entries.end();
        if (perm_idx<entries.size() && entries[perm_idx].module) {
            auto& saved=entries[perm_idx];
            if (!saved.effective_info || !(saved.spec==spec) || !(spec==saved.spec)) return false;
            it=entries.begin()+perm_idx;
        }""")
    # Publish only complete blobs and drain writer queue even on shutdown.
    db=root/"src/video_core/cache_storage.cpp"; s=db.read_text()
    start=s.index("    while (!stoken.stop_requested()) {",s.index("void ProcessIO("))
    end=s.index("\n}\n",start)
    s=s[:start]+"""    for (;;) {
        std::packaged_task<void()> request{};
        {
            std::unique_lock lk{submit_mutex};
            Common::CondvarWait(request_cv,lk,stoken,[&]{return !req_queue.empty();});
            if (req_queue.empty()) {
                if (stoken.stop_requested()) break;
                continue;
            }
            request=std::move(req_queue.front());
            req_queue.pop();
        }
        if(request.valid()) request();
    }"""+s[end:]
    s=s.replace("u32 num_requests{};\n","").replace("std::mutex m_request{};\n","")
    old="""        std::scoped_lock lock{m_request};
        req_queue.emplace(std::move(request));
    }

    std::scoped_lock lk{submit_mutex};
    ++num_requests;
    request_cv.notify_one();"""
    assert s.count(old)==1
    s=s.replace(old,"""        std::scoped_lock lock{submit_mutex};
        req_queue.emplace(std::move(request));
    }
    request_cv.notify_one();""")
    old="""                const auto file = IOFile{path, FileAccessMode::Create};
                file.Write(v);"""
    assert s.count(old)==1
    s=s.replace(old,"""                auto temp=path;
                temp+=".tmp";
                {
                    const auto file=IOFile{temp,FileAccessMode::Create};
                    if (!file.IsOpen()) return;
                    file.Write(v);
                }
                std::error_code ec;
                if (std::filesystem::file_size(temp,ec)!=v.size()*sizeof(T) || ec) {
                    std::filesystem::remove(temp,ec);return;
                }
                std::filesystem::rename(temp,path,ec);
                if (ec) std::filesystem::remove(temp,ec);""")
    db.write_text(s)
    # SRT: visit a page only after a dirty DWORD was confirmed. Otherwise a
    # clean pointer word could suppress another dirty descriptor on that page.
    raster=v/"vk_rasterizer.cpp"; s=raster.read_text()
    old="            if(!visited.insert(page).second)continue;\n            if(!buffer_cache.IsRegionGpuModified(page,PageSize))continue;"
    assert old in s
    s=s.replace(old,"            if(visited.contains(page))continue;\n            if(!buffer_cache.IsRegionGpuModified(page,PageSize))continue;")
    old="            if(!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)))continue;\n            buffer_cache.TrackSrtSourcePage(page);"
    assert old in s
    s=s.replace(old,"            if(!buffer_cache.IsRangeGpuWritten(source,sizeof(u32)))continue;\n            visited.insert(page);\n            buffer_cache.TrackSrtSourcePage(page);")
    raster.write_text(s)
    return {"barrier":"exact shared DXVK barrier tree and conservative read ranges; original scheduler",
            "cache":"persistent driver/ABI root; synchronized atomic files; valid shader preload",
            "lifetime":"constructor auxiliary Vulkan modules released",
            "srt":"dirty DWORD validated before marking visited page",
            "cpu":"FEX retained","fps":"original videoout, FPS and Android presentation code retained"}
