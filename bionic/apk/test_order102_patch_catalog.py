#!/usr/bin/env python3
"""Compare the actual pinned donor applicators against the generated guest-memory XML."""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET

import order102_patch_catalog as catalog

FIXTURES = Path(__file__).parent / "testdata/order102_donor"
sys.path.insert(0, str(FIXTURES))
import order1886_frame_rate as timing
import order1886_display as display
import order1886_resolution as donor_resolution
import order1886_post_effects as donor_effects
import patch_android_resolution as android_resolution


def active_lines(node, enabled):
    result = []
    for line in node.findall("PatchList/Line"):
        if line.get("IfEnabled") and line.get("IfEnabled") not in enabled:
            continue
        if line.get("IfDisabled") and line.get("IfDisabled") in enabled:
            continue
        assert line.get("Type") == "bytes"
        result.append((int(line.get("Address"), 16) - catalog.IMAGE_BASE,
                       bytes.fromhex(line.get("Expected")), bytes.fromhex(line.get("Value"))))
    return result


def memory_image(lines):
    data = bytearray(max(address + len(old) for address, old, _ in lines) + 64)
    for address, old, new in lines:
        assert len(old) == len(new) and old
        data[address:address + len(old)] = old
    return data


def xml_apply(image, lines):
    # This decoder is only the catalogue side of the comparison. Native
    # transaction/rollback semantics are tested separately against production C++.
    for address, old, new in lines:
        assert image[address:address + len(old)] in (old, new)
    for address, old, new in lines:
        image[address:address + len(old)] = new


def write_boot(path, image):
    path.write_bytes(timing.HEADER.pack(b"PS4BOOT2", len(image), 0, 0, 0, 0, 0) + image)


def boot_image(path):
    data, start, size = timing.prepared_image(path)
    return data[start:start + size]


def check_preserved(before, after):
    selected_names = set(catalog.RESOLUTIONS)
    def identity(node):
        return tuple(node.get(k, "") for k in ("Title", "Name", "Author", "AppVer", "AppElf"))
    new = {identity(n): n for n in after.findall("Metadata")}
    for old in before.findall("Metadata"):
        got = new[identity(old)]
        assert old.get("isEnabled") == got.get("isEnabled"), identity(old)
        if old.get("AppVer") != "01.02" or old.get("Name") not in selected_names:
            # Whitespace changes on the outer tree are irrelevant to the XML reader.
            assert old.attrib == got.attrib
            assert [n.attrib for n in old.findall("PatchList/Line")] == [
                n.attrib for n in got.findall("PatchList/Line")]


def main():
    for name, entry in json.loads((FIXTURES / "provenance.json").read_text()).items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == entry["sha256"]
    before_bytes = (FIXTURES / "TheOrder1886.before.xml").read_bytes()
    before = ET.fromstring(before_bytes)
    generated = catalog.upgrade_xml(before_bytes)
    assert catalog.upgrade_xml(generated) == generated
    after = ET.fromstring(generated)
    check_preserved(before, after)
    nodes = {n.get("Name"): n for n in after.findall("Metadata") if n.get("AppVer") == "01.02"}
    assert len(nodes) == 13
    assert all(nodes[name].get("isEnabled") == "false" for name in catalog.EFFECTS)
    with tempfile.TemporaryDirectory(prefix="order102-catalog-") as temp:
        temp = Path(temp)
        # Apply the actual Android bound overlay to an untouched donor source.
        source = temp / "order1886_resolution.py"
        source.write_bytes((FIXTURES / "order1886_resolution.py").read_bytes())
        android_resolution.patch(source)
        spec = importlib.util.spec_from_file_location("donor_android_resolution", source)
        resolution = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(resolution)
        boot = temp / "boot.bin"
        for name, width in catalog.RESOLUTIONS.items():
            for aspect in ("original", "16:9"):
                enabled = {catalog.ASPECT_NAME} if aspect == "16:9" else set()
                lines = active_lines(nodes[name], enabled)
                image = memory_image(lines)
                # The comparison includes every original instruction checked by
                # the donor, including unchanged retail stack and heap capacities.
                site_map = {address: old for address, old, _ in lines}
                for address, old in resolution.sites():
                    assert site_map[address] == old, hex(address)
                write_boot(boot, image)
                if aspect == "16:9":
                    display.apply_prepared(boot, {**display.recipe(aspect), "source_verified": True,
                                                 "recipe_sha256": display.recipe_sha256(aspect)})
                profile = {**resolution.recipe(width, aspect), "source_verified": True,
                           "recipe_sha256": resolution.recipe_sha256(width, aspect)}
                resolution.apply_prepared(boot, profile)
                expected = boot_image(boot)
                xml_apply(image, lines)
                assert image == expected, (name, aspect)
                xml_apply(image, lines)
                assert image == expected, (name, aspect, "idempotent")
        names = list(catalog.EFFECTS)
        donor_names = list(donor_effects.EFFECTS)
        for switches in itertools.product((False, True), repeat=4):
            lines = [line for name, on in zip(names, switches) if on
                     for line in active_lines(nodes[name], set())]
            if not lines:
                continue
            disabled = [name for name, on in zip(donor_names, switches) if on]
            image = memory_image(lines)
            write_boot(boot, image)
            donor_effects.apply_prepared(boot, {**donor_effects.recipe(disabled),
                                               "source_verified": True,
                                               "recipe_sha256": donor_effects.recipe_sha256(disabled)})
            expected = boot_image(boot)
            xml_apply(image, lines)
            assert image == expected, disabled
        # Upgrade a previously user-selected catalogue without resetting any choice.
        for node in before.findall("Metadata"):
            node.set("isEnabled", "true" if node.get("Name") in (catalog.ASPECT_NAME,
                     "Resolution Patch (720p)", "Disable Cloth Simulation") else "false")
        upgraded = ET.fromstring(catalog.upgrade_xml(ET.tostring(before)))
        check_preserved(before, upgraded)
    print("ORDER102_DONOR_RECIPES_PASS: 8 resolution/aspect byte-for-byte comparisons, "
          "15 effect combinations, idempotence and existing selection/legacy preservation")


if __name__ == "__main__":
    main()
