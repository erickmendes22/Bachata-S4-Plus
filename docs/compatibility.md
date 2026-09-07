# Bachata S4+ Compatibility List

This page tracks game compatibility with **Bachata S4+**.

Compatibility results may vary depending on:

- Bachata S4+ version
- game version/update
- device
- SoC
- GPU
- Android version
- Vulkan driver
- execution backend
- emulator settings
- available RAM
- thermal conditions

A game reaching gameplay does **not** necessarily mean that it is fully playable from beginning to end.

---


> [!NOTE]
> The compatibility database is currently being populated. 
> More test results will be added progressively.

# Status Legend

| Status | Meaning |
|---|---|
| 🟢 Playable | Reaches gameplay and can be played with no major blocking issue observed |
| 🟢 Gameplay | Reaches gameplay, but full playability has not been confirmed |
| 🟡 In-Game / Issues | Reaches gameplay but has significant graphical, performance, input or stability issues |
| 🟡 Boots | Boots and reaches menus or intro, but does not reach normal gameplay |
| 🟠 Rendering Issues | Runs, but graphics are significantly broken |
| 🟠 Input Issues | Runs, but controls or input prevent normal gameplay |
| 🟠 Infinite Loop | Game/emulator remains running but becomes stuck in an endless loop |
| 🔴 Crash | Crashes before reaching the expected gameplay state |
| 🔴 No Boot | Does not boot successfully |
| ⚪ Untested | Not yet tested on the current Bachata S4+ release |

---

# Backend Legend

| Backend | Meaning |
|---|---|
| FEX | Game tested using the FEX execution backend |
| Box64 | Game tested using the Box64 execution backend |
| Both | Tested successfully or compared on both backends |
| Unknown | Backend was not recorded |

---

# Recommended Compatibility Report Information

When adding a new result, include whenever possible:

- Game name
- Title ID / CUSA
- Region
- Game version
- Bachata S4+ version
- Backend
- Device
- SoC
- Android version
- GPU driver
- Status
- Major issues
- Video link
- Additional notes

---

# Compatibility List

## Playable / Gameplay

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🟢 Gameplay | Reaches gameplay normally | [Watch](VIDEO_URL) |

---

## In-Game With Issues

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🟡 In-Game / Issues | Graphical issues during gameplay | [Watch](VIDEO_URL) |

---

## Boots / No Gameplay

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🟡 Boots | Reaches main menu but crashes when starting gameplay | — |

---

## Rendering Issues

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🟠 Rendering Issues | Geometry or textures render incorrectly | [Watch](VIDEO_URL) |

---

## Input / Controller Issues

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🟠 Input Issues | Game runs but required input is unavailable | — |

---

## Infinite Loop / Softlock

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🟠 Infinite Loop | Gets stuck at loading transition | — |

---

## Crash

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🔴 Crash | Crashes before gameplay | — |

---

## No Boot

| Game | Title ID | Game Version | Bachata S4+ | Backend | Device / SoC | Driver | Status | Notes | Video |
|---|---|---:|---:|---|---|---|---|---|---|
| Example Game | CUSA00000 | 1.00 | 0.1 | FEX | Snapdragon 8 Elite | Turnip | 🔴 No Boot | Emulator exits immediately | — |

---

## Untested

| Game | Title ID | Last Known State | Notes |
|---|---|---|---|
| Example Game | CUSA00000 | ⚪ Untested | Needs testing on current release |

---

# Detailed Game Notes

Use this section when a game needs more information than fits in the main table.

---

## Game Name

**Title ID:** `CUSA00000`  
**Region:** USA / EUR / JPN  
**Game Version:** `1.00`  
**Bachata S4+ Version:** `0.1`  
**Backend:** `FEX`  
**Device:** `Device Name`  
**SoC:** `Snapdragon ...`  
**Android:** `Android ...`  
**GPU Driver:** `Driver name/version`

### Status

🟢 Gameplay

### What Works

- Boot
- Menus
- Gameplay
- Audio
- Controller

### Known Issues

- Example graphical issue
- Example performance issue
- Example crash condition

### Required Settings

- Setting 1
- Setting 2

### Video

[Watch test video](VIDEO_URL)

### Additional Notes

Add any game-specific information here.

---

# Testing Notes

Compatibility results should preferably be reproduced more than once before being considered stable.

When testing a regression, compare:

1. Last known working Bachata S4+ build
2. First known broken build
3. Same game version
4. Same backend
5. Same driver
6. Same emulator configuration

This helps determine whether a problem is caused by:

- emulator changes
- backend changes
- graphics driver changes
- game updates
- configuration changes
- device-specific behavior

---

# Video Evidence

When available, compatibility entries can include links to real-device gameplay tests.

Official Bachata S4+ game testing videos are published through:

**Daedalus Emulator**

YouTube: `YOUR_YOUTUBE_CHANNEL_URL`

Videos are useful for documenting:

- actual gameplay state
- graphical issues
- performance
- regressions
- fixes
- FEX vs Box64 differences
- driver differences

---

# Contributing Compatibility Results

If you submit a compatibility report, please provide as much information as possible.

Recommended format:

**Game:**  
**Title ID:**  
**Game Version:**  
**Bachata S4+ Version:**  
**Backend:**  
**Device:**  
**SoC:**  
**Android Version:**  
**GPU Driver:**  
**Status:**  
**Issue:**  
**Settings:**  
**Video:**  
**Logs:**  

Incomplete reports may still be useful, but detailed reports are much easier to reproduce and investigate.

---

# Important

Compatibility changes frequently.

A result listed here applies only to the tested configuration and should not be interpreted as a guarantee that the game will behave identically on every device.

Bachata S4+ is experimental software.
