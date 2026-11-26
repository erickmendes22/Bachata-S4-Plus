#!/usr/bin/env python3
"""Hook selection migration into the existing selector and native launch request.

Run after Apktool decodes the exact 0.2.7 frontend. Rebuild both classes4.dex and
classes8.dex; add the separately D8-compiled OrderPatchCatalog helper to the APK.
The selector reuses the existing verified runtime installer in its existing
background worker. The launch hook does not add or clobber any register.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

HELPER = "Lcom/bachatas4/android/patches/OrderPatchCatalog;"
INSTALLER = "Lcom/bachatas4/android/service/GlibcSessionRuntime;"
SELECTOR = Path("smali_classes4/com/bachatas4/android/patches/PatchSelectorActivity.smali")
LAUNCHER = Path("smali_classes8/com/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher.smali")
RUNTIME = Path("smali_classes8/com/bachatas4/android/service/GlibcSessionRuntime.smali")


def method_range(body: str, name: str) -> tuple[int, int, str]:
    # Smali method names are whitespace-delimited tokens. A word boundary also
    # matches Kotlin's access$validateRequest accessor, which coexists with the
    # private validateRequest method in the real 0.2.7 frontend.
    pattern = re.compile(r"(?m)^\.method[^\n]*[ \t]" + re.escape(name) + r"\([^\n]*\n[\s\S]*?^\.end method$")
    matches = list(pattern.finditer(body))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {name} method")
    found = matches[0]
    return found.start(), found.end(), found.group()


def hook_selector(body: str) -> str:
    start, end, method = method_range(body, "activeRuntimeDirectory")
    if HELPER in method:
        raise ValueError("Order catalogue selector hook already applied")
    if len(re.findall(r"(?m)^\s*return-object [vp]\d+\s*$", method)) != 2:
        raise ValueError("Original selector no longer has two runtime-directory returns")
    # The previous implementation returned an older runtime if the current
    # manifest's directory had not been installed yet. Reuse the same complete,
    # verified installer as the session, on loadPatchesAsync's worker thread.
    # No partial directory or catalogue is created by this hook.
    method = f""".method private activeRuntimeDirectory()Ljava/io/File;
    .locals 1

    new-instance v0, {INSTALLER}
    invoke-direct {{v0, p0}}, {INSTALLER}-><init>(Landroid/content/Context;)V
    invoke-virtual {{v0}}, {INSTALLER}->install()Ljava/nio/file/Path;
    move-result-object v0
    invoke-interface {{v0}}, Ljava/nio/file/Path;->toFile()Ljava/io/File;
    move-result-object v0
    invoke-static {{v0}}, {HELPER}->prepare(Ljava/io/File;)V
    return-object v0
.end method"""
    return body[:start] + method + body[end:]


def validate_installer(body: str, selector: str) -> None:
    # Pin the existing API/worker contract before mutating either class. This
    # class is already in the frontend; only install() is invoked, never display
    # startup or the legacy CPU backend.
    if not re.search(r"(?m)^\.method public constructor <init>\(Landroid/content/Context;\)V$", body):
        raise ValueError("Existing runtime installer constructor changed")
    _, _, install = method_range(body, "install")
    if not install.startswith(".method public final install()Ljava/nio/file/Path;"):
        raise ValueError("Existing runtime installer entry point changed")
    for anchor in ("runtime/manifest.json", "runtime/runtime.zip", "RuntimeInstaller;->install-"):
        if anchor not in install:
            raise ValueError("Existing runtime installer no longer verifies the bundled archive")
    _, _, worker = method_range(selector, "loadPatchesAsync")
    if ("PatchSelectorActivity$6;" not in worker or "Ljava/lang/Thread;->start()V" not in worker):
        raise ValueError("Patch loading no longer uses its existing background worker")


def hook_launcher(body: str) -> str:
    start, end, method = method_range(body, "validateRequest")
    if HELPER in method:
        raise ValueError("Order catalogue launch hook already applied")
    # Preserve the path object and every live register, including the zero used
    # by subsequent toRealPath() array construction.
    pattern = re.compile(r"(invoke-virtual[^\n]*RuntimeProcessRequest;->getRuntimeRoot\(\)Ljava/nio/file/Path;"
                         r"\s*\n\s*move-result-object ([vp]\d+))")
    matches = list(pattern.finditer(method))
    if len(matches) != 1:
        raise ValueError("Original launcher runtime-root validation changed")
    method = pattern.sub(lambda match: match[1] + "\n\n    invoke-static {" + match[2] + "}, "
                         + HELPER + "->prepare(Ljava/nio/file/Path;)V", method)
    return body[:start] + method + body[end:]


def apply(decoded: Path) -> None:
    # Validate both anchors before changing either decoded class.
    selector = (decoded / SELECTOR).read_text(encoding="utf-8")
    validate_installer((decoded / RUNTIME).read_text(encoding="utf-8"), selector)
    sources = [(decoded / SELECTOR, hook_selector), (decoded / LAUNCHER, hook_launcher)]
    updates = [(path, hook(path.read_text(encoding="utf-8"))) for path, hook in sources]
    for path, body in updates:
        path.write_text(body, encoding="utf-8")
    print("BACHATA_ORDER102_CATALOG_SELECTOR_AND_LAUNCH_HOOK_READY")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decoded", type=Path)
    apply(parser.parse_args().decoded)
