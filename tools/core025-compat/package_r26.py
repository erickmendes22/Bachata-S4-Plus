#!/usr/bin/env python3
"""Package the pre-FSR R25 with unique runtime ID, verified native RB and catalog."""
import argparse,copy,hashlib,io,json,zipfile,xml.etree.ElementTree as E
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('core');p.add_argument('patches');p.add_argument('work');a=p.parse_args()
sha=lambda d:hashlib.sha256(d).hexdigest();w=Path(a.work);w.mkdir(parents=True,exist_ok=True)
assert sha(Path(a.base).read_bytes())=='b941ffbd9e4a6b073e157c91c2598aeed153313a535a7f05af59e5fba1aaa184'
core=Path(a.core).read_bytes();xml=Path(a.patches,'MarvelsSpiderMan_CUSA02999_0100.xml').read_bytes()
assert b'bs4_fsr31' not in core
runtime_id='bachata-s4-n026-0.2.6-r'
assert len(runtime_id)==len('bachata-s4-r025-0.2.6-r') and runtime_id.endswith('-r')
with zipfile.ZipFile(a.base) as old:
    manifest=json.loads(old.read('assets/runtime/manifest.json'));assert manifest['runtimeVersion']=='bachata-s4-r025-0.2.6-r';manifest['runtimeVersion']=runtime_id
    before_bytes=old.read('assets/runtime/runtime.zip');replacements={'host/shadps4-arm64-025':core}
    with zipfile.ZipFile(io.BytesIO(before_bytes)) as before:
        for prefix in ['patches/bachata-official','user/patches/bachata-official']:
            fn=prefix+'/files.json';catalog=json.loads(before.read(fn))
            assert not any('CUSA02999' in ids or 'CUSA02299' in ids for ids in catalog.values())
            catalog['MarvelsSpiderMan_CUSA02999_0100.xml']=['CUSA02999','CUSA02299']
            replacements[fn]=(json.dumps(catalog,indent=2)+'\n').encode()
            replacements[prefix+'/MarvelsSpiderMan_CUSA02999_0100.xml']=xml
        assert sha(before.read('host/shadps4-arm64-fex'))=='5c162129531b9446557c25c6a06ff5fe2a85f489c8d35d6faa5b929234735882'
        with zipfile.ZipFile(w/'runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
            for info in before.infolist():out.writestr(copy.copy(info),replacements.get(info.filename,before.read(info)))
            for fn,b in replacements.items():
                if fn not in before.namelist():
                    info=copy.copy(before.getinfo(fn.rsplit('/',1)[0]+'/MarvelsSpiderMan_CUSA11993_0100.xml'));info.filename=fn;out.writestr(info,b)
        mapped={x['path']:x for x in manifest['files']}
        for fn,b in replacements.items():
            item={'path':fn,'size':len(b),'sha256':sha(b)}
            if fn in mapped:mapped[fn].update(item)
            else:manifest['files'].append(item)
    apk_changes={'assets/runtime/runtime.zip':(w/'runtime.zip').read_bytes(),'assets/runtime/manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
    def signature(n):return n.upper().startswith('META-INF/') and n.upper().endswith(('.RSA','.DSA','.EC','.SF','MANIFEST.MF'))
    with zipfile.ZipFile(w/'unsigned.apk','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
        for info in old.infolist():
            if not signature(info.filename):out.writestr(copy.copy(info),apk_changes.get(info.filename,old.read(info)))
    with zipfile.ZipFile(w/'unsigned.apk') as final:
        assert all(final.read(n)==old.read(n) for n in old.namelist() if n not in apk_changes and not signature(n))
    with zipfile.ZipFile(w/'runtime.zip') as final,zipfile.ZipFile(io.BytesIO(before_bytes)) as before:
        assert not any('fsr31' in n.lower() for n in final.namelist())
        for item in manifest['files']:
            b=final.read(item['path']);assert len(b)==item['size'] and sha(b)==item['sha256']
        assert all(final.read(n)==before.read(n) for n in before.namelist() if n not in replacements)
        for prefix in ['patches/bachata-official','user/patches/bachata-official']:
            catalog=json.loads(final.read(prefix+'/files.json'))
            for name,ids in catalog.items():
                root=E.fromstring(final.read(prefix+'/'+name))
                # New entry is visible under both the requested and diagnostic IDs.
                if name=='MarvelsSpiderMan_CUSA02999_0100.xml':
                    assert ids==[x.text for x in root.findall('./TitleID/ID')]
                    assert len(root.findall('Metadata'))==7
    report={'runtimeVersion':runtime_id,'runtimeCollisionRemoved':True,'diagnosticDispatcherSha256':'19f4e03f08c4fb10b0dd5d6b5e2b0838a53700942636fd932bb7ea6966a32634','includedDispatcherSha256':'5c162129531b9446557c25c6a06ff5fe2a85f489c8d35d6faa5b929234735882','fsr31PayloadAndHooks':False,'coreSha256':sha(core),'catalogIds':['CUSA02999','CUSA02299'],'spiderPatchOptions':7,'androidDexPreserved':True,'otherRuntimesPreserved':True,'allManifestHashesVerified':True,'deviceValidated':False}
    (w/'r26-package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: unique pre-FSR runtime, valid mirrored patch catalog, byte-identical DEX/legacy cores, all file hashes verified')
