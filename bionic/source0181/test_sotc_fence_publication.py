#!/usr/bin/env python3
"""Run actual SotC EOP/EOS publication, tracking and readback code.

Vulkan scheduling/storage is deterministic fixture data; MemoryTracker,
RegionManager, Rasterizer invalidation and the SotC BufferCache readback
methods are compiled from the fully overlaid source. A backing label must
survive both old and future readbacks and reach the next GPU upload.
"""
import argparse
import ast
import os
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
args = parser.parse_args()
src = (args.source / "src").resolve()
here = Path(__file__).parent


def block(text, marker):
    start = text.index(marker)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[start:end + 1]
    raise AssertionError(f"unclosed C++ block: {marker}")


def callback(text, event):
    case = text[text.index(f"case PM4ItOpcode::{event}: {{"):]
    return block(case, "[this](void* address, u64 data, u32 num_bytes)")


cache = (src / "video_core/buffer_cache/buffer_cache.cpp").read_text()
header = (src / "video_core/buffer_cache/buffer_cache.h").read_text()
cp = (src / "video_core/amdgpu/liverpool.cpp").read_text()
cp_header = (src / "video_core/amdgpu/liverpool.h").read_text()
renderer = (src / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
helper = block(cp, "void Liverpool::WriteFenceValue(")
eop = callback(cp, "EventWriteEop")
eos = callback(cp, "EventWriteEos")
assert "void WriteFenceValue(void* address, u64 data, u32 num_bytes);" in cp_header
assert helper.index("rasterizer->InvalidateMemory(") < helper.index("TryWriteBacking(")
assert "WriteFenceValue(address, data, num_bytes);" in eop
assert "WriteFenceValue(address, data, num_bytes);" in eos
assert "DeferPriorityOperation" not in helper and "SOTC_EOP_DEFER" not in helper

# Reuse the existing deterministic GPU-storage fixture, never its test cases or
# a replacement tracker. Its watcher-only shim observes protection pairing.
tree = ast.parse((here / "test_sotc_readback_completion.py").read_text())
harness = next(ast.literal_eval(n.value) for n in tree.body
               if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
               and t.id == "HARNESS" for t in n.targets))
harness = harness.split("\nint main(){", 1)[0]
tree = ast.parse((here / "test_memory_transaction.py").read_text())
stubs = {}
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "write" and len(node.args) == 2
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in {"core/emulator_settings.h", "video_core/page_manager.h"}):
        stubs[node.args[0].value] = ast.literal_eval(node.args[1])
assert len(stubs) == 2

methods = cache[cache.index("BachataReadback::Span BufferCache::ReadbackWindow("):
                cache.index("void BufferCache::ReadMemory(")]
for marker in ("void BufferCache::InvalidateMemory(", "void BufferCache::MarkGuestWriteWindow(",
               "void BufferCache::ReadMemory("):
    methods += "\n" + block(cache, marker)
download = block(cache, "void BufferCache::DownloadMemory(")
# The exact SotC branch is the exercised implementation. The unrelated legacy
# branch requires additional Vulkan APIs and is an explicit unreachable guard.
download = download[:download.index("    MarkReadbacksDirty(device_addr,size);")]
download += "    (void)arena; assert(false);\n}\n"
methods += "\n" + download
decl = header[header.index("    struct ReadbackItem {"):
              header.index("    bool SynchronizeMemory(")]
decl += """
    void MarkGuestWriteWindow(VAddr,u64);
    void InvalidateMemory(VAddr,u64,bool assume_locks=false,bool guest_fault=false);
    void ReadMemory(VAddr,u64,bool is_write=false,bool assume_locks=false);
    void DownloadMemory(const Buffer*,VAddr,u64);
"""
harness = harness.replace(
    '    std::string_view GameSerial()const{return "CUSA08809";}',
    '    inline static std::string_view serial="CUSA08809";\n'
    "    std::string_view GameSerial()const{return serial;}")
harness = harness.replace("struct Scheduler {\n", """struct Scheduler {
    struct Semaphore {u64 waits{};void Wait(u64){++waits;}} semaphore;
    Semaphore* GetWorkSemaphore(){return &semaphore;}
    void WaitSubmitted(u64,bool){}
""")
harness = harness.replace("struct Memory {\n", """struct Memory {
    bool TryWriteBacking(void* address,const void* source,u64 size) {
        const VAddr a=reinterpret_cast<VAddr>(address);
        assert(a+size<=bytes.size());std::memcpy(bytes.data()+a,source,size);return true;
    }
    u64 Value(VAddr address,u32 size)const {
        u64 value=0;std::memcpy(&value,bytes.data()+address,size);return value;
    }
""")
harness = harness.replace("class BufferCache {\npublic:\n", """class BufferCache {
public:
    struct CommandProcessor {
        bool PrepareGpuSideFault(){return false;}
        template<bool>void SendCommand(auto&& function){function();}
    } commands;
    CommandProcessor* liverpool=&commands;
""")
harness = harness.replace("@DECLARATIONS@", decl).replace("@METHODS@", methods)
harness += """
#define ASSERT(value) assert(value)
namespace Core {
struct Memory {
    inline static VideoCore::Memory* current{};
    static VideoCore::Memory* Instance(){assert(current);return current;}
};
}
namespace Vulkan {
class Rasterizer {
public:
    VideoCore::BufferCache& buffer_cache;
    struct TextureCache {void InvalidateMemory(VAddr,u64){}} texture_cache;
    explicit Rasterizer(VideoCore::BufferCache& value):buffer_cache(value){}
    bool IsMapped(VAddr a,u64 n)const{return n && a+n<=buffer_cache.physical.bytes.size();}
    bool InvalidateMemory(VAddr,u64,bool assume_locks=false,bool guest_fault=false);
};
"""
harness += block(renderer, "bool Rasterizer::InvalidateMemory(") + "\n}\n"
harness += """
namespace AmdGpu {
class Liverpool {
public:
    Vulkan::Rasterizer* rasterizer;
    void WriteFenceValue(void* address,u64 data,u32 num_bytes);
    void PublishEop(VAddr address,u64 value,u32 bytes) {
        auto publish=@EOP@;publish(reinterpret_cast<void*>(address),value,bytes);
    }
    void PublishEos(VAddr address,u64 value,u32 bytes) {
        auto publish=@EOS@;publish(reinterpret_cast<void*>(address),value,bytes);
    }
    void Publish(bool eos,VAddr address,u64 value,u32 bytes) {
        if(eos)PublishEos(address,value,bytes);else PublishEop(address,value,bytes);
    }
};
@HELPER@
}
"""
MAIN = r"""
int main(){
    constexpr VAddr page=0x10000,neighbor=page+128;
    constexpr u64 value=0x1122334455667788ULL;
    u32 cases=0;
    for(const auto title:{"CUSA08809","CUSA08034"}) {
        Common::ElfInfo::serial=title;
        for(bool eos:{false,true})for(u32 bytes:{4u,8u})
        for(VAddr label:{page+32,page+4092,page+16380})for(bool pending:{false,true}) {
            VideoCore::BufferCache cache;
            Core::Memory::current=&cache.physical;
            Vulkan::Rasterizer renderer(cache);AmdGpu::Liverpool cp{&renderer};
            cache.GpuWrite(page,32_KB,0x5a);
            const u64 zero=0,expected=bytes==4?u32(value):value;
            std::memcpy(cache.gpu.bytes.data()+label,&zero,sizeof(zero));
            cache.physical.TryWriteBacking(reinterpret_cast<void*>(label),&zero,sizeof(zero));
            VideoCore::BufferCache::AsyncReadback old{};
            if(pending)cache.BeginAsyncReadback(old,label,bytes,0);
            cp.Publish(eos,label,value,bytes);
            assert(cache.physical.Value(label,bytes)==expected);
            assert(cache.memory_tracker->IsRegionCpuModified(label,bytes));
            assert(!cache.memory_tracker->IsRegionGpuModified(label,bytes));
            if(pending) {
                assert(!cache.FinishAsyncReadback(old));
                assert(!old.staging.buffer->held && cache.inflight_readbacks.empty());
            } else {
                cache.ReadMemory(label,bytes,false,false);
            }
            // This is the value tested by the guest/PM4 wait. The old backing
            // publication path deterministically restored zero at this point.
            assert(cache.physical.Value(label,bytes)==expected);
            assert(cache.physical.bytes[neighbor]==0x5a);
            assert(cache.physical.bytes[page+24_KB]==0x5a);
            // A later bind must not reuse the arena's old label either.
            u64 uploaded=0;
            cache.memory_tracker->ForEachUploadRange(label,bytes,false,
                [&](VAddr a,u64 n){
                    uploaded+=n;
                    std::memcpy(cache.gpu.bytes.data()+a,cache.physical.bytes.data()+a,n);
                },[]{});
            u64 gpu_value=0;std::memcpy(&gpu_value,cache.gpu.bytes.data()+label,bytes);
            assert(uploaded>=bytes && gpu_value==expected);
            ++cases;
        }
        // An uploaded but read-only page still needs CPU dirty publication;
        // it requires no GPU wait when no GPU-owned bytes exist.
        for(bool eos:{false,true})for(u32 bytes:{4u,8u}) {
            VideoCore::BufferCache cache;Core::Memory::current=&cache.physical;
            Vulkan::Rasterizer renderer(cache);AmdGpu::Liverpool cp{&renderer};
            constexpr VAddr label=page+64;
            cache.memory_tracker->ForEachUploadRange(page,4096,false,[](VAddr,u64){},[]{});
            cp.Publish(eos,label,value,bytes);
            assert(cache.memory_tracker->IsRegionCpuModified(label,bytes));
            assert(cache.scheduler.semaphore.waits==0);
            ++cases;
        }
    }
    // Other titles retain the prior behavior; this fix cannot turn their
    // physical fence stores into the SotC readback protocol.
    for(const auto title:{"CUSA00785","UNRELATED"}) {
        Common::ElfInfo::serial=title;
        for(bool eos:{false,true}) {
            VideoCore::BufferCache cache;Core::Memory::current=&cache.physical;
            Vulkan::Rasterizer renderer(cache);AmdGpu::Liverpool cp{&renderer};
            constexpr VAddr label=page+64;
            cache.GpuWrite(page,4096,0);
            cp.Publish(eos,label,value,8);
            assert(cache.physical.Value(label,8)==value);
            assert(cache.memory_tracker->IsRegionGpuModified(label,8));
            assert(!cache.memory_tracker->IsRegionCpuModified(label,8));
            assert(cache.scheduler.semaphore.waits==0);
            ++cases;
        }
    }
    Common::ElfInfo::serial="CUSA08809";
    VideoCore::BufferCache cache;Core::Memory::current=&cache.physical;
    AmdGpu::Liverpool headless{nullptr};
    headless.Publish(false,page,value,8);
    assert(cache.physical.Value(page,8)==value);
    std::cout<<"BACHATA_SOTC_FENCE_PUBLICATION_PASS cases="<<cases+1
             <<" real-EOP/EOS/readback/tracker/retained-snapshot/neighbors/next-upload/title-scope\n";
}
"""
program = harness.replace("@HELPER@", helper).replace("@EOP@", eop).replace("@EOS@", eos) + MAIN
invalidate = "        rasterizer->InvalidateMemory(std::bit_cast<VAddr>(address), num_bytes, true);"
assert helper.count(invalidate) == 1
write = "    ASSERT(memory->TryWriteBacking(address, &data, num_bytes));"
assert helper.count(write) == 1
after = helper.replace(invalidate, "").replace(
    write, write + "\n    if(rasterizer)rasterizer->InvalidateMemory("
    "std::bit_cast<VAddr>(address), num_bytes, true);")
raw = """auto* memory = Core::Memory::Instance();
        ASSERT(memory->TryWriteBacking(address, &data, num_bytes));"""
variants = [
    ("actual", program, True),
    ("missing_invalidation", program.replace(helper, helper.replace(invalidate, "")), False),
    ("invalidation_after_store", program.replace(helper, after), False),
    ("eop_bypasses_helper", program.replace(eop, eop.replace(
        "WriteFenceValue(address, data, num_bytes);", raw)), False),
    ("eos_bypasses_helper", program.replace(eos, eos.replace(
        "WriteFenceValue(address, data, num_bytes);", raw)), False),
]
# EOP/EOS lambdas have identical bodies; replace only their named method when
# exercising a single missing caller, not every identical lambda occurrence.
for index, event in ((3, "Eop"), (4, "Eos")):
    method = block(program, f"    void Publish{event}(")
    variants[index] = (variants[index][0], program.replace(method, method.replace(
        "WriteFenceValue(address, data, num_bytes);", raw)), False)

with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    for name, content in stubs.items():
        path = temp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for name, content, success in variants:
        cpp = temp / (name + ".cpp")
        binary = temp / name
        cpp.write_text(content)
        subprocess.run(["c++", "-std=c++23", "-O1", "-pthread", "-Wall", "-Wextra", "-Werror",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all", "-I", str(temp),
                        "-isystem", str(src), str(cpp), "-o", str(binary)], check=True)
        result = subprocess.run([str(binary)], timeout=20, capture_output=True, text=True,
            env={**os.environ, "SOTC_RB_HOT": "0", "SOTC_RB_NARROW": "64",
                 "SOTC_RB_STREAM_MAX_KB": "64", "SOTC_FAULT_GRACE": "0"})
        assert (result.returncode == 0) == success, (name, result.stdout, result.stderr)
        if success:
            print(result.stdout.strip())
        else:
            assert "Assertion" in result.stderr, (name, result.stderr)
            print("BACHATA_SOTC_FENCE_NEGATIVE_PASS " + name)
