"""GPU-memory transaction adapted from exact effective Order c53cd01+756a4f0.
Keep the actual FEX backing/VMM and both title-specific fixes.
No changes to guest CPU, HLE ABI, videoout, presenter, or FPS.
"""
from pathlib import Path
import re

def apply(root:Path, order:bool):
    v=root/"src/video_core"
    def edit(p,a,b,n=1):
        s=p.read_text()
        if s.count(a)!=n: raise RuntimeError(f"memory transaction source drift {p.name}: {a[:90]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    rm=v/"buffer_cache/region_manager.h"
    edit(rm,"#include <utility>","#include <utility>\n#include <atomic>")
    # All readers/writers of the published dirty words use atomic accesses.
    # Their existing region lock still serializes transitions and watchers.
    edit(rm,"const u64 word = state[index] & mask;",
         "const u64 word = std::atomic_ref<u64>(state[index]).load(std::memory_order_acquire) & mask;")
    edit(rm,"return state[start_word] & (start_mask & end_mask);",
         "return std::atomic_ref<u64>(state[start_word]).load(std::memory_order_acquire) & (start_mask & end_mask);")
    edit(rm,"if (state[start_word] & start_mask) {",
         "if (std::atomic_ref<u64>(state[start_word]).load(std::memory_order_acquire) & start_mask) {")
    edit(rm,"if (state[i]) {","if (std::atomic_ref<u64>(state[i]).load(std::memory_order_acquire)) {")
    edit(rm,"return state[end_word] & end_mask;",
         "return std::atomic_ref<u64>(state[end_word]).load(std::memory_order_acquire) & end_mask;")
    for name,prot in (("cpu","write_prot"),("gpu","read_prot")):
        edit(rm,f"""            const u64 prev = {name}[index];
            if constexpr ({name}_op == StateOp::Clear) {{
                {name}[index] &= ~mask;
            }} else {{
                {name}[index] |= mask;
            }}
            {prot}[index] = ({name}[index] ^ prev) & mask;""",
        f"""            auto word=std::atomic_ref<u64>({name}[index]);
            if constexpr ({name}_op == StateOp::Clear) {{
                const u64 prev=word.fetch_and(~mask,std::memory_order_acq_rel);
                {prot}[index]=prev & mask;
            }} else {{
                const u64 prev=word.fetch_or(mask,std::memory_order_acq_rel);
                {prot}[index]=~prev & mask;
            }}""")
    mt=v/"buffer_cache/memory_tracker.h"
    text=mt.read_text()
    start=text.index("    /// Call 'func' for each CPU modified range")
    end=text.index("    /// Call 'func' for each GPU modified range",start)
    text=text[:start]+r'''    /// Donor upload transaction: protect CPU-written bytes first, snapshot via
    /// the FEX physical alias, and only then publish GPU ownership.
    /// The callback must not execute a guest read or re-enter the tracker.
    void ForEachUploadRange(VAddr cpu_addr, u64 size, bool is_written, auto&& func,
                            auto&& on_upload) {
        if (!size || cpu_addr >= (1ULL<<MAX_CPU_PAGE_BITS) ||
            size > (1ULL<<MAX_CPU_PAGE_BITS)-cpu_addr) return;
        struct HeldRegions {
            std::vector<std::pair<RegionManager*,Bounds>> items;
            ~HeldRegions() {
                for (auto it=items.rbegin();it!=items.rend();++it)
                    it->first->Unlock(it->second);
            }
        } held;
        if (is_written) {
            held.items.reserve((size+(cpu_addr&HIGHER_PAGE_MASK)+HIGHER_PAGE_SIZE-1)
                               /HIGHER_PAGE_SIZE);
        }
        IteratePages<true>(cpu_addr,size,[&](RegionManager* manager,u64 offset,u64 n) {
            if (!is_written) {
                if (manager->template IsRegionModified<Type::CPU>(offset,n))
                    manager->template ForEachModifiedRange<Type::CPU,StateOp::Clear,StateOp::None>(
                        offset,n,func);
                return;
            }
            const auto bounds=manager->GetBounds(offset,n);
            manager->Lock(bounds);
            held.items.emplace_back(manager,bounds);
            manager->template ForEachModifiedRange<Type::CPU,StateOp::Clear,StateOp::None,false>(
                offset,n,func);
        });
        on_upload();
        if (is_written) {
            IteratePages(cpu_addr,size,[&](RegionManager* manager,u64 offset,u64 n) {
                manager->template ChangeRegionState<StateOp::None,StateOp::Set,false>(offset,n);
            });
        }
    }

'''+text[end:]
    # Guard every public tracker entry against zero/overflow and out-of-GART indices.
    text=text.replace("        using FuncReturn = typename std::invoke_result<Func, RegionManager*, u64, size_t>::type;",
        """        if (!size || cpu_address >= (1ULL<<MAX_CPU_PAGE_BITS) ||
            size > (1ULL<<MAX_CPU_PAGE_BITS)-cpu_address) return false;
        using FuncReturn = typename std::invoke_result<Func, RegionManager*, u64, size_t>::type;""")
    mt.write_text(text)
    cache=v/"buffer_cache/buffer_cache.cpp";s=cache.read_text()
    a=s.index("bool BufferCache::SynchronizeMemory(const Buffer* arena")
    b=s.index("\nbool BufferCache::SynchronizeMemoryFromImage",a)
    old=s[a:b]
    assert old.count("    memory_tracker->ForEachUploadRange(")==1
    assert old.count("    });\n    if (total_size_bytes>64_MB")==1
    assert old.count("        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);")==1
    body=old.replace("    size_t total_size_bytes{};","    size_t total_size_bytes{};\n    Vulkan::StagingBufferRef staging{};")
    if order:
        # Image readback resolution may re-enter buffer tracking. Complete it
        # before locking any region; account for the page-expanded CPU copy.
        body=body.replace("    memory_tracker->ForEachUploadRange(",
            """    const auto begin=Common::AlignDown(device_addr,4_KB);
    const auto end=Common::AlignUp(device_addr+size,4_KB);
    if(end>begin) texture_cache.ResolveImageReadbacks(begin,end-begin,true);
    memory_tracker->ForEachUploadRange(""",1)
        assert body.count("            texture_cache.ResolveImageReadbacks(copy.dstOffset,copy.size,true);\n")==1
        body=body.replace("            texture_cache.ResolveImageReadbacks(copy.dstOffset,copy.size,true);\n","")
    body=body.replace("    });\n    if (total_size_bytes>64_MB","    }, [&] {\n    if (total_size_bytes>64_MB",1)
    body=body.replace("        const auto staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);",
                      "        staging = staging_pool.Request(total_size_bytes, MemoryType::HostUncached);",1)
    assert body.count("        runtime.CopyBuffer(staging.buffer, arena, copies);\n    }")==1
    body=body.replace("        runtime.CopyBuffer(staging.buffer, arena, copies);\n    }",
        "    }\n    });\n    // Vulkan command recording happens outside the region locks.\n    if (!copies.empty()) runtime.CopyBuffer(staging.buffer, arena, copies);",1)
    cache.write_text(s[:a]+body+s[b:])
    # Read watchers must prevent both reads and writes (PROT_WRITE alone is
    # not a valid read-trapping protection on AArch64).
    page=v/"page_manager.cpp"
    if not order:
        edit(page,"            return ReadPerm() | WritePerm();",
             "            return num_read_watchers ? Core::MemoryPermission::None : ReadPerm() | WritePerm();")
    # Preserve exact interval provenance rather than triggering downloads of
    # unrelated CPU-owned dwords on the same GPU-dirty page. The actual
    # SRT readback code runs on the sole GPU owner, after a synchronous
    # command handoff. Protect the cross-thread interval reads as well.
    h=v/"buffer_cache/buffer_cache.h"
    edit(h,"#include <deque>","#include <deque>\n#include <shared_mutex>\n#include <mutex>")
    edit(h,"    RangeSet gpu_modified_ranges;\n    RangeSet srt_source_pages;",
         """    class SynchronizedRanges {
    public:
        void Add(VAddr a,size_t n) { std::unique_lock l{mutex};ranges.Add(a,n); }
        void Subtract(VAddr a,size_t n) { std::unique_lock l{mutex};ranges.Subtract(a,n); }
        bool Intersects(VAddr a,size_t n) const {
            std::shared_lock l{mutex};return ranges.Intersects(a,n);
        }
        template<class F> void ForEachInRange(VAddr a,size_t n,F&& fn) const {
            std::shared_lock l{mutex};ranges.ForEachInRange(a,n,std::forward<F>(fn));
        }
    private:
        mutable std::shared_mutex mutex;
        RangeSet ranges;
    };
    SynchronizedRanges gpu_modified_ranges;
    SynchronizedRanges srt_source_pages;""")
    s=cache.read_text()
    p=s.index("bool BufferCache::IsRangeGpuWritten(")
    q=s.index("\n}",p)+2
    old=s[p:q]
    assert "gpu_modified_ranges.Intersects(addr,size)" in old
    s=s[:p]+"""bool BufferCache::IsRangeGpuWritten(VAddr addr, size_t size) {
    if (size==0 || addr>UINT64_MAX-size) return false;
    return gpu_modified_ranges.Intersects(addr,size);
}"""+s[q:]
    cache.write_text(s)
    # Keep the stable runtime-home cache path isolated by actual shader ABI
    # and driver. Do not change other user paths or restore old graphics PSOs.
    pc=v/"renderer_vulkan/vk_pipeline_cache.cpp"
    ser=v/"renderer_vulkan/vk_pipeline_serialization.cpp"
    versions="-".join(re.search(rf"{n} = (\d+)u;",ser.read_text())[1] for n in
                      ("ShaderMetaVersion","ShaderBinaryVersion","PipelineKeyVersion"))
    s=pc.read_text()
    for inc in ('#include "common/path_util.h"','#include "common/elf_info.h"','#include <filesystem>'):
        if inc not in s: s=inc+"\n"+s
    anchor="    // BACHATA_DRIVER_CACHE: initialize the driver cache BEFORE warming" if order else "    auto [cache_result, cache] = instance.GetDevice().createPipelineCacheUnique({});"
    assert s.count(anchor)==1
    s=s.replace(anchor,r'''#ifdef __ANDROID__
    if (EmulatorSettings.IsPipelineCacheEnabled()) {
        using namespace Common::FS;
        const auto serial=Common::ElfInfo::Instance().GameSerial();
        if (serial=="CUSA00785" || serial=="CUSA08809" || serial=="CUSA08034") {
            const auto user=GetUserPath(PathType::UserDir);
            const auto runtime=user.parent_path().parent_path();
            if (user.filename()=="user" && runtime.filename()=="runtime" &&
                runtime.parent_path().filename()=="files") {
                std::string key;
                for(auto b:instance.GetPipelineCacheUUID()) key+=fmt::format("{:02x}",unsigned(b));
                const auto stable=runtime.parent_path()/"runtime-home"/"cache-bionic-0181-@VERS@" /
                    fmt::format("{:x}-{:x}-{:x}-{}",instance.GetVendorID(),instance.GetDeviceID(),
                                instance.GetDriverVersion(),key);
                std::error_code ec;
                std::filesystem::create_directories(stable,ec);
                if(!ec && std::filesystem::is_directory(stable,ec)) {
                    SetUserPath(PathType::CacheDir,stable);
                    LOG_INFO(Render,"BACHATA_PERSISTENT_CACHE_ROOT {}",stable.string());
                }
            }
        }
    }
#endif
'''.replace("@VERS@",versions)+anchor)
    pc.write_text(s)
    if order:
        # A driver cache HIT can come from the driver's internal cache even
        # when initialDataSize is zero. Save the first valid payload anyway.
        live=v/"renderer_vulkan/order_live_pso_cache.h"
        edit(live,"    if(disk&&!path.empty()&&!hit) {","    if(disk&&!path.empty()&&(!hit||bytes.empty())) {")
    return {"upload":"actual donor CPU-protect/snapshot/GPU-publish transaction",
            "atomic_dirty_words":True,"range_provenance":"exact synchronized byte intervals",
            "precise_page_permissions":"both accesses trapped on read-watch",
            "stable_cache_root":True,"order_cache_hit_with_empty_input":"persist valid payload",
            "cpu":"FEX unchanged","fps":"original Bachata videoout and presenter unchanged"}
