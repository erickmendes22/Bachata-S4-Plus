"""Restore native Android runtime contracts lost by the 0.18.1 source update.

Donors: FEX host be6bc2e9 and GoW3 1759fda5fd58 / 10afc84abce3.
No changes to guest save files, readback mode or videoout guest ABI.
"""
from pathlib import Path


def replace(path: Path, old: str, new: str):
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"Android runtime parity anchor drift: {path}: {old[:100]}")
    path.write_text(text.replace(old, new, 1))


def apply(root: Path):
    driver = root / "src/core/libraries/videoout/driver.cpp"
    replace(driver, '#include "imgui/renderer/imgui_core.h"',
            '#include "imgui/renderer/imgui_core.h"\n'
            '#ifdef ENABLE_BACHATA_RUNTIME\n'
            '#include "platform/bachata/runtime_client.h"\n'
            '#endif')
    replace(driver, "    presenter->Present(req.frame);",
            "    presenter->Present(req.frame);\n"
            "#ifdef ENABLE_BACHATA_RUNTIME\n"
            "    // Original Bachata frame protocol: report only actual guest flips.\n"
            "    Platform::Bachata::ReportPresentedFrame();\n"
            "#endif")

    imgui = root / "src/imgui/renderer/imgui_impl_sdl3.cpp"
    replace(imgui, """    if (bd->gamepads.Size == 0)
        return;
    io.BackendFlags |= ImGuiBackendFlags_HasGamepad;""",
            """    if (bd->gamepads.Size == 0) {
#ifdef ENABLE_BACHATA_RUNTIME
        // The Java touch controller is delivered to the guest pad via the
        // runtime socket, not registered as an SDL gamepad. Read the same
        // locked snapshot on the ImGui thread, without consuming pad samples.
        const auto state = controllers[0]->ReadState();
        using Button = Libraries::Pad::OrbisPadButtonDataOffset;
        const auto pressed = [&](Button button) {
            return state.connected &&
                   (static_cast<u32>(state.buttonsState) & static_cast<u32>(button)) != 0;
        };
        if (state.connected)
            io.BackendFlags |= ImGuiBackendFlags_HasGamepad;
        io.AddKeyEvent(ImGuiKey_GamepadStart, pressed(Button::Options));
        io.AddKeyEvent(ImGuiKey_GamepadFaceDown, pressed(Button::Cross));
        io.AddKeyEvent(ImGuiKey_GamepadFaceRight, pressed(Button::Circle));
        io.AddKeyEvent(ImGuiKey_GamepadFaceUp, pressed(Button::Triangle));
        io.AddKeyEvent(ImGuiKey_GamepadDpadUp, pressed(Button::Up));
        io.AddKeyEvent(ImGuiKey_GamepadDpadDown, pressed(Button::Down));
        io.AddKeyEvent(ImGuiKey_GamepadDpadLeft, pressed(Button::Left));
        io.AddKeyEvent(ImGuiKey_GamepadDpadRight, pressed(Button::Right));
        io.AddKeyEvent(ImGuiKey_GamepadL1, pressed(Button::L1));
        io.AddKeyEvent(ImGuiKey_GamepadR1, pressed(Button::R1));
        io.AddKeyEvent(ImGuiKey_GamepadL3, pressed(Button::L3));
        io.AddKeyEvent(ImGuiKey_GamepadR3, pressed(Button::R3));
#endif
        return;
    }
    io.BackendFlags |= ImGuiBackendFlags_HasGamepad;""")

    return {"fps":"guest flip event","pad":"remote SDL gamepad input"}
