#!/usr/bin/env python3
"""Choose the complete actual libc Mspace family as one boot provider."""
from pathlib import Path


def apply(root: Path) -> None:
    def replace(rel, old, new):
        p = root / rel
        src = p.read_text(encoding='utf-8')
        if src.count(old) != 1:
            raise RuntimeError(f'{rel}: donor Mspace anchor count={src.count(old)}: {old[:100]}')
        p.write_text(src.replace(old, new, 1), encoding='utf-8')

    h = 'src/core/linker.h'
    cpp = 'src/core/linker.cpp'
    sysmodule = 'src/core/libraries/sysmodule/sysmodule_internal.cpp'
    replace(h, '    s32 PrepareBootModule(const std::filesystem::path& path);', '''    s32 PrepareBootModule(const std::filesystem::path& path);
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    void SelectDonorMspaceProvider(s32 libc_handle);
#endif''')
    replace(h, '    std::vector<u32> m_prepared_boot_modules;', '''    std::vector<u32> m_prepared_boot_modules;
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    bool m_donor_mspace_active{};
    bool m_donor_mspace_pending{};
    std::vector<Loader::SymbolRecord> m_donor_mspace_exports;
#endif''')
    replace(cpp, '#include "core/libraries/kernel/kernel.h"', '#include "core/libraries/playgo/bachata_installed_package.h"\n#include <array>\n#include "core/libraries/kernel/kernel.h"')
    replace(cpp, '    // Relocate all modules\n', '''#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    m_donor_mspace_active = BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial());
    m_donor_mspace_pending = m_donor_mspace_active;
#endif
    // Relocate all modules
''')
    replace(cpp, 's32 Linker::PrepareBootModule(const std::filesystem::path& path) {', '''#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
static std::span<const std::string_view> DonorMspaceNids() {
    // Every allocation/handle operation and the stats/aligned-realloc imports
    // observed in the actual ISS boot log share one provider.
    static constexpr std::array<std::string_view, 11> nids{
        "-hn1tcVHq5Q", "W6SiVSiCDtI", "OJjm-QOIHlI", "Vla-Z+eXlxo",
        "LYo3GhIlB38", "gigoVHZvVPE", "iF1iQHzxBJU", "fEoW6BJsPt4",
        "mfHdJTIvhuo", "k04jLXu3+Ic", "p6lrRW8-MLY"};
    return nids;
}

void Linker::SelectDonorMspaceProvider(s32 libc_handle) {
    if (!m_donor_mspace_active || !m_donor_mspace_pending) return;
    m_donor_mspace_pending = false;
    std::vector<Loader::SymbolRecord> candidates;
    auto* libc = libc_handle >= 0 ? GetModule(libc_handle) : nullptr;
    if (libc) {
        for (const auto nid : DonorMspaceNids()) {
            const Loader::SymbolRecord* unique = nullptr;
            bool ambiguous = false;
            for (const auto& library : libc->GetExportLibs()) {
                if (library.name != "libc") continue;
                for (const auto& module : libc->GetExportModules()) {
                    Loader::SymbolResolver key{};
                    key.name = nid;
                    key.library = library.name;
                    key.library_version = library.version;
                    key.module = module.name;
                    key.type = Loader::SymbolType::Function;
                    const auto* record = libc->export_sym.FindSymbol(key);
                    if (!record || !record->virtual_address || record->hle_adapter || record->hle_fallback) continue;
                    if (unique && record != unique) ambiguous = true;
                    if (!unique) unique = record;
                }
            }
            if (!unique || ambiguous) break;
            candidates.push_back(*unique);
        }
    }
    if (candidates.size() == DonorMspaceNids().size()) {
        m_donor_mspace_exports = std::move(candidates);
    }
    LOG_INFO(Core_Linker, "BACHATA_DONOR_MSPACE_PROVIDER guest={} required={} libc={}",
             m_donor_mspace_exports.size(), DonorMspaceNids().size(), libc_handle);
}
#endif

s32 Linker::PrepareBootModule(const std::filesystem::path& path) {''')
    replace(cpp, '    const bool prefer_guest_fios2 = sr.library == "libSceFios2" &&', '''    const auto mspace_nids = DonorMspaceNids();
    const auto mspace_nid = std::ranges::find(mspace_nids, sr.name);
    const bool donor_mspace = m_donor_mspace_active &&
        sr.type == Loader::SymbolType::Function && mspace_nid != mspace_nids.end() &&
        ((sr.library == "libc" && sr.module == "libc") ||
         (sr.library == "libSceLibcInternal" && sr.module == "libSceLibcInternal"));
    if (donor_mspace) {
        if (!m_donor_mspace_exports.empty()) {
            *return_info = m_donor_mspace_exports.at(mspace_nid - mspace_nids.begin());
            return true;
        }
        if (hle_record && !hle_record->hle_fallback) {
            *return_info = *hle_record;
            // Initial relocation is provisional until the entire native
            // family is known. A chosen HLE family must never mix with LLE.
            return !m_donor_mspace_pending;
        }
    }
    const bool prefer_guest_fios2 = sr.library == "libSceFios2" &&''')
    replace(cpp, '    // Check if it an exported function from one of our loaded libraries\n    for (const auto& mod : m_modules) {', '''    // Check if it an exported function from one of our loaded libraries
    for (const auto& mod : m_modules) {
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
        if (donor_mspace) break; // no partial native Mspace provider
#endif''')
    replace(sysmodule, '        if (libc >= 0 || fios_handle >= 0) linker->RelocateAllImports();', '''        linker->SelectDonorMspaceProvider(libc);
        if (libc >= 0 || fios_handle >= 0) linker->RelocateAllImports();''')
