#!/usr/bin/env python3
"""Use official pre-FSR 0.2.6 Android code and runtime, add patched native 025."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('core');p.add_argument('dispatcher');p.add_argument('work');a=p.parse_args()
w=Path(a.work);w.mkdir(parents=True,exist_ok=True);sha=lambda d:hashlib.sha256(d).hexdigest()
core=Path(a.core).read_bytes();dispatch=Path(a.dispatcher).read_bytes()
assert b'bs4_fsr31' not in core and b'BACHATA_FSR31' not in dispatch
assert sha(dispatch)=='5c162129531b9446557c25c6a06ff5fe2a85f489c8d35d6faa5b929234735882'
with zipfile.ZipFile(a.base) as old:
    manifest=json.loads(old.read('assets/runtime/manifest.json'))
    assert manifest['runtimeVersion']=='bachata-s4-plus-0.2.6-r'
    manifest['runtimeVersion']='bachata-s4-r025-0.2.6-r'
    original_runtime=old.read('assets/runtime/runtime.zip')
    with zipfile.ZipFile(io.BytesIO(original_runtime)) as before,zipfile.ZipFile(w/'runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
        assert not any('fsr31' in n.lower() for n in before.namelist())
        for info in before.infolist():
            out.writestr(copy.copy(info),dispatch if info.filename=='host/shadps4-arm64-fex' else before.read(info))
        info=copy.copy(before.getinfo('host/shadps4-arm64-024'));info.filename='host/shadps4-arm64-025'
        out.writestr(info,core)
    for item in manifest['files']:
        if item['path']=='host/shadps4-arm64-fex':item.update(size=len(dispatch),sha256=sha(dispatch))
    manifest['files'].append({'path':'host/shadps4-arm64-025','size':len(core),'sha256':sha(core)})
    replacements={'assets/runtime/runtime.zip':(w/'runtime.zip').read_bytes(),'assets/runtime/manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
    def signature(n):return n.upper().startswith('META-INF/') and n.upper().endswith(('.RSA','.DSA','.EC','.SF','MANIFEST.MF'))
    with zipfile.ZipFile(w/'unsigned.apk','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
        for info in old.infolist():
            if not signature(info.filename):out.writestr(copy.copy(info),replacements.get(info.filename,old.read(info)))
    with zipfile.ZipFile(w/'unsigned.apk') as result:
        assert all(old.read(n)==result.read(n) for n in old.namelist() if n not in replacements and not signature(n))
    with zipfile.ZipFile(w/'runtime.zip') as runtime,zipfile.ZipFile(io.BytesIO(original_runtime)) as before:
        for item in manifest['files']:
            b=runtime.read(item['path']);assert len(b)==item['size'] and sha(b)==item['sha256']
        changes=[n for n in before.namelist() if before.read(n)!=runtime.read(n)]
        assert changes==['host/shadps4-arm64-fex']
        assert not any('fsr31' in n.lower() for n in runtime.namelist())
    report={'baseApkSha256':sha(Path(a.base).read_bytes()),'runtimeVersion':manifest['runtimeVersion'],'core025Sha256':sha(core),'androidDexAndOtherApkEntriesPreserved':True,'legacyCoresPreserved':True,'fsr31PayloadAndHooks':False,'runtimeChanges':changes+['host/shadps4-arm64-025'],'deviceValidated':False}
    (w/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: pre-FSR Android DEX intact, native 025 installed, legacy runtimes intact, all runtime hashes verified')
