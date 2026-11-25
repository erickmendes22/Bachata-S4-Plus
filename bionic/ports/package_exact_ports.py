#!/usr/bin/env python3
"""Preserve original host resources; insert only isolated donor modules and bridge."""
import argparse, hashlib, io, json, pathlib, re, struct, zipfile

def sha(b):return hashlib.sha256(b).hexdigest()
def u16(b,o):return struct.unpack_from("<H",b,o)[0]
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def words(*a):return struct.pack("<"+"I"*len(a),*a)
def chunk(t,h,p):return struct.pack("<HHI",t,h,len(p)+8)+p

def manifest(data):
    if u16(data,0)!=3:raise RuntimeError("not Android binary XML")
    chunks=[];off=u16(data,2)
    while off<len(data):
        size=u32(data,off+4)
        if size<8 or off+size>len(data):raise RuntimeError("invalid XML chunk")
        chunks.append(bytearray(data[off:off+size]));off+=size
    pool=chunks[0]
    if u16(pool,0)!=1 or u32(pool,12)!=0 or u32(pool,16)&256:
        raise RuntimeError("host string pool layout changed")
    n=u32(pool,8);start=u32(pool,20);header=u16(pool,2)
    strings=[]
    for i in range(n):
        p=start+u32(pool,header+i*4);length=u16(pool,p)
        if length&0x8000:raise RuntimeError("unexpected long XML string")
        strings.append(bytes(pool[p+2:p+2+length*2]).decode("utf-16le"))
    def sid(s):
        if s not in strings:strings.append(s)
        return strings.index(s)
    rm=chunks[1]
    if u16(rm,0)!=0x180:raise RuntimeError("resource map missing")
    ids=[u32(rm,i) for i in range(8,len(rm),4)]
    def attr(s,rid):
        i=sid(s)
        ids.extend([0]*max(0,i+1-len(ids)))
        if ids[i] not in (0,rid):raise RuntimeError("attribute id mismatch")
        ids[i]=rid
        return i
    name=attr("name",0x01010003)
    theme=attr("theme",0x01010000)
    exported=attr("exported",0x01010010)
    process=attr("process",0x01010011)
    orient=attr("screenOrientation",0x0101001e)
    config=attr("configChanges",0x0101001f)
    factory=attr("appComponentFactory",0x0101057a)
    ns=sid("http://schemas.android.com/apk/res/android")
    act=sid("activity");app=sid("application")
    f=sid("com.bachata.ports.PortFactory")
    changed=0;out=[]
    def activity(cls,proc,land,flags):
        entries=[(theme,1,0x0103022e),(name,3,sid(cls)),(exported,0x12,0),
                 (process,3,sid(proc)),(config,0x11,flags)]
        if land:entries.append((orient,0x10,6))
        entries.sort(key=lambda a:ids[a[0]])
        body=words(0,0xffffffff,0xffffffff,act)
        body+=struct.pack("<HHHHHH",20,20,len(entries),0,0,0)
        for k,t,v in entries:
            body+=words(ns,k,v if t==3 else 0xffffffff)+struct.pack("<HBBI",8,0,t,v)
        return [chunk(0x102,16,body),chunk(0x103,16,words(0,0xffffffff,0xffffffff,act))]
    for c in chunks[2:]:
        t=u16(c,0)
        if t==0x102 and u32(c,20)==app:
            base=16+u16(c,24)
            for i in range(u16(c,28)):
                p=base+i*u16(c,26)
                if u32(c,p+4)==factory:
                    struct.pack_into("<I",c,p+8,f)
                    struct.pack_into("<I",c,p+16,f)
                    changed+=1
        if t==0x103 and u32(c,20)==app:
            out+=activity("ro.cobrabm.fexdroid.Order1886Activity",":exact_order",True,1264)
            out+=activity("com.gow3.android.MainActivity",":exact_sotc",False,5616)
            out+=activity("ro.cobrabm.fexdroid.GameActivity",":exact_sotc",True,5616)
        out.append(bytes(c))
    if changed!=1:raise RuntimeError("factory anchor changed")
    vals=[];offsets=[];pos=0
    for s in strings:
        v=s.encode("utf-16le")
        offsets.append(pos);x=struct.pack("<H",len(v)//2)+v+b"\0\0";vals.append(x);pos+=len(x)
    payload=b"".join(vals);payload+=b"\0"*((-len(payload))%4)
    newpool=chunk(1,28,words(len(strings),0,0,28+4*len(strings),0)+words(*offsets)+payload)
    body=newpool+chunk(0x180,8,words(*ids))+b"".join(out)
    return chunk(3,8,body)

def signature(n):return n.startswith("META-INF/") and (n.endswith((".RSA",".DSA",".EC",".SF")) or n=="META-INF/MANIFEST.MF")
def dex_members(z):return {n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex",n)}
def module(original,rebuilt):
    buf=io.BytesIO()
    with zipfile.ZipFile(original) as a,zipfile.ZipFile(rebuilt) as b,zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        if not dex_members(a)<=dex_members(b):raise RuntimeError("donor dex set lost")
        for n in a.namelist():
            if n.endswith("/") or signature(n) or n.startswith("lib/") or n in dex_members(a):continue
            z.writestr(n,a.read(n))
        for n in sorted(dex_members(b)):
            z.writestr(n,b.read(n))
    return buf.getvalue()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",type=pathlib.Path,required=True)
    p.add_argument("--rebuilt",type=pathlib.Path,required=True)
    p.add_argument("--bridge",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args()
    rep=json.loads((a.stage/"parity-inputs.json").read_text())
    mods={k:module(a.stage/k/"original.apk",a.rebuilt/(k+".apk")) for k in ("order","sotc")}
    native={}
    for k in ("order","sotc"):
        for f in (a.stage/k/"lib/arm64-v8a").glob("*.so"):
            n=f.name
            if n=="libc++_shared.so":continue
            if n=="libandroidx.graphics.path.so":
                # Resolve this JNI library from the donor-specific installed
                # alias, not the host Compose version (see bridge loader).
                n="libbachata_sotc_graphics_path.so"
            if n in native:raise RuntimeError("donor library name collision: "+n)
            native[n]=f.read_bytes()
    for f in (a.stage/"native-exec-aliases").glob("*.so"):native[f.name]=f.read_bytes()
    with zipfile.ZipFile(a.stage/"bachata/original.apk") as original,zipfile.ZipFile(a.rebuilt/"bachata.apk") as patched,zipfile.ZipFile(a.output,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        if not dex_members(original)<=dex_members(patched):raise RuntimeError("host dex set lost")
        for n in original.namelist():
            if n.endswith("/") or signature(n) or n in dex_members(original):continue
            if n=="AndroidManifest.xml":
                z.writestr(n,manifest(original.read(n)));continue
            if n.startswith("lib/arm64-v8a/"):
                if pathlib.PurePosixPath(n).name in native:raise RuntimeError("host native name collision "+n)
                z.writestr(n,original.read(n),compress_type=zipfile.ZIP_STORED)
            else:z.writestr(n,original.read(n))
        for n in sorted(dex_members(patched)):z.writestr(n,patched.read(n))
        index=max(int(re.sub(r"\D","",n) or "1") for n in dex_members(patched))+1
        z.writestr(f"classes{index}.dex",a.bridge.read_bytes())
        for k,v in mods.items():
            z.writestr(f"assets/exact-ports/{k}.apk",v,compress_type=zipfile.ZIP_STORED)
            z.writestr(f"assets/exact-ports/{k}.sha256",sha(v)+"\n")
        for n,v in native.items():z.writestr("lib/arm64-v8a/"+n,v,compress_type=zipfile.ZIP_STORED)
        rep["integration_candidate"]={"module_sha256":{k:sha(v) for k,v in mods.items()},
                                     "added_native_sha256":{n:sha(v) for n,v in native.items()},
                                     "device_verified":False}
        z.writestr("assets/exact-ports/provenance.json",json.dumps(rep,indent=2))
    with zipfile.ZipFile(a.output) as z:
        if z.testzip() is not None:raise RuntimeError("invalid output APK")
        for n,v in native.items():
            if sha(z.read("lib/arm64-v8a/"+n))!=sha(v):raise RuntimeError("native bytes changed")
        for k,v in mods.items():
            if sha(z.read(f"assets/exact-ports/{k}.apk"))!=sha(v):raise RuntimeError("module changed")
    print("Assembled unified integration candidate; gameplay not verified")

if __name__=="__main__":main()
