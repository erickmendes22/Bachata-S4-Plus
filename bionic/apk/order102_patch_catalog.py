#!/usr/bin/env python3
"""Adapt the pinned Order 01.02 donor recipes to Bachata's in-memory XML patches.

No guest file, CPU backend, or prepared port image is imported. Addresses in
the public XML convention are donor RVAs plus 0x400000. The native reader must
implement RequireAllExpected and the mutually exclusive IfEnabled/IfDisabled
conditions before this catalogue is packaged.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
import zipfile

DONOR_REVISION = "c53cd01d032995fe622033623ab64b4cf6b02233"
DONOR_BASE = "https://github.com/JulioCacko/The-Order-1886_pc/blob/" + DONOR_REVISION
CATALOG_VERSION = "order1886-0102-port-v1"
XML_NAME = "TheOrder1886.xml"
RUNTIME_PATHS = tuple(prefix + "/bachata-official/" + XML_NAME
                      for prefix in ("patches", "user/patches"))
ASPECT_NAME = "16:9 Aspect Ratio (Full Screen)"
IMAGE_BASE = 0x400000

# Exact instruction bytes from scripts/order1886_post_effects.py at DONOR_REVISION.
EFFECTS = {
    "Disable Motion Blur": (
        "Desativa a intensidade de motion blur pelo caminho nativo do jogo.",
        ((0x835086, "c5fa10864c010000", "c5f857c00f1f4000"),)),
    "Disable Depth of Field": (
        "Desativa a intensidade de profundidade de campo nas lentes normal e alternativa.",
        ((0x8358AF, "c5fa5d9e98030000", "c5e057db0f1f4000"),
         (0x835617, "c5fa5da62c020000", "c5d857e40f1f4000"),
         (0x81DD89, "c5fa5d05d3e8c100", "c5f857c00f1f4000"))),
    "Disable Film Grain": (
        "Remove a intensidade de granulação nas lentes normal e alternativa.",
        ((0x8355DF, "c5fa5d9e24020000", "c5e057db0f1f4000"),
         (0x835887, "c5fa5d9e60030000", "c5e057db0f1f4000"))),
    "Disable Chromatic Aberration": (
        "Remove o deslocamento de cores da aberração cromática em todos os caminhos da lente.",
        ((0x81DE57, "8b86c4030000", "31c00f1f4000"),
         (0x81DE63, "488b86bc030000", "31c00f1f440000"),
         (0x81DEC1, "8b8e74030000", "31c90f1f4000"),
         (0x81DECA, "488b8e6c030000", "31c90f1f440000"),
         (0x81DEF7, "8b5108", "31d290"),
         (0x81DEFD, "488b09", "31c990"))),
}
RESOLUTIONS = {
    "Resolution Patch (900p)": 1600,
    "Resolution Patch (720p)": 1280,
    "Resolution: 540p (extreme performance)": 960,
    "Resolution: 360p (ultra performance)": 640,
}
STORES = ((0x44CEF7, "c78584fcffff00050000"),
          (0x44CF01, "c78588fcffffd0020000"),
          (0x44CF1F, "c785d8fbffff00050000"),
          (0x44CF29, "c785dcfbffffd0020000"))
STACK_SITES = (
    (0xCA6030, "b80000e00f"),
    (0xCA5E87, "488d880000200a"),
    (0xCA5E92, "488d900000500b"),
    (0xCA5EA5, "48c743600000200a"),
    (0xCA5EB5, "48c7437800009004"),
    *((rva, "48c783" + disp + "000000009004") for rva, disp in
      ((0xCA5ECB, "9000"), (0xCA5EE4, "a800"), (0xCA5F7A, "3801"))),
    *((rva, "48c783" + disp + "000000003001") for rva, disp in
      ((0xCA5EFD, "c000"), (0xCA5F16, "d800"), (0xCA5F2F, "f000"),
       (0xCA5F48, "0801"), (0xCA5F61, "2001"))),
)
HEAP_SITES = ((0x298D0B, "ba0000e028"), (0x298D33, "be0000e028"),
              (0x298D63, "48c705c29741010000e028"), (0x2997CC, "be0000e028"))
ASPECT_RVA = 0x44CE86
ASPECT_EXPECTED = "c78518fcffff9a991940"
ASPECT_REPLACEMENT = "c78518fcffff398ee33f"


def instruction(rva: int, expected: str, replacement: str, **conditions: str) -> ET.Element:
    old, new = bytes.fromhex(expected), bytes.fromhex(replacement)
    if not old or len(old) != len(new):
        raise ValueError("Every recipe must replace a complete, equal-length instruction")
    return ET.Element("Line", Type="bytes", Address=f"0x{rva + IMAGE_BASE:08x}",
                      Expected=old.hex(), Value=new.hex(), **conditions)


def replace_immediate(expected: str, at: int, value: int) -> str:
    code = bytearray.fromhex(expected)
    code[at:at + 4] = struct.pack("<I", value)
    return code.hex()


def resolution_lines(width: int) -> list[ET.Element]:
    # Match Python's ties-to-even rounding in the actual donor, including 900p
    # -> 896 and 540p -> 544. At these widths its max(1, scene/native) policy
    # deliberately keeps all GPU stack/heap sizes at retail capacity.
    height = round(width * 9 / 16 / 8) * 8
    cinematic_height = round(width / 2.4)
    lines = [instruction(0x44CEF5, "7441", "7541")]
    for (rva, expected), value in zip(STORES, (width, height, width, height)):
        lines.append(instruction(rva, expected, replace_immediate(expected, 6, value)))
    lines.append(instruction(0x839C54, "bf80070000", replace_immediate("bf80070000", 1, width)))
    for condition, scene_height in (("IfEnabled", height), ("IfDisabled", cinematic_height)):
        lines.append(instruction(0x839C59, "be20030000",
                                 replace_immediate("be20030000", 1, scene_height),
                                 **{condition: ASPECT_NAME}))
    lines.extend(instruction(rva, expected, expected) for rva, expected in STACK_SITES + HEAP_SITES)
    # Guard the aspect dependency in the same transaction as the 16:9 scene.
    # The separate aspect patch writes exactly these bytes, so either order is safe.
    lines.append(instruction(ASPECT_RVA, ASPECT_EXPECTED, ASPECT_REPLACEMENT,
                             IfEnabled=ASPECT_NAME))
    return lines


def upgrade_xml(raw: bytes) -> bytes:
    root = ET.fromstring(raw)
    if root.tag != "Patch" or "CUSA00785" not in {n.text for n in root.findall("TitleID/ID")}:
        raise ValueError("Not the expected bundled The Order catalogue")
    existing = {n.get("Name"): n for n in root.findall("Metadata") if n.get("AppVer") == "01.02"}
    if not set(RESOLUTIONS).issubset(existing) or ASPECT_NAME not in existing:
        raise ValueError("The published Order 01.02 catalogue changed; inspect before merging")
    if root.get("BachataPortCatalog") not in (None, CATALOG_VERSION):
        raise ValueError("Refusing to replace a different port catalogue version")
    root.set("BachataPortCatalog", CATALOG_VERSION)
    for name, width in RESOLUTIONS.items():
        node = existing[name]
        node.set("RequireAllExpected", "true")
        node.set("Source", DONOR_BASE + "/scripts/order1886_resolution.py")
        node.set("Note", f"Quadro {width}x{round(width * 9 / 16 / 8) * 8}. "
                 f"Cena cinematográfica {width}x{round(width / 2.4)}; "
                 "com 16:9 selecionado, a cena ocupa o quadro inteiro. "
                 "Escolha somente uma resolução.")
        for old in list(node):
            node.remove(old)
        ET.SubElement(node, "PatchList").extend(resolution_lines(width))
    for name, (note, edits) in EFFECTS.items():
        node = existing.get(name)
        if node is None:
            node = ET.SubElement(root, "Metadata", Title="The Order 1886", Name=name,
                                 Author="The Order PC port", PatchVer="1.0", AppVer="01.02",
                                 AppElf="eboot.bin", isEnabled="false")
        elif node.get("Source") != DONOR_BASE + "/scripts/order1886_post_effects.py":
            raise ValueError("Unexpected pre-existing 01.02 effect recipe: " + name)
        node.set("Note", note)
        node.set("RequireAllExpected", "true")
        node.set("Source", DONOR_BASE + "/scripts/order1886_post_effects.py")
        for old in list(node):
            node.remove(old)
        ET.SubElement(node, "PatchList").extend(instruction(*edit) for edit in edits)
    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def runtime_updates(original_apk: zipfile.ZipFile) -> dict[str, bytes]:
    """Return both replacement entries for compact_runtime's verified file table."""
    with zipfile.ZipFile(io.BytesIO(original_apk.read("assets/runtime/runtime.zip"))) as runtime:
        originals = [runtime.read(path) for path in RUNTIME_PATHS]
        if originals[0] != originals[1]:
            raise ValueError("Bundled immutable/user Order catalogue copies differ")
        catalogue = upgrade_xml(originals[0])
        for prefix in ("patches", "user/patches"):
            index = json.loads(runtime.read(prefix + "/bachata-official/files.json"))
            if "CUSA00785" not in index.get(XML_NAME, []):
                raise ValueError("Order 01.02 is missing from the bundled title index")
    return {path: catalogue for path in RUNTIME_PATHS}


def catalogue_identity(catalogue: bytes) -> str:
    return hashlib.sha256(catalogue).hexdigest()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    result = upgrade_xml(a.source.read_bytes())
    a.output.write_bytes(result)
    print(CATALOG_VERSION, catalogue_identity(result), len(result))
