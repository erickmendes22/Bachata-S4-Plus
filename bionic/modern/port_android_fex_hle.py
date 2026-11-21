#!/usr/bin/env python3
"""Restore executable HLE registration that the FEX-enabled 0.21.1 port omitted.

The 0.21.1 module-driven HLE table excludes libSceAvPlayer. Prelinking
guest calls to it therefore manufactures ENOSYS veneers, even though real
AvPlayer HLE exists. The older Bachata glibc runtime initializes it.
Also call the existing FEX libc alias registration that implements the
known LLE-unsafe functions; never map ARM host entrypoints as guest code.
"""
from pathlib import Path
import argparse

ANCHOR = """    const auto& game_specific_modules_path =
        sys_module_path /
        (game_info->GameSerial().empty() ? std::string_view("no_serial") : game_info->GameSerial());
    {"""

REPLACEMENT = """    const auto& game_specific_modules_path =
        sys_module_path /
        (game_info->GameSerial().empty() ? std::string_view("no_serial") : game_info->GameSerial());
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    // BIONIC_021_FEX_EARLY_AVPLAYER_HLE: prevent ENOSYS veneers from being
    // cached for functions already implemented by libSceAvPlayer HLE.
    // Preserve game-specific LLE where the user has actually installed it.
    if (!std::filesystem::exists(game_specific_modules_path / "libSceAvPlayer.sprx")) {
        Libraries::AvPlayer::RegisterLib(sym);
    }
    // BIONIC_021_FEX_LIBC_ALIASES: the original FEX-specific aliases for
    // known broken LLE memory, math, string and C++ runtime entrypoints.
    Libraries::LibcInternal::ForceRegisterLib(sym);
#endif
    {"""

def integrate(root: Path) -> None:
    path = root / "src/core/libraries/libs.cpp"
    source = path.read_text()
    if "BIONIC_021_FEX_EARLY_AVPLAYER_HLE" in source:
        raise RuntimeError("FEX HLE boot fix already present")
    count = source.count(ANCHOR)
    if count != 1:
        raise RuntimeError(f"{path}: expected one versioned 0.21.1 HLE anchor, found {count}")
    if "Libraries::AvPlayer::RegisterLib" in source:
        raise RuntimeError("Upstream has its own AvPlayer registration; review for duplicate")
    if "Libraries::LibcInternal::ForceRegisterLib" in source:
        raise RuntimeError("Upstream has its own FEX aliases; review for duplicate")
    path.write_text(source.replace(ANCHOR, REPLACEMENT, 1))
    print("BIONIC_021_FEX_EARLY_HLE_REGISTRATION_READY")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    integrate(ap.parse_args().source)
