#!/usr/bin/env python3
"""Adapt native ARM64/Android kernel UUID generation on the modern 0.21.1 HLE.

Unlike Linux/glibc, Bionic has no libuuid headers or libuuid.so. This replaces
only the native host UUID provider, not PS4 UUID syscall behavior or HLE symbols.
"""
import argparse
from pathlib import Path

def replace_one(path, old, new):
    content=path.read_text()
    if content.count(old) != 1:
        raise RuntimeError(f"{path}: modern UUID API changed; refusing partial port")
    path.write_text(content.replace(old,new,1))

def main(source):
    p=source/"src/core/libraries/kernel/kernel.cpp"
    text=p.read_text()
    if "BIONIC_021_NATIVE_UUID" in text:
        print("BIONIC_021_NATIVE_UUID_ALREADY_PRESENT")
        return
    old_include="#ifdef _WIN64\n#include <Rpc.h>\n#else\n#include <uuid/uuid.h>\n#endif"
    new_include="#ifdef _WIN64\n#include <Rpc.h>\n#elif defined(__ANDROID__)\n#include <stdlib.h>\n#else\n#include <uuid/uuid.h>\n#endif"
    old_call="""#ifdef _WIN64
    UUID uuid;
    if (UuidCreate(&uuid) != RPC_S_OK) {
        return ORBIS_KERNEL_ERROR_EFAULT;
    }
#else
    uuid_t uuid;
    uuid_generate(uuid);
#endif"""
    new_call="""#ifdef _WIN64
    UUID uuid;
    if (UuidCreate(&uuid) != RPC_S_OK) {
        return ORBIS_KERNEL_ERROR_EFAULT;
    }
#elif defined(__ANDROID__)
    // BIONIC_021_NATIVE_UUID: generate RFC 4122 v4 in Android Bionic.
    u8 uuid[sizeof(OrbisKernelUuid)];
    arc4random_buf(uuid, sizeof(uuid));
    uuid[6] = (uuid[6] & 0x0f) | 0x40;
    uuid[8] = (uuid[8] & 0x3f) | 0x80;
#else
    uuid_t uuid;
    uuid_generate(uuid);
#endif"""
    if old_include not in text or old_call not in text:
        if "uuid/uuid.h" not in text and "uuid_generate(uuid)" not in text:
            print("BIONIC_021_NATIVE_UUID_UPSTREAM_ALREADY_PORTABLE")
            return
        raise RuntimeError("0.21.1 UUID source partially changed: requires review")
    replace_one(p,old_include,new_include)
    replace_one(p,old_call,new_call)
    print("BIONIC_021_NATIVE_UUID_PORTED")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True,type=Path)
    main(ap.parse_args().source)
