#!/usr/bin/env python3
"""Let the game's FIOS2 exports replace an early FEX HLE fallback.

The inFAMOUS donor links the game's libc/FIOS2 modules and does not implement
its archive API with aliases. Keep the original PS4 library running on FEX;
do not substitute an archive parser or copy the donor's CPU runtime.
"""
from pathlib import Path


POLICY_METHODS = r'''    // BACHATA_SHARED_IO_FIOS_EXPORTS: configured for this resolver at boot.
    // The explicit .use-hle override wins even when a game PRX is loaded.
    void SetFios2PreferGuestExports(bool prefer) noexcept {
        m_fios2_prefer_guest_exports.store(prefer, std::memory_order_relaxed);
    }

    [[nodiscard]] bool Fios2PreferGuestExports() const noexcept {
        return m_fios2_prefer_guest_exports.load(std::memory_order_relaxed);
    }

'''

REGISTRATION = r'''        // BACHATA_SHARED_IO_FIOS_POLICY: an available guest export, not a
        // title allowlist or the spelling of a host path, chooses FIOS2 LLE.
        // Register the usable HLE up front for absent modules. Resolve leaves
        // that fallback provisional until the original PRX can replace it.
        const bool fios_force_hle =
            std::filesystem::exists(game_specific_modules_path / "libSceFios2.use-hle");
        sym->SetFios2PreferGuestExports(!fios_force_hle);
        Libraries::Fios2::RegisterLib(sym);
        LOG_INFO(Lib_Kernel, "BACHATA_FIOS2_EARLY_HLE_READY");
        LOG_INFO(Lib_Kernel,
                 "BACHATA_SHARED_IO_FIOS_POLICY prefer_guest={} forced_hle={} fallback=available",
                 !fios_force_hle, fios_force_hle);
'''

PROVISIONAL = r'''#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    if (prefer_guest_fios2 && hle_record != nullptr && !hle_record->hle_fallback) {
        // BACHATA_SHARED_IO_FIOS_PROVISIONAL: this is a working HLE adapter,
        // not ENOSYS. Relocate writes its FEX veneer but must not set the
        // permanent relocation bit before the game's PRX has been loaded.
        // LoadAndStartModule -> RelocateAnyImports will then install the
        // original guest export, including data exports and its own imports.
        *return_info = *hle_record;
        return false;
    }
#endif

'''


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Shared FIOS export drift ({label}): {count}")
    return text.replace(old, new, 1)


def apply(root):
    root = Path(root)
    header = root / "src/core/loader/symbols_resolver.h"
    libs = root / "src/core/libraries/libs.cpp"
    linker = root / "src/core/linker.cpp"
    h, lib, cpp = (path.read_text() for path in (header, libs, linker))
    if "BACHATA_SHARED_IO_FIOS_EXPORTS" in h:
        if ("BACHATA_SHARED_IO_FIOS_POLICY" not in lib or
                "BACHATA_SHARED_IO_FIOS_PROVISIONAL" not in cpp):
            raise RuntimeError("Partial shared FIOS export overlay")
        return {"sharedIoFiosExports": "already applied"}
    h = once(h, "#include <filesystem>", "#include <atomic>\n#include <filesystem>",
             "atomic boot policy dependency")
    h = once(h, "    void AddFunction(const SymbolResolver& s, std::shared_ptr<GuestCpu::HleCallAdapter> adapter);",
             POLICY_METHODS + "    void AddFunction(const SymbolResolver& s, std::shared_ptr<GuestCpu::HleCallAdapter> adapter);",
             "resolver policy API")
    h = once(h, "    std::unique_ptr<GuestCpu::HleCallRegistry> hle_registry;",
             "    std::atomic_bool m_fios2_prefer_guest_exports{true};\n"
             "    std::unique_ptr<GuestCpu::HleCallRegistry> hle_registry;",
             "resolver policy lifetime")
    begin = lib.index("        const bool shadow_guest_archive =")
    end = lib.index('        LOG_INFO(Lib_Kernel, "BIONIC_BOOT_STAGE=LIBC_HLE_END");', begin)
    previous = lib[begin:end]
    if previous.count("Libraries::Fios2::RegisterLib(sym);") != 1:
        raise RuntimeError("Shared FIOS registration boundary changed")
    lib = lib[:begin] + REGISTRATION + lib[end:]
    lib = once(lib,
        "        // BACHATA_SHADOW_PREFER_GUEST_FIOS2: CUSA08809 loaded shadow.cwks\n"
        "        // before early FIOS2 HLE was added. ArchiveMountSync only aliases\n"
        "        // /app0; it does not provide the contents of any PSARC archive.\n",
        "        // BACHATA_SHADOW_PREFER_GUEST_FIOS2 now applies to every actual\n"
        "        // FIOS2 guest export. An /app0 alias cannot implement PSARC.\n",
        "generalize the existing archive preference")
    cpp = once(cpp,
        "    const auto* record = m_hle_symbols.FindSymbol(sr);\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    if (record != nullptr && !record->hle_fallback) {\n"
        "#else\n"
        "    if (record != nullptr) {\n"
        "#endif\n"
        "        *return_info = *record;\n",
        "    const auto* const hle_record = m_hle_symbols.FindSymbol(sr);\n"
        "#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU\n"
        "    const bool prefer_guest_fios2 = sr.library == \"libSceFios2\" &&\n"
        "                                    m_hle_symbols.Fios2PreferGuestExports();\n"
        "    if (hle_record != nullptr && !hle_record->hle_fallback && !prefer_guest_fios2) {\n"
        "#else\n"
        "    if (hle_record != nullptr) {\n"
        "#endif\n"
        "        *return_info = *hle_record;\n",
        "guest FIOS precedence with independent HLE record")
    cpp = once(cpp,
        "        record = mod->export_sym.FindSymbol(sr);\n"
        "        if (record) {\n"
        "            *return_info = *record;\n",
        "        const auto* const guest_record = mod->export_sym.FindSymbol(sr);\n"
        "        if (guest_record) {\n"
        "            *return_info = *guest_record;\n",
        "preserve fallback across unmatched guest exports")
    cpp = once(cpp, "    const auto aeronid = AeroLib::FindByNid(sr.name.c_str());",
               PROVISIONAL + "    const auto aeronid = AeroLib::FindByNid(sr.name.c_str());",
               "provisional but usable early FIOS fallback")
    cpp = once(cpp,
        "        if (record != nullptr && record->hle_fallback) {\n"
        "            return_info->hle_adapter = record->hle_adapter;\n",
        "        if (hle_record != nullptr && hle_record->hle_fallback) {\n"
        "            return_info->hle_adapter = hle_record->hle_adapter;\n",
        "retain existing unsupported adapter after guest search")
    for path, text in ((header, h), (libs, lib), (linker, cpp)):
        path.write_text(text)
    return {
        "sharedIoFiosExports": "actual FIOS2 guest export before provisional HLE, all serials",
        "cpu": "original PS4 library executes through existing FEX path",
        "override": "libSceFios2.use-hle preserves explicit HLE preference",
        "loader": "unchanged staged/game selection, missing-module fallback and SAF IFile",
        "relocation": "late PRX replaces early veneers through existing RelocateAnyImports",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print(apply(args.source))
