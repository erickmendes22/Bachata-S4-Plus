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
        # Sparse saved permutation indices are allowed. Never consider uninitialized holes.
        s=s.replace("const auto& it = std::ranges::find(it_pgm.value()->modules, spec, &Program::Module::spec);",
                    """const auto it = std::ranges::find_if(it_pgm.value()->modules, [&](const auto& m) {
            return bool(m.module) && m.spec == spec;
        });""")
    if not order:
        anchor="const auto& it = std::ranges::find(it_pgm.value()->modules, spec, &Program::Module::spec);"
        assert s.count(anchor)==1
        s=s.replace(anchor, """auto& saved_modules=it_pgm.value()->modules;
        auto it=saved_modules.end();
        if (perm_idx<saved_modules.size() && saved_modules[perm_idx].module) {
            auto& saved=saved_modules[perm_idx];
            if (saved.spec.bitset != spec.bitset ||
                !(saved.spec==spec) || !(spec==saved.spec)) return false;
            it=saved_modules.begin()+perm_idx;
        }""")
        anchor="    it_pgm.value()->InsertPermut(module, std::move(spec), perm_idx);"
        assert s.count(anchor)==1
        s=s.replace(anchor,"    spec.info = &it_pgm.value()->info;\n"+anchor)
    p.write_text(s)
    return {"drain_cache_writes": True, "atomic_blob_publication":True,
            "order_independent_shader_restore": order}
