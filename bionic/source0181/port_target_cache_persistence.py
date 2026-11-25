"""Persist shader modules across compatible builds and drain cache writes on shutdown."""
from pathlib import Path

def apply(root, order):
    cache=root/"src/video_core/cache_storage.cpp"
    s=cache.read_text()
    start=s.index("    while (!stoken.stop_requested()) {",s.index("void ProcessIO("))
    end=s.index("\n}\n",start)
    s=s[:start]+"""    for (;;) {
        std::packaged_task<void()> request{};
        {
            std::unique_lock lk{submit_mutex};
            Common::CondvarWait(request_cv, lk, stoken, [&] { return !req_queue.empty(); });
            // Stop only after all queued shader writes have been committed.
            if (req_queue.empty()) {
                if (stoken.stop_requested()) break;
                continue;
            }
            request = std::move(req_queue.front());
            req_queue.pop();
        }
        if (request.valid()) request();
    }"""+s[end:]
    s=s.replace("u32 num_requests{};\n","").replace("std::mutex m_request{};\n","")
    old="""        std::scoped_lock lock{m_request};
        req_queue.emplace(std::move(request));
    }

    std::scoped_lock lk{submit_mutex};
    ++num_requests;
    request_cv.notify_one();"""
    assert old in s
    s=s.replace(old,"""        std::scoped_lock lock{submit_mutex};
        req_queue.emplace(std::move(request));
    }
    request_cv.notify_one();""")
    # Write a complete temporary blob before atomically publishing it.
    old="""                const auto file = IOFile{path, FileAccessMode::Create};
                file.Write(v);"""
    assert old in s
    s=s.replace(old,"""                auto tmp = path;
                tmp += ".tmp";
                {
                    const auto file = IOFile{tmp, FileAccessMode::Create};
                    if (!file.IsOpen()) return;
                    file.Write(v);
                }
                std::error_code ec;
                if (std::filesystem::file_size(tmp, ec) != v.size() * sizeof(T) || ec) {
                    std::filesystem::remove(tmp, ec);
                    return;
                }
                std::filesystem::rename(tmp, path, ec);
                if (ec) {
                    LOG_WARNING(Render, "Shader cache publish failed: {}", ec.message());
                    std::filesystem::remove(tmp, ec);
                }""")
    cache.write_text(s)
    p=root/"src/video_core/renderer_vulkan/vk_pipeline_serialization.cpp"
    s=p.read_text()
    # Keep the existing version validation; do not preload incompatible shader formats.
    if order:
        mark="""    u32 num_pipelines{};
    u32 num_total_pipelines{};"""
        assert mark in s
        s=s.replace(mark,"""    // Accuracy mode does not serialize graphics PSOs: their state has to be
    // derived from live registers. Restore compatible shader modules independently.
    if (AmdGpu::BachataOrderNoMsaa()) {
        u32 restored{};
        Storage::DataBase::Instance().ForEachBlob(
            Storage::BlobType::ShaderMeta, [&](std::vector<u8>&& data) {
                Serialization::Archive ar{std::move(data)};
                infos.fill(nullptr);
                modules.fill(nullptr);
                fetch_shader = nullptr;
                if (LoadPipelineStage(ar, 0)) ++restored;
            });
        infos.fill(nullptr);
        modules.fill(nullptr);
        fetch_shader = nullptr;
        LOG_INFO(Render, "BACHATA_ORDER_CACHE: restored {} compatible shader modules", restored);
    }

"""+mark)
        # The disk key includes the original permutation index. A directional
        # live-draw match at a different index is not an archive identity.
        # Preserve stable Info pointers and never replace an occupied slot.
        anchor="const auto& it = std::ranges::find(it_pgm.value()->modules, spec, &Program::Module::spec);"
        assert s.count(anchor)==1
        s=s.replace(anchor, """auto& saved_modules=it_pgm.value()->modules;
        auto it=saved_modules.end();
        if (perm_idx<saved_modules.size() && saved_modules[perm_idx].module) {
            auto& saved=saved_modules[perm_idx];
            if (!saved.effective_info || saved.spec.bitset != spec.bitset ||
                !(saved.spec==spec) || !(spec==saved.spec)) return false;
            it=saved_modules.begin()+perm_idx;
        }""")
    p.write_text(s)
    if order:
        # Sample process memory and live object cardinalities on new PSOs.
        # ru_maxrss is Linux/Android peak RSS in KiB, not GPU heap usage.
        pc=root/"src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
        c=pc.read_text()
        anchor="#include <ranges>"
        assert c.count(anchor)==1
        c=c.replace(anchor,anchor+"\n#ifdef __ANDROID__\n#include <sys/resource.h>\n#endif")
        anchor='        LOG_INFO(Render_Vulkan, "Compiling graphics pipeline {:#x}", pipeline_hash);'
        assert c.count(anchor)==1
        c=c.replace(anchor,anchor+"""
#ifdef __ANDROID__
        if (AmdGpu::BachataOrderNoMsaa() &&
            (graphics_pipelines.size()==1 || graphics_pipelines.size()%64==0)) {
            size_t shaders=0;
            for (auto p=program_cache.begin();p!=program_cache.end();++p) {
                if (!p.value()) continue;
                for (const auto& m:p.value()->modules) if (m.module) ++shaders;
            }
            struct rusage usage{};
            const int rss_ok=getrusage(RUSAGE_SELF,&usage);
            LOG_INFO(Render_Vulkan,"BACHATA_ORDER_PSO_PRESSURE graphics={} compute={} programs={} modules={} peak_rss_kib={}",
                     graphics_pipelines.size(),compute_pipelines.size(),program_cache.size(),
                     shaders,rss_ok==0?static_cast<long long>(usage.ru_maxrss):-1LL);
        }
#endif
""")
        pc.write_text(c)
    return {"drain_cache_writes": True, "atomic_blob_publication":True,
            "order_independent_shader_restore": order,
            "order_pso_pressure_samples": order}
