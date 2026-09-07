# Bachata S4+ — Third-Party Notices and Project Origins

This document describes the known upstream projects, references, and third-party components relevant to Bachata S4+.

It is provided for attribution, transparency, and licensing information.

Third-party software remains subject to its respective copyright and license terms.

---

## Bachata S4

Project: `JICA98/Bachata-S4`

Role in Bachata S4+:

Bachata S4 Android release **0.1.8** was used as the primary historical binary base from which development of Bachata S4+ began.

The source archive associated with the historical release available during Bachata S4+ development did not contain the complete application/emulator source corresponding to the APK.

Bachata S4+ therefore does not claim that it was created by simply compiling or forking a complete Bachata S4 0.1.8 source tree.

Bachata S4+ is an independent community modification and is not an official Bachata S4 release.

Copyright remains with the respective Bachata S4 authors and contributors.

---

## shadPS4

Project: `shadps4-emu/shadPS4`

Role:

PlayStation 4 emulator technology forming a major part of the upstream technical lineage behind Bachata S4 and related projects.

Bachata S4+ does not claim authorship or ownership of shadPS4.

Any shadPS4 code or components remain subject to their respective upstream copyright and licensing terms.

Copyright belongs to the shadPS4 developers and contributors.

---

## FEX-Emu

Project: `FEX-Emu/FEX`

Role:

x86/x86-64 userspace emulation technology for ARM64 systems.

FEX is used as an execution backend in the Android emulation environment used by Bachata S4+.

Bachata S4+ includes independent configuration, integration, preset and compatibility work around the FEX execution environment.

FEX itself remains subject to its upstream licensing and copyright terms.

Copyright belongs to the FEX-Emu developers and contributors.

---

## Box64

Project: `ptitSeb/box64`

Role:

x86-64 userspace emulation technology targeting ARM64 and other architectures.

Bachata S4+ includes experimental development and integration work intended to provide Box64 as an alternative execution backend.

Box64 itself remains subject to its upstream license and copyright terms.

Copyright belongs to ptitSeb and the Box64 contributors.

---

## onRps4-Android

Project: `dev-Ali2008/onRps4-Android`

Role in Bachata S4+:

onRps4-Android was used as an architectural and behavioral reference while researching and implementing Box64 integration in an Android PS4 emulation environment.

The public onRps4-Android repository examined during development did not provide the complete emulator source code corresponding to its application.

Bachata S4+ therefore does not claim that the closed-source emulator implementation of onRps4-Android was available or incorporated into this repository.

Reference to onRps4-Android acknowledges its influence on the investigation, architecture and design direction of the Box64 integration.

Copyright and ownership of onRps4-Android remain with its respective author or authors.

---

## Mesa / Turnip

Mesa and related graphics components may be used with Bachata S4+ as part of the Android Vulkan graphics environment.

Turnip is part of the Mesa open-source graphics ecosystem and is commonly used as a Vulkan driver on supported Qualcomm Adreno hardware.

Mesa, Turnip and related components remain independent third-party software and retain their respective upstream licenses and copyrights.

Bachata S4+ does not claim authorship or ownership of these components.

---

## Android Open Source Project

Bachata S4+ runs on Android and may use components, APIs or libraries originating from the Android Open Source Project.

Android and AOSP components remain subject to their respective upstream copyright and licensing terms.

Bachata S4+ does not claim authorship or ownership of Android or AOSP components.

---

## GNU and Runtime Components

Depending on the release and runtime configuration, Bachata S4+ may interact with or redistribute components from GNU and other runtime projects.

These may include components such as:

- glibc
- runtime libraries
- standard C/C++ libraries
- loader components
- supporting system libraries

Each component remains subject to its own respective license.

Inclusion in a Bachata S4+ distribution does not change or replace the license of those components.

---

## Other Third-Party Components

Bachata S4+ may include, interact with or redistribute additional third-party open-source components depending on the release.

These may include:

- compression libraries
- multimedia libraries
- Vulkan-related libraries
- graphics libraries
- emulator dependencies
- Android libraries
- runtime dependencies
- debugging and diagnostic components

Third-party components retain their original licenses, copyrights and notices.

The Bachata S4+ project license does not relicense third-party software.

---

## Bachata S4+ Original Modifications

Original work developed specifically for Bachata S4+ may include:

- Android integration modifications
- application UI changes
- runtime selection logic
- FEX configuration and presets
- Box64 integration work
- per-game configuration
- controller handling improvements
- physical controller support
- Android TV and remote-control navigation
- touch-control modifications
- synthetic motion-control implementations
- memory compatibility changes
- GPU compatibility experiments
- synchronization experiments
- Vulkan-related compatibility work
- diagnostic instrumentation
- diagnostic export functionality
- game-specific compatibility fixes
- runtime configuration improvements
- independently developed patches and modifications

Unless otherwise stated, original Bachata S4+ project code published in this repository is made available under:

**GNU General Public License v2.0 or later (`GPL-2.0-or-later`).**

This license declaration applies only to material for which the Bachata S4+ project has the right to specify licensing.

It does not change or replace the licenses of third-party components.

---

## Binary-Derived Development

Some Bachata S4+ development has been performed using publicly distributed application binaries where complete source code was not available.

Such work may include:

- compatibility analysis
- debugging
- interoperability research
- behavioral comparison
- binary inspection
- independent implementation
- patch development

Availability of a binary application does not imply availability of its source code.

Bachata S4+ does not claim ownership of third-party binary code.

Where upstream source code is actually incorporated, its respective license and copyright requirements must be preserved.

---

## No Claim of Upstream Authorship

The Bachata S4+ project does not claim authorship or ownership of:

- Bachata S4
- shadPS4
- FEX-Emu
- Box64
- onRps4-Android
- Mesa
- Turnip
- Android
- GNU components
- or any other third-party project

References to these projects are provided to document:

- technical lineage
- dependencies
- development references
- research influences
- attribution
- licensing information

---

## Project Independence

Bachata S4+ is an independent community project.

It is not an official release, continuation or distribution of:

- Bachata S4
- shadPS4
- FEX-Emu
- Box64
- onRps4-Android
- Mesa

unless explicitly stated by the respective upstream project.

No endorsement or official affiliation is implied.

---

## Sony / PlayStation Trademark Notice

Sony Interactive Entertainment, PlayStation, PS4 and related names, trademarks, logos and product names belong to their respective owners.

Bachata S4+ is not affiliated with, authorized by, sponsored by or endorsed by Sony Interactive Entertainment.

The project does not claim ownership of any Sony Interactive Entertainment intellectual property.

---

## Games and Copyrighted Content

Bachata S4+ does not provide or distribute:

- PlayStation 4 games
- pirated games
- copyrighted game data
- console firmware
- decryption keys
- licenses
- copyrighted PlayStation system files

Users are responsible for obtaining and using software and content legally.

---

## Licensing

Unless otherwise stated, original Bachata S4+ code published in this repository is licensed under:

**GNU General Public License v2.0 or later**

SPDX identifier:

`GPL-2.0-or-later`

Third-party components remain under their respective licenses.

See the `LICENSE` file in this repository for the primary Bachata S4+ license.

---

## Updates to This Notice

This document should be updated whenever:

- a new third-party component is introduced;
- an upstream project is incorporated;
- new source code is imported;
- a license changes;
- additional project origins are identified;
- attribution information becomes more complete.

The goal of this document is to keep Bachata S4+ development transparent about its technical origins and dependencies.
