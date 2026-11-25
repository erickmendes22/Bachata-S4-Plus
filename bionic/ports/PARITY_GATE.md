# Complete port parity: release gate

Rejected baseline: Bachata Order 5f89cdc and SotC 81aa7c1 (E0C554DB/BDE1197C diagnostics).
Do not keep cherry-picking isolated fixes into these diverged generic renderers.

Use the entire pinned donor runtimes (Order 0.1.37 and SotC 0.2.0 NGS2; GPU inherited from 0.1.69), not just their shaders. Native dependency closure, original caches, shader compiler, guest preparation, AHB presenter and audio/input must remain intact. SotC retains strict AOT without generic FEX. The exact donor APK and every ELF/member hash are recorded by the importer.

The importer validates the original inputs and stages executable aliases for Android target-37 restrictions. It intentionally produces no installable APK. Neither original standalone application is a substitute for integration. Android classes and resources, activity processes, game path/SAF, installed-library execution, settings, saves, and lifecycle must be adapted without altering the donor core behavior. Three different C++ runtimes must stay isolated.

A final unified APK requires the original Bachata signer, explicit per-title launch routing, unchanged donor core hashes and comparable device gameplay validation. Do not label any package equivalent before this gate is met. Other games retain the original generic runtime. See AGENTS.md.
