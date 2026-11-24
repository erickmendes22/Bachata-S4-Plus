"""Generate native code from SRT1 cache, with checked guest-memory callbacks."""
from pathlib import Path
import shutil

def apply(root:Path):
    rel="src/shader_recompiler/ir/passes/"
    p=root/(rel+"flatten_extended_userdata_pass.cpp")
    shutil.copyfile(Path(__file__).with_name("srt_native_checked.h"),root/(rel+"srt_native_checked.h"))
    s=p.read_text()
    def edit(old,new):
        nonlocal s
        if s.count(old)!=1: raise RuntimeError("checked SRT JIT drift: "+old[:120])
        s=s.replace(old,new,1)
    edit('#include "core/memory.h"','#include "core/memory.h"\n#include "shader_recompiler/ir/passes/srt_native_checked.h"')
    edit('std::deque<std::unique_ptr<u32[]>> g_walkers;',
r'''std::deque<std::unique_ptr<u32[]>> g_walkers;
using CheckedNative=Shader::CheckedArm64Srt::Native;
std::deque<std::unique_ptr<CheckedNative>> g_native_walkers;
static_assert(static_cast<u32>(SrtOp::End)==Shader::CheckedArm64Srt::End &&
              static_cast<u32>(SrtOp::PopPtr)==Shader::CheckedArm64Srt::PopPtr &&
              static_cast<u32>(SrtOp::Bfe)==Shader::CheckedArm64Srt::Bfe);
struct NativeContext { u32* flat; std::vector<VAddr>& sources; };
u64 CheckedPush(void*,u64,u32,u32,u32);
void CheckedCopy(void*,u64,u32,u32,u32,u32,u32);
constexpr size_t NativePrefix=(sizeof(CheckedNative*)+sizeof(u32)-1)/sizeof(u32);''')
    edit('''    auto copy = std::make_unique<u32[]>(words);
    std::memcpy(copy.get(), code, words * sizeof(u32));
    std::scoped_lock lock{g_walker_mutex};
    return g_walkers.emplace_back(std::move(copy)).get();''',
r'''    // Runtime-only prefix; persisted data still starts with SRT1.
    auto copy=std::make_unique<u32[]>(words+NativePrefix);
    auto native=BachataCompat::Sotc608()?nullptr:
        CheckedNative::Create({code,words},CheckedPush,CheckedCopy);
    const CheckedNative* entry=native.get();
    std::memcpy(copy.get(),&entry,sizeof(entry));
    std::memcpy(copy.get()+NativePrefix,code,words*sizeof(u32));
    std::scoped_lock lock{g_walker_mutex};
    if(native)g_native_walkers.emplace_back(std::move(native));
    return g_walkers.emplace_back(std::move(copy)).get()+NativePrefix;''')
    edit('void DumpSrtProgram(const Shader::Info& info, const u32* code, size_t words) {',
r'''u64 CheckedPush(void* opaque,u64 cur,u32 off,u32 zero,u32 opcode) {
    auto& ctx=*static_cast<NativeContext*>(opaque);
    if(zero||cur<0x10000ULL)return 0;
    u64 next{};
    const u64 address=cur+u32(off<<2);
    if(!TryReadGuest(address,ctx.flat,next)) {
        LOG_WARNING(Render_Recompiler,"BIONIC_PORTABLE_SRT_BAD_POINTER: opcode={} address={:#x}",
                    opcode,address);
        next=0;
    }
    const u64 local=reinterpret_cast<u64>(ctx.flat);
    if(address>=0x10000&&address<0x10000000000ULL-7&&
       !(address>=local&&address<local+16*sizeof(u32))) {
        ctx.sources.push_back(address);ctx.sources.push_back(address+sizeof(u32));
    }
    return next&0xFFFFFFFFFFFFULL;
}
void CheckedCopy(void* opaque,u64 cur,u32 off,u32 b,u32 count,u32 zero,u32 opcode) {
    auto& ctx=*static_cast<NativeContext*>(opaque);
    if(count>1&&!zero&&cur>=0x10000ULL) {
        const u64 address=cur+u32(off<<2);
        if(Core::Memory::Instance()->TryReadBacking(address,ctx.flat+b,count*sizeof(u32))) {
            for(u32 j=0;j<count;++j)ctx.sources[b+j]=address+j*sizeof(u32);
            return;
        }
    }
    for(u32 j=0;j<count;++j) {
        ctx.sources[b+j]=0;
        u32 value{};
        if(!zero&&cur>=0x10000ULL) {
            const u64 address=cur+u32((off+j)<<2);
            if(TryReadGuest(address,ctx.flat,value))ctx.sources[b+j]=address;
            else {
                LOG_WARNING(Render_Recompiler,"BIONIC_PORTABLE_SRT_BAD_READ: opcode={} address={:#x}",
                            opcode+j,address);
                value=0;
            }
        }
        ctx.flat[b+j]=value;
    }
}
void DumpSrtProgram(const Shader::Info& info, const u32* code, size_t words) {''')
    edit('''    static_cast<void>(user_data);
    u32* const ops = const_cast<u32*>(code) + 1;''',
r'''    static_cast<void>(user_data);
    if(!BachataCompat::Sotc608()) {
        const CheckedNative* native{};
        std::memcpy(&native,code-NativePrefix,sizeof(native));
        if(native&&native->flat_count<=source_addresses.size()) {
            source_addresses.reserve(source_addresses.size()+native->parent_words);
            NativeContext context{flat,source_addresses};
            static const bool reported=[] {
                LOG_INFO(Render_Recompiler,"BACHATA_CHECKED_ARM64_SRT_JIT_ACTIVE");
                return true;
            }();
            (void)reported;
            native->run(&context,flat);
            return;
        }
    }
    u32* const ops = const_cast<u32*>(code) + 1;''')
    p.write_text(s)
    return {"native":"ARM64 expressions and checked guest callbacks; W^X; interpreter fallback",
            "cache":"SRT1 portable bytes; code regenerated; SotC unchanged"}
