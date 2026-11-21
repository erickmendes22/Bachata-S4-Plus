#!/usr/bin/env python3
"""Make upstream shadPS4 0.18.1 Linux SIGSEGV context work on ARM64/Bionic.

Desktop shadPS4's signal_context.cpp supports x86_64 and Apple ARM64 but
explicitly errors out on Linux/Android ARM64. Decode the AArch64 Linux ESR
record from ucontext_t, rather than misclassifying every page fault as read.
No Linux-only glibc interfaces, system copy or API-level syscall required.
"""
from __future__ import annotations
from pathlib import Path


def require_once(src: str, old: str, new: str, detail: str) -> str:
    n = src.count(old)
    if n != 1:
        raise RuntimeError(f"ARM64 signal context {detail}: {n} anchors")
    return src.replace(old, new, 1)


def apply(root: Path) -> dict:
    path = root / "src/common/signal_context.cpp"
    source = path.read_text(encoding="utf-8")
    source = require_once(
        source, '#include "common/signal_context.h"\n',
        '#include "common/signal_context.h"\n'
        '#include <cstddef>\n#include <cstdint>\n#include <cstring>\n',
        "headers")
    arm64_esr = '''
#if defined(ARCH_ARM64) && defined(__linux__)
// Linux arm64 signal frames store extended records in mcontext.__reserved.
// Magic=0x45535201 indicates the kernel's ESR_EL1 (exception syndrome).
// The 8-byte record header is {uint32_t magic, uint32_t size}; the ESR follows.
static std::uint64_t LinuxArm64Esr(void* context) {
    const auto& m = reinterpret_cast<ucontext_t*>(context)->uc_mcontext;
    const auto* bytes = reinterpret_cast<const unsigned char*>(m.__reserved);
    constexpr std::uint32_t kEsrMagic = 0x45535201U;
    constexpr std::size_t kHeaderSize = 8;
    for (std::size_t offset = 0; offset + kHeaderSize <= sizeof(m.__reserved);) {
        std::uint32_t magic = 0, size = 0;
        std::memcpy(&magic, bytes + offset, sizeof(magic));
        std::memcpy(&size, bytes + offset + sizeof(magic), sizeof(size));
        if (magic == 0 || size == 0 || size < kHeaderSize ||
            size > sizeof(m.__reserved) - offset) {
            break;
        }
        if (magic == kEsrMagic && size >= kHeaderSize + sizeof(std::uint64_t)) {
            std::uint64_t esr = 0;
            std::memcpy(&esr, bytes + offset + kHeaderSize, sizeof(esr));
            return esr;
        }
        offset += size;
    }
    return 0;
}
#endif

'''
    source = require_once(source, "namespace Common {\n",
                          "namespace Common {\n"+arm64_esr, "ESR parser")

    source = require_once(
        source,
        '    return (void*)((ucontext_t*)ctx)->uc_mcontext.gregs[REG_RIP];\n'
        '#else\n#error "Unsupported architecture"',
        '    return (void*)((ucontext_t*)ctx)->uc_mcontext.gregs[REG_RIP];\n'
        '#elif defined(ARCH_ARM64) && defined(__linux__)\n'
        '    return reinterpret_cast<void*>(static_cast<std::uintptr_t>(\n'
        '        reinterpret_cast<ucontext_t*>(ctx)->uc_mcontext.pc));\n'
        '#else\n#error "Unsupported architecture"',
        "PC")
    source = require_once(
        source,
        '    return ((ucontext_t*)ctx)->uc_mcontext.gregs[REG_ERR] & 0x2;\n'
        '#else\n#error "Unsupported architecture"',
        '    return ((ucontext_t*)ctx)->uc_mcontext.gregs[REG_ERR] & 0x2;\n'
        '#elif defined(ARCH_ARM64) && defined(__linux__)\n'
        '    const auto esr = LinuxArm64Esr(ctx);\n'
        '    // ESR data abort WnR bit indicates a write fault.\n'
        '    return esr != 0 && (esr & (1ULL << 6)) != 0;\n'
        '#else\n#error "Unsupported architecture"',
        "write")
    source = require_once(
        source,
        '    return ((ucontext_t*)ctx)->uc_mcontext.gregs[REG_ERR] & 0x10;\n'
        '#else\n#error "Unsupported architecture"',
        '    return ((ucontext_t*)ctx)->uc_mcontext.gregs[REG_ERR] & 0x10;\n'
        '#elif defined(ARCH_ARM64) && defined(__linux__)\n'
        '    const auto exception_class = (LinuxArm64Esr(ctx) >> 26) & 0x3f;\n'
        '    // EC=0x20/0x21: instruction abort at current/lower EL.\n'
        '    return exception_class == 0x20 || exception_class == 0x21;\n'
        '#else\n#error "Unsupported architecture"',
        "execution")
    path.write_text(source, encoding="utf-8")

    # WindowSDL::SetIcon(std::filesystem::path) is declared by the ARM64 host
    # but the original header never explicitly included <filesystem>.
    window = root / "src/sdl_window.h"
    header = window.read_text(encoding="utf-8")
    if '#include <filesystem>' not in header:
        header = require_once(header, '#include <string>\n',
                              '#include <filesystem>\n#include <string>\n',
                              "SDL header")
        window.write_text(header, encoding="utf-8")
    return {
        "arm64Context": "uc_mcontext.pc and Linux ESR extension records",
        "writeFaultClassification": "ESR WnR bit",
        "executeFaultClassification": "ESR exception class 0x20/0x21",
        "SDLFilesystemInclude": True,
    }
