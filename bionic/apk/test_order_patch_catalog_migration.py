#!/usr/bin/env python3
"""Compile and execute the exact Java XML migration helper against runtime trees."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import order102_patch_catalog as catalogue
import patch_order_catalog_frontend as hooks

HERE = Path(__file__).parent
RELATIVE = Path("patches/bachata-official/TheOrder1886.xml")
BASE = (HERE / "testdata/order102_donor/TheOrder1886.before.xml").read_bytes()
NEW = catalogue.upgrade_xml(BASE)
FIELDS = ("Title", "Name", "Author", "AppVer", "AppElf")


def identity(node):
    return tuple(node.get(field, "") for field in FIELDS)


def selected(raw):
    return {identity(n): n.get("isEnabled") == "true" for n in ET.fromstring(raw).findall("Metadata")}


def choose(raw, names, app="01.02"):
    root = ET.fromstring(raw)
    for node in root.findall("Metadata"):
        node.set("isEnabled", "true" if node.get("Name") in names and node.get("AppVer") == app else "false")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def create_runtime(parent, name, raw=NEW):
    root = parent / ("bachata-s4-plus-0.2.7-bionic-" + name)
    for prefix in (Path(), Path("user")):
        path = root / prefix / RELATIVE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return root


def edit(root, raw, time):
    path = root / "user" / RELATIVE
    path.write_bytes(raw)
    os.utime(path, (time, time))


def compare_functional_bytes(before, after):
    old, new = ET.fromstring(before), ET.fromstring(after)
    assert old.attrib == new.attrib
    assert [n.text for n in old.findall("TitleID/ID")] == [n.text for n in new.findall("TitleID/ID")]
    for a, b in zip(old.findall("Metadata"), new.findall("Metadata"), strict=True):
        assert {k: v for k, v in a.attrib.items() if k != "isEnabled"} == {
            k: v for k, v in b.attrib.items() if k != "isEnabled"}
        assert [n.attrib for n in a.findall("PatchList/Line")] == [n.attrib for n in b.findall("PatchList/Line")]
    # Entire instruction elements, including attribute order and whitespace,
    # must remain byte-for-byte the new payload, not copied from the old XML.
    assert re.findall(rb"<Line\b[^>]*>", before) == re.findall(rb"<Line\b[^>]*>", after)


def test_hooks():
    selector = """.class public LSelector;
.method private activeRuntimeDirectory()Ljava/io/File;
    .locals 10
    if-eqz v2, :fallback
    return-object v3
    :fallback
    return-object v0
.end method
.method private unrelated()V
    return-void
.end method
.method private loadPatchesAsync()V
    .locals 2
    new-instance v0, Ljava/lang/Thread;
    new-instance v1, Lcom/bachatas4/android/patches/PatchSelectorActivity$6;
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    return-void
.end method
"""
    installer = """.class public final Lcom/bachatas4/android/service/GlibcSessionRuntime;
.method public constructor <init>(Landroid/content/Context;)V
    .locals 0
    return-void
.end method
.method public final install()Ljava/nio/file/Path;
    .locals 2
    const-string v0, "runtime/manifest.json"
    const-string v0, "runtime/runtime.zip"
    invoke-virtual {v0, v1}, Lcom/bachatas4/android/runtime/install/RuntimeInstaller;->install-gIAlu-s(Ljava/io/InputStream;Lcom/bachatas4/android/runtime/install/RuntimeManifest;)Ljava/lang/Object;
    return-object v0
.end method
"""
    # The real 0.2.7 DEX includes this synthetic accessor and the private method.
    # Keep the accessor's descriptor/register flow faithful to that DEX; a word
    # boundary before validateRequest incorrectly accepts both declarations.
    launcher = """.class public Lcom/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher;
.method public static final synthetic access$validateRequest(Lcom/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher;Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;Z)Lcom/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher$NativeLaunch;
    .locals 0
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher;->validateRequest(Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;Z)Lcom/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher$NativeLaunch;
    move-result-object p0
    return-object p0
.end method
.method private final validateRequest(Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;Z)Lcom/bachatas4/android/runtime/process/NativeRuntimeProcessLauncher$NativeLaunch;
    .locals 9
    const/4 v1, 0x0
    invoke-virtual {p1}, Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;->getRuntimeRoot()Ljava/nio/file/Path;

    move-result-object v0
    new-array v2, v1, [Ljava/nio/file/LinkOption;
    invoke-interface {v0, v2}, Ljava/nio/file/Path;->toRealPath([Ljava/nio/file/LinkOption;)Ljava/nio/file/Path;
    return-object v0
.end method
"""
    a, b = hooks.hook_selector(selector), hooks.hook_launcher(launcher)
    assert a.count(hooks.HELPER) == 1 and b.count(hooks.HELPER) == 1
    hooks.validate_installer(installer, selector)
    for broken in (installer.replace("RuntimeInstaller;->install-", "OtherInstaller;->install-"),
                   installer.replace("public final install()", "private final install()")):
        try:
            hooks.validate_installer(broken, selector)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted an incompatible existing installer")
    def unchanged(body):
        return [line.strip() for line in body.splitlines() if line.strip() and hooks.HELPER not in line]
    start, end, _ = hooks.method_range(selector, "activeRuntimeDirectory")
    new_start, new_end, method = hooks.method_range(a, "activeRuntimeDirectory")
    assert a[:new_start] + a[new_end:] == selector[:start] + selector[end:]
    # Execute the replacement method's register flow with an installer contract
    # double. Verify the returned object originates from a completed install,
    # migration happens afterwards, and install failure never returns old data.
    def execute_selector(fail=False):
        registers = {"p0": object()}
        events = []
        installed_path, installed_file = object(), object()
        pending = None
        for line in (line.strip() for line in method.splitlines()):
            if not line or line.startswith("."):
                continue
            opcode, operands = line.split(" ", 1)
            if opcode == "new-instance":
                target, kind = operands.split(", ")
                assert kind == hooks.INSTALLER
                registers[target] = object()
            elif opcode == "move-result-object":
                registers[operands] = pending
            elif opcode.startswith("invoke-"):
                args, target = operands.split("}, ", 1)
                values = [registers[arg] for arg in args[1:].split(", ")]
                if target == hooks.INSTALLER + "-><init>(Landroid/content/Context;)V":
                    assert len(values) == 2 and values[1] is registers["p0"]
                elif target == hooks.INSTALLER + "->install()Ljava/nio/file/Path;":
                    events.append("install")
                    if fail:
                        return events, None
                    pending = installed_path
                elif target == "Ljava/nio/file/Path;->toFile()Ljava/io/File;":
                    assert values == [installed_path]
                    pending = installed_file
                elif target == hooks.HELPER + "->prepare(Ljava/io/File;)V":
                    assert values == [installed_file]
                    events.append("prepare")
                else:
                    raise AssertionError("Unexpected selector operation " + target)
            elif opcode == "return-object":
                assert registers[operands] is installed_file
                events.append("return")
                return events, installed_file
            else:
                raise AssertionError("Unexpected selector opcode " + opcode)
        raise AssertionError("Selector did not return")
    assert execute_selector()[0] == ["install", "prepare", "return"]
    assert execute_selector(True) == (["install"], None)
    assert unchanged(b) == unchanged(launcher)
    assert b.index(hooks.HELPER) < b.index("->toRealPath")
    _, _, accessor = hooks.method_range(launcher, "access$validateRequest")
    assert hooks.method_range(b, "access$validateRequest")[2] == accessor
    start, end, original = hooks.method_range(launcher, "validateRequest")
    # An accessor alone must never satisfy the private entry point, and two
    # complete declarations must still fail before any file can be modified.
    for broken in (launcher[:start] + launcher[end:], launcher + original + "\n"):
        try:
            hooks.hook_launcher(broken)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted a missing or duplicate exact launcher method")
    for fn, body in ((hooks.hook_selector, a), (hooks.hook_launcher, b)):
        try:
            fn(body)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted a duplicate hook")


def main():
    with tempfile.TemporaryDirectory(prefix="order102-migration-") as temp:
        temp = Path(temp)
        classes = temp / "classes"
        classes.mkdir()
        runner = temp / "MigrationRunner.java"
        runner.write_text("""import java.io.File;
public final class MigrationRunner {
    public static void main(String[] args) {
        com.bachatas4.android.patches.OrderPatchCatalog.prepare(new File(args[0]));
        com.bachatas4.android.patches.OrderPatchCatalog.prepare(new File(args[0]).toPath());
    }
}
""")
        compiler = [shutil.which("javac")] if shutil.which("javac") else ["java", "com.sun.tools.javac.Main"]
        # The local runtime includes javac's module but no ct.sym archive. CI's
        # full JDK uses --release 8; the local compiler still enforces Java 8 syntax/bytecode.
        language = ["--release", "8", "-Xlint:all"] if shutil.which("javac") else [
            "-source", "8", "-target", "8", "-Xlint:all,-options"]
        java_source = HERE / "java/com/bachatas4/android/patches/OrderPatchCatalog.java"
        subprocess.run(compiler + language + ["-Werror", "-d", str(classes),
                                   str(java_source), str(runner)], check=True)
        def run(root):
            return subprocess.run(["java", "-cp", str(classes), "MigrationRunner", str(root)],
                                  check=True, capture_output=True, text=True)
        def case(name):
            parent = temp / name
            parent.mkdir()
            return parent, create_runtime(parent, "current")
        count = 0

        parent, current = case("recent-identity")
        stale = create_runtime(parent, "zzzzzzzz", BASE)
        recent = create_runtime(parent, "aaaaaaaa", BASE)
        untouched = create_runtime(parent, "newest-untouched", BASE)
        edit(stale, choose(BASE, {"Resolution Patch (900p)"}), 100)
        intended = choose(BASE, {"Resolution Patch (720p)", catalogue.ASPECT_NAME,
                                 "Disable Cloth Simulation"})
        edit(recent, intended, 200)
        os.utime(untouched / "user" / RELATIVE, (300, 300))
        result = run(current)
        got = (current / "user" / RELATIVE).read_bytes()
        compare_functional_bytes(NEW, got)
        for key, state in selected(intended).items():
            assert selected(got)[key] == state
        assert all(not value for key, value in selected(got).items()
                   if key[1] in catalogue.EFFECTS and key[3] == "01.02")
        assert "SELECTION_MIGRATED" in result.stderr
        saved = choose(got, {"Disable Film Grain"})
        (current / "user" / RELATIVE).write_bytes(saved)
        run(current)
        assert (current / "user" / RELATIVE).read_bytes() == saved
        count += 1

        parent, current = case("explicit-all-off")
        old = create_runtime(parent, "old", BASE)
        recent = create_runtime(parent, "recent", BASE)
        edit(old, choose(BASE, {"Resolution Patch (720p)"}), 100)
        edit(recent, choose(BASE, set()), 200)
        run(current)
        assert not any(selected((current / "user" / RELATIVE).read_bytes()).values())
        count += 1

        parent, current = case("current-choice-wins")
        old = create_runtime(parent, "old", BASE)
        edit(old, choose(BASE, {"Resolution Patch (720p)"}), 100)
        current_choice = choose(NEW, {"Disable Film Grain"})
        (current / "user" / RELATIVE).write_bytes(current_choice)
        run(current)
        assert (current / "user" / RELATIVE).read_bytes() == current_choice
        count += 1

        parent, current = case("version-author-isolation")
        old = create_runtime(parent, "old", BASE)
        legacy = ET.fromstring(choose(BASE, {"Disable Motion Blur"}, "01.00"))
        for node in legacy.findall("Metadata"):
            if node.get("Name") == "Resolution Patch (720p)" and node.get("AppVer") == "01.02":
                node.set("Author", "another author")
                node.set("isEnabled", "true")
        edit(old, ET.tostring(legacy), 100)
        run(current)
        states = selected((current / "user" / RELATIVE).read_bytes())
        assert any(state for key, state in states.items() if key[1] == "Disable Motion Blur" and key[3] == "01.00")
        assert not any(state for key, state in states.items() if key[3] == "01.02")
        count += 1

        for name, bad in (("malformed-newest", b"<Patch>"),
                          ("doctype", b'<!DOCTYPE Patch SYSTEM "file:///dev/null"><Patch/>')):
            parent, current = case(name)
            old = create_runtime(parent, "old", BASE)
            bad_root = create_runtime(parent, "bad", BASE)
            edit(old, choose(BASE, {"Resolution Patch (720p)"}), 100)
            edit(bad_root, bad, 200)
            run(current)
            assert (current / "user" / RELATIVE).read_bytes() == NEW
            count += 1

        parent, current = case("equal-time-conflict")
        for name, choices in (("first", {"Resolution Patch (720p)"}), ("second", set())):
            old = create_runtime(parent, name, BASE)
            edit(old, choose(BASE, choices), 100)
        run(current)
        assert (current / "user" / RELATIVE).read_bytes() == NEW
        count += 1

        parent, current = case("no-history")
        run(current)
        assert (current / "user" / RELATIVE).read_bytes() == NEW
        count += 1

        parent, current = case("raw-attributes-comments")
        text = NEW.decode().replace("<TitleID>", '<!-- <Metadata isEnabled="false"> -->\n    <TitleID>', 1)
        text = text.replace('Note="Quadro ', 'Note="mentions isEnabled=\'false\'; Quadro ', 1)
        raw = text.encode()
        assert b"mentions isEnabled='false';" in raw
        for prefix in (Path(), Path("user")):
            (current / prefix / RELATIVE).write_bytes(raw)
        old = create_runtime(parent, "old", BASE)
        edit(old, choose(BASE, {"Resolution Patch (900p)"}), 100)
        run(current)
        got = (current / "user" / RELATIVE).read_bytes()
        compare_functional_bytes(raw, got)
        assert b'<!-- <Metadata isEnabled="false"> -->' in got
        assert b"mentions isEnabled='false';" in got
        assert any(state for key, state in selected(got).items() if key[1] == "Resolution Patch (900p)" and key[3] == "01.02")
        count += 1

        parent, current = case("two-processes")
        old = create_runtime(parent, "old", BASE)
        edit(old, choose(BASE, {"Resolution Patch (720p)"}), 100)
        processes = [subprocess.Popen(["java", "-cp", str(classes), "MigrationRunner", str(current)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for process in processes:
            process.communicate(timeout=30)
            assert process.returncode == 0
        got = (current / "user" / RELATIVE).read_bytes()
        compare_functional_bytes(NEW, got)
        assert any(state for key, state in selected(got).items() if key[1] == "Resolution Patch (720p)" and key[3] == "01.02")
        count += 1
    test_hooks()
    print(f"ORDER102_SELECTION_MIGRATION_PASS: {count} real Java runtime-tree cases; "
          "full identity, newest edited selection, bytes preserved, malformed history, "
          "idempotence, process locking, selector install/prepare/return and register-safe launch hook")


if __name__ == "__main__":
    main()
