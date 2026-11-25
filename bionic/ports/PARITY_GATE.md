# Functional parity — FEX remains mandatory

User correction: do not import the donor runtimes or AOT, and do not replace Bachata's cores with the donor cores. The old binary import approach is removed from the active branch.

Reference Order Android: 756a4f0cc603b02971d45b36354143249a4fe492, PC c53cd01d032995fe622033623ab64b4cf6b02233. Reference SotC GPU in 0.2.0: 0366868550bde078d9ed9d88bc72d8acb1584679, PC 732cb37d3470d2dad2cc99da19283253c96b53fc. Compare actual staged source (including Android overlays and AHB wiring) against actual 0.18.1 FEX source after all Bachata overlays. CPU FEX/JIT and HLE guest ABI, frontend, SAF and packaging remain Bachata. GPU translation, descriptor identity, cache persistence, render passes, texture/metadata ownership, readbacks, PM4 scheduling, Android frame transport, and real FPS are the functional parity scope.

Source differences are leads, not proof of behavioral differences. Classify necessary API/CPU differences and adapt remaining differences by coherent subsystem. The comparison artifact is not an APK, nor is it evidence that any regression is fixed. Require signed dual-core APK and matched gameplay before claiming complete equivalence.
