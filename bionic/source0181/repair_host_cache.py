#!/usr/bin/env python3
"""Audit restored host objects and archives before Ninja trusts timestamps.
Run 45404408523: nm reported string_field.cc.o and helpers.cc.o as
unrecognised, but returned success for the archive. Link then failed.
Do not identify objects by basename: protobuf has several helpers.cc files.
"""
import argparse
import pathlib
import subprocess
import tempfile

def bad_binary(path):
    try:
        if not path.stat().st_size:
            return "empty file"
        with path.open("rb") as f:
            header = f.read(20)
        if path.suffix == ".o":
            if header[:4] != b"\x7fELF" or len(header) < 20:
                return "not ELF"
            if header[4:6] != b"\x02\x01" or header[18:20] != b"\x3e\x00":
                return "not x86-64 host ELF"
            check = subprocess.run(["readelf", "-SW", str(path)], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE, text=True)
            if check.returncode or check.stderr.strip():
                return check.stderr.strip() or "invalid ELF sections"
        elif header[:8] not in (b"!<arch>\n", b"!<thin>\n"):
            return "not ar archive"
        check = subprocess.run(["nm", "-P", "--defined-only", str(path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        errors = [s for s in check.stderr.splitlines() if not s.endswith(": no symbols")]
        if check.returncode or errors:
            return "; ".join(errors) or "nm failed"
        return None
    except OSError as e:
        return str(e)

def repair(roots):
    broken = count = 0
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in (".o", ".a"):
                continue
            count += 1
            reason = bad_binary(path)
            if reason:
                print(f"BIONIC_HOST_CACHE_CORRUPT {path}: {reason}", flush=True)
                path.unlink()
                broken += 1
    print(f"BIONIC_HOST_CACHE_AUDIT checked={count} removed={broken}", flush=True)
    return broken

def selftest():
    with tempfile.TemporaryDirectory() as t:
        root = pathlib.Path(t)
        good = root / "good.o"
        bad = root / "bad.o"
        archive = root / "libbad.a"
        subprocess.run(["cc", "-x", "c", "-c", "-o", str(good), "-"],
                       input=b"int answer(void){return 42;}", check=True)
        bad.write_bytes(b"truncated")
        subprocess.run(["ar", "rcs", str(archive), str(good), str(bad)], check=True)
        assert repair([root]) == 2
        assert good.is_file() and not bad.exists() and not archive.exists()
        print("BIONIC_HOST_CACHE_CORRUPTION_SELFTEST_PASS")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("roots", nargs="*", type=pathlib.Path)
    a = p.parse_args()
    if a.selftest:
        selftest()
    else:
        print(f"BIONIC_HOST_CACHE_REMOVED={repair(a.roots)}")
