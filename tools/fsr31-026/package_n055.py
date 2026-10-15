#!/usr/bin/env python3
"""Package the validated final-color SDK into the exact n054 Android/core payload."""
import argparse,copy,hashlib,io,json,struct,zipfile
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()
def signature(name):
    return name.upper().startswith('META-INF/') and name.upper().endswith(('.RSA','.DSA','.EC','.SF','MANIFEST.MF'))
def aligned_write(out,original,data):
    entry=copy.copy(original)
    if entry.compress_type==zipfile.ZIP_STORED:
        # Preserve non-alignment extra fields, rebuild padding at the new offset.
        extra=entry.extra;kept=b'';at=0
        while at<len(extra):
            tag,size=struct.unpack_from('<HH',extra,at)
            assert at+4+size<=len(extra)
            if tag not in (0xd935,0xffff):kept+=extra[at:at+4+size]
            at+=4+size
        alignment=16384 if entry.filename.endswith('.so') else 4
        start=out.fp.tell()+30+len(entry.filename.encode('utf-8'))+len(kept)
        if start%alignment:
            pad=(-start-4)%alignment
            kept+=struct.pack('<HH',0xd935,pad)+b'\0'*pad
        entry.extra=kept
    out.writestr(entry,data)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('base');parser.add_argument('sdk');parser.add_argument('work')
    args=parser.parse_args();work=Path(args.work);work.mkdir(parents=True,exist_ok=True)
    base=Path(args.base).read_bytes();sdk=Path(args.sdk).read_bytes()
    assert sha(base)=='864ef09497e9b3a494adb9cddfcd790841e51c587628142874ec0408204a22a7'
    assert sha(sdk)=='c68ebe3697661a14b26f2ca10ac7887d4f923180e4b8e6f3a04a7d556f56f304'
    assert sdk[:4]==b'\x7fELF' and struct.unpack_from('<H',sdk,18)[0]==183
    assert b'BS4_TEST_NO_DRAW_BOUNDARY' not in sdk and b'BS4_TEST_ACCEPT_UNRELATED_SCENE' not in sdk
    target='host/libbachata_fsr31.so';runtime='bachata-s4-n055-0.2.6-r'
    with zipfile.ZipFile(io.BytesIO(base)) as apk:
        manifest=json.loads(apk.read('assets/runtime/manifest.json'))
        assert manifest['runtimeVersion']=='bachata-s4-n054-0.2.6-r'
        assert len(manifest['runtimeVersion'])==len(runtime)
        manifest['runtimeVersion']=runtime
        with zipfile.ZipFile(io.BytesIO(apk.read('assets/runtime/runtime.zip'))) as old:
            assert 'host/shadps4-arm64-023' not in old.namelist()
            native=sha(old.read('host/shadps4-arm64-025'))
            assert native=='c1cf8986c2a5f6f9f33d32a073eff797e2717b4848cd475c4d19f26dc7042bb2'
            with zipfile.ZipFile(work/'runtime.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
                for info in old.infolist():out.writestr(copy.copy(info),sdk if info.filename==target else old.read(info))
            with zipfile.ZipFile(work/'runtime.zip') as out:
                assert out.testzip() is None
                assert set(out.namelist())==set(old.namelist())
                assert [n for n in old.namelist() if out.read(n)!=old.read(n)]==[target]
                for item in manifest['files']:
                    if item['path']==target:item.update(size=len(sdk),sha256=sha(sdk))
                    data=out.read(item['path']);assert len(data)==item['size'] and sha(data)==item['sha256'],item['path']
        replacements={'assets/runtime/runtime.zip':(work/'runtime.zip').read_bytes(),
            'assets/runtime/manifest.json':(json.dumps(manifest,indent=2)+'\n').encode()}
        with zipfile.ZipFile(work/'unsigned.apk','w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
            for info in apk.infolist():
                if not signature(info.filename):aligned_write(out,info,replacements.get(info.filename,apk.read(info)))
        with zipfile.ZipFile(work/'unsigned.apk') as out:
            assert out.testzip() is None
            for name in apk.namelist():
                if name not in replacements and not signature(name):assert out.read(name)==apk.read(name),name
            with (work/'unsigned.apk').open('rb') as stream:
                for info in out.infolist():
                    if info.compress_type!=zipfile.ZIP_STORED:continue
                    stream.seek(info.header_offset+26);name,extra=struct.unpack('<HH',stream.read(4))
                    offset=info.header_offset+30+name+extra
                    assert offset%(16384 if info.filename.endswith('.so') else 4)==0,info.filename
    report={'release':'n055','sourceCommit':'1586ddba0c3faa4653a32446553ad34124a6f53d','ciRun':38730560673,
        'baseApkSha256':sha(base),'sdkSha256':sha(sdk),'native025Sha256':native,'runtimeVersion':runtime,
        'runtimeEntriesVerified':len(manifest['files']),'nativeCoreRecompiled':False,'nativeCoreModified':False,
        'allNonSDKRuntimePayloadsIdentical':True,'androidDexAndManifestPreserved':True,
        'storedZipAlignmentVerified':True,'arm64AndGpuValidationPassed':True,
        'finalColorIdentityAndSamePassDrawCorrectionsIncluded':True,'deviceValidated':False,
        'phoneCyanEliminationConfirmed':False,'unrelatedR27HookRegressionRepaired':False}
    (work/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
