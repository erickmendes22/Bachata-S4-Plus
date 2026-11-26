#!/usr/bin/env python3
"""Execute the effective FIOS HLE and real FEX callback argument encoder.

Only the file/backend and Linker execution boundaries are substituted. The HLE
helpers, async entrypoints, queries and callback bridge come from the generated
source, not a second implementation. No game executable is needed for this ABI
contract. This is not a test of actual FEX translation or Android gameplay.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def function(text, signature):
    if text.count(signature) != 1:
        raise AssertionError(f"FIOS source drift {signature}: {text.count(signature)}")
    start = text.index(signature)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[start:end + 1]
    raise AssertionError("unclosed " + signature)


def program(root):
    cpp = (root / "src/core/libraries/fios2/fios2.cpp").read_text()
    callback = (root / "src/core/guest_cpu/guest_callback.h").read_text()
    callback = re.sub(r'^\s*#(?:include|pragma)[^\n]*\n', '', callback, flags=re.M)
    begin = cpp.index("namespace {\nstd::mutex g_op_mutex;")
    end = cpp.index("} // namespace", begin) + len("} // namespace")
    helpers = cpp[begin:end]
    names = ["sceFiosFHOpen", "sceFiosFHPread", "sceFiosFHRead", "sceFiosFHClose",
             "sceFiosFHPwrite", "sceFiosArchiveGetMountBufferSize", "sceFiosArchiveMount",
             "sceFiosArchiveUnmountSync", "sceFiosArchiveUnmount",
             "sceFiosDirectoryCreateSync", "sceFiosDirectoryCreate", "sceFiosDHOpenSync",
             "sceFiosDHOpen", "sceFiosDeleteSync", "sceFiosDelete", "sceFiosStat", "sceFiosOpWait", "sceFiosOpWaitUntil",
             "sceFiosOpSyncWait", "sceFiosOpGetActualCount", "sceFiosOpGetError",
             "sceFiosOpIsDone", "sceFiosOpDelete"]
    methods = "\n".join(function(cpp, f"{'s64' if n == 'sceFiosOpGetActualCount' else 's32'} PS4_SYSV_ABI {n}(")
                         for n in names)
    # These registered async entrypoints must continue using the common helper.
    for name in names:
        if name.startswith("sceFiosOp") or name.endswith("Sync"):
            continue
        body = function(methods, f"s32 PS4_SYSV_ABI {name}(")
        if "CompleteAsyncOp(" not in body:
            raise AssertionError("async completion missing: " + name)
    prelude = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <mutex>
#include <span>
#include <string>
#include <string_view>
#include <type_traits>
#include <unordered_map>
#include <variant>
#include <vector>
#include <sys/mman.h>
using s32=int32_t;using s64=int64_t;using u8=uint8_t;using u32=uint32_t;
using u64=uint64_t;using VAddr=uint64_t;
#define PS4_SYSV_ABI __attribute__((sysv_abi))
#if FIOS_TEST_FEX
#define SHADPS4_ENABLE_FEX_GUEST_CPU 1
#endif
volatile u64 log_checksum=0;
template<class T>void ConsumeOne(const T& value){
    if constexpr(std::is_convertible_v<T,const char*>){
        const char* text=value;
        if(text)log_checksum=log_checksum+std::strlen(text);
    }
}
template<class... T>void Consume(const T&... values){(ConsumeOne(values),...);}
constexpr int Lib_SysModule=1,Core_Linker=2;
#define LOG_INFO(...) Consume(__VA_ARGS__)
#define LOG_WARNING(...) Consume(__VA_ARGS__)
#define LOG_ERROR(...) Consume(__VA_ARGS__)
#define LOG_CRITICAL(...) Consume(__VA_ARGS__)
using TestCallback=s32 PS4_SYSV_ABI (*)(void*,s32,u8,s32);
namespace Core {
struct GuestExecutionFailure{int Stage;std::string Error;};
class Linker {
public:
    bool guest=false;u32 calls=0;std::vector<u64> registers;
    void* FindByAddress(VAddr) {return guest ? this : nullptr;}
    std::variant<u64,GuestExecutionFailure> RunGuestFunction(VAddr fn,
            std::span<const u64> args,VAddr) {
        assert(guest && args.size()==4);++calls;
        registers.assign(args.begin(),args.end());
        auto cb=reinterpret_cast<TestCallback>(fn);
        return static_cast<u64>(cb(reinterpret_cast<void*>(args[0]),
            static_cast<s32>(args[1]),static_cast<u8>(args[2]),static_cast<s32>(args[3])));
    }
};
}
namespace Common {
template<class T>struct Singleton{static T* Instance(){static T value;return &value;}};
}
@GUEST_CALLBACK@
namespace Libraries::Kernel {
std::vector<u8> file(8192);s32 open_result=4,close_result=0;
s64 read_result=4096,write_result=7,seek_result=0;u32 reads=0,writes=0;
s32 posix_open(const char*,s32,s32){return open_result;}
s32 posix_close(s32){return close_result;}
s32 posix_unlink(const char*){return 0;}
s64 sceKernelRead(s32,void* buffer,u64 size){
    ++reads;assert(size<=file.size());
    if(read_result<0)return read_result;
    const auto count=std::min(size,static_cast<u64>(read_result));
    std::memcpy(buffer,file.data(),count);return count;
}
s64 sceKernelPread(s32 fd,void* buffer,u64 size,s64 offset){
    assert(offset>=0);return sceKernelRead(fd,buffer,size);
}
s64 sceKernelPwrite(s32,void*,u64 size,s64 offset){
    ++writes;assert(size<=file.size() && offset>=0);return write_result;
}
s64 posix_lseek(s32,s64,s32){return seek_result;}
s64 sceKernelWrite(s32,const void*,u64 size){
    ++writes;assert(size<=file.size());return write_result;
}
}
namespace Libraries::Fios2 {
@HELPERS@
struct FiosStat {s64 size;};
s32 backend_status=0;s64 archive_size=0x100001003LL;
s64 sceFiosArchiveGetMountBufferSizeSync(const void*,const char*,const void*){
    return backend_status<0 ? backend_status : archive_size;
}
s32 sceFiosArchiveMountSync(const void*,s32* handle,const char*,const char*,void*,s64,s32){
    if(handle)*handle=backend_status<0?-1:1;
    return backend_status;
}
s32 sceFiosStatSync(const void*,const char*,FiosStat* stat){
    if(stat)stat->size=8192;
    return backend_status;
}
@METHODS@
}
using namespace Libraries::Fios2;
struct State {
    s64 expected_count=0;s32 expected_error=0;int completed=0;
    bool nested=false,erase=false;FiosOpAttr* release_attr=nullptr;s32* handle=nullptr;
    char* release_path=nullptr;
    s32 op=0;
};
s32 PS4_SYSV_ABI Completed(void* pointer,s32 op,u8 event,s32 error) {
    auto& s=*static_cast<State*>(pointer);
    // This consumer deliberately ignores events other than COMPLETE, as a game
    // event dispatcher does. With the old ABI, FHOpen never wakes it.
    if(event!=1)return 0;
    assert(error==s.expected_error);++s.completed;s.op=op;
    if(error==0){
        assert(op>0);assert(QueryOpActualCount(op)==s.expected_count);
        assert(sceFiosOpGetActualCount(op)==s.expected_count);
        assert(sceFiosOpGetError(op)==0 && sceFiosOpIsDone(op)==1);
        assert(sceFiosOpWait(op)==0 && sceFiosOpWaitUntil(op,1)==0 && sceFiosOpSyncWait(op)==0);
        if(s.handle)assert(*s.handle==4);
    } else {
        assert(op==error && QueryOpActualCount(op)==error);
        assert(sceFiosOpGetError(op)==error && sceFiosOpWait(op)==error);
    }
    if(s.nested){
        State child;child.expected_count=16;
        FiosOpAttr attr{};attr.p_callback=reinterpret_cast<void*>(Completed);
        attr.p_callback_context=&child;std::array<u8,16> bytes{};
        const s32 next=sceFiosFHRead(&attr,4,bytes.data(),bytes.size());
        assert(next>op && child.completed==1 && bytes[9]==Libraries::Kernel::file[9]);
    }
    if(s.erase)assert(sceFiosOpDelete(op)==0);
    if(s.release_path){assert(munmap(s.release_path,4096)==0);s.release_path=nullptr;}
    delete s.release_attr;s.release_attr=nullptr;
    return 17; // A callback status must not replace the I/O operation result.
}
FiosOpAttr Attributes(State& s){
    FiosOpAttr a{};a.deadline=1;a.p_callback=reinterpret_cast<void*>(Completed);
    a.p_callback_context=&s;a.priority_and_flags=0x7e;return a;
}
int main(){
    auto* linker=Common::Singleton<Core::Linker>::Instance();
    for(size_t i=0;i<Libraries::Kernel::file.size();++i)Libraries::Kernel::file[i]=i%251;
    int scenarios=0;
    for(bool guest:{false,true}){
#if !FIOS_TEST_FEX
        if(guest)continue;
#endif
        linker->guest=guest;
        for(s64 count:{s64{0},s64{1},s64{4096},(s64{1}<<34)+7}){
            State s;s.expected_count=count;auto a=Attributes(s);
            const s32 op=CompleteAsyncOp(&a,count);
            assert(op>0 && s.completed==1 && s.op==op);
            if(guest){assert(linker->registers[2]==1 && linker->registers[3]==0);}
            ++scenarios;
        }
        {State s;auto a=Attributes(s);s32 fd=-1;s.handle=&fd;s.nested=true;
         const s32 op=sceFiosFHOpen(&a,&fd,"/app0/art/cache/all_shaders.xpps",nullptr);
         assert(op>0 && fd==4 && s.completed==1);++scenarios;}
        {State s;auto a=Attributes(s);s32 fd=-1;s.handle=&fd;
         s.release_path=static_cast<char*>(mmap(nullptr,4096,PROT_READ|PROT_WRITE,
                                              MAP_PRIVATE|MAP_ANONYMOUS,-1,0));
         assert(s.release_path!=MAP_FAILED);
         std::strcpy(s.release_path,"/app0/art/cache/all_shaders.xpps");
         const s32 op=sceFiosFHOpen(&a,&fd,s.release_path,nullptr);
         assert(op>0 && fd==4 && s.completed==1 && s.release_path==nullptr);++scenarios;}
        {State s;s.expected_error=-13;auto a=Attributes(s);s32 fd=91;
         Libraries::Kernel::open_result=-13;
         assert(sceFiosFHOpen(&a,&fd,"missing",nullptr)==-13);
         assert(fd==-1 && s.completed==1);
         if(guest){assert(linker->registers[2]==1 && static_cast<s32>(linker->registers[3])==-13);}
         Libraries::Kernel::open_result=4;++scenarios;}
        std::array<u8,4096> bytes{};
        {State s;s.expected_count=4096;auto a=Attributes(s);
         assert(sceFiosFHPread(&a,4,bytes.data(),bytes.size(),0)>0 && s.completed==1);
         assert(bytes[250]==250 && bytes[251]==0);++scenarios;}
        for(bool positioned:{false,true}){
            State s;s.expected_error=-1;auto a=Attributes(s);auto before=Libraries::Kernel::reads;
            const auto op=positioned?sceFiosFHPread(&a,4,bytes.data(),-1,0):
                                     sceFiosFHRead(&a,4,bytes.data(),-1);
            assert(op==-1 && s.completed==1 && Libraries::Kernel::reads==before);++scenarios;
        }
        {State s;auto a=Attributes(s);assert(sceFiosFHClose(&a,4)>0 && s.completed==1);++scenarios;}
        {State s;s.expected_count=7;auto a=Attributes(s);
         assert(sceFiosFHPwrite(&a,4,bytes.data(),7,0)>0 && s.completed==1);++scenarios;}
        for(bool invalid:{false,true}){
            State s;s.expected_error=invalid?-1:-9;auto a=Attributes(s);
            Libraries::Kernel::write_result=-9;Libraries::Kernel::seek_result=-9;
            const auto before=Libraries::Kernel::writes;
            assert(sceFiosFHPwrite(&a,4,bytes.data(),invalid?-1:7,0)==s.expected_error);
            assert(s.completed==1);if(invalid)assert(before==Libraries::Kernel::writes);
            Libraries::Kernel::write_result=7;Libraries::Kernel::seek_result=0;++scenarios;
        }
        for(s32 status:{0,-13}){
            backend_status=status;
            {State s;s.expected_count=archive_size;s.expected_error=status;auto a=Attributes(s);
             auto op=sceFiosArchiveGetMountBufferSize(&a,"archive",nullptr);
             assert((status<0?op==status:op>0) && s.completed==1);++scenarios;}
            {State s;s.expected_error=status;auto a=Attributes(s);s32 handle=-1;
             auto op=sceFiosArchiveMount(&a,&handle,"archive","/mount",nullptr,0,0);
             assert((status<0?op==status:op>0) && s.completed==1);++scenarios;}
            {State s;s.expected_error=status;auto a=Attributes(s);FiosStat stat{};
             auto op=sceFiosStat(&a,"file",&stat);
             assert((status<0?op==status:op>0) && s.completed==1);++scenarios;}
        }
        backend_status=0;
        {State s;auto a=Attributes(s);assert(sceFiosArchiveUnmountSync(&a,1)==0 && s.completed==0);
         assert(sceFiosArchiveUnmount(&a,1)>0 && s.completed==1);++scenarios;}
        for(bool valid:{false,true}){
            State s;s.expected_error=valid?0:-1;auto a=Attributes(s);
            auto op=sceFiosDirectoryCreate(&a,valid?"directory":nullptr);
            assert((valid?op>0:op==-1) && s.completed==1);++scenarios;
            s.completed=0;
            op=sceFiosDelete(&a,valid?"file":nullptr);
            assert((valid?op>0:op==-1) && s.completed==1);++scenarios;
        }
        {State s;s.expected_error=-1;auto a=Attributes(s);s32 handle=91;
         assert(sceFiosDHOpen(&a,&handle,"directory",nullptr)==-1);
         assert(s.completed==1 && handle==-1);++scenarios;}
        {State s;s.expected_count=7;s.erase=true;s.release_attr=new FiosOpAttr(Attributes(s));
         auto op=CompleteAsyncOp(s.release_attr,7);assert(op>0 && s.completed==1);
         assert(g_op_actual_counts.find(op)==g_op_actual_counts.end());++scenarios;}
        {State s;auto a=Attributes(s);a.p_callback=nullptr;
         assert(CompleteAsyncOp(&a,8)>0 && s.completed==0);
         assert(CompleteAsyncOp(nullptr,9)>0);++scenarios;}
    }
#if FIOS_TEST_FEX
    assert(linker->calls>20);
#else
    assert(linker->calls==0);
#endif
    std::cout<<"scenarios="<<scenarios<<" guest_bridge_calls="<<linker->calls<<"\n";
}
'''
    return prelude.replace("@GUEST_CALLBACK@", callback).replace("@HELPERS@", helpers).replace("@METHODS@", methods)


def run_case(tmp, name, source, fex=1, expect_pass=True):
    cpp = tmp / (name + ".cpp")
    exe = tmp / name
    cpp.write_text(source)
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        raise RuntimeError("C++ compiler required for FIOS ABI gate")
    build = subprocess.run([compiler, "-std=c++20", "-O1", "-pthread", "-Wall", "-Wextra",
                            "-Werror", f"-DFIOS_TEST_FEX={fex}", str(cpp), "-o", str(exe)],
                           text=True, capture_output=True, timeout=60)
    if build.returncode:
        raise AssertionError(f"{name} failed to compile (not a negative control):\n{build.stderr}")
    try:
        result = subprocess.run([str(exe)], text=True, capture_output=True, timeout=5)
    except subprocess.TimeoutExpired:
        if expect_pass:
            raise
        return "blocked as expected"
    if expect_pass != (result.returncode == 0):
        raise AssertionError(f"{name}: unexpected status {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip() if expect_pass else "rejected at runtime"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    text = program(args.source.resolve())
    mutations = {
        "complete_event_zero": ("constexpr u8 FiosOpEventComplete = 1;", "constexpr u8 FiosOpEventComplete = 0;"),
        "native_old_arguments": ("cb(context, op, FiosOpEventComplete, err)", "cb(context, op, static_cast<u8>(err), static_cast<s32>(result))"),
        "fex_old_arguments": ('callback, "sceFiosOpCallback", context, op, FiosOpEventComplete, err',
                              'callback, "sceFiosOpCallback", context, op, static_cast<u8>(err), result'),
        "truncate_count": ("g_op_actual_counts[op] = actual_count;", "g_op_actual_counts[op] = static_cast<s32>(actual_count);"),
        "lose_error": ("MaybeInvokeOpCallback(op_attr, err, err, 0);", "MaybeInvokeOpCallback(op_attr, err, 0, 0);"),
        "write_missing_callback": ("const s32 op = CompleteAsyncOp(op_attr, written);", "const s32 op = AllocateOpHandle(written);"),
        "size_returns_bytes": ("return CompleteAsyncOp(op_attr, result);", "return static_cast<s32>(result);"),
        "published_after_callback": ("MaybeInvokeOpCallback(op_attr, op, 0, actual_count);", "g_op_actual_counts.erase(op);\n    MaybeInvokeOpCallback(op_attr, op, 0, actual_count);\n    g_op_actual_counts[op]=actual_count;"),
        "callback_under_lock": ("MaybeInvokeOpCallback(op_attr, op, 0, actual_count);", "std::scoped_lock held{g_op_mutex};\n    MaybeInvokeOpCallback(op_attr, op, 0, actual_count);"),
        "path_used_after_callback": (
            '''    LOG_INFO(Lib_SysModule,
             "[FIOS-HLE][FHOpen] path='{}' handle={} op_attr={} open_params={}", path, fd,
             op_attr, open_params);
    return CompleteAsyncOp(op_attr, 0);''',
            '''    const auto op = CompleteAsyncOp(op_attr, 0);
    LOG_INFO(Lib_SysModule,
             "[FIOS-HLE][FHOpen] path='{}' handle={} op_attr={} open_params={}", path, fd,
             op_attr, open_params);
    return op;'''),
    }
    results = {}
    with tempfile.TemporaryDirectory(prefix="bachata-fios-abi-") as directory:
        tmp = Path(directory)
        results["native"] = run_case(tmp, "native", text, fex=0)
        results["fex_argument_bridge"] = run_case(tmp, "fex", text)
        for name, (old, new) in mutations.items():
            if text.count(old) != 1:
                raise AssertionError(f"mutation anchor {name}: {text.count(old)}")
            results[name] = run_case(tmp, name, text.replace(old, new, 1), expect_pass=False)
        # Every additional async wrapper can independently strand a callback user.
        for name in ["sceFiosArchiveMount", "sceFiosArchiveUnmount", "sceFiosDirectoryCreate",
                     "sceFiosDHOpen", "sceFiosDelete", "sceFiosStat"]:
            body = function(text, "s32 PS4_SYSV_ABI " + name + "(")
            old = "return CompleteAsyncOp(op_attr, result < 0 ? result : 0);"
            assert body.count(old) == 1
            broken = body.replace(old, "return result >= 0 ? AllocateOpHandle(0) : result;")
            results[name + "_missing_callback"] = run_case(
                tmp, name, text.replace(body, broken, 1), expect_pass=False)
    print(json.dumps({"gate": "common FIOS completion ABI", "results": results,
                      "negativeControls": len(results) - 2, "androidGameplayTested": False}, indent=2))


if __name__ == "__main__":
    main()
