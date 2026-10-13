#!/usr/bin/env python3
# Repackage only the tested SDK and runtime identity; preserve current core/DEX.
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('sdk');p.add_argument('work');p.add_argument('--sdk-sha',required=True);a=p.parse_args()
w=Path(a.work);w.mkdir(parents=True,exist_ok=True);sdk=Path(a.sdk).read_bytes();sha=lambda data:hashlib.sha256(data).hexdigest();assert sha(sdk)==a.sdk_sha
base=Path(a.base);assert sha(base.read_bytes())=='8aecaa5bb6edf3ba77aca0706a37399f163020d44651548cab08444ecc6155a2'
with zipfile.ZipFile(base) as old:
 m=json.loads(old.read('assets/runtime/manifest.json'));assert m['runtimeVersion']=='bachata-s4-r023-0.2.6-r';new='bachata-s4-r024-0.2.6-r';assert len(new)==len(m['runtimeVersion']);m['runtimeVersion']=new
 original=old.read('assets/runtime/runtime.zip')
 with zipfile.ZipFile(io.BytesIO(original)) as r,zipfile.ZipFile(w/'runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  assert sha(r.read('host/shadps4-arm64-025'))=='a4d218a1af0bd10dadc32096e3cfbee7e7fc98a1ee4c3326b56bd0c0780f9f3a'
  for info in r.infolist():out.writestr(copy.copy(info),sdk if info.filename=='host/libbachata_fsr31.so' else r.read(info))
 for item in m['files']:
  if item['path']=='host/libbachata_fsr31.so':item.update(size=len(sdk),sha256=sha(sdk))
 replacements={'assets/runtime/runtime.zip':(w/'runtime.zip').read_bytes(),'assets/runtime/manifest.json':(json.dumps(m,indent=2)+'\n').encode()}
 def signature(n):return n.upper().startswith('META-INF/') and n.upper().endswith(('.RSA','.DSA','.EC','.SF','MANIFEST.MF'))
 with zipfile.ZipFile(w/'unsigned.apk','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for info in old.infolist():
   if not signature(info.filename):out.writestr(copy.copy(info),replacements.get(info.filename,old.read(info)))
 with zipfile.ZipFile(w/'unsigned.apk') as result:
  assert all(old.read(n)==result.read(n) for n in old.namelist() if n not in replacements and not signature(n))
  dex={n:sha(result.read(n)) for n in result.namelist() if n.endswith('.dex')}
 with zipfile.ZipFile(w/'runtime.zip') as r,zipfile.ZipFile(io.BytesIO(original)) as before:
  core_sha=sha(r.read('host/shadps4-arm64-025'))
  changed=[n for n in r.namelist() if r.read(n)!=before.read(n)];assert changed==['host/libbachata_fsr31.so']
  for item in m['files']:
   content=r.read(item['path']);assert len(content)==item['size'] and sha(content)==item['sha256'],item['path']
 report={'runtimeVersion':new,'sdkSha256':sha(sdk),'core025Sha256':core_sha,'dexPreserved':dex,'onlyRuntimePayloadChange':changed,'nativeControlsAndOtherCoreRoutesPreserved':True,'gpuValidation':'passed synthetic camera/FSR/original-HUD tests','deviceCrashValidated':False}
 (w/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: tested SDK installed, full runtime manifest checked, current core025 and all Android/other-runtime payloads preserved')
