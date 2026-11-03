#!/usr/bin/env python3
"""GameHub/R8/R9 differential evidence, from original Android files. No APK build.
This script does not claim visual or Vulkan command-stream equivalence.
"""
from pathlib import Path
import argparse, hashlib, json, re, struct, zipfile

EXPECTED = {
 "original": "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404",
 "gamehub_dd_elf": "4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9",
 "r9_elf": "b8a589ee04205778935f8a0b1e3f396c5fa55edf22a7427e6ab0ac04906bb496",
 "r8_zip": "2aeb3b02444df8e2d241c293944705bb3b627f6cb51dfb10ab16385ef5e72756",
 "gamehub_dd_zip": "8255659cc205110e0fa89f2d364292b86fe563a2cedafbc41915bead5a611ecb",
}
def digest(raw): return hashlib.sha256(raw).hexdigest()
def zip_item(path, item):
    with zipfile.ZipFile(path) as z: return z.read(item)
def vk_names(raw):
    return set(m.decode() for m in re.findall(
        rb'(VK_[A-Za-z][A-Za-z_0-9]{5,96})\x00',raw))
def facts(raw):
    lines=raw.decode("utf-8","replace").splitlines()
    return {
      "predication":sum("Unimplemented IT_SET_PREDICATION" in s for s in lines),
      "unmapped":sum("not fully GPU mapped" in s for s in lines),
      "cached_permutation_conflict":sum("Cached permutation 0 of" in s for s in lines),
      "unavailable_extensions":sorted({m.group(1) for s in lines if
         (m:=re.search(r"Extension (VK_[A-Za-z0-9_]+) unavailable",s))}),
      "unsupported_formats":sorted({m.group(1) for s in lines if
         "not fully supported" in s and
         (m:=re.search(r"vk_format=([A-Za-z0-9_]+)",s))}),
      "subgroups":next((s for s in lines if s.startswith("GPU subgroups:")),None),
      "async_warning":sum("queued geometry draws can be skipped until ready" in s for s in lines),
    }
def elf_word(data, addr):
    if data[:4]!=b"\x7fELF" or data[4]!=2 or data[5]!=1: raise ValueError("ELF64 LE required")
    phoff=struct.unpack_from("<Q",data,0x20)[0]
    ent,num=struct.unpack_from("<HH",data,0x36)
    for i in range(num):
        t,_,off,va,_,size,_,_=struct.unpack_from("<IIQQQQQQ",data,phoff+i*ent)
        if t==1 and va<=addr and addr+4<=va+size:
            return struct.unpack_from("<I",data,off+addr-va)[0]
    raise ValueError(f"No mapped ELF VA 0x{addr:x}")
def main():
    p=argparse.ArgumentParser()
    for key in ("original","r8_zip","r9_zip","gamehub_dd_zip","r8_logs","gamehub_logs"):
        p.add_argument("--"+key.replace("_","-"),required=True,type=Path)
    a=p.parse_args()
    src=a.original.read_bytes()
    r8=a.r8_zip.read_bytes()
    r9=zip_item(a.r9_zip,"libvulkan_freedreno.so")
    dd=a.gamehub_dd_zip.read_bytes()
    ddelf=zip_item(a.gamehub_dd_zip,"libvulkan_freedreno.so")
    for label,raw,expected in [
        ("original",src,EXPECTED["original"]),
        ("gamehub_dd_elf",ddelf,EXPECTED["gamehub_dd_elf"]),
        ("r9_elf",r9,EXPECTED["r9_elf"]),
        ("r8_zip",r8,EXPECTED["r8_zip"]),
        ("gamehub_dd_zip",dd,EXPECTED["gamehub_dd_zip"])]:
        assert digest(raw)==expected, f"{label}: changed binary, do not reuse stale conclusions"
    opcodes={0xca2f04:0x97fffb1e,0xca2f08:0x350011c0,0xca2f1c:0x528000e1,
             0xca3034:0x52800101,0xca313c:0x2a1f03e0,
             0xca316c:0xb90002f9,0xca3170:0xf90006e8}
    for va,word in opcodes.items():
        assert elf_word(src,va)==word, f"Gralloc opcode mismatch at {va:x}"
    rf=facts(zip_item(a.r8_logs,"logs/android-game.log"))
    gf=facts(zip_item(a.gamehub_logs,"logs/android-game.log"))
    for field in ("unavailable_extensions","unsupported_formats","subgroups"):
        assert rf[field]==gf[field], f"Previously shared capability differs: {field}"
    out={"original_opcodes_verified":len(opcodes),
         "r8":rf, "gamehub":gf,
         "vulkan_binary_names_only_in_original":sorted(vk_names(src)-vk_names(r9)),
         "vulkan_binary_names_only_in_r9":sorted(vk_names(r9)-vk_names(src)),
         "cannot_infer_from_shared_warnings":["predication","unmapped","async_warning"],
         "missing_evidence":["R9 game runtime/frames", "shader IR3 output comparison",
              "device command-stream trace","GPU resolve/blit correctness"]}
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
