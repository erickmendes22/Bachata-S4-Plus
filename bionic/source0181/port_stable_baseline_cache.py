"""Preserve known gameplay core, fixing cache location and ordered IO only."""
from pathlib import Path
import re

def apply(root, target):
    p=root/"src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
    ser=(root/"src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp").read_text()
    abi="-".join(re.search(rf"{v}\s*=\s*(\d+)u;",ser)[1] for v in ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
    s=p.read_text()
    anchor="        .supports_shader_stencil_export = instance_.IsShaderStencilExportSupported(),\n    };"
    assert s.count(anchor)==1
    insert=r''' 
#ifdef __ANDROID__
    // The extracted runtime directory is keyed by the APK core hash.
    // Keep only cache data outside it; config, saves and SAF stay unchanged.
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if (@TITLE@ && EmulatorSettings.IsPipelineCacheEnabled()) {
        using namespace Common::FS;
        const auto old=GetUserPath(PathType::CacheDir);
        const auto version_dir=old.parent_path().parent_path();
        const auto runtime_dir=version_dir.parent_path();
        if (runtime_dir.filename()=="runtime" &&
            version_dir.filename().string().starts_with("bachata-s4-plus-") &&
            old.filename()=="cache") {
            try {
                const auto uuid=instance.GetPipelineCacheUUID();
                std::string uuid_hex;
                for(const auto byte:uuid) uuid_hex+=fmt::format("{:02x}",static_cast<unsigned>(byte));
                const auto driver=fmt::format("{:x}-{:x}-{:x}-{}",instance.GetVendorID(),
                    instance.GetDeviceID(),instance.GetDriverVersion(),uuid_hex);
                const auto stable=runtime_dir.parent_path()/"runtime-home"/"bionic-cache-v2"/
                    "@TARGET@-@ABI@"/driver;
                std::error_code ec;
                std::filesystem::create_directories(stable,ec);
                if(!ec && std::filesystem::is_directory(stable,ec) && !ec) {
                    SetUserPath(PathType::CacheDir,stable);
                    LOG_INFO(Render_Vulkan,"BACHATA_CACHE_ROOT_STABLE target=@TARGET@ abi=@ABI@ path={}",stable.string());
                } else {
                    LOG_WARNING(Render_Vulkan,"BACHATA_CACHE_ROOT_FALLBACK error={}",ec.message());
                }
            } catch (...) {
                LOG_WARNING(Render_Vulkan,"BACHATA_CACHE_ROOT_FALLBACK exception");
            }
        }
    }
#endif
'''
    title='serial=="CUSA00785"' if target=="order" else '(serial=="CUSA08809" || serial=="CUSA08034")'
    s=s.replace(anchor,anchor+insert.replace("@TITLE@",title).replace("@TARGET@",target).replace("@ABI@",abi))
    for h in ("common/elf_info.h","common/path_util.h"):
        if f'#include "{h}"' not in s:s=f'#include "{h}"\n'+s
    if "#include <filesystem>" not in s:s="#include <filesystem>\n"+s
    if target=="sotc":
        # Upstream WarmUp passes *pipeline_cache to the cached pipeline
        # constructors. Make the handle valid first, retain the same warmup.
        a="    WarmUp();\n\n    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});"
        assert s.count(a)==1
        s=s.replace(a,"    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});")
        a="    pipeline_cache = std::move(cache);\n}"
        assert s.count(a)==1
        s=s.replace(a,"    pipeline_cache = std::move(cache);\n    WarmUp();\n}")
    else:
        # Match the tested Android accuracy profile: no legacy aggregate
        # driver snapshot on single-MSAA. Preserve serialized shader/PSO cache.
        a="if (!BachataCompat::Sotc608() && EmulatorSettings.IsPipelineCacheEnabled())"
        assert s.count(a)==1
        s=s.replace(a,'if (!BachataCompat::Sotc608() && serial!="CUSA00785" && EmulatorSettings.IsPipelineCacheEnabled())')
    p.write_text(s)
    # Source-derived lifetime bug: IO queue counters were manipulated under
    # two unrelated locks and writes could be dropped on Close. Keep one lock
    # and drain. Preserve native blob formats, profile checks and shader ABI.
    from port_target_cache_persistence import apply as drain
    result=drain(root,order=False)
    return {"cache_root":"stable title-core/serialization ABI/driver namespace, no incompatible cache import",
            "source_base":target,"cache_io":result}
