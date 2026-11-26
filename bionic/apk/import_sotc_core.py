"""Combine independently compiled Bachata FEX cores, verifying exact revision and ABI."""
import hashlib,re,subprocess,sys
from pathlib import Path
REV="d95da7bddb405a4a2da9a8f1d7451a0aab2cdb87"
stage=Path(sys.argv[1])
lib=Path(sys.argv[2])
assert (stage/"BIONIC_SOURCE_REVISION.txt").read_text().strip()==REV
src=stage/"lib/arm64-v8a"
old="libbachata_bionic_core.so"
new="libbachata_sotc_core.so"
def sha(b):return hashlib.sha256(b).hexdigest()
def needed(p):return set(re.findall(r"Shared library: \[(.*?)\]",subprocess.check_output(["readelf","-d",str(p)],text=True)))
raw=(src/old).read_bytes()
assert ("BACHATA_CORE_REVISION="+REV).encode() in raw
assert needed(src/old)==needed(lib/old),"Core DT_NEEDED mismatch"
for dep in needed(src/old):
    if not (src/dep).is_file():continue
    assert (lib/dep).is_file() and sha((src/dep).read_bytes())==sha((lib/dep).read_bytes()),"Mismatched shared dependency: "+dep
symbols=subprocess.check_output(["readelf","--dyn-syms","--wide",str(src/old)],text=True)
for name in ("JNI_OnLoad","Java_org_libsdl_app_SDLActivity_nativeSetupJNI","Java_org_libsdl_app_SDLAudioManager_nativeSetupJNI","Java_org_libsdl_app_SDLControllerManager_nativeSetupJNI","Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run","Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop"):
    assert any(line.split()[-1]==name and " GLOBAL " in line and " UND " not in line for line in symbols.splitlines() if line.split()),"Missing "+name
(lib/new).write_bytes(raw)
assert sha((lib/new).read_bytes())==sha(raw)
print("BACHATA_PINNED_SOTC_FEX_CORE_VERIFIED",REV,sha(raw))
