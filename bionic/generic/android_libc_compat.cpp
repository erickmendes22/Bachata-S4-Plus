// SPDX-License-Identifier: GPL-2.0-or-later
// PS4 libc compatibility functions for the Android/FEX guest. Only direct
// x86-64 SysV ABI-compatible functions are aliased. Callback-driven setjmp,
// qsort, FILE objects and iostream globals require separate guest semantics.
#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <limits>
#include <memory>
#include <string>
#include <vector>

#include "core/libraries/libs.h"
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
#include "common/va_ctx.h"
#include "core/libraries/libc_internal/printf.h"
#include "core/libraries/libc_internal/libc_internal_io.h"
#include "core/libraries/kernel/file_system.h"
#include "core/memory.h"

namespace Libraries::LibcInternal {
void* FexLibcGuestAllocate(std::size_t bytes);
namespace {
bool GuestAccess(std::uintptr_t address, std::size_t count, bool write) {
    if (count == 0) return true;
    if (!address || count > std::numeric_limits<std::uintptr_t>::max() - address) return false;
    auto* memory = Core::Memory::Instance();
    void* begin{};
    void* end{};
    u32 protection{};
    if (memory->QueryProtection(address, &begin, &end, &protection) != 0) return false;
    if (address < reinterpret_cast<std::uintptr_t>(begin) ||
        count > reinterpret_cast<std::uintptr_t>(end) - address) return false;
    const auto required = static_cast<u32>(write ? Core::MemoryProt::CpuWrite :
                                                  Core::MemoryProt::CpuRead);
    return (protection & required) != 0;
}

bool GuestString(const char* ptr, std::size_t cap, std::string& result) {
    if (!ptr) return false;
    const auto start = reinterpret_cast<std::uintptr_t>(ptr);
    std::size_t scanned = 0;
    while (scanned < cap) {
        const auto addr = start + scanned;
        if (addr < start) return false;
        auto* memory = Core::Memory::Instance();
        void* begin{};
        void* end{};
        u32 protection{};
        if (memory->QueryProtection(addr, &begin, &end, &protection) != 0 ||
            !(protection & static_cast<u32>(Core::MemoryProt::CpuRead))) return false;
        const auto last = reinterpret_cast<std::uintptr_t>(end);
        if (addr >= last) return false;
        const auto length = std::min(cap - scanned, last - addr);
        const void* nul = std::memchr(reinterpret_cast<const void*>(addr), 0, length);
        const auto bytes = nul ? reinterpret_cast<std::uintptr_t>(nul) - addr : length;
        result.append(reinterpret_cast<const char*>(addr), bytes);
        if (nul) return true;
        scanned += length;
    }
    return false;
}

int PS4_SYSV_ABI GuestPuts(const char* str) {
    std::string text;
    if (!GuestString(str, 1024 * 1024, text)) return EOF;
    if (std::fwrite(text.data(), 1, text.size(), stdout) != text.size()) return EOF;
    if (std::fputc('\n', stdout) == EOF) return EOF;
    return static_cast<int>(text.size() + 1);
}
int PS4_SYSV_ABI GuestPutchar(int ch) { return std::putchar(ch); }

char* PS4_SYSV_ABI GuestStrerror(int code) {
    thread_local char* output = nullptr;
    if (!output) output = static_cast<char*>(FexLibcGuestAllocate(256));
    if (!output) return nullptr;
    const char* message = std::strerror(code);
    std::snprintf(output, 256, "%s", message ? message : "Unknown error");
    return output;
}
char* PS4_SYSV_ABI GuestStrdup(const char* input) {
    std::string value;
    if (!GuestString(input, 1024 * 1024, value)) return nullptr;
    char* output = static_cast<char*>(FexLibcGuestAllocate(value.size() + 1));
    if (!output) return nullptr;
    std::memcpy(output, value.c_str(), value.size() + 1);
    return output;
}

std::size_t PS4_SYSV_ABI GuestStrnlen(const char* s, std::size_t n) {
    if (n == 0) return 0;
    std::string text;
    if (GuestString(s, std::min<std::size_t>(n, 1024 * 1024), text))
        return text.size();
    return std::min<std::size_t>(n, 1024 * 1024);
}
char* PS4_SYSV_ABI GuestStrncpy(char* d, const char* s, std::size_t n) {
    if (n && !GuestAccess(reinterpret_cast<std::uintptr_t>(d), n, true)) return nullptr;
    return std::strncpy(d, s, n);
}
int PS4_SYSV_ABI GuestStrncmp(const char* a, const char* b, std::size_t n) {
    return std::strncmp(a, b, n);
}
char* PS4_SYSV_ABI GuestStrncat(char* d, const char* s, std::size_t n) {
    return std::strncat(d, s, n);
}
const char* PS4_SYSV_ABI GuestStrrchr(const char* s, int ch) {
    return std::strrchr(s, ch);
}
const char* PS4_SYSV_ABI GuestStrchr(const char* s, int ch) {
    return std::strchr(s, ch);
}
std::size_t PS4_SYSV_ABI GuestStrcspn(const char* a, const char* b) {
    return std::strcspn(a, b);
}
int PS4_SYSV_ABI GuestStrcoll(const char* a, const char* b) {
    return std::strcoll(a, b);
}
std::size_t PS4_SYSV_ABI GuestStrlcpy(char* d, const char* s, std::size_t cap) {
    std::string text;
    if (!GuestString(s, 1024 * 1024, text)) return 0;
    if (cap) {
        if (!GuestAccess(reinterpret_cast<std::uintptr_t>(d), cap, true)) return 0;
        const auto copied = std::min(text.size(), cap - 1);
        std::memcpy(d, text.data(), copied);
        d[copied] = 0;
    }
    return text.size();
}
std::uint64_t PS4_SYSV_ABI GuestStrtoumax(const char* s, char** end, int radix) {
    return std::strtoull(s, end, radix);
}
int PS4_SYSV_ABI GuestRand() { return std::rand(); }
void PS4_SYSV_ABI GuestSrand(unsigned seed) { std::srand(seed); }
std::int64_t PS4_SYSV_ABI GuestTime(std::int64_t* out) {
    const std::int64_t now = static_cast<std::int64_t>(std::time(nullptr));
    if (out && GuestAccess(reinterpret_cast<std::uintptr_t>(out), sizeof(*out), true))
        *out = now;
    return now;
}
double PS4_SYSV_ABI GuestDifftime(std::int64_t b, std::int64_t a) {
    return std::difftime(static_cast<std::time_t>(b), static_cast<std::time_t>(a));
}

#define MATH_U64(name, call) double PS4_SYSV_ABI Fex_##name(double x) { return std::call(x); }
#define MATH_F32(name, call) float PS4_SYSV_ABI Fex_##name(float x) { return std::call(x); }
#define MATH_BIN64(name, call) double PS4_SYSV_ABI Fex_##name(double x, double y) { return std::call(x, y); }
#define MATH_BIN32(name, call) float PS4_SYSV_ABI Fex_##name(float x, float y) { return std::call(x, y); }
MATH_U64(sin, sin)
MATH_F32(sinf, sin)
MATH_U64(cos, cos)
MATH_F32(cosf, cos)
MATH_U64(tan, tan)
MATH_U64(asin, asin)
MATH_U64(acos, acos)
MATH_U64(atan, atan)
MATH_F32(atanf, atan)
MATH_U64(exp, exp)
MATH_F32(expf, exp)
MATH_F32(exp2f, exp2)
MATH_U64(log, log)
MATH_U64(log10, log10)
MATH_U64(tanh, tanh)
MATH_F32(tanhf, tanh)
MATH_BIN64(atan2, atan2)
MATH_BIN64(pow, pow)
MATH_BIN32(powf, pow)
MATH_BIN64(fmod, fmod)
MATH_BIN32(fmodf, fmod)
float PS4_SYSV_ABI Fex_frexpf(float value, int* out) {
    if (!out || !GuestAccess(reinterpret_cast<std::uintptr_t>(out), sizeof(*out), true)) return 0.0f;
    return std::frexp(value, out);
}
float PS4_SYSV_ABI Fex_ldexpf(float value, int exponent) {
    return std::ldexp(value, exponent);
}
float PS4_SYSV_ABI Fex_modff(float value, float* out) {
    if (!out || !GuestAccess(reinterpret_cast<std::uintptr_t>(out), sizeof(*out), true)) return 0.0f;
    return std::modf(value, out);
}


OrbisFILE* PS4_SYSV_ABI GuestFopen(const char* path, const char* mode) {
    return internal_fopen(path, mode);
}
int PS4_SYSV_ABI GuestFclose(OrbisFILE* file) { return internal_fclose(file); }
std::size_t PS4_SYSV_ABI GuestFread(void* dst, std::size_t size,
                                    std::size_t count, OrbisFILE* file) {
    if (!file || !GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                               sizeof(*file), true)) return 0;
    if (size && count > std::numeric_limits<std::size_t>::max() / size) return 0;
    if (size && count && !GuestAccess(reinterpret_cast<std::uintptr_t>(dst),
                                       size * count, true)) return 0;
    return internal_fread(static_cast<char*>(dst), size, count, file);
}
std::size_t PS4_SYSV_ABI GuestFwrite(const void* src, std::size_t size,
                                     std::size_t count, OrbisFILE* file) {
    if (!file || !GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                               sizeof(*file), true) || file->_Handle < 0) return 0;
    if (!size || !count || count > std::numeric_limits<std::size_t>::max() / size)
        return 0;
    const auto bytes = size * count;
    if (!GuestAccess(reinterpret_cast<std::uintptr_t>(src), bytes, false)) return 0;
    const auto written = Libraries::Kernel::sceKernelWrite(file->_Handle, src, bytes);
    if (written < 0) {
        file->_Mode |= 0x200;
        return 0;
    }
    return static_cast<std::size_t>(written) / size;
}
int PS4_SYSV_ABI GuestFputs(const char* str, OrbisFILE* file) {
    std::string value;
    if (!GuestString(str, 1024 * 1024, value) || !file ||
        !GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                     sizeof(*file), true) || file->_Handle < 0) return EOF;
    const auto written = Libraries::Kernel::sceKernelWrite(file->_Handle,
                                                           value.data(), value.size());
    return written == static_cast<std::int64_t>(value.size()) ? 0 : EOF;
}
int PS4_SYSV_ABI GuestFgetc(OrbisFILE* file) {
    if (!file || !GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                              sizeof(*file), true)) return EOF;
    char ch{};
    // Internal read executes on the host and uses a native stack temporary.
    return internal_fread(&ch, 1, 1, file) == 1 ?
        static_cast<unsigned char>(ch) : EOF;
}
int PS4_SYSV_ABI GuestFflush(OrbisFILE* file) { return internal_fflush(file); }
int PS4_SYSV_ABI GuestFseek(OrbisFILE* file, long offset, int whence) {
    return internal_fseek(file, offset, whence);
}
long PS4_SYSV_ABI GuestFtell(OrbisFILE* file) {
    if (!file || !GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                               sizeof(*file), false) || file->_Handle < 0) return -1;
    return Libraries::Kernel::posix_lseek(file->_Handle, 0, 1);
}
int PS4_SYSV_ABI GuestFgetpos(OrbisFILE* file, Orbisfpos_t* out) {
    if (!out || !GuestAccess(reinterpret_cast<std::uintptr_t>(out),
                              sizeof(*out), true)) return -1;
    const auto at = GuestFtell(file);
    if (at < 0) return -1;
    std::memset(out, 0, sizeof(*out));
    out->_Off = at;
    return 0;
}
int PS4_SYSV_ABI GuestFeof(OrbisFILE* file) {
    return file && GuestAccess(reinterpret_cast<std::uintptr_t>(file),
        sizeof(*file), false) && ((file->_Mode & 0x100) != 0);
}
int PS4_SYSV_ABI GuestFerror(OrbisFILE* file) {
    return file && GuestAccess(reinterpret_cast<std::uintptr_t>(file),
        sizeof(*file), false) && ((file->_Mode & 0x200) != 0);
}
void PS4_SYSV_ABI GuestClearerr(OrbisFILE* file) {
    if (file && GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                            sizeof(*file), true)) file->_Mode &= ~u16{0x300};
}

enum class PrintKind { Printf, Sprintf, Snprintf, Fprintf };
class SysvPrintHle final : public Core::GuestCpu::HleCallAdapter {
public:
    explicit SysvPrintHle(PrintKind mode_) : mode(mode_) {}
    Core::GuestCpu::HleCallResult Invoke(Core::GuestCpu::HleCallFrame& frame) const override {
        constexpr std::array<std::size_t, 6> regs{7, 6, 2, 1, 8, 9};
        const std::size_t fixed = mode == PrintKind::Printf ? 1 : (mode == PrintKind::Snprintf ? 3 : 2);
        const auto fmt_addr = static_cast<std::uintptr_t>(frame.gpr[regs[fixed - 1]]);
        std::string format;
        if (!GuestString(reinterpret_cast<const char*>(fmt_addr), 4096, format) ||
            frame.rsp > std::numeric_limits<std::uintptr_t>::max() - sizeof(u64) ||
            !GuestAccess(frame.rsp + sizeof(u64), sizeof(u64), false)) {
            return Core::GuestCpu::HleCallFailure{EFAULT, Name()};
        }
        Common::VaRegSave saved{};
        for (std::size_t n = 0; n < regs.size(); ++n)
            saved.gp[n] = frame.gpr[regs[n]];
        for (std::size_t n = 0; n < 8; ++n)
            std::memcpy(&saved.fp[n], frame.xmm[n].data(), sizeof(saved.fp[n]));
        Common::VaList arguments{
            static_cast<u32>(fixed * sizeof(u64)), 48,
            reinterpret_cast<void*>(frame.rsp + sizeof(u64)), &saved
        };
        constexpr std::size_t MaxOutput = 1024 * 1024;
        char* dst = nullptr;
        std::size_t cap = MaxOutput;
        std::vector<char> buffer;
        if (mode == PrintKind::Printf || mode == PrintKind::Fprintf) {
            buffer.resize(MaxOutput);
            dst = buffer.data();
        } else {
            dst = reinterpret_cast<char*>(frame.gpr[regs[0]]);
            if (mode == PrintKind::Snprintf) cap = frame.gpr[regs[1]];
            if (cap > MaxOutput ||
                (cap && !GuestAccess(reinterpret_cast<std::uintptr_t>(dst), cap, true))) {
                frame.gpr[0] = static_cast<u64>(-1);
                return true;
            }
            if (mode == PrintKind::Sprintf) {
                // No dest length is present in sprintf's ABI. Require a mapped
                // writable region of this size and never write beyond it.
                void* start{};
                void* end{};
                u32 prot{};
                if (Core::Memory::Instance()->QueryProtection(
                        reinterpret_cast<std::uintptr_t>(dst), &start, &end, &prot) != 0 ||
                    !(prot & static_cast<u32>(Core::MemoryProt::CpuWrite))) {
                    frame.gpr[0] = static_cast<u64>(-1);
                    return true;
                }
                cap = std::min<std::size_t>(MaxOutput,
                          reinterpret_cast<std::uintptr_t>(end) -
                          reinterpret_cast<std::uintptr_t>(dst));
            }
        }
        struct Context { char* destination; std::size_t capacity; };
        Context output{dst, cap};
        auto writer = [](char c, void* opaque, std::size_t idx, std::size_t) {
            auto* b = static_cast<Context*>(opaque);
            if (b->capacity && b->destination) {
                if (idx < b->capacity) b->destination[idx] = c;
                else if (c == '\0') b->destination[b->capacity - 1] = 0;
            }
        };
        const auto result = _vsnprintf(writer, reinterpret_cast<char*>(&output),
                                       format.c_str(), &arguments);
        if ((mode == PrintKind::Printf || mode == PrintKind::Fprintf) && result >= 0) {
            const auto written = std::min<std::size_t>(result, MaxOutput - 1);
            if (mode == PrintKind::Printf) {
                (void)std::fwrite(buffer.data(), 1, written, stdout);
            } else {
                auto* file = reinterpret_cast<OrbisFILE*>(frame.gpr[regs[0]]);
                if (!file || !GuestAccess(reinterpret_cast<std::uintptr_t>(file),
                        sizeof(*file), true) || file->_Handle < 0 ||
                    Libraries::Kernel::sceKernelWrite(file->_Handle, buffer.data(),
                         written) != static_cast<std::int64_t>(written)) {
                    frame.gpr[0] = static_cast<u64>(-1);
                    return true;
                }
            }
        }
        frame.gpr[0] = static_cast<u64>(static_cast<std::int64_t>(result));
        return true;
    }
private:
    PrintKind mode;
};

void AddPrintfAlias(Core::Loader::SymbolsResolver* sym, const char* nid, PrintKind kind) {
    Core::Loader::SymbolResolver sr{};
    sr.name = nid;
    sr.library = "libc";
    sr.library_version = 1;
    sr.module = "libc";
    sr.type = Core::Loader::SymbolType::Function;
    sym->AddFunction(sr, std::make_shared<SysvPrintHle>(kind));
}
} // namespace


void RegisterFexLibcGuestObjects(Core::Loader::SymbolsResolver* sym) {
    // Resolve PS4 ELF STT_OBJECT imports as readable guest addresses.
    // The vendor libc.prx is not shipped. These are compatible OrbisFILE
    // objects, not host Bionic FILE* or native-pointer placeholders.
    constexpr std::size_t GuestDataSize = 0x4000;
    static_assert(0x100 + 3 * sizeof(OrbisFILE) <= GuestDataSize);
    auto* memory = Core::Memory::Instance();
    void* allocation = nullptr;
    const auto error = memory->MapMemory(
        &allocation, 0, GuestDataSize, Core::MemoryProt::CpuReadWrite,
        Core::MemoryMapFlags::NoFlags, Core::VMAType::Flexible,
        "BachataFexLibcObjects");
    if (error != 0 || !allocation) {
        // Do not register a host pointer or zero as an emulated PS4 symbol.
        return;
    }
    std::memset(allocation, 0, GuestDataSize);
    auto* need = static_cast<std::uint32_t*>(allocation);
    *need = 1;  // OpenOrbis Need_sceLibc marker.
    auto* streams = reinterpret_cast<OrbisFILE*>(
        reinterpret_cast<std::uintptr_t>(allocation) + 0x100);
    for (std::size_t i = 0; i < 3; ++i) {
        auto* file = std::construct_at(&streams[i]);
        file->_Idx = static_cast<u8>(i);
        file->_Handle = static_cast<s32>(i);
        file->_Mode = i == 0 ? 0x0001 : 0x2002;
        file->_Buf = &file->_Cbuf;
        file->_Bend = file->_Buf + 1;
        file->_Next = file->_Buf;
        file->_Rend = file->_Buf;
        file->_Wend = file->_Buf;
        file->_WRend = file->_Buf;
        file->_WWend = file->_Buf;
        file->_Rback = &file->_Cbuf;
        file->_WRback = &file->unk1;
    }
    // The game uses libc#libc. A few modules import the same data from
    // libSceLibcInternal; register both namespaces, retaining one backing.
    LIB_OBJ("P330P3dFF68", "libc", 1, "libc", need);
    LIB_OBJ("1TDo-ImqkJc", "libc", 1, "libc", &streams[0]);
    LIB_OBJ("2sWzhYqFH4E", "libc", 1, "libc", &streams[1]);
    LIB_OBJ("H8AprKeZtNg", "libc", 1, "libc", &streams[2]);
    LIB_OBJ("P330P3dFF68", "libSceLibcInternal", 1, "libSceLibcInternal", need);
    LIB_OBJ("1TDo-ImqkJc", "libSceLibcInternal", 1, "libSceLibcInternal", &streams[0]);
    LIB_OBJ("2sWzhYqFH4E", "libSceLibcInternal", 1, "libSceLibcInternal", &streams[1]);
    LIB_OBJ("H8AprKeZtNg", "libSceLibcInternal", 1, "libSceLibcInternal", &streams[2]);
}

void RegisterFexLibcCompatAliases(Core::Loader::SymbolsResolver* sym) {
#define ALIAS(nid, function) LIB_FUNCTION(nid, "libc", 1, "libc", function)
    ALIAS("YQ0navp+YIc", GuestPuts);
    ALIAS("m5wN+SwZOR4", GuestPutchar);
    ALIAS("xeYO4u7uyJ0", GuestFopen);
    ALIAS("uodLYyUip20", GuestFclose);
    ALIAS("lbB+UlZqVG0", GuestFread);
    ALIAS("MpxhMh8QFro", GuestFwrite);
    ALIAS("QrZZdJ8XsX0", GuestFputs);
    ALIAS("MUjC4lbHrK4", GuestFflush);
    ALIAS("rQFVBXp-Cxg", GuestFseek);
    ALIAS("Qazy8LmXTvw", GuestFtell);
    ALIAS("LxcEU+ICu8U", GuestFeof);
    ALIAS("AHxyhN96dy4", GuestFerror);
    ALIAS("AEuF3F2f8TA", GuestFgetc);
    ALIAS("St9nbxSoezk", GuestClearerr);
    ALIAS("SHlt7EhOtqA", GuestFgetpos);
    ALIAS("5jNubw4vlAA", GuestStrnlen);
    ALIAS("RIa6GnWp+iU", GuestStrerror);
    ALIAS("g7zzzLDYGw0", GuestStrdup);
    ALIAS("6sJWiWSRuqk", GuestStrncpy);
    ALIAS("aesyjrHVWy4", GuestStrncmp);
    ALIAS("kHg45qPC6f0", GuestStrncat);
    ALIAS("9yDWMxEFdJU", GuestStrrchr);
    ALIAS("ob5xAW4ln-0", GuestStrchr);
    ALIAS("q0F6yS-rCms", GuestStrcspn);
    ALIAS("gjbmYpP-XJQ", GuestStrcoll);
    ALIAS("SfQIZcqvvms", GuestStrlcpy);
    ALIAS("QNyUWGXmXNc", GuestStrtoumax);
    ALIAS("cpCOXWMgha0", GuestRand);
    ALIAS("VPbJwTCgME0", GuestSrand);
    ALIAS("wLlFkwG9UcQ", GuestTime);
    ALIAS("-VVn74ZyhEs", GuestDifftime);
    ALIAS("H8ya2H00jbI", Fex_sin);
    ALIAS("Q4rRL34CEeE", Fex_sinf);
    ALIAS("2WE3BTYVwKM", Fex_cos);
    ALIAS("-P6FNMzk2Kc", Fex_cosf);
    ALIAS("T7uyNqP7vQA", Fex_tan);
    ALIAS("7Ly52zaL44Q", Fex_asin);
    ALIAS("JBcgYuW8lPU", Fex_acos);
    ALIAS("OXmauLdQ8kY", Fex_atan);
    ALIAS("weDug8QD-lE", Fex_atanf);
    ALIAS("NVadfnzQhHQ", Fex_exp);
    ALIAS("8zsu04XNsZ4", Fex_expf);
    ALIAS("wuAQt-j+p4o", Fex_exp2f);
    ALIAS("rtV7-jWC6Yg", Fex_log);
    ALIAS("WuMbPBKN1TU", Fex_log10);
    ALIAS("JM4EBvWT9rc", Fex_tanh);
    ALIAS("SAd0Z3wKwLA", Fex_tanhf);
    ALIAS("HUbZmOnT-Dg", Fex_atan2);
    ALIAS("9LCjpWyQ5Zc", Fex_pow);
    ALIAS("1D0H2KNjshE", Fex_powf);
    ALIAS("pKwslsMUmSk", Fex_fmod);
    ALIAS("88Vv-AzHVj8", Fex_fmodf);
    ALIAS("aaDMGGkXFxo", Fex_frexpf);
    ALIAS("kn0yiYeExgA", Fex_ldexpf);
    ALIAS("3+UPM-9E6xY", Fex_modff);
    // Native x86-64 FEX veneers: required for returns-twice setjmp semantics.
    // The adapter is a registration token only; the FEX veneer allocator
    // substitutes verified guest x86 code before this adapter can be invoked.
    const auto add_guest_nonlocal_jump = [&](const char* nid) {
        Core::Loader::SymbolResolver sr{};
        sr.name = nid;
        sr.library = "libc";
        sr.library_version = 1;
        sr.module = "libc";
        sr.type = Core::Loader::SymbolType::Function;
        sym->AddFunction(sr, Core::GuestCpu::MakeUnsupportedHleCallAdapter());
    };
    add_guest_nonlocal_jump("gNQ1V2vfXDE"); // setjmp
    add_guest_nonlocal_jump("sjpkrhugvVI"); // _setjmp
    add_guest_nonlocal_jump("lKEN2IebgJ0"); // longjmp
    add_guest_nonlocal_jump("+F+9hhi6k9Q"); // _longjmp
    AddPrintfAlias(sym, "hcuQgD53UxM", PrintKind::Printf);
    AddPrintfAlias(sym, "tcVi5SivF7Q", PrintKind::Sprintf);
    AddPrintfAlias(sym, "eLdDw6l0-bU", PrintKind::Snprintf);
    AddPrintfAlias(sym, "fffwELXNVFA", PrintKind::Fprintf);
#undef ALIAS
}
} // namespace Libraries::LibcInternal
#endif
