#!/usr/bin/env python3
"""Report *all* failed NDK translation units and unique root compiler errors.

Do not assume the first error is the only failure. Ninja -k 0 attempts every
independent source and this condenses the results for the next patch round.
"""
from __future__ import annotations
import re
import sys
from collections import Counter
from pathlib import Path

def main(source: Path, destination: Path) -> None:
    raw = source.read_text(errors="replace")
    lines = [re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", line)
             for line in raw.splitlines()]
    failures = []
    errors = []
    for line in lines:
        if "FAILED: " in line and ("CMakeFiles/" in line or "libbachata_bionic_core" in line):
            failures.append(line[:320])
        if (re.search(r"(^|\s)(fatal error:|error:|undefined reference to|ld\.lld: error:)", line)
                and "command" not in line[:65]):
            clean = re.sub(r"^.*?(?=(?:\.\./|/).+?:\d+:)", "", line)
            errors.append(clean[:450])
    counts = Counter(errors)
    out = [
        "BACHATA_NDK_ALL_ERRORS_REPORT",
        f"compiled_units_failed={len(failures)}",
        f"error_instances={len(errors)}",
        f"distinct_error_messages={len(counts)}",
        "",
        "FAILED_TRANSLATION_UNITS:",
        *failures[:250],
        "",
        "COMPILER_ERRORS (all distinct messages, count prefixed):",
        *(f"[{count}] {message}" for message,count in counts.most_common(500)),
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(out) + "\n")
    print("\n".join(out[:300]))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: extract_native_errors.py <ninja.log> <summary.txt>")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
