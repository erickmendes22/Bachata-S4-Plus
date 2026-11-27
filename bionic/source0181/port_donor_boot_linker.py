#!/usr/bin/env python3
"""Transfer the G3PROBE5 linked-module relocation and provider contract.

ISS 879fe3c and TLOU 62ea759 scripts/link_modules.py + src/probe.c.
Use the native game modules already loaded through FEX/SAF, not boot images.
Host-owned SDK objects and the explicit host runtime contracts stay HLE.
"""
from pathlib import Path

POLICY = r'''static bool DonorLibcImport(const Loader::SymbolResolver& sr) {
    return sr.library == "libc" || sr.library == "libSceLibcInternal";
}

static bool DonorHostContract(const Loader::SymbolResolver& sr) {
    // Both donors' runtime_resolve() intercepts these libc contracts. The SDK
    // marker objects belong to the Bachata/FEX loader. Stateless sincosf/time
    // are also supplied by the donor runtime. Do not move their ownership.
    static constexpr std::array<std::string_view, 15> functions{
        "bzQExy189ZI", "8G2LB+A3rzg", "tsvEmnenz48", "H2e8t5ScQGc",
        "3GPpjQdAMTw", "9rAeANT2tyE", "2emaaluWzUw", "uMei1W9uyNo",
        "8zTFvBIAIN8", "Q3VBxCXhUHs", "+P6FRGH4LfA", "DfivPArhucg",
        "j4ViWNHEgww", "wLlFkwG9UcQ", "pztV4AF18iI"};
    if (sr.type == Loader::SymbolType::Object)
        return sr.name == "P330P3dFF68" || sr.name == "ZT4ODD2Ts9o";
    return sr.type == Loader::SymbolType::Function &&
           ((sr.library == "libc" && sr.name != "pztV4AF18iI" &&
             std::ranges::find(functions, sr.name) != functions.end()) ||
            (sr.library == "libSceLibcInternal" && sr.name == "pztV4AF18iI"));
}

const Loader::SymbolRecord* Linker::FindDonorBootExport(const Loader::SymbolResolver& sr) const {
    // The donor builds the export index before running any module initializer.
    // Only actual prepared modules enter this index. Other game/custom modules
    // cannot acquire the fallback privileges of a firmware libc export.
    const auto unique = [&](std::string_view wanted, bool exact) {
        const Loader::SymbolRecord* found = nullptr;
        for (const s32 handle : m_donor_boot_handles) {
            const auto* mod = GetModule(handle);
            if (!mod) continue;
            if (wanted == "libc" && handle != m_donor_boot_handles[0]) continue;
            for (const auto& lib : mod->GetExportLibs()) {
                if (lib.name != wanted || (exact && lib.version != sr.library_version)) continue;
                for (const auto& module : mod->GetExportModules()) {
                    if (exact && module.name != sr.module) continue;
                    auto key = sr;
                    key.library = lib.name;
                    key.library_version = lib.version;
                    key.module = module.name;
                    const auto* candidate = mod->export_sym.FindSymbol(key);
                    if (!candidate || !candidate->virtual_address || candidate->hle_adapter ||
                        candidate->hle_fallback) continue;
                    if (found && found != candidate)
                        return std::pair<const Loader::SymbolRecord*,bool>{nullptr,true};
                    found = candidate;
                }
            }
        }
        return std::pair<const Loader::SymbolRecord*,bool>{found,false};
    };
    if (sr.type != Loader::SymbolType::Function && sr.type != Loader::SymbolType::Object)
        return nullptr;
    auto [exact, ambiguous] = unique(sr.library, true);
    if (exact || ambiguous) return exact;
    if (sr.library == "libSceLibcInternal") {
        auto [alias, alias_ambiguous] = unique("libc", false);
        if (alias || alias_ambiguous) return alias;
    }
    return unique(sr.library, false).first;
}

void Linker::SelectDonorBootProviders(s32 libc_handle, s32 fios_handle) {
    if (!m_donor_mspace_active || m_donor_boot_selected) return;
    m_donor_boot_handles = {libc_handle, fios_handle};
    m_donor_boot_selected = true;
    if (libc_handle < 0) return;
    // An actual linked donor uses one native libc for heap/stdio/C++/locale.
    // A partial provider must not switch those families halfway through boot.
    // Prove closure on the real imports of the eboot AND both boot modules.
    size_t native = 0, host = 0, missing = 0;
    for (const auto& mod : m_modules) {
        for (const auto& record : mod->import_sym.GetSymbols()) {
            const auto fields = Common::SplitString(record.name, '#');
            if (fields.size() != 5) continue;
            Loader::SymbolResolver sr{};
            sr.name = fields[0]; sr.library = fields[1]; sr.module = fields[3];
            if (!DonorLibcImport(sr)) continue;
            if (fields[4] == "Function") sr.type = Loader::SymbolType::Function;
            else if (fields[4] == "Object") sr.type = Loader::SymbolType::Object;
            else continue;
            const auto* begin = fields[2].data();
            const auto* end = begin + fields[2].size();
            const auto result = std::from_chars(begin,end,sr.library_version);
            if (result.ec != std::errc{} || result.ptr != end) { ++missing; continue; }
            const auto* hle = m_hle_symbols.FindSymbol(sr);
            if (DonorHostContract(sr) && hle && !hle->hle_fallback) { ++host; continue; }
            if (FindDonorBootExport(sr)) { ++native; continue; }
            ++missing;
            LOG_WARNING(Core_Linker,"BACHATA_DONOR_LIBC_MISSING {} {} {}",sr.name,sr.library,sr.module);
        }
    }
    // One native provider, even when an import is missing. Missing imports
    // remain errors, not a reason to switch heap/FILE ownership mid-boot.
    m_donor_native_libc = GetModule(libc_handle) != nullptr;
    LOG_INFO(Core_Linker,"BACHATA_DONOR_LIBC_PROVIDER native={} host={} missing={} chosen={}",
             native,host,missing,m_donor_native_libc);
}

'''

RESOLUTION = r'''    const bool donor_libc = m_donor_mspace_active && DonorLibcImport(sr) &&
        (sr.type == Loader::SymbolType::Function || sr.type == Loader::SymbolType::Object);
    const bool donor_host = donor_libc && DonorHostContract(sr) &&
        hle_record && !hle_record->hle_fallback;
    if (donor_libc && !donor_host) {
        if (!m_donor_boot_selected) {
            // Provisional relocation: no guest code runs before selection.
            // Do not seal a host heap/stdio object before libc is linked.
            if (hle_record) *return_info = *hle_record;
            else if (sr.type == Loader::SymbolType::Function)
                return_info->hle_adapter = m_hle_symbols.AddUnsupportedFunction(sr);
            return false;
        }
        if (m_donor_native_libc) {
            if (const auto* native = FindDonorBootExport(sr)) {
                *return_info = *native;
                return true;
            }
            // A later-loaded module cannot switch ownership of a selected
            // native libc. An unresolved late import remains a genuine error.
            return_info->name = sr.name;
            LOG_ERROR(Core_Linker,"BACHATA_DONOR_LIBC_LATE_MISSING {} {}",sr.name,sr.library);
            if (sr.type == Loader::SymbolType::Function) {
                auto key = sr;
                key.name += ".donor_missing";
                return_info->hle_adapter = m_hle_symbols.AddUnsupportedFunction(key);
            }
            return false;
        }
    }
'''


def apply(root: Path):
    root=Path(root)/'src/core'
    def edit(rel,a,b):
        p=root/rel;s=p.read_text();assert s.count(a)==1,(rel,a[:100],s.count(a));p.write_text(s.replace(a,b,1))
    edit('linker.h','#include <algorithm>','#include <algorithm>\n#include <array>')
    edit('linker.h','    void SelectDonorMspaceProvider(s32 libc_handle);','''    void SelectDonorMspaceProvider(s32 libc_handle);
    void SelectDonorBootProviders(s32 libc_handle, s32 fios_handle);''')
    edit('linker.h','    bool m_donor_mspace_active{};','''    std::array<s32,2> m_donor_boot_handles{-1,-1};
    bool m_donor_boot_selected{}, m_donor_native_libc{};
    const Loader::SymbolRecord* FindDonorBootExport(const Loader::SymbolResolver&) const;
    bool m_donor_mspace_active{};''')
    edit('linker.cpp','#include <array>','#include <array>\n#include <charconv>')
    edit('linker.cpp','static std::span<const std::string_view> DonorMspaceNids() {',POLICY+'static std::span<const std::string_view> DonorMspaceNids() {')
    # Do not change the older dedicated Mspace selection path until the
    # complete native provider is selected, including its actual imports.
    edit('linker.cpp','    const auto mspace_nids = DonorMspaceNids();','    const auto mspace_nids = DonorMspaceNids();\n'+RESOLUTION.replace('if (donor_libc && !donor_host)', 'if (donor_libc && !donor_host &&\n        (m_donor_boot_selected || std::ranges::find(mspace_nids, sr.name) == mspace_nids.end()))'))
    # Mirror the donor's by-NID/version fallback for already linked modules
    # after the established exact/HLE precedence. Avoid bypassing Mspace.
    edit('linker.cpp','    // BACHATA_SHARED_IO_LIBC_DEPENDENCY:', '''    if (m_donor_mspace_active && m_donor_boot_selected && !donor_mspace &&
        !donor_libc && (sr.library != "libSceFios2" || prefer_guest_fios2)) {
        if (const auto* native = FindDonorBootExport(sr)) {
            *return_info = *native;
            return true;
        }
    }
    // BACHATA_SHARED_IO_LIBC_DEPENDENCY:''')
    # Match donor link_modules.py handling of defined and weak-undefined
    # relocations. Keep the existing FEX relocation logic for all other titles.
    edit('linker.cpp','''            auto sym_visibility = sym.GetVisibility();
            u64 symbol_virtual_addr = 0;''','''            auto sym_visibility = sym.GetVisibility();
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
            if (m_donor_mspace_active && (sym_bind == STB_GLOBAL || sym_bind == STB_WEAK)) {
                if (sym.st_shndx != 0) {
                    rel_value = (sym.st_shndx == 0xfff1 ? 0 : rel_base_virtual_addr) + sym.st_value + addend;
                    rel_is_resolved = true;
                    module->SetRelaBit(bit_idx);
                    break;
                }
                if (sym_bind == STB_WEAK && Common::SplitString(names_tlb + sym.st_name, '#').size() != 3) {
                    rel_value = 0;
                    rel_is_resolved = true;
                    module->SetRelaBit(bit_idx);
                    break;
                }
            }
#endif
            u64 symbol_virtual_addr = 0;''')
    edit('libraries/sysmodule/sysmodule_internal.cpp','        linker->SelectDonorMspaceProvider(libc);','        linker->SelectDonorMspaceProvider(libc);\n        linker->SelectDonorBootProviders(libc, fios_handle);')
    return {'linked_module_index': True, 'native_libc_import_closure':True,'defined_and_weak_relocations':True}
