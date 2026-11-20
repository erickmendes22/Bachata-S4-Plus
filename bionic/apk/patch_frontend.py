#!/usr/bin/env python3
"""Fix v0.2.7 NativeRuntimeBridge SDL JNI initialization using source-controlled smali.

Run in GitHub Actions after Apktool disassembles the pristine release.
Only the exact NativeRuntimeBridge class changes; all other frontend DEX is
preserved by extracting the rebuilt classes8.dex into the final APK assembler.
"""
from __future__ import annotations

import argparse
from pathlib import Path

CLASS = Path(
    "smali_classes8/com/bachatas4/android/runtime/process/NativeRuntimeBridge.smali"
)
OLD = """    const-string v0, "bachata_native_runtime"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    .line 14
    invoke-static {}, Lorg/libsdl/app/SDL;->setupJNI()V"""
NEW = """    const-string v0, "bachata_native_runtime"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    # Loading the large Bionic core in <clinit> is premature: the Java
    # service has not provided its working directory or driver environment.
    # The JNI adapter loads the core via loadCoreAndSetupJNI() after setup.
    .line 14"""
CORE_HELPER = """
.method public static final loadCoreAndSetupJNI()V
    .locals 1

    const-string v0, "bachata_bionic_core"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    invoke-static {}, Lorg/libsdl/app/SDL;->setupJNI()V

    return-void
.end method
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("decoded", type=Path)
    args = ap.parse_args()
    file = args.decoded / CLASS
    if not file.exists():
        raise SystemExit(f"Expected original 0.2.7 class missing: {file}")
    body = file.read_text(encoding="utf-8")
    if body.count(OLD) != 1:
        raise SystemExit("Refusing wrong dex: NativeRuntimeBridge.<clinit> anchor mismatch")
    body = body.replace(OLD, NEW, 1)
    if "loadCoreAndSetupJNI()V" in body:
        raise SystemExit("Core boot helper already present: refuse double patch")
    body += CORE_HELPER
    file.write_text(body, encoding="utf-8")
    print("BIONIC_FRONTEND_DEFERRED_CORE_LOAD_READY: adapter first; core and SDL initialized after service setup")


if __name__ == "__main__":
    main()
