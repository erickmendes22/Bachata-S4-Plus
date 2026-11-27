"""Port Order's shader-only background cache restore without replaying graphics PSOs.

Donor: The-Order-1886_pc c53cd01, StartBackgroundWarmUp/MergeWarmStage/PumpWarmUp.
The FEX core has a different cache ABI: keep its metadata parser and program ownership.
"""
from pathlib import Path

def apply(root):
    src = root / 'src'
    def edit(rel, old, new, count=1):
        p = src / rel
        s = p.read_text()
        if s.count(old) != count:
            raise RuntimeError(f'Order shader warmup anchor {rel}: {old[:100]} count={s.count(old)}')
        p.write_text(s.replace(old, new))
    v = 'video_core/renderer_vulkan/'
    # Reader uses the existing on-disk format, but rejects truncated cache data
    # without invoking the emulator's fatal guest assertion on the warm thread.
    edit('common/serdes.h', '#include <string>', '#include <string>\n#include <stdexcept>')
    edit('common/serdes.h', '    void Advance(size_t size) {', '''    [[nodiscard]] size_t Remaining() const { return container.size() - offset; }
    bool CheckedRead() const { return checked_read; }
    void Require(size_t size) const {
        if (checked_read && size > Remaining()) throw std::runtime_error("truncated shader cache");
    }
    void Advance(size_t size) {
        Require(size);''')
    edit('common/serdes.h', '    explicit Archive(std::vector<u8>&& v) : container{v} {}', '''    explicit Archive(std::vector<u8>&& v, bool checked = false)
        : container{std::move(v)}, checked_read{checked} {}''')
    edit('common/serdes.h', '    std::vector<u8> container{};', '    std::vector<u8> container{};\n    bool checked_read{};')
    edit('common/serdes.h', '    void Read(T* ptr, size_t size) {', '    void Read(T* ptr, size_t size) {\n        ar.Require(size);')
    edit('common/serdes.h', '        Read(num_elements);\n        for (int i = 0;', '''        Read(num_elements);
        if (ar.CheckedRead() && num_elements > ar.Remaining())
            throw std::runtime_error("invalid shader cache element count");
        for (size_t i = 0;''')
    edit('common/serdes.h', '        Read(length);\n        s.resize(length);', '        Read(length);\n        ar.Require(length);\n        s.resize(length);')
    # Direct disk reads are permitted only for the directory store. It publishes
    # each blob by rename; any live hash is excluded before a worker can publish.
    edit('video_core/cache_storage.h', '    void ForEachBlob(BlobType type, const std::function<void(std::vector<u8>&& data)>& func);', '''    void ForEachBlob(BlobType type, const std::function<void(std::vector<u8>&& data)>& func);
    void ForEachWarmMeta(const std::function<bool(std::vector<u8>&&)>& consume, const std::function<bool()>& cancelled);
    bool LoadWarmBinary(const std::string& name, std::vector<u32>& spv);''')
    edit('video_core/cache_storage.cpp', 'void DataBase::FinishPreload() {', '''template<class T> static bool ReadWarmBlob(const std::filesystem::path& path, std::vector<T>& data) {
    using namespace Common::FS;
    constexpr u64 MaxBlob = 32 * 1024 * 1024;
    const auto file = IOFile{path, FileAccessMode::Read};
    if (!file.IsOpen()) return false;
    const u64 bytes = file.GetSize();
    if (!bytes || bytes > MaxBlob || bytes % sizeof(T)) return false;
    data.resize(bytes / sizeof(T));
    return file.Read(data) == data.size();
}
void DataBase::ForEachWarmMeta(const std::function<bool(std::vector<u8>&&)>& consume,
                               const std::function<bool()>& cancelled) {
    if (!opened || EmulatorSettings.IsPipelineCacheArchived()) return;
    std::error_code ec;
    for (auto it = std::filesystem::directory_iterator(cache_path, ec);
         !ec && it != std::filesystem::directory_iterator{}; it.increment(ec)) {
        if (cancelled()) return;
        if (it->path().extension() != ".meta") continue;
        std::vector<u8> data;
        if (ReadWarmBlob(it->path(), data) && !consume(std::move(data))) return;
    }
}
bool DataBase::LoadWarmBinary(const std::string& name, std::vector<u32>& spv) {
    if (!opened || EmulatorSettings.IsPipelineCacheArchived()) return false;
    auto path = cache_path / name;
    path.replace_extension("spv");
    return ReadWarmBlob(path, spv);
}
void DataBase::FinishPreload() {''')
    (src / v / 'order_warmup_mailbox.h').write_text('''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <condition_variable>
#include <deque>
#include <mutex>
#include <optional>
#include <utility>
namespace Vulkan {
template<class T, size_t Limit=16> class OrderWarmupMailbox {
public:
    bool Push(T value) {
        std::unique_lock lock{mutex};
        cv.wait(lock, [&] { return stopped || queue.size() < Limit; });
        if (stopped) return false;
        queue.push_back(std::move(value));
        return true;
    }
    std::optional<T> Take() {
        std::unique_lock lock{mutex};
        if (queue.empty()) return {};
        T value = std::move(queue.front()); queue.pop_front();
        lock.unlock(); cv.notify_one();
        return value;
    }
    void Finish() { std::scoped_lock lock{mutex}; finished=true; }
    bool Drained() { std::scoped_lock lock{mutex}; return finished && queue.empty(); }
    void Cancel() {
        { std::scoped_lock lock{mutex}; stopped=true; }
        cv.notify_all();
    }
private:
    std::mutex mutex;
    std::condition_variable cv;
    std::deque<T> queue;
    bool finished{},stopped{};
};
}
''')
    edit(v+'vk_pipeline_cache.h', '#include <functional>', '''#include <functional>
#include <unordered_set>
#include "video_core/renderer_vulkan/order_warmup_mailbox.h"''')
    edit(v+'vk_pipeline_cache.h', '    Shader::Pools pools;', '''    Shader::Pools pools;
    struct OrderWarmStage {
        vk::Device device;
        std::unique_ptr<Program> program;
        std::unique_ptr<Shader::Info> info;
        Shader::StageSpecialization spec;
        size_t permutation{};
        vk::ShaderModule module{};
        ~OrderWarmStage() { if (module) device.destroyShaderModule(module); }
    };
    struct OrderWarmup {
        OrderWarmupMailbox<std::unique_ptr<OrderWarmStage>> ready;
        std::jthread reader;
        std::unordered_set<u64> live_hashes;
        size_t merged{},discarded{};
    };
    std::unique_ptr<OrderWarmup> order_warmup;
    void StartOrderWarmup();
    void PumpOrderWarmup();
    bool MergeOrderWarmStage(OrderWarmStage& stage);
    void StopOrderWarmup();''')
    edit(v+'vk_pipeline_cache.cpp', 'PipelineCache::~PipelineCache() {', 'PipelineCache::~PipelineCache() {\n    StopOrderWarmup();')
    edit(v+'vk_pipeline_cache.cpp', 'const GraphicsPipeline* PipelineCache::GetGraphicsPipeline(const DrawIndirectParams params) {', 'const GraphicsPipeline* PipelineCache::GetGraphicsPipeline(const DrawIndirectParams params) {\n    PumpOrderWarmup();')
    edit(v+'vk_pipeline_cache.cpp', 'const ComputePipeline* PipelineCache::GetComputePipeline() {', 'const ComputePipeline* PipelineCache::GetComputePipeline() {\n    PumpOrderWarmup();')
    edit(v+'vk_pipeline_cache.cpp', '    auto runtime_info = BuildRuntimeInfo(hw_stage, sw_stage);', '''    if (order_warmup) order_warmup->live_hashes.insert(params.hash);
    auto runtime_info = BuildRuntimeInfo(hw_stage, sw_stage);''')
    edit(v+'vk_pipeline_cache.cpp', '    liverpool->InvalidateDrawSnapshots();\n    FinishGraphicsWorkers();', '    StopOrderWarmup();\n    liverpool->InvalidateDrawSnapshots();\n    FinishGraphicsWorkers();')
    edit(v+'vk_pipeline_serialization.cpp', '#include "common/serdes.h"', '''#include "common/serdes.h"
#include "common/hash.h"
#include "common/thread.h"
#ifdef __ANDROID__
#include <sys/resource.h>
#endif''')
    edit(v+'vk_pipeline_serialization.cpp', '    spec.Deserialize(ar);\n    return info.Deserialize(ar) && effective_info.Deserialize(ar);', '''    spec.Deserialize(ar);
    if (!info.Deserialize(ar) || !effective_info.Deserialize(ar)) return false;
    if (ar.CheckedRead() && (perm_idx > 4096 || perm_hash_ar != HashCombine(info.pgm_hash, perm_idx) ||
        effective_info.pgm_hash != info.pgm_hash || effective_info.hw_stage != info.hw_stage ||
        effective_info.sw_stage != info.sw_stage)) return false;
    return true;''')
    edit(v+'vk_pipeline_serialization.cpp', 'void PipelineCache::WarmUp() {', '''void PipelineCache::StartOrderWarmup() {
    order_warmup = std::make_unique<OrderWarmup>();
    auto* warm = order_warmup.get();
    warm->reader = std::jthread([this, warm](std::stop_token stop) {
        Common::SetCurrentThreadName("shadPS4:ShaderWarmup");
#ifdef __ANDROID__
        setpriority(PRIO_PROCESS, 0, 5);
#endif
        try {
            Storage::DataBase::Instance().ForEachWarmMeta([&](std::vector<u8>&& data) {
                if (stop.stop_requested()) return false;
                auto stage = std::make_unique<OrderWarmStage>();
                stage->device = instance.GetDevice();
                stage->program = std::make_unique<Program>();
                stage->info = std::make_unique<Shader::Info>();
                stage->spec.info = &stage->program->info;
                try {
                    Serialization::Archive ar{std::move(data), true};
                    if (!LoadShaderMeta(ar, stage->program->info, *stage->info,
                                        stage->spec, stage->permutation)) return true;
                    const auto hash = stage->program->info.pgm_hash;
                    std::vector<u32> spv;
                    if (!Storage::DataBase::Instance().LoadWarmBinary(
                            fmt::format("{:#018x}_{}", hash, stage->permutation), spv) ||
                        spv.size() < 5 || spv[0] != 0x07230203u) return true;
                    if (stop.stop_requested()) return false;
                    auto result = stage->device.createShaderModule({.codeSize=spv.size()*sizeof(u32),
                                                                   .pCode=spv.data()});
                    if (result.result != vk::Result::eSuccess) return true;
                    stage->module = result.value;
                    return warm->ready.Push(std::move(stage));
                } catch (const std::exception&) { return true; }
            }, [&] { return stop.stop_requested(); });
        } catch (const std::exception&) {
            LOG_WARNING(Render_Vulkan,"Order shader warmup store read interrupted");
        }
        warm->ready.Finish();
    });
}
bool PipelineCache::MergeOrderWarmStage(OrderWarmStage& stage) {
    const auto hash=stage.program->info.pgm_hash;
    // A live compile can write meta and SPIR-V at different instants. Do not
    // install a background pair for any hash observed by the guest since start.
    if (order_warmup->live_hashes.contains(hash)) return false;
    auto [it, inserted] = program_cache.try_emplace(hash);
    if (inserted) it.value()=std::move(stage.program);
    auto& program=*it.value();
    if (program.info.hw_stage!=stage.info->hw_stage || program.info.sw_stage!=stage.info->sw_stage)
        return false;
    const auto perm=stage.permutation;
    if (perm<program.modules.size() && program.modules[perm].module) return false;
    // Never mutate an Info that a live pipeline can already reference.
    program.InsertPermut(stage.module,std::move(stage.spec),perm,std::move(stage.info));
    stage.module=nullptr;
    return true;
}
void PipelineCache::PumpOrderWarmup() {
    if (!order_warmup) return;
    auto& warm=*order_warmup;
    for (unsigned i=0;i<4;++i) {
        auto stage=warm.ready.Take();
        if (!stage) break;
        if (MergeOrderWarmStage(**stage)) ++warm.merged;
        else ++warm.discarded;
    }
    if (warm.ready.Drained()) StopOrderWarmup();
}
void PipelineCache::StopOrderWarmup() {
    if (!order_warmup) return;
    auto& warm=*order_warmup;
    warm.reader.request_stop();
    warm.ready.Cancel();
    if (warm.reader.joinable()) warm.reader.join();
    LOG_INFO(Render_Vulkan,"BACHATA_ORDER_SHADER_WARMUP merged={} discarded={}",warm.merged,warm.discarded);
    order_warmup.reset();
}
void PipelineCache::WarmUp() {''')
    edit(v+'vk_pipeline_serialization.cpp', '    // Accuracy mode does not serialize graphics PSOs:', '''    // Android donor: shader modules only, restored asynchronously. Compute
    // PSOs also wait for live selection; graphics state is never replayed.
    if (AmdGpu::BachataOrderNoMsaa() && !EmulatorSettings.IsPipelineCacheArchived() &&
        !EmulatorSettings.IsPatchShaders() && !EmulatorSettings.IsShaderCollect()) {
        Storage::DataBase::Instance().FinishPreload();
        StartOrderWarmup();
        LOG_INFO(Render_Vulkan,"BACHATA_ORDER_CACHE shader_modules=background graphics=live");
        return;
    }
    // Accuracy mode does not serialize graphics PSOs:''')
    edit(v+'vk_pipeline_serialization.cpp', 'void PipelineCache::Sync() {\n    scheduler.DrainDrawPipe();', 'void PipelineCache::Sync() {\n    scheduler.DrainDrawPipe();\n    StopOrderWarmup();')
    edit(v+'vk_pipeline_serialization.cpp', '    info.Read(this, sizeof(Shader::InfoPersistent));\n    info.Read(flattened_ud_buf);', '''    info.Read(this, sizeof(Shader::InfoPersistent));
    if (ar.CheckedRead() && (buffers.size()>buffers.capacity() || images.size()>images.capacity() ||
        samplers.size()>samplers.capacity() || fmasks.size()>fmasks.capacity() ||
        sharp_tables.size()>sharp_tables.capacity())) return false;
    info.Read(flattened_ud_buf);''')
    edit(v+'vk_pipeline_serialization.cpp', '        walker_func = RegisterWalkerCode(ar.CurrPtr(), walker_func_size);', '''        ar.Require(walker_func_size);
        walker_func = RegisterWalkerCode(ar.CurrPtr(), walker_func_size);''')

if __name__ == '__main__':
    import sys
    apply(Path(sys.argv[1]))
