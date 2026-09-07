# Bachata S4+

<p align="center">
  <b>Experimental PlayStation 4 emulation project for ARM64 Android devices.</b>
</p>

<p align="center">
  Community modification based on Bachata S4, focused on compatibility,
  ARM64 execution, controller support, FEX/Box64 experimentation and
  game-specific improvements.
</p>

---

> [!IMPORTANT]
> **Bachata S4+ is an independent community project.**
>
> It is not an official Bachata S4 release and is not maintained,
> endorsed or supported by the original Bachata S4 developers.

## 📱 About Bachata S4+

**Bachata S4+** is an experimental PlayStation 4 emulation project focused
on ARM64 Android devices.

The project started from the Android binary releases of **Bachata S4** and
has since received independent modifications, compatibility research,
runtime experimentation, controller improvements, Android UI changes and
game-specific fixes.

The historical Bachata S4 build used as the main starting point for this
project was **Bachata S4 0.1.8**.

The public source archive associated with that historical release did not
contain the complete application/emulator source corresponding to the APK.

Because of this, Bachata S4+ should be understood as an independent
community modification and compatibility research project rather than a
traditional source-code fork of Bachata S4 0.1.8.

---

## 📺 Official Bachata S4+ Game Testing Channel

Real-device game tests, compatibility demonstrations and development
progress are published on the official Bachata S4+ testing channel:

### Daedalus Emulator

▶️ **YouTube:** https://youtube.com/@daedalusemulator

The channel may include:

- real ARM64 Android gameplay
- Bachata S4+ compatibility tests
- performance demonstrations
- FPS tests
- FEX testing
- Box64 testing
- new compatibility fixes
- before/after comparisons
- regression tests
- experimental build demonstrations
- others emulators gameplay 

Videos can also be linked directly from the compatibility database so users
can visually verify the state of tested games.

---

## 🚀 Current Release

### Bachata S4+ v0.1

The first public Bachata S4+ release.

This release establishes the initial public base of the project for future
compatibility development and testing.

### Main goals

- ARM64 Android PS4 emulation
- FEX execution backend
- Box64 execution backend experimentation
- Per-game configuration
- Physical controller support
- Touch controls
- Controller-first UX improvements
- Vulkan compatibility work
- GPU synchronization research
- Memory compatibility improvements
- Game-specific fixes
- Diagnostic and debugging tools
- Compatibility testing on real Android hardware

➡️ See the **Releases** section of this repository to download published builds.

---

## ⚙️ Execution Backends

### FEX

FEX is used as an x86/x86-64 userspace execution layer on ARM64 devices.

Bachata S4+ includes additional work around FEX configuration, runtime
behavior and per-game compatibility.

Development may include different FEX presets intended for performance,
compatibility or debugging.


### Box64

Bachata S4+ also contains experimental work for using **Box64** as an
alternative x86-64 execution backend.

The Box64 implementation is still considered experimental and may behave
differently depending on the game and device.

The **onRps4-Android** project was used as an architectural and behavioral
reference while investigating Box64 integration on Android.

Bachata S4+ does **not** claim that the closed emulator source code of
onRps4-Android was available or incorporated into this repository.

---

## 🎮 Game Compatibility

PlayStation 4 emulation on Android is still highly experimental.

Games may:

- run normally
- reach gameplay with graphical or performance problems
- boot but fail before gameplay
- freeze
- crash
- render incorrectly
- have broken audio
- have controller/input problems
- require specific drivers or settings
- behave differently between FEX and Box64

A game reaching gameplay does **not** necessarily mean that it is fully
playable from beginning to end.

Compatibility can also change between releases.

A dedicated compatibility database will be maintained in:

`docs/compatibility.md`

---

## 🧪 Experimental Development

Bachata S4+ development frequently involves testing changes that affect
low-level emulator behavior.

Current and future research areas may include:

### CPU / Runtime

- FEX configuration
- Box64 integration
- x86-64 → ARM64 execution
- runtime selection
- per-game CPU configuration
- synchronization behavior

### GPU

- Vulkan compatibility
- GPU synchronization
- command submission
- buffer handling
- shader compatibility
- memory behavior
- driver-specific workarounds

### Android

- application lifecycle
- ARM64 runtime integration
- controller handling
- Android TV / remote navigation
- touch controls
- per-game settings
- driver management
- runtime extraction
- diagnostic export

### Game-specific compatibility

Some games require specific workarounds that are not appropriate to enable
globally.

Whenever possible, Bachata S4+ attempts to isolate these changes so that a
fix for one title does not cause regressions in unrelated games.

---

## 🧩 Compatibility Philosophy

A compatibility fix should ideally satisfy three requirements:

**1. Fix the target problem**

The change should produce a measurable improvement in the affected game or
subsystem.

**2. Avoid global regressions**

A fix should not break games that were already working.

**3. Be reproducible**

Changes should eventually be documented so their behavior can be reproduced,
reviewed and compared between builds.

Experimental fixes may be removed or reverted if they introduce regressions.

---

## 📊 Test Environment

Bachata S4+ is primarily developed and tested on modern ARM64 Android
hardware.

Results can vary significantly depending on:

- SoC
- GPU
- RAM
- Android version
- graphics driver
- Vulkan driver
- device manufacturer
- thermal limits
- game update/version
- emulator configuration
- selected execution backend

Compatibility reports should always include as much of this information as
possible.

---

## 🐛 Reporting Compatibility Problems

Before reporting a problem, please check whether it already exists in the
compatibility database or Issues section.

Useful reports should include:

- game name
- Title ID / CUSA
- game version
- Bachata S4+ version
- Android device
- SoC
- Android version
- GPU driver
- FEX or Box64
- relevant emulator settings
- exact point where the problem occurs
- logs or diagnostic package when available

Reports such as only **"game doesn't work"** are usually not enough to
investigate a problem.

---

## 🧰 Diagnostics

Bachata S4+ development relies heavily on diagnostic information.

When investigating crashes, freezes, rendering problems or game-specific
regressions, diagnostic packages may be requested.

Logs are especially useful when comparing:

- working vs broken builds
- FEX vs Box64
- different graphics drivers
- different game versions
- different emulator settings

---

## 🔬 Project Origin and Technical Lineage

Bachata S4+ exists thanks to work from several independent projects.

A simplified relationship is:

    shadPS4
       │
       └── PlayStation 4 emulation technology
              │
              ├── ARM64 / mobile-related development
              │
              └── Bachata S4
                     │
                     └── Bachata S4+
                          independent community modifications

    FEX-Emu
       │
       └── x86/x86-64 execution on ARM64
              │
              └── Bachata S4+

    Box64
       │
       └── x86-64 execution on ARM64
              │
              └── Bachata S4+

    onRps4-Android
       │
       └── architectural / behavioral reference
           for Android Box64 integration

This diagram represents technical lineage and references only.

It does not imply ownership, endorsement or official affiliation between
these projects.

---

## 🙏 Credits

Bachata S4+ would not exist without the work of many emulator and open-source
developers.

Special thanks to:

### Bachata S4 / JICA98

Primary historical Android binary base and one of the main projects from
which Bachata S4+ development originated.

### shadPS4

PlayStation 4 emulator project and the core upstream technology behind much
of the emulation work used by projects in this ecosystem.

Thanks to all shadPS4 developers and contributors.

### FEX-Emu

Provides x86/x86-64 userspace emulation technology for ARM64 systems.

Thanks to all FEX developers and contributors.

### Box64

Provides x86-64 userspace emulation technology for ARM64 and other
architectures.

Thanks to ptitSeb and all Box64 contributors.

### onRps4-Android / dev-Ali2008

Used as an architectural and behavioral reference during research into
Android Box64 integration and fexcore presets inspiration.

The public onRps4-Android repository examined during development did not
provide the complete emulator source corresponding to its application.

### Mesa / Turnip

Thanks to Mesa and Turnip developers and contributors for their work on the
open-source graphics stack and Vulkan drivers used throughout the Android
emulation ecosystem.

### Community testers

Thanks to everyone who tests games, reports regressions, provides diagnostic
logs and helps verify compatibility improvements.

See [`NOTICE.md`](NOTICE.md) for additional attribution and licensing
information.

---

## 📜 License

Original Bachata S4+ project code published through this repository is
distributed under the:

**GNU General Public License v2.0 or later — GPL-2.0-or-later**

except where explicitly stated otherwise.

Third-party components remain under their respective licenses and copyright
terms.

See:

- [`LICENSE`](LICENSE)
- [`NOTICE.md`](NOTICE.md)

for additional information.

The Bachata S4+ license declaration does not relicense third-party software.

---

## ⚖️ Legal Notice

Bachata S4+ does **not** provide or distribute:

- PlayStation 4 games
- pirated games
- copyrighted game data
- console firmware
- copyrighted PlayStation system files
- decryption keys
- licenses
- copyrighted content belonging to third parties

Users are responsible for obtaining and using games, firmware and other
content legally.

Bachata S4+ is intended for emulator development, interoperability,
compatibility research and legitimate use with legally obtained software.

---

## 🔎 Reverse Engineering and Compatibility Research

Some Bachata S4+ development may involve analysis of publicly distributed
application binaries for purposes including interoperability, debugging,
compatibility research and independent implementation.

Availability of an application binary does not imply availability of its
source code.

Where source code from another open-source project is actually incorporated,
its copyright notices and applicable license requirements must be preserved.

Bachata S4+ does not claim authorship of third-party components.

---

## ™️ Trademark Disclaimer

Bachata S4+ is not affiliated with Sony Interactive Entertainment.

**PlayStation**, **PS4** and related trademarks, product names and logos are
the property of their respective owners.

Bachata S4+ is also not an official release of Bachata S4, shadPS4,
FEX-Emu, Box64 or onRps4-Android.

All third-party project names are used only for identification, attribution
and technical documentation.

---

## 🗺️ Project Roadmap

Development priorities currently include:

- improve compatibility without breaking already working games
- continue FEX optimization
- improve Box64 compatibility
- improve physical controller support
- improve virtual controller support
- improve FPS HUD
- add FG
- improve per-game configuration
- identify and isolate game-specific fixes
- improve diagnostic tools
- document compatibility changes
- create a public compatibility database
- make development changes increasingly reproducible and traceable
- document upstream components and their licenses more completely

The roadmap may change as emulator development progresses.

---

## 📦 Releases

Public builds are distributed through the GitHub **Releases** section.

Each release should include:

- version number
- APK
- release notes
- major fixes
- known regressions
- compatibility changes
- relevant testing notes

Experimental development builds may behave differently from stable public
releases.

---

## ⭐ Supporting the Project

The most useful ways to help Bachata S4+ are:

- test games
- report regressions
- provide detailed logs
- compare different builds
- document working configurations
- verify fixes on different devices
- contribute technical research
- improve documentation

If the project is useful to you, you can also star the repository to make it
easier for other users to find.

---

<p align="center">
  <b>Bachata S4+</b><br>
  Experimental PlayStation 4 emulation research for ARM64 Android.
</p>
