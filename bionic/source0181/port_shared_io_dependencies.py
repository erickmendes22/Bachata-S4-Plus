#!/usr/bin/env python3
"""Complete dependencies actually imported by the game's original FIOS2 PRX.

Keep FEX and the original guest modules. Match the donor's unique libc export
fallback without changing strong host contracts or inventing archive content.
"""
from pathlib import Path


LIBC_FALLBACK = r'''#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BACHATA_SHARED_IO_LIBC_DEPENDENCY: libSceLibcInternal is a firmware
    // namespace. The donor's link_modules.py can use unique actual libc
    // exports. Here only the observed calendar imports may use
    // that alias: FEX owns the HLE heap and FILE contracts, so an unsupported
    // allocator/stdio import must never silently cross to the guest heap.
    // Strong HLE and exact guest exports already won above.
    const bool shared_io_libc_nid =
        sr.name == "1mecP7RgI2A" ||  // gmtime
        sr.name == "5bBacGLyLOs" ||  // gmtime_s
        sr.name == "efhK-YSUYYQ" ||  // localtime
        sr.name == "n7AepwR0s34";    // mktime
    if (sr.library == "libSceLibcInternal" && sr.module == "libSceLibcInternal" &&
        sr.type == Loader::SymbolType::Function && shared_io_libc_nid) {
        const Loader::SymbolRecord* libc_record = nullptr;
        VAddr libc_base{};
        bool ambiguous = false;
        for (const auto& mod : m_modules) {
            for (const auto& export_library : mod->GetExportLibs()) {
                if (export_library.name != "libc") continue;
                for (const auto& export_module : mod->GetExportModules()) {
                    auto candidate = sr;
                    candidate.library = "libc";
                    candidate.library_version = export_library.version;
                    candidate.module = export_module.name;
                    const auto* record = mod->export_sym.FindSymbol(candidate);
                    if (!record || !record->virtual_address || record->hle_adapter) continue;
                    // Repeated library/module metadata can reach the same
                    // export twice; it is still one actual symbol record.
                    if (libc_record && libc_record != record) ambiguous = true;
                    if (!libc_record) {
                        libc_record = record;
                        libc_base = mod->GetBaseAddress();
                    }
                }
            }
        }
        if (libc_record && !ambiguous) {
            *return_info = *libc_record;
            LOG_INFO(Core_Linker,
                     "BACHATA_SHARED_IO_LIBC_BIND nid={} import_base={:#x} libc_base={:#x} address={:#x}",
                     sr.name, m->GetBaseAddress(), libc_base, return_info->virtual_address);
            return true;
        }
    }
#endif

'''

SDK_OBJECT = r'''    // BACHATA_SHARED_IO_LIBC_SDK_OBJECT: the SDK marker is a 32-bit object
    // in guest VM, not a host .bss address. Reuse the initialized Need_sceLibc
    // backing only after RegisterFexLibcGuestObjects has mapped and published it.
    {
        auto& symbols = linker->GetHLESymbols();
        Core::Loader::SymbolResolver marker{};
        marker.name = "P330P3dFF68";
        marker.library = "libc";
        marker.library_version = 1;
        marker.module = "libc";
        marker.type = Core::Loader::SymbolType::Object;
        const auto* object = symbols.FindSymbol(marker);
        if (object && !object->hle_adapter && object->virtual_address != 0) {
            // AddSymbol may grow the registry: retain only the address value.
            const VAddr address = object->virtual_address;
            if (memory->ClampGpuRangeSize(address, sizeof(u32)) == sizeof(u32)) {
                marker.name = "ZT4ODD2Ts9o";
                marker.library = "libSceLibcInternal";
                marker.module = "libSceLibcInternal";
                symbols.AddSymbol(marker, address);
                LOG_INFO(Loader, "BACHATA_SHARED_IO_LIBC_SDK_OBJECT address={:#x} bytes=4", address);
            }
        }
    }
'''

CXA_FINALIZE = r'''// BACHATA_SHARED_IO_CXA_FINALIZE: __cxa_atexit and __cxa_finalize
// must share one ownership domain. Select/remove under the table mutex, then
// invoke from a value copy without holding it across reentrant guest code.
void PS4_SYSV_ABI fex_libc_cxa_finalize(void* dso_handle) {
    static std::atomic_bool reported{false};
    if (!reported.exchange(true, std::memory_order_relaxed)) {
        LOG_INFO(Lib_LibcInternal, "BACHATA_SHARED_IO_CXA_FINALIZE dso={}", dso_handle);
    }
    for (;;) {
        CxaAtexitEntry entry{};
        bool found = false;
        {
            std::lock_guard lock{AtexitMutex};
            for (std::size_t i = AtexitEntries.size(); i != 0; --i) {
                if (dso_handle && AtexitEntries[i - 1].dso_handle != dso_handle) continue;
                entry = AtexitEntries[i - 1];
                AtexitEntries.erase(AtexitEntries.begin() + (i - 1));
                found = true;
                break;
            }
        }
        if (!found) return;
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
        // Registrations enter through an FEX HLE. The stored address remains
        // x86 guest code even if module state later becomes invalid: the bridge
        // reports that failure; it must never become a native indirect call.
        static_cast<void>(Core::GuestCpu::RunGuestFunctionOrAbort(
            reinterpret_cast<const void*>(entry.func), "__cxa_finalize", entry.arg));
#else
        entry.func(entry.arg);
#endif
    }
}

'''

DISC_MAP = r'''#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BACHATA_SHARED_IO_DISC_MAP: no disc bitmap exists for the installed
    // files. A success with three zero outputs fabricates a mapping; the
    // original FIOS library must receive the donor's explicit absence result.
    static std::atomic_bool reported{false};
    if (!reported.exchange(true, std::memory_order_relaxed)) {
        LOG_INFO(Lib_DiscMap,
                 "BACHATA_SHARED_IO_DISC_MAP query=7C980FFB0AA27E7A result={:#x} outputs=untouched",
                 ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO);
    }
    return ORBIS_DISC_MAP_ERROR_NO_BITMAP_INFO;
#else
    *flags = 0;
    *ret1 = 0;
    *ret2 = 0;
    return ORBIS_OK;
#endif'''


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Shared FIOS dependency drift ({label}): {count}")
    return text.replace(old, new, 1)


def apply(root):
    root = Path(root)
    linker = root / "src/core/linker.cpp"
    linker_header = root / "src/core/linker.h"
    emulator = root / "src/emulator.cpp"
    cxa = root / "src/core/libraries/libc_internal/libc_internal_cxa.cpp"
    cxa_header = cxa.with_suffix(".h")
    disc = root / "src/core/libraries/disc_map/disc_map.cpp"
    cpp, header, boot, cx, cxh, disk = (
        p.read_text() for p in (linker, linker_header, emulator, cxa, cxa_header, disc))
    if "BACHATA_SHARED_IO_LIBC_DEPENDENCY" in cpp:
        if ("BACHATA_SHARED_IO_LIBC_SDK_OBJECT" not in boot or
                "BACHATA_SHARED_IO_DISC_MAP" not in disk or
                "BACHATA_SHARED_IO_LIBC_REBIND" not in header or
                "BACHATA_SHARED_IO_CXA_FINALIZE" not in cx or
                "void PS4_SYSV_ABI fex_libc_cxa_finalize(void* dso_handle);" not in cxh):
            raise RuntimeError("Partial shared FIOS dependency overlay")
        return {"sharedIoDependencies": "already applied"}
    if "BACHATA_SHARED_IO_FIOS_PROVISIONAL" not in cpp:
        raise RuntimeError("Apply shared_io_fios_exports before shared_io_dependencies")
    cpp = once(cpp,
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n    if (prefer_guest_fios2 && hle_record != nullptr && !hle_record->hle_fallback)",
        LIBC_FALLBACK + "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n    if (prefer_guest_fios2 && hle_record != nullptr && !hle_record->hle_fallback)",
        "actual libc export after exact resolution")
    header = once(header, "        const auto exports = m->GetExportModules();\n",
        "        const auto exports = m->GetExportModules();\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "        // BACHATA_SHARED_IO_LIBC_REBIND: libc can arrive after the original FIOS PRX.\n"
        "        const bool exports_libc =\n"
        '            std::ranges::contains(m->GetExportLibs(), "libc", &LibraryInfo::name);\n'
        "#endif\n", "late libc module export")
    header = once(header,
        "                if (std::ranges::contains(imports, export_mod.name, &ModuleInfo::name)) {",
        "                if (std::ranges::contains(imports, export_mod.name, &ModuleInfo::name)\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "                    || (exports_libc &&\n"
        '                        std::ranges::contains(imports, "libSceLibcInternal", &ModuleInfo::name))\n'
        "#endif\n"
        "                ) {", "late unresolved Internal imports")
    boot = once(boot,
        "    Libraries::LibcInternal::RegisterFexLibcGuestObjects(&linker->GetHLESymbols());\n",
        "    Libraries::LibcInternal::RegisterFexLibcGuestObjects(&linker->GetHLESymbols());\n" + SDK_OBJECT,
        "guest-mapped int32 SDK object")
    cx = once(cx, '#include "core/libraries/libs.h"',
        '#include "core/libraries/libs.h"\n#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n'
        '#include "core/guest_cpu/guest_callback.h"\n#endif', "guest destructor bridge")
    cx = once(cx,
        " * game process is terminated by the host (no orderly exit), so simply\n"
        " * accepting the registration is enough to satisfy module start; we keep the\n"
        " * table so a future __cxa_finalize implementation can drain it.\n",
        " * process can also finalize a loaded DSO. Both operations use this same\n"
        " * table; the selected entry is removed before invoking guest code.\n",
        "shared cxa table contract")
    cx = once(cx,
        "     * registration; the table is retained for a future __cxa_finalize. */",
        "     * registration in the shared table consumed by __cxa_finalize. */",
        "atexit completion contract")
    cx = once(cx, "void RegisterFexLibcCxaAliases(Core::Loader::SymbolsResolver* sym) {",
        CXA_FINALIZE + "void RegisterFexLibcCxaAliases(Core::Loader::SymbolsResolver* sym) {\n"
        '    LIB_FUNCTION("H2e8t5ScQGc", "libc", 1, "libc", fex_libc_cxa_finalize);\n'
        '    LIB_FUNCTION("H2e8t5ScQGc", "libSceLibcInternal", 1, "libSceLibcInternal",\n'
        "                 fex_libc_cxa_finalize);",
        "strong matching cxa finalizer")
    cxh = once(cxh,
        "int PS4_SYSV_ABI fex_libc_cxa_atexit(void (*func)(void*), void* arg, void* dso_handle);",
        "int PS4_SYSV_ABI fex_libc_cxa_atexit(void (*func)(void*), void* arg, void* dso_handle);\n"
        "void PS4_SYSV_ABI fex_libc_cxa_finalize(void* dso_handle);",
        "finalizer ABI declaration")
    disk = once(disk, '#include "common/logging/log.h"',
                '#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n#include <atomic>\n#endif\n\n#include "common/logging/log.h"',
                "bounded query evidence")
    disk = once(disk, "    *flags = 0;\n    *ret1 = 0;\n    *ret2 = 0;\n    return ORBIS_OK;",
                DISC_MAP, "no nonexistent disc bitmap")
    for path, text in ((linker, cpp), (linker_header, header), (emulator, boot),
                       (cxa, cx), (cxa_header, cxh), (disc, disk)):
        path.write_text(text)
    return {
        "sharedIoDependencies": "four calendar NIDs via unique actual libc exports, late rebind, guest-mapped int32 SDK object",
        "cxa": "strong atexit/finalize share table, reverse claim order, DSO filter, exactly once and FEX callbacks",
        "preserved": "strong HLE, exact guest namespace, allocators, FEX/SAF and desktop paths",
        "discMap": "7C returns NO_BITMAP_INFO without output writes; one actual-call breadcrumb",
        "causality": "remaining boot freeze not proven without calls from device gameplay",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    print(apply(parser.parse_args().source))
