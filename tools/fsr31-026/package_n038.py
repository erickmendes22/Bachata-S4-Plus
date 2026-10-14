#!/usr/bin/env python3
"""Replace only n037's FSR SDK and re-extraction identity; retain its APK/native cores."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('sdk');p.add_argument('work');a=p.parse_args()
w=Path(a.work);w.mkdir(parents=True,exist_ok=True)
base=Path(a.base).read_bytes();assert sha(base)=='a5c8099284bd810dab7c54a81a237c6bdb45cc9cc0121142c0b97c243f2a54a2'
sdk=Path(a.sdk).read_bytes();target='host/libbachata_fsr31.so';runtime='bachata-s4-n038-0.2.6-r'
with zipfile.ZipFile(io.BytesIO(base)) as apk:
 m=json.loads(apk.read('assets/runtime/manifest.json'));assert m['runtimeVersion']=='bachata-s4-n037-0.2.6-r'
 assert len(m['runtimeVersion'])==len(runtime);m['runtimeVersion']=runtime
 with zipfile.ZipFile(io.BytesIO(apk.read('assets/runtime/runtime.zip'))) as old:
  assert 'host/shadps4-arm64-023' not in old.namelist()
  assert sha(old.read('host/shadps4-arm64-025'))=='c1cf8986c2a5f6f9f33d32a073eff797e2717b4848cd475c4d19f26dc7042bb2'
  with zipfile.ZipFile(w/'runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
   for info in old.infolist():out.writestr(copy.copy(info),sdk if info.filename==target else old.read(info))
  for item in m['files']:
   if item['path']==target:item.update(size=len(sdk),sha256=sha(sdk))
  with zipfile.ZipFile(w/'runtime.zip') as out:
   assert out.testzip() is None
   assert all(out.read(n)==old.read(n) for n in old.namelist() if n!=target)
   for item in m['files']:
    b=out.read(item['path']);assert len(b)==item['size'] and sha(b)==item['sha256'],item['path']
 replacements={'assets/runtime/runtime.zip':(w/'runtime.zip').read_bytes(),'assets/runtime/manifest.json':(json.dumps(m,indent=2)+'\n').encode()}
 def signature(n):return n.upper().startswith('META-INF/') and n.upper().endswith(('.RSA','.DSA','.EC','.SF','MANIFEST.MF'))
 with zipfile.ZipFile(w/'unsigned.apk','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for info in apk.infolist():
   if not signature(info.filename):out.writestr(copy.copy(info),replacements.get(info.filename,apk.read(info)))
 with zipfile.ZipFile(w/'unsigned.apk') as out:
  assert out.testzip() is None
  assert all(out.read(n)==apk.read(n) for n in apk.namelist() if n not in replacements and not signature(n))
report={'base':'n037','runtimeVersion':runtime,'baseSha256':sha(base),'sdkSha256':sha(sdk),'native025ByteIdenticalToN037':True,'allOtherCoresByteIdenticalToN037':True,'androidDexByteIdenticalToN037':True,'patchCatalogsByteIdenticalToN037':True,'runtimeHashesVerified':True,'nativeCoreCompiled':False,'deviceValidated':False}
(w/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
