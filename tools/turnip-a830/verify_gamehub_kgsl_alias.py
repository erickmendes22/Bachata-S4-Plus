#!/usr/bin/env python3
"""Source and executable boundary tests for the GameHub A830 KGSL alias retry.

Optional: --elf ORIGINAL_GAMEHUB_SO validates directly against the exact
original ELF; CI without the copyrighted binary only tests the source
contract and compiles the actual recovered helper function for edge cases.
"""
import argparse, hashlib, importlib.util, pathlib, subprocess, tempfile, struct

DIR = pathlib.Path(__file__).resolve().parent
PATCHER = DIR / "apply_gamehub_kgsl_alias_4gb.py"
ELF_HASH = "1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404"
ORIGINAL = {
  0xA3C964: 0x8b08012a,  # add x10, x9, x8 (start+length)
  0xA3C968: 0xd100054a,  # sub x10, x10, #1
  0xA3C96C: 0xca090149,  # eor x9, x10, x9
  0xA3C970: 0xd360fd29,  # lsr x9, x9, #32
  0xA3C974: 0xb5000669,  # cbnz x9, 0xa3ca40
  0xA3C888: 0xb2600108,  # orr x8, x8, #0x100000000 (FORCE_32BIT)
  0xA3CB3C: 0x8b08012a,
  0xA3CB40: 0xd100054a,
  0xA3CB44: 0xca090149,
  0xA3CB48: 0xd360fd29,
  0xA3CB4C: 0xb4fff169,  # cbz x9, normal bind
}
def load_patch():
    spec = importlib.util.spec_from_file_location("gamehub_kgsl", PATCHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def read_word(elf: bytes, va: int):
    assert elf[:4] == b"\x7fELF" and elf[4] == 2 and elf[5] == 1
    off = struct.unpack_from("<Q",elf,0x20)[0]
    size,count = struct.unpack_from("<HH",elf,0x36)
    for i in range(count):
        typ,_,file_off,start,_,filesz,_,_ = struct.unpack_from("<IIQQQQQQ",elf,off+i*size)
        if typ == 1 and start <= va and va+4<=start+filesz:
            return struct.unpack_from("<I",elf,file_off+va-start)[0]
    raise AssertionError(hex(va))
def check_original(path):
    elf=path.read_bytes()
    assert hashlib.sha256(elf).hexdigest()==ELF_HASH
    for va,code in ORIGINAL.items():
        got=read_word(elf,va)
        assert got==code, f"ELF changed @0x{va:x}: {got:08x} != {code:08x}"
    print(f"PASS original ELF {len(ORIGINAL)} instructions / SHA256")

def check_source(patched):
    s=patched.read_text()
    m=load_patch()
    assert s.count("kgsl_gamehub_a830_alias_crosses_4gb(")==2
    assert "attempt ? KGSL_MEMFLAGS_FORCE_32BIT : 0ull" in s
    assert "kgsl_bo_needs_alias" in s and "kgsl_bo_destroy_alias" in s
    chunk=s.split("kgsl_bo_create_alias(",1)[1].split("kgsl_bo_destroy_alias(",1)[0]
    order=["IOCTL_KGSL_GPUOBJ_ALLOC","IOCTL_KGSL_GPUMEM_GET_INFO",
           "kgsl_gamehub_a830_alias_crosses_4gb(info.gpuaddr, bo->size)",
           "IOCTL_KGSL_GPUMEM_BIND_RANGES","bo->alias_handle = alloc.id"]
    points=[chunk.index(x) for x in order]
    assert points == sorted(points)
    assert "if (attempt == 0)\n            continue;" in chunk
    assert "IOCTL_KGSL_GPUMEM_FREE_ID" in chunk
    assert "strerror(saved_errno)" in chunk
    header = m.REPLACEMENT.split("static VkResult\nkgsl_bo_create_alias",1)[0]
    program = "#include <stdint.h>\n#include <stdio.h>\n" + header + r'''
int main() {
   struct Case { uint64_t base, length; bool crosses; };
   Case tests[] = {
      {0, 0, true}, {0, 1, false},
      {0xfffffffeULL, 2, false},
      {0xfffffffeULL, 3, true},
      {0xffffffffULL, 1, false},
      {0xffffffffULL, 2, true},
      {0x100000000ULL, 1, false},
      {0xfffff000ULL, 0x1000, false},
      {0xfffff000ULL, 0x1001, true},
      {0xffff00000000ULL, 4096, false},
      {UINT64_MAX, 1, false},
      {UINT64_MAX, 2, true},
      {0, 0x100000000ULL, false},
      {0, 0x100000001ULL, true},
      {0x100000000ULL, 0x100000000ULL, false},
      {0x100000001ULL, 0x100000000ULL, true},
   };
   for (auto t : tests)
      if (kgsl_gamehub_a830_alias_crosses_4gb(t.base,t.length) != t.crosses)
         return 1;
   return 0;
}
'''
    with tempfile.TemporaryDirectory() as d:
        cpp=pathlib.Path(d)/"test.cpp"
        out=pathlib.Path(d)/"test"
        cpp.write_text(program)
        subprocess.run(["clang++","-std=c++20","-Wall","-Wextra","-Werror",
                         str(cpp),"-o",str(out)],check=True)
        subprocess.run([str(out)],check=True)
    print("PASS A830 source contract + 16 compiled C++ boundary edge cases")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=pathlib.Path)
    p.add_argument("--elf",type=pathlib.Path)
    a=p.parse_args()
    if a.source: check_source(a.source)
    if a.elf: check_original(a.elf)
    if not (a.source or a.elf): p.error("specify --source and/or --elf")
