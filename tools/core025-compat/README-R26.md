# R26: diagnostic runtime collision, native RB and Spider-Man catalog

Diagnostic BS4-20261013-7BDFB44A claims runtime `bachata-s4-r025-0.2.6-r`
but loads `libbachata_fsr31.so` and reports dispatcher SHA
`19f4e03f08c4fb10b0dd5d6b5e2b0838a53700942636fd932bb7ea6966a32634`.
Those bytes match `CORE025-FSR31-PORT-R25-P36.apk` exactly. The pre-FSR R25
has dispatcher SHA `5c162129531b9446557c25c6a06ff5fe2a85f489c8d35d6faa5b929234735882`
and no FSR3 payload. Both APKs used the same runtime identity, allowing the
existing installed runtime to be reused. R26 uses the distinct identity
`bachata-s4-n026-0.2.6-r`, preserving length and the extraction suffix.

The fatal event is `RefreshGraphicsStages: unhandled stage_en: 325`.
An ARM64 negative control using the diagnostic's exact core rejects 325;
the pre-FSR core's existing normalization accepts it as 0x45 and enters
the native LS/HS path. No further stage patch is needed. The new test follows
the original native switch, rather than stopping immediately after the hook.
It retains rejection for unknown stage encodings.

## RB

Clean 025 contained a disconnected copied wrapper at 0x3e82e00 whose call
resolved to 0x24a4b0 and whose return resolved to 0xde3988; both are stale
destinations. It used old 024 component offsets 0x28c/0x294 and old member
offset 0x3ff0. R26 removes that unused wrapper and attaches to actual 025
Presenter::PrepareFrame at 0x12933e0. The native 025 uses offsets
0x294/0x29c, member 0x4948, and getenv PLT 0x6cb060.

The wrapper preserves caller GP, all SIMD registers and NZCV across getenv.
Disabled, empty, zero and false settings retain native mapping. Enabled
settings apply the existing Android R/B override after native format handling.
It does not touch alpha or another render target. inFAMOUS and game fixes remain.

## Patches

The supplied SELF SHA d9736579d38c3862e208e6c3fc5f9a9a6d946e024ecd226235ea9c773b20a70b
matches all 16 known patch sites, including original RIP operands and INT3
code cave. Addresses do not need relocation. The new catalog supports
the requested CUSA02999 and the diagnostic's CUSA02299 for this executable.
Both runtime catalog copies include the new XML and files.json entry.
Seven options are present: 720p, 900p, sun shadows off, SSAO off, vehicles
50%, pedestrians 50% and 60 FPS. Expected bytes are included, options default
disabled, and frame-timing references 1/30 and adjacent 1/60 are checked.
The original CUSA11993 catalog and all other game catalogs remain unchanged.

## Verification and limits

216 existing native ARM64 compatibility cases and 42 stage/RB cases pass at
zero and Android-like PIE biases. getenv is modeled with deliberate caller
register clobber to test ABI preservation. Native constant interning remains
modeled as documented by the R25 test. Catalog bytes are verified directly
against the user-supplied EBOOT, without publishing the game binary.
All packaged manifest hashes and preserved DEX/legacy runtime bytes are
checked, and P36 V2/V3 signatures are verified. These checks are local;
device gameplay is not validated in this environment.
