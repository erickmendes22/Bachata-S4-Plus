#!/usr/bin/env python3
"""Embed mandatory CUSA08809/01.00 SNDX into the core before optional patch selection.

Use only against the source checkout used to compile the actual optimized core025.
This does not recompile or replace the Bachata R30 binary by itself.
"""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

AUDIO = {
    "0x00da169d": "4b8b44ec40488d50ff48c1ea2e750d4a8d04b0a80f740c4489f9eb57e9920000009090",
    "0x00da179d": "498b54cc404c8d5aff49c1eb2e750e4a8d14b2f6c20f740b4489feeb75e9a800000090",
}
HOOK = """    // Mandatory, non-selectable audio fix for CUSA08809 01.00. Applied
    // before managed/legacy patches regardless of user patch preferences.
    if (g_game_serial == "CUSA08809" && CurrentAppVersion() == "01.00") {
        struct Write { const char* guest; const char* value; };
        static constexpr Write writes[] = {
            {"0x00da169d", "4b8b44ec40488d50ff48c1ea2e750d4a8d04b0a80f740c4489f9eb57e9920000009090"},
            {"0x00da179d", "498b54cc404c8d5aff49c1eb2e750e4a8d14b2f6c20f740b4489feeb75e9a800000090"},
        };
        struct Resolved { uintptr_t target; std::vector<uint8_t> bytes; };
        std::vector<Resolved> resolved;
        bool valid = g_eboot_address && g_eboot_image_size;
        for (const auto& entry : writes) {
            uint64_t guest = 0;
            std::vector<uint8_t> bytes;
            if (!valid || !ParseStrictHexAddress(entry.guest, guest) ||
                guest < 0x400000 || !ParseStrictHexBytes(entry.value, bytes) ||
                guest - 0x400000 > g_eboot_image_size ||
                bytes.size() > g_eboot_image_size - (guest - 0x400000)) {
                valid = false;
                break;
            }
            const uintptr_t target = g_eboot_address + guest - 0x400000;
            if (!IsWithinEbootBounds(target, bytes.size())) {
                valid = false;
                break;
            }
            resolved.push_back({target, std::move(bytes)});
        }
        if (!valid || resolved.size() != 2) {
            LOG_CRITICAL(Loader, "SOTC_SNDX_INTERNAL_FAILED reason=invalid_guest_layout");
        } else {
            for (const auto& w : resolved) {
                if (std::memcmp(reinterpret_cast<void*>(w.target), w.bytes.data(),
                                w.bytes.size()) != 0) {
                    std::memcpy(reinterpret_cast<void*>(w.target), w.bytes.data(),
                                w.bytes.size());
                }
            }
            LOG_INFO(Loader, "SOTC_SNDX_INTERNAL_APPLIED serial=CUSA08809 version=01.00 writes=2");
        }
    }
"""

def apply_cpp(filename):
    p = Path(filename)
    text = p.read_text(encoding="utf-8")
    if "SOTC_SNDX_INTERNAL_APPLIED" in text:
        assert HOOK.strip() in text, "Divergent pre-existing audio hook"
        return False
    anchor = "void OnGameLoaded() {\n"
    assert text.count(anchor) == 1, "Unexpected source revision"
    p.write_text(text.replace(anchor, anchor + HOOK, 1), encoding="utf-8")
    return True

def clean_optional_xml(filename):
    p = Path(filename)
    tree = ET.parse(p)
    n = 0
    for plist in tree.findall(".//PatchList"):
        for line in list(plist):
            key = line.get("Address", "").lower()
            if key in AUDIO:
                assert line.get("Value", "").lower() == AUDIO[key], "Different SNDX bytes"
                plist.remove(line)
                n += 1
    if n:
        tree.write(p, encoding="utf-8", xml_declaration=True)
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--patch-xml", nargs="*", default=[])
    a = ap.parse_args()
    changed = apply_cpp(Path(a.source) / "src/common/memory_patcher.cpp")
    removed = sum(clean_optional_xml(path) for path in a.patch_xml)
    print(f"mandatory SNDX hook installed={changed}; duplicated XML entries removed={removed}")
    print("Native source change only. Compile into the actual Bachata core025 before making an APK.")

if __name__ == "__main__":
    main()
