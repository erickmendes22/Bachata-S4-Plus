#!/usr/bin/env python3
"""FreeBSD/Orbis amd64 setjmp/longjmp executed as GUEST x86-64 code in FEX.

Based on the ABI of FreeBSD releng/9.3 libc/amd64/gen/{setjmp,_setjmp}.S
(BSD-3-Clause). Saves guest RIP, RSP, callee-saved registers, FCW and MXCSR.
Signal-mask transfer is NOT implemented: no false claims of full sigsetjmp.
"""
from __future__ import annotations
import base64
import hashlib
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

SALT=bytes.fromhex("518D64A635DED8C1E6B039B1C3E55230")
X86_MEMCPY=bytes.fromhex("4889f84889d1fcf3a4c3") # rax=rdi; rcx=rdx; cld; rep movsb; ret
X86_SETJMP=bytes.fromhex("488b042448890748895f084889671048896f184c8967204c896f284c8977304c897f38d97f400fae5f4431c0c3")
X86_LONGJMP=bytes.fromhex("4889fa89f00fae5c24fc8b7a4483e7c08b7424fc83e63f09f7897c24fc0fae5424fc488b0a488b5a08488b6210488b6a184c8b62204c8b6a284c8b72304c8b7a38d96a4085c07502ffc048890c24c3")
ALIASES={"setjmp":"gNQ1V2vfXDE","_setjmp":"sjpkrhugvVI",
         "longjmp":"lKEN2IebgJ0","_longjmp":"+F+9hhi6k9Q"}

def nid(name):
    return base64.b64encode(hashlib.sha1(name.encode()+SALT).digest()[:8][::-1]).decode().rstrip("=")

def c_bytes(b):
    return ", ".join(f"0x{x:02x}" for x in b)

def apply(root:Path):
    for name,value in ALIASES.items():
        if nid(name)!=value:
            raise RuntimeError(f"PS4 NID mismatch {name}: {nid(name)}")
    path=root/"src/core/guest_cpu/hle_call_adapter.cpp"
    content='#include "common/elf_info.h"\n'+path.read_text()
    begin=content.index("    constexpr std::size_t veneer_size = 16;\n")
    end_anchor="    __builtin___clear_cache(reinterpret_cast<char*>(code), reinterpret_cast<char*>(code + veneer_size));\n"
    end=content.index(end_anchor,begin)+len(end_anchor)
    if content.count(end_anchor)!=1 or "mov r10, rcx preserves" not in content[begin:end]:
        raise RuntimeError("FEX HLE veneer template diverged; refuse guessed patch")
    emitted="""    // BIONIC_GUEST_X86_NONLOCAL_JUMP: do NOT use ARM64/host setjmp().
    // A guest native return-twice veneer saves/restores PS4 x86 stack and RIP.
    // FreeBSD amd64 jmp_buf: rip, rbx, rsp, rbp, r12-r15, FCW, MXCSR.
    constexpr u8 guest_setjmp[]{"""+c_bytes(X86_SETJMP)+"""};
    constexpr u8 guest_longjmp[]{"""+c_bytes(X86_LONGJMP)+"""};
    const std::string_view full = adapter.Name();
    const auto hash = full.substr(0, full.find('#'));
    const bool is_libc = full.find("#libc#1#libc#Function") != std::string_view::npos;
    const bool do_setjmp = is_libc && (hash == "gNQ1V2vfXDE" || hash == "sjpkrhugvVI");
    const bool do_longjmp = is_libc && (hash == "lKEN2IebgJ0" || hash == "+F+9hhi6k9Q");
    constexpr u8 guest_memcpy[]{0x48,0x89,0xf8,0x48,0x89,0xd1,0xfc,0xf3,0xa4,0xc3};
    const bool do_memcpy = Common::ElfInfo::Instance().GameSerial() == "CUSA00785" && is_libc && hash == "Q3VBxCXhUHs";
    auto* const code = static_cast<u8*>(page);
    std::size_t written = 0;
    if (do_memcpy) {
        if (sizeof(guest_memcpy)>size) {
            munmap(page,size);
            return HleVeneerFailure{ENOSPC};
        }
        std::memcpy(code,guest_memcpy,sizeof(guest_memcpy));
        written=sizeof(guest_memcpy);
        std::fprintf(stderr,"BIONIC_ORDER_GUEST_MEMCPY_VENEER bytes=%zu\\n",written);
    } else if (do_setjmp || do_longjmp) {
        const u8* native_code = do_setjmp ? guest_setjmp : guest_longjmp;
        const size_t bytes = do_setjmp ? sizeof(guest_setjmp) : sizeof(guest_longjmp);
        if (bytes > size) {
            munmap(page, size);
            return HleVeneerFailure{ENOSPC};
        }
        std::memcpy(code, native_code, bytes);
        written = bytes;
        std::fprintf(stderr, "BIONIC_GUEST_X86_NONLOCAL_JUMP type=%s bytes=%zu\\n",
                     do_setjmp ? "setjmp" : "longjmp", bytes);
    } else {
        // Normal, unchanged FEX syscall veneer for ALL other HLE functions.
        constexpr u8 preserve_fourth_argument[]{0x49, 0x89, 0xca};
        constexpr u8 prefix[]{0x48, 0xb8};
        constexpr u8 suffix[]{0x0f, 0x05, 0xc3};
        std::memcpy(code, preserve_fourth_argument, sizeof(preserve_fourth_argument));
        std::memcpy(code + sizeof(preserve_fourth_argument), prefix, sizeof(prefix));
        const auto operation = adapter.Operation();
        const auto operation_offset = sizeof(preserve_fourth_argument) + sizeof(prefix);
        std::memcpy(code + operation_offset, &operation, sizeof(operation));
        std::memcpy(code + operation_offset + sizeof(operation), suffix, sizeof(suffix));
        written = 16;
    }
    __builtin___clear_cache(reinterpret_cast<char*>(code), reinterpret_cast<char*>(code + written));
"""
    content=content[:begin]+emitted+content[end:]
    path.write_text(content)
    return {"nativeGuestX86":True,"setjmpBytes":len(X86_SETJMP),
            "longjmpBytes":len(X86_LONGJMP),"aliases":ALIASES,
            "signalMask":"not yet emulated"}

def selftest():
    for name,value in ALIASES.items():
        assert nid(name)==value
    assert nid("memcpy")=="Q3VBxCXhUHs"
    assert len(X86_SETJMP)==45 and len(X86_LONGJMP)==79
    if platform.machine() not in ("x86_64","AMD64"):
        raise RuntimeError("Needs x86-64 Linux host to execute guest assembly test")
    with tempfile.TemporaryDirectory(prefix="bionic-jmp-") as folder:
        d=Path(folder)
        assembly=(".text\n.global fex_jump_set\n.type fex_jump_set, @function\n"
                  "fex_jump_set:\n.byte "+c_bytes(X86_SETJMP)+
                  "\n.global fex_jump_go\n.type fex_jump_go, @function\n"
                  "fex_jump_go:\n.byte "+c_bytes(X86_LONGJMP)+
                  "\n.global fex_memcpy\n.type fex_memcpy, @function\nfex_memcpy:\n.byte "+c_bytes(X86_MEMCPY)+
                  '\n.section .note.GNU-stack,"",@progbits\n')
        (d/"jump.S").write_text(assembly)
        source="""#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
extern void* fex_memcpy(void*,const void*,size_t);
extern int fex_jump_set(uint64_t*) __attribute__((returns_twice));
extern void fex_jump_go(uint64_t*, int) __attribute__((noreturn));
static uint64_t env[16]; static volatile int calls;
__attribute__((noinline)) static void nested(int code) {
  calls++; fex_jump_go(env,code);
}
static int trial(int code) {
  int ret=fex_jump_set(env); if(ret==0) nested(code); return ret;
}
int main(void) {
  unsigned char source[512], dest[514];
  for (unsigned i=0;i<sizeof(source);++i) source[i]=(unsigned char)(i*17);
  for (unsigned n=0;n<=512;++n) {
    memset(dest,0xa5,sizeof(dest));
    if (fex_memcpy(dest+1,source,n)!=dest+1 ||
        memcmp(dest+1,source,n) || dest[0]!=0xa5 || dest[n+1]!=0xa5) abort();
  }
  memset(env,0xa5,sizeof(env));
  if(trial(7)!=7 || calls!=1) abort();
  if(trial(0)!=1 || calls!=2) abort();
  if(trial(109)!=109 || calls!=3) abort();
  if(env[0]==0 || env[2]==0 || env[3]==0) abort();
  puts("BIONIC_GUEST_X86_SETJMP_LONGJMP_RETURNS_TWICE_PASS");
}
"""
        (d/"test.c").write_text(source)
        subprocess.run(["cc","-O0",str(d/"test.c"),str(d/"jump.S"),"-o",str(d/"test")],check=True)
        subprocess.run([str(d/"test")],check=True,timeout=10)
    print("BIONIC_GUEST_X86_NONLOCAL_JUMP_ABI_PASS")

if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="selftest": selftest()
    else: raise SystemExit("usage: guest_jump_abi.py selftest")
