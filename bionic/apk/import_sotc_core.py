"""Import the exact signed revised SotC core without rewriting it."""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
REV="1401b3733b8facb592b5a49f14047369815e2a3e"
APK=Path(sys.argv[1])
LIB=Path(sys.argv[2])
PREFIX="lib/arm64-v8a/"
OLD="libbachata_bionic_core.so"
NEW="libbachata_sotc_core.so"
def sha(b):return hashlib.sha256(b).hexdigest()
def needed(p):
    return set(re.findall(r"Shared library: \[(.*?)\]",subprocess.check_output(["readelf","-d",str(p)],text=True)))
with zipfile.ZipFile(APK) as z:
    build=json.loads(z.read("assets/bachata-bionic-build.json"))
    raw=z.read(PREFIX+OLD)
    assert build["nativeCoreSourceRevision"]==REV
    assert build["nativeCoreSha256"]==sha(raw)
    assert ("BACHATA_CORE_REVISION="+REV).encode() in raw
    dst=LIB/NEW
    dst.write_bytes(raw)
    # All APK-bundled dependencies must be present and export every
    # symbol required by the old core; exact same dependencies are preferred.
    main=LIB/OLD
    assert needed(dst)==needed(main), "SotC and current core dependency list differs"
    for dep in needed(dst):
        if PREFIX+dep not in z.namelist():continue
        old=z.read(PREFIX+dep)
        current=LIB/dep
        # A mismatch is not silently accepted. This protects ABI and
        # preserves the independently tested runtime's libraries.
        assert current.is_file() and sha(current.read_bytes())==sha(old), "SotC shared dependency differs: "+dep
    symbols=subprocess.check_output(["readelf","--dyn-syms","--wide",str(dst)],text=True)
    for name in ("JNI_OnLoad","Java_org_libsdl_app_SDLActivity_nativeSetupJNI",
                 "Java_org_libsdl_app_SDLAudioManager_nativeSetupJNI",
                 "Java_org_libsdl_app_SDLControllerManager_nativeSetupJNI",
                 "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run",
                 "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop"):
        assert any(line.split()[-1]==name and " GLOBAL " in line and " UND " not in line
                   for line in symbols.splitlines() if line.split()), "Missing "+name
    assert sha(dst.read_bytes())==build["nativeCoreSha256"]
    print("BACHATA_PINNED_SOTC_CORE_VERIFIED",REV,sha(raw))
