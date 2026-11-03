#!/usr/bin/env python3
"""Restore exact GameHub QTI mapper selection order in the V38 gralloc loader.

Original GameHub ARM64 @ 0xca2c0c..0xca2cc8:
  dlsym(RTLD_DEFAULT, "android_load_sphal_library")
  sphal("mapper.qti.so", RTLD_NOW)   @0xca2c44-0xca2c54
  if unavailable dlopen("libmain_hook.so", RTLD_NOW) @0xca2c60..0xca2c80
  try again with sphal->"mapper.qti.so"
  dlsym(handle, "AIMapper_loadIMapper").
In V38 the custom IMapper backend iterated /vendor/lib64/hw/mapper.* files
and selected the FIRST, not necessarily QTI. Prefer the GameHub provider,
retaining enumeration as a fallback.
"""
from pathlib import Path
import sys

PREFERRED_OLD="""   for (unsigned d = 0; d < ARRAY_SIZE(dirs); d++) {"""
PREFERRED_NEW="""   // Verified original GameHub loader calls the QTI provider by name first.
   // Directory enumeration stays as fallback for non-QTI devices.
   void *qti = sphal("mapper.qti.so", RTLD_NOW);
   if (qti) {
      load_imapper_fn qti_load = (load_imapper_fn)
         dlsym(qti, "AIMapper_loadIMapper");
      if (qti_load) {
         *out_load = qti_load;
         return qti;
      }
      dlclose(qti);
   }

   for (unsigned d = 0; d < ARRAY_SIZE(dirs); d++) {"""

FALLBACK_OLD="""   if (!sphal)
      sphal = (sphal_load_fn)dlsym(RTLD_DEFAULT,
                                  "android_load_sphal_library");

   load_imapper_fn load = NULL;"""
FALLBACK_NEW="""   if (!sphal)
      sphal = (sphal_load_fn)dlsym(RTLD_DEFAULT,
                                  "android_load_sphal_library");

   // Original GameHub tries libmain_hook.so if the loader symbol is hidden.
   // This is useful inside Android/FEX app namespaces, but optional.
   if (!sphal) {
      void *hook = dlopen("libmain_hook.so", RTLD_NOW | RTLD_LOCAL);
      if (hook)
         sphal = (sphal_load_fn)dlsym(hook,
                                     "android_load_sphal_library");
   }

   load_imapper_fn load = NULL;"""

def apply(path:Path):
    s=path.read_text()
    if "GameHub A830 gralloc: legacy FD/stride" not in s:
        raise ValueError("Requires GameHub legacy-gralloc metadata-overlay patch")
    for name,old,new in [("QTI priority",PREFERRED_OLD,PREFERRED_NEW),
                          ("libmain_hook fallback",FALLBACK_OLD,FALLBACK_NEW)]:
        if s.count(old)!=1:
            raise ValueError("Pinned gralloc source drift / already patched: "+name)
        s=s.replace(old,new,1)
    for name in ("mapper.qti.so", "libmain_hook.so",
                 "android_load_sphal_library", "AIMapper_loadIMapper"):
        if name not in s:
            raise ValueError("Expected GameHub QTI loader fragment absent: "+name)
    path.write_text(s)
    print("PASS: original GameHub QTI mapper priority + libmain_hook fallback integrated")

if __name__ == "__main__":
    apply(Path(sys.argv[1]) if len(sys.argv)>1 else
          Path("src/util/u_gralloc/u_gralloc_aimapper.c"))
