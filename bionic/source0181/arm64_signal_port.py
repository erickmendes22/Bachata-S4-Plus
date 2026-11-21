#!/usr/bin/env python3
"""Retain proven ARM64 FEX signal handling and add the 0.18.1 execute-fault API.

The source merge keeps the ARM64 host's GetRip, IncrementRip and Linux ESR
write-fault decoding. Replacing them with upstream x86_64 paths would regress
guest memory protection. The new 0.18.1 API additionally needs IsExecuteError.
"""
from __future__ import annotations
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"ARM64 {label}: expected 1 source anchor, found {n}")
    return text.replace(old, new, 1)


def apply(root: Path) -> dict:
    source_file = root / "src/common/signal_context.cpp"
    header_file = root / "src/common/signal_context.h"
    text = source_file.read_text(encoding="utf-8")
    head = header_file.read_text(encoding="utf-8")
    # These are ALREADY present in the working native FEX 0.16.1 host.
    for anchor in (
        "void IncrementRip(void* ctx, u64 length)",
        "#elif defined(__linux__) && defined(ARCH_ARM64)",
        "reinterpret_cast<const esr_context*>(record)",
        "return esr->esr & 0x40",
    ):
        if anchor not in text:
            raise RuntimeError("Proven ARM64 FEX signal handling missing: " + anchor)
    if "bool IsExecuteError(void* ctx)" not in text:
        addition = """
bool IsExecuteError(void* ctx) {
#if defined(_WIN32)
    return ((EXCEPTION_POINTERS*)ctx)->ExceptionRecord->ExceptionInformation[0] == 0xf;
#elif defined(__APPLE__) && defined(ARCH_X86_64)
    return ((ucontext_t*)ctx)->uc_mcontext->__es.__err & 0x10;
#elif defined(__APPLE__) && defined(ARCH_ARM64)
    const auto esr = ((ucontext_t*)ctx)->uc_mcontext->__es.__esr;
    const auto kind = (esr >> 26) & 0x3f;
    return kind == 0x20 || kind == 0x21;
#elif defined(__FreeBSD__) && defined(ARCH_X86_64)
    return ((ucontext_t*)ctx)->uc_mcontext.mc_err & 0x10;
#elif defined(ARCH_X86_64)
    return ((ucontext_t*)ctx)->uc_mcontext.gregs[REG_ERR] & 0x10;
#elif defined(__linux__) && defined(ARCH_ARM64)
    const auto* context = static_cast<const ucontext_t*>(ctx);
    const auto* record = context->uc_mcontext.__reserved;
    const auto* const end = record + sizeof(context->uc_mcontext.__reserved);
    while (static_cast<size_t>(end - record) >= sizeof(_aarch64_ctx)) {
        const auto* header = reinterpret_cast<const _aarch64_ctx*>(record);
        if (header->magic == 0 && header->size == 0) break;
        const size_t remaining = end - record;
        if (header->size < sizeof(*header) || header->size > remaining ||
            (header->size % alignof(_aarch64_ctx)) != 0) break;
        if (header->magic == ESR_MAGIC) {
            if (header->size < sizeof(esr_context)) return false;
            const auto esr = reinterpret_cast<const esr_context*>(record)->esr;
            const auto kind = (esr >> 26) & 0x3f;
            return kind == 0x20 || kind == 0x21;
        }
        record += header->size;
    }
    return false;
#else
    return false;
#endif
}

"""
        text = replace_once(text, "} // namespace Common\n",
                            addition + "} // namespace Common\n",
                            "execute-fault implementation")
        source_file.write_text(text, encoding="utf-8")
    if "bool IsExecuteError(void* ctx);" not in head:
        head = replace_once(head, "bool IsWriteError(void* ctx);",
                            "bool IsWriteError(void* ctx);\n"
                            "bool IsExecuteError(void* ctx);",
                            "header API")
        header_file.write_text(head, encoding="utf-8")

    # WindowSDL::SetIcon(std::filesystem::path) is declared by the host
    # but <filesystem> is not explicitly included in the old header.
    window = root / "src/sdl_window.h"
    window_header = window.read_text(encoding="utf-8")
    if '#include <filesystem>' not in window_header:
        window_header = replace_once(window_header, '#include <string>\n',
                                     '#include <filesystem>\n#include <string>\n',
                                     "SDL filesystem include")
        window.write_text(window_header, encoding="utf-8")
    return {
        "nativeSignalHandlersPreserved": ["GetRip", "IncrementRip", "IsWriteError"],
        "new0181SignalApi": "IsExecuteError from Linux ARM64 ESR class",
        "SDLFilesystemInclude": True,
    }
