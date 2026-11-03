#!/usr/bin/env python3
"""Exact executable .text diff: original GameHub A830 vs working GameHub DD.

This verifies the same compiled IR3 code is present in both functional driver
versions. It does not establish whether R11 renders any real shader correctly.
"""
import argparse, hashlib, json, struct
from pathlib import Path

HASHES = {
  "original": "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404",
  "dd": "4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9",
}
def sections(buf):
    shoff = struct.unpack_from("<Q",buf,0x28)[0]
    ent,count,names_index = struct.unpack_from("<HHH",buf,0x3a)
    vals=[struct.unpack_from("<IIQQQQIIQQ",buf,shoff+n*ent) for n in range(count)]
    section=vals[names_index]
    names=buf[section[4]:section[4]+section[5]]
    return {names[item[0]:].split(b"\0",1)[0].decode():item for item in vals}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("original",type=Path)
    p.add_argument("dd",type=Path)
    args=p.parse_args()
    orig=args.original.read_bytes()
    dd=args.dd.read_bytes()
    assert hashlib.sha256(orig).hexdigest()==HASHES["original"]
    assert hashlib.sha256(dd).hexdigest()==HASHES["dd"]
    a=sections(orig)[".text"]
    b=sections(dd)[".text"]
    assert a[3]==b[3] and a[5]==b[5]
    x=orig[a[4]:a[4]+a[5]]
    y=dd[b[4]:b[4]+b[5]]
    changes=[]
    start=None
    for i,(u,v) in enumerate(zip(x,y)):
        if u!=v and start is None:
            start=i
        if u==v and start is not None:
            changes.append((start,i))
            start=None
    if start is not None: changes.append((start,len(x)))
    total=sum(end-begin for begin,end in changes)
    assert total==12 and len(changes)==7
    assert all(not (begin + a[3] < 0xadeb00 and end + a[3] > 0xac5ccc)
               for begin,end in changes), "Unexpected change in IR3 executable path"
    result={
        "functional_driver_text_bytes":len(x),
        "changed_executable_bytes":total,
        "changed_regions":[{"address":hex(a[3]+i),"length":j-i}
                           for i,j in changes],
        "compiled_ir3_shader_path_identical":True,
        "limitations":"This is only original-vs-DD, not GameHub-vs-R11 semantic equivalence",
    }
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
