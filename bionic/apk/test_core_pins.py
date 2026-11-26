"""Prevent stale duplicated revisions before downloading APK build artifacts."""
import json
import tempfile
from pathlib import Path
from core_pins import read_pins, require_revision

def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("Invalid core artifact identity accepted")

def test():
    p = read_pins()
    raw = b"ELF fixture\x00BACHATA_CORE_REVISION=" + p["sotc_revision"].encode() + b"\x00"
    require_revision(raw, p["sotc_revision"], "SotC")
    reject(lambda: require_revision(raw, p["revision"], "SotC"))
    reject(lambda: require_revision(b"ELF fixture", p["sotc_revision"], "SotC"))
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)/"reuse.json"
        for change in ({"sotc_revision": p["revision"]}, {"sotc_run": p["run"]},
                       {"sotc_revision": "stale"}, {"run": True}, {"sotc_run": -1}):
            path.write_text(json.dumps({**p, **change}), encoding="utf-8")
            reject(lambda: read_pins(path))
    root = Path(__file__).resolve().parents[2]
    for name in ("assemble_apk.py", "import_sotc_core.py"):
        source = (Path(__file__).parent/name).read_text()
        assert 'read_pins()' in source and 'require_revision(' in source
        import re
        assert not re.search(r'(?m)^\s*(?:SOTC_REV|REV)\s*=\s*["\'][0-9a-f]{40}["\']', source), name
    workflow = (root/".github/workflows/bachata-bionic-source0181-build.yml").read_text()
    assert "python3 bionic/apk/core_pins.py" in workflow
    assert "steps.core.outputs.sotc_run" in workflow
    assert "steps.core.outputs.sotc_revision" in workflow
    for key in ("revision", "sotc_revision"):
        assert p[key] not in workflow, "Duplicated revision in workflow"
    print("BACHATA_DUAL_CORE_PINS_PASS", p["revision"], p["sotc_revision"])

if __name__ == "__main__":
    test()
