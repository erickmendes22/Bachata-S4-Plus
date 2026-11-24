#!/usr/bin/env python3
"""Source-first parity for the actual Shadow NGS2 imports and Order image descriptor contract."""
from pathlib import Path

def one(s, a, b):
    if s.count(a) != 1:
        raise RuntimeError("Donor parity anchor drift: " + a[:150])
    return s.replace(a,b,1)

def apply(root: Path):
    libs = root / "src/core/libraries/libs.cpp"
    cmake = root / "CMakeLists.txt"
    resource = root / "src/shader_recompiler/resource.h"
    src = libs.read_text()
    src = one(src, '#include "core/libraries/fios2/fios2.h"',
              '#include "core/libraries/fios2/fios2.h"\n'
              'namespace Libraries { void RegisterBachataSotcNgs2(Core::Loader::SymbolsResolver*); }')
    src = one(src, '        const bool shadow_guest_archive =\n',
              '        // The same 11 NGS2 NIDs as the dedicated SotC Android mixer.\n'
              '        // Register before guest relocation; the firmware LLE remains preferred.\n'
              '        if (game_specific_modules_path.filename() == "CUSA08809" &&\n'
              '            !std::filesystem::exists(game_specific_modules_path / "libSceNgs2.sprx")) {\n'
              '            Libraries::RegisterBachataSotcNgs2(sym);\n'
              '        }\n'
              '        const bool shadow_guest_archive =\n')
    libs.write_text(src)

    local=Path(__file__).resolve().parent
    c=cmake.read_text()
    anchor='target_sources(shadps4 PRIVATE "' + str(local.parent/"generic"/"android_fex_fiber.cpp") + '")\n'
    c=one(c,anchor,anchor+'target_sources(shadps4 PRIVATE "'+str(local/"sotc_ngs2_mixer.c")+'" "'+str(local/"donor_parity_bridge.cpp")+'")\n')
    cmake.write_text(c)
    s=resource.read_text()
    s=one(s,'struct ImageResource {','// Source-equivalent mapped image check from Order Android ImageResource::GetSharp.\n'
          'bool IsBachataMappedImageBase(u64 address);\n\nstruct ImageResource {')
    s=one(s,'        if (!image.Valid()) {\n',
          '        if (!image.Valid() || (!std::is_constant_evaluated() && image.Address() != 0 &&\n'
          '                              !IsBachataMappedImageBase(image.Address()))) {\n')
    s=one(s,'#include <bit>\n','#include <bit>\n#include <type_traits>\n')
    resource.write_text(s)
    return {"shadow":"actual donor PCM/VAG/ATRAC9 NGS2 mixer, 11 imports, FEX callbacks, staged LLE wins",
            "order":"image mapping validated during GetSharp before SPIR-V specialization"}
