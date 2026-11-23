#!/usr/bin/env python3
"""FEX/PS4 libc NID and import coverage audit, without a runtime false-pass."""
from __future__ import annotations
import argparse
import hashlib
import re
from pathlib import Path

SALT = bytes.fromhex("518d64a635ded8c1e6b039b1c3e55230")
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
OBSERVED = """
__cxa_pure_virtual _ZNSt8ios_base4InitD1Ev _ZNSt6_WinitD1Ev catchReturnFromMain exit
sprintf setjmp tan qsort longjmp pow time gmtime_s mktime difftime fmod atan2 _Sin
acos atan _Getpctype asin cos exp log sin fopen fprintf fwrite fclose vsprintf
_Getptolower localeconv strtoumax _Stod _Stoul powf strcspn strcoll putchar
printf frexpf ldexpf modff rand srand strchr fgetc strerror fgetpos fseek
feof fread _Getptoupper strrchr atanf _FCosh expf fmodf _FLog _FSinh tanhf
_Log snprintf fputs strlcpy localtime asctime fflush strncpy getchar
sceKernelChmod sceKernelUtimes ferror clearerr ftell strncat
_ZSt13_Syserror_mapi _ZNSs6assignEPKcm _Assert exp2f puts
sceKernelReleaseFlexibleMemory _Exit sceKernelFutimes strnlen strncmp
""".split()
CRITICAL = """
malloc free realloc calloc vsnprintf puts printf sprintf snprintf
fopen fclose fread fwrite fseek fflush fprintf fgetc fputs qsort _Log
""".split()
def nid(name: str) -> str:
    digest = int.from_bytes(hashlib.sha1(name.encode("utf-8") + SALT).digest()[:8], "little")
    return "".join(ALPHABET[(digest >> (58 - i * 6)) & 63] for i in range(10)) + ALPHABET[(digest & 15) * 4]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def registered(overlay: Path, upstream: Path | None) -> tuple[set[str], list[str]]:
    boot = read(overlay / "android_libc_boot.cpp")
    compat = read(overlay / "android_libc_compat.cpp")
    found = set(re.findall(r'LIB_FUNCTION\("([^"]+)", "libc",', boot))
    errors: list[str] = []
    for imported, function in re.findall(r'ALIAS\("([^"]+)",\s*(\w+)\)', compat):
        found.add(imported)
        if function.startswith("Fex_"):
            name = function[4:]
        elif function.startswith("Guest"):
            name = function[5:6].lower() + function[6:]
        else:
            errors.append(f"unknown registration: {function}")
            continue
        if imported != nid(name):
            errors.append(f"NID mismatch for {function}: declared={imported}, expected={nid(name)} ({name})")
    for imported, kind in re.findall(
        r'AddPrintfAlias\(sym,\s*"([^"]+)",\s*PrintKind::(\w+)\)', compat
    ):
        found.add(imported)
        if imported != nid(kind.lower()):
            errors.append(f"NID mismatch for printf adapter {kind}: {imported} vs {nid(kind.lower())}")
    if upstream is not None:
        for file in (upstream / "src/core/libraries/libc_internal").glob("*.cpp"):
            found.update(re.findall(r'LIB_FUNCTION\("([^"]+)", "libc",', read(file)))
    return found, errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay", type=Path, default=Path("bionic/generic"))
    parser.add_argument("--upstream", type=Path)
    args = parser.parse_args()
    assert len(OBSERVED) == len(set(OBSERVED)) == 87
    assert nid("puts") == "YQ0navp+YIc"
    assert nid("malloc") == "gQX+4GDQjpM"
    found, errors = registered(args.overlay, args.upstream)
    covered = sorted(name for name in OBSERVED if nid(name) in found)
    missing = sorted(set(OBSERVED) - set(covered))
    critical_missing = [name for name in CRITICAL if nid(name) not in found]
    print(f"Observed 065B4073 unresolved import names: {len(OBSERVED)}")
    print(f"Implemented as explicit FEX libc HLE aliases: {len(covered)}/{len(OBSERVED)}")
    print("Uncovered imported functions (not claimed fixed):")
    for name in missing:
        print(f"  {name:<40} {nid(name)}")
    print(f"Critical ABI aliases missing: {critical_missing}")
    for error in errors:
        print("ERROR:", error)
    return 1 if errors or critical_missing else 0

if __name__ == "__main__":
    raise SystemExit(main())
