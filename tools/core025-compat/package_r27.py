#!/usr/bin/env python3
"""R26 -> R27: scoped Elden 024 dispatch and removal of native 023."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
from route_r27 import patch
from test_route_r27 import test
sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('work');a=p.parse_args();w=Path(a.work);w.mkdir(parents=True,exist_ok=True)
base=Path(a.base).read_bytes();assert sha(base)=='9bed0e88fb2ff6508609b0e7fdef073a2b460e1aef87d4be2a7a56fc6125ce1f'
removed='host/shadps4-arm64-023';changed='host/shadps4-arm64-fex';runtime_id='bachata-s4-n027-0.2.6-r'
with zipfile.ZipFile(io.BytesIO(base)) as old:
 manifest=json.loads(old.read('assets/runtime/manifest.json'));assert manifest['runtimeVersion']=='bachata-s4-n026-0.2.6-r';assert len(runtime_id)==len(manifest['runtimeVersion']);manifest['runtimeVersion']=runtime_id
 with zipfile.ZipFile(io.BytesIO(old.read('assets/runtime/runtime.zip'))) as before:
  assert removed in before.namelist();(w/'dispatcher-base').write_bytes(before.read(changed));digest=patch(w/'dispatcher-base',w/'dispatcher');checks=test(w/'dispatcher');dispatcher=(w/'dispatcher').read_bytes()
  with zipfile.ZipFile(w/'runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
   for info in before.infolist():
    if info.filename!=removed:out.writestr(copy.copy(info),dispatcher if info.filename==changed else before.read(info))
  manifest['files']=[item for item in manifest['files'] if item['path']!=removed]
  for item in manifest['files']:
   if item['path']==changed:item.update(size=len(dispatcher),sha256=digest)
  with zipfile.ZipFile(w/'runtime.zip') as final:
   assert not any('023' in n or 'fsr31' in n.lower() for n in final.namelist())
   for item in manifest['files']:
    b=final.read(item['path']);assert len(b)==item['size'] and sha(b)==item['sha256'],item['path']
   assert all(final.read(n)==before.read(n) for n in before.namelist() if n not in [changed,removed])
   assert sha(final.read('host/shadps4-arm64-024'))=='04294ca3223e26c864429f243a21fe8f9de99400074fb9bf8630109939490702'
   assert sha(final.read('host/shadps4-arm64-025'))=='373aba94528c85dfcf2846df4589d85d285bf865b3e658bd85de0df11cb80c59'
 replacements={'assets/runtime/runtime.zip':(w/'runtime.zip').read_bytes(),'assets/runtime/manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
 def signature(n):return n.upper().startswith('META-INF/') and n.upper().endswith(('.RSA','.DSA','.EC','.SF','MANIFEST.MF'))
 with zipfile.ZipFile(w/'unsigned.apk','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for info in old.infolist():
   if not signature(info.filename):out.writestr(copy.copy(info),replacements.get(info.filename,old.read(info)))
 with zipfile.ZipFile(w/'unsigned.apk') as final:
  assert final.testzip() is None
  assert all(final.read(n)==old.read(n) for n in old.namelist() if n not in replacements and not signature(n))
report={'runtimeVersion':runtime_id,'elden024Ids':['CUSA18723','CUSA28527','CUSA28863'],'core023Removed':True,'old023RoutesRemoved':True,'defaultCore':'025','driveclub020Retained':True,'core024And025Unmodified':True,'androidDexUnmodified':True,'allPatchCatalogsUnmodified':True,'manifestHashesVerified':True,'dispatcherSha256':digest,'tests':checks,'deviceValidated':False}
(w/'r27-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
