"""Add opt-in transactional opcode guards for the donor's versioned patch recipes."""
from pathlib import Path
import shutil


def apply(root):
    src = Path(root) / 'src'
    header = src / 'common/memory_patcher.h'
    path = src / 'common/memory_patcher.cpp'
    h = header.read_text()
    text = path.read_text()
    if 'BACHATA_PATCH_GROUP_APPLIED' in text:
        raise RuntimeError('guarded patch group overlay applied twice')

    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise RuntimeError(f'guarded patch anchor count={text.count(old)}: {old[:100]!r}')
        text = text.replace(old, new)

    anchor = '    bool little_endian{false};\n};'
    assert h.count(anchor) == 1
    h = h.replace(anchor, '''    bool little_endian{false};
    std::string expected;
    std::string if_enabled;
    std::string if_disabled;
};''')
    anchor = '    bool is_enabled{false};\n    std::vector<PatchLine> lines;'
    assert h.count(anchor) == 1
    h = h.replace(anchor, '''    bool is_enabled{false};
    bool require_all_expected{false};
    std::vector<PatchLine> lines;''')
    replace('#include "memory_patcher.h"', '''#include "memory_patcher.h"
#include "common/guarded_patch_group.h"
#include "core/memory.h"''')
    replace('    line.address = node.attribute("Address").value();', '''    line.expected = node.attribute("Expected").value();
    line.if_enabled = node.attribute("IfEnabled").value();
    line.if_disabled = node.attribute("IfDisabled").value();
    line.address = node.attribute("Address").value();''')
    replace('        def.note = it->attribute("Note").value();', '''        def.note = it->attribute("Note").value();
        def.require_all_expected = it->attribute("RequireAllExpected").as_bool(false);''')
    replace('bool ApplyLine(const PatchDefinition& def, const PatchLine& line, bool version_matches,',
            GROUP_SUPPORT + '\nbool ApplyLine(const PatchDefinition& def, const PatchLine& line, bool version_matches,')
    replace('    const auto app_version = CurrentAppVersion();\n\n    for (const auto& def : defs) {',
            '''    const auto app_version = CurrentAppVersion();
    const auto choices = GuardedChoices(defs, &enabled_ids, app_version);

    for (const auto& def : defs) {''')
    replace('        bool all_lines_ok = true;', '''        if (def.require_all_expected) {
            std::string error;
            const bool applied = ApplyGuardedGroup(def, choices, version_matches, error);
            result.ok &= applied;
            result.records.push_back({def.id, def.name,
                applied ? PatchApplyStatus::Applied : PatchApplyStatus::WriteFailed, error});
            continue;
        }

        bool all_lines_ok = true;''')
    replace('''    const auto app_version = CurrentAppVersion();
    auto patch_xml = doc.child("Patch");''', '''    const auto app_version = CurrentAppVersion();
    const auto definitions = EnumeratePatchDefinitions(path);
    const auto choices = GuardedChoices(definitions, nullptr, app_version);
    auto patch_xml = doc.child("Patch");''')
    replace('''        const bool version_matches = metadata_app_ver == app_version;

        auto patch_list = it->first_child();''', '''        const bool version_matches = metadata_app_ver == app_version;

        if (it->attribute("RequireAllExpected").as_bool(false)) {
            PatchDefinition def;
            def.name = name;
            def.app_version = metadata_app_ver;
            def.require_all_expected = true;
            for (const auto line : it->first_child().children()) {
                def.lines.push_back(BuildPatchLine(line));
            }
            std::string error;
            ApplyGuardedGroup(def, choices, version_matches, error);
            continue;
        }

        auto patch_list = it->first_child();''')
    header.write_text(h)
    path.write_text(text)
    shutil.copy2(Path(__file__).with_name('guarded_patch_group.h'),
                 src / 'common/guarded_patch_group.h')
    return {'contract': 'RequireAllExpected', 'versionGated': True,
            'allPreimagesBeforeWrites': True, 'conditions': ['IfEnabled', 'IfDisabled'],
            'legacyWithoutAttributeUnchanged': True}


GROUP_SUPPORT = r'''struct GuardedPatchChoices {
    std::unordered_set<std::string> known;
    std::unordered_set<std::string> enabled;
    std::unordered_set<std::string> ambiguous;
};

GuardedPatchChoices GuardedChoices(const std::vector<PatchDefinition>& definitions,
                                  const std::unordered_set<std::string>* selected,
                                  const std::string& version) {
    GuardedPatchChoices choices;
    for (const auto& def : definitions) {
        if (def.app_version != version) continue;
        if (!choices.known.insert(def.name).second) choices.ambiguous.insert(def.name);
        if (selected ? selected->contains(def.id) : def.is_enabled) {
            choices.enabled.insert(def.name);
        }
    }
    return choices;
}

bool ApplyGuardedGroup(const PatchDefinition& def, const GuardedPatchChoices& choices,
                       bool version_matches, std::string& error) {
    const auto reject = [&](const char* reason) {
        error = reason;
        LOG_WARNING(Loader, "BACHATA_PATCH_GROUP_REJECT name={} reason={}", def.name, error);
        return false;
    };
    if (!version_matches) return reject("app version mismatch");
    if (!g_eboot_address || !g_eboot_image_size ||
        g_eboot_image_size > UINTPTR_MAX - g_eboot_address) {
        return reject("invalid game image bounds");
    }
    std::vector<GuardedGroup::Write> writes;
    writes.reserve(def.lines.size());
    for (const auto& line : def.lines) {
        if (line.type != PatchLineType::Bytes || line.little_endian ||
            !line.target.empty() || !line.size.empty() || line.mask_offset != 0) {
            return reject("guarded groups require fixed raw bytes");
        }
        if (!line.if_enabled.empty() && !line.if_disabled.empty()) {
            return reject("conflicting patch conditions");
        }
        const auto& condition = line.if_enabled.empty() ? line.if_disabled : line.if_enabled;
        if (!condition.empty()) {
            if (!choices.known.contains(condition) || choices.ambiguous.contains(condition)) {
                return reject("unknown or ambiguous conditional patch");
            }
            const bool active = choices.enabled.contains(condition);
            if ((!line.if_enabled.empty() && !active) ||
                (!line.if_disabled.empty() && active)) continue;
        }
        std::uint64_t address{};
        GuardedGroup::Write write;
        if (!ParseStrictHexAddress(line.address, address) || address < 0x400000 ||
            address - 0x400000 > g_eboot_image_size ||
            !ParseStrictHexBytes(line.expected, write.expected) ||
            !ParseStrictHexBytes(line.value, write.value)) {
            return reject("invalid fixed address or expected/value bytes");
        }
        write.offset = static_cast<std::size_t>(address - 0x400000);
        writes.push_back(std::move(write));
    }
    auto* memory = Common::Singleton<Core::MemoryManager>::Instance();
    const auto mapped = [&](std::size_t offset, std::size_t size) {
        // Unlike ClampRangeSize's <1 GiB fast path, this validates every VMA.
        // PS4 executable mappings share the guest's 40-bit address space.
        return memory->ClampGpuRangeSize(g_eboot_address + offset, size) == size;
    };
    if (!GuardedGroup::Apply(
            std::span{reinterpret_cast<std::uint8_t*>(g_eboot_address),
                      static_cast<std::size_t>(g_eboot_image_size)},
            std::span<const GuardedGroup::Write>{writes}, mapped, error)) {
        LOG_WARNING(Loader, "BACHATA_PATCH_GROUP_REJECT name={} reason={}", def.name, error);
        return false;
    }
#ifdef MEMORY_PATCHER_TEST_OBSERVER
    if (auto observer = GetPatchMemoryObserver()) {
        for (const auto& write : writes) observer(def.name);
    }
#endif
    LOG_INFO(Loader, "BACHATA_PATCH_GROUP_APPLIED name={} writes={} expected=verified",
             def.name, writes.size());
    return true;
}
'''
