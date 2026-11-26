#!/usr/bin/env python3
"""Exercise the real pinned-base DEX guard and APK ZIP writer without native builds."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import warnings
import zipfile

import assemble_apk as assembler

ORIGINAL_NAMES = ["classes.dex", *(f"classes{n}.dex" for n in range(2, 16))]
EXTRA_DEX_HASHES = {
    "classes14.dex": "3597f7f0d836f3442404bd4c5b5dbcb901c163b4890c693f5fef42aa46a47d2c",
    "classes15.dex": "6b89aaacaf4fc87a175cc70f04a324553f794ac8725b8fa44fee8b62b53acdbe",
}


def archive(entries: list[tuple[str, bytes]]) -> bytes:
    result = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # Duplicate-name negative fixture.
        with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED) as output:
            for name, data in entries:
                output.writestr(name, data)
    return result.getvalue()


def test(reference_apk: Path | None = None) -> None:
    assert assembler.HELPER_DEX == "classes16.dex"
    if reference_apk is None:
        originals = {name: b"dex\n039\0original:" + name.encode() for name in ORIGINAL_NAMES}
    else:
        with zipfile.ZipFile(reference_apk) as reference:
            build = json.loads(reference.read("assets/bachata-bionic-build.json"))
            assert build["baseSha256"] == assembler.EXPECTED_BASE_SHA256
            assembler.validate_base_dex_layout(reference)
            originals = {name: reference.read(name) for name in ORIGINAL_NAMES}
        for name, expected in EXTRA_DEX_HASHES.items():
            assert hashlib.sha256(originals[name]).hexdigest() == expected, name
    originals["assets/preserved.txt"] = b"unrelated frontend asset"
    changed = {
        "classes4.dex": b"dex\n039\0reviewed selector hook",
        "classes8.dex": b"dex\n039\0reviewed native launcher hook",
        assembler.HELPER_DEX: b"dex\n039\0Lcom/bachatas4/android/patches/OrderPatchCatalog;",
    }
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(archive(list(originals.items())))) as original:
        assembler.validate_base_dex_layout(original)
        with zipfile.ZipFile(output, "w") as result:
            assembler.write_apk_entries(original, result, dict(changed))
    with zipfile.ZipFile(io.BytesIO(output.getvalue())) as result:
        assert result.testzip() is None
        assert len(result.namelist()) == len(set(result.namelist()))
        dex_names = {name for name in result.namelist() if re.fullmatch(r"classes[0-9]*\.dex", name)}
        assert dex_names == set(ORIGINAL_NAMES) | {"classes16.dex"}
        for name, data in originals.items():
            if name in changed:
                assert result.read(name) != data, name
            else:
                assert result.read(name) == data, name
        for name, data in changed.items():
            assert result.read(name) == data, name
    negative_layouts = {
        "old_thirteen_dex_assumption": ORIGINAL_NAMES[:-2],
        "missing_first": ORIGINAL_NAMES[1:],
        "missing_integration_dex": [name for name in ORIGINAL_NAMES if name != "classes8.dex"],
        "gap": [name for name in ORIGINAL_NAMES if name != "classes14.dex"],
        "extra_dex": ORIGINAL_NAMES + ["classes17.dex"],
        "helper_collision": ORIGINAL_NAMES + ["classes16.dex"],
        "duplicate_original": ORIGINAL_NAMES + ["classes14.dex"],
        "wrong_first_name": ["classes1.dex"] + ORIGINAL_NAMES[1:],
    }
    for label, names in negative_layouts.items():
        with zipfile.ZipFile(io.BytesIO(archive([(name, b"fixture") for name in names]))) as original:
            try:
                assembler.validate_base_dex_layout(original)
            except SystemExit as error:
                assert "Unexpected base DEX layout" in str(error), (label, error)
            else:
                raise AssertionError("Unexpected DEX layout accepted: " + label)
    print("BACHATA_FRONTEND_DEX_LAYOUT_PASS:",
          "15 real reference DEX" if reference_apk else "15 fixture DEX",
          "; originals except 4/8 preserved; helper16 appended; 8 unexpected layouts rejected")
    if reference_apk:
        for name in EXTRA_DEX_HASHES:
            print(name, len(originals[name]), hashlib.sha256(originals[name]).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-apk", type=Path)
    test(parser.parse_args().reference_apk)
