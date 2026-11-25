#!/usr/bin/env python3
"""Import complete known donor runtimes without mixing ABIs or rewriting their cores.

This is an input/staging gate, NOT a claim of functional equivalence.
The final Android integration must preserve these inputs and pass device tests.
"""
import argparse
import hashlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import tarfile
import zipfile

PINS = {
    "order": {
        "repository": "erickmendes22/gow3_android_daedalus_fork",
        "source": "756a4f0cc603b02971d45b36354143249a4fe492",
        "run": 44980141404, "artifact": 14737726767,
        "version": "0.1.37", "target_sdk": 30,
        "apk_sha256": "3bcf45225b8f4ac90b9b2e9cf5ab15afafe07b7935be9b437995c2c3ac942fbc",
    },
    "sotc": {
        "repository": "erickmendes22/ShadowOfTheColossus-Android-Aot",
        "source": "6556a9f15747395c13b48a058394b00866989b6e",
        "run": 45109431755, "artifact": 14789291050,
        "gpu_source": "0366868550bde078d9ed9d88bc72d8acb1584679",
        "gpu_run": 45069117755,
        "version": "0.2.0", "target_sdk": 28,
        "apk_sha256": "a4324bace40d2e2958c96cee80d2ae4970d6859bfe385a4e71c16289a64fc9cf",
    },
    "bachata": {
        "repository": "erickmendes22/Bachata-S4-Plus",
        "source": "5f89cdc32a1972ae0c166ad076f48d4b6bf28330",
        "run": 45616521572, "artifact": 15022563487,
        "target_sdk": 37,
        "apk_sha256": "3709f7cd9f9c1aa6a71252d4652dfb663b92f1e872afb67c2a16817dd5c8192f",
    },
}
ORDER_LIBS = {
    "liborder1886_probe.so", "liborder1886cpu.so", "libps4gpu.so",
    "liborder1886present.so", "liborder1886_pkg_util.so",
    "liborder1886_python.so", "libpython3.13.so", "libc++_shared.so",
}
SOTC_LIBS = {
    "libbbgpu.so", "libgow3gpu.so", "libgow3cpu.so", "libbbcpu.so",
    "libgow3present.so", "libc++_shared.so",
}
SOTC_EXE = (
    "sotcport/arm64/bin/sotc-probe", "sotcport/arm64/bin/gow3-prepare",
    "sotcport/arm64/bin/kgsl-chip-id", "sotcport/arm64/bin/orbis-pkg-util",
    "sotcport/arm64/python/bin/python3.13",
)
def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def safe_name(name):
    p = pathlib.PurePosixPath(name)
    require(not p.is_absolute() and ".." not in p.parts, f"unsafe member {name}")
    return p

def readelf(path, *flags):
    return subprocess.check_output(["readelf", *flags, str(path)], text=True)

def inspect_elf(path):
    hdr = readelf(path, "-h")
    require("AArch64" in hdr, f"non-ARM64 ELF: {path}")
    dyn = readelf(path, "-d")
    ph = readelf(path, "-l")
    return {"sha256": sha(path.read_bytes()),
            "needed": re.findall(r"\(NEEDED\).*?\[(.*?)\]", dyn),
            "soname": re.findall(r"\(SONAME\).*?\[(.*?)\]", dyn),
            "interpreter": "INTERP" in ph}

def store(root, name, data):
    dst = root / safe_name(name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dst

def dynamic_symbols(path):
    exports, imports = set(), set()
    for line in readelf(path, "--dyn-syms", "--wide").splitlines():
        fields = line.split()
        if len(fields) < 8 or not fields[0].endswith(":"):
            continue
        if fields[4] not in ("GLOBAL", "WEAK"):
            continue
        name = fields[7].split("@")[0]
        if fields[6] == "UND":
            if fields[4] == "GLOBAL":
                imports.add(name)
        else:
            exports.add(name)
    return exports, imports

def import_apk(kind, apk, out):
    require(sha(apk.read_bytes()) == PINS[kind]["apk_sha256"],
            f"{kind}: APK pin mismatch")
    root = out / kind
    root.mkdir()
    # Keep an original APK for resource/class isolation and reproducible provenance.
    shutil.copyfile(apk, root / "original.apk")
    files, elfs = {}, {}
    with zipfile.ZipFile(apk) as z:
        require(z.testzip() is None, f"{kind}: damaged APK")
        names = z.namelist()
        require(len(names) == len(set(names)), f"{kind}: duplicate ZIP members")
        for n in names:
            safe_name(n)
            if n.endswith("/"):
                continue
            if n.startswith(("assets/", "lib/arm64-v8a/")) or n in (
                "AndroidManifest.xml", "resources.arsc"
            ) or re.fullmatch(r"classes\d*\.dex", n):
                data = z.read(n)
                p = store(root, n, data)
                files[n] = sha(data)
                if n.startswith("lib/arm64-v8a/"):
                    elfs[n] = inspect_elf(p)
        require("classes.dex" in files and "AndroidManifest.xml" in files, kind)
        if kind == "order":
            require(ORDER_LIBS == {pathlib.PurePosixPath(n).name for n in elfs},
                    "Order native library set changed")
            require(all(n in files for n in ("assets/order1886-toolchain.zip",
                                            "assets/order1886-turnip-default.zip")),
                    "Order runtime assets missing")
        if kind == "sotc":
            payload = z.read("assets/runtime.payload")
            require(sha(payload) == z.read("assets/runtime.sha256").decode().strip(),
                    "SotC payload hash mismatch")
            with tarfile.open(fileobj=io.BytesIO(payload)) as tar:
                manifest = json.load(tar.extractfile("runtime-manifest.json"))
                require(manifest["aot_mode"] == "strict" and
                        manifest["fex_runtime_included"] is False and
                        manifest["on_device_aot_compiler_included"] is True,
                        "SotC must retain strict AOT, not generic FEX")
                require(manifest["audio_engine"]["id"] == "ngs2-software-mixer",
                        "SotC NGS2 host missing")
                for m in tar.getmembers():
                    safe_name(m.name)
                    if m.isfile():
                        data = tar.extractfile(m).read()
                        files["payload/" + m.name] = sha(data)
                        if data.startswith(b"\x7fELF"):
                            p = store(root, "payload/" + m.name, data)
                            elfs["payload/" + m.name] = inspect_elf(p)
            probe = "payload/sotcport/arm64/bin/sotc-probe"
            require(elfs[probe]["sha256"] == manifest["audio_engine"]["host_sha256"],
                    "SotC NGS2 executable mismatch")
            require(all("payload/sotcport/arm64/lib/" + n in elfs for n in SOTC_LIBS),
                    "SotC native library set incomplete")
            require(all(elfs["payload/" + n]["interpreter"] for n in SOTC_EXE),
                    "SotC executable set incomplete")
            driver = "payload/sotcport/arm64/drivers/gamehub-dd/libvulkan_freedreno.so"
            require(files[driver] == manifest["driver"]["library_sha256"],
                    "SotC driver mismatch")
            cpu = elfs["payload/sotcport/arm64/lib/libgow3cpu.so"]
            require(not any("fex" in n.lower() for n in cpu["needed"]),
                    "SotC CPU depends on FEX")
            host_exports, _ = dynamic_symbols(root / probe)
            _, gpu_imports = dynamic_symbols(root / "payload/sotcport/arm64/lib/libbbgpu.so")
            unresolved = {n for n in gpu_imports if n.startswith(("runtime_", "bbgpu_", "sotc_"))
                          and n not in host_exports}
            require(not unresolved, f"SotC host/GPU ABI mismatch: {sorted(unresolved)}")
    return {**PINS[kind], "files": files, "elf": elfs}

def main():
    p = argparse.ArgumentParser()
    for name in PINS:
        p.add_argument("--" + name, type=pathlib.Path, required=True)
    p.add_argument("--out", type=pathlib.Path, required=True)
    a = p.parse_args()
    require(not a.out.exists(), "refusing to overwrite staging directory")
    a.out.mkdir(parents=True)
    modules = {name: import_apk(name, getattr(a, name), a.out) for name in PINS}
    cxx = {name: modules[name]["elf"]["lib/arm64-v8a/libc++_shared.so"]["sha256"]
           for name in PINS}
    require(len(set(cxx.values())) == 3, "unexpected dependency identity")
    # The two donor binaries are not interchangeable with the host core.
    # Android 10+ target-SDK restrictions prohibit executing a private filesDir
    # binary in the target-37 host. The final installer must map the original
    # donor executable bytes to installed executable native-library paths.
    aliases = {}
    for name in SOTC_EXE:
        alias = "libbachata_sotc_exec_" + pathlib.PurePosixPath(name).name.replace("-", "_").replace(".", "_") + ".so"
        aliases[name] = {"apk_entry": "lib/arm64-v8a/" + alias,
                         "sha256": modules["sotc"]["files"]["payload/" + name]}
        store(a.out / "native-exec-aliases", alias,
              (a.out / "sotc" / "payload" / name).read_bytes())
    order_alias = "libbachata_order_cxx.so"
    store(a.out / "native-exec-aliases", order_alias,
          (a.out / "order/lib/arm64-v8a/libc++_shared.so").read_bytes())
    report = {
        "schema": 1, "source": "exact complete donor APKs, no per-shader cherry-picks",
        "modules": modules, "cxx_sha256": cxx, "sotc_exec_aliases": aliases,
        "order_private_cxx": order_alias,
        "android_integration_ready": False, "gameplay_verified": False,
        "required_device_gates": [
            "single original-signer Bachata APK; no external APK installation",
            "actual title routing and no generic fallback for selected titles",
            "isolated libraries/classes/resources and donor native executable hashes",
            "SotC strict AOT verify/compile with matching game and patch hashes",
            "original donor AHB presenter, correct real-frame FPS and input/audio",
            "same game files, settings, patches, driver and comparable scene",
            "cold/warm shader cache, texture streaming, saves, suspend/resume",
            "frame-time p50/p95/p99, image comparisons and crash-free matched runs",
            "other Bachata titles retain original generic execution path",
        ],
    }
    (a.out / "parity-inputs.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Exact donor inputs and native ABI verified; Android integration and gameplay remain unverified.")

if __name__ == "__main__":
    main()
