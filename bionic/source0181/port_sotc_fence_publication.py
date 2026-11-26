#!/usr/bin/env python3
"""Publish SotC EOP/EOS backing labels through the active donor ownership path.

The FEX physical alias bypasses guest page protections. Invalidating before the
write resolves neighboring GPU data and marks the label's page CPU-modified;
otherwise a retained readback can restore the old label and strand a guest or
PM4 wait. This does not enable the donor's optional deferred EOP path.
"""
from pathlib import Path


FENCE_PUBLICATION = r'''void Liverpool::WriteFenceValue(void* address, u64 data, u32 num_bytes) {
    const auto serial = Common::ElfInfo::Instance().GameSerial();
    if (rasterizer && (serial == "CUSA08809" || serial == "CUSA08034")) {
        // The physical alias cannot fault through the guest's page protection.
        // Resolve GPU bytes before publishing the new label, invalidate older
        // readbacks, and make the next GPU bind upload this CPU-owned value.
        // This is the donor's normal EOP/EOS path, without optional EOP deferral.
        rasterizer->InvalidateMemory(std::bit_cast<VAddr>(address), num_bytes, true);
    }
    auto* memory = Core::Memory::Instance();
    ASSERT(memory->TryWriteBacking(address, &data, num_bytes));
}

'''


def apply(root):
    src = Path(root) / "src"
    header = src / "video_core/amdgpu/liverpool.h"
    cpp = src / "video_core/amdgpu/liverpool.cpp"

    def replace(text, old, new, label):
        if text.count(old) != 1:
            raise RuntimeError(f"SotC fence publication drift ({label}): {text.count(old)}")
        return text.replace(old, new, 1)

    h = header.read_text()
    h = replace(h, "    void ProcessCommands();",
                "    void WriteFenceValue(void* address, u64 data, u32 num_bytes);\n"
                "    void ProcessCommands();", "helper declaration")

    s = cpp.read_text()
    s = replace(s, "void Liverpool::ProcessCommands() {",
                FENCE_PUBLICATION + "void Liverpool::ProcessCommands() {",
                "normal fence publication")
    old_eos = '''                event_eos->SignalFence([](void* address, u64 data, u32 num_bytes) {
                    auto* memory = Core::Memory::Instance();
                    ASSERT(memory->TryWriteBacking(address, &data, num_bytes));
                });'''
    new_eos = '''                event_eos->SignalFence([this](void* address, u64 data, u32 num_bytes) {
                    WriteFenceValue(address, data, num_bytes);
                });'''
    s = replace(s, old_eos, new_eos, "EOS label")
    old_eop = '''                event_eop->SignalFence(
                    [](void* address, u64 data, u32 num_bytes) {
                        auto* memory = Core::Memory::Instance();
                        ASSERT(memory->TryWriteBacking(address, &data, num_bytes));
                    },'''
    new_eop = '''                event_eop->SignalFence(
                    [this](void* address, u64 data, u32 num_bytes) {
                        WriteFenceValue(address, data, num_bytes);
                    },'''
    s = replace(s, old_eop, new_eop, "EOP label")
    # Build both edited texts before publishing either, so anchor drift cannot
    # leave a half-adapted source tree.
    header.write_text(h)
    cpp.write_text(s)
    return {
        "sotcFencePublication": "invalidate/readback before physical EOP/EOS label write",
        "titles": ["CUSA08809", "CUSA08034"],
        "donorPath": "active WriteFenceValue; no SOTC_EOP_DEFER opt-in",
        "ownership": "CPU label survives outstanding readbacks and subsequent GPU uploads",
    }
